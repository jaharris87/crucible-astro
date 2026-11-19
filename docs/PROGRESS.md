# CRUCIBLE progress

Updated 2026-11-19. **Phase 0A/0B complete; Phase 1 S01/S03 active; quarantined S02 and three-state diagnostic integrated.**
[Phase 1 milestone #2 — Data qualification and benchmark definition](https://github.com/jaharris87/crucible-astro/milestone/2)
tracks S01–S03 and justified Phase 1 issues as created. It stays open through
scientific acceptance, reviewed human merges and passing integration checks.
[Authority](PHASE_1_AUTHORITY.md), [handoff](HANDOFF.md) and the
[final Phase 0B closeout](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582)
provide the governing records. No additional project board is used.

## Phases

| Phase | Dependency | Status | Issues / evidence | Linked PRs |
| --- | --- | --- | --- | --- |
| 0A — Design | Reference investigation | Complete | [Review and disposition](REVIEW.md), [maintainer transition](TRANSITION.md) | None — documentation-only work |
| 0B — Bootstrap | Authorization supplied; publication readiness for public content | Complete including audit #8 at `01f06d8`; [final closeout](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582) | [Milestone / B01–B04](https://github.com/jaharris87/crucible-astro/milestone/1) | [B02 PR #5](https://github.com/jaharris87/crucible-astro/pull/5), [B03 PR #6](https://github.com/jaharris87/crucible-astro/pull/6), [B04 PR #7](https://github.com/jaharris87/crucible-astro/pull/7), [audit PR #9](https://github.com/jaharris87/crucible-astro/pull/9) |
| 1 — Data qualification | 0B complete; Phase 1 authorized; D-018/D-019 direction/contract accepted; qualification pending | Multi-trajectory audit active; no qualified dataset | [Milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2), [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10) | [Merged audit/card PR #12](https://github.com/jaharris87/crucible-astro/pull/12) |
| 2 — Full-state baseline | Qualified data and benchmark | Not started | [S04](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 3 — Reduced dynamics | Reproducible baseline; method decision | Not started | [S05](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 4 — Controlled comparison | Reduced-method evidence; authorized comparison scope | Not started | [S06](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 5 — Prototype and reporting | Comparison evidence; release readiness | Not started | [S07](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |

## Bootstrap issues

| Local issue | Phase | Dependencies | Status / next gate | Linked PRs |
| --- | --- | --- | --- | --- |
| [B01 #1 — Repository](https://github.com/jaharris87/crucible-astro/issues/1) | 0B | D-001 confirmed | Complete; seed `c3846a4`, [closeout](https://github.com/jaharris87/crucible-astro/issues/1#issuecomment-6958852938) | None — explicit seed exception |
| [B02 #2 — Package/checks](https://github.com/jaharris87/crucible-astro/issues/2) | 0B | B01 complete | Complete; human-merged `5d81381`, [integration checks](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959449805) | [PR #5](https://github.com/jaharris87/crucible-astro/pull/5) |
| [B03 #3 — CI/progress/reporting](https://github.com/jaharris87/crucible-astro/issues/3) | 0B | B01/B02 complete | Complete at `6858849`; fresh review, delegated human merge and merged CI passed ([receipt](https://github.com/jaharris87/crucible-astro/pull/6#issuecomment-6959958285)) | [PR #6](https://github.com/jaharris87/crucible-astro/pull/6) |
| [B04 #4 — Validator](https://github.com/jaharris87/crucible-astro/issues/4) | 0B | B02/B03 complete | Integrated at `8835481`; [human merge and passing merged CI](https://github.com/jaharris87/crucible-astro/pull/7#issuecomment-6960492520); synthetic validation only | [PR #7](https://github.com/jaharris87/crucible-astro/pull/7) |
| [#8 — External audit closeout](https://github.com/jaharris87/crucible-astro/issues/8) | 0B closeout | B04 integrated; D-013–D-015 accepted | Complete at `01f06d8`; [human merge/integration](https://github.com/jaharris87/crucible-astro/pull/9#issuecomment-6960937971), merged CI passes 42 tests | [PR #9](https://github.com/jaharris87/crucible-astro/pull/9) |

Keep phase, dependency, status and linked PR fields current at issue/PR handoffs and closeout. Add actual issue/milestone URLs when created; keep “None” explicit until a PR exists. Link each completed claim to its checks/review or merged SHA. Scientific milestones NS1–NS3 are not implied complete by engineering progress.

## Phase 1 issues and gates

| Work | Dependencies | Current status / next gate | PR |
| --- | --- | --- | --- |
| [S01 #10 — Meaning/provenance and data card](https://github.com/jaharris87/crucible-astro/issues/10) | B04/0B complete; D-002 | Audit/card integrated in #12; [findings/acceptance packet](phase1/S01_AUDIT.md), [living raw card](data-cards/genesis_datacard_ccsn_raw_candidate.md); limited ingestion scope accepted; bounded input association checked; qualification/custodianship open | [Merged PR #12](https://github.com/jaharris87/crucible-astro/pull/12); [Merged evidence PR #24](https://github.com/jaharris87/crucible-astro/pull/24) |
| [S02 #11 — Quarantined reader/extraction](https://github.com/jaharris87/crucible-astro/issues/11) | Limited three-pair S01 ingestion semantics accepted; physical gates remain open | Quarantined engineering scope complete at `099d21e`; [integration receipt](https://github.com/jaharris87/crucible-astro/pull/13#issuecomment-6962235209); 86 tests and merged CI pass; all scientific eligibility false | [Merged PR #13](https://github.com/jaharris87/crucible-astro/pull/13) |
| [RHS diagnostic proposal #14](https://github.com/jaharris87/crucible-astro/issues/14) | S01 evidence; separate execution authority and exact EOS/build dependencies | Complete at `eb5e25d`; source/evidence review, human merge, merged CI and 96 local tests pass; authority exhausted, no label qualification | [Merged PR #16](https://github.com/jaharris87/crucible-astro/pull/16) |
| [Proposed fresh-RHS subset #18](https://github.com/jaharris87/crucible-astro/issues/18) | D-019 contract accepted; D-020 physical loop/offline checks and engineering evidence review integrated | Preparation-only human merge at `6807741`; initial/focused review and [merged CI / 126 local tests](https://github.com/jaharris87/crucible-astro/pull/20#issuecomment-6966731838) pass; RHS-PILOT-R1 resolved, exact pilot membership/state bits unchanged; official matching rate entry identified; D-020 physical loop returned normally; all 5,157 records/echoes and both controls pass fixed-width checks; exact offline comparison passes all 5,157 states / 825,120 components, fresh engineering evidence review integrated in #25, human scientific acceptance open, call authority exhausted; no upstream evaluation-history prerequisite | [Merged PR #20](https://github.com/jaharris87/crucible-astro/pull/20) |
| [Reader energy-zero alignment #21](https://github.com/jaharris87/crucible-astro/issues/21) | Expanded S03 raw checks; familiar layout, no new physical semantics | Complete at `87f550c`; fresh review, human merge and [137-test integration](https://github.com/jaharris87/crucible-astro/pull/22#issuecomment-6966932648) pass; binary bits and all scientific exclusions preserved | [Merged PR #22](https://github.com/jaharris87/crucible-astro/pull/22) |
| [Native pilot HDF5 candidate #23](https://github.com/jaharris87/crucible-astro/issues/23) | D-019 semantics; complete #18 comparison required for real materialization | Engineering issue closed after human merge at `c26069e`; repaired local materialization/card/execution evidence reviewed; [265-test combined integration and merged CI](https://github.com/jaharris87/crucible-astro/pull/25#issuecomment-6968843133) pass; all scientific masks false, S01/#18 scientific gates open | [Merged PR #25](https://github.com/jaharris87/crucible-astro/pull/25) |
| [Remaining-primary reference #26](https://github.com/jaharris87/crucible-astro/issues/26) | D-021 working pool; D-023 exact execution; pilot evidence integrated | Preparation human-merged at `775f988`; exact 19,159 calls and full comparison/job/actual-receipt/transfer checks [complete](https://github.com/jaharris87/crucible-astro/issues/26#issuecomment-7012879183), including both repeat controls; physical-call authority exhausted. Fresh retained execution review under #31 remains pending; no scientific qualification | [Merged PR #28](https://github.com/jaharris87/crucible-astro/pull/28) |
| [S03 #15 — Coverage/benchmark/partitions](https://github.com/jaharris87/crucible-astro/issues/15) | S02 engineering integrated; S01/D-004/D-005/D-007 scientific gates open | Preparation integrated at `615c99b`; D-018 multi-trajectory direction accepted; [83-pair reconnaissance](phase1/MULTITRAJECTORY_AUDIT.md) complete, all 6,433 ordinary states audited / 5,157 source-table candidates; input/position evidence integrated in #19 at `116e682`; 80/5,157 remains a qualification pilot; [fixed primary expansion](phase1/PRIMARY_EXPANSION_AUDIT.md) checks 380 familiar histories / 24,314 table candidates and measured positions; D-021 accepts the exact expanded working input/group contract, integrated with #24 records at `33c368c`; [candidate constructor/checks](phase1/PARTITIONS.md) reproduce all accepted groups/roles and retain exclusions; human-merged #27 at `4840ba1`, [265-test/CI integration and post-merge review freshness](https://github.com/jaharris87/crucible-astro/pull/27#issuecomment-6968843354) pass; scientific gate fails for zero eligible membership; final qualification/metrics/tolerances/final-test use remain open | [Merged PR #17](https://github.com/jaharris87/crucible-astro/pull/17); [Merged multi-trajectory PR #19](https://github.com/jaharris87/crucible-astro/pull/19); [Merged expansion PR #24](https://github.com/jaharris87/crucible-astro/pull/24); [Merged partition PR #27](https://github.com/jaharris87/crucible-astro/pull/27) |
| [Provisional physical-abundance budgets #29](https://github.com/jaharris87/crucible-astro/issues/29) | D-022 bounded implementation | Engineering issue closed after human merge at `5e42cb9` on 2026-11-19; [338-test exact-tree/CI integration](https://github.com/jaharris87/crucible-astro/pull/30#issuecomment-7012669858) passes. Scientific allowances/scales/timescales/critical selection unresolved; no model prediction or scientific-accuracy claim | [Merged PR #30](https://github.com/jaharris87/crucible-astro/pull/30) |
| [Primary native-RHS union #31](https://github.com/jaharris87/crucible-astro/issues/31) | Complete D-020/D-023 packets; exact D-021 working membership | One actual separate 24,314-state / 380-history candidate; [card](data-cards/genesis_datacard_ccsn_primary_native_rhs_union_v0_1.md)/[contract](phase1/PRIMARY_RHS_DATASET.md), exact-repeat deduplication and independent every-field/source/membership author check. Four masks false; fresh source/execution/artifact review, human merge and integration pending; #10/#15 scientific gates open | None — draft creation pending |

## Scientific progress

A metadata-only inventory and three-pair structural audit are documented in
[S01](phase1/S01_AUDIT.md); **zero training/reference records are qualified**.
The maintainer identifies one [parent simulation](phase1/PARENT_PROVENANCE.md);
wider coverage and related-run/family grouping are not established. The three-state
[label audit](https://github.com/jaharris87/crucible-astro/pull/16) measured stored/fresh
differences, not model accuracy or data qualification. D-018 requires multiple trajectories in the training pool and separate related-group
holdouts; A/B/C are audit aliases, not assigned partitions. D-019 accepts the
new pointwise reference contract, with energy/rollout excluded. D-020 and D-023 separately authorized the exact pilot and remaining-primary
loops; both have completed numerical/evidence closure and their call authorities
are exhausted. Fresh primary execution/artifact review and scientific
qualification remain separate. The [147-record proposal](phase1/NEXT_RHS_SUBSET.md)
is retained as a superseded standalone proposal; the live #18 record tracks
actual attempts and results. D-021 accepts the exact expanded working scope
and operational grouping; [candidate mechanical partitions](phase1/PARTITIONS.md)
match that oracle, while the scientific gate fails for zero eligible records.
Reconstruction/RHS/rollout accuracy, abundance/energy scientific accuracy,
physical failures, inference/integration costs and reproducibility of a scientific
benchmark are **not yet evaluated**. The numerical-reference contract is accepted; no dataset qualification, final
benchmark partition or final-test use has human scientific acceptance. Synthetic tests and structural checks do not
supply that acceptance; NS1–NS3 remain incomplete.

Reports: [current Phase 1 snapshot](reports/2026-11-17-phase1-start.md), [meeting-report template](MEETING_REPORT_TEMPLATE.md), [initial bootstrap status](reports/2026-11-17-bootstrap.md). Reporting policy: [WORKFLOW](WORKFLOW.md#two-connected-progress-views-and-meeting-report).
