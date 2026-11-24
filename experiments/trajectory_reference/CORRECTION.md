# D-040 correction-controlled trajectory guide

The maintainer [accepted the protocol and conditional producer scope](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7140960473)
on 2026-11-24. The [frozen protocol](CORRECTION_PROTOCOL.md), SHA256
`a7eac47716dc710780469b4f107adec59e3fd6e60d435cd62ef60560f13be0a8`,
is controlling. Fresh exact-candidate implementation review must pass before any
native build, compiled fixture or physical evaluation. This guide records the
procedure; implementation and public synthetic tests establish no trajectory
result or reference acceptance. Human reference/final acceptance and merge remain
separate. Stop before Phase 2E.

The numerical RHS remains `native-XNet-b64-productsum113-b64-v1`; binary64 Y,
forcing, physics, inputs and global convergence gates stay fixed. Only the local
nonlinear stopping rule changes: two consecutive **raw** A-weighted corrections
must pass under the same current weights, with all other gates passing. Standard
correction controls are `(1e-15,1e-13)`; tight controls are `(1e-16,1e-14)`.
Residual reporting always uses the original `(1e-13,1e-11)` weights. A large raw
residual remains visible and does not retrospectively change D-036/D-039 outcomes.
There is no local truncation-error controller, training or physical-accuracy claim.

## Offline preparation

Use the locked noneditable installation in [Contributing](../../CONTRIBUTING.md)
and a clean, committed implementation checkout. Keep private configurations and
artifacts outside Git. The D-040 preparation config has exactly:

```json
{
  "trajectory_prepare_config": "/absolute/private/original-prepare-config.json",
  "assembly_root": "/absolute/private/completed-d039-directory"
}
```

The first file is the unchanged original resolver with `annex`, `benchmark_access`
and `source_config`. The second locates completed D-039 raw evidence with the
accepted preparation/campaign hashes, not a new evaluation. The qualified loader
checks the exact original development/validation initial records, species and
D-019 F. Original annex, both input NPZs, producer sources/tables and retained
D-039 initial original/variant workspaces are hash-bound. No final-test input is
selected or inspected.

```sh
.venv/bin/python -B experiments/trajectory_reference/correction_campaign.py prepare \
  /absolute/private/correction-prepare-config.json \
  /absolute/private/correction-build-A --source-root "$PWD"
```

Preparation never builds or evaluates a producer. It stages original sources
read-only, separate adaptations/diffs, committed source/tree identity, a diff from
D-039 physical source `245ed9525ee9877653beab80eaf91bdd5493800c`, original private
annex/inputs and the complete host checker dependency closure. The reused original
helper plan is retained under `preparation-history/` as an offline-only receipt;
it grants no historical process authority. New wire inputs change only the two
correction-control fields relative to the corresponding original wires.

The actual plan has twenty processes per build: two initial controls, twelve
trajectories and six diagnostics. The 5 ms/10 ms diagnostic inputs do not exist
at preparation. The runner extracts their exact Y bytes only from a successful
L3 standard trajectory, records the source accepted-stream hash, attempt identity,
row, time bits, Y hash and new input hash, then invokes the diagnostic process.
It neither extrapolates nor makes an extra physical call to freeze these states.

Retain every failed preparation/build and its reason. Transfer complete staged
directories to new private execution-host locations; do not reuse old objects or
executables. The two planned fresh builds and at most two total prephysical
replacement builds are a lead-owned audited allowance, not an automatic loop.
A successful build stopped by preflight consumes a build attempt. No source
repair/rebuild after physical work in that build is authorized.

## Reviewed host execution

After the exact implementation review, use the pinned Intel 2025.3,
PrgEnv-intel 8.7.0, Cray parallel HDF5 1.14.3.9 environment and sequential MKL.
The build records source/compiler/module/environment/executable/library identities.
Only the 113-bit assembly module adds `-fp-model strict`; the native source flags
remain `-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`.

Within the accepted allocation:

```sh
module load cpu intel/2025.3 PrgEnv-intel/8.7.0 cray-hdf5-parallel/1.14.3.9
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
bash /absolute/private/correction-build-A/bundle/build.sh
python3 -S -B /absolute/private/correction-build-A/correction_campaign.py \
  execute /absolute/private/correction-build-A --srun
```

The caller runs the build separately. The runner never starts a compiler. All
sixteen prior compiled prerequisites and eight focused correction fixtures must
pass before the two initial controls. Controls require original D-019 and retained
D-039 original/variant bits, coefficients, moments, static maps, IEEE evidence and
exact-arithmetic checks; native `SUCCESS` alone cannot pass them.

The fixed sequence is both L0 standards; both L0 tights and their joint pilot
separation gate; both L1 standards; both L2 standards; both L3 standards; both L3
tights and four-level/global separation gates; then six frozen-state diagnostics.
An ordinary numerical failure completes the other case in that stage and stops
dependent stages. Identity, corruption, nonfinite or forensic failures stop
immediately. Every dependent plan remains explicitly conditionally unattempted.
No failed case is excluded, and no mesh/tolerance/factor change is an automatic
repair. Each completed named process needs complete consistent counters.

The ten native attempts and thirty Newton iterations apply per step call. They
are algorithm limits, not a cap on actual accepted substeps, total Newton work
or RHS calls. There is no inherited D-039 `MAX_RHS` or D-013 resource cap. Retain
actual accepted/attempted steps, Newton iterations and guarded/kernel counters,
including refusals, as well as CPU/wall/RSS/storage and unavailable scopes.

One audited infrastructure-interrupted process restart per build is permitted:

```sh
python3 -S -B /absolute/private/correction-build-A/correction_campaign.py \
  execute /absolute/private/correction-build-A --srun \
  --infrastructure-restart 'specific infrastructure reason; retained scheduler evidence'
```

Independently verify the old producer and controller are terminal before this
restart. If the controller itself was killed, the runner preserves the original
campaign/attempt receipts before recovering the single stale active record.
Native terminal `SUCCESS`/`FAILURE` records cannot be relabelled or repeated.

The runner preserves the partial attempt under `interrupted/`, verifies completed
artifacts and resumes only the interrupted named process from its identical
original input in a new process. It refuses completed-process repeats, numerical
failure restarts, changed source/build/input identities and a second interruption
restart. Native numerical retries remain part of the original process. An
interruption retains its last flushed artifacts/counter checkpoints and declares
unavailable in-flight diagnostics and the unknown unflushed-call interval.
Observed counters are lower bounds when that interval is unknown; it is never
silently counted as zero. Complete attempt accounting and passing completed named
processes remain necessary. Unknown in-flight counters alone do not waive or fail
the separate numerical trajectory gates allowed by the protocol.

## Preserve, analyze and release Build B

Keep the full raw directory, scheduler/build receipts, configurations, source
diffs, exceptions and failures. [Wire and retention details](CORRECTION_WIRE.md)
define the compact ordinary stream and retained first-step/failure/diagnostic
workspaces. Forensic capture must use buffered values, never new physical calls.
Derived JSON/NPZ artifacts remain separate, versioned and loaded without pickle.

On the execution host, collect a fresh read-only identity receipt:

```sh
python3 -S -B /absolute/private/correction-build-A/correction_host_identities.py \
  /absolute/private/correction-build-A \
  /absolute/private/correction-build-A/host-identity-verification.json --quiescent
sha256sum /absolute/private/correction-build-A/host-identity-verification.json
```

The `--quiescent` flag records the lead’s independently verified terminal
producer/controller state; do not collect while a process can still write outputs.
A failed or incomplete terminal snapshot may also be collected, with incomplete
accounting explicit and no inferred qualification. Changed campaign/artifact bytes
refuse collection. The collector hashes actual recorded execution-host runtime libraries and retained
build files. It does not remap vendor paths onto the analysis machine or invoke
any executable. Retain its explicit SHA256 for portable offline verification.

On the analysis machine, with the complete raw archive and host receipt:

```sh
.venv/bin/python -B experiments/trajectory_reference/correction_report.py analyze \
  /absolute/private/correction-build-A /absolute/private/A-verification \
  --host-identity-sha EXACT_HOST_RECEIPT_SHA256
.venv/bin/python -B experiments/trajectory_reference/correction_report.py reload \
  /absolute/private/correction-build-A /absolute/private/A-verification \
  --host-identity-sha EXACT_HOST_RECEIPT_SHA256
```

Fresh-process reload recomputes metrics and checks NPZ dtype, shape and array
bytes. Successful numerical qualification, provenance verification and reload
produce a separate `A-verification.release.json`, bound to the original report,
raw campaign/preparation and source. A report without that successful release
cannot release Build B. Failed analysis/reload artifacts remain retained.

Only after all twenty A processes and independent verification pass, prepare B
from the same clean committed source, using the A release receipt's exact hash:

```sh
.venv/bin/python -B experiments/trajectory_reference/correction_campaign.py prepare \
  /absolute/private/correction-prepare-config.json \
  /absolute/private/correction-build-B --source-root "$PWD" --build-label B \
  --build-a /absolute/private/correction-build-A \
  --build-a-verification /absolute/private/A-verification.release.json \
  --build-a-verification-sha EXACT_A_RELEASE_SHA256
```

B preparation copies and binds A's preparation, campaign and release receipts;
execution checks successful A qualification/reload and identical source/input
closure before any compiled prerequisite or physical call. Build B gets a fresh
isolated directory and follows the identical host build/execution/identity/
analysis/reload procedure. Both builds must independently pass. Then compare:

```sh
.venv/bin/python -B experiments/trajectory_reference/correction_report.py compare \
  /absolute/private/correction-build-A /absolute/private/correction-build-B \
  /absolute/private/AB-comparison \
  --a-host-identity-sha EXACT_A_HOST_RECEIPT_SHA256 \
  --b-host-identity-sha EXACT_B_HOST_RECEIPT_SHA256
```

Serialization identity, global numerical convergence and clean-build numerical
reproduction are separate checks. Preserve signed differences, masks/memberships,
all inventory/moment comparisons and mesh/counter differences. Passing these
fixed numerical gates still needs independent artifact assessment and the human
reference/merge/final decisions. Keep issue #44, the 2D goal and milestone #3 open
until their actual exits; no Phase 2E outcome is generated here.
