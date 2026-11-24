# CRUCIBLE progress

Updated **2026-11-24**. Phase 1, the documentation migration, **2A–2C are complete**:
[Phase 1 receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012),
[2A receipt](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315),
[2B receipt](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7043899683).
The original 2C implementation is merged through [PR #48](https://github.com/jaharris87/crucible-astro/pull/48)
at `505d5562040ec7733ec7903c7123f86921653186`; [merged checks](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045039634)
and the scheduled [independent integrated audit](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045144994)
passed within their recorded limits. Subsequent independent Codex, Claude and
Gemini audits supplied concrete counterevidence. The maintainer authorized their
[bounded assessment and repair](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047204328)
before final closeout. [Consolidated dispositions](reports/2026-11-20-phase2c-audit-assessment.md)
preserve attribution, reproduced defects, rejected claims and deferred work.

**Final 2C acceptance:** the maintainer [accepted closeout](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047751430)
after [PR #49](https://github.com/jaharris87/crucible-astro/pull/49) merged at
`eaa94463475e068c303b32f6a307f6f53ea5cc4e`. The [merged-result receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047719265)
records 651 passing installed tests and merged Linux CI, eight-attempt regression
with 80/80 arrays bitwise unchanged, 20,879 passing frozen callbacks, reload/compare
and original scoring/protected-artifact checks. No demonstrated repair blocker
remains. The accepted negative 2B result, original source bindings and final-test
seal remain unchanged. [Final #43 closure](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047856713) followed PR #50 / `75b2ec3`; milestone #3 stays open.

**Active 2D / D-035:** the maintainer invoked #44 on 2026-11-20. Clean startup
at current merged main `75b2ec3` and preceding final receipts were verified once.
One native goal covers 2D only. Read-only producer/input discovery and the
[concrete two-case protocol](../experiments/trajectory_reference/PROTOCOL.md) are
prepared; bounded independent protocol review and focused repairs pass.
[D-036 / scientific and producer acceptance](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7048328458)
was [explicitly given](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7048371383).
Work resumed on explicit maintainer request, 2026-11-23, for offline diagnosis,
repository repairs and a bounded revised diagnostic proposal. D-038 and D-039 bounded producer campaigns are complete; no further producer
execution is authorized; [draft PR #51](https://github.com/jaharris87/crucible-astro/pull/51) is incomplete.
No producer work occurred before the decision.
The first native build (`c28c527`, job 61685010) succeeded. All ten synthetic
scenarios executed; two correct expected failures were falsely rejected because
the runner searched console output instead of the native terminal status.
No physical control, Jacobian or trajectory started. The runner repair passes
focused independent review, all 120 Phase 2D Python tests and offline replay of
all ten native fixture results. D-037 [explicitly accepts](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7050412199)
one replacement fresh build; job 61689197 is submitted from reviewed `a771930`.
The maintainer then requested a pause. Job 61689197 is terminal CANCELLED:
both controls passed, five development runs failed at the first step, validation
L0 was interrupted, and four validation runs plus six diagnostics were not attempted.
No reproduction build was submitted. [Pause checkpoint](reports/2026-11-20-phase2d-checkpoint.md)
and [live receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7050616078)
preserve results, raw identities, independently confirmed diagnostic protocol
defect and next review/authority boundary. No reference set is accepted.
On resumption, D-038 protocol review and focused repair verification pass at
`ae69715` (P2D-DIAG-001 mass-weighted reporting fix). All 909 installed tests,
Linux CI and required checks pass. The [concrete decision packet](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7106057047)
received [explicit scientific/producer acceptance](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7107405775)
in chat (“approved”) before any diagnostic build/call. The accepted campaign now completed: one build, eleven synthetic fixtures, nine
processes and 4,384 RHS calls; no repair/restart/trajectory step. The [diagnostic
report](reports/2026-11-23-phase2d-diagnostics.md) records passing identity,
repeatability, twelve complete Jacobians and 36 directional agreement checks,
with four refused directional samples retained. Conditional assembly error is
material but does not explain the full stalled residual. Fresh reload and bounded
independent artifact assessment pass. No trajectory rerun or later phase is authorized.
D-034 does not delegate 2D merges. See [handoff](HANDOFF.md) for the next decision.

**Resumed on maintainer request, 2026-11-24:** D-039 reporting and independent
assessment are complete; no new producer work has occurred. The preserved
2026-11-23 pause remains historical. [D-040's concrete proposal](../experiments/trajectory_reference/CORRECTION_PROTOCOL.md)
explicitly changes nonlinear stopping while retaining D-039's RHS and original
global convergence gates. Next: independent protocol review and explicit
scientific/producer decision. [The resumption record](reports/2026-11-24-phase2d-resumption.md)
also retains model-scaling/log/PCA/AE/width feedback for later scope. The one 2D
goal is active; full 2D remains incomplete, with no accepted trajectory reference.

## Phase status

| Phase | Dependency | Status / evidence |
| --- | --- | --- |
| 0A — Design | Reference investigation | Complete; [review](REVIEW.md), [transition](TRANSITION.md) |
| 0B — Bootstrap | Adopted workflow/publication authority | Complete through audit `01f06d8`; [final receipt](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582), [milestone #1](https://github.com/jaharris87/crucible-astro/milestone/1) |
| 1 — Qualification/benchmark | 0B; S01–S03 authority | D-025 accepted; actual [exit evidence](phase1/PHASE1_CLOSEOUT.md), [qualified data card](data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md), final closure in the live receipt |
| 2 — Full-state baseline | D-029; qualified benchmark | 2A/2B integrated; negative 2B pointwise result preserved; 2C implementation, audits, repairs and merged checks accepted; 2D protocol preparation active; [incremental sequence](PHASE_2_LAUNCH.md), milestone #3 |
| 3–5 — Reduction/comparison/prototype | Later accepted baselines/science/scope | Not started; no architecture or model selected |

## Active Phase 2 sequence

| Sub-phase | Dependency / deliverable | Status / next gate |
| --- | --- | --- |
| [2A #41](https://github.com/jaharris87/crucible-astro/issues/41) | Qualified named-version/use/split arrays, example and tests | Complete at PR #46 / `8b6cf71`; 489 installed-package tests, merged CI and all-row structural checks in final receipt |
| [2B #42](https://github.com/jaharris87/crucible-astro/issues/42) | Integrated 2A; frozen pointwise MLP/comparator and reproducible validation | Complete at PR #47 / `a81552e`; 515 installed-package tests, exact independent review, human merge, merged CI/reload/preservation checks in final receipt; negative D-024 result; final-test model outcomes sealed |
| [2C #43](https://github.com/jaharris87/crucible-astro/issues/43) | Integrated 2B; checked callable adapter, independent analytic/stiff integration and scheduled merged 2A–2C audit | Complete: original PR #48 / `505d556`, scheduled audit and reconciled external audits, repair PR #49 / `eaa9446`, merged checks and explicit final acceptance; no fitting, real MLP rollout or new XNet execution |
| [2D #44](https://github.com/jaharris87/crucible-astro/issues/44) | Integrated 2C; accepted real reference trajectories/protocol | Active: D-038 diagnostics complete with independent artifact PASS; D-039 completed: arithmetic/derivatives pass, development first-step fails, validation reduced step only; independent artifact PASS; original failed/interrupted campaign preserved; no full-horizon reference; draft PR #51 |
| [2E #45](https://github.com/jaharris87/crucible-astro/issues/45) | Integrated 2D; frozen pointwise/rollout/cost evaluation and report | Scope and final-test release pending; human baseline acceptance before milestone closure |

D-027 migration #39 is closed at `804fb75`; its linked final receipt controls closure.
Later issues remain short dependency/deliverable summaries. No next sub-phase
starts before scope acceptance and preceding integration. The completed 2C audit,
repair and acceptance records remain in #43 and its PRs; original reports and
dispositions are preserved. Fresh-context read-only Sol High protocol review of
[D-039](../experiments/trajectory_reference/ASSEMBLY_QUALIFICATION_PROTOCOL.md)
passes at `8bcdb8f` without blockers. The maintainer [explicitly accepted](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7109353327)
its distinct numerical RHS and bounded qualification scope. Exact-candidate
implementation review and focused P2D-ASM-001 repair verification pass at `245ed95`;
1,006 installed tests, Linux CI and required checks passed before execution.
Job61873636 completed one build, sixteen compiled prerequisites and eleven physical
processes; both tight runs are correctly conditionally unattempted. The [actual
report](reports/2026-11-23-phase2d-assembly.md) retains 177,347 RHS calls, passing
arithmetic/derivative checks, development's ten failed first-step attempts and
validation's accepted 0.78125 microsecond endpoint. No requested interval or full
10 ms trajectory completes. Offline reporting portability repair passes 1,010 tests
and verification; fresh reload passes all 255 arrays and independent artifact
assessment gives bounded PASS without blockers. Final development corrections
are entirely lost to binary64 rounding; no absence-of-root claim follows.
Next: prepare an evidence-backed numerical proposal.
No further producer execution or full trajectory continuation is authorized. The
required passing 2D reference set remains incomplete.

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
