# CRUCIBLE progress

Updated 2026-11-17. Local documentation view; **Phase 0B authorized and active; publication confirmed under D-001; seed initialization pending**. Issue IDs below refer to local drafts, not created GitHub issues. B03 will connect this view to actual issues, milestones and PRs after publication confirmation. Use existing GitHub milestones/issues plus this small table; no custom dashboard is needed.

## Phases

| Phase | Dependency | Status | Issues / evidence | Linked PRs |
| --- | --- | --- | --- | --- |
| 0A — Design | Reference investigation | Complete | [Review and disposition](REVIEW.md), [maintainer transition](TRANSITION.md) | None — documentation-only work |
| 0B — Bootstrap | Authorization supplied; publication readiness for public content | Active — local preparation | [B01–B04](BACKLOG.md#bootstrap-sequence) | None — repository/PRs not created |
| 1 — Data qualification | 0B; scientific contracts and provenance | Not started | [S01–S03](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 2 — Full-state baseline | Qualified data and benchmark | Not started | [S04](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 3 — Reduced dynamics | Reproducible baseline; method decision | Not started | [S05](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 4 — Controlled comparison | Reduced-method evidence; comparison budget | Not started | [S06](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |
| 5 — Prototype and reporting | Comparison evidence; release readiness | Not started | [S07](BACKLOG.md#next-scientific-issues-draft-in-detail-only-after-their-prerequisites) | None |

## Bootstrap issues

| Local issue | Phase | Dependencies | Status / next gate | Linked PRs |
| --- | --- | --- | --- | --- |
| [B01 — Repository](BACKLOG.md#b01--establish-repository-identity-and-adopt-the-design) | 0B | D-001 publication readiness | Active — seed preparation; publication confirmed; seed pending | None |
| [B02 — Package/checks](BACKLOG.md#b02--minimal-package-and-repeatable-development-checks) | 0B | B01 | Not started | None |
| [B03 — CI/progress/reporting](BACKLOG.md#b03--minimal-ci-issuepr-records-and-review-lifecycle) | 0B | B01/B02 | Prepared locally; live linkage/CI pending B01/B02 | None |
| [B04 — Validator demonstration](BACKLOG.md#b04--demonstrate-the-complete-cycle-with-fixture-manifest-species-order-validation) | 0B | B02/B03 | Not started | None |

Keep phase, dependency, status and linked PR fields current at issue/PR handoffs and closeout. Add actual issue/milestone URLs when created; keep “None” explicit until a PR exists. Link each completed claim to its checks/review or merged SHA. Scientific milestones NS1–NS3 are not implied complete by engineering progress.

## Scientific progress

Dataset coverage, evaluated regimes, reconstruction/RHS/rollout accuracy, abundance and energy accuracy, physical failures, inference/integration costs and reproducibility: **not yet evaluated**. No experiments support results yet. Replace this status only for the evaluated scope, linking the experiment record, dataset/split and source/artifact identities; leave unmeasured quantities explicitly “not yet evaluated.” Synthetic bootstrap tests are software evidence, not scientific results.

Reports: [meeting-report template](MEETING_REPORT_TEMPLATE.md), [initial bootstrap status](reports/2026-11-17-bootstrap.md). Reporting policy: [WORKFLOW](WORKFLOW.md#two-connected-progress-views-and-meeting-report).
