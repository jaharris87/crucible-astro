# Backlog and phase dependencies

B01–B04 scope was adopted by the maintainer on 2026-11-17 (D-010); the maintainer separately authorized execution on 2026-11-17. B01–B04 are now [GitHub issues in the Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1); [PROGRESS](PROGRESS.md) records current dependencies, status and PR links. D-013 supersedes D-011 resource caps and accounting; the linked section below preserves the policy transition. Phase 1 S01–S03 execution was authorized on 2026-11-17 ([authority](PHASE_1_AUTHORITY.md)); [milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2) tracks its gates. Later scientific issues remain provisional. IDs remain stable when mapped to future issue numbers. All implementation follows [WORKFLOW](process/WORKFLOW.md); scientific checks follow [VALIDATION](science/VALIDATION.md). No dates are implied.

Current work: 2A is [integrated](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315); D-030 invokes only [2B #42](https://github.com/jaharris87/crucible-astro/issues/42), the selected small full-state MLP and zero-RHS comparator. The exact concrete experiment received independent review and maintainer acceptance under D-031 before fitting. [The existing sequence](PHASE_2_LAUNCH.md) owns later dependencies.

## Bootstrap sequence

`Phase 0A accepted + new authority → B01 → B02 → B03 → B04 → Phase 0B exit`

B02 and drafting B03 may overlap in isolated workspaces after B01, but the demonstration waits for working CI and review records. The first repository seed may need a maintainer-approved initialization action because no PR can precede the repository/base commit. Record that one-time bootstrap action explicitly; it does not replace B04's complete workflow.

### B01 — Establish repository identity and adopt the design

**Problem:** no project repository or accepted ongoing development setup exists.

**Scope:** after explicit Phase 0B authorization, verify workspace/state; use the accepted `jaharris87/crucible-astro` public destination; verify availability, selected license and institutional copyright/release readiness without re-asking accepted owner/visibility; initialize local/remote repository as authorized; seed reviewed documents; adopt concise root agent/contributor guidance and a simple `main` integration branch. Convert this local backlog into only the immediate issues. Record scope of one-time initialization and candidate identity.

**Non-goals:** importing chemical/XNet trees, mirroring upstream branches, public release without license/rights decision, changing global Codex settings.

**Depends:** D-001 publication readiness, D-010/D-011 adoption, and new phase authority. **Acceptance/evidence:** correct owner/remote/visibility verified; license/copyright/release readiness recorded before public publication; unresolved readiness leaves publication pending, without changing to private visibility; seed files reflect the reviewed design plus documented maintainer adoption; future workflow has no accidental Phase 0A permanent ban; no reference source copied; maintainer agrees bootstrap record. **Human point:** creation/settings/license authority. **Milestone:** enabling all, no scientific credit.

### B02 — Minimal package and repeatable development checks

**Problem:** contributors need one reproducible command path before implementing a validator.

**Scope:** choose supported Python version based on collaborator environments, `pyproject.toml`, one lock strategy, `src/crucible` package skeleton without model code; configure a small test runner and lint/static checks; document clean setup and commands. Recommend standard-library JSON for first fixture manifests, pytest for tests; no torch/scikit-learn/HDF dependencies until used.

**Non-goals:** installing every candidate ML library, generic plugins, CLI framework, multiple package managers or GPU matrix.

**Depends:** B01; routine tooling decisions recorded. **Acceptance/evidence:** clean isolated setup from declared inputs; package imports without data access/training/writes; test runner correctly reports deliberate test failure in a temporary probe and successful control; no bulk data or machine paths in package. Record exact versions/check commands. **Human point:** only if collaborator/platform constraints require a consequential support choice. **Milestone:** NS2 infrastructure.

### B03 — Minimal CI, issue/PR records and review lifecycle

**Problem:** a candidate must have durable acceptance/evidence/review records and reproducible checks.

**Scope:** one issue template, compact PR template, fast CI on push/PR including drafts; contributor workflow; available branch protections with verified check names; no ready-only agent router. Templates include issue/dependencies/non-goals, risks and authority, head/base identity, actual checks, original findings/dispositions and human handoff. Establish a lightweight issue/milestone progress view showing phases, dependencies, status and linked PRs. Maintain the [local progress view](PROGRESS.md) with actual issue/milestone/PR links once created; use existing GitHub capabilities, not a custom dashboard. Create/adopt the reusable [meeting-report template](process/MEETING_REPORT_TEMPLATE.md) and [initial bootstrap status report](reports/2026-11-17-bootstrap.md), and link both from README and handoff. The local documents are prepared in advance; B03 must reconcile them with actual bootstrap state.

**Depends:** B01/B02. **Acceptance/evidence:** a draft candidate actually triggers CI; intentional failing probe is detected before corrected passing candidate; minimum read-only workflow permissions verified; settings match real plan/access constraints; review brief and disposition record can be completed without external AI services. The progress view covers all phases and B01–B04 with explicit dependencies/status and actual PR links or “None”; the template and initial report are reachable from both README and handoff and agree with issue/PR evidence. Scientific results remain explicitly **“not yet evaluated”** until supported by linked experiment records; bootstrap/CI checks do not count as scientific results. All added workflow behavior reviewed at exact SHA. **Human point:** repository settings and merge. **Milestone:** evidence infrastructure.

### B04 — Demonstrate the complete cycle with fixture-manifest species-order validation

**Problem:** arrays with the same shape and species set can be silently misinterpreted when column order differs. Build a small useful safeguard and exercise the full workflow before science code grows.

**Contract to specify before implementation:** a tiny JSON manifest declares schema version, fixture ID, ordered species identities, named payload, payload SHA-256 and declared units/state convention. A synthetic payload independently carries ordered column identities. Validator compares **ordered sequences**, expected dimensions and checksum; it does not sort both sides or trust two copies of a hash as proof of agreement. For this issue support one simple text/JSON payload and schema only. Species are synthetic sentinels, not an asserted nuclear network.

**Test-first acceptance:**

1. A valid small fixture passes with a documented success result.
2. A same-shape permutation in the manifest (same set, different order; unchanged valid payload/checksum) fails specifically for order mismatch, naming expected/observed positions. The inconsistent fixture is intentional and isolated under negative-test fixtures.
3. Duplicate or missing identities, payload checksum mismatch and unsupported schema version each fail distinctly; no unrelated earlier failure can satisfy the ordering test. The positive fixture remains a control.
4. A temporary controlled mutation replacing ordered comparison with set comparison makes the order test fail. Preserve the observed result, then restore the actual implementation. Do not merge the mutation or leave deliberately failing CI.
5. Clean setup and the fast test suite pass on the final candidate and merged result; documentation states that validation checks schema/identity, not physical correctness or real-data qualification.

**Full-cycle evidence:** governing issue → investigation/contract → isolated implementation and recorded initial failing test → checks/self-review → committed/pushed draft PR → fresh-context independent reviewer on exact head/base → preserved findings and explicit dispositions (or PASS with limits) → pushed fixes and focused review as needed → ready PR → human review/merge decision → merged-SHA checks, issue closeout and handoff. One reviewer can cover requirements, correctness, test effectiveness and provenance. No scientific acceptance implied by the synthetic schema.

**Review/stopping:** one initial independent review plus focused repair verification per candidate issue; further broad rounds require maintainer direction. D-013 removes compute/resource caps and accounting. Stop on scope ambiguity or invalid evidence; unresolved blockers never become a pass.

**Depends:** B02/B03; no real-data semantics decision required. **Human point:** final merge. **Milestone:** useful NS1 integrity precursor and NS2 contract discipline. **Phase 0B ends only after this full cycle and the separately authorized [audit closeout #8](https://github.com/jaharris87/crucible-astro/issues/8) complete.**

## Bootstrap verification budget

D-011's original resource caps and accounting are **superseded by D-013**,
accepted 2026-11-17: “Remove all compute/resource limits.” There is no active
repository CPU/GPU, job-time, memory, scratch or fixture-storage cap, pre-run
reservation or per-command ledger requirement. [DECISIONS](DECISIONS.md#decision-d-013-remove-compute-and-resource-limits)
records the choice; [WORKFLOW](process/WORKFLOW.md#resources-and-authority) is canonical.
The unchanged [ledger body](VERIFICATION.md) and executed launch/evidence records
preserve the rules and observations that applied to their historical work.

Scope and authority remain: Phase 0B permits the minimal package, synthetic
validator and bounded audit closeout, not scientific models/training, real-data qualification, a new science
phase or purchases. Ordinary package-manager downloads are within authorized
bootstrap. Actual scientific cost and environment evidence remain necessary for
future reproducible claims; removing caps does not manufacture permission to run
new experiments.

The review allowance remains one initial independent review plus focused repair
verification per governing issue. Further broad review needs maintainer direction;
no unresolved blocker becomes a pass. D-014's narrow documentation lane starts
after Phase 0B and does not waive review for this closeout.

## Next scientific issues (draft in detail only after their prerequisites)

| ID | Problem / deliverable | Depends | Acceptance and decision gate |
| --- | --- | --- | --- |
| [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10) | Producer/run provenance and target audit for a bounded selected subset, plus living Genesis data card | B04, D-002 | Source+patch/build/run identity or explicit missing links; binary layout verified; accepted/trial/NSE/initial semantics; quantify stored-versus-fresh RHS if authorized; state/energy contract and quarantine inventory approved; data card records actual template source/revision, access/rights, raw/derived links and explicit qualification limits. No training. |
| [S02 #11](https://github.com/jaharris87/crucible-astro/issues/11) | Audited reader and fixtures | S01 accepted semantics | Independent decoded values, species/units/layout and validity tests; raw/derived checksums and linked derived data card; no guessed `edot` block or cross-format alignment; synthetic public fixtures plus local real checks while rights are unresolved; commit real records only with confirmed redistribution authority. |
| [S03 #15](https://github.com/jaharris87/crucible-astro/issues/15) | Coverage inventory and leakage-resistant benchmark partition | S01/S02, D-004/D-005/D-007 | Multi-trajectory training pool with supported coverage; accepted group/lineage disjointness and an explicit within-parent limitation when applicable; train-only preprocessing rules and meaningful split checks, with actual fit-boundary tests when that implementation exists; domain/horizon/energy/reference/metrics/tolerances signed off. NS1 coverage gaps tracked. |
| S04 | Staged identity/full-state baseline and reproducible evaluation | S03/D-025, D-003/D-028, separate experiment authority | Fail-closed named-view access before fitting; train-only preprocessing, comparator, pointwise reporting, save/reload and analytic integration checks first. Real held-out rollout/failure/cost exit remains, gated on separately accepted forcing/history and authorized pinned trajectory/convergence reference. Actual Genesis model card binds artifact/data/split/evidence/limitations; no model-size search. |
| S05 | One initial reduced dynamics method | S04, D-006 | Chain-rule/finite-step tests, reconstruction/RHS/rollout separation, matched baseline comparison, closure/constraint diagnostics and energy evidence. |
| S06 | Controlled distinct-method comparison | S05, comparison scope and method decision | At least two reduced approaches with fair tuning/data; r-process cases for NS3; all errors/failures/cost and reproduction records; human down-selection. |
| S07 | Callable multi-approach prototype and release package | S06, D-001/D-008 | At least two approach examples via stable semantic contract; retrieval/checksum/reload and invalid-input tests; supported regimes/limits, release rights, independent audit and human acceptance. |

Do not precreate a large speculative issue tree for all candidate architectures. Later issues gain numeric science tolerances and explicit experiment scope only after independent references and the task are understood. Resource use remains reported evidence, without a standing resource cap.

D-022 / [issue #29](https://github.com/jaharris87/crucible-astro/issues/29) adds
bounded configurable physical-abundance budget diagnostics and a
[current readiness report](phase1/ERROR_BUDGET_READINESS.md) to S03 preparation.
The 0.1%, 1%, 5% relative-change tiers are provisional engineering settings, not
accepted scientific tolerances or a Phase 1 exit. Final allowances, scales,
physical timescales and critical species remain open for physical uses. D-024/D-025
separately accept the named numerical reference and partitions. S04/S05 later acceptance must separately establish admissible-state and
constraint evidence, reconstruction/decoded chain-rule consistency and closure,
free-running abundance/energy/weak-Ye/equilibrium behavior, solver/Jacobian/JVP
numerical compatibility and matched-accuracy cost. See the
[validation requirements](science/VALIDATION.md#provisional-pointwise-abundance-budgets-and-later-acceptance).
No model or numerical integration implementation is authorized by this addition.


## Post-audit transition

The [independent-audit assessment](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016554530)
and accepted D-027/D-028 directions remain preserved. Phase 1 and the migration
and 2A are complete, with receipts linked from [handoff](HANDOFF.md). D-030 authorizes
**2B only** within [milestone #3](https://github.com/jaharris87/crucible-astro/milestone/3).
[The incremental execution sequence](PHASE_2_LAUNCH.md) replaces the former draft:
#41 access → #42 pointwise baseline → #43 analytic integration → #44 real references
→ #45 frozen evaluation/cost. Later issues hold short summaries until prerequisites
are understood; each requires scope acceptance and preceding integration.

2A implemented named-version/use/split access with qualification, payload,
ordered species/units, exact memberships, use and cross-role physical-input checks.
Reuse that interface and separate local path configuration. 2B verifies the actual
train-only preprocessing fit boundary by changing held-out values. The earlier
advisory loader patch remains historical and is not the adopted implementation.

Measure actual loading/scoring costs before adding caching, streaming or detail
repairs. Preserve complete D-024 counts/detail and D-026 history/group MSE weights;
never average chunk RMS values. Supplementary diagnostics must be predeclared and
must not alter headline metrics or selection criteria. D-025 memberships and the
sealed final test remain fixed. No extra split, latent architecture, plugin
hierarchy or physical error floor is authorized.

Real-rollout reference preparation must specify initial states, continuous forcing
and interpolation, intervals/output grid, supported table/domain checks, retained
weak/screening/neutrino/heating policy, solver/convergence studies and failure
handling. It needs a bounded producer-execution proposal and human acceptance;
current pointwise labels/historical saved Y are insufficient. Physical abundance
budgets, heating and application observables require their own evidence. Record
RHS and end-to-end integration cost separately at matched accuracy, including
failures and solver work, with training/setup costs explicit.

With 2A integrated, 2B must propose a coherent declared experiment and its routine
preparation/checks together, with validation-based stopping and all trials retained.
Scientific scope/reference changes, final-test release/use and every merge remain
human decisions under WORKFLOW. Use functions and small records for problem/reference,
data/benchmark, representation/RHS and integration/evaluation responsibilities;
extract shared interfaces only when actual implementations need them. Bound further
historical provenance work by its relevance to the intended use.

<a id="proposed-documentation-migration"></a>

### Documentation migration plan

**Plan accepted under D-027, 2026-11-19; execution separately authorized after
verified Phase 1 closure in [issue #39](https://github.com/jaharris87/crucible-astro/issues/39).**
The table and plan below preserve the accepted pre-move source/destination map.
The [migration record](process/DOCUMENTATION_MIGRATION.md) binds its actual
implementation source and compatibility/recovery checks. Human merge and merged
verification are complete in [the final receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012);
Phase 2A now has separate D-029 authority.
[The maintainer accepted this concrete plan](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7017529663)
for separately authorized post-Phase-1 work. Migrate maintained scientific guides and contributor
process into separate directories, while keeping historical evidence and all
five distinct dataset cards at their current paths. The demonstrated problem is
conflicting current claims and poor navigation, not the number of files.

| Current guide | Proposed maintained path |
| --- | --- |
| `docs/DESIGN.md` | `docs/science/DESIGN.md` |
| `docs/VALIDATION.md` | `docs/science/VALIDATION.md` |
| `docs/EVIDENCE.md` | `docs/science/EVIDENCE.md` |
| `docs/phase1/NATIVE_BENCHMARK.md` | `docs/science/benchmark/NATIVE_RHS.md` |
| `docs/phase1/PARTITIONS.md` | `docs/science/benchmark/PARTITIONS.md` |
| `docs/phase1/S02_READER.md` | `docs/science/data/XNET_READER.md` |
| `docs/phase1/PRIMARY_RHS_DATASET.md` | `docs/science/data/PRIMARY_RHS_DATASET.md` |
| `docs/phase1/RHS_DATASET.md` | `docs/science/data/PILOT_RHS_DATASET.md` |
| `docs/phase1/ERROR_BUDGETS.md` | `docs/science/validation/PHYSICAL_ERROR_BUDGETS.md` |
| `docs/WORKFLOW.md` | `docs/process/WORKFLOW.md` |
| `docs/AGENT_BRIEFS.md` | `docs/process/AGENT_BRIEFS.md` |
| `docs/MEETING_REPORT_TEMPLATE.md` | `docs/process/MEETING_REPORT_TEMPLATE.md` |

Keep README as the scientist entry, CONTRIBUTING as installation/checks, and
AGENTS as the agent entry. Keep DECISIONS, ROADMAP/BACKLOG, PROGRESS and HANDOFF at
existing paths: policy, scope, current status and resumption have distinct roles.
Keep PHASE1_CLOSEOUT as the Phase 1 artifact/exit index; freeze its closure evidence
once genuinely complete. Each card describes a distinct raw/quarantined/pilot/union/
qualified identity; these are not redundant drafts to delete. Current guides should
link the accepted contract and index rather than duplicate execution/status history.

Keep all other Phase 1 audit/proposal/execution/provenance/guidance snapshots,
Phase 0 records, `docs/bootstrap/`, `docs/audits/` and dated `docs/reports/` verbatim
at their existing paths. Route readers through the closeout/transition indexes.
This deliberately avoids breaking historical relative links or changing report
bytes merely to create a uniform `archive/` tree. A physical historical-file move
would need a revised explicit plan; it is not included in this recommendation.
`experiments/` keeps finite recipe documentation beside its code.

Execute later as one bounded documentation issue/PR after Phase 1 closeout and
separate authorization, not as a new closeout gate. Before moving any maintained
guide, inventory its inbound path/fragment links and any accepted artifact binding.
Keep heading text/order unchanged on the first move: every old `path#fragment`
maps to the listed new path with the **same fragment**, including duplicate-heading
suffixes. Retain short old-path compatibility pages with every original anchor
forwarding to that section; update maintained links/AGENTS routes.
Historical reports and cards stay byte-identical and can continue using old links.
Bind the migration to its actual source revision; frozen source/hash-bound versions
remain recoverable from Git and retained checkouts, never replaced by a stub in
an accepted local manifest.

Acceptance: check both old/new paths and fragments, report/card byte preservation,
unchanged mathematical/qualification/authority meanings and bound-source recovery;
run the documented synthetic example and normal CI. Obtain fresh review of the
actual path/content candidate and human merge. Do not combine the migration with
model architecture, new data schemas or rewritten scientific policy. The alternatives
considered were retaining current paths after cleanup or expanding the proposal to
relocate historical files; neither was selected. A materially different migration
needs its own explicit plan and decision.
