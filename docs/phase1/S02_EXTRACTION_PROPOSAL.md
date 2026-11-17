# Bounded reader and derived-dataset proposal

Proposed 2026-11-17 under [S01 #10](https://github.com/jaharris87/crucible-astro/issues/10).
**Maintainer accepted the quarantined three-pair reader/local extraction scope
on 2026-11-17.** [S02 #11](https://github.com/jaharris87/crucible-astro/issues/11)
is active in an isolated worktree. Physical qualification remains pending; no bulk
conversion has started. This responds to the maintainer's question about making
the raw XNet binaries easier to use for training. Formatting cannot qualify labels.

Recommend two linked documentation layers: a brief card for the unchanged raw
collection and a card for each versioned derived dataset, with its parent manifest,
extraction recipe, exclusions and acceptance. The current [raw card](../data-cards/genesis_datacard_ccsn_raw_candidate.md)
is a draft; no qualified training dataset exists.

Start with the three [audited pairs](S01_AUDIT.md), one observed binary layout,
and only a local derived extraction. Use HDF5 named arrays plus a small JSON
identity/recipe manifest when extraction is accepted. HDF5 offers named groups,
typed arrays, slicing and attached attributes ([official h5py guide](https://docs.h5py.org/en/stable/quick.html));
it fits vector abundances without forcing them into CSV columns. This is a
reversible storage recommendation, not a scientific choice or new framework.
Use project-local, pinned dependencies only when the accepted implementation
actually needs them. No ML library, model stack or registry is needed.

Preserve original binary64 values, species order and raw row identities. Name the
stored derivative `stored_derivative_unqualified`, rather than `rhs_target`.
Keep explicit record ordinals, step/time, internal `dt`, Y, ordered Z/A and
declared units, provenance status, companion regime evidence, and separate
state/RHS/energy/rollout eligibility and exclusion reasons. Retain stored energy
as a diagnostic with its interval semantics, never as deposited heating. No
inferred isomer identity, fixed Ye, clipping, normalization or subsampling.
Unknown source conditions stay unknown; they are not replaced with zeros.
Fluxes can remain in raw storage unless the accepted reader contract needs them;
their lengths/endpoints still participate in strict layout validation.

The implementation should require an explicit local path resolver, raw hashes,
expected ordered species and supported layout; reject malformed markers, truncated
records, trailing bytes, incompatible dimensions/order/units and unsupported
variants with actionable errors. Independently decoded local records supply real
oracles. Synthetic hand-specified binary fixtures provide public CI coverage,
including a valid control and targeted negative cases. Keep real records local
until their redistribution authority is explicitly confirmed. Default training
eligibility remains false for this unqualified scope, independent of finite values.

The derived manifest binds selected raw digests/record ordinals, species header
digest, reader revision/configuration, output digest, validity policy and human
acceptance reference. The derived card reports that this is an exploratory
ingestion artifact until physical qualification is separately satisfied. Check
raw digests before/after extraction; write to a distinct derived root, refuse
to overwrite raw inputs, and report exact extraction failures.

No split or normalization is embedded irreversibly in raw extraction. S03 will
bind accepted derived membership to grouped partitions, maintain related records
and copies together, and require train-only fitted preprocessing in later phases.
No scalers are fitted in Phase 1. With only one confirmed parent simulation,
the most that could be proposed is a within-simulation exploratory benchmark,
whose tracer/neighborhood grouping still needs original mapping evidence.

The accepted bounded S02 issue is assigned to [milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2)
with these concrete reader/oracle/mask/identity checks. A broader conversion of
the collection needs accepted semantics and an explicit bounded conversion scope;
this proposal grants neither. Phase 1 remains incomplete until its scientific,
benchmark, review/merge and integration gates hold.
