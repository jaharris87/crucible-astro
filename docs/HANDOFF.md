# CRUCIBLE handoff

Updated **2026-11-20**. Phase 1, the D-027 documentation migration, **2A and
2B are complete**. [D-032](DECISIONS.md#decision-d-032-phase-2c-launch-and-bounded-numerical-verification)
invokes **2C only**, governed by
[issue #43](https://github.com/jaharris87/crucible-astro/issues/43).
[Milestone #3](https://github.com/jaharris87/crucible-astro/milestone/3) and
[the existing sequence](PHASE_2_LAUNCH.md) remain the only phase tracking structure.

## Verified starting state

Startup inspected a clean checkout, read the live governing issue and fetched
`origin/main`; both checkout and remote are at
**`a81552e9fc1c22ffb595936b5a0348a9f58fe766`**, the human-approved PR #47 merge.
Read the [Phase 1 final receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration final receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012),
[2A final receipt](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315)
and [2B final receipt](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7043899683)
once. They record completed review, concrete human merges and merged verification;
these settled exits are not reopened. The 2B merge has 515 installed-package tests,
merged CI, bitwise fresh reload/clean refit and complete reproduced reports.

The [actual 2B model card](model-cards/genesis_modelcard_full_state_mlp_v0_1.md),
[validation report](reports/2026-11-20-phase2b.md),
[aggregate record](../experiments/mlp_baseline/results.json) and
[experiment guide](../experiments/mlp_baseline/README.md) retain the original
artifact/results and their review boundaries. The frozen model is an honest
negative digital-fidelity baseline: zero whole-vector D-024 attainment at every
profile and unbounded binary64 nonzero relative RMS/max reports. This does not
authorize retraining or block independent mathematical integration verification.

Retained local configuration and original 2B artifacts were located read-only.
Model NPZ SHA256 `4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793`,
manifest `3d11aca1efcff2e025fa196bf00352ac42477a44eba39f8cd464ac8c3188740e`
and predictions `70fc334c873a07791fdcad0a25e7e51f4a71e4235cbd43140ed234613a2c84db`
match their retained records. Private paths remain in ignored local configuration.
No artifact regeneration or model execution was needed for startup.

## Active 2C work and next decision

The native goal was inspected (none existed), then created for **active 2C only**:

> Complete CRUCIBLE Phase 2C: establish a small callable RHS and numerical
> integration path with independent analytic and stiff-problem verification,
> consistent state/units/Jacobians, complete failure and convergence evidence,
> clean reproduction, independent review, human-approved merge, merged-result
> verification, and the scheduled bounded post-integration 2A–2C code audit
> with findings appropriately resolved or dispositioned.

Integration branch: `codex/phase2c-numerical-integration`, from the exact verified
main above. The [concrete numerical protocol](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044234697)
received a [fresh-context read-only independent `gpt-6.1-sol` High PASS](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044293163),
with no consequential findings or protocol edits. SHA256:
`35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2`.
**The maintainer accepted the exact protocol in [D-033](DECISIONS.md#decision-d-033-accept-the-reviewed-phase-2c-numerical-protocol)**
([receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044376981)).
Implementation is active; no accepted campaign has run yet. Next action: implement
and verify the accepted protocol, then obtain ordinary exact-candidate review.
[D-034](DECISIONS.md#decision-d-034-bounded-2c-recommendations-and-merge-delegation)
delegates sufficiently vetted 2C recommendations, including reviewed/check-passing
implementation or repair merges. Final 2C closeout remains an explicit maintainer
decision after all audit/repair exits. The [Qiosk and original-paper trace](../experiments/integration/GROUNDING.md)
records the reaffirmed design lineage and deliberate nuclear adaptations.
No silence, generic goal continuation or protocol acceptance grants merge authority.

After acceptance, implement/check/report autonomously within that exact protocol.
Reuse the frozen loader/model/scalers; preserve physical ordered 160 Y, recorded
T9/rho, composition-derived Ye and native signed Y/s output. Frozen-model checks
are train/validation pointwise/callable equivalence only. Synthetic fixtures verify
integration; no real MLP rollout or new producer/reference execution. Model-based
final-test access stays sealed; structural all-role loader checks are distinct.

Keep one coherent PR unless a concrete reason requires a split. Follow self-review,
draft PR, fresh exact-candidate independent review, repairs/focused verification,
concrete human merge decision and merged-result checks. **Then** perform the
already scheduled bounded fresh-context read-only `gpt-6.1-sol` High merged 2A–2C
audit in #43. Preserve original audit findings/dispositions and route required
repairs through reviewed PRs/human merges/merged checks. Do not auto-close #43 at
first implementation merge. Keep the goal/issue incomplete through required audit
exits; milestone #3 stays open. Stop after 2C. 2D/2E need separate authority.

## Scientific and execution boundary

D-025 qualifies `ccsn-primary-native-rhs-pointwise` 0.1.0: **24,314 states /
380 histories / 94 operational groups**, with **17,659 / 3,220 / 3,435**
train/validation/test states. Full ordered 160-species molar Y, recorded T9/rho,
and native Ye=Q/B define the pinned D-019 instantaneous RHS. D-024 headline
metrics and the explicitly accepted D-026 successor scorer remain distinct from
the unchanged original qualification/scorer bindings.

[The qualified card](data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md)
and [finite contract](science/benchmark/NATIVE_RHS.md) own purpose/limitations.
Qualification covers finite within-parent numerical emulation; physical application,
heating/energy and rollout accuracy remain unqualified. One parent, operational
grouping, residual correlation and component-support gaps limit inference.
Dataset redistribution rights remain unresolved. Original HDF5 quarantine masks
remain false; permitted use resolves through the separate overlay.

D-017/D-020/D-023 producer authority is exhausted. No new producer build/run,
RHS/NSE/Jacobian/trajectory call, raw/reference modification, bulk conversion,
paid service, release or deployment is authorized. 2D requires its concrete
scientific/reference execution decision; 2E requires frozen-protocol final-test
release. No reduced modeling, model-family search or Phase 3 follows this authority.
