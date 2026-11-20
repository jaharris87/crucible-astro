# Phase 2B full-state MLP experiment

This is one fixed CPU instantaneous-RHS experiment, accepted under
[D-031](../../docs/DECISIONS.md#decision-d-031-accept-the-reviewed-small-full-state-mlp-experiment)
and [issue #42](https://github.com/jaharris87/crucible-astro/issues/42).
The exact protocol is [phase2b.json](../../configs/mlp_baseline/phase2b.json);
the [reviewed proposal](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042652534)
records its numerical choices and [acceptance](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042848745).
It is one fixed 162→64→64→160 tanh/linear MLP.
Actual [results](results.json), [validation report](../../docs/reports/2026-11-20-phase2b.md)
and [model card](../../docs/model-cards/genesis_modelcard_full_state_mlp_v0_1.md)
document the reproducible negative fidelity outcome.

Use all ordered 160 molar-Y components plus recorded T9/rho to predict all 160
fresh signed native instantaneous RHS components. Scaling is learned on train
only; output scaling is inverted before scoring. There is no reduction, energy
head, clipping, conservation projection or model-based final-test access.

## Run locally

Real data, predictions, weights and private records remain local; unresolved data
rights do not become release permission through the software license. Configure
accepted files using the existing [loading guide](../../docs/science/data/LOADING.md).
From this checkout, replace the absolute example paths with private local paths:

```sh
uv sync --locked --no-editable
uv run --no-sync python -B -m crucible.mlp_baseline train \
  /absolute/access.json /absolute/attempt-001 \
  --protocol configs/mlp_baseline/phase2b.json --source-root "$PWD"
uv run --no-sync python -B -m crucible.mlp_baseline reload-check \
  /absolute/access.json /absolute/attempt-001 \
  --protocol configs/mlp_baseline/phase2b.json --source-root "$PWD"
```

The runner loads train and validation once each, retains epoch logs, selected and
last-finite checkpoints, numerical failures, physical predictions/labels and
strict source/configuration/environment/qualification bindings. It rejects a
changed protocol or runtime. Source hashes refer to actual module/configuration/
lock bytes, including for a noneditable install with `--source-root`. Retain the
command, Git commit and process logs alongside each attempt, including preflight
refusals before the numerical core creates its output directory. Use a new attempt
identity rather than overwriting any prior run.

Score each full model/split separately with the original D-026 successor:

```sh
uv run --no-sync python -B experiments/mlp_baseline/score.py \
  /absolute/access.json /absolute/attempt-001 validation mlp
```

Repeat that scoring command for `train mlp`, `validation zero` and `train zero`.

MLP scoring requires the completed run's `result.json`, matching model/manifest
and prediction hashes, and the selected role's exact data contract, record order
and target bytes. The receipt binds those identities before scoring the verified
prediction snapshot. The zero comparator needs no model/run result. These
[audit repairs](../../docs/reports/2026-11-20-phase2c-audit-assessment.md) leave
the original frozen artifacts and D-026 scoring arithmetic unchanged.

Scoring retains full per-component/per-species/history/group/category/regime detail,
all D-024 profiles, native supplementary diagnostics and a cost/provenance receipt.
There is no test role. A failed/nonfinite vector is a failed attempt, never a
successful-case exclusion. Physical headline errors use the accepted `A*(p-f)`
definition in **mass_fraction/s**, while model outputs/labels remain in native Y/s.

## Reload and exact clean reproduction

`model.npz` contains only numeric weights/biases/scales; `model.json` binds exact
species, units, memberships, reference and protocol identities. `predictions.npz`
contains both train/validation physical predictions, original labels and ordered
record IDs. They are private artifacts and are loaded with `allow_pickle=False`.

Use a fresh checkout of the recorded source and a fresh locked noneditable
installation on the same CPU/platform to repeat the exact protocol once in a new
output directory. Compare every array in `model.npz` and `predictions.npz` by
dtype, shape and bytes; compare selected epoch and complete epoch logs too. The
accepted tolerance is zero. Container/manifest metadata and measured runtimes
are distinct from numerical identity. Cross-platform identity is unclaimed.
Do not change a seed, architecture, learning rate or tolerance after seeing a
poor result. One exact reproduction is a check, not another selection candidate.

The actual held-out-independence check keeps training fixed, changes validation
Y/T9/rho/targets in memory, and compares `diagnostic_epoch_one` scale and epoch-one
weight hashes with the actual fit. These must remain equal; validation checkpoint
selection is allowed to change. No altered inputs are written to accepted files.

Pointwise digital fidelity, physical application, energy, rollout accuracy and
matched-accuracy speedup remain separate claims. Phase 2C needs its later scope
acceptance; this experiment authorizes no integration or new reference execution.
