# CRUCIBLE initial bootstrap status — 2026-11-17

**Snapshot:** Phase 0B launch authorized 2026-11-17; no Git commit or PR exists. **B01 local preparation active; publication confirmed under D-001; seed initialization pending.** This report prepares B03 reporting; it does not satisfy B03's live workflow/CI requirements.

**Development:** Phase 0A design and independent review completed; maintainer adopted the bootstrap scope, workflow and verification budget. Root guidance and handoff now reflect the invoked launch prompt; the native Phase 0B goal is active. Local progress/reporting documents were added at the maintainer's request. See the [current progress view](../PROGRESS.md) and [transition record](../TRANSITION.md).

| Phase / issue | Dependencies / next gate | Status | Linked PR |
| --- | --- | --- | --- |
| 0A — Design | None outstanding for design handoff | Complete; [review evidence](../REVIEW.md) | None — local documentation |
| 0B / B01 | Institutional copyright/release confirmation before publication | Active — seed preparation | None |
| 0B / B02 | B01 | Not started | None |
| 0B / B03 | B01/B02 | Not started; reporting documents prepared only | None |
| 0B / B04 | B02/B03 | Not started | None |

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

**Decisions:** owner `jaharris87`, public visibility, BSD-3-Clause and D-010/D-011 are accepted. The maintainer confirmed the 2026 UT-Battelle, LLC notice, no additional institutional/government-rights notice and release readiness. The concrete publication confirmation is prepared in [BOOTSTRAP](../BOOTSTRAP.md#publication-decision-d-001).

**Next interval:** complete local seed preparation, use the recorded D-001 confirmation, then execute [B01–B04](../BACKLOG.md) within the adopted aggregate 2 CPU-hour verification budget and associated limits. No model training, GPU, bulk-data work or HPC is authorized by this report.

**Links:** [meeting-report template](../MEETING_REPORT_TEMPLATE.md), [decisions](../DECISIONS.md), [handoff](../HANDOFF.md), [roadmap](../ROADMAP.md).
