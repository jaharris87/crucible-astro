# Three-state accepted-output RHS diagnostic — 2026-11-17

**Execution completed; scientific acceptance remains open; training eligibility is false.**
Governing [issue #14](https://github.com/jaharris87/crucible-astro/issues/14),
maintainer D-017 authorization; implementation and live review record:
[PR #16](https://github.com/jaharris87/crucible-astro/pull/16).
Author/orchestrated execution: `gpt-6.1-sol` High, no substitution.
This report publishes permitted aggregate audit metrics and fingerprints only.
Original data redistribution is not cleared; raw vectors, state values, source
snapshots, executable, full receipts and machine-specific locators remain private.

## Question and exact scope

At three preserved ordinary outputs of local audit pair B, compare stored native
abundance derivatives with fresh `cross_sect` then `yderiv` evaluations at the
emitted full-state composition and recorded conditions. Aliases D1, D2 and D3
identify the three reviewed records in issue #14, in that order. Their exact
ordinals and lossless raw-record association are bound by the reviewed helper,
input stream and private manifest. No record selection changed during execution.

Exactly three reference RHS evaluations completed. No integration, trajectory
rerun, NSE solve, Jacobian solve, training, bulk label regeneration or energy
comparison occurred. Original references and raw inputs remained unchanged.
The harness, Python helper, build/run scripts, fingerprint bindings and synthetic
tests remain byte-identical to executed source
`7ea920b2b994c9962a98e600b7af0321d52c70b3`, base
`099d21ead2056d5abcac97295d2a5f3d2d83b270`. Only documentation follows that source
candidate. The [fresh independent source gate](https://github.com/jaharris87/crucible-astro/pull/16#issuecomment-6962405691)
passed before compilation or reference execution.

## Inputs, reference and physical settings

[bindings.json](bindings.json) binds the individual modified producer modules,
selected EOS/include, network/rate/weak inputs, EOS table, original binary,
companion output and control by SHA-256. The nested producer HEAD alone does not
identify its modified source. The reviewed private manifest additionally binds
the selected lossless state stream and all copied files. No preserved object or
module files entered the fresh build.

The maintainer explicitly selected upstream XNet Starkiller Helmholtz EOS source
for a **new diagnostic reference**. This selection does not recover the historical
generating EOS/build. It is a confounding factor when attributing stored-versus-
fresh differences solely to the known Newton-iterate/state alignment issue.
Historical generating source, executable, compiler and EOS association remain
unresolved; this experiment does not establish a solver defect or its cause.

The executed harness preserved composition bits, recorded time/temperature/density,
weak=1, screening=1, self-heating=0, neutrino-control=1 and the source temperature
switch. EOS Ye came from the supplied composition. Runtime assertions confirmed
160 species, 176 FFN entries, zero NNU entries, reaction counts
(683, 1345, 16, 4), and no neutrino reaction flags 7–10. Neutrino absence was a
property of the bound candidate tables, not a physics switch made to permit a run.
No flooring, clipping, normalization or history-Ye substitution was applied.

## Two attempts and runtime disposition

Attempt 01 stopped in prebuild verification: system Python 3.6.15 rejected the
helper's `argparse.add_subparsers(required=True)`. It produced no compiler
invocation, reference executable, RHS/NSE call or scheduled job. The original
failure and bundle were retained without overwrite. The
[lead's recorded disposition](https://github.com/jaharris87/crucible-astro/pull/16#issuecomment-6962519036)
permitted an explicitly verified helper runtime while preserving reviewed source,
compiler, precision, EOS, network and physics.

Attempt 02 used Python 3.12.12 through a private PATH shim containing only a
`python3` link. The interpreter checksum was recorded, the exact bundle verified,
and all ten synthetic helper tests passed there under pytest 9.0.2 before the
compiler started. Before/after shim checks established unchanged login compiler
wrapper/compiler selection, loaded modules and library search environment.
This does not extend the project's supported Python versions; original locked
package checks used Python 3.12.9.

The new reference build used the reviewed scripts without flag changes:
Intel ifx 2025.3.0 through the Cray `ftn`/`h5pfc` wrapper, CPU environment,
PrgEnv-intel 8.7.0, Cray PE 2.7.36, Cray MPICH 9.1.0, parallel HDF5 1.14.3.9 and
MKL 2025.3 sequential. Recorded flags include `-g -O0 -traceback`,
`-qopenmp-stubs`, default real64/int32, and explicit EOS preprocessing. The
runtime precision, endian and one-rank assertions passed.

Build and computation environments were recorded separately. The compute job's
library search path included an additional system fabric entry relative to the
login build; they are **not asserted byte-identical**. Actual loaded-library maps
and hashes of 68 runtime shared-library files are retained with the comparison.
The public report omits all library paths. No code or compiler/physics fallback
was introduced after the source gate.

## Aggregate results

Let the 160-component difference be `fresh RHS − stored RHS`. Norms below are
unweighted native abundance-rate errors, in **Y/s**, over all 160 species for
each of these three records only: L1 is the sum of absolute component differences,
L2 is their Euclidean norm, and L∞ is their largest absolute value. They are
measured differences, not accepted error tolerances, pass/fail thresholds or
dataset-level estimates.

| Record alias | Absolute L1 (Y/s) | L2 (Y/s) | L∞ (Y/s) |
| --- | ---: | ---: | ---: |
| D1 | 19.786469368975013 | 7.258277910783365 | 5.387828808683142 |
| D2 | 4.553900767776886 | 1.5802250761083507 | 1.2454643864925856 |
| D3 | 1.1404954020065967e-25 | 5.690145440569352e-26 | 3.141086352409025e-26 |

All supplied state/condition bits matched their before/after echoes, all stored
and fresh derivative components were finite, and all 160 component differences
per record were retained. A separate author stdlib decoding of the binary output
recomputed all 480 signed differences and all table entries, matching the helper
report. Baryon and charge-rate diagnostics are retained privately; no numerical
acceptance threshold or fixed-charge constraint was imposed. Author recomputation
is not a substitute for the independent evidence/report review tracked in PR #16.

D1 and D2 show disagreement with this selected new reference at the two hot
states. The comparison does not separate Newton-iterate alignment, reference/EOS
association and floating-point cancellation contributions. No acceptable learning
error budget has been chosen, and these three records do not characterize the
whole run.

D3 is below the FFN table's first electron-density coordinate. The unchanged
`ffn_rate` selects and extrapolates its first interval
(`xnet_ffn.f90:97–108`, fingerprint in bindings). That extrapolation's scientific
accuracy is unqualified. D3's small stored-versus-fresh difference does not validate
the extrapolation, the reference or the dataset.

## Actual execution resources and timing boundaries

A single CPU shared job completed with exit `0:0` on AMD EPYC 7763 hardware,
one MPI rank, `OMP_NUM_THREADS=1`, and MKL sequential. Its scheduler placement
requested two Slurm CPUs (one physical core), 1 GiB and five minutes; these are
this experiment's placement details, not standing project resource caps. Private
receipts retain account, job, node and allocation details.

| Measured boundary | Elapsed | Maximum RSS |
| --- | ---: | ---: |
| Whole fresh `build.sh` via GNU time | 8.45 s | 81,920 KiB |
| Whole `run.sh` via GNU time | 7.36 s | 111,100 KiB |
| Scheduler batch | 10 s | Not inferred from scheduler's zero RSS field |
| Scheduler MPI step | 1 s | Not inferred from scheduler's zero RSS field |

The GNU-time boundaries include wrapper verification and associated setup/work;
`run.sh` additionally includes launcher, reference initialization, I/O, comparison
and library hashing. The scheduler MPI step also includes process/initialization
work. None is an isolated RHS-call latency or a speedup/cost-baseline measurement.
No runtime failure occurred in attempt 02, and execution stopped after the three
comparisons.

## Portable fixity record

All entries below are SHA-256. These identify retained private artifacts; they do
not distribute the artifacts or establish historical generating provenance.
Individual input/source fingerprints are in the unchanged public bindings file.

```text
public bindings.json
001234a9aabff8fe40188f4da0a5fb307e2456c384f10a5c3301a684ac618fd6
reviewed input/source bundle archive
2cb053a39a6f308f4a60f29be7d610cdf912bd960e47e1cc3dfe1abf2bd5627f
private manifest
731fcde474e462770cdca008b4b3301a3ec499b853fc59d19f513f3f6e5d71a2
lossless three-state input stream
ed28dcc5b01909616a6f6546cc20ff87361a02c619bb1db4769b09faf2b21d01
new reference executable
9aafda656e49c095cf445422df3039092e388f11bafc21344378830140e6832f
fresh binary output
87f63faca1b3ab1ece0a1459ee932e4c6ef7779132ce54535e42bb268a1424be
all-component comparison report
4e8ada0faad55eee7975b7deb6d675483b7ff7528e1543ccefdffab333526ed6
runtime loaded-library maps
5bab1f42d3a2a82baa86262635d8eeaf5c262c59d68aec0e9d8106ec80d31f4e
attempt 02 execution evidence archive
964a639b1b7609504f85ec02895448647830d624a011e8d42530c316037a2e2c
attempt 01 failure evidence archive
ae4e1e561220650e2a96e397a2eb0a9ac483b5f3325832711c52a42c8f6dfa20
Python 3.12.12 interpreter
16949501ae4b1185beacd6fb9df5867c27d1bf72ee6c1bfd46b0189f2a96b02d
h5pfc wrapper
53f0766e233f32add26d151043f05665cb20016489e7695122d289062e5761d6
ftn wrapper
59dcb81e235e1c34522071ca42afe945007ca1b5507e728680d85c2ee7b21d01
ifx compiler
e4df8fb0bcbbb8f71cc37b5f2d0ccfdc8d7a9ca3c98457137c8e71152122e540
```

Build and run logs, timing, helper/runtime proofs, full loaded-library hashes,
original-state associations and author binary-check script remain with those
private receipts. Author preparation checks at the executed source recorded
96 passing locked/noneditable Python tests, including ten synthetic diagnostic
controls; the independent source gate is separately linked above. These are
software evidence. Subsequent independent
execution-evidence/report review, CI, a concrete human merge decision and merged
integration receipts belong to the live PR/issue. This report does not close the
issue or request readiness/merge automatically.

**All training eligibility remains false.** This bounded diagnostic qualifies
neither original state/RHS/energy/rollout labels nor a benchmark, split, transform
or scientific model. Further reference execution, label recomputation or training
requires its own authorized scope and applicable scientific decisions.
