# Initial backlog and concrete Phase 0B handoff

B01–B04 scope was adopted by the maintainer on 2026-11-17 (D-010); the maintainer separately authorized execution on 2026-11-17. B01–B04 are now [GitHub issues in the Phase 0B milestone](https://github.com/jaharris87/crucible-astro/milestone/1); [PROGRESS](PROGRESS.md) records current dependencies, status and PR links. D-013 supersedes D-011 resource caps and accounting; the linked section below preserves the policy transition. Later scientific issues remain provisional. IDs remain stable when mapped to future issue numbers. All implementation follows [WORKFLOW](WORKFLOW.md); scientific checks follow [VALIDATION](VALIDATION.md). No dates are implied.

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

**Scope:** one issue template, compact PR template, fast CI on push/PR including drafts; contributor workflow; available branch protections with verified check names; no ready-only agent router. Templates include issue/dependencies/non-goals, risks and authority, head/base identity, actual checks, original findings/dispositions and human handoff. Establish a lightweight issue/milestone progress view showing phases, dependencies, status and linked PRs. Maintain the [local progress view](PROGRESS.md) with actual issue/milestone/PR links once created; use existing GitHub capabilities, not a custom dashboard. Create/adopt the reusable [meeting-report template](MEETING_REPORT_TEMPLATE.md) and [initial bootstrap status report](reports/2026-11-17-bootstrap.md), and link both from README and handoff. The local documents are prepared in advance; B03 must reconcile them with actual bootstrap state.

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
records the choice; [WORKFLOW](WORKFLOW.md#resources-and-authority) is canonical.
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
| S01 | Producer/run provenance and target audit for a bounded selected subset | B04, D-002 | Source+patch/build/run identity or explicit missing links; binary layout verified; accepted/trial/NSE/initial semantics; quantify stored-versus-fresh RHS if authorized; state/energy contract and quarantine inventory approved. No training. |
| S02 | Audited reader and tiny real fixture | S01 accepted semantics | Independent decoded values, species/units/layout and validity tests; raw/derived checksums; no guessed `edot` block or cross-format alignment; fixture redistribution confirmed. |
| S03 | Coverage inventory and leakage-resistant benchmark partition | S01/S02, D-004/D-005/D-007 | Parent groups disjoint; train-only transform rule tested; domain/horizon/energy/metrics/tolerance policy signed off; limited coverage labeled honestly. NS1 coverage gaps tracked. |
| S04 | Identity/full-state baseline and reproducible evaluation path | S03, D-003, authorized experiment scope | Analytic independent check, frozen train/validation/test protocol, save/reload, held-out rollouts and failure accounting, physical metrics and cost; no model-size search. |
| S05 | One initial reduced dynamics method | S04, D-006 | Chain-rule/finite-step tests, reconstruction/RHS/rollout separation, matched baseline comparison, closure/constraint diagnostics and energy evidence. |
| S06 | Controlled distinct-method comparison | S05, comparison scope and method decision | At least two reduced approaches with fair tuning/data; r-process cases for NS3; all errors/failures/cost and reproduction records; human down-selection. |
| S07 | Callable multi-approach prototype and release package | S06, D-001/D-008 | At least two approach examples via stable semantic contract; retrieval/checksum/reload and invalid-input tests; supported regimes/limits, release rights, independent audit and human acceptance. |

Do not precreate a large speculative issue tree for all candidate architectures. Later issues gain numeric science tolerances and explicit experiment scope only after independent references and the task are understood. Resource use remains reported evidence, without a standing resource cap.
