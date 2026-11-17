# Provisional scientific and software design

Status: provisional design, not implemented API. Maintainer accepted CCSN particle trajectories first and both target types, starting with the identity/full-state instantaneous-RHS path (D-002/D-003). Remaining scientific choices and the limits of those selections are in [DECISIONS](DECISIONS.md). Evidence identifiers resolve in [EVIDENCE](EVIDENCE.md). Use concrete functions and records first; introduce a shared protocol only when two working implementations require it.

## Responsibilities and minimal layout

```text
crucible-astro/
  README.md, AGENTS.md, CONTRIBUTING.md, LICENSE, CITATION.cff
  pyproject.toml                 # packaging and small development tool configuration
  <one environment lockfile>    # selected in bootstrap; no copied legacy requirements
  src/crucible/
    data.py                     # validated records and selected reader, when needed
    transforms.py               # fitted maps and derivative maps
    baseline.py                 # first actual baseline
    evaluate.py                 # shared physical-space metrics
  tests/
    fixtures/                   # tiny synthetic and approved real fixtures
    test_*.py
  configs/                      # versioned experiment definitions
  manifests/                    # dataset, split, and artifact identities
  experiments/                  # small run records, metrics, failure summaries
  examples/                     # bounded callable demonstration
  docs/                         # this package, decisions, research notes
  .github/                      # minimal issue/PR templates and fast CI
```

The B02 candidate adds only the minimal package/check scaffold; the scientific layout above remains provisional. Create directories when their first issue needs them. `crucible` is a proposed import name, subject to name availability at packaging time. Recommend Python for the first data and benchmark path; defer ML library selection until the baseline issue. A thin future adapter may call XNet or another reference solver, but CRUCIBLE should neither vendor whole reference trees nor own their build systems by default. No base-class hierarchy, plugin discovery, distributed scheduler, model registry service, mandatory autoencoder, or hydrodynamics binding in bootstrap.

## Scientific contract before a model

Describe one task as `du/dt = F(u, c, t)` or a separately typed finite-step map. Here `u` is the explicitly declared physical state, `c` the required external conditions; neither symbol fixes abundance convention, network, nor thermodynamic closure. If thermodynamics are coupled, their evolution and energy terms must be specified as part of the selected task rather than hidden inside a composition surrogate.

The data contract must settle:

| Record | Required meaning and failure behavior |
| --- | --- |
| Network identity | Ordered species records with stable identity, A, Z, optional isomer identity; rates/masses/screening/weak-input versions; full versus selected inventory. Names alone are insufficient. |
| Physical state | Shape `(..., n_species)` and axis order; abundance convention, time/temperature/density units, normalization and missing-species policy. No silent permutation or unit conversion. |
| Conditions | Named values and units, prescribed/evolved/derived status, interpolation policy, availability at inference. T, density, Ye, neutrino fields, or other controls are candidates to verify, not mandatory universal inputs. |
| Sample identity | Dataset, parent simulation, trajectory/zone, record/step identity, time, regime, and split group; these accompany predictions and metrics. |
| Target | Kind, units, state/conditions/time at evaluation, validity and reason. `instantaneous_rhs`, `step_average`, and `finite_step_update` cannot be interchanged. |
| Energy | Observable definition and sign, units (for example energy per mass per time only if established), nuclear versus deposited/net heating, neutrino/rest-mass/EOS treatment, and alignment. |
| Provenance | Exact generator and modifications, inputs, build, run, raw files and extraction recipe. Unknown values remain explicit; they cannot authorize training. |

The observed XNet source distinguishes trial state `yt`, accepted/current `y`, and old `yo`; writes raw `y` to binary records while HDF mass fractions use `A*y`; and writes NSE zero derivative placeholders. In backward Euler, the inspected derivative and corrected state are successive Newton iterates at the same new time; this is normal implicit-solver bookkeeping, not proof of a solver defect. Source intent does not establish the existing run's generating build or label alignment to the learning-error budget [N1–N4]. Phase 1 must settle the relationship empirically and from the producer call graph. Do not convert supplied nuclear derivatives with the chemical `M*omega/rho` formula [C2].

## Small callable boundaries

These are semantic sketches, not a requirement to implement all names/classes:

| Capability | Proposed input → output | Must be checked |
| --- | --- | --- |
| Read audited data | manifest + selected trajectory IDs → records and validity masks | Checksums, dimensions, ordered identities, units, record completeness; unknown schema fails explicitly |
| Fit a transform | training records + configuration → immutable fitted artifact | Training IDs only, no validation/test fitting; constants/floors handled explicitly |
| Encode / decode | physical state ↔ representation | Identity is valid; input schema and saved transforms match; reconstruction evaluated in physical space |
| Transform derivative | state, physical RHS, conditions and their derivatives if required → representation RHS | Correct chain rule; unsupported nondifferentiable cases rejected/masked |
| Predict RHS | time, represented state, declared conditions → signed vector in declared coordinate units | Dimensions, finite values, compatibility, out-of-domain status; no step-size meaning smuggled into RHS |
| Predict a step (if selected) | start state, start time, step size, required condition history → end state or increment | Interval semantics, irregular cadence, causal available inputs; separate from RHS interface |
| Integrate | initial state, conditions/history, time interval, solver policy, model artifact → trajectory + diagnostics/status | Solver tolerances, rejected steps, failures, fallback counts, domain exits, requested outputs |
| Read energy | declared state/dynamics/conditions and energy policy → named observables + status | Reference consistency; unavailable readout is explicit, never fabricated zero |
| Evaluate | prediction + reference + fixed metric specification → metric record | Identity alignment, masks, units, denominators, failures and cost components |

Phase 2 implements only the chosen baseline path. Phase 3 adds a reduced method and extracts only genuinely shared behavior. Phase 5 stabilizes a small inference boundary demonstrated with at least two materially different approaches; callers use declared capabilities rather than neural-network internals. Artifacts declare whether they offer RHS or finite-step prediction. No universal `predict` whose output meaning depends on undocumented mode flags.

## Representation and derivative consistency

For fixed preprocessing `x=S(u)` and encoder `z=E(x)`, the column-vector chain rule is

```text
dz/dt = J_E(x) J_S(u) F(u,c,t).
```

If the composed representation is `z=G(u,c,t)`, it instead needs

```text
dz/dt = (partial G/partial u) F + (partial G/partial c) dc/dt + partial G/partial t.
```

A conditioned encoder may therefore require condition derivatives that are unavailable at inference. The simpler unconditioned map is a recommendation for an initial comparison, not a permanent restriction. Test affine and nonlinear transforms against independently computed derivatives. For the conventional nuclear definitions, **if verified** as `X_i=A_i Y_i`, fixed A implies `dX_i/dt=A_i dY_i/dt`; this does not settle the producer's normalization, excluded species, or energy convention.

Offsets vanish for affine maps. Do not apply a state scaler or PCA centering unchanged to a derivative, independently normalize targets and call them coordinate derivatives, or use a local Jacobian to transform a finite interval as though it were instantaneous. A finite-step target transforms through its two endpoint states. Clipping/flooring destroys information and may be nondifferentiable; retain masks and quantify effects instead of claiming an exact invertible map. Output scaling used only for optimization must be inverted before integration.

A nonlinear reduced state can lose information required for closed dynamics even with excellent reconstruction. Test history dependence/closure error on held-out trajectories before adding state or memory. Reduced dimension, constraints, decoder design, and model family remain experimental choices [D-003, D-006].

## Data and artifact stewardship

Recommend a versioned tiny fixture set. D-013 removes the former proposed storage cap; fixture scope and redistribution still require review. Start with synthetic data; add a few audited real records only after provenance, redistribution, and expected outputs are established. Include valid and deliberately invalid species ordering, unknown schema, units, and validity cases. No copied 560 MB `postp.h5` in Git.

A dataset manifest (proposed JSON initially, using standard-library tooling) records:

- Schema version, dataset ID, description, license/access conditions, custodian and immutable location plus SHA-256 and byte size of each payload. A local path is a resolver hint, never identity.
- Generator repository/revision, dirty diff or patch checksum, relevant source inventory, executable checksum, compiler/build flags, linked libraries, environment, hardware when material, and command/configuration/input checksums. A Git SHA alone cannot describe the modified reference source [N4].
- Network, rates/masses and other nuclear inputs; ordered species identities and hash; every quantity's units, state convention, dimensions, output cadence and interpolation.
- Parent simulations, trajectory IDs, initial compositions, thermodynamic history and closure, source-target timing/alignment, accepted/trial/interval semantics, solver settings and convergence evidence.
- Record-level validity flags with reasons (`unknown_provenance`, `nse_placeholder`, `alignment_unverified`, `nonfinite`, etc.); separate state, RHS, energy, and rollout validity. A state may be useful when its derivative is not. Never infer NSE solely because the derivative is zero.
- Reader/extraction revision, selection recipe, raw-parent checksums, derived-output checksums, audit result and human acceptance reference. Missing provenance produces quarantine or a narrower explicitly described use, not invented metadata.

Split manifests contain exact group memberships, parent provenance, construction rule/seed and digest, with no overlap between related simulation families. Transform artifacts bind fitted parameters to training membership and input schema. Model artifacts bind weights/parameters, architecture/configuration, target kind, species/units, transforms, dataset/split, seeds, training/search procedure and resource use, optimizer/checkpoint selection, software environment, and artifact checksums. Save/load must reproduce predictions within a predeclared serialization tolerance.

Maintain a living data card from S01 through each derived qualified subset, using
the actual official Genesis template when accessible and recording its revision.
Link detailed manifests/audits/benchmark records; distinguish the raw collection
from derived identities, rights and qualifications. Private data can have a public
card without being public. From Phase 2 onward each model artifact has a current
model card binding that actual artifact, training data/split and evaluation
evidence to its uses and limitations. Update it when those bindings or claims
change. Record unavailable template access explicitly; do not invent conformance,
trained artifacts/results, a registry or agent cards. See [guidance evidence](phase1/GENESIS_GUIDANCE.md).

Use institutional/object storage for larger immutable datasets and artifacts, with human-selected custodian, access/retention and recovery policy. Do not assume AmSC credentials or deployment exists. A DOI/archive can accompany public releases; day-to-day storage need not begin with a new service. Track manifests and small metric tables in Git; keep bulk arrays/checkpoints/logs external. Document retrieval and verify checksums before use. Avoid opaque executable serialization for untrusted artifacts; choose simple data formats where practical.

## Experiments and reporting linkage

Each experiment record links issue, candidate source SHA (and patch if applicable), dataset/split/transform/model digests, command/configuration/environment, seed(s), execution resources, start/end/status, raw metrics, figures, and all failures. A result is provisional until checks and qualification status are recorded. Summaries link these records; hand-edited dashboard values are not evidence. Reporting and external audit packets are defined in [WORKFLOW](WORKFLOW.md).
