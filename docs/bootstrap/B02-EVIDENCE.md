# B02 local implementation evidence

Date: 2026-11-17. Governing [issue #2](https://github.com/jaharris87/crucible-astro/issues/2).
Worker: explicit `gpt-6.1-sol`, high reasoning; implementation and self-review,
not independent review. Branch: `bootstrap/b02-package`. Integration base:
`c3846a4660e5915fe56c115202d9b1581a2319fd` (verified main/origin/main/HEAD at start).
Candidate identity is the commit containing this record; final head/base must
be copied to the PR record when published. Draft [PR #5](https://github.com/jaharris87/crucible-astro/pull/5) now exists; no CI or human merge is claimed.

The original implementation/check and lead-reconciliation records below are
preserved historical evidence. The B02-R1 repair section supersedes earlier
freshness statements for its changed configuration and new regression test.

## Declared environment

Local platform: Darwin arm64, 16 logical CPUs. Python 3.12.9 and uv 0.10.11;
initial Python support is `>=3.12,<3.13`, with `.python-version` pinning 3.12.9.
This is a reversible tooling choice based on the installed collaborator
environment, not evidence for other platforms. Zero runtime dependencies;
pytest and Ruff are the only direct development dependencies.

`uv lock` resolved pytest 9.2.0, Ruff 0.17.5, iniconfig 2.3.1, packaging 26.3,
pluggy 1.7.0 and Pygments 2.21.0. The lock also records Windows-only colorama
0.4.6, not installed on this host. All registry/artifact locators are public
PyPI locations with hashes. The exact build backend `uv_build==0.10.11` is
pinned separately in `pyproject.toml`; the public PyPI release metadata
confirmed version 0.10.11, Python >=3.8 and 19 distributions. Matching uv
can use its bundled backend. `uv sync --locked` built and installed
`crucible-astro==0.0.0` successfully.

## Observed checks

Commands use the uv executable directly on PATH, with project-local
`UV_CACHE_DIR`, `UV_PYTHON_DOWNLOADS=never`, and pytest plugin autoload disabled.
Download/build/install concurrency was set to one for setup. Exact successful
setup/check commands are documented in [CONTRIBUTING](../../CONTRIBUTING.md).

| Check | Actual observation |
| --- | --- |
| Lock and editable setup | `uv lock`, then `uv sync --locked`: exit 0; seven packages installed including the project |
| Lint | `ruff check .`: exit 0, `All checks passed!` |
| Format | `ruff format --check .`: exit 0 |
| Deliberate runner failure | Temporary `.local/b02/test_probe.py` asserted False with message `B02 deliberate test-runner failure`; pytest exit 1, `1 failed in 0.02s`, failure was that exact AssertionError |
| Corrected runner control | Same temporary test changed to assert True; pytest exit 0, `1 passed in 0.00s`; probe then removed |
| Import regression | Final installed-environment test: pytest exit 0, `1 passed in 0.02s`; empty outside working directory, no output, audit permits package-code reads only and rejects tested side effects |
| Clean noneditable reproduction | Isolated local clone of implementation snapshot `c579b59` (full identity below), initially without an environment; locked noneditable setup, lint, format and the one import test all exit 0 |

The temporary failure/corrected commands were `python -B -m pytest -q -p
no:cacheprovider .local/b02/test_probe.py --basetemp=<dedicated-scratch>`.
The final test used the same invocation without the temporary probe path.
Local raw receipts are retained under ignored `.local/b02/`; this portable
record preserves the outcomes without publishing machine paths.

## Preserved setup failures and limits

- macOS rejected an attempted 1 GiB `RLIMIT_DATA` before uv execution. The
  wrapper was corrected to measure peak RSS, while retaining 30 CPU-second
  and 100 MiB single-file limits. No hard RSS enforcement is claimed.
- uv was installed under pyenv's 3.13.0 interpreter only; selecting 3.12.9
  caused the uv shim to exit 127 before dependency work. The resolved uv
  executable then worked; CONTRIBUTING documents the PATH requirement.
- Default sandbox network policy blocked PyPI. Authorized dependency resolution
  and installation were retried with sandbox escalation and succeeded.
- An initial import-test invocation failed in pytest temporary-directory setup
  because the scratch parent did not exist. Creating that parent corrected
  setup; the import test then passed. No package change was needed.

## Clean reproduction and candidate binding

The clean checkout was created from committed implementation snapshot
`c579b599347470be2c6d396a0a20e0e7d5e1c922` using `git clone --local --no-hardlinks --branch
bootstrap/b02-package . .local/b02/clean`. It inherited no environment or
untracked source. From that checkout the following commands succeeded, using
the previously downloaded dependency cache, the declared interpreter and no
network access during installation:

```sh
uv sync --locked --no-editable --offline
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
mkdir -p .local/test-scratch
uv run --no-sync python -B -m pytest -p no:cacheprovider --basetemp=.local/test-scratch/run
```

Pytest collected one test and reported `1 passed in 0.02s`. Its child ran in
an empty directory outside the clean checkout's source tree. A second explicit
`python -I -B` invocation from an empty sibling directory verified the installed
origin `site-packages/crucible/__init__.py`, distribution version `0.0.0`, no
runtime requirements and an unchanged working directory. No source checkout
path was used as the installed module origin. Cache reuse means this is a
clean-environment reproduction, not a second cold network-download test.

The final evidence/accounting edits change documentation only; package,
lockfile and tests remain identical to this clean-tested snapshot. Subsequent README/progress/handoff reconciliation changes descriptive metadata only, with no runtime/build configuration change. No additional test rerun is warranted for those evidence
edits. The following SHA-256 identities bind the tested implementation inputs:

| Input | SHA-256 |
| --- | --- |
| `.python-version` | `7c31b8cce5796f169ade750a43dfa5f9fb4c326e90aab5c8e83189b0f6011eb8` |
| `pyproject.toml` | `df396e2d39627956b1b75cb0d12149cf36fa93453c904f69dd6c76aef71999f9` |
| `uv.lock` | `377eb7c50c43b6cee82cd35040f376cb042253be512982f4acbb43785cee9834` |
| `src/crucible/__init__.py` | `e88260f09b2dc5f33544dbb7fb3b86cb3fc2653969a718d4901a55cedf7ee4d3` |
| `tests/test_import.py` | `554b1fa6ba55a11a5462ea7a0abc7c2667de298557b8c78b824478224ec72c07` |

## Resource observations and self-review

Sixteen recorded commands used **2.320553 child CPU-seconds** and **5.246011
seconds wall time** in aggregate, measured through `getrusage(RUSAGE_CHILDREN)`
and a monotonic clock. This includes subprocess descendants that were reaped
by their parent. Maximum observed RSS was **61,505,536 bytes** across setup and
checks; the maximum among pytest commands was **46,989,312 bytes**. All were
under 1 GiB. B02-generated files including the clean clone and receipts, but
excluding environments/caches, totaled **317,241 bytes** at inspection, under
100 MiB. The initial pre-exec and sandbox-blocked attempts lack complete CPU
receipts; the shared ledger charges **30 CPU-seconds** overall to include
these, inspections and final documentation/commit overhead. Raw timings,
return codes and output remain in ignored `.local/b02/runs.jsonl` and logs.

Self-review inspected the complete diff against issue #2, package/build inputs,
actual resolved lock, import-probe scope, temporary-probe removal, newly added
documentation links and local-path screening. No models, data or reference
code were added; no machine paths occur in the new public package/configuration
or evidence. The initializer is only a docstring. No unresolved implementation
blocker was identified. This is an author self-review, with **no independent
review coverage claimed**. No real data, training, CI or scientific results are
evaluated.

## Remaining gates

Lead publication of the repair to the existing draft PR, exact-pushed-candidate
focused independent verification, final finding disposition, human merge
decision and merged-result verification remain required. B03 provides CI
later; this B02 candidate has no CI.

## Lead reconciliation and self-review

Lead inspected the full B02 diff, resolved lock, clean-install/import raw receipts and failure/control logs, and reconciled README, progress, handoff and bootstrap status with actual GitHub records. Executable inputs retain the hashes above; no software rerun for descriptive documentation edits. Lead reconciliation check passed: 29 tracked files screened, 113 local links and 22 anchors resolved, no absolute machine-path/credential-pattern errors, and all five executable/configuration/lock/test inputs byte-equal to the tested commit. Measured check CPU time was 0.0102 seconds. The PR discussion is the source of record for exact final head/base and independent review, avoiding a self-referential commit hash in the candidate.

## B02-R1 repair: installed license preservation

Original finding, P2/high confidence: **“The noneditable distribution drops the
BSD copyright and license text.”** Fresh-context read-only `gpt-6.1-sol`, high
reasoning, reviewed head `44326c682100572b79774dab67bee4ff5173584d` against base
`c3846a4660e5915fe56c115202d9b1581a2319fd`. The original finding and evidence
were [preserved in PR #5 before repair](https://github.com/jaharris87/crucible-astro/pull/5#issuecomment-6959156535).
The initial reviewer reported no other consequential finding; this was not
acceptance or a human merge decision.

The reviewer found `License-Expression: BSD-3-Clause` in installed METADATA,
but no `License-File` field or LICENSE/notice in RECORD. The root LICENSE has
the accepted UT-Battelle notice and full redistribution terms. Author
disposition: **agree; repair required**. No reviewed finding was erased or
converted to an approval.

Repair is limited to `project.license-files = ["LICENSE"]` and one installed-
distribution regression. The test requires the expression and `License-File`
metadata, the LICENSE entry in installed RECORD, and exact installed bytes
matching the root LICENSE. The existing initializer/import contract is
unchanged. No additional dependency or scientific code is introduced.

Before changing package configuration, the new regression ran against the
retained old noneditable installation in `.local/b02/clean/`, with that
environment's Python and pytest, using:

```sh
python -B -m pytest -q -p no:cacheprovider tests/test_distribution.py --basetemp=.local/b02/scratch/repair/old
```

Observed: exit 1, `1 failed in 0.02s`; exact failure was
`installed.metadata.get_all("License-File")` returning `None` instead of
`["LICENSE"]`. The old installation is retained unchanged. This verifies
that the new regression detects the original packaging failure.

The exact repair source snapshot is
`4ec0af57c7990b7981a0f6c60bb876bc30012d7b`, a descendant of reviewed head
`44326c682100572b79774dab67bee4ff5173584d`. It was cloned with
`git clone --local --no-hardlinks --branch bootstrap/b02-package . .local/b02/repair-clean`
into a new directory, retaining the old failed installation. In the new
checkout, the commands below succeeded with the pinned interpreter, uv
version, project-local dependency cache and no dependency network access:

```sh
uv sync --locked --no-editable --offline
mkdir -p .local/test-scratch
uv run --no-sync python -B -m pytest -p no:cacheprovider --basetemp=.local/test-scratch/run
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
```

The build ran again, installed a noneditable distribution into its own fresh
environment, and left the committed lock unchanged. Pytest collected both
tests and reported **2 passed in 0.03s**; lint and format exited 0. The
existing import regression still checks empty outside-directory execution,
no output and its bounded side-effect audit.

A separate isolated `python -I -B` inspection used the new environment and an
empty sibling working directory. Import resolved inside `site-packages`.
Installed METADATA had `License-Expression: BSD-3-Clause` and
`License-File: LICENSE`. Installed RECORD contained:

```text
crucible_astro-0.0.0.dist-info/licenses/LICENSE,sha256=9wHkeGHepknZQeQcV8AF5CgudYnhBJeGC8igkMly4PY,1466
```

The installed file equaled the complete root LICENSE byte-for-byte:
**1,466 bytes**, SHA-256
`f701e47861dea649d941e41c57c005e4282e7589e10497860bc8a090c972e0f6`.
The inspection independently recomputed the RECORD digest and size and
verified the empty working directory stayed unchanged. No root license text,
runtime dependency or scientific behavior was changed.

Repair fingerprints (the unchanged lock, initializer and import-test hashes
remain those in the historical table):

| Input | SHA-256 |
| --- | --- |
| `pyproject.toml` | `991b95b16044d71fa9b202b9ffa9023740fc4fd563e750eddca908ed4a7ed7f9` |
| `tests/test_distribution.py` | `d06ae988b90e378766f2b1de149236ee9c7883345b2a2a8cfe86b5007ad71035` |
| `LICENSE` | `f701e47861dea649d941e41c57c005e4282e7589e10497860bc8a090c972e0f6` |

Seven repair commands used **0.857341 measured child CPU-seconds** and
**1.426356 seconds wall time**, including the expected old-install failure.
Maximum observed RSS was **44,515,328 bytes**; total retained B02 generated
files, clone metadata and receipts excluding environments/caches measured
**708,151 bytes** at inspection. Both remain within the adopted caps. The
shared ledger charges **20 CPU-seconds**, including unmeasured inspection,
documentation and commit overhead, and releases 100 of the pre-run 120
CPU-second repair reservation. Raw commands, timings and output are retained
as `repair-*` records in ignored `.local/b02/runs.jsonl` and logs.

The combined lead accounting was corrected to an **800 CPU-second** envelope
using <= 50 s aggregate local-command elapsed × 16 logical cores where CPU
measurements were unavailable; no network-wait exclusion remains. Original
check observations remain preserved. After this repair, the ledger contains
**1,000 CPU-seconds charged plus 60 reserved** for focused independent review.

Author self-review inspected the narrow source delta, original finding,
old-install regression failure, clean rebuild output, full license bytes and
metadata/RECORD evidence. Final edits after the tested source snapshot change
only evidence/accounting documents; no repeated successful software check is
needed for those edits. The repair is **locally verified, awaiting exact-
pushed-candidate focused independent verification** and final disposition.
No push, focused review, ready transition, CI or merge is claimed.
