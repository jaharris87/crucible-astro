# B04 implementation and local verification evidence

Date: 2026-11-17. Governing [issue #4](https://github.com/jaharris87/crucible-astro/issues/4),
[prior investigation](https://github.com/jaharris87/crucible-astro/issues/4#issuecomment-6958940130),
[contract specified before implementation](B04-CONTRACT.md).
Implementation/self-review: explicit `gpt-6.1-sol` High, no substitution or escalation,
no subagents. This is author evidence, not independent review or scientific acceptance.

## Candidate and scope

Base `6858849bb8ecdfb208fcefeaa2a1e3a7da42a4b8` (human-merged B03).
Tested source commit `89d9dd1946f1da7d2342ca51557ad8a90dd806e6`,
tree `74ee2e24c73f76f5589366e9f90a75e06e7bc3c4`, branch `bootstrap/b04-manifest`,
app-managed isolated worktree. This later receipt changes documentation only;
the final PR record must bind its actual head/base and required CI/review outcomes.

Added one concrete standard-library validator and value-error subclass, 40 targeted
contract tests, tiny original synthetic fixtures, and contract documentation. No
runtime/development dependency, lock, CI, initializer, scientific model or reference
change. The deliberately inconsistent order manifest is isolated in the clearly
named negative directory, whose payload is a byte-identical copy of the valid
payload; this preserves the single-sibling-payload contract without traversal.

Success is the plain dictionary of fixture ID, ordered species, shape and actual
payload checksum documented in the contract and asserted by `test_valid_manifest`.
Schema, units and state convention are explicitly synthetic. No loader framework,
sorting, scientific conversion, nuclear identities or two-hash agreement shortcut.

## Test-first and mutation evidence

Before implementation the contract, fixtures and tests were written, then a callable
stub raised `NotImplementedError("B04 validation is not implemented")`. The observed
initial run of `test_valid_manifest` and `test_manifest_order_mismatch` exited 1:
**2 failed**, both for that missing implementation. Raw snapshot identities:

| Initial artifact | SHA-256 |
| --- | --- |
| Callable stub | `386ed07a2803793163239450a941f3f148a51fadf4900cc4e305d4c9080e4ca1` |
| Initial tests | `36a50a4535d2a090c68a56d5783c3f484c45415a842268cf536135c0c2fd83e2` |
| Initial contract | `2d2cfd21278f086451d910516fe94e05e27c3ad97c87cf9e397a9c2e0015af21` |

The final tests differ from their initial snapshot only by formatting; an actual
AST comparison passed. After implementation all **40 validator tests passed**.
They cover the valid control, checksum computed from actual bytes, same-set order
permutation with unchanged checksum/payload/shape, duplicates on both sides,
missing/unexpected identities, unsupported schema, dimensions and minimal malformed
JSON/type/path/finite-number/read-size cases. Specific error codes are asserted.

The required mutation changed **only**:

```diff
-    if species != columns:
+    if set(species) != set(columns):
```

Editable source binding was explicitly asserted against `src/crucible/manifest.py`
and its mutated comparison before running:

```sh
python -B -m pytest -q -p no:cacheprovider \
  --basetemp=.local/b04/scratch/mutation \
  tests/test_manifest.py::test_manifest_order_mismatch
```

Observed exit 1, **1 failed** at the exception assertion after the valid control:

```text
E       Failed: DID NOT RAISE ManifestValidationError
```

This detects accepting the same-shape, same-set permutation. The mutation was
never committed and was restored in a `finally` block. Original/restored bytes
were directly compared and their hashes agree:

| Source state | SHA-256 |
| --- | --- |
| Original and byte-identical restored/final | `b621b681b1dcdcb6636f41a9fdd8619ff78501212f1e145814f6425b1e915fd4` |
| Temporary set-comparison mutation | `a166da664266d6c4d002d9af2ff7c00c196cb33534b4ffafba56732a0cb67136` |

After restoration both the valid and order controls passed (**2 passed**); lint
and format checks passed. The final validator test hash is
`4b7faab5eebb477dcf016fd4bd64924bf0de76bffc786332a313075a7282ea35`.
Both tracked payload copies hash to
`96e260dbc926fff7f3060e3f227ae76d3a5076bc0349258555f642e5430057b7`.

## Clean committed reproduction

A fresh local clone of the committed feature branch, without hardlinks, was clean
before installation and remained clean after checks. Exact version controls:
Python **3.12.9**, uv **0.10.11**, locked pytest **9.2.0**, Ruff **0.17.5**;
no interpreter or dependency downloads. Existing cache was used with:

```sh
export UV_PYTHON_DOWNLOADS=never
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTHONDONTWRITEBYTECODE=1
uv sync --locked --offline --no-editable
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -B -m pytest -q -p no:cacheprovider \
  --basetemp="$TMPDIR/clean"
```

The harness clears inherited `PYTHONPATH`, `PYTHONHOME`, `VIRTUAL_ENV` and
`UV_PROJECT_ENVIRONMENT`; plugin overrides are empty and scratch is explicitly
bounded to the retained receipt area. An actual imported-module probe asserts
that the validator comes from this clone's `.venv` site-packages, not source,
that noneditable direct-URL metadata is false for editable, and that installed
validator bytes match the final source hash above.

Observed: locked noneditable installation PASS, lint PASS, format PASS,
**42 passed / 0 skipped**. This includes the full installed LICENSE bytes,
SPDX/License-File metadata and RECORD-inventory regression, plus the isolated
root-package import audit for file access, writes, output, dependencies, network
and subprocess activity. The unchanged initializer remains a docstring.

The harness records each command's actual exit status, elapsed wall time,
`RUSAGE_CHILDREN` user+system CPU, and maximum child RSS (macOS reports bytes).
These portable summaries are adapted from raw local receipts; machine paths
are omitted. Labels map directly to ignored `.local/b04/<label>.json` and `.log`.

| Label | Exit | Child CPU s | Wall s | Peak RSS bytes |
| --- | ---: | ---: | ---: | ---: |
| `01-editable-sync` | 0 | 0.060691 | 0.051173 | 47824896 |
| `02-initial-red` | 1 | 0.322519 | 0.338067 | 45547520 |
| `03-format` | 0 | 0.014250 | 0.272734 | 20447232 |
| `04-source-tests` | 0 | 0.301787 | 0.306638 | 46759936 |
| `05-mutated-source-binding` | 0 | 0.020638 | 0.022516 | 18989056 |
| `06-order-mutation` | 1 | 0.270352 | 0.273429 | 45531136 |
| `07-restored-order-control` | 0 | 0.249486 | 0.252156 | 44957696 |
| `08-lint` | 0 | 0.013741 | 0.011622 | 22659072 |
| `09-format-check` | 0 | 0.021573 | 0.010860 | 27017216 |
| `10-clean-clone` | 0 | 0.074775 | 0.071806 | 10878976 |
| `11-clean-sync` | 0 | 0.055268 | 0.041547 | 48873472 |
| `12-clean-binding` | 0 | 0.045584 | 0.048265 | 25231360 |
| `13-clean-lint` | 0 | 0.018710 | 0.261502 | 22495232 |
| `14-clean-format` | 0 | 0.021049 | 0.011330 | 27475968 |
| `15-clean-suite` | 0 | 0.307906 | 0.323318 | 46432256 |
| `16-clean-status` | 0 | 0.008163 | 0.009981 | 9043968 |

Total measured child CPU: **1.806492 seconds**; recorded command wall time:
**2.306943 seconds**. Maximum observed child RSS: **48,873,472 bytes**;
maximum test-command RSS: **46,759,936 bytes**, both below 1 GiB. Retained
B04 clone/scratch/receipts excluding environments/caches measured **4,698,308
bytes** before this evidence receipt, below 100 MiB. Serial processes only.
No GPU, training, real data, bulk downloads, HPC or CI launched by the worker.

The worker conservatively charges **120 CPU-seconds**, covering all measured
work and unmeasured command/edit/inspection/commit/receipt overhead with ample
elapsed-times-16-logical-CPUs allowance; no unmeasured network waiting was excluded.
Unused **120** of the original **240** reservation is released. Shared phase
charge becomes **1,746 / 7,200**. Separately reserve **120** for lead source/docs/
remote reconciliation, per lead direction, giving **1,866 charged+reserved**.
No CI or independent-review allocation is included in that lead reservation.

macOS hard address-space/RSS and scratch filesystem enforcement were not available;
these are measured observations, not proof of enforcement. Existing Linux CI
controls must run on the eventual PR. The import regression is bounded and does
not prove every possible side effect. Only Python 3.12/macOS is locally verified;
CI/Linux and other platforms await their actual checks.

## Self-review, retention and pending gates

The author inspected the complete source/tests/fixture/contract/ledger delta
against issue acceptance, including malformed paths/types, actual-byte checksum,
expected/observed order diagnostics, test false-pass routes, absence of scientific
claims, unchanged initializer/lock/CI and portable public documentation. The
ordering test validates identical bytes, membership and dimensions before requiring
`order_mismatch`; no unrelated rejection satisfies it. The required targeted
mutation provides direct effectiveness evidence. No shared abstraction or extra
scientific semantics was introduced. This self-review is not independent review.

Raw initial failure, all command logs/JSON, test-first snapshots with checksums,
original and mutated source snapshots, mutation/restoration receipt, clean clone
and execution scripts remain in ignored `.local/b04/` for lead preservation before
managed-worktree archival. The test-first contract/tests and fixture files were
retained before replacing the stub. No intentionally failing source is tracked.

Remaining: lead reconciliation and draft push/PR; exact pushed-head CI and fresh
read-only independent review; preserve original findings/dispositions and focused
repair checks if needed; explicit human merge decision; merged-SHA integration
checks and Phase 0B closeout. No such outcome is claimed by this receipt. Scientific
results and real-data qualification remain **not yet evaluated**; Phase 1 is outside
this authorization.
