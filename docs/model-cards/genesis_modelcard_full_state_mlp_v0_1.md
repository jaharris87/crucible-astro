# Full-state native-RHS MLP — model card 0.1.0

**Actual artifact:** Phase 2B seed 20261120, selected epoch 407, CPU binary64.
This is a reproducible **negative D-024 digital-fidelity result**. Code review, human merge and merged-result verification are tracked in
[issue #42](https://github.com/jaharris87/crucible-astro/issues/42).
This card describes a private local artifact; it is not a model release.

## Identity and intended use

| Binding | Actual identity |
| --- | --- |
| Model NPZ SHA256 | `4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793` |
| Model manifest SHA256 | `3d11aca1efcff2e025fa196bf00352ac42477a44eba39f8cd464ac8c3188740e` |
| Train/validation predictions NPZ SHA256 | `70fc334c873a07791fdcad0a25e7e51f4a71e4235cbd43140ed234613a2c84db` |
| Executed source | `5ea61f157e7e38bbd2a106bf1b51d9560fcad55f` |
| Configuration and environment | [Fixed protocol](../../configs/mlp_baseline/phase2b.json), lock/source digests and actual versions in [aggregate results](../../experiments/mlp_baseline/results.json) |
| Scientific authority | [D-031 acceptance](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042848745), after [independent proposal review](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042701075) |

Intended use is a small, reproducible full-state comparison control on the named
finite within-parent pointwise benchmark. It has no qualified physical application,
energy, trajectory, hydrodynamic coupling or speedup use. No final-test predictions
or performance evaluation have been made. Do not interpret successful serialization
or a lower optimization loss as scientific validity.

## Data and task

The [qualified data card](../data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md)
and [loading contract](../science/data/LOADING.md) identify
`ccsn-primary-native-rhs-pointwise` 0.1.0 and its unchanged D-025 qualification overlay,
D-019 native reference, species order and exact grouped memberships. Training uses
17,659 states /274 histories /66 operational groups; validation uses 3,220 /51 /14.
The final-test membership remains sealed for model use. One parent simulation,
operational groups, residual correlations and support gaps limit generalization.

Inputs are all ordered 160 molar-abundance Y components plus recorded T9 in GK
and density in g/cm³. Targets are all 160 fresh native instantaneous signed dY/dt
components in `molar_abundance_Y/s`. Composition-derived Ye is not an independent
feature. IDs, groups, categories, packets, time, stored derivatives and energy
are not predictive features. Raw/quarantined artifacts, original qualification
bindings, memberships and reference projects were preserved.

## Method and development

The network is 162→64→64→160, tanh after the two hidden affine maps and an unrestricted
linear output, with 24,992 parameters. There is no encoder, PCA, decoder, species
reduction, extra physical head, clipping or conservation projection. Each input
and target column uses training-only max-absolute scaling, with denominator 1 only
for an exactly all-zero training column. Constant columns remain inputs/loss terms.
Output scaling is inverted before physical scoring. This optimization transform
is not a derivative coordinate map.

One seed 20261120, Xavier-uniform gain 1/zero biases, Adam 0.001, batches 256 including
the tail, one CPU thread for intra/inter-op work and deterministic algorithms.
Validation pooled normalized MSE alone selects the earliest strictly best checkpoint,
including epoch 0. Training stopped after 437 epochs under patience 30; selected
epoch 407 has validation normalized MSE `0.00010598150261279192`. No search or
additional selection candidate was run. The deterministic comparator returns 160
exact zeros. Exact architecture/optimizer/stopping/failure rules remain in the
accepted protocol, not imported from a chemical system.

Training/validation target scaling produced 145 /34 nonzero-to-zero binary64
underflows; input underflows 0. These and nonexact round trips are counted under
the predeclared numerical bound. Original physical labels remain intact, including
tiny nonzeros, and all remain in physical scoring. No physical floor was added.

## Evaluation and reproducibility

The [validation report](../reports/2026-11-20-phase2b.md) and
[aggregate results](../../experiments/mlp_baseline/results.json) give complete
headline populations/weights and full private report digests. Physical headline
errors are the accepted `A*(prediction-label)` errors in **mass_fraction/s**;
model predictions and labels stay in native Y/s.

On validation, MLP pooled absolute RMS is 4,591,539.195415232 versus
21,757,462.437253535 for zero RHS. Both attain 0/3,220 whole vectors at each of
0.1%, 1%, 5%. MLP nonzero relative RMS/max and relative macro RMS have status
`UNBOUNDED_BINARY64_REPORT`; they are not zero or failed predictions. The
exact rational profile comparisons remain defined. Zero-target behavior, signed
and absolute errors, per-species and supplied history/group/category/regime
strata, all failures and native supplementary diagnostics are retained in full.
There are no fitted physical allowances or successful-case exclusions.

Report pooled, equal-history and history-first equal-group MSE before taking RMS;
these reporting weights do not replace pooled normalized-MSE checkpoint selection.
The actual D-026 successor source/adoption receipt is bound separately from the
unchanged original qualification scorer. No scorer repair or detail omission was
needed. The honest negative profile result does not authorize further fitting.

Fresh-process reload and a clean checkout/fresh locked noneditable refit reproduce
every weight, scale, train/validation prediction, selected epoch and complete epoch
log bitwise at the accepted zero tolerance. Actual validation-extrema mutation
with training fixed leaves fitted scales and first-epoch weights unchanged;
validation selection may depend on validation. Serialization identity, numerical
reproducibility and predictive fidelity are separate conclusions. Cross-platform
bitwise reproduction is unclaimed; Linux CI checks synthetic software behavior.
The fresh reproduction reused the locked package cache; cold-network reproduction
was not tested.

Actual fitting took 29.02s (clean refit 30.35s), peak about 930MB, on Apple M4 Max
with 64GiB RAM. Loading and full exact reporting are measured separately in the
linked aggregate record. Single-call inference timings under concurrent reporting
are informational, not matched-accuracy speedup evidence. No failed fits,
reproduction attempts or data/species exclusions occurred; operational and
synthetic-test failures/dispositions are retained in issue/run evidence.

## Guidance, access and maintenance

This manual narrative is Genesis-guided and claims no machine/schema/template
conformance. On 2026-11-20 the official BPSW
[model-card page](https://gitlab.osti.gov/genesis/modcon-bpsw/-/blob/main/cards/templates/model-card.md)
and raw-file URL redirected to sign-in; its anonymous project API returned 404.
The actual model template/current commit therefore remains unavailable. The
[guidance evidence](../phase1/GENESIS_GUIDANCE.md) separately pins the official
released data-card guidance at v2.0.0; that data template is not substituted for
the inaccessible model template. Current access probes are retained locally.

[Zhang, Ramanuj and Sankaran](https://doi.org/10.1111/jace.70267) distinguish
linear PCA transport coordinates from nonlinear learned RHS dynamics and
separate pointwise from integrated assessment. That reasoning informs the
separation of evaluations here; chemical architectures, hyperparameters, units
and performance are not nuclear prescriptions.

The CRUCIBLE maintainer is the artifact/data custodian. Real records, predictions,
weights, private paths and complete detailed reports remain local. Redistribution
rights remain unresolved; BSD-3-Clause software publication grants no model/data
release authority. See the [local reproduction guide](../../experiments/mlp_baseline/README.md).
Update this card when its artifact, evaluation or limitations change. Phase 2C
requires later accepted scope; its analytic integration checks and scheduled
post-2C audit in #43 are not performed by this 2B artifact.
