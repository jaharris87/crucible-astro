# Datacard for the CCSN raw candidate collection

Last updated: **2026-11-17**. Card version **0.5.1**, dataset local alias
`ccsn-raw-candidate`; no public dataset release/version has been established.
**Living narrative draft; not qualified for training, reference evaluation or
final-test use.** This card describes raw outputs, not a derived training dataset.

Uses the adaptable narrative portion of the official Genesis data-card template
**v2.0.0**, retrieved from the official release; [source/version/access evidence](../phase1/GENESIS_GUIDANCE.md).
The full machine metadata are incomplete (notably formal custodianship, rights, sensitivity determinations and generating provenance); no YAML/schema
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
about 220 GB including other files. The initial reader artifact contains three
pairs (1,384 records). The separate [fixed primary expansion](../phase1/PRIMARY_EXPANSION_AUDIT.md)
now audits all 30,472 ordinary full-Y records in 380 familiar-layout histories,
including the retained 80-history pilot. No representative CCSN or NSM/r-process
coverage or qualified label count follows from that expansion.

The maintainer identifies the parent as **Chimera D9.6-SN160-3D**, used in
Sandoval et al. (2021) and Neopane et al. (2026). [Original-paper checks and
production attribution](../phase1/PARENT_PROVENANCE.md) distinguish reported
lineage from independently corroborated model facts. This is one identified
hydrodynamic parent, not simulation-independent coverage from two publications.

The maintainer attributes simulation production to Eric Lentz; XNet source to
Raph Hix and J. Austin Harris; workflow tooling to Andre Sieverding; and this
post-processing execution to James Ternullo. Formal data-custodian/retention and
reuse/release documentation remain unestablished. Participation in the same
Genesis ENACT-AI research group does not supply an inferred dataset license.

Recovered controls, network/mapping candidates and selected input slices
corroborate all three pairs' initial time/T/rho. A/B use the inspected NSE
initialization fallback; C's mapped/normalized initialization is reproduced to
floating-point precision. The dangling extrema link is not a demonstrated runtime
dependency. Candidate processed tables have zero active neutrino reactions;
historical generating inputs/build association remains distinct. A separately
reviewed three-state fresh-RHS diagnostic is complete, with all scientific masks
still false; see [its evidence](https://github.com/jaharris87/crucible-astro/pull/16).

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
settle generating-build association. Native composition-derived Ye is
`sum(Z*Y)/sum(A*Y)`; raw charge/baryon moments remain separate diagnostics and Y
is never normalized. Historical proxy-screen receipts are preserved. Optional formats/batching must not be inferred
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
deposited heating or an instantaneous energy RHS. Original raw data have not been
cleaned, clipped or physically converted. The separate quarantined HDF5 extraction and authorized three-state RHS diagnostic
are complete; neither regenerates original trajectories or performs an NSE solve.
No bulk collection conversion has occurred.

Related software is the inspected XNet snapshot; the CRUCIBLE production reader
is in [merged PR #13](https://github.com/jaharris87/crucible-astro/pull/13), integrated as quarantined ingestion only. The [audit](../phase1/S01_AUDIT.md) links source locations,
original scientific context and retained local manifests/oracles. There is no
associated trained AI model. The [completed bounded extraction](genesis_datacard_ccsn_quarantined_v0_1.md)
has raw-parent checksums, record identities, explicit masks and its own linked
card. Its original [extraction proposal](../phase1/S02_EXTRACTION_PROPOSAL.md) is
retained; the actual artifact is not a qualified training subset.

## Reusable

The [initial 83-pair reconnaissance](../phase1/MULTITRAJECTORY_AUDIT.md) and
[fixed expansion](../phase1/PRIMARY_EXPANSION_AUDIT.md) are separate evidence
products. The initial 80 familiar histories / 5,157 table-screened states remain
a qualification pilot. The combined 380 familiar histories have 24,314 source-table
candidates, all scientifically unqualified; 15 selected shorter-layout files
remain quarantined. Measured positions/categories and source-formula Ye checks
support a new benchmark proposal, not accepted physical families or partitions.
The [signed-zero reader repair](../phase1/S02_READER.md) preserves binary energy
bits. No bulk conversion or new training artifact was produced.

The [remaining primary reference proposal](../phase1/PRIMARY_REFERENCE_PROPOSAL.md)
prepares **19,157** new candidate states in **300** histories plus **two explicit
pilot repeat controls**: **19,159 proposed calls** across 301 histories. With
retained pilot labels, the unique input union remains 24,314 states / 380 histories.
Input-only preparation/checks are complete; D-020's pilot call authority is
exhausted and no primary build/run or scientific eligibility is authorized.
[Issue #26](https://github.com/jaharris87/crucible-astro/issues/26) tracks fresh
source/input review and the separate later execution decision. Original raw,
pilot and preparation evidence remain immutable.

Current eligibility is **limited to authorized structural investigation**.
All 1,384 records in the initial three-pair artifact remain unqualified for
state training, instantaneous RHS, energy targets and rollout reference use. Reason sets differ: unknown
provenance affects all; 3 initial and 1185 explicitly flagged NSE rows have invalid
RHS labels; 196 others still lack accepted-state alignment and conditions evidence.
See the [eligibility table](../phase1/S01_AUDIT.md#physical-interpretation-and-exclusions)
for separate uses rather than a single usable/unusable score.

Raw integrity is represented by a local filename/size inventory and selected
payload/source checksums. Full collection content hashing, missing/failed trajectory
counts, representative physical coverage, historical rate/mass/build identity,
accepted physical grouping, reference verification and storage/recovery stewardship
remain open. Selected canonical particle identities and measured position histories
are now numerically associated; this does not prove independent families. Passing structural
checks does not establish physical validity. Do not cite this card as evidence of
scientific qualification; no dataset citation or license can yet be supplied.

Maintain this card with the audit/manifest and benchmark gates. A later derived
dataset gets its own version and card linking exact raw parents, reader/recipe,
exclusions and acceptance. The audit JSON is an evidence product, not a training
dataset. Card changes are versioned in Git; raw originals stay unchanged.

## Governed Use

The maintainer authorized Phase 1 inspection and portable documentation in the
[execution record](../PHASE_1_AUTHORITY.md). D-017 completed exactly three
reviewed isolated RHS calls and is exhausted. D-019 selects a new native numerical
reference; its [preparation is integrated](https://github.com/jaharris87/crucible-astro/pull/20),
with subsequent D-020 authority limited to the exact 5,157-state pilot build/run.
Permission is not completed execution or scientific qualification. Broader
producer execution, original reference modifications, bulk conversion, data
publication and training remain outside scope. Required dataset ownership/reuse and institutional
release evidence is unknown, not presumed denied or approved. No additional
regulatory classification is inferred here.

Scientific acceptance of subset/conditions/exclusions, energy/reference/tolerances
and benchmark partitions is pending. The maintainer accepted quarantined
three-pair ingestion, the native numerical-reference contract and read-only primary
audit expansion;
[S02 #11](https://github.com/jaharris87/crucible-astro/issues/11) implements that
bounded scope with scientific eligibility false. Every candidate merge requires a concrete human decision after the
adopted review/check cycle. The data-card draft does not replace any of these gates.

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
[pinned-reference scope](../phase1/RHS_REFERENCE_SCOPE.md) records official
rate-entry identity and separates native numerical verification from upstream
nuclear-data evaluation history.

Intended future use is a qualified instantaneous-RHS, full-state starting path
(D-003), subject to physical conditioning and label qualification. Finite-step
prediction needs a separate interval/history contract. **Training, scientific
evaluation and inference use are not qualified now.** No Phase 2 work is authorized.

The [S03 coverage/decision sheet](../phase1/BENCHMARK.md) reports observed ranges
and grouping/eligibility gaps. No benchmark membership, final-test use, preprocessing fit or numerical scientific
tolerance is accepted. Related tracers, snapshots and derived copies must stay
together under a justified grouping rule. The collection has one maintainer-identified
parent; any pilot must be labeled within-simulation exploration and cannot claim
simulation-independent generalization. Sampling bias, unbound generating/history
conditions, NSE/initial placeholders, unmeasured RHS alignment and missing broader
CCSN/NSM coverage prevent general scientific claims. Human review is required.

Change log: **0.5.1, 2026-11-17** — linked the exact remaining-primary
input-only preparation and separate execution gate; raw identity and scientific
eligibility unchanged. **0.5.0, 2026-11-17** — linked expanded state/position coverage,
native Ye formula, integrated reader/reference preparation and official rate-entry
provenance; primary partitions, qualification and data rights remain open.
**0.4.0, 2026-11-17** — recorded accepted numerical-reference
contract, execution deferral and multi-trajectory benchmark direction; artifact
identity and scientific eligibility unchanged. **0.3.0, 2026-11-17** — added maintainer-reported parent/roles,
original-paper corroboration and completed diagnostic status; no qualification
or license inferred. **0.2.0, 2026-11-17** — linked the integrated quarantined
extraction and S03 coverage/decision sheet; raw collection identity unchanged.
**0.1.0, 2026-11-17** — initial raw-collection narrative card from
the official released template; bounded audit and open rights/provenance gates.
Prepared with Codex; source/guidance investigators explicitly `gpt-6.1-sol` High.
No full machine validation or scientific acceptance yet; exact-candidate review
and human integration receipts are retained in [PR #12](https://github.com/jaharris87/crucible-astro/pull/12).
