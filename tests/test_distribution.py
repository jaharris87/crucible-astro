"""Check license metadata and noneditable distribution notice contents."""

import json
from importlib.metadata import distribution
from pathlib import Path

import pytest


def test_installed_distribution_contains_complete_license():
    installed = distribution("crucible-astro")
    assert installed.metadata["License-Expression"] == "BSD-3-Clause"
    assert installed.metadata.get_all("License-File") == ["LICENSE"]

    direct_url = json.loads(installed.read_text("direct_url.json") or "{}")
    if direct_url.get("dir_info", {}).get("editable", False):
        pytest.skip(
            "uv editable installs do not copy license files; "
            "use uv sync --locked --no-editable to check the installed inventory"
        )

    # distribution.files reads RECORD, so this also checks the installed inventory.
    license_paths = [
        path
        for path in installed.files or []
        if path.as_posix().endswith(".dist-info/licenses/LICENSE")
    ]
    assert len(license_paths) == 1
    expected = (Path(__file__).resolve().parents[1] / "LICENSE").read_bytes()
    assert installed.locate_file(license_paths[0]).read_bytes() == expected
