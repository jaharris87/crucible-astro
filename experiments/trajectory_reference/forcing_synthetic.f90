! Exercise the actual adapted xnet_conditions module without any physical kernel.
program forcing_synthetic
  use, intrinsic :: iso_fortran_env, only: int64
  use, intrinsic :: ieee_arithmetic
  use xnet_types, only: dp
  use xnet_conditions
  implicit none
  character(32) :: scenario
  real(dp) :: query(1),temperature(1),density(1),expected_t,expected_r
  real(dp),parameter :: probes(6)=[0.0_dp,0.001_dp,0.003_dp,0.006_dp,0.010_dp,0.011_dp]
  integer :: location(1),j,k,status_unit
  call get_command_argument(1,scenario)
  open(newunit=status_unit,file='fixture-status.txt',status='new',action='write')
  write(status_unit,'(a)') 'RUNNING'
  flush(status_unit)
  allocate(nh(1),th(3,1),t9h(3,1),rhoh(3,1))
  nh=3
  th(:,1)=[0.0_dp,0.003_dp,0.011_dp]
  t9h(:,1)=2.0_dp+3.0_dp*th(:,1)
  rhoh(:,1)=1000.0_dp-7.0_dp*th(:,1)
  location=1; temperature=-1; density=-1
  select case(trim(scenario))
  case('forcing')
    do j=1,size(probes)
      query=probes(j)
      call t9rhofind(j,query,location,temperature,density)
      expected_t=2.0_dp+3.0_dp*query(1)
      expected_r=1000.0_dp-7.0_dp*query(1)
      if (abs(temperature(1)-expected_t)>16*epsilon(1.0_dp)*max(1.0_dp,abs(expected_t))) &
        error stop 'affine temperature oracle'
      if (abs(density(1)-expected_r)>16*epsilon(1.0_dp)*max(1.0_dp,abs(expected_r))) &
        error stop 'affine density oracle'
      do k=1,3
        if (query(1)/=th(k,1)) cycle
        if (transfer(temperature(1),0_int64)/=transfer(t9h(k,1),0_int64)) &
          error stop 'exact knot temperature bits'
        if (transfer(density(1),0_int64)/=transfer(rhoh(k,1),0_int64)) &
          error stop 'exact knot density bits'
      enddo
    enddo
  case('outside')
    query=-epsilon(1.0_dp)
    call t9rhofind(1,query,location,temperature,density)
    error stop 'UNEXPECTED outside forcing return'
  case('nonfinite')
    th(2,1)=ieee_value(0.0_dp,ieee_quiet_nan); query=0.001_dp
    call t9rhofind(1,query,location,temperature,density)
    error stop 'UNEXPECTED nonfinite forcing return'
  case('nonincreasing')
    th(2,1)=th(1,1); query=0.001_dp
    call t9rhofind(1,query,location,temperature,density)
    error stop 'UNEXPECTED nonincreasing forcing return'
  case default
    error stop 'unknown forcing fixture scenario'
  end select
  write(status_unit,'(a)') 'PASS'
  close(status_unit)
end program forcing_synthetic
