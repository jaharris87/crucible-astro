# Provisional physical-abundance error budgets

[Issue #29](https://github.com/jaharris87/crucible-astro/issues/29), D-022.
This is a bounded Phase 1 diagnostic, with **no approved scientific numerical
budget**. The requested relative-change tiers 0.1%, 1% and 5% are illustrative
engineering sensitivity settings. There is no model, training, architecture
selection, integration experiment, producer call or qualified heating target.
[Current benchmark readiness](ERROR_BUDGET_READINESS.md) records the actual gaps.

Three outcomes stay separate: synthetic oracles/checks establish bounded software
and arithmetic evidence; the report describes pointwise satisfaction of a supplied
provisional budget; integrated scientific accuracy remains `NOT_EVALUATED`.
Neither `NO_VIOLATIONS_PROVISIONAL` nor a passing test qualifies data or a model.
Human reference/observable/tolerance/benchmark acceptance is still required.

## Physical rate budget

For an individual species or explicitly linear physical abundance observable q:

```text
|qdot_prediction - qdot_reference| <= L_q
L_q = (a_q + r_q S_q) / tau_q
normalized error = |qdot_prediction - qdot_reference| / L_q
```

`a_q` is an absolute **abundance-change** allowance, `r_q` dimensionless,
`S_q` an abundance-change scale, and `tau_q > 0` an independently justified
physical timescale in seconds. A solver timestep is not `tau_q`. Changing numerical
step metadata changes none of these metrics. No numerical clipping threshold
supplies a physical floor; no held-out error or extrema may be used to choose
allowances, timescales, critical species or normalization after testing.
All these scientific choices remain unresolved for the current benchmark.

The verified native unit labels are `molar_abundance_Y` and `molar_abundance_Y/s`;
no new physical-unit interpretation is inferred. The source convention is molar Y,
with fixed ordered A and Z. In mass-fraction
space `X_i=A_i Y_i` and `Xdot_i=A_i F_i`. Group coefficients apply to the selected
physical space, never a learned latent coordinate. Every species gets its own
physical-error and budget record, even when only a group budget is supplied.
Group records link all nonzero constituents and expose unresolved individual
budgets; compensating errors cannot imply per-member success. Designated critical
or trace species retain their own normalized/physical maxima and exceedances.
A null critical selection is unresolved; an explicit empty selection needs
provenance and means the caller deliberately selected none.

`S_q` can be an explicitly supplied nonnegative bound with provenance, or
`max_j |q(t_j)-q(t_0)|` from separately qualified discrete reference samples.
An interior excursion is retained even when both endpoints agree. The latter is
only a **sampled maximum**. It supplies no continuous supremum, interpolation,
unknown-gap bridge or proof of adequate temporal sampling. The interval has its
own identity, history, qualification/coverage provenance, exact sampled endpoints
and strictly increasing times; a missing/unqualified interval is not evaluated.
The sampled interval duration must equal the configured physical `tau_q` exactly;
a mismatched duration is rejected. This avoids applying an excursion over one
horizon to a different rate horizon. The module supports only one explicitly
predeclared **fixed calibration interval per quantity**, reused across all report
samples/histories, with calibration provenance and `frozen_before_testing=true`.
It does not silently choose a sample-local window or fit held-out calibration.
Acceptance of that calibration's scope/representativeness remains the caller's
scientific responsibility. A different scale/horizon model needs its own contract.
An explicit bound is a caller's documented assertion, not a bound proved by this
software. A raw saved history is not automatically a qualified rollout reference.
Freeze the metric/reference-interval definition before test use. Metric
normalization is evaluation metadata, never model input or fitted preprocessing.
The current benchmark has no accepted scales and none are extracted to choose
budgets behind the test boundary.

A separate possible later **state or reconstruction** score uses a denominator
`a_state + r_state*|q_reference|` in abundance units. It measures state amplitude,
whereas this module compares instantaneous rates against interval change over a
physical timescale. These definitions are distinct; the state-amplitude score is
not implemented here and does not silently replace `S_q` or cancel `tau_q`.

## Small JSON interface

`crucible.error_budgets.evaluate(config, reference, prediction=None,
intervals=None)` returns ordinary JSON-compatible dictionaries. The separate
`physics_diagnostics(reference, prediction=None)` uses the same identity checks.
The command line prints a report without writing input files:

```sh
uv run python -B -m crucible.error_budgets \
  configs/error_budgets/provisional_tiers.json \
  configs/error_budgets/synthetic_reference.json
uv run python -B -m crucible.error_budgets \
  configs/error_budgets/synthetic_oracle.json \
  configs/error_budgets/synthetic_reference.json \
  --prediction configs/error_budgets/synthetic_prediction.json
```

The public examples are mathematical sentinels only. The resolved synthetic
allowances are hand-chosen oracle values, not proposed nuclear tolerances.
`synthetic_readiness_report.json` and `synthetic_diagnostic_report.json` are
reproducible outputs, not current-benchmark or surrogate outcomes.

| Record | Required fields / behavior |
| --- | --- |
| Configuration | `schema=crucible.error_budgets.v1`, `config_id`, ordered `species`, `abundance_space` Y or X, `relative_tiers`, `critical_species` and selection provenance, `species_budgets`, `groups` |
| Species | Ordered objects containing stable `id`, integer positive `A`, integer `0<=Z<=A`; stable id must distinguish any isomers. Configuration/reference/prediction lists must agree exactly; no sorting/permutation |
| Budget | `absolute_change`, `timescale_s`, `scale`. Null/missing values remain unresolved; negative/nonfinite allowance, nonpositive timescale or malformed scale is an error |
| Explicit scale | `mode=explicit`, nonnegative finite `value`, nonempty `provenance` |
| Sampled scale | `mode=sampled_max_excursion`, `interval_id`, `usage=fixed_calibration_interval`, `frozen_before_testing=true`, `calibration_provenance`; supply an interval map separately using the contract below |
| Group | Unique `id`, finite nonzero linear `coefficients` keyed by known species ids, `budget`; coefficients may be signed |
| Reference/prediction | `schema=crucible.rhs_samples.v1`, `dataset_id`, ordered species, units exactly `Y: molar_abundance_Y`, `F: molar_abundance_Y/s`, `time: s`, nonempty `samples`; prediction also has `prediction_id` |
| Sample | `sample_id`, `history_id`, `group_id`, `category`, finite nonnegative `time_s`, ordered `F`; reference also contains ordered `Y`. Carry raw digest/ordinal identities in `sample_id`, dataset manifest identity in `dataset_id` and accepted group identity in `group_id`. Match every identity/order exactly; duplicate sample ids are errors |
| Failure | Prediction row `success=false` may omit F; otherwise F has one entry per species. Null/nonfinite components count as whole-row failures for every monitored quantity. No attempted row silently disappears |
| Regime | Optional `{label, provenance}` on reference samples; label is `burning`, `near_equilibrium`, `freeze_out` or `unknown`. Absent means unknown. Labels are supplied evidence, never inferred from zero F or invented temperature thresholds |
| Qualified sampled interval | Same sample schema/species/units metadata plus `interval_id`, `history_id`, `qualified=true`, `qualification_provenance`, `coverage_provenance`, `semantics=discrete_samples_no_interpolation`, `times_s`, exact `[first,last]` `coverage_s`, and ordered finite `Y` matrix. Caller owns scientific evidence for qualification and adequacy |

The report binds the exact canonical JSON configuration SHA256, input/prediction
identities and ordered sample identities/regime provenance. Preserve the actual
input/configuration artifacts as evidence, not only a human label. The evaluator
is not a manifest verifier or scientific-qualification authority.

Each tier includes per-sample physical absolute/normalized errors, normalized RMS
and maximum, physical absolute RMS/maximum, exceedance count/fraction, and identical
summaries within history/group/category/regime strata. No time weighting or
independent-group confidence claim is implied. `attempted`, `valid`, `failed`,
`budget_evaluated`, `budget_not_evaluated` and the exceedance denominator are
explicit. `fraction_exceeding_evaluated` uses finite successful comparisons with
resolved budgets; `violations_or_failed_fraction_attempted` retains failed
attempts in its denominator. This latter fraction is descriptive, not a success
fraction: unresolved budgets also have their own visible count. The overall
status is incomplete if any species budget, critical selection or prediction is
unresolved/failed, even when a group has no violation. All per-tier results remain
visible when different tiers disagree.

A zero budget gives normalized zero only for exactly zero error; any nonzero
error is an explicit violation with `UNBOUNDED` normalization, null normalized
RMS/max and an unbounded count. No epsilon is inserted. Overflow/nonfinite
predictions or physical differences fail visibly. JSON never contains NaN or
Infinity. No prediction document means `NOT_EVALUATED`, zero prediction attempts,
the full reference population/identities retained, and no physical model errors.
An empty prediction array is malformed, not an empty successful benchmark.

Linear rate differences and sampled excursions accumulate the exact rational
values of the decoded binary64 components and configured coefficients, including
the integer A factor in X space, before rounding the final nonnegative magnitude
once to binary64. This retains small changes hidden by separately rounded totals,
products or component differences. The sampled maximum is selected before that
rounding. A final overflow or a nonzero magnitude that rounds to zero is an
explicit failed rate comparison or rejected sampled scale; a tiny nonmaximum
excursion does not invalidate a representable maximum. Budget construction,
normalized errors, exceedance comparisons and summary statistics retain their
existing binary64 arithmetic and rounding limits. This is no exact-arithmetic
guarantee for the complete budget report and selects no scientific parameters.

## Separate physics diagnostics

The supported convention is explicitly
`closed_full_inventory_no_aux_Q_over_B`, matching the currently pinned native
reference, not every XNet version. For unmodified supplied Y and F compute:

```text
B = A dot Y; Q = Z dot Y; Ye = Q/B, with finite B > 0
baryon-rate residual = A dot F
charge-moment rate = Z dot F
Ye_dot = (B*(Z dot F) - Q*(A dot F))/B^2
```

The implementation uses the algebraically equivalent quotient form to avoid
unnecessary products. A weak charge-moment change is not a charge-conservation
failure. No constant-charge constraint is imposed. State negativity and exact
boundary incompatibility `Y_i=0 and F_i<0` are reported by species, independently
of rate-error budgets. These are diagnostics without accepted physical tolerance,
not proofs of positive integrated solutions. Negative states are preserved, not
projected into a valid state. No state/RHS clipping, renormalization or projection
is performed. Unsupported open/truncated/auxiliary-reservoir balances are
`UNAVAILABLE`; this formula is not silently applied to them.
Heating is `EXCLUDED_NOT_EVALUATED` for Phase 1's `iheat=0` contract. No heating
head, zero heating truth, accepted energy score or energy closure is fabricated.

## Later acceptance, without choosing a method

Later authorized model work must define the applicable physically admissible set,
including nonnegative composition, network-consistent baryon/external balances,
and weak Ye evolution. Where selected, hard constraint enforcement needs its own
correctness/effectiveness evidence; a soft penalty is not a hard guarantee.
Projection alone does not prove positivity, stable dynamics or an accurate
physical path. Do not implement an encoder, decoder, latent flux architecture or
training algorithm from these requirements.

Keep reconstruction error separate from decoded dynamical consistency. A decoder
`Y=D(z,p,t)` needs `Ydot=J_z D * zdot + J_p D * pdot + partial_t D` for all
conditioning dependencies. An accurate reconstruction alone does not establish
that chain rule, latent closure or history independence. Later work needs both
physical residual and representation/closure evidence, where appropriate.
Free-running held-out trajectories must separately validate abundances/yields,
energy and weak Ye, equilibrium approach/departure and relevant closure, failure
and domain exits, solver/tolerance sensitivity, Jacobian/JVP numerical consistency,
and total measured cost at matched accuracy. A blanket rule requiring every
Jacobian eigenvalue to be negative is inappropriate, including conserved/null
modes. No Jacobian/solver execution is introduced here. An actual model card starts
with an actual Phase 2 artifact; this work creates no trained model card.

## Original guidance and source limits

Inspected 2026-11-17 local date (UTC retrieval on 2026-11-18); references remain
read-only. These sources motivate questions, not nuclear units or thresholds.

- [Official CVODE mathematics, §3.2.1 Eq. 3.6](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html)
  scales state error with `atol + rtol*|y|` in a weighted RMS norm. This is a useful
  dimensional/scaling principle, not adoption of CVODE, its tolerances, or a claim
  that local solver error controls long-time surrogate error. The `latest` page
  was inspected; no immutable SUNDIALS release is claimed.
- Maintainer-linked [XNet at b4389c7](https://github.com/jaharris87/XNet/tree/b4389c72467a5b64db6074d2fa18dd05531c72c7)
  local `source/xnet_abundances.F90` has auxiliary `xext/yext/zext` moments and
  total `Ye=Q/B`; its SHA256 is `7b2513e586077599b33fe6ef6fda1c1d19a4463e8d0a15414e8ba1031b250769`.
  `xnet_integrate.F90` has a mass-excess/cv branch active only for `iheat>0`
  (SHA256 `a98cf25420d4c5afafa85f110d2bc990600d7c3324b820d0d0b91c8cd4f95d7b`).
  The **distinct pinned** declared-reference `xnet_abundances.f90` has no auxiliary
  reservoir and uses the supplied full-160 moments, `Ye=Q/B` (SHA256
  `68bb4ada6833dc1bac3e4479d180b000d1eeee413e085e08fef1b6d9ea3dbdd5`).
  Its EOS wrapper calls that no-aux interface (SHA256
  `c9ca83db11a9f425b2bd2db0e352ac63398b768775129ba8b9fc1740d26d3908`).
  [Reference preparation](../../experiments/rhs_reference/README.md) binds the generating
  candidate; a newer checkout is not a substitute.
- [ChemNODE v3](https://arxiv.org/abs/2101.04749v3), revised 2021-10-07: inspected
  abstract describes integrated chemical-kinetics training. Full-text HTML access
  failed in the original guidance inspection; no detailed nuclear claim follows.
- [Phy-ChemNODE, NeurIPS 2024 workshop paper](https://ml4physicalsciences.github.io/2024/files/NeurIPS_ML4PS_2024_151.pdf),
  pp. 1–3/equation 3: inspected chemical reconstruction/data/latent/elemental loss
  terms are optimization penalties, not a general proof of hard conservation.
  Its chemical Y denotes mass fraction, unlike this project's molar Y.
  No speedup/accuracy claim transfers to nuclei.
- [Hix and Meyer, astro-ph/0509698v1](https://arxiv.org/abs/astro-ph/0509698v1):
  inspected review abstract supplies stiffness/equilibrium background. The
  originally attempted full-text HTML retrieval failed; no uninspected theorem
  or adopted numerical tolerance is asserted.

The local source-observation receipt SHA256 is
`cc03310da51d000521d47060f1494f067a57a09c9a30d710e5f715ace746d885`.
It records source versions/access limits, not new producer execution or acceptance.

D-024 subsequently accepts a distinct [native digital-fidelity benchmark](NATIVE_BENCHMARK.md)
with direct exact-label relative profiles. It does not replace this physical-change
budget or supply its unresolved application allowances/scales/timescales. Its
separate schema/module leaves this API/configurations/results unchanged.
