# Development setup

Read [AGENTS.md](AGENTS.md) and the [workflow](docs/WORKFLOW.md) before changing
the project. Work from a governing issue and feature branch. The workflow
specifies independent review, the future narrow documentation lane and the
concrete human merge decision required for every post-seed change.

## Quick start

Use Python **3.12.9** and uv **0.10.11**. Python 3.12 is the initial supported
minor version; other minors and Windows are unverified. Put uv on `PATH`
independently of Python: a uv pyenv shim installed only under another Python
version can disappear when this checkout selects 3.12.9.

From the repository root:

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

The default editable setup deliberately skips one installed-license inventory
assertion; metadata is still checked. The noneditable verification below must
pass it without a skip. The S02 extraction module uses pinned h5py (and its
locked NumPy dependency) for HDF5 output. The root package remains inert; pytest and Ruff are
the development dependencies. JSON handling uses the standard library. See the
[quarantined reader contract](docs/phase1/S02_READER.md) for the explicit local
resolver/recipe and scientific exclusions. Private data are never CI inputs.

## Isolated reproduction

Use a fresh checkout without an inherited project environment or external pytest
plugins when collecting verification evidence:

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

The ignored `.local/` directory holds caches, temporary scratch and local
receipts. Do not commit environments, caches or machine-specific paths. A cold
cache needs ordinary package-manager network access. Only a deliberate
dependency change should regenerate `uv.lock`; review metadata and lock changes
together. The build backend is pinned separately in `build-system.requires`
because isolated builds are separate from runtime dependency locking.

## Installed-package verification

In a second fresh checkout, use `uv sync --locked --no-editable`, then run the
same checks with `uv run --no-sync`. For a reused noneditable environment after
source edits, force the pinned uv version to reinstall the project:

```sh
uv sync --locked --no-editable --reinstall-package crucible-astro
```

This avoids testing a previously installed copy when an edit is not picked up
by the existing build cache. uv 0.10.11 documents `--reinstall-package` as
reinstalling the named package regardless of whether it is already installed.
A fresh checkout remains the preferred acceptance path; this note does not claim
cache behavior is identical across uv versions.

The distribution regression checks SPDX and `License-File` metadata. uv 0.10.11
editable installations omit copied license files from the installed inventory,
so the byte/inventory assertion explicitly skips there. Noneditable verification
must check the complete root LICENSE and installed inventory without that skip.

`tests/test_import.py` launches isolated Python from an empty temporary directory,
disables bytecode writes, and checks output, runtime dependency imports, data-file
access, common write events, network and subprocess operations during root-package
import. The initializer remains a docstring; validation lives in
`crucible.manifest`. This bounded regression is not a security sandbox or proof
about every possible side effect.

## CI and retained evidence

The one-job `fast-checks` workflow runs on PRs to main, including drafts, and
pushes to main. It installs with `uv sync --locked --no-editable`, checks lint and
format, and runs the serial test suite without the editable inventory skip.
D-013 removes repository-imposed compute/resource caps, reservations and command
accounting. Historical [verification records](docs/VERIFICATION.md) remain
unchanged evidence; they are not current execution requirements. This grants no
new scientific phase, task or purchase authority. See the canonical
[workflow](docs/WORKFLOW.md#resources-and-authority) for scope and failure rules.

Preserve intentional failure evidence and restore temporary probes. Use pytest
temporary fixtures or `TMPDIR` for scratch. Record actual commands, results,
negative controls and limitations in the governing issue/PR. Keep subsequent
CI/review/merge receipts there rather than committing a receipt solely to record
that the previous head passed. Scientific results remain **not yet evaluated**
until qualified experiments support them.

Use the issue form, PR template and canonical workflow for exact candidate/base,
review findings/dispositions and merged-result verification. D-014's narrow lane
applies only after Phase 0B; this closeout, code, policy and scientific changes
retain independent review. Choose models through the canonical
[model policy](docs/WORKFLOW.md#model-selection-and-escalation) (D-012/D-015).
