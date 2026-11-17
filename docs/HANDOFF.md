# CRUCIBLE Phase 0B handoff

Date: 2026-11-17. **Phase 0B authorized and active; B01 local preparation underway.** The maintainer invoked the launch prompt, including B03 reporting requirements. Native goal confirmed active in Codex chat `01a1eafe-4230-7b81-a3ba-f7e0a122bd1b`; it excludes Phase 1/models and remains incomplete until every exit, including human merge and merged-result checks, holds. The Phase 0A goal and historical transition remain complete. Startup inspection found documentation only and no Git repository; both connected GitHub and authenticated owner CLI lookups returned 404 for the destination. No remote publication has occurred.

## Accepted decisions and guidance

- D-001: public **`jaharris87/crucible-astro`**, **BSD-3-Clause**. Maintainer confirmed **Copyright (c) 2026 UT-Battelle, LLC.**, no additional institutional/government-rights notice and applicable release readiness for this seed/bootstrap code.
- D-002: initial training-set emphasis on **CCSN particle trajectories**; qualification and eventual NSM/r-process coverage remain necessary for the broader milestones.
- D-003: explore **both** target kinds, beginning with **qualified instantaneous RHS and the identity/full-state baseline**. Finite-step exploration remains planned with a separate contract; chemical precedent does not validate nuclear labels.
- D-010: workflow and **B01–B04 adopted**, including draft PRs, explicit exact-candidate fresh review, human merge decisions and the complete synthetic-validator demonstration.
- D-011: **2 aggregate CPU-hours for B01–B04 verification**, local and CI; 10 minutes per CI job; 1 GiB per test process; 100 MiB generated test scratch excluding dependency environments/caches. No GPU/training/bulk-data/HPC; review allowance and conservative accounting are in [BACKLOG](BACKLOG.md#bootstrap-verification-budget).

Root [AGENTS.md](../AGENTS.md) is now active. See [DECISIONS](DECISIONS.md) for answers and open questions, [TRANSITION](TRANSITION.md) for adoption/licensing evidence, and [WORKFLOW](WORKFLOW.md) for canonical process. D-004–D-009 remain open; no scientific choice blocks B04's synthetic demonstration.

## Completed work and preserved evidence

Phase 0A investigated chemical/nuclear sources, final proposal and selected papers, and XNet/fTimer workflows. Two Sol High investigators and one Astra High scientific investigator supported lead integration; fresh-context Astra High review and focused correction verification passed. The implicit-method clarification and R-001 energy-rate correction remain incorporated. [EVIDENCE](EVIDENCE.md) and [REVIEW](REVIEW.md) describe the original checks and limitations.

This transition records maintainer answers, activates concise guidance, reconciles living documents and supplies a future launch prompt. The original final reviewed core and receipts are preserved in the [historical archive](TRANSITION.md#historical-review-preservation). Original review inventories describe archived Phase 0A content, not the changed living documents. No later edit is represented as part of the earlier independent review.

## Progress and reporting

B03 now includes a lightweight issue/milestone view, reusable reporting and initial bootstrap status. Local documents are prepared: [progress view](PROGRESS.md), [meeting-report template](MEETING_REPORT_TEMPLATE.md), and [initial bootstrap status report](reports/2026-11-17-bootstrap.md). B03 live CI and GitHub linkage remain pending; local reporting preparation is authorized and underway. Scientific results remain **“not yet evaluated”** until supported by linked experiments.

## Remaining prerequisites and limitations

The exact source/build/run association, binary/HDF layout, label fidelity, physical units/conditions/energy conventions, scientific tolerances and method comparisons remain future audit/decision work. No dataset qualification, code implementation, training, solver run, timing claim or Git/GitHub mutation occurred during these documentation tasks. Copyright/release readiness was confirmed by the maintainer under D-001 before publication.

## Next authorized action

Continue authorized local B01 preparation. D-001 institutional notice/year and release-readiness confirmation is recorded. Now establish the minimum seed on main under the explicit one-time exception, create bounded B01–B04 issues/milestone, and execute B02/B03/B04 through their human merge checkpoints. The exception does not authorize later direct-to-main implementation.

Phase 0B will establish the authorized repository and minimal development environment/CI, then take the synthetic species-order validator through issue, checks, pushed PR, independent review, disposition, human merge and merged-result verification. It is incomplete while required human merge/integration exits remain pending. It does not begin real-data ingestion or model development.

Transition verification passed: 95 local links, 11 heading anchors, historical archive/review preservation and all 59 reference fingerprints checked. Full outcomes are recorded in TRANSITION.md.

## Active B01 record

See [bootstrap/publication packet](BOOTSTRAP.md), [explicit seed allowlist](PUBLIC_SEED.txt), and [verification budget ledger](VERIFICATION.md). Exact startup history is preserved in ignored `.local/phase-0b-startup/`; public historical receipts are explicitly portable adaptations. Proposed local LICENSE begins `Copyright (c) 2026 UT-Battelle, LLC.` The maintainer confirmed that exact notice, that no additional notice is required, and release readiness. No GitHub issues/PRs, independent Phase 0B reviews, human merge decisions or scientific results exist yet.
