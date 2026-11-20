# Load the qualified pointwise benchmark

`crucible.benchmark.load_benchmark` reads the accepted
`ccsn-primary-native-rhs-pointwise` version `0.1.0` as ordinary NumPy arrays.
It joins the separate D-025 qualification overlay, immutable HDF5 payload and
exact accepted memberships. The HDF5's original four false quarantine masks stay
unchanged. Loading the HDF5 by itself does not establish qualified membership.

The [qualified card](../../data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md)
describes the finite numerical-emulation purpose and limits. The
[Phase 1 access record](../../phase1/PHASE1_CLOSEOUT.md#local-access-and-recovery)
identifies the accepted artifacts. Real files and private metadata remain local;
redistribution rights remain unresolved. Public tests use synthetic records only.
Phase 2A authorizes this access implementation; fitting and later work have their
own authority. The immutable overlay's `scope.execution_authority` is its historical
Phase 1 snapshot, preserved verbatim in returned `qualification_scope` metadata.

## Local configuration

Create an ignored local access file, for example `.local/benchmark-access.json`:

```json
{
  "overlay": "/absolute/local/qualified-view/overlay-manifest.json",
  "path_overrides": {}
}
```

Use the retained overlay unchanged. If a file moves, add its original SHA256 as a
key in `path_overrides` and its new local path as the value. This works for the
payload, overlay, or any consumed JSON parent. It changes only location, never
identity. No directory search, remote download or registry is involved. A missing
file produces a refusal; obtain its exact accepted bytes from the custodian.
Do not change a digest to bless a different file.

Relative paths in the configuration resolve beside that JSON file. For a Python
mapping configuration they resolve from the working directory. Relative paths
inside an accepted overlay resolve beside its effective path, including an
override of the overlay itself. Absolute historical locators are used unless a
digest override is supplied; an old development checkout may no longer exist.
The loader resolves paths before reading and checks exact file content and any
declared byte length. Unknown configuration keys and malformed override maps fail.

A missing bound file refusal names its file and SHA256. Recover the exact bytes
and add that digest to `path_overrides`; do not rewrite the accepted overlay.
For example, the scoring configuration is also committed at
`configs/native_fidelity/primary_benchmark.json`. Its accepted digest is
`f971e8cf75fdcf76f50f5a8bcce30e247b7fa0e332949c221f3fd9adebaf158e`:

```json
"path_overrides": {
  "f971e8cf75fdcf76f50f5a8bcce30e247b7fa0e332949c221f3fd9adebaf158e": "/absolute/checkout/configs/native_fidelity/primary_benchmark.json"
}
```

## Scientist example

After installing the project as described in [Contributing](../../../CONTRIBUTING.md#quick-start):

```sh
uv run python -B examples/load_benchmark.py /absolute/local/benchmark-access.json
```

The example prints shapes, counts, units and reproducibility hashes. It does not
print private record IDs, local reference paths or abundance/rate values. Use
`--split validation` or `--split test` to inspect another membership. This performs
no scoring or final-test performance evaluation.

For an interactive session:

```python
from crucible.benchmark import load_benchmark

data = load_benchmark(
    "ccsn-primary-native-rhs-pointwise",
    "0.1.0",
    use="rhs_training",
    split="train",
    config="/absolute/local/benchmark-access.json",
)
Y, T9, rho, F = data["Y"], data["T9"], data["rho"], data["fresh_rhs"]
```

The function requires an explicit name, version, use and split. Supported uses are
`state_training` and `rhs_training`; supported splits are `train`, `validation`,
`test`. These strings describe purpose-specific data eligibility and do not grant
execution authority. Energy, rollout and unknown uses fail before reading data.
Unknown names, versions and splits also fail. There is no caller-supplied trust
root or option to accept a replacement benchmark.

## Returned values and ordering

The return value is a dictionary. Every per-record array has the same leading
dimension and follows the **exact accepted membership list order**, joined by
record ID. This differs from the payload's numeric `(particle0, raw_ordinal)`
order. Train/validation/test have 17,659/3,220/3,435 rows respectively.

| Key | Shape / meaning |
| --- | --- |
| `Y` | `(N,160)`, original ordered molar abundance Y |
| `fresh_rhs` | `(N,160)`, fresh native instantaneous dY/dt in Y/s |
| `T9`, `rho` | `(N,)`, GK and g/cm³ |
| `time`, `native_EOS_Ye` | `(N,)`, source seconds and native composition-derived Ye=Q/B |
| `species_Z_A` | `(160,2)`, ordered integer Z,A shared by Y and F columns |
| `record_id`, `particle0`, `raw_ordinal` | `(N,)`, exact record and canonical history/ordinal identities |
| `group`, `category` | `(N,)`, accepted operational group and recorded history category |
| `source_packet`, `source_call_sequence` | `(N,)`, generating packet and original call identity |
| `physical_input_sha256`, `source_input_sha256` | `(N,)`, intentionally distinct identities explained below |
| `metadata` | Name/version/use/split, units, full ordered species, exact hashes, qualification scope, reference identities and role counts |

Float arrays preserve original binary64 values, including signed zero. No
normalization, clipping, species permutation, unit conversion, preprocessing fit
or framework tensor conversion occurs. Arrays are independent in-memory results;
editing one does not edit any local input. Native EOS Ye is provided as metadata
per state, not an independent fitted input or a fixed imposed Ye.

`metadata` retains the original D-025 scoring-source hash separately from the
accepted D-026 successor's source hash, arithmetic identity and adoption receipt.
The loader does not execute a scorer. Future results must identify the actual
scorer used; a loader receipt alone cannot establish that execution. Reference
identity metadata retains historical private locators, so do not publish the
entire returned object without an appropriate data-sharing decision.

## Checks and limitations

Before returning any split, the loader checks the independently pinned accepted
overlay SHA256 and all files it consumes. A coherently rewritten overlay and
parent graph still fail that fixed acceptance root. It checks qualification and
per-record uses, reconstructs the complete original mechanical partition through
`partitions.validate_scientific`, and checks exact candidate/membership/eligibility
bindings. It validates every payload row and all three roles, not just the
requested split: complete ID joins, shapes, finite values, units, species order,
canonical payload ordering, unchanged false masks and source/reference links.

The physical input fingerprint is
`SHA256(species-payload-digest-bytes + little-endian T9 + rho + full Y)`.
The source-call digest is instead SHA256 of the original `5i5d` call prefix plus
full Y, using the **source** call sequence and original stored diagnostic scalar.
Both are checked separately; canonical output sequence cannot replace source call
sequence. Cross-partition physical duplicates are rejected even when only loading
train. For this leakage check alone, positive and negative zeros count as the same
physical input; fingerprint validation and returned arrays retain their bits.

This is an in-memory reader for one accepted finite version, with complete
validation on each call and no cache. It reads a verified payload byte snapshot
and the original pool/candidate JSONs, so peak memory exceeds the returned split.
It consumes only the bound files needed for these checks; it does not reopen all
historical raw/reference streams, rerun their comparator or reestablish scientific
qualification. The pinned overlay and payload identify that previously accepted
evidence. No producer, generator, solver, scoring, training or integration runs.

One parent, operational grouping, residual correlation and finite component
coverage remain limitations. Physical application, energy and rollout accuracy
remain unqualified. Future preprocessing learns only from training data; loading
validation or test records grants no authority to adapt choices to them.
