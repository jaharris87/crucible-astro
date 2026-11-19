# Validation and experiment qualification

D-025 qualifies the exact [finite native pointwise benchmark](phase1/NATIVE_BENCHMARK.md) and its separate [qualified view](phase1/PHASE1_CLOSEOUT.md). The requirements below govern later work as it becomes applicable. No learned model, physical application accuracy, energy or rollout accuracy has been demonstrated. Acceptance thresholds are set **before** examining final test outcomes and approved by the maintainer for the named purpose. Unknown thresholds block that scientific acceptance claim, not honest reporting of exploratory failures.

## Five separate evidence categories

| Category | Question | Required evidence |
| --- | --- | --- |
| Software correctness | Does the program implement the independently specified behavior? | Focused positive/negative tests, contract checks, deterministic fixtures, relevant regression tests; demonstrate failure for the intended defect |
| Numerical agreement | Does it reproduce a stated mathematical/reference calculation within justified error? | Independent analytic/reference values, precision, tolerances, solver convergence/refinement studies and per-field differences |
| Scientific validity | Is the task, reference, regime, observable, and interpretation physically appropriate? | Network/input review, coverage and held-out trajectories, applicable constraints, uncertainty/limitations and human scientific acceptance |
| Provenance | Can every claim be bound to the actual inputs, generator, artifacts, and code? | Checksums, patches/build identity, manifests, commands, immutable run records and audit trail |
| Performance | Is useful accuracy obtained at lower measured cost? | Matched task/accuracy, hardware, precision, timing boundaries, repetitions, failures, preprocessing and integration overhead |

A passing parser test proves no physics. Agreement with XNet measures fidelity to that declared reference, not nature. Source inspection cannot prove which binary generated a run. Low training loss and excellent reconstruction do not establish RHS accuracy, closure, stable rollout, or speed [C1–C3, P3–P5, W1 in EVIDENCE].

## Phase 1 qualification protocol

1. Inventory the smallest useful real subset without reading all bulk data. Identify authoritative species metadata, network inputs, raw layouts, compiler widths/endianness and Fortran record markers; validate record lengths, optional flux blocks and every field. The HDF-named writer includes binary output; its `edot` write differs from the other writer, so do not hard-code a guessed scalar layout [N2].
2. Bind source plus dirty patches, executable, configuration, input trajectory and output files. Existing binary-copy identity is useful but insufficient [N4]. If association cannot be recovered, classify data as exploratory and plan a separately authorized small regeneration after preserving originals. No guessed training semantics.
3. Trace initialization, solver acceptance, output cadence, NSE transitions and interpolation. In the inspected BE source, `ydot` precedes the final correction to the emitted state; both Newton iterates represent the new implicit time. This is not an old-time explicit derivative or evidence of a solver defect. Initial output precedes the initial RHS evaluation [N1]. In future bounded producer checks, reevaluate the reference RHS at audited accepted states and quantify mismatch against solver tolerance and the intended learning-error budget. Distinguish state error from RHS error near stiffness/cancellation. Do not repair original data in place.
4. Mask unknown/initial/NSE derivative records. A zero can be a genuine RHS or a placeholder: classify by producer state and reliable flags/alignment, never value alone. If the necessary flags cannot be recovered, quarantine the ambiguous records. State/reconstruction eligibility is separate from RHS eligibility.
5. Audit finite-step alternatives independently. `(y-yo)/tdel` in the patcher describes one internal step, not necessarily the interval between saved records (routine output is every 20 steps). A saved-endpoint difference needs its own interval and condition-history definition. Neither is an instantaneous RHS [N3].
6. Establish energy semantics. The inspected evolution routine computes `edot = -(enm-enold)/tdel`, a signed internal-step average nuclear mass-energy rate, while NSE writes zero; verify sign/units/loss terms and alignment before treating it as instantaneous or deposited heating [N5]. Compare compatible observables, including integrated energy where required.
7. Produce a human-reviewed data audit with usable, quarantined and missing coverage, exact limitations, reproducible extraction recipe and a tiny approved fixture. Failure to establish labels blocks real-data training; it does not block synthetic development.

## Independent synthetic and fixture checks

Use test-first development when an oracle is specified independently: parser fields and failures, species mappings, transforms and Jacobians, validity masks, split membership, serialization and callable contracts. Avoid tests that merely repeat implementation logic.

- An analytic two-state interconversion with equal conserved weights and nonnegative solutions checks signed RHS, integration, and conservation; label it mathematical, not a real nuclear channel. A stiff linear system with known matrix-exponential solution checks solver behavior and step sensitivity. Neither qualifies an astrophysical regime.
- Explicit reordered-species sentinels test rejection of a same-shape, same-set permutation; do not trust matching array sizes. Tests cover duplicate/missing identities and a valid control so rejection is for the intended reason.
- Affine and smooth nonlinear transforms check inverse behavior and derivatives using analytic derivatives plus a finite-difference convergence sweep. A single arbitrary finite-difference epsilon is not a sufficient oracle. Cover constant features, floors, clipping, omitted species and condition dependence as supported.
- A train-only preprocessing probe changes held-out extrema while leaving training fixed: fitted parameters must remain unchanged. An overlap probe puts related trajectories from the same parent on both sides and must fail the split audit.
- Tiny real fixtures bind raw records, extraction, expected independent interpretation and human audit. Keep separate validity masks for state, RHS and energy. Unverified records can be negative fixtures but cannot become positive physical truth.
- Serialization tests assert identity/schema checks and physical predictions after reload. Inference rejects incompatible species/unit/schema/artifact combinations and returns explicit failure/domain status.

## Benchmark definition and partitions

Before fitting, freeze the scientific task: intended use, network/rate/EOS/weak inputs, state and conditions, regime bounds, initial compositions, horizon/output grid, RHS versus step target, energy definition, references, observables, metric aggregation, tolerances, and experiment/search protocol. Each numerical tolerance gets a reason: analytic error bounds, reference refinement, floating-point propagation, application need or measured reference uncertainty. The maintainer signs the definition; it is not inferred from a chemical score.

Use independent parent simulation/case groups for primary holdout; related tracers, trajectory variants, repeated seeds of one physical case, neighboring samples and derived copies remain in one group unless a different estimand is explicitly justified. Stratify coverage by physical regimes only without breaking groups. Separate in-domain held-out cases from regime extrapolation challenges. If only one parent simulation is available, label results within-simulation exploration; do not claim simulation-level generalization. Three example trajectory IDs do not establish representative coverage.

Training fits all scalers, bases and encoders. Validation chooses hyperparameters and checkpoints using a recorded search procedure; retain actual trials and resource use. The locked test partition is used for final comparison; if its outcomes guide redesign, disclose that reuse and establish a new confirmatory partition. Preserve split manifests and ordered sample IDs across stages. Never recreate membership from an unsorted file glob or match shuffled predictions to external row order [C3].

## Evaluation ladder

| Level | Measurements and required diagnostics |
| --- | --- |
| Representation | Physical-space reconstruction by species and regime; absolute and floored relative/log errors; conservation/positivity; worst trajectories; dimension/cost. Identity has exact reconstruction by definition, not a scientific accuracy advantage. |
| RHS or step | Separate coordinate-space optimization losses from physical-unit target errors; signed vector/component bias and tails; masks; weighting/floors; energy error when available. Report target kind and interval. |
| Rollout | Held-out initial states and histories; repeated evolution to full declared horizon; abundance histories, final yields and relevant grouped observables; energy rate and integrated energy; freeze-out/transition failures; solver success, rejections, stiffness-related cost and domain exits. |
| Constraints | For a closed complete nuclear inventory, check baryon normalization and derivative residuals consistent with its convention. Check positivity with explicit numerical tolerance, not hidden clipping. Track Ye against the appropriate weak/neutrino evolution rather than imposing constant charge; open/truncated networks need their own balance accounting. |
| Robustness | Time-step/tolerance sensitivity, controlled perturbations, train/validation/test regime coverage, out-of-domain behavior, seed variability where training is stochastic; report worst cases as well as aggregates. |
| Performance | Inference latency and throughput plus full integration wall time at matched scientific accuracy and outputs; evaluation count, memory, preprocessing/encoding/decoding, transfers and solver overhead, warmup, batch size, precision, hardware/software, repetitions and spread. Count failed runs/fallbacks. Training cost reported separately. |

Use physical units and specify abundance floors rather than hiding rare-species error in a single normalized RMSE. Include median/tails/max and denominators; a method that fails on a trajectory cannot remove it from accuracy/cost summaries without a visible failure count. Report both successful-case errors and coverage/failure fraction. A reduced method with lower inference cost but more rejected solver steps may be slower overall. Reference and surrogate must use the same conditioning histories and comparison times; interpolation error belongs in the budget.

For energy, compare a recovered physical readout and any learned readout against an independent compatible reference when selected. Mass-weighted RHS can represent nuclear release under declared conventions, but neutrino losses, thermalization and EOS effects distinguish deposited heat [P3]. Do not require an auxiliary neural head as the only solution. If energy cannot yet be qualified, mark that milestone evidence incomplete.

## Provisional pointwise abundance budgets and later acceptance

D-022 authorizes the bounded [physical-abundance diagnostic](phase1/ERROR_BUDGETS.md)
and [current readiness report](phase1/ERROR_BUDGET_READINESS.md), not scientific
numerical thresholds. The 0.1%, 1%, 5% relative-change tiers are sensitivity
settings. Freeze justified physical allowances/timescales, reference interval and
sampled-scale definitions, critical species, group observables and denominators
before final testing; no held-out adaptation or hidden clipping floors.
Report every constituent's physical/normalized errors and failed attempts, even
when linear group errors cancel. Unresolved choices and absent predictions do not
pass. Preserve numerical implementation evidence, provisional pointwise budget
satisfaction and integrated scientific accuracy as three separate outcomes.

Later authorized model acceptance separately needs admissible-state/constraint
and positivity evidence, appropriate weak Ye and energy closure, reconstruction
versus decoded chain-rule consistency (including conditioning derivatives),
closure/history tests, free-running held-out trajectories and equilibrium
behavior. Solver/tolerance and Jacobian/JVP numerical consistency and total cost
at matched accuracy need their own experiments. A soft constraint loss or an
output projection proves none of these by itself; no blanket negative-eigenvalue
rule or reduction architecture is adopted. Heating remains excluded/unevaluated
under Phase 1's `iheat=0` reference. Current native no-aux Q/B diagnostics cannot
silently stand in for unsupported open/auxiliary-reservoir balances.

## D-024 native digital-fidelity benchmark

The maintainer separately accepted fixed exact-label relative profiles for the
finite D-019 numerical-emulation purpose, recorded in D-024 and
[the native benchmark](phase1/NATIVE_BENCHMARK.md). Direct `1/1000`, `1/100`, `1/20`
profiles use all ordered species and separate zero/nonzero populations without a
floor or conditional-assembly envelope. Exact binary-rational decisions avoid
subnormal/threshold rounding; physical errors, failed attempts/finite violations,
record attainment and declared history/group weighting remain visible.
These accepted research objectives neither fill D-022's unresolved physical-change
budget nor establish application/integrated accuracy or nuclear/EOS uncertainty.
D-025 subsequently accepts the exact named reference/subset/final partitions for
this finite purpose. Its separate accepted overlay supplies positive state/RHS
eligibility; the original HDF5 quarantine masks remain false. The original pending
packet still fails the scientific gate; the accepted overlay passes it against
the original complete mechanical inputs. Physical/solver/cost gates for wider uses
remain. Neither decision authorizes model development, training or new execution.

## Fast CI versus scientific qualification

Recommend fast CI on synthetic/tiny audited fixtures, clean package import, formatting/static checks selected in bootstrap, manifest/split checks, deterministic transform/serialization/inference tests and one analytic integration smoke test when implemented. D-013 removes repository job-time and resource caps. Completed Phase 0B covered repository/workflow and synthetic validation. [Phase 1 authority](PHASE_1_AUTHORITY.md) now permits bounded qualification/ingestion/benchmark work, with its scientific gates; model development/training still requires a later authorized phase. Failures stay visible.

Larger scientific qualification is manually authorized and artifact-backed: real held-out rollouts, solver refinement, seed repetitions, cost measurements and cross-platform runs. Each issue must state the authorized experiment, evidence to retain and stop-on-nonfinite/divergence/no-improvement rules. D-013 removes mandatory numeric resource caps and accounting, while actual hardware, configuration, runtime and cost remain reproducibility evidence. Work outside the authorized experiment requires a new decision before launch. A scientific gate cannot be bypassed merely because fast CI is green; documentation-only work does not inherit every scientific run.

## Method comparison gate

The maintainer selected the identity/full-state instantaneous-RHS starting path, contingent on qualified labels, with finite-step prediction retained for later exploration (D-003). A fixed linear reduced model with a simple learned RHS remains a diagnostic recommendation; select reduced model families after data/closure evidence. Candidates include nonlinear latent dynamics, operator inference/nonintrusive ROM, or physics-guided grouping where equilibrium assumptions hold [P1, P4]. A PCA reconstruction-only result is not a dynamics comparison. Freeze common data, tests, task and reporting; permit method-appropriate tuning with disclosed search procedures and resource use. Compare matched effort where useful and include accuracy-cost curves when necessary. Record negative results and the reason for down-selection. CCSN-only evidence cannot satisfy NS3's r-process scope [P1].

## Named Phase 1 qualification under D-025

D-025 accepts the exact finite native-emulation reference/data/partitions and
D-024 digital-fidelity objectives. [The exit record](phase1/PHASE1_CLOSEOUT.md)
and qualified card bind the actual separate overlay and complete original-input
scientific checks. The preserved all-false payload remains immutable. Earlier
preparation-time pending statuses are superseded only for this named purpose;
physical application/energy/rollout accuracy and D-022 allowances remain separate.
Final exact-candidate independent review, human merge and merged checks are
required in the live final receipt before Phase 1 closes.
