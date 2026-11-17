# CRUCIBLE

**A framework for learning and reduced modeling of astrophysical reaction networks.**

Repository: **[jaharris87/crucible-astro](https://github.com/jaharris87/crucible-astro), public, BSD-3-Clause**. Phase 0B bootstrap only; [live closeout status and final integration evidence](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582) are authoritative for completion. This candidate snapshot follows completed B01–B03 and introduces B04's synthetic manifest validator in [PR #7](https://github.com/jaharris87/crucible-astro/pull/7). Clean noneditable setup, lint/format and 42 tests pass locally; the ordered-to-set mutation is caught and restored. Independent review, human merge and merged-result checks must be recorded before Phase 0B closes. [B03 integration](https://github.com/jaharris87/crucible-astro/pull/6#issuecomment-6959958285) includes draft-PR CI failure/pass evidence, actual protections and reviewed D-012 model policy. No trained model or qualified dataset exists; scientific results are **not yet evaluated**. Phase 1 requires separate authorization.

## Charter

CRUCIBLE will make reaction-network surrogates and reduction methods reproducible, comparable, and callable. Its enduring research object is the relationship between physical composition, representations, kinetics, integration, and scientifically useful observables. ENACT-AI/Genesis supplies initial use cases and reporting obligations, not the project's lifetime or a requirement to include every funding workstream.

The framework must admit a full-state/identity representation and multiple reduction approaches. The expected nuclear task has **one physical kinetics source function**, possibly a vector of species or reduced-coordinate derivatives. A reconstruction decoder is part of a representation; chemical surface/deposition heads are not nuclear requirements. Energy readout needs an explicit physical definition and validation, whether recovered from dynamics or predicted separately.

Initial scope: provenance-aware data ingestion, reproducible baselines, reduced dynamics, integrated trajectory evaluation, fair comparisons, and a small callable research prototype. Production hydrodynamic coupling, a universal network solver, neutrino-flavor modeling, top-level supernova observables, autonomous active learning, and distributed training infrastructure are outside the initial implementation scope. They require separate scientific cases and decisions.

Success means a collaborator can identify exactly which network, data, split, transforms, model, integration settings, and resources produced a claim; reproduce its bounded benchmark; and see where it fails. CI success and training loss are insufficient scientific evidence. The maintainer owns scientific acceptance and merge decisions.

## Read this package

| Need | Document |
| --- | --- |
| Phase exits and NS1–NS3 mapping | [Roadmap](docs/ROADMAP.md) |
| Repository layout, provisional interfaces, provenance | [Design](docs/DESIGN.md) |
| Scientific qualification and performance evidence | [Validation](docs/VALIDATION.md) |
| Issue-to-merge cycle, orchestration, reporting, external audits | [Workflow](docs/WORKFLOW.md) |
| Active project guidance and reusable reviewer briefs | [AGENTS](AGENTS.md), [agent briefs](docs/AGENT_BRIEFS.md) |
| Python environment and development checks | [Contributing](CONTRIBUTING.md) |
| Bounded first issues and complete Phase 0B demonstration | [Backlog](docs/BACKLOG.md) |
| Phase/issue progress and collaborator reporting | [Progress](docs/PROGRESS.md), [meeting-report template](docs/MEETING_REPORT_TEMPLATE.md), [initial bootstrap status](docs/reports/2026-11-17-bootstrap.md) |
| Accepted requirements, recommendations, open decisions | [Decision register and maintainer packet](docs/DECISIONS.md) |
| Source locators, verified observations, limitations | [Evidence](docs/EVIDENCE.md) |
| Completion status and next authorized action | [Handoff](docs/HANDOFF.md) |
| Historical Phase 0A review and findings disposition | [Review record](docs/REVIEW.md) |
| Maintainer adoption, licensing evidence and preserved history | [Transition record](docs/TRANSITION.md) |
| Invoked Phase 0B scope and checkpoints | [Phase 0B launch prompt](docs/PHASE_0B_LAUNCH.md) |

The policy source of truth is the workflow; the scientific contracts are in design and validation; decisions are recorded only in the decision register. Other documents link to those sources rather than introducing separate rules. Machine-specific reference locations live only in the evidence inventory. All proposed runtime paths and artifact identifiers are portable.

## Phase 0A authority

The completed Phase 0A assignment permitted reading references and creating/revising this local design package. Its limits excluded repository creation, branches, commits, pushes, PRs, reference edits, environment installation, data generation, training, HPC jobs and framework implementation. Those limits belonged to that assignment and are **not permanent development policy**. The subsequent maintainer transition permitted local documentation changes and activation of root [AGENTS.md](AGENTS.md) only. On 2026-11-17 the maintainer separately invoked the Phase 0B launch prompt. That invocation now authorizes B01–B04, subject to its publication and human merge checkpoints; historical Phase 0A/transition limits remain preserved.
