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
| Clean noneditable reproduction | Pending before final candidate handoff |

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

Peak memory, CPU accounting and final self-review are completed below before
handoff. No real data, models, training, CI or scientific results are evaluated.

## Remaining gates

Lead publication as a draft PR, exact-pushed-candidate fresh independent review,
finding dispositions, human merge decision and merged-result verification
remain required. B03 provides CI later; this B02 candidate has no CI.
