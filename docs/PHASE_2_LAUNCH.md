# Phase 2 — Incremental execution sequence

The maintainer invoked this five-part structure on **2026-11-19** under
[D-029](DECISIONS.md#decision-d-029-incremental-phase-2-and-2a-execution), superseding
the former uninvoked D-028 launch draft at this path. Phase 1 and the D-027
migration are complete; [handoff](HANDOFF.md) records verified startup and current
scope. 2A is complete through PR #46 at `8b6cf71`; D-030 invokes only 2B.
Its concrete MLP experiment requires review and maintainer acceptance before fitting.
This is the single Phase 2 sequence; live issues hold execution detail.

Build one reproducible identity/full-state baseline, assessing instantaneous RHS,
integrated abundance evolution and cost separately. Reduced representations,
model-family comparisons and Phase 3 remain outside scope. Preserve D-019's
reference, D-024 metrics, D-025 qualification/memberships and D-026 successor
scorer identity without rewriting original bindings. Heating/energy remains
excluded unless separately qualified. No accuracy or speedup promise is required.

## Sequence and boundaries

Use one [Phase 2 milestone](https://github.com/jaharris87/crucible-astro/milestone/3),
normally one issue and coherent PR per sub-phase. Detail the active issue; later
issues remain short dependency/deliverable summaries. Each next sub-phase needs
accepted scope and integrated preceding work. Combine that decision with the normal
human merge checkpoint where practical. Use a native goal for the active sub-phase
only; no broad orchestration goal or additional tracker. Current status and next
decision belong in [progress](PROGRESS.md) and [handoff](HANDOFF.md).

| Sub-phase | Deliverable / acceptance boundary |
| --- | --- |
| **[2A — Load the qualified benchmark #41](https://github.com/jaharris87/crucible-astro/issues/41)** | Complete through [PR #46](https://github.com/jaharris87/crucible-astro/pull/46) / [final receipt](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315): minimal named-version/use/split loader, ordinary arrays and metadata, verified overlay/payload/species/units/reference/membership identities, physical-input duplicate checks, scientist example, synthetic tests and local real-data check. No training/fitted preprocessing. |
| [2B — Establish a pointwise baseline #42](https://github.com/jaharris87/crucible-astro/issues/42) | Active under D-030: propose one small CPU-capable full-state MLP and deterministic zero-RHS comparator with inputs/targets, transforms/loss, trial/seed/selection/stopping/resources. After experiment acceptance, fit/check/report coherently, fit learned preprocessing on training only, prove independence and reload, retain failures and create an actual-artifact Genesis-guided model card. Develop on train/validation; no final-test performance evaluation. |
| [2C — Verify numerical integration #43](https://github.com/jaharris87/crucible-astro/issues/43) | Small callable path verified against independent analytic solutions, including stiffness where appropriate, convergence, relevant conservation/positivity and solver failures. Any implicit Jacobian must match the integrated RHS. Retain diagnostics; analytic behavior does not qualify astrophysical rollouts. No new XNet calls. |
| [2D — Establish real trajectory references #44](https://github.com/jaharris87/crucible-astro/issues/44) | Small pinned-XNet proposal with initial states, full forcing/interpolation, grid/horizons/domain, solver/convergence, observables/tolerances, failures/resources. Scientific and producer authority must cover required runs and justified retries before execution. Establish on development/validation histories; predefine final holdout protocol. Exit requires named numerical evidence and human reference acceptance. |
| [2E — Evaluate evolution and cost #45](https://github.com/jaharris87/crucible-astro/issues/45) | Freeze model/preprocessing/protocol and obtain final-test release. Attempt all declared pointwise/real-rollout horizons, retain failures/domain exits/solver diagnostics, report physical-space species/group errors and separate RHS/full-integration costs. Verify reload/clean reproduction, finalize card/report/limits and obtain human baseline or negative-result acceptance before milestone closure. |

Saved historical states plus fresh pointwise labels do not establish a converged
trajectory under the pinned reference. Missing references or unattempted required
rollouts are incomplete. If 2D is blocked, preserve work and present the concrete
gap without a general historical-provenance investigation. Speedup requires a
meaningful matched-accuracy comparison with hardware, precision, setup, solver and
Jacobian work and failures visible. Report poor accuracy honestly. No final-test
tuning; later research must disclose test reuse and address confirmatory evaluation.

## Engineering and evidence

Follow [WORKFLOW](process/WORKFLOW.md): issue → implementation/checks → self-review
→ draft PR → fresh independent review → repair → concrete human merge → merged
verification. Use `gpt-6.1-sol` High as advanced default, Luna for useful narrow work,
and Astra only under the existing justified-escalation policy. Independent reviewers
are fresh and separate from authors. Routine reversible engineering and steps in
an accepted experiment need no per-command approval; every merge remains human-owned.

Keep private paths configurable, real data local and accepted raw/overlay/reference
artifacts unchanged. Reuse existing validation and ordinary functions; extract
shared abstractions only when actual implementations need them. Synthetic tests
keep CI independent of real records. Distinguish structural final-test checks from
model-based final-test evaluation. Address scoring memory/I/O only where the actual
experiment shows a need, preserving aggregate/detail metrics and history/group
weights; supplementary diagnostics do not replace D-024 headline metrics or
introduce unapproved physical allowances.

Retain configurations, data/split/scorer identities, environment, seeds/trials,
measured results, failures and reload/reproduction evidence in linked records.
Model cards describe actual artifacts and official Genesis guidance/revision/access
gaps. Current guides stay concise; issues/PRs/experiment and review records hold
execution detail. No registry, general solver/data platform, paid services,
deployment or data release is authorized. Close each goal only after its actual
exits; close the milestone after accepted reviewed integration of 2E, then stop
before Phase 3.
