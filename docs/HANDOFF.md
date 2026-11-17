# CRUCIBLE Phase 0B handoff

Date: 2026-11-17. **Phase 0B active; B01/B02 complete; B03 in draft PR #6;
B04 not implemented.** Native goal remains active and incomplete until all exits
hold. No Phase 1, real-data ingestion or model work is authorized.

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
- [B03 #3](https://github.com/jaharris87/crucible-astro/issues/3), [draft PR #6](https://github.com/jaharris87/crucible-astro/pull/6), branch `bootstrap/b03-ci`, managed worktree `b03-ci-preparation`, base `5d81381ddfde28cb6f86980e616d7c5065bae768`. [Evidence](bootstrap/B03-EVIDENCE.md) records configuration, reporting, D-012 and the intended failing draft CI run. The temporary probe is removed in this candidate; final passing check and fresh review remain required before human handoff. The PR discussion/checks bind subsequent outcomes to exact head/base/tested merge identities. `main` protection is configured and read back; see below.
- [B04 #4](https://github.com/jaharris87/crucible-astro/issues/4) has a
  [contract investigation](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6958940130)
  only; no validator/test/mutation implementation. It awaits integrated B03.

Current Sol workers explicitly use `gpt-6.1-sol` High without substitution.
B03 implementation/self-review is not independent review. No B03 human merge
authority has been delegated.

## Progress, reporting and history

[Progress view](PROGRESS.md), [Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1), [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap report](reports/2026-11-17-bootstrap.md) show actual issue/PR links and dependencies. Scientific results remain **not yet evaluated**; synthetic checks do not complete NS1–NS3.

All 21 startup files, original Phase 0A review/inventories/archive and transition records are preserved byte-for-byte in ignored `.local/phase-0b-startup/`; relocations and archive hash are in [BOOTSTRAP](BOOTSTRAP.md#local-provenance-preservation). Public historical receipts are labeled portable adaptations; later edits/code do not inherit the old review. Raw B02 receipts are in ignored `.local/b02/`. Reference code/data/PDFs were not changed or published.

## Budget, limitations and next authorized action

[Verification ledger](VERIFICATION.md): 1,194 CPU-seconds charged after the first CI job (11 seconds × 4 CPUs = 44); 120 remains reserved for lead checks and 2,400 for the corrected CI job. No subsequent job is launched without reconciling its predecessor. Each job is capped at 10 minutes; test processes use a 1 GiB address-space limit and scratch a 100 MiB tmpfs. First-run measured peak RSS was 40,980 KiB and scratch use 84 bytes.

Verified protection: `fast-checks` from GitHub Actions app 15368 required on an up-to-date PR; administrators enforced; stale approvals dismissed; conversations resolved; force pushes/deletions blocked. Zero separate human approval count follows the sole-maintainer provision, while exact independent review and explicit human merge remain required. Actions default read/no approval and auto-merge false. [Canonical protection record](WORKFLOW.md#bootstrap-protection).

Next: require corrected passing CI for the exact final B03 candidate, dispatch a fresh `gpt-6.1-sol` High reviewer covering workflow and D-012 policy, preserve findings/dispositions and focused fixes if needed, then present the human merge checkpoint. This document is the pre-final-CI candidate snapshot; [PR #6](https://github.com/jaharris87/crucible-astro/pull/6) is the source of record for subsequent live outcomes and exact final SHAs. Only after the human merge and merged-result checks can B03 close and B04 proceed. Phase 0B remains incomplete.

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

B03’s fresh `gpt-6.1-sol` High review, human merge and integration are pending.
At Phase 0B closeout, list AGENTS.md, docs/WORKFLOW.md, docs/AGENT_BRIEFS.md,
docs/DECISIONS.md and this handoff, the canonical section, exact review/merge
status and model availability limitations. No model unavailability/substitution
has been reported in this pass; no Astra invocation occurred. This policy grants
no Phase 1 authority.
