# Phase 1 data-qualification status

2026-11-17. [Milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2),
[current progress](../PROGRESS.md), [audit](../phase1/S01_AUDIT.md).

Phase 0A/0B are complete, including human-merged audit PR #9 and its passing
42-test integration check. The maintainer authorized Phase 1 S01–S03; the native
goal is active. No model development or training has started.

The supplied data are raw XNet outputs. A lightweight inventory found 42,362
binary/text file pairs. Three pairs, containing 1384 saved records, were decoded;
their binary framing and scalar values agree with companion text. This is useful
reader evidence, not proof that the data are suitable training labels.

The audit distinguishes 3 initial records, 1185 explicitly marked NSE records and
196 other records. Initial/NSE derivatives are unsuitable RHS labels; accepted-state
alignment of the others is unmeasured. All remain unqualified because generating
inputs/build/run association and necessary conditions are incomplete. Stored energy
is an internal-step diagnostic, not qualified deposited heating. Repeated identities
in condensed species output require separate treatment from the full binary state.

The original remote location is accessible. About 1.7 MB of candidate controls,
network inputs and slab metadata were recovered locally without copying bulk
histories or running XNet. Initial composition/history inputs exist remotely;
an extrema link is dangling. Their historical association still needs audit. The inspected runtime reads
extrapolation information from the history file, not the trailing extrema path,
so that dangling link is not itself a demonstrated runtime blocker. Recovered
candidate processed tables contain weak reactions but zero active neutrino
reactions; the generating-table association still requires evidence.

A [living raw-data card](../data-cards/genesis_datacard_ccsn_raw_candidate.md)
uses the official released Genesis v2.0.0 narrative template and states missing
rights/provenance explicitly. Dataset publication is not authorized by its public
card. A derived training-friendly dataset will have its own linked card/version.

The maintainer accepted a small quarantined reader/local extraction, with every
scientific training/reference flag false; S02 #11 has draft PR #13 in an isolated worktree (86 tests/CI pass; fresh review
pending). Draft audit/card PR #12 is open; neither is human-merged.
S01 #10 remains open. Scientific D-004/D-005/D-007 acceptance, qualified reference,
benchmark grouping/tolerances, reviewed merges and integration checks remain ahead.
S03 will not claim simulation-level independence from an unverified single-source
collection. Wider CCSN/NSM coverage and NS1–NS3 remain incomplete.

Scientific reconstruction/RHS/rollout/energy accuracy and speedup are **not yet
evaluated**. Next: review the audit/card candidate, verify the reader against
independent oracles, and recover original provenance before requesting physical
benchmark acceptance. The milestone/native goal stay open until actual exits hold.
