# CRUCIBLE handoff

Updated **2026-11-20**. Phase 1, the D-027 documentation migration and **2A are
complete**. [D-030](DECISIONS.md#decision-d-030-phase-2b-launch-and-selected-full-state-mlp)
invokes **2B only**, governed by
[issue #42](https://github.com/jaharris87/crucible-astro/issues/42).
[Milestone #3](https://github.com/jaharris87/crucible-astro/milestone/3) and
[the existing sequence](PHASE_2_LAUNCH.md) remain the only phase tracking structure.

## Verified starting state

Startup inspected a clean checkout and fetched `origin/main`, both at
**`8b6cf713969c4abdcc5353aa18141461bb509616`**, the PR #46 merge. Startup read the
[Phase 1 final receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration final receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012)
and [2A final receipt](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315)
once. All record completed review, human merge and merged verification; these
settled exits are not reopened. The 2A receipt records 489 installed-package tests,
merged CI, all-row structural checks and unchanged accepted artifacts. Historical
reports/cards/reviews and original qualification bindings remain preserved.

## Active 2B work and next decision

The sole native goal is active/incomplete:

> Complete CRUCIBLE Phase 2B: establish one reproducible CPU-capable full-state
> MLP and deterministic comparator on the accepted pointwise benchmark, with
> train-only preprocessing, validation-only development, save/reload and clean
> reproduction evidence, a Genesis-guided model card, independent review,
> human-approved merge and merged-result verification.

Integration branch: `codex/phase2b-full-state-mlp`, from the verified main above.
The selected direction is one small full-state MLP plus exact zero-RHS comparator.
The [exact concrete protocol](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042652534)
received a [fresh-context read-only independent `gpt-6.1-sol` High scope/simplicity PASS](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7042701075),
with no consequential findings or changes. Proposal SHA256:
`0ce78f0d008f3bf166b4efacabc923a633e7fe6d587fb0984de0b1ba3dba60d8`.
**Maintainer experiment acceptance remains pending before fitting**.
The original ridge proposal and its review remain historical records in #42;
their numerical choices and review coverage do not transfer to the MLP.
No fitting or model-based performance evaluation has occurred.

Reuse `crucible.benchmark.load_benchmark` and its scientist-facing contract.
Load train/validation arrays once each per experiment process and reuse them;
measure actual costs before adding caching or streaming. Fit every learned
preprocessing quantity on training only and verify independence by changing held-out
values with training fixed. Never predict or score the final-test partition in 2B.
Keep software public and real data, predictions, weights and private records local.

Issue #42 will retain exact protocol/review/dispositions/acceptance and execution
records; its coherent PR will hold candidate SHAs, checks, independent code review,
human merge and integration receipts. Ordinary review includes scope, readability
and maintainability. Keep this goal incomplete while any required decision or
integration exit remains. No broader Phase 2 goal or new tracker is created.
The integrated 2A–2C audit remains after 2C integration in existing #43.

Next action: obtain maintainer acceptance of that exact reviewed protocol.
Acceptance authorizes routine implementation, fitting,
checking and reporting without per-command permission. Poor fidelity does not
authorize another architecture, seed search or protocol change. Every merge remains
a concrete human decision. Stop after integrated 2B; do not begin 2C here.

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
