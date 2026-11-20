# Phase 2C external-audit assessment — 2026-11-20

Assessment under [issue #43](https://github.com/jaharris87/crucible-astro/issues/43),
after the original implementation merged at
`505d5562040ec7733ec7903c7123f86921653186` through PR #48.
[Maintainer assessment/repair authority](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047204328)
does not accept auditor proposals wholesale. D-034 covers sufficiently vetted
repair merges; **final 2C closeout remains reserved**. This report supplements the
[original 2C evidence](2026-11-20-phase2c.md), not a replacement qualification or
new numerical protocol. Current lifecycle status belongs in [handoff](../HANDOFF.md).

## Evidence boundary and preservation

All three isolated checkouts were inspected: actual HEAD `505d556`, with only
uncommitted proposals. Original reports, full diffs, changed-file snapshots,
selected diagnostic scripts/logs and hash inventories are preserved unchanged in
the ignored local 2C execution record. Original checkouts remain untouched. The
public record identifies originals without publishing private paths or arrays.

| Auditor / report SHA256 | Actual proposal | Checks evidenced; limits |
| --- | --- | --- |
| Claude Opus 5.5 — `c56a22dda71ba91de8ab6d847232f6cee534f3567ac43eb09a1f4e1c538c8d47` | Four files, +83/−1: loader refusal, tests, loading guide, nonlinear fixture | Reported original 610 passed/one expected editable skip; proposed 611/one skip. Retained synthetic/frozen checks and independent headline calculations support its reproduction claims. macOS editable only; no noneditable install, CI/Linux, full exact rescoring, fitting, final-test evaluation or MLP rollout. |
| Gemini — `9f3e43a30e2285a467f99fe98348774b1d83f0e47368e2d1c357a353e51d51c9` | Eight files, +118/−22: loader, callable, wrapper, metric and tests | Static inspection and Ruff only. Python/pytest were unavailable in its sandbox. Describing proposed tests as regression-tested does not establish execution; one alleged metric defect is false in the pinned environment. |
| Codex — `bb3b1340a8d4c939f02df8285132a2baac87ce643a01c8d9afebb9ca388f8697` | Three files, +46/−2: wrapper, partition hashing, wrapper tests; scoring remedy not implemented | Reported installed suite 611 original/614 proposed, Ruff/docs and synthetic/frozen verification; retained logs/scripts corroborate bounded checks. No fitting, real rollout, producer calls or final-test model evaluation. |

Scope was the integrated loader → preprocessing/model/persistence → scoring →
callable → numerical wrapper/diagnostics path and its guidance. None supplies
scientific acceptance, final closeout, or authority for 2D. Agreement is
corroboration only. Earlier ordinary review and the scheduled merged audit passed
within their recorded boundaries; new reproductions below are counterevidence to
completeness, not grounds to rewrite those reports.

The lead and two bounded fresh-context Sol High assessors investigated distinct
failure and integrity questions. A separate worker implemented only the scoring
adapter/tests in an isolated checkout. None may independently review its own
repair. Focused exact-candidate review remains a separate integration gate.

## Demonstrated defects and accepted bounded corrections

| Attribution | Disposition and evidence | Correction / exit significance |
| --- | --- | --- |
| Codex F1: initial terminal event | **Accept.** Actual Radau returns `t=[t0,t0]`, repeated initial state and a root at `t0`; the old wrapper called this malformed history. | Permit only that matching initial-root case, retain raw history and initial requested output, classify intentional terminal stop. Other duplicate histories still refuse. Failure-accounting defect must be repaired before closeout. |
| Gemini D2: first-step failure | **Accept defect; improve proposal.** Actual SciPy 1.18.1, `t0=1e12`, `y'=-1e6 y`, `y0=1`, horizon `t0+1`, `rtol=1e-6`, `atol=1e-9` returns status −1 and a **non-None zero-segment** OdeSolution. Calling it raises IndexError. A `sol is None` fix alone misses this. | Preserve the known initial state without interpolation when no interval was accepted; retain failure status/message/counters and incomplete horizon. Test the real solver and missing/unusable interpolant controls. Required failure-accounting repair. |
| Codex F2: substituted predictions accepted by scorer adapter | **Accept.** At the audited revision, a synthetic recorded zero-prediction run scored 0/2; substituting exact targets under the same IDs scored 2/2 despite the recorded digest. Missing or incomplete `result.json` also passed. | Before sample construction, bind the prediction byte snapshot to the completed result, model/manifest identities, contract, selected nonempty role count/order and target bytes; record identities in receipt. Zero comparator stays independent. This is provenance correctness, not changed D-024/D-026 arithmetic. Required repair. |
| Claude F1: missing local scoring-config locator | **Accept operational failure.** An external historical checkout was removed after original merged checks. Digest override to identical committed config restores the exact frozen data contract. No evidence of changed qualified data or false historical checks. | Preserve original access/overlay; repair current private resolver. Missing-file error names file/digest and recovery mechanism; document digest relocation. Reproduction must work again before closeout. |
| Gemini D5: overlay override with relative children | **Accept.** Relocated overlay bytes passed identity, but relative child paths still used the old directory; direct new-path configuration succeeds. | Resolve relative children beside the effective, digest-overridden overlay path. Test whole-bundle relocation with identical returned arrays/metadata. No trust-root change. |
| Gemini D3: scalar and exception boundaries | **Accept.** Booleans were accepted as numerical tolerances/event values; malformed callback/event times/states could escape their intended diagnostic guard. | Reject bool scalars; validate finite real times and event values inside the appropriate callback guard. Keep separate RHS/event/solver failure categories. Narrow API/diagnostic correction. |
| Gemini D4: CPU and condition shape refusals | **Accept.** Non-CPU conversion occurred before CPU refusal; a 0D condition ndarray raised TypeError via `len`. These already failed closed. | Check CPU before NumPy extraction and condition array dimension before length. Public synthetic meta-device and shape controls; no accelerator requirement. Error quality, not new capability. |
| Codex F3: repeated species hashing | **Accept small simplification.** Same ordered-species digest recomputed 30,472 times per validation; hoisting once preserves returned result and corrupted-row refusal. Assessor local timing 2.23→0.269 s for that validation only. | Hoist one invariant digest, retaining every comparison. No global cache/new loader API or end-to-end speedup claim. |
| Claude F8 / Gemini P4 / Codex status cleanup | **Accept.** Current guidance at `505d556` still described PR #48 as pending. | Refresh handoff/progress, shorten transient README status and add 2B/2C scientist routes. Preserve dated reports as history; update living model card separately. No documentation redesign. |

Original frozen result/model/prediction file hashes agree with the recorded run;
the scoring guard defect does **not** demonstrate corruption of the published 2B
metrics. Original negative fidelity and counted scaling underflows stand.

## Rejected claims and bounded deferrals

| Attribution | Disposition, rationale and trigger |
| --- | --- |
| Gemini D1: negative singleton L2 norm | **Reject alleged defect.** Pinned NumPy 2.5.5 `np.hypot.identity == 0`; the actual `np.hypot.reduce([[-2],[-5]], axis=1)` gives `[2,5]` and maximum 5. Explicit `initial=None` gives the alleged behavior, but the implementation does not use it. Add a regression, preserve metric source/arithmetic. |
| Claude F4: nonlinear stiff fixture | **Accept coverage observation; defer expansion.** Positive accepted fixtures are linear; the wrapper supplies no Jacobian and delegates numerical approximation to Radau through the same checked RHS. Independent assessment ran the proposed nonlinear fixture successfully (Jacobian evaluations 16/19/22), finding no defect. Useful targeted coverage when nonlinear learned/reference integration or a Jacobian interface is authorized; not an additional accepted 2C campaign requirement. No formal nuclear/Jacobian qualification follows from it. |
| Claude F5 / D3: compatibility vs provenance | **Defer policy change.** Full frozen contract equality is deliberate accepted behavior and the recovered current contract matches exactly. Loosening it is not needed for these repairs. Before a future loader/scorer metadata change, propose an explicit semantic compatibility rule retaining original provenance rather than editing the frozen manifest. |
| Claude F6 / D4 and Gemini P1: summary scorer / report cost | **Accept cost; defer implementation.** Recorded full train report is about 619 s, 6.4 GB peak and 923 MB JSON. Per-component dictionaries and throwaway full JSON validation contribute. D-026 source is pinned; summary/hybrid arithmetic or changed output needs an explicit successor decision before repeated large-scale scoring/model comparisons. Auditor ≤1-ulp headline checks do not prove universal threshold equivalence. |
| Gemini P2 / Claude minor: repeated split loading | **Accept observation; defer API.** Each role revalidates the full finite artifact. The digest hoist removes demonstrated redundant work now. Consider a local multi-split validated pass only when measured use warrants it; no global cache/streaming platform. |
| Claude F7 / Gemini P3: per-callback overhead, Jacobian/vectorization | **Accept overhead; defer optimization.** Current callbacks preserve original inference/scaling checks; no learned integration occurs. Synthetic microbenchmarks do not require an unused autograd/JVP or vectorization interface. Revisit under an accepted learned-dynamics/cost protocol, preserving physical-coordinate derivatives and exact or declared numerical equivalence. |
| Claude minor: weaken campaign source comparison | **Reject change now.** Exact commit/tree/source comparison protects declared reproduction. A separately identified repair regression may compare arrays across known source revisions; do not silently turn it into original-source reproduction. |
| Assessment follow-up: failed callable-check report reload | **Accept limitation; defer repair.** Optional nonfinite discrepancy metrics in a failed check are not automatically reloadable. Raw failures persist; no failed report can become PASS. Required before relying on automatic replay of such failed callable reports. Current passing evidence remains reloadable; document limitation now. |
| Gemini optional: Python patch pin | **Retain for exact 2B reproduction.** A general future inference/reproduction environment needs an explicit compatibility decision; do not edit pinned training code just to relax an incidental constraint. |
| Gemini optional: RSS field consistency | **Defer.** Existing native values carry explicit platform-dependent units; no ambiguous current measurement established. Normalize new scripts when touched for a demonstrated need. |
| Gemini optional: scaling-underflow comment | **Accept explanatory value; document in living card/assessment.** Preserve frozen `mlp_baseline.py` identity. Its round-trip allowance does not forbid underflow; the original counts 145 train/34 validation remain explicit. No extra source edit needed. |

## Scientific interpretation and later gates

**Claude F2 / Gemini S1:** accept the objective/metric mismatch and measured dynamic
range, reject the architecture-wide impossibility claim. Scaled MSE weights native
squared errors by `1/y_scale²`; D-024 measures unfloored nonzero relative errors
and exact-zero attainment. Independent validation-only diagnostics confirm
2,476/3,220 records have a nonzero scaled target below 1e-15 (median 85.5 such
components). But binary64 spacing near 1e-200 is about 1.45e-216, not spacing near
one. An unfitted same-architecture zero-weight network with output bias 1e-200
represents that value exactly and all other outputs as exact zero. This refutes a
universal representation theorem; it says nothing about the frozen model's
accuracy or learnability. A log-difference calculation avoids the auditor's
max/min overflow: species nonzero dynamic-range median about 123.6 decades.
No fitting or new model selection occurred.

**Claude F3:** accept large pointwise balance residuals; qualify the reported
normalization and rollout inference. Independently recomputed validation median
`|A·prediction|` is 6.1505e6 /s, versus label 6.6613e-16 /s. The audit's 3.4499e7
normalized figure divides predicted residual by **reference** absolute flux,
although its table suggests the prediction's own flux. With its own flux,
`|A·prediction| / (A·|prediction|)` has median 0.1190 and maximum 0.5104, respecting
the triangle bound. Median `|Z·(prediction-reference)|` is 2.7046e6 Y/s; this is a
charge-rate error, not a universal charge-conservation requirement (weak reactions
may change Ye). Multiplying a pointwise rate by saved-record spacing is a frozen-rate
Euler indicator, not an integrated trajectory or a justified physical allowance.
These observations reinforce the negative baseline's limitations without
establishing a nuclear rollout result.

**Gemini S2:** already explicit scope boundary: a two-variable toy stiffness ratio
does not verify the nuclear model, nonlinear transients or its 160-state Jacobian.
No quoted general nuclear stiffness range is adopted as a measurement of CRUCIBLE.

**Claude D1–D2 and Gemini later-policy proposals:** defer to separately accepted
2D/2E scopes. Recommend reference-first protocol design and explicit observables,
domain/horizon/failure accounting; decide then whether any bounded learned-model
diagnostic is scientifically useful. No automatic ban or permission is inferred.
Supplementary physical/floored metrics need their own thresholds/timescales and
scientific acceptance; none replaces D-024 or becomes a 2C acceptance criterion.
Scorer/compatibility proposals (Claude D3–D4) retain the triggers above. No new
2D decision is necessary to repair this implementation or close 2C eventually.

## Repair verification and integration

The repair source is `d8917c9aabee7103c5b9610feeeca25086a5fd9b` (including the
scoring repair cherry-picked as `2be2d6a`). On Python 3.12.9 / locked macOS arm64,
a forced noneditable wheel rebuild verified the committed implementation:

- Full installed suite: **651 passed, zero skips** (8.32 s); focused affected
  suite 222 passed. Ruff lint/format, whitespace and documentation/frozen-source
  checks pass. No new dependency or environment relaxation.
- Same fixed eight-attempt mathematical protocol: complete/PASS. Every one of
  80 persisted arrays is dtype/shape/byte-identical to the original `f3a12a7`
  campaign. Tight global maxima remain 4.48695e-10 (exchange) and 1.43233e-9
  (forced stiff); refinement/constraints and both expected failures pass.
  Fresh processes reload both old and repair artifacts. This is explicitly a
  cross-source repair regression, not the strict original-source comparison.
- All 17,659 train + 3,220 validation callable checks pass, zero violations;
  original saved batch and same-row predictions remain bitwise equal. Prediction
  NPZ SHA256 remains `932be7f604f10f25aedb7e85cc8657021e844c0dba3d6ff63cc84f338f1a871b`.
  Fresh reload and original-versus-repair numerical compare pass at declared
  `atol=rtol=1e-12`. The recovered full contract digest is unchanged.
- Repaired scoring guard accepts both original roles, checking current artifacts,
  selected metadata/count/order and target bits without inference or exact
  rescoring. Substitution/missing/incomplete/mismatched controls refuse in tests;
  zero comparator remains independent and verified snapshots prevent path
  replacement between verification and consumption.
- Eighteen protected source/config/report/public-artifact files are byte-identical
  to `505d556`, including `native_fidelity.py`, `mlp_baseline.py`, metric/oracle
  source, lock and original reports/results. Intake hashes of all external
  reports/proposals and their checkout HEADs still match.

Measured repair rerun costs (observations, not a speedup claim): synthetic setup
0.292 s, integration 0.194 s, persistence 0.00755 s, total 0.506 s; peak RSS
78,790,656 bytes, non-manifest artifacts 168,703 bytes. Frozen checker total
11.46 s, loading 4.01 s, setup 0.0148 s, peak RSS 1,017,774,080 bytes and
102,936,170 non-report artifact bytes. No failed numerical attempts were omitted;
the two expected negative attempts remain incomplete horizons by design.
Retained local logs include initial assessment/setup probes and formatting
corrections; no repair-suite or accepted-protocol numerical failure occurred.

Fresh focused independent review of the exact pushed candidate, protected
integration and merged-result verification remain pending. Original manifests
are unchanged; new receipts identify repaired source explicitly. No broad audit
repetition, fitting, producer execution, real MLP trajectory, final-test model
evaluation or new physical allowance. The original accepted negative 2B outcome
remains unchanged; final 2C closeout remains the maintainer's decision.
