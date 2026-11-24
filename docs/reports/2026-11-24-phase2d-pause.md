# Phase 2D — requested pause after first full L0 trajectory

**2026-11-24: paused on the maintainer's explicit request.** Job **61935889**
is terminal CANCELLED, with no continuing producer job. This is a human pause,
not a numerical failure or an infrastructure restart. No converged/reproduced
reference set or final 2D acceptance is claimed.

## Actual completed and interrupted work

Physical source is independently reviewed **`dd07cc1194ffe4771e900678f1de636152876bfd`**,
tree `38f0c4c96e12a68281d36cbb9eea5de11c61a259`; executable SHA256
`1ed8b5be53aa00711aa8a997590b3ee03b3c77a49ae223be588878a56b47ad65`.
The [D-040 protocol](../../experiments/trajectory_reference/CORRECTION_PROTOCOL.md)
and all original inputs/physics remain unchanged. Preparation002 SHA256 is
`38e94025679e191c205c5500fa6aa111e30a6c7b64c15fa21febbddd48b62912`.

| Work | Actual outcome |
| --- | --- |
| First planned Build A | Succeeded; no replacement build used |
| Compiled prerequisites | All 24 pass, including correction/wire/failure-buffer and precision fixtures |
| Development and validation initial controls | Both pass original/variant identity and arithmetic checks |
| Development L0 standard | Native SUCCESS / exit 0; 10 ms complete, 116 accepted records including the initial state; host per-run checks pass |
| Validation L0 standard | Interrupted by requested cancellation at retained time **0.0008089892900679394 s**, 15 complete accepted records including initial; no final native counters or successful terminal status |
| Other Build A work | Both L0 tight runs, L1/L2/L3 standard and L3 tight runs, and all six frozen-state diagnostics unattempted: sixteen processes |
| Build B | Not prepared/submitted/executed; its fresh build and twenty processes remain unattempted |

The first complete development curve is a per-run result, **not a converged
trajectory reference**. The joint pilot, four-level refinement, tight-control
comparison, full derivative checks, clean reproduction and human reference
acceptance are still missing. Historical saved abundances remain context only.

Development completed **115 accepted steps / 596 Newton iterations**, zero native
step retries and zero projection. It used **206,259 physical RHS calls /
220,009 guarded requests**. Each initial control used one physical call/request.
Validation's last flushed checkpoint reports **27,503 physical RHS calls**,
80 Newton iterations and fourteen accepted steps. This is a lower bound for that
interrupted process: the unflushed in-flight interval is unknown, not zero.
The original campaign/attempt manifests retain their interrupted STARTING/RUNNING
state; they have not been rewritten to manufacture orderly completion.

The actual first development step independently passes the new binary decoder
and raw-correction algebra checks: six iterations at 100 microseconds, final
current/previous normalized corrections about 0.0092154 / 0.0560755. Its raw
residual norm is about 1866.3, retained as a diagnostic under the explicitly
accepted new stopping policy. This local check proves no global accuracy.

## Preservation, costs and next boundary

The full raw source/build/input/output/job directory is preserved remotely and
copied locally, unchanged, in a private archive. SHA256
**`845185dc506a1a8f72e3b003d7713d43b7fac6772c80acf0dc86181cc6c19645`**;
size **94,046,976 bytes**. It includes scheduler receipts and a successful
quiescent read-only identity recheck of all **68** actual execution-system library
files. Private paths/arrays stay in the ignored locator. Original reference
projects, pointwise qualification, model/scalers and historical failures remain
unchanged. A full derived report/reload and independent actual-artifact assessment
have not yet been performed for this paused campaign.

Measured build: 10.48 s wall, 9.86 s CPU, peak RSS 95,156 KiB. Scheduler job
elapsed is 8 min 43 s (cleanup through 8 min 52 s), reported total CPU 8 min
33.799 s. Development native step process completed in 7 min 3 s wall / 7 min
1.876 s CPU, peak RSS 147,652 KiB. These scopes differ; they are not additive
cost caps or a speedup claim. Validation's Slurm step is FAILED after cancellation,
which does not establish a numerical failure before the human stop.

Resume with read-only checkpoint verification and an explicit bounded resumption
decision covering the human-interrupted validation process and remaining work.
Do not label this pause an infrastructure fault or invoke the infrastructure-only
restart allowance for it. Do not silently repeat completed controls/development
work, change source/equations/forcing/tolerances, or submit Build B. Preserve the
frozen source and every completed/partial artifact. Reference/merge/final acceptance
and Phase 2E remain separate. Keep #44 and milestone #3 open; the 2D objective is
incomplete and its native goal is paused on request.
