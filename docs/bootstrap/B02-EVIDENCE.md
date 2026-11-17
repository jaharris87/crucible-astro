# B02 local implementation evidence

Date: 2026-11-17. Governing [issue #2](https://github.com/jaharris87/crucible-astro/issues/2).
Worker: explicit `gpt-6.1-sol`, high reasoning; implementation and self-review,
not independent review. Branch: `bootstrap/b02-package`. Integration base:
`c3846a4660e5915fe56c115202d9b1581a2319fd` (verified main/origin/main/HEAD at start).
Candidate identity is the commit containing this record; final head/base must
be copied to the PR record when published. No PR, CI or human merge is claimed.

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
lockfile, tests and README used to build the package remain identical to this
clean-tested snapshot. No additional test rerun is warranted for those evidence
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

Lead publication as a draft PR, exact-pushed-candidate fresh independent review,
finding dispositions, human merge decision and merged-result verification
remain required. B03 provides CI later; this B02 candidate has no CI.
