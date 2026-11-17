# CRUCIBLE

**A framework for learning and reduced modeling of astrophysical reaction networks.**

Repository: **[jaharris87/crucible-astro](https://github.com/jaharris87/crucible-astro), public, BSD-3-Clause**. Status: **Phase 0B active**, 2026-11-17. B01's documentation seed is published after confirmed copyright/release readiness. B01/B02 are complete; the maintainer merged the minimal package in [PR #5](https://github.com/jaharris87/crucible-astro/pull/5) at `5d81381ddfde28cb6f86980e616d7c5065bae768`, with [merged-result checks](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959449805). B03 CI/templates/reporting and the future model policy are active as a local candidate; no B03 PR exists yet. B04 is not implemented. No trained model or qualified dataset exists; scientific results are **not yet evaluated**. The native goal covers B01–B04 only.

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
