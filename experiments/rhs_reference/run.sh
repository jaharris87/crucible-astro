#!/bin/bash
# Only after review and a successful recorded fresh build. Exactly the fixed 5157 RHS calls; execution requires separate authorization.
set -euo pipefail
cd "$(dirname "$0")"
python3 reference.py verify .
test ! -e run.log
sha256sum -c executable.sha256
test ! -e fresh.bin
test ! -e kernel.log
test ! -e loaded-maps.txt
test ! -e comparison.json
test ! -e components.jsonl
test ! -e used-maps.bin
test ! -e used-maps-after.bin
exec > >(tee run.log) 2>&1
printf 'UTC start: '; date -u
uname -a
python3 --version
sha256sum manifest.json rhs_evaluator
ldd rhs_evaluator
printf 'LD_LIBRARY_PATH=%s\n' "${LD_LIBRARY_PATH-}"
export OMP_NUM_THREADS=1
set -x
srun -n 1 -c 1 ./rhs_evaluator
sha256sum -c executable.sha256
python3 reference.py compare .
printf 'UTC end: '; date -u
