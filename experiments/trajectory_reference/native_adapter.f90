! CRUCIBLE's original bounded numerical adaptation. No learned source is called.
module native_adapter
  use, intrinsic :: iso_fortran_env, only: int8,int32,int64,real64
  use, intrinsic :: ieee_arithmetic
  use, intrinsic :: ieee_exceptions, only: ieee_get_flag,ieee_invalid,ieee_divide_by_zero, &
                                          ieee_overflow,ieee_underflow,ieee_inexact
  use xnet_types, only: dp
  use assembly113_math, only: qp,precision_contract,assembly_modes,assemble113,write_kind_record
  use nuclear_data, only: ny,aa,zz
  use xnet_abundances, only: y,yt,ydot,y_moment
  use xnet_conditions, only: tt,t9t,rhot,yet,cv,etae,detaedt9,tdel
  use xnet_controls, only: zb_lo,zb_hi,kitmx,ijac,ymin,iweak,tdel_maxmult
  use xnet_integrate, only: cross_sect,yderiv
  use xnet_jacobian, only: dydotdy,jac,jacobian_scale,jacobian_decomp,jacobian_bksub,indx
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
  logical :: evaluation_stream_enabled=.false.
  integer :: evaluation_unit,ieee_unit,fd_attempt_unit
  logical :: assembly_enabled=.false.,assembly_math_ok=.false.
  integer :: assembly_eval_unit,assembly_newton_unit,assembly_attempt_unit,assembly_ieee_unit,assembly_role=1
  integer(int64) :: assembly_context=1,fresh_requests=0,assembly_calls=0,last_assembly_call=0,last_jacobian_call=0
  real(dp) :: last_original_rhs(160),last_variant_rhs(160)
  real(qp) :: aq_totals(160),aq_classes(4,160),aq_absolute(160)
  real(qp),allocatable :: aq_products(:),aq_running(:)
  integer(int64) :: assembly_original_before(5),assembly_original_after(5)
  integer :: aq_lo(4,160),aq_hi(4,160),aq_parts(4,6794)
  integer(int64) :: an_ids(10)
  integer(int32) :: an_pivots(160)
  real(dp) :: an_scalars(8),an_old(160),an_pre(160),an_fv(160),an_fo(160),an_j(160,160),an_m(160,160)
  real(dp) :: an_rhs(160),an_lu(160,160),an_delta(160),an_unprojected(160),an_post(160)
  real(dp) :: an_weights(160),an_residual(160),an_projection(160)
contains
  subroutine enable_assembly_source()
    use reaction_data, only: b1,b2,b3,b4,la,le,n11,n21,n22,n31,n32,n33,n41,n42,n43,n44
    integer :: offsets(4),counts(4),o
    logical :: ok
    character(160) :: reason
    call precision_contract(ok,reason)
    if (.not.ok) call fail('assembly precision contract '//trim(reason))
    call write_kind_record()
    counts=[size(b1),size(b2),size(b3),size(b4)]
    if (ny/=160.or.any(counts/=[1862,4860,53,19])) call fail('assembly native map dimensions')
    offsets=[0,counts(1),sum(counts(1:2)),sum(counts(1:3))]
    allocate(aq_products(sum(counts)),aq_running(sum(counts)))
    aq_parts=1
    do o=1,4
      aq_lo(o,:)=la(o,:)+offsets(o); aq_hi(o,:)=le(o,:)+offsets(o)
    enddo
    aq_parts(1,1:1862)=n11
    aq_parts(1,1863:6722)=n21; aq_parts(2,1863:6722)=n22
    aq_parts(1,6723:6775)=n31; aq_parts(2,6723:6775)=n32; aq_parts(3,6723:6775)=n33
    aq_parts(1,6776:6794)=n41; aq_parts(2,6776:6794)=n42
    aq_parts(3,6776:6794)=n43; aq_parts(4,6776:6794)=n44
    open(newunit=assembly_eval_unit,file='assembly-evaluations.bin',status='new',access='stream',form='unformatted')
    write(assembly_eval_unit) int(z'43524145',int32),1_int32,160_int32,496_int32,0_int32,0_int32,0_int32,0_int32
    open(newunit=assembly_newton_unit,file='assembly-newton.bin',status='new',access='stream',form='unformatted')
    write(assembly_newton_unit) int(z'4352414e',int32),1_int32,160_int32,78568_int32,10_int32,160_int32,0_int32,0_int32
    open(newunit=assembly_attempt_unit,file='native-step-attempts.bin',status='new',access='stream',form='unformatted')
    write(assembly_attempt_unit) int(z'43524154',int32),1_int32,7_int32,0_int32
    open(newunit=assembly_ieee_unit,file='assembly-ieee.bin',status='new',access='stream',form='unformatted')
    write(assembly_ieee_unit) int(z'43524149',int32),1_int32,21_int32,0_int32
    assembly_enabled=.true.
    assembly_role=1; assembly_context=1
  end subroutine enable_assembly_source

  subroutine evaluate_assembly_source()
    use reaction_data, only: b1,b2,b3,b4
    integer :: before_nearest,after_nearest,before_gradual,after_gradual
    logical :: flags_before(5),flags_after(5)
    character(160) :: reason
    last_original_rhs=ydot(:,1); last_assembly_call=rhs_count; assembly_math_ok=.false.
    last_variant_rhs=ieee_value(0.0_dp,ieee_quiet_nan)
    aq_totals=ieee_value(0.0_qp,ieee_quiet_nan); aq_classes=aq_totals(1)
    aq_products=aq_totals(1); aq_running=aq_totals(1); aq_absolute=aq_totals(1)
    call assembly_modes(before_nearest,before_gradual)
    if (before_nearest/=1.or.before_gradual/=1) call fail('assembly arithmetic mode before evaluation')
    call ieee_get_flag([ieee_invalid,ieee_divide_by_zero,ieee_overflow,ieee_underflow,ieee_inexact],flags_before)
    call assemble113(last_evaluated_state,[b1(:,1),b2(:,1),b3(:,1),b4(:,1)],aq_lo,aq_hi,aq_parts, &
                     last_variant_rhs,aq_totals,aq_classes,aq_products,aq_running,aq_absolute,assembly_math_ok,reason)
    call ieee_get_flag([ieee_invalid,ieee_divide_by_zero,ieee_overflow,ieee_underflow,ieee_inexact],flags_after)
    write(assembly_ieee_unit) rhs_count,assembly_original_before,assembly_original_after, &
      merge(1_int64,0_int64,flags_before),merge(1_int64,0_int64,flags_after)
    flush(assembly_ieee_unit)
    if (.not.assembly_math_ok) call fail('assembly arithmetic '//trim(reason))
    call assembly_modes(after_nearest,after_gradual)
    if (after_nearest/=1.or.after_gradual/=1) call fail('assembly arithmetic mode after evaluation')
    assembly_calls=assembly_calls+1
    write(assembly_eval_unit) real(rhs_count,dp),real(assembly_role,dp),real(assembly_context,dp), &
      last_evaluated_conditions,sum(aa*last_evaluated_state),sum(zz*last_evaluated_state),last_evaluated_eos, &
      real(before_nearest,dp),real(after_nearest,dp),real(before_gradual,dp),real(after_gradual,dp), &
      last_evaluated_state,last_original_rhs,last_variant_rhs
    flush(assembly_eval_unit)
    ydot(:,1)=last_variant_rhs
  end subroutine evaluate_assembly_source

  subroutine save_assembly_workspace(original_filename,assembly_filename)
    use reaction_data, only: csect1,csect2,csect3,csect4,b1,b2,b3,b4
    character(*),intent(in) :: original_filename,assembly_filename
    integer :: unit,ios
    integer(int32) :: original_header(12),assembly_header(9)
    if (.not.assembly_enabled.or..not.workspace_ready) return
    if (physical_phase/=2) then
      write(log_unit,*) 'ASSEMBLY_WORKSPACE_UNAVAILABLE original RHS incomplete',physical_phase, &
                        coefficient_count,rhs_count,last_assembly_call
      return
    endif
    ! A failure before postassembly cannot reuse a preceding call's quad result.
    if (last_assembly_call/=rhs_count) then
      last_assembly_call=rhs_count; last_original_rhs=ydot(:,1); assembly_math_ok=.false.
      last_variant_rhs=ieee_value(0.0_dp,ieee_quiet_nan)
      aq_totals=ieee_value(0.0_qp,ieee_quiet_nan); aq_classes=aq_totals(1)
      aq_products=aq_totals(1); aq_running=aq_totals(1); aq_absolute=aq_totals(1)
    endif
    original_header=[int(z'43524442',int32),1_int32,160_int32,int(size(csect1),int32),int(size(csect2),int32), &
      int(size(csect3),int32),int(size(csect4),int32),int(size(b1),int32),int(size(b2),int32), &
      int(size(b3),int32),int(size(b4),int32),int(branch_size,int32)]
    open(newunit=unit,file=original_filename,status='new',access='stream',form='unformatted',iostat=ios)
    if (ios==0) then
      write(unit,iostat=ios) original_header
      if (ios==0) write(unit,iostat=ios) real(last_assembly_call,dp),last_evaluated_conditions, &
        sum(aa*last_evaluated_state),sum(zz*last_evaluated_state),last_evaluated_eos, &
        last_evaluated_state,last_original_rhs,csect1,csect2,csect3,csect4,b1,b2,b3,b4
      if (ios==0) write(unit,iostat=ios) int(branch_signature,int32)
      close(unit,iostat=ios)
    endif
    if (ios/=0) write(log_unit,*) 'ASSEMBLY_ORIGINAL_WORKSPACE_UNAVAILABLE',ios
    assembly_header=[int(z'43524157',int32),1_int32,160_int32,int(size(b1),int32),int(size(b2),int32), &
      int(size(b3),int32),int(size(b4),int32),int(160+640+2*size(aq_products)+160,int32), &
      merge(1_int32,0_int32,assembly_math_ok)]
    open(newunit=unit,file=assembly_filename,status='new',access='stream',form='unformatted',iostat=ios)
    if (ios==0) then
      write(unit,iostat=ios) assembly_header
      if (ios==0) write(unit,iostat=ios) real(last_assembly_call,dp),last_evaluated_conditions, &
        sum(aa*last_evaluated_state),sum(zz*last_evaluated_state),last_evaluated_eos, &
        last_evaluated_state,last_original_rhs,last_variant_rhs
      if (ios==0) write(unit,iostat=ios) aq_totals,aq_classes,aq_products,aq_running,aq_absolute
      close(unit,iostat=ios)
    endif
    if (ios/=0) write(log_unit,*) 'ASSEMBLY_QUAD_WORKSPACE_UNAVAILABLE',ios
  end subroutine save_assembly_workspace

  subroutine begin_assembly_newton(step,iteration,old,pre,time,h)
    integer,intent(in) :: step,iteration
    real(dp),intent(in) :: old(160),pre(160),time,h
    real(dp) :: unavailable
    unavailable=ieee_value(0.0_dp,ieee_quiet_nan)
    an_ids=[newton_count,int(step,int64),int(iteration,int64),0_int64,0_int64,0_int64,0_int64, &
            -999_int64,-999_int64,0_int64]
    an_scalars=[time,h,unavailable,unavailable,unavailable,cumulative_projection,nonlinear_atol,nonlinear_rtol]
    an_old=old; an_pre=pre; an_fv=unavailable; an_fo=unavailable; an_j=unavailable; an_m=unavailable
    an_rhs=unavailable; an_lu=unavailable; an_delta=unavailable; an_unprojected=unavailable
    an_post=unavailable; an_weights=unavailable; an_residual=unavailable; an_projection=unavailable; an_pivots=0
  end subroutine begin_assembly_newton

  subroutine write_assembly_newton(phase)
    integer,intent(in) :: phase
    an_ids(10)=phase
    write(assembly_newton_unit) an_ids,an_scalars,an_old,an_pre,an_fv,an_fo,an_j,an_m,an_rhs,an_lu, &
      an_delta,an_unprojected,an_post,an_weights,an_residual,an_projection,an_pivots
    flush(assembly_newton_unit)
  end subroutine write_assembly_newton

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

  subroutine enable_evaluation_stream()
    open(newunit=evaluation_unit,file='diagnostic-evaluations.bin',status='new',access='stream',form='unformatted')
    open(newunit=ieee_unit,file='diagnostic-ieee.bin',status='new',access='stream',form='unformatted')
    open(newunit=fd_attempt_unit,file='fd-probe-attempts.bin',status='new',access='stream',form='unformatted')
    evaluation_stream_enabled=.true.
  end subroutine enable_evaluation_stream

  subroutine observe_ieee(nearest_flag,gradual_flag,supported_flag)
    integer(int64),intent(out) :: nearest_flag,gradual_flag,supported_flag
    type(ieee_round_type) :: rounding
    logical :: gradual
    call ieee_get_rounding_mode(rounding)
    nearest_flag=merge(1_int64,0_int64,rounding==ieee_nearest)
    supported_flag=merge(1_int64,0_int64,ieee_support_underflow_control())
    gradual_flag=-1
    if (supported_flag==1) then
      call ieee_get_underflow_mode(gradual)
      gradual_flag=merge(1_int64,0_int64,gradual)
    endif
  end subroutine observe_ieee

  logical function unchanged_real_bits(left,right)
    real(dp),intent(in) :: left(:),right(:)
    integer :: j
    unchanged_real_bits=.false.
    if (size(left)/=size(right)) return
    do j=1,size(left)
      if (transfer(left(j),0_int64)/=transfer(right(j),0_int64)) return
    enddo
    unchanged_real_bits=.true.
  end function unchanged_real_bits

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
    if (assembly_enabled) then
      open(newunit=unit,file='assembly-counters.json',status='new',action='write')
      write(unit,'(a)') '{"schema":"crucible.assembly-counters.v1",'
      write(unit,'(a,i0,a)') '"fresh_requests":',fresh_requests,','
      write(unit,'(a,i0,a)') '"rhs":',rhs_count,','
      write(unit,'(a,i0,a)') '"assembly_calls":',assembly_calls,'}'
      close(unit)
    endif
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
      if (assembly_enabled) call save_assembly_workspace('baseline-failure.bin','assembly-failure.bin')
      call save_failure_workspace()
      call snapshot_runtime()
      call elapsed_cost()
      write(log_unit,'(a)') 'FAILURE '//reason
      write(status_unit,'(a)') 'FAILURE '//reason
      flush(log_unit); flush(status_unit); flush(column_unit); flush(branch_unit); flush(residual_unit); flush(counter_unit)
      flush(base_unit)
      if (evaluation_stream_enabled) then
        flush(evaluation_unit); flush(ieee_unit); flush(fd_attempt_unit)
      endif
      if (assembly_enabled) then
        flush(assembly_eval_unit); flush(assembly_newton_unit); flush(assembly_attempt_unit); flush(assembly_ieee_unit)
      endif
      call counters()
    endif
    error stop 1
  end subroutine fail

  subroutine finish()
    call snapshot_runtime()
    call counters()
    call elapsed_cost()
    if (evaluation_stream_enabled) then
      close(evaluation_unit); close(ieee_unit); close(fd_attempt_unit)
    endif
    if (assembly_enabled) then
      close(assembly_eval_unit); close(assembly_newton_unit); close(assembly_attempt_unit); close(assembly_ieee_unit)
    endif
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
    integer :: j,mutation_unit,mutation_ios
    integer(int64) :: nearest_before,nearest_after,gradual_before,gradual_after,support_before,support_after
    logical :: flags(5)
    real(dp), parameter :: eta_cuts(7)=[-2.0_dp,0.0_dp,2.0_dp,5.0_dp,10.0_dp,20.0_dp,40.0_dp]
    if (assembly_enabled) fresh_requests=fresh_requests+1
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
    if (evaluation_stream_enabled) then
      call observe_ieee(nearest_before,gradual_before,support_before)
      if (nearest_before/=1) call fail('diagnostic requires IEEE nearest rounding')
      if (assembly_enabled) then
        call ieee_get_flag([ieee_invalid,ieee_divide_by_zero,ieee_overflow,ieee_underflow,ieee_inexact],flags)
        assembly_original_before=merge(1_int64,0_int64,flags)
      endif
    endif
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
    if (evaluation_stream_enabled) then
      call observe_ieee(nearest_after,gradual_after,support_after)
      call ieee_get_flag([ieee_invalid,ieee_divide_by_zero,ieee_overflow,ieee_underflow,ieee_inexact],flags)
      if (assembly_enabled) assembly_original_after=merge(1_int64,0_int64,flags)
      write(ieee_unit) rhs_count,nearest_before,nearest_after,support_after,gradual_before,gradual_after, &
                       merge(1_int64,0_int64,flags)
      flush(ieee_unit)
      if (nearest_after/=1.or.support_before/=support_after.or.gradual_before/=gradual_after) &
        call fail('diagnostic IEEE mode changed')
      if (.not.unchanged_real_bits(state,yt(:,1)).or. &
          .not.unchanged_real_bits([time,temp,density],[tt(1),t9t(1),rhot(1)])) then
        open(newunit=mutation_unit,file='diagnostic-input-mutation.bin',status='new', &
             access='stream',form='unformatted',iostat=mutation_ios)
        if (mutation_ios==0) then
          write(mutation_unit,iostat=mutation_ios) time,temp,density,state,tt(1),t9t(1),rhot(1),yt(:,1)
          close(mutation_unit,iostat=mutation_ios)
        endif
        if (mutation_ios/=0) write(log_unit,*) 'DIAGNOSTIC_MUTATION_SNAPSHOT_UNAVAILABLE',mutation_ios
        call fail('diagnostic physical evaluation mutated supplied input')
      endif
      write(evaluation_unit) real(rhs_count,dp),time,temp,density,state,ydot(:,1)
      flush(evaluation_unit)
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
    if (assembly_enabled) call evaluate_assembly_source()
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
    integer(int64) :: probe_id1,probe_id2,count_before
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
      if (evaluation_stream_enabled) write(fd_attempt_unit) real(jacobian_count,dp),real(column,dp),real(stencil,dp), &
                                                    delta,d1,d2,p1(column),p2(column),0.0_dp,0.0_dp,0.0_dp,0.0_dp
      return
    endif
    probe_id1=0; probe_id2=0; count_before=rhs_count
    if (assembly_enabled) then
      assembly_role=4; assembly_context=jacobian_count
    endif
    call fresh(p1,time,temp,density,f1,ok1,why1,.true.)
    if (rhs_count>count_before) probe_id1=rhs_count
    if (ok1) then
      if (any(branch_signature/=base_branch)) then
        ok1=.false.; why1='branch crossing'
      endif
    endif
    count_before=rhs_count
    if (assembly_enabled) assembly_role=5
    call fresh(p2,time,temp,density,f2,ok2,why2,.true.)
    if (rhs_count>count_before) probe_id2=rhs_count
    if (ok2) then
      if (any(branch_signature/=base_branch)) then
        ok2=.false.; why2='branch crossing'
      endif
    endif
    ok=ok1.and.ok2
    if (evaluation_stream_enabled) then
      write(fd_attempt_unit) real(jacobian_count,dp),real(column,dp),real(stencil,dp),delta,d1,d2, &
                             p1(column),p2(column),merge(1.0_dp,0.0_dp,ok1),merge(1.0_dp,0.0_dp,ok2), &
                             real(probe_id1,dp),real(probe_id2,dp)
      flush(fd_attempt_unit)
    endif
    if (.not.ok) write(log_unit,*) 'FD_REFUSAL domain/branch',jacobian_count,column,stencil, &
                                          delta,d1,d2,p1(column),p2(column),trim(why1),' / ',trim(why2)
  end subroutine column_probe

  subroutine full_jacobian(base,time,temp,density,f0,matrix,increment_factor,complete)
    real(dp),intent(in) :: base(:),time,temp,density
    real(dp),intent(out) :: f0(:),matrix(:,:)
    real(dp),optional,intent(in) :: increment_factor
    logical,optional,intent(out) :: complete
    real(dp) :: delta,scale,f1(size(base)),f2(size(base)),w(3),d1,d2
    integer :: column,reduction,stencil,k,base_branch(branch_size)
    integer,parameter :: stencils(3)=[0,1,-1]
    logical :: ok,weights_ok,found
    character(160) :: reason
    if (present(complete)) then
      complete=.true.
      matrix=ieee_value(0.0_dp,ieee_quiet_nan)
    endif
    if (present(increment_factor)) then
      if (.not.any(increment_factor==[0.1_dp,1.0_dp,10.0_dp,100.0_dp])) call fail('undeclared diagnostic increment factor')
    endif
    jacobian_count=jacobian_count+1
    write(base_unit) real(jacobian_count,dp),time,temp,density,base
    flush(base_unit)
    if (assembly_enabled) then
      assembly_role=3; assembly_context=jacobian_count
    endif
    call fresh(base,time,temp,density,f0,ok,reason)
    if (assembly_enabled) last_jacobian_call=rhs_count
    if (.not.ok) call fail('Jacobian baseline '//trim(reason))
    base_branch=branch_signature
    do column=1,size(base)
      scale=max(abs(base(column)),1e-8_dp/aa(column))
      delta=epsilon(1.0_dp)**(1.0_dp/3.0_dp)*scale
      if (present(increment_factor)) delta=delta*increment_factor
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
      if (.not.found) then
        if (present(complete)) then
          complete=.false.
          write(log_unit,*) 'DIAGNOSTIC_COLUMN_INCOMPLETE',jacobian_count,column
        else
          call fail('no admissible same-branch finite-difference column after eight halvings')
        endif
      endif
    enddo
    ! Physical workspace restoration is a real fresh evaluation, never assignment
    ! of saved F alone: EOS, coefficients, b and ydot must all match the baseline.
    if (assembly_enabled) then
      assembly_role=6; assembly_context=jacobian_count
    endif
    call fresh(base,time,temp,density,f0,ok,reason)
    if (.not.ok) call fail('Jacobian restore '//trim(reason))
    if (any(branch_signature/=base_branch)) call fail('Jacobian baseline branch failed restoration')
    flush(column_unit); flush(branch_unit); flush(residual_unit); flush(counter_unit)
  end subroutine full_jacobian

  subroutine adapted_step(kstep,inr)
    integer,intent(in) :: kstep
    integer,intent(inout) :: inr(zb_lo:zb_hi)
    integer :: iteration,i,lu_info(1),solve_info(1)
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
    if (assembly_enabled) then
      write(assembly_attempt_unit) real(kstep,dp),real(attempt_count,dp),time,h,temp,density,real(rhs_count,dp)
      flush(assembly_attempt_unit)
    endif
    active=.true.; rdt=1.0_dp/h; mult=-1.0_dp; unused_rhs=0; unused_correction=0
    do iteration=1,30
      newton_count=newton_count+1
      if (assembly_enabled) call begin_assembly_newton(kstep,iteration,old,iterate,time,h)
      call full_jacobian(iterate,time,temp,density,f,matrix)
      if (assembly_enabled) then
        an_j=matrix; an_fv=f; an_fo=last_original_rhs
        an_ids(4:6)=[jacobian_count,last_jacobian_call,rhs_count]
      endif
      dydotdy(:,:,1)=matrix
      call jacobian_scale(rdt,mult,mask_in=active)
      matrix_jacobian_id=jacobian_count
      if (assembly_enabled) then
        an_m=jac(:,:,1)
        call write_assembly_newton(1)
      endif
      if (.not.all(ieee_is_finite(jac))) call fail('nonfinite I/h-J matrix')
      lu_count=lu_count+1
      call checkpoint()
      if (assembly_enabled) then
        lu_info=-999
        call jacobian_decomp(kstep,mask_in=active,status_out=lu_info)
        an_lu=jac(:,:,1); an_pivots=int(indx(:,1),int32); an_ids(8)=lu_info(1)
        if (lu_info(1)/=0) then
          call write_assembly_newton(2)
          call fail('assembly native factorization info /= 0')
        endif
      else
        call jacobian_decomp(kstep,mask_in=active)
      endif
      if (.not.all(ieee_is_finite(jac))) then
        if (assembly_enabled) call write_assembly_newton(2)
        call fail('nonfinite LU factors')
      endif
      equation=(old-iterate)/h+f
      if (assembly_enabled) then
        an_rhs=equation
        call write_assembly_newton(2)
      endif
      if (.not.all(ieee_is_finite(equation))) call fail('nonfinite Newton right-hand side')
      solve_count=solve_count+1
      call checkpoint()
      if (assembly_enabled) then
        solve_info=-999; correction=ieee_value(0.0_dp,ieee_quiet_nan)
        call jacobian_bksub(kstep,reshape(equation,[160,1]),correction,unused_rhs,unused_correction, &
                            mask_in=active,status_out=solve_info)
        an_ids(9)=solve_info(1)
        if (solve_info(1)/=0) then
          call write_assembly_newton(3)
          call fail('assembly native linear solve info /= 0')
        endif
        an_delta=correction(:,1)
      else
        call jacobian_bksub(kstep,reshape(equation,[160,1]),correction,unused_rhs,unused_correction,mask_in=active)
      endif
      if (.not.all(ieee_is_finite(correction))) then
        if (assembly_enabled) call write_assembly_newton(3)
        call fail('nonfinite Newton correction')
      endif
      iterate=iterate+correction(:,1)
      if (assembly_enabled) an_unprojected=iterate
      if (.not.all(ieee_is_finite(iterate))) then
        call save_failure_state(iterate,time,temp,density)
        if (assembly_enabled) call write_assembly_newton(3)
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
      if (assembly_enabled) then
        an_post=iterate; an_projection=iterate-an_unprojected; an_scalars(5)=projection
        call write_assembly_newton(3)
        assembly_role=10; assembly_context=newton_count
      endif
      call fresh(iterate,time,temp,density,f,ok,reason)
      if (.not.ok) call fail('post-update '//trim(reason))
      final_residual=iterate-old-h*f
      weight=nonlinear_atol+nonlinear_rtol*max(abs(aa*old),abs(aa*iterate))
      final_norm=maxval(abs(aa*final_residual)/weight)
      final_l1=sum(abs(aa*final_residual))
      if (assembly_enabled) then
        an_ids(7)=rhs_count; an_weights=weight; an_residual=final_residual
        an_scalars(3:4)=[final_norm,final_l1]
        call write_assembly_newton(4)
      endif
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
