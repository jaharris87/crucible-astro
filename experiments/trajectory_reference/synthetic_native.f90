! Uses the actual numerical adapter with a small independent mathematical oracle.
program synthetic_native
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
  integer :: k,inr(1)
  call get_command_argument(1,scenario)
  call open_diagnostics()
  allocate(helm_density(2),helm_temperature(2))
  helm_density=[1e-12_dp,1e15_dp]; helm_temperature=[1e3_dp,1e13_dp]
  state=0; state(1)=0.5_dp; state(2)=0.25_dp
  y(:,1)=state; yt=y; original=state
  select case(trim(scenario))
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
end program synthetic_native
