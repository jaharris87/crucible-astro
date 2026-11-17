! Original CRUCIBLE harness; reference implementations are supplied separately.
! Three accepted-output states only. No integration, NSE, flooring or normalization.
program rhs_evaluator
  use, intrinsic :: iso_fortran_env, only: int8, int32, int64, real64
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use xnet_types, only: dp
  use xnet_parallel, only: parallel_initialize, parallel_finalize, parallel_myproc, parallel_nprocs
  use xnet_controls
  use nuclear_data, only: ny, aa, zz, read_nuclear_data
  use reaction_data, only: read_reaction_data, nnnu, nffn, nreac, iwk1
  use xnet_abundances, only: yt, ydot
  use xnet_conditions, only: tt, t9t, rhot, yet, cv, etae, detaedt9, t9dot
  use xnet_screening, only: screening_init
  use xnet_eos, only: eos_initialize
  use xnet_integrate, only: cross_sect, yderiv
  implicit none
  integer :: inp, out, k, ios, maps, saved_maps
  integer(int32) :: magic, version, nstate, nspecies, ordinal, step
  integer(int32), parameter :: ordinals(3) = [1_int32, 676_int32, 741_int32]
  integer(int8) :: endian(4)
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
  szbatch = 1989
  szone = 1989
  nzone = 1989
  nzone_max = 1989
  zb_lo = 1
  zb_hi = 1
  zb_offset = 0
  zone_id = [1989, 1, 1, 1]
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
  if (any(iwk1 >= 7 .and. iwk1 <= 10)) error stop 'Unexpected active neutrino reaction flags'
  call screening_init()
  call eos_initialize()
  allocate(yt(ny,1), ydot(ny,1))
  allocate(tt(1), t9t(1), rhot(1), yet(1), cv(1), etae(1), detaedt9(1), t9dot(1))

  open(newunit=inp, file='states.bin', access='stream', form='unformatted', status='old', action='read')
  read(inp) magic, version, nstate, nspecies
  if (magic /= int(z'43525543',int32) .or. version /= 1 .or. nstate /= 3 .or. nspecies /= 160) &
    error stop 'Invalid bounded state input'
  read(inp) input_z, input_a
  if (.not. same_bits(input_z,zz) .or. .not. same_bits(input_a,aa)) error stop 'Species mismatch'
  open(newunit=out, file='fresh.bin', access='stream', form='unformatted', status='new', action='write')
  write(out) magic, version, nstate, nspecies, input_z, input_a
  do k = 1, 3
    read(inp) ordinal, step, scalars, input_y, stored
    if (ordinal /= ordinals(k)) error stop 'Unexpected record ordinal'
    if (step <= 0 .or. .not. all(ieee_is_finite(scalars))) error stop 'Invalid ordinary state header'
    if (scalars(2) <= 0 .or. scalars(3) <= 0) error stop 'Invalid temperature/density'
    if (.not. all(ieee_is_finite(input_y)) .or. .not. all(ieee_is_finite(stored))) &
      error stop 'Nonfinite input abundance/derivative'
    yt(:,1) = input_y
    tt(1) = scalars(1)
    t9t(1) = scalars(2)
    rhot(1) = scalars(3)
    scalar_before = [tt(1), t9t(1), rhot(1)]
    y_before = yt(:,1)
    call cross_sect(mask_in=active)
    call yderiv(mask_in=active)
    scalar_after = [tt(1), t9t(1), rhot(1)]
    if (.not. same_bits(scalar_before,scalar_after) .or. .not. same_bits(y_before,yt(:,1))) &
      error stop 'Reference changed the supplied state'
    if (.not. all(ieee_is_finite(ydot(:,1))) .or. .not. ieee_is_finite(yet(1))) &
      error stop 'Nonfinite fresh RHS/EOS Ye'
    ! Full echoed before/after values permit independent byte-level verification.
    write(out) ordinal, step, scalars, scalar_after, yet(1), iweak(1), input_y, yt(:,1), stored, ydot(:,1)
  end do
  read(inp, iostat=ios) magic
  if (ios >= 0) error stop 'Trailing input or truncated final word'
  close(inp)
  close(out)
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
