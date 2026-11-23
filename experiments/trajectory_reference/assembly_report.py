"""Offline D-039 reporting and fresh-process reload; never invoke a producer.

Recompute the host-safe raw science gates, retain unsuccessful/conditional work,
and use the existing numeric JSON/NPZ artifact boundary. Qualification here means
only the accepted arithmetic/first-step investigation, never a trajectory reference.
"""

import argparse
import importlib.util
import io
import json
import platform
import re
from pathlib import Path

import numpy as np

from crucible import trajectory_reference as artifacts

HERE = Path(__file__).resolve().parent
DECISIONS = ("pass", "software_pass", "fatal", "ordinary_numerical_failure")
UNATTEMPTED = {"UNATTEMPTED", "CONDITIONALLY_UNATTEMPTED"}
REPORT = "assembly-verification.json"
HOST_IDENTITIES = "host-identity-verification.json"


def require(condition, message):
    if not condition:
        raise ValueError("assembly report: " + message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def numeric_details(value):
    """Retain numeric vectors once, with explicit masks for undefined displays."""
    if isinstance(value, dict):
        result = {key: numeric_details(item) for key, item in value.items()}
        if "exact" in value and isinstance(value.get("rounded"), list):
            rounded = value["rounded"]
            result["rounded"] = np.array(
                [np.nan if x is None else x for x in rounded], dtype="<f8"
            )
            result["rounded_finite"] = np.array(
                [x is not None and np.isfinite(x) for x in rounded], dtype=bool
            )
        return result
    if isinstance(value, (list, tuple)):
        if value:
            try:
                array = np.asarray(value)
            except (TypeError, ValueError, OverflowError):
                array = None
            if array is not None and array.dtype.kind in "biuf":
                return array.copy()
        return [numeric_details(item) for item in value]
    return value


def verify_retained_build(root, prepared, campaign, contract, expected_host_sha):
    """Verify local retained bytes and a hash-bound live execution-host recheck.

    Vendor paths are neither remapped nor silently skipped. The separate receipt
    rechecks those files on their actual host using the unchanged executed checker.
    """
    require(
        isinstance(expected_host_sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_host_sha),
        "explicit execution-host identity receipt SHA256 required",
    )
    proof = json.loads(artifacts.checked(root / HOST_IDENTITIES, expected_host_sha))
    helper = load_module(
        "_assembly_report_host_identities", HERE / "assembly_host_identities.py"
    )
    build = campaign["build"]
    expected, attempts = helper.expected_library_files(campaign)
    require(
        proof.get("schema") == "crucible.phase2d.assembly-host-identities.v1"
        and proof.get("numerical_source") == contract.SOURCE_NAME
        and proof.get("source_commit") == prepared["source_commit"]
        and proof.get("source_tree") == prepared["source_tree"]
        and proof.get("prepared_sha256") == contract.digest(root / "prepared.json")
        and proof.get("campaign_sha256") == contract.digest(root / "campaign.json")
        and proof.get("collector_sha256")
        == contract.digest(HERE / "assembly_host_identities.py")
        and proof.get("build") == build
        and proof.get("checked_files") == expected
        and proof.get("completed_attempts") == attempts,
        "execution-host identity proof differs from retained campaign",
    )
    require(
        all(
            Path(name).is_absolute() and re.fullmatch(r"[0-9a-f]{64}", h)
            for name, h in expected.items()
        ),
        "invalid retained library identity",
    )
    require(
        json.loads((root / "bundle/linked-library-hashes.json").read_text())
        == build["libraries"],
        "linked library receipt differs",
    )
    for name, identity in build["build_files"].items():
        require(
            contract.digest(contract.diag.safe_file(root, name)) == identity,
            "retained build file identity differs",
        )
    for name, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
        ("assembly_synthetic", "assembly-executable.sha256"),
    ):
        fields = (root / "bundle" / receipt).read_text().split()
        require(
            len(fields) == 2
            and Path(fields[1]).name == name
            and fields[0]
            == build["executables"][name]
            == contract.digest(root / "bundle" / name),
            "retained executable identity differs",
        )
    return {
        "sha256": expected_host_sha,
        "checked_files": len(expected),
        "scope": "actual execution-host recheck plus retained build/runtime receipts",
    }


def _stage_checks(prepared, campaign, outcomes):
    """Check conditional execution from recomputed outcomes, not success flags."""
    by_stage = {
        stage: [s for s in prepared["attempts"] if s["stage"] == stage]
        for stage in ("identity", "derivative", "standard", "tight")
    }
    records = {a["name"]: a for a in campaign["attempts"]}

    def attempted(spec):
        return records[spec["name"]].get("status") not in UNATTEMPTED

    def passed(stage):
        return all(outcomes[s["name"]].get("pass") is True for s in by_stage[stage])

    identity, derivative, standard = (
        passed(stage) for stage in ("identity", "derivative", "standard")
    )
    if any(attempted(s) for s in by_stage["derivative"]):
        require(identity, "derivatives executed before all identity/arithmetic gates")
    if any(attempted(s) for s in by_stage["standard"]):
        require(identity and derivative, "first steps executed before frozen gates")
    if any(attempted(s) for s in by_stage["tight"]):
        require(standard, "tight work executed without both standard passes")
    for spec in prepared["attempts"]:
        record = records[spec["name"]]
        if record.get("status") != "CONDITIONALLY_UNATTEMPTED":
            continue
        stage, reason = spec["stage"], record.get("skip_reason")
        require(
            (
                stage in {"standard", "tight"}
                and identity
                and not derivative
                and reason == "DERIVATIVE_GATES_FAILED"
            )
            or (
                stage == "tight"
                and identity
                and derivative
                and not standard
                and reason == "BOTH_STANDARD_ATTEMPTS_DID_NOT_PASS"
            ),
            "unsupported conditional exclusion",
        )
        require(
            not (Path(campaign["_root"]) / "attempts" / spec["name"]).exists(),
            "conditionally unattempted process has raw execution directory",
        )
    return {"identity": identity, "derivative": derivative, "standard": standard}


def _capture_workspaces(root, prepared, gates):
    """Keep unique private numeric operands/results; raw probes remain immutable."""
    captured, unavailable, matrices = {}, {}, {}
    for spec in prepared["attempts"]:
        work = root / "attempts" / spec["name"]
        for path in sorted(work.glob("assembly-*.bin")):
            if not re.fullmatch(
                r"assembly-(baseline-\d{3}|accepted|failure)\.bin", path.name
            ):
                continue
            relative = str(path.relative_to(root))
            try:
                raw = gates.parse_workspace(path.read_bytes())
                old_name = path.name.removeprefix("assembly-")
                if old_name in {"accepted.bin", "failure.bin"}:
                    old_name = "baseline-" + old_name
                old = gates.parse_original((work / old_name).read_bytes())
                key = gates.sha(
                    (work / "used-maps.bin").read_bytes()
                    + (work / "species.bin").read_bytes()
                    + old["comparison"]
                    + raw["comparison"]
                )
                require(
                    key in gates.WORKSPACES, "workspace lacks recomputed arithmetic"
                )
                if key not in captured:
                    captured[key] = {
                        "conditions": np.asarray(raw["conditions"], dtype="<f8"),
                        "Y": np.asarray(raw["Y"], dtype="<f8"),
                        "F_original": np.asarray(raw["original"], dtype="<f8"),
                        "F_variant": np.asarray(raw["variant"], dtype="<f8"),
                        "quad_bytes": {
                            name: np.frombuffer(payload, dtype=np.uint8)
                            .copy()
                            .reshape(-1, 16)
                            for name, payload in raw["quad"].items()
                        },
                    }
            except (OSError, ValueError, KeyError, TypeError) as exc:
                unavailable[relative] = str(exc)
        matrix = work / "jacobian-factor-1.bin"
        if matrix.is_file():
            values = np.frombuffer(matrix.read_bytes(), dtype="<f8")
            if values.size == 160 * 160:
                matrices[spec["name"]] = values.copy().reshape(160, 160, order="F")
            else:
                unavailable[str(matrix.relative_to(root))] = "matrix extent differs"
    return captured, matrices, unavailable


def analyze(root, host_identity_sha=None):
    root = Path(root).resolve()
    gates = load_module("_assembly_report_arithmetic", HERE / "assembly_arithmetic.py")
    gates.WORKSPACES.clear()
    contract = load_module("_assembly_report_campaign", HERE / "assembly_campaign.py")
    report = {
        "schema": "crucible.phase2d.assembly-verification.v1",
        "numerical_source": contract.SOURCE_NAME,
        "software_pass": False,
        "qualification_pass": False,
        "trajectory_reference_qualified": False,
        "scientific_accuracy_acceptance": False,
        "state_coordinate": "ordered_160_physical_Y_binary64",
        "units": {
            "Y": "molar_abundance_Y",
            "F_original": "molar_abundance_Y/s",
            "F_variant": "molar_abundance_Y/s",
            "time": "s",
            "T9": "GK",
            "rho": "g/cm^3",
        },
        "attempts": {},
        "errors": [],
        "call_counts_complete": False,
        "host_identity_verification_sha256": host_identity_sha,
        "analysis_environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "analysis_code_sha256": {
            name: contract.digest(HERE / name)
            for name in (
                "assembly_report.py",
                "assembly_arithmetic.py",
                "assembly_campaign.py",
                "assembly_host_identities.py",
            )
        },
    }
    for name, path in (
        ("trajectory_reference.py", Path(artifacts.__file__)),
        ("rhs_reference/arithmetic.py", HERE.parent / "rhs_reference/arithmetic.py"),
        ("rhs_reference/reference.py", HERE.parent / "rhs_reference/reference.py"),
    ):
        report["analysis_code_sha256"][name] = contract.digest(path)
    prepared, campaign = None, None
    try:
        prepared = json.loads((root / "prepared.json").read_text())
        for spec in prepared["attempts"]:
            report["attempts"][spec["name"]] = {
                "stage": spec["stage"],
                "state": spec["state"],
                "status": "UNDETERMINED"
                if (root / "attempts" / spec["name"]).exists()
                else "UNATTEMPTED",
                "completed": False,
                "skip_reason": "CAMPAIGN_RECORD_UNAVAILABLE",
            }
        campaign = json.loads((root / "campaign.json").read_text())
        report.update(
            protocol_sha256=prepared["protocol_sha256"],
            annex_sha256=prepared["annex_sha256"],
            source_commit=prepared["source_commit"],
            source_tree=prepared["source_tree"],
            prepared_sha256=contract.digest(root / "prepared.json"),
            campaign_sha256=contract.digest(root / "campaign.json"),
            campaign_exception=campaign.get("exception"),
            campaign_complete=campaign.get("complete"),
            build=campaign.get("build"),
        )
        require(
            len(prepared["attempts"]) == len(campaign["attempts"]) == 13,
            "thirteen planned process records required",
        )
        for spec, record in zip(
            prepared["attempts"], campaign["attempts"], strict=True
        ):
            report["attempts"][spec["name"]] = {
                "stage": spec["stage"],
                "state": spec["state"],
                "status": record.get("status", "UNKNOWN"),
                "completed": record.get("completed", False),
                "skip_reason": record.get("skip_reason"),
                "raw_files": record.get("files", {}),
            }
        contract.validate_prepared(root, prepared)
        require(
            campaign.get("schema") == "crucible.phase2d.assembly-campaign.v1"
            and campaign.get("numerical_source") == contract.SOURCE_NAME
            and campaign.get("prepared_sha256") == report["prepared_sha256"],
            "campaign/preparation binding differs",
        )
        require(
            prepared["immutable_files"].get("assembly_arithmetic.py")
            == report["analysis_code_sha256"]["assembly_arithmetic.py"],
            "offline arithmetic source differs from executed science gate",
        )
        for name in ("rhs_reference/arithmetic.py", "rhs_reference/reference.py"):
            require(
                prepared["immutable_files"].get(name)
                == report["analysis_code_sha256"][name],
                "offline arithmetic dependency differs from executed gate",
            )
        report["host_identity_verification"] = verify_retained_build(
            root, prepared, campaign, contract, host_identity_sha
        )
        for spec, record in zip(
            prepared["attempts"], campaign["attempts"], strict=True
        ):
            require(
                all(record.get(k) == v for k, v in spec.items()), "attempt plan differs"
            )
        attempts_folder = root / "attempts"
        if attempts_folder.exists():
            require(
                {p.name for p in attempts_folder.iterdir() if p.is_dir()}
                <= {s["name"] for s in prepared["attempts"]},
                "undeclared attempt directory",
            )
        report["precision"] = gates.precision_gate(root)
        outcomes, physical, requests, counts_complete = {}, 0, 0, True
        for spec, record in zip(
            prepared["attempts"], campaign["attempts"], strict=True
        ):
            output = report["attempts"][spec["name"]]
            if record.get("status") in UNATTEMPTED:
                require(
                    not (root / "attempts" / spec["name"]).exists(),
                    "unattempted record hides an execution directory",
                )
                outcomes[spec["name"]] = {"pass": False, "software_pass": True}
                continue
            function = {
                "identity": gates.identity_attempt_gate,
                "derivative": gates.derivative_attempt_gate,
                "standard": gates.first_step_gate,
                "tight": gates.first_step_gate,
            }[spec["stage"]]
            gate = function(root, spec, record)
            outcomes[spec["name"]] = gate
            output["recomputed"] = gate
            if "science_gate" in record:
                require(
                    all(
                        record["science_gate"].get(k) == gate.get(k) for k in DECISIONS
                    ),
                    "saved/recomputed science-gate decisions differ",
                )
            try:
                native = json.loads(
                    (root / "attempts" / spec["name"] / "counters.json").read_text()
                )
                scope = json.loads(
                    (
                        root / "attempts" / spec["name"] / "assembly-counters.json"
                    ).read_text()
                )
                require(
                    type(native["rhs"]) is int and type(scope["fresh_requests"]) is int,
                    "invalid counter type",
                )
                require(
                    native["rhs"] >= 0 and scope["fresh_requests"] >= native["rhs"],
                    "invalid guarded/physical counts",
                )
                physical += native["rhs"]
                requests += scope["fresh_requests"]
                output["native_counters"], output["assembly_counters"] = native, scope
            except (OSError, ValueError, KeyError, TypeError) as exc:
                counts_complete = False
                output["counter_unavailable"] = str(exc)
        report.update(
            physical_rhs_calls_observed=physical,
            fresh_requests_observed=requests,
            call_counts_complete=counts_complete,
        )
        campaign_for_checks = {**campaign, "_root": str(root)}
        report["stages"] = _stage_checks(prepared, campaign_for_checks, outcomes)
        complete = all(
            a.get("completed") is True or a.get("status") == "CONDITIONALLY_UNATTEMPTED"
            for a in campaign["attempts"]
        )
        report["software_pass"] = bool(
            complete
            and campaign.get("complete") is True
            and counts_complete
            and report["precision"]["software_pass"]
            and report["precision"]["pass"]
            and all(g.get("software_pass") is True for g in outcomes.values())
            and physical == campaign.get("physical_rhs_calls")
            and requests == campaign.get("guarded_fresh_requests")
            and physical <= requests <= contract.MAX_RHS
        )
        report["qualification_pass"] = bool(
            report["software_pass"]
            and all(g.get("pass") is True for g in outcomes.values())
        )
        require(
            campaign.get("qualification_pass") is report["qualification_pass"],
            "saved/recomputed qualification differs",
        )
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        report["errors"].append(str(exc))
        report["software_pass"] = report["qualification_pass"] = False
    if prepared is not None:
        try:
            operands, matrices, unavailable = _capture_workspaces(root, prepared, gates)
            report.update(
                workspace_arrays=operands,
                derivative_matrices=matrices,
                unavailable_numeric_details=unavailable,
            )
            require(
                not report["software_pass"] or not unavailable,
                "verified numeric workspace could not be retained",
            )
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            report["errors"].append(str(exc))
            report["software_pass"] = report["qualification_pass"] = False
    report["workspaces"] = gates.WORKSPACES
    return numeric_details(report)


def reload_report(root, report_name=REPORT):
    root = Path(root).resolve()
    saved = json.loads((root / report_name).read_text())
    manifest = saved.pop("array_artifact")
    name = Path(manifest["path"])
    require(
        not name.is_absolute() and ".." not in name.parts, "unsafe array artifact path"
    )
    payload = artifacts.checked(root / name, manifest["sha256"])
    with np.load(io.BytesIO(payload), allow_pickle=False) as file:
        require(
            set(file.files) == set(manifest["arrays"]),
            "derived array membership differs",
        )
        arrays = {key: file[key].copy() for key in file.files}
    for key, array in arrays.items():
        expected = manifest["arrays"][key]
        require(
            array.dtype.str == expected["dtype"]
            and list(array.shape) == expected["shape"]
            and artifacts.digest_bytes(array.tobytes()) == expected["sha256"],
            "derived array identity differs",
        )
    report = analyze(
        root, host_identity_sha=saved.get("host_identity_verification_sha256")
    )
    metadata, recomputed = artifacts.split_report(report)
    require(
        metadata == saved and set(arrays) == set(recomputed),
        "recomputed report differs",
    )
    for key, array in arrays.items():
        other = recomputed[key]
        require(
            array.dtype == other.dtype
            and array.shape == other.shape
            and array.tobytes() == other.tobytes(),
            "recomputed array bytes differ",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("verify", "reload"):
        child = sub.add_parser(command)
        child.add_argument("root", type=Path)
        child.add_argument("--report-name", default=REPORT)
        if command == "verify":
            child.add_argument("--host-identity-sha256", required=True)
    args = parser.parse_args()
    require(
        Path(args.report_name).name == args.report_name
        and args.report_name.endswith(".json"),
        "report name must be a JSON basename",
    )
    report = (
        analyze(args.root, args.host_identity_sha256)
        if args.command == "verify"
        else reload_report(args.root, args.report_name)
    )
    if args.command == "verify":
        artifacts.artifact_report(args.root / args.report_name, report)
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "software_pass",
                    "qualification_pass",
                    "trajectory_reference_qualified",
                )
            }
        )
    )
    if not report["software_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
