# S02 quarantined reader and local extraction

Implementation contract for [issue #11](https://github.com/jaharris87/crucible-astro/issues/11).
The maintainer accepted the bounded three-pair ingestion scope on 2026-11-17.
Scientific qualification, source/build association, physical conditioning,
reference accuracy, rights and benchmark gates remain open. Successful extraction
sets **every scientific training/reference eligibility flag to false**.

## Supported format and checks

`crucible.xnet` reads one explicitly selected layout,
`xnet-ts-le-i32-f64-six-v1`: signed int32 little-endian positive matching Fortran
record markers and binary64 scalars/vectors. It does not detect or guess variants.
The first four metadata widths are 320, 76, 160 and 160 bytes. The fifth payload
contains int32 `ny` and binary64 `Z[ny]`, `A[ny]`; the sixth contains int32 `nflx`
and two int32 endpoint arrays of length `nflx`, using one-based species indices.
Dimensions are explicit and checked; neither 160 species nor 909 fluxes is hardcoded.
Z/A must be integral, unique, ordered as declared and valid identifiers. This
identifies neither isomers nor rates/masses. The entire species payload, including
`ny`, is fingerprinted separately from the raw pair.

Each data payload has int32 step, then five binary64 scalars in this order:
time, temperature, density, internal `dt`, stored energy rate. Binary64 vectors
follow: Y (`ny`), flux (`nflx`), stored derivative (`ny`). Exact payload width is
`44 + 8*(2*ny+nflx)`. Framing must consume complete EOF. The reader checks raw
hashes, expected dimensions/count, species order/header hash and exact declared
unit tokens. Nonfinite dynamics, nonpositive T/density, negative internal dt,
negative step or nonincreasing time fail. These are ingestion checks, not accepted
scientific tolerances. No clipping, conversion, normalization or fitting occurs.

The accepted ingestion unit dictionary is:

```json
{
  "time": "s", "temperature": "GK", "density": "g/cm^3",
  "internal_dt": "s", "Y": "molar_abundance_Y",
  "stored_derivative_unqualified": "molar_abundance_Y/s",
  "stored_energy_rate_unqualified": "erg/g/s"
}
```

The Y token records the inspected source's molar-abundance convention (mass fraction
A·Y); it performs no conversion. These are source-indicated ingestion conventions,
not proof that the inspected snapshot generated the supplied records. Stored energy
is the signed internal-step mass-excess change rate, not qualified deposited heating
or instantaneous energy RHS. Internal dt is not the saved-output interval.

The ASCII companion must use the observed first six headings `k Time T(GK) Density
dE/dt Timestep`, condensed columns and final `It` heading. Every record's six
scalars must match ordinally at the writer's printed precision: time `.8E`, T/rho
`.3E`, energy/internal dt `.2E`, exact integer step. For an **exactly zero binary
energy diagnostic only**, the companion spellings `0.00E+00` and `-0.00E+00` are
equivalent. The original binary sign bit and payload identity are preserved;
no approximate tolerance or other-column equivalence is introduced. The expanded
read-only audit found five such sign differences in four histories, tracked in
[issue #21](https://github.com/jaharris87/crucible-astro/issues/21). Its initial
strict-alignment failures and separate signed-zero disposition remain retained.
Public regression fixtures are synthetic; local real-data checks establish only
ingestion, with every scientific exclusion unchanged. The observed tails are two
nonnegative iteration integers or the literal final `NSE`. Row counts, unknown
tails or scalar mismatches fail with companion-specific errors. Only reliably
aligned explicit NSE text classifies NSE. Zero derivatives never classify NSE.
Condensed headings/values are checked for shape/numeric readability but cannot
supply network identities; repeated headings are permitted and ignored as identities.

Initialization is the first producer output (required step zero), independent of
stored derivative value. Ordinary stored derivatives have unverified accepted-state
RHS alignment because the inspected source writes a trial/Newton-iterate derivative
before final correction. The [S01 evidence](S01_AUDIT.md) gives source locations and
physical limitations. The reader does not execute or import producer code.

## Explicit local recipe

Keep real recipes, resolvers, receipts and data under ignored local storage.
A resolver JSON supplies absolute `candidate_root` and a separate `derived_root`.
The latter must be outside the former. Relative raw locators must resolve within
the candidate root; traversal and escaping symlinks fail. Output names are simple
letters/digits/underscore/hyphen aliases. Existing output paths, including dangling
symlinks, are refused. A fresh output directory contains `data.h5` and `manifest.json`.
This local interface assumes no concurrent external mutation of directory symlinks;
raw content is rehashed after extraction to detect source changes.

A recipe contains `dataset_id`, `dataset_version`, `acceptance_reference` and one
to three explicit `pairs`. Each pair declares `alias`, relative `ts_path`/`ev_path`,
`layout`, `units`, `ts_sha256`, `ev_sha256`, `expected_species` (ordered `[Z,A]` pairs),
`species_header_sha256`, `expected_nflx` and `expected_records`. Expected values
come from accepted audit evidence, not auto-inference or filename guesses.
The retained ignored S02 recipe selects precisely the accepted three audited pairs;
the public synthetic recipe in tests contains no real values or locators.

```sh
uv run --no-sync python -B -m crucible.xnet \
  --resolver .local/s02/resolver.json \
  --recipe .local/s02/recipe.json --output-name three-pair-v0_1_0
```

This is bounded extraction authority, not permission to loop over the collection.
No original data or reference project is written. Both inputs are fingerprinted
before decoding and checked again after writing; a failure removes the temporary
derived directory and reports its reason. A post-check change by an external
process is outside this fixity observation. Permissions/redistribution remain
unknown and the resulting local artifact must not be published as a data release.

## Artifact contract and reproducibility

Each HDF5 pair group preserves species order, record ordinal, raw marker offset,
step, original binary64 time/T/rho/internal dt, Y, stored derivative and stored
energy rate. It also stores raw-payload hashes, raw-pair/header identity attributes,
explicit companion NSE/alignment evidence, structural readability, four separate
false eligibility arrays and JSON exclusion-reason lists. Reasons distinguish
initialization, explicit NSE placeholders, ordinary accepted-state RHS alignment,
energy interval meaning, unverified history association, grouping and unknown provenance.
Unknown conditions remain unknown; no fixed Ye or sufficient T/rho/Ye closure
is inferred. Flux values stay in raw files; dimensions/endpoints are validated.

The JSON manifest binds dataset ID/version, exact raw relative locators/digests,
ordered species/header hash, every selected record ordinal, acceptance reference,
extractor module source SHA-256, complete recipe and canonical recipe SHA-256,
Python/h5py/NumPy versions and the output HDF5 digest. The Git candidate/lockfile
supplied with review binds the wider software environment. The recipe and output
hash do not claim HDF5 bytes are identical across library/platform versions;
reproduction compares arrays/membership and retains a new fixity digest.

HDF5 extraction actually uses `h5py==3.15.1`, a fixed release installed/tested on
the supported Python 3.12.9 environment; NumPy is its locked transitive dependency.
The lock includes macOS/Linux wheels. No ML dependency is introduced. Root package
import remains inert; h5py/NumPy load only when extraction is invoked. CI runs
public synthetic controls and failures with no private filesystem dependency.
The [derived card](../data-cards/genesis_datacard_ccsn_quarantined_v0_1.md) links
raw parents, local recipes and explicit qualification/rights gaps.
