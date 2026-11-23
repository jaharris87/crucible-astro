"""Offline preparation and fixed, gated D-039 assembly qualification runner.

This module never builds a producer. Only the lead executes the reviewed native
candidate under the separately accepted producer authority. Host execution uses
stdlib-only raw-artifact science gates from assembly_arithmetic.py.
"""

import argparse
import importlib.util
import json
import os
import platform
import resource
import shutil
import struct
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Reuse the existing bounded I/O/build/process helpers, never its physical plan.

_SPEC = importlib.util.spec_from_file_location(
    "assembly_d038_io", HERE / "diagnostic_campaign.py"
)
diag = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(diag)
common = diag.common
digest, save, require = diag.digest, diag.save, diag.require
PROTOCOL_SHA256 = "ff5515f04ecfdb9cb75f284882dc88d5beef30a25d1a4a8b9e9a18ba741abf02"
SOURCE_NAME = "native-XNet-b64-productsum113-b64-v1"
MAX_RHS = 10398034
D038_SOURCE_COMMIT = "ae6971522ba1333f550664ac793be6b662e3dae4"
D038_PREPARED_SHA256 = (
    "04e67ec31da8df2ab93b2998b743ef8580f2654db70ad2489da6ba2fa4ad2ee6"
)
D038_CAMPAIGN_SHA256 = (
    "964eb4a759f1052b212351afad12d1da13bda7d96d8a78c029116b727d72c7dd"
)
D038_ARCHIVE_SHA256 = "02f2c62ade306d21f8cd5c584577fc215e1df34f646114559f5f05efcc8523bd"
BASELINE_SHA256 = {
    "development-initial": "f1f0d291fd32e12d3c3a58cd19865ef5e204b0f71c727056e2b3a82da5c371f4",
    "validation-initial": "64040f3583668ad36218b836af31eececba18df9fdc5e6afef5956dbd9b3a823",
    "development-newton300": "a45462c0464028015aadaf290ab6564d92ab6cebfc4d623a3e6ebbc3507d253d",
}
STANDARD_SHA256 = {
    "development": "e01360c67159d80c23dd6820851ace68a7cf3375158b7ce29e705117397eb4ae",
    "validation": "6df2cb7df8464994a5e7997825a4cd3393b47bcbc10fc435af855c5908cce1fe",
}
TIGHT_SHA256 = {
    "development": "316cc070cb8db199ee1a8318c2d5c18024dff13631252f4af99645f2f844894e",
    "validation": "27ed0768df74810e51f59b4be7bfcc0cadad8745eb221d5ab11b11e147a60aae",
}
HOST_FILES = ("assembly_campaign.py", "assembly_arithmetic.py")


def fixed_plan(states, first_step_inputs):
    require(
        [s["name"] for s in states] == list(diag.STATES),
        "fixed assembly state population differs",
    )
    require(
        set(first_step_inputs) == set(STANDARD_SHA256),
        "first-step case population differs",
    )
    plans = []
    for suffix, stage, command in (
        ("identity-3", "identity", "assembly-repeat-3"),
        ("identity-1", "identity", "assembly-repeat-1"),
        ("derivative", "derivative", "assembly-diagnose"),
    ):
        for state in states:
            plans.append(
                {
                    "name": state["name"] + "-" + suffix,
                    "state": state["name"],
                    "stage": stage,
                    "arguments": [command],
                    "mode": 0,
                    "input": state["input"],
                    "input_sha256": state["input_sha256"],
                    "companions": {},
                }
            )
    for stage in ("standard", "tight"):
        for case in STANDARD_SHA256:
            entry = first_step_inputs[case][stage]
            plans.append(
                {
                    "name": case + "-" + stage,
                    "state": case + "-initial",
                    "stage": stage,
                    "arguments": ["assembly-step"],
                    "mode": 1,
                    "input": entry["path"],
                    "input_sha256": entry["sha256"],
                    "companions": {},
                }
            )
    return plans


def tight_input(standard):
    """Derive only the predeclared two-control change; preserve all other bytes."""
    require(len(standard) >= 48, "truncated standard L0 input")
    require(
        struct.unpack_from("<2d", standard, 32) == (1e-13, 1e-11),
        "standard nonlinear controls differ",
    )
    return standard[:32] + struct.pack("<2d", 1e-14, 1e-12) + standard[48:]


def copy_checked(source, destination, identity):
    require(
        digest(source) == identity, "source artifact identity differs: " + str(source)
    )
    payload = Path(source).read_bytes()
    require(diag.sha(payload) == identity, "source artifact changed during copy")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {"path": str(destination), "sha256": identity}


def prepare(config_path, diagnostic_annex, destination, source_root):
    """Stage exact accepted inputs/original controls and a separately named plan."""
    import numpy as np

    from crucible import trajectory_reference as ref

    start = time.perf_counter()
    source_root, destination = Path(source_root).resolve(), Path(destination).resolve()
    config = json.loads(Path(config_path).read_text())
    require(
        set(config)
        == {"trajectory_prepare_config", "diagnostic_root", "standard_inputs"}
        and set(config["standard_inputs"]) == set(STANDARD_SHA256),
        "assembly preparation config fields differ",
    )
    require(
        Path(__file__).read_bytes()
        == (
            source_root / "experiments/trajectory_reference/assembly_campaign.py"
        ).read_bytes(),
        "running assembly preparation source differs",
    )
    require(
        digest(
            source_root
            / "experiments/trajectory_reference/ASSEMBLY_QUALIFICATION_PROTOCOL.md"
        )
        == PROTOCOL_SHA256,
        "assembly protocol identity differs",
    )
    previous_root = Path(config["diagnostic_root"]).resolve()
    require(
        digest(previous_root / "prepared.json") == D038_PREPARED_SHA256
        and digest(previous_root / "campaign.json") == D038_CAMPAIGN_SHA256,
        "accepted D-038 source receipts differ",
    )
    old_prepared = json.loads((previous_root / "prepared.json").read_text())
    old_campaign = json.loads((previous_root / "campaign.json").read_text())
    require(
        old_prepared["source_commit"] == D038_SOURCE_COMMIT
        and old_campaign["complete"]
        and old_campaign["stage_a_pass"],
        "D-038 source/completeness differs",
    )
    archive = previous_root.parent.parent / "d038-final-001.tar.gz"
    if archive.exists():
        require(
            digest(archive) == D038_ARCHIVE_SHA256,
            "available D-038 archive identity differs",
        )
    # This helper verifies qualified Y/species/D-019 F and exact frozen wire bytes;
    # its old nine-process plan is retained as an unused offline history receipt.
    prepared = diag.prepare(
        config["trajectory_prepare_config"], diagnostic_annex, destination, source_root
    )
    history = destination / "preparation-history/diagnostic-input-preparation.json"
    history.parent.mkdir()
    (destination / "prepared.json").replace(history)
    references, controls = {}, {}
    old_attempts = {a["name"]: a for a in old_campaign["attempts"]}
    for state in diag.STATES:
        old_name = state + "-repeat-3"
        references[state] = {
            "path": "reference-baselines/" + state + "/baseline-001.bin",
            "sha256": BASELINE_SHA256[state],
        }
        copy_checked(
            previous_root / "attempts" / old_name / "baseline-001.bin",
            destination / references[state]["path"],
            BASELINE_SHA256[state],
        )
        controls[state] = {}
        for name in ("used-maps.bin", "species.bin", "diagnostic-ieee.bin"):
            identity = old_attempts[old_name]["files"][name]["sha256"]
            target = "reference-baselines/" + state + "/" + name
            copy_checked(
                previous_root / "attempts" / old_name / name,
                destination / target,
                identity,
            )
            controls[state][name] = {"path": target, "sha256": identity}
    for name, identity in (
        ("prepared.json", D038_PREPARED_SHA256),
        ("campaign.json", D038_CAMPAIGN_SHA256),
    ):
        copy_checked(
            previous_root / name, destination / "reference-records" / name, identity
        )
    first_step_inputs = {}
    for case, identity in STANDARD_SHA256.items():
        raw = Path(config["standard_inputs"][case]).read_bytes()
        require(
            diag.sha(raw) == identity, "original standard L0 input identity differs"
        )
        with np.load(
            destination / "inputs" / (case + ".npz"), allow_pickle=False
        ) as file:
            original_case = ref.validate_case({k: file[k].copy() for k in file.files})
        require(
            raw
            == ref.wire_input(
                original_case, mode=1, mesh=ref.nested_mesh(original_case, 0)
            ),
            "standard L0 wire differs from qualified case",
        )
        tight = tight_input(raw)
        require(
            diag.sha(tight) == TIGHT_SHA256[case],
            "predeclared tight L0 identity differs",
        )
        first_step_inputs[case] = {}
        for stage, payload, expected in (
            ("standard", raw, identity),
            ("tight", tight, TIGHT_SHA256[case]),
        ):
            name = "inputs/" + case + "-" + stage + "-L0.bin"
            (destination / name).write_bytes(payload)
            first_step_inputs[case][stage] = {"path": name, "sha256": expected}
    public = source_root / "experiments/trajectory_reference"
    for name in (*HOST_FILES, "ASSEMBLY_QUALIFICATION_PROTOCOL.md"):
        shutil.copy2(public / name, destination / name)
    for name in ("arithmetic.py", "reference.py"):
        target = destination / "rhs_reference" / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(public.parent / "rhs_reference" / name, target)
    prepared.update(
        schema="crucible.phase2d.assembly-prepared.v1",
        numerical_source=SOURCE_NAME,
        protocol_sha256=PROTOCOL_SHA256,
        diagnostic_protocol_sha256=diag.PROTOCOL_SHA256,
        reference_baselines=references,
        reference_controls=controls,
        first_step_inputs=first_step_inputs,
        attempts=fixed_plan(prepared["states"], first_step_inputs),
        input_preparation_history={
            "path": str(history.relative_to(destination)),
            "sha256": digest(history),
            "status": "OFFLINE_HELPER_ONLY_NINE_PLANS_NOT_EXECUTED",
        },
        diagnostic_source={
            "source_commit": D038_SOURCE_COMMIT,
            "prepared_sha256": D038_PREPARED_SHA256,
            "campaign_sha256": D038_CAMPAIGN_SHA256,
            "raw_archive_sha256": D038_ARCHIVE_SHA256,
            "archive_checked": archive.exists(),
        },
    )
    prepared["immutable_files"] = {
        str(p.relative_to(destination)): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    prepared["costs"]["assembly_prepare_total_wall_seconds"] = (
        time.perf_counter() - start
    )
    save(destination / "prepared.json", prepared)
    return prepared


def validate_prepared(root, prepared):
    require(
        prepared.get("schema") == "crucible.phase2d.assembly-prepared.v1"
        and prepared.get("protocol_sha256") == PROTOCOL_SHA256
        and prepared.get("numerical_source") == SOURCE_NAME,
        "assembly preparation identity differs",
    )
    require(
        prepared.get("annex_sha256") == diag.ANNEX_SHA256
        and prepared.get("diagnostic_protocol_sha256") == diag.PROTOCOL_SHA256,
        "diagnostic input/protocol metadata differs",
    )
    source_record = prepared.get("diagnostic_source", {})
    require(
        set(source_record)
        == {
            "source_commit",
            "prepared_sha256",
            "campaign_sha256",
            "raw_archive_sha256",
            "archive_checked",
        }
        and source_record["source_commit"] == D038_SOURCE_COMMIT
        and source_record["prepared_sha256"] == D038_PREPARED_SHA256
        and source_record["campaign_sha256"] == D038_CAMPAIGN_SHA256
        and source_record["raw_archive_sha256"] == D038_ARCHIVE_SHA256
        and type(source_record["archive_checked"]) is bool,
        "D-038 source metadata differs",
    )
    diag.validate_prepared(root, prepared)
    require(
        digest(root / "ASSEMBLY_QUALIFICATION_PROTOCOL.md") == PROTOCOL_SHA256,
        "assembly protocol bytes differ",
    )
    require(
        prepared["attempts"]
        == fixed_plan(prepared["states"], prepared["first_step_inputs"]),
        "fixed thirteen-process plan differs",
    )
    for name, identity in prepared["immutable_files"].items():
        require(
            digest(diag.safe_file(root, name)) == identity,
            "immutable assembly source/input differs",
        )
    for name, actual in (
        ("assembly_campaign.py", Path(__file__)),
        ("diagnostic_campaign.py", Path(diag.__file__)),
        ("campaign.py", Path(common.__file__)),
    ):
        require(
            prepared["immutable_files"].get(name) == digest(actual),
            "running host script identity differs",
        )
    require(
        digest(root / "reference-records/prepared.json") == D038_PREPARED_SHA256
        and digest(root / "reference-records/campaign.json") == D038_CAMPAIGN_SHA256,
        "retained D-038 source receipts differ",
    )
    original = json.loads((root / "reference-records/campaign.json").read_text())
    original_prepared = json.loads(
        (root / "reference-records/prepared.json").read_text()
    )
    require(
        original_prepared["source_commit"] == D038_SOURCE_COMMIT
        and original["complete"]
        and original["stage_a_pass"],
        "retained D-038 qualification context differs",
    )
    original_attempts = {a["name"]: a for a in original["attempts"]}
    for state, identity in BASELINE_SHA256.items():
        for name in ("used-maps.bin", "species.bin", "diagnostic-ieee.bin"):
            control = prepared["reference_controls"][state][name]
            expected = {
                "path": "reference-baselines/" + state + "/" + name,
                "sha256": original_attempts[state + "-repeat-3"]["files"][name][
                    "sha256"
                ],
            }
            require(
                control == expected
                and digest(root / control["path"]) == control["sha256"],
                "retained D-038 control binding differs",
            )
        entry = prepared["reference_baselines"][state]
        require(
            entry
            == {
                "path": "reference-baselines/" + state + "/baseline-001.bin",
                "sha256": identity,
            },
            "retained D-038 baseline binding differs",
        )
        require(
            digest(root / entry["path"]) == identity,
            "retained D-038 baseline bytes differ",
        )
    for case, identity in STANDARD_SHA256.items():
        standard, tight = (
            prepared["first_step_inputs"][case]["standard"],
            prepared["first_step_inputs"][case]["tight"],
        )
        require(
            standard
            == {"path": "inputs/" + case + "-standard-L0.bin", "sha256": identity}
            and tight
            == {
                "path": "inputs/" + case + "-tight-L0.bin",
                "sha256": TIGHT_SHA256[case],
            },
            "first-step input bindings differ",
        )
        require(
            digest(root / standard["path"]) == identity
            and digest(root / tight["path"]) == TIGHT_SHA256[case],
            "first-step input bytes differ",
        )
        require(
            (root / tight["path"]).read_bytes()
            == tight_input((root / standard["path"]).read_bytes()),
            "tight input changed bytes outside controls",
        )
    for name in (
        *HOST_FILES,
        "rhs_reference/arithmetic.py",
        "rhs_reference/reference.py",
    ):
        require(
            name in prepared["immutable_files"],
            "science-gate dependency absent from immutable manifest",
        )


def build_identities(root):
    result = diag.build_identities(root)
    executable = root / "bundle/assembly_synthetic"
    receipt = (root / "bundle/assembly-executable.sha256").read_text().split()
    require(
        len(receipt) == 2
        and Path(receipt[1]).name == "assembly_synthetic"
        and receipt[0] == digest(executable),
        "precision fixture executable identity differs",
    )
    result["executables"]["assembly_synthetic"] = receipt[0]
    return result


def synthetic_checks(root):
    extra = (("trajectory_synthetic", "retry-snapshot", None),) + tuple(
        ("assembly_synthetic", name, None)
        for name in ("precision", "arithmetic", "malformed", "nonfinite", "overflow")
    )
    return common.synthetic_checks(root, extra_scenarios=extra)


def science_gates(root):
    return diag.load_module(
        "assembly_host_science_gates", root / "assembly_arithmetic.py"
    )


def check_identity(root, prepared, spec, result, baselines):
    """Reuse D-038 structural/original-F gates, then compare accepted raw bits."""
    command = "repeat-3" if spec["arguments"] == ["assembly-repeat-3"] else "repeat-1"
    baseline, counts = diag.check_process(
        root,
        {**spec, "arguments": [command]},
        result,
        baseline=baselines.get(spec["state"]),
    )
    entry = prepared["reference_baselines"][spec["state"]]
    expected = diag.parse_baseline((root / entry["path"]).read_bytes())
    require(
        baseline[0] == expected["comparison_bytes"],
        "original frozen workspace differs from accepted D-038 bits",
    )
    for name in ("used-maps.bin", "species.bin"):
        reference = prepared["reference_controls"][spec["state"]][name]
        require(
            (root / "attempts" / spec["name"] / name).read_bytes()
            == (root / reference["path"]).read_bytes(),
            "original static control differs from D-038",
        )
    ieee_reference = prepared["reference_controls"][spec["state"]][
        "diagnostic-ieee.bin"
    ]
    modes = diag.ieee_rows((root / ieee_reference["path"]).read_bytes())[0][1:6]
    require(baseline[3] == modes, "original IEEE modes differ from D-038")
    baselines.setdefault(spec["state"], baseline)
    return counts


def skip(manifest, stage, reason):
    for attempt in manifest["attempts"]:
        if attempt["stage"] == stage and attempt["status"] == "UNATTEMPTED":
            attempt.update(status="CONDITIONALLY_UNATTEMPTED", skip_reason=reason)


def execute(root, *, srun=False):
    """Execute fixed stages once; raw science gates decide every transition."""
    root = Path(root).resolve()
    prepared = json.loads((root / "prepared.json").read_text())
    validate_prepared(root, prepared)
    path = root / "campaign.json"
    require(
        not path.exists() and not (root / "attempts").exists(),
        "no assembly restart/repetition authorized",
    )
    manifest = {
        "schema": "crucible.phase2d.assembly-campaign.v1",
        "numerical_source": SOURCE_NAME,
        "prepared_sha256": digest(root / "prepared.json"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "threads": {
            k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "attempts": [
            {**s, "status": "UNATTEMPTED", "completed": False}
            for s in prepared["attempts"]
        ],
        "complete": False,
        "qualification_pass": False,
        "physical_rhs_calls": 0,
        "guarded_fresh_requests": 0,
        "call_accounting_complete": False,
        "gates": {},
    }
    started = time.perf_counter()
    save(path, manifest)
    try:
        require(
            all(
                os.environ.get(k) == "1" for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")
            ),
            "one-thread environment required",
        )
        build = build_identities(root)
        manifest["build"] = build
        save(path, manifest)
        # A cached old eleven-fixture receipt cannot satisfy this exact population.
        manifest["synthetic"] = synthetic_checks(root)
        save(path, manifest)
        gates = science_gates(root)
        precision = gates.precision_gate(root)
        manifest["gates"]["precision"] = precision
        save(path, manifest)
        require(precision["pass"], "independent precision/conversion gate failed")
        launcher = ["srun", "-n", "1", "-c", "1"] if srun else []
        baselines = {}
        for i, spec in enumerate(prepared["attempts"]):
            if spec["stage"] == "standard" and i == 9:
                gate = gates.derivative_gate(root)
                manifest["gates"]["derivative"] = gate
                save(path, manifest)
                require(
                    gate["software_pass"], "derivative software/forensic gate failed"
                )
                if not gate["pass"]:
                    skip(manifest, "standard", "DERIVATIVE_GATES_FAILED")
                    skip(manifest, "tight", "DERIVATIVE_GATES_FAILED")
                    break
            if spec["stage"] == "tight" and i == 11:
                standards = [
                    a for a in manifest["attempts"] if a["stage"] == "standard"
                ]
                if not all(a.get("qualification_pass") for a in standards):
                    skip(manifest, "tight", "BOTH_STANDARD_ATTEMPTS_DID_NOT_PASS")
                    break
            require(
                digest(root / "prepared.json") == manifest["prepared_sha256"],
                "prepared record changed during campaign",
            )
            for name, identity in prepared["immutable_files"].items():
                require(
                    digest(diag.safe_file(root, name)) == identity,
                    "immutable source/input changed during campaign",
                )
            require(
                build_identities(root) == build,
                "build/library identity changed during campaign",
            )
            manifest["attempts"][i]["status"] = "STARTING"
            save(path, manifest)
            result = common.run_attempt(
                root,
                spec,
                root / "bundle/trajectory_driver",
                launcher,
                resume=False,
                arguments=tuple(spec["arguments"]),
            )
            attempt = manifest["attempts"][i] = {**spec, **result}
            save(path, manifest)
            work = root / "attempts" / spec["name"]
            counts_path = work / "counters.json"
            if counts_path.exists():
                counts = json.loads(counts_path.read_text())
                attempt["native_counters"] = counts
                if type(counts.get("rhs")) is int and counts["rhs"] >= 0:
                    manifest["physical_rhs_calls"] += counts["rhs"]
            assembly_counts_path = work / "assembly-counters.json"
            require(
                assembly_counts_path.is_file(),
                "guarded fresh-request accounting missing",
            )
            assembly_counts = json.loads(assembly_counts_path.read_text())
            attempt["assembly_counters"] = assembly_counts
            require(
                set(assembly_counts)
                == {"schema", "fresh_requests", "rhs", "assembly_calls"}
                and assembly_counts["schema"] == "crucible.assembly-counters.v1"
                and all(
                    type(assembly_counts[k]) is int and assembly_counts[k] >= 0
                    for k in ("fresh_requests", "rhs", "assembly_calls")
                ),
                "invalid assembly request counters",
            )
            require(
                assembly_counts["rhs"] == attempt.get("native_counters", {}).get("rhs")
                and assembly_counts["fresh_requests"] >= assembly_counts["rhs"],
                "guarded/kernel call counters disagree",
            )
            manifest["guarded_fresh_requests"] += assembly_counts["fresh_requests"]
            save(path, manifest)
            require(
                manifest["guarded_fresh_requests"] <= MAX_RHS,
                "qualification guarded-request scope exceeded",
            )
            if spec["stage"] == "identity":
                check_identity(root, prepared, spec, result, baselines)
                gate = gates.identity_attempt_gate(root, spec, result)
                attempt["science_gate"] = gate
                save(path, manifest)
                require(
                    gate["software_pass"] and gate["pass"] and not gate["fatal"],
                    "identity/arithmetic attempt gate failed",
                )
                if i == 5:
                    gate = gates.identity_gate(root)
                    manifest["gates"]["identity"] = gate
                    save(path, manifest)
                    require(
                        gate["software_pass"] and gate["pass"],
                        "identity/arithmetic qualification gate failed",
                    )
            elif spec["stage"] == "derivative":
                status = (work / "status.txt").read_text().splitlines()[-1:]
                require(
                    result.get("returncode") == 0 and status == ["SUCCESS"],
                    "derivative native fatal failure",
                )
                gate = gates.derivative_attempt_gate(root, spec, result)
                attempt["science_gate"] = gate
                save(path, manifest)
                require(
                    gate["software_pass"] and not gate["fatal"],
                    "derivative shared/forensic/nonfinite gate failed",
                )
                # Ordinary directional-window failures remain raw outcomes; all
                # three states run before the aggregate science gate above.
            else:
                gate = gates.first_step_gate(root, spec, result)
                attempt["science_gate"] = gate
                attempt["qualification_pass"] = gate["pass"]
                save(path, manifest)
                require(
                    gate["software_pass"] and not gate["fatal"],
                    "first-step shared/forensic/nonfinite failure",
                )
                require(
                    gate["pass"] or gate["ordinary_numerical_failure"],
                    "unclassified first-step failure",
                )
            attempt["validation_completed"] = True
            save(path, manifest)
        manifest["complete"] = all(
            a["completed"] or a["status"] == "CONDITIONALLY_UNATTEMPTED"
            for a in manifest["attempts"]
        )
        manifest["call_accounting_complete"] = manifest["complete"]
        manifest["qualification_pass"] = (
            manifest["complete"]
            and all(
                manifest["gates"].get(stage, {}).get("pass")
                for stage in ("precision", "identity", "derivative")
            )
            and all(
                a.get("qualification_pass")
                for a in manifest["attempts"]
                if a["stage"] in ("standard", "tight")
            )
        )
    except BaseException as exc:
        manifest["exception"] = repr(exc)
        for item in manifest["attempts"]:
            if item["status"] == "STARTING":
                record_path = root / "attempts" / item["name"] / "attempt.json"
                if record_path.exists():
                    record = json.loads(record_path.read_text())
                    if not record.get("completed"):
                        record["status"] = "INTERRUPTED"
                        record["files"] = common.snapshot(record_path.parent)
                        save(record_path, record)
                    item.update(record)
                else:
                    item["status"] = "INTERRUPTED_BEFORE_LAUNCH"
                    if record_path.parent.exists():
                        item["files"] = common.snapshot(record_path.parent)
        raise
    finally:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        manifest["wall_seconds_this_process"] = time.perf_counter() - started
        manifest["children_cpu_seconds"] = usage.ru_utime + usage.ru_stime
        manifest["children_peak_rss_bytes"] = usage.ru_maxrss * (
            1024 if platform.system() == "Linux" else 1
        )
        manifest["artifact_bytes"] = sum(
            p.stat().st_size
            for p in root.rglob("*")
            if p.is_file() and not p.is_symlink()
        )
        save(path, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    for name in ("config", "annex", "destination"):
        prep.add_argument(name, type=Path)
    prep.add_argument("--source-root", type=Path, default=Path.cwd())
    run = sub.add_parser("execute")
    run.add_argument("root", type=Path)
    run.add_argument("--srun", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.config, args.annex, args.destination, args.source_root)
    else:
        execute(args.root, srun=args.srun)


if __name__ == "__main__":
    main()
