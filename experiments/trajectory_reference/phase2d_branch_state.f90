! Original observational state only. Hooks never alter a physical equation or call it.
module phase2d_branch_state
  implicit none
  integer, parameter :: branch_size=10240
  integer :: branch_signature(branch_size)=0
contains
  integer function side(value,boundary)
    use, intrinsic :: iso_fortran_env, only: real64
    real(real64), intent(in) :: value,boundary
    side=0
    if (value<boundary) side=-1
    if (value>boundary) side=1
  end function side
end module phase2d_branch_state
