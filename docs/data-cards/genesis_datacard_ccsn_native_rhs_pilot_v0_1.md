# Datacard for the quarantined native-RHS CCSN pilot

Card version **0.1.0**, 2026-11-17. Intended local dataset ID
`ccsn-native-rhs-pilot-quarantined`, dataset version **0.1.0**.
**Preparation draft: the real materialization gate remains pending.** No new
HDF5 artifact identity is claimed in this revision. No public dataset release,
qualified training records, scientific performance result or trained model exists.

This living narrative draft follows the six adaptable capability sections of the
official Genesis template **v2.0.0**, pinned in
[guidance evidence](../phase1/GENESIS_GUIDANCE.md). Required custodian, rights and
sensitivity fields remain incomplete. No YAML/schema conformance, machine
validation or catalog submission is claimed. Card version and dataset version
are independent; replace pending artifact statements only with actual receipts.

## Machine Usability Snapshot

| Capability | Current support / limitation |
| --- | --- |
| Discoverability | Public draft description; no released dataset or catalog record |
| Accessibility | Explicit local recipe; no public endpoint or access grant |
| Interoperability | Documented HDF5/JSON contract for one fixed v2 reference format |
| Reusability | Source-bound materializer; real output and independent verification pending |
| Governed Use | Authorized bounded quarantine; dataset rights/sensitivity unresolved |
| AI Usability | State, RHS, energy and rollout eligibility all false |
| License clarity | Software BSD-3-Clause; no inferred dataset license |
| Fixity / context | Explicit parent digests required; new output digest pending |

## Discoverable

Purpose: preserve the exact original full 160-species states alongside newly
evaluated pointwise native XNet RHS values for scientific inspection. This is a
separate derived dataset from the
[raw CCSN candidate](genesis_datacard_ccsn_raw_candidate.md) and
[three-pair quarantine](genesis_datacard_ccsn_quarantined_v0_1.md).
The intended pilot has 5,157 source-table candidate states from 80 histories;
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
finite materialization of its verified outputs. The final manifest must bind
original-state raw-ts/raw-ev/payload/input-state ancestry separately from the
new label's source preparation, generating executable, retained result and
completed comparator. It records recipe/source/software identities and output
digest. These new-reference identities do not prove the historical generator.

The full coefficient-conditioned comparator and retained receipts are a hard
precondition for the real candidate. Finite physical output and exact retained
controls alone are insufficient. Even a complete comparator establishes bounded
numerical assembly under declared coefficients, not rate/EOS/astrophysical
accuracy. Actual HDF5/manifest identities and independent full-field/bitwise
verification remain pending here. Scientific tolerance/accuracy acceptance and
sufficient coverage remain open; no missing evidence is relabeled as successful.

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

Change log: **0.1.0, 2026-11-17** — new narrative card and materialization contract,
prepared with `gpt-6.1-sol` High; actual real artifact and review gates pending.
