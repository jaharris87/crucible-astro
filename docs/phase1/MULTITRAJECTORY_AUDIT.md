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
as a duplicate-history test. Actual object identities and generating writer/
slab-converter association remain to be recovered.

Next recover bounded actual pdata/inab identities, row/column arrays, selected
first-frame geometry, available original IDs and source/configuration lineage
for this finite pool. Inspect links/relationships and the actual slab-conversion
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
