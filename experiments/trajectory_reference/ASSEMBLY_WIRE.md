# D-039 native artifact layouts

These files support the [accepted qualification protocol](ASSEMBLY_QUALIFICATION_PROTOCOL.md),
not a general trajectory format. Original D-036/D-038 layouts remain documented
in [forensic retention](FORENSIC_RETENTION.md) and [diagnostic wire formats](DIAGNOSTIC_WIRE.md).
All numeric streams use little-endian values. Refuse an unsupported representation,
wrong magic/version/count, trailing or partial row, nonfinite required field or
unexplained unavailable field. Raw files are immutable; derived reports are separate.

## Physical evaluations

`assembly-evaluations.bin` starts with eight int32 values:
`[0x43524145,1,160,496,0,0,0,0]`. Each row then contains 496 binary64 values:

| Block | Count / fields |
| --- | --- |
| Metadata | 16: call ID, role, context ID, time, T9, rho, B, Q, Ye, cv, etae, detaedt9, assembly nearest before/after, assembly gradual-underflow before/after |
| State | 160 physical Y |
| Original F | 160 native binary64 Y/s values from unchanged `yderiv` |
| Variant F | 160 binary64 Y/s values after the distinct promoted assembly |

Call/role/context fields are exact integer-valued binary64 metadata, not predictive
features. Original-kernel mode/exception observations remain in
`diagnostic-ieee.bin` (eleven int64 values per call); branch changes and stencil
attempts retain the D-038 streams. Bind these records by physical-call ID.
There is one EOS/rate/kernel evaluation per row, followed by variant postassembly;
the two F vectors do not denote two physical calls or two learned sources.

`assembly-ieee.bin` has four int32 header values `[0x43524149,1,21,0]` and 21
int64 values per physical call: call ID, five original-kernel flags before,
five after, five assembly-module flags before and five after. Each five-flag
block is invalid, divide-by-zero, overflow, underflow and inexact. Flags are
sticky observations and are not cleared; an already-set flag cannot be attributed
solely to the following operation. Underflow/inexact observations remain distinct
from unsupported arithmetic, nonfinite computation or failed conversion checks.

## Assembly workspaces

`assembly-baseline-001.bin` (and 002/003 for identity repeats),
`assembly-accepted.bin` and `assembly-failure.bin` start with nine int32 values:

`[0x43524157,1,160,1862,4860,53,19,14548,math_ok]`.

They contain 490 binary64 values: call ID, time, T9, rho, B, Q, Ye, cv, etae,
detaedt9, then Y, original F and variant F (160 each). The remaining values are
14,548 IEEE binary128 operands/results, **sixteen bytes each**, in this order:

| Block | Count / order |
| --- | --- |
| Final totals before binary64 conversion | 160 |
| Class totals | 640, Fortran ordering of four classes × 160 species |
| Products | 6,794, native extended-entry order within reaction order 1–4 |
| Running class sums | 6,794 in the same order |
| Absolute-term sums | 160 |

Decode binary128 from its sign, fifteen-bit exponent and 112 stored fraction bits
using exact rational arithmetic; do not rely on the local NumPy `longdouble`
format. The compiled precision fixture establishes kind, storage, representation,
conversion and mode behavior before physical evaluation. Check `math_ok` and the
supported-operand/intermediate bounds rather than treating successful parsing as
arithmetic qualification.

Paired `baseline-001.bin` / 002 / 003, `baseline-accepted.bin` and
`baseline-failure.bin` retain the original D-038 baseline layout with original F,
coefficients, binary64 b and branch signature. Both files describe the same
physical-call input and native coefficient workspace; the assembly file adds the
distinct numerical result. On exhaustion, use the retained last evaluated state,
conditions, EOS, original/variant F and quad buffers. Native retry cleanup may
already have reset mutable trial arguments. Preserve that distinction.
If the native original RHS has not completed (`physical_phase=1`), no current
assembly pair can be exported: log it as unavailable and retain the generic
phase-tagged failure workspace with its unavailable F/b fields. A failed assembly
or mode check cannot reuse a preceding call's quad or variant buffers.

In D-039, the generic `failure-workspace.bin` F field follows the integrated
variant source once assembly completes. `baseline-failure.bin` explicitly carries
original F; `assembly-failure.bin` adds variant F and quad operands/results.
The source identity and filenames distinguish those meanings.

Frozen derivative commands retain the D-038 directional stream layouts, but only
factor one (slot two of the four-slot Jv format) is declared. Other slots are
unavailable, not additional attempted matrices. D-039 has three full matrices and
nine state/direction comparisons, rather than D-038's twelve and thirty-six.

## Newton records

`assembly-newton.bin` starts with eight int32 values:
`[0x4352414e,1,160,78568,10,160,0,0]`.
Every phase record contains ten int64 values, 78,568 binary64 values and 160 int32
pivots. Integer metadata are Newton ID, step, iteration, Jacobian ID, Jacobian
baseline call, pre-update F restoration call, post-update F call, LU info, solve
info and phase. Phases 1–4 retain pre-LU, post-LU, pre-post-update-F and final
residual states. Unavailable blocks use explicit NaNs and unavailable info uses
−999; phase and failure status determine which fields are required. Flush before
operations that may fail. Incomplete attempts retain available phases and cannot
qualify as complete first-step evidence.

Binary64 blocks are time, h, normalized residual norm, residual A-L1, projection
A-L1, cumulative final projection before this step, aN, rN; old Y, pre-update Y,
pre-update variant F and original F (160 each); J, unfactored M and LU (160 × 160
each, Fortran ordering), with RHS (160) between M and LU; then correction,
unprojected Y, projected post-update Y, weights, component residual and projection
delta (160 each). Bind matrices to the Jacobian baseline, and post-update residuals
to their actual post-update call. Neither workspace may be substituted for the
other.

The four phase records are observational exports of one Newton iteration, not
additional iterations or physical evaluations. First-step status records must
separately retain requested interval, every attempted h, achieved time, accepted
or failed outcome and any conditionally skipped tight attempt. A short accepted
step does not complete the original requested interval or a 10 ms reference.

`native-step-attempts.bin` has int32 header `[0x43524154,1,7,0]` followed by seven
binary64 values per attempt: step, attempt ID, time, h, T9, rho and preceding RHS
call count. `first-step.bin` has header `[0x43524153,1,160,0]`, followed by requested
h, achieved time, accepted flag, attempt count, final normalized residual and final
projection, then endpoint Y (160). A failed request retains its unchanged initial
endpoint and explicit failure status. `assembly-counters.json` separates guarded
fresh-call requests from physical original-kernel evaluations and completed variant
assemblies; all planned conditional outcomes remain in the campaign manifest.
