# Remaining-primary reference: retained execution evidence

Recorded 2026-11-19 from the completed D-023 packet under
[issue #26](https://github.com/jaharris87/crucible-astro/issues/26). The separate
[union contract](PRIMARY_RHS_DATASET.md) and
[living data card](../data-cards/genesis_datacard_ccsn_primary_native_rhs_union_v0_1.md)
record actual two-source materialization under issue #31. This is retained
numerical/provenance evidence, not fresh review approval or scientific qualification.

D-023 completed the authorized finite primary execution: exactly **19,159 fixed-state call pairs = 19,157 new states in 300 histories + two explicit repeat controls from one pilot history**. One fresh build and one Slurm job ran, without retries or source/physics changes. Existing pilot artifacts remain unchanged; the two repeat outputs are engineering controls and add no unique example. The unique pilot/new input union remains 24,314 states in 380 histories. Independent retained-evidence review and scientific acceptance remain separate.

Reviewed source `abecad208cacd022ea209f6bfa5f4b9ef5363658` remained clean and byte-identical to the seven prepared software files. All 38 immutable bundle entries rehashed successfully at closeout. Runtime used one MPI rank, one active zone/CPU/thread, unchanged full-160 Y/time/T9/rho, native composition `Ye=sum(Z*Y)/sum(A*Y)`, weak/screening enabled, heating off and `nnnu=0`. No normalization, clipping, floor, rate/source change, integration/NSE/Jacobian call, model or training occurred. The original native reaction-map conventions were retained.

The pinned Intel 2025.3 / PrgEnv-intel 8.7.0 / Cray HDF5 parallel 1.14.3.9 toolchain and flags were unchanged: `-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`, EOS preprocessing and sequential MKL. The Python-only shim selected verified Python 3.12.12; 62 focused synthetic checks passed. Build and runtime environments are recorded separately; 68 loaded shared-library file hashes are bound in the comparison and execution receipt. The selected EOS/table is a new reference dependency, not historical generating-build proof.

Slurm job **61513686** completed `0:0` on AMD EPYC 7763 hardware. It reserved two hardware CPUs and ran the reviewed `srun -n 1 -c 1` with `OMP_NUM_THREADS=1`. Whole `build.sh` elapsed **8.54 s**. Whole `run.sh` elapsed **2:49:40**, including verification, initialization, launcher, I/O, exact-rational comparison and hashing; Slurm whole-job elapsed was **2:49:44**. The evaluator step elapsed **9 s**, including initialization and I/O. These are not isolated RHS timings or speedup evidence.

All **19,159 records / 3,065,440 fresh components** passed full comparison. Every input/header/species/scalar/Y/stored echo remained bit-identical, all exported values were finite, static maps matched before/after, and appended controls **19158/19159** matched retained vectors exactly. The used 39,237,632 reaction coefficients are retained privately. Independent local stdlib decoding checked every output, JSON vector, norm, identity and control; it did not rerun the expensive exact comparator or any physics.

Every coefficient-conditioned assembly and baryon check passed its operation-derived bound. Maximum displayed matched residual/bound ratios were **0.2717762172809784** for components and **0.05888312097283753** for baryon rate. Global component residual/bound maxima were `3.191475739645422e-4 / 9.130700779024019e-2`; global baryon residual/bound maxima were `1.7978008432596615e-3 / 5.92427187611499e-1` (global maxima need not share a row/component). All 38,318 native nearest-rounding/gradual-underflow reports were true. These conditional roundoff checks are not application tolerances or rate/EOS/astrophysical-accuracy evidence.

Stored-versus-fresh absolute differences, **Y/s over all 19,159 call records, including both repeats**:

| Norm | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| L1 | 1.016596409991207e-34 | 2.34434441232527e-06 | 1339843891.6444397 |
| L2 | 4.111801460709786e-35 | 1.0206540679780746e-06 | 495094871.2348586 |
| Linf | 2.407412430484045e-35 | 7.338039846871425e-07 | 382342163.1695505 |

The completion JSON also retains separate statistics for the 19,157 new states. These differences do not establish a solver defect, energy target or accepted scientific error budget. All scientific-acceptance and training-eligibility flags remain **false**. No calls were made during resumed evidence closeout, and physical-call authority remains exhausted.

SHA256 bindings:

| Artifact | SHA256 |
| --- | --- |
| Preparation/runtime manifest | `a51f43bd5e053159457d61f45a5672e1308a6199158730f4fed269d517ff2146` |
| Fixed states | `b6c514f8101894a39c11ecfdee52fb4b70a242ba13d74adeb3e8e66fc2f53fbd` |
| Call-role selection | `8dc08d78637469efd08cf105ee6f9491ac9953c418de1ff04db48680f23af14f` |
| Canonical configuration | `aff01e92d0f08b837ee403771dc5fab7738635707d00abdc6fef234ab93db218` |
| Executable | `9205d30ca97bcb69e42eb48febb54e75f0be50d4e221de28d0a8b9575c71e381` |
| Fresh output | `5bfe797b12a702373d39f87dfbc852ee49d7f23a67681ab0eeaafb175cb3ea8d` |
| Components | `f8a788bdd0ec98c1316da8fbb2285d5533ceace0e7af1f3adc4d266fe98d8b4f` |
| Comparison | `1c4fad2c19e99693525feabd252d2333a18ef5d4e4e04547dc5331dfb3a2b61a` |
| Execution receipt | `219eb993487b9426fb07b170ca4e17b6d04448b6fd993add0899f7ddec14349c` |
| Complete private evidence archive | `33020f9af733701a15ffa091e5f1a0f56372ad11049baf8e8c8ee922ecb3cc38` |

The 833,167,360-byte final archive and every listed transfer/file hash passed. The seven-field primary execution receipt binds the five actual parents, explicit new/repeat batch roles, canonical configuration hash, library map and twelve actual local build/run/job evidence roles. Raw vectors/states, original source dependencies and private account/node/library paths remain local. No pilot-only materializer or union materialization was invoked by this execution worker.

## Review and authority boundary

All D-023 physical-call authority is exhausted. No retry, extra evaluation,
reference change, integration, NSE/Jacobian or training is authorized by this
report. The separate union materializer subsequently created one new local
quarantined artifact after verified closure; it did not execute physics or rerun
the expensive exact comparator. Original pilot and primary execution artifacts
remain immutable. Fresh source/scientific/provenance review of both actual
execution chains and the complete HDF5/working-membership proof, appropriate
findings disposition, human merge and merged integration remain gates. Rate/EOS/
astrophysical accuracy, final scientific memberships and budget allowances are
not inferred from these conditional roundoff diagnostics.
