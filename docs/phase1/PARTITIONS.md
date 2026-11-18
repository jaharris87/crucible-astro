# D-021 candidate partition constructor and scientific gate

[S03 #15](https://github.com/jaharris87/crucible-astro/issues/15) implements the
maintainer's [working-scope acceptance](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-6968022017),
recorded in [D-021](../DECISIONS.md#decision-d-021-working-primary-input-scope-and-grouping).
This accepts the finite operational input/group semantics. It does not qualify
references, final eligible memberships, metrics/tolerances or final-test use.
Phase 2, fitting and training remain unauthorized.

## Accepted finite rule

The population is the exact expanded 380-history / 24,314 source-table-candidate
pool in [the audit](PRIMARY_EXPANSION_AUDIT.md). The 80-history pilot's old 21
groups are not inherited. The measured source-clock window is
0.41412702025718645–0.8525275190077543 s, all 2,193 frames. Later records retain
whole-history groups; the constructor invents no late positions.

`crucible.partitions.measured_components` independently reconstructs the groups
from canonical integer particle IDs and retained `(frame,history,3)` arrays of
radius in cm and theta/phi in radians. At each measured frame, convert to
`(r sin(theta) cos(phi), r sin(theta) sin(phi), r cos(theta))`; for every pair,
take the median of Cartesian separation divided by the sum of radii. Each history
links to its closest other history, breaking exact metric ties by numeric
canonical ID. The undirected connected components, with sorted members and
lexicographic component ordering, are the operational groups. No spatial cutoff
or physical-family independence is asserted. Residual proximity, one parent,
unequal sampling, missing layouts, component-envelope gaps and one Compressed
group in each held-out role remain limitations of the accepted working scope.

`construct_candidate(pool, contract, groups)` then implements the frozen
allocation, rather than returning a copied role table:

1. Anchor the groups containing the global candidate minima/maxima of T9,
   density and native source-formula Ye=Q/B. Resolve equal scalar values by numeric
   `(particle0, ordinal)`.
2. Visit stored rows in numeric order, then categories in string order. For a
   stratum absent from anchored training groups, anchor its minimum-hash group.
3. Within each homogeneous category, let `q=max(1,15*N//100)`, where `N` includes
   anchors. Sort nonanchors by the fixed group hash, then sorted numeric members;
   allocate the first `q` to validation, next `q` to test, and remainder to training.
   Insufficient nonanchors fail, without fallback or retuning.

The exact rank encoding is SHA256 of compact, sorted-key UTF-8 JSON
`[namespace, sorted_numeric_members, tag]`, separators `(',', ':')`, with:

```text
namespace = Chimera/D9.6-SN160-3D/canonical-zero-based-global-particle-ID
tag       = phase1-primary-expanded-operational-allocation-v1
```

The immutable original accepted assignment remains an oracle: any recomputed
group/member/role difference fails `accepted_assignment`. A population, platform
or input change cannot silently choose a different real assignment. No precision
tolerance or new scientific threshold is introduced.

## Explicit inputs and executable boundary

The module is import-inert and has no HDF5 or private-file import dependency.
NumPy is loaded only for measured geometry and the explicit CLI; it is already
locked through the existing ingestion dependency. No new dependency or framework
is introduced.

The JSON pool has four fields:

| Field | Required contents |
| --- | --- |
| `metadata` | Pool/version and parent identities; namespace/tag; working-scope decision; reference-configuration and producer species-payload SHA256; ordered species `{id,A,Z}`, count; units; measured time window. The local reference identity pins the existing D-019 manifest, without qualifying labels. |
| `histories` | Canonical integer `particle0`, parent, stored row, known category, full raw ancestor SHA256 identities, and explicit `known_related` canonical IDs. The local adapter also retains raw ts/ev paths and the known-ancestry limitation. |
| `records` | Exact record ID, particle/ordinal/parent, ordered-species SHA256 and count, input fingerprint SHA256, unchanged T9/rho/source-formula Ye/time, candidate flag and exclusion reasons, raw ancestor hashes, and explicit `derived_from` record IDs. |
| `source_exclusions` | Reason-bearing source inventory outside the ordinary-record pool, including initial/NSE summaries and the 15 selected unsupported-layout histories. No excluded member is replaced. |

The supported units are `Y=molar_abundance_Y`, `temperature=GK`,
`density=g/cm^3`, `time=s`, following [the source-indicated ingestion convention](S02_READER.md).
This is full unchanged Y, with no normalization, species permutation or unit
conversion. The fingerprint is the retained audited full `(Y,T9,rho)` identity;
this metadata constructor does not reread raw Y or claim that a supplied hash
alone proves physical correctness.

The contract independently binds exact metadata, the order-independent pool
SHA256, five exact counts (`histories`, `ordinary_records`, `candidate_records`,
`excluded_records`, `groups`) and canonical `accepted_groups` entries
`{members:[integer IDs], role:train|validation|test}`. `pool_digest` sorts the
history and record collections by canonical particle ID and record ID; ordered
species and other declared sequences remain ordered. The real contract also
records the immutable frozen-protocol and original-assignment file SHA256s.
Raw input files are checked by the CLI config before deserialization; the
contract file itself is a separately bound acceptance input, never inferred from
the observed pool.

The CLI consumes a config whose `pool` and `contract` entries each contain
`{path,sha256}`; `positions` is a nonempty list of such entries. Relative paths
resolve against the config directory; explicit absolute local paths are also
supported. The position NPZs are the retained audit arrays with keys
`positions_r_theta_phi`, `trajectory_ids_row_zone_gpid0` (ID column 2), and
`times_by_file` (source-clock column 0). Full clocks must agree across files and
packs and match the exact declared window. No pickled arrays are loaded.

```sh
python -B -m crucible.partitions /path/to/config.json /path/to/new-candidate.json
```

Output creation is exclusive. It serializes complete history/record roles and
known ancestry, ordinary exclusion reasons and source exclusions, metadata,
contract/pool hashes, groups and anchors. Its status is always
`CANDIDATE_MECHANICAL_PASS_PENDING_SCIENTIFIC_QUALIFICATION`.

The mechanical checks require complete unique histories, records, canonical
states and group membership; known parent/category/species/count/units; complete
reason-bearing candidate exclusions; whole related histories and raw/derived
ancestry; acyclic known derivations; and no exact candidate input fingerprint
crossing roles. New display IDs cannot evade canonical or declared-copy checks.
Unknown parents/groups and empty candidate roles fail. Unknown physical family
relations cannot be discovered from metadata: absence of a recovered relation is
explicit uncertainty, not independence evidence.

## Separate scientific-readiness gate

`validate_scientific(candidate, membership, eligibility, acceptance)` never
promotes candidate metadata or fabricates positive eligibility. It requires:

- A complete eligibility map for every candidate ID, with explicit true/false
  status. Zero eligible records or unknown eligibility fails.
- Nonempty qualified membership in **each** role, no changed roles or unknown
  IDs, evidence SHA256 for every included record, and complete disjoint
  membership or explicit reason-bearing exclusions for the entire candidate set.
- A separate human task/reference/domain/metrics/tolerance decision receipt,
  bound to the exact canonical candidate, membership and eligibility hashes.

Receipt authenticity, evidence adequacy and scientific acceptance remain human
responsibilities. A bound receipt is an input requirement, not an automated
judgment of physics. The function returns only a check report; it does not alter
candidate records, grant final-test access or close S01/S03. Source-table screening,
passing software checks and empty disjoint sets cannot establish qualification.

For later authorized work, fit every learned transform, scale, abundance floor,
feature/species selection and cutoff from training records only. Validation may
support authorized choices; final-test data cannot choose them. Test the actual
fit boundary when a fitter exists in Phase 2. This change creates no dummy fitter,
model stack or fitted preprocessing artifact.

## Actual bounded verification

The one local deterministic adapter joins the retained old/new ordinary audit
metadata to `full_history_metadata` by exact trajectory locator. It retains all
30,472 ordinary decisions, resolves full ts/ev hashes from the separate pilot
166-file and new-wave 624-file current-fixity manifests, carries the producer
species-payload identity plus the ordered 160-species table, and binds the retained
reference manifest. It records all parent digests and this recipe. Original
reference projects, scripts, raw arrays and audit packets remain untouched.

The constructor recomputed groups directly from the two retained measured NPZs.
It reproduced all 94 group memberships and all 380 history / 24,314 candidate
record roles exactly against the accepted original oracle. All 6,158 ordinary
exclusion memberships/reasons also match; reversed histories, records and group
members produce identical output. The result is 66/14/14 groups,
274/51/55 histories and 17,659/3,220/3,435 candidates. The separate scientific
check currently returns **expected failure `empty_eligible`: qualification
pending, zero eligible records**, with no final acceptance receipt.

Public tests use mathematical synthetic inputs only: hand-specified grouping and
hash-allocation oracles, total-category quota arithmetic, separate categories,
order invariance, malformed identity/species/count/parent/group controls,
derived-copy and related-tracer crossover, raw ancestor overlap, exact duplicate
inputs across roles, incomplete allocation, cyclic ancestry, empty/unknown or
ineligible scientific membership, missing evidence/acceptance, and the actual
bound JSON/NPZ CLI. Each negative case has a valid control. Real private records
and data rights are not CI dependencies.

All new real artifacts are confined to the ignored
`.local/phase1-audit/production-partitions-v0_1_0/` packet: adapter/recipe, bound
pool/contract/config, candidate JSON, pending eligibility/membership, verification
and manifest. Exact file hashes and source freshness are retained there and in
the draft PR. No producer/compiler/EOS/RHS/rates/NSE/Jacobian/integration call,
HPC transfer, training or model result was introduced. Human scientific acceptance
and independent exact-candidate review/merge/integration remain separate gates.

The retained final-source receipt binds these actual SHA256 identities (the
original candidate and final-source reconstruction are byte-identical):

| Artifact | SHA256 |
| --- | --- |
| Final constructor source | `b9db19d7d9db27df6a0d1bab1c78caceac338c6b79dcd051d3f752f71f038a5b` |
| Candidate JSON bytes | `211e33ad75af8c77b383188814d2e2b41e8b9eed3773a9e84aa8c6576efd9c79` |
| Canonical candidate JSON | `72a65dab6dbfc03d4cc9fa3bdadd551b2b4d0f298363853d6cbbc2564ccf8027` |
| Final-source verification | `286f52843d7c648107fd9c576b2ae4b86bd4cb5420146f221169fc7677f67e29` |
| Final packet manifest | `ae30a060b7c52568c6fc56431c82cec7d93e7fab386246b06a12df03b74c80cb` |
