"""Read-only execution-system identity recheck for the completed D-039 campaign.

No compiler, executable, solver or physical source is invoked. The original,
source-bound host checker hashes retained build files and actual vendor libraries.
The recorded hostname distinguishes this recheck from the original compute host.
"""

import argparse
import datetime
import importlib.util
import json
import platform
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError("assembly host identities: " + message)


def expected_library_files(campaign):
    """All build-linked and actually mapped runtime files, without substitution."""
    expected = dict(campaign["build"]["libraries"])
    attempts = []
    for record in campaign["attempts"]:
        if not record.get("completed"):
            continue
        require(
            record.get("loaded_library_unavailable_reason") is None,
            "runtime library evidence unavailable",
        )
        libraries = record.get("loaded_library_hashes")
        require(
            isinstance(libraries, dict) and libraries,
            "runtime library evidence missing",
        )
        for name, identity in libraries.items():
            require(
                name not in expected or expected[name] == identity,
                "runtime library identity changed between processes",
            )
            expected[name] = identity
        attempts.append(record["name"])
    require(expected and attempts, "no completed physical-process identity evidence")
    return expected, attempts


def collect(root):
    root = Path(root).resolve()
    spec = importlib.util.spec_from_file_location(
        "_completed_assembly_identity_contract", root / "assembly_campaign.py"
    )
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract)
    prepared = json.loads((root / "prepared.json").read_text())
    campaign = json.loads((root / "campaign.json").read_text())
    contract.validate_prepared(root, prepared)
    require(campaign.get("complete") is True, "campaign not completely accounted")
    require(
        campaign["prepared_sha256"] == contract.digest(root / "prepared.json"),
        "campaign/preparation differs",
    )
    # This is the unmodified executed host check, including actual absolute paths.
    require(
        contract.build_identities(root) == campaign["build"],
        "live host build/library identities differ from executed campaign",
    )
    expected, attempts = expected_library_files(campaign)
    checked = {}
    for name, identity in sorted(expected.items()):
        require(
            Path(name).is_absolute() and Path(name).is_file(),
            "actual execution-host library unavailable",
        )
        checked[name] = contract.digest(Path(name))
        require(checked[name] == identity, "actual execution-host runtime file changed")
    return {
        "schema": "crucible.phase2d.assembly-host-identities.v1",
        "numerical_source": campaign["numerical_source"],
        "source_commit": prepared["source_commit"],
        "source_tree": prepared["source_tree"],
        "prepared_sha256": contract.digest(root / "prepared.json"),
        "campaign_sha256": contract.digest(root / "campaign.json"),
        "collector_sha256": contract.digest(Path(__file__)),
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "host": platform.node(),
        "build": campaign["build"],
        "checked_files": checked,
        "completed_attempts": attempts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    record = collect(args.root)
    with args.output.open("x") as stream:
        stream.write(json.dumps(record, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {"host_recheck": "PASS", "checked_files": len(record["checked_files"])}
        )
    )


if __name__ == "__main__":
    main()
