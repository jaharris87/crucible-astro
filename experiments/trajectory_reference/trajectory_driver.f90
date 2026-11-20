! Standalone CRUCIBLE driver for the hash-bound Phase 2D native path.
program trajectory_driver
  use, intrinsic :: iso_fortran_env, only: int8,int32,int64,real64
  use, intrinsic :: ieee_arithmetic
  use xnet_types, only: dp
  use xnet_parallel, only: parallel_initialize,parallel_finalize,parallel_myproc,parallel_nprocs
  use xnet_controls
  use nuclear_data, only: ny,aa,zz,read_nuclear_data
  use reaction_data, only: read_reaction_data,nnnu,nffn,nreac,iwk1
  use xnet_abundances, only: y,yo,yt,ydot
  use xnet_conditions
  use xnet_screening, only: screening_init
  use xnet_eos, only: eos_initialize
  use xnet_jacobian, only: read_jacobian_data
  use xnet_integrate_be, only: solve_be
  use native_adapter
  implicit none
  integer :: inp,output,ios,k,j,step,its(1),saved_maps,maps
  integer(int32) :: header(8),magic
  integer(int8) :: endian(4)
  integer(int64) :: file_size,file_position
  real(dp),allocatable :: forcing_time(:),forcing_t9(:),forcing_rho(:),requested(:),mesh(:)
  real(dp) :: input_z(160),input_a(160),initial(160),f(160),b0,baryon,charge,native_ye,total
  real(dp) :: abar,zbar,z2bar,zibar,target,remaining,h,clock_start,clock_stop,phase_start
  character(80) :: data_description
  character(160) :: reason
  character(4096) :: map_line
  logical :: ok,active(1)
  call open_diagnostics()
  call cpu_time(clock_start)
  if (storage_size(1)/=32.or.storage_size(1.0)/=64.or.dp/=real64) call fail('required int32/defaultreal64')
  magic=int(z'01020304',int32); endian=transfer(magic,endian)
  if (any(endian/=[4_int8,3_int8,2_int8,1_int8])) call fail('little-endian stream required')
  call parallel_initialize()
  if (parallel_nprocs()/=1) call fail('exactly one MPI rank required')
  myid=parallel_myproc(); nproc=1; mythread=1; nthread=1
  nzevolve=1; nzbatchmx=1; nzbatch=1; szbatch=1; szone=1; nzone=1; nzone_max=1
  zb_lo=1; zb_hi=1; zb_offset=0; zone_id=[1,1,1,1]
  iweak0=1; iscrn=1; iheat=0; ineutrino=1; iprocess=0; isolv=1
  idiag=0; itsout=0; kitmx=30; ijac=1; ymin=0; tdel_maxmult=2
  if (t9min/=0.01_dp) call fail('changed strong-reaction cutoff')
  allocate(lzactive(1),iweak(1),kmon(2,1),ktot(5,1))
  lzactive=.true.; active=.true.; iweak=iweak0; kmon=0; ktot=0
  open(newunit=lun_diag,file='kernel.log',status='new',action='write')
  call read_nuclear_data('network',data_description)
  call read_reaction_data('network')
  if (ny/=160.or.nffn/=176.or.nnnu/=0) call fail('unexpected network dimensions/NNU')
  if (any(nreac/=[683,1345,16,4])) call fail('unexpected reaction counts')
  if (any(iwk1<0.or.iwk1>4)) call fail('unexpected one-reactant weak flags')
  call screening_init()
  call eos_initialize()
  call read_jacobian_data('network')
  allocate(y(ny,1),yo(ny,1),yt(ny,1),ydot(ny,1))
  allocate(t(1),to(1),tt(1),tdel(1),tdel_next(1),tdel_old(1))
  allocate(t9(1),t9o(1),t9t(1),rho(1),rhoo(1),rhot(1),ye(1),yeo(1),yet(1))
  allocate(cv(1),etae(1),detaedt9(1),t9dot(1),nt(1),nto(1),ntt(1),nh(1))
  open(newunit=inp,file='input.bin',access='stream',form='unformatted',status='old',action='read',iostat=ios)
  if (ios/=0) call fail('cannot open input.bin')
  read(inp,iostat=ios) header
  if (ios/=0) call fail('truncated input header')
  if (header(1)/=int(z'43524432',int32).or.header(2)/=1.or.header(3)/=160) call fail('input magic/version/species')
  if (header(4)<2.or.header(4)>50000.or.header(5)<1.or.header(5)>50000 &
      .or.header(6)<1.or.header(6)>1000000) call fail('input dimensions outside bounded structural limits')
  if (header(7)<0.or.header(7)>2.or.header(8)<1.or.header(8)>160) call fail('input mode/direction coordinate')
  allocate(forcing_time(header(4)),forcing_t9(header(4)),forcing_rho(header(4)))
  allocate(requested(header(5)),mesh(header(6)))
  read(inp,iostat=ios) nonlinear_atol,nonlinear_rtol,input_z,input_a,initial, &
                         forcing_time,forcing_t9,forcing_rho,requested,mesh
  if (ios/=0) call fail('truncated input payload')
  inquire(unit=inp,size=file_size,pos=file_position)
  if (file_position/=file_size+1) call fail('trailing input bytes')
  close(inp)
  if (.not.same_bits(input_z,zz).or..not.same_bits(input_a,aa)) call fail('ordered species identity mismatch')
  if (.not.((nonlinear_atol==1e-13_dp.and.nonlinear_rtol==1e-11_dp).or. &
             (nonlinear_atol==1e-14_dp.and.nonlinear_rtol==1e-12_dp))) call fail('unapproved nonlinear controls')
  if (.not.all(ieee_is_finite(forcing_time)).or..not.all(ieee_is_finite(forcing_t9)) &
      .or..not.all(ieee_is_finite(forcing_rho))) call fail('nonfinite forcing inputs')
  if (any(forcing_time(2:)<=forcing_time(:size(forcing_time)-1))) call fail('nonincreasing forcing inputs')
  if (any(forcing_t9<=0).or.any(forcing_rho<=0)) call fail('nonpositive forcing inputs')
  if (.not.all(ieee_is_finite(mesh)).or..not.all(ieee_is_finite(requested))) call fail('nonfinite grids')
  if (any(mesh(2:)<=mesh(:size(mesh)-1)).or.any(requested(2:)<=requested(:size(requested)-1))) &
    call fail('nonincreasing grids')
  if (forcing_time(1)>0.or.forcing_time(size(forcing_time))<0.01_dp) call fail('forcing misses full horizon')
  if (mesh(1)<0.or.mesh(size(mesh))>0.01_dp) call fail('mesh outside horizon')
  if (header(7)==1) then
    if (mesh(1)/=0.or.mesh(size(mesh))/=0.01_dp) call fail('trajectory mesh endpoints')
    if (requested(1)/=0.or.requested(size(requested))/=0.01_dp) call fail('requested endpoints')
    do j=1,size(requested)
      if (.not.any(mesh==requested(j))) call fail('requested time missing from mesh')
    enddo
    do j=1,size(forcing_time)
      if (forcing_time(j)>0.and.forcing_time(j)<0.01_dp) then
        if (.not.any(mesh==forcing_time(j))) call fail('interior forcing knot missing from mesh')
      endif
    enddo
  endif
  nh=size(forcing_time)
  allocate(th(nh(1),1),t9h(nh(1),1),rhoh(nh(1),1))
  th(:,1)=forcing_time; t9h(:,1)=forcing_t9; rhoh(:,1)=forcing_rho
  t=mesh(1); tt=t; to=t; nt=1; ntt=1; nto=1
  tdel=0; tdel_old=0; tdel_next=0
  call t9rhofind(0,tt,ntt,t9t,rhot,mask_in=active)
  t9=t9t; t9o=t9t; rho=rhot; rhoo=rhot
  y(:,1)=initial; yo=y; yt=y
  call fresh(initial,tt(1),t9t(1),rhot(1),f,ok,reason)
  if (.not.ok) call fail('initial state '//trim(reason))
  ye=yet; yeo=yet
  b0=sum(aa*initial)
  write(log_unit,*) 'INITIAL_MOMENTS',b0,sum(zz*initial),yet(1),t9t(1),rhot(1)
  call cpu_time(phase_start)
  write(log_unit,*) 'SETUP_CPU_SECONDS',phase_start-clock_start
  select case(header(7))
  case(0)
    open(newunit=output,file='control.bin',status='new',access='stream',form='unformatted')
    write(output) f
    close(output)
  case(1)
    open(newunit=output,file='accepted.bin',status='new',access='stream',form='unformatted')
    call accepted_row()
    step=0
    do k=2,size(mesh)
      target=mesh(k)
      do while (t(1)<target)
        step=step+1
        remaining=target-t(1)
        if (tdel_next(1)>0) then
          h=min(remaining,tdel_next(1))
        else
          h=remaining
        endif
        tt=t+h
        if (h==remaining) tt=target
        tdel=tt-t
        if (tt(1)<=t(1).or.tdel(1)<=0) call fail('unrepresentable forward time')
        call t9rhofind(step,tt,ntt,t9t,rhot,mask_in=active)
        yt=y; its=0
        call solve_be(step,its)
        if (its(1)/=0) call fail('ten native step attempts exhausted')
        if (t(1)>target) call fail('accepted step crossed mesh target')
        accepted_count=accepted_count+1
        baryon=sum(aa*y(:,1))
        if (.not.ieee_is_finite(baryon).or.abs(baryon-b0)>1e-10_dp*max(1.0_dp,abs(b0))) &
          call fail('accepted-state baryon drift bound')
        if (any(y<0).or..not.all(ieee_is_finite(y))) call fail('invalid accepted state')
        call accepted_row()
        call checkpoint()
        tdel_old=tdel
      enddo
      if (t(1)/=target) call fail('mesh target not reached exactly')
    enddo
    if (t(1)/=0.01_dp) call fail('incomplete horizon')
    close(output)
  case(2)
    call directional_sweep(initial,tt(1),t9t(1),rhot(1),header(8))
  end select
  call cpu_time(clock_stop)
  write(log_unit,*) 'PHYSICS_PHASE_CPU_SECONDS',clock_stop-phase_start
  ! Retain actual loaded mappings after runtime-selected math kernels have run.
  open(newunit=maps,file='/proc/self/maps',status='old',action='read',iostat=ios)
  if (ios/=0) call fail('cannot read loaded library maps')
  open(newunit=saved_maps,file='loaded-maps.txt',status='new',action='write')
  do
    read(maps,'(a)',iostat=ios) map_line
    if (ios/=0) exit
    write(saved_maps,'(a)') trim(map_line)
  enddo
  close(maps); close(saved_maps)
  call cpu_time(clock_stop)
  write(log_unit,*) 'CPU_SECONDS',clock_stop-clock_start
  flush(lun_diag); close(lun_diag)
  call parallel_finalize()
  call finish()
contains
  subroutine accepted_row()
    real(dp) :: native_yet
    call y_moment(y(:,1),native_yet,total,abar,zbar,z2bar,zibar)
    baryon=sum(aa*y(:,1)); charge=sum(zz*y(:,1))
    if (.not.domain(y(:,1),t9(1),rho(1),reason)) call fail('accepted row '//trim(reason))
    write(output) t(1),y(:,1),ydot(:,1),final_residual,baryon,charge,native_yet, &
                  final_norm,final_l1,final_projection,cumulative_projection
    flush(output)
  end subroutine accepted_row
  logical function same_bits(left,right)
    real(dp),intent(in) :: left(:),right(:)
    integer :: i
    same_bits=.false.
    if (size(left)/=size(right)) return
    do i=1,size(left)
      if (transfer(left(i),0_int64)/=transfer(right(i),0_int64)) return
    enddo
    same_bits=.true.
  end function same_bits
end program trajectory_driver
