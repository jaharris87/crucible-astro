# Development, orchestration and review playbook

Status: ongoing workflow adopted by the maintainer on 2026-11-17 (D-010). D-013 removes resource caps/accounting, D-014 adds the future narrow documentation lane, and D-015 retains canonical model policy here; see [DECISIONS](../DECISIONS.md). Adoption alone was not execution authority. The maintainer separately invoked Phase 0B on 2026-11-17; current authority and checkpoints are recorded in [HANDOFF](../HANDOFF.md). The [transition](../TRANSITION.md) remains historical. Historical Phase 0A limits remain in the [charter](../../README.md#phase-0a-authority). This playbook is the single source for development process; [agent briefs](AGENT_BRIEFS.md) apply it without creating a second policy.

## One orchestrator, durable state

One orchestrator owns decomposition, dependency order, integration and evidence completeness. Bounded workers get an issue/subtask, inputs, acceptance, exclusions, writable area, stopping condition and handoff format. Start with at most three concurrent specialists; add concurrency only when independent authorized work warrants it. Use isolated worktrees/checkouts for concurrent implementation, each on its own issue branch, and serialize changes to shared contracts. Read-only investigators/reviewers need no writable branch. Never share a mutable implementation checkout across concurrent workers.

Use existing Codex workers, local tools, issues and PRs; no custom agent server or mandatory external service. Record explicit model/reasoning choices and any substitution; no worker is needed merely to fill a role. Apply [model selection and escalation](WORKFLOW.md#model-selection-and-escalation) for work after Phase 0B. Existing Phase 0B assignments continue unchanged.

Before resuming, read the issue, decision register, current handoff, candidate identity and relevant experiment records. A chat summary or agent memory is not authoritative project state. The orchestrator records completed work, actual checks, artifacts, remaining work/blockers, decisions, and the next authorized action after each substantive task. A worker's assertion is verified against evidence before becoming an accepted fact.

## Model selection and escalation

Accepted D-012 on 2026-11-17, effective **after Phase 0B**, now complete.
Historical Phase 0B assignments remain unchanged in their records. This policy supersedes the earlier
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
   or Sol analysis is insufficient, and the expected deliverable, scope,
   reasoning effort and stopping condition. Consider focused Sol work or
   increased effort when useful without mandatory wasteful retries. Avoid
   repeating completed investigations or supplying unnecessary context.
6. Sol remains the normal lead. Return Astra findings for lead verification and
   integration; record the resolution and remaining uncertainty.
7. Astra is neither a routine reviewer nor an automatic final check. Fresh
   context and evidence establish independence, not model expense.
8. Justified escalation is permitted within existing task and spending
   authority without per-choice approval. It grants no broader scope or purchase
   authority, does not waive review requirements, and changes no human scientific
   or merge authority. D-013 removes the former resource-cap/accounting requirement.

Always record model and reasoning effort in the [briefs](AGENT_BRIEFS.md) and
durable issue/PR evidence. Include the question, insufficiency, expected benefit,
deliverable/scope/effort/stop and lead outcome/uncertainty when escalating; omit
empty escalation fields for ordinary assignments. Substitutions still require
the availability and alternatives record above (D-015). No global settings or agent tooling changes are
required. Model availability limitations must remain explicit.

## Governing issue through closeout

1. **Issue:** specify problem, scope/non-goals, dependencies, risk classes, independently observable acceptance, required software/scientific evidence, stopping rules and decisions/authority. Investigate before fixing uncertain physics. Split consequential unanswered scientific choices from ordinary reversible engineering choices.
2. **Investigation:** read targeted sources and current state; record findings, assumptions, actual producer semantics, likely failure modes and proposed checks. Keep data/reference inputs immutable. Escalate only missing choices that materially affect the task.
3. **Implementation and checks:** isolated feature branch from the verified integration base (use simple `main` with available agreed protection, no upstream mirror). Test-first where the expected behavior is independently specified. Stay within the authorized issue scope. Retain scientific runs through manifests and run records.
4. **Self-review:** inspect the complete diff against acceptance, unnecessary complexity, tests that could falsely pass, error paths, docs, local-path leakage and claims versus observed evidence. Self-review precedes the review candidate and does not count as independent review.
5. **Pushed PR candidate:** when authorized by the development task, commit and push the complete candidate and open a **draft PR** targeting `main`. Record governing issue, exact head SHA and base SHA, checks/evidence and gaps. Draft means not ready for human merge; it does not prohibit agent review.
6. **Fresh independent review:** except for eligible future [narrow documentation](WORKFLOW.md#narrow-documentation-lane), explicitly dispatch a fresh-context read-only reviewer against the open PR's exact pushed candidate. Supply issue/acceptance, diff/source, relevant evidence and risk brief. Do not supply a persuasive implementation narrative or prior favorable conclusions. PR record is the review source of record; local checkout supports it. Reviewers cannot silently repair what they review.
7. **Disposition and repair:** preserve original consequential findings before changing the candidate. Record fix, evidence-backed disagreement, bounded deferral or human-accepted limitation. Push substantive fixes, identify old/new SHAs, and obtain focused independent verification of fixes plus introduced risk. Newly implicated risks add review viewpoints. Documentation-only edits can omit a full rerun with a recorded reason, but every final candidate needs an explicit evidence/freshness disposition.
8. **Human review/merge:** make ready for review only when required checks and review coverage/dispositions or narrow-lane eligibility are complete for the current candidate. For the narrow lane, record eligibility and passing CI instead of an independent-review record. Human maintainer judges scientific acceptance and merge. Immediately before merge compare the reviewed or narrow-lane eligible head, actual head and base; new code/base changes trigger appropriate renewed checks/review. No agent merges by inference from silence or an earlier recommendation.
9. **Integration and closeout:** record merged SHA and rerun applicable checks on the merged result, including interactions with concurrent changes. Preserve failures and follow-up links; do not claim issue completion until integration acceptance holds. A premature auto-close is reopened/recorded if integration fails. Clean up authorized worktrees only after retained evidence and unrelated work are safe.

**Lifecycle reconciliation:** XNet uses draft PRs before explicit independent review; fTimer's native trigger and coverage workflows skip drafts [W1, W2]. CRUCIBLE uses draft PRs, ordinary CI and explicit reviewer dispatch when independent review is required, with no copied ready-only routing. Phase 0B CI must run on draft PRs. If a later integration needs ready PRs, revise this single lifecycle and its templates together in a governing issue; do not retain both rules. Do not copy XNet's mirror/development branch structure or fTimer's PAT/label/queue system.

Where GitHub permissions/plan support it, propose PR-required protection, named required fast checks, and stale-approval dismissal. Verify actual settings in bootstrap; these controls support but do not replace explicit exact-SHA records or human scientific judgment. GitHub documents [stale review and latest-push controls](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). If a single-maintainer repository cannot require a distinct human approval, keep the maintainer merge record and independent agent evidence; do not pretend an agent comment is a GitHub human approval or silently bypass an unmet required check.

### Bootstrap protection

Verified during B03 on 2026-11-17: `main` requires a PR and the named
`fast-checks` check from GitHub Actions app 15368, with strict up-to-date checks
and administrator enforcement. Stale approvals are dismissed, conversations
must be resolved, force pushes/deletion are blocked, and auto-merge is disabled.
The repository has one human maintainer; zero separate approving reviews and no
distinct latest-push approval are required by GitHub. The adopted single-maintainer
provision requires fresh exact-SHA independent agent evidence where required by
the risk lane, and an explicit human merge decision in every lane. D-014 changes
only future narrow-documentation review; it does not change GitHub protection or
waive review for this closeout. An agent comment is not a human approval. See [B03 evidence](../bootstrap/B03-EVIDENCE.md)
and [PR #6](https://github.com/jaharris87/crucible-astro/pull/6) for actual readback
and check identities. Preserve stronger controls if settings change; report any
unavailable control or consequential weakening before proceeding. No unmet check
may be bypassed.

## Proportionate risk review

| Change risk | Required viewpoints | Evidence beyond ordinary diff review |
| --- | --- | --- |
| Documentation/process | Requirements, scope, consistency and source support | Checked links and consequential claims; authority changes surfaced |
| Parser/schema/validator/tests | Above + correctness, test effectiveness and provenance | Valid control, targeted malformed/mutated cases, exact failure reason |
| Model/transform/solver/physics | Above + scientific/numerical review | Independent equations/references, state/units/derivatives, tolerances, held-out results and constraints |
| Packaging/build/concurrency | Above + portability/operational review | Clean requested environment, actual resolved configuration, relevant concurrency/negative checks |
| Retained scientific or HPC evidence | Scientific + provenance/performance as applicable | Candidate/run binding, actual resource/cost evidence, immutable artifacts and independently recomputed claims |

Roles are viewpoints, not a fixed number of agents. One independent reviewer may cover several roles for a small change. A scientific-policy change usually needs specialized expertise even if it edits only Markdown. Reviewers challenge speculative abstractions and identify the smallest simplification preserving required safeguards. `PASS` with stated limitations is valid; no quota of findings, style churn or arbitrary line-count gates.

### Narrow documentation lane

D-014 was accepted on 2026-11-17 and takes effect **after Phase 0B**. A change limited to typos, links, status or
non-policy wording may use CI and an explicit human merge without mandatory
agent review. Record eligibility, the exact head/base, supporting status evidence
where relevant and the required check result in the PR. Self-review and
merged-result verification still apply.

Code, tests, CI, packaging, interfaces, policy/authority and scientific claims
retain independent review even when edited in Markdown. Mixed or uncertain
changes use the full lane; unresolved consequential concerns are not light-lane
eligible. The current audit closeout uses full exact-candidate independent review.
This exception changes no required CI check, protection or human merge control.

## Review record and practical completion

Each required independent-review invocation records reviewer/model/session class, fresh-context/read-only status, role/risk, issue and PR, exact candidate/base, playbook revision, supplied evidence boundary, checks independently performed, result and limitations. Each consequential finding has stable ID, original statement, severity/confidence, candidate SHA, location, evidence, consequence, smallest proposed fix and verification requirement.

Dispositions:

- **Fix:** link repair SHA and actual verification.
- **Disagree with evidence:** preserve the finding, cite counterevidence; unresolved consequential scientific disputes go to the maintainer.
- **Defer:** link a bounded follow-up with origin finding/PR/SHA, consequence, trigger, acceptance and why it does not invalidate the current claim.
- **Accepted limitation:** name the human accepting it and the constrained claim. Agents cannot waive acceptance criteria through this category.

Completion requires all blocking findings resolved; every consequential finding disposed; required checks/evidence present for the current candidate; scientific limits and decisions visible; appropriate independent review/re-review or narrow-lane eligibility complete; and human review/merge decision followed by integration checks. Minor suggestions do not create endless gates. Default review budget: one initial round plus focused repair review; a third broad review requires maintainer direction, with the new risk or unresolved blocker explained. A round budget stops/escalates work, **never converts an unresolved blocker into a pass**. Persistent disagreement or repeated new blockers requires a decision packet. No continued review merely to obtain unanimity or generate more comments.

### Resources and authority

D-013, accepted by the maintainer on 2026-11-17, removes **all compute/resource
limits**: aggregate CPU caps, pre-run reservations, per-command accounting,
repository job timeouts, memory/scratch caps and the proposed fixture-storage cap.
No replacement resource ledger or numeric limit is required. The historical
[verification ledger](../VERIFICATION.md), executed launch and evidence remain
unchanged records of their original rules and observations.

This grants no new task, scientific phase or purchase authority. Phase 0B remains
the minimal package, synthetic validator and separately authorized audit closeout;
scientific models/training, real-data qualification and Phase 1 were outside that bootstrap task.
Phase 1 now has separate [execution authority](../PHASE_1_AUTHORITY.md); models/training
remain outside it. Experiments need explicit scope and scientific acceptance, not an inferred
permission from removing caps. Actual hardware/configuration, runtime, failures
and cost remain evidence for reproducibility and fair scientific comparison.

Stop on scope ambiguity, corrupted provenance, nonfinite dynamics, runaway solver
failures or a predeclared validation-plateau rule. Preserve partial results and
failure status. The review-round allowance above is unchanged process policy;
it cannot turn an unresolved blocker into a pass.

## Maintainer decisions

Investigate enough to make a decision concrete before asking. Use the interactive question interface when available; offer two or three meaningful choices, recommendation first, and allow free text. Normally ask no more than three related decisions together. Required scientific/scope/authority choices stay pending until answered; optional recommendations may remain proposed. Continue independent authorized work. Record the answer, owner/date, consequences and supporting evidence in [DECISIONS](../DECISIONS.md), apply it consistently, and do not ask again without materially new evidence.

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

B03 establishes one lightweight issue/milestone progress view, starting with [PROGRESS](../PROGRESS.md), plus linked result tables rather than a bespoke dashboard. Populate actual GitHub links during authorized bootstrap and maintain phase, dependencies, status and PR links at handoffs. README and handoff link the [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap report](../reports/2026-11-17-bootstrap.md).

**Development view:** phase/issue, owner, dependencies, status, candidate/merged PR and SHA, actual checks, blocker/decision IDs, next bounded action. Use states proposed → ready → active → review → human decision → integrated; blocked names a specific missing input.

**Science view:** benchmark/dataset revision and coverage (network, T/rho/Ye/regimes/parent cases), task and method, split/seed, reconstruction/RHS/rollout results, abundance/energy errors, failures/constraints, inference and integration runtime, reproducibility/qualification status, artifact IDs. Link every row to its experiment and governing issue. Track unevaluated regions explicitly.

Use the reusable meeting-report template for concise dated collaborator reports, normally one page. Dated reports are retained evidence-backed snapshots; the progress view tracks current state. Update the latter at substantive handoffs, using live issue/PR links for subsequent CI, review and merge receipts. Do not commit a new receipt solely to record the previous head's check; a substantive new change still needs its own final-candidate evidence/freshness disposition. Scientific results must remain explicitly **“not yet evaluated”** until supported by linked experiments, including dataset/split and source/artifact identities. Evaluate and label each metric/regime separately; never replace unmeasured values with zero, targets, training loss or passing synthetic CI.

## Independent external audits

Offer occasional Claude/Gemini audits at Phase 0A design acceptance, Phase 1 data-contract qualification, and Phase 4/5 comparison/release boundaries. These are advisory audits, not mandatory dependencies or claims those services are configured. Do not upload nonpublic source/data without authority. If unavailable, record unavailable/deferred and use a fresh independent reviewer; never invent an external endorsement.

Portable packet: charter/requirements, decisions with unresolved items, exact source SHA or documentation checksums, relevant diff/files, provenance and dataset/split manifests, tiny permitted fixtures, commands/environment, raw metric/failure tables, authorized scope and reviewer brief. Exclude machine-specific paths, credentials and large/private data; supply sanitized locators and explicit omissions. Ask for counterexamples, unsupported claims, leakage, physical inconsistencies, unfair comparisons and unnecessary complexity. Preserve returned findings with service/model/date/candidate and disposition using the same record as internal review. External agreement does not substitute for reference evidence or human acceptance.

## Development orchestration versus scientific active learning

The development orchestrator coordinates issues and evidence. The final proposal also describes a future uncertainty-driven XNet workflow [P1]; it is a separate scientific system that selects new calculations and retraining. It needs a new scope/decision after a basic locked benchmark works: calibrated selection/uncertainty criteria, frozen holdout protection, valid parameter domain, reference-generator checks, human gates, explicit campaign scope, plateau/coverage/failed-run stopping rules and comparison to a nonadaptive sampling baseline. Do not enable it implicitly through the software worker system. PRISM sensitivity analysis and broader ENACT workstreams are separate projects unless explicitly added.
