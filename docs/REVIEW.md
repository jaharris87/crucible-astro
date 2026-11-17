# Phase 0A independent review and completion evidence

Portable historical receipt: only local-inventory links have been replaced with filenames. Exact original and inventories remain in `.local/phase-0b-startup/docs/`; see [preservation record](BOOTSTRAP.md#local-provenance-preservation). No Phase 0B candidate inherits this review.

Date: 2026-11-17. This record preserves review evidence; it does not claim scientific qualification of datasets or models.

## Invocation and candidate

- **RV-0A-01:** fresh-context, read-only Astra High (`gpt-6-astra`, reasoning `high`), specialist `independent_design_review`. Reviewer did not author or investigate for this package previously.
- Context: original assignment requirements, maintainer's implicit-method clarification, all design documents, selected source inventory and original reference files. No favorable implementation narrative or prior review conclusions supplied.
- Candidate: local documentation identity `e083e9fe50bf282069b946a012913e02a62982cc2cf81d644db469496ae9e84d`, recorded in initial inventory (`REVIEW_SNAPSHOT.json`, local only). No PR/SHA exists because this assignment prohibits Git/GitHub changes; this is the expressly scoped Phase 0A review exception.
- Scope: requirements, scientific/source support, architecture/simplicity, provenance, workflow consistency and acceptance. One thorough targeted pass; no executable science or data qualification.
- Result: one low-severity factual correction; otherwise PASS within scope. No blocking architecture, workflow, scientific-scope or acceptance gap established.

## Preserved original finding R-001

**Title:** Identify `edot` as a rate, not an increment.

**Severity/confidence:** Low / high. **Candidate:** RV-0A-01 identity above. **Original location:** `docs/EVIDENCE.md:54`, N5.

**Original statement:** “Current `edot` is a step mass-energy change.”

**Evidence:** Q `nuclear_kinetics/source_postp/xnet_evolve.f90:142–145` assigns `edot(izb) = -(enm(izb)-enold(izb)) / tdel(izb)`.

**Consequence:** The inventory misidentifies the dimensional quantity, potentially confusing an energy increment with an internal-step average energy rate when defining future labels.

**Smallest fix:** Say “signed internal-step average nuclear mass-energy rate,” optionally retain the exact formula. Preserve unresolved units, energy-loss conventions and actual run provenance.

**Verification requested:** Compare corrected text directly with the cited assignment and ensure related design/validation wording remains consistent.

**Disposition — agree and fix:** corrected EVIDENCE N5 and VALIDATION step 6 to identify the signed internal-step average rate and exact expression. Unknown physical units/loss conventions and generating-run identity remain open. Lead verified the source assignment. Focused independent verification passed below; no scientific implementation or data change was needed.

## Reviewer checks and limitations

Reviewer reported reading all candidate Markdown and inventories; matching the 11 candidate file hashes and selected source hashes/sizes; independently tracing BE evaluation/correction/acceptance, initial output, energy calculation, ordinary/NSE output and finite-step patcher; checking chemical PCA/projection/vector source; reading final proposal pp. 4–6 and summary p. 1; checking the chemistry, Hix–Meyer, QSE and tracer passages including selected rendered equations; and verifying XNet/fTimer PR-state behavior directly.

No binary/HDF records decoded, reference solver/training executed, environments installed or files modified by reviewer. Inspection was targeted, not exhaustive. Review does not certify scientific data, model performance or current remote configuration. The original missing review-record link and in-progress handoff were closeout items, not suppressed findings.

## Replacement review and final freshness

RV-0A-02 is a focused read-only follow-up by the same independent reviewer, against the corrected scientific/design core in final core inventory (`FINAL_SNAPSHOT.json`, local only). It checks R-001, related wording, and the added W4 CI/template evidence with eight additional source fingerprints. This is verification of a repair, not a second favorable review counted as independent coverage. HANDOFF and this review receipt are excluded from the core inventory because they record the review outcome; their final changes require lead consistency/link checks, not recursive review of the receipt itself.

Status: **RV-0A-02 PASS; R-001 resolved.** Reviewer verified final core identity `e28dda4d0525d8d758b9c14c8d14d10b138ae87b6450fcf4e83becb80b74552a`, all 10 core hashes and all 59 source fingerprints. Corrected rate wording matches the producer assignment; W4 is source-supported. No new material risk or consequential finding established. Only EVIDENCE, VALIDATION and SOURCE_SNAPSHOT changed within the core; other core documents retain their originally reviewed content. No new scientific or architectural choices were made during closeout.

## Original-requirement coverage

| Requirement group | Delivered evidence |
| --- | --- |
| Charter, enduring scope, Phase 0A authority | README; DECISIONS R-001–R-004 |
| Chemical/nuclear/proposal/workflow investigation and precise citations | EVIDENCE C/N/P/W entries; SOURCE_SNAPSHOT; source/PDF verification above |
| Unresolved scientific choices; one vector source; identity support | DESIGN; DECISIONS D-002–D-007; VALIDATION |
| Every phase: deliverables/non-goals/dependencies/evidence/human/milestones | ROADMAP, distinct from funding phases |
| Concrete repository/data/interface proposal, provenance/storage | DESIGN; BACKLOG B02/S01–S03 |
| Issue-to-human-merge cycle, isolation, exact-candidate review, budgets/stop | WORKFLOW; AGENT_BRIEFS; BACKLOG B04 |
| Proposed instructions and reusable risk-specific briefs | AGENT_BRIEFS, intentionally not activated as root AGENTS |
| Initial backlog and full-cycle bootstrap demonstration | BACKLOG B01–B04 and dependency-linked S01–S07 |
| Separate software/numerical/scientific/provenance/performance checks | VALIDATION; physical/energy/rollout and failure criteria |
| Development/science views, meeting reports and external audits | WORKFLOW; no claimed Claude/Gemini audit or configured service |
| Decision classifications, recommendations and presentation convention | DECISIONS; WORKFLOW; no silence-as-approval |
| Persistent goal, bounded delegation and durable stop/handoff | Native goal; HANDOFF; this independently reviewed completion record |

Final lead closeout: verified replacement PASS and disposition, actual files against every row above, maintainer packet and Phase 0B handoff; checked 63 local links and 10 heading anchors with no errors, balanced code fences, all 10 core and 59 source hashes with no mismatch. Workspace contains only Markdown and documentation JSON inventories; no `.git`, active root `AGENTS.md`, or implementation files. No reference writes, Git/GitHub changes, environment installation, training, dataset generation or HPC actions were performed. All Phase 0A completion criteria are satisfied; pending future implementation decisions do not prevent completing this design package. Final review/handoff status edits are evidence-only receipts checked by the lead; the independently verified core identity is unchanged.
