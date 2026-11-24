program assembly_synthetic
  use assembly113_math, only: precision_fixture
  implicit none
  character(24) :: scenario
  character(160) :: reason
  integer :: unit
  logical :: ok
  call get_command_argument(1,scenario)
  open(newunit=unit,file='fixture-status.txt',status='new',action='write')
  write(unit,'(a)') 'RUNNING'
  flush(unit)
  call precision_fixture(trim(scenario),ok,reason)
  if (.not.ok) then
    write(unit,'(a)') 'FAILURE '//trim(reason)
    close(unit)
    error stop 1
  endif
  write(unit,'(a)') 'PASS'
  close(unit)
end program assembly_synthetic
