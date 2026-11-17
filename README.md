# CRUCIBLE

**A framework for learning and reduced modeling of astrophysical reaction networks.**

Repository: **[jaharris87/crucible-astro](https://github.com/jaharris87/crucible-astro), public, BSD-3-Clause**. Phase 0A/0B are complete; [Phase 1 S01–S03 is authorized](docs/PHASE_1_AUTHORITY.md). For current dependencies and acceptance gates, see [Progress](docs/PROGRESS.md) and [Handoff](docs/HANDOFF.md). No trained model or qualified dataset exists; scientific results are **not yet evaluated**. Model development/training requires a later phase.

## Charter

CRUCIBLE will make reaction-network surrogates and reduction methods reproducible, comparable, and callable. Its enduring research object is the relationship between physical composition, representations, kinetics, integration, and scientifically useful observables. ENACT-AI/Genesis supplies initial use cases and reporting obligations, not the project's lifetime or a requirement to include every funding workstream.

The framework must admit a full-state/identity representation and multiple reduction approaches. The expected nuclear task has **one physical kinetics source function**, possibly a vector of species or reduced-coordinate derivatives. A reconstruction decoder is part of a representation; chemical surface/deposition heads are not nuclear requirements. Energy readout needs an explicit physical definition and validation, whether recovered from dynamics or predicted separately.

Initial scope: provenance-aware data ingestion, reproducible baselines, reduced dynamics, integrated trajectory evaluation, fair comparisons, and a small callable research prototype. Production hydrodynamic coupling, a universal network solver, neutrino-flavor modeling, top-level supernova observables, autonomous active learning, and distributed training infrastructure are outside the initial implementation scope. They require separate scientific cases and decisions.

Success means a collaborator can identify exactly which network, data, split, transforms, model, integration settings, and resources produced a claim; reproduce its bounded benchmark; and see where it fails. CI success and training loss are insufficient scientific evidence. The maintainer owns scientific acceptance and merge decisions.

## Read this package

Start with [Contributing](CONTRIBUTING.md#quick-start) to install and run checks.
Use [Progress](docs/PROGRESS.md) for current state and the linked live issue/PR
records for subsequent CI, review and merge receipts.

| Science and scope | Document |
| --- | --- |
| State, targets, energy, interfaces and provenance | [Design](docs/DESIGN.md) |
| Qualification and comparison evidence | [Validation](docs/VALIDATION.md), [source evidence](docs/EVIDENCE.md) |
| Phases, dependencies and acceptance | [Roadmap](docs/ROADMAP.md), [backlog](docs/BACKLOG.md) |
| Accepted and open choices | [Decisions](docs/DECISIONS.md) |

| Development and reporting | Document |
| --- | --- |
| Setup and checks | [Contributing](CONTRIBUTING.md) |
| Issue-to-merge process and external audits | [Workflow](docs/WORKFLOW.md) |
| Agent entry point and reusable briefs | [AGENTS](AGENTS.md), [agent briefs](docs/AGENT_BRIEFS.md) |
| Current state and resumption | [Progress](docs/PROGRESS.md), [handoff](docs/HANDOFF.md) |
| Dated collaborator reports | [Meeting-report template](docs/MEETING_REPORT_TEMPLATE.md), [initial bootstrap snapshot](docs/reports/2026-11-17-bootstrap.md) |

| Historical records | Document |
| --- | --- |
| Phase 0A review and adoption | [Review record](docs/REVIEW.md), [transition](docs/TRANSITION.md) |
| Executed launch and seed | [Launch prompt](docs/PHASE_0B_LAUNCH.md), [bootstrap record](docs/BOOTSTRAP.md) |
| External-audit assessment | [Dispositions](docs/audits/2026-11-17-external-audit-disposition.md) |

The policy source of truth is the workflow; the scientific contracts are in design and validation; decisions are recorded only in the decision register. Other documents link to those sources rather than introducing separate rules. Machine-specific reference locations live only in the evidence inventory. All proposed runtime paths and artifact identifiers are portable.

## Phase 0A authority

The completed Phase 0A assignment permitted reading references and creating/revising this local design package. Its limits excluded repository creation, branches, commits, pushes, PRs, reference edits, environment installation, data generation, training, HPC jobs and framework implementation. Those limits belonged to that assignment and are **not permanent development policy**. The subsequent maintainer transition permitted local documentation changes and activation of root [AGENTS.md](AGENTS.md) only. On 2026-11-17 the maintainer separately invoked the Phase 0B launch prompt. That invocation now authorizes B01–B04, subject to its publication and human merge checkpoints; historical Phase 0A/transition limits remain preserved.
