# CRUCIBLE Phase 1 handoff

Updated **2026-11-17**. Phase 0A/0B are complete. **Phase 1 S01 is active;
no dataset or benchmark is scientifically qualified.** Native persistent goal
created and active for the exact [Phase 1 S01–S03 objective](PHASE_1_AUTHORITY.md).
Do not close it for partial exploration or a pending human merge.

[Milestone #2 — Phase 1 — Data qualification and benchmark definition](https://github.com/jaharris87/crucible-astro/milestone/2)
is open. [Progress](PROGRESS.md) tracks dependencies/issues/PRs; the [meeting snapshot](reports/2026-11-17-phase1-start.md) summarizes scientific status. No extra board.
The [final Phase 0B closeout](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6960154582)
confirms B01–B04 plus audit PR #9 integrated at
`01f06d8d3c2f9833dd84c5c3c9c05c034811c679`, with fresh review, concrete human
merges and passing merged CI (42 tests). Previous audit-in-progress statements
were stale; dated reports and original review records remain preserved.

## Current authority and work

The maintainer explicitly authorized Phase 1 on 2026-11-17; see the
[execution record](PHASE_1_AUTHORITY.md) and D-016 in [DECISIONS](DECISIONS.md).
Every merge still needs a concrete human decision. No producer execution,
reference edits, bulk conversion, training/model development, paid service or
deployment is authorized. Stop after Phase 1. D-013 removes resource caps and
per-command accounting; D-012/D-015 model policy and scientific gates remain.

[S01 issue #10](https://github.com/jaharris87/crucible-astro/issues/10) covers the
bounded source/data audit and living data card. The clean initial base was
`01f06d8`; branch `codex/phase1-s01-audit` holds [draft audit/card PR #12](https://github.com/jaharris87/crucible-astro/pull/12). The maintainer accepted the quarantined three-pair S02 reader/extraction scope;
[S02 #11](https://github.com/jaharris87/crucible-astro/issues/11) has [draft reader/extraction PR #13](https://github.com/jaharris87/crucible-astro/pull/13) in an
isolated worktree, with all scientific eligibility false. S03 and final benchmark
partitions remain gated; create its bounded milestone issue as prerequisites become concrete.

## Findings and evidence

- Candidate data exist at the maintainer's current ignored location. Updated
  `.local/REFERENCES.md` and `.local/phase1-paths.json` resolve it explicitly;
  bulk data were not copied. Derived audit evidence is separate under
  `.local/phase1-audit/`, not committed. References/raw inputs remain read-only.
- [S01 audit](phase1/S01_AUDIT.md): metadata-only inventory of 42,362 binary/text
  pairs; three decoded pairs / 1384 saved records, with framing/species/scalar
  checks and independent byte interpretation of one pair. This is software and
  source evidence, not training qualification. All physical-use gates remain open.
- Missing original histories/network inputs, build/run binding and tracer mapping
  prevent qualification. Initial/NSE derivative placeholders are excluded;
  ordinary stored derivatives have unmeasured accepted-state alignment. Energy
  is an internal-step diagnostic, not deposited heating. Condensed species output
  has repeated identities; full binary identity is separate. Recovered candidate tables specify zero active neutrino reactions; this narrows
  the earlier conditioning concern, conditional on generating-table association.
  Weak reactions remain, and a physical task is not yet accepted.
- [Raw data card](data-cards/genesis_datacard_ccsn_raw_candidate.md) uses the
  official released Genesis v2.0.0 narrative template as a living draft, with
  unknowns explicit and no full machine/schema-conformance claim. [Guidance
  evidence](phase1/GENESIS_GUIDANCE.md) pins sources/hashes and the current GitLab
  model-template access gap. Public documentation does not release the data.
- [Bounded extraction proposal](phase1/S02_EXTRACTION_PROPOSAL.md) recommends a
  small local HDF5/JSON derivative with its own linked card, exact raw identities
  and separate masks. No bulk conversion or label qualification is implied.
  Phase 2/model-artifact acceptance now calls for actual model cards; no model
  card/results or agent cards are fabricated.

Scientific performance/reconstruction/RHS/rollout/energy accuracy and cost remain
**not yet evaluated**. The coverage inventory is bounded and descriptive; no
simulation independence or representative NS1/NS3 coverage is established.

## Pending decisions and next action

The maintainer accepted only the three-pair quarantined ingestion semantics
before S02 and supplied the original Perlmutter location (kept local). Bounded
read-only inventory recovered input symlink locations and small metadata/network
candidates; the extrema symlink is dangling but not consumed by the inspected runtime. No producer execution was requested
or performed. [S01](phase1/S01_AUDIT.md) tracks subsequent recovery limits.
[Proposal #14](https://github.com/jaharris87/crucible-astro/issues/14) requests a
three-state offline accepted-output RHS comparison. D-017 execution authorization
was presented interactively and remains pending. The original external EOS source
files are inaccessible to the available login; two local reference versions differ,
so no substitution is authorized. Request original readable copies/version evidence
before any build/run. No producer execution has occurred.
D-004/D-005/D-007 remain open physical/benchmark contracts; no threshold or energy
choice is forced from structural observations. Missing semantics/provenance is
not successful completion. If recovery fails, prepare a concrete separately
authorized tiny producer/accepted-state RHS check after its inputs are known.

Fresh read-only exact-head/base independent reviews of PRs #12/#13 passed
with no consequential findings. PR comments preserve original results/limits;
only doc/status freshness updates follow for PR #12. Continue with final-candidate
CI/freshness disposition and the concrete human merge checkpoint. S01 candidate CI passes
42 tests; S02 candidate CI/local noneditable checks pass 86 tests. S02
head is `fb19f592f0e84d5b97c974322f353b7e48efbf5f`, base `01f06d8`. Its
local three-pair extraction and independent record oracles agree; all scientific
eligibility remains false. Private output/receipt is in the worker's ignored
`.local/s02/derived/three-pair-v0_1_0-final`, not a public dataset release. Present the concrete merge candidate only after required
checks/review hold. Human scientific acceptance is a separate gate. Verify any
human-approved merge and keep milestone/issues current. Phase 1 closes only when
its actual roadmap exits, card, accepted data/benchmark scope, reviewed merges and
integration checks hold.

Assignments so far: read-only producer audit and official-card guidance research,
both explicitly `gpt-6.1-sol` High, no substitution or Astra escalation. The lead
integrates and verifies in the current Codex session; no global model/tooling
settings changed. S02 implementation is explicitly `gpt-6.1-sol` High in a managed isolated worktree. Fresh exact-candidate PR reviews passed; see live PR records for final freshness and human merge checkpoints.
