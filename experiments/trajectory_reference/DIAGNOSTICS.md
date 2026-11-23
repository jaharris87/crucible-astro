# Frozen-state diagnostic guide

**D-038 was explicitly accepted on 2026-11-23.** The [actual receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7107405775)
authorizes the exact [protocol](DIAGNOSTIC_PROTOCOL.md) and bounded producer
envelope. Its proposal-time header remains frozen evidence. The single authorized
campaign completed; see the [actual diagnostic report](../../docs/reports/2026-11-23-phase2d-diagnostics.md).
The commands below document reproduction within an explicitly accepted execution
scope; they grant no completed-process repeat or new build/evaluation. Offline
verification/reload of the retained evidence remains available.
This guide grants no trajectory rerun, reference acceptance, merge or Phase 2E.

The original two initial states and chronological development L0 Jacobian baseline
300 define three diagnostic states. Six repeatability processes precede three
finite-difference processes. No trajectory is integrated. The private annex, input
hashes and old campaign remain immutable; do not recreate a missing original.

## Prepare a new source-bound directory

Use the locked noneditable installation in [Contributing](../../CONTRIBUTING.md)
and a clean committed checkout. The first config is the existing private 2D
resolver with exactly `annex`, `benchmark_access`, `source_config`; the second
argument is the fixed D-038 private diagnostic annex. Preparation revalidates the
qualified initial states/species/original control labels and derives no new labels.

```sh
.venv/bin/python -B experiments/trajectory_reference/diagnostic_campaign.py prepare \
  /absolute/private/access.json /absolute/private/diagnostic-annex.json \
  /absolute/private/diagnostic-attempt-001 --source-root "$PWD"
```

The three ordinary mode-zero native input files and Newton-only old-state/h
companions are compared to the exact frozen annex. A separate pinned source copy,
patches, protocol, host scripts and all immutable identities are staged. The
manifest declares exactly nine commands, without a trajectory plan.

## Build and execute only after accepted authority

Transfer the complete new directory and verify its archive/content identities.
Within the declared one-rank/thread CPU allocation, use the same pinned modules
and compiler as D-036. The execution host needs the standard library, Python 3.12,
and the native executable; it needs no NumPy, benchmark loader or model.

```sh
module load cpu intel/2025.3 PrgEnv-intel/8.7.0 cray-hdf5-parallel/1.14.3.9
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
bash /absolute/private/diagnostic-attempt-001/bundle/build.sh
python3 /absolute/private/diagnostic-attempt-001/diagnostic_campaign.py \
  execute /absolute/private/diagnostic-attempt-001 --srun
```

Eleven compiled synthetic prerequisites, including evaluated-state retention after
ten retry-cleanup resets, precede physical calls. Exact repeat/control/echo/static-
map/IEEE checks gate stage C. The native diagnostic source additionally checks
baseline restoration after probes. A diagnostic `SUCCESS` records completion of
the fixed investigation; failed derivative windows/matrices/linear solves remain
scientific outcomes. Every failed/interrupted/unattempted process stays visible.
There is no automatic restart, completed-process repeat or trajectory retry.

## Offline evidence and reproduction

Preserve the full host directory, including failures, before deriving reports.
[Wire formats](DIAGNOSTIC_WIRE.md) describe native operand/probe/matrix streams.
The report checks raw identities and independently reconstructs Jacobians and
conditional arithmetic from those streams. Exact fixed-b polynomials, BE residuals
and linear backward errors do not verify rates/EOS or create trajectory truth.
Run the offline report and then a separate-process reload:

```sh
.venv/bin/python -B experiments/trajectory_reference/diagnostic_report.py \
  verify /absolute/private/diagnostic-attempt-001
.venv/bin/python -B experiments/trajectory_reference/diagnostic_report.py \
  reload /absolute/private/diagnostic-attempt-001
```

These create `diagnostic-verification.json` and its numeric NPZ once, refusing
overwrite, then reload/recompute without writes or native calls. Software evidence
and scientific derivative outcomes are reported separately. Missing/inconsistent
evidence fails closed; serialization success does not turn a failed sample into a
qualified reference. Keep exact-rational results and zero/undefined masks with
the rounded numeric displays.

Fresh native processes in stage A test repeatability at identical states. Exact
save/reload of derived arrays is a separate check. Neither is clean trajectory
reproduction or reference convergence. After the report and independent assessment,
stop for the next concrete numerical/protocol decision. No new solver tolerance,
trajectory rerun, reference acceptance, merge or Phase 2E follows automatically.
