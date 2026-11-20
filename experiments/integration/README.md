# Phase 2C mathematical integration verification

`crucible.integration` keeps one ordered state source separate from numerical
integration. This is the identity-state specialization of CRUCIBLE's planned
nuclear workflow: the source returns signed coordinate rates, while the wrapper
owns time stepping and diagnostics. The accepted 2C campaign integrates only
mathematical fixtures. The frozen nuclear MLP is checked pointwise separately;
this code does not load it or establish nuclear rollout validity.

The governing protocol is the exact accepted issue #43 proposal
([proposal](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044234697),
[review](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044293163),
[acceptance](https://github.com/jaharris87/crucible-astro/issues/43#issuecomment-7044376981)),
SHA256 `35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2`.
Its preserved local file is the authority input; this guide is not a replacement.

## Checked callable

`RHSContract` declares exact ordered component names, state/rate/time units and
condition names/units. `integrate_rhs(rhs, y0, times, contract=...,
expected_contract=..., rtol=..., atol=...)` compares both contracts and consumes
the declared dimension. Inputs and callback results must be finite binary64
NumPy vectors, with strictly increasing binary64 times in seconds. The source
receives a read-only owned state copy. There is no coordinate transform,
normalization, clipping, permutation, fallback or supplied Jacobian interface.
The adapter/caller remains responsible for declaring and validating its actual
external condition function; the wrapper verifies the condition declaration.

SciPy Radau uses `jac=None`, `vectorized=False`, `dense_output=True`,
`t_eval=None`, `first_step=None`, `max_step=inf`. Numerical Jacobian calls use the
same checked callback and physical integration coordinates. `IntegrationResult`
retains accepted-step `accepted_t`, `accepted_y`, and requested `requested_t`,
`output_y`, `present`; state arrays have `(time, component)` shape. Missing
requested rows contain NaNs and a false presence mask. Interpolation is evaluated
only inside the returned accepted interval. Every output is required for a full
positive result. A terminal event is an incomplete outcome even when SciPy
reports success. Exceptions retain their type/message and last **trial** callback
state/time. If SciPy raises, accepted history, horizon, numerical outputs and
solver counters are explicitly unavailable; trial times never replace them.

`nfev`, `njev`, `nlu` and actual callback/event invocation counts are retained.
Rejected-step and linear-solve counts are unavailable through this API and are
recorded as null. `nfev` need not include numerical Jacobian callback invocations.

## Retained numerical evidence

The runner has exactly six positive attempts: reversible exchange and forced
stiff pair, each at L0/L1/L2. Independent closed-form exponential/trigonometric
oracles, all requested/accepted states, signed errors, missing/defined masks,
absolute/amplitude/relative metrics, exchange constraints and refinement checks
are retained. Singularity truth is explicitly undefined at/after one second,
even if finite numerical states happen to extend slightly beyond that instant.
Its defined pre-singularity errors are diagnostic, without an amplitude bound.
The two additional L1 attempts are the terminal exchange event and finite-time
singularity. Expected negative outcomes must fail for their declared reason;
an arbitrary operational exception cannot satisfy the singularity control.

Run from an exact committed checkout with its locked installed environment.
Choose a new ignored local output directory every time; the runner refuses an
existing directory. For example (replace paths with local resolvers):

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  .venv/bin/python -m crucible.integration_verification run \
  .local/phase2c/campaign-unique-id --protocol /path/to/protocol-v1.md \
  --lock uv.lock --source-root "$PWD"
.venv/bin/python -m crucible.integration_verification reload \
  .local/phase2c/campaign-unique-id
.venv/bin/python -m crucible.integration_verification compare \
  /path/to/first/campaign /path/to/clean/repeat
```

No campaign has been run merely by adding this implementation. The lead records
actual accepted campaign and clean locked noneditable reproduction receipts.
Development tests are distinct from those campaigns. Keep stdout/stderr logs for
all commands, including failed tests and operational failures.

Each campaign writes incremental `manifest.json`, per-attempt numeric NPZ files
(`allow_pickle=False` on read), and `attempts.log`; incomplete operational runs
are preserved. Every declared numerical attempt continues independently after
another numerical attempt fails. Setup failures stop the campaign and retain an
incomplete manifest. Protocol/library/source identities, installed source byte
agreement, lock hash, Python/platform/hardware/thread settings and installed
package RECORD hashes are recorded; original wheel archive identities must be
retained by environment setup if available. Times distinguish setup, integration,
persistence and total; RSS values are cumulative process high-water marks,
with units normalized to bytes. NPZ byte sizes and aggregate non-manifest storage
are retained. These are reproduction observations, not performance claims.

Run `reload` in a fresh process. It verifies each NPZ hash/size and every array's
membership, dtype, shape, size and byte digest, then recomputes signed errors and
metrics with exact same-environment equality. `compare` requires exact source,
protocol, lock/library identities, classifications, grids and masks; numeric
state/oracle/error arrays use `atol=rtol=1e-12`. Counters and timings are reported,
without requiring bitwise agreement. This does not replace analytic accuracy,
constraint/refinement requirements, or the separate frozen callable checks.
