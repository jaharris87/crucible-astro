# Phase 2D — D-039 distinct assembly qualification

**2026-11-23: arithmetic and derivative checks pass; first-step qualification
fails. No trajectory reference qualifies.** The maintainer [explicitly accepted
D-039](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7109353327)
before execution. Job **61873636** completed `0:0`, accounting for eleven executed
physical processes and two conditionally unattempted processes. Development
exhausted its native first-step attempts; validation accepted a reduced step.
The job's success status records complete accounting, not numerical qualification.

## Contract, source and provenance

The [accepted protocol](../../experiments/trajectory_reference/ASSEMBLY_QUALIFICATION_PROTOCOL.md)
names **`native-XNet-b64-productsum113-b64-v1`**. It preserves native binary64
coefficients, rates/EOS/physics, all 160 physical Y coordinates, composition-derived
Ye, and the original two development/validation initial states and forcing.
Abundance operands and b are promoted before products; native-order products,
class sums and left-to-right class joins use exactly 113 significand bits, followed
by one binary64 conversion per F component. This is a distinct digital RHS,
separate from D-019. Frozen-MLP compatibility remains unestablished. Original
pointwise data, weights/scalers, reference projects and historical failures remain
unchanged. Heating, active NSE/neutrino evaluation and final-test use are excluded.

Executed source is **`245ed9525ee9877653beab80eaf91bdd5493800c`**, tree
`27a4bbfc3e1b7db1c1ea59227bfc8f8aba0fa21c`. Independent exact-candidate review and
focused P2D-ASM-001 synthetic-interface repair verification preceded submission.
Preparation002 binds all **120 immutable identities**. Preparation001 was never
built or executed and is retained with its supersession reason. One fresh build
and all **16 compiled synthetic prerequisites** passed; no repair build,
infrastructure restart, completed-process repeat or numerical retry campaign
occurred. Native internal retries are accounted below.

| Retained object | SHA256 |
| --- | --- |
| Accepted protocol | `ff5515f04ecfdb9cb75f284882dc88d5beef30a25d1a4a8b9e9a18ba741abf02` |
| Preparation002 manifest | `466ed27595039ed142a2d653d6ba8a470994942136985c3214f5626b10b175ed` |
| Full raw source/build/input/output/job archive | `6b44f97052abaa407931994948819b1f99f9a073aaa72e51fc494bc0fd875580` |
| Execution-system identity recheck | `0911a964d3a64f3851fb80596dd99df04240bf5f8431242f89a35b93e0c50450` |
| Derived verification v2 JSON | `1331cf985b43eff9e7f625cd4ddf2278d5b6771997fce6054ee28b30731b3f5d` |
| Derived verification v2 NPZ | `fe6e07d58b96f90cf08e5dd37317ce5fc17b6a589931b8f6676d713137d62b3e` |

Private paths, states, coefficients and arrays remain local. The raw archive is
unchanged. Extraction omitted only the recorded absolute host Python-shim symlink.

## Arithmetic, identity and derivatives

All six identity processes pass: twelve calls across the three fixed D-038 states,
with within-process and fresh-process bitwise repeatability. Original F, native
coefficients, moments and conditioning reproduce D-038; initial controls also
match D-019. Exact rational verification independently emulates ordered binary128
products and sums, checks the operand/count-derived rounding bounds, and verifies
nearest-even binary64 conversion including zero semantics. All five distinct
retained workspaces pass every component. These checks qualify assembly conditional
on native binary64 b; they do not qualify rate/EOS/coefficient physical accuracy.

All three frozen full-F Jacobians complete. Independent difference-form checks
reproduce all **480 selected columns**; the actual source recomputes Ye and other
composition-dependent conditions while holding external forcing fixed. All **nine
state × direction agreement checks** pass their predeclared stable-window rule.
Of 81 direction/multiplier samples, 77 are admissible; the four largest-multiplier
refusals at development initial/Newton300 directions 1 and 2 remain explicit.
The other eight multipliers in each affected direction supply passing windows.

| Frozen state | max abs(original F − variant F), Y/s | Exact sum(A × variant F), 1/s |
| --- | ---: | ---: |
| Development initial | 4.263594747e-6 | +3.680470665e-10 |
| Validation initial | 7.998895803e-7 | −2.280600812e-12 |
| Development Newton300 | 3.828309232e-6 | +2.881542760e-14 |

Instantaneous baryon rates are diagnostics, not integrated drift or physical-error
bounds. Native binary64 coefficients and final F conversion still contribute
rounding. No charge conservation or silent renormalization is imposed.

## All first-step outcomes

Both standard processes request **1e-4 s**, using unchanged nonlinear controls
`aN=1e-13`, `rN=1e-11`, factor-one full-F finite differences and native LU/Newton.

| Declared process | Native attempts / Newton iterations | Achieved endpoint | Result |
| --- | ---: | ---: | --- |
| Development standard | 10 / 300 | 0 s | Failed; final normalized residual 4.430184552 > 1 |
| Validation standard | 8 / 213 | 7.8125e-7 s | Reduced step accepted; residual 0.189755162 |
| Development tight | 0 / 0 | None | Conditionally unattempted: both standard passes required |
| Validation tight | 0 / 0 | None | Same predeclared condition |

Development's final attempted h is 1.953125e-7 s. Every attempted h, all four
Newton phases, unfactored matrices, LU factors/pivots, F calls, residuals and
failure workspace are retained. No negative-iterate projection occurred in either
standard process. Validation's accepted Y is finite/nonnegative, in the declared
domain; nonunit initial baryon inventory changes by about 2.22e-16, below
`1e-10*max(1,abs(B0))`. Projection is zero against the unchanged step/cumulative
limits. All attempted physical evaluations and Jacobian probes retain their domain,
branch and IEEE accounting. No failed case is excluded or replaced.

The campaign records **177,347 physical RHS calls / 187,855 guarded requests**:
12 identity calls; 415/418/415 frozen-derivative calls; 102,601 development and
73,486 validation calls. Standard work accounts for 513 full Jacobians, LU solves
and Newton iterations, 18 step attempts and 16 retries. This is inside the accepted
finite scope; unused authority does not permit postphysical reruns.

Neither process completes the requested 1e-4 s interval. No 10 ms trajectory,
same-output-grid refinement comparison, global numerical convergence or clean
trajectory reproduction is established. Higher-precision assembly alone did not
remove the development solvability blocker. Solver-control refinement cannot
establish physical forcing accuracy or recover unresolved forcing history.

## Reporting, reproduction and cost

The first local reporter incorrectly tried to open cluster-library paths on the
analysis machine. Its failed JSON/NPZ remain preserved. Reporting-only repair
`e5cfa62c95203455da655d8b35db8eb00d5bc01a` leaves physical source, science gates and
criteria unchanged. A separate read-only execution-system check rehashes all
**68 actual build/runtime library files** against original compute-process
identities; its hostname is retained. The local verifier requires that receipt's
explicit SHA256 and verifies retained executables, build files and receipts.
No library path is remapped or skipped. See the [runnable guide](../../experiments/trajectory_reference/ASSEMBLY_QUALIFICATION.md).

Versioned offline verification passes software/provenance/failure-accounting
checks, with qualification and trajectory-reference flags false. Fresh-process
reload/recomputation also passes all 255 arrays by dtype, shape and bytes. This
is serialization and offline numerical-recomputation evidence, not clean trajectory
reproduction. Independent actual-artifact assessment is in progress.
Public synthetic tests cover arithmetic, nonlinear/failure records and malformed
or substituted identity evidence without private CI dependencies: **1,010 tests
pass, zero skips**; lint/format and frozen-documentation checks pass.

Measured scheduler wall is **8 min 54 s**, total CPU **517.237 s**. Build wall is
13.14 s, CPU 11.26 s, peak RSS 90,556 KiB. Campaign command wall is 513.18 s and
controller CPU 107.31 s; native development/validation steps consume 221.727 /
159.902 CPU s, with scheduler peak RSS 1,378,768 / 978,184 KiB. Batch peak RSS is
559,060 KiB; allocation records two CPUs and native work uses one rank/thread.
Scopes overlap and are not additive wall times. Raw campaign storage is
2,668,593,191 bytes; compressed archive 1,570,163,412 bytes; derived v2 JSON/NPZ
2,737,088 / 2,032,226 bytes. Persistence/diagnostic overhead is included in these
measurements; no matched-accuracy speedup is claimed.

D-039 permits no further producer build or physical evaluation. Complete the
artifact assessment and prepare the smallest evidence-backed next numerical
proposal. Any new execution or changed numerical contract needs a separate explicit
decision. Full 2D references, reference acceptance, exact integration-candidate
review, human-approved merge and merged-result verification remain outstanding.
Keep #44, the native 2D goal and milestone #3 open. Phase 2E remains excluded.
