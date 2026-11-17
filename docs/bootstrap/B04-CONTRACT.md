# B04 synthetic manifest v1

Contract specified before implementation for [issue #4](https://github.com/jaharris87/crucible-astro/issues/4), following the [investigation](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6958940130).

`crucible.manifest.validate_manifest(path)` reads a UTF-8 JSON manifest and one
named sibling JSON payload, each a regular file of at most 1 MiB. It returns a
plain dictionary with `fixture_id`, `species`, `shape`, and `payload_sha256` on
success; it raises `ManifestValidationError` (a `ValueError`) with a stable
`.code` and readable diagnostic on failure. No files are written.

Manifest required fields:

| Field | v1 meaning |
| --- | --- |
| `schema_version` | Integer `1`; boolean, string and unknown versions rejected |
| `fixture_id` | Nonempty string |
| `species` | Nonempty ordered list of unique nonempty synthetic identity strings |
| `payload` | Simple sibling filename, no slash/backslash, absolute/traversal path or symlink |
| `payload_sha256` | 64 lowercase hexadecimal characters, checked against actual bytes |
| `shape` | Two positive integers `[rows, columns]`, booleans rejected |
| `units` | Exactly `synthetic_dimensionless` |
| `state_convention` | Exactly `synthetic_sentinel` |

Payload required fields are `columns` (independent ordered identities with the
same uniqueness rule) and `values` (rectangular finite JSON numbers; booleans and
strings rejected). Extra object fields are ignored. Integers retain exact JSON
integer values; floating-point values must be finite. No normalization,
conversion, nuclear identity or astrophysical meaning is inferred.

Validation establishes manifest fields and schema, checks actual payload bytes,
decodes payload identities, compares membership, compares **ordered lists**, and
then checks dimensions and numeric values. Expected order comes from manifest
`species`; observed order comes from payload `columns`. Order diagnostics name
every differing zero-based position. A checksum establishes bytes, not semantic
agreement. No identity sorting occurs.

Reason codes: `unsupported_schema`, `invalid_manifest`, `invalid_payload`,
`invalid_json`, `file_read_error`, `file_too_large`, `duplicate_identity`,
`checksum_mismatch`, `identity_mismatch`, `order_mismatch`, `shape_mismatch`.
Missing/unexpected identities are relative to the manifest expectation.

The valid fixture has columns alpha/beta/gamma and values `[[11,22,33],[44,55,66]]`,
using `sentinel_` prefixes. The intentional `tests/fixtures/manifest/negative/`
order manifest changes only species order. Its sibling payload is a byte-identical
copy of the valid payload to retain the simple sibling-file contract. The order
test independently checks equal payload bytes, hash, shape and identity set and
runs the valid control before asserting the specific order failure.

These engineering checks establish schema, byte and identity consistency only.
Physical correctness and real-data qualification are **not yet evaluated**.
