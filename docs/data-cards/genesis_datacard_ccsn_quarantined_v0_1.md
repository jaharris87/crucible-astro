# Datacard for the quarantined CCSN three-pair extraction

Card version **0.5.0**, 2026-11-17. Local dataset ID
`ccsn-three-pair-quarantined`, exploratory dataset version **0.1.0**.
No public dataset release. **No qualified training or reference records.**
The bounded artifact was actually extracted and checked; reader/card engineering
integrated through [PR #13](https://github.com/jaharris87/crucible-astro/pull/13) at `099d21e`.

Living narrative draft using the six adaptable capability sections of the official
Genesis data-card template **v2.0.0**; see [released-template evidence](../phase1/GENESIS_GUIDANCE.md).
Formal custodianship, rights, sensitivity and generating provenance remain
incomplete. No full YAML/schema conformance or machine validation is claimed.

## Machine Usability Snapshot

| Capability | Current support / limitation |
| --- | --- |
| Discoverability | Public description; local artifact only, no catalog record |
| Accessibility | Explicit local resolver; no public data endpoint/access grant |
| Interoperability | Named HDF5 arrays and JSON identity/recipe manifest; one supported layout |
| Reusability | Reproducible bounded ingestion recipe; physical qualification remains open |
| Governed Use | Maintainer-authorized quarantine; dataset rights/release status unknown |
| AI Usability | All state/RHS/energy training and rollout-reference eligibility false |
| License clarity | No established dataset license; software BSD-3-Clause does not cover data by inference |
| Fixity / context | Raw pair/header/record and output digests retained locally; scientific provenance unknown |

## Discoverable

Purpose: make exactly the three audited binary/text pairs inspectable through a
strict reader while preserving their scientific exclusions. Keywords: CCSN, XNet,
quarantined ingestion, molar abundance, derivative provenance. This is purposive
structural sampling, not representative coverage or a benchmark. It contains
1384 saved records: 3 initial, 1185 explicitly marked NSE and 196 other rows,
all with scientific eligibility false. [Coverage/benchmark preparation](../phase1/BENCHMARK.md)
reports observed T/rho ranges and the missing grouping/qualification gates. The parent is
[ccsn-raw-candidate](genesis_datacard_ccsn_raw_candidate.md), with the
[S01 audit](../phase1/S01_AUDIT.md) supplying bounded layout evidence.
No model, measured scientific accuracy or speedup is associated with this dataset.

## Accessible

The artifact is local HDF5 plus JSON. Exact raw identities, locators, selected
record ordinals, recipe and output checksums remain in ignored storage. There is
no public data download, DOI, catalog submission or redistribution grant. Access
requires existing authorization from the maintainer and eventual custodian.
Neither the public card nor local availability establishes public data rights.
No real records or private fixtures are included in the repository/CI.

## Interoperable

The [S02 reader contract](../phase1/S02_READER.md) specifies the supported
little-endian record layout, explicit units, exact identity/order checks, reliable
companion alignment and HDF5 field dictionary. Original binary64 values and
ordered Z/A are retained without conversion. Species are not relabeled from
malformed repeated condensed headings. Flux values stay in the unchanged raw
parents; framing, dimensions and endpoints participate in strict checks.

Stored derivative and energy names explicitly say `unqualified`. Internal dt is
not the saved-output interval; energy is the inspected source's internal-step
mass-excess diagnostic, not deposited heating. The source-to-generating-run link
and sufficient historical physical conditioning remain unknown. D-019 accepts
a separate pinned native pointwise reference using T9/rho and composition-derived
`Ye=sum(Z*Y)/sum(A*Y)`; it does not retroactively qualify these stored labels.
No fixed Ye is imposed. Initial and explicit NSE exclusions are separate
from ordinary accepted-state RHS alignment and provenance exclusions.

## Reusable

The manifest binds dataset/version, raw parents and ordinal membership, ordered
species, extractor source/configuration hash, software versions, acceptance
reference and output digest. Raw hashes are checked before and after extraction.
The committed source/lock accompanies the local recipe. Exact original producer
source/build/input association, accepted related-run/trajectory-family grouping, rate/mass/weak/neutrino
input identity, convergence and physical reference accuracy remain unverified.
A structurally readable row is not scientifically qualified. Every scientific
eligibility mask remains false, including ordinary finite values. No numerical
scientific acceptance threshold is inferred from these files.

## Governed Use

The maintainer accepted this narrow ingestion/extraction scope under
[issue #11](https://github.com/jaharris87/crucible-astro/issues/11). Producer roles are now attributed by the maintainer in the linked parent record;
formal custodianship, institutional release, reuse license and sensitivity
determinations remain undocumented. This original software/card publication does not
authorize dataset redistribution. Original raw data/reference projects are unchanged.
Bulk conversion, regeneration/producer execution, model training, deployment and
scientific acceptance require separate authority/evidence. Human merge decisions
and independent exact-candidate review still apply.

## AI Usable

D-018 requires a multi-trajectory training pool and defensible grouped holdouts;
A/B/C are audit aliases, not assigned partitions. Each qualified saved state
would be an individual pointwise example, with many correlated examples per
trajectory. Coverage needs full composition and conditions, not Ye alone.
D-019 accepts a new pinned pointwise numerical-reference contract, with energy/
rollout targets excluded. D-020 subsequently authorizes only the exact
5,157-state pilot build/run; further calls, actual reference verification and
scientific qualification remain separately gated. This does not qualify this raw/quarantined artifact
or change any immutable bytes or masks. See [accepted decisions](../DECISIONS.md)
and the [current benchmark investigation](../phase1/BENCHMARK.md). The
[380-history expansion](../phase1/PRIMARY_EXPANSION_AUDIT.md) and prepared
5,157-state pilot inputs are separate audit/preparation products, not revisions
of this immutable three-pair dataset or an accepted primary split. The
[pinned-reference scope](../phase1/RHS_REFERENCE_SCOPE.md) separates entry
provenance and numerical verification from upstream rate re-evaluation.

The maintainer has identified the single parent and production roles; see
[parent evidence](../phase1/PARENT_PROVENANCE.md). An external local provenance
overlay/card records that later metadata, while immutable HDF/manifest unknown-parent
fields preserve extraction-time status. No scientific eligibility changed.

Current artifact use is local structural investigation only. State training,
instantaneous RHS training, energy training and rollout-reference use are all
unqualified. Unknown generating provenance/conditions affect every row; initial,
NSE and ordinary rows retain additional distinct reasons. No preprocessing is
fitted, no split or final-test partition is embedded and no model is trained.
S03 partitions need recovered grouping and their own acceptance; fitting later
preprocessing must use training membership only. No scientific result is claimed.

Change log: **0.5.0, 2026-11-17** — linked the separate primary expansion,
source Ye and reference-scope clarification; dataset version, bytes and scientific
masks remain unchanged. **0.4.0, 2026-11-17** — recorded accepted numerical-reference
contract, execution deferral and multi-trajectory benchmark direction; artifact
identity and scientific eligibility unchanged. **0.3.0, 2026-11-17** — added subsequent parent/role attribution
without rewriting artifact metadata or eligibility. **0.2.0, 2026-11-17** — added actual bounded coverage/integration
and S03 decision-sheet link; card version changes, dataset version stays 0.1.0.
**0.1.0, 2026-11-17** — initial derived narrative card and bounded
reader/extraction contract, prepared with `gpt-6.1-sol` High. The live issue/PR retains actual extraction/check, independent initial/freshness
reviews, concrete delegated human merge and passing merged-result receipts. Scientific qualification and rights remain open.
