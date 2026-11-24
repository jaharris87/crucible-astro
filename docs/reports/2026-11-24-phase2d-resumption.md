# Phase 2D resumption and modeling followups

**2026-11-24.** The maintainer explicitly resumed the 2D goal after the preserved
2026-11-23 pause. Actual checkout is `codex/phase2d-trajectory-references`, starting
at `b6c8c8f`; remote main remains `75b2ec3`, draft PR #51 and issue #44 are open.
D-038/D-039 evidence and their independent assessments are complete. Their
producer allowances were exhausted at resumption, before any new build or
physical evaluation. No full-horizon reference qualified at that checkpoint.
The subsequent D-040 acceptance, implementation and execution receipts below
record later work separately; they do not change the D-039 result.

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
is authorized by its preparation. Fresh independent protocol review passes as
recorded below. The maintainer then explicitly answered **“Accept protocol and
producer scope (Recommended)”**; [the actual receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7140960473)
accepts BOTH the exact reviewed protocol and its producer envelope. No physical
work preceded that answer. Implementation/checks and fresh exact implementation
review come before executing the accepted conditional campaign.

## Independent protocol review

Fresh-context **gpt-6.1-sol High**, separate from the author and numerical advisor,
reviewed exact pushed `d5bbe8967d3039859a44566d8629f0efc9c32c15` against main
`75b2ec32c7983e94a73e88c6b09250a9506eb2d0`, immediate delta from `b6c8c8f`.
Workflow substantive revision is `41b9f631bb88476b9e96108d1f2fe81d22780b62`.
Protocol SHA256 is
`a7eac47716dc710780469b4f107adec59e3fd6e60d435cd62ef60560f13be0a8`.
**Result: bounded protocol PASS, no consequential findings or required repairs.**

The reviewer independently checked governing issue/PR metadata, requirements,
original/adapted solver and corrected directional semantics, raw archive and
inherited protocol/annex/input/source hashes. They decoded all 513 final-phase
Newton records, exactly reproduced all four counterfactual first pairs and
confirmed zero projection, small inventory drift and final development rounding
stagnation. They reconstructed 101/105 base intervals, 9,888 requested intervals
across the proposed run set, diagnostic request arithmetic, staged authority,
retention, failure coverage and reproduction criteria. Scope, readability and
simplicity were included; `git diff --check` passed. The official CVODE source
supports the state-error distinction but does not confer its solver guarantees.

The review was read-only: no edits, build/compilation, physical evaluation,
remote compute, training, commit or posting. It reviewed a protocol, not an
implementation or new trajectory evidence. Ordinary successful-step probe F
and matrices will be unavailable for retrospective forensic verification under
the explicitly proposed compact retention. Original failures, physical limits,
unestablished frozen-MLP compatibility and human decision gates remain visible.
The review grants no producer/reference/merge/final acceptance. Issue #44 holds
the decision presentation and the actual acceptance receipt above.

## Implementation checks and independent review

D-040 implementation candidate `ba9f66ef71671e6b9a4c3009a8bdbcb8b1c71236`, tree
`7cb12f96bba672197172d35eb41a7db50c3d0d1d`, passed **1,108 installed public
tests, zero skips**, Ruff lint/format, documentation/frozen/navigation and
whitespace checks. Preparation001 independently verifies 148 immutable artifacts,
84 staged source files and all twenty per-build plans; manifest SHA256
`86a8060c6b1a4ac6ed732cbeb9a73f33f4d460bcc984e2bdfe490448ead575c4`.
No producer build, compiled fixture, physical evaluation or job submission has
occurred. This preparation is retained unexecuted while review repairs are made.

Fresh-context read-only **gpt-6.1-sol High** exact-candidate review returned
**CHANGES REQUIRED** on that candidate against main `75b2ec3`. The reviewer
independently passed all 1,108 tests and source/preparation checks, reproduced the
four offline prefixes and both retained initial derivative checks, and confirmed
the assembly113 module, D-039 diagnostic helper and build recipe are unchanged.
No native compilation/execution, remote compute, source edit or posting occurred.

| Finding | Original evidence / consequence | Disposition and verification |
| --- | --- | --- |
| P2D-CORR-IMPL-001, P2/high | `correction_campaign.py` at candidate lines 1064–1079 rebuilds a resumed specification and loses `restart_of`, created near line 953. Actual synthetic runner interrupt/resume can report qualification while real `correction_report.verify_interrupted` refuses `restart predecessor differs`. A permitted restart therefore cannot release Build B. | Fix: preserve the predecessor through active/completed records. Isolated repair `9280b99`, integrated as `f697adb`, adds the real runner-to-verifier regression with a missing-link negative control. Lead also connects controller-kill recovery to the real verifier. Focused independent repair verification is required before execution. |
| P2D-CORR-IMPL-002, P3/high | Runnable guide lines 163/166/197 omit the `.json` suffix required by `write_report`; direct reproduction raises `new JSON/NPZ destinations required`. | Same repair uses matching `.json` analyze/reload/compare examples and preserves `.release.json` naming. Focused verification required. |

Independent retention disposition: no additional blocker under the protocol's
explicit delegation of exact persistence schemas. Retained probes have exact
input/original F/variant F; complete coefficient/113-bit polynomial workspaces
are retained at named initial, Newton baseline/post and terminal evaluations.
**This is not per-probe coefficient/quad retention or verification.** The
[wire contract](../../experiments/trajectory_reference/CORRECTION_WIRE.md) and
[guide](../../experiments/trajectory_reference/CORRECTION.md) state this before
execution. Ordinary successful-step probe F/matrices are also unavailable for
retrospective forensic checks. All actually written raw outputs remain preserved.
No numerical criterion or physical execution scope changes through this clarification.

The new decoder/checker independently replays the original standard-run prefixes
under counterfactual correction weights, reaching pairs at 6/6/6/7 iterations.
Replay JSON SHA256
`6542a97960db547223744da36025247f12e82c59db2512068b597472660d2f52`
binds raw archive, checker bytes and derived prefix streams. These are offline
software checks, not new standard/tight executions or full-trajectory evidence.
Focused independent gpt-6.1-sol High verification **PASS** covers exact final
producer source `dd07cc1194ffe4771e900678f1de636152876bfd`, tree
`38f0c4c96e12a68281d36cbb9eea5de11c61a259`. Both findings resolve; 98 correction-
focused tests, lint/format and whitespace checks independently pass, including
the original reproduction, both interruption paths and the missing-link negative
control. No remaining finding or material repair risk is reported. Lead's repaired
full installed suite again passes all 1,108 tests. The [actual review receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7141977684)
precedes any producer execution.

Preparation002 verifies all 148 immutable artifacts, 84 source files and twenty
per-build plans at that exact source/tree; manifest SHA256
`38e94025679e191c205c5500fa6aa111e30a6c7b64c15fa21febbddd48b62912`.
Preparation001 remains unexecuted and unchanged, with a separate supersession
receipt. The [Build A submission receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7142064795)
records job **61935889**, submitted only after review and remote identity checks.
Native build/fixture/numerical outcomes remain unclaimed at submission; the live
issue retains actual subsequent outcomes. Build B is conditional on A's complete
verification and fresh-process reload/release. Status-document updates do not
change the pinned producer source. No reference/merge/final acceptance or 2E.

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
