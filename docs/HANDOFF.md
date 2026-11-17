# CRUCIBLE Phase 0B handoff

Date: 2026-11-17. **Phase 0B authorized and active; B01 complete; B02 in draft review.** Native goal is active in chat `01a1eafe-4230-7b81-a3ba-f7e0a122bd1b` and remains incomplete until all phase exits hold. No Phase 1, real-data ingestion or model work is authorized.

## Authority and publication

The maintainer invoked the launch prompt and confirmed D-001: `Copyright (c) 2026 UT-Battelle, LLC.`, no additional government-rights/institutional notice required, and release readiness for the portable documentation and original Phase 0B bootstrap code. Owner/public/BSD-3-Clause, D-010 workflow and D-011 budgets are accepted. D-002/D-003 retain CCSN-first and both targets starting with qualified instantaneous RHS; D-004–D-009 remain open and do not block synthetic B04. See [DECISIONS](DECISIONS.md).

[Public repository](https://github.com/jaharris87/crucible-astro), `main`, BSD-3-Clause and admin access verified by GitHub API. B01's explicitly authorized one-time seed is `c3846a4660e5915fe56c115202d9b1581a2319fd`, containing exactly [22 allowlisted files](PUBLIC_SEED.txt). [B01 closeout](https://github.com/jaharris87/crucible-astro/issues/1#issuecomment-6958852938) records checks and the exception. No later direct-to-main action is authorized by that exception.

## Actual work and candidates

- [B02 issue #2](https://github.com/jaharris87/crucible-astro/issues/2), [draft PR #5](https://github.com/jaharris87/crucible-astro/pull/5), branch `bootstrap/b02-package`, base `c3846a4660e5915fe56c115202d9b1581a2319fd`. The PR record holds the exact current head/base and subsequent independent findings/dispositions. Initial implementation snapshot `c579b599347470be2c6d396a0a20e0e7d5e1c922` passed its software controls. Initial independent review of `44326c682100572b79774dab67bee4ff5173584d` found B02-R1: installed distribution omitted LICENSE. The [original finding and disposition](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959156535) are preserved. Repaired source `29b87bc9ee43564fc39b6ac4fa0e6a05f36ac273` passes strict clean noneditable installation, 2 tests without skips, lint/format and full installed-license/metadata/RECORD verification; the old install fails the new regression. [Evidence](bootstrap/B02-EVIDENCE.md) binds code/config/lock/test hashes. Later documentation reconciliation changes no executable inputs. Focused independent repair verification and human merge remain pending at this snapshot; the live PR discussion carries subsequent outcome and exact candidate identities.
- B02 uses Python 3.12.9, uv 0.10.11, one lock, pytest/Ruff and zero runtime dependencies. [Reproduction commands](../CONTRIBUTING.md). Observed test RSS stayed below 1 GiB; macOS rejected the attempted hard memory limit. Clean reproduction reused downloaded dependencies. Other platforms are unverified. Normal editable setup passes import/metadata but explicitly skips the copied-license inventory check because this uv backend does not copy license files for editable installs. Strict noneditable acceptance passes both tests; B03 CI will use noneditable installation.
- [B03 issue #3](https://github.com/jaharris87/crucible-astro/issues/3): isolated local preparation on `bootstrap/b03-ci`, commit `b03c0d5968a80095a6bd0c0c1e5ab9e4b8e43850`, from the seed base. Managed worktree name `b03-ci-preparation` is attached to this chat. Four files only: workflow, issue form, PR template and preparation record. YAML/configuration, shell syntax and whitespace checks passed; no test/CI run, push, PR or protection change. Reconcile onto merged B02 before live work. Proposed `fast-checks` is not yet an observed or required check.
- [B04 issue #4](https://github.com/jaharris87/crucible-astro/issues/4): [contract investigation](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6958940130) recorded; no validator/test/mutation implementation. Depends on integrated B02/B03.

All Sol workers explicitly used `gpt-6.1-sol`, high reasoning; no substitution. Implementation/self-review is not fresh independent PR review. No human merge approval is claimed.

## Progress, reporting and history

[Progress view](PROGRESS.md), [Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1), [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap report](reports/2026-11-17-bootstrap.md) show actual issue/PR links and dependencies. Scientific results remain **not yet evaluated**; synthetic checks do not complete NS1–NS3.

All 21 startup files, original Phase 0A review/inventories/archive and transition records are preserved byte-for-byte in ignored `.local/phase-0b-startup/`; relocations and archive hash are in [BOOTSTRAP](BOOTSTRAP.md#local-provenance-preservation). Public historical receipts are labeled portable adaptations; later edits/code do not inherit the old review. Raw B02 receipts are in ignored `.local/b02/`. Reference code/data/PDFs were not changed or published.

## Budget, limitations and next authorized action

See [verification ledger](VERIFICATION.md) for measured charges, pre-run reservations and the 7,200 CPU-second aggregate cap. No CI has run. Repository Actions defaults are read-only and cannot approve PRs; `main` is currently unprotected. B03 must verify live draft CI failure/pass, effective permissions and actual protection settings before its acceptance.

Next: exact-head/base focused read-only verification of repaired B02 PR #5 and introduced risks, preserve its disposition, then make ready and present the concrete human merge checkpoint. The initial fresh review is complete and its finding remains a blocker until focused verification passes. Do not merge without the maintainer merging or explicitly delegating that exact candidate. After the human decision, verify the merged result and close #2; then integrate B03 and subsequently B04 through their own gates. Continue independent preparation while a checkpoint is pending. Phase 0B cannot be marked complete while any human merge, integration check or other exit is missing.

## Accepted policy queued for B03 closeout

The maintainer added a model-selection policy effective **after Phase 0B**, recorded in [B03 scope addition](https://github.com/jaharris87/crucible-astro/issues/3#issuecomment-6959269014), planned decision D-012. B03 will add the canonical WORKFLOW section, concise AGENTS link, explicit model/effort/escalation brief fields, decision and next-orchestrator handoff. A fresh `gpt-6.1-sol` High reviewer must cover that policy change; no policy-review or merge completion is claimed here. Current agents/orchestrator continue unchanged. Historical launch/archives/reviews remain accurate; no global settings/tooling changes or Phase 1 authority.
