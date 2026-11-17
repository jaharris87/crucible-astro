# Maintainer-directed transition from Phase 0A to Phase 0B

Portable historical record, adapted during B01 solely to remove links to local-only artifacts. The exact original is retained in `.local/phase-0b-startup/docs/TRANSITION.md`; see [preservation record](BOOTSTRAP.md#local-provenance-preservation). This record describes the prior transition, not current execution authority.

Date: 2026-11-17. This is a **local documentation-only handoff**, after Phase 0A completion. It neither starts Phase 0B nor authorizes Git/GitHub mutations. The completed Phase 0A native goal is not reopened.

## Decisions and authority

The maintainer selected `jaharris87/crucible-astro`, public; CCSN particle trajectories first; and exploration of both target types beginning with instantaneous RHS. [DECISIONS](DECISIONS.md) records the answers and their limits. Interactive answers adopted **BSD-3-Clause**, **B01–B04 and the workflow** (D-010), and **the clarified phase-wide verification budget** (D-011). Scientific contract decisions D-004–D-009 remain open and do not block a synthetic bootstrap demonstration.

Root [AGENTS.md](../AGENTS.md) and the [future launch prompt](PHASE_0B_LAUNCH.md) reflect accepted policy; a planning choice is not authority to launch that prompt. No LICENSE, package, environment, repository, issue, branch, commit or PR is created by this transition.

## Licensing evidence

Sources consulted 2026-11-17:

- [ORNL Software Licensing](https://ornl.github.io/software-catalog/about/licenses/) lists BSD-3 and Apache-2.0 among its examples. It expressly requires approval before uploading ORNL software to the ORNL GitHub organization. It does not resolve this project's release status, ownership, or the personal-account case.
- The [linked BSD example](https://ornl.github.io/software-catalog/about/licenses/bsd-3-clause.txt) contains a 2018 copyright notice naming Lawrence Livermore National Security, LLC. It is not CRUCIBLE's notice. Do not copy it unchanged.
- [OSI's BSD-3-Clause text](https://opensource.org/license/bsd-3-clause) permits source/binary redistribution and modification subject to notice/disclaimer retention and non-endorsement conditions. It contains no express patent-grant section.
- [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0), sections 3–4, supplies an express contributor patent grant and patent-litigation termination condition, plus modified-file/notice obligations. Consider it if that patent clarity matters to the intended contribution ecosystem; no demonstrated project need currently requires switching.

Adopted choice: BSD-3-Clause remains the selected permissive default. **UT-Battelle, LLC is the maintainer's proposed copyright holder**, not a legal ownership conclusion established from employment alone. Before public publication, obtain the maintainer's confirmation of the correct institutional copyright wording/year, any required government-rights notice, and applicable release clearance. This gate follows the tentative information supplied; it is not a claim that the public ORNL page specifically governs a personal GitHub account. No need to choose private visibility while that fact is unresolved: keep local preparation local.

Package/dependency licenses and any future data permissions require their own checks before distribution. Selecting the project's code license does not license copied chemical/XNet code, proposal PDFs, or datasets.

## Historical review preservation

The original Phase 0A review record (`REVIEW.md`), initial inventory (`REVIEW_SNAPSHOT.json`), final reviewed-core inventory (`FINAL_SNAPSHOT.json`), and reference fingerprints (`SOURCE_SNAPSHOT.json`) are preserved unchanged. They describe Phase 0A, **not** subsequent maintainer-directed adoption.

Because this directory has no Git history, the exact final reviewed core and closeout receipts are also preserved in `phase-0a-reviewed.tar.gz` (retained locally; see [preservation record](BOOTSTRAP.md#local-provenance-preservation)), SHA-256:

```text
1b76f73f5ae36d4a75b134755e9f29a3747df731e1fa9e513891880c0ce5a4b3
```

The archive contains 14 files: all 10 final-core inventory entries plus review/handoff receipts and both review inventories. Original final-core hashes can be verified against archived members even as living documents change. Do not regenerate old inventories to imply that the earlier reviewer approved new decisions. This archive and machine-specific evidence inventories are local provenance, not automatic public seed content.

## Maintainer-directed changes

- DECISIONS records explicit owner/public/BSD-3-Clause choices, CCSN-first and RHS-first/both-target sequence, and interactive D-010/D-011 adoption. No scientific evidence gate was waived.
- Root AGENTS activates concise routing, accepted policy, decision handling, resumption/handoff and scientific/review safeguards. AGENT_BRIEFS links to it instead of retaining a competing live instruction draft.
- README, WORKFLOW, BACKLOG, ROADMAP, DESIGN and VALIDATION reconcile adopted policy/direction with still-provisional science/interfaces. B04 shares the adopted phase-wide verification cap; it does not get a separate allowance.
- PHASE_0B_LAUNCH is a ready-to-use future prompt with a bounded native goal, explicit Git/GitHub/local authority, narrowly recorded seed exception, publication readiness, human merge checkpoints, budget accounting and all phase exits. It has not been executed.
- HANDOFF records current status and remaining prerequisites. Original REVIEW, review inventories, SOURCE_SNAPSHOT and archive remain unchanged. No new independent-review endorsement is claimed for this maintainer-directed transition; this task requested consistency verification.

## Transition verification

Completed lead verification:

- All 95 local links and 11 heading anchors resolve; Markdown code fences balance.
- Archive SHA-256 matches the recorded value; all 10 archived final-core entries match their reviewed hashes. Original REVIEW, REVIEW_SNAPSHOT, FINAL_SNAPSHOT and SOURCE_SNAPSHOT are byte-for-byte unchanged. All 59 selected reference fingerprints still match.
- Living guidance consistently records accepted owner/public/BSD-3-Clause, D-002/D-003 direction, adopted D-010 scope/workflow and D-011 phase-wide cap; proposals and remaining publication/scientific gates are explicit.
- Root guidance routes to one canonical workflow and decision register. Temporary local-only limits do not become permanent Git bans. The future prompt separately authorizes Git/GitHub/local work while preserving publication readiness, concrete human merge checkpoints and every Phase 0B exit.
- Launch prompt is approximately 1,200 words and has not been executed. No Git metadata, LICENSE, environment, framework or external repository was created. No Git/GitHub mutations or reference changes occurred.

Transition complete. No new independent review, software test execution or scientific qualification is claimed. Stop and await a separately authorized Phase 0B task.

## Subsequent maintainer-directed B03 refinement

On 2026-11-17, the maintainer added progress/reporting deliverables to B03. Local PROGRESS.md, MEETING_REPORT_TEMPLATE.md and the initial dated bootstrap report were prepared, linked from README/handoff, and reflected in the backlog, workflow, roadmap and unexecuted launch prompt. B03 still requires actual issue/milestone/PR linkage during separately authorized bootstrap. All scientific results are explicitly “not yet evaluated.” Original review records/inventories/archive and verification budget remain unchanged.

B03 refinement verification: all 131 local links and 22 heading anchors resolve; code fences balance. Historical review/inventories and archive are unchanged. No Git repository was initialized or Phase 0B operation executed.
