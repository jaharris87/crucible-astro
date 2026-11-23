! CRUCIBLE's original bounded numerical adaptation. No learned source is called.
module native_adapter
  use, intrinsic :: iso_fortran_env, only: int32,int64,real64
  use, intrinsic :: ieee_arithmetic
  use xnet_types, only: dp
  use nuclear_data, only: ny,aa,zz
  use xnet_abundances, only: y,yt,ydot,y_moment
  use xnet_conditions, only: tt,t9t,rhot,yet,cv,etae,detaedt9,tdel
  use xnet_controls, only: zb_lo,zb_hi,kitmx,ijac,ymin,iweak,tdel_maxmult
  use xnet_integrate, only: cross_sect,yderiv
  use xnet_jacobian, only: dydotdy,jac,jacobian_scale,jacobian_decomp,jacobian_bksub
  use actual_eos_module, only: helm_density=>d,helm_temperature=>t
  use phase2d_branch_state, only: branch_signature,branch_size,side
  implicit none
  real(dp) :: nonlinear_atol=1e-13_dp,nonlinear_rtol=1e-11_dp
  real(dp) :: final_residual(160)=0,final_norm=0,final_l1=0,final_projection=0,cumulative_projection=0
  integer :: log_unit,status_unit,column_unit,branch_unit,residual_unit,counter_unit,base_unit
  integer(int64) :: rhs_count=0,coefficient_count=0,jacobian_count=0,lu_count=0,solve_count=0,newton_count=0,retry_count=0
  integer(int64) :: projection_count=0,probe_count=0,accepted_count=0,attempt_count=0
  integer :: last_branch(branch_size)=0
  integer :: last_step=-1
  integer(int64) :: wall_start=0,wall_rate=0
  real(dp) :: cpu_start=0
  logical :: opened=.false.,runtime_saved=.false.,workspace_ready=.false.,failure_state_saved=.false.
  integer :: physical_phase=0
  ! Native retry cleanup mutates yt/tt/t9t/rhot/yet after a failed step, while
  ! F/coefficient/assembly workspaces retain their last physical evaluation.
  ! Keep its inputs and EOS outputs together without reevaluating any physics.
  real(dp) :: last_evaluated_state(160),last_evaluated_conditions(3),last_evaluated_eos(4)
  integer :: last_evaluated_iweak
  integer(int64) :: matrix_jacobian_id=0
contains
  subroutine open_diagnostics()
    call system_clock(wall_start,wall_rate)
    call cpu_time(cpu_start)
    open(newunit=log_unit,file='native.log',status='new',action='write')
    open(newunit=status_unit,file='status.txt',status='new',action='write')
    open(newunit=column_unit,file='fd-columns.bin',status='new',access='stream',form='unformatted')
    open(newunit=branch_unit,file='branch-events.bin',status='new',access='stream',form='unformatted')
    open(newunit=residual_unit,file='newton-residuals.bin',status='new',access='stream',form='unformatted')
    open(newunit=counter_unit,file='counter-events.bin',status='new',access='stream',form='unformatted')
    open(newunit=base_unit,file='jacobian-bases.bin',status='new',access='stream',form='unformatted')
    opened=.true.
    write(log_unit,*) 'WALL_START_COUNT_RATE',wall_start,wall_rate
    write(status_unit,'(a)') 'RUNNING'
    flush(status_unit)
    write(log_unit,'(a)') 'branch-events rows: call,time,index,old,new (all f64; 1-based index)'
    write(log_unit,'(a)') 'fd-columns rows: Jacobian,column,stencil,reductions,offset1,offset2 (f64)'
    write(log_unit,'(a)') 'counter-events rows: 14 int64 in counters.json key order'
    write(log_unit,'(a)') 'PROJECTION step iteration species before after signed_delta A_abs_delta'
  end subroutine open_diagnostics

  subroutine counters()
    integer :: unit
    open(newunit=unit,file='counters.json',status='new',action='write')
    write(unit,'(a)') '{'
    write(unit,'(a,i0,a)') '"rhs":',rhs_count,','
    write(unit,'(a,i0,a)') '"coefficient":',coefficient_count,','
    write(unit,'(a,i0,a)') '"eos":',coefficient_count,','
    write(unit,'(a,i0,a)') '"screening":',coefficient_count,','
    write(unit,'(a,i0,a)') '"weak":',coefficient_count,','
    write(unit,'(a,i0,a)') '"jacobian":',jacobian_count,','
    write(unit,'(a,i0,a)') '"lu":',lu_count,','
    write(unit,'(a,i0,a)') '"linear_solve":',solve_count,','
    write(unit,'(a,i0,a)') '"newton":',newton_count,','
    write(unit,'(a,i0,a)') '"retry":',retry_count,','
    write(unit,'(a,i0,a)') '"step_attempt":',attempt_count,','
    write(unit,'(a,i0,a)') '"projection":',projection_count,','
    write(unit,'(a,i0,a)') '"probe":',probe_count,','
    write(unit,'(a,i0)') '"accepted":',accepted_count
    write(unit,'(a)') '}'
    close(unit)
  end subroutine counters

  subroutine checkpoint()
    write(counter_unit) rhs_count,coefficient_count,coefficient_count,coefficient_count,coefficient_count, &
                        jacobian_count,lu_count, &
                        solve_count,newton_count,retry_count,attempt_count,projection_count,probe_count,accepted_count
    flush(counter_unit)
  end subroutine checkpoint

  subroutine snapshot_runtime()
    integer :: input,output,ios,j
    character(4096) :: line
    character(20),parameter :: sources(2)=[character(20)::'/proc/self/maps','/proc/self/status']
    character(20),parameter :: destinations(2)=[character(20)::'loaded-maps.txt','memory-status.txt']
    if (runtime_saved) return
    runtime_saved=.true.
    do j=1,2
      open(newunit=input,file=trim(sources(j)),status='old',action='read',iostat=ios)
      if (ios/=0) then
        write(log_unit,*) 'RUNTIME_SNAPSHOT_UNAVAILABLE',trim(sources(j)),ios
        cycle
      endif
      open(newunit=output,file=trim(destinations(j)),status='new',action='write',iostat=ios)
      if (ios/=0) then
        write(log_unit,*) 'RUNTIME_SNAPSHOT_WRITE_UNAVAILABLE',trim(destinations(j)),ios
        close(input)
        cycle
      endif
      do
        read(input,'(a)',iostat=ios) line
        if (ios/=0) exit
        write(output,'(a)',iostat=ios) trim(line)
        if (ios/=0) exit
      enddo
      if (ios>0) write(log_unit,*) 'RUNTIME_SNAPSHOT_PARTIAL',trim(sources(j)),ios
      close(input); close(output)
    enddo
    flush(log_unit)
  end subroutine snapshot_runtime

  subroutine elapsed_cost()
    integer(int64) :: wall_end
    real(dp) :: cpu_end
    call system_clock(wall_end)
    call cpu_time(cpu_end)
    if (wall_rate>0) then
      write(log_unit,*) 'WALL_SECONDS',real(wall_end-wall_start,dp)/real(wall_rate,dp)
    else
      write(log_unit,'(a)') 'WALL_SECONDS_UNAVAILABLE system_clock rate not positive'
    endif
    write(log_unit,*) 'TOTAL_CPU_SECONDS',cpu_end-cpu_start
  end subroutine elapsed_cost

  subroutine save_failure_state(state,time,temp,density)
    real(dp),intent(in) :: state(:),time,temp,density
    integer :: unit,ios
    if (failure_state_saved) return
    failure_state_saved=.true.
    open(newunit=unit,file='failure-state.bin',status='new',access='stream',form='unformatted',iostat=ios)
    if (ios/=0) then
      write(log_unit,*) 'FAILURE_STATE_UNAVAILABLE',ios
      return
    endif
    write(unit,iostat=ios) time,temp,density,state
    if (ios/=0) write(log_unit,*) 'FAILURE_STATE_PARTIAL',ios
    close(unit,iostat=ios)
    if (ios/=0) write(log_unit,*) 'FAILURE_STATE_CLOSE_UNAVAILABLE',ios
  end subroutine save_failure_state

  subroutine save_failure_workspace()
    use reaction_data, only: csect1,csect2,csect3,csect4,b1,b2,b3,b4
    integer :: unit,ios
    integer(int32) :: header(15)
    real(dp) :: nan
    ! The flag is set only inside fresh after driver/stub allocations are ready.
    ! Header/network/setup failures never dereference unallocated native arrays.
    if (.not.workspace_ready) then
      write(log_unit,'(a)') 'FAILURE_WORKSPACE_UNAVAILABLE physical workspaces not initialized'
      return
    endif
    if (.not.failure_state_saved) call save_failure_state(last_evaluated_state,last_evaluated_conditions(1), &
                                                       last_evaluated_conditions(2),last_evaluated_conditions(3))
    write(log_unit,*) 'FAILURE_WORKSPACE_LAST_EVALUATION',physical_phase,last_evaluated_conditions
    write(log_unit,*) 'FAILURE_WORKSPACE_JACOBIAN_BASE',matrix_jacobian_id
    header=[int(z'43524657',int32),1_int32,int(ny,int32),int(size(csect1),int32), &
            int(size(csect2),int32),int(size(csect3),int32),int(size(csect4),int32), &
            int(size(b1),int32),int(size(b2),int32),int(size(b3),int32),int(size(b4),int32), &
            int(size(jac,1),int32),int(size(jac,2),int32),int(physical_phase,int32),int(last_evaluated_iweak,int32)]
    open(newunit=unit,file='failure-workspace.bin',status='new',access='stream',form='unformatted',iostat=ios)
    if (ios/=0) then
      write(log_unit,*) 'FAILURE_WORKSPACE_UNAVAILABLE',ios
      return
    endif
    nan=ieee_value(0.0_dp,ieee_quiet_nan)
    write(unit,iostat=ios) header
    if (ios==0) write(unit,iostat=ios) last_evaluated_conditions,last_evaluated_eos,last_evaluated_state
    if (physical_phase==2) then
      if (ios==0) write(unit,iostat=ios) ydot,csect1,csect2,csect3,csect4,b1,b2,b3,b4,jac
    else
      ! Phase 1 means yderiv was never called at this state; these explicit NaNs
      ! denote unavailable current F/b, rather than invented zeros or stale data.
      if (ios==0) write(unit,iostat=ios) spread(nan,1,size(ydot)),csect1,csect2,csect3,csect4, &
                                         spread(nan,1,size(b1)+size(b2)+size(b3)+size(b4)),jac
    endif
    if (ios/=0) write(log_unit,*) 'FAILURE_WORKSPACE_PARTIAL',ios
    close(unit,iostat=ios)
    if (ios/=0) write(log_unit,*) 'FAILURE_WORKSPACE_CLOSE_UNAVAILABLE',ios
  end subroutine save_failure_workspace

  subroutine fail(reason)
    character(*), intent(in) :: reason
    if (opened) then
      call save_failure_workspace()
      call snapshot_runtime()
      call elapsed_cost()
      write(log_unit,'(a)') 'FAILURE '//reason
      write(status_unit,'(a)') 'FAILURE '//reason
      flush(log_unit); flush(status_unit); flush(column_unit); flush(branch_unit); flush(residual_unit); flush(counter_unit)
      flush(base_unit)
      call counters()
    endif
    error stop 1
  end subroutine fail

  subroutine finish()
    call snapshot_runtime()
    call counters()
    call elapsed_cost()
    write(status_unit,'(a)') 'SUCCESS'
    flush(status_unit)
    close(log_unit); close(status_unit); close(column_unit); close(branch_unit); close(residual_unit); close(counter_unit)
    close(base_unit)
  end subroutine finish

  logical function domain(state,temp,density,reason)
    real(dp), intent(in) :: state(:),temp,density
    character(*),intent(out) :: reason
    real(dp) :: baryon,charge,total,ye_native,abar,zbar,z2bar,zibar,electron_density
    domain=.false.; reason='nonfinite state/forcing'
    if (.not.all(ieee_is_finite(state))) return
    if (.not.ieee_is_finite(temp).or..not.ieee_is_finite(density)) return
    reason='abundance outside [0,1]'
    if (any(state<0).or.any(state>1)) return
    reason='temperature/density domain'
    if (temp<0.01_dp.or.temp>100.0_dp.or.density<=0) return
    baryon=sum(aa*state); charge=sum(zz*state); total=sum(state)
    reason='nonpositive or nonfinite abundance moments'
    if (.not.ieee_is_finite(baryon).or..not.ieee_is_finite(charge).or..not.ieee_is_finite(total)) return
    if (baryon<=0.or.total<=0) return
    ! Use exactly the pinned native moment convention before any EOS call.
    call y_moment(state,ye_native,total,abar,zbar,z2bar,zibar)
    if (.not.ieee_is_finite(ye_native).or.ye_native<=0) return
    electron_density=density*ye_native
    if (.not.ieee_is_finite(electron_density).or.electron_density<=0) return
    reason='FFN log10(rho*Ye) outside [1,11)'
    if (log10(electron_density)<1.0_dp.or.log10(electron_density)>=11.0_dp) return
    reason='Helmholtz initialized grid unavailable'
    if (.not.allocated(helm_density).or..not.allocated(helm_temperature)) return
    reason='outside actual initialized Helmholtz table endpoints'
    if (electron_density<helm_density(1).or.electron_density>helm_density(size(helm_density))) return
    if (temp*1e9_dp<helm_temperature(1).or.temp*1e9_dp>helm_temperature(size(helm_temperature))) return
    domain=.true.; reason='admissible'
  end function domain

  subroutine fresh(state,time,temp,density,f,ok,reason,is_probe)
    use reaction_data, only: csect1,csect2,csect3,csect4,b1,b2,b3,b4
    real(dp), intent(in) :: state(:),time,temp,density
    real(dp), intent(out) :: f(:)
    logical, intent(out) :: ok
    character(*), intent(out) :: reason
    logical, optional, intent(in) :: is_probe
    logical :: active(1),probe
    integer :: j
    real(dp), parameter :: eta_cuts(7)=[-2.0_dp,0.0_dp,2.0_dp,5.0_dp,10.0_dp,20.0_dp,40.0_dp]
    f=ieee_value(0.0_dp,ieee_quiet_nan)
    probe=.false.
    if (present(is_probe)) probe=is_probe
    if (probe) probe_count=probe_count+1
    ok=domain(state,temp,density,reason)
    if (.not.ok) then
      if (.not.probe) call save_failure_state(state,time,temp,density)
      return
    endif
    if (.not.ieee_is_finite(time)) then
      ok=.false.; reason='nonfinite time'
      if (.not.probe) call save_failure_state(state,time,temp,density)
      return
    endif
    active=.true.
    yt(:,1)=state; tt(1)=time; t9t(1)=temp; rhot(1)=density
    last_evaluated_state=state
    last_evaluated_conditions=[time,temp,density]
    ! EOS/weak outputs are captured only after cross_sect returns below.
    workspace_ready=.false.; physical_phase=1
    coefficient_count=coefficient_count+1
    call cross_sect(mask_in=active)
    last_evaluated_eos=[yet(1),cv(1),etae(1),detaedt9(1)]
    last_evaluated_iweak=iweak(1)
    workspace_ready=.true.
    ok=all(ieee_is_finite(csect1)).and.all(ieee_is_finite(csect2)) &
       .and.all(ieee_is_finite(csect3)).and.all(ieee_is_finite(csect4)) &
       .and.all(ieee_is_finite(yet)).and.all(ieee_is_finite(cv)).and.all(ieee_is_finite(etae)) &
       .and.all(ieee_is_finite(detaedt9))
    if (.not.ok) then
      reason='nonfinite computed EOS/coefficient workspace'
      call save_failure_state(state,time,temp,density)
      call fail(trim(reason))
    endif
    rhs_count=rhs_count+1; physical_phase=2
    call yderiv(mask_in=active)
    if (.not.all(ieee_is_finite(ydot)).or..not.all(ieee_is_finite(b1)).or. &
        .not.all(ieee_is_finite(b2)).or..not.all(ieee_is_finite(b3)).or..not.all(ieee_is_finite(b4))) then
      reason='nonfinite computed physical F/assembly workspace'
      call save_failure_state(state,time,temp,density)
      call fail(trim(reason))
    endif
    branch_signature(10020)=iweak(1)
    do j=1,7
      branch_signature(10026+j)=side(etae(1),eta_cuts(j))
    enddo
    do j=1,branch_size
      if (branch_signature(j)/=last_branch(j)) then
        write(branch_unit) real(rhs_count,dp),time,real(j,dp),real(last_branch(j),dp),real(branch_signature(j),dp)
      endif
    enddo
    last_branch=branch_signature
    f=ydot(:,1)
    reason='admissible'
  end subroutine fresh

  ! Three-node first derivative at the baseline. Offsets are actual representable
  ! displacements, including asymmetric rounded central and one-sided stencils.
  subroutine three_weights(x1,x2,w,ok)
    real(dp),intent(in) :: x1,x2
    real(dp),intent(out) :: w(3)
    logical,intent(out) :: ok
    ok=.false.; w=0
    if (.not.ieee_is_finite(x1).or..not.ieee_is_finite(x2)) return
    if (x1==0.or.x2==0.or.x1==x2) return
    w(1)=-(x1+x2)/(x1*x2)
    w(2)=x2/(x1*(x2-x1))
    w(3)=-x1/(x2*(x2-x1))
    ok=all(ieee_is_finite(w))
  end subroutine three_weights

  subroutine column_probe(base,time,temp,density,column,delta,stencil,base_branch,f1,f2,d1,d2,ok)
    real(dp),intent(in) :: base(:),time,temp,density,delta
    integer,intent(in) :: column,stencil,base_branch(branch_size)
    real(dp),intent(out) :: f1(:),f2(:),d1,d2
    logical,intent(out) :: ok
    real(dp) :: p1(size(base)),p2(size(base))
    logical :: ok1,ok2
    character(160) :: why1,why2
    p1=base; p2=base
    select case(stencil)
    case(0)
      p1(column)=base(column)-delta; p2(column)=base(column)+delta
    case(1)
      p1(column)=base(column)+delta; p2(column)=base(column)+2*delta
    case(-1)
      p1(column)=base(column)-delta; p2(column)=base(column)-2*delta
    end select
    ! Rounding may erase nominal perturbations. Refuse rather than divide by zero.
    d1=p1(column)-base(column); d2=p2(column)-base(column)
    if (d1==0.or.d2==0.or.d1==d2) then
      ok=.false.
      write(log_unit,*) 'FD_REFUSAL increment',jacobian_count,column,stencil,delta,d1,d2,p1(column),p2(column)
      return
    endif
    call fresh(p1,time,temp,density,f1,ok1,why1,.true.)
    if (ok1) then
      if (any(branch_signature/=base_branch)) then
        ok1=.false.; why1='branch crossing'
      endif
    endif
    call fresh(p2,time,temp,density,f2,ok2,why2,.true.)
    if (ok2) then
      if (any(branch_signature/=base_branch)) then
        ok2=.false.; why2='branch crossing'
      endif
    endif
    ok=ok1.and.ok2
    if (.not.ok) write(log_unit,*) 'FD_REFUSAL domain/branch',jacobian_count,column,stencil, &
                                          delta,d1,d2,p1(column),p2(column),trim(why1),' / ',trim(why2)
  end subroutine column_probe

  subroutine full_jacobian(base,time,temp,density,f0,matrix)
    real(dp),intent(in) :: base(:),time,temp,density
    real(dp),intent(out) :: f0(:),matrix(:,:)
    real(dp) :: delta,scale,f1(size(base)),f2(size(base)),w(3),d1,d2
    integer :: column,reduction,stencil,k,base_branch(branch_size)
    integer,parameter :: stencils(3)=[0,1,-1]
    logical :: ok,weights_ok,found
    character(160) :: reason
    jacobian_count=jacobian_count+1
    write(base_unit) real(jacobian_count,dp),time,temp,density,base
    flush(base_unit)
    call fresh(base,time,temp,density,f0,ok,reason)
    if (.not.ok) call fail('Jacobian baseline '//trim(reason))
    base_branch=branch_signature
    do column=1,size(base)
      scale=max(abs(base(column)),1e-8_dp/aa(column))
      delta=epsilon(1.0_dp)**(1.0_dp/3.0_dp)*scale
      ! If addition rounded away, the nearest successor supplies a nonzero ULP.
      if (base(column)+delta==base(column)) delta=nearest(base(column),1.0_dp)-base(column)
      found=.false.
      do reduction=0,8
        do k=1,3
          stencil=stencils(k)
          if (stencil==-1.and.base(column)+2*delta<=1.0_dp) cycle
          call column_probe(base,time,temp,density,column,delta,stencil,base_branch,f1,f2,d1,d2,ok)
          if (.not.ok) cycle
          call three_weights(d1,d2,w,weights_ok)
          if (.not.weights_ok) cycle
          ! Difference form avoids subtracting two large baseline terms.
          matrix(:,column)=w(2)*(f1-f0)+w(3)*(f2-f0)
          if (.not.all(ieee_is_finite(matrix(:,column)))) call fail('nonfinite numerical Jacobian quotient')
          write(column_unit) real(jacobian_count,dp),real(column,dp),real(stencil,dp),real(reduction,dp),d1,d2
          found=.true.; exit
        enddo
        if (found) exit
        delta=delta/2.0_dp
      enddo
      if (.not.found) call fail('no admissible same-branch finite-difference column after eight halvings')
    enddo
    ! Physical workspace restoration is a real fresh evaluation, never assignment
    ! of saved F alone: EOS, coefficients, b and ydot must all match the baseline.
    call fresh(base,time,temp,density,f0,ok,reason)
    if (.not.ok) call fail('Jacobian restore '//trim(reason))
    if (any(branch_signature/=base_branch)) call fail('Jacobian baseline branch failed restoration')
    flush(column_unit); flush(branch_unit); flush(residual_unit); flush(counter_unit)
  end subroutine full_jacobian

  subroutine adapted_step(kstep,inr)
    integer,intent(in) :: kstep
    integer,intent(inout) :: inr(zb_lo:zb_hi)
    integer :: iteration,i
    real(dp) :: old(160),iterate(160),f(160),matrix(160,160),equation(160),correction(160,1)
    real(dp) :: unused_rhs(1),unused_correction(1),rdt(1),mult(1),before,projection,weight(160)
    real(dp) :: time,temp,density,h
    logical :: active(1),ok
    character(160) :: reason
    if (inr(1)/=0) return
    if (kitmx/=30.or.ijac/=1.or.ymin/=0.or.tdel_maxmult/=2) call fail('changed BE numerical controls')
    attempt_count=attempt_count+1
    if (kstep==last_step) retry_count=retry_count+1
    last_step=kstep
    old=y(:,1); iterate=yt(:,1)
    h=tdel(1); time=tt(1); temp=t9t(1); density=rhot(1)
    if (.not.ieee_is_finite(h).or.h<=0) call fail('nonpositive/nonfinite step')
    write(log_unit,*) 'STEP_ATTEMPT',kstep,attempt_count,time,h
    active=.true.; rdt=1.0_dp/h; mult=-1.0_dp; unused_rhs=0; unused_correction=0
    do iteration=1,30
      newton_count=newton_count+1
      call full_jacobian(iterate,time,temp,density,f,matrix)
      dydotdy(:,:,1)=matrix
      call jacobian_scale(rdt,mult,mask_in=active)
      matrix_jacobian_id=jacobian_count
      if (.not.all(ieee_is_finite(jac))) call fail('nonfinite I/h-J matrix')
      lu_count=lu_count+1
      call checkpoint()
      call jacobian_decomp(kstep,mask_in=active)
      if (.not.all(ieee_is_finite(jac))) call fail('nonfinite LU factors')
      equation=(old-iterate)/h+f
      if (.not.all(ieee_is_finite(equation))) call fail('nonfinite Newton right-hand side')
      solve_count=solve_count+1
      call checkpoint()
      call jacobian_bksub(kstep,reshape(equation,[160,1]),correction,unused_rhs,unused_correction,mask_in=active)
      if (.not.all(ieee_is_finite(correction))) call fail('nonfinite Newton correction')
      iterate=iterate+correction(:,1)
      if (.not.all(ieee_is_finite(iterate))) then
        call save_failure_state(iterate,time,temp,density)
        call fail('nonfinite Newton iterate before projection')
      endif
      projection=0
      do i=1,160
        if (iterate(i)<0) then
          before=iterate(i); iterate(i)=0
          projection=projection+aa(i)*abs(before)
          projection_count=projection_count+1
          write(log_unit,*) 'PROJECTION',kstep,iteration,i,before,0.0_dp,-before,aa(i)*abs(before)
        endif
      enddo
      call fresh(iterate,time,temp,density,f,ok,reason)
      if (.not.ok) call fail('post-update '//trim(reason))
      final_residual=iterate-old-h*f
      weight=nonlinear_atol+nonlinear_rtol*max(abs(aa*old),abs(aa*iterate))
      final_norm=maxval(abs(aa*final_residual)/weight)
      final_l1=sum(abs(aa*final_residual))
      if (.not.all(ieee_is_finite(final_residual)).or..not.ieee_is_finite(final_norm) &
          .or..not.ieee_is_finite(final_l1)) call fail('nonfinite post-update residual')
      write(residual_unit) real(kstep,dp),real(iteration,dp),time,h,final_residual,final_norm,final_l1,projection
      flush(residual_unit); flush(counter_unit)
      write(log_unit,*) 'NEWTON',kstep,iteration,final_norm,final_l1,projection
      flush(log_unit)
      call checkpoint()
      if (final_norm<=1) then
        if (projection>1e-12_dp) call fail('final Newton projection exceeds per-step bound')
        if (cumulative_projection+projection>1e-10_dp) call fail('cumulative final projection exceeds bound')
        final_projection=projection
        cumulative_projection=cumulative_projection+projection
        yt(:,1)=iterate
        inr(1)=iteration
        return
      endif
    enddo
    write(log_unit,*) 'RETRY nonconvergence',kstep,time,h,final_norm
    flush(log_unit)
  end subroutine adapted_step

  subroutine directional_sweep(base,time,temp,density,coordinate)
    real(dp),intent(in) :: base(160),time,temp,density
    integer,intent(in) :: coordinate
    real(dp),parameter :: multipliers(9)=[1e-2_dp,3e-3_dp,1e-3_dp,3e-4_dp,1e-4_dp, &
                                             3e-5_dp,1e-5_dp,3e-6_dp,1e-6_dp]
    real(dp) :: f0(160),matrix(160,160),v(160),jv(160),dv(160),p1(160),p2(160),f1(160),f2(160)
    real(dp) :: h1,h2,m,scale(160),nan,w1,w2
    integer :: output,jout,direction,mi,choice,stencil,i,base_branch(branch_size)
    integer,parameter :: order(3)=[0,1,-1]
    logical :: ok,ok1,ok2,found
    character(160) :: reason1,reason2
    call full_jacobian(base,time,temp,density,f0,matrix)
    base_branch=branch_signature
    open(newunit=jout,file='jacobian.bin',status='new',access='stream',form='unformatted')
    write(jout) matrix
    close(jout)
    open(newunit=output,file='directional.bin',status='new',access='stream',form='unformatted')
    scale=max(abs(base),1e-8_dp/aa)
    nan=ieee_value(0.0_dp,ieee_quiet_nan)
    do direction=1,3
      v=scale
      if (direction==2) then
        do i=1,160
          if (mod(i,2)==0.and.base(i)>0) v(i)=-v(i)
        enddo
      else if (direction==3) then
        v=0; v(coordinate)=scale(coordinate)
      endif
      jv=matmul(matrix,v)
      if (.not.all(ieee_is_finite(jv))) call fail('nonfinite production Jv')
      do mi=1,9
        m=multipliers(mi); found=.false.
        do choice=1,3
          stencil=order(choice)
          select case(stencil)
          case(0)
            h1=-m; h2=m
          case(1)
            h1=m; h2=2*m
          case(-1)
            h1=-m; h2=-2*m
          end select
          p1=base+h1*v; p2=base+h2*v
          call fresh(p1,time,temp,density,f1,ok1,reason1,.true.)
          if (ok1) then
            if (any(branch_signature/=base_branch)) then
              ok1=.false.; reason1='branch crossing'
            endif
          endif
          call fresh(p2,time,temp,density,f2,ok2,reason2,.true.)
          if (ok2) then
            if (any(branch_signature/=base_branch)) then
              ok2=.false.; reason2='branch crossing'
            endif
          endif
          if (ok1.and.ok2) then
            ! Independent scalar directional formula; no production-weight helper.
            w1=h2/(h1*(h2-h1)); w2=-h1/(h2*(h2-h1))
            dv=w1*(f1-f0)+w2*(f2-f0)
            if (.not.all(ieee_is_finite(dv))) call fail('nonfinite diagnostic directional quotient')
            found=.true.; exit
          endif
          write(log_unit,*) 'DIRECTION_REFUSAL',direction,mi,stencil,trim(reason1),' / ',trim(reason2)
        enddo
        if (.not.found) then
          dv=nan; p1=nan; p2=nan; f1=nan; f2=nan
        endif
        write(output) real(direction,dp),real(mi,dp),real(stencil,dp),merge(1.0_dp,0.0_dp,found),h1,h2, &
                      v,jv,dv,p1-base,p2-base,f0,f1,f2
        flush(output)
      enddo
    enddo
    call fresh(base,time,temp,density,f0,ok,reason1)
    if (.not.ok) call fail('directional restore '//trim(reason1))
    close(output)
  end subroutine directional_sweep
end module native_adapter

! Called only on guarded native LAPACK failure; no source evaluation occurs here.
subroutine native_linear_failure(code,name)
  use, intrinsic :: iso_fortran_env, only: error_unit
  use native_adapter, only: fail
  implicit none
  integer,intent(in) :: code
  character(*),intent(in) :: name
  character(160) :: reason
  write(reason,'(a,a,a,i0)') 'LAPACK ',trim(name),' info=',code
  write(error_unit,'(a)') trim(reason)
  call fail(trim(reason))
end subroutine native_linear_failure
