! Original observational state only. Hooks never alter a physical equation or call it.
module phase2d_branch_state
  implicit none
  integer, parameter :: branch_size=10240
  integer :: branch_signature(branch_size)=0
  integer :: status_sink=0,log_sink=0
  logical :: diagnostics_ready=.false.
contains
  subroutine abort_linear(info,operation)
    use, intrinsic :: iso_fortran_env, only: error_unit
    integer,intent(in) :: info
    character(*),intent(in) :: operation
    if (diagnostics_ready) then
      write(log_sink,'(a,a,a,i0)') 'FAILURE LAPACK ',trim(operation),' info=',info
      write(status_sink,'(a,a,a,i0)') 'FAILURE LAPACK ',trim(operation),' info=',info
      flush(log_sink); flush(status_sink)
    endif
    write(error_unit,'(a,a,a,i0)') 'FAILURE LAPACK ',trim(operation),' info=',info
    error stop 1
  end subroutine abort_linear
  integer function side(value,boundary)
    use, intrinsic :: iso_fortran_env, only: real64
    real(real64), intent(in) :: value,boundary
    side=0
    if (value<boundary) side=-1
    if (value>boundary) side=1
  end function side
end module phase2d_branch_state
