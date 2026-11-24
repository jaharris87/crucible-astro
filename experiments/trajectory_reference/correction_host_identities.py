"""Read-only live execution-host library receipt for D-040 offline verification.

Run this on the execution host after the campaign. It hashes existing files only;
no executable, compiler, fixture or physical source is invoked or substituted.
"""

import argparse
import datetime
import importlib.util
import json
import platform
import re
from pathlib import Path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def partial_attempts(campaign):
    """Archived interruptions and terminally quiescent unfinished current records."""
    entries = list(campaign.get("interrupted_attempts", []))
    archived = {entry["record"]["name"] for entry in entries}
    for record in campaign["attempts"]:
        if (
            record["name"] not in archived
            and not record.get("completed")
            and record.get("status") not in ("UNATTEMPTED", "CONDITIONALLY_UNATTEMPTED")
        ):
            entries.append(
                {
                    "record": record,
                    "directory": None
                    if record["status"] == "INTERRUPTED_BEFORE_LAUNCH"
                    else "attempts/" + record["name"],
                }
            )
    return entries


def expected_library_files(campaign):
    """Known process-time hashes, including available interrupted-process records."""
    helper = load(
        "_correction_library_inventory",
        Path(__file__).parent / "assembly_host_identities.py",
    )
    if any(a.get("completed") for a in campaign["attempts"]):
        expected, attempts = helper.expected_library_files(campaign)
    else:
        expected, attempts = dict(campaign["build"]["libraries"]), []
    for entry in partial_attempts(campaign):
        for name, identity in entry["record"].get("loaded_library_hashes", {}).items():
            if identity is None:
                continue
            if not Path(name).is_absolute() or not re.fullmatch(
                r"[0-9a-f]{64}", identity
            ):
                raise ValueError("invalid retained interrupted library identity")
            if name in expected and expected[name] != identity:
                raise ValueError("interrupted-process library identity differs")
            expected[name] = identity
    return expected, attempts


def interrupted_mapping_evidence(root, campaign, contract):
    """Recover last-flushed map paths, distinguishing later hashes from run hashes."""
    evidence = []
    for entry in partial_attempts(campaign):
        record, directory = entry["record"], entry.get("directory")
        detail = {
            "name": record["name"],
            "directory": directory,
            "recorded_hashes": {
                k: v
                for k, v in record.get("loaded_library_hashes", {}).items()
                if v is not None
            },
            "mapped_paths": [],
            "mapping_sha256": None,
            "observed_live_hashes": {},
            "unavailable": [],
        }
        if directory is None:
            detail["unavailable"].append(
                "No launched process mapping record; interrupted before launch."
            )
            evidence.append(detail)
            continue
        work = contract.safe_file(root, directory)
        maps = work / "loaded-maps.txt"
        if not maps.exists():
            detail["unavailable"].append(
                "Interrupted process has no flushed runtime mapping file."
            )
        else:
            inventory = record.get("files", {}).get("loaded-maps.txt")
            if inventory is not None:
                contract.require(
                    contract.digest(maps) == inventory["sha256"],
                    "interrupted runtime mapping changed",
                )
            else:
                detail["unavailable"].append(
                    "No process-time mapping inventory was flushed; mapping hash is a later quiescent raw snapshot."
                )
            detail["mapping_sha256"] = contract.digest(maps)
            paths = set()
            for line in maps.read_text().splitlines():
                columns = line.split(maxsplit=5)
                if (
                    len(columns) == 6
                    and "x" in columns[1]
                    and columns[5].startswith("/")
                ):
                    path = Path(columns[5])
                    if path.resolve() != (root / "bundle/trajectory_driver").resolve():
                        paths.add(str(path))
            detail["mapped_paths"] = sorted(paths)
            for name in detail["mapped_paths"]:
                if Path(name).is_file():
                    detail["observed_live_hashes"][name] = contract.digest(Path(name))
                else:
                    detail["unavailable"].append(
                        "Mapped file unavailable on execution host: " + name
                    )
        missing = set(detail["mapped_paths"]) - set(detail["recorded_hashes"])
        if missing:
            detail["unavailable"].append(
                "Process-time hashes were not flushed for some mapped files; later actual-host observations are separately labelled."
            )
        if not detail["mapped_paths"] and not detail["recorded_hashes"]:
            detail["unavailable"].append(
                "No interrupted runtime library identity evidence is available."
            )
        evidence.append(detail)
    return evidence


def collect(root, *, quiescent=False):
    root = Path(root).resolve()
    contract = load("_correction_identity_contract", root / "correction_campaign.py")
    contract.require(
        quiescent is True,
        "lead must verify all producers/controllers terminal before identity collection",
    )
    initial_campaign_sha = contract.digest(root / "campaign.json")
    prepared = json.loads((root / "prepared.json").read_text())
    campaign = json.loads((root / "campaign.json").read_text())
    contract.validate_prepared(root, prepared)
    contract.require(
        campaign["prepared_sha256"] == contract.digest(root / "prepared.json"),
        "campaign/preparation differs",
    )
    contract.require(
        contract.build_identities(root) == campaign["build"],
        "live build/library identity differs",
    )
    expected, attempts = expected_library_files(campaign)
    interrupted = interrupted_mapping_evidence(root, campaign, contract)
    for detail in interrupted:
        for name, identity in detail["observed_live_hashes"].items():
            contract.require(
                name not in expected or expected[name] == identity,
                "interrupted mapped file differs from known process-time hash",
            )
            expected[name] = identity
    checked = {}
    for name, identity in sorted(expected.items()):
        path = Path(name)
        contract.require(
            path.is_absolute() and path.is_file(),
            "actual execution-host library unavailable",
        )
        checked[name] = contract.digest(path)
        contract.require(checked[name] == identity, "execution-host library changed")
    contract.require(
        contract.digest(root / "campaign.json") == initial_campaign_sha,
        "campaign changed during identity collection",
    )
    for record in campaign["attempts"]:
        if record.get("completed"):
            contract.verify_attempt_files(root, record)
    for entry in partial_attempts(campaign):
        if (
            entry.get("directory") is not None
            and entry["record"].get("files") is not None
        ):
            contract.verify_attempt_files(
                root, entry["record"], directory=entry["directory"]
            )
    return {
        "schema": "crucible.phase2d.correction-host-identities.v1",
        "campaign_accounting_complete": campaign.get("complete") is True,
        "producer_quiescence_basis": "LEAD_VERIFIED_PRODUCERS_AND_CONTROLLER_TERMINAL",
        "numerical_source": contract.SOURCE_NAME,
        "protocol_sha256": contract.PROTOCOL_SHA256,
        "build_label": prepared["build_label"],
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
        "interrupted_library_evidence": interrupted,
        "library_identity_scope": "Completed and available interrupted process-time hashes are verified; interrupted raw mappings may add explicitly labelled later observations. Missing in-flight identity evidence remains unavailable.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--quiescent",
        action="store_true",
        required=True,
        help="confirm independently verified terminal producers/controller",
    )
    args = parser.parse_args()
    record = collect(args.root, quiescent=args.quiescent)
    with args.output.open("x") as stream:
        stream.write(json.dumps(record, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {"host_recheck": "PASS", "checked_files": len(record["checked_files"])}
        )
    )


if __name__ == "__main__":
    main()
