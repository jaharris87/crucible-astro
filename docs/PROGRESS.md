# CRUCIBLE progress

Updated **2026-11-19**. Phase 0A/0B are complete. Phase 1's exact finite native
pointwise benchmark has D-025 human acceptance and a delivered qualified overlay;
[the final integration receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482)
tracks remaining audit corrections, exact-candidate review, human closeout merge
and merged checks. **Phase 1 is not complete.** No Phase 2 is authorized.
[Milestone #2 — Data qualification and benchmark definition](https://github.com/jaharris87/crucible-astro/milestone/2)
tracks S01–S03 and bounded follow-ups; there is no additional board.

## Phase status

| Phase | Dependency | Status / evidence |
| --- | --- | --- |
| 0A — Design | Reference investigation | Complete; [review](REVIEW.md), [transition](TRANSITION.md) |
| 0B — Bootstrap | Adopted workflow/publication authority | Complete through audit `01f06d8`; [final receipt](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582), [milestone #1](https://github.com/jaharris87/crucible-astro/milestone/1) |
| 1 — Qualification/benchmark | 0B; S01–S03 authority | D-025 accepted; actual [exit evidence](phase1/PHASE1_CLOSEOUT.md), [qualified data card](data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md), final closure in the live receipt |
| 2 — Full-state baseline | Qualified benchmark and separate authorization | Not started/authorized; [S04/model-card requirements](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) |
| 3–5 — Reduction/comparison/prototype | Later accepted baselines/science/scope | Not started; no architecture or model selected |

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
| [Audit reconciliation #36](https://github.com/jaharris87/crucible-astro/issues/36) | Independent audits of `15ac601`, accepted D-024/D-025 | [Dispositions](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016554530); D-026 accepted, [PR #37 merged `850996e`, 454 tests/CI pass](https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017579899). Current guidance/decision/base refresh still needs final review freshness, human closeout merge and integration | [#37 numerical repairs](https://github.com/jaharris87/crucible-astro/pull/37), [#35 closeout](https://github.com/jaharris87/crucible-astro/pull/35) |

## Scientific status

Qualified view: **24,314 / 380 / 94** states/histories/operational groups, with
17,659/3,220/3,435 states in train/validation/test. It supports only the named
finite within-parent native numerical-emulation claim. Energy/rollouts, physical
application accuracy, independent simulations and wider CCSN/NSM coverage remain
unqualified. Model/reconstruction/rollout performance, scientific speedup and
fitted preprocessing are **not evaluated**. Full NS1–NS3 are not completed here.

[Handoff](HANDOFF.md) gives the stop/resumption boundary. Historical
[Phase 1 start](reports/2026-11-17-phase1-start.md) and
[bootstrap report](reports/2026-11-17-bootstrap.md) remain unchanged snapshots.
Use [the meeting-report template](MEETING_REPORT_TEMPLATE.md) and actual final
receipt/card for current reporting, not those dated snapshots.
