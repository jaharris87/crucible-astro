# Three-state RHS alignment diagnostic

Issue [#14](https://github.com/jaharris87/crucible-astro/issues/14), maintainer
D-017 authorization, 2026-11-17. Preparation: `gpt-6.1-sol` High. This directory
contains original CRUCIBLE experiment support, not a qualified scientific model
or a general XNet interface. **The authorized three-state execution is complete;
scientific acceptance remains open.** The exact source passed independent review
before its first build. See the [portable run report](RUN_REPORT_2026-11-17.md)
for both attempts, exact bindings, aggregate results and interpretation limits.
Humans retain scientific acceptance and merge authority. D-017 supplied authority
for this completed diagnostic, not standing permission for additional runs.

The bounded question compares stored derivatives with fresh `cross_sect` then
`yderiv` evaluations at exactly three already-audited ordinary emitted states
(pair B, zero-based data ordinals 1, 676, 741). It does not integrate a trajectory,
solve NSE, regenerate a dataset, fit anything, or evaluate the stored energy
field. Three-point agreement would not qualify the whole dataset or demonstrate
solver convergence. No acceptable numerical error tolerance has been selected.

## Reference binding and limits

`bindings.json` contains fingerprints only; no reference code/data is distributed.
The producer snapshot is the inspected modified `source_postp` tree, nested HEAD
`200b024cd06abdf4edaee489d6229edaa9ae30b3`; the listed individual file hashes,
not that HEAD alone, bind the actual kernel source. Nuclear/rate inputs are the
recovered candidate SN160 files. The maintainer explicitly selected the upstream
XNet Starkiller Helmholtz `actual_eos.F90` and `eos_type.F90` for this **new**
reference diagnostic. Their required `xnet_macros.fh` include is bound too. This
selection does not establish historical generating-build identity. The EOS table
is supplied separately with its explicit checksum. All real snapshots, absolute
locators, manifests, logs, results and libraries belong under ignored `.local/`.

The harness uses the original RHS routines unchanged. Setup follows inspected
`postp.f90:125–143,174–196`, with only the kernel dependency closure linked;
Jacobian, output, NSE, trajectory driver and integration routines are not called.
`xnet_integrate.f90:532–597` refreshes EOS, weak controls, screening and rates;
`:309–350` evaluates species derivatives. `xnet_eos_starkiller.f90:48–58` derives
Ye from composition. The driver does not substitute trajectory Ye. It preserves
weak=1, screening=1, heating=0, neutrino-control=1, and the source's temperature
switch. Recovered binary controls and control-file hash are checked. Network
`nnnu=0`, no one-reactant flags 7–10, species160, FFN176, and reaction counts
(683,1345,16,4) are asserted. A mismatch stops the experiment; it is not repaired
by disabling physics. These checks also explain why this candidate needs no
neutrino histories for its three RHS calls.

## Preparation (Python only)

Supply a local JSON configuration with four keys:

- `files`: every destination in `bindings.json.files`, plus `helm_table.dat`,
  mapped to `{"path": "/absolute/original/file", "sha256": "..."}`.
- `raw_ts`, `raw_ev`, `control`: objects with that same path/checksum form.

Every bound file must match the reviewed fingerprints. No directory walk copies
objects or module artifacts. The helper reads raw records directly with stdlib
`struct`; it has no dependency on the S02 reader or reference Python scripts.
Preparation preserves raw scalar/state/derivative bytes in a little-endian stream
and checks all companion row step identities and the selected rows' ordinary
classification. No clipping, flooring, normalization or text round-trip occurs.

```sh
python3 experiments/rhs_alignment/diagnostic.py prepare \
  /absolute/ignored/config.json /absolute/ignored/.local/diagnostic-bundle
python3 experiments/rhs_alignment/diagnostic.py verify \
  /absolute/ignored/.local/diagnostic-bundle
```

`manifest.json` records every copied source/input, the selection, raw hashes and
local locators. Its original preparation status is preserved; the separate run
report binds the later build and execution receipts. Keep its checksum in the
issue/experiment receipt. Treat changes to the harness, bindings or build
procedure after review as a changed source candidate.

## Recorded build and three-state execution procedure

For an independently authorized reuse, transfer the prepared ignored bundle to a
new isolated writable scratch directory on the authorized existing Perlmutter
account; leave originals unchanged. Use the
reviewed `build.sh` and `run.sh` from that bundle. Do not run an original `postp`,
source patcher, `make all`, trajectory job, or repository build by analogy.

```sh
# On Perlmutter, inside an appropriate existing-account CPU allocation/environment:
module load cpu
module load intel/2025.3
module load PrgEnv-intel/8.7.0
module load cray-hdf5-parallel/1.14.3.9
export LD_LIBRARY_PATH="$CRAY_LD_LIBRARY_PATH:${LD_LIBRARY_PATH-}"
# Select an explicitly verified Python-only shim; record its target and checksum.
export PATH="${diagnostic_python_shim:?set the approved private shim directory}:$PATH"
python3 --version
bash build.sh
bash run.sh
```

Read-only module inspection found this CPU stack exposes `h5pfc` through Cray
`ftn` and Intel `ifx` 2025.3.0; no classic `ifort` was found. This explicitly
records the new diagnostic toolchain, without claiming the original compiler
was recovered. The recorded execution used Python 3.12.12 through a private
shim containing only `python3`; the default system Python 3.6.15 caused the
preserved first attempt to stop before compilation. Before/after shim checks
verified the login compiler/wrapper and library environment were unchanged.
Compute-job environment and loaded libraries were recorded separately, including
a system fabric search-path addition; build/run environments are not asserted
byte-identical. See the run report for completed checks.

The commands illustrate the recorded procedure, not an additional execution
grant. `build.sh` creates a new `build/` directory and fails if one exists. It records compiler-wrapper expansion,
versions, module/compiler environment, commands' output, linkage and executable
checksum. Precision/flags follow the retained log: `-g -O0 -traceback`,
`-qopenmp-stubs`, default real64/int32 and MKL sequential. `-fpp` explicitly
processes the selected EOS includes, with no accelerator macros. No source,
compiler-precision, EOS or network fallback is permitted on build failure.
PARDISO is unnecessary because no Jacobian is built or solved. The minimal link
retains MPI, HDF5 and BLAS; one rank/one thread preserves the original one-zone
kernel path. No runtime or reference-accuracy promise is made.

`run.sh` verifies the bound inputs again, records the executable and linkage,
launches one rank, and runs the Python comparison only after successful completion.
The run verifies its executable against the fresh build checksum before and after
execution. The program rejects unexpected precision/endian/rank/network metadata. It echoes
all supplied state scalars and arrays and checks time/T9/density/Y bit identity
before and after every evaluation. It writes all 160 stored/fresh derivatives,
composition-derived Ye and effective weak control, plus actual loaded library paths
from `/proc/self/maps`. The comparison independently rejects changed echoes,
nonfinite values or unexpected lengths; hashes runtime shared-library files;
and writes component differences, absolute L1/L2/Linf, baryon and charge-rate
summaries and state hashes. Weak reactions mean charge-rate zero is not imposed.
The raw saved energy scalar is only echoed for identity; it is not compared to RHS.

Stop on input/configuration/species mismatch, active neutrino tables, unavailable
required dependency, failed build, changed state, nonfinite result, or completion
of the three comparisons. Preserve partial files and failure logs; never overwrite
them or silently rerun with altered physics. Outputs use `status='new'`, and the
helper refuses an existing bundle/comparison. Accepted-state label fidelity,
historical generating association, and scientific tolerance acceptance remain
separate questions even when this diagnostic completes.

## Preparation verification

Synthetic Python tests independently construct binary framing and known numerical
answers, including signed-zero identity, corrupted markers/controls/NSE selection,
nonfinite input, state/scalar mutation, and 3–4–5 norm/baryon/charge controls.
They do not execute Fortran or verify its runtime behavior. Static shell syntax
and repository checks accompanied source review. The run report separately
records the completed reference execution and author output checks. Subsequent
independent evidence/report review and human merge/integration receipts belong
in the live issue/PR; execution success does not qualify training labels.
