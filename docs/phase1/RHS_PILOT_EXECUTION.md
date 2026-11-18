# Native pointwise RHS pilot: retained execution evidence

D-020's exact pilot under [issue #18](https://github.com/jaharris87/crucible-astro/issues/18)
completed on **2026-11-18 UTC**: one fresh build and one Slurm job, exactly 5,157
fixed-state `cross_sect`/`yderiv` pairs across 80 histories, all 160 components
retained. Its physical-call authority is exhausted. No retry, source/physics
change, additional reference evaluation, integration/NSE/Jacobian call or training
occurred. The completed numerical checks below are retained facts; independent
final evidence review and human scientific acceptance remain separate gates.
The [new derived card](../data-cards/genesis_datacard_ccsn_native_rhs_pilot_v0_1.md)
and [materialization contract](RHS_DATASET.md) describe the actual quarantined
HDF5 candidate under [issue #23 / PR #25](https://github.com/jaharris87/crucible-astro/pull/25).
Every scientific-use mask remains false. This report changes no benchmark role.

## Declared generating reference and actual execution

Reviewed source `00cf10b75d27b300e1650931029e657949e77ec4`, integrated through
PR #20, remained clean and byte-identical after execution; the preparation bundle
and its six runtime files were rechecked unchanged. D-019's newly declared native
reference uses unchanged full Y and recorded time/T9/rho, with native EOS
`Ye=sum(Z*Y)/sum(A*Y)`. It does not establish the historical generating build.

The retained configuration uses one MPI rank, one active zone and thread;
`iweak0=1`, `iscrn=1`, `iheat=0`, `ineutrino=1`, `nnnu=0`; 160 species, 176 FFN
entries and reaction counts `(683,1345,16,4)`. The strong-rate switch remains
`t9min=0.01`. No normalization, clipping, floors or fixed Ye were introduced.
The native reaction-map convention is preserved; reconstructing upstream rate
history is not a new prerequisite (see [reference scope](RHS_REFERENCE_SCOPE.md)).

Actual build/run records retain Intel 2025.3, PrgEnv-intel 8.7.0 and Cray parallel
HDF5 1.14.3.9, flags `-g -O0 -traceback -qopenmp-stubs -real-size 64 -integer-size 32`,
EOS preprocessing and sequential MKL. A Python-only shim selected Python 3.12.12;
tool identities were checked before build/run and all 30 remote synthetic helper
checks passed. Build and computation environments were retained separately,
including **68 mapped shared-library file identities**. The selected EOS/table
is a new reference dependency, not historical-build evidence.

Slurm job `61509220` completed `0:0` on AMD EPYC 7763 hardware. It reserved two
hardware CPUs and ran the reviewed `srun -n 1 -c 1` with `OMP_NUM_THREADS=1`.
The final job, batch, extern and evaluator-step accounting rows all report
`COMPLETED`, `0:0`. Scheduler timestamps are retained in their recorded timezone;
the run's UTC end record is 03:33:07 on 2026-11-18.

| Measurement | Actual scope / value |
| --- | --- |
| Whole `build.sh` elapsed | 7.53 s; wrapper includes verification/build/linking |
| Whole `run.sh` elapsed | 45:50.56; verification, initialization, launcher, I/O, exact-rational comparison and hashing |
| Scheduler whole-job elapsed | 45:53, two allocated CPUs |
| Evaluator scheduler step | 4 s; includes initialization, launcher and I/O, not isolated RHS timing |
| Run wrapper maximum resident set | 172,388 KiB; not an isolated kernel memory measurement |

These measurements support reproducibility; they are not an inference benchmark
or speedup claim. No standalone RHS timing or scientific application accuracy
was measured.

## Completed numerical and independent decoding checks

All 5,157 state/header/species/scalar/Y/stored echoes were bit-identical and all
exported values finite. Runtime maps before/after matched the expected maps.
The two retained D-017 controls, sequences **58 and 62**, matched exact bits.
All **825,120 components** and **10,561,536 exported coefficients** were retained.
Independent local standard-library decoding checked all rows/components, JSON
round trips and every stored-versus-fresh norm. All 5,157 coefficient-conditioned
assembly and baryon checks passed their operation-derived bounds.

| Displayed roundoff diagnostic | Maximum |
| --- | ---: |
| Component residual / its derived bound | 0.2627320069044581 |
| Baryon residual / its derived bound | 0.05002814538309847 |
| Global component absolute residual | 2.2662145392705757e-4 |
| Global component absolute bound | 9.403371369370196e-2 |
| Global baryon absolute residual | 1.8284060620037178e-3 |
| Global baryon absolute bound | 6.119800890087225e-1 |

Global residual and bound maxima need not belong to the same row/component;
they must not be divided to infer a worst-case ratio. Displayed ratios summarize
already successful exact-rational checks and are not scientific tolerances.

Stored-versus-fresh absolute differences (`molar_abundance_Y/s`):

| Norm | Minimum | Median | Maximum |
| --- | ---: | ---: | ---: |
| L1 | 4.230293426120926e-30 | 4.0747653141210044e-7 | 1.2166848165595555e9 |
| L2 | 2.3715113803862624e-30 | 1.700409739837683e-7 | 4.5149936677027124e8 |
| Linf | 1.627025617018337e-30 | 1.2088968559531565e-7 | 3.4904818411571294e8 |

These differences do not establish a solver defect, energy target or application
tolerance. The proof verifies assembly from exported native coefficients; it
does not establish rate, EOS or astrophysical accuracy. All recorded scientific
acceptance and training eligibility remain false. The finite pilot remains
separate from the expanding primary benchmark audit.

## Retained identity and materialization evidence

| Artifact | SHA-256 |
| --- | --- |
| Preparation/runtime manifest | `10cf0d3250c83ff9c57c65adeb6ce4f323d7c9efadebf97f5b87013dd2f386e6` |
| Fixed states | `aa0d6fe52420183601e8c3301b19e497058397621eb66c64a2c4ffc6c6dc290f` |
| Configuration, canonical JSON | `0302d02d7c136ef63fdba1d515dffc2c58b7353bff4c53562ad1b53142524873` |
| Executable | `6dfcbbb4b4eb4ae14446b3a17303045c99b71b810d5d4c53e8fd7d841c8627bc` |
| Fresh output | `cbb9b6c90e5d3cd7e5cf1e14134c543aedb1acd83970c17dc2e894924fc681a2` |
| Complete components JSONL | `c8d90f35b7298d3117b27b2e8ae29c28c3146756872f835fe1ac253f4a4096de` |
| Complete comparison | `e21a5aa979fb633fdb400f8ee61800cd8b9880d7e437827a47e90a8eedd1858b` |
| Finite actual execution receipt | `84c21a6f3d19331b99a3442d4be094136c337f0931e75249ec359b43086f1e47` |
| Complete private execution archive | `ab9b5d07881d00c5fa9770edf3d405a813a58844b980be65365c48df697d7f0a` |

All 39 final transferred files matched transfer hashes; the retained local
inventory binds 230 files. The finite execution receipt links the five output/
preparation parents, canonical configuration and library identities to actual
build manifest/log/exit/driver/runtime proof, run log, job script/final scheduler
status/hardware/environment/exit and loaded-map record. Every one of those twelve
local evidence files was rehashed during materialization and independent HDF5
verification. Private paths, account/node/library locations, raw vectors,
actual states and original reference sources remain local.

The first materialization attempt refused before creating output because its
locator formatter omitted the leading zero of a raw four-digit tracer filename
(**RHS-DATA-R3**). The refusal, unchanged recipe and a literal public regression's
red→green results are retained. A one-line formatter repair preserves original
locators; the subsequent engineering attempt produced **one** HDF5 candidate.
No producer call or comparator repeat occurred. Independent interpretation of
every output field matches its retained parent bytes/identities, including all
19 histories with leading-zero tracer IDs, and confirms zero positive masks.
Actual derived output/manifest/recipe identities are on the separate living card.
Fresh focused review must cover R1/R2 provenance repairs, R3 and retained
execution/materialization evidence. Human acceptance, merge and integration
remain required; this report is not a review approval or dataset release.
