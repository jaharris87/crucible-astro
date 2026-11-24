# Phase 2D pause checkpoint — 2026-11-20

**Incomplete; no accepted trajectory reference.** Paused at the maintainer’s
request. [Governing receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7050616078)
records actual outcomes and bounded independent assessment; [draft PR #51](https://github.com/jaharris87/crucible-astro/pull/51)
remains open. This author-prepared checkpoint is not final scientific acceptance
or an independently reviewed report closeout.

## Source and authority

D-036 accepted the frozen [protocol](../../experiments/trajectory_reference/PROTOCOL.md),
SHA256 `966fbff8d2322ae8e6666063f35c1b87cced7d5ccbaf663ccae362613f98fdad`.
D-037 explicitly accepted one replacement build after the first successful build
was stopped by a runner-only synthetic gate error. Code candidate
`a771930d0e4f9b52077416b6fa32bb5f4b67f7ae` passed independent ordinary/focused
review, all 120 Phase 2D public Python tests and Linux CI. The full local installed
suite passes **771 tests**; Ruff, documentation and whitespace checks pass.
Physical artifact acceptance remains separate from code review.

The two fixed permitted saved states and sparse prescribed T9/rho histories define
new 10 ms IVPs, not historical hydrodynamic reproduction. All 160 physical Y
components, pinned native dY/dt, composition-derived Ye, inputs and memberships
remain unchanged. Heating, learned rollouts, fitting and final-test outcomes were
not used. The negative 2B baseline remains unchanged.

## Actual population and numerical evidence

| Work in primary campaign | Observed outcome |
| --- | --- |
| Replacement fresh build; ten compiled synthetic fixtures | Pass |
| Two initial RHS controls | Success; exact original D-019 component bits |
| Development L0, L1, L2, L3 and tight | Five numerical failures, each at first step; achieved horizon 0 |
| Validation L0 | Interrupted on requested pause; 25 complete saved records, last time 0.00002539062500000003 s of 0.01 s |
| Validation L1–L3 and tight | Not attempted |
| Six planned Jacobian diagnostic processes | Not attempted |
| Clean reproduction | Prepared only; no build or physical process submitted |

No case was excluded or replaced; no numerical failure was retried. The primary
manifest remains incomplete and interrupted validation has no native SUCCESS.
Missing requested outputs, convergence, constraints and reproduction cannot pass.

Independent read-only Sol High assessment of the hash-checked development L0
bundle confirms **P2D-NUM-001**: ten step attempts × 30 Newton iterations, zero
accepted steps/projections; all 300 normalized residuals exceed one. At smallest
attempted h=1.953125e-7 s, minimum norm is 15.9308 and final norm 27.4511.
Independent recomputation of 290 residual norms agrees exactly. No equation,
indexing or linear-solve defect was demonstrated. Cancellation and finite-
difference/Newton precision limits are supported hypotheses, not proven causes.
No global refinement differences or full-horizon reference accuracy are established.

**P2D-PROP-003**, independently confirmed, is a protocol defect: direction two’s
mixed signs and trace-abundance floor admit no central or one-sided two-probe
stencil at any of nine multipliers for either fixed initial state. Source follows
the accepted protocol, but the required stable window is impossible. A fixed
nonnegative alternating-support direction is a possible narrow replacement;
EOS/branch admissibility and derivative agreement remain untested. It is not an
accepted protocol change.

A separately corroborated forensic gap affects exhaustion snapshots: native retry
cleanup resets Y/time/forcing after the tenth failure, while saved F/LU retain the
preceding evaluation. Those snapshot fields are not one consistent evaluated
state. Retained residual and Jacobian-baseline streams support the numerical
failure above. Repair snapshot retention before new producer work.

## Retention, costs and resumption

First preflight-only raw archive SHA256:
`f39ba5279ef648e62f0c4837623403901d75d8ac200b5fcfae2df738661f7f03`.
Paused primary raw archive SHA256:
`75a5949e8fb74cfe386a415e40c7ecc2e284042d96614b2179a3bf77bb617ec2`.
Both full source/build/log/input/output archives remain private. Original source,
accepted data, model/scalers and historical evidence are preserved.

Job 61689197 is terminal CANCELLED on user request: scheduler elapsed 6m23s,
reported total CPU 6m13.246s; batch peak RSS 449,776 KiB. The paused raw archive is
about 48 MiB. These are measured checkpoint costs, not isolated integration costs
or compute caps. The first build used 12.76 s wall, 9.83 s CPU and 91,044 KiB peak
RSS. Complete timing/storage and artifact verification remain unfinished.

On resume, analyze/reload all retained artifacts offline, repair the forensic
retention path, and prepare a reviewed bounded diagnostic/integration revision
addressing the measured residual failure and direction admissibility. Obtain
explicit scientific/protocol and producer scope acceptance before any new build
or physical evaluation. Do not classify this pause or a numerical failure as an
automatic infrastructure retry. No tolerance relaxation, new case or extra run is
accepted. Human reference, merge and final 2D acceptance remain outstanding.
Keep issue #44 and milestone #3 open. Phase 2E is not started.
