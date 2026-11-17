# Datacard for the CCSN raw candidate collection

Last updated: **2026-11-17**. Card version **0.1.0**, dataset local alias
`ccsn-raw-candidate`; no public dataset release/version has been established.
**Living narrative draft; not qualified for training, reference evaluation or
final-test use.** This card describes raw outputs, not a derived training dataset.

Uses the adaptable narrative portion of the official Genesis data-card template
**v2.0.0**, retrieved from the official release; [source/version/access evidence](../phase1/GENESIS_GUIDANCE.md).
The full machine metadata are incomplete (notably original creators/custodian,
rights, sensitivity determinations and generating provenance); no YAML/schema
conformance or validation is claimed. Unknown does not mean not applicable.

## Machine Usability Snapshot

| Template capability / support | Current evidence |
| --- | --- |
| Discoverability | Intended: Yes; this draft describes a local candidate, not a catalog registration |
| Accessibility | Intended: Yes within authorized collaboration; no public data endpoint or established access grant |
| Interoperability | Intended: Yes; one small binary scope audited, wider variants unknown |
| Reusability | Intended: Yes; provenance and qualification gates remain open |
| Governed Use | Intended: Yes; dataset rights/release authority unresolved |
| AI Usability | Intended: Yes eventually; no qualified training/evaluation labels now |
| License clarity | No dataset license/redistribution evidence established |
| Checksum / fixity | Selected raw/source artifacts hashed locally; whole collection not payload-hashed |
| Semantic context | Partial; [audit](../phase1/S01_AUDIT.md) separates observations from gaps |

## Discoverable

Purpose: investigate whether maintainer-supplied CCSN post-processing outputs can
support reproducible nuclear-network surrogate benchmarks. Keywords: CCSN,
XNet, reaction network, particle trajectory, abundance, provenance audit.
No model has been trained and no scientific accuracy/speedup is reported.

The collection contains raw XNet binary time series, companion text diagnostics,
some HDF-named products, source/build artifacts and setup scripts. The filename
suggests a particular source simulation/network; that is a lead, not verified
parent provenance. The lightweight inventory found 42,362 binary/text pairs,
about 220 GB including other files. Only three pairs (1384 records) were decoded
for this audit. This is not representative coverage of CCSN or NSM/r-process.

The maintainer supplied the local collection. Original producer authors, dataset
creator/contributors, generating facilities/funding, timestamps and responsible
data custodian remain to be established; repository copyright/sponsorship cannot
be substituted for dataset ownership. Small candidate control/network/mapping files were subsequently recovered from
the maintainer-supplied original remote location. Initial composition/history
targets exist there; an extrema link is dangling. Their historical run
association remains unproven. For one audited tracer, recovered initial abundances are all zero: the inspected
source therefore uses NSE initialization even below its separate NSE-advance
temperature threshold. Initial composition Ye agrees with the appended initial
Ye, which differs from the history Ye. No initial NSE solve was reproduced.
These are distinct source-conditioned quantities, not a fixed-Ye contract.
The current bundled source is a modified
XNet snapshot, not a proven generating build. See the [provenance gaps](../phase1/S01_AUDIT.md#producer-evidence-and-missing-associations).

This portable card is authorized for public project documentation. Dataset
sensitivity/release markings and reuse rights have not been established by the
audit. Local availability and a public card do not make the underlying data public.

## Accessible

The raw data remain at a maintainer-controlled local location, excluded from Git.
Authorized local work uses the ignored reference locator and explicit path
configuration; paths and unapproved metadata are omitted here. No public download,
DOI for this collection, automated access service or retention agreement exists
in the project record. Contact the project maintainer through the existing
collaboration to determine access and the responsible custodian.

Neither project BSD-3-Clause licensing nor the Phase 0B bootstrap release
approval establishes dataset redistribution rights. No raw records or real-data
fixtures accompany this card. External sharing requires the missing rights evidence.

## Interoperable

The bounded binary audit verified Fortran sequential framing, six metadata
records, 160 ordered `(Z,A)` species and 909 flux entries in one observed layout.
The [field dictionary and offsets](../phase1/S01_AUDIT.md#verified-layout-bounded-to-these-files)
define time, T9, density, internal step, stored energy, Y, flux and stored
derivative blocks. Source indicates s, GK, g/cm³, molar abundance Y and nominal
erg/g/s for the internal-step mass-excess rate; these source meanings do not
settle generating-build association. Optional formats/batching must not be inferred
from these files. Isomers/rates/masses are not identified by `(Z,A)` alone.

Initial and NSE derivative records are unavailable as RHS labels. The remaining
stored derivatives precede the final implicit Newton correction in the inspected
source. Binary records lack explicit NSE status; companion flags require verified
association. A zero derivative alone is never a missing-value or regime code.
Unknown provenance and conditions remain explicit unknowns. Source can consume neutrino histories, but recovered candidate processed tables
specify zero active neutrino reactions. That is conditional evidence, not proof
of the generating inputs. Weak reactions remain active; fixed Ye is not justified.

Condensed species output has repeated identities in inspected text and cannot be
used as an authoritative multi-species selection. Full binary Y has a separate
ordered species header. Source energy is an internal-step diagnostic, not
deposited heating or an instantaneous energy RHS. No raw data cleaning, physical
conversion, clipping, producer execution or bulk extraction has been performed.

Related software is the inspected XNet snapshot; the CRUCIBLE production reader
is in [draft PR #13](https://github.com/jaharris87/crucible-astro/pull/13), not integrated. The [audit](../phase1/S01_AUDIT.md) links source locations,
original scientific context and retained local manifests/oracles. There is no
associated trained AI model. A [bounded derived-extraction proposal](../phase1/S02_EXTRACTION_PROPOSAL.md)
describes a future HDF5/JSON artifact with raw-parent checksums, record identities,
explicit masks and a separate linked card. It is not a qualified subset yet.

## Reusable

Current eligibility is **limited to authorized structural investigation**.
All 1384 inspected records remain unqualified for state training, instantaneous
RHS, energy targets and rollout reference use. Reason sets differ: unknown
provenance affects all; 3 initial and 1185 explicitly flagged NSE rows have invalid
RHS labels; 196 others still lack accepted-state alignment and conditions evidence.
See the [eligibility table](../phase1/S01_AUDIT.md#physical-interpretation-and-exclusions)
for separate uses rather than a single usable/unusable score.

Raw integrity is represented by a local filename/size inventory and selected
payload/source checksums. Full collection content hashing, missing/failed trajectory
counts, physical coverage, rate/mass identity, parent/tracer mapping, reference
convergence and storage/recovery stewardship remain open. Passing structural
checks does not establish physical validity. Do not cite this card as evidence of
scientific qualification; no dataset citation or license can yet be supplied.

Maintain this card with the audit/manifest and benchmark gates. A later derived
dataset gets its own version and card linking exact raw parents, reader/recipe,
exclusions and acceptance. The audit JSON is an evidence product, not a training
dataset. Card changes are versioned in Git; raw originals stay unchanged.

## Governed Use

The maintainer authorized Phase 1 inspection and portable documentation in the
[execution record](../PHASE_1_AUTHORITY.md). Subsequent D-017 permits only a
reviewed isolated three-state RHS diagnostic, not data regeneration. Broader
producer execution, original reference modifications, bulk conversion, data
publication and training remain outside scope. Required dataset ownership/reuse and institutional
release evidence is unknown, not presumed denied or approved. No additional
regulatory classification is inferred here.

Scientific acceptance of subset/conditions/exclusions, energy/reference/tolerances
and benchmark partitions is pending. The maintainer accepted only a quarantined three-pair reader/local extraction;
[S02 #11](https://github.com/jaharris87/crucible-astro/issues/11) implements that
bounded scope with scientific eligibility false. Every candidate merge requires a concrete human decision after the
adopted review/check cycle. The data-card draft does not replace any of these gates.

## AI Usable

Intended future use is a qualified instantaneous-RHS, full-state starting path
(D-003), subject to physical conditioning and label qualification. Finite-step
prediction needs a separate interval/history contract. **Training, scientific
evaluation and inference use are not qualified now.** No Phase 2 work is authorized.

No benchmark membership, final-test use, preprocessing fit or numerical scientific
tolerance is accepted. Related tracers, snapshots and derived copies must stay
together under a justified grouping rule. The number and identity of independent
parent simulations remain unverified; if only one is established, any pilot must
be labeled within-simulation exploration. Sampling bias, unbound generating/history
conditions, NSE/initial placeholders, unmeasured RHS alignment and missing broader
CCSN/NSM coverage prevent general scientific claims. Human review is required.

Change log: **0.1.0, 2026-11-17** — initial raw-collection narrative card from
the official released template; bounded audit and open rights/provenance gates.
Prepared with Codex; source/guidance investigators explicitly `gpt-6.1-sol` High.
No full machine validation or scientific acceptance yet; exact-candidate review
and human integration receipts are retained in [PR #12](https://github.com/jaharris87/crucible-astro/pull/12).
