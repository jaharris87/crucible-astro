# S03 benchmark definition: preparation and unresolved gates

2026-11-17, [S03 #15](https://github.com/jaharris87/crucible-astro/issues/15),
[Phase 1 milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2).
**No scientific train/validation/final-test membership is defined or accepted.**
This sheet records the actual bounded coverage and the decisions/evidence needed
to define an honest benchmark. It does not qualify labels or complete S03.

## Declared scope and coverage

Scope is exactly the three purposively selected [S01 pairs](S01_AUDIT.md), now
represented by the local [S02 derived dataset/card](../data-cards/genesis_datacard_ccsn_quarantined_v0_1.md).
The original XNet outputs remain unchanged. The derived manifest binds exact raw
pair identities, every saved record ordinal, ordered species, extraction recipe,
reader source and output fixity. Exact private membership stays local.
Coverage below was recomputed from the retained HDF5 arrays and agrees with the
raw audit. It is descriptive, **not a supported scientific domain**.

| Pair | Saved rows | Initial | Explicit NSE | Other | Observed T9 (GK) | Observed density (g/cm³) |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| A | 587 | 1 | 514 | 72 | 0.025253–26.8774 | 0.24520–2.30264×10¹⁰ |
| B | 742 | 1 | 671 | 70 | 0.023553–24.2839 | 0.16026–1.42912×10¹⁰ |
| C | 55 | 1 | 0 | 54 | 0.029559–1.06886 | 0.071333–3327.19 |
| Total | **1384** | **3** | **1185** | **196** | Purposive audit coverage | Not representative coverage |

Each pair has 160 ordered binary `(Z,A)` entries. All observed output spans are
approximately 0.414127–100 s; that endpoint is not an accepted physical rollout
horizon. Source/input inspection corroborates extrapolation for B. No broader
CCSN, NSM or r-process coverage is established by these three examples.

Every S02 scientific eligibility count is **zero**: state training, instantaneous
RHS, energy and rollout reference. Initial and explicit NSE records account for
1188 RHS exclusions; the 196 other rows still have unverified accepted-state
alignment, conditions and generating provenance. These reason sets can overlap;
unknown provenance affects all rows. The separately authorized [three-state
diagnostic #14](https://github.com/jaharris87/crucible-astro/issues/14) measures only
its named states. Success there cannot qualify all other rows or establish a
reference convergence/error budget.

## Scientific decision sheet

| Contract item | Current evidence / recommendation | Acceptance gate |
| --- | --- | --- |
| Intended task | D-003 accepts the starting sequence: full-state instantaneous `dY/dt = F(Y,c,t)`; finite-step prediction stays separate | Data/target qualification under D-004 still open |
| State and identity | Preserve source Y convention, ordered full binary species and explicit record identity; isomers/rates are not determined by `(Z,A)` alone | Accepted generating/declared-reference network and complete state contract |
| Conditions and closure | T/rho/time have inspected source units; one original history is associated by initial values/extrapolation. Initial composition Ye and history Ye differ. Candidate processed tables have zero neutrino rates, conditional on association; weak reactions remain | D-004: required `c`, inference availability, interpolation, prescribed/evolved status and thermal closure. No fixed Ye or presumed universal T/rho/Ye closure |
| Domain | Table above is observed raw coverage, including unqualified/NSE records | Human accepts a named qualified subset and domain, not these extrema as a validity box |
| Horizon | Instantaneous RHS is pointwise. A later rollout needs qualified initial states, history/grid, full attempted interval and domain-exit rules | No accepted rollout horizon; 100 s output endpoint is not one |
| Abundance observables | Propose signed species RHS components in physical source convention; later abundance histories/yields require a qualified rollout reference | Select observables/aggregation before model evaluation; condensed multi-species text is not authoritative |
| Energy | Store internal-step mass-excess diagnostic separately. Recommend exclude it as an instantaneous/deposited-heating target while meanings/reference are unqualified | D-005 must accept the pilot energy policy; exclusion is not energy-milestone completion |
| Constraints | Report baryon/positivity diagnostics and appropriate Ye evolution; do not normalize/clip away errors or enforce fixed charge | D-005/D-007: applicable constraints and justified tolerances |
| Reference | D-017 authorizes a small new documented kernel diagnostic with selected EOS dependencies; historical build association remains a distinct question | D-007: authoritative reference identity and numerical/physical error evidence; no reference accuracy acceptance yet |
| Metrics | Propose signed physical-unit component differences, absolute-error distributions by species/trajectory/regime, and explicit failure/eligible denominators | Accept weighting, relative/log floors, aggregates and observable-specific thresholds with reasons before final-test use |
| Cost | No inference/integration speedup measured; label-audit runtime is not surrogate performance | Later matched task/reference/hardware/timing boundaries; no Phase 2 measurements now |

No numerical scientific tolerance is inferred from source convergence controls,
observed normalization residuals, passing CI or a future three-state difference.
Use the [validation contract](../VALIDATION.md#benchmark-definition-and-partitions)
and preserve reconstruction, pointwise RHS, rollout, energy, provenance and cost
evidence separately. No reduction architecture or learning method is selected.

## Identity and leakage requirements

Raw identity is `(binary digest, companion digest, record ordinal)` together with
source units/species and explicit slab/local-zone locators. The ordinal is needed
because NSE repeats integration-step numbers. Derived copies retain raw ancestry;
different output hashes or file names do not make independent observations.
The derived identity adds source manifest, extraction configuration/source and
output digest. These are storage/lineage identities, not independent physical groups.

Before scientific partition construction, recover the parent hydrodynamic
simulation/run, tracer identity, reruns/variants and relationships among neighboring
or derived trajectories. All three current parent identities remain unverified.
Slab numbers, aliases and shared file containers cannot supply independence.
Conservatively keep the unresolved collection together in quarantine for engineering
use; this does not assert that its actual physical parent count is one.

Primary recommendation after qualification is **parent/family-disjoint holdout**,
with enough qualified independent groups for the intended allocation. If only one
parent is confirmed, the maintainer may instead accept an explicitly narrower
within-simulation trajectory-family estimand and justified grouping rule. That
cannot demonstrate simulation-level generalization. Random neighboring-row splits
and A/B/C-as-independent-parent splits are not acceptable shortcuts.

A concrete future split record must bind the accepted source/qualified membership,
group mapping and estimand, construction rule/version, seed when used, exact sorted
train/validation/test IDs and digest, exclusions with reasons, and human acceptance.
Construction must be unchanged by input enumeration order. No split fractions,
seed or real final-test membership is chosen before those prerequisites exist.

Checks on that actual implementation must verify uniqueness, complete declared
allocation or explicit exclusion, and pairwise disjoint raw ancestry, tracers and
accepted parent/family groups. Deliberate derived-copy duplication and related-group
overlap must fail distinctly. Unknown grouping or zero eligible membership must
not pass a scientific partition audit merely because empty sets are disjoint.
No such real-data partition check is claimed to have passed now.

## Train-only preparation and stopping boundary

Later fitted scalers, bases, encoders, species selections, floors and data-dependent
cutoffs use **training membership only**. Validation selects later hyperparameters
and checkpoints under a recorded protocol. Locked-test outcomes cannot guide
redesign without declaring reuse and establishing new confirmatory evidence.
Test the actual fit boundary when it exists by changing held-out extrema while
holding training fixed; fitted parameters must be unchanged. A test-only dummy
mean would not prove a future preprocessing implementation obeys this rule.
Phase 1 introduces no fitter or Phase 2 stack merely to manufacture that test.

S03 preparation can advance while S01/diagnostic work continues, but final S03
and Phase 1 acceptance remain open until the physical/reference decisions,
qualified membership, group/estimand acceptance, concrete partitions and meaningful
split checks hold. Scientific acceptance and software merge are separate. Keep
the [raw card](../data-cards/genesis_datacard_ccsn_raw_candidate.md), derived card,
milestone and handoff current; missing provenance or limited exploration is not
full training qualification.
