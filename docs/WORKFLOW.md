# Development, orchestration and review playbook

Status: ongoing workflow adopted by the maintainer on 2026-11-17 (D-010), with the bootstrap budget in D-011. Adoption alone was not execution authority. The maintainer separately invoked Phase 0B on 2026-11-17; current authority and checkpoints are recorded in [HANDOFF](HANDOFF.md). The [transition](TRANSITION.md) remains historical. Historical Phase 0A limits remain in the [charter](../README.md#phase-0a-authority). This playbook is the single source for development process; [agent briefs](AGENT_BRIEFS.md) apply it without creating a second policy.

## One orchestrator, durable state

One orchestrator owns decomposition, dependency order, integration and evidence completeness. Bounded workers get an issue/subtask, inputs, acceptance, exclusions, writable area, budget, stopping condition and handoff format. Start with at most three concurrent specialists; add concurrency only when independent work warrants it and resources permit. Use isolated worktrees/checkouts for concurrent implementation, each on its own issue branch, and serialize changes to shared contracts. Read-only investigators/reviewers need no writable branch. Never share a mutable implementation checkout across concurrent workers.

Use existing Codex workers, local tools, issues and PRs; no custom agent server or mandatory external service. Record explicit model/reasoning choices and any substitution; no worker is needed merely to fill a role. Apply [model selection and escalation](#model-selection-and-escalation) for work after Phase 0B. Existing Phase 0B assignments continue unchanged.

Before resuming, read the issue, decision register, current handoff, candidate identity and relevant experiment records. A chat summary or agent memory is not authoritative project state. The orchestrator records completed work, actual checks, artifacts, remaining work/blockers, decisions, and the next authorized action after each substantive task. A worker's assertion is verified against evidence before becoming an accepted fact.

## Model selection and escalation

Accepted D-012 on 2026-11-17, effective **after Phase 0B**. The current Phase 0B
orchestrator and agents continue unchanged. This policy supersedes the earlier
routine Astra High assignment for difficult scientific/design synthesis and
independent critique. Executed launch prompts, archives and historical review
assignments remain historical evidence; future briefs reference this section.

1. `gpt-6.1-sol` is the default advanced model for orchestration, substantive
   implementation, scientific reasoning and independent review; use high
   reasoning effort by default.
2. `gpt-6-luna` with high reasoning is suitable for narrow inventories,
   straightforward extraction and mechanical checks.
3. Explicitly pin Sol to `gpt-6.1-sol`. Do not use GPT-5.6 Sol or silently
   substitute. If unavailable, report available alternatives before substituting.
4. Astra is exceptional and bounded. State a concrete substantial expected
   benefit, such as resolving a scientific inconsistency, difficult mathematics
   or a consequential architectural disagreement.
5. Before escalation to Astra, explain the question, why existing investigation
   and Sol analysis are insufficient, and the expected deliverable, scope,
   reasoning effort and stopping condition. Consider focused Sol work or
   increased effort when useful; no wasteful retry or repetition of completed
   investigation is mandatory.
6. Sol remains the normal lead. Return Astra findings for lead verification and
   integration; record the resolution and remaining uncertainty.
7. Astra is neither a routine reviewer nor an automatic final check. Fresh
   context and evidence establish independence, not model expense.
8. Justified escalation is permitted within existing scope and resource
   authority without per-choice approval. It grants no broader scope or budget,
   does not waive review/compute limits, and changes no human scientific or
   merge authority.

Record model, reasoning effort, escalation justification (or not applicable),
expected deliverable/stop and actual outcome in the [briefs](AGENT_BRIEFS.md)
and durable issue/PR evidence. No global settings or agent tooling changes are
required. Model availability limitations must remain explicit.

## Governing issue through closeout

1. **Issue:** specify problem, scope/non-goals, dependencies, risk classes, independently observable acceptance, required software/scientific evidence, resource budget, stopping rules and decisions/authority. Investigate before fixing uncertain physics. Split consequential unanswered scientific choices from ordinary reversible engineering choices.
2. **Investigation:** read targeted sources and current state; record findings, assumptions, actual producer semantics, likely failure modes and proposed checks. Keep data/reference inputs immutable. Escalate only missing choices that materially affect the task.
3. **Implementation and checks:** isolated feature branch from the verified integration base (use simple `main` with available agreed protection, no upstream mirror). Test-first where the expected behavior is independently specified. Stay within the issue and budgets. Retain scientific runs through manifests and run records.
4. **Self-review:** inspect the complete diff against acceptance, unnecessary complexity, tests that could falsely pass, error paths, docs, local-path leakage and claims versus observed evidence. Self-review precedes the review candidate and does not count as independent review.
5. **Pushed PR candidate:** when authorized by the development task, commit and push the complete candidate and open a **draft PR** targeting `main`. Record governing issue, exact head SHA and base SHA, checks/evidence and gaps. Draft means not ready for human merge; it does not prohibit agent review.
6. **Fresh independent review:** explicitly dispatch a fresh-context read-only reviewer against the open PR's exact pushed candidate. Supply issue/acceptance, diff/source, relevant evidence and risk brief. Do not supply a persuasive implementation narrative or prior favorable conclusions. PR record is the review source of record; local checkout supports it. Reviewers cannot silently repair what they review.
7. **Disposition and repair:** preserve original consequential findings before changing the candidate. Record fix, evidence-backed disagreement, bounded deferral or human-accepted limitation. Push substantive fixes, identify old/new SHAs, and obtain focused independent verification of fixes plus introduced risk. Newly implicated risks add review viewpoints. Documentation-only edits can omit a full rerun with a recorded reason, but every final candidate needs an explicit evidence/freshness disposition.
8. **Human review/merge:** make ready for review only when required checks and independent coverage/dispositions are complete for the current candidate. Human maintainer judges scientific acceptance and merge. Immediately before merge compare reviewed head, actual head and base; new code/base changes trigger appropriate renewed checks/review. No agent merges by inference from silence or an earlier recommendation.
9. **Integration and closeout:** record merged SHA and rerun applicable checks on the merged result, including interactions with concurrent changes. Preserve failures and follow-up links; do not claim issue completion until integration acceptance holds. A premature auto-close is reopened/recorded if integration fails. Clean up authorized worktrees only after retained evidence and unrelated work are safe.

**Lifecycle reconciliation:** XNet uses draft PRs before explicit independent review; fTimer's native trigger and coverage workflows skip drafts [W1, W2]. CRUCIBLE uses draft PRs plus explicit reviewer dispatch and ordinary CI, with no copied ready-only routing. Phase 0B CI must run on draft PRs. If a later integration needs ready PRs, revise this single lifecycle and its templates together in a governing issue; do not retain both rules. Do not copy XNet's mirror/development branch structure or fTimer's PAT/label/queue system.

Where GitHub permissions/plan support it, propose PR-required protection, named required fast checks, and stale-approval dismissal. Verify actual settings in bootstrap; these controls support but do not replace explicit exact-SHA records or human scientific judgment. GitHub documents [stale review and latest-push controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). If a single-maintainer repository cannot require a distinct human approval, keep the maintainer merge record and independent agent evidence; do not pretend an agent comment is a GitHub human approval or silently bypass an unmet required check.

### Planned bootstrap protection

For this sole-human-maintainer repository, propose PR-required protection of
`main`, the actual named `fast-checks` check after observing it, strict up-to-date
checks, stale-review dismissal, resolved conversations, and blocked force pushes
and deletion. Keep automatic merge disabled. If a separate human approval cannot
be satisfied, use zero separately required approvals while retaining the explicit
human merge decision and fresh independent agent evidence. These are proposed
settings, not verified controls. The orchestrator must record available plan/access
constraints and settings authority, preserve any stronger existing controls, and
verify effective settings. Using the accepted sole-maintainer provision needs no
additional approval just for zero separate approvals; unresolved consequential
settings choices still go to the maintainer. No unmet check may be bypassed.

## Proportionate risk review

| Change risk | Required viewpoints | Evidence beyond ordinary diff review |
| --- | --- | --- |
| Documentation/process | Requirements, scope, consistency and source support | Checked links and consequential claims; authority changes surfaced |
| Parser/schema/validator/tests | Above + correctness, test effectiveness and provenance | Valid control, targeted malformed/mutated cases, exact failure reason |
| Model/transform/solver/physics | Above + scientific/numerical review | Independent equations/references, state/units/derivatives, tolerances, held-out results and constraints |
| Packaging/build/concurrency | Above + portability/operational review | Clean requested environment, actual resolved configuration, relevant concurrency/negative checks |
| Retained scientific or HPC evidence | Scientific + provenance/performance as applicable | Candidate/run binding, resource accounting, immutable artifacts and independently recomputed claims |

Roles are viewpoints, not a fixed number of agents. One independent reviewer may cover several roles for a small change. A scientific-policy change usually needs specialized expertise even if it edits only Markdown. Reviewers challenge speculative abstractions and identify the smallest simplification preserving required safeguards. `PASS` with stated limitations is valid; no quota of findings, style churn or arbitrary line-count gates.

## Review record and practical completion

Each invocation records reviewer/model/session class, fresh-context/read-only status, role/risk, issue and PR, exact candidate/base, playbook revision, supplied evidence boundary, checks independently performed, result and limitations. Each consequential finding has stable ID, original statement, severity/confidence, candidate SHA, location, evidence, consequence, smallest proposed fix and verification requirement.

Dispositions:

- **Fix:** link repair SHA and actual verification.
- **Disagree with evidence:** preserve the finding, cite counterevidence; unresolved consequential scientific disputes go to the maintainer.
- **Defer:** link a bounded follow-up with origin finding/PR/SHA, consequence, trigger, acceptance and why it does not invalidate the current claim.
- **Accepted limitation:** name the human accepting it and the constrained claim. Agents cannot waive acceptance criteria through this category.

Completion requires all blocking findings resolved; every consequential finding disposed; required checks/evidence present for the current candidate; scientific limits and decisions visible; appropriate re-review complete; and human review/merge decision followed by integration checks. Minor suggestions do not create endless gates. Default review budget: one initial round plus focused repair review; a third broad review requires maintainer direction, with the new risk or unresolved blocker explained. A round budget stops/escalates work, **never converts an unresolved blocker into a pass**. Persistent disagreement, repeated new blockers, or exhausted compute requires a decision packet. No continued review merely to obtain unanimity or generate more comments.

For expensive computation, the issue states numeric CPU/GPU-hours, wall time, memory/disk, job count, seed/search limits and stopping conditions. Stop on exhausted budget, corrupted provenance, nonfinite dynamics, runaway solver failures or the predeclared validation-plateau rule. Preserve partial results and failure status; obtain authority before raising caps. Default in the absence of an expensive-work budget is no launch. The adopted phase-wide Phase 0B verification cap and accounting rule are in [BACKLOG](BACKLOG.md#bootstrap-verification-budget); B04 shares that cap. A third broad review round requires maintainer direction before proceeding; a new risk is the reason to request it, not an automatic budget increase.

## Maintainer decisions

Investigate enough to make a decision concrete before asking. Use the interactive question interface when available; offer two or three meaningful choices, recommendation first, and allow free text. Normally ask no more than three related decisions together. Required scientific/scope/authority choices stay pending until answered; optional recommendations may remain proposed. Continue independent authorized work. Record the answer, owner/date, consequences and supporting evidence in [DECISIONS](DECISIONS.md), apply it consistently, and do not ask again without materially new evidence.

Fallback format:

```text
Decision D-###: title
Question: one clear question
Why my decision is needed: scientific / architecture / scope / authority reason
Recommendation: preferred option and why
A — option (Recommended): meaning and principal tradeoff
B — alternative: meaning and principal tradeoff
C — only if useful
Impact: dependent work, cost and reversibility
Evidence: prepared proposal and source links
```

Routine reversible implementation/document choices within authority are made by the orchestrator. A chosen option is not blanket authorization for new phases or external actions beyond the requested task.

## Two connected progress views and meeting report

B03 establishes one lightweight issue/milestone progress view, starting with [PROGRESS](PROGRESS.md), plus linked result tables rather than a bespoke dashboard. Populate actual GitHub links during authorized bootstrap and maintain phase, dependencies, status and PR links at handoffs. README and handoff link the [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap report](reports/2026-11-17-bootstrap.md).

**Development view:** phase/issue, owner, dependencies, status, candidate/merged PR and SHA, actual checks, blocker/decision IDs, next bounded action. Use states proposed → ready → active → review → human decision → integrated; blocked names a specific missing input.

**Science view:** benchmark/dataset revision and coverage (network, T/rho/Ye/regimes/parent cases), task and method, split/seed, reconstruction/RHS/rollout results, abundance/energy errors, failures/constraints, inference and integration runtime, reproducibility/qualification status, artifact IDs. Link every row to its experiment and governing issue. Track unevaluated regions explicitly.

Use the reusable meeting-report template for concise dated collaborator reports, normally one page. Reports are evidence-backed snapshots; the progress view tracks current state. Scientific results must remain explicitly **“not yet evaluated”** until supported by linked experiments, including dataset/split and source/artifact identities. Evaluate and label each metric/regime separately; never replace unmeasured values with zero, targets, training loss or passing synthetic CI.

## Independent external audits

Offer occasional Claude/Gemini audits at Phase 0A design acceptance, Phase 1 data-contract qualification, and Phase 4/5 comparison/release boundaries. These are advisory audits, not mandatory dependencies or claims those services are configured. Do not upload nonpublic source/data without authority. If unavailable, record unavailable/deferred and use a fresh independent reviewer; never invent an external endorsement.

Portable packet: charter/requirements, decisions with unresolved items, exact source SHA or documentation checksums, relevant diff/files, provenance and dataset/split manifests, tiny permitted fixtures, commands/environment, raw metric/failure tables, scope/budget and reviewer brief. Exclude machine-specific paths, credentials and large/private data; supply sanitized locators and explicit omissions. Ask for counterexamples, unsupported claims, leakage, physical inconsistencies, unfair comparisons and unnecessary complexity. Preserve returned findings with service/model/date/candidate and disposition using the same record as internal review. External agreement does not substitute for reference evidence or human acceptance.

## Development orchestration versus scientific active learning

The development orchestrator coordinates issues and evidence. The final proposal also describes a future uncertainty-driven XNet workflow [P1]; it is a separate scientific system that selects new calculations and retraining. It needs a new scope/decision after a basic locked benchmark works: calibrated selection/uncertainty criteria, frozen holdout protection, valid parameter domain, reference-generator checks, human gates, per-campaign simulation/training/storage caps, plateau/coverage/failed-run stopping rules and comparison to a nonadaptive sampling baseline. Do not enable it implicitly through the software worker system. PRISM sensitivity analysis and broader ENACT workstreams are separate projects unless explicitly added.
