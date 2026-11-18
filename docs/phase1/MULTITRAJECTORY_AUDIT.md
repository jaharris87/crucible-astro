# Multi-trajectory reconnaissance and grouping gaps

2026-11-17 under [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10)
and [S03 #15](https://github.com/jaharris87/crucible-astro/issues/15).
**Read-only reconnaissance, not a training dataset, sufficient coverage claim,
accepted partition or authority for additional XNet execution.** D-018 requires
multiple trajectories in the training pool; D-019 accepts the new pointwise
reference contract while explicitly deferring execution.

## Why the audit expanded

A/B/C are aliases for three initial format-audit examples. They are neither ML
terminology nor accepted training/validation/test assignments. Each qualified
saved state is an individual pointwise example; one history can contribute many
correlated examples. The maintainer correctly required a multi-trajectory training
pool whose coverage supports the intended held-out task. The earlier suggestion
of one trajectory per role was premature and is superseded.

C's observed Ye was outside A/B's ranges. That established a difference relative
to those two examples only. It did not establish C as out of domain relative to
a larger pool or justify a primary benchmark. Its eventual role follows the
broader full-state/condition and grouping evidence.

## Fixed reconnaissance recipe

The existing local inventory has 42,362 filename pairs across 28 populated slabs.
Within each populated slab, sort by `(binary byte size, relative path)` and take
the minimum, lower median and maximum ranks, deduplicating. This gives 82 pairs;
add original C as an anchor for **83 distinct pairs**, including original A/B/C.
This samples organizational/output-length diversity, not representative physics.

Read six metadata records and framed scalar headers via seeks, plus complete
companions. Check framing/counts, ordered species, all six scalar columns,
explicit NSE and observed endpoints. For familiar 9876-byte payloads only,
inspect up to eight unique ordinary noninitial/non-NSE states: first/last,
earliest temperature/density minima/maxima, and quarter/three-quarter ordinal
positions. Deduplication gives **402 states across 80 histories**. No Y payloads
are read from unfamiliar layouts. No reader extension or new HDF5 extraction
occurs. Retain exact membership, consumed segments, hashes and recipe locally.

## Observations

| Observation | Count |
| --- | ---: |
| Scalar-aligned saved records | 78,168 |
| Initial records | 83 |
| Explicit NSE records | 71,522 |
| Other noninitial/non-NSE records | 6,563 |
| Familiar 9876-byte layout | 80 pairs / 76,568 records |
| Quarantined 8596-byte layout | 3 pairs / 1,600 records |
| Ordinary records in familiar layout | 6,433 |
| Sampled composition states / components | 402 / 64,320 |

All inspected framing and six-column companion checks passed. Three selected
pairs from one collection region have 8596-byte payloads, 1280 bytes shorter than the supported
layout. Size metadata flags all 177 binaries in that region as incompatible with the
current reader layout; only three were inspected here. The width is consistent
with a missing appended 160-component binary64 block, but this is **not an
accepted field interpretation**. Keep that variant quarantined pending its own
format/source audit. Do not assume every `ts_` file supplies stored RHS labels.

Across all scalar records, T9 reaches 40.5691 GK and density 3.8134×10¹⁰ g/cm³;
these include unqualified/NSE states. Eighty-one trajectories end at 100 s and
two near 0.488127 s. Endpoints do not establish successful completion or an
accepted rollout horizon.

| Descriptive quantity in the 402 sampled states | Observed range |
| --- | --- |
| T9 | 0.02205466–8.91434632 GK |
| Density | 0.05874555–2.29679342×10⁹ g/cm³ |
| Composition-derived Ye | 0.36841656–0.58275567 |
| `sum(A_i*Y_i)` | 0.999999869885819–1.000000126871419 |

All sampled Y components are finite/nonnegative; maximum observed absolute baryon
residual is 1.301141812071194×10⁻⁷. These observations set no scientific tolerance.
Using the existing FFN table screen descriptively gives 318 inside / 84 outside;
each of the 80 histories has at least one inside sample. These are neither
qualified labels nor an approved evaluation list.

## Joint composition and conditions

Compare full 160-component **unnormalized** `X=A*Y` using L1 distance, retaining
T/rho/time alongside each match. No fitted representation or preprocessing is
introduced. Nearest-other-file sampled composition distances span approximately
7.9×10⁻¹⁴–0.6974 (median 0.05114); no grouping or physical threshold is inferred.

C's first sampled state has distance 7.9159×10⁻¹⁴ to another file's sampled
composition, with nearly coincident T/rho/time. Across its six sampled states,
nearest-other-file distances range approximately 7.9×10⁻¹⁴–4.11×10⁻⁴. Thus C is
not inherently outside this broader pool merely because its Ye differed from
A/B. Nearly coincident samples also warn against treating filenames as independent
information. Similar starting states do not prove identical full histories or
common physical lineage; distinct histories can legitimately share initial
composition. Neither these distances nor marginal ranges demonstrate sufficient
joint training coverage.

## Physical identity: verified storage mapping and remaining gaps

The inspected bundled `postp.f90:234–236,290–313` and
`model_input_pdata.f90:213–222,575–588` use output zone `k` as pdata particle-axis
index `k-1` and literal inab dataset `Abundance/k`. Pdata row/column reads are
commented out at `model_input_pdata.f90:128–139`. Three recovered samples agree
with their slab/zone labels; this does not verify every candidate's physical ID.
Separate workflow scripts use differing indexing conventions. Preserve namespace
and indexing base rather than promoting filenames to authoritative tracer IDs.

Read-only CHIMERA reference implementations show a possible mapping route:
`HDF_IO_MODULE.f90:1155–1157` writes particle dimensions; analysis
`particle_module.f90:591–601` derives row/column labels. Its read path allows an
`override_row`; seeding supports Fibonacci and regular angular layouts. These
are source observations, not recovered generating configuration. A 5001-element
axis does not prove the seeding layout, geometry, independence or family groups.
Eulerian cell locations and interpolated enclosed mass are not stable tracer IDs.

The inspected initial-abundance writer groups exact first-frame radii and can
hard-link abundance datasets. Shared composition/link identity does not prove
identical histories; zero-abundance NSE initialization is especially unsuitable
as a duplicate-history test. The later metadata addendum below recovers selected object/link identities;
generating writer/slab-converter association remains unresolved.

The metadata addendum below recovers row/column arrays and selected first-frame
geometry for this pool; actual generating source/configuration lineage remains
unresolved. Inspect links/relationships and the actual slab-conversion
mapping. State specific unavailable evidence rather than assuming physical
families from neighboring numbers. Any grouping rule and within-parent statistical
claim require human acceptance before final partitions.

## Reproducibility, limits and next gate

Ignored local artifacts are bound as follows; exact private membership and raw
records are not published:

| Artifact | SHA-256 |
| --- | --- |
| Audit source | `9d32122962f50cc8383eabac1a365ae88994a0d22a0103da34fd1f4bf721b2d2` |
| Exact membership | `87ede3f2df908cc540ddcca4b6be106aee9e20e9bb8a4b5ab76a2296808dcba3` |
| Report and recipe | `95c6c0a603612740f9f776e4d435e803522f3e6c6323f51258513483e48a5106` |
| Joint-summary source | `e97f6fcaf64046e1158f9edf3582a61652d6d6108305a23140c5face0f0a8426` |
| Joint summary | `ea282047e3160e8940cdd01e48246362a02b53e1c0ae3a16d2e39f6b2f775bbe` |

Consumed binary segments were reread unchanged; file identity/stat fields and
complete companions were unchanged. **Unread payloads were not fully hashed**;
this is segment-bound reconnaissance, not fresh full-file fixity. Approximately
5.46 MB of binary segments and 14.87 MB of companions were read. No raw/reference
edits, producer/Fortran/model execution, training dataset or HDF5 extraction
occurred. Only separate ignored audit artifacts were written.

The sample is purposive and sparse; unsampled histories/states, failed/short
outputs, unfamiliar layouts and wider CCSN/NSM coverage remain gaps. Define the
intended region and assess a pooled multi-trajectory candidate set with accepted
lineage/groups before choosing memberships. Then present a revised exact
reference-evaluation proposal. Execution remains deferred, scientific eligibility
zero, and Phase 1 incomplete.

## Complete ordinary-state audit of the fixed pool

A separate read-only follow-on inspects all **6,433 ordinary, noninitial/non-NSE
states** in the same 80 familiar-layout histories: **1,029,280 Y components**.
The other three files and their 130 ordinary rows remain quarantined. Original
reconnaissance artifacts above are unchanged; this addendum replaces sparse
sampling only for arithmetic on this fixed candidate pool.

All components are finite/nonnegative: 761,988 positive and 267,292 zero. The
existing source-table screen retains **5,157 candidate states across all 80
histories** and excludes 1,276, all below `log10(rho*compositionYe)=1`. Each
history contributes 36–109 inside-screen candidates. These are exact candidate
counts, not accepted training membership or an authorized evaluation list.

| Quantity | All 6,433 ordinary states | 5,157 inside-screen candidates |
| --- | --- | --- |
| Time (s) | 0.414127021–100 | 0.414127021–11.86541195 |
| T9 (GK) | 0.02205466–8.91434632 | 0.10869285–8.91434632 |
| Density (g/cm³) | 0.05874555–2.29679342×10⁹ | 18.56832890–2.29679342×10⁹ |
| Composition Ye | 0.36825298–0.58276703 | Same observed range |
| `sum(A_i*Y_i)` | 0.999999829663290–1.000000216101342 | Same observed range |

Maximum absolute baryon residual is 2.161013414880841×10⁻⁷. No scientific tolerance
is inferred. All 6,433 composition-only and Y+T9+rho binary64 fingerprints are
unique in the bound species/reference namespace. **Zero exact duplicates does
not establish independence or remove near-coincidence evidence.** Time/trajectory
identity stays attached; no near-duplicate threshold or grouping was selected.

| Follow-on artifact | SHA-256 |
| --- | --- |
| All-state audit source | `ab5520b0e765403dc8b589eb163da8355b99297bf7e17f0a3c914fd0eca512ea` |
| Report/per-history profiles | `7b7396a7dc5bab3e0ae9eae99527067291d70550873f9164486b673dba0bf110` |
| Local per-record features/fingerprints | `b223247e156df82211742c1c1c9c58070b0476635cc449021cfe722f47d5a813` |
| Namespace | `df72c4cb7bee0b9a558b8fadea6479e7cd122b7b92bbe6ccb15c9bda552f5b55` |
| Execution receipt | `581bb8c20f37bbd322e1930c3d68631c9a40d3fe9ee4e3cdc83def9dec442209` |

Prior consumed-segment identities reproduce exactly; added Y/header/marker bytes
were reread unchanged, with unchanged companions/stat fields. Unread payloads
were not fully hashed. About 8.23 MB of additional Y bytes were read; no full
vectors, labels, HDF5 extraction or training dataset was produced. The initial
JSON/Python dictionary-key comparison failure was corrected before all-state
processing and retained locally. No producer/model execution occurred.

## Recovered input identity and first-frame metadata

A bounded independent Python/HDF read recovered metadata for all 83 selected
zones across 28 input containers. Every full row-ID array matches its containing
slab label, and every full column-ID array is exactly `1..5001`. The selected raw
zone-to-storage-column association is therefore verified for this finite pool.
Existing category metadata covers all selected keys and agrees with zero-based
`(row-1)*5001+(column-1)`; a separate merged-filename script is one-based. Keep
these namespaces distinct. Categories are existing metadata, not a fresh
classification or proof of the historical script invocation.

All selected first-frame radius/theta/phi/mass-coordinate values are finite.
Selected radius and enclosed-mass bands are disjoint in increasing stored-row
order. This supports preparing an explicit **within-parent stored-row-cohort
proposal**, limited to selected points; it does not prove seeding shells,
independent physical families or neighborhoods. All selected cell-location
vectors are zero, and coordinate attributes do not bind units/frame. Original
seeding configuration, generating revision and actual analysis reshape/slab
conversion provenance were not found by the bounded inventory; existence
elsewhere remains possible.

No selected names share an inab object within the same container. Selected
object link counts are 79×1, 3×2 and 1×5; some links include unselected names.
Shared initial composition or link identity does not prove duplicate physical
histories. Retain these links in lineage investigation without automatically
merging or separating trajectories.

| Metadata artifact | SHA-256 |
| --- | --- |
| Packet manifest and source bindings | `4dae0e5257376afba4ca373264e7688ac0fedd874542220af61de4131922ea17` |
| Selected metadata | `356e6977b58ecf33d691776546381d35d0503e7c4806982c571d6afcd462e455` |
| Aggregate summary | `249d24faf580dd6383df3cea435171f8abcc1d92f4f1f15990cbeba2983e9686` |

File identities/stat fields and selected slices were stable; **no fresh full-parent
HDF hashes were computed**. Thirteen small source files were recovered as bytes,
not imported or executed. Actual Python/HDF runtime, import/DNS failure receipts
and corrected category-table parsing are retained locally. This recovery ran no
XNet, Fortran, original producer scripts, regeneration or model. The separate initial-input addendum below strengthens numerical association;
no physical-family or dataset qualification follows automatically from it.

## Initial-input association addendum

A separate bounded HDF read and independent arithmetic check now bind initial
conditions for the expanded pool: **all 83 raw first-record time/T9/rho triples
match bit-for-bit** to the recovered first pdata frame, using the inspected
`T9 = T * 1e-9` conversion. All 83 extrapolation tau values are positive/finite;
this is not a rollout-horizon or extrapolation-accuracy acceptance.

Seventy native initial abundance vectors are exactly zero and select the
inspected source's NSE initialization fallback. No NSE solve or equilibrium
composition reproduction was attempted. Thirteen nonzero vectors follow name
mapping and retained-mass normalization; independent sequential arithmetic
reproduces all **2,080 emitted initial Y components bit-for-bit**. All thirteen
are familiar-layout files. The three shorter payloads remain quarantined; only
their independently checked scalar prefixes enter the initial-condition comparison.

For all 83 inputs, appended inab Ye differs bitwise from history Ye. Keep these
quantities distinct; neither replaces the accepted reference's composition-derived
Ye. Raw description/path fields are mostly NUL-filled, and one nominal input
locator points elsewhere. Preserve those bytes; do not use the headers as proof
of historical input paths or infer why they differ. Numerical association is
strong evidence but does not prove historical build/run identity or full-history
accuracy.

| Association artifact | SHA-256 |
| --- | --- |
| Selected input slices | `10cb78d7c1a238bbe23f905098ec1a119bc722c0f0dadf1ec5beefed7b76cfa6` |
| Independent comparison | `5dcd9f1879e2f863cb7d4f07ae918ef879b4be04d52cc30c4de421782e632ac7` |
| Addendum manifest/readers/receipts | `1eaf3b1f6b8f400a74d6a18f792039383aa12ed3a237d002206fa05a21b7e19a` |

The earlier packet's 31 manifest entries remain byte-identical. The separate
addendum retains independent reader/comparison sources, connection/runtime and
slice identity receipts; it makes no fresh full-parent HDF hash claim. No
original scripts, NSE/Fortran/XNet, models or reference kernels were executed.
Scientific eligibility and the execution deferral remain unchanged.

## Illustrative cohort split: diagnostic only

To make the grouping/coverage tradeoff reviewable, a private deterministic
proposal keeps each stored-row cohort whole. Range-end and existing category
anchors go to training; the remaining sorted cohorts are interleaved into roles.
This is a **data-specific diagnostic rule, not established ML terminology, an
accepted family definition or a recommended primary split**. No labels or fitted
preprocessing enter the construction.

| Illustrative role | Cohorts | Histories | Candidate states |
| --- | ---: | ---: | ---: |
| Training | 19 | 56 | 3,526 |
| Validation | 4 | 12 | 769 |
| Test | 4 | 12 | 862 |
| Total | 27 | 80 | 5,157 |

The proposed membership is complete/unique and disjoint by its **proposed**
cohort/history/raw-record keys, and invariant to reversed/cyclic input order.
These checks validate a private candidate construction, not final S03 partitions
or physical independence. Initial A/B/C examples receive no special allocation.

Marginal T/rho/Ye overlap is generally strong, but one illustrative test state
has T9 8.914346 versus training maximum 8.831011 GK. Full-state comparisons expose
additional differences:

| Descriptive distance to candidate training points | Validation median / max | Test median / max |
| --- | --- | --- |
| Nearest full-160 unnormalized X L1 | 0.07970 / 0.46470 | 0.09442 / 0.78415 |
| Nearest unweighted log(T9)/log(rho) L2 | 0.006245 / 0.06664 | 0.007614 / 0.14681 |
| X L1 at that nearest-condition point | 0.74731 / 2.00000 | 1.10151 / 2.00000 |

These fixed-coordinate diagnostic comparisons fit no scale and imply no accepted
physical threshold. One nearly condition-coincident pair has log-condition
distance 0.00016816 but X L1 1.99585. Thus condition proximity alone cannot prove
joint coverage. Conversely, some cross-cohort states are close in composition;
neither observation settles related-group independence. The private report
retains conditions and identities together and independently checks six extrema
with scalar arithmetic.

This exercise makes a multi-history option concrete but **does not establish a
matched primary benchmark**. Whole-row exclusion changes the question to new
stored-row cohorts; its suitability and joint coverage need scientific judgment.
Possible next steps are stronger physical-family mapping, a different explicitly
limited grouping claim, or targeted expansion of candidate histories. Do not
freeze this illustrative split or choose a near-duplicate/coverage cutoff merely
to make the checks pass.

Private sheet SHA-256: `ffc4af068f8d2db950e81d0421e39584e66f447bbe1d639b0a2e20b21aaec519`;
assignments: `073643288588dfb32a6c44250cb2a6cd2f4ad7b9f7e16b987fa4d4d83c09c59c`;
coverage report: `6c0b05211815fc6845ef5625988d9546f84ef207165e756ba5bf2292c205f5bc`.
No scientific partition, fitted preprocessing, model or new reference call exists.

## Current full-file fixity and remaining locator gap

A later separate pass hashes all **166 selected raw files in full** (786,312,334
bytes), with stable descriptor/path stat identities before/after. Every companion
hash matches the earlier reconnaissance. This establishes new current full-file
identities; it does not retroactively turn earlier segment-only checks into full
hashing. Source SHA-256:
`1de8c0fdb285e28eb45b1d1a3db4b9b956653bc306c7d59472a171ba05689c6c`;
private full-fixity manifest:
`ecac32e779c5a559d8b6cec7355b1fa08873d934130e498b17818c2aecdbf08d`.
Only hashes/stat metadata were written separately; no raw bytes were copied or
converted. Original input HDF parents still have only selected-slice/stat binding,
not fresh full-parent hashes.

The final locator check covers the supplied postprocessing root, all 26
immediate-parent entries and explicit paths in the recovered workflow sources.
It found no bound seeding `pinput`, source-particle HDF/configuration,
`partdim`/`override_row` invocation or actual slab-conversion receipt. It did not
recursively search unrelated descendants or treat a 2D example as this 3D input.
Locator-check manifest:
`172d4c73e40591b5b3a044aa7ec4f9792745df916896efa4df9fd84b850f69b1`.

A concrete maintainer question requests the recoverable source/location for that
association. Until the grouping/claim is accepted, do not equate stored IDs with
physical families or call the primary holdout matched. The accepted pointwise
reference contract remains useful; additional producer execution is still deferred.
No required scientific gate is waived and Phase 1 remains incomplete.
