# CRUCIBLE handoff

Updated **2026-11-23**. Phase 1, the documentation migration and **2A–2C are
complete**. The maintainer explicitly [accepted final 2C closeout](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047751430)
after all audit repairs and merged-result checks. [Milestone #3](https://github.com/jaharris87/crucible-astro/milestone/3)
remains open; [the single Phase 2 sequence](PHASE_2_LAUNCH.md) owns dependencies.
**2D is active under the maintainer’s 2026-11-20 launch / D-035.** Read-only
source/input discovery and a concrete [protocol](../experiments/trajectory_reference/PROTOCOL.md)
are prepared. Independent protocol review and focused repairs pass;
[D-036](DECISIONS.md#decision-d-036-reviewed-2d-protocol-and-producer-scope) asks
for explicit scientific/producer acceptance, now [given](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7048371383).
Implementation and synthetic verification are active; no producer work occurred
before that answer.

## Verified integrated state

The original 2C implementation was independently reviewed and merged through
[PR #48](https://github.com/jaharris87/crucible-astro/pull/48) at
**`505d5562040ec7733ec7903c7123f86921653186`**. Its merged tree equals the reviewed
tree; locked noneditable 611-test suite, CI, synthetic reload and private callable
checks passed in the [merged receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045039634).
The scheduled fresh-context read-only Sol High merged 2A–2C audit also passed,
with its original scope/limits preserved in the [audit receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7045144994).
Those passing checks did not cover every defect subsequently demonstrated.

Earlier settled receipts: [Phase 1](https://github.com/jaharris87/crucible-astro/issues/15#issuecomment-7014392482),
[migration](https://github.com/jaharris87/crucible-astro/issues/39#issuecomment-7019298012),
[2A](https://github.com/jaharris87/crucible-astro/issues/41#issuecomment-7020463315),
[2B](https://github.com/jaharris87/crucible-astro/issues/42#issuecomment-7043899683).
The [2B model card](model-cards/genesis_modelcard_full_state_mlp_v0_1.md),
[dated report](reports/2026-11-20-phase2b.md) and [guide](../experiments/mlp_baseline/README.md)
retain the frozen negative digital-fidelity baseline. Zero whole-vector attainment
and unbounded binary64 relative RMS/max are accepted results, not repair authority.

## Accepted audit reconciliation and next boundary

The maintainer requested assessment of Codex, Claude and Gemini audits of
`505d556`. The [consolidated dispositions](reports/2026-11-20-phase2c-audit-assessment.md)
preserve attribution, reproduced defects, qualified scientific claims and bounded
deferrals. Original reports/proposals/checkouts remain unchanged.

[Repair PR #49](https://github.com/jaharris87/crucible-astro/pull/49) merged at
**`eaa94463475e068c303b32f6a307f6f53ea5cc4e`** under D-034 after a fresh separate
Sol High exact-candidate review and required CI. The merged tree equals the
reviewed tree. Actual merged locked noneditable suite and Linux CI each pass
**651 tests, zero skips**. All eight synthetic attempts pass with all 80 arrays
bitwise unchanged; all 20,879 permitted callbacks, fresh reload/compare, original
scoring provenance and preservation checks pass. The [merged receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047719265)
records exact checks/limits; the [final maintainer acceptance](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047751430)
supplies the last reserved decision. No further broad 2A–2C audit is scheduled.

[Status PR #50](https://github.com/jaharris87/crucible-astro/pull/50) merged at
`75b2ec32c7983e94a73e88c6b09250a9506eb2d0`; the [final 2C receipt](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7047856713)
records closure. Startup verified current main at that SHA with a clean checkout;
no completed 2C goal was resumed. One native goal now covers active 2D only.

Under [D-035](DECISIONS.md#decision-d-035-phase-2d-launch-concrete-producer-authority-pending),
branch `codex/phase2d-trajectory-references` prepares one coherent #44 candidate.
Two fixed permitted initial states and saved T9/rho forcing were recovered and
verified through the existing loader. They define new 10 ms forced IVPs, not
hydrodynamic reproduction. All private inputs remain local. Read-only source
inspection found native coefficient lag, an incomplete full-F Jacobian and
negative-iterate projection; the proposed small native adaptation makes these
explicit. Original source, accepted data, model/scalers and evidence are unchanged.

**Execution checkpoint:** the first native build at `c28c527` succeeded in
job 61685010 (12.76 s wall, 9.83 s CPU, 91,044 KiB peak RSS). Preflight then
stopped: the LU/nonfinite negative fixtures wrote the correct native failure
statuses, but the runner incorrectly searched their console output. No physical
evaluation started. Full raw preflight evidence is retained locally; archive
SHA256 `f39ba5279ef648e62f0c4837623403901d75d8ac200b5fcfae2df738661f7f03`.
The runner-only repair has public positive/wrong-reason regression tests.

**Resumed on explicit maintainer request, 2026-11-23.** Offline diagnosis and
repository repairs were authorized; the separately accepted D-038 campaign has now completed.
The [diagnosis](reports/2026-11-23-phase2d-diagnosis.md) rechecks the full retained
population and proposes [D-038](../experiments/trajectory_reference/DIAGNOSTIC_PROTOCOL.md).
The protocol and focused implementation repair review pass at `ae69715`;
[D-038 scientific/producer acceptance](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7107405775)
was explicitly given in chat (“approved”). Exact repaired installed suite: 909 tests, zero skips; Linux CI,
Ruff lint/format, documentation and whitespace checks pass. Private preparation
003 binds that source/tree and all 92 immutable identities. Job 61864997 completed
one fresh build, eleven synthetic prerequisites and all nine diagnostic processes,
with 4,384 RHS calls and no trajectory step, repair build or restart. Earlier
unexecuted preparations remain preserved.
The prior pause remains preserved. Job 61689197 is terminal CANCELLED;
no campaign or reproduction job is left running. The [pause checkpoint](reports/2026-11-20-phase2d-checkpoint.md)
and [actual receipt](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7050616078)
record completed/failed/interrupted/unattempted work and raw identities.
Both controls passed; all five development runs failed first-step residual
convergence. Validation L0 was interrupted at 25.4 microseconds of 10 ms.
No full-horizon reference passed. Direction two is inadmissible for both initial
states at every multiplier; exhaustion snapshots need consistent state/F retention.

**D-038 result:** [the diagnostic report](reports/2026-11-23-phase2d-diagnostics.md)
records passing identity/repeatability, all twelve full-F Jacobians and all 36
prescribed directional agreement checks. Four of 81 directional samples were
explicitly refused; stable adjacent windows remain. Exact conditional arithmetic
shows material assembly cancellation, but removing that discrepancy does not
remove the dominant frozen Newton residual. All four frozen linear solves complete;
small normwise backward errors do not establish componentwise forward accuracy.
Fresh offline verification/reload passes all 7,070 derived arrays. Fresh-context
read-only Sol High artifact assessment gives bounded PASS without blockers.
Raw archive SHA256 is
`02f2c62ade306d21f8cd5c584577fc215e1df34f646114559f5f05efcc8523bd`.
Measured job wall is 55 s / total CPU 42.546 s; complete costs and artifact hashes
are in the report. No full-horizon reference has passed.

**D-039 completed:** the [distinct-source qualification report](reports/2026-11-23-phase2d-assembly.md)
records the [explicitly accepted](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7109353327)
bounded campaign. Exact physical source `245ed9525ee9877653beab80eaf91bdd5493800c`
passed independent review/focused P2D-ASM-001 repair verification before execution.
Preparation002 binds all 120 immutable identities. Job 61873636 is terminal
COMPLETED, with one build, sixteen compiled synthetic prerequisites and eleven
physical processes; two tight processes are conditionally unattempted. All identity,
arithmetic and three frozen full-F Jacobian / nine directional checks pass.
Development failed all ten first-step attempts (300 Newton iterations, final norm
4.430184552); validation accepted only 0.78125 microseconds (213 iterations),
completing neither its requested 100 microseconds nor the original 10 ms horizon.
The campaign used 177,347 physical RHS calls / 187,855 guarded requests. Raw archive
SHA256 `6b44f97052abaa407931994948819b1f99f9a073aaa72e51fc494bc0fd875580`.
No postphysical build, restart, process repeat or continuation is authorized.

Offline report verification passes after reporting-only repair `e5cfa62`: the
original failed report is preserved. All 68 actual execution-system library files
match retained compute-process identities through an explicit hash-bound read-only
receipt; retained build/executable identities are also verified locally. Scientific
criteria and executed gates are unchanged. All 1,010 public tests, lint/format and
frozen-documentation checks pass. Fresh-process reload/recomputation passes all 255 arrays; independent actual-artifact
assessment gives bounded PASS without blocking findings. The independent review
also confirms final development updates are entirely lost to binary64 rounding;
this is local stagnation, not proof that no other representable root exists.
The report records exact scope and remaining limits.

**Next authorized action:** prepare a concrete next numerical proposal from the
verified retained development failure. D-039 reporting/artifact assessment is complete.
New producer execution requires a separate reviewed protocol and explicit decision.
The [guide](../experiments/trajectory_reference/ASSEMBLY_QUALIFICATION.md) and
[wire formats](../experiments/trajectory_reference/ASSEMBLY_WIRE.md) retain original/
variant F and all failures. The distinct numerical RHS preserves D-019 and frozen
artifacts; frozen-MLP compatibility is unestablished. No full-horizon reference or
global convergence/clean trajectory reproduction exists. Reference acceptance,
merge, final 2D acceptance and Phase 2E remain separate decisions.
Original failures and the reviewed forensic retention repair remain preserved.
The stopped campaign used exact reviewed `a771930`,
submitted after [explicit D-037 acceptance](https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7050412199).
Focused independent review passes the repair, all 120 Phase 2D Python tests and
offline replay of ten native fixture results. CI also passes at that candidate.
The accepted D-036 equations,
inputs, physics, physical-run counts and numerical criteria stay fixed. Ordinary
exact-candidate code review passes with P2D-IMPL-001 resolved; physical artifact
review and reference evidence are still outstanding. The independently prepared
reproduction has identical source/tree/protocol/annex and all 94 immutable hashes;
do not submit it under this pause; new execution needs the revised decision above.
Original protocol findings and focused PASS remain in #44;
[draft PR #51](https://github.com/jaharris87/crucible-astro/pull/51) remains incomplete. This is not reference acceptance or merge approval; D-034 does not
carry into 2D. Keep #44/native goal incomplete and milestone #3 open.

Deferred compatibility/scorer/callback/loading/nonlinear verification proposals
retain their triggers in the assessment; they are not blanket prerequisites or
approved redesigns. Preserve the frozen negative baseline and sealed final test.

## Evidence and reproduction boundaries

D-033 accepted the [reviewed protocol](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044376981),
SHA256 `35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2`.
The accepted campaign executed at `f3a12a7`: six positive integrations and both
expected negative attempts passed constraints/refinement and fresh reproduction.
All 20,879 permitted frozen callbacks passed saved-batch/one-row identity and the
declared singleton/batch allowance. The [dated 2C report](reports/2026-11-20-phase2c.md),
[aggregates](../experiments/integration/results.json) and
[public synthetic artifacts](../experiments/integration/artifacts/manifest.json)
retain those original source bindings. Repair regression evidence is separate.

Private records, original model/scalers/predictions and run evidence remain local.
The model NPZ SHA256 remains
`4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793`.
An old external development checkout containing the scoring configuration was
removed after original merged checks. The current private resolver now overrides
that digest to the identical committed bytes; the original overlay and 2B access
file were preserved. See the [loading guide](science/data/LOADING.md).

The [Qiosk/original Zhang-paper trace](../experiments/integration/GROUNDING.md)
continues to ground the separation of source learning, representation and
integration. Analytic wrapper verification supplies no nuclear rollout claim.
Preserve physical ordered 160 Y, T9/rho, composition-derived Ye and signed Y/s;
no fitting, projection, real MLP integration or final-test model use.

## Scientific and execution boundary

D-025 qualifies `ccsn-primary-native-rhs-pointwise` 0.1.0: **24,314 states /
380 histories / 94 operational groups**, with **17,659 / 3,220 / 3,435**
train/validation/test states. Full ordered 160-species molar Y, recorded T9/rho,
and native Ye=Q/B define the pinned D-019 instantaneous RHS. D-024 headline
metrics and the explicitly accepted D-026 successor scorer remain distinct from
the unchanged original qualification/scorer bindings.

[The qualified card](data-cards/genesis_datacard_ccsn_native_pointwise_qualified_v0_1.md)
and [finite contract](science/benchmark/NATIVE_RHS.md) own purpose/limitations.
Qualification covers finite within-parent numerical emulation; physical application,
heating/energy and rollout accuracy remain unqualified. One parent, operational
grouping, residual correlation and component-support gaps limit inference.
Dataset redistribution rights remain unresolved. Original HDF5 quarantine masks
remain false; permitted use resolves through the separate overlay.

D-017/D-020/D-023 producer authority is exhausted. D-036 grants only the named
2D protocol/execution scope; D-037 adds only the named replacement fresh build.
No original reference modification, bulk conversion, paid service,
release or deployment is authorized. 2D requires its concrete
scientific/reference execution decision; 2E requires frozen-protocol final-test
release. No reduced modeling, model-family search or Phase 3 follows this authority.
