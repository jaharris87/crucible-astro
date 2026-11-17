# CRUCIBLE progress

Updated 2026-11-17. **Phase 0A/0B complete; Phase 1 S01 active.**
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
| 1 — Data qualification | 0B complete; Phase 1 authorized; scientific contracts and provenance pending | S01 active; no qualified dataset | [Milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2), [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10) | None — audit candidate in preparation |
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
| [S01 #10 — Meaning/provenance and data card](https://github.com/jaharris87/crucible-astro/issues/10) | B04/0B complete; D-002 | Active bounded audit; [findings/acceptance packet](phase1/S01_AUDIT.md), [living raw card](data-cards/genesis_datacard_ccsn_raw_candidate.md); limited ingestion scope accepted; original input recovery active | None — documentation candidate in preparation |
| [S02 #11 — Quarantined reader/extraction](https://github.com/jaharris87/crucible-astro/issues/11) | Limited three-pair S01 ingestion semantics accepted; physical gates remain open | Active isolated implementation of [bounded proposal](phase1/S02_EXTRACTION_PROPOSAL.md); no training/reference eligibility | None |
| S03 — Coverage/benchmark/partitions | S01/S02; D-004/D-005/D-007 | Not started; parent mapping, conditioning, reference/tolerances and human benchmark acceptance pending | None |

## Scientific progress

A metadata-only inventory and three-pair structural audit are documented in
[S01](phase1/S01_AUDIT.md); **zero training/reference records are qualified**.
The collection's independent parent identities and wider coverage are unverified.
Reconstruction/RHS/rollout accuracy, abundance/energy scientific accuracy,
physical failures, inference/integration costs and reproducibility of a scientific
benchmark are **not yet evaluated**. No dataset, benchmark partition or final-test
use has human scientific acceptance. Synthetic tests and structural checks do not
supply that acceptance; NS1–NS3 remain incomplete.

Reports: [current Phase 1 snapshot](reports/2026-11-17-phase1-start.md), [meeting-report template](MEETING_REPORT_TEMPLATE.md), [initial bootstrap status](reports/2026-11-17-bootstrap.md). Reporting policy: [WORKFLOW](WORKFLOW.md#two-connected-progress-views-and-meeting-report).
