# Source and arithmetic audit for the fixed candidate

This is source inspection plus a reviewable implementation proposal, not a
completed reference run. Reference file identities are those in `bindings.json`;
no producer/EOS source was edited or vendored. Original D-017 support is unchanged.

## Current-state dependency and order

The entry point is the same one-zone D-017 setup. Every state resets Y, time, T9
and density from preserved input bytes. The inspected active path is:

- `xnet_integrate.f90:532–597`: `cross_sect` refreshes EOS, effective weak flag,
  screening, temperature moments, partition functions and FFN coefficients.
- `:227–266`: `update_iweak` assigns from `iweak0` each time, never a prior flag.
- `xnet_abundances.f90:41–48` defines raw baryon moment B=sum(A*Y), raw
  charge moment Q=sum(Z*Y), and native Ye=Q/B. Both preparation/grid gates use
  this ratio with positive finite B; they preserve Y, not normalized Y. The
  decoder retains raw B/Q diagnostics separately from the EOS-returned Ye.
- `xnet_eos_starkiller.f90:48–65`: moments come from current Y; a local EOS state
  receives rho/T/composition and calls the rho/T mode. In pinned `actual_eos.F90`
  `:258–273,364`, that mode takes current inputs and does no Newton iteration.
  Module tables and Coulomb/input constants are initialized once (`:1535–1612`),
  with no last-state guess/index cache on this path. It does not use history Ye.
- `xnet_screening.f90:179–277` overwrites all active h arrays; one-reactant h is
  zeroed. `xnet_data.f90:130–151` refreshes partition functions and placeholder0.
  `xnet_ffn.f90:86–123` recomputes local grid brackets and each rate.
- `xnet_integrate.f90:600–750` assigns all current csect values on the admitted
  flags. The harness rejects one-reactant flags outside0..4 and nonzero nnnu.
  Native three-reactant coefficient thresholding remains exactly as supplied.
- `:346–395` overwrites b arrays and every species derivative. No csect assignment
  occurs in `yderiv`; the harness additionally checks its before/after bits.
  Timers/counters and zone IDs are diagnostic; heating is off.

The harness poisons only these refreshed work/output arrays before each call,
then rejects surviving nonfinite coefficients/b/work/results. It exports static
mapping arrays before/after and compares them with an independently parsed
expected snapshot. This detects stale-path dependence without adding a physical
call or changing Y. Full runtime/order compatibility is untested until separately
authorized execution; the two retained in-grid controls additionally expose an
order/environment difference. Any mismatch stops rather than silently resetting
physics or repeating calls. No claim of empirical exhaustive order testing is made.

## Combinatorial factors and independent assembly

`xnet_data.f90:546–576,596–716` reads participant lists plus extended a/mu maps;
`:718–747` derives each extended target/reactant index. The selected map has
6,794 entries (1,862/4,860/53/19), not merely one entry per nonzero net coefficient.
Some species/reactions have separate destruction and creation entries.

`cross_sect` supplies rates/density/partition/screening/weak factors, not the
identical-reactant factorial. `yderiv:346–350` forms b=a*csect. Independent
assembly therefore uses flux=csect*product(Y_reactants)/factorial(largest multiplicity)
and integer product-minus-reactant counts. This is the supplied **native**
convention, verified against read-only `xnet_preprocess.f90:734–777,802–805`
(SHA256 `703bb775fdf8a18bd5d2a9750d4400e6ef6771301832b51ac16c82543b08e25f`).
For two distinct identical reactant pairs this differs by a factor of two from
product(multiplicity!), a distinction preserved in private static evidence and
a hand-known synthetic example. No producer weight/rate is repaired, and no
claim of physical combinatorial correctness or historical generator execution
is made. The [current scope clarification](../../docs/phase1/RHS_REFERENCE_SCOPE.md)
records the official matching rate entry and parks the upstream-history
investigation separately. The accepted target remains native numerical behavior;
that investigation is not an added Phase 1 execution/qualification prerequisite.
Numerical verification and human scientific acceptance still apply.
The initial checker rejected this distinction before any bundle/build;
its failed preparation evidence remains private. It never divides an already formed b
by that factorial a second time. For every exported extended a, the checker
identifies its exact numerator k by binary equality to float(k/symmetry), then
checks summed integer numerators equal independent net stoichiometry. This allows
separate canceling entries and quantifies binary rounding of fractions such as
1/6. Every reaction's exact integer baryon balance must hold. Charge may change.

The static input parser follows only the pinned nets3/nets4 layout; the selected
nets4's20-byte final record is unused by the inspected initializer. Full hashes
still bind it. Exported maps must match the prepared stream exactly both times.

## Conditional roundoff envelope

All bounds use exact Python Fractions for serialized binary64 inputs; the
reference algebra is independent reaction stoichiometry. Let u=2^-53,
N=2^-1022 (minimum **normal**, not minimum subnormal), gamma(m)=m*u/(1-m*u).
For n product operands, m=n-1, A=product(max(1,abs(operand))), use

`E_product = gamma(m)*abs(exact_product) + 4*n*N*A*(1+u)^m`.

The factor A bounds amplification of a flushed original/intermediate operand by
all remaining factors. At most n original-input plus3*(n-1) operand/result flush
events are covered. Thus a subnormal input Y flushed before multiplication by a
large coefficient is covered; a generic Nops*minimum-subnormal floor would not be.
The bound permits gradual underflow or DAZ/FTZ and arbitrary binary product
association; FMA is covered by the unfused operation-count envelope. It is
conservative, potentially very loose for extreme values. No FP mode is changed.

For each species, sum product error envelopes; add exact a-quantization error
relative to integer/symmetry factors. Bound summation with gamma(M) times summed
absolute term envelopes plus `4*M*N/(1-M*u)`, where M=number of extended terms+3
covers class accumulation and the three final additions. The four-N allowance
covers operand/result flushes and their rounding per sum. Reject unsupported
operation counts, nonfinite producer b/coefficients/results or an absolute-term
overflow envelope. The admitted states have0<=Y<=1, so products after finite b
cannot overflow; no Y is changed or clipped to satisfy this envelope.

Nearest rounding is queried immediately before assembly and after it, using
[IEEE_GET_ROUNDING_MODE](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2025-3/ieee-get-rounding-mode.html);
non-nearest mode stops. Standard underflow mode is recorded when supported; it
does not identify DAZ. Bounds permit either flush behavior. Actual compiler
flags/wrapper/library/runtime receipts remain required. Excess-precision or
unsupported arithmetic semantics would require review, never a silent flag change.

The exact component residual must lie inside that derived bound. Since exact
stoichiometry conserves baryons, sum(A_i*component_bound_i) bounds the serialized
fresh baryon residual. Reported float bounds are rounded outward. This is
coefficient-conditioned arithmetic evidence, **not a rate/EOS error bound,
application tolerance or scientific accuracy acceptance**. Runtime compatibility
and usefulness/tightness of these conservative bounds remain untested. Energy,
rollout targets and fixed-charge constraints are excluded.

## RHS-PILOT-R1 source-formula repair

[Initial independent review](https://github.com/jaharris87/crucible-astro/pull/20#issuecomment-6966564190)
found that both preparation/control grid gates used Q as Ye. The corrected gates
use native Q/B and reject nonpositive/nonfinite B, without modifying original Y.
Synthetic nonunit-B positive/negative cases cover both paths, including a boundary
case that the raw-Q proxy incorrectly accepts. Historical 83-pilot audit receipts
used the old proxy and are preserved, not relabeled as corrected. A separate
raw-data arithmetic implementation, without importing the experiment helpers,
checks all 6,433 ordinary records; the
5,157 selected identities/state bytes and two retained controls remain unchanged.
This formula repair does not qualify data or supply producer execution authority.
