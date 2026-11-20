! Original observational state only. Hooks never alter a physical equation or call it.
module phase2d_branch_state
  implicit none
  integer, parameter :: branch_size=10240
  integer :: branch_signature(branch_size)=0
contains
  subroutine abort_linear(info,operation)
    integer,intent(in) :: info
    character(*),intent(in) :: operation
    ! A plain external bridge avoids a dense-module -> adapter-module dependency.
    ! Its implementation calls the same snapshot/flush/failure path as domain errors.
    interface
      subroutine native_linear_failure(code,name)
        integer,intent(in) :: code
        character(*),intent(in) :: name
      end subroutine native_linear_failure
    end interface
    call native_linear_failure(info,operation)
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
