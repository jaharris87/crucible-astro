# Distinct assembly qualification guide

The maintainer [explicitly accepted D-039](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7109353327)
on 2026-11-23: the distinct numerical RHS **and** its bounded qualification
scope. The [reviewed protocol](ASSEMBLY_QUALIFICATION_PROTOCOL.md) retains its
preparation-time proposal header; the actual acceptance receipt controls authority.
Implementation review must pass at the exact pushed candidate before execution.
This guide records a procedure; it grants no additional build, repeat or run.

`native-XNet-b64-productsum113-b64-v1` preserves native binary64 coefficients,
physics and physical Y coordinates, promotes b/Y before abundance products and
sums, and returns binary64 F. This changes digital RHS identity. Original D-019,
the frozen negative MLP baseline, inputs and failures remain unchanged. Frozen-MLP
compatibility is unestablished; no learned-model integration is included.

## Prepare locally without producer calls

Use the locked noneditable installation from [Contributing](../../CONTRIBUTING.md)
and a clean committed checkout. The private preparation config has exactly:

```json
{
  "trajectory_prepare_config": "/absolute/private/original-prepare-config.json",
  "diagnostic_root": "/absolute/private/completed-d038-directory",
  "standard_inputs": {
    "development": "/absolute/private/original-development-L0.bin",
    "validation": "/absolute/private/original-validation-L0.bin"
  }
}
```

The first entry is the existing D-036 resolver with `annex`, `benchmark_access`
and `source_config`. The second locates retained D-038 evidence, not a newly run
baseline. Standard inputs must match the predeclared original hashes. The annex
below is the unchanged D-038 three-state annex. No private input is fetched from
CI, silently regenerated or substituted.

```sh
.venv/bin/python -B experiments/trajectory_reference/assembly_campaign.py prepare \
  /absolute/private/assembly-prepare-config.json \
  /absolute/private/diagnostic-annex.json \
  /absolute/private/assembly-attempt-001 --source-root "$PWD"
```

Preparation verifies the existing qualified development/validation states, species,
original controls, chronological Newton300 record, original source bindings and
retained baseline identities. It stages separate source and immutable inputs.
Two new tight-input copies change only the declared sixteen nonlinear-control
bytes; their expected hashes were fixed before execution. The old tight L3 input
is not substituted. A retained helper-preparation receipt identifies its unused
nine-process diagnostic plan; the actual assembly manifest has thirteen plans.

Record source/tree, preparation and archive hashes. Transfer the complete directory
to a fresh private host location and reverify identities before building. Original
reference projects and inputs stay read-only. Retain every failed preparation or
build separately, with the reason and source diff.

## Build and execute the accepted fixed plan

The pinned CPU environment remains Intel 2025.3, PrgEnv-intel 8.7.0 and parallel
HDF5 1.14.3.9, with sequential MKL and one native rank/thread. Use the accepted host
script pattern from D-038, pinning Python/compiler/wrapper executable identities
and preserving build/environment/library receipts. Only the new assembly module
adds strict floating-point compilation; original producer-object flags remain
unchanged. No global FP-mode repair or lower-precision fallback is permitted.

Within that allocation:

```sh
module load cpu intel/2025.3 PrgEnv-intel/8.7.0 cray-hdf5-parallel/1.14.3.9
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
bash /absolute/private/assembly-attempt-001/bundle/build.sh
python3 /absolute/private/assembly-attempt-001/assembly_campaign.py \
  execute /absolute/private/assembly-attempt-001 --srun
```

The host runner uses standard-library offline science gates, without a Python RHS
callback. All eleven original compiled synthetic scenarios and five new precision/
arithmetic/refusal scenarios must pass before physical work. The precision fixtures
test actual binary128 representation, promotion, conversion, subnormal/tie behavior
and FP modes. A compiler supporting a kind name alone is insufficient.

Six identity processes precede three factor-one frozen derivative processes.
Original F, coefficients and conditioning must reproduce retained D-038 bits;
the initial original-F controls also match D-019. Exact rational assembly and
directional checks gate first-step work. A process success flag alone cannot pass
these gates.

Two standard first-step processes request h=1e-4 s from the original initial
states. Each calls native `solve_be` once, retaining its ten attempts and thirty
Newton iterations per attempt, then stops at acceptance or failure. Only if both
standard attempts pass are the two declared tight counterparts run. Every failed,
interrupted, refused and conditionally unattempted item stays in the manifest.
An ordinary numerical failure is an outcome; identity/corruption/nonfinite failures
stop dependent physical work. No case, forcing, tolerance or FD-factor change is
an automatic repair.

A reduced accepted step may end before 1e-4 s. Record requested and achieved times
and all attempted h values. That endpoint does not complete the original interval;
different standard/tight endpoints do not establish same-time agreement. Neither
is a 10 ms trajectory reference.

## Preserve, verify and reload offline

Preserve the complete raw host directory, including source patches, executable/
library/environment identities, inputs, stream files, status, scheduler and cost
receipts before deriving anything. [Wire formats](ASSEMBLY_WIRE.md) distinguish
original/variant F, binary128 workspaces, physical-call IDs and Newton phases.
Retain the last evaluated workspace separately from retry-reset arguments and
the Jacobian baseline. Forensic exports must not call the producer again.

```sh
.venv/bin/python -B experiments/trajectory_reference/assembly_report.py verify \
  /absolute/private/assembly-attempt-001
.venv/bin/python -B experiments/trajectory_reference/assembly_report.py reload \
  /absolute/private/assembly-attempt-001
```

Offline analysis checks immutable identities, complete attempted/conditional work,
precision and exact arithmetic bounds, derivative windows, Newton/LU associations,
unchanged residual/domain/projection/baryon criteria and requested versus achieved
endpoints. Keep exact bounds, masks and numeric arrays, without pickle. Fresh-process
reload recomputes checks and array identities from raw records; it performs no
physical call. Distinguish software verification from scientific qualification.

Measure loading/setup/solver/persistence costs, CPU/wall, RSS and raw/derived
storage, with unavailable scopes explicit. Precision and persistence overhead are
part of this numerical implementation; no matched-accuracy speedup is established.
Fresh native repeats, derived-byte identity and offline recomputation are separate
from clean full-trajectory reproduction.

Stop after qualification reporting and independent actual-artifact assessment.
D-039 permits one fresh build and at most two prephysical build/preflight repair
builds. It permits no postphysical rebuild, completed-process repeat, infrastructure
restart, numerical-failure rerun or full trajectory continuation. The later small
10 ms reference campaign still needs its own accepted protocol/producer decision.
Keep the full 2D goal and #44 incomplete; reference acceptance, merge and final
2D acceptance remain human decisions. Phase 2E and final-test model use are excluded.
