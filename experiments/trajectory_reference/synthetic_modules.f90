! Independent synthetic closure for testing native_adapter without producer code,
! data, tables, MPI or any physical RHS evaluation. Link with the declared MKL.
module xnet_types
  use, intrinsic :: iso_fortran_env, only: real64
  implicit none
  integer,parameter :: dp=real64
end module
module nuclear_data
  use xnet_types
  implicit none
  integer :: ny=160
  real(dp) :: aa(160)=1,zz(160)=1
end module
module xnet_controls
  use xnet_types
  implicit none
  integer :: zb_lo=1,zb_hi=1,kitmx=30,ijac=1,iweak(1)=1
  real(dp) :: ymin=0,tdel_maxmult=2
end module
module xnet_conditions
  use xnet_types
  implicit none
  real(dp) :: tt(1)=0,t9t(1)=1,rhot(1)=100,yet(1)=1,cv(1)=1,etae(1)=1,detaedt9(1)=0,tdel(1)=0.01_dp
end module
module xnet_abundances
  use xnet_types
  implicit none
  real(dp) :: y(160,1)=0,yt(160,1)=0,ydot(160,1)=0
contains
  subroutine y_moment(state,ye,total,abar,zbar,z2bar,zibar)
    use nuclear_data, only: aa,zz
    real(dp),intent(in) :: state(:)
    real(dp),intent(out) :: ye,total,abar,zbar,z2bar,zibar
    real(dp) :: baryon,charge
    total=sum(state); baryon=sum(aa*state); charge=sum(zz*state)
    ye=charge/baryon; abar=baryon/total; zbar=charge/total
    z2bar=sum(state*zz*zz)/total; zibar=sum(state*zz**1.5_dp)/total
  end subroutine
end module
module actual_eos_module
  use xnet_types
  implicit none
  real(dp),allocatable :: d(:),t(:)
end module
module reaction_data
  use xnet_types
  implicit none
  real(dp) :: csect1(1,1)=1,csect2(1,1)=1,csect3(1,1)=1,csect4(1,1)=1
  real(dp) :: b1(1,1)=1,b2(1,1)=1,b3(1,1)=1,b4(1,1)=1
end module
module xnet_integrate
  use xnet_types
  implicit none
  integer :: synthetic_case=0
contains
  subroutine cross_sect(mask_in)
    use xnet_conditions
    use xnet_abundances, only: yt,y_moment
    logical,intent(in) :: mask_in(:)
    real(dp) :: total,abar,zbar,z2bar,zibar
    call y_moment(yt(:,1),yet(1),total,abar,zbar,z2bar,zibar)
    cv=1; etae=1; detaedt9=0
  end subroutine
  subroutine yderiv(mask_in)
    use xnet_abundances
    logical,intent(in) :: mask_in(:)
    ydot=0
    select case(synthetic_case)
    case(0)
      ! Quadratic reaction conserves the nonunit total exactly as a mathematical IVP.
      ydot(1,1)=-1000.0_dp*yt(1,1)**2
      ydot(2,1)=-ydot(1,1)
    case(1)
      ! No admissible nonnegative BE root: projection must never manufacture success.
      ydot(1,1)=-60.0_dp
      ydot(2,1)=60.0_dp
    end select
  end subroutine
end module
module xnet_jacobian
  use phase2d_branch_state, only: abort_linear
  use xnet_types
  implicit none
  real(dp) :: dydotdy(160,160,1)=0,jac(160,160,1)=0
  integer :: pivots(160)=0
  logical :: force_bad_lu=.false.
contains
  subroutine jacobian_scale(diag,mult,mask_in)
    real(dp),intent(in) :: diag(:),mult(:)
    logical,intent(in) :: mask_in(:)
    integer :: i
    jac(:,:,1)=mult(1)*dydotdy(:,:,1)
    do i=1,160
      jac(i,i,1)=jac(i,i,1)+diag(1)
    enddo
  end subroutine
  subroutine jacobian_decomp(step,mask_in)
    integer,intent(in) :: step
    logical,intent(in) :: mask_in(:)
    integer :: info
    if (force_bad_lu) jac=0
    call dgetrf(160,160,jac(:,:,1),160,pivots,info)
    if (info/=0) call abort_linear(info,'dgetrf')
  end subroutine
  subroutine jacobian_bksub(step,rhs,dy,t9rhs,dt9,mask_in)
    integer,intent(in) :: step
    real(dp),intent(in) :: rhs(:,:),t9rhs(:)
    real(dp),intent(out) :: dy(:,:),dt9(:)
    logical,intent(in) :: mask_in(:)
    integer :: info
    dy=rhs; dt9=0
    call dgetrs('N',160,1,jac(:,:,1),160,pivots,dy,160,info)
    if (info/=0) call abort_linear(info,'dgetrs')
  end subroutine
end module
