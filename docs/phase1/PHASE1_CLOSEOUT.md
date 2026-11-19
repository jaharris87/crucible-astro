# Phase 1 qualification and exit evidence

2026-11-19. [Closeout PR #35](https://github.com/jaharris87/crucible-astro/pull/35).
[The live final integration receipt](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482)
records whether final review, human merge and merged checks are complete.
D-025 accepts the named benchmark; acceptance alone does not close the phase.
[Milestone #2](https://github.com/jaharris87/crucible-astro/milestone/2) and the
native S01–S03 goal close only after every exit below is actually satisfied.
The subsequent independent audits of `15ac601` are assessed under
[issue #36](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016554530).
Their numerical corrections [merged in PR #37 at `850996e`](https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017579899)
with the reviewed tree, D-026 acceptance and 454 merged tests/CI passing. PR #35
subsequently merged at `e86c7a2` after final independent freshness and concrete
human approval; its reviewed tree, installed package, 454 tests and merged CI pass.
The live final receipt records actual administrative closure.
Original audit reports, proposals and accepted data are preserved.

## What the data support

`ccsn-primary-native-rhs-pointwise` 0.1.0 qualifies **24,314 exact states from
380 histories** for finite within-parent pinned-native-XNet pointwise numerical
emulation. [The qualified data card](../data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md) gives the scientist-facing
purpose, provenance, physical meanings, access/rights, preparation, coverage and
limits. It links the unchanged raw and quarantined collections.

The full ordered 160-species Y and recorded T9/rho define the unchanged state;
Ye is the native Q/B moment. Fresh D-019 numerical F replaces unqualified stored
step derivatives as the target. Weak/screening are retained, heating off and
active neutrino rates zero. Energy/rollouts stay excluded. D-024 scores direct
digital fidelity; no physical abundance-change or application allowance is invented.
One parent, operational groups, residual correlations and support gaps bound the
claim; no simulation independence or broader physical accuracy is asserted.

D-026 accepts scorer source `c287f873ede888c12128552046176fd6618556081dc907c4fccadb491bd056b7`
as an explicit reporting-arithmetic successor. The original D-025 overlay, scoring
configuration and predecessor source binding remain unchanged; future results bind
the actual successor plus its adoption receipt. This does not relabel the data or
change the fixed D-024 profiles and named qualification scope.

## Actual qualified view and preparation

A new local JSON overlay references the **unchanged 109,687,400-byte HDF5** and
38,652-byte payload manifest. It does not copy or rewrite either. State/RHS use
eligibility is positive for 24,314 named records only; energy/rollout positives
remain zero, and all four original HDF5 quarantine masks remain false.

The retained one-off generator/recipe binds actual D-025 receipt to the accepted
proposal, then per-record qualification, exact membership and final canonical
acceptance digests, then overlay/delivery manifests. No record hashes a future
receipt or itself. File SHA256 and canonical JSON digests are labeled separately.
This is a bounded recipe, not a new registry or metadata framework.

Author checks reconstruct the original candidate from the complete pool,
contract and groups; call the existing complete scientific validator; verify all
24,314 IDs, use masks, memberships, original packet digests and working physical
input fingerprints; and rehash 43 parent bindings. Working fingerprints and
source-call digests have different documented encodings and are checked separately.
The initial pre-output incorrect hash comparison is preserved; no output was
created by that failed preflight. A separately interpreted author verifier passes
18 rejection controls. Actual fresh independent verification is a separate gate.

| Retained local artifact | SHA256 |
| --- | --- |
| Accepted proposal | `0a6c16002f02ee5d2b5bdcf81d60c11edf4ea05b39c6cd469aab7d0bfa635a42` |
| Accepted packet manifest | `f3555be7c105e96511d5800bf8a0b827736c37f4dae04a04bc570ac443bf9847` |
| Overlay manifest | `e1bcd8b3cceabf252c1307ad008cdbc4a1da1cd556e84bf923d742ce3cf2ce0c` |
| Delivery manifest | `11dd68c7df41d7c48cbdfed931988d4a0ef0ae737fb706e5df72999e44993421` |
| Final acceptance file | `ca4c1f3bb3149d75b02006f0a0b9371e46c29472115c6c0354955a44f17ae35d` |
| Generator | `d3c3da1c80dd7d2397469c3147f9d498de6c1e38c536a7fca035ae1d0d65d6f4` |
| Explicit recipe | `b3cfc7f474deb8f71d2af8c4cb14aa3fee1d7392847ea41043073037fdb8dcf7` |
| Author verifier | `1663d0da8a78700743798f7f3d48ffa9e1f6c8a6c9eb83e6d61b1a4533e1c83d` |
| Author result | `a119d9382284397e678f823efca18267f2f47b34c4c83739f7c98fc1a6009654` |

Private recipes/paths/records remain local. The view resolves through those explicit
locators and digests; CI does not depend on them. Dataset redistribution authority
is unresolved. Archived preparation-time pending/false statuses remain historical;
only the separate D-025-bound overlay provides current qualified uses.

### Local access and recovery

Request the named view/version and local locator configuration from the maintainer.
Inspect its overlay manifest to locate the unchanged payload, accepted eligibility
and exact membership files, then verify their declared digests before use. Loading
the HDF5 alone does not recover qualification. There is currently no committed
qualified-split loader; a fail-closed ordinary array-loading function is proposed
before the first fit in the [transition recommendation](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016854401).

Retain the pinned source checkouts or recover their exact committed file versions
from Git and verify the manifest hashes. A worktree's local path is a locator,
not the source identity. Do not edit accepted manifests to relocate files or rerun
their preparation recipes; a future loader can use a separate local resolver
while checking the original identities. Canonical absolute paths can be obtained
with `Path(path).resolve()` before supplying them to the strict materializers;
their no-symlink and inspectable-partial-output policies are unchanged.

## Required exit evidence

| Requirement | Actual evidence / closure gate |
| --- | --- |
| S01 layout/species/units/timing and exclusions | [S01 audit](S01_AUDIT.md), [expanded audit](PRIMARY_EXPANSION_AUDIT.md), [declared reference](RHS_REFERENCE_SCOPE.md); initial/NSE/table/layout exclusions retained |
| Accepted/trial derivative alignment | Three-state and full finite reference audits quantify stored/fresh differences without a solver-defect claim; only fresh native F qualifies |
| Original versus new provenance | [Parent attribution](PARENT_PROVENANCE.md), separate actual pilot/primary build/run chains; historical generator gap explicit |
| S02 independently interpreted reader | [PR #32 independent actual review](https://github.com/jaharris87/crucible-astro/pull/32#pullrequestreview-5977900994), complete 24,314-row/two-chain evidence and malformed/ordering/validity tests |
| Actual primary reference execution | [Execution report](PRIMARY_REFERENCE_EXECUTION.md); all 19,159 authorized calls verified, controls/echoes/conditional arithmetic/receipt/transfer checks pass; no new call authority |
| Qualified/excluded counts and partitions | Overlay/card: 17,659/3,220/3,435 states, 274/51/55 histories, 66/14/14 operational groups; 6,158 ordinary exclusions; exact original-input scientific validator and fresh overlay verification |
| Human task/reference/metrics/tolerance acceptance | [D-025](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014300546), [D-024 scoring](NATIVE_BENCHMARK.md), [train-only/grouping rules](PARTITIONS.md) |
| Living Genesis data card | Actual pinned v2.0.0 guidance/template and new linked qualified card; access/rights/schema limits explicit |
| Reviewed engineering merges/checks | [PR #32 integration](https://github.com/jaharris87/crucible-astro/pull/32#issuecomment-7014367929), [PR #34 integration](https://github.com/jaharris87/crucible-astro/pull/34#issuecomment-7014572050); 419 merged tests, CI and exact reviewed trees |
| Assessed audit corrections | [Issue #36 dispositions](https://github.com/jaharris87/crucible-astro/issues/36#issuecomment-7016554530); [PR #37 integration](https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017579899), exact reviewed tree, independent initial/focused review, D-026 and 454 merged tests/CI; current-document review freshness/human merge remains |
| Final independent artifact/source review and human closeout merge/checks | Must be recorded with exact candidates/artifacts in the live final receipt before phase/milestone/goal completion |

## Stop and wider gaps

No model, architecture, fitting, rollout, final-test performance or speedup result
was produced. No Phase 2 is authorized. The Phase 2/later acceptance criteria
require actual model cards and separate physical, integrated, solver and cost
validation. Wider CCSN/NSM coverage and full NS1–NS3 remain incomplete; this phase
qualifies the named benchmark, not the entire raw collection or those wider claims.
