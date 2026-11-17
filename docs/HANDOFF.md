# CRUCIBLE Phase 0B handoff

Date: 2026-11-17. **B01–B03 complete; B04 final-cycle candidate snapshot.**
The [live closeout record](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582) is authoritative for subsequent review, human
merge, merged-result checks, final budget and native goal completion. Do not infer
completion from this pre-merge snapshot. Once all six exits are verified there,
Phase 0B ends and D-012 applies to subsequent work. No Phase 1, real-data ingestion
or model work is authorized.

## Authority and publication

D-001 public `jaharris87/crucible-astro`, BSD-3-Clause, 2026 UT-Battelle, LLC notice,
no additional institutional/government-rights notice and seed/bootstrap release
readiness were confirmed by the maintainer. D-010 workflow and D-011 budget apply.
D-002/D-003 retain CCSN-first and both targets starting with qualified instantaneous
RHS; D-004–D-009 remain open and do not block synthetic B04. See [DECISIONS](DECISIONS.md).
B01’s one-time seed exception does not authorize later direct-to-main changes.

## Actual work and candidates

- [B01 #1](https://github.com/jaharris87/crucible-astro/issues/1) is complete at
  seed `c3846a4660e5915fe56c115202d9b1581a2319fd`; [closeout](https://github.com/jaharris87/crucible-astro/issues/1#issuecomment-6958852938).
- [B02 #2](https://github.com/jaharris87/crucible-astro/issues/2) is closed after
  human `jaharris87` merged [PR #5](https://github.com/jaharris87/crucible-astro/pull/5)
  at `5d81381ddfde28cb6f86980e616d7c5065bae768`, tree-identical to reviewed
  `e84fce0`. [Merged integration receipt](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959449805)
  records locked noneditable setup, lint/format and 2 tests passing.
  Initial B02-R1 (missing installed LICENSE) and its [disposition](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959156535)
  remain preserved; focused verification passed before merge. [B02 evidence](bootstrap/B02-EVIDENCE.md)
  retains the earlier negative controls and installed-distribution contract.
- B02 uses Python 3.12.9, uv 0.10.11, one lock, pytest/Ruff, zero runtime
  dependencies. Normal editable setup checks metadata but skips copied-license
  inventory because uv omits those files there; noneditable acceptance passes
  both tests without skips. B03 CI uses noneditable setup. macOS hard memory
  enforcement was unavailable; Linux CI controls ran in B03; measured details are in its evidence.
- [B03 #3](https://github.com/jaharris87/crucible-astro/issues/3) is closed after
  fresh `gpt-6.1-sol` High [PASS review](https://github.com/jaharris87/crucible-astro/pull/6#issuecomment-6959896792),
  explicit maintainer delegation of exact head `1f4601fa7b9616d8f93c97e7a12d7714a83c4862`,
  and merge `6858849bb8ecdfb208fcefeaa2a1e3a7da42a4b8`. [Merged integration](https://github.com/jaharris87/crucible-astro/pull/6#issuecomment-6959958285)
  and [main CI](https://github.com/jaharris87/crucible-astro/actions/runs/44168684071)
  passed. [B03 evidence](bootstrap/B03-EVIDENCE.md) preserves failure/pass/protection history.
- [B04 #4](https://github.com/jaharris87/crucible-astro/issues/4), [PR #7](https://github.com/jaharris87/crucible-astro/pull/7),
  adds the bounded synthetic [manifest contract](bootstrap/B04-CONTRACT.md).
  [Evidence](bootstrap/B04-EVIDENCE.md) records initial test-first failure,
  specific same-shape/same-set order rejection, ordered-to-set mutation failure,
  byte-identical restoration and clean noneditable installation with all 42 tests
  passing. Candidate source/checks are author evidence until independently reviewed.
  The live closeout record links exact final head/base, review/dispositions,
  human decision, merged SHA and integration when available.

Current Sol workers explicitly use `gpt-6.1-sol` High without substitution.
No model unavailability or Astra invocation occurred. B04 still requires its
own exact-candidate human merge decision; earlier B03 delegation does not cover it.

## Progress, reporting and history

[Progress view](PROGRESS.md), [Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1), [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap report](reports/2026-11-17-bootstrap.md) show actual issue/PR links and dependencies. Scientific results remain **not yet evaluated**; synthetic checks do not complete NS1–NS3.

All 21 startup files, original Phase 0A review/inventories/archive and transition records are preserved byte-for-byte in ignored `.local/phase-0b-startup/`; relocations and archive hash are in [BOOTSTRAP](BOOTSTRAP.md#local-provenance-preservation). Public historical receipts are labeled portable adaptations; later edits/code do not inherit the old review. Raw B02 receipts are in ignored `.local/b02/`. Reference code/data/PDFs were not changed or published.

## Budget, limitations and next authorized action

[Verification ledger](VERIFICATION.md) contains measured local checks and conservative
charges/reservations; [live closeout](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582) records final reconciliation after CI
and review. Stop before the shared 7,200 CPU-second cap. CI jobs remain capped at
10 minutes, test address space at 1 GiB and designated scratch at 100 MiB.
macOS cannot enforce the same hard memory limit; observed RSS is recorded.

Verified protection: `fast-checks` from GitHub Actions app 15368 required on an up-to-date PR; administrators enforced; stale approvals dismissed; conversations resolved; force pushes/deletions blocked. Zero separate human approval count follows the sole-maintainer provision, while exact independent review and explicit human merge remain required. Actions default read/no approval and auto-merge false. [Canonical protection record](WORKFLOW.md#bootstrap-protection).

Next: complete B04 required final-head CI, fresh Sol High independent review and
findings disposition, then present its concrete human merge checkpoint. After
human merge, verify merged-result CI and update [the live closeout record](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582),
close issue #4/milestone and the native goal only if all exits hold, then stop.
This link keeps the handoff resumable without claiming post-merge facts in a
pre-merge commit. Original/merged evidence and remaining limitations stay durable.

## Future orchestrator: accepted D-012 after Phase 0B

The canonical [Model selection and escalation](WORKFLOW.md#model-selection-and-escalation)
section implements all eight points of [accepted D-012](DECISIONS.md#decision-d-012-model-selection-and-exceptional-escalation).
It takes effect **after Phase 0B**; current orchestrator/agents continue unchanged.
Automatically loaded AGENTS links it; AGENT_BRIEFS records explicit model/effort,
escalation justification, bounded deliverable/stop and lead integration/outcome.
Sol High is the advanced default including science/review, Luna High serves narrow
work, and Astra is exceptional with no per-choice approval within existing
scope/resources and no extra authority/budget. Historical launch/archive/review
assignments are preserved. No global settings or tooling was changed.

D-012's five changed guidance files are AGENTS.md, docs/WORKFLOW.md,
docs/AGENT_BRIEFS.md, docs/DECISIONS.md and docs/HANDOFF.md. All eight points
passed the fresh B03 review and are merged at `6858849`; merged-result CI passed.
The canonical procedure remains in WORKFLOW, with concise routing elsewhere.
This is repository guidance, not a global model setting or tooling installation;
future runtime availability must be checked when assignments are made. It grants
no Phase 1 authority.
