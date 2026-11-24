# Phase 2D correction-controlled trajectories — D-040 proposal v1

**PROPOSED, NOT ACCEPTED. No new producer build or physical evaluation is
authorized.** Prepared 2026-11-24 for [#44](https://github.com/jaharris87/crucible-astro/issues/44)
and draft [PR #51](https://github.com/jaharris87/crucible-astro/pull/51), within the
existing [Phase 2 sequence](../../docs/PHASE_2_LAUNCH.md). Fresh independent
protocol review, explicit human acceptance of BOTH the numerical protocol and
the execution envelope, and ordinary exact-candidate implementation review must
precede execution. Reference acceptance, merge and Phase 2E remain separate.

## Question and deliberate change

Can correction-controlled adapted native backward Euler resolve and reproduce
the two already fixed 10 ms forced IVPs using the D-039 numerical RHS
**`native-XNet-b64-productsum113-b64-v1`**? The proposed reference claim is numerical
resolution on these inputs, requested grids and settings, not physical accuracy,
hydrodynamic reproduction, an independent exact solution or learned-model skill.

The [D-039 report](../../docs/reports/2026-11-23-phase2d-assembly.md) establishes
passing conditional arithmetic and derivative checks but failed first-step
qualification. Its final development updates round away when added to binary64
Y. A large unpreconditioned backward-Euler residual can accompany a very small
state correction in a stiff system: locally, `delta = -(I-h*J)^(-1)*R` where
`R=Y-Yold-h*F`. This relation motivates testing correction size; it is not an
error bound when J is approximate or the nonlinear map is nonsmooth.

This proposal **replaces D-036's raw residual acceptance gate**, explicitly;
it cannot make D-036/D-039 pass retrospectively. The original native BE tests
relative Newton corrections (`xnet_integrate_be.f90`, original digest below,
lines 266–330); the current adapter instead tests raw post-update residuals
(`native_adapter.f90` at `245ed95`, lines 764–803). Neither is adopted unchanged.
[CVODE 7.8 mathematical considerations, §3.2.1.1](https://sundials.readthedocs.io/en/v7.8.0/cvode/Mathematics_link.html#nonlinear-solve)
provides a relevant distinction between nonlinear state-error estimates and
integration error. Our two-correction test below is **not CVODE's contraction-rate
test**, and this driver has no local truncation-error controller. The prescribed
mesh and measured global refinement remain indispensable.

Alternative: retain the strict raw-residual requirement and develop genuinely
higher-precision state/update/source semantics. That changes more contracts;
simply storing a compensated increment while rounding every RHS input to
binary64 would not convey sub-ULP state information to the reaction products.
No such alternative is included here. No solver benchmark matrix is proposed.

## Fixed physical problem, inputs and producer

The [D-036 protocol](PROTOCOL.md), SHA256
`966fbff8d2322ae8e6666063f35c1b87cced7d5ccbaf663ccae362613f98fdad`,
continues to define the initial-state selection, original inputs, forcing,
requested outputs, domain, physics, meshes, global metrics and reproduction
allowances **except for the explicit replacements in this document**. The
[D-039 protocol](ASSEMBLY_QUALIFICATION_PROTOCOL.md), SHA256
`ff5515f04ecfdb9cb75f284882dc88d5beef30a25d1a4a8b9e9a18ba741abf02`,
defines the distinct RHS assembly; that source identity and arithmetic contract
are retained. Neither prior execution allowance is renewed by reference.

- Exactly the original one train/development and one validation history, selected
  by numeric canonical history order and earliest consecutive accepted block
  spanning 10 ms, before trajectory outcomes. No new split or substitute case.
- Original private annex SHA256
  `697049acca510794eda3149a2d88a11477f49e4724519cb3ba4fef22e7cdb3b1`;
  input NPZs development
  `b02862988b83b7412a8a53d40868adf5f6b04cf7eca7798b7bebf6789fc31da6`
  and validation
  `bc70b3c75bdb8a5046a310de3a13b125a991fcaf165f70631ce79bf5875a9bb9`.
  The local annex retains exact source records/t0, species and initial Y bits.
- All 160 ordered physical molar Y in binary64; F is signed Y/s. Define
  `tau=source_time-source_t0` in seconds, horizon `[0,0.010]`. No logarithmic
  state transformation, floor, normalization or accepted-state repair.
- Prescribed T9 in GK and rho in g/cm³, from the original saved knots through
  the first knot at/after 10 ms. Piecewise linear in each physical quantity:
  `q=qL+((tau-tL)/(tR-tL))*(qR-qL)`. Exact knots return saved bits. Reject
  nonfinite/nonincreasing knots, missing coverage and extrapolation. Requested
  outputs are the original exact binary64 millisecond grid union interior knots:
  12 development and 16 validation states, including both endpoints.
- All F/probes/accepted/output states obey D-036: finite `0<=Y_i<=1`, positive
  B=`sum(A*Y)` and total Y, Ye=`sum(Z*Y)/B > 0`, positive rho,
  `0.01<=T9<=100`, `1<=log10(rho*Ye)<11`, and actual initialized Helmholtz
  table bounds before EOS evaluation. Hold external forcing fixed for state
  derivatives; recompute composition-derived Ye and coefficient dependencies.
- Keep `iweak0=1,iscrn=1,iheat=0,ineutrino=1` with asserted `nnnu=0`, 160 species,
  176 FFN entries and reaction counts `[683,1345,16,4]`; retain native weak,
  screening, table and rate cutoffs. No heating, active neutrino or NSE evaluation.
  Historical later Y is context only, not trajectory truth.

Start staged adaptations from physical source
`245ed9525ee9877653beab80eaf91bdd5493800c`; retain the exact diff and new committed
source/tree. Original producer HEAD `200b024cd06abdf4edaee489d6229edaa9ae30b3`
plus per-file bindings defines the inputs, not HEAD alone. Keep the original
preparation `a51f43bd5e053159457d61f45a5672e1308a6199158730f4fed269d517ff2146`,
[rate/network/EOS bindings](../rhs_reference/bindings.json), and original BE
SHA256 `4fddd97ecb1e08bfdf29dec948517cb90e2b0353ddcc765a6858dd0cd5818852`
and dense-module SHA256
`5de0d789e2a055fe6a409287cd64124832a1645a5b1edd9ad05f0ba806417d38`.
All original projects/inputs and historical outputs remain read-only.

Use the same Intel 2025.3 / PrgEnv-intel 8.7.0 / Cray parallel HDF5 1.14.3.9
toolchain, sequential MKL, one rank/thread, original recorded preprocessing and
`-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`. Only the
113-bit assembly module retains additional `-fp-model strict`. Reject changed
precision/FP behavior; retain all compiler/module/environment/runtime-library,
source/patch/configuration/table/build/executable identities. Two isolated fresh
build directories, no old objects or executable reuse. Freeze implementation
before the first physical call; Build B uses the same source as Build A.

The RHS retains native binary64 coefficients and rates/EOS, promotes coefficients
and Y before native-order products and ordered class sums in exactly 113
significand bits, then rounds F once to binary64. Original F is also retained.
This is distinct from D-019; frozen-MLP compatibility is still unestablished.
Original data, memberships, overlays, weights/scalers and scores are unchanged.

## Local nonlinear and Jacobian contract

Keep fresh full-F finite-difference J at every Newton iteration, native dense
`I/h-J`, LU/back-substitution with every `info==0`, 30 Newton iterations per
attempt and ten native attempts per step call, halving h on nonconvergence.
All D-036 finite-difference scales, representable increments, central/second-order
one-sided stencils, eight possible halvings, branch checks and fresh restoration
remain unchanged. No supplied analytic or learned Jacobian is introduced.

Let `delta[k]` be the **raw computed Newton correction before adding to Y or
projecting**, and Y[k] the resulting post-projection iterate. For each iteration,
after a successful fresh F at Y[k], form

```
W_i[k] = aC + rC*max(|A_i*Yold_i|, |A_i*Y[k]_i|)
Ccurrent[k]  = max_i |A_i*delta[k]_i|   / W_i[k]
Cprevious[k] = max_i |A_i*delta[k-1]_i| / W_i[k]
```

Accept only at k>=2 when **both Ccurrent and Cprevious <=1**, under the SAME
current weights, with every domain/finite/LU/projection/balance gate passing.
Reset correction history at every retry. Never test only the rounded applied
change `Y[k]-Y[k-1]`, which could be zero despite a large raw correction. Record
both corrections, actual applied updates, norms, correction ratios and bitwise
stagnation. A noncontracting but sufficiently small pair may pass; this is an
estimated state-convergence policy, not proof of a nearby exact BE root.

| Control | aC | rC |
| --- | ---: | ---: |
| Standard | 1e-15 | 1e-13 |
| Tight | 1e-16 | 1e-14 |

These numerical state-correction scales are deliberately well below the global
nonlinear-sensitivity allowances below. They are not nuclear physical-error
floors. A-weighting is retained solely for continuity with the accepted numerical
inventory comparisons; Y remains the kinetics coordinate. No new claim that
mass-fraction rates are the primary physical target follows.

Retain every component of `R=Y[k]-Yold-h*F(Y[k])`, its A-weighted L1, and its
original D-036 normalized infinity norm using fixed `(aN,rN)=(1e-13,1e-11)`
for ALL runs. Raw R must be finite, but `norm(R)<=1` is **no longer an acceptance
criterion**. Do not reuse correction weights and call them the old residual
weights. Report large residuals alongside corrections and global differences.

Keep existing negative-Newton-iterate-to-zero projection, disclosed per species;
no positive abundance cutoff (`ymin=0`). Final-iteration projection A-weighted
L1 <=1e-12 per accepted step and cumulative <=1e-10 per run. Earlier iteration
projections are fully retained; the raw correction before projection is tested,
so a tiny projected/applied change cannot manufacture convergence. Each accepted
state additionally requires `|B-B0|<=1e-10*max(1,|B0|)` against actual nonunit B0.
Do not impose constant charge or Ye.

Per build verify six frozen states: both initials and each case's L3-standard
requested states at 5 ms and 10 ms. Use a separate fresh diagnostic process per
state, the production full-F J and the D-039 directional implementation:
scaled all-ones, **nonnegative odd-species support**, and the coordinate with
largest initial A*Y (numeric order breaks ties). Scale `max(|Y_i|,1e-8/A_i)`;
nine multipliers `[1e-2,3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6]`, all attempts
retained. Require two adjacent admissible estimates mutually agreeing and
agreeing with Jv componentwise within
`1e-7+1e-3*max(|A_i*Jv_i|,|A_i*Dv_i|)`. No stable window is a failure; no new
epsilon/direction is selected after outcomes. The original D-036 mixed-sign
direction-two defect is not reintroduced. No repeated D-039 factor sweep.

## Global evidence and conditional run sequence

Keep D-036 meshes L0–L3: union exact binary64 `j*1e-4,j=0..100`, outputs and
forcing knots; subdivide every interval into `2^level` pieces. Nominal maxima
are 100, 50, 25 and 12.5 microseconds. Native reductions may shorten steps;
land on all requested mesh targets/outputs/knots and exactly 10 ms. Reject
nonpositive/unrepresentable progress. No local integration-error estimate is
added; solver success alone never qualifies a trajectory.

Per build, each case has **six** named runs: L0 standard, L0 tight, L1 standard,
L2 standard, L3 standard and L3 tight. Thus **24 trajectories** across two builds.
L0 tight is a new full-horizon pilot; it is not substituted for finest tight.

1. Build A and compiled prerequisites; two initial controls below. Run both L0
   standards, then both L0 tights only if both standards complete all gates.
2. Pilot joint gate: all four reach 10 ms with complete outputs and constraints;
   standard/tight differences on requested outputs satisfy max-time
   `||A*dY||inf<=1e-9` and `||A*dY||1<=1e-8` for BOTH cases. Failure stops
   dependent stages, not a request to lower h or change controls automatically.
3. Run A's two L1 standards, then two L2 standards, then two L3 standards, then
   two L3 tights. At an ordinary numerical failure complete the other case at
   that stage, then stop dependent stages. Shared identity/corruption failures
   stop immediately. Every remaining run is explicitly conditionally unattempted.
4. Require four-level mesh convergence and finest nonlinear separation below;
   then execute six-state Jacobian diagnostics and artifact verification.
5. Only if ALL A requirements pass, perform fresh Build B and its twelve matching
   runs under the same stage gates, six diagnostics and independent numerical
   verification. Require the clean-reproduction comparisons below as well.

All levels compare on the same original requested grids. Retain signed dY,
`dX=A*dY`, component RMS/max, timewise vector L1/L2/Linf, pooled RMS, maximum
locations, endpoints and B/Q/Ye plus n/p/alpha/A>=12/A>=48 inventories (last two
overlap). Relative differences are supplementary with explicit zero handling.
Required passes, unchanged from D-036:

- L2/L3 max-time `||dX||inf<=1e-6` and `||dX||1<=1e-5`.
- For each norm, L1/L2 and L2/L3 maxima <=0.75 of the preceding pair's maximum,
  unless that preceding maximum is <=1e-10. At least one strict accepted-step
  refinement per successive mesh pair; identical accepted meshes cannot pass.
- L3 standard/tight max-time `||dX||inf<=1e-9` and `||dX||1<=1e-8`.
- Finite/domain/positivity/projection/B gates, full horizon and exact complete
  requested outputs for EVERY required run; all six diagnostic states pass.
- B versus A: identical requested grids/masks/status/membership and
  `|A_i*(Y_B-Y_A)|<=1e-12+1e-10*|A_i*Y_A|` at every requested output of every
  matched run, same allowance for derived inventories/moments. Both builds
  independently pass original criteria. Report mesh/counter differences too.

These are fixed numerical resolution targets, not D-024 profiles, formal order,
physical-accuracy guarantees or independent-solver truth. No failed case is
excluded. Refinement holds sparse forcing and physical inputs fixed; it measures
neither interpolation sensitivity nor rate/EOS uncertainty.

## Concrete producer authority requested

The whole conditional sequence above is one decision, with no permission per
command or successful stage. It includes only:

- Two fresh planned builds plus at most TWO replacement builds TOTAL following
  compilation or prephysical synthetic/preflight implementation failures. This
  explicitly includes a successful build stopped by preflight. Preserve each
  attempt/diff; same physics/protocol/toolchain. No source change/rebuild after
  physical evaluation in that build; a scientific or postphysical code defect
  stops for a new decision. Build B must use A's frozen physical source.
- Per build, all sixteen D-039 compiled prerequisites plus focused correction
  fixtures: independently solvable stiff BE at a residual-rounding floor;
  nonlinearity; retry/history reset; raw-versus-rounded correction; previous
  correction/current weights; projection and incomplete-horizon refusals.
  Public Python synthetic/oracle tests and offline reporting require no physical
  calls. Native compilation/fixtures are covered only after acceptance.
- Two fresh initial control processes per build (FOUR planned). Each evaluates
  original and variant F together once at its fixed initial input, requiring
  original D-019 and retained D-039 variant bits, coefficients and moments to
  match. Reuse D-039 exact-arithmetic validation only where source/flags/semantics
  are identical; independently verify retained initial and diagnostic workspaces
  with its rational oracle, without new calls. Any identity mismatch stops.
- The 24 trajectories and TWELVE six-state diagnostic processes; all fresh RHS,
  rates/EOS/weak/screening, full-F finite differences, post-F, LU/Newton and native
  retries required by those named processes. No exploratory extra physical checks.
- At most ONE infrastructure-interrupted process restart per build, from its
  identical original inputs in a new process/attempt directory. Retain partial
  outputs/reason, verify completed artifacts and do not repeat completed processes.
  No numerical-failure restart, source repair after physical calls, new cases,
  changed forcing/criteria, extra levels or heating/NSE evaluation is covered.

There are 40 planned physical processes (4 controls +24 trajectories +12
diagnostics), conditionally fewer, plus at most two infrastructure restarts.
Native ten-attempt/30-iteration limits are per step call, not bounds on total
accepted steps. Let N be the actual trajectory Newton-iteration count. With
`Q=2+160*9*3*2=8642`, each Newton iteration uses at most Q+1 guarded fresh
requests. The twelve diagnostic processes contribute at most
`12*(1+Q+3*9*3*2+1)=105672` requests, reusing one production J per state;
do not wrap the directional sweep in a second unnecessary full-J evaluation.
The 24 requested meshes contain 9,888 intervals (101 development and 105
validation L0 intervals, multiplied by `2*(1+1+2+4+8+8)`).
Report actual accepted/attempted steps, N and all counters, including
refused requests; do not imply requested mesh intervals bound native substeps.
The prescribed processes/horizons and algorithm define authority, not a new
D-013 resource cap. Retain every failure, missing output, exception, refusal,
interruption and conditional skip; failure leaves 2D incomplete.

## Retention, reproduction and resource estimates

Use a predeclared compact trajectory mode, distinct from D-039's full forensic
first-step mode. Preserve all raw outputs actually written, separately from
versioned derived JSON and numeric NPZ (`allow_pickle=False`):

- Every initial/accepted/output state, time, T9/rho, original and variant post-F,
  moments, inventories, constraints, step/attempt/call IDs and complete counters.
- EVERY Newton iteration's old/pre/unprojected/post Y, raw current/previous delta,
  applied update, correction weights/norms, raw residual and original residual
  norms, projection vector, statuses and matrix/call identity; all failed attempts.
- Every finite-difference stencil/increment/reduction/refusal and branch transition
  with role/call IDs; inputs are reconstructible from baseline plus perturbation.
  Ordinary successful-step probe F and dense J/LU matrices are not retained.
- Complete F/probe/coefficient/113-bit workspaces and four-phase J/M/LU/pivots/RHS
  for each trajectory's FIRST step (all its attempts), all fixed diagnostic
  processes, and the last failing evaluation/iteration. Buffer the current
  workspace so failure capture needs no new physical evaluation. Rejected input,
  last evaluated workspace and matrix baseline remain distinct. If interrupted,
  retain the last flushed record and report unavailable in-flight diagnostics.

Retention is chosen BEFORE outcomes; do not generate then discard forensic
streams or overwrite accepted historical records. Exact native/persistence schemas
and reconstruction checks belong to the reviewed implementation. Keep this small:
ordinary functions/records/runners, no solver platform or general registry.

Fresh-process offline reload verifies exact dtype/shape/array bytes, raw/derived
correspondence and recomputation of every metric. Build B supplies clean numerical
reproduction from identical hash-bound inputs/source/environment in new directories;
serialization identity, numerical equivalence and convergence are separate claims.
Retain raw archives/configurations/diffs/build/executable/runtime identities and
all conditional failure accounting. Measure setup/load, integration, persistence,
CPU/wall, RSS/storage and unavailable measurement scopes. Private arrays/paths
stay local; public synthetic tests have no private-data CI dependency.

Planning estimates, NOT caps or reservations: fresh build roughly 20 s wall,
0.1 GiB RSS; integration memory <2 GiB. At roughly 3–6 Newton iterations per
requested interval, millions of fresh calls and approximately 6–15 CPU-hours
are plausible, with substantial uncertainty and potentially much more if native
reductions accumulate. Compact raw output is estimated at a few GiB, potentially
tens of GiB with extensive retries/diagnostics; full D-039 logging throughout
could exceed 200 GiB and is not proposed. No performance promise or speedup
claim follows. Report measured costs and failures.

Predefine later held-out generation with the identical source/forcing/selection/
mesh/acceptance procedure after a separately frozen evaluation protocol and
explicit release; do not generate or inspect final-test outcomes now. Finish with
a concise report/guide, exact-candidate review, human acceptance of the named
reference claim, human merge decision and merged-result verification. Keep #44,
the 2D goal and milestone #3 open until their respective exits. Stop before 2E.
