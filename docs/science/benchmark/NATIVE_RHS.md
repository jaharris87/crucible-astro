# D-024 finite native-RHS fidelity benchmark

2026-11-19, [issue #33](https://github.com/jaharris87/crucible-astro/issues/33),
[S03 #15](https://github.com/jaharris87/crucible-astro/issues/15).
**D-024 scoring and D-025 named data/reference/final partitions accepted.**
The separate [qualified overlay/card](../../data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md)
and [final receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482) supply actual qualification and closure evidence.
The preparation-time pending statements below describe the preserved proposal,
not a current denial of D-025 acceptance.
The maintainer selected “Accept native-RHS fidelity profiles (Recommended)” in
[the D-024 decision](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7013147287),
binding proposal SHA256
`902625688aca39d3b6ba56f79f41709e6ed084b5a6bcd1f90c14d85e4b839262`.
The source proposal's original NOT ACCEPTED heading is historical; the later
receipt accepts its scoring option, not its separately reserved data qualification.

These are fixed numerical research fidelity objectives against retained digital
labels. Their rationale is the explicitly limited numerical-emulation task, not
an inferred astrophysical application tolerance, nuclear/EOS uncertainty, or an
assembly-bound allowance. No model exists and no successful profile attainment,
scientific accuracy, speedup or final-test performance use is claimed here.
D-022's separate [physical abundance-change budgets](../validation/PHYSICAL_ERROR_BUDGETS.md) and all their
unresolved scientific allowances/scales/timescales/critical selections stay intact.

## Frozen finite task and bindings

| Item | Contract |
| --- | --- |
| Task | Instantaneous full-state `dY/dt=F_native` at unchanged full ordered 160-species Y and recorded T9/rho, under the pinned D-019 native numerical reference |
| Conditions | Native composition-derived `Ye=Q/B`, `Q=Z dot Y`, `B=A dot Y>0`; weak/screening on, heating off, asserted zero active neutrino rates; no constant-charge constraint |
| Time | Preserve the supplied time/record identity and reference call context. The evaluator is pointwise, with no forecast interval, condition interpolation or invented predictive time feature |
| Inputs/features | Full physical composition and declared native conditions. Sample, tracer, history, group, category and packet identities are provenance/grouping metadata, not shortcut predictive features; no fitted feature selection is implemented |
| Units | Y=`molar_abundance_Y`, F=`molar_abundance_Y/s`, T9=GK, rho=`g/cm^3`, time=s. Mass-fraction rate uses verified `Xdot=A*F` with fixed ordered A |
| State/species identity | All 160 ordered `(id,A,Z)` entries in [the frozen JSON configuration](../../../configs/native_fidelity/primary_benchmark.json); stable ids distinguish species; no permutation, clipping, normalization or projection |
| Domain | Exactly the named 24,314 candidate inputs in 380 histories/94 operational groups. Finite within-parent points, not a rectangular T/rho/Y validity box, independent physical families or representative CCSN/NSM coverage |
| Horizon/energy | Instantaneous RHS only. Heating, stored energy fields, integrated trajectories/yields and equilibrium/rollout accuracy remain excluded/unevaluated |
| Preprocessing/search | None fitted in Phase 1. Later authorized transforms/scales/bases/features use training only; validation supports recorded authorized choices; final test cannot guide redesign without disclosed reuse/new confirmation |
| Working roles | D-021 rule: train/validation/test = 66/14/14 groups, 274/51/55 histories and 17,659/3,220/3,435 candidates. Complete [partition constructor/checks](PARTITIONS.md) preserve ancestry/whole-history groups; D-025 accepts these exact roles through the separate qualified overlay |

The source evaluator assigns unchanged Y, time, T9 and rho, calls the pinned
`cross_sect` then `yderiv`, and checks echoed state/configuration bits. This scoring
implementation calls neither routine and invents no new reference or conditioning.
The [reference-scope record](../../phase1/RHS_REFERENCE_SCOPE.md) and retained source/input/build
receipts distinguish this declared native numerical calculation from the unknown
historical generator of the raw stored derivative. Stored derivatives are audit-only.

The immutable primary union is integrated in [PR #32](https://github.com/jaharris87/crucible-astro/pull/32),
including its [quarantined-union living card](https://github.com/jaharris87/crucible-astro/blob/1ce03d821e55bef64843c53046a49f59b23e5e3d/docs/data-cards/genesis_datacard_ccsn_primary_native_rhs_union_v0_1.md).
Payload SHA256 `f4171d1600586f28b4a514071c8c029d1a84c7634f9f11ae8a6b4b25c6a0c980`
(109,687,400 bytes), manifest SHA256
`78f5c7f51e041aa82698cc3f7832f399a00738da775432bcd80763f767fb4b86`
(38,652 bytes). The manifest binds both native reference packets, exact ordered
species, original raw ancestry, execution/comparison receipts and all exclusions.
The D-021 working candidate bytes have SHA256
`211e33ad75af8c77b383188814d2e2b41e8b9eed3773a9e84aa8c6576efd9c79`.
Original pool/contract/group identities are retained in that partition packet.
All four real HDF5 scientific eligibility masks remain false.

## Accepted profiles and exact arithmetic

For species i at one sample, use the exact decoded binary64 label f and prediction p:

```text
e_i = A_i * (p_i - f_i)
component meets r  <=>  |e_i| <= r * |A_i*f_i|
r = 1/1000, 1/100, 1/20
```

Positive A cancels from the relative inequality; it does not cancel from physical
errors. The implementation uses Python exact rational arithmetic on the decoded
binary64 values and fixed decimal fractions. It never rounds `r*|f|` to zero or
uses an epsilon at a threshold. Exact equality meets the profile. Tiny/subnormal
nonzero targets stay in the nonzero population. This does not imply that tiny
rates are physically consequential.

For nonzero targets report `|e|/|A*f|`, RMS/max and exceedances with explicit
nonzero denominators. For exact zero targets, zero error meets every profile;
any nonzero prediction violates each. Report physical absolute RMS/max and
nonzero-prediction count/fraction there, with **no zero-subset relative RMS**.
Signed zeros count as numerical zero. No clipping floor or assembly envelope is
added. All-population statistics retain physical signed/absolute errors over
every component; relative RMS/max are defined only for the nonzero population.

A record attains a profile only when its entire ordered prediction vector is
finite and every monitored component meets it. A null/nonfinite component or
explicit failed prediction fails the whole vector and every component's attempted
comparison; finite violations remain a separate count. Finite input vectors with
physical difference/reporting overflow still have an exact mathematical decision
and remain valid attempts, with an explicit unbounded report marker.
Malformed identities/order/units and nonfinite native reference Y/F reject; they
cannot define a usable zero/nonzero target population. A native reference's
optional `success` flag must be exactly boolean `true` when present; omitted flags
retain the existing valid-reference convention. Declared failures or malformed
flags reject with the sample ID before target populations are constructed.
Absent prediction arrays are NOT_EVALUATED, never a zero-error result. Empty populations are
NOT_APPLICABLE/count zero, never success.

## Explicit reporting and weighting

`crucible.native_fidelity.evaluate_native(config, reference, prediction=None)`
uses a distinct `crucible.native_fidelity.v1` configuration and the existing
strict ordered sample schema documented in [the D-022 interface](../validation/PHYSICAL_ERROR_BUDGETS.md#small-json-interface).
It does not call or change the D-022 physical-budget evaluator. All species in the
configuration are monitored; the real frozen config has 160, while public
mathematical examples intentionally have two. The three rational profiles are fixed.

Reports include per-component physical signed/absolute error and relative error
where defined; pooled and per-species physical signed mean/min/max, absolute
RMS/max; nonzero relative RMS/max; and complete history/group/category/regime
strata. Regimes are provenance-bearing supplied labels or unknown, with no inferred
burning/NSE/freeze-out threshold. Group statistics never replace constituent
species errors. Exact config identity and sample/prediction identities are retained.

For each all/nonzero/zero population, explicitly count reference components and
records with components, attempted/valid/failed components and records, finite
profile violations, met/attained counts, valid exceedance denominator/fraction,
and attainment fraction over **all attempted** components/records. Every field
named record attainment or record finite violation uses the **whole ordered
vector**, including inside population/per-species summaries; its denominator is
records having components in that selected subset. Component counters remain
subset-specific, so an agreeing subset can have zero component violations while
its record fails elsewhere in the vector. The report labels this scope explicitly.
Successful-case statistics are labeled conditional; failures cannot be dropped from attempted
fractions. A population with no reference components is not applicable even if
other populations exist. No averaging over empty successful sets is called a pass.

For physical RMS, and separately for nonzero relative RMS, report:

1. Pooled: square-root of mean squared component errors over valid components.
2. Equal-history: mean squared component errors inside each history, average
   those history MSEs equally, then square-root.
3. Equal-group: calculate history MSEs, average equally over histories inside
   each operational group, average group MSEs equally, then square-root.

Each population retains counts of reference and valid histories/groups, those
without valid components, and failed components/records. Macro RMS is explicitly
conditional on valid vectors: empty population histories/groups are omitted only
with visible counts, and mixed-success histories retain their failure counts.
No effective independent sample count or confidence claim is implied.

Metric values carry `FINITE`, `ROUNDED_TO_ZERO`, `UNBOUNDED_BINARY64_REPORT` or
`NOT_APPLICABLE` status. Scalar rational values use binary64 rounding. Under D-026,
physical sums/squares remain exact with 70-digit Decimal RMS rendering; relative
MSE/macro accumulation and RMS rendering use 80-digit Decimal as specified below.
Exact profile comparisons never use these reporting approximations. Nonzero report underflow is marked;
overflow yields null plus its status. JSON contains neither NaN nor Infinity.

```sh
uv run python -B -m crucible.native_fidelity \
  configs/native_fidelity/synthetic_config.json \
  configs/native_fidelity/synthetic_reference.json \
  --prediction configs/native_fidelity/synthetic_prediction.json
```

The committed compact synthetic report is a hand-checkable analytic-vector
example, not a trained-model or benchmark result. Public tests use Fraction and
analytic oracles, binary64 threshold neighbors, subnormals, zero targets, failure
and overflow cases, macro-weight examples and unchanged-input checks; no real
records, producer calls or final-test results enter public CI.

### Accepted reporting-arithmetic successor (D-026)

The `crucible.native_fidelity.relative-decimal80.v1` report arithmetic identity
is the **accepted D-026 successor**, source SHA256
`c287f873ede888c12128552046176fd6618556081dc907c4fccadb491bd056b7`,
distinct from the original scorer SHA256
`a1d50fedc951dbe332d25bd09e7c32e0539024f6f0a8f193b271ed0253ca0df0`
bound by the accepted D-025 overlay. [The human adoption receipt](https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017529239)
accepts this successor; the original configuration, overlay and scorer identity
remain unchanged. Future results bind both the qualified dataset and actual
successor source/adoption receipt rather than rewriting that overlay.
Reports expose the new arithmetic identity and predecessor hash. Only nonzero
relative mean-squares and their history/group averaging use 80-digit Decimal;
physical sums/squares remain exact Fraction with 70-digit Decimal RMS rendering.
Both report paths explicitly use ROUND_HALF_EVEN and exponent limits +/-999999,
independent of caller Decimal context. All profile decisions, zero/failure policy,
maxima, per-component errors and history-first/group-second weighting are unchanged.
For finite binary64 inputs, nonzero relative errors are at least `2^-53` and below
`2^2099`, so Decimal avoids binary64 intermediate square overflow/underflow.
At the named maximum 3,890,240 components/380 histories/94 groups, positive-sum
roundoff bounds conservatively limit relative arithmetic error before binary64
rendering to `1e-71`; this is not a universal correctly-rounded, bit-identical or
one-ulp guarantee. Exact-zero ratios remain zero. Explicit report underflow and
overflow markers remain; no profile threshold, data qualification or scientific
accuracy is changed by this reporting-arithmetic adoption. Detailed-report memory and
streaming remain separate follow-up work.

## Separate physics, assembly and later acceptance

Native no-auxiliary-reservoir diagnostics remain separate: state nonnegativity,
`A dot F`, exact-zero boundary compatibility and weak `Ye_dot=(B*Z dot F-Q*A dot F)/B^2`.
Unsupported open/external/auxiliary balances stay unavailable. No state or rate
is repaired. At the native-facing boundary, a sample whose optional physics
output contains a nonfinite quantity is explicitly UNAVAILABLE, with an overall
DIAGNOSTICS_WITH_UNAVAILABLE_SAMPLES status. Other finite diagnostic samples and
unsupported-network unavailability are preserved. No nonfinite value is clipped
or replaced with a fabricated finite physical value, and defined exact scoring is
retained. D-022's helper/API remains unchanged.
Heating is EXCLUDED_NOT_EVALUATED, not zero truth. Conditional
assembly bounds/residuals/cancellation diagnostics belong to reference verification;
they are neither noise in the exact digital label nor a model allowance. No
bound-inclusive scoring envelope was adopted.

D-024 grants no data/reference/final-partition acceptance, qualified overlay,
model/training/architecture, new labels, producer/solver/Jacobian execution or
merge authority. D-017/D-020/D-023 physical calls are exhausted. Later authorized
work separately needs application tolerances, reconstruction/decoded chain-rule
and closure evidence, integrated abundance/energy/weak-Ye/equilibrium behavior,
solver/JVP compatibility and matched-accuracy total cost. Actual Phase 2 artifacts
need model cards; this document invents none.

## Preserved preparation packet and subsequent qualification

An ignored one-off recipe prepared the exact private proposal before D-025. It
checks the bound original pool/contract/groups, reconstructs the complete accepted
candidate through the existing partition code, joins all 24,314 HDF record IDs
and species identities, preserves 6,158 ordinary and source-layout/initial/NSE
exclusions, and verifies that all four HDF masks remain false. That original proposal includes all 24,314 candidate roles but grants no eligibility.
With the original mechanical inputs, `validate_scientific` rejects that preserved
pending packet as `empty_eligible`.
The immutable quarantined dataset and its old masks are never rewritten.

The proposal binds payload/manifest/card, native reference receipts, frozen
benchmark/config/scorer, working candidate, original mechanical inputs, proposed
membership/exclusions and explicit limitations. File SHA256s remain in the private
packet and its public PR receipt; no private row IDs, paths or arrays enter Git.
There is no new core qualification framework or registry.

D-025 subsequently bound the exact proposal digest and accepted reference, subset
and final partitions. A separate new overlay binds the unchanged payload, human
receipt and exact eligibility/membership digests checked against the original
complete mechanical inputs. The proposal does not hash itself or a future receipt;
the [closeout record](../../phase1/PHASE1_CLOSEOUT.md) gives the resulting identities.
Redistribution remains a separate gate. This numerical-emulation qualification
does not qualify raw energy/rollout fields, physical application accuracy or NS1/NS3.

The accepted scoring configuration is byte-preserved, including its historical
preparation-time `qualification_status`. Current purpose-specific eligibility
comes solely from the D-025-bound overlay; that old metadata is not rewritten
to change an accepted artifact hash. See the final qualified card and receipt.
