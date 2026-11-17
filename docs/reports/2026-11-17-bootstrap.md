# CRUCIBLE initial bootstrap status — 2026-11-17

**Snapshot:** Phase 0B active, B01 complete, B02 [draft PR #5](https://github.com/jaharris87/crucible-astro/pull/5) awaiting exact-candidate focused repair verification and human merge. Source/code evidence: [B02 record](../bootstrap/B02-EVIDENCE.md); later changes reconcile documentation. This report does not satisfy pending live CI or merge exits.

**Development:** confirmed publication readiness and published the allowlisted public seed `c3846a4660e5915fe56c115202d9b1581a2319fd`; retained original local history. Created [Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1) and four governing issues. B02 locked package, failure/control, import and clean-install checks pass locally. Initial independent review found missing installed-license text; the preserved B02-R1 repair now passes strict noneditable checks (2 tests, full license/metadata/RECORD) and awaits focused verification. B03 workflow/templates are prepared in isolation and unpushed; B04 has a contract investigation only. [Current progress](../PROGRESS.md).

| Phase / issue | Dependencies / next gate | Status | Linked PR |
| --- | --- | --- | --- |
| 0A — Design | None outstanding for design handoff | Complete; [historical review](../REVIEW.md) | None — local documentation |
| 0B / [B01 #1](https://github.com/jaharris87/crucible-astro/issues/1) | D-001 confirmed | Complete; documented seed exception | None |
| 0B / [B02 #2](https://github.com/jaharris87/crucible-astro/issues/2) | B01 complete; focused repair verification then human merge | Repair review | [#5](https://github.com/jaharris87/crucible-astro/pull/5) |
| 0B / [B03 #3](https://github.com/jaharris87/crucible-astro/issues/3) | B02 integration | Local preparation; live CI/protection pending | None |
| 0B / [B04 #4](https://github.com/jaharris87/crucible-astro/issues/4) | B02/B03 integration | Contract preparation only | None |

**Science:** planned emphasis is CCSN particle trajectories and instantaneous RHS first, with finite-step exploration later. No dataset, model or experiment has been qualified or evaluated.

| Evidence category | Result |
| --- | --- |
| Dataset coverage / evaluated regimes | **not yet evaluated** |
| Reconstruction / RHS / rollout accuracy | **not yet evaluated** |
| Abundance / energy-generation accuracy | **not yet evaluated** |
| Physical constraints / failure diagnostics | **not yet evaluated** |
| Inference / end-to-end integration cost | **not yet evaluated** |
| Scientific reproducibility | **not yet evaluated** |

**Interpretation and milestones:** NS1–NS3 remain unfulfilled scientific deliverables. Completed design/review and future synthetic CI checks are development evidence, not abundance, energy or performance results.

**Decisions:** owner `jaharris87`, public visibility, BSD-3-Clause and D-010/D-011 are accepted. The maintainer confirmed the 2026 UT-Battelle, LLC notice, no additional institutional/government-rights notice and release readiness. The publication confirmation is recorded in [BOOTSTRAP](../BOOTSTRAP.md#publication-decision-d-001).

**Next interval:** finish B02 focused repair verification and present the exact human merge checkpoint, then continue [B01–B04](../BACKLOG.md) within the adopted aggregate 2 CPU-hour verification budget and associated limits. No model training, GPU, bulk-data work or HPC is authorized by this report.

**Links:** [meeting-report template](../MEETING_REPORT_TEMPLATE.md), [decisions](../DECISIONS.md), [handoff](../HANDOFF.md), [roadmap](../ROADMAP.md).
