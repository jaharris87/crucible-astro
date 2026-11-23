# CRUCIBLE

**A framework for learning and reduced modeling of astrophysical reaction networks.**

CRUCIBLE develops faster approximations to astrophysical reaction networks. Its
first benchmark uses the full ordered composition vector of 160 nuclear species
(molar abundance Y), temperature in GK and density in g/cm³ as inputs. The
prediction target is each species' instantaneous rate of change, dY/dt, in
`molar_abundance_Y/s`, calculated by a pinned XNet reference. Electron fraction is
derived from composition. Whole histories and their operational groups stay
together in fixed training, validation and test splits for later model fitting,
selection and final evaluation. See the [benchmark contract](docs/science/benchmark/NATIVE_RHS.md#frozen-finite-task-and-bindings).

**Current status:** Phase 0A/0B and Phase 1 are complete. Qualification covers
24,314 states from 380 histories for finite within-parent numerical emulation.
The documentation migration and Phase 2A qualified-data access are complete.
Phase 2B is [complete](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7043899683)
at PR #47 / `a81552e`: the frozen full-state MLP and zero-RHS comparator reproduce,
with zero D-024 whole-vector attainment at every profile. This negative fidelity
result remains unchanged. The [2C analytic campaign and frozen callable checks](docs/reports/2026-11-20-phase2c.md)
verify the numerical path separately from predictive fidelity. 2C, its audit
repairs and final closeout are complete through PR #50 / `75b2ec3`. Phase 2D
native reference implementation is active under [issue #44](https://github.com/jaharris87/crucible-astro/issues/44);
the reviewed protocol and bounded producer scope are accepted under D-036.
2D resumed on 2026-11-23 with offline diagnosis after primary numerical failures;
D-038 now authorizes bounded frozen-state diagnostics. Later trajectory execution
needs a separate accepted protocol; no full-horizon reference has passed. See the [diagnosis](docs/reports/2026-11-23-phase2d-diagnosis.md),
[checkpoint](docs/reports/2026-11-20-phase2d-checkpoint.md) and current
[progress](docs/PROGRESS.md) and [handoff](docs/HANDOFF.md).
Physical application, energy, rollout accuracy and speedup remain
**not evaluated**.
Use [Progress](docs/PROGRESS.md) and [Handoff](docs/HANDOFF.md) for current work and
the [final Phase 1 receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482) for closure evidence.

Repository: **[jaharris87/crucible-astro](https://github.com/jaharris87/crucible-astro), public, BSD-3-Clause**.

## Charter

CRUCIBLE will make reaction-network surrogates and reduction methods reproducible,
comparable and callable, connecting physical composition, representations, kinetics,
integration and scientific observables.

The design adapts Qiosk's separation of representation, vector source learning
and integrated evaluation to verified nuclear semantics. The current full-state
path is the initial comparison control; the
[Qiosk and Zhang-paper trace](experiments/integration/GROUNDING.md) explains this
lineage and the deliberate adaptations.

The framework must support the identity/full-state path and multiple reduction
approaches, with **one potentially vector-valued physical kinetics source**.
Reconstruction is part of the representation. Energy needs its own physical
definition and validation. [Design](docs/science/DESIGN.md) owns the scientific
contracts; [the roadmap](docs/ROADMAP.md) defines scope and later phase gates,
including the boundary before production hydrodynamic coupling.

Initial scope covers provenance-aware ingestion, reproducible baselines, reduced
dynamics, integrated evaluation, fair comparisons and a callable research
prototype. Production coupling, a universal network solver, neutrino-flavor
modeling, top-level supernova observables, autonomous active learning and
distributed training infrastructure require separate scientific cases and decisions.

Every claim must identify its network, data, split, transforms, model, integration
settings and resources, with reproducible evidence and visible failures. Passing
CI or low training loss alone cannot establish scientific validity. The maintainer
owns scientific acceptance and merge decisions.

## Read this package

For scientific use, follow these routes:

| I want to… | Start here |
| --- | --- |
| Understand what the accepted data can support | [Qualified data card](docs/data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md), then [finite benchmark and limitations](docs/science/benchmark/NATIVE_RHS.md#frozen-finite-task-and-bindings) |
| Load the accepted data and inspect its splits | [Loading guide and runnable example](docs/science/data/LOADING.md); [HDF5 contract](docs/science/data/PRIMARY_RHS_DATASET.md) and [partition checks](docs/science/benchmark/PARTITIONS.md) for details |
| Score an RHS prediction | [Native numerical profiles and reporting](docs/science/benchmark/NATIVE_RHS.md#accepted-profiles-and-exact-arithmetic), plus the runnable synthetic example below |
| Reproduce the frozen full-state baseline | [Model card](docs/model-cards/genesis_modelcard_full_state_mlp_v0_1.md) and [2B experiment guide](experiments/mlp_baseline/README.md) |
| Use the callable boundary or verify integration | [2C guide](experiments/integration/README.md), [numerical report](docs/reports/2026-11-20-phase2c.md) and [audit assessment](docs/reports/2026-11-20-phase2c-audit-assessment.md) |
| Understand physical accuracy and unevaluated uses | [Qualification and validation](docs/science/VALIDATION.md), [physical error budgets](docs/science/validation/PHYSICAL_ERROR_BUDGETS.md); pointwise fidelity does not establish energy, rollout accuracy or speedup |
| Trace scientific evidence or historical decisions | [Source evidence](docs/science/EVIDENCE.md), [decision register](docs/DECISIONS.md), [Phase 1 exit index](docs/phase1/PHASE1_CLOSEOUT.md) |
| Resume development or find the next authorized action | [Handoff](docs/HANDOFF.md), [progress](docs/PROGRESS.md), [workflow](docs/process/WORKFLOW.md) |

The real data remain local with unresolved redistribution rights.
`crucible.benchmark.load_benchmark` verifies the accepted qualification overlay,
payload and exact memberships, then returns ordinary arrays and metadata for
one named use and split. The [loading guide](docs/science/data/LOADING.md) explains
private path configuration, dimensions/units and permitted uses.

Follow [Contributing](CONTRIBUTING.md#quick-start) to install and run checks, then
try this small analytic-vector scoring example without real data:

```sh
uv run python -B -m crucible.native_fidelity \
  configs/native_fidelity/synthetic_config.json \
  configs/native_fidelity/synthetic_reference.json \
  --prediction configs/native_fidelity/synthetic_prediction.json
```

This exercises the numerical scorer; it is not a trained model or a scientific
performance result.

For planning, use the [roadmap](docs/ROADMAP.md), [backlog](docs/BACKLOG.md) and
[decision register](docs/DECISIONS.md). [Workflow](docs/process/WORKFLOW.md) is the
process source of truth; [AGENTS](AGENTS.md) routes agent work. Reporting uses the
[meeting-report template](docs/process/MEETING_REPORT_TEMPLATE.md); the
[initial bootstrap report](docs/reports/2026-11-17-bootstrap.md) is a dated snapshot.

Historical evidence is indexed through [Transition](docs/TRANSITION.md) and the
[Phase 1 exit record](docs/phase1/PHASE1_CLOSEOUT.md). The
[migration record](docs/process/DOCUMENTATION_MIGRATION.md) maps old guide paths
and pinned source recovery. Machine-specific locators stay local.

<a id="phase-0a-authority"></a>

Historical Phase 0A authority and adoption are preserved in [Transition](docs/TRANSITION.md).
Current scope and decisions are recorded in the linked handoff and decision register.
