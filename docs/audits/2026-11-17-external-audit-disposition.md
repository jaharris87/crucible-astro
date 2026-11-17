# External-audit dispositions — 2026-11-17

[Issue #8](https://github.com/jaharris87/crucible-astro/issues/8) governs this
bounded bootstrap closeout. Claude and Gemini supplied advisory reports, not PR
approval or scientific acceptance. A fresh-context read-only `gpt-6.1-sol` High
assessment inspected both reports/patches against current source; the same worker
then authored this follow-up and is **not its independent reviewer**. Final
candidate CI, fresh review, human merge and integration belong in the live PR/issue.

## Evidence boundary and accepted choices

Both audits inspected B02 main `5d81381` and moving B03 candidate `1f4601f`.
Claude identified its model as `claude-opus-5-5`; Gemini's report did not identify
an exact model. Their reported tests are auditor evidence, not reruns by CRUCIBLE.
The assessment inspected main `6858849`, B04 `dc514bb`, both proposed diffs and
the later reference-routing documentation delta. This authoring is based on B04
merge `8835481e2b9dea15eda52fb5d9a6a41b366c091e` ([integration receipt](https://github.com/jaharris87/crucible-astro/pull/7#issuecomment-6960492520)).
B04 now has a docstring-only initializer, separate `crucible.manifest` validator,
42-test/mutation evidence and human-merged integration. No new B04 implementation
blocker was established by either audit.

The maintainer [accepted D-013–D-015](https://github.com/jaharris87/crucible-astro/issues/8#issuecomment-6960426760):
D-013 removes **all compute/resource limits**, reservations and command accounting
now; D-014 permits the narrow non-policy documentation lane **after Phase 0B**;
D-015 keeps all eight canonical model-policy points in WORKFLOW with concise
explicit AGENTS routing. These choices grant no new task, science phase or
purchase authority. This CI/policy closeout retains full independent review and
human merge. See [DECISIONS](../DECISIONS.md).

## Per-finding disposition

“Applied” means implemented in this candidate, pending its review/merge. “Defer”
identifies the trigger and intended acceptance; it does not authorize later work.
Evidence references are current [WORKFLOW](../WORKFLOW.md),
[CONTRIBUTING](../../CONTRIBUTING.md), [DESIGN](../DESIGN.md),
[VALIDATION](../VALIDATION.md), [B04 contract](../bootstrap/B04-CONTRACT.md) and
[B04 evidence](../bootstrap/B04-EVIDENCE.md), with preserved historical source in Git.

| ID / finding | Disposition, evidence and landing or follow-up |
| --- | --- |
| **A1 — duplicated current status** | **Accept/apply narrowly.** README routes to PROGRESS/HANDOFF; BOOTSTRAP is labeled historical. Live issue/PR receipts hold subsequent state. Preserve explicit AGENTS authority boundaries and dated snapshots rather than making every document a current tracker. |
| **A2 — accounting overhead** | **Accept; superseded by D-013.** Historical VERIFICATION shows conservative charges and maximum reservations. Remove active caps/reservations/micro-ledger and CI controls; preserve the ledger body. Actual scientific cost evidence remains required when making performance claims. |
| **A3 — uniform process weight** | **Accept/apply D-014.** WORKFLOW defines a future typo/link/status/non-policy-wording lane with CI and human merge. Policy, code, scientific claims and this closeout retain independent review. No retrospective review waiver. |
| **A4 — repeated rules** | **Accept targeted simplification.** Canonical WORKFLOW owns process/model detail; AGENTS, contributor guidance and templates route there. DECISIONS records choices; historical receipts remain evidence. Repeated scientific “not yet evaluated” labels are useful safeguards, not a reason to erase limits on claims. |
| **A5 — model-policy location** | **Accept D-015, reject removing accepted requirements.** Keep concise explicit Sol High selection/substitution guidance in AGENTS and all eight D-012 points in WORKFLOW. Briefs always name model/effort; escalation fields appear only when needed. No tool-neutral waiver of explicit model selection. |
| **A6 — navigation/readability** | **Accept bounded subset.** Group README navigation, link one quickstart in CONTRIBUTING, retain isolated/noneditable verification and editable-skip explanation. Annotate historical DECISIONS checkpoints without reordering/erasing history. Defer wholesale history relocation or a new prose policy until an actual navigation need. |
| **A7 — import audit too strict** | **Defer future relaxation; reject B04 blocker/patch.** B04 deliberately keeps the initializer a docstring and imports validation separately. Claude's broad package/stdlib read prefixes permit more reads than the current contract. Revisit only if an eager root import is needed, with tests preserving data/write/dependency restrictions. |
| **A8 — stale reused noneditable install** | **Accept scoped caveat.** CONTRIBUTING already required a fresh checkout; B04 verified installed bytes in a fresh clone. uv 0.10.11 local CLI help confirms `--reinstall-package`; document `uv sync --locked --no-editable --reinstall-package crucible-astro` for reused environments. The auditor's stale-cache probe was not repeated or generalized to other versions. |
| **A9 — address-space/RSS mismatch** | **Resolved by D-013 removal.** CI no longer enforces either resource cap. Historical controls were accurately labeled address-space limits. GNU time reports RSS and is not an equivalent hard enforcement mechanism; no unsupported replacement or numerical-library failure claim is adopted. |
| **A10 — provenance tiers/Jacobians** | **Defer to S01/S02 and D-006/D-007 preparation.** Before real-data use, specify missing-metadata eligibility separately for state/RHS/training. Before rollout qualification, record integrator class and needed Jacobian source with cost/failure evidence. No integrator is selected; neither question blocks synthetic B04. |
| **A11 — CI cancellation** | **Defer optional change.** No observed correctness failure requires concurrency cancellation. Revisit if superseded runs cause a concrete operational problem; retain failure evidence and final-head required checks. No cancellation configuration is added. |
| **F-01 — self-referential receipts** | **Accept/apply.** Historical receipt commits did trigger another final-head check. Keep subsequent CI/review/merge outcomes in live PR/issue records; meaningful new changes still need fresh candidate evidence. D-013 removes accounting requirements rather than moving mandatory micro-ledgers elsewhere. |
| **F-02 — status synchronization** | **Accept bounded changes.** Stable README routing and snapshot/live-record separation reduce churn. Preserve B03-PREPARATION and dated reports as historical evidence rather than deleting or silently merging original records. No broad history rewrite. |
| **F-03 — collaborator onboarding** | **Accept with one command home.** CONTRIBUTING has the pinned-version quickstart, expected skip and isolated reproduction path; README links it. Duplicating commands in both documents would recreate drift. No new dependency or platform promise. |
| **F-04 — anticipated B04 imports** | **Already addressed by B04 design; reject patch.** The suggested docstring-initializer/separate-manifest option is current source. Gemini's patch allows submodule import events but still forbids their file reads. No import-regression relaxation is needed or applied. |
| **F-05 — Python/backend ranges** | **Reject patch; defer support expansion.** CONTRIBUTING declares verified Python 3.12 only; `uv.lock` requires `==3.12.*`. Widening metadata with an unchanged lock is inconsistent. Isolated build-backend pinning is separate from the runtime lock. A future support issue must update/recheck the actual supported configuration. |
| **F-06 — privileged scratch mount** | **Accept removal under D-013; reject claimed equivalence.** Remove tmpfs enforcement entirely as expressly directed. A post-run `du` would not prevent transient overuse or measure deleted files and can be skipped on test failure. It is not installed as a substitute cap; historical successful tmpfs checks remain preserved. |
| **F-07 — template/brief density** | **Accept constrained simplification.** Shorten the PR template and condition escalation fields while retaining exact head/base/tested-source binding, original findings/dispositions, repair verification, freshness, human merge and integration. Remove resource accounting under D-013; keep full review for this policy/CI change. |
| **F-08 — allegedly empty Claude worktree** | **Reject the empty-worktree premise; accept cleanup after evaluation.** It contained proposed edits and an audit report, so retain those while evaluating. The maintainer clarified both auditor checkouts were temporary scratch. After assessment and initial independent review, verify report/patch snapshots, then remove the two checkouts and Claude scratch branch. This cleanup is complete; only small ignored receipts and public dispositions remain. Keep `.claude/` ignored for future local scratch. |
| **Gemini — nullable provenance schema** | **Accept existing principle; defer schema to S01/S02.** DESIGN already permits explicit unknowns, quarantine or narrower use; VALIDATION separates state/RHS eligibility. Future acceptance must distinguish exploratory loading from training qualification. Nullability cannot qualify unknown labels; no real-data schema or science investigation belongs in this closeout. |

## Corrections and preservation

Gemini's “under 50 CPU-seconds” estimate conflicts with its own cited CI figures:
44 + 72 = 116 CPU-seconds before local work. Claude's 3,906/7,200 figure included
outstanding reservations, not only consumed CPU. These are corrections to the
historical reports, not a new accounting requirement. Both “B04 not implemented”
statements are historical. The auditors did not reinspect private scientific
sources; their praise does not freshly verify EVIDENCE's nuclear-source claims.
This assessment/authoring did not investigate those sources either.

Original reports and proposed patches remain unchanged in the maintainer's
ignored `.local/audits/` preservation, alongside their manifest/status snapshots.
They contain machine-specific context and are not published wholesale. SHA-256
identities bind the local originals:

| Preserved artifact | SHA-256 |
| --- | --- |
| Claude report | `80e97a23d65e352296eaa72d693efbcdd941ea59a1459a1cb48b947379f4d5ea` |
| Claude proposed patch | `26d11c6c1047973d6ce4038595836cdaa5803981f5c1b73c72a39a87f53d7c48` |
| Gemini report | `b5750e83cc88f131b7f7b828be9ffbdc4c0677eb8807f435cb66b64aaf539884` |
| Gemini proposed patch | `6bca0d18972732a8755a278a4efbd6f44b9258efeda96f14a283b80d3d476e1e` |

The author checked source/diff and policy consistency, preserved-history hashes,
local links/anchors, YAML structure, extracted shell syntax and ignored local
exclusions. uv CLI help was read; no software test/install was repeated because
runtime source, tests, fixtures, dependencies and lock are unchanged. Required
locked CI on the final pushed candidate remains the lead's next verification;
passing CI, independent review, human merge or Phase 0B completion are not claimed
by this author receipt. The functional B04 read-size bound remains schema
validation, not a resource-allocation policy. Scientific results remain
**not yet evaluated**.
