# Quarantined native pointwise RHS materialization

[Issue #23](https://github.com/jaharris87/crucible-astro/issues/23) is a bounded
S02 follow-up. D-019 defines the new pointwise numerical reference and D-020
separately authorizes the exact 5,157-state pilot under
[issue #18](https://github.com/jaharris87/crucible-astro/issues/18).
The new dataset ID is `ccsn-native-rhs-pilot-quarantined`, version `0.1.0`;
its [living card](../../data-cards/genesis_datacard_ccsn_native_rhs_pilot_v0_1.md)
is separate from both the raw collection and the original three-pair extraction.
All scientific masks remain false. Numerical-reference verification does not
establish rate/EOS/astrophysical accuracy, accepted grouping, or data rights.

## Inputs and gate

`python -m crucible.rhs_data /absolute/recipe.json /absolute/new-destination`
uses the existing h5py dependency and standard JSON. It imports no producer and
performs no build, physical evaluation, coefficient assembly, integration or
training. Root-package import remains inert; HDF5 import occurs after validation.
Input files remain external and immutable; real records never enter Git or CI.
The destination's parent must already exist. Existing destinations, symlinks
(including dangling links and symlink ancestors), parent traversal, input path
collisions and destinations inside any input directory are refused. The recipe
may live alongside a new output directory; it cannot live within the output.
A failure after creation leaves inspectable incomplete output, without a success
manifest; preserve it and use a separately identified repair attempt.

The recipe has exactly these keys:

- `schema`: `crucible.native-rhs-materialization.v1`.
- `dataset_id`, `dataset_version`: explicit nonempty strings.
- `inputs`: exactly `preparation`, `states`, `selection`, `fresh`, `components`,
  `comparison`, `executable`, `execution`. Each is an explicit `{path, sha256}`
  binding to an absolute regular file. These mean the PR #20 preparation `manifest.json`,
  `states.bin`, `selection.json`, retained `fresh.bin`, completed `components.jsonl`,
  completed `comparison.json`, the retained generating executable, and the finite
  execution receipt specified below.
- `expected`: exactly `count`, `species_Z_A`, `units`, `exact_controls`.
  The real pilot count is **5157** and controls are **[58, 62]**. Supply all 160
  `[Z,A]` integer pairs in their verified source order, and the exact unit dictionary
  below. Tiny public fixtures use the same 160-species/2,048-coefficient wire format
  with two rows and explicitly synthetic species and controls.

Use independently retained expected hashes; never bless changed files by updating
hashes merely to obtain success. The comparison must bind the preparation,
result, components and executable hashes, report completion and both exact
controls, and retain runtime-library identities. The preparation must bind states
and selection. The execution receipt binds actual retained build/run evidence.
Every row must pass the source comparator's conditional assembly flag and finite component/baryon residual bounds, with scientific acceptance
false. Row counts, sequential identities, raw ordinal/locator ancestry and
per-trajectory raw-parent consistency are checked. Raw locators preserve the
three-digit slab row and four-digit tracer filename, including leading zeros. Missing/malformed JSON,
duplicate keys, nonfinite values, wrong dimensions, trailing/truncated binary,
wrong order, echoes or JSON/binary bits are refused. Hashes are checked again
before writing. This consumes the completed independent proof, without rerunning
its expensive mathematics or treating self-declared flags as scientific acceptance.

**Real materialization gate:** the full source comparator must complete and its
complete output and receipts must be retained before creating the single real
candidate. The actual pilot satisfied this gate as documented in the
[retained execution report](../../phase1/RHS_PILOT_EXECUTION.md) before its one candidate was
created; the [living card](../../data-cards/genesis_datacard_ccsn_native_rhs_pilot_v0_1.md)
pins the actual output identities. A normal physical loop, finite components, controls, or partial JSONL
alone do not satisfy this gate. The implementation's synthetic checks do not
claim the gate passed. The actual receipt belongs in the live issue/PR and card.

## Finite execution receipt

The eighth primary input `execution` repairs the missing actual build/run closure
identified in RHS-DATA-R1 on the first draft candidate. It has exactly six keys:

| Key | Exact meaning/type |
| --- | --- |
| `schema` | String `crucible.rhs-pilot-execution.v1` |
| `status` | String `completed`; write only after completed comparison/job closure |
| `parents` | Exact map of `preparation`, `executable`, `fresh`, `components`, `comparison` to their recipe SHA-256 strings |
| `configuration_sha256` | Digest of nonempty preparation `configuration`, canonically encoded as below |
| `runtime_shared_libraries_sha256` | Nonempty map of absolute POSIX library-path strings to 64-character lowercase hexadecimal SHA-256 strings; exactly equals the comparison map |
| `evidence` | Exact twelve-role map below; each value is an explicit `{path, sha256}` local file binding |

Configuration digest bytes are exactly
`json.dumps(configuration, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()`.
The preparation manifest binds original source/kernel/scripts/physics-input
identities and configuration. The retained actual build manifest must have that
same digest; build logs and drivers bind the actual generating build. These links
preserve declared source/configuration and actual execution ancestry together.

The evidence roles are exactly `build_manifest`, `build_log`, `build_exit`,
`build_driver`, `build_runtime`, `run_log`, `job_script`, `job_status`, `loaded_maps`,
`job_hardware`, `job_environment`, `run_exit`. Every path must be an absolute
existing regular file, with no symlink ancestor or parent traversal. Paths must
be distinct, including from primary inputs. Every declared file is actually read,
hash-checked and rechecked before output; destinations inside an evidence parent
are refused. `build_manifest` must match the primary preparation digest;
`build_exit` and `run_exit` must strip to bytes `0`. Other evidence is retained and
hash-bound; producer interpretation and fresh review establish its meaning,
without introducing platform-specific log parsers or scanning directories.

For the actual attempt, `build_runtime` names retained `runtime-proof.txt`,
`job_hardware` names `job-hardware.txt`, `job_environment` names
`job-selected-env.txt`, `run_exit` names `job-exit.txt`, and `job_status` names the
final scheduler accounting receipt. A digest-valid receipt is engineering
provenance, not scientific acceptance. Library-map structure is validated in both
comparison and execution receipts (RHS-DATA-R2); remote HPC library files need
not exist on the local materialization machine.

## Output fields

`dataset.h5` uses little-endian binary64 for all physical fields, retaining their
original bits including signed zero. It contains no normalization, clipping,
fixed Ye, fitted preprocessing or split membership.

| Field | Shape | Meaning / unit |
| --- | --- | --- |
| `species_Z_A` | (160,2) | Ordered integer Z,A; no inferred species names |
| `sequence` | (N,) | One-based pilot ordering |
| `row_id`, `tracer_id` | (N,) | Original slab-row and tracer/zone integer identities |
| `raw_ordinal`, `step` | (N,) | Saved-record ordinal and raw producer step |
| `time` | (N,) | s |
| `T9` | (N,) | GK |
| `rho` | (N,) | g/cm^3 |
| `internal_dt` | (N,) | s; internal step, not saved-output interval |
| `Y` | (N,160) | molar_abundance_Y; exact original full state |
| `fresh_rhs` | (N,160) | molar_abundance_Y/s; newly evaluated instantaneous source |
| `native_EOS_Ye` | (N,) | dimensionless; source-returned composition EOS Ye, Q/B |
| `stored_dY_unqualified` | (N,160) | molar_abundance_Y/s; raw diagnostic, not fresh label |
| `stored_energy_unqualified` | (N,) | erg/g/s; stored internal-step diagnostic only |
| `raw_provenance/*` | (N,) strings | Record locator and raw-ts/raw-ev/raw-payload/input-state hashes |
| `eligibility/*` | (N,) booleans | Separate all-false state/RHS/energy/rollout masks |

The `units` recipe dictionary consists of the nine physical field names above,
each mapped to the exact unit string in the table (excluding the descriptive
text after semicolons). `Y`, `fresh_rhs`, `stored_dY_unqualified` retain their
explicit abundance convention. Each mask carries its own reason attribute:
state qualification unaccepted; RHS only conditionally verified with physical
accuracy unaccepted; energy diagnostic unqualified; rollout lacks integration/
history qualification. Stored labels do not inherit fresh-label provenance.
Large coefficient evidence stays in the bound audit parent, outside HDF features.

`manifest.json` binds the recipe and original recipe bytes' digest, every input
path/digest, ordered species/units/count, materializer source digest and runtime
Python/distribution/h5py/HDF5/NumPy versions, and final HDF5 length/digest. It has
separate original-state and newly generated-label provenance, links to the full
source preparation/reference/comparison/execution closure, and records all-false eligibility.
The schema is the extraction version; the committed source and pinned `uv.lock`
are the portable software recipe. A manifest is a local integrity receipt, not
permission to redistribute data or an accepted scientific claim.

## Verification and limits

Public synthetic tests use literal independently located byte fields, distinct
scalars, signed zeros and ordered species sentinels. They check HDF5 bytes,
units, identities, ancestry separation and all-false masks, plus deliberate
failures rebound to valid hashes to reach the intended semantic gate. CI uses
no private inputs and executes no producer. Real-candidate verification must
independently reinterpret every parent field and compare every HDF5 value/identity,
including byte equality and absence of positive masks. Neither suite qualifies
original historical derivatives, physical accuracy, rollout, energy, coverage or
benchmark membership. Any future positive eligibility needs explicit scientific
acceptance and a separately identified artifact or overlay, preserving this one.


## Actual materialization and preserved refusal

The first actual validation refused before creating an output directory because
`ts_0445` was incorrectly reconstructed as `ts_445` (RHS-DATA-R3). The unchanged
recipe, refusal receipt and public literal regression's failing/passing outputs
are retained. The narrow formatter repair changes no physical values, ordinals,
sequence or parent identity. Its second engineering attempt created the only
actual candidate. No producer or comparator was repeated.

An independently implemented verifier importing neither materializer nor producer
checked all 5,157 rows / 80 histories / 160 species against parent wire bytes and
JSON, all scalar/integer/raw-provenance fields, units/dimensions and four separate
all-false masks. It checked all 19 histories with leading-zero tracer IDs, read an
original raw species header independently and rehashed every primary and retained
execution evidence file after the scan. The card records the exact artifact and
verification identities. This is software/identity evidence; scientific accuracy,
accepted grouping, rights and fresh review/human acceptance remain separate.
