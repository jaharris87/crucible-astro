# Working on CRUCIBLE

CRUCIBLE develops reproducible learning and reduced modeling of astrophysical reaction networks. Read [README](README.md), the current task/governing issue, [handoff](docs/HANDOFF.md), and relevant [decisions](docs/DECISIONS.md) before acting. Inspect actual workspace/repository state when resuming; do not infer it from a prior chat.

## Authority and accepted policy

The maintainer adopted the [development workflow](docs/WORKFLOW.md), B01–B04 scope and [verification budget](docs/BACKLOG.md#bootstrap-verification-budget) on 2026-11-17 (D-010/D-011). Follow them for authorized development. Adopted policy is not authorization to execute a new phase.

**Current boundary:** Phase 0B B01–B04 was explicitly authorized on 2026-11-17 by invocation of [the launch prompt](docs/PHASE_0B_LAUNCH.md), including progress/reporting acceptance. The native Phase 0B goal is active. Git/GitHub and local bootstrap implementation are authorized within that task; publication requires the recorded D-001 confirmation (now supplied for this seed/bootstrap code) and every post-seed merge requires a concrete human decision. Phase 1, real-data ingestion and scientific models remain outside scope. Phase 0A and transition records remain historical.

Accepted destination: public `jaharris87/crucible-astro`, BSD-3-Clause. Do not re-ask owner, visibility or license direction. The maintainer confirmed `Copyright (c) 2026 UT-Battelle, LLC.`, no additional institutional/government-rights notice, and release readiness for the portable seed and original bootstrap code on 2026-11-17. See D-001 and [licensing evidence](docs/TRANSITION.md#licensing-evidence).

## Targeted documentation routing

- Phase scope, dependencies and acceptance: [roadmap](docs/ROADMAP.md), [backlog](docs/BACKLOG.md).
- Scientific/data/interface work: relevant [design](docs/DESIGN.md) and [validation](docs/VALIDATION.md) sections; original [evidence](docs/EVIDENCE.md) before adopting claims.
- Implementation, review or delegation: [workflow](docs/WORKFLOW.md), [bounded worker/reviewer briefs](docs/AGENT_BRIEFS.md).
- Adoption history and historical review limits: [transition](docs/TRANSITION.md). Preserve original review records/inventories; do not relabel later edits as independently reviewed.

Distinguish accepted requirements, verified facts, recommendations, assumptions and open questions. Interfaces and later method choices remain provisional unless the decision register says otherwise. Create shared abstractions when actual implementations need them.

## Scientific safeguards

CCSN particle trajectories are the initial emphasis (D-002). Explore both targets, starting with the qualified instantaneous-RHS identity/full-state path (D-003); finite-step prediction needs its own later interval/history contract. These directions do not qualify any dataset. D-004–D-009 remain open; no scientific decision blocks B04's synthetic demonstration.

Preserve raw data and reference projects. Establish species order, units, conditioning, target timing, validity and energy semantics from the actual producer. One physical source may be vector-valued; a decoder is not a second source. Do not import chemical heads, conversions or invariants by analogy. Keep reconstruction, RHS/update, rollout, provenance and cost evidence separate. Train-only preprocessing and grouped holdouts prevent leakage; CI success or lower loss alone is not scientific validity.

## Decisions, execution and handoff

Make routine reversible choices within scope. Prepare concrete evidence before asking consequential scientific, scope or authority questions; use the interactive interface or D-### format in the workflow, recommendation first, meaningful alternatives, normally no more than three together and free-text answers. Record answers and apply them consistently. Silence is not approval; continue independent authorized work while required decisions remain pending.

Use one orchestrator with bounded workers, initially at most three useful specialists. For Sol subagents explicitly select `gpt-6.1-sol` with high reasoning effort; if unavailable, report available alternatives before substituting. Do not use GPT-5.6 Sol or silently substitute. Concurrent implementations use isolated worktrees. Independent reviewers are fresh-context and read-only, review exact pushed PR candidates, and preserve findings/dispositions; substantive fixes receive appropriate re-review. Humans own scientific acceptance and merge decisions. Do not exceed compute/review budgets or silently waive an acceptance criterion.

Durable state belongs in documents, issues, PRs and experiment records. At handoff record actual changes/checks, exact candidates/artifacts, completed and remaining work, limitations, decisions and next authorized action. Never invent successful runs, reviews or approvals. Close a persistent goal only when its actual exit criteria are satisfied; a missing human merge decision is not completion.
