! Original CRUCIBLE harness; reference implementations are supplied separately.
! Fixed 5157-state candidate only; preparation is not execution authority. No integration, NSE, flooring or normalization.
program rhs_evaluator
  use, intrinsic :: iso_fortran_env, only: int8, int32, int64, real64
  use, intrinsic :: ieee_arithmetic
  use xnet_types, only: dp
  use xnet_parallel, only: parallel_initialize, parallel_finalize, parallel_myproc, parallel_nprocs
  use xnet_controls
  use nuclear_data, only: ny, aa, zz, gg, read_nuclear_data
  use reaction_data, only: read_reaction_data, nnnu, nffn, nreac, iwk1, nan, la, le, &
    n1i, n2i, n3i, n4i, mu1, mu2, mu3, mu4, n10, n20, n30, n40, a1, a2, a3, a4, &
    csect1, csect2, csect3, csect4, b1, b2, b3, b4
  use xnet_screening, only: h1, h2, h3, h4
  use xnet_abundances, only: yt, ydot
  use xnet_conditions, only: tt, t9t, rhot, yet, cv, etae, detaedt9, t9dot
  use xnet_screening, only: screening_init
  use xnet_eos, only: eos_initialize
  use xnet_integrate, only: cross_sect, yderiv
  implicit none
  integer :: inp, out, k, ios, maps, saved_maps
  integer(int32) :: magic, version, nstate, nspecies, ordinal, step, sequence, row_id, zone
  real(dp) :: poison, coefficients_before(2048)
  type(ieee_round_type) :: rounding
  logical :: gradual
  integer(int8) :: endian(4)
  integer(int64) :: file_size, file_position
  real(dp) :: scalars(5), input_z(160), input_a(160), input_y(160), stored(160)
  real(dp) :: scalar_after(3), scalar_before(3), y_before(160)
  character(80) :: data_desc
  character(4096) :: map_line
  logical :: active(1)

  if (storage_size(1) /= 32 .or. storage_size(1.0) /= 64 .or. dp /= real64) &
    error stop 'Required int32/default-real64/dp-real64 precision not active'
  magic = int(z'01020304', int32)
  endian = transfer(magic, endian)
  if (any(endian /= [4_int8, 3_int8, 2_int8, 1_int8])) error stop 'Little endian required'

  call parallel_initialize()
  if (parallel_nprocs() /= 1) error stop 'Exactly one MPI rank required'
  myid = parallel_myproc()
  nproc = 1
  mythread = 1
  nthread = 1
  nzevolve = 1
  nzbatchmx = 1
  nzbatch = 1
  szbatch = 1
  szone = 1
  nzone = 1
  nzone_max = 1
  zb_lo = 1
  zb_hi = 1
  zb_offset = 0
  zone_id = [1, 1, 1, 1]
  ! These settings are checked against the original binary controls by preparation.
  iweak0 = 1
  iscrn = 1
  iheat = 0
  ineutrino = 1
  iprocess = 0
  isolv = 1
  idiag = 0
  itsout = 0
  ! Preserve source default t9min, but reject an unexpected source snapshot.
  if (t9min /= 0.01_dp) error stop 'Unexpected strong-reaction temperature switch'
  allocate(lzactive(1), iweak(1), kmon(2,1), ktot(5,1))
  lzactive = .true.
  active = .true.
  iweak = iweak0
  kmon = 0
  ktot = 0
  open(newunit=lun_diag, file='kernel.log', status='new', action='write')

  call read_nuclear_data('network', data_desc)
  call read_reaction_data('network')
  if (ny /= 160 .or. nffn /= 176 .or. nnnu /= 0) error stop 'Unexpected network dimensions/NNU'
  if (any(nreac /= [683, 1345, 16, 4])) error stop 'Unexpected reaction counts'
  if (any(iwk1 < 0 .or. iwk1 > 4)) error stop 'Unexpected one-reactant flags'
  call screening_init()
  call eos_initialize()
  allocate(yt(ny,1), ydot(ny,1))
  allocate(tt(1), t9t(1), rhot(1), yet(1), cv(1), etae(1), detaedt9(1), t9dot(1))

  open(newunit=inp, file='states.bin', access='stream', form='unformatted', status='old', action='read')
  read(inp) magic, version, nstate, nspecies
  if (magic /= int(z'43525543',int32) .or. version /= 2 .or. nstate /= 5157 .or. nspecies /= 160) &
    error stop 'Invalid bounded state input'
  read(inp) input_z, input_a
  if (.not. same_bits(input_z,zz) .or. .not. same_bits(input_a,aa)) error stop 'Species mismatch'
  open(newunit=out, file='fresh.bin', access='stream', form='unformatted', status='new', action='write')
  write(out) magic, version, nstate, nspecies, input_z, input_a
  call write_maps('used-maps.bin')
  poison = ieee_value(0.0_dp, ieee_quiet_nan)
  do k = 1, nstate
    read(inp) sequence, row_id, zone, ordinal, step, scalars, input_y, stored
    if (sequence /= k .or. row_id <= 0 .or. zone <= 0 .or. ordinal <= 0) error stop 'Invalid state identity'
    szbatch = zone
    zone_id = [zone, 1, 1, 1]
    if (iweak0 /= 1 .or. iscrn /= 1 .or. iheat /= 0 .or. ineutrino /= 1 .or. nnnu /= 0) &
      error stop 'Changed reference configuration'
    ! Poison only outputs/workspaces which the inspected active path refreshes.
    ! This is a stale-state detector, not a replacement rate/EOS implementation.
    h1=poison; h2=poison; h3=poison; h4=poison; gg=poison
    csect1=poison; csect2=poison; csect3=poison; csect4=poison
    b1=poison; b2=poison; b3=poison; b4=poison
    ydot=poison; yet=poison; cv=poison; etae=poison; detaedt9=poison
    if (step <= 0 .or. .not. all(ieee_is_finite(scalars))) error stop 'Invalid ordinary state header'
    if (scalars(2) <= 0 .or. scalars(3) <= 0) error stop 'Invalid temperature/density'
    if (.not. all(ieee_is_finite(input_y)) .or. .not. all(ieee_is_finite(stored))) &
      error stop 'Nonfinite input abundance/derivative'
    if (any(input_y < 0.0_dp .or. input_y > 1.0_dp)) error stop 'Unsupported arithmetic-bound input'
    yt(:,1) = input_y
    tt(1) = scalars(1)
    t9t(1) = scalars(2)
    rhot(1) = scalars(3)
    scalar_before = [tt(1), t9t(1), rhot(1)]
    y_before = yt(:,1)
    call cross_sect(mask_in=active)
    call check_rounding()
    coefficients_before = [csect1(:,1),csect2(:,1),csect3(:,1),csect4(:,1)]
    call yderiv(mask_in=active)
    call check_rounding()
    if (.not. same_bits(coefficients_before,[csect1(:,1),csect2(:,1),csect3(:,1),csect4(:,1)])) &
      error stop 'yderiv changed coefficients'
    scalar_after = [tt(1), t9t(1), rhot(1)]
    if (.not. same_bits(scalar_before,scalar_after) .or. .not. same_bits(y_before,yt(:,1))) &
      error stop 'Reference changed the supplied state'
    if (.not. all(ieee_is_finite(ydot(:,1))) .or. .not. ieee_is_finite(yet(1))) &
      error stop 'Nonfinite fresh RHS/EOS Ye'
    if (iweak(1) /= 1 .or. .not. all(ieee_is_finite(b1)) .or. .not. all(ieee_is_finite(b2)) .or. &
      .not. all(ieee_is_finite(b3)) .or. .not. all(ieee_is_finite(b4))) error stop 'Invalid assembly workspace'
    if (.not. all(ieee_is_finite(csect1)) .or. .not. all(ieee_is_finite(csect2)) .or. &
      .not. all(ieee_is_finite(csect3)) .or. .not. all(ieee_is_finite(csect4))) error stop 'Invalid coefficients'
    ! Full echoed before/after values permit independent byte-level verification.
    write(out) sequence, row_id, zone, ordinal, step, scalars, scalar_after, yet(1), iweak(1), &
      input_y, yt(:,1), stored, ydot(:,1), csect1(:,1), csect2(:,1), csect3(:,1), csect4(:,1)
  end do
  inquire(unit=inp,size=file_size,pos=file_position)
  if (file_position /= file_size+1) error stop 'Trailing input bytes'
  close(inp)
  close(out)
  call write_maps('used-maps-after.bin')
  ! Capture actual loaded library paths (including runtime-selected BLAS kernels).
  open(newunit=maps, file='/proc/self/maps', status='old', action='read')
  open(newunit=saved_maps, file='loaded-maps.txt', status='new', action='write')
  do
    read(maps,'(a)',iostat=ios) map_line
    if (ios /= 0) exit
    write(saved_maps,'(a)') trim(map_line)
  end do
  close(maps)
  close(saved_maps)
  close(lun_diag)
  call parallel_finalize()
contains
  subroutine check_rounding()
    call ieee_get_rounding_mode(rounding)
    if (rounding /= ieee_nearest) error stop 'Nearest rounding required for assembly bound'
    if (ieee_support_underflow_control()) then
      call ieee_get_underflow_mode(gradual)
      write(lun_diag,*) 'IEEE nearest, gradual underflow reporting:',gradual
    endif
    ! DAZ is not identified by this standard query. Offline bounds permit DAZ/FTZ.
  end subroutine check_rounding
  subroutine write_maps(filename)
    character(*), intent(in) :: filename
    integer :: unit
    open(newunit=unit,file=filename,access='stream',form='unformatted',status='new',action='write')
    write(unit) la, le
    write(unit) 1_int32,nreac(1),nan(1),n1i,mu1,n10,a1
    write(unit) 2_int32,nreac(2),nan(2),n2i,mu2,n20,a2
    write(unit) 3_int32,nreac(3),nan(3),n3i,mu3,n30,a3
    write(unit) 4_int32,nreac(4),nan(4),n4i,mu4,n40,a4
    close(unit)
  end subroutine write_maps
  logical function same_bits(left,right)
    real(dp), intent(in) :: left(:), right(:)
    integer :: j
    same_bits = .false.
    if (size(left) /= size(right)) return
    do j = 1, size(left)
      if (transfer(left(j),0_int64) /= transfer(right(j),0_int64)) return
    end do
    same_bits = .true.
  end function same_bits
end program rhs_evaluator
