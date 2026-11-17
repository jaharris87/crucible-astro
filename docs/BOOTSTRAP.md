# Phase 0B bootstrap record

Date: 2026-11-17. **B01 complete**: confirmed publication, public repository and seed `c3846a4660e5915fe56c115202d9b1581a2319fd`. [Issue #1 closeout](https://github.com/jaharris87/crucible-astro/issues/1#issuecomment-6958852938) records the one-time exception and actual checks. [Milestone](https://github.com/jaharris87/crucible-astro/milestone/1) and B01–B04 issues now exist. This is a historical B01 record, not a tracker of later issues. Preparation observations below remain historical; [PROGRESS](PROGRESS.md) and [HANDOFF](HANDOFF.md) route to current execution state.

## Publication decision D-001

Accepted and not reopened: public `jaharris87/crucible-astro`, BSD-3-Clause. Proposed exact first line of [LICENSE](../LICENSE):

```text
Copyright (c) 2026 UT-Battelle, LLC.
```

The remaining license text is the standard BSD-3-Clause text from [SPDX](https://github.com/spdx/license-list-data/blob/main/text/BSD-3-Clause.txt), with the selected year/holder substituted. The [OSI description](https://opensource.org/license/bsd-3-clause) is a cross-reference. LICENSE is confirmed by the maintainer; it was published in the seed.

**Confirmed:** 2026-11-17: Maintainer explicitly answered “Confirm all three; proceed with public publication” to the prepared D-001 checkpoint: `Copyright (c) 2026 UT-Battelle, LLC.`, no additional government-rights/institutional notice required, and portable documentation plus original Phase 0B bootstrap code cleared for public release. No clearance is inferred from employment, account ownership or license selection. Basis: [TRANSITION licensing evidence](TRANSITION.md#licensing-evidence). No third-party institutional submission is authorized or performed.

Publication checkpoint satisfied. Publish only the prepared allowlisted seed under the launch authority. If different wording is required, apply the exact supplied wording and recheck the seed before publishing. A response that leaves clearance or required notices unresolved does not unlock publication.

## Public seed and initialization exception

The explicit file allowlist is [PUBLIC_SEED.txt](PUBLIC_SEED.txt); it includes only portable guidance, reporting, appropriate license and minimal repository metadata. Do not use broad `git add .` for initialization. Check every allowlisted path and the staged diff, plus excluded local provenance, before the minimum seed commit. The pending license becomes publishable only after D-001 is recorded.

The launch authorizes one minimum seed commit on `main` after publication readiness, because a PR needs a base. Record its exact SHA in B01 and this handoff. B02/B03/B04 implementation must use branches, draft PRs, exact-candidate independent review and human merge decisions. The seed does not contain package implementation, CI or a validator. No branch-protection exception is assumed for subsequent changes.

## Local provenance preservation

Before edits, all 21 startup files were copied byte-for-byte to ignored `.local/phase-0b-startup/` with their original relative layout and SHA-256 inventory `preservation.json`. This includes the exact pre-launch AGENTS, README, HANDOFF, EVIDENCE, TRANSITION, REVIEW, all three JSON inventories and the Phase 0A archive. No original reference projects or raw data were changed.

Relocations from public paths (exact bytes retained in that local tree):

| Original path | Local preserved path |
| --- | --- |
| `docs/SOURCE_SNAPSHOT.json` | `.local/phase-0b-startup/docs/SOURCE_SNAPSHOT.json` |
| `docs/REVIEW_SNAPSHOT.json` | `.local/phase-0b-startup/docs/REVIEW_SNAPSHOT.json` |
| `docs/FINAL_SNAPSHOT.json` | `.local/phase-0b-startup/docs/FINAL_SNAPSHOT.json` |
| `docs/history/phase-0a-reviewed.tar.gz` | `.local/phase-0b-startup/docs/history/phase-0a-reviewed.tar.gz` |

EVIDENCE now uses aliases, public bibliographic links and explicit non-distributed-reference notes. REVIEW and TRANSITION are labeled portable historical receipts with local-inventory links replaced by plain filenames; their exact originals are retained above. New documents and later edits are not claimed to have Phase 0A independent-review coverage. Archive SHA-256 remains `1b76f73f5ae36d4a75b134755e9f29a3747df731e1fa9e513891880c0ce5a4b3`.

## Startup observations and authority

- No `.git` directory or implementation was present. Connected GitHub lookup and authenticated owner `gh api repos/jaharris87/crucible-astro` both returned 404. CLI authentication identifies `jaharris87`; do not infer private publication or overwrite history if a repository subsequently appears.
- GitHub connector provides repository reads and PR actions but no repository/issue/milestone creation or protection-setting tools in the current catalog. Use authenticated `gh` for those missing capabilities once publication is confirmed; reread remote state first.
- Existing B03 scope and roadmap already include progress dependencies/status/PRs, reusable meeting template, initial report and “not yet evaluated” scientific results. No second dashboard or speculative scientific issue tree is needed.
- Prepared local issue bodies: `.local/issues/B01.md` through `B04.md`. Their published records are issues #1–#4; see the milestone and current handoff for execution status.
- One read-only B02/B03 tooling investigator was dispatched as explicit `gpt-6.1-sol`, high reasoning, fresh context. This is investigation, not independent candidate review. No substitution was made.

## Verification and remaining gates

The aggregate D-011 cap is 7,200 CPU-seconds across local and CI verification. Keep actual accounting in [VERIFICATION](VERIFICATION.md), estimate each next check first, and do not repeat passing checks without changes or unresolved concerns. B02 local software checks now exist; no CI, mutation, independent Phase 0B review or post-seed merge/integration result exists at this snapshot.

Completed: public repository/base and issue/milestone links; B02 local package/fresh setup/import controls. Pending: B02 independent review/human merge/integration; B03 draft-PR failure/pass CI, exact required checks and actual protection settings; B04 test-first invalid controls and ordered-to-set mutation; exact-SHA fresh reviews/dispositions; human merges; merged-result checks and closeout. Scientific results: **not yet evaluated**.

## Tooling investigation

Read-only `gpt-6.1-sol` high investigator verified Darwin arm64, 16 logical CPUs, Python 3.12.9 and 3.13.0, and uv 0.10.11. Default uv cache access was sandbox-restricted; project-local `UV_CACHE_DIR=.local/cache/uv` is the selected path. Adopt Python 3.12.9 initially, one uv.lock, no runtime dependencies, pytest/Ruff development checks and a pinned build backend. No collaborator constraint was supplied; support choice is reversible. No installation or tests occurred in the investigation. Conservative charge: 20 CPU-seconds. B02/B03 will verify the actual environment and draft CI; no review coverage is claimed.
