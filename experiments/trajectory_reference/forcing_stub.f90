! Synthetic declarations only: no physical XNet source is linked to this fixture.
module xnet_types
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  integer,parameter :: dp=real64
end module xnet_types
module xnet_controls
  implicit none
  integer :: nzevolve=1,zb_lo=1,zb_hi=1
  logical,target :: lzactive(1)=.true.
end module xnet_controls
