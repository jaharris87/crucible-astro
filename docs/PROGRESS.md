# CRUCIBLE progress

Updated **2026-11-20**. Phase 1, the documentation migration and **2A are complete**:
[Phase 1 receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012),
[2A receipt](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315).
Verified merged main is `8b6cf713969c4abdcc5353aa18141461bb509616` (PR #46).
[D-030](DECISIONS.md#decision-d-030-phase-2b-launch-and-selected-full-state-mlp)
invokes **2B only** under existing milestone #3. The sole active native goal covers
2B through human merge and merged verification; [handoff](HANDOFF.md) records its
exact objective. The model fit/reload/bitwise clean refit and all complete train/validation reports
reproduce. The exact independently reviewed MLP experiment is accepted under
[D-031](DECISIONS.md#decision-d-031-accept-the-reviewed-small-full-state-mlp-experiment).
Numerical reporting is complete; independent PR review and human merge/integration
remain required.

## Phase status

| Phase | Dependency | Status / evidence |
| --- | --- | --- |
| 0A — Design | Reference investigation | Complete; [review](REVIEW.md), [transition](TRANSITION.md) |
| 0B — Bootstrap | Adopted workflow/publication authority | Complete through audit `01f06d8`; [final receipt](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582), [milestone #1](https://github.com/jaharris87/crucible-astro/milestone/1) |
| 1 — Qualification/benchmark | 0B; S01–S03 authority | D-025 accepted; actual [exit evidence](phase1/PHASE1_CLOSEOUT.md), [qualified data card](data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md), final closure in the live receipt |
| 2 — Full-state baseline | D-029; qualified benchmark | 2A integrated; 2B numerical exits pass; negative pointwise result; review/merge/integration in live issue; [incremental sequence](PHASE_2_LAUNCH.md), milestone #3 |
| 3–5 — Reduction/comparison/prototype | Later accepted baselines/science/scope | Not started; no architecture or model selected |

## Active Phase 2 sequence

| Sub-phase | Dependency / deliverable | Status / next gate |
| --- | --- | --- |
| [2A #41](https://github.com/jaharris87/crucible-astro/issues/41) | Qualified named-version/use/split arrays, example and tests | Complete at PR #46 / `8b6cf71`; 489 installed-package tests, merged CI and all-row structural checks in final receipt |
| [2B #42](https://github.com/jaharris87/crucible-astro/issues/42) | Integrated 2A; one pointwise model/comparator proposal and reproducible validation | Active D-030; selected small full-state MLP + zero comparator; [MLP protocol](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042652534) / [independent scope PASS](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042701075); [experiment accepted](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042848745), fit/reload/bitwise refit and all full scoring reports reproduce; [card](model-cards/genesis_modelcard_full_state_mlp_v0_1.md)/[report](reports/2026-11-20-phase2b.md); review/merge/integration tracked in live issue; final-test outcomes sealed |
| [2C #43](https://github.com/jaharris87/crucible-astro/issues/43) | Integrated 2B; analytic integration/convergence/failure checks | Scope acceptance pending; no new XNet execution |
| [2D #44](https://github.com/jaharris87/crucible-astro/issues/44) | Integrated 2C; accepted real reference trajectories/protocol | Scope and scientific/producer-execution decisions pending |
| [2E #45](https://github.com/jaharris87/crucible-astro/issues/45) | Integrated 2D; frozen pointwise/rollout/cost evaluation and report | Scope and final-test release pending; human baseline acceptance before milestone closure |

D-027 migration #39 is closed at `804fb75`; its linked final receipt controls closure.
Later issues remain short dependency/deliverable summaries. The integrated audit
stays after 2C integration in #43. No next sub-phase starts before scope acceptance
and preceding integration. Current protocol, review and next decision remain in #42;
its PR will carry execution/review/merge/integration receipts.

## Phase 1 issue dependencies and integrations

| Work | Dependencies | Actual status / next gate | PRs |
| --- | --- | --- | --- |
| [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10) | 0B, audited producer/reference semantics | D-025 named-scope acceptance; final overlay/card/source review and closeout integration in final receipt | [#12](https://github.com/jaharris87/crucible-astro/pull/12), [#19](https://github.com/jaharris87/crucible-astro/pull/19), [#24](https://github.com/jaharris87/crucible-astro/pull/24), [#35 closeout](https://github.com/jaharris87/crucible-astro/pull/35) |
| [S02 #11](https://github.com/jaharris87/crucible-astro/issues/11) | Accepted bounded semantics | Quarantined reader complete; malformed/order/units/mask checks and independently interpreted real records | [#13](https://github.com/jaharris87/crucible-astro/pull/13) |
| [Diagnostic #14](https://github.com/jaharris87/crucible-astro/issues/14) | Separate D-017 authority | Exactly three calls complete/reviewed; authority exhausted | [#16](https://github.com/jaharris87/crucible-astro/pull/16) |
| [S03 #15](https://github.com/jaharris87/crucible-astro/issues/15) | S01/S02, accepted reference and groups | D-024/D-025 accepted; exact qualified memberships checked by author; fresh final artifact review and closeout integration remain in receipt | [#17](https://github.com/jaharris87/crucible-astro/pull/17), [#27](https://github.com/jaharris87/crucible-astro/pull/27), [#34](https://github.com/jaharris87/crucible-astro/pull/34), [#35 closeout](https://github.com/jaharris87/crucible-astro/pull/35) |
| [Pilot reference #18](https://github.com/jaharris87/crucible-astro/issues/18) | D-019/D-020, exact inputs and execution | All 5,157 calls and retained evidence verified; D-025 accepts named numerical purpose, final overlay closure tracked above | [#20](https://github.com/jaharris87/crucible-astro/pull/20), [#25](https://github.com/jaharris87/crucible-astro/pull/25) |
| [Reader repair #21](https://github.com/jaharris87/crucible-astro/issues/21) | Exact zero-sign evidence | Complete; original binary bits and other alignment checks preserved | [#22](https://github.com/jaharris87/crucible-astro/pull/22) |
| [Pilot HDF5 #23](https://github.com/jaharris87/crucible-astro/issues/23) | Complete pilot reference evidence | Quarantined engineering complete; original pilot artifact/card unchanged | [#25](https://github.com/jaharris87/crucible-astro/pull/25) |
| [Remaining reference #26](https://github.com/jaharris87/crucible-astro/issues/26) | D-021 scope, reviewed D-023 authority | All 19,159 calls verified (19,157 new + two repeated controls); fresh retained-evidence review integrated; authority exhausted | [#28](https://github.com/jaharris87/crucible-astro/pull/28), [#32](https://github.com/jaharris87/crucible-astro/pull/32) |
| [Physical diagnostics #29](https://github.com/jaharris87/crucible-astro/issues/29) | D-022 direction | Engineering complete; physical allowances/timescales/scales remain unapproved for later application uses | [#30](https://github.com/jaharris87/crucible-astro/pull/30) |
| [Primary union #31](https://github.com/jaharris87/crucible-astro/issues/31) | Both completed reference packets, exact working membership | Engineering complete, merged `44c25ab`; [390-test integration](https://github.com/jaharris87/crucible-astro/pull/32#issuecomment-7014367929); immutable all-false payload | [#32](https://github.com/jaharris87/crucible-astro/pull/32) |
| [Native scoring #33](https://github.com/jaharris87/crucible-astro/issues/33) | D-024, primary union | Merged `950ffa8`; both findings fixed, bounded freshness and [419-test merged integration](https://github.com/jaharris87/crucible-astro/pull/34#issuecomment-7014572050) pass | [#34](https://github.com/jaharris87/crucible-astro/pull/34) |
| [Audit reconciliation #36](https://github.com/jaharris87/crucible-astro/issues/36) | Independent audits of `15ac601`, accepted D-024/D-025 | [Dispositions](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016554530); D-026 accepted, [PR #37 integrated `850996e`](https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017579899). PR #35 integrated `e86c7a2` after final independent review/human approval; merged tree, installed package, 454 tests and CI pass. Closure recorded in the final receipt | [#37 numerical repairs](https://github.com/jaharris87/crucible-astro/pull/37), [#35 closeout](https://github.com/jaharris87/crucible-astro/pull/35) |

## Scientific status

Qualified view: **24,314 / 380 / 94** states/histories/operational groups, with
17,659/3,220/3,435 states in train/validation/test. It supports only the named
finite within-parent native numerical-emulation claim. Energy/rollouts, physical
application accuracy, independent simulations and wider CCSN/NSM coverage remain
unqualified. MLP fit/preprocessing/reload, bitwise clean reproduction and complete pointwise
reports are verified. Validation whole-vector attainment is 0
for every D-024 profile; nonzero relative RMS/max have unbounded binary64 reports.
Reconstruction/rollout performance and scientific speedup remain **not evaluated**. Full NS1–NS3 are not completed here.

[Handoff](HANDOFF.md) gives the stop/resumption boundary. Historical
[Phase 1 start](reports/2026-11-17-phase1-start.md) and
[bootstrap report](reports/2026-11-17-bootstrap.md) remain unchanged snapshots.
Use [the meeting-report template](process/MEETING_REPORT_TEMPLATE.md) and actual final
receipt/card for current reporting, not those dated snapshots.
