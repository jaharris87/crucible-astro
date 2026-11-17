# CRUCIBLE progress

Updated 2026-11-17. **Phase 0B active.** [GitHub milestone](https://github.com/jaharris87/crucible-astro/milestone/1) tracks B01–B04; this view supplies phase dependencies, work status and actual PR links. No separate Project board is needed.

## Phases

| Phase | Dependency | Status | Issues / evidence | Linked PRs |
| --- | --- | --- | --- | --- |
| 0A — Design | Reference investigation | Complete | [Review and disposition](REVIEW.md), [maintainer transition](TRANSITION.md) | None — documentation-only work |
| 0B — Bootstrap | Authorization supplied; publication readiness for public content | Active — B03 draft CI/review | [Milestone / B01–B04](https://github.com/jaharris87/crucible-astro/milestone/1) | [B02 PR #5](https://github.com/jaharris87/crucible-astro/pull/5), [B03 PR #6](https://github.com/jaharris87/crucible-astro/pull/6) |
| 1 — Data qualification | 0B; scientific contracts and provenance | Not started | [S01–S03](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 2 — Full-state baseline | Qualified data and benchmark | Not started | [S04](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 3 — Reduced dynamics | Reproducible baseline; method decision | Not started | [S05](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 4 — Controlled comparison | Reduced-method evidence; comparison budget | Not started | [S06](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 5 — Prototype and reporting | Comparison evidence; release readiness | Not started | [S07](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |

## Bootstrap issues

| Local issue | Phase | Dependencies | Status / next gate | Linked PRs |
| --- | --- | --- | --- | --- |
| [B01 #1 — Repository](https://github.com/jaharris87/crucible-astro/issues/1) | 0B | D-001 confirmed | Complete; seed `c3846a4`, [closeout](https://github.com/jaharris87/crucible-astro/issues/1#issuecomment-6958852938) | None — explicit seed exception |
| [B02 #2 — Package/checks](https://github.com/jaharris87/crucible-astro/issues/2) | 0B | B01 complete | Complete; human-merged `5d81381`, [integration checks](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959449805) | [PR #5](https://github.com/jaharris87/crucible-astro/pull/5) |
| [B03 #3 — CI/progress/reporting](https://github.com/jaharris87/crucible-astro/issues/3) | 0B | B01/B02 complete | Draft review: intended failure and corrected pass observed, protections verified; final-head check freshness/independent review/human merge pending | [PR #6](https://github.com/jaharris87/crucible-astro/pull/6) |
| [B04 #4 — Validator](https://github.com/jaharris87/crucible-astro/issues/4) | 0B | B02 complete; B03 pending | Contract investigated; implementation and full cycle pending | None |

Keep phase, dependency, status and linked PR fields current at issue/PR handoffs and closeout. Add actual issue/milestone URLs when created; keep “None” explicit until a PR exists. Link each completed claim to its checks/review or merged SHA. Scientific milestones NS1–NS3 are not implied complete by engineering progress.

## Scientific progress

Dataset coverage, evaluated regimes, reconstruction/RHS/rollout accuracy, abundance and energy accuracy, physical failures, inference/integration costs and reproducibility: **not yet evaluated**. No experiments support results yet. Replace this status only for the evaluated scope, linking the experiment record, dataset/split and source/artifact identities; leave unmeasured quantities explicitly “not yet evaluated.” Synthetic bootstrap tests are software evidence, not scientific results.

Reports: [meeting-report template](MEETING_REPORT_TEMPLATE.md), [initial bootstrap status](reports/2026-11-17-bootstrap.md). Reporting policy: [WORKFLOW](WORKFLOW.md#two-connected-progress-views-and-meeting-report).
