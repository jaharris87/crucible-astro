# Phase 2D diagnostic protocol v1 — D-038 proposal

**PROPOSED; not accepted and no execution authorized by this document.**
Prepared 2026-11-23 under [issue #44](https://github.com/jaharris87/crucible-astro/issues/44).
This is a bounded investigation inside the existing [Phase 2 sequence](../../docs/PHASE_2_LAUNCH.md),
not another launch or Phase 2E. Preserve the accepted [D-036 protocol](PROTOCOL.md)
and its failed/interrupted campaign unchanged. A fresh independent Sol High review
and explicit acceptance of this scientific protocol AND producer envelope precede
any new build or physical call. Reference acceptance and merge remain separate.

## Question, frozen states and unchanged physics

Why did fresh native backward-Euler Newton residuals stall above the accepted
criterion? Distinguish identity/state leakage, deterministic RHS assembly error,
finite-difference sensitivity and linear algebra error. This experiment supplies
diagnostics, not a converged trajectory, physical accuracy bound or selected solver.

Use exactly three states, fixed before new evaluations:

1. The original development initial state, unchanged accepted input NPZ SHA256
   `b02862988b83b7412a8a53d40868adf5f6b04cf7eca7798b7bebf6789fc31da6`.
2. The original validation initial state, unchanged input NPZ SHA256
   `bc70b3c75bdb8a5046a310de3a13b125a991fcaf165f70631ce79bf5875a9bb9`.
3. Development L0 Jacobian-baseline record **300**, the last chronological
   pre-update iterate at the smallest attempted step. Choose it by position,
   without minimizing a residual. Source stream SHA256
   `fb424cfc1f60258878df3244c8cf283c7d6927fa89b0c6bee9f901387b104775`;
   164 little-endian binary64 values per record; selected record SHA256
   `074440ec3e7d73729c0879f8109c2819e2220df97ad3680de98e1bc5fcfaa217`.
   Its Y bytes SHA256 is
   `5d571931e428b4ede04e61c7d3b8bb0d940d3fabb35da0e8363e1cc5b4ce4c39`.
   Time and frozen BE h are 1.953125e-7 s. T9/rho must equal the original
   interpolant at that time, bit for bit as saved. The old BE state is the
   unchanged development Y0. Do not use the inconsistent exhaustion snapshot.

The source raw archive SHA256 is
`75a5949e8fb74cfe386a415e40c7ecc2e284042d96614b2179a3bf77bb617ec2`.
A private annex binds the derived inputs, species and source records, SHA256
`dbb954afac144d9305a87e483c0c08833a8cdf2487d390f2d6532e5e72a814eb`.
No original input is regenerated or
modified, no split/history/case replacement occurs, and no final-test data are used.
All 160 physical Y and signed native dY/dt units, T9/rho forcing, composition-derived
Ye=Q/B, network/rate/EOS data, flags and domain/branch rules remain D-036.
Heating/NSE/active neutrino evaluation and learned models remain excluded.

## Producer and implementation

Use the same hash-bound original closure, modules/compiler/libraries/flags and
one-rank/thread host configuration as D-036. Stage a new private source/build,
retain originals, exact patches and all source/environment/executable identities.
The numerical adapter may add diagnostic-only increment factors and observational
probe export; its default factor remains one. Do not modify physical RHS arithmetic.
A narrow driver command performs the fixed diagnostics using the existing native
initialization. This is no Python RHS callback or new solver framework.

Repair failure snapshots to bind physical workspace to its actual last evaluated
Y/time/T9/rho and EOS outputs across native retry cleanup. Preserve the old binary
layout and document old artifact limitations; identify the distinct Jacobian
baseline associated with any retained matrix/LU. Test this via a synthetic retry
cleanup fixture before physical calls. Preserve both rejected arguments and last
physical workspace when they differ; no snapshot is silently relabeled as a root.

## Stages and measured quantities

**A — Identity/repeatability.** Six processes: for each state, three identical
fresh evaluations in one process, then one evaluation in a fresh process (12 F
calls). Complete all six before stage C. Compare all repeated F/coefficient/b
bits, echoed inputs, moments, branches and IEEE modes. Both original initial-state
F controls must match D-019 component bits exactly. A mismatch stops all subsequent
physical work. Exact repeatability does not rule out deterministic roundoff.

**B — Conditional arithmetic, offline.** Export static participant/multiplicity/
mu/la/le maps and ordered species, plus Y, F, csect and b after the baseline calls.
Verify mappings using the existing independent Phase 1 arithmetic routines.
Use exact binary-rational arithmetic to measure b minus a*csect and native F minus
the exact abundance polynomial conditional on the exported binary64 b. Retain
signed/absolute term totals, zero/net cancellation masks, contributors and derived
multiplication/summation/FTZ/DAZ bounds. This quantifies combined abundance-product
and summation discrepancy; reconstructed terms cannot empirically separate those
two rounding sources. It does not verify EOS/rates or create new trajectory truth.
At state 3, compare h times the measured discrepancy to unchanged D-036 nonlinear
weights; recompute serialized BE residuals exactly to expose residual-evaluation
rounding separately. No new tolerance or physical error floor is inferred.

**C — Frozen derivative diagnostics.** Three processes, one per state. Compute
full fresh-F Jacobians at exactly `[0.1,1,10,100]` times the original production
column delta. Keep state scaling, representable-increment weights, central/forward/
upper-bound backward preference, eight halvings and domain/branch gates unchanged.
Hold time/T9/rho fixed while each probe recomputes Ye/EOS/weak/screening. Preserve
failed columns/matrices and continue other declared factors/states unless identity,
nonfinite computation or a shared input/build error requires a stop. No replacement
factor, extra halving or production factor selection follows from these outcomes.
Retain every executed probe Y/F, increments/refusals/branches, baseline/workspace
restores, complete matrices and counters. Export coefficient/b payload at baseline
and the frozen candidate only; exporting it at every probe is unnecessary here.

Independently evaluate three directions with the original nine multipliers and
D-036 agreement criterion. Direction 1 is s_i=max(abs(Y_i),1e-8/A_i). Replace the
impossible mixed-sign direction 2 **for these diagnostics only** with v_i=s_i on
one-based odd species and zero on even species; direction 3 remains the coordinate
of largest original initial X, ties by species order. Preserve the original
P2D-PROP-003 failure. A nonnegative direction removes the abundance-bound obstacle;
EOS/branch admissibility and derivative agreement are unproven. Keep central,
forward, backward order; retain all nine outcomes with no chosen new window/delta.
Compare each of the four Jv vectors to the same independent directional sweep,
using two adjacent admissible multipliers and unchanged componentwise threshold
`1e-7+1e-3*max(abs(A*Jv),abs(A*Dv))`. Report every pass/failure, not a selected factor.
Also compare the native fixed-coefficient monomial matrix against the exact
independent derivative of the exported fixed-b polynomial; it is not the full-F J.

Serialization/recomputation checks are separate from that scientific agreement
criterion. Let e be binary64 epsilon and Nmin the minimum normal binary64 value.
For a two-probe quotient with weights w1,w2 and terms
t1=w1*(F1-F0), t2=w2*(F2-F0), allow
`512*e*(abs(t1)+abs(t2))+32*Nmin*(abs(w1)+abs(w2)+1)` componentwise.
Require nonzero normal offsets, their difference/products and weights, and finite
differences/products/sums. Otherwise mark the arithmetic envelope unsupported.
The Nmin terms cover DAZ/FTZ losses amplified by the quotient weights; an
unamplified subnormal constant is insufficient. The relative term conservatively
covers the short nearest-rounding weight/subtraction/product/sum chains.
For Jv use `512*e*sum(abs(J_ij*v_j))+32*160*Nmin`; every nonzero fixed v must be
normal and at most one. For M use `512*e*(abs(J)+I/h)+32*Nmin`, and for the native
Newton RHS use `512*e*(abs((Yold-Y)/h)+abs(F))+32*Nmin*(1+1/h)`; h and its
reciprocal must be normal and finite. These operation-count/flush allowances
check saved arithmetic, not derivative adequacy or physical error. Exact-rational
conditional assembly, derivative and residual checks additionally retain their
own operand/count-derived bounds and unsupported masks.

**D — Frozen linear/Newton algebra.** Only at state 3, for every complete matrix
form M=I/h-J and the unchanged native right-hand side (Yold-Y)/h+F. Retain unfactored
M, RHS, LU/pivots/info and correction. Require native LAPACK info=0; report other
factors even if one fails. Independently evaluate exact linear residuals and scaled
normwise/componentwise backward errors. Also compare the alternate algebraic RHS
-(Y-Yold-h*F)/h offline. A small backward error does not qualify J or bound forward
error. One fresh F at the factor-one candidate Y+correction is permitted if the
existing domain gates pass. Do not clip/project it, iterate, reduce h, accept a
step or advance time. A refused candidate is reported, not replaced.

## Concrete execution envelope and stopping

Request one fresh diagnostic build, plus at most two fresh repair builds after a
build OR prephysical synthetic-preflight implementation failure. Retain every
attempt. Repairs must preserve this protocol/toolchain/physics; no automatic
postphysical rebuild or numerical rerun. Compiled synthetic prerequisites include
the original ten and the new retry-cleanup snapshot fixture; all must pass before
stage A. Project-local public Python tests use independent small arithmetic oracles.

Exactly six repeatability and three derivative processes are planned. No trajectory
process or clean-trajectory reproduction is authorized. Conservative fresh-F bounds:

| Work | Maximum calls |
| --- | ---: |
| A: 3+1 repeats per state | 12 |
| C: native setup baseline, once per state | 3 |
| C: 12 matrices, at most 2+160*9*3*2 calls each | 103704 |
| C: independent directions, 3*3*9*3*2 probes | 486 |
| C: directional baseline restores | 3 |
| D: one factor-one candidate | 1 |
| Total | 104209 |

Invalid probes refused before the kernel reduce actual counts. Nominal first-
admissible-stencil work is about 4045 calls. No additional monomial-Jacobian
physical evaluations are needed: use each current baseline coefficient workspace.
Native scope counters and raw streams establish actual usage, not an inferred
pass from an exit flag. No infrastructure restart or completed-process repetition
is included; preserve interrupted outputs and request a concrete amendment if needed.

Refuse nonfinite dynamics/matrices, identity/domain/coverage violations, unsupported
arithmetic or missing required outputs. A domain/branch-refused probe is an explicit
failed sample, not authorization to repair inputs. Snapshot/executable/input identity
failures stop the campaign. Unattempted and interrupted work remains visible.
Do not discard failures or extend this envelope to make a diagnostic pass.

## Artifacts, reproduction and decision

Retain immutable source/patch/build/table/environment/executable/library identities,
annex/inputs, every planned process/sample and status, matrices/probes/F/branches,
exact-arithmetic derived arrays and undefined masks, costs and exceptions locally.
Use versioned numeric streams and JSON/NPZ; object/pickle arrays are forbidden.
Fresh-process reload verifies dtype/shape/array bytes and recomputes all derived
metrics exactly from raw outputs. Stage A explicitly tests fresh native-process
reproduction at unchanged states; it is not clean trajectory reproduction.

Diagnostic software passes only if identity, required output completeness and
recomputation checks pass and every fixed sample is accounted for. Derivative or
linear/numerical failures are scientific outcomes, not successful reference
qualification. Stop after the diagnostic report and independent assessment. Prepare
a separate accepted trajectory protocol/execution decision after the evidence;
even an improved candidate residual grants no trajectory retry, changed nonlinear
controls, model rollout, reference acceptance, merge or Phase 2E authority.

Estimates, not caps: roughly 14 s build from the measured replacement build;
seconds to a few minutes native work plus setup/persistence; <1 GiB memory;
roughly 10–300 MiB probe records plus source/table/build outputs. Worst-case extra
refused probes and diagnostics increase storage/runtime. Measure actual CPU/wall,
loading/setup/persistence, RSS and storage; no matched-accuracy speedup claim.

Numerical basis: original `yderiv` forms b=a*csect, sequential signed abundance
products/class sums, then four class sums. The [SUNDIALS difference-quotient discussion](https://sundials.readthedocs.io/en/v6.1.0/kinsol/Mathematics_link.html#difference-quotient-jacobian-approximations)
uses state scales and an optional function-error parameter; it motivates examining
increment sensitivity, not adopting its solver/defaults. [LAPACK DGET02](https://github.com/Reference-LAPACK/lapack/blob/master/TESTING/LIN/dget02.f)
checks scaled linear residuals. The existing [original-paper trace](GROUNDING.md)
continues to separate representation, one vector source, integration and scientific
evaluation; this diagnostic changes none of those scientific prediction targets.
