# Phase 2D resumption and modeling followups

**2026-11-24.** The maintainer explicitly resumed the 2D goal after the preserved
2026-11-23 pause. Actual checkout is `codex/phase2d-trajectory-references`, starting
at `b6c8c8f`; remote main remains `75b2ec3`, draft PR #51 and issue #44 are open.
D-038/D-039 evidence and their independent assessments are complete. Their
producer allowances are exhausted; **no new build or physical evaluation has
occurred on this resumption**. No full-horizon reference qualifies.

## Next numerical decision

The [D-040 proposal](../../experiments/trajectory_reference/CORRECTION_PROTOCOL.md)
keeps the distinct D-039 source, binary64 physical Y, fixed cases/forcing/physics
and global resolution/reproduction criteria. It explicitly replaces the raw
backward-Euler residual stopping gate with two small raw Newton corrections;
residuals remain fully reported. Native source inspection and the numerical
rationale are linked in that protocol. This is a new criterion needing human
acceptance, not a retroactive pass or a claim that precision cannot matter.

An offline counterfactual reweights retained D-039 **standard-run** corrections;
it does not execute proposed standard/tight runs. At the original `h=1e-4 s`:

| Case / proposed controls | First pair, iterations | Previous / current correction norm |
| --- | --- | --- |
| Development standard | 5 / 6 | 0.05607553 / 0.00921540 |
| Development tight | 5 / 6 | 0.56075530 / 0.09215399 |
| Validation standard | 5 / 6 | 0.36859861 / 0.000783434 |
| Validation tight | 6 / 7 | 0.00783434 / 0.00784619 |

Both corrections use the same current post-state weights, exactly as proposed.
The underlying raw archive remains SHA256
`6b44f97052abaa407931994948819b1f99f9a073aaa72e51fc494bc0fd875580`;
local derived calculation JSON SHA256 is
`5acca3ed5aad66d7c4a1ec97787f209940dbe3ca8c03537221cb7d44188749f7`.
These observations motivate a pilot; they predict neither later steps nor global
accuracy. The protocol proposes a single conditional 24-trajectory envelope with
two fresh builds, early joint failure gates and fixed diagnostics. No execution
is authorized by its preparation. Fresh protocol review is pending.

## Maintainer modeling feedback retained for the next proposal

These followups come from the maintainer's 2026-11-24 meeting feedback. They do
not select or fit a replacement model under 2D. The [existing sequence](../PHASE_2_LAUNCH.md)
and D-006 still control later reduction work; this is not a competing launch plan.

| Topic | Current verified fact | Followup and trigger |
| --- | --- | --- |
| Input scaling | The frozen MLP already divides each Y/T9/rho column by its training-only maximum absolute value; zero-column scale is one. Targets are independently scaled the same way. See `fit_scale` and `_prepare` in `src/crucible/mlp_baseline.py` and `configs/mlp_baseline/phase2b.json`. | In the next accepted model proposal, assess scaling and dynamic range explicitly, keeping training-only fitting and existing grouped holdouts. Scaling itself is not missing from 2B. |
| Log features or coordinates | Current features/state are physical Y, T9 and rho with linear scaling. Logs have not been qualified. | Propose log(Y), log(T), log(rho) features with explicit units/reference scales and exact-zero policy. Distinguish feature encoding from evolving `u=ln(Y/Yref)`, which gives `du/dt=F/Y` only for positive Y and needs its own boundary/Jacobian contract. Signed F cannot simply be logged. Feature logs do not change prescribed forcing interpolation or automatically fix native Y update rounding. |
| PCA/AE reconstruction and reduced dynamics | The 162→64→64→160 MLP is the accepted full-state negative control. Its 64-unit hidden layers are not a reduced physical state. Identity/full-state first was the accepted sequence, not evidence against reduction. | Prioritize a separately accepted reconstruction/reduced-dynamics proposal at D-006/S05. Keep reconstruction, reduced RHS/closure and decoded trajectory errors separate. No requirement to improve the frozen MLP before proposing reduction. Training and Phase 3 remain unauthorized here. |
| Wider MLP hidden layers | The fixed small baseline was not an optimized architecture. Nonlinear reaction products and temperature-dependent rates motivate investigating capacity; they do not increase the number of physical input coordinates or prove a particular width optimal. | Carry wider-than-input hidden layers as a hypothesis for a later bounded model comparison, not a silent 2B architecture/checkpoint change or current sweep. |
| Y versus A-weighted metrics | The kinetics state and target are Y and dY/dt. D-024 accepts specific A-weighted absolute reports, not a universal choice of primary physical quantity; componentwise relative criteria cancel A. | Retain the earlier maintainer request to revisit kinetic Y errors separately from inventory/B diagnostics in a future metric decision. No historical rescoring or numerical threshold change now. |

Original model NPZ SHA256 remains
`4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793`.
No fitting, changed preprocessing, learned rollout, final-test inspection or
Phase 2E work is included. The immediate decision is a reviewed 2D numerical
protocol and its concrete producer scope; reference/merge/final acceptance remain
separate after evidence exists.
