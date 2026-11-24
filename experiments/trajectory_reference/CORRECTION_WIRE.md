# D-040 native wire contract

This is the explicit compact retention plan for the NEW D-040 commands. It does
not reinterpret historical D-036/D-038/D-039 streams. The accepted protocol stays
byte-for-byte unchanged. Exact implementation review must pass before compilation
or physical evaluation. This source has not yet been compiled or evaluated.

## Invocation and inputs

Run `trajectory_driver correction-control`, `correction-trajectory` or
`correction-diagnose` in a fresh attempt directory containing `input.bin` and the
usual hash-bound network/tables. There are no further CLI arguments. The existing
input-v1 layout, species identity checks and forcing remain unchanged. Header
word 7 is zero for controls/diagnostics and one for trajectories. The leading two
binary64 values mean correction controls in these commands ONLY: exactly
`(1e-15,1e-13)` standard or `(1e-16,1e-14)` tight. The adapter then sets the
separate residual-reporting controls to `(1e-13,1e-11)` for every new run.

For a frozen diagnostic, the initial vector is the frozen state, and the first
mesh/requested time is its exact time (0, 5 or 10 ms). The direction coordinate
remains the dominant initial A*Y coordinate selected before the trajectory.
The diagnostics use one factor-one full-F J, followed by the unchanged D-039
directional helper with nonnegative odd-species support. There is no factor sweep
and no second production J. The fixed D-039 directional and matrix-status wire
layouts remain unchanged; adjacent-window acceptance is an offline gate.

`correction-control` writes `control.bin` (160 variant F binary64) and
`control-original.bin` (160 original F binary64). All new commands export
`species.bin`, `used-maps.bin`, `baseline-001.bin` and
`assembly-baseline-001.bin`. Controls make exactly one fresh evaluation.

## Compact Newton stream

All integers/floats use the existing little-endian, int32/int64/binary64 contract,
with Fortran array order. `correction-newton.bin` begins with eight int32 words:
`[0x4352434e,1,160,1936,12,0,0,0]`. Each row contains 12 int64 then 1,936 binary64
(15,584 bytes). Integer IDs, in order:

| Offset (zero based) | Meaning |
| --- | --- |
| 0–2 | Global Newton ID, native step ID, iteration within attempt |
| 3–6 | J ID, J baseline call, J restore call, post-F call |
| 7–8 | Native LU and solve info (`-999` means not reached) |
| 9 | Last completed phase, zero through four |
| 10 | Global native attempt ID |
| 11 | Whether pre/post Y are bitwise identical |

The first 16 float scalars are:
`time,h,raw_residual_Linf,raw_residual_AL1,projection_AL1,cumulative_projection_before,`
`aN,rN,aC,rC,Ccurrent,Cprevious,raw_delta_ALinf,raw_delta_AL1,applied_ALinf,applied_AL1`.
The raw residual Linf is the original D-036 normalized A-weighted infinity norm;
it is reported and checked finite, but does not decide convergence.

The remaining twelve contiguous vectors each have 160 components:

| Vector | Float slice (zero based) | Meaning |
| --- | --- | --- |
| 0 | 16:176 | Old accepted state at attempt start |
| 1 | 176:336 | Pre-update Newton state |
| 2 | 336:496 | Unprojected `pre + raw_delta` |
| 3 | 496:656 | Post-projection Newton state |
| 4 | 656:816 | Current raw computed delta |
| 5 | 816:976 | Previous raw delta within this attempt |
| 6 | 976:1136 | Actual applied `post - pre` |
| 7 | 1136:1296 | Current correction weights |
| 8 | 1296:1456 | Signed raw `post-old-h*F(post)` |
| 9 | 1456:1616 | Signed projection `post-unprojected` |
| 10 | 1616:1776 | Variant post-F |
| 11 | 1776:1936 | Original post-F |

Every completed iteration emits and flushes one phase-four row, including failed
attempts. A fatal failure before its row emits the last partial phase, with NaNs
for unknown float fields. Phases are the existing D-039 phases: one after J/M,
two after LU/RHS, three after correction/projection, four after fresh post-F and
raw residual. J/M/RHS fields not yet reached remain unavailable. First iteration
previous delta and Cprevious are NaNs. Each retry resets history. Acceptance
requires iteration >=2, both ratios <=1 under the SAME current weights, and all
other gates; first-iteration NaNs are never compared to accept a step. Projection
and the old residual retain separate weights/semantics.

The native `newton-residuals.bin`, every projection log, counter-events,
native-step-attempts, all IEEE observations, J baselines, selected fd-columns,
every fd-probe-attempt (including refusals) and branch-events remain retained in
their existing layouts. `fd-probe-attempts.bin` has 12 binary64 per row:
`J,column,stencil,nominal_delta,d1,d2,p1_column,p2_column,ok1,ok2,call1,call2`.
Its call IDs are zero for a request refused before evaluation; domain or branch
refusals have false status. The selected fd-columns row adds actual reduction
count. Baseline plus the actual representable one-coordinate offsets reconstruct
all column inputs. Branch-event IDs bind transitions to physical call IDs.

## Accepted states

The existing headerless `accepted.bin` stays exactly 488 binary64 per row, with
variant F in its F slot; `accepted-forcing.bin` remains three binary64 per row.
The supplemental `correction-accepted.bin` header is eight int32:
`[0x43524341,1,160,496,0,0,0,0]`. Each following row uses the existing
assembly-evaluation layout (496 binary64):
`call,role=11,accepted_count,time,T9,rho,B,Q,Ye,cv,etae,detaedt9,`
`nearest_before,nearest_after,gradual_before,gradual_after,Y[160],originalF[160],variantF[160]`.
The four mode flags are one, as asserted at the generating assembly call.
State/time/variant-F bytes align with the corresponding accepted row. The initial
row has accepted_count zero and RHS call one. All process counters start zero;
J/attempt/Newton IDs begin one. `probe_count` counts guarded probe requests,
including refusals; `rhs_count` counts actual evaluations. `accepted_count` is
incremented by the driver only after native `solve_be` succeeds.

## Predeclared forensic retention and buffers

Ordinary successful Newton iterations write compact rows and all attempt/branch/
IEEE/counter metadata, without disk probe F or dense J/LU. In memory, only the
CURRENT iteration keeps its original/variant F records (496 binary64 each, at
most 8,643 rows = 34,295,424 bytes; below 33 MiB), four matrix phases (about 2.4 MiB)
and the baseline/post coefficient/113-bit workspaces. Each next iteration reuses
these buffers. No per-probe 113-bit polynomial workspace is buffered.

Every trajectory's first native step retains all attempts and all raw original/
variant F/probe rows in `assembly-evaluations.bin`, with all four dense phases in
`assembly-newton.bin`. The six diagnostic processes retain all their raw F/probe
rows and the single full J/directional records. Both streams retain their D-039
headers/layouts. The legacy `diagnostic-evaluations.bin` retains original F for
the directly forensic calls; compact ordinary F is carried by the new records.
On fatal failure, the last iteration's buffered raw assembly-evaluation rows and
matrix phases are flushed to those same streams, without a new evaluation.

Coefficient/113-bit forensic granularity is explicit: full original and quad
workspaces at initial, retained Newton BASELINE and POST evaluations, final
accepted state and last actual failing evaluation. This does NOT claim full
per-probe polynomial/coefficient verification: retained probes carry their exact
input/original F/variant F, stencil and J/call IDs. Baseline/post workspaces permit
the existing exact rational assembly oracle. Files `forensic-original-NNNNNNNNNNNN.bin`
and `forensic-assembly-NNNNNNNNNNNN.bin` pair by RHS call ID for initial and first
step/diagnostic baselines/posts. `baseline-accepted.bin` and
`assembly-accepted.bin` retain the final full-horizon workspace. Ordinary current
baseline/post buffers are flushed only on failure, as
`failure-iteration-{baseline,post}-{original,assembly}.bin` where available.
The original/quad file formats are unchanged from ASSEMBLY_WIRE.md.

`baseline-failure.bin`, `assembly-failure.bin` and `failure-workspace.bin` refer
to the last ACTUAL evaluated input/workspace. A rejected post-update input is
separately retained in `failure-state.bin`, which may therefore differ. Native
retry cleanup cannot change the recorded actual-evaluation inputs. An interrupted
process may lose unflushed in-flight buffers; preserve its last flushed records
and disclose unavailable diagnostics rather than invent them.

## Compiled prerequisites (prepared only)

The existing `trajectory_synthetic` executable gains successful scenarios
`correction-nonlinear`, `correction-stiff`, `correction-rounded`,
`correction-current`, `correction-retry` and `correction-projection`.
The stiff affine scalar has an independently computed 113-bit BE root; its
nearest binary64 state has a large raw residual and small consecutive computed
corrections. The rounded-update scenario has a raw `1e-17` correction which
rounds away at Y=0.5 and remains unacceptable under strict fixture weights.
The current-weight adversary changes whether the previous correction passes;
retry and nonlinear scenarios exercise the real adapter. Synthetic-only controls
deliberately vary to exercise guards; physical commands accept only the two fixed
protocol settings. `correction-projection-bound` must fail with
`final Newton projection exceeds per-step bound`; `correction-incomplete` must
fail with `incomplete horizon`. All sixteen historical prerequisites remain.

These fixtures are source only until the exact implementation review passes.
