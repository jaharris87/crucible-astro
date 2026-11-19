# CRUCIBLE handoff

Updated **2026-11-19**. Phase 1 and the D-027 documentation migration are complete.
The maintainer authorized incremental Phase 2 under [D-029](DECISIONS.md#decision-d-029-incremental-phase-2-and-2a-execution).
Only **2A — qualified benchmark access** is active, governed by
[issue #41](https://github.com/jaharris87/crucible-astro/issues/41).
[Milestone #3](https://github.com/jaharris87/crucible-astro/milestone/3) tracks 2A–2E;
[the execution sequence](PHASE_2_LAUNCH.md) reconciles the former launch draft.

## Verified starting state

Startup inspected actual clean merged main **`804fb754b2276a4e859d849ac0a6b78647c2a709`**.
[Phase 1 final receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482)
is COMPLETE; milestone #2 is closed with 29 closed / zero open items.
[Migration final receipt](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012)
confirms PR #40 human merge, exact reviewed tree, 454 installed-package tests,
preservation/navigation checks and merged CI success. The former goals are complete;
these settled exits are not reopened. Historical reports/cards and accepted bindings
remain unchanged. The migration checker documents its original source and recovery.

## Active 2A work and next decision

The sole native goal is active/incomplete:

> Complete CRUCIBLE Phase 2A: provide verified, straightforward access to the
> accepted qualified benchmark, with a runnable example, meaningful tests,
> independent review, human-approved merge and merged-result verification.

Integration branch: `codex/phase2a-benchmark-access`, from the verified main above.
A bounded `gpt-6.1-sol` High author works in an isolated loader worktree; a separate
fresh-context read-only `gpt-6.1-sol` High reviewer will review the exact pushed
candidate. Issue #41 / its PR hold actual commands, artifact checks, full head/base,
review findings/dispositions, CI and eventual human/integration receipts.
Do not infer review, merge or completion from this implementation checkpoint.

The implementation adds `crucible.benchmark.load_benchmark`,
[a scientist guide](science/data/LOADING.md) and `examples/load_benchmark.py`.
It uses the unchanged accepted overlay as a fixed trust root, verifies consumed
bindings and all roles through existing partition validation, and returns ordinary
arrays/metadata in exact accepted membership order. Digest-based local path
overrides relocate files without rewriting accepted manifests. Physical-input
fingerprints and source-call identities are separately checked; signed zeros stay
in output but count equally for cross-role physical duplicate detection.

Public tests exercise qualification, rebinding, order/units, membership/use,
physical duplicates, paths and the example. The local real-data structural check
compares returned fields bit for bit with the HDF5 for all 24,314 rows, verifies
17,659/3,220/3,435 states, 274/51/55 histories and 66/14/14 groups, their disjointness,
and unchanged accepted input hashes. Final exact-candidate results and retained
operational failures are in issue #41 / its PR. Each load rereads a full verified
payload snapshot plus mechanical JSONs; memory exceeds the returned split. It
reuses accepted evidence without rerunning historical producer/comparator streams.
No training, fitted preprocessing or model-based final-test evaluation occurs.

Next decision after checks/review: concrete **2A merge approval**, normally combined
with acceptance of the bounded **2B proposal scope** in
[issue #42](https://github.com/jaharris87/crucible-astro/issues/42).
Begin 2B only after 2A integration and its scope acceptance; fitting additionally
requires acceptance of its coherent experiment proposal. Keep this goal incomplete
until the actual 2A merge and merged-result checks pass. Later goals cover only
the then-active sub-phase; no broad Phase 2 native goal exists.

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
