! Bounded original D-038 diagnostic commands. No trajectory advancement occurs.
module diagnostic_native
  use native_adapter
  use xnet_jacobian, only: indx,jacobian_build
  use reaction_data, only: csect1,csect2,csect3,csect4,b1,b2,b3,b4,nreac,nan,la,le, &
    n1i,n2i,n3i,n4i,mu1,mu2,mu3,mu4,n10,n20,n30,n40,a1,a2,a3,a4
  implicit none
contains
  subroutine read_linear_inputs(enabled,old,h,time)
    logical,intent(out) :: enabled
    real(dp),intent(out) :: old(160),h
    real(dp),intent(in) :: time
    logical :: has_old,has_h
    integer :: unit,ios
    integer(int64) :: size_bytes,position
    character(160) :: reason
    inquire(file='old-state.bin',exist=has_old)
    inquire(file='frozen-h.bin',exist=has_h)
    if (has_old.neqv.has_h) call fail('diagnostic old-state/frozen-h companion pair incomplete')
    enabled=has_old; old=0; h=0
    if (.not.enabled) return
    open(newunit=unit,file='old-state.bin',status='old',access='stream',form='unformatted',action='read')
    read(unit,iostat=ios) old
    if (ios/=0) call fail('diagnostic truncated old-state')
    inquire(unit=unit,size=size_bytes,pos=position)
    if (position/=size_bytes+1) call fail('diagnostic trailing old-state bytes')
    close(unit)
    open(newunit=unit,file='frozen-h.bin',status='old',access='stream',form='unformatted',action='read')
    read(unit,iostat=ios) h
    if (ios/=0) call fail('diagnostic truncated frozen-h')
    inquire(unit=unit,size=size_bytes,pos=position)
    if (position/=size_bytes+1) call fail('diagnostic trailing frozen-h bytes')
    close(unit)
    if (.not.ieee_is_finite(h).or.h/=1.953125e-7_dp.or.time/=h) call fail('diagnostic frozen h/time mismatch')
    if (.not.domain(old,t9t(1),rhot(1),reason)) call fail('diagnostic old-state '//trim(reason))
  end subroutine read_linear_inputs

  subroutine export_maps()
    integer :: unit
    open(newunit=unit,file='species.bin',status='new',access='stream',form='unformatted')
    write(unit) zz,aa
    close(unit)
    open(newunit=unit,file='used-maps.bin',status='new',access='stream',form='unformatted')
    write(unit) la,le
    write(unit) 1_int32,nreac(1),nan(1),n1i,mu1,n10,a1
    write(unit) 2_int32,nreac(2),nan(2),n2i,mu2,n20,a2
    write(unit) 3_int32,nreac(3),nan(3),n3i,mu3,n30,a3
    write(unit) 4_int32,nreac(4),nan(4),n4i,mu4,n40,a4
    close(unit)
  end subroutine export_maps

  subroutine export_baseline(filename,state,f)
    character(*),intent(in) :: filename
    real(dp),intent(in) :: state(160),f(160)
    integer :: unit
    integer(int32) :: header(12)
    if (.not.unchanged_real_bits(state,last_evaluated_state).or..not.unchanged_real_bits(f,ydot(:,1))) &
      call fail('diagnostic baseline payload does not match current evaluation')
    header=[int(z'43524442',int32),1_int32,160_int32,int(size(csect1),int32),int(size(csect2),int32), &
            int(size(csect3),int32),int(size(csect4),int32),int(size(b1),int32),int(size(b2),int32), &
            int(size(b3),int32),int(size(b4),int32),int(branch_size,int32)]
    open(newunit=unit,file=filename,status='new',access='stream',form='unformatted')
    write(unit) header
    write(unit) real(rhs_count,dp),last_evaluated_conditions,sum(aa*state),sum(zz*state),last_evaluated_eos, &
                state,f,csect1,csect2,csect3,csect4,b1,b2,b3,b4
    write(unit) int(branch_signature,int32)
    close(unit)
  end subroutine export_baseline

  subroutine check_baseline_identity(f,reference_f,reference_workspace,reference_branch)
    real(dp),intent(in) :: f(160),reference_f(160),reference_workspace(:)
    integer,intent(in) :: reference_branch(branch_size)
    if (.not.unchanged_real_bits(f,reference_f)) call fail('diagnostic baseline F identity mismatch')
    if (.not.unchanged_real_bits([last_evaluated_eos,csect1(:,1),csect2(:,1),csect3(:,1),csect4(:,1), &
                                  b1(:,1),b2(:,1),b3(:,1),b4(:,1)],reference_workspace)) &
      call fail('diagnostic baseline EOS/coefficient/assembly identity mismatch')
    if (any(branch_signature/=reference_branch)) call fail('diagnostic baseline branch identity mismatch')
  end subroutine check_baseline_identity

  subroutine dump_matrix(filename,matrix)
    character(*),intent(in) :: filename
    real(dp),intent(in) :: matrix(:,:)
    integer :: unit
    open(newunit=unit,file=filename,status='new',access='stream',form='unformatted')
    write(unit) matrix
    close(unit)
  end subroutine dump_matrix

  subroutine run_native_diagnostic(command,base,time,temp,density,first_f,coordinate,linear_enabled,old,h)
    character(*),intent(in) :: command
    real(dp),intent(in) :: base(160),time,temp,density,first_f(160),old(160),h
    integer,intent(in) :: coordinate
    logical,intent(in) :: linear_enabled
    real(dp),parameter :: factors(4)=[0.1_dp,1.0_dp,10.0_dp,100.0_dp]
    real(dp) :: f(160),matrices(160,160,4),fixed_matrix(160,160),deltas(160,4)
    real(dp),allocatable :: reference_workspace(:)
    integer :: reference_branch(branch_size)
    integer :: i,unit,status_unit,repeat_count
    integer(int64) :: rhs_before,rhs_after
    logical :: ok,complete(4),linear_ok(4),active(1)
    character(160) :: reason
    character(40) :: filename
    active=.true.; linear_ok=.false.
    reference_workspace=[last_evaluated_eos,csect1(:,1),csect2(:,1),csect3(:,1),csect4(:,1), &
                         b1(:,1),b2(:,1),b3(:,1),b4(:,1)]
    reference_branch=branch_signature
    call export_maps()
    if (command=='repeat-3'.or.command=='repeat-1') then
      call export_baseline('baseline-001.bin',base,first_f)
      repeat_count=1
      if (command=='repeat-3') repeat_count=3
      do i=2,repeat_count
        call fresh(base,time,temp,density,f,ok,reason)
        if (.not.ok) call fail('diagnostic repeat '//trim(reason))
        call check_baseline_identity(f,first_f,reference_workspace,reference_branch)
        write(filename,'(a,i3.3,a)') 'baseline-',i,'.bin'
        call export_baseline(trim(filename),base,f)
      enddo
      return
    endif
    if (command/='diagnose') call fail('unknown diagnostic command')
    open(newunit=status_unit,file='matrix-status.bin',status='new',access='stream',form='unformatted')
    do i=1,4
      rhs_before=rhs_count
      call full_jacobian(base,time,temp,density,f,matrices(:,:,i),factors(i),complete(i))
      rhs_after=rhs_count
      call check_baseline_identity(f,first_f,reference_workspace,reference_branch)
      write(filename,'(a,i1,a)') 'jacobian-factor-',i,'.bin'
      call dump_matrix(trim(filename),matrices(:,:,i))
      write(status_unit) factors(i),real(jacobian_count,dp),merge(1.0_dp,0.0_dp,complete(i)), &
                         real(rhs_before,dp),real(rhs_after,dp)
      flush(status_unit)
    enddo
    close(status_unit)
    call export_baseline('baseline-001.bin',base,f)
    ! The original fixed-b monomial derivative uses the current setup coefficient
    ! workspace. It performs no fresh F, EOS or rate calculation.
    call jacobian_build(mask_in=active)
    matrix_jacobian_id=-1
    fixed_matrix=dydotdy(:,:,1)
    if (.not.all(ieee_is_finite(fixed_matrix))) call fail('nonfinite diagnostic fixed-b matrix')
    call dump_matrix('fixed-b-jacobian.bin',fixed_matrix)
    write(log_unit,'(a)') 'DIAGNOSTIC_FIXED_B_MATRIX_BUILDS 1 (not a full-F Jacobian)'
    call diagnostic_directions(base,time,temp,density,first_f,coordinate,matrices,complete)
    call check_baseline_identity(ydot(:,1),first_f,reference_workspace,reference_branch)
    if (linear_enabled) then
      do i=1,4
        if (.not.complete(i)) cycle
        call diagnostic_linear(i,matrices(:,:,i),base,old,first_f,h,deltas(:,i),linear_ok(i))
      enddo
    endif
    open(newunit=unit,file='candidate-status.txt',status='new',action='write')
    if (.not.linear_enabled) then
      write(unit,'(a)') 'SKIPPED no frozen linear state'
    elseif (.not.complete(2).or..not.linear_ok(2)) then
      write(unit,'(a)') 'SKIPPED incomplete or failed factor-one linear solve'
    else
      ! The only candidate is the unprojected factor-one Newton correction.
      f=base+deltas(:,2)
      if (.not.domain(f,temp,density,reason)) then
        write(unit,'(a)') 'REFUSED '//trim(reason)
        open(newunit=status_unit,file='candidate-refused.bin',status='new',access='stream',form='unformatted')
        write(status_unit) time,temp,density,f
        close(status_unit)
      else
        call candidate_evaluation(f,time,temp,density)
        write(unit,'(a)') 'EVALUATED'
      endif
    endif
    close(unit)
  end subroutine run_native_diagnostic

  subroutine candidate_evaluation(state,time,temp,density)
    real(dp),intent(in) :: state(160),time,temp,density
    real(dp) :: f(160)
    logical :: ok
    character(160) :: reason
    call fresh(state,time,temp,density,f,ok,reason)
    if (.not.ok) call fail('diagnostic candidate '//trim(reason))
    call export_baseline('candidate.bin',state,f)
  end subroutine candidate_evaluation

  subroutine diagnostic_directions(base,time,temp,density,f0,coordinate,matrices,complete)
    real(dp),intent(in) :: base(160),time,temp,density,f0(160),matrices(160,160,4)
    integer,intent(in) :: coordinate
    logical,intent(in) :: complete(4)
    real(dp),parameter :: multipliers(9)=[1e-2_dp,3e-3_dp,1e-3_dp,3e-4_dp,1e-4_dp, &
                                         3e-5_dp,1e-5_dp,3e-6_dp,1e-6_dp]
    integer,parameter :: stencils(3)=[0,1,-1]
    real(dp) :: v(160),scale(160),jv(160,3,4),dv(160),p1(160),p2(160),f1(160),f2(160),restore_f(160)
    real(dp) :: h1,h2,m,w1,w2,quiet_nan
    integer :: output,attempts,jout,direction,mi,k,stencil,i,base_branch(branch_size)
    logical :: ok1,ok2,found,ok
    character(160) :: why1,why2
    quiet_nan=ieee_value(0.0_dp,ieee_quiet_nan); jv=quiet_nan
    base_branch=branch_signature
    scale=max(abs(base),1e-8_dp/aa)
    open(newunit=output,file='directional.bin',status='new',access='stream',form='unformatted')
    open(newunit=attempts,file='direction-attempts.bin',status='new',access='stream',form='unformatted')
    do direction=1,3
      v=scale
      if (direction==2) then
        do i=2,160,2
          v(i)=0
        enddo
      elseif (direction==3) then
        v=0; v(coordinate)=scale(coordinate)
      endif
      do i=1,4
        if (.not.complete(i)) cycle
        jv(:,direction,i)=matmul(matrices(:,:,i),v)
        if (.not.all(ieee_is_finite(jv(:,direction,i)))) call fail('nonfinite diagnostic Jv')
      enddo
      do mi=1,9
        m=multipliers(mi); found=.false.
        do k=1,3
          stencil=stencils(k)
          select case(stencil)
          case(0)
            h1=-m; h2=m
          case(1)
            h1=m; h2=2*m
          case(-1)
            h1=-m; h2=-2*m
          end select
          p1=base+h1*v; p2=base+h2*v
          call fresh(p1,time,temp,density,f1,ok1,why1,.true.)
          if (ok1.and.any(branch_signature/=base_branch)) then
            ok1=.false.; why1='branch crossing'
          endif
          call fresh(p2,time,temp,density,f2,ok2,why2,.true.)
          if (ok2.and.any(branch_signature/=base_branch)) then
            ok2=.false.; why2='branch crossing'
          endif
          write(attempts) real(direction,dp),real(mi,dp),real(stencil,dp),h1,h2, &
                         merge(1.0_dp,0.0_dp,ok1),merge(1.0_dp,0.0_dp,ok2),p1,p2
          flush(attempts)
          if (ok1.and.ok2) then
            w1=h2/(h1*(h2-h1)); w2=-h1/(h2*(h2-h1))
            dv=w1*(f1-f0)+w2*(f2-f0)
            if (.not.all(ieee_is_finite(dv))) call fail('nonfinite independent directional quotient')
            found=.true.; exit
          endif
          write(log_unit,*) 'DIAGNOSTIC_DIRECTION_REFUSAL',direction,mi,stencil,trim(why1),' / ',trim(why2)
        enddo
        if (.not.found) then
          dv=quiet_nan; p1=quiet_nan; p2=quiet_nan; f1=quiet_nan; f2=quiet_nan
        endif
        write(output) real(direction,dp),real(mi,dp),real(stencil,dp),merge(1.0_dp,0.0_dp,found),h1,h2, &
                      v,jv(:,direction,2),dv,p1-base,p2-base,f0,f1,f2
        flush(output)
      enddo
    enddo
    call fresh(base,time,temp,density,restore_f,ok,why1)
    if (.not.ok) call fail('diagnostic directional restore '//trim(why1))
    if (.not.unchanged_real_bits(restore_f,f0)) call fail('diagnostic directional restore changed baseline F')
    close(output); close(attempts)
    open(newunit=jout,file='diagnostic-jv.bin',status='new',access='stream',form='unformatted')
    write(jout) jv
    close(jout)
  end subroutine diagnostic_directions

  subroutine diagnostic_linear(ordinal,matrix,base,old,f,h,delta,ok)
    integer,intent(in) :: ordinal
    real(dp),intent(in) :: matrix(160,160),base(160),old(160),f(160),h
    real(dp),intent(out) :: delta(160)
    logical,intent(out) :: ok
    real(dp) :: unfactored(160,160),rhs(160,1),correction(160,1),rdt(1),mult(1),dummy_rhs(1),dummy_delta(1)
    integer :: unit,lu_info(1),solve_info(1)
    logical :: active(1)
    character(40) :: filename
    active=.true.; rdt=1.0_dp/h; mult=-1.0_dp
    dydotdy(:,:,1)=matrix
    call jacobian_scale(rdt,mult,mask_in=active)
    matrix_jacobian_id=ordinal
    unfactored=jac(:,:,1)
    if (.not.all(ieee_is_finite(unfactored))) call fail('nonfinite frozen I/h-J')
    rhs(:,1)=(old-base)/h+f
    if (.not.all(ieee_is_finite(rhs))) call fail('nonfinite frozen Newton RHS')
    lu_info=-999; solve_info=-999; dummy_rhs=0; dummy_delta=0
    delta=ieee_value(0.0_dp,ieee_quiet_nan)
    correction=ieee_value(0.0_dp,ieee_quiet_nan)
    lu_count=lu_count+1
    call checkpoint()
    call jacobian_decomp(0,mask_in=active,status_out=lu_info)
    if (.not.all(ieee_is_finite(jac))) call fail('nonfinite diagnostic LU workspace')
    if (lu_info(1)==0) then
      solve_count=solve_count+1
      call checkpoint()
      call jacobian_bksub(0,rhs,correction,dummy_rhs,dummy_delta,mask_in=active,status_out=solve_info)
      if (solve_info(1)==0) then
        if (.not.all(ieee_is_finite(correction))) call fail('nonfinite diagnostic Newton correction')
        delta=correction(:,1)
      endif
    endif
    ok=lu_info(1)==0.and.solve_info(1)==0
    write(filename,'(a,i1,a)') 'linear-factor-',ordinal,'.bin'
    open(newunit=unit,file=trim(filename),status='new',access='stream',form='unformatted')
    write(unit) int(z'4352444c',int32),1_int32,160_int32,int(lu_info(1),int32),int(solve_info(1),int32)
    write(unit) h,base,old,f,unfactored,rhs,jac,delta
    write(unit) int(indx(:,1),int32)
    close(unit)
    write(log_unit,*) 'DIAGNOSTIC_LINEAR_STATUS',ordinal,lu_info(1),solve_info(1)
  end subroutine diagnostic_linear
end module diagnostic_native
