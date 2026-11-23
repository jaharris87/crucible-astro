# Phase 2D — completed D-038 frozen-state diagnostics

**2026-11-23: diagnostic evidence passes; no trajectory reference qualifies.**
The maintainer [accepted D-038](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7107405775)
before execution. Job **61864997** completed `0:0`: one fresh build, all eleven
compiled synthetic prerequisites and all nine declared native processes passed
their software checks. No repair build, infrastructure restart, trajectory step
or numerical retry occurred. This report follows the [original offline diagnosis](2026-11-23-phase2d-diagnosis.md);
it does not relabel that report or the failed D-036 campaign as newly successful.

## Scope and identity

The [accepted diagnostic protocol](../../experiments/trajectory_reference/DIAGNOSTIC_PROTOCOL.md)
uses the unchanged development and validation initial states, plus chronological
development L0 Jacobian-baseline record 300. No case was selected from new outcomes.
Six repeatability processes precede three derivative processes. Physical ordered
160-species Y, Y/s derivatives, T9/rho forcing, native composition-derived Ye,
network, tables, physics and domains remain those of D-036. Heating, active NSE,
learned-model integration and final-test outcomes are excluded.

Executable/analysis source is **`ae6971522ba1333f550664ac793be6b662e3dae4`**;
later status-only heads do not replace that binding. All 92 immutable preparation
identities and completed raw-stream identities verify. The eleven compiled
fixtures include consistent evaluated-state retention after all ten retry resets.
The same executable and 68 runtime-library identities serve all nine processes.
Native counters record **4,384 RHS calls**: 12 identity calls, then 1,450 / 1,471 /
1,451 calls for development initial / validation initial / Newton300 diagnostics,
within the declared 104,209-call envelope. All Newton, retry, step, projection and
accepted-step counters are zero.

| Retained object | SHA256 |
| --- | --- |
| Accepted protocol | `ea722cbabf71d79453a30c35f6f07de7a2c065fe14a9a2e1f442160ada4be7a1` |
| Fixed private annex | `dbb954afac144d9305a87e483c0c08833a8cdf2487d390f2d6532e5e72a814eb` |
| Full raw source/build/input/output/job archive | `02f2c62ade306d21f8cd5c584577fc215e1df34f646114559f5f05efcc8523bd` |
| Derived verification JSON | `3ca39a51b46878f2866ba25d9de21f3db293e68ac84801778edd7272dbfb9081` |
| Derived numeric NPZ | `b5c2a6f949c3ad550c8c9c4e761835fd9bf85b7836e749a8cbf2967cb04ceb2c` |

Private locations, states, coefficients and arrays remain local. The original raw
archive is unchanged. Local extraction omitted an absolute Python shim symlink,
recorded separately; this does not alter the archive or numerical files.

## Repeatability, derivatives and conditional arithmetic

Within-process repeats, fresh-process baselines and diagnostic baselines agree
bitwise. Both initial-state original-F controls match D-019 bits. IEEE observations
show nearest rounding, unchanged supported gradual underflow and no invalid,
divide-by-zero or overflow flags; they do not identify DAZ.

All **12 full-F Jacobians** complete. Independent difference-form recomputation
matches all **1,920 selected finite-difference columns** exactly. No column needed
a halving. All **36 state × direction × factor agreement checks** pass the
unchanged A-weighted threshold and two-adjacent-multiplier criterion. Of 81 independent
direction/multiplier samples, **77 are admissible and four are explicitly refused**:
the largest multiplier for directions 1 and 2 at development initial and Newton300.
The other eight multipliers supply stable windows. Validation admits all nine
multipliers for all three directions. No refusal is replaced or omitted, and no
production increment factor is selected from these outcomes.

Exact binary-rational reconstruction reproduces the fixed-b polynomial and its
160 × 160 derivative at all three states, and the polynomial at the single frozen
candidate. Native b formation, assembly and fixed-b derivative satisfy their
supported operand/count-derived rounding envelopes. This tests arithmetic
conditional on native binary64 coefficients; it does not verify those coefficients,
rates or EOS, or separate product-rounding error from summation-rounding error.

| State | max abs(native F − exact fixed-b F), Y/s | max abs(A × difference), 1/s | sum(A × native F), 1/s |
| --- | ---: | ---: | ---: |
| Development initial | 4.263696739e-6 | 8.213306716e-6 | +1.300698554e-5 |
| Validation initial | 7.998895810e-7 | 7.998895810e-7 | −1.273390143e-6 |
| Development Newton300 | 3.828309235e-6 | 9.714655575e-6 | −1.378709087e-5 |

The exact fixed-b polynomial baryon rates are respectively approximately
−5.83e-12, −2.27e-12 and +1.83e-14 1/s. These three instantaneous rates neither
establish integrated drift over 10 ms nor prove the original numerical RHS cannot
meet D-036. No constant-charge condition is imposed.

## Frozen linear solve and nonlinear residual

All four LAPACK factor/solve pairs return info `0/0`. Saved unfactored matrices
and right-hand sides match separate NumPy recomputation bitwise. Exact
mass-scaled backward errors retain both measures:

| FD factor | Normwise backward error | Maximum componentwise backward error |
| --- | ---: | ---: |
| 0.1 | 4.304633226e-20 | 1.513864258e-5 |
| 1 | 5.143624832e-20 | 8.944810102e-6 |
| 10 | 6.698904158e-20 | 3.214951235e-6 |
| 100 | 5.158086447e-20 | 4.599863746e-5 |

Mass-scaled absolute linear-residual maxima are about 1.81–2.82e-15 1/s.
Small normwise backward error does not establish accurate corrections in every
component; conditioning and correction forward error remain unestablished.
Native RHS versus exact alternate −R/h differs by at most 6.8643e-15 Y/s.
Separate-operation BE residual rounding contributes at most 8.0547e-9 on the
unchanged nonlinear scale.

Let `R_native = A*(Y−Yold−h*F_native)/scale`,
`C = A*h*(F_native−F_exact_fixed_b)/scale`, and `R_fixed = R_native+C`.
Signed entries of largest absolute magnitude are:

| Quantity | Frozen baseline | Unprojected factor-one candidate |
| --- | ---: | ---: |
| R_native | +32.128946924, species 93 | −27.451099849, species 93 |
| C | −15.633231889, species 108 | +18.020651802, species 101 |
| R_fixed | +32.376607999, species 93 | −30.501776368, species 93 |

The candidate equals saved Y plus the factor-one correction bitwise, without
projection. At species 93 its assembly contribution is −3.050676519; the baseline
contribution there is +0.247661076. Assembly discrepancy is material on D-036's
weights, but does **not** remove the dominant residual or establish its sole cause.
The candidate remains above the required nonlinear norm of one. No root, accepted
step, converged trajectory or global error bound results.

## Reproduction, costs and independent assessment

Offline verification and a separate-process fresh reload/recomputation pass,
including all **7,070 arrays'** dtype, shape and bytes. These are serialization
and frozen-state numerical-recomputation evidence, not clean trajectory reproduction
or trajectory convergence. The [runnable guide](../../experiments/trajectory_reference/DIAGNOSTICS.md)
gives commands and the [wire guide](../../experiments/trajectory_reference/DIAGNOSTIC_WIRE.md)
defines raw layouts. Original failed/interrupted D-036 artifacts remain unchanged.

Measured costs: scheduler job wall 55 s and total CPU 42.546 s;
build wall 19.01 s, CPU 15.42 s and peak RSS 95,188 KiB; campaign command wall
27.60 s and CPU 10.29 s; nine native scheduler steps total about 12.90 CPU s.
These overlapping scopes are not additive wall times. Batch peak RSS is
389,416 KiB. The allocation reports two allocated CPUs; native work uses one
rank/thread. Raw archive is 48,460,949 bytes; derived JSON 266,532,727 bytes and
NPZ 57,291,640 bytes; extracted campaign totals 481,704,700 bytes. Exact-rational
report expansion exceeded the initial typical storage estimate; this is measured
cost evidence, not a new resource cap or speedup claim.

A fresh-context, read-only **gpt-6.1-sol High** reviewer independently checked
identities, every derived array, original record 300, repeatability, runtime
libraries, retry-retention fixture, all selected finite differences and directional
checks, exact fixed-b F/J/candidate arithmetic, linear backward errors and residual
decomposition. Result: **bounded PASS, no blocking finding**. The reviewer used no
compiler, producer, remote process, physical evaluation or source edits. The lead's
separate-process full report recomputation complements the reviewer's independent
raw-equation calculations; the reviewer did not duplicate that reload command.
This assessment covers D-038 artifacts, not final exact-candidate PR acceptance.

## Remaining decision

D-038 stops here. No full-horizon trajectory reference has passed; the original
five development failures, interrupted validation run and all unattempted work
remain counted in the [pause report](2026-11-20-phase2d-checkpoint.md).
A proposed higher-precision product-and-sum assembly would change the numerical
RHS and therefore needs a separately named source and explicit scientific/producer
decision. It must preserve original D-019 controls and all frozen artifacts.
Neither that change nor another trajectory run is authorized by these diagnostics.
Keep #44, the 2D goal and milestone #3 incomplete. Reference acceptance, merge and
final 2D acceptance remain human decisions; Phase 2E is excluded.
