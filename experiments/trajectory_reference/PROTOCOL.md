# Phase 2D proposed native-XNet trajectory protocol v2

**PROPOSED, NOT ACCEPTED; no producer build or physical evaluation authorized.**
Governing [issue #44](https://github.com/jaharris87/crucible-astro/issues/44),
[existing Phase 2 sequence](../../docs/PHASE_2_LAUNCH.md). Prepared 2026-11-20.
This protocol and its fixed private input annex require a separate fresh-context
Sol High review and explicit human acceptance of both science and execution.
Neither acceptance authorizes a merge or Phase 2E.

## Question, reference claim and limits

Can the pinned D-019 **fresh** native kinetics system, `dY/dtau = F(Y,T9(tau),rho(tau))`,
be reproduced and numerically resolved on two specified 10 ms forced initial-value
problems? State is all 160 ordered physical molar Y, binary64; rates are signed Y/s.
Time is seconds and selects prescribed conditions, not a new predictive feature.
The proposed claim is finite numerical resolution on the named intervals/grids,
under this exact source, forcing, physics and method. It is not a physical-error
bound, reconstruction of the hydrodynamic simulation, full-history reference,
independent solver validation, or learned-model accuracy/speedup result.

Saved Y initializes each problem unchanged. Later historical Y and stored RHS
are contextual only; neither is trajectory truth. Saved binary T9/rho knots
**define new prescribed forcing**. Complete original hydro forcing is not retained
locally for these cases. Interpolating sparse outputs cannot recover unresolved
forcing. Solver refinement holds that interpolant fixed; no interpolation-sensitivity
or rate/EOS uncertainty study is included. No additional forcing is required by
this exact heating-off, zero-active-neutrino RHS. Any contrary runtime discovery
stops execution; no neutrino/radius/history-Ye closure is invented for the MLP.

Keep representation, one vector source, integration and evaluation distinct.
The original-paper/source trace is in [GROUNDING](GROUNDING.md). The frozen 2B
MLP/scalers, negative D-024 results and final-test seal stay unchanged. No learned
integration, fitting, preprocessing change, pointwise rescoring or energy target.

## Fixed cases and immutable inputs

Use exactly **one development/train and one validation history**, from the accepted
D-025 grouped memberships. For each role independently, visit histories by numeric
canonical particle ID; partition accepted records into maximal consecutive raw-ordinal
blocks; take the earliest block spanning at least 0.010 source seconds in the first
qualifying history. Initialize at its first record. This rule uses membership and
time coverage before any new trajectory outcome. It avoids crossing a historical
membership gap and creates no new split. Two cases establish this small contract,
not representative CCSN coverage. No replacement after failure.

Exact private record/group identities, source t0, 160 Y bytes, ordered `(Z,A)`, raw
parent digests, all forcing knots and exact requested binary64 grids are frozen in
`proposal-inputs.json`, SHA256
`697049acca510794eda3149a2d88a11477f49e4724519cb3ba4fef22e7cdb3b1`.
The custodian-local annex and numeric inputs are reviewed with this protocol;
they are not public redistributable data. Input NPZ SHA256:

| Case | Input NPZ SHA256 | Requested outputs |
| --- | --- | ---: |
| Development | `b02862988b83b7412a8a53d40868adf5f6b04cf7eca7798b7bebf6789fc31da6` | 12 |
| Validation | `bc70b3c75bdb8a5046a310de3a13b125a991fcaf165f70631ce79bf5875a9bb9` | 16 |

Preparation used the checked loader with `state_training` on train/validation;
this selects qualified **initial states**, not existing rollout qualification.
No positive rollout eligibility is added to the original data. The loader checked
all consumed identities and structural memberships; no final-test outcomes were used.
Preserve overlay `e1bcd8b3cceabf252c1307ad008cdbc4a1da1cd556e84bf923d742ce3cf2ce0c`,
membership `f5a99420101fb7b73e94d481d64aab2c279a5f04915d76f20b84edd2b98bdd3a`,
and payload `f4171d1600586f28b4a514071c8c029d1a84c7634f9f11ae8a6b4b25c6a0c980`.
Derived 2D artifacts remain separate from these and all original reference/model evidence.

## State, forcing, output and domain contract

Set `tau = source_time - source_t0`; source seconds are the retained first-column
producer clock, not silently relabeled post-bounce time. Integrate `[0,0.010]`.
Use the saved T9 in GK and rho in g/cm^3, through the first knot at/after 10 ms.
Knots outside the requested horizon only bracket interpolation; they are not extra
requested evolution. Output times are the exact annex arrays: binary64 `j*0.001`,
`j=0..10`, union all strictly interior forcing knots, sorted and unique.

At an exactly equal knot, return its stored condition bits. Otherwise locate the
unique adjacent knots and compute, separately for T9 and rho,
`q = q_left + ((tau-t_left)/(t_right-t_left))*(q_right-q_left)` in binary64,
without contraction/reassociation beyond the pinned compiler's recorded semantics.
Reject any nonfinite/non-increasing knots, nonpositive conditions, missing full
coverage or query outside the closed forcing interval. No endpoint hold/extrapolation.
Use a separately staged narrow adaptation of native `t9rhofind` to enforce these
semantics during both normal steps and retries; preserve the original source.

Every RHS/Jacobian probe and accepted/output state requires finite Y, `0<=Y_i<=1`,
positive finite `B=sum(A*Y)` and total abundance, `Ye=sum(Z*Y)/B > 0`, positive rho,
`0.01<=T9<=100`, and `1<=log10(rho*Ye)<11`. Also require the pinned Helmholtz
rho*Ye/temperature table coverage, checking its initialized actual grid endpoints
before any EOS call; no table-index clamping is accepted as coverage. These are
numerical/table-domain gates, not a learned-domain detector. Evaluate moments with
the pinned native convention; retain independently recomputed moments too.
Domain failures, including a trial/probe failure, are explicit. No normalization,
clipping of inputs, imposed constant charge/Ye, extrapolation or NSE fallback.

## Source, physics, build and deliberate numerical adaptations

The original producer checkout identifies HEAD `200b024cd06abdf4edaee489d6229edaa9ae30b3`
plus retained local changes; **file digests, not that Git SHA alone, define D-019**.
Retain all entries in [bindings.json](../rhs_reference/bindings.json), including
network/rate/mass/weak inputs, macros, Helmholtz source/table and their hashes.
The original primary preparation manifest is
`a51f43bd5e053159457d61f45a5672e1308a6199158730f4fed269d517ff2146`.
Add these hash-bound native numerical files:

| File | Original SHA256 |
| --- | --- |
| `xnet_integrate_be.f90` | `4fddd97ecb1e08bfdf29dec948517cb90e2b0353ddcc765a6858dd0cd5818852` |
| `xnet_jacobian_dense.f90` | `5de0d789e2a055fe6a409287cd64124832a1645a5b1edd9ad05f0ba806417d38` |

Keep `iweak0=1`, `iscrn=1`, `iheat=0`, `ineutrino=1` with **asserted nnnu=0**,
160 species, 176 FFN entries and reaction counts `[683,1345,16,4]`.
Retain native weak switching, strong cutoff `t9min=0.01`, FFN log-rate cutoff -30,
screening and other coefficient thresholds exactly. No NSE module/transition,
self-heating, normalization, network/rate or EOS-equation change. Record actual
weak flags, FFN cells and detectable coefficient threshold crossings. Heating/energy
output is unavailable for this claim, not zero physical heating.

Use a small standalone original Fortran driver and the pinned kernel closure,
plus adapted BE/dense modules and a small original numerical adapter. Do not link
production `postp`, abundance initialization, `evolve`, BDF, NSE or output modules.
Original BE freezes composition-dependent coefficients within a step, its dense
matrix omits their Y dependence, and it clips negative Newton iterates. Therefore
this is an **explicitly adapted numerical path**, not unchanged native BE:

1. Refresh `cross_sect -> yderiv` on every nonlinear iterate (including constant
   forcing). The physical RHS code and all its inputs remain unchanged.
2. Replace the monomial-only matrix with a numerical Jacobian of the **entire fresh
   F**, recomputing composition-derived Ye/EOS/weak/screening for each probe while
   holding time/T9/rho fixed. Use native dense `I/h-J`, LU and back-substitution;
   require every LAPACK `info==0`, otherwise fail the attempt.
3. Replace the native relative-update/mass-only stopping test with the fresh
   post-update BE residual test below. Use `ijac=1`, at most 30 Newton iterations,
   native ten step attempts with `tdel_maxmult=2`; record every reduction/iteration.
4. Set `ymin=0`: positive trace abundances are never dropped. Preserve and record
   every existing negative-iterate-to-zero correction, including species, pre/post
   values, signed and A-weighted magnitude. This is disclosed internal projection,
   not claimed projection-free integration. It cannot substitute for the residual
   test. No added global renormalization or accepted-state repair.

Stage copies separately; retain the exact transformation script, source diff,
original/resulting per-file hashes, driver/configuration/CRUCIBLE commit and tree
before build. No reference tree is patched in place. Use the D-019 Intel 2025.3 /
PrgEnv-intel 8.7.0 / Cray parallel HDF5 1.14.3.9 CPU toolchain and
`-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`, EOS preprocessing,
sequential MKL. Add dense module -> original numerical adapter -> adapted BE ->
driver in dependency order to the [existing build recipe](../rhs_reference/build.sh).
One MPI rank, active zone and thread. Record wrapper expansion, compiler/library/
module/environment/CPU identities, executable hash and loaded-library hashes.
No old objects, executable reuse, alternate compiler or silent build fallback.
Read-only startup confirmed the named modules are visible; no build has run.

## Numerical controls and Jacobian verification

This is backward Euler in physical Y. Local nonlinear controls are not a global
trajectory-error estimate. At every candidate accepted step, recompute fresh F
at the **post-update, post-projection** Y and require

`max_i |A_i*(Ynew_i-Yold_i-h*Fnew_i)| /
 (aN+rN*max(|A_i*Yold_i|,|A_i*Ynew_i|)) <= 1`,

with `aN=1e-13`, `rN=1e-11`; also retain every residual and `sum_i |A_i*r_i|`.
Reject nonfinite residuals. No cancellation through a signed baryon sum.
A tighter nonlinear-control run at the finest mesh uses `aN=1e-14,rN=1e-12`.
The final Newton correction's projection must have A-weighted L1 <=1e-12 per
accepted step and cumulative <=1e-10 per run. Earlier trial projections remain
fully reported; the accepted root residual tests their final equation effect.
Do not claim unchanged trajectories merely because projections are disclosed.

For numerical Jacobian column i, use `s_i=max(|Y_i|,1e-8/A_i)` and nominal
`delta_i=eps_binary64^(1/3)*s_i`, rounded to a nonzero representable increment.
Use central differences when both probes satisfy domain/branch gates; otherwise
second-order forward (or backward at the upper boundary) differences. Actual
representable increments enter the appropriate nonuniform finite-difference
weights. Reduce the increment at most eight times by two to find admissible
same-branch probes, else fail. Never perturb by normalizing or fixing Ye.
Retain increments, stencil/branch/refusal details and finite quotient checks.
Restore baseline Y and **reevaluate** fresh F after probes to restore all EOS/rate/
b/ydot workspaces. Numerical approximation includes all dependencies; no exact
analytic-Jacobian claim or learned-model Jacobian interface is introduced.

Verify independently implemented directional finite differences at each initial
state, plus finest-run requested midpoint/final state: six fixed states total.
Use three fixed directions in scaled coordinates: all ones; alternating signs
with negative entries made positive at zero Y; and the coordinate of largest
initial X (numeric species order breaks ties). Direction scale is s_i above.
Use the same domain predicates, with one-sided probes where necessary, and the
fixed multiplier sweep `[1e-2,3e-3,1e-3,3e-4,1e-4,3e-5,1e-5,3e-6,1e-6]`.
Retain every attempted multiplier. Require a window of two adjacent admissible
multipliers for which both successive directional estimates and production Jv
agree componentwise within
`1e-7 + 1e-3*max(|A_i*Jv_i|,|A_i*Dv_i|)` in mass_fraction/s.
A kink/branch crossing with no stable one-sided window fails; do not choose a new
production delta after outcomes. The absolute diagnostic scale corresponds to
1e-9 mass-fraction over 10 ms, below the requested trajectory resolution; it is
not a physical rate-error floor. Synthetic independent polynomial derivatives,
nonlinear stiff solution and boundary/refusal tests must pass first.

## Time refinement, observables and pass/fail

Freeze four mesh levels L0–L3. The base mesh is the union of binary64 `j*1e-4`,
`j=0..100`, requested outputs and interior forcing knots. Subdivide each base
interval uniformly into `2^level` pieces; retain all exact endpoints. Thus nominal
h maxima are `1e-4,5e-5,2.5e-5,1.25e-5 s`; no native timestep guess may enlarge them.
Native failed-step reductions may shorten a step. Record actual meshes/step ranges
so an inactive nominal refinement is visible. Land on every mesh/output/knot and
horizon, refusing no progress. No inference of formal order from these levels.
Ten milliseconds and these meshes define a proposed short-window experiment;
source inspection does not prove they resolve nuclear timescales.

Compare all levels on the same requested grids. For each pair retain signed
`dY`, `dX=A*dY`, per-species RMS/max, per-time vector L1/L2/Linf and pooled RMS,
maximum locations, endpoint errors and native B, Q, Ye. Also retain inventory in
neutrons, protons, alpha, A>=12 and A>=48 (overlap declared). Relative differences
are supplementary with explicit zero/undefined handling; no floor hides trace
components. D-024 profiles are not trajectory thresholds.

Required numerical resolution: L2/L3 `max_time ||dX||inf <=1e-6` and
`max_time ||dX||1 <=1e-5`. For both norms, require successive L1/L2 and L2/L3
maxima <=0.75 of the preceding pair's maximum, unless that preceding maximum
is already <=1e-10 (absolute roundoff/plateau allowance). If actual accepted
meshes are identical, explicitly identify this; the absolute differences alone
cannot establish an active time-refinement result. Require at least one strict
accepted-step refinement between each successive pair. No Richardson extrapolate
or formal order is claimed. These are proposed numerical inventory-resolution
targets, selected before outcomes; they are not approved nuclear physical floors.

Every run requires `max |B(t)-B0| <=1e-10*max(1,|B0|)` at every accepted and requested
state, and nonnegative Y after the disclosed Newton policy. Preserve the actual
nonunit B0. No constant-Q/Ye constraint: weak evolution may change charge. Require
all domain checks, finite diagnostics, residual/projection bounds, exactly complete
requested grids and achieved endpoint==requested endpoint. Status alone is insufficient.
Finest standard/tight nonlinear runs must differ by <=1e-9 in max vector Linf(dX)
and <=1e-8 in max vector L1(dX). This separates nonlinear from mesh error.

All required metrics must pass for **both cases**; no successful-case exclusions.
Passing a tighter run of one solver supplies refinement evidence, not an independent
solution or general nuclear validation. Failure means 2D stays incomplete and a
concrete revised protocol/refinement decision is needed, without automatic relaxation.

## Requested producer authority and failure accounting

Acceptance is requested for this exact scope, separately from merge approval:

- Two fresh isolated builds (campaign and clean reproduction), plus at most two
  failed-build repair attempts; same declared toolchain/physics and protocol.
  No build, including syntax-only compilation, occurs before acceptance.
- Two initial-state fresh RHS controls **per campaign, four planned controls total**, before that
  campaign's trajectories. Compare with the original D-019 labels at unchanged
  Y/T9/rho and same toolchain; require exact component bits. Mismatch stops that
  physical campaign; do not loosen identity tolerances or substitute inputs.
  An infrastructure restart reuses that campaign's completed, hash-verified control
  artifacts; if a control was interrupted without a complete result, its single
  identical-input restart is covered by the campaign restart allowance below.
  Retain both attempted control records; no completed control is reevaluated.
  This permits at most six control attempts across both campaigns, including
  up to one interrupted-control repeat per campaign under its shared restart rule.
- **Ten trajectories per campaign:** each of the two cases at four fixed mesh
  levels plus one finest-mesh tighter-nonlinear run. Repeat those ten once in the
  fresh build/environment. No learned model is loaded/evaluated.
- The six-state, three-direction, nine-multiplier Jacobian diagnostic sweep once
  in each campaign; its full-F evaluations, all numerical-Jacobian/RHS/coefficient/
  EOS/screening/weak evaluations required by the declared steps, residuals and
  native retries are covered. No NSE, neutrino-active or heating evaluation.
- At most one identical-protocol infrastructure-interruption restart per campaign,
  fresh process/attempt ID, retaining all partial outputs and reasons. Resume only
  uncompleted declared runs after verifying completed artifacts; no numerical-failure
  restart, easier case, tolerance change or additional level is authorized.

These are a bounded scientific execution envelope, not D-013 compute caps.
Native per-step ten attempts and 30 Newton iterations are algorithmic failure
rules. Refuse nonprogress/unrepresentable time, identity/configuration/domain
mismatch, nonfinite equations/matrix, invalid LU or failed residual/convergence.
A failed trajectory retains last accepted state, achieved horizon, raw diagnostics,
missing-output mask and trial failures; it never becomes full-horizon success.
Each other declared case/level remains a separate attempt, unless a shared setup/
identity failure stops the campaign. No exclusion or numerical retry is hidden.
All failures/interruptions, including setup/build failures before a run manifest,
are logged and retained. Implementation repairs must preserve this protocol;
material scientific/scope changes require a new decision.

## Artifacts, reproduction, tests and resources

Keep private inputs, histories, paths, trajectories and raw producer streams local.
Write new immutable run directories, streaming raw accepted-step records and trial/
projection/retry/status diagnostics; no overwrites. Derive versioned numeric NPZ
(`allow_pickle=False`) plus JSON manifests/metrics. Retain initial Y/species,
forcing/grids, all four levels and tighter runs, raw/derived hashes, sources/diffs,
build/executable/libraries, statuses/counters/messages, output-presence masks,
horizons, all component/vector/constraint/refinement/Jacobian metrics and failures.
Count RHS/coefficient/Jacobian/LU/linear-solve/Newton/retry work explicitly;
unavailable diagnostics get a reason rather than fabricated zero.

Fresh-process reload requires exact dtype/shape/byte identities for every array,
raw-to-derived correspondence and exact recomputation of same-environment metrics.
Clean reproduction uses the same immutable inputs, source/protocol and pinned
build/environment in a new directory/process. Require identical grids/masks/status/
case membership and `|A_i*(Yrepeat-Yfirst)| <=1e-12+1e-10*|A_i*Yfirst|` at every
accepted common requested output; apply the same allowance to derived inventory
observables and moments. Report accepted-mesh/counter differences separately.
All original numerical passes must also pass independently in the repeat. Byte
serialization identity, numerical reproduction and convergence are separate exits.
Cross-platform reproduction and a cold dependency download are not claimed.

Public synthetic tests cover forcing endpoints/interior/knots, no coverage or
extrapolation, nonfinite/domain failures, meaningful nonlinear BE/Jacobian oracles,
nonunit inventory balance, projection/residual refusal, failed LU, incomplete
horizons, interrupted/persistence/reload failures and species/unit/identity changes.
Use small ordinary functions/records/runners; no solver framework/registry or
private-data CI requirement. Revisit deferred audit suggestions only at their
actual trigger; new nonlinear native integration triggers the nonlinear fixture,
not scorer redesign, callback optimization or general model compatibility changes.

Record measured loading, staging/build, setup, integration, diagnostics, persistence
and total CPU/wall time, peak RSS with explicit byte units, raw/derived storage and
hardware/thread settings. Estimates only: one CPU, <2 GiB working memory, <1 GiB
new scientific output, approximately 0.2–4 CPU-hours for both campaigns; dense
finite-difference Jacobians may dominate. Queue delay and troubleshooting are
unknown. These estimates are not reservations, limits or speedup evidence.

Provide a concise reference-verification report and runnable guide. Ordinary
exact-candidate PR review must cover implementation, numerical/scientific meaning,
provenance, failure completeness, readability and simplicity. Preserve original
2B/2C evidence and the accepted overlay. Human named-reference acceptance, concrete
merge approval and final 2D acceptance remain explicit, followed by merged checks;
issue/goal stay incomplete until all hold. Keep milestone #3 open.

Later 2E must separately freeze the unchanged model/preprocessing, matching forcing/
output/observable/failure/cost protocol and held-out selection rule, then explicitly
release final-test reference generation/evaluation. Apply the same membership/time
rule to held-out histories only after that release, without outcome-based case
replacement. No final-test case is generated/inspected here; no 2E execution follows
this protocol. Poor frozen-MLP fidelity grants no new checkpoint or training scope.
