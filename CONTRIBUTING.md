# Development setup

Read [AGENTS.md](AGENTS.md) and the [workflow](docs/WORKFLOW.md) before changing
the project. Work from a governing issue and feature branch; post-seed changes
need an exact-candidate independent review and a concrete human merge decision.

B02 uses Python **3.12.9** and uv **0.10.11**, with one project-local `.venv`
and committed `uv.lock`. Python 3.12 is the initial supported minor version;
this reversible bootstrap choice uses an interpreter verified in the current
collaborator environment. Other Python minors and Windows are unverified.
The only development dependencies are pytest and Ruff; the package has no
runtime dependencies. JSON fixture handling will use the standard library.

Install the declared Python and uv versions before these commands. Put the uv
executable on `PATH` independently of the selected Python: a uv pyenv shim
installed only under another Python version will disappear when this
checkout selects 3.12.9. Run from a fresh checkout, with no inherited project
environment:

```sh
export UV_CACHE_DIR="$PWD/.local/cache/uv"
export UV_PYTHON_DOWNLOADS=never
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
uv sync --locked
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
mkdir -p .local/test-scratch
uv run --no-sync python -B -m pytest -p no:cacheprovider --basetemp=.local/test-scratch/run
```

The ignored `.local/` directory holds local caches, bounded temporary scratch
and execution receipts. Do not commit environments, caches or machine-specific
paths. Dependency installation needs network access on a cold cache. Only a
deliberate dependency change should regenerate the lock with `uv lock`;
review both metadata and lock changes. The build backend is pinned separately
in `build-system.requires` because build isolation is separate from runtime
dependency locking.

To verify a distributable installation rather than the normal editable setup,
use `uv sync --locked --no-editable` in a second fresh checkout, then run the
same checks. This installs `crucible` from the declared `src/` package instead
of relying on the current directory. The distribution regression checks SPDX
and `License-File` metadata in both setups. uv 0.10.11 editable installations
do not copy license files into the installed inventory, so the byte/inventory
assertion explicitly skips there. The noneditable setup must pass that
assertion against the complete root LICENSE; it is required packaging
verification, not replaced by the editable check.

`tests/test_import.py` launches isolated
Python from an empty temporary directory, disables bytecode writes, and checks
for output, runtime dependency imports, data-file access, common write events,
network and subprocess operations during package import. This is a bounded
regression check, not a security sandbox or proof about every possible side
effect. The current package initializer contains only a docstring.

Before verification, estimate resource use and update
[the shared ledger](docs/VERIFICATION.md). B01–B04 share 7,200 CPU-seconds,
1 GiB per test process and 100 MiB generated test scratch; environments/caches
are excluded from the scratch cap. Run tests serially, keep scratch bounded,
measure process CPU/peak memory, and stop before a cap is exceeded. CI jobs
will have a maximum 10-minute timeout. Preserve intentional failure evidence
and restore temporary probes; do not leave a failing probe in the candidate.
See [B02 evidence](docs/bootstrap/B02-EVIDENCE.md) for the actual local results
and their limits. These checks do not qualify data or establish scientific
validity; scientific results remain **not yet evaluated**.
