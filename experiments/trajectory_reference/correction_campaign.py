"""Offline D-040 preparation and the fixed conditional twenty-process host plan.

No command in this module compiles a producer. Preparation imports only offline
loaders. Execution requires the separately reviewed candidate and accepted D-040
producer authority, and calls the native executable only through the fixed plan.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import resource
import shutil
import struct
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL_SHA256 = "a7eac47716dc710780469b4f107adec59e3fd6e60d435cd62ef60560f13be0a8"
SOURCE_NAME = "native-XNet-b64-productsum113-b64-v1"
D039_SOURCE = "245ed9525ee9877653beab80eaf91bdd5493800c"
D039_PREPARED = "466ed27595039ed142a2d653d6ba8a470994942136985c3214f5626b10b175ed"
D039_CAMPAIGN = "690b39f184938a7e7026f80a6197964f6541ed818de908828bd63ab5d014685f"
ANNEX_SHA256 = "697049acca510794eda3149a2d88a11477f49e4724519cb3ba4fef22e7cdb3b1"
INPUT_SHA256 = {
    "development": "b02862988b83b7412a8a53d40868adf5f6b04cf7eca7798b7bebf6789fc31da6",
    "validation": "bc70b3c75bdb8a5046a310de3a13b125a991fcaf165f70631ce79bf5875a9bb9",
}
CASES = ("development", "validation")
CONTROLS = {"standard": (1e-15, 1e-13), "tight": (1e-16, 1e-14)}
TRAJECTORY_STAGES = (
    "L0-standard",
    "L0-tight",
    "L1-standard",
    "L2-standard",
    "L3-standard",
    "L3-tight",
)
STAGES = ("control", *TRAJECTORY_STAGES, "derivative")
REFERENCE_FILES = (
    "baseline-001.bin",
    "assembly-baseline-001.bin",
    "species.bin",
    "used-maps.bin",
    "diagnostic-ieee.bin",
    "assembly-kind.bin",
)
HOST_FILES = (
    "correction_campaign.py",
    "correction_checks.py",
    "correction_report.py",
    "correction_host_identities.py",
    "campaign.py",
    "diagnostic_campaign.py",
    "assembly_campaign.py",
    "assembly_arithmetic.py",
    "assembly_host_identities.py",
)
NATIVE_ADDITIONS = ("CORRECTION_PROTOCOL.md", "CORRECTION_WIRE.md")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


common = load_module("correction_common_io", HERE / "campaign.py")
diag = load_module("correction_diagnostic_io", HERE / "diagnostic_campaign.py")
digest, save = common.digest, common.save


def require(condition, message):
    if not condition:
        raise ValueError("correction campaign: " + message)


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def safe_file(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe artifact path")
    require(not (root / path).is_symlink(), "symlinked immutable artifact")
    return root / path


def correction_input(raw, control="standard"):
    """Change only the two predeclared controls in a validated old wire input."""
    require(len(raw) >= 48 and control in CONTROLS, "invalid control/input")
    require(
        struct.unpack_from("<3i", raw) == (0x43524432, 1, 160), "wire header differs"
    )
    return raw[:32] + struct.pack("<2d", *CONTROLS[control]) + raw[48:]


def fixed_plan(inputs):
    plans = []
    for stage in STAGES[:-1]:
        for case in CASES:
            entry = inputs[case][stage]
            trajectory = stage != "control"
            level, control = (
                (int(stage[1]), stage[3:]) if trajectory else (0, "standard")
            )
            plans.append(
                {
                    "name": case + "-" + stage,
                    "case": case,
                    "state": case + "-initial",
                    "stage": stage,
                    "arguments": [
                        "correction-trajectory" if trajectory else "correction-control"
                    ],
                    "mode": int(trajectory),
                    "level": level,
                    "control": control,
                    "time": 0.0,
                    "input": entry["path"],
                    "input_sha256": entry["sha256"],
                    "companions": {},
                }
            )
    for case in CASES:
        for suffix, when in (("J0", 0.0), ("J5", 0.005), ("J10", 0.01)):
            name = case + "-" + suffix
            entry = inputs[case]["control"]
            spec = {
                "name": name,
                "case": case,
                "state": case + "-" + suffix,
                "stage": "derivative",
                "arguments": ["correction-diagnose"],
                "mode": 0,
                "level": 3,
                "control": "standard",
                "time": when,
                "input": entry["path"]
                if when == 0
                else "derived-inputs/" + name + "/input.bin",
                "companions": {},
            }
            if when == 0:
                spec["input_sha256"] = entry["sha256"]
            else:
                spec["derived_from"] = {"attempt": case + "-L3-standard", "time": when}
            plans.append(spec)
    return plans


def copy_checked(source, destination, identity):
    payload = Path(source).read_bytes()
    require(sha(payload) == identity, "retained input/source identity differs")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(payload)
    destination.chmod(0o444)
    return {"path": str(destination), "sha256": identity}


def prepare(
    config_path,
    destination,
    source_root,
    *,
    build_label="A",
    build_a=None,
    build_a_verification=None,
    build_a_verification_sha=None,
):
    """Load qualified inputs, retain original bindings and stage committed sources."""
    import numpy as np

    from crucible import trajectory_reference as ref

    started = time.perf_counter()
    destination, source_root = Path(destination).resolve(), Path(source_root).resolve()
    config = json.loads(Path(config_path).read_text())
    require(
        set(config) == {"trajectory_prepare_config", "assembly_root"},
        "prepare config fields differ",
    )
    require(
        build_label in ("A", "B")
        and ((build_a is not None) == (build_label == "B"))
        and ((build_a_verification is not None) == (build_label == "B"))
        and ((build_a_verification_sha is not None) == (build_label == "B")),
        "build label/predecessor differs",
    )
    require(not destination.exists(), "new preparation destination required")
    public = source_root / "experiments/trajectory_reference"
    require(
        (public / "correction_campaign.py").read_bytes() == Path(__file__).read_bytes(),
        "running preparation source differs",
    )
    require(
        digest(public / "CORRECTION_PROTOCOL.md") == PROTOCOL_SHA256,
        "accepted protocol differs",
    )
    old_root = Path(config["assembly_root"]).resolve()
    require(
        digest(old_root / "prepared.json") == D039_PREPARED
        and digest(old_root / "campaign.json") == D039_CAMPAIGN,
        "accepted D-039 receipts differ",
    )
    old_prepared = json.loads((old_root / "prepared.json").read_text())
    old_campaign = json.loads((old_root / "campaign.json").read_text())
    require(
        old_prepared["source_commit"] == D039_SOURCE
        and old_campaign["complete"] is True,
        "D-039 source/accounting differs",
    )
    # This reused helper performs the qualified-loader check and original staging,
    # but its historical physical plan is never executed by this module.
    prepared = ref.prepare(
        config["trajectory_prepare_config"], destination, source_root
    )
    history = destination / "preparation-history/original-prepared.json"
    history.parent.mkdir()
    (destination / "prepared.json").replace(history)
    original_config = json.loads(Path(config["trajectory_prepare_config"]).read_text())
    copy_checked(
        original_config["annex"], destination / "original-annex.json", ref.ANNEX_SHA256
    )
    for name, identity in (
        ("prepared.json", D039_PREPARED),
        ("campaign.json", D039_CAMPAIGN),
    ):
        copy_checked(
            old_root / name,
            destination / "reference-records" / ("d039-" + name),
            identity,
        )
    old_attempts = {a["name"]: a for a in old_campaign["attempts"]}
    references, inputs = {}, {}
    original_specs = {a["name"]: a for a in prepared["attempts"]}
    for case in CASES:
        state = case + "-initial"
        attempt = old_attempts[state + "-identity-3"]
        references[state] = {}
        for name in REFERENCE_FILES:
            identity = attempt["files"][name]["sha256"]
            relative = "reference-baselines/" + state + "/" + name
            copy_checked(
                old_root / "attempts" / attempt["name"] / name,
                destination / relative,
                identity,
            )
            references[state][name] = {"path": relative, "sha256": identity}
        with np.load(
            destination / "inputs" / (case + ".npz"), allow_pickle=False
        ) as file:
            arrays = ref.validate_case({k: file[k].copy() for k in file.files})
        inputs[case] = {}
        for stage in STAGES[:-1]:
            trajectory = stage != "control"
            level, control = (
                (int(stage[1]), stage[3:]) if trajectory else (0, "standard")
            )
            base_name = case + ("-L" + str(level) if trajectory else "-control")
            base = (destination / original_specs[base_name]["input"]).read_bytes()
            expected = ref.wire_input(
                arrays,
                mode=int(trajectory),
                mesh=ref.nested_mesh(arrays, level) if trajectory else np.array([0.0]),
            )
            require(base == expected, "original wire serialization differs")
            payload = correction_input(base, control)
            relative = "inputs/correction/" + case + "-" + stage + ".bin"
            target = destination / relative
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(payload)
            inputs[case][stage] = {"path": relative, "sha256": sha(payload)}
    for name in (
        *HOST_FILES,
        "CORRECTION_PROTOCOL.md",
        "CORRECTION_WIRE.md",
        "CORRECTION.md",
    ):
        shutil.copy2(public / name, destination / name)
    for name in ("arithmetic.py", "reference.py"):
        target = destination / "rhs_reference" / name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(public.parent / "rhs_reference" / name, target)
    # Keep original sources read-only, adaptations separate; extend the existing
    # manifest with only this predeclared D-040 addition population.
    native_manifest_path = destination / "bundle/source-manifest.json"
    native_manifest = json.loads(native_manifest_path.read_text())
    for name in NATIVE_ADDITIONS:
        target = destination / "bundle" / name
        require(
            not target.exists() or target.read_bytes() == (public / name).read_bytes(),
            "staged correction source collision",
        )
        target.write_bytes((public / name).read_bytes())
        native_manifest["files"][name] = {
            "bytes": target.stat().st_size,
            "sha256": digest(target),
        }
    save(native_manifest_path, native_manifest)
    source_diff = subprocess.run(
        [
            "git",
            "diff",
            "--binary",
            D039_SOURCE,
            "HEAD",
            "--",
            "experiments/trajectory_reference",
            "src/crucible/trajectory_reference.py",
        ],
        cwd=source_root,
        check=True,
        capture_output=True,
    ).stdout
    (destination / "source-diff-from-d039.patch").write_bytes(source_diff)
    prepared.update(
        schema="crucible.phase2d.correction-prepared.v1",
        protocol_sha256=PROTOCOL_SHA256,
        numerical_source=SOURCE_NAME,
        build_label=build_label,
        original_protocol_sha256=ref.PROTOCOL_SHA256,
        original_annex_sha256=ref.ANNEX_SHA256,
        retained_assembly={
            "source_commit": D039_SOURCE,
            "prepared_sha256": D039_PREPARED,
            "campaign_sha256": D039_CAMPAIGN,
        },
        reference_baselines=references,
        inputs=inputs,
        attempts=fixed_plan(inputs),
        input_preparation_history={
            "path": str(history.relative_to(destination)),
            "sha256": digest(history),
            "status": "OFFLINE_HELPER_ONLY_OLD_PLAN_NOT_EXECUTED",
        },
        source_predecessor=D039_SOURCE,
        source_diff={"path": "source-diff-from-d039.patch", "sha256": sha(source_diff)},
        authority={
            "decision": "D-040",
            "receipt": "https://github.com/jaharris87/crucible-astro/issues/44#issuecomment-7140960473",
            "implementation_review_required_before_build": True,
        },
    )
    if build_a is not None:
        aroot = Path(build_a).resolve()
        aprep = json.loads((aroot / "prepared.json").read_text())
        require(
            aprep["build_label"] == "A"
            and aprep["source_commit"] == prepared["source_commit"]
            and aprep["source_tree"] == prepared["source_tree"],
            "Build B source differs from A",
        )
        proof = json.loads(Path(build_a_verification).read_text())
        require(
            digest(build_a_verification) == build_a_verification_sha,
            "Build A release receipt identity differs",
        )
        expected = {
            "schema": "crucible.correction.verification.v1",
            "qualification_pass": True,
            "prepared_sha256": digest(aroot / "prepared.json"),
            "campaign_sha256": digest(aroot / "campaign.json"),
            "source_commit": prepared["source_commit"],
            "source_tree": prepared["source_tree"],
            "protocol_sha256": PROTOCOL_SHA256,
            "build_label": "A",
            "artifact_identity_pass": True,
            "reload_pass": True,
        }
        require(
            all(proof.get(k) == v for k, v in expected.items()),
            "Build A verification does not release Build B",
        )
        target = destination / "reference-records/build-a-verification.json"
        copy_checked(build_a_verification, target, build_a_verification_sha)
        for name in ("prepared.json", "campaign.json"):
            copy_checked(
                aroot / name,
                destination / "reference-records" / ("build-a-" + name),
                digest(aroot / name),
            )
        prepared["build_a"] = {
            "root": str(aroot),
            "prepared_sha256": digest(aroot / "prepared.json"),
            "campaign_sha256": digest(aroot / "campaign.json"),
            "verification": {
                "path": str(target.relative_to(destination)),
                "sha256": build_a_verification_sha,
            },
        }
    prepared["immutable_files"] = {
        str(p.relative_to(destination)): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    prepared["costs"]["correction_prepare_total_wall_seconds"] = (
        time.perf_counter() - started
    )
    for name in prepared["immutable_files"]:
        (destination / name).chmod(0o444)
    save(destination / "prepared.json", prepared)
    (destination / "prepared.json").chmod(0o444)
    return prepared


def validate_prepared(root, prepared):
    """Pure byte checks, usable on analysis hosts without vendor library access."""
    require(
        prepared.get("schema") == "crucible.phase2d.correction-prepared.v1"
        and prepared.get("protocol_sha256") == PROTOCOL_SHA256
        and prepared.get("numerical_source") == SOURCE_NAME,
        "preparation identity differs",
    )
    require(prepared.get("build_label") in ("A", "B"), "build identity differs")
    require(
        prepared["attempts"] == fixed_plan(prepared["inputs"]),
        "fixed twenty-process plan differs",
    )
    require(
        prepared["retained_assembly"]
        == {
            "source_commit": D039_SOURCE,
            "prepared_sha256": D039_PREPARED,
            "campaign_sha256": D039_CAMPAIGN,
        },
        "retained D-039 context differs",
    )
    require(
        prepared.get("original_annex_sha256") == ANNEX_SHA256,
        "original annex identity differs",
    )
    mandatory = {
        *HOST_FILES,
        "rhs_reference/arithmetic.py",
        "rhs_reference/reference.py",
        "CORRECTION_PROTOCOL.md",
        "original-annex.json",
        "bundle/source-manifest.json",
        "reference-records/d039-prepared.json",
        "reference-records/d039-campaign.json",
        "source-diff-from-d039.patch",
    }
    require(mandatory <= set(prepared["immutable_files"]), "source closure incomplete")
    for name, identity in prepared["immutable_files"].items():
        require(
            digest(safe_file(root, name)) == identity,
            "immutable source/input changed: " + name,
        )
    require(
        digest(root / "CORRECTION_PROTOCOL.md") == PROTOCOL_SHA256
        and digest(root / "reference-records/d039-prepared.json") == D039_PREPARED
        and digest(root / "reference-records/d039-campaign.json") == D039_CAMPAIGN,
        "frozen receipts/protocol changed",
    )
    require(
        digest(root / "original-annex.json") == prepared["original_annex_sha256"],
        "original annex changed",
    )
    require(
        prepared.get("source_predecessor") == D039_SOURCE
        and prepared.get("source_diff")
        == {
            "path": "source-diff-from-d039.patch",
            "sha256": digest(root / "source-diff-from-d039.patch"),
        },
        "physical predecessor/diff differs",
    )
    for case, identity in INPUT_SHA256.items():
        require(
            prepared["immutable_files"].get("inputs/" + case + ".npz") == identity,
            "original input NPZ binding differs",
        )
    old = json.loads((root / "reference-records/d039-campaign.json").read_text())
    old_attempts = {a["name"]: a for a in old["attempts"]}
    for case in CASES:
        state = case + "-initial"
        for name in REFERENCE_FILES:
            expected = {
                "path": "reference-baselines/" + state + "/" + name,
                "sha256": old_attempts[state + "-identity-3"]["files"][name]["sha256"],
            }
            require(
                prepared["reference_baselines"][state][name] == expected
                and prepared["immutable_files"].get(expected["path"])
                == expected["sha256"],
                "D-039 initial reference binding differs",
            )
        for stage, entry in prepared["inputs"][case].items():
            require(
                prepared["immutable_files"].get(entry["path"]) == entry["sha256"],
                "planned input binding differs",
            )
            raw = (root / entry["path"]).read_bytes()
            control = "standard" if stage == "control" else stage[3:]
            require(
                struct.unpack_from("<2d", raw, 32) == CONTROLS[control],
                "correction controls differ",
            )
    history = prepared["input_preparation_history"]
    require(
        digest(root / history["path"]) == history["sha256"],
        "original preparation history differs",
    )
    original = json.loads((root / history["path"]).read_text())
    require(
        original["source_commit"] == prepared["source_commit"]
        and original["source_tree"] == prepared["source_tree"],
        "original helper source identity differs",
    )
    original_specs = {s["name"]: s for s in original["attempts"]}
    for case in CASES:
        for stage, entry in prepared["inputs"][case].items():
            suffix = "control" if stage == "control" else stage[:2]
            old_entry = original_specs[case + "-" + suffix]
            base = safe_file(root, old_entry["input"])
            require(
                prepared["immutable_files"].get(old_entry["input"]) == digest(base),
                "original wire immutable binding differs",
            )
            control = "standard" if stage == "control" else stage[3:]
            require(
                (root / entry["path"]).read_bytes()
                == correction_input(base.read_bytes(), control),
                "stage input differs outside declared correction controls",
            )


def build_b_release_gate(root):
    """Verify the independently reloaded A receipt and identical frozen inputs."""
    root = Path(root)
    prepared = json.loads((root / "prepared.json").read_text())
    require(prepared["build_label"] == "B", "B release requested for another build")
    context = prepared["build_a"]
    proof_entry = context["verification"]
    require(
        digest(root / proof_entry["path"]) == proof_entry["sha256"],
        "A release proof changed",
    )
    proof = json.loads((root / proof_entry["path"]).read_text())
    a_prepared = root / "reference-records/build-a-prepared.json"
    a_campaign = root / "reference-records/build-a-campaign.json"
    require(
        digest(a_prepared) == context["prepared_sha256"]
        and digest(a_campaign) == context["campaign_sha256"],
        "A release source receipts changed",
    )
    aprep, acampaign = (
        json.loads(a_prepared.read_text()),
        json.loads(a_campaign.read_text()),
    )
    expected = {
        "schema": "crucible.correction.verification.v1",
        "qualification_pass": True,
        "prepared_sha256": context["prepared_sha256"],
        "campaign_sha256": context["campaign_sha256"],
        "source_commit": prepared["source_commit"],
        "source_tree": prepared["source_tree"],
        "protocol_sha256": PROTOCOL_SHA256,
        "build_label": "A",
        "artifact_identity_pass": True,
        "reload_pass": True,
    }
    require(
        all(proof.get(k) == v for k, v in expected.items()),
        "A verified qualification/reload release absent",
    )
    require(
        aprep["build_label"] == "A"
        and acampaign.get("qualification_pass") is True
        and acampaign.get("complete") is True
        and acampaign.get("prepared_sha256") == context["prepared_sha256"],
        "A source/campaign qualification differs",
    )
    for key in (
        "source_commit",
        "source_tree",
        "protocol_sha256",
        "inputs",
        "reference_baselines",
        "source_diff",
    ):
        require(
            aprep[key] == prepared[key],
            "B frozen source/input identity differs from A: " + key,
        )
    # Only original helper timing/environment receipts and B's additional A proof
    # are expected to have different metadata hashes. Actual staged source,
    # forcing, initial controls and all planned trajectory inputs must match.
    ignored = {"preparation-history/original-prepared.json"}
    compared = {
        name: identity
        for name, identity in aprep["immutable_files"].items()
        if name not in ignored
    }
    require(
        all(
            prepared["immutable_files"].get(name) == identity
            for name, identity in compared.items()
        ),
        "B immutable source/input closure differs from A",
    )
    return {
        "pass": True,
        "artifact_identity_pass": True,
        "verification_sha256": proof_entry["sha256"],
        "compared_immutable_files": len(compared),
    }


def build_identities(root):
    result = diag.build_identities(root)
    for executable, receipt in (("assembly_synthetic", "assembly-executable.sha256"),):
        fields = (root / "bundle" / receipt).read_text().split()
        require(
            len(fields) == 2
            and Path(fields[1]).name == executable
            and fields[0] == digest(root / "bundle" / executable),
            "fixture executable receipt differs",
        )
        result["executables"][executable] = fields[0]
    return result


def synthetic_checks(root):
    extra = (("trajectory_synthetic", "retry-snapshot", None),) + tuple(
        ("assembly_synthetic", name, None)
        for name in ("precision", "arithmetic", "malformed", "nonfinite", "overflow")
    )
    extra += tuple(
        ("trajectory_synthetic", "correction-" + name, None)
        for name in ("nonlinear", "stiff", "rounded", "current", "retry", "projection")
    )
    extra += (
        (
            "trajectory_synthetic",
            "correction-projection-bound",
            "FAILURE final Newton projection exceeds per-step bound",
        ),
        ("trajectory_synthetic", "correction-incomplete", "FAILURE incomplete horizon"),
    )
    return common.synthetic_checks(root, extra_scenarios=extra)


def science_gates(root):
    return load_module("correction_frozen_science_gates", root / "correction_checks.py")


def bind_diagnostic(root, prepared, spec):
    """Freeze exact L3 requested bytes without extrapolation or a new F call."""
    if "derived_from" not in spec:
        return spec
    parent = spec["derived_from"]["attempt"]
    campaign = json.loads((root / "campaign.json").read_text())
    source_attempt = next(a for a in campaign["attempts"] if a["name"] == parent)
    require(
        source_attempt.get("qualification_pass") is True
        and source_attempt.get("completed") is True,
        "diagnostic source trajectory did not pass",
    )
    work = root / "attempts" / parent
    verify_attempt_files(root, source_attempt)
    raw = (work / "accepted.bin").read_bytes()
    width = 488 * 8
    require(raw and len(raw) % width == 0, "malformed diagnostic source stream")
    when = spec["time"]
    rows = [
        i
        for i in range(len(raw) // width)
        if raw[i * width : i * width + 8] == struct.pack("<d", when)
    ]
    require(len(rows) == 1, "missing/duplicate exact diagnostic time")
    row = rows[0]
    y = raw[row * width + 8 : row * width + 161 * 8]
    template = (root / prepared["inputs"][spec["case"]]["control"]["path"]).read_bytes()
    header = list(struct.unpack_from("<8i", template))
    require(
        header[:3] == [0x43524432, 1, 160] and header[6] == 0,
        "diagnostic template differs",
    )
    start = 48 + (480 + 3 * header[3]) * 8
    data = bytearray(template[:start])
    data[2608:3888] = y
    data.extend(struct.pack("<2d", when, when))
    header[4:7] = [1, 1, 0]
    struct.pack_into("<8i", data, 0, *header)
    binding = {
        "schema": "crucible.phase2d.correction-state-binding.v1",
        "source_attempt": parent,
        "source_accepted_sha256": sha(raw),
        "source_attempt_sha256": digest(work / "attempt.json"),
        "source_input_sha256": source_attempt["input_sha256"],
        "row": row,
        "time": when,
        "time_binary64_hex": struct.pack("<d", when).hex(),
        "Y_sha256": sha(y),
        "input_sha256": sha(data),
    }
    target = safe_file(root, spec["input"])
    record_path = target.parent / "state-binding.json"
    if target.exists() or record_path.exists():
        require(
            target.read_bytes() == data
            and json.loads(record_path.read_text()) == binding,
            "existing diagnostic binding differs",
        )
    else:
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(data)
        save(record_path, binding)
    return {
        **spec,
        "input_sha256": sha(data),
        "state_binding": {
            "path": str(record_path.relative_to(root)),
            "sha256": digest(record_path),
        },
    }


def verify_attempt_files(root, record, *, directory=None):
    work = root / (directory or ("attempts/" + record["name"]))
    require(record.get("files") is not None, "attempt artifact inventory missing")
    for name, entry in record["files"].items():
        path = work / name
        require(
            path.is_file()
            and digest(path) == entry["sha256"]
            and path.stat().st_size == entry["bytes"],
            "retained attempt artifact changed",
        )


def account(manifest):
    records = manifest["attempts"] + [
        a["record"] for a in manifest.get("interrupted_attempts", [])
    ]
    for counter, filename, key in (
        ("physical_rhs_calls", "counters.json", "rhs"),
        ("guarded_fresh_requests", "assembly-counters.json", "fresh_requests"),
    ):
        field = (
            "native_counters" if filename == "counters.json" else "assembly_counters"
        )
        manifest[counter] = sum(a.get(field, {}).get(key, 0) for a in records)
    manifest["call_count_scope"] = (
        "Exact completed-process totals plus observed interrupted checkpoints; unflushed intervals remain unknown. Runtime restart does not imply zero unobserved calls."
    )
    manifest["call_accounting_complete"] = all(
        a.get("counter_accounting_complete")
        for a in records
        if a["status"] not in ("UNATTEMPTED", "CONDITIONALLY_UNATTEMPTED")
    )


def retain_counters(root, attempt):
    work = root / "attempts" / attempt["name"]
    for filename, key in (
        ("counters.json", "native_counters"),
        ("assembly-counters.json", "assembly_counters"),
    ):
        path = work / filename
        if path.is_file():
            attempt[key] = json.loads(path.read_text())
    native, assembly = (
        attempt.get("native_counters", {}),
        attempt.get("assembly_counters", {}),
    )
    attempt["counter_accounting_complete"] = (
        bool(native and assembly) and attempt.get("completed") is True
    )
    if attempt.get("completed") is True:
        require(
            bool(native and assembly), "completed process counter accounting missing"
        )
    else:
        attempt["interruption_scope"] = {
            "available": "HASHED_LAST_FLUSHED_ARTIFACTS_AND_COUNTER_CHECKPOINTS",
            "unavailable": "IN_FLIGHT_DIAGNOSTICS_AND_UNFLUSHED_CALL_INTERVAL",
            "unflushed_calls": None,
        }
    if native:
        require(
            set(native) == diag.COUNTERS
            and all(type(x) is int and x >= 0 for x in native.values()),
            "invalid native counters",
        )
    if assembly:
        require(
            set(assembly) == {"schema", "fresh_requests", "rhs", "assembly_calls"}
            and assembly["schema"] == "crucible.assembly-counters.v1"
            and all(
                type(assembly[k]) is int and assembly[k] >= 0
                for k in ("fresh_requests", "rhs", "assembly_calls")
            ),
            "invalid guarded counters",
        )
    if native and assembly:
        require(
            assembly["rhs"] == native["rhs"]
            and assembly["fresh_requests"] >= native["rhs"],
            "counter disagreement",
        )


def _terminal(work):
    status = work / "status.txt"
    return (
        status.read_text().splitlines()[-1]
        if status.exists() and status.read_text().splitlines()
        else ""
    )


def _interrupt_record(root, manifest):
    for item in manifest["attempts"]:
        if item["status"] != "STARTING":
            continue
        path = root / "attempts" / item["name"] / "attempt.json"
        if path.exists():
            record = json.loads(path.read_text())
            if record.get("completed"):
                item.update(record)
                continue
            record.update(
                status="ARTIFACT_CAPTURE_FAILURE"
                if _terminal(path.parent).startswith(("SUCCESS", "FAILURE"))
                else "INTERRUPTED",
                files=common.snapshot(path.parent),
            )
            save(path, record)
            item.update(record)
        else:
            item.update(
                status="INTERRUPTED_BEFORE_LAUNCH",
                completed=False,
                files=common.snapshot(path.parent) if path.parent.exists() else {},
            )
        retain_counters(root, item)


def _resume(root, manifest, prepared, reason):
    require(
        isinstance(reason, str) and reason.strip(),
        "infrastructure restart requires recorded reason",
    )
    require(
        manifest.get("stop_kind") == "INFRASTRUCTURE_INTERRUPTION"
        and not manifest.get("interrupted_attempts"),
        "only one infrastructure-interrupted process restart per build",
    )
    require(
        manifest["prepared_sha256"] == digest(root / "prepared.json"),
        "restart preparation changed",
    )
    pending = [
        a
        for a in manifest["attempts"]
        if a["status"] in ("INTERRUPTED", "INTERRUPTED_BEFORE_LAUNCH")
    ]
    require(len(pending) == 1, "restart needs exactly one interrupted process")
    interrupted = pending[0]
    work = root / "attempts" / interrupted["name"]
    require(
        not interrupted.get("completed")
        and not _terminal(work).startswith(("SUCCESS", "FAILURE")),
        "completed/numerical failure cannot restart",
    )
    for record in manifest["attempts"]:
        if record.get("completed"):
            verify_attempt_files(root, record)
    if work.exists():
        verify_attempt_files(root, interrupted)
        retained = root / "interrupted" / (interrupted["name"] + "-attempt-1")
        retained.parent.mkdir(exist_ok=True)
        work.rename(retained)
        directory = str(retained.relative_to(root))
    else:
        directory = None
    manifest["interrupted_attempts"] = [
        {
            "record": dict(interrupted),
            "directory": directory,
            "infrastructure_reason": reason.strip(),
            "restart_from": "IDENTICAL_ORIGINAL_INPUT_T0_NEW_PROCESS",
        }
    ]
    index = manifest["attempts"].index(interrupted)
    manifest["attempts"][index] = {
        **prepared["attempts"][index],
        "status": "UNATTEMPTED",
        "completed": False,
        "restart_of": directory,
    }
    manifest.pop("exception", None)
    manifest.pop("stop_kind", None)


def execute(root, *, srun=False, infrastructure_restart=None):
    """Run stage pairs; identity faults stop immediately, numerical faults after pair."""
    root = Path(root).resolve()
    prepared = json.loads((root / "prepared.json").read_text())
    validate_prepared(root, prepared)
    for name, path in (
        ("correction_campaign.py", Path(__file__)),
        ("campaign.py", Path(common.__file__)),
        ("diagnostic_campaign.py", Path(diag.__file__)),
    ):
        require(
            digest(path) == prepared["immutable_files"][name],
            "running host script changed",
        )
    path = root / "campaign.json"
    if path.exists():
        require(
            infrastructure_restart is not None,
            "existing campaign requires bounded infrastructure restart",
        )
        manifest = json.loads(path.read_text())
        _resume(root, manifest, prepared, infrastructure_restart)
    else:
        require(
            infrastructure_restart is None and not (root / "attempts").exists(),
            "new campaign required",
        )
        manifest = {
            "schema": "crucible.phase2d.correction-campaign.v1",
            "numerical_source": SOURCE_NAME,
            "build_label": prepared["build_label"],
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
            "interrupted_attempts": [],
            "gates": {},
            "complete": False,
            "qualification_pass": False,
            "physical_rhs_calls": 0,
            "guarded_fresh_requests": 0,
            "call_accounting_complete": False,
            "algorithm": {
                "native_attempts_per_step_call": 10,
                "newton_iterations_per_attempt": 30,
                "resource_cap": None,
            },
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
        require(
            "build" not in manifest or manifest["build"] == build,
            "restart build identity changed",
        )
        manifest["build"] = build
        save(path, manifest)
        gates = science_gates(root)
        if prepared["build_label"] == "B":
            release = build_b_release_gate(root)
            manifest["gates"]["build_b_release"] = release
            require(
                release.get("pass") is True,
                "Build A independent verification has not released Build B",
            )
        manifest["synthetic"] = synthetic_checks(root)
        save(path, manifest)
        precision = gates.precision_gate(root)
        manifest["gates"]["precision"] = precision
        require(precision.get("pass") is True, "precision prerequisite failed")
        launcher = ["srun", "-n", "1", "-c", "1"] if srun else []
        for stage in STAGES:
            aggregate_gate = None
            stage_records = [a for a in manifest["attempts"] if a["stage"] == stage]
            for original in stage_records:
                index = next(
                    i
                    for i, a in enumerate(manifest["attempts"])
                    if a["name"] == original["name"]
                )
                if original.get("completed"):
                    verify_attempt_files(root, original)
                    continue
                require(
                    original["status"] == "UNATTEMPTED", "invalid active attempt status"
                )
                validate_prepared(root, prepared)
                require(
                    digest(root / "prepared.json") == manifest["prepared_sha256"]
                    and build_identities(root) == build,
                    "source/build changed during campaign",
                )
                spec = bind_diagnostic(root, prepared, prepared["attempts"][index])
                manifest["attempts"][index] = {
                    **spec,
                    "status": "STARTING",
                    "completed": False,
                }
                save(path, manifest)
                result = common.run_attempt(
                    root,
                    spec,
                    root / "bundle/trajectory_driver",
                    launcher,
                    resume=False,
                    arguments=tuple(spec["arguments"]),
                )
                attempt = {**spec, **result}
                work = root / "attempts" / spec["name"]
                if (
                    result.get("returncode") is not None
                    and result["returncode"] < 0
                    or result.get("status") == "EXCEPTION"
                ) and not _terminal(work).startswith(("SUCCESS", "FAILURE")):
                    attempt.update(status="INTERRUPTED", completed=False)
                    save(
                        work / "attempt.json",
                        {**result, "status": "INTERRUPTED", "completed": False},
                    )
                    manifest["attempts"][index] = attempt
                    retain_counters(root, attempt)
                    manifest["stop_kind"] = "INFRASTRUCTURE_INTERRUPTION"
                    raise RuntimeError(
                        "native process interrupted; audited infrastructure restart may resume once"
                    )
                manifest["attempts"][index] = attempt
                retain_counters(root, attempt)
                account(manifest)
                save(path, manifest)
                gate = gates.attempt_gate(root, spec, result)
                attempt.update(
                    science_gate=gate,
                    qualification_pass=gate.get("pass") is True,
                    validation_completed=True,
                )
                save(path, manifest)
                require(
                    not gate.get("identity_failure")
                    and gate.get("software_pass", True)
                    and not gate.get("fatal", False),
                    "shared identity/corruption/forensic gate failed",
                )
                require(
                    gate.get("pass") is True
                    or (
                        stage != "control"
                        and gate.get("ordinary_numerical_failure") is True
                    ),
                    "unclassified native/initial control failure",
                )
            stage_records = [a for a in manifest["attempts"] if a["stage"] == stage]
            passed = all(a.get("qualification_pass") is True for a in stage_records)
            if stage == "L0-tight" and passed:
                gate = gates.pilot_gate(root)
                manifest["gates"]["pilot"] = gate
                aggregate_gate = gate
                passed = gate.get("pass") is True
            elif stage == "L3-tight" and passed:
                gate = gates.trajectory_gate(root)
                manifest["gates"]["trajectory"] = gate
                aggregate_gate = gate
                passed = gate.get("pass") is True
            elif stage == "derivative" and passed:
                gate = gates.derivative_gate(root)
                manifest["gates"]["derivative"] = gate
                aggregate_gate = gate
                passed = gate.get("pass") is True
            if aggregate_gate is not None:
                require(
                    not aggregate_gate.get("identity_failure")
                    and aggregate_gate.get("software_pass", True)
                    and not aggregate_gate.get("fatal", False),
                    "shared aggregate identity/corruption gate failed",
                )
            save(path, manifest)
            if not passed:
                for attempt in manifest["attempts"]:
                    if attempt["status"] == "UNATTEMPTED":
                        attempt.update(
                            status="CONDITIONALLY_UNATTEMPTED",
                            skip_reason=stage.upper() + "_JOINT_GATE_FAILED",
                        )
                manifest["stop_kind"] = "ORDINARY_NUMERICAL_FAILURE"
                break
        manifest["complete"] = all(
            a.get("completed") or a["status"] == "CONDITIONALLY_UNATTEMPTED"
            for a in manifest["attempts"]
        )
        account(manifest)
        manifest["attempt_accounting_complete"] = manifest["complete"] and all(
            (
                a.get("directory") is not None
                or a["record"]["status"] == "INTERRUPTED_BEFORE_LAUNCH"
            )
            and bool(a.get("infrastructure_reason"))
            and bool(a["record"].get("interruption_scope"))
            for a in manifest["interrupted_attempts"]
        )
        manifest["qualification_pass"] = (
            manifest["complete"]
            and manifest["attempt_accounting_complete"]
            and all(a.get("qualification_pass") is True for a in manifest["attempts"])
            and all(
                manifest["gates"].get(k, {}).get("pass") is True
                for k in ("precision", "pilot", "trajectory", "derivative")
            )
        )
    except BaseException as exc:
        manifest["exception"] = repr(exc)
        _interrupt_record(root, manifest)
        if "stop_kind" not in manifest:
            manifest["stop_kind"] = (
                "INFRASTRUCTURE_INTERRUPTION"
                if any(
                    a["status"] in ("INTERRUPTED", "INTERRUPTED_BEFORE_LAUNCH")
                    for a in manifest["attempts"]
                )
                else "IDENTITY_OR_SOFTWARE_FAILURE"
            )
        for attempt in manifest["attempts"]:
            if attempt["status"] == "UNATTEMPTED":
                attempt["unattempted_reason"] = manifest["stop_kind"]
        account(manifest)
        raise
    finally:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        manifest.setdefault("execution_invocations", []).append(
            {
                "wall_seconds": time.perf_counter() - started,
                "children_cpu_seconds_cumulative": usage.ru_utime + usage.ru_stime,
                "children_peak_rss_bytes": usage.ru_maxrss
                * (1024 if platform.system() == "Linux" else 1),
            }
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
    prep.add_argument("config", type=Path)
    prep.add_argument("destination", type=Path)
    prep.add_argument("--source-root", type=Path, default=Path.cwd())
    prep.add_argument("--build-label", choices=("A", "B"), default="A")
    prep.add_argument("--build-a", type=Path)
    prep.add_argument("--build-a-verification", type=Path)
    prep.add_argument("--build-a-verification-sha")
    run = sub.add_parser("execute")
    run.add_argument("root", type=Path)
    run.add_argument("--srun", action="store_true")
    run.add_argument("--infrastructure-restart", metavar="REASON")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(
            args.config,
            args.destination,
            args.source_root,
            build_label=args.build_label,
            build_a=args.build_a,
            build_a_verification=args.build_a_verification,
            build_a_verification_sha=args.build_a_verification_sha,
        )
    else:
        execute(
            args.root,
            srun=args.srun,
            infrastructure_restart=args.infrastructure_restart,
        )


if __name__ == "__main__":
    main()
