# Quarantined primary native-RHS union

This page specifies the immutable payload and its finite construction recipe.
For current purpose-specific eligibility and accepted splits, use the separate
[D-025 qualified view/card](../../data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md).
Its acceptance does not change the payload masks described below.

[Issue #31](https://github.com/jaharris87/crucible-astro/issues/31) creates a separate
local dataset, `ccsn-primary-native-rhs-union-quarantined`, version `0.1.0`.
One actual candidate contains **24,314 unique records in 380 histories** from the
completed D-020 pilot and D-023 remaining-primary packet. The
[living card](../../data-cards/genesis_datacard_ccsn_primary_native_rhs_union_v0_1.md)
pins its output and verification identities. The original raw collection, pilot
HDF5/card and both generating packets remain unchanged. All four scientific
eligibility masks remain false; no fitted preprocessing or model is introduced.

## Explicit recipe and execution gate

Run `python -B -m crucible.primary_data /absolute/recipe.json /absolute/new-output`.
The output parent must exist. The exact recipe keys are:

| Key | Contract |
| --- | --- |
| `schema` | `crucible.primary-native-rhs-union.v1` |
| `dataset_id`, `dataset_version` | Explicit nonempty separate dataset identifiers |
| `packets` | Exactly named `pilot` and `primary` objects; enumeration does not choose output ordering |
| `working_partition` | Absolute `{path,sha256}` binding to the accepted D-021 working construction |

Each packet has exactly `inputs` and `expected`. Its eight input bindings are
`preparation`, `states`, `selection`, `fresh`, `components`, `comparison`,
`executable`, `execution`, each exactly `{path,sha256}`. Expected fields remain
`count`, ordered `species_Z_A`, exact `units` and `exact_controls`, following the
[pilot field contract](PILOT_RHS_DATASET.md). The pilot is 5,157 calls with controls
`[58,62]`; the primary packet is 19,159 calls with controls `[19158,19159]`.
All parents remain outside the output directory. Symlinks/dangling links,
parent traversal, existing outputs, collisions, wrong schemas/units/order/counts,
nonfinite values, truncated/trailing wire data and incomplete/failed comparison
or execution evidence refuse before output. Inputs/evidence are rehashed before
writing. A post-creation failure remains inspectable and receives no success
manifest; preserve failures rather than overwriting them.

Real materialization requires the **complete** D-023 comparison, successful job
closure, actual execution receipt and verified transfers. Finite physical output
or partial JSONL is insufficient. These gates were satisfied before this actual
candidate; [the execution report](../../phase1/PRIMARY_REFERENCE_EXECUTION.md) records retained
facts. This materializer executes neither producer nor expensive comparator.
The old pilot CLI, eight bindings and exact six-key D-020 receipt remain valid.
Only the explicit union path enables the primary format; no pilot-format rewrite
or compatibility substitution occurs.

## Two reference chains and exact controls

Both packets undergo the shared echo, ordered-species, JSON/binary-bit, finite
component/bound, ancestry and actual-build/run checks in `rhs_data.py`. Their
**26 pinned core reference assets**, source configuration and raw-root identity
must match, including each asset's declared manifest digest. The CRUCIBLE harness,
preparation manifest and executable identities intentionally differ; both actual
chains are retained. Every local evidence file is actually read/hash-checked and
rechecked. Remote absolute-POSIX library paths identify runtime files; the reader
does not require those HPC files to exist locally.

The D-023 receipt has exactly seven top-level keys: `schema`, `status`, `batch`,
`parents`, `configuration_sha256`, `runtime_shared_libraries_sha256`, `evidence`.
Schema is `crucible.rhs-primary-execution.v1`, status `completed`. The other six
keys retain the [finite pilot receipt semantics](PILOT_RHS_DATASET.md#finite-execution-receipt),
with primary schema identity. Batch is exactly:

```json
{
  "calls": 19159,
  "new_states": 19157,
  "repeat_controls": 2,
  "new_histories": 300,
  "call_histories": 301,
  "repeat_control_sequences": [19158, 19159],
  "selection_sha256": "8dc08d78637469efd08cf105ee6f9491ac9953c418de1ff04db48680f23af14f"
}
```

Integer types are checked, rather than accepting JSON numeric equivalence. The
preparation's immutable `execution_authorized:false` records its preparation-time
status; the separately bound D-023 authority and completed actual receipt record
later execution. No preparation artifact is rewritten to change that history.
The twelve evidence roles, successful stripped-byte `0` build/run exits,
preparation/executable/output/comparison links, canonical configuration digest and
strict matching library maps are checked for each source separately.

The first 19,157 primary selections are exactly role `new`, with checked trajectory
locators. The last two are role `repeat_control`, with original pilot call
identities **58 and 62**. A repeat must have the same canonical raw ID, ordinal,
raw-ts/raw-ev/payload hashes, full state/conditions/stored bits, native EOS Ye and
fresh F bits as its pilot source. Only the first four bytes of harness sequence
intentionally differ. The per-call input-state digest includes that source call
sequence and is checked separately in each packet. Both repeats are then omitted.
Missing/extra/misclassified controls, changed values/ancestry, duplicate IDs and
any new-state overlap with a pilot history fail; there is no tolerance fallback.

## Exact working membership and canonical output

The independently digest-bound D-021 construction has 30,472 ordinary records:
24,314 candidates and 6,158 exclusions, with 380 histories in 94 working groups.
The retained candidate file SHA-256 is
`211e33ad75af8c77b383188814d2e2b41e8b9eed3773a9e84aa8c6576efd9c79`.
The unique source union must equal its candidate ID set exactly. Every selected
record joins to the original history/parent, group/working role, raw ancestors,
raw locator, ordinal, species and unchanged time/T9/rho. The full-input fingerprint
is independently checked as SHA256 of species-payload digest bytes followed by
little-endian T9/rho and original full Y bytes. Known raw/derived/related ancestry
must stay in its group/role and remain acyclic. Exclusions are retained in the
linked parent, not silently replaced with another output state.

Output order is numeric **`(particle0, raw_ordinal)`**, independent of packet or
working-record enumeration. `sequence` is the new one-based canonical output
position. The original per-packet call identity remains separately visible.
The manifest records the working join proof and unchanged counts:
66/14/14 groups, 274/51/55 histories and 17,659/3,220/3,435 candidates for
train/validation/test. These are linked working-scope identities, not qualified
training/test membership. No role/group/split array is embedded in HDF5.

All original [physical fields and units](PILOT_RHS_DATASET.md#output-fields) retain
binary64 bits and scientific exclusions. Additional fields are:

| Field | Shape/type | Meaning |
| --- | --- | --- |
| `particle0` | (24314,), int64 | Canonical parent particle identity from the bound working construction |
| `source/packet` | (24314,), string | `pilot` or `primary` generating packet |
| `source/call_sequence` | (24314,), int32 | Original source call sequence, distinct from canonical output sequence |
| `source/execution_sha256` | (24314,), string | Exact generating actual-execution receipt digest |

`raw_provenance/input_state_sha256` keeps the original packet's input digest,
including that packet's call sequence. It must not be recomputed using canonical
output `sequence`. The manifest retains both complete generating input/executable/
comparison/execution chains separately from original-state selection ancestry,
plus the explicit recipe/working parent, source/reader digests and output digest.
Large coefficient proof remains in the bound audit parents, outside HDF features.
No normalization, clipping, fixed Ye, energy target or rollout truth is invented.

## Checks and actual candidate

Public tests use literal independent streams with five unique examples and two
explicit repeats, deliberately interleaved numeric identity/call ordering and
negative zeros. They verify output bytes and both provenance chains, then target
malformed repeat roles/identities/state/F/Ye, overlap, source/species/configuration,
receipts/libraries, working membership/ancestry/fingerprints and path/wire guards.
Cryptographic parent hashes are coherently rebound in negative fixtures to reach
the intended semantic check. Existing pilot and provisional-budget tests remain
unchanged. Private packets are never CI fixtures.

One local candidate was created on 2026-11-19 after all real gates passed. A
separate standard-library/h5py verifier importing neither materializer nor producer
checked every vector/scalar bit, integer/raw identity, source call/execution link,
all source-call JSON round trips, exact repeat omissions and full working join.
It rehashed all seventeen primary/working inputs and twenty-four retained evidence
files after checking. All 74 leading-zero histories and five negative-zero stored
energy values were preserved; all floats were finite and every scientific mask
was false. Exact identities are in the living card. This independent
implementation check does not replace fresh read-only review. Human scientific
acceptance, rights, each merge and merged-result verification remain separate.
