# Native-XNet trajectory reference experiment

Phase 2D only, [issue #44](https://github.com/jaharris87/crucible-astro/issues/44),
[draft PR #51](https://github.com/jaharris87/crucible-astro/pull/51).
The maintainer [accepted D-036](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7048371383):
the exact [v2 protocol](PROTOCOL.md), SHA256
`966fbff8d2322ae8e6666063f35c1b87cced7d5ccbaf663ccae362613f98fdad`,
and its concrete producer envelope. Its preparation-time proposed header is
preserved as frozen evidence; the receipt records actual acceptance. This does
not grant a merge, named-reference acceptance, final 2D acceptance or Phase 2E.

**Incomplete, diagnosis resumed 2026-11-23:** no full-horizon reference is
accepted. The [bounded diagnostic proposal](DIAGNOSTIC_PROTOCOL.md) needs new
scientific/producer acceptance. Read the
[checkpoint](../../docs/reports/2026-11-20-phase2d-checkpoint.md) before using the
commands below: further execution requires revised accepted protocol/producer
authority, not an automatic retry of the failed campaign.

Two fixed saved states and their prescribed sparse T9/rho interpolants define
new 10 ms IVPs. They do not reproduce the original hydro trajectories. Keep all
private inputs, source copies, paths and numeric trajectories local. No model
is loaded and no fitting, learned rollout, heating or final-test use occurs.
[Grounding](GROUNDING.md) distinguishes representation, one vector kinetics
source, native integration and evaluation, with multiple original Zhang papers.

## Prepare and run the accepted campaign

Use a clean committed checkout and the locked noneditable installation from
[Contributing](../../CONTRIBUTING.md). The ignored private configuration contains
exactly `annex`, `benchmark_access` and `source_config`, each an absolute local
path. `annex` is the accepted private proposal-inputs JSON (exact digest in the
protocol); `benchmark_access` is the existing qualified-loader resolver;
`source_config` is the retained original reference preparation configuration.
Do not edit accepted artifacts or replace digests to recover missing files.

```sh
.venv/bin/python -B -m crucible.trajectory_reference prepare \
  /absolute/private/access.json /absolute/private/campaign-001 --source-root "$PWD"
```

Preparation verifies the exact two input NPZs, initial memberships/state/species
and original source/network/EOS/table hashes. It stages separate original and
adapted files with seven explicit diffs. Physical RHS evaluation arithmetic is
unchanged; observational branch assignments and read-only table visibility are
recorded source changes. The native BE numerical path is explicitly adapted.
All sources, forcing, meshes, control expectations and executable inputs are
bound before build. No old object or executable is reused.

Transfer this new private campaign directory to the authorized CPU host and
enter the allocation with the pinned modules. Use one rank/thread, the same
D-019 compiler flags and no compiler fallback:

```sh
module load cpu intel/2025.3 PrgEnv-intel/8.7.0 cray-hdf5-parallel/1.14.3.9
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
bash /absolute/private/campaign-001/bundle/build.sh
python3 /absolute/private/campaign-001/campaign.py \
  /absolute/private/campaign-001 --srun
```

The host runner uses only the Python standard library and compiled executables;
it provides no Python RHS callback. Ten independent compiled synthetic scenarios
must pass first, including actual-adapter polynomial/nonlinear oracles, native
forcing endpoints/knots, projection refusal, fatal computed nonfinite values and expected failures. Then both exact
initial RHS controls precede ten trajectories and six Jacobian diagnostic states.
Every declared case/level remains visible after a numerical failure. A failed
exact control stops the campaign. No automatic numerical retry, replacement case,
additional level or relaxed tolerance is permitted.

The single declared infrastructure restart requires
`--infrastructure-restart --restart-reason 'actual infrastructure reason'`.
Use it only after confirming the original process is terminal. It retains the
interrupted attempt, verifies completed artifacts and does not repeat completed
controls. A numerical failure is not an infrastructure interruption.

## Verification, reload and reproduction

After retaining the full raw host directory locally, run:

```sh
.venv/bin/python -B -m crucible.trajectory_reference verify /absolute/private/campaign-001
.venv/bin/python -B -m crucible.trajectory_reference reload /absolute/private/campaign-001
```

`verify` creates new JSON/NPZ derived artifacts and refuses overwrite. It checks
all 18 declared control/trajectory/diagnostic processes, raw identities/status,
forcing arithmetic, complete outputs/horizons, baryon/positivity/domain, actual
BE residual/projection, all three mesh comparisons, tighter nonlinear controls
and all 18 directional sweeps. Diagnostic derivatives are recomputed from saved
F probes, separately from the native production Jacobian. An expected software
negative fixture never becomes a successful nuclear trajectory.

`reload` writes nothing: fresh-process dtype/shape/array-byte checks and all raw
metrics must recompute exactly, including retained failure/undefined masks.
Run the same preparation/source and accepted sequence once in a new directory
with a second fresh build, preserving the first. This is the declared reproduction,
not a new selection trial. Verify/reload it, then compare:

```sh
.venv/bin/python -B -m crucible.trajectory_reference compare \
  /absolute/private/campaign-001 /absolute/private/campaign-repeat-001 \
  /absolute/private/reproduction.json
```

Source/protocol/inputs and linked libraries must agree. Required original passes
must independently pass again; requested trajectories/inventories/moments must
meet the predeclared numerical-equivalence allowance. Serialization identity,
numerical reproduction, measured refinement and physical accuracy stay separate.
Failures leave 2D incomplete and require the concrete next decision in #44.

## Retained evidence and costs

`accepted.bin` contains all accepted states/F/residuals/moments and control
values; `accepted-forcing.bin` aligns actual T9/rho with those times. Separate
streams retain every Jacobian baseline and column stencil/increment, Newton residual,
projection, branch change and counter checkpoint. Raw logs, terminal status,
loaded maps/library hashes and native process memory remain available on failure.
Fatal rejected-state/workspace snapshots distinguish unavailable current values
from actual nonfinite coefficients/F. No nonfinite physical evaluation can be
recovered by trying another finite-difference stencil.
JSON/NPZ reports preserve all component/vector errors and missing-output masks.

Record setup/loading, native CPU/wall, parent/launcher wall, incremental I/O,
post-phase runtime-snapshot persistence, peak RSS and actual artifact storage.
The native physical-phase timer includes diagnostics and incremental output; it
is not an isolated RHS benchmark. D-013 estimates are not caps. No matched-accuracy
speedup or physical adequacy follows from these timings or numerical passes.
