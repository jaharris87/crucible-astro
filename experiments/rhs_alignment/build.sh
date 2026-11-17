#!/bin/bash
# Run only after exact-candidate independent source review has passed.
set -euo pipefail
cd "$(dirname "$0")"
python3 diagnostic.py verify .
# No preserved object/module is accepted; preparation does not create this directory.
test ! -e build.log
test ! -e rhs_evaluator
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
for name in LOADEDMODULES PE_ENV CRAYPE_VERSION CRAY_MPICH_VERSION MKLROOT OMP_NUM_THREADS; do
  printf '%s=%s\n' "$name" "${!name-}"
done
printf 'LD_LIBRARY_PATH=%s\n' "${LD_LIBRARY_PATH-}"
cd build
set -x
flags=(-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32)
sources=(xnet_types xnet_constants xnet_parallel xnet_util xnet_controls xnet_conditions xnet_ffn xnet_nnu xnet_data xnet_abundances xnet_timers xnet_fd)
for name in "${sources[@]}"; do
  h5pfc "${flags[@]}" -c "../refs/producer/${name}.f90" -o "${name}.o"
done
for name in eos_type actual_eos; do
  h5pfc "${flags[@]}" -fpp -c "../refs/tools/starkiller-helmholtz/${name}.F90" -o "${name}.o"
done
for name in xnet_eos_starkiller xnet_screening xnet_integrate; do
  h5pfc "${flags[@]}" -qmkl=sequential -c "../refs/producer/${name}.f90" -o "${name}.o"
done
h5pfc "${flags[@]}" -c ../rhs_evaluator.f90 -o rhs_evaluator.o
objects=()
for name in "${sources[@]}" eos_type actual_eos xnet_eos_starkiller xnet_screening xnet_integrate rhs_evaluator; do
  objects+=("${name}.o")
done
h5pfc "${flags[@]}" -o ../rhs_evaluator "${objects[@]}" -qmkl=sequential -lpthread -lm -ldl
cd ..
sha256sum rhs_evaluator > executable.sha256
sha256sum manifest.json
cat executable.sha256
ldd rhs_evaluator
printf 'UTC end: '; date -u
