# Phase 2D assembly qualification v1 — D-039 proposal

**PROPOSED; no new producer execution is authorized.** Prepared 2026-11-23 for
[issue #44](https://github.com/jaharris87/crucible-astro/issues/44), inside the
existing [Phase 2 sequence](../../docs/PHASE_2_LAUNCH.md). This proposal follows the
[completed D-038 evidence](../../docs/reports/2026-11-23-phase2d-diagnostics.md).
Fresh independent protocol review and explicit human acceptance of BOTH the new
numerical source/claim and this producer scope precede any build or physical call.
The complete 2D objective remains a converged, reproduced, human-accepted reference
set and human-approved integration. This qualification alone cannot satisfy it.

## Question and source choice

Does evaluating the abundance polynomial in higher precision, while preserving
native binary64 coefficients, pass independent arithmetic/derivative checks and
remove the original first-step solvability blocker under unchanged local controls?
D-038 found material assembly discrepancy but did not establish it as the sole
cause, prove original-F failure inevitable or show another increment factor preferable.

Recommend the separately named numerical RHS
**`native-XNet-b64-productsum113-b64-v1`**. Each fresh call runs the unchanged native
`cross_sect → yderiv`, retaining original F and binary64 b. A small original
routine then promotes b and each abundance operand **before multiplication**,
forms products in native participant order, accumulates each reaction-order class
in native extended-entry order, joins the four class totals left-to-right, and
rounds each final derivative once to binary64. Explicit scalar assignments retain
this operation sequence. Promoting only sums or recomputing b is excluded.

The mathematical polynomial conditional on native binary64 b is unchanged, but
this **changes the numerical RHS**. It is not the original D-019 digital reference.
Accepting D-039 would accept investigating this distinct source, not accepting its
trajectory accuracy. Original producer projects, D-019 controls/data/qualification,
all original failed attempts and the frozen MLP/scalers remain unchanged. The MLP
was fitted to original digital F; its compatibility with this new source is not
established by unchanged T9/rho features. Sampled original/variant differences
supply no trajectory-error bound and authorize no learned-model rollout.

Alternative: retain original digital F as the required trajectory source and
continue offline numerical-method analysis. That preserves the exact digital
target but does not remove its observed assembly discrepancy. D-038 has not proved
that another solver could not meet the original criteria. No solver, tolerance or
RHS change follows automatically from either choice.

## Fixed states, forcing and producer

Reuse the exact three D-038 states and its annex SHA256
`dbb954afac144d9305a87e483c0c08833a8cdf2487d390f2d6532e5e72a814eb`.
The [D-038 protocol](DIAGNOSTIC_PROTOCOL.md#question-frozen-states-and-unchanged-physics)
binds both original initial NPZs, source archive and chronological Newton300 record.
Frozen diagnostic input-file SHA256s are:

| State | Input SHA256 |
| --- | --- |
| Development initial | `5fb576e90c25bd3f9c2582e48f435ed1009536fc178058f6d98bf823f846f9c0` |
| Validation initial | `4493fb2948ce2dd5a295eec789d076f12bd87a326acdfecbae94e1b777708064` |
| Development Newton300 | `fe1e0bd11ad3f52b5dedc51d9acef8c19f43694ed5fd74e039358b000c322f6b` |

First-step attempts start from the same original development/validation Y0, with
the original saved T9/rho interpolation and zero time origin. Request the original
first L0 interval **h=1e-4 s**. Reuse these original standard L0 input bytes:

| Case | Standard input SHA256 | New tight counterpart SHA256 |
| --- | --- | --- |
| Development | `e01360c67159d80c23dd6820851ace68a7cf3375158b7ce29e705117397eb4ae` | `316cc070cb8db199ee1a8318c2d5c18024dff13631252f4af99645f2f844894e` |
| Validation | `6df2cb7df8464994a5e7997825a4cd3393b47bcbc10fc435af855c5908cce1fe` | `27ed0768df74810e51f59b4be7bfcc0cadad8745eb221d5ab11b11e147a60aae` |

The tight counterpart is a **separate derived file**, changing only two little-
endian binary64 controls at offset 32 to `(1e-14,1e-12)`; preserve every other byte.
The original tight file uses the L3 mesh and is not substituted. These derived
identities were computed before new physical outcomes; verify them during staging.
Retain the existing full forcing files, domain, endpoint/knot behavior and source
identities from [D-036](PROTOCOL.md). No history, membership, initial-state,
species-order, unit, forcing/interpolation or physical-setting change is proposed.

Keep all 160 physical molar Y, signed Y/s, binary64 solver coordinates and
composition-derived Ye=Q/B. Native binary64 moments, EOS, rates, screening, weak
and b formation are unchanged. Heating and active NSE/neutrino evaluation remain
excluded as in D-036. No normalization or new clipping/projection is added.

Stage separately from originals, starting with reviewed source
`ae6971522ba1333f550664ac793be6b662e3dae4`. Retain the new exact diff, committed
source/tree, source manifest, build recipe, compiler/libraries, executable, tables
and environment. Use the same pinned Intel 2025.3 / PrgEnv-intel 8.7.0 /
parallel-HDF5 1.14.3.9 CPU toolchain, sequential MKL, one rank/thread and existing
`-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32` flags. Only the
new assembly module additionally uses `-fp-model strict`; no global FP-mode change.
Original producer objects retain their flags. Hash all linked/runtime libraries,
including any new precision support library. Push and independently review the
actual implementation candidate before producer execution. A code repair within
this fixed contract is routine; a changed contract requires a new decision.

## Precision and independent arithmetic gate

Use `selected_real_kind(33,4931)`, requiring radix 2, **exactly 113 significand
bits**, 128-bit storage and binary128 exponent range. Reject an unsupported kind
or silent fallback. Intel's [real-data model](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2026-2/model-for-real-data.html)
documents binary128; its [strict FP option](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2026-2/fp-model-fp.html)
disables contraction. These documentation expectations do not qualify the actual
pinned compiler/runtime: the compiled fixtures must establish the required behavior.

Before physical calls, require all eleven existing synthetic scenarios plus
precision/arithmetic fixtures: kind/range/storage, nearest rounding, cancellation
with a known exact rational answer, promotion before products, all four reaction
orders and ordered class summation, malformed/nonfinite refusal, exact promotion
and return of signed minimum/maximum binary64 subnormals, normal/subnormal ties
and overflow refusal. Use volatile runtime operands where constant folding could
hide conversion behavior. Require exact promotion and gradual nearest final
conversion; reject flushing or changed FP modes, without repairing the environment.
Record actual modes/flags before/after the module and original kernel. Public
Python tests use independent small exact-rational oracles, not private data.

At each of the three frozen states export original F, coefficients, binary64 b,
variant F and the pre-conversion binary128 species totals, with a documented
versioned byte representation independently decoded into exact fractions.
For species i define exact conditional polynomial P_i, absolute term sum W_i,
extended-entry counts N_io, `m_i=sum_o((o+1)*N_io)+3`, `u_q=2^-113` and
`gamma_m=m*u_q/(1-m*u_q)`. Require:

`abs(F_quad_i-P_i) <= E_qi = gamma_(m_i)*W_i`.

The 6,794 native extended entries give `m_i<=33973`. At most five finite binary64
operands form any term, with 0<=Y<=1. Their nonzero exponent range and the finite
term totals fit inside binary128; verify this support from the actual operands,
counts and intermediate exports rather than assuming it. Unsupported bounds fail.
Final F must be the correctly rounded nearest-even binary64 conversion of the
decoded quad total (including explicit signed-zero checks). Also require the
conservative combined bound:

`abs(F_variant_i-P_i) <= E_qi + 2^-53*(abs(P_i)+E_qi) + 2^-1075`.

All bound calculations use exact/outward arithmetic; preserve separated terms,
unsupported/zero masks and original-minus-variant differences. Require every
component within bounds; report baryon rates without imposing constant charge.
These are arithmetic envelopes, not nuclear physical-error floors or global
trajectory tolerances. Native coefficient/rate/EOS quantization remains unqualified.

## Fixed execution sequence and qualification criteria

1. **Identity:** six processes, three fresh evaluations together and one in a
   fresh process at each state: twelve full-F calls. Compare original F, csect/b,
   inputs, moments, branches and modes against retained D-038 baseline bits; both
   initial original-F controls must also match D-019 exactly. Require variant F
   and quad totals bitwise repeatable within/across processes and all arithmetic
   gates. An identity, arithmetic, mode or shared-input/build failure stops later work.
2. **Derivatives:** three processes, one per frozen state. Exactly one factor-one
   full **variant-F** Jacobian, holding time/T9/rho fixed, recomputing native Ye
   and all composition-dependent conditions at each probe. Retain original state
   scales, representable offsets, stencil preference, eight halvings and branch
   gates. Use the three D-038 directions, including nonnegative odd-species
   support, and all nine multipliers. Require all three direction comparisons
   per state to pass the unchanged `1e-7+1e-3*max(abs(A*Jv),abs(A*Dv))` criterion
   at two adjacent admissible multipliers. Retain all refusals/failures; complete
   other fixed derivative states after an ordinary window failure, but do not
   start first-step work unless all gates pass. No factor sweep/selection, frozen
   linear candidate or additional physical diagnostic is included.
3. **Standard first steps:** two fresh processes, one per original case. A narrow
   command calls native `solve_be` **once** and bypasses the driver's continuation
   loop. Request h=1e-4, with native ten attempts, factor-two reductions and thirty
   Newton iterations per attempt. Stop at its first accepted step or failure.
   Complete both cases after ordinary nonlinear failure; stop globally on a shared
   identity/forensic/nonfinite corruption. No case or h replacement.
4. **Tight counterparts:** only if BOTH standard attempts pass, execute the two
   predeclared tight first-step processes, with no other change. Otherwise retain
   both as conditionally unattempted. Both executed tight attempts must pass.

Solver/Jacobian/linear algebra stay D-036: binary64 full fresh-F numerical J,
factor-one delta, native dense M=I/h-J and LU, no new equilibration/refinement or
analytic/learned J. Standard `(aN,rN)=(1e-13,1e-11)`, tight `(1e-14,1e-12)`;
require `max(abs(A*(Ynew-Yold-h*Fnew))/(aN+rN*max(abs(A*Yold),abs(A*Ynew))))<=1`.
Disclose and retain native negative-Newton-to-zero projection. Final projection
A-L1 <=1e-12 per accepted step and cumulative <=1e-10; accepted baryon difference
from original B0 <=1e-10*max(1,abs(B0)); all domain/forcing/positivity checks apply.
Every factor/solve must have info=0. Unsupported arithmetic or missing/mismatched
forensic evidence fails qualification; no tolerance, physics or selection relaxation.

The endpoint for this qualification is **the first native accepted step**, which
may occur below requested 1e-4 after native reductions. Record requested h, every
attempted h, achieved time and outputs explicitly. A shorter step does not complete
the requested 1e-4 interval. Standard/tight endpoints at different achieved times
cannot establish same-time nonlinear agreement. Passing all executed stages proves
only arithmetic behavior, tested derivatives and initial-step solvability, not
full-horizon convergence, balance, clean trajectory reproduction or physical accuracy.

## Concrete authority, failures, artifacts and costs

Request **one fresh qualification build plus at most two fresh repair builds**
after build or prephysical synthetic-preflight implementation failure: at most
three builds total, including successful builds stopped by preflight. Retain all
attempts and exact diffs. Repairs preserve this protocol/toolchain/physics.
No postphysical rebuild, infrastructure restart, completed-process repeat,
numerical-failure rerun or full trajectory continuation is included.

Six identity + three derivative + two standard + at most two conditional tight
processes are planned. A conservative full-J bound is
`Q=2+160*9*3*2=8642` guarded fresh requests (baseline/restore, 160 columns, nine
increments, three stencils, two probes). Count even refused requests as physical
for this upper bound; original kernel plus variant postassembly is one full-F call.

| Work | Maximum full-F calls |
| --- | ---: |
| Identity | 12 |
| Three derivative setup calls | 3 |
| Three factor-one full Jacobians | 25926 |
| Three-state directional probes | 486 |
| Directional baseline restores | 3 |
| Four first-step process setups | 4 |
| First-step Newton: 4*10*30*(Q+1 post-update F) | 10371600 |
| **Total** | **10398034** |

Maximum diagnostics: 1,203 full Jacobians, 192,480 completed columns,
5,196,960 column-stencil attempts, 243 directional-stencil attempts, 1,200
Newton/LU/solve records, forty native step attempts, thirty-six retries and four
accepted endpoints. These finite-loop scope bounds are not D-013 compute caps.
No undeclared physical checks are added to persistence or offline analysis.

Retain every planned process, conditional skip, interruption, failure and exception.
Use ordinary versioned binary streams and JSON/NPZ, never pickle. Every physical
call records exact input Y/time/T9/rho, original/variant F, moments, role, call ID,
modes and branch-change events. FD attempts retain offsets, stencil/reduction,
refusal reason and probe IDs. Each Newton record binds old/pre-update Y, J baseline
and call ID, J, unfactored M, RHS, LU/pivots/info, correction, unprojected/projected
Y, post-update call ID, weights, component residuals and projection. Preserve
baseline/accepted/failure coefficient/b/quad-total workspaces. Keep rejected
arguments, last evaluated workspace and matrix baseline distinct across retry
cleanup; do not label a rejected argument's workspace as its physical evaluation.
Forensic exports add no physical calls. Exact-polynomial reporting is required at
the three frozen states and retained accepted/failure workspaces, not every probe.

Preserve raw outputs before separate derived analysis. Verify source/input/file
hashes, requested versus achieved endpoints, complete columns/records/counters and
array dtype/shape/bytes. Fresh-process reload recomputes derived checks from raw
records within the declared exact/bounded arithmetic criteria; identity repeats
remain bitwise. This is not another build or a clean trajectory reproduction.
Independent read-only assessment must review actual outcomes before proposing a
later trajectory campaign. No failed case may be dropped or silently repaired.

Estimates, not caps: build roughly 20 s wall / 0.1 GiB RSS from D-038; nominal
first-admissible-stencil work up to about 389,000 full-F calls, historically roughly
150 CPU s before unmeasured binary128/persistence overhead. Allow approximately
minutes to tens of minutes typically, potentially hours at worst-case probe loops;
record frozen-stage throughput to improve later estimates without adding trials.
Expected memory <2 GiB, typical storage several GiB; maximum raw probes/forensics
can require tens of GiB. Measure setup/loading/integration/persistence, CPU/wall,
RSS/storage and unavailable scopes. No compute reservation or speedup claim follows.

Stop after qualification reporting and independent assessment. Any later two-case
10 ms, four-mesh/tight/clean-reproduction campaign needs a separately accepted
protocol and producer decision for this new source, retaining D-036 thresholds
unless explicitly changed. Do not substitute these short steps for the full 2D
reference goal. No reference acceptance, merge, final 2D acceptance, model work,
final-test release or Phase 2E authority is requested here.
