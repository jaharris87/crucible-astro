#!/bin/bash
# Fresh build recipe; staging never invokes it.
# Requires concrete accepted producer scope; the D-038 proposal grants no authority.
set -euo pipefail
cd "$(dirname "$0")"
python3 stage_native.py verify .
test ! -e build.log
test ! -e build
test ! -e trajectory_driver
test ! -e forcing_synthetic
test ! -e trajectory_synthetic
test ! -e executable.sha256
mkdir build
exec > >(tee build.log) 2>&1
printf 'UTC start: '; date -u
uname -a
python3 --version
command -v h5pfc
sha256sum "$(command -v h5pfc)"
h5pfc -show
h5pfc -showconfig
h5pfc --version
if type module >/dev/null 2>&1; then module list; fi
for name in LOADEDMODULES PE_ENV CRAYPE_VERSION CRAY_MPICH_VERSION MKLROOT OMP_NUM_THREADS MKL_NUM_THREADS; do
  printf '%s=%s\n' "$name" "${!name-}"
done
printf 'LD_LIBRARY_PATH=%s\n' "${LD_LIBRARY_PATH-}"
lscpu
for required_module in cpu/1.0 intel/2025.3 PrgEnv-intel/8.7.0 cray-hdf5-parallel/1.14.3.9; do
  [[ ":${LOADEDMODULES-}:" == *":${required_module}:"* ]] || {
    printf 'Required pinned module absent: %s\n' "$required_module"
    exit 1
  }
done
test "${OMP_NUM_THREADS-}" = 1
test "${MKL_NUM_THREADS-}" = 1
cd build
set -x
flags=(-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32)
h5pfc "${flags[@]}" -c ../phase2d_branch_state.f90 -o phase2d_branch_state.o
sources=(xnet_types xnet_constants xnet_parallel xnet_util xnet_controls xnet_conditions xnet_ffn xnet_nnu xnet_data xnet_abundances xnet_timers xnet_fd)
for name in "${sources[@]}"; do
  h5pfc "${flags[@]}" -c "../refs/producer/${name}.f90" -o "${name}.o"
done
for name in eos_type actual_eos; do
  h5pfc "${flags[@]}" -fpp -c "../refs/tools/starkiller-helmholtz/${name}.F90" -o "${name}.o"
done
for name in xnet_eos_starkiller xnet_screening xnet_integrate xnet_jacobian_dense; do
  h5pfc "${flags[@]}" -qmkl=sequential -c "../refs/producer/${name}.f90" -o "${name}.o"
done
h5pfc "${flags[@]}" -c ../native_adapter.f90 -o native_adapter.o
h5pfc "${flags[@]}" -c ../diagnostic_native.f90 -o diagnostic_native.o
h5pfc "${flags[@]}" -c ../refs/producer/xnet_integrate_be.f90 -o xnet_integrate_be.o
h5pfc "${flags[@]}" -c ../trajectory_driver.f90 -o trajectory_driver.o
objects=(phase2d_branch_state.o)
for name in "${sources[@]}" eos_type actual_eos xnet_eos_starkiller xnet_screening xnet_integrate xnet_jacobian_dense native_adapter diagnostic_native xnet_integrate_be trajectory_driver; do
  objects+=("${name}.o")
done
h5pfc "${flags[@]}" -o ../trajectory_driver "${objects[@]}" -qmkl=sequential -lpthread -lm -ldl
# Synthetic closure is separately compiled in its own module/object directory.
# It calls the identical native_adapter against an independent quadratic source.
mkdir synthetic
cd synthetic
h5pfc "${flags[@]}" -c ../../phase2d_branch_state.f90 -o phase2d_branch_state.o
h5pfc "${flags[@]}" -qmkl=sequential -c ../../synthetic_modules.f90 -o synthetic_modules.o
h5pfc "${flags[@]}" -c ../../native_adapter.f90 -o native_adapter.o
h5pfc "${flags[@]}" -c ../../synthetic_native.f90 -o synthetic_native.o
h5pfc "${flags[@]}" -o ../../trajectory_synthetic phase2d_branch_state.o synthetic_modules.o native_adapter.o synthetic_native.o -qmkl=sequential -lpthread -lm -ldl
cd ..
mkdir forcing-synthetic
cd forcing-synthetic
h5pfc "${flags[@]}" -c ../../forcing_stub.f90 -o forcing_stub.o
h5pfc "${flags[@]}" -c ../../refs/producer/xnet_conditions.f90 -o xnet_conditions.o
h5pfc "${flags[@]}" -c ../../forcing_synthetic.f90 -o forcing_synthetic.o
h5pfc "${flags[@]}" -o ../../forcing_synthetic forcing_stub.o xnet_conditions.o forcing_synthetic.o
cd ../..
sha256sum forcing_synthetic > forcing-executable.sha256
sha256sum trajectory_synthetic > synthetic-executable.sha256
sha256sum trajectory_driver > executable.sha256
sha256sum source-manifest.json
cat executable.sha256
ldd trajectory_driver | tee linked-libraries.txt
python3 - <<'PYHASH'
import hashlib
import json
from pathlib import Path
paths = set()
for line in Path("linked-libraries.txt").read_text().splitlines():
    for word in line.split():
        if word.startswith("/") and Path(word).is_file():
            paths.add(Path(word).resolve())
records = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
Path("linked-library-hashes.json").write_text(json.dumps(records, indent=2) + "\n")
PYHASH
printf 'UTC end: '; date -u
