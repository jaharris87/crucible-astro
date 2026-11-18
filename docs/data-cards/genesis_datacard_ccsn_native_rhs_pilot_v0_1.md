# Datacard for the quarantined native-RHS CCSN pilot

Card version **0.2.0**, 2026-11-17. Local dataset ID
`ccsn-native-rhs-pilot-quarantined`, dataset version **0.1.0**.
**One local quarantined candidate has been materialized and independently
checked against every parent field.** No public dataset release, qualified
training records, scientific performance result or trained model exists.

This living narrative draft follows the six adaptable capability sections of the
official Genesis template **v2.0.0**, pinned in
[guidance evidence](../phase1/GENESIS_GUIDANCE.md). Required custodian, rights and
sensitivity fields remain incomplete. No YAML/schema conformance, machine
validation or catalog submission is claimed. Card version and dataset version
are independent; identities below describe the actual retained candidate.

## Machine Usability Snapshot

| Capability | Current support / limitation |
| --- | --- |
| Discoverability | Public draft description; no released dataset or catalog record |
| Accessibility | Explicit local recipe; no public endpoint or access grant |
| Interoperability | Documented HDF5/JSON contract for one fixed v2 reference format |
| Reusability | Source-bound materializer; complete parent/HDF5 field checks pass; scientific qualification open |
| Governed Use | Authorized bounded quarantine; dataset rights/sensitivity unresolved |
| AI Usability | State, RHS, energy and rollout eligibility all false |
| License clarity | Software BSD-3-Clause; no inferred dataset license |
| Fixity / context | Actual input/execution/recipe/source/output digests retained; historical build association unverified |

## Discoverable

Purpose: preserve the exact original full 160-species states alongside newly
evaluated pointwise native XNet RHS values for scientific inspection. This is a
separate derived dataset from the
[raw CCSN candidate](genesis_datacard_ccsn_raw_candidate.md) and
[three-pair quarantine](genesis_datacard_ccsn_quarantined_v0_1.md).
The actual candidate has 5,157 source-table candidate states from 80 histories;
purposive pilot coverage is not an accepted primary benchmark. Keywords: CCSN,
XNet, pointwise RHS, molar abundance, provenance, quarantined data engineering.
The parent generator/build association and physical qualification remain distinct
from the new declared reference. No scientific accuracy or speedup is claimed.

## Accessible

The candidate is local HDF5 plus a JSON manifest; real inputs and output remain
in ignored storage outside worktrees. There is no public data download, DOI,
catalog entry or redistribution grant. Access requires existing authorization
from the maintainer and eventual custodian. The public card and software do not
grant data rights. Public CI uses only synthetic independently specified streams.

## Interoperable

The [materialization contract](../phase1/RHS_DATASET.md) defines exact source-PR-20
v2 little-endian binary fields, ordered Z/A, dimensions, units, raw-record
identities and HDF5 fields. Original full Y, time/T9/rho, internal dt, fresh RHS,
source-returned native EOS Ye and stored diagnostics retain binary64 bits,
including signed zero. There is no normalization, clipping or fixed Ye.
Fresh targets are instantaneous pointwise `molar_abundance_Y/s`, conditional on
the declared full state and native thermodynamic/rate configuration. Stored dY
and internal-step energy retain explicit unqualified diagnostic names. Large
coefficient proof remains linked in the raw audit parent rather than copied as
features. No finite-step, integrated trajectory or energy target is qualified.

## Reusable

D-019 accepts the new pointwise full-Y/T9/rho reference contract, with native
`Ye=sum(Z*Y)/sum(A*Y)`. D-020 separately authorizes the exact pilot under
[issue #18](https://github.com/jaharris87/crucible-astro/issues/18).
[Issue #23](https://github.com/jaharris87/crucible-astro/issues/23) authorizes this
finite materialization of its verified outputs. The actual manifest binds
original-state raw-ts/raw-ev/payload/input-state ancestry separately from the
new label's source preparation, generating executable, retained result and
completed comparator. A separate finite execution receipt binds that preparation,
executable, result and completed comparison/components to twelve explicit retained
actual build/run evidence files, including hardware/environment/job identities.
Both runtime-library maps require absolute paths and canonical SHA-256 identities
and must agree; remote library files need not exist locally. All declared retained
evidence files are actually hash-checked and rechecked before output. The manifest
records recipe/source/software identities and output
digest. These new-reference identities do not prove the historical generator.

The full coefficient-conditioned comparator completed successfully before
materialization; its exact execution/job/transfer closure is retained. See the
[portable execution report](../phase1/RHS_PILOT_EXECUTION.md). This establishes
bounded numerical assembly under declared coefficients, not rate/EOS/astrophysical
accuracy. Scientific tolerance/accuracy acceptance and sufficient coverage remain
open; no positive scientific eligibility follows.

The actual candidate is 22,513,144-byte HDF5 plus an 18,684-byte manifest. Local
Python 3.12.9 / h5py 3.15.1 / HDF5 1.14.6 / NumPy 2.5.5 materialization used
source commit `9e74875a8afbde4f3f2a2cf23e562f3045b35671`; its code is bound by the
source digest below. A separate verifier importing neither materializer nor
producer compared every row's three 160-component vectors and six scalar fields
bit-for-bit, five integer identities and five raw-ancestry columns exactly, all
ordered species/units/dimensions, and all four masks. Every float was finite;
zero scientific entries were positive. Species order also matches a separately
interpreted original raw header. All 19 leading-zero tracer histories match.
The real records contain no negative zeros; public synthetic controls separately
exercise sign-bit preservation. Every primary and twelve execution evidence
identities was rechecked after the scan. This independently implemented software
check is not the required fresh reviewer acceptance.

| Actual artifact / receipt | SHA-256 |
| --- | --- |
| HDF5 candidate | `f193d8d47f0a3054302b4b6656a799cb8d8905f93262b8b3ca9135dbcce1f08f` |
| Output manifest | `3779b712bb4988c1779f2c1d196e6819840e217253763224cd7a8471086b1ee1` |
| Explicit local recipe | `e867afdf9f5982f696093d844f0aeca7748d343bcc4bff98db23fcfd98eda639` |
| Materializer source | `a804216325af8b5c740b824b8756598fccc2f01079e5a07591f38e24b72156e1` |
| Independent verifier source | `71dc2512e5b9a33a1eedf0cac6d7528e8dfbd6efed14d7424f7fe2e0336c0b0c` |
| Independent every-field receipt | `20a3658110f0b77a30aa0c1a1b02f9b5c76400bd633e4b6660cfabd01313562d` |

The local recipe/manifest carry the absolute resolver paths, original-state
selection ancestry and the new label's completed reference/execution parents.
The execution report pins their exact public digest identities. Raw vectors and
private resolver paths are not redistributed in this card. The first attempt's
pre-output locator refusal and RHS-DATA-R3 red→green regression remain preserved;
the second materialization attempt made the single retained candidate using the
unchanged recipe. No producer or comparator repeat occurred.

## Governed Use

The maintainer authorizes narrow Phase 1 S01–S03 work and the exact D-020 pilot;
this work adds no physical evaluations. The
[parent provenance record](../phase1/PARENT_PROVENANCE.md) records attributed
production roles and Chimera lineage. Exact historical run/build association,
formal custodianship, reuse/release license and sensitivity determination remain
unresolved. Software publication does not authorize dataset redistribution.
Original raw data/reference projects and earlier artifacts remain immutable.
Broader conversion, regeneration, training and deployment require separate
authority. Humans retain scientific acceptance and every merge decision.

## AI Usable

All scientific masks are false with separate state/RHS/energy/rollout reasons.
Engineering materialization and coefficient-conditioned numerical verification
cannot turn them positive. Potential future use starts with full-state identity
and instantaneous RHS, contingent on accepted scientific membership/reference
accuracy. No split is embedded, no preprocessing fitted, no model trained and
no final test consumed. D-018's multi-trajectory training and defensible grouped
holdout investigation remains open; the pilot does not freeze a primary role.
Future qualification requires explicit acceptance and a new identified artifact
or overlay preserving this quarantine. Energy and rollout need their own later
contracts and evidence. No model or agent card/results are invented.

Change log: **0.2.0, 2026-11-17** — recorded completed pilot evidence, actual
quarantined HDF5/manifest identity and independently implemented all-field checks;
all scientific masks remain false. Preserved the first pre-output refusal and
RHS-DATA-R3 zero-padded locator repair. Focused independent review and human
acceptance/merge remain pending. **0.1.0, 2026-11-17** — new narrative card and materialization contract,
prepared with `gpt-6.1-sol` High; subsequent RHS-DATA-R1/R2 repairs add actual
execution-receipt closure and strict runtime-library identities. Original review
findings remain preserved on PR #25; no historical review approval is inferred
for subsequent artifact/card updates.
