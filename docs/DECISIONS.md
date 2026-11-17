# Decision register and maintainer packet

Prepared 2026-11-17; maintainer-directed transition updates on the same date are recorded below. Original Phase 0A review and inventories remain historical; see [transition record](TRANSITION.md). Status vocabulary: **accepted requirement** (user instruction); **verified fact** (bounded source evidence); **recommendation** (proposed, not adopted); **assumption** (temporary working premise); **open question** (requires evidence/judgment). Future choices do not block finishing this design package. No unanswered recommendation is approval.

## Established direction and evidence

| ID / class | Statement | Basis / consequence |
| --- | --- | --- |
| R-001 accepted requirement | Phase 0A is local documentation and read-only investigation only; stop after reviewed design package | Original assignment; future workflow may include Git/GitHub, implementation and computation when authorized |
| R-002 accepted requirement | Durable reaction-network research framework beyond funding; multiple approaches and identity/full-state support | Charter; no mandatory AE, PCA, latent dimension or chemical heads |
| R-003 accepted requirement | One potentially vector-valued physical source task; reconstruction is not another source | Original assignment; energy treatment still needs a physical contract |
| R-004 accepted requirement | Human scientific/merge authority; exact-candidate fresh review; reproducible evidence | Workflow and validation; former explicit resource-budget requirement superseded by D-013; D-014 adds only the future narrow documentation exception; no scientific approval from CI |
| F-001 verified fact | Final proposal explicitly compares a small multi-method set with abundance/energy/cost, NS1–NS3 and a callable prototype | P1; NS1 includes CCSN+NSM, NS3 r-process; hundred-fold objective is narrowly scoped, not achieved |
| F-002 verified fact | Chemical implementation separates representation/readouts from vector source regression; full-data scaling and row identity hazards exist | C1–C3; transfer mathematics and responsibilities, not software wholesale |
| F-003 verified fact | Current producer stores trial/Newton-iterate derivative, output composition can be corrected afterward; NSE derivative zeros are placeholders | N1–N3; implicit end-time iteration issue, not proof of explicit stepping or a solver defect; run association still open |
| F-004 verified fact | Current source tree is locally modified; matching executable copies do not establish complete generating provenance | N4; recover or regenerate in a separately authorized future task |
| F-005 verified fact | XNet uses draft review candidates; fTimer trigger/coverage skips drafts | W1/W2; choose one lifecycle compatible with actual mechanism |
| R-006 accepted policy | Draft PR + explicit fresh reviewer, then ready for human review; simple `main`; minimal CI/templates; B01–B04 scope adopted | D-010 / WORKFLOW; no copied mirror branches or full bot system |
| REC-002 recommendation | Small Python path, standard JSON fixtures first; extract interfaces as real implementations need them | DESIGN/B02; no framework/library lock-in before experiments |
| R-005 accepted direction | Initial emphasis on CCSN particle trajectories as the training set; retain later NSM/r-process coverage | D-002; specific data/closure qualification remains open, and CCSN-only evidence cannot complete NS3 |
| A-001 assumption | Existing local assets may support an initial bounded data audit | They are not yet qualified training inputs; S01 may reveal missing provenance/coverage |
| A-002 assumption | A CPU-capable baseline and small fixture checks can establish the first pipeline | Tooling and task scope verified before running; former resource-cap requirement removed by D-013; no performance promise |

## Maintainer decisions addressed during transition

These are planning choices, not authorization to execute Phase 0B. Owner/visibility and D-002/D-003 were answered directly by the maintainer; do not ask them again without materially new evidence. Remaining bootstrap choices are asked interactively, no more than three together.

### Decision D-001: Bootstrap repository publication posture

**Status:** owner, visibility and BSD-3-Clause license direction accepted, 2026-11-17, including interactive license selection. Intended repository: **`jaharris87/crucible-astro`, public**. The earlier private-bootstrap recommendation is superseded; do not silently create a private repository instead.

**Maintainer response:** “Keep it public. BSD-3 is probably fine.” Proposed copyright holder: **UT-Battelle, LLC**, based on employment; that wording is tentative, not independently established ownership. GitHub account ownership and copyright ownership are separate.

**Accepted license posture:** BSD-3-Clause for permissive research reuse; maintainer selected the recommended option interactively. Apache-2.0 is a meaningful alternative if an explicit contributor patent grant is desired. See [licensing evidence and publication prerequisite](TRANSITION.md#licensing-evidence). Do not copy ORNL's example copyright line, which names another laboratory's operator. Confirm the correct holder/year/institutional notices and applicable release status before public publication; no LICENSE is created in this transition.

**Impact:** B01 uses the accepted account/visibility and chosen license posture. Publication readiness was confirmed during the authorized Phase 0B launch; see the dated confirmation below. The launch supplies bounded Git/GitHub authority.

**Publication confirmation:** 2026-11-17: Maintainer explicitly answered “Confirm all three; proceed with public publication” to the prepared D-001 checkpoint: `Copyright (c) 2026 UT-Battelle, LLC.`, no additional government-rights/institutional notice required, and portable documentation plus original Phase 0B bootstrap code cleared for public release. This supersedes the pending publication status above; reference code/data/PDFs remain excluded.

### Decision D-002: First scientific benchmark emphasis

**Status:** accepted direction, 2026-11-17. **Initial training-set emphasis: CCSN particle trajectories**, following the recommended CCSN pilot before extending to NSM/r-process coverage.

**Maintainer response:** “going with your recommendation, initial emphasis will be on CCSN particle trajectories as the training set.”

**Impact:** S01–S06 prioritize auditing suitable CCSN assets. This does not certify the existing run, define its benchmark partitions, or settle units/conditioning/thermal closure (D-004). A prescribed-history pilot remains the working plan pending that contract. NS1's combined coverage and NS3's r-process scope remain unchanged. No data ingestion, generation or training authorized here.

### Decision D-003: First baseline target strategy

**Status:** accepted sequence, 2026-11-17. **Explore both instantaneous RHS and finite-step targets; start with A, the qualified instantaneous-RHS path.** The selected A includes the identity/full-state baseline proposed in the packet; compression/model families remain separate research choices.

**Maintainer response:** “both will be explored, but start with (A) since this is what was done for the chemical kinetics.”

**Interpretation:** chemical work supplies precedent for an RHS target, not proof of nuclear label semantics or a requirement to copy its reduced architecture. Qualify/recompute labels only under a later authorized task. If labels cannot be qualified, return with evidence instead of silently switching to finite-step targets. Keep finite-step exploration as a later separately defined interval/history contract; it is not discarded.

**Impact:** S01 audit priorities and S04 initial baseline; D-004–D-007 remain open. D-002/D-003 and all later scientific choices are **not prerequisites for B04's synthetic bootstrap demonstration**.

## Bootstrap adoption decisions presented interactively

### Decision D-010: Workflow and B01–B04 scope

**Status:** accepted, 2026-11-17; maintainer selected “Adopt B01–B04 and workflow.” This is policy/scope adoption only, not execution authority.

**Question presented:** adopt the prepared bootstrap scope and workflow, or revise them?

**Recommendation / A:** adopt B01–B04, simple `main`, minimal package/CI, draft PRs with explicitly dispatched fresh-context exact-commit reviewers, preserved findings/dispositions, human merge decisions, and synthetic species-order validator through merged-result checks.

**B:** revise before adoption; maintainer supplies changes in free text. No manufactured alternate process is needed.

**Why / impact:** accepted ongoing policy and root agent guidance must reflect the maintainer's choice; adopting scope does not execute it. Evidence: [WORKFLOW](WORKFLOW.md), [B01–B04](BACKLOG.md).

### Decision D-011: Bootstrap verification budget

**Status:** historically accepted, 2026-11-17; maintainer selected “Adopt these caps,” including stop/report before exceeding and conservative local/CI accounting. **Resource caps, reservations and command accounting are superseded by D-013 below.** The initial-plus-focused review allowance remains process policy. Original terms follow as history.

**Question presented:** adopt the clarified phase-wide caps, or revise them?

**Recommendation / A:** 2 CPU-hours across B01–B04 verification, 10 minutes per CI job, 1 GiB per test process, 100 MiB generated test scratch excluding dependency environments/caches; no GPU, training, bulk-data downloads or HPC. One initial review plus focused repair verification; escalate unresolved blockers. Record local and CI usage conservatively and stop before exceeding caps.

**B:** revise limits or accounting scope in free text.

**Why / impact:** original B04 proposal limited its verification; the proposed extension makes the complete bootstrap bounded while clarifying memory/scratch scope. Approval adopts these limits, not permission to execute Phase 0B. Evidence: [B04](BACKLOG.md#b04--demonstrate-the-complete-cycle-with-fixture-manifest-species-order-validation), [WORKFLOW](WORKFLOW.md#review-record-and-practical-completion).

### Decision D-012: Model selection and exceptional escalation

**Status:** accepted by maintainer `jaharris87` on 2026-11-17, effective **after
Phase 0B**. [Accepted scope recorded in B03](https://github.com/jaharris87/crucible-astro/issues/3#issuecomment-6959269014).
The current Phase 0B orchestrator/agents and executed assignments continue unchanged.

**Decision:** adopt the eight-point canonical [model selection and escalation
policy](WORKFLOW.md#model-selection-and-escalation): `gpt-6.1-sol` High is the
advanced default, including science and independent review; `gpt-6-luna` High
serves narrow mechanical work. Sol must be pinned explicitly, with alternatives
reported before any unavailable-model substitution. Astra requires a substantial
expected benefit, a pre-escalation question/insufficiency/deliverable/scope/effort/
stop record, and lead verification/integration plus outcome/uncertainty. It is
neither routine reviewer nor automatic final check. Focused Sol or increased
effort is considered when useful without mandatory wasteful retries. Justified
escalation within existing authority needs no per-choice approval and grants no
larger scope/budget or altered human authority.

**Supersedes:** the active WORKFLOW assignment of difficult scientific/design
synthesis and independent critique routinely to Astra High, for work after Phase
0B. Historical Phase 0A Astra assignments/reviews, executed PHASE_0B_LAUNCH and
archives remain accurate and unchanged. Future prompts reference current policy.

**Implementation/acceptance:** canonical WORKFLOW, concise automatically loaded
AGENTS guidance, explicit model/effort/escalation/outcome brief fields and HANDOFF
visibility are included in B03. Fresh `gpt-6.1-sol` High review of the exact pushed
B03 candidate, dispositions, human merge and integration remain required. No
global settings/tooling changes or Phase 1 authority. Phase 0B closeout must list
these files, canonical policy, review/merge status and availability limitations.

### Decision D-013: Remove compute and resource limits

**Status:** accepted by maintainer `jaharris87` on 2026-11-17, effective immediately.
The exact answer was **“Remove all compute/resource limits.”** The
[decision receipt](https://github.com/jaharris87/crucible-astro/issues/8#issuecomment-6960426760)
records the choice, which is broader than the presented accounting simplification.

**Decision / supersedes:** remove aggregate CPU/resource caps, reservations,
per-command accounting, repository job-time, memory/scratch and proposed fixture
storage caps. D-011's resource/accounting provisions and conflicting active
workflow/validation guidance are superseded. Historical ledger bodies, executed
launch, reviews and evidence remain unchanged; they do not govern new runs.
Scientific hardware/runtime/cost evidence and functional parser/schema bounds
remain meaningful evidence and validation, not resource-allocation caps.

**Authority / implementation:** no new task, scientific phase or purchase authority;
human merge and the review-round allowance remain. [Issue #8](https://github.com/jaharris87/crucible-astro/issues/8)
implements active documentation, templates and CI consistently through its own
full independent review, human merge and integration checks. No replacement
resource limits or ledger are introduced. See [WORKFLOW](WORKFLOW.md#resources-and-authority).

### Decision D-014: Narrow documentation lane after Phase 0B

**Status:** accepted by maintainer `jaharris87` on 2026-11-17, effective **after
Phase 0B**. Exact answer: **“Adopt narrow light lane after Phase 0B (Recommended).”**
See the [decision receipt](https://github.com/jaharris87/crucible-astro/issues/8#issuecomment-6960426760).

**Decision:** typo/link/status/non-policy wording changes may use CI and an explicit
human merge without mandatory agent review. Code, policy, scientific claims and
this closeout retain full independent review. Mixed or uncertain changes use the
full lane. Eligibility, candidate identity, CI and human merge remain recorded;
required checks/protections and applicable merged-result verification remain.
Canonical scope: [narrow documentation lane](WORKFLOW.md#narrow-documentation-lane).

### Decision D-015: Canonical model policy with concise AGENTS guidance

**Status:** accepted by maintainer `jaharris87` on 2026-11-17. Exact answer:
**“Keep canonical WORKFLOW plus concise AGENTS summary (Recommended).”** See the
[decision receipt](https://github.com/jaharris87/crucible-astro/issues/8#issuecomment-6960426760).

**Decision:** retain all eight points of [D-012's canonical policy](WORKFLOW.md#model-selection-and-escalation),
with concise explicit Sol High selection/substitution guidance and routing in
AGENTS. Always record model/effort; supply escalation details when escalating
instead of repeated empty fields. Availability and substitution records remain
required. D-013 supersedes resource caps only; D-012's scope, escalation,
independence and human-authority safeguards remain. No global setting/tool change
or new phase is authorized.

## Decisions prepared but not yet ripe for a request

| ID / status | Question and recommendation | Evidence needed / gate / owner |
| --- | --- | --- |
| D-004 open scientific contract | Which abundance convention, ordering, units, conditioning and thermal closure? Recommend preserve verified physical source convention at ingestion with explicit conversions; begin prescribed histories if D-002 supports it. Do not prescribe T/rho/Ye-only inputs if neutrino effects matter. | S01 producer/reference audit and inference-availability analysis; before S03; scientific maintainer |
| D-005 open energy/constraints | Nuclear release, deposited heating and/or integrated energy? Recover consistent energy from physical dynamics where valid; compare a learned readout only as a controlled alternative. Select baryon/charge/positivity constraints for actual reactions; weak reactions rule out automatic fixed Ye. | Mass/rate/weak/EOS and energy producer semantics, reference agreement; before S03 scientific thresholds; scientific maintainer |
| D-006 open method comparison | Which initial reduction and second family? Recommend fixed linear/PCA diagnostic after identity; select nonlinear latent, operator inference or valid physics grouping from measured closure/coverage evidence. | Phase 2 results, equilibrium applicability, tuning budget; before S05/S06; scientific maintainer |
| D-007 open qualification/resources | Which authoritative reference, independent groups, tolerances, cost baseline, storage custodian and execution-resource evidence? Recommend solver-refinement plus analytic controls; define observable-specific thresholds before locked test use. | Data audit, pilot resource estimate and application needs; before qualification/expensive run; maintainer and resource owner |
| D-008 open proposal scope | How does collaboration interpret broad embedded-simulation language versus nuclear-specific production coupling in Phase II? Recommend callable stand-alone prototype now; separate production-coupling project later. | Final narrative pp. 4–5 and summary p. 1, collaborator confirmation before integration commitment; scientific/project lead |
| D-009 deferred active learning | Should adaptive reference generation become a later CRUCIBLE extension? Recommend separate scoped proposal only after benchmark and uncertainty/selection validation work. | Locked benchmark, nonadaptive baseline, domain/cost/stopping/human gates; future owner |

## Answer/change log

- 2026-11-17, audit closeout: maintainer accepted D-013/D-014/D-015 as recorded above and in issue #8. D-013 applies now; D-014 starts after Phase 0B; D-015 retains the canonical D-012 policy. Original log entries below remain in their original order.

- 2026-11-17: Maintainer accepted D-012 through the linked B03 scope addition, effective after Phase 0B; current agents continue unchanged. Canonical policy replaces future routine Astra assignments without rewriting historical execution.

- 2026-11-17: Maintainer explicitly answered “Confirm all three; proceed with public publication” to the prepared D-001 checkpoint: `Copyright (c) 2026 UT-Battelle, LLC.`, no additional government-rights/institutional notice required, and portable documentation plus original Phase 0B bootstrap code cleared for public release.

- 2026-11-17, Phase 0B launch: maintainer explicitly invoked B01–B04, including reporting acceptance, bounded seed exception, publication prerequisite and concrete human merge checkpoints. Native persistent goal created and active. Earlier statements that execution authority was absent describe their historical tasks. D-001 notice/release confirmation is still pending. **Historical checkpoint: the pending confirmation was subsequently supplied by the D-001 confirmation entry above.**
- 2026-11-17, agent selection: maintainer requires explicit `gpt-6.1-sol` with high reasoning for Sol subagents; no GPT-5.6 Sol or silent substitution. If unavailable, report alternatives before substituting.

- 2026-11-17, B03 refinement: maintainer added a lightweight phase/issue/milestone progress view (dependencies, status, linked PRs), reusable meeting-report template and initial bootstrap status report, both linked from README and handoff. Scientific results remain explicitly “not yet evaluated” until supported by experiments. This extends D-010 reporting deliverables without changing D-011 budgets or authorizing Phase 0B execution. **Historical policy-adoption checkpoint: execution was separately authorized at launch; D-013 later removed resource caps/accounting.**

- 2026-11-17, Phase 0A closeout: no future implementation choice had yet been approved. This historical status is superseded by the maintainer-directed transition entries above; implementation authority is still absent. **Historical checkpoint only: the subsequent Phase 0B launch supplied bounded implementation authority.**
- 2026-11-17: Maintainer clarified that an implicit method evaluates the new-time RHS. Lead agrees: N1 concerns successive Newton iterates at the same new time, not explicit old-state evaluation. Accepted clarification incorporated in design/evidence/validation; relevance of residual label mismatch remains to be quantified against solver and learning tolerances.

- 2026-11-17, transition: owner `jaharris87`, public visibility, CCSN-first emphasis, and RHS-first with later finite-step exploration accepted from the maintainer. Interactive answers then adopted BSD-3-Clause, the B01–B04 workflow/scope (D-010), and the phase-wide verification caps (D-011). No Phase 0B execution authorized. **Historical adoption checkpoint: superseded for execution authority by the Phase 0B launch; D-013 later removed resource caps/accounting.**

When an answer arrives, record exact choice/free-text qualification, date/owner, evidence, affected issues/documents and superseded decision. Silence, elapsed time and a preselected interactive option are not approval. Reopen only with materially new evidence.
