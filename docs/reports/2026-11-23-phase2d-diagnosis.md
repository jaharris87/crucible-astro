# Phase 2D offline diagnosis — 2026-11-23

**2D remains incomplete: no accepted full-horizon reference.** Work resumed on the
maintainer’s explicit request. This author-prepared report adds offline checks to
the preserved [pause checkpoint](2026-11-20-phase2d-checkpoint.md); it does not
relabel the original campaign or its review. [Issue #44](https://github.com/jaharris87/crucible-astro/issues/44)
and [draft PR #51](https://github.com/jaharris87/crucible-astro/pull/51) remain open.
No new native build or physical evaluation was performed for this diagnosis.

## Evidence checked and actual outcomes

Reverified the complete paused archive SHA256
`75a5949e8fb74cfe386a415e40c7ecc2e284042d96614b2179a3bf77bb617ec2`,
all 94 prepared source/input identities and every completed attempt’s inventory.
The host-specific absolute Python shim is preserved in the archive but omitted
from local extraction; it is not an input, source or native output. Original raw
and accepted artifacts remain unchanged. Main remains `75b2ec3`; the paused
execution source is still `a771930`, regardless of later diagnostic-tool repairs.

Offline verification accounts for all 18 declared primary processes. Both initial
RHS controls match original D-019 component bits. Five numerical failures and the
interrupted validation run remain failures; four validation and six Jacobian
processes were not attempted. No clean reproduction was submitted.

| Development run | Retained accepted steps | Final attempted h (s) | Minimum norm in final trial | Final norm |
| --- | ---: | ---: | ---: | ---: |
| L0 | 0 | 1.953125e-7 | 15.9308134 | 27.4510998 |
| L1 | 0 | 9.765625e-8 | 7.8348743 | 12.1843414 |
| L2 | 0 | 4.8828125e-8 | 3.6799102 | 10.0088550 |
| L3 | 0 | 2.44140625e-8 | 2.0215758 | 5.1999413 |
| L3 tight | 0 | 2.44140625e-8 | 20.2157583 | 51.9994130 |

Each run retains all 300 Newton residual rows; the required norm is at most one.
No Newton projection occurred. Validation retains 25 complete accepted-state
records (including initial), ending at 2.539062500000003e-5 s of 0.01 s, and 1261
complete Newton rows before interruption. Its native status remains RUNNING,
its process manifest incomplete, and its outputs are not a completed reference.
Missing-output masks remain explicit even when process finalization did not occur.

Fresh-process derived JSON/NPZ reload passes exact dtype, shape and array-byte
recomputation while correctly reporting `numerical_pass=false`. This establishes
reproduction of the saved analysis, not reproduction of a successful trajectory.
The private verification JSON SHA256 is
`4751d4730c74fe0e1ca8e0faceb0bd4dc0d4d3e5b64bd4aec0155e441203e812`.
The verifier’s source hashes and exact numeric-detail manifests are embedded.

## Findings and bounded dispositions

- **P2D-NUM-001:** accepted nonlinear convergence failed. The existing independent
  L0 recomputation and this full-population offline inspection support the failure.
  Smaller steps lowering typical residuals and coarse saved F increments motivate
  investigation of cancellation and finite-difference/Newton precision. They do
  not establish one cause, a converged solution, or new tolerances.
- **P2D-PROP-003:** the original mixed-sign diagnostic direction is inadmissible
  at all nine multipliers for both initial states. Preserve the original protocol.
  A nonnegative alternating-support direction is proposed only for the new
  frozen-state diagnostic; derivative/EOS/branch agreement is not yet measured.
- **P2D-IMPL-002 (snapshot association):** independently corroborated at pause;
  retry cleanup reset state/forcing before exhaustion persistence, mixing those
  fields with the preceding F/LU. Repository repair `7247209` retains evaluated
  inputs/EOS outputs and records the distinct matrix baseline. Historical bytes
  are unchanged. Public static checks pass; the new compiled synthetic retry
  fixture and independent repair verification remain pending.

The offline coefficient-conditioned arithmetic tools reuse the accepted Phase 1
mapping/bound routines. Independent small public oracles cover signed cancellation,
repeated reactants, subnormal amplification, fixed-b derivatives, BE residuals and
linear backward errors. They import no physical evaluator. Conditional exact
arithmetic is not an EOS/rate validation or replacement reference.

## Next concrete decision

[Proposed D-038 diagnostic protocol](../../experiments/trajectory_reference/DIAGNOSTIC_PROTOCOL.md)
freezes the two original initial states and development L0 Jacobian-baseline record
300. It proposes a single diagnostic build, repeatability controls, conditional
arithmetic, four fixed finite-difference increments and frozen linear/Newton algebra.
It does not integrate a trajectory or select new solver controls. The proposal
and implementation require fresh exact-candidate independent review, then explicit
scientific and producer-scope acceptance before any build or physical call.
A later trajectory protocol and authority remain separate. No learned-model
rollout, fitting, changed preprocessing, final-test outcomes or Phase 2E is included.
