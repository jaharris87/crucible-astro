# Fixed pointwise reference pilot

Issue [#18](https://github.com/jaharris87/crucible-astro/issues/18), Phase 1
milestone #2. Prepared with `gpt-6.1-sol` High. D-019 accepts a new numerical
reference contract. At preparation merge all producer build/run was deferred;
**D-020 now authorizes only this exact reviewed 5,157-state pilot**, with pinned
inputs/configuration and stop-on-failure, no automatic rerun. See the live issue
for actual attempts and results; other evaluations remain unauthorized. The completed D-017 experiment and its three calls are immutable
history, not permission for this candidate. This directory contains original
software only; no reference source, real states or data are distributed.

The maintainer selected **“Expand primary benchmark audit; keep current pool as
pilot (Recommended)”**. This fixed 80-history/5,157-state candidate is a
qualification pilot; the primary audit expands read-only. No current split or
primary benchmark is locked, and this answer grants no producer execution.

This candidate prepares exactly 5,157 source-table-screened ordinary states from
80 familiar-layout histories in the fixed 83-pair audit. It excludes initial,
explicit companion-NSE and screened-out records, and the three unfamiliar layouts.
These states are candidates, not qualified training examples or final partitions.
The finite list is independent of a later human grouping decision. No model,
training architecture, trajectory regeneration, integration, NSE, Jacobian or
energy target is introduced. No scientific tolerance is selected.

## What is prepared

`reference.py prepare CONFIG NEW_IGNORED_BUNDLE` reads the bound audit JSONL and
full 166-file fixity receipt, validates full selected raw/companion hashes, then
preserves original ordinal/step/scalar/Y/stored-derivative bits in `states.bin`.
It independently checks companion precision/ordinary status, species, controls,
source-grid membership and exact selected counts. Raw files are never copied.
Reference dependencies must match `bindings.json` exactly. Only the small pinned
kernel/EOS/network closure and required EOS table are copied into the ignored
primary-workspace bundle; copied dependencies/state input are read-only.

The local CONFIG has exactly these keys:

- `files`: all paths in `bindings.json.files`, each with absolute `path` and
  `sha256`, including the table. No directory walk/object reuse is performed.
- `raw_root`: explicit absolute root of the unchanged raw collection.
- `records`, `fixity`, `d017_states`, `d017_fresh`: absolute path/checksum objects
  for the independently retained state audit, full fixity, and completed controls.

The prepared manifest binds all source/software/input bytes and private locators;
`selection.json` binds every actual record/ordinal/full raw digest. The independent
static reaction-input parser builds `expected-maps.bin` and validates factors and
baryon stoichiometry **without calling any producer routine**. The two in-grid
D-017 B states are included in the 5,157, with their retained fresh vectors bound
as controls. The cold D-017 state is excluded. Their later exact-bit comparison
adds no kernel calls. Exact agreement is an engineering control conditional on
unchanged kernel, declared configuration, precision, compiler/math/runtime
semantics; it is not a scientific accuracy tolerance. A mismatch stops; it does
not trigger a rerun or tolerance fallback.

```sh
python3 experiments/rhs_reference/reference.py prepare /absolute/.local/config.json /absolute/.local/new-bundle
python3 experiments/rhs_reference/reference.py verify /absolute/.local/new-bundle
```

Keep all real artifacts in the primary ignored preparation directory. There is no
HDF training dataset writer, positive scientific mask or portable real fixture.
The raw stored derivative and saved energy scalar are audit-only; the energy
scalar is echoed unchanged but never evaluated as a target.

## Future reviewed procedure, requiring separate human execution authority

No command below has been executed for this candidate. After exact-source fresh
review and separately accepted finite execution scope, use an isolated fresh
scratch bundle and the same pinned CPU modules/toolchain/flags as D-017:

```sh
module load cpu
module load intel/2025.3
module load PrgEnv-intel/8.7.0
module load cray-hdf5-parallel/1.14.3.9
export LD_LIBRARY_PATH="$CRAY_LD_LIBRARY_PATH:${LD_LIBRARY_PATH-}"
export PATH="${reference_python_shim:?explicit verified Python-only shim}:$PATH"
bash build.sh
bash run.sh
```

The build script is derived byte-for-byte in flags/dependency order from D-017:
`-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`, EOS preprocessing
without accelerator macros, MKL sequential. No old objects/modules, implicit
reference substitution, source patch or build failure fallback is accepted.
One MPI rank/thread and one active zone call fresh `cross_sect` then `yderiv`
**exactly once per fixed state**, preserving time/T9/rho/Y. Composition supplies
`Ye = Q/B`, with raw moments `Q=sum(Z*Y)` and positive finite
`B=sum(A*Y)` from pinned `y_moment`; raw Q is a separate diagnostic, not Ye
when B differs from one. Y is never divided by B. Weak/screening remain enabled,
heating off, and active neutrino count must be
zero. Existing native rate thresholds remain untouched. [Source audit](SOURCE_AUDIT.md)
explains current-state refresh, combinatorics, FP assumptions and limits.
The [current scope clarification](../../docs/phase1/RHS_REFERENCE_SCOPE.md)
identifies the official rate entry and retains native behavior. Reconstructing
upstream rate-evaluation history is not a new Phase 1 prerequisite; producer
authorization, numerical verification and human scientific acceptance remain
required.

The harness exports static maps before/after and all 2,048 coefficient values
actually used after each same call pair (~84.5 MB coefficient payload). No rate,
EOS or RHS routine is called to export or independently check them. It preserves
full before/after echoes and all 160 fresh components, stops on configuration,
identity, stale workspace, nonfinite or rounding-mode mismatch, and does not
change FP mode. The decoder verifies every echo, exact D-017 controls, maps and
coefficient-conditioned assembly bounds; writes private component/norm/baryon/
charge evidence; and binds executable/libraries. Weak charge rate is not forced
to zero. Partial outputs/failures remain; no overwrite/retry is automatic.

These checks verify conditional algebraic assembly and roundoff/conservation.
They do **not** independently verify rate/EOS accuracy, astrophysical truth,
historical generation, group coverage or accepted reference adequacy. Humans
retain scientific acceptance, merge and producer-execution decisions. Do not
close #18 merely for preparation or software checks.

## Checks performed in preparation

Synthetic Python controls cover hand-known stoichiometry, repeated-reactant
factors, separate creation/destruction entries, DAZ-amplified subnormal loss,
3–4–5 difference norms, malformed framing/maps/species/state/counts and changed
output echoes. Only Python tests, lint/format and `bash -n` are permitted in this
preparation gate. No Fortran compiler, including syntax-only mode, or producer
call may be used before the separate decision.
