# CRUCIBLE handoff

Updated **2026-11-20**. Phase 1, the documentation migration, **2A and 2B are
complete**. Phase **2C only** remains under [issue #43](https://github.com/jaharris87/crucible-astro/issues/43),
[the single Phase 2 sequence](PHASE_2_LAUNCH.md) and open milestone #3.
No 2D work is authorized.

## Verified integrated state

The original 2C implementation was independently reviewed and merged through
[PR #48](https://github.com/jaharris87/crucible-astro/pull/48) at
**`505d5562040ec7733ec7903c7123f86921653186`**. Its merged tree equals the reviewed
tree; locked noneditable 611-test suite, CI, synthetic reload and private callable
checks passed in the [merged receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045039634).
The scheduled fresh-context read-only Sol High merged 2A–2C audit also passed,
with its original scope/limits preserved in the [audit receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045144994).
Those passing checks did not cover every defect subsequently demonstrated.

Earlier settled receipts: [Phase 1](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012),
[2A](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315),
[2B](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7043899683).
The [2B model card](model-cards/genesis_modelcard_full_state_mlp_v0_1.md),
[dated report](reports/2026-11-20-phase2b.md) and [guide](../experiments/mlp_baseline/README.md)
retain the frozen negative digital-fidelity baseline. Zero whole-vector attainment
and unbounded binary64 relative RMS/max are accepted results, not repair authority.

## Active audit reconciliation and next gate

The maintainer requested independent assessment of Codex, Claude and Gemini audits
of exactly `505d556`, including their isolated uncommitted proposals. Original
reports, complete patches, file snapshots and diagnostics remain unchanged, with
local preservation inventories and public hashes. The
[assessment receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047204328)
and [consolidated dispositions](reports/2026-11-20-phase2c-audit-assessment.md)
record actual reproduction and limits. Work is on `codex/phase2c-audit-repairs`
from that verified main; only the isolated scoring worker authored its two files.

Next: complete repair-candidate checks, publish one coherent draft PR, obtain a
fresh independent focused exact-candidate review, repair/verify findings and use
normal protected integration under [D-034](DECISIONS.md#decision-d-034-bounded-2c-recommendations-and-merge-delegation).
Verify the actual merge and update #43. The broad integrated audit is not repeated;
the new review covers repairs and affected behavior. **Final 2C closeout remains
the maintainer's reserved decision**, after all required exits. Keep issue/goal
incomplete and milestone #3 open. No generic continuation or elapsed time grants
that decision.

Native goal (existing, not replaced):

> Complete CRUCIBLE Phase 2C: establish a small callable RHS and numerical
> integration path with independent analytic and stiff-problem verification,
> consistent state/units/Jacobians, complete failure and convergence evidence,
> clean reproduction, independent review, human-approved merge, merged-result
> verification, and the scheduled bounded post-integration 2A–2C code audit
> with findings appropriately resolved or dispositioned.

The native service currently retains its earlier blocked/waiting status; the
new explicit repair instruction supplies work authority without completing the
goal. Its final-closeout dependency remains outstanding.

## Evidence and reproduction boundaries

D-033 accepted the [reviewed protocol](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044376981),
SHA256 `35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2`.
The accepted campaign executed at `f3a12a7`: six positive integrations and both
expected negative attempts passed constraints/refinement and fresh reproduction.
All 20,879 permitted frozen callbacks passed saved-batch/one-row identity and the
declared singleton/batch allowance. The [dated 2C report](reports/2026-11-20-phase2c.md),
[aggregates](../experiments/integration/results.json) and
[public synthetic artifacts](../experiments/integration/artifacts/manifest.json)
retain those original source bindings. Repair regression evidence is separate.

Private records, original model/scalers/predictions and run evidence remain local.
The model NPZ SHA256 remains
`4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793`.
An old external development checkout containing the scoring configuration was
removed after original merged checks. The current private resolver now overrides
that digest to the identical committed bytes; the original overlay and 2B access
file were preserved. See the [loading guide](science/data/LOADING.md).

The [Qiosk/original Zhang-paper trace](../experiments/integration/GROUNDING.md)
continues to ground the separation of source learning, representation and
integration. Analytic wrapper verification supplies no nuclear rollout claim.
Preserve physical ordered 160 Y, T9/rho, composition-derived Ye and signed Y/s;
no fitting, projection, real MLP integration or final-test model use.

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
