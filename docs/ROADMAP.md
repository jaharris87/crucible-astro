# Phased roadmap and exit criteria

These are engineering phases, distinct from ENACT-AI's funding Phase I/II. Maintainer-directed transition choices are recorded in [DECISIONS](DECISIONS.md); the original reviewed version is preserved through [TRANSITION](TRANSITION.md). No calendar deadlines are assigned from historical month/day labels. The [backlog](BACKLOG.md) makes immediate work issue-sized; later phases are deliberately conditional. Scientific gates use [VALIDATION](VALIDATION.md), not a blanket training-loss threshold.

## Milestone interpretation

The final narrative, PDF pp. 4–6 [P1 in EVIDENCE](EVIDENCE.md), supplies:

- **NS1:** representative CCSN and NSM trajectories with reference network solutions. A tiny fixture or one source simulation is enabling evidence, not completion.
- **NS2:** implemented and verified callable prototype accommodating proposed approaches. A draft interface or one model is enabling evidence; Phase 5 demonstrates distinct approaches through the stabilized boundary.
- **NS3:** quantitative stand-alone comparison of reduced **r-process** representations against full-network post-processing. A CCSN pilot can prepare tools but cannot alone complete NS3.
- Common metrics: abundance evolution, energy generation and inference cost. Metric 3's proposed hundred-fold r-process energy-inference reduction is an objective; “suitable accuracy” still requires a benchmark and scientific threshold. No achieved speedup is claimed here.

The broad summary/section-4 integration language and nuclear-specific section-3 production-coupling deferral are recorded as a scope ambiguity in D-008. This roadmap follows the explicit nuclear-specific boundary while requesting collaborator confirmation before any coupling commitment.

## Phase 0A — Discovery, decisions and documented design

**Deliverables:** this navigable charter/design/workflow/backlog/evidence package, classified decisions, maintainer packet, independent review and disposition, durable handoff.

**Non-goals:** all implementation, environment setup, Git/GitHub mutation, training, data generation, reference edits. These are assignment limits, not future policy.

**Dependencies/open decisions:** accessible reference sources and selected workspace; future scientific choices can remain unresolved with gates and owners.

**Exit evidence:** every requested deliverable mapped to a file; consequential claims checked against source; independent fresh-context review preserved; consequential findings fixed or explicitly disposed; no conflicting rules, hidden model commitments, unbounded compute or untraceable acceptance; local links checked; maintainer decisions and exact next scope recorded.

**Human point:** review recommended bootstrap/scientific direction; authorize any future phase separately. **Milestone relation:** design support for NS1–NS3, no scientific milestone claimed complete.

## Phase 0B — Repository and development-workflow bootstrap

**Deliverables:** authorized repository identity/visibility/license; minimal Python package/tool setup and reproducible development environment; adopted agent/contributor guidance; simple issue/PR templates and fast CI; lightweight phase/issue/milestone progress with dependencies, status and linked PRs; reusable meeting-report template and initial bootstrap report linked from README/handoff; one completed real workflow demonstration (B04).

**Non-goals:** real-data training, decoder/model selection, large artifacts, broad review bots or production coupling. Synthetic fixture validation is the only planned scientific-adjacent behavior.

**Dependencies/open decisions:** Phase 0B authorization supplied 2026-11-17; accepted owner `jaharris87` and public visibility (D-001), with license/release readiness confirmed before publication; accepted workflow/scope (D-010), with D-011 resource caps later removed by D-013; final environment choice after checking collaborator constraints. D-002/D-003 and later scientific choices are not prerequisites for the synthetic bootstrap demonstration. Package tooling choices are reversible; public release/license decisions need maintainer authority.

**Exit evidence:** progress/reporting artifacts match actual issue/PR evidence and unsupported scientific results remain “not yet evaluated”; fresh checkout environment and fast checks reproduced; intentionally permuted species metadata rejected for the correct reason and valid control accepted; demonstration has governing issue, test-first failure, isolated implementation, self-review, pushed exact-SHA draft PR, fresh independent review, preserved dispositions, human merge decision, merged-SHA checks and closeout. If the human defers merge, the phase remains awaiting that exit rather than claiming completion.

**Human point:** repository settings/license and actual merge. **Milestone relation:** infrastructure toward NS1 data checks and NS2 contracts, no qualified physics.

## Phase 1 — Verified data semantics, provenance, ingestion and partitions

**Deliverables:** audited producer/run association, state/units/species/conditions and target contract, robust reader for one documented format, masks, tiny real fixtures when redistribution is confirmed (otherwise synthetic public fixtures plus local real-data checks), dataset and grouped split manifests, coverage inventory, benchmark definition and living Genesis data card linking raw and derived identities. [Execution authority](PHASE_1_AUTHORITY.md) was supplied 2026-11-17; [milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2) tracks actual gates.

**Non-goals:** model search or accepting labels by shape; wholesale dataset conversion before a bounded audit; presumed fixed Ye, inferred NSE from zero vectors, or invented provenance.

**Dependencies/open decisions:** B04; accepted CCSN particle-trajectory emphasis (D-002), D-004 target/conditions, D-005 energy and constraints, D-007 reference/tolerances/storage. Trace current BE label staleness and initial/NSE records; resolve or quarantine. If regeneration is necessary, propose a separately authorized task using an authorized copy of producer code.

**Exit evidence:** independently interpreted records match reader outputs; expected format/unit/species failures detected; raw/build/run identity and limitations documented; usable versus invalid labels counted; leakage audit shows group disjointness; reference accuracy justified and task/tolerances signed off; data card current with source/template revision or explicit access gap, qualification status and access/rights. Enough independent groups for the intended claim, or explicitly limit the benchmark claim. Reviewed human merges and passing integration checks are required before closing the phase milestone/native goal. If the required real semantics remain unknown, this phase cannot claim complete data qualification; limited exploration is not full training qualification.

**Human point:** accept data subset, physical task, exclusions, reference/tolerances and any new generation scope. **Milestone relation:** establishes NS1 evidence; full NS1 still needs representative CCSN and NSM coverage, which may require expanding the pilot.

## Phase 2 — Small reproducible end-to-end baseline

**Deliverables:** identity/full-state representation, one selected simple baseline
with a deterministic comparator, train-only preprocessing, bounded fitting,
persistence/reload and pointwise metrics on the accepted numerical benchmark.
Provide straightforward named-view/version/use/split loading before the first fit.
Verify integration on an independent analytic problem, then add the held-out
rollout harness and small audited real demonstration after their separate reference
gate. Create/update an official-Genesis-guided model card binding the actual model,
training data/split, evaluation evidence, intended use and limitations; record the
guidance revision/access gaps. No trained-model card is created during Phase 1.

**Non-goals:** mandatory compression, large hyperparameter sweep or proof of production usefulness. Finite-step modeling must use its own contract if chosen.

**Dependencies/open decisions:** Phase 1 qualified labels and authorized experiment scope; accepted RHS-first baseline sequence (D-003) and qualified D-004 state/conditions; chosen CPU-capable tooling. Identity/full-state baseline is the selected starting path. Finite-step prediction is retained for later exploration with a separate contract; model-family and detailed science choices remain open.

**Accepted staging (D-028):** pointwise work and analytic integration checks can
precede a real rollout reference. Before real rollouts, accept the initial-state,
time-dependent forcing/interpolation, horizon/output and observable contract;
prepare a separately authorized pinned-XNet trajectory/convergence calculation.
Current fresh pointwise labels do not qualify a continuous solution, historical
solver convergence or energy. Retain the real-rollout exit below; this staging
does not move it to Phase 3 or authorize producer execution. [Transition work and
the accepted documentation plan](BACKLOG.md#post-audit-transition) remain bounded;
D-027's migration needs later separate authorization.

**Exit evidence:** clean rerun from recorded artifacts reproduces metrics within declared tolerance; independent analytic solution passes; trained transforms cannot depend on held-out data; reload agrees; full declared held-out horizons attempted and all failures reported; baseline reference, energy availability and inference/integration cost recorded; model card resolves to the actual artifact/data/split/evidence and states unevaluated regimes. Update that card when any bound artifact or material evaluation/limitation changes throughout later phases. Method performance may be poor: acceptance here establishes an honest reproducible pipeline, not scientific deployment suitability. Any pipeline failure remains a blocker.

**Human point:** accept baseline adequacy as a comparison control and set performance hypotheses, not retroactive test thresholds. **Milestone relation:** early NS2 path and NS3 comparison machinery.

Pointwise fidelity, integrated scientific accuracy and matched-accuracy total
computational cost remain separate results. Later cost comparisons include solver
failures/steps/Jacobian work, preprocessing and setup boundaries; reference audit
job runtime alone is not a surrogate speedup. Let the first end-to-end results
motivate shared interfaces and reduction choices; no plugin or latent architecture
is selected by this plan. The [draft launch prompt](PHASE_2_LAUNCH.md) is unexecuted.

## Phase 3 — Initial reduced dynamics and trajectory validation

**Deliverables:** one selected reduction plus dynamics; explicit derivative/step transformation; separate reconstruction/RHS/rollout results; decoded abundance and energy diagnostics; closure/domain/stability analysis.

**Non-goals:** universal latent dimension, claims from reconstruction alone, expanding abstractions before implementations need them.

**Dependencies/open decisions:** reproducible Phase 2; D-006 first reduction, dimension/tuning protocol and treatment of violated constraints; regime transitions and energy contract.

**Exit evidence:** independent derivative consistency checks; matched held-out trajectories and integration settings; full failures and cost accounting; comparison against identity control with uncertainty and justified thresholds. A negative result is acceptable as a documented research outcome if it supports a human go/no-go decision, not as a claim of an accurate surrogate.

**Human point:** retain, revise or reject the method; authorize next controlled comparison. **Milestone relation:** NS3 preliminary evidence, r-process qualification required for actual NS3 credit; NS2 second implementation experience.

## Phase 4 — Controlled comparison of selected methods

**Deliverables:** small method set selected from evidence, locked benchmark/configurations and disclosed tuning procedures/resource use, abundance/energy/cost and failure tables, repeatability evidence and justified down-selection.

**Non-goals:** exhaustive architecture tournament, post hoc test-set tuning, unexplained speed claims or importing silicon-burning QSE assumptions into r-process cases.

**Dependencies/open decisions:** Phase 3 diagnostics; maintainer selects scientifically distinct families and relevant regimes. Expand NS1 coverage if pilot is insufficient. Decide whether grouped physics reduction is valid before implementing it.

**Exit evidence:** at least two actual reduced approaches compared to the full/reference baseline on the same applicable held-out task; all planned metrics including failures and end-to-end costs published in run records; r-process reference comparison present for NS3; reproduction and independent audit packet completed; down-selection records accuracy-cost tradeoffs rather than a single loss winner.

**Human point:** accept scientific interpretation and selected method(s), decide whether objectives were met, revise scope openly if not. **Milestone relation:** principal NS3 evidence and final coverage check for NS1; hundred-fold objective assessed only under its defined scope.

## Phase 5 — Packaged prototype, examples and scientific reporting

**Deliverables:** versioned callable interface, at least two materially different approach adapters, reproducible bounded examples, artifact retrieval/verification and compatibility checks, support/limitation statement, benchmark release package and scientific report.

**Non-goals:** production hydrodynamics embedding, guaranteed all-network support, or automatic active-learning campaigns.

**Dependencies/open decisions:** evidence from comparison; D-001 release rights/storage, D-008 scope; stabilize the interface around proven use, not anticipated engines.

**Exit evidence:** a fresh consumer runs both approach examples through the documented contract; incompatible species/units/artifacts and unavailable capabilities fail clearly; results match retained evidence within agreed tolerance; release artifacts resolve and verify; human accepts scientific claims and release terms; independent boundary audit disposed.

**Human point:** scientific acceptance, public release and any next production/coupling/active-learning project. **Milestone relation:** NS2 delivery; NS1/NS3 results and limitations packaged for collaborators. Funding milestone completion remains a collaboration judgment supported by evidence, not inferred from engineering phase labels.
