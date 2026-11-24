! Uses the actual numerical adapter with a small independent mathematical oracle.
program synthetic_native
  use, intrinsic :: iso_fortran_env, only: int32,int64
  use, intrinsic :: ieee_arithmetic
  use native_adapter
  use xnet_integrate, only: synthetic_case
  use xnet_jacobian, only: force_bad_lu
  implicit none
  character(32) :: scenario
  character(160) :: reason
  real(dp) :: state(160),f(160),matrix(160,160),w(3),derivative,exact,original(160),nan
  real(dp),parameter :: offsets(2,3)=reshape([-0.001_dp,0.003_dp, &
                                            0.002_dp,0.005_dp,-0.004_dp,-0.007_dp],[2,3])
  logical :: ok
  integer :: k,inr(1),trial,unit
  integer(int32) :: workspace_header(15)
  real(dp) :: evaluated(160),expected_f(160),expected_conditions(3),expected_eos(4)
  real(dp) :: saved_state(163),saved_workspace(327),initial_ye
  real(dp) :: previous(160),delta(160),weights(160),current,prior,rounded(160)
  real(qp) :: exact_stiff
  integer(int64) :: before_newton
  call get_command_argument(1,scenario)
  call open_diagnostics()
  allocate(helm_density(2),helm_temperature(2))
  helm_density=[1e-12_dp,1e15_dp]; helm_temperature=[1e3_dp,1e13_dp]
  state=0; state(1)=0.5_dp; state(2)=0.25_dp
  y(:,1)=state; yt=y; original=state
  select case(trim(scenario))
  case('correction-nonlinear')
    correction_enabled=.true.; inr=0
    call adapted_step(1,inr)
    exact=1.0_dp/(1.0_dp+sqrt(21.0_dp))
    if (inr(1)<2.or.abs(yt(1,1)-exact)>1e-13_dp) call fail('correction nonlinear exact root')
    if (abs(sum(yt(:,1))-0.75_dp)>1e-12_dp) call fail('correction nonlinear inventory')
    if (current_ratio>1.or.previous_ratio>1) call fail('correction nonlinear consecutive pair')
  case('correction-stiff')
    correction_enabled=.true.; synthetic_case=3; inr=0
    exact_stiff=(real(original(1),qp)+real(tdel(1),qp)*real(1e20_dp,qp)*real(1.0_dp/3.0_dp,qp)) &
      /(1.0_qp+real(tdel(1),qp)*real(1e20_dp,qp))
    call adapted_step(1,inr)
    if (inr(1)<2) call fail('correction stiff did not accept consecutive pair')
    if (abs(real(yt(1,1),qp)-exact_stiff)>real(spacing(yt(1,1)),qp)) call fail('correction stiff BE oracle')
    if (final_norm<=1) call fail('correction stiff fixture lacks residual rounding floor')
    if (current_ratio>1.or.previous_ratio>1) call fail('correction stiff raw pair')
  case('correction-rounded')
    correction_enabled=.true.; correction_atol=1e-20_dp; correction_rtol=0
    synthetic_case=4; inr=0
    call adapted_step(1,inr)
    if (inr(1)/=0.or.newton_count/=30) call fail('rounded applied update manufactured convergence')
    if (.not.unchanged_real_bits(yt(:,1),original)) call fail('rounded fixture did not stagnate')
    if (current_ratio<=1) call fail('rounded fixture raw correction not detected')
  case('correction-current')
    ! Both corrections must use current weights, not weights at the prior state.
    delta=0; previous=0; rounded=original
    rounded(1)=0.01_dp; state(1)=0.01_dp
    previous(1)=1e-3_dp; delta(1)=1e-6_dp
    call correction_norms(state,rounded,delta,previous,1e-8_dp,1e-2_dp,weights,current,prior)
    if (current>=1.or.prior<=1) call fail('current weights did not reject previous correction')
    if (abs(prior-1e-3_dp/(1e-8_dp+1e-4_dp))>1e-12_dp) call fail('current weights numeric oracle')
    call correction_norms(original,original,delta,previous,1e-8_dp,1e-2_dp,weights,current,prior)
    if (prior>=1) call fail('fixture does not distinguish stale previous weights')
    call correction_wire_fixture()
  case('correction-retry')
    correction_enabled=.true.; correction_atol=1e-20_dp; correction_rtol=0
    synthetic_case=4; inr=0
    call adapted_step(1,inr)
    if (inr(1)/=0) call fail('retry setup unexpectedly converged')
    synthetic_case=5; yt=y; inr=0; before_newton=newton_count
    call adapted_step(1,inr)
    if (inr(1)/=2.or.newton_count-before_newton/=2.or.retry_count/=1) call fail('retry correction history reset')
    if (current_ratio/=0.or.previous_ratio/=0) call fail('retry history retained failed correction')
  case('correction-projection')
    correction_enabled=.true.; synthetic_case=1; inr=0
    call adapted_step(1,inr)
    if (inr(1)/=0.or.projection_count==0.or.current_ratio<=1) call fail('correction projection false convergence')
  case('correction-projection-bound')
    correction_enabled=.true.; correction_atol=1.0_dp; correction_rtol=0
    synthetic_case=1; inr=0
    call adapted_step(1,inr)
    call fail('UNEXPECTED excessive final projection accepted')
  case('correction-incomplete')
    call require_complete_horizon(0.005_dp)
    call fail('UNEXPECTED incomplete horizon accepted')
  case('polynomial')
    do k=1,3
      call three_weights(offsets(1,k),offsets(2,k),w,ok)
      if (.not.ok) call fail('synthetic polynomial weights rejected')
      ! Independent exact derivative of p(x)=3+7x+11x^2 at x=0 is seven.
      derivative=w(1)*3+w(2)*(3+7*offsets(1,k)+11*offsets(1,k)**2) &
                             +w(3)*(3+7*offsets(2,k)+11*offsets(2,k)**2)
      if (abs(derivative-7)>1e-10_dp) call fail('polynomial derivative oracle')
    enddo
    call three_weights(0.0_dp,1.0_dp,w,ok)
    if (ok) call fail('zero offset accepted')
    call three_weights(1.0_dp,1.0_dp,w,ok)
    if (ok) call fail('duplicate offset accepted')
    call full_jacobian(state,0.0_dp,1.0_dp,100.0_dp,f,matrix)
    if (abs(matrix(1,1)+1000)>1e-5_dp.or.abs(matrix(2,1)-1000)>1e-5_dp) &
      call fail('nonlinear full-J exact derivative oracle')
    matrix(1:2,1)=0
    if (maxval(abs(matrix))>1e-5_dp) call fail('nonlinear full-J cross-column oracle')
  case('nonlinear')
    inr=0
    call adapted_step(1,inr)
    if (inr(1)<=0) call fail('nonlinear stiff BE failed to converge')
    ! Solve 10*x^2+x-0.5=0 independently and stably.
    exact=1.0_dp/(1.0_dp+sqrt(21.0_dp))
    if (abs(yt(1,1)-exact)>1e-12_dp) call fail('nonlinear stiff BE exact root')
    if (abs(sum(yt(:,1))-0.75_dp)>1e-12_dp) call fail('nonunit inventory conservation')
    if (abs(yt(2,1)-(0.75_dp-exact))>1e-12_dp) call fail('nonlinear second component')
    if (final_norm>1.or.newton_count<=1.or.final_projection/=0) call fail('nonlinear convergence evidence')
  case('boundary')
    if (.not.domain(state,0.01_dp,100.0_dp,reason)) call fail('lower valid temperature rejected')
    if (.not.domain(state,100.0_dp,100.0_dp,reason)) call fail('upper valid temperature rejected')
    if (domain(state,0.009_dp,100.0_dp,reason)) call fail('low temperature accepted')
    if (domain(state,1.0_dp,1e11_dp,reason)) call fail('upper FFN density boundary accepted')
    state(1)=-1e-20_dp
    if (domain(state,1.0_dp,100.0_dp,reason)) call fail('negative abundance accepted')
    state=original; state(1)=1.0001_dp
    if (domain(state,1.0_dp,100.0_dp,reason)) call fail('upper abundance bound accepted')
    state=original; nan=ieee_value(0.0_dp,ieee_quiet_nan); state(1)=nan
    if (domain(state,1.0_dp,100.0_dp,reason)) call fail('NaN abundance accepted')
    state=0
    if (domain(state,1.0_dp,100.0_dp,reason)) call fail('zero inventory accepted')
  case('projection')
    synthetic_case=1; inr=0
    call adapted_step(1,inr)
    if (inr(1)/=0) call fail('projection manufactured a converged root')
    if (final_norm<=1.or.projection_count==0) call fail('projection refusal lacks evidence')
  case('retry-snapshot')
    ! Exercise retained evaluation/F association through all ten native-style
    ! failed-retry resets. No original producer or extra source is called here.
    zz(2)=0.5_dp
    initial_ye=sum(zz*original)/sum(aa*original)
    do trial=1,10
      evaluated=original
      evaluated(1)=original(1)-0.01_dp*trial
      evaluated(2)=original(2)+0.01_dp*trial
      expected_conditions=[1e-4_dp/2.0_dp**(trial-1),1.0_dp+0.01_dp*trial,100.0_dp+trial]
      call fresh(evaluated,expected_conditions(1),expected_conditions(2),expected_conditions(3),f,ok,reason)
      if (.not.ok) call fail('retry snapshot synthetic evaluation refused')
      expected_f=f
      expected_eos=[sum(zz*evaluated)/sum(aa*evaluated),1.0_dp,1.0_dp,0.0_dp]
      ! These are the fields changed by solve_be's failed-step cleanup, including
      ! the final tenth failure. They deliberately differ from evaluated inputs.
      yt(:,1)=original
      tt(1)=expected_conditions(1)/2.0_dp
      t9t(1)=0.75_dp
      rhot(1)=90.0_dp
      yet(1)=initial_ye
    enddo
    call save_failure_workspace()
    open(newunit=unit,file='failure-state.bin',status='old',access='stream',form='unformatted')
    read(unit) saved_state
    close(unit)
    if (.not.same_bits(saved_state,[expected_conditions,evaluated])) &
      call fail('retry exhaustion failure-state contains reset inputs')
    open(newunit=unit,file='failure-workspace.bin',status='old',access='stream',form='unformatted')
    read(unit) workspace_header
    read(unit) saved_workspace
    close(unit)
    if (workspace_header(2)/=1.or.workspace_header(14)/=2.or.workspace_header(15)/=1) &
      call fail('retry snapshot changed wire version or evaluation phase')
    if (.not.same_bits(saved_workspace,[expected_conditions,expected_eos,evaluated,expected_f])) &
      call fail('retry exhaustion workspace input/EOS/F association')
  case('nonfinite')
    synthetic_case=2
    call fresh(state,0.0_dp,1.0_dp,100.0_dp,f,ok,reason,.true.)
    call fail('UNEXPECTED computed nonfinite source returned')
  case('failed-lu')
    force_bad_lu=.true.; inr=0
    call adapted_step(1,inr)
    call fail('singular LU unexpectedly returned')
  case default
    call fail('unknown synthetic scenario')
  end select
  call finish()
contains
  subroutine correction_wire_fixture()
    ! Construct affine-BE records; this fixture makes NO fresh/source request.
    ! Counter/call IDs below are synthetic metadata, not physical-call evidence.
    real(dp) :: pre(160),raw(160),prior_raw(160),post(160),r(160),cw(160),cc,cp
    real(dp) :: expected(1936),values(1936),record(496),records(496,3),read_record(496)
    real(dp) :: phase_read(78568),workspace_read(338),assembly_read(490)
    real(qp) :: quad_read(962)
    integer(int32) :: header(8),oh(12),qh(9),pivots(160),branches_read(branch_size)
    integer(int64) :: ids(12),phase_read_ids(10),bytes
    integer :: i,p,reader,read_status
    pre=original; pre(1)=1.0_dp/3.0_dp
    raw=0; raw(1)=((original(1)-pre(1))/0.01_dp)/(100.0_dp+1e20_dp)
    prior_raw=2*raw; post=pre+raw; r=post-original
    call correction_norms(original,post,raw,prior_raw,1e-15_dp,1e-13_dp,cw,cc,cp)
    nonlinear_atol=1e-15_dp; nonlinear_rtol=1e-13_dp
    call enable_correction_source(.false.)
    open(newunit=assembly_eval_unit,file='assembly-evaluations.bin',status='new',access='stream',form='unformatted')
    write(assembly_eval_unit) int(z'43524145',int32),1_int32,160_int32,496_int32,0_int32,0_int32,0_int32,0_int32
    flush(assembly_eval_unit)
    open(newunit=assembly_newton_unit,file='assembly-newton.bin',status='new',access='stream',form='unformatted')
    write(assembly_newton_unit) int(z'4352414e',int32),1_int32,160_int32,78568_int32,10_int32,160_int32,0_int32,0_int32
    newton_count=7; attempt_count=3; rhs_count=13; last_step=2; previous_delta=prior_raw
    call begin_assembly_newton(2,2,original,pre,0.01_dp,0.01_dp)
    an_ids(4:9)=[5_int64,11_int64,12_int64,13_int64,0_int64,0_int64]
    an_fv=0; an_fo=0; an_fo(1)=0.125_dp; an_j=0
    an_j(1,1)=-1e20_dp; an_j(159,160)=0.25_dp; an_m=-an_j
    do i=1,160
      an_m(i,i)=an_m(i,i)+100.0_dp
    enddo
    call write_assembly_newton(1)
    an_lu=an_m; an_rhs=(original-pre)/0.01_dp
    an_pivots=[(int(i,int32),i=1,160)]
    call write_assembly_newton(2)
    an_delta=raw; an_unprojected=post; an_post=post; an_projection=0
    applied_update=post-pre; an_scalars(5)=0
    call write_assembly_newton(3)
    an_weights=1e-13_dp+1e-11_dp*max(abs(original),abs(post)); an_residual=r
    an_scalars(3:4)=[maxval(abs(r)/an_weights),sum(abs(r))]
    current_weights=cw; current_ratio=cc; previous_ratio=cp
    last_original_rhs=an_fo; last_variant_rhs=0
    call write_assembly_newton(4)
    call write_correction_iteration(4)
    ! Ordinary retention buffers both rows; failure flush must preserve order.
    record=[11.0_dp,3.0_dp,5.0_dp,0.01_dp,1.0_dp,100.0_dp,sum(pre),sum(pre), &
      1.0_dp,1.0_dp,1.0_dp,0.0_dp,1.0_dp,1.0_dp,1.0_dp,1.0_dp,pre,last_original_rhs,last_variant_rhs]
    records(:,1)=record
    call retain_assembly_record(record)
    record(1:3)=[13.0_dp,10.0_dp,7.0_dp]; records(:,2)=record
    call retain_assembly_record(record)
    inquire(unit=assembly_eval_unit,size=bytes)
    if (buffer_count/=2.or.bytes/=32) call fail('compact fixture wrote ordinary probe rows prematurely')
    allocate(aq_products(1),aq_running(1))
    aq_totals=0.25_qp; aq_classes=0.125_qp; aq_products=0.5_qp; aq_running=0.75_qp; aq_absolute=1
    last_evaluated_state=pre; last_evaluated_conditions=[0.01_dp,1.0_dp,100.0_dp]
    last_evaluated_eos=[1.0_dp,1.0_dp,1.0_dp,0.0_dp]; branch_signature=0; assembly_math_ok=.true.
    last_assembly_call=11
    call buffer_correction_workspace(correction_baseline)
    last_assembly_call=13
    call buffer_correction_workspace(correction_post)
    accepted_count=2
    call write_correction_accepted(post,0.01_dp,1.0_dp,100.0_dp,sum(post),sum(post))
    call flush_correction_failure()
    ! The first-step path writes directly and failure flush must not duplicate it.
    last_step=1; record(1)=14; records(:,3)=record
    call retain_assembly_record(record)
    call flush_correction_failure()
    flush(assembly_eval_unit); flush(assembly_newton_unit)
    inquire(unit=assembly_eval_unit,size=bytes)
    if (bytes/=32_int64+3_int64*496*8) call fail('compact fixture probe flush count')
    rewind(assembly_eval_unit)
    read(assembly_eval_unit) header
    if (any(header/=[int(z'43524145',int32),1_int32,160_int32,496_int32,0_int32,0_int32,0_int32,0_int32])) &
      call fail('compact fixture evaluation header')
    do p=1,3
      read(assembly_eval_unit) read_record
      if (.not.same_bits(read_record,records(:,p))) call fail('compact fixture evaluation row order or bytes')
    enddo
    inquire(unit=assembly_newton_unit,size=bytes)
    if (bytes/=32_int64+4_int64*(80+78568*8+640)) call fail('compact fixture phase flush count')
    rewind(assembly_newton_unit)
    read(assembly_newton_unit) header
    if (any(header/=[int(z'4352414e',int32),1_int32,160_int32,78568_int32,10_int32,160_int32,0_int32,0_int32])) &
      call fail('compact fixture matrix header')
    do p=1,4
      read(assembly_newton_unit) phase_read_ids,phase_read,pivots
      if (any(phase_read_ids/=[7_int64,2_int64,2_int64,5_int64,11_int64,12_int64,13_int64, &
          0_int64,0_int64,int(p,int64)])) call fail('compact fixture matrix phase IDs')
      if (phase_read(649)/=-1e20_dp.or.phase_read(26249)/=100.0_dp+1e20_dp) &
        call fail('compact fixture J/M byte offsets')
      if (phase_read(26247)/=0.25_dp.or.phase_read(51847)/=-0.25_dp) &
        call fail('compact fixture matrix column order')
      if (p==1.and.ieee_is_finite(phase_read(52009))) call fail('compact fixture early LU availability')
      if (p==1.and.any(pivots/=0)) call fail('compact fixture early pivots')
      if (p>=2) then
        if (any(pivots/=[(int(i,int32),i=1,160)]).or.phase_read(77607)/=-0.25_dp) &
          call fail('compact fixture retained LU/pivots')
      endif
      if (p==2.and.ieee_is_finite(phase_read(77609))) call fail('compact fixture early correction availability')
      if (p==3.and.ieee_is_finite(phase_read(78249))) call fail('compact fixture early residual availability')
      if (p==4.and.phase_read(78249)/=r(1)) call fail('compact fixture final residual byte offset')
    enddo
    inquire(unit=correction_unit,size=bytes)
    if (bytes/=32_int64+12*8+1936*8) call fail('compact fixture Newton row count')
    rewind(correction_unit)
    read(correction_unit) header
    if (any(header/=[int(z'4352434e',int32),1_int32,160_int32,1936_int32,12_int32,0_int32,0_int32,0_int32])) &
      call fail('compact fixture Newton header')
    read(correction_unit) ids,values
    if (any(ids/=[7_int64,2_int64,2_int64,5_int64,11_int64,12_int64,13_int64,0_int64,0_int64, &
        4_int64,3_int64,1_int64])) call fail('compact fixture Newton IDs and stagnation')
    expected(1:16)=[0.01_dp,0.01_dp,maxval(abs(r)/an_weights),sum(abs(r)),0.0_dp,0.0_dp, &
      1e-13_dp,1e-11_dp,1e-15_dp,1e-13_dp,cc,cp,maxval(abs(raw)),sum(abs(raw)),0.0_dp,0.0_dp]
    expected(17:176)=original; expected(177:336)=pre; expected(337:496)=post; expected(497:656)=post
    expected(657:816)=raw; expected(817:976)=prior_raw; expected(977:1136)=0; expected(1137:1296)=cw
    expected(1297:1456)=r; expected(1457:1936)=0
    expected(1777:1936)=last_original_rhs
    if (.not.same_bits(values,expected)) call fail('compact fixture Newton scalars or vector byte offsets')
    read(correction_unit,iostat=read_status) values
    if (read_status>=0) call fail('compact fixture duplicated Newton failure row')
    inquire(unit=correction_accepted_unit,size=bytes)
    if (bytes/=32_int64+496*8) call fail('compact fixture accepted row count')
    rewind(correction_accepted_unit)
    read(correction_accepted_unit) header
    if (any(header/=[int(z'43524341',int32),1_int32,160_int32,496_int32,0_int32,0_int32,0_int32,0_int32])) &
      call fail('compact fixture accepted header')
    read(correction_accepted_unit) read_record
    record=records(:,2); record(2:3)=[11.0_dp,2.0_dp]
    if (.not.same_bits(read_record,record)) call fail('compact fixture accepted original and variant F layout')
    do p=1,2
      if (p==1) then
        open(newunit=reader,file='failure-iteration-baseline-original.bin',status='old', &
          access='stream',form='unformatted')
      else
        open(newunit=reader,file='failure-iteration-post-original.bin',status='old',access='stream',form='unformatted')
      endif
      read(reader) oh,workspace_read,branches_read
      close(reader)
      if (any(oh/=[int(z'43524442',int32),1_int32,160_int32,1_int32,1_int32,1_int32,1_int32, &
          1_int32,1_int32,1_int32,1_int32,int(branch_size,int32)])) call fail('compact fixture workspace header')
      if (workspace_read(1)/=9+2*p.or..not.same_bits(workspace_read(11:170),pre)) &
        call fail('compact fixture distinct workspace call or input')
      if (.not.same_bits(workspace_read(171:330),last_original_rhs)) call fail('compact fixture original workspace F')
      if (any(branches_read/=0).or.any(workspace_read(331:338)/=1)) call fail('compact fixture workspace coefficients')
    enddo
    open(newunit=reader,file='failure-iteration-baseline-assembly.bin',status='old',access='stream',form='unformatted')
    read(reader) qh,assembly_read,quad_read
    close(reader)
    if (any(qh/=[int(z'43524157',int32),1_int32,160_int32,1_int32,1_int32,1_int32,1_int32,962_int32,1_int32])) &
      call fail('compact fixture quad header')
    if (assembly_read(1)/=11.or..not.same_bits(assembly_read(11:170),pre)) call fail('compact fixture quad input')
    if (any(quad_read(1:160)/=0.25_qp).or.any(quad_read(161:800)/=0.125_qp).or. &
        quad_read(801)/=0.5_qp.or.quad_read(802)/=0.75_qp.or.any(quad_read(803:962)/=1.0_qp)) &
      call fail('compact fixture quad byte offsets')
    if (coefficient_count/=0.or.probe_count/=0.or.rhs_count/=13.or.fresh_requests/=0) &
      call fail('compact wire fixture made a source request')
    close(assembly_eval_unit); close(assembly_newton_unit)
    write(log_unit,'(a)') 'SYNTHETIC_WIRE_ONLY constructed IDs; no fresh evaluation'
    rhs_count=0; newton_count=0; attempt_count=0; accepted_count=0
    correction_iteration_active=.false.
  end subroutine correction_wire_fixture

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
end program synthetic_native
