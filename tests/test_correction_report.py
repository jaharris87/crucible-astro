"""Public offline D-040 reporting adversaries; no producer/private inputs."""

import copy
import importlib.util
import json
import os
import struct
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def load_report():
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/correction_report.py"
    )
    spec = importlib.util.spec_from_file_location("correction_report_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False))


def populations():
    stages = (
        "control",
        "L0-standard",
        "L0-tight",
        "L1-standard",
        "L2-standard",
        "L3-standard",
        "L3-tight",
        "derivative",
    )
    specs = [
        {"name": case + "-" + stage, "stage": stage, "case": case}
        for stage in stages[:-1]
        for case in ("development", "validation")
    ]
    specs += [
        {"name": case + "-" + suffix, "stage": "derivative", "case": case}
        for case in ("development", "validation")
        for suffix in ("J0", "J5", "J10")
    ]
    prepared = {"attempts": specs}
    campaign = {
        "attempts": [{**s, "status": "RETURNED", "completed": True} for s in specs],
        "complete": True,
    }
    outcomes = {s["name"]: {"pass": True} for s in specs}
    aggregate = {k: {"pass": True} for k in ("pilot", "trajectory", "derivative")}
    return prepared, campaign, outcomes, aggregate, stages


@pytest.mark.parametrize(
    "failed", ["control", "L0-standard", "L0-tight", "L2-standard", "L3-tight"]
)
def test_success_exit_cannot_bypass_failed_joint_prerequisite(tmp_path, failed):
    report = load_report()
    prepared, campaign, outcomes, aggregate, stages = populations()
    name = next(s["name"] for s in prepared["attempts"] if s["stage"] == failed)
    outcomes[name]["pass"] = False
    with pytest.raises(ValueError, match="dependent stage"):
        report.stage_checks(tmp_path, prepared, campaign, outcomes, aggregate, stages)


def test_pilot_failure_preserves_both_cases_and_all_conditional_names(tmp_path):
    report = load_report()
    prepared, campaign, outcomes, aggregate, stages = populations()
    aggregate["pilot"]["pass"] = False
    for record in campaign["attempts"]:
        if stages.index(record["stage"]) > stages.index("L0-tight"):
            record.update(
                status="CONDITIONALLY_UNATTEMPTED",
                completed=False,
                skip_reason="L0-TIGHT_JOINT_GATE_FAILED",
            )
            outcomes[record["name"]]["pass"] = False
    checked = report.stage_checks(
        tmp_path, prepared, campaign, outcomes, aggregate, stages
    )
    assert len(campaign["attempts"]) == 20
    assert checked["L0-tight"] == {"pass": False, "attempted": 2, "required": 2}
    assert checked["derivative"]["attempted"] == 0
    assert (
        len(
            [
                r
                for r in campaign["attempts"]
                if r["status"] == "CONDITIONALLY_UNATTEMPTED"
            ]
        )
        == 14
    )


def test_unsupported_conditional_exclusion_refused(tmp_path):
    report = load_report()
    prepared, campaign, outcomes, aggregate, stages = populations()
    campaign["attempts"][-1].update(
        status="CONDITIONALLY_UNATTEMPTED", skip_reason="UNLUCKY_CASE"
    )
    with pytest.raises(ValueError, match="unsupported conditional"):
        report.stage_checks(tmp_path, prepared, campaign, outcomes, aggregate, stages)


def run_arrays(step=0.005):
    t = np.arange(round(0.01 / step) + 1, dtype=float) * step
    return {
        "accepted_t": t,
        "requested_t": np.array([0.0, 0.005, 0.01]),
        "requested_Y": np.array([[0.25, 0.25], [0.25, 0.25], [0.25, 0.25]]),
        "output_present": np.ones(3, dtype=bool),
        "missing_output": np.zeros(3, dtype=bool),
    }


def test_missing_requested_state_is_explicit_and_prevents_qualification(tmp_path):
    report = load_report()
    accepted = np.zeros((2, 488))
    accepted[:, 0] = [0.0, 0.01]
    accepted[:, 1:161] = 0.001
    accepted.astype("<f8").tofile(tmp_path / "accepted.bin")
    result = report.trajectory_arrays(
        tmp_path, {"outputs": (0.0, 0.005, 0.01), "A": [1.0] * 160, "Z": [1.0] * 160}
    )
    assert result["output_present"].tolist() == [True, False, True]
    assert np.isnan(result["requested_Y"][1]).all()
    runs = {f"L{i}-standard": result for i in range(4)}
    runs.update({"L0-tight": result, "L3-tight": result})
    checked = report.case_metrics(runs, np.ones(160), np.ones(160))
    assert checked["pass"] is False
    assert checked["refinement"]["complete_levels"].tolist() == [False] * 4


def test_large_residual_does_not_add_old_local_acceptance_gate():
    report = load_report()
    runs = {f"L{i}-standard": run_arrays(0.005 / 2**i) for i in range(4)}
    runs.update({"L0-tight": run_arrays(), "L3-tight": run_arrays(0.005 / 8)})
    for run in runs.values():
        run["raw_residual_norm_diagnostic"] = np.array([0.0, 1e90])
    checked = report.case_metrics(runs, np.array([1.0, 2.0]), np.array([0.0, 1.0]))
    assert checked["pass"] is True
    assert checked["refinement"]["comparisons"][0]["dX"].shape == (3, 2)
    assert "relative_defined" in checked["pilot"]


def test_numerically_different_fresh_run_cannot_be_serialization_pass():
    report = load_report()
    first, repeat = run_arrays(), run_arrays()
    repeat["requested_Y"][1, 1] += 1e-7
    result = report.compare_runs(
        first, repeat, np.array([1.0, 2.0]), np.array([0.0, 1.0])
    )
    assert result["pass"] is False
    assert result["component_pass"][1, 1] == np.bool_(False)
    assert result["comparison"]["X"]["maximum_location"].tolist() == [1, 1]
    assert result["accepted_mesh_identical"]


def test_reproduction_requires_exact_masks_and_grid():
    report = load_report()
    first, repeat = run_arrays(), run_arrays()
    repeat["missing_output"][1] = True
    with pytest.raises(ValueError, match="grid/masks"):
        report.compare_runs(first, repeat, np.array([1.0, 2.0]), np.array([0.0, 1.0]))
    repeat = run_arrays()
    repeat["requested_t"][1] = np.nextafter(0.005, np.inf)
    with pytest.raises(ValueError, match="grid/masks"):
        report.compare_runs(first, repeat, np.array([1.0, 2.0]), np.array([0.0, 1.0]))


def counter_fixture(tmp_path):
    native = {"rhs": 3, "newton": 1}
    guarded = {
        "schema": "crucible.assembly-counters.v1",
        "rhs": 3,
        "assembly_calls": 3,
        "fresh_requests": 4,
    }
    write_json(tmp_path / "counters.json", native)
    write_json(tmp_path / "assembly-counters.json", guarded)
    return {
        "native_counters": native,
        "assembly_counters": guarded,
        "counter_accounting_complete": True,
    }


def test_missing_completed_counter_is_never_reported_as_zero(tmp_path):
    report = load_report()
    record = counter_fixture(tmp_path)
    (tmp_path / "counters.json").unlink()
    with pytest.raises(ValueError, match="completed process counter"):
        report.verify_counters(tmp_path, record, ("rhs", "newton"), completed=True)


def test_interrupted_counter_interval_remains_unknown(tmp_path):
    report = load_report()
    record = counter_fixture(tmp_path)
    record.update(
        counter_accounting_complete=False, interruption_scope={"unflushed_calls": None}
    )
    result = report.verify_counters(
        tmp_path, record, ("rhs", "newton"), completed=False
    )
    assert not result["complete"]
    assert result["native_counters"]["rhs"] == 3
    assert result["unavailable"]["unflushed_calls"] is None


def identity_fixture(tmp_path, report):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    exes = {}
    for name, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
        ("assembly_synthetic", "assembly-executable.sha256"),
    ):
        (bundle / name).write_bytes(name.encode())
        exes[name] = report.digest(bundle / name)
        (bundle / receipt).write_text(exes[name] + "  " + name + "\n")
    libraries = {"/actual/execution/vendor/library.so": "a" * 64}
    write_json(bundle / "linked-library-hashes.json", libraries)
    build = {
        "executables": exes,
        "libraries": libraries,
        "build_files": {
            str(p.relative_to(tmp_path)): report.digest(p) for p in bundle.iterdir()
        },
    }
    prepared = {"source_commit": "b" * 40, "source_tree": "c" * 40, "build_label": "A"}
    campaign = {
        "complete": True,
        "build": build,
        "attempts": [
            {
                "name": "development-control",
                "completed": True,
                "loaded_library_hashes": libraries,
                "loaded_library_unavailable_reason": None,
            }
        ],
        "interrupted_attempts": [],
    }
    write_json(tmp_path / "prepared.json", prepared)
    write_json(tmp_path / "campaign.json", campaign)
    contract = SimpleNamespace(SOURCE_NAME="source", PROTOCOL_SHA256="d" * 64)
    proof = {
        "schema": "crucible.phase2d.correction-host-identities.v1",
        "numerical_source": contract.SOURCE_NAME,
        "source_commit": prepared["source_commit"],
        "source_tree": prepared["source_tree"],
        "protocol_sha256": contract.PROTOCOL_SHA256,
        "build_label": "A",
        "prepared_sha256": report.digest(tmp_path / "prepared.json"),
        "campaign_sha256": report.digest(tmp_path / "campaign.json"),
        "collector_sha256": report.digest(
            report.HERE / "correction_host_identities.py"
        ),
        "build": build,
        "completed_attempts": ["development-control"],
        "checked_files": libraries,
        "interrupted_library_evidence": [],
        "campaign_accounting_complete": True,
        "producer_quiescence_basis": "LEAD_VERIFIED_PRODUCERS_AND_CONTROLLER_TERMINAL",
    }
    write_json(tmp_path / report.HOST_IDENTITIES, proof)
    return prepared, campaign, contract, proof


def test_explicit_execution_host_proof_does_not_read_or_remap_vendor_paths(tmp_path):
    report = load_report()
    prepared, campaign, contract, _ = identity_fixture(tmp_path, report)
    result = report.verify_retained_build(
        tmp_path,
        prepared,
        campaign,
        contract,
        report.digest(tmp_path / report.HOST_IDENTITIES),
    )
    assert result["pass"]
    assert result["checked_files"] == campaign["build"]["libraries"]


@pytest.mark.parametrize(
    "tamper", ["proof-sha", "source", "library", "executable", "missing-build-file"]
)
def test_tampered_identity_or_incomplete_build_refused(tmp_path, tamper):
    report = load_report()
    prepared, campaign, contract, proof = identity_fixture(tmp_path, report)
    expected = report.digest(tmp_path / report.HOST_IDENTITIES)
    if tamper == "proof-sha":
        expected = "0" * 64
    elif tamper == "source":
        proof["source_commit"] = "0" * 40
    elif tamper == "library":
        proof["checked_files"] = {"/different/library.so": "a" * 64}
    elif tamper == "executable":
        (tmp_path / "bundle/trajectory_driver").write_bytes(b"replacement")
    else:
        (tmp_path / "bundle/executable.sha256").unlink()
    if tamper in {"source", "library"}:
        write_json(tmp_path / report.HOST_IDENTITIES, proof)
        expected = report.digest(tmp_path / report.HOST_IDENTITIES)
    with pytest.raises((ValueError, OSError)):
        report.verify_retained_build(tmp_path, prepared, campaign, contract, expected)


def saved_report(tmp_path, report):
    output = tmp_path / "analysis.json"
    value = {
        "schema": "synthetic",
        "qualification_pass": False,
        "artifact_identity_pass": True,
        "host_identity_sha256": "a" * 64,
        "prepared_sha256": "b" * 64,
        "campaign_sha256": "c" * 64,
        "source_commit": "d" * 40,
        "source_tree": "e" * 40,
        "protocol_sha256": "f" * 64,
        "build_label": "A",
        "signed_zero": np.array([-0.0, 0.0], dtype="<f8"),
        "undefined": np.array([np.nan, np.inf], dtype="<f8"),
        "mask": np.array([False, True]),
        "ids": np.array([2**60 + 1], dtype="<i8"),
    }
    report.write_report(output, value)
    return output, value


def test_numeric_reload_keeps_failed_qualification_and_writes_bound_release(
    tmp_path, monkeypatch
):
    report = load_report()
    output, value = saved_report(tmp_path, report)
    monkeypatch.setattr(report, "analyze", lambda *_: value)
    result = report.reload_report(tmp_path, output, "a" * 64)
    assert result["qualification_pass"] is False
    release = json.loads(output.with_suffix(".release.json").read_text())
    assert release["reload_pass"] is True
    assert release["qualification_pass"] is False
    assert release["report_json_sha256"] == report.digest(output)
    assert release["report_npz_sha256"] == report.digest(output.with_suffix(".npz"))
    with pytest.raises(FileExistsError):
        report.reload_report(tmp_path, output, "a" * 64)


@pytest.mark.parametrize(
    "tamper", ["raw-array", "metadata", "npz-bytes", "dtype", "host"]
)
def test_reload_refuses_changed_bytes_dtype_metadata_or_host(
    tmp_path, monkeypatch, tamper
):
    report = load_report()
    output, value = saved_report(tmp_path, report)
    recomputed = copy.deepcopy(value)
    host = "a" * 64
    if tamper == "raw-array":
        recomputed["signed_zero"][0] = 0.0
    elif tamper == "metadata":
        recomputed["qualification_pass"] = True
    elif tamper == "dtype":
        recomputed["ids"] = recomputed["ids"].astype(np.float64)
    elif tamper == "host":
        host = "0" * 64
    else:
        with output.with_suffix(".npz").open("ab") as stream:
            stream.write(b"tamper")
    monkeypatch.setattr(report, "analyze", lambda *_: recomputed)
    with pytest.raises(ValueError):
        report.reload_report(tmp_path, output, host)
    assert not output.with_suffix(".release.json").exists()


def test_newton_mixed_ids_and_binary64_are_mmap_views_and_partial_tail_is_retained(
    tmp_path,
):
    report = load_report()
    path = tmp_path / "correction-newton.bin"
    ids = tuple(range(12))
    values = np.arange(1936, dtype=float)
    path.write_bytes(
        struct.pack("<8i", 0x4352434E, 1, 160, 1936, 12, 0, 0, 0)
        + struct.pack("<12q1936d", *ids, *values)
    )
    arrays = report.newton_arrays(path)
    assert arrays["ids"].dtype == np.dtype("<i8")
    assert arrays["ids"][0].tolist() == list(ids)
    assert np.array_equal(arrays["values"][0], values)
    with path.open("ab") as stream:
        stream.write(b"partial")
    with pytest.raises(ValueError, match="truncated"):
        report.newton_arrays(path)
    retained = report.retain_numeric(tmp_path)[path.name]
    assert retained["bytes"].tobytes().endswith(b"partial")


def test_fresh_process_reload_streams_large_mmap_without_numpy_load(tmp_path):
    report = load_report()
    raw = tmp_path / "raw.bin"
    data = np.memmap(raw, mode="w+", dtype="<f8", shape=(262144, 4))
    data[:] = np.arange(4)
    data.flush()
    value = {
        "host_identity_sha256": "a" * 64,
        "raw": np.memmap(raw, mode="r", dtype="<f8", shape=data.shape)[:, ::2],
    }
    output = tmp_path / "stream.json"
    report.write_report(output, value)
    # Actual fresh interpreter, and np.load is disabled: reload must compare
    # NPY headers/bytes through ZIP streams rather than loading entire arrays.
    code = """
import importlib.util, pathlib, sys, numpy as np
p=pathlib.Path(sys.argv[1]); root=pathlib.Path(sys.argv[2])
s=importlib.util.spec_from_file_location('fresh_report', p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
m.analyze=lambda *_: {'host_identity_sha256':'a'*64, 'raw':np.memmap(root/'raw.bin',mode='r',dtype='<f8',shape=(262144,4))[:,::2]}
np.load=lambda *a,**k: (_ for _ in ()).throw(AssertionError('whole NPZ load forbidden'))
m.reload_report(root,root/'stream.json','a'*64,release=False)
"""
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            code,
            str(report.HERE / "correction_report.py"),
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        env=environment,
    )
    assert result.returncode == 0, result.stderr


def synthetic_pipeline(tmp_path, monkeypatch, report):
    """Report API integration with synthetic runner/checker seams only.

    Gate mathematical correctness has separate independent checker tests; this
    fixture exercises all twenty report records, native bytes and array metrics.
    """
    prepared, campaign, _, _, stages = populations()
    prepared.update(
        schema="synthetic",
        source_commit="a" * 40,
        source_tree="b" * 40,
        protocol_sha256="c" * 64,
        build_label="A",
        inputs={},
        costs={},
        reference_baselines={},
        source_diff={"sha256": "d" * 64},
    )
    immutable = {}
    for name in (
        "correction_report.py",
        "correction_checks.py",
        "correction_campaign.py",
        "correction_host_identities.py",
        "assembly_arithmetic.py",
        "rhs_reference/arithmetic.py",
        "rhs_reference/reference.py",
    ):
        path = (
            report.HERE.parent / name
            if name.startswith("rhs_reference/")
            else report.HERE / name
        )
        immutable[name] = report.digest(path)
    prepared["immutable_files"] = immutable
    data = {"A": [1.0] * 160, "Z": [0.0] + [1.0] * 159, "outputs": [0.0, 0.005, 0.01]}
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    for case in ("development", "validation"):
        path = inputs / (case + ".bin")
        write_json(path, data)
        prepared["inputs"][case] = {
            "control": {"path": str(path.relative_to(tmp_path))}
        }
    for spec, record in zip(prepared["attempts"], campaign["attempts"], strict=True):
        spec.update(
            input="inputs/" + spec["case"] + ".bin",
            input_sha256=report.digest(inputs / (spec["case"] + ".bin")),
        )
        record.update(spec)
        work = tmp_path / "attempts" / spec["name"]
        work.mkdir(parents=True)
        write_json(work / "input.bin", data)
        (work / "status.txt").write_text("SUCCESS\n")
        record.update(
            counter_fixture(work),
            qualification_pass=True,
            science_gate={"pass": True, "identity_failure": False},
        )
        if spec["stage"].startswith("L"):
            level = int(spec["stage"][1])
            t = np.linspace(0.0, 0.01, 2 ** (level + 1) + 1)
            accepted = np.zeros((len(t), 488), dtype="<f8")
            accepted[:, 0] = t
            accepted[:, 1:3] = [0.25, 0.75]
            accepted.tofile(work / "accepted.bin")
    write_json(tmp_path / "prepared.json", prepared)
    campaign.update(
        schema="crucible.phase2d.correction-campaign.v1",
        numerical_source="synthetic",
        build_label="A",
        prepared_sha256=report.digest(tmp_path / "prepared.json"),
        qualification_pass=True,
        attempt_accounting_complete=True,
        physical_rhs_calls=60,
        guarded_fresh_requests=80,
        call_accounting_complete=True,
        interrupted_attempts=[],
        build={"libraries": {"/actual/linked/library.so": "e" * 64}},
        gates={},
    )
    write_json(tmp_path / "campaign.json", campaign)
    contract = SimpleNamespace(
        SOURCE_NAME="synthetic",
        PROTOCOL_SHA256="c" * 64,
        CASES=("development", "validation"),
        STAGES=stages,
        diag=SimpleNamespace(COUNTERS=("rhs", "newton")),
        validate_prepared=lambda *_: None,
        build_b_release_gate=lambda *_: {"pass": True},
    )
    check = SimpleNamespace(
        parse_input=lambda raw: json.loads(raw),
        assembly=None,
        attempt_gate=lambda *_: {"pass": True, "identity_failure": False},
        precision_gate=lambda *_: {"pass": True},
        pilot_gate=lambda *_: {"pass": True},
        trajectory_gate=lambda *_: {"pass": True},
        derivative_gate=lambda *_: {"pass": True},
    )
    original = report.load
    monkeypatch.setattr(
        report,
        "load",
        lambda name, path: (
            contract
            if name == "_correction_report_campaign"
            else check
            if name == "_correction_report_checks"
            else original(name, path)
        ),
    )
    monkeypatch.setattr(report, "verify_retained_build", lambda *_: {"pass": True})
    monkeypatch.setattr(report, "forensic_arithmetic", lambda *_: {"pass": True})
    monkeypatch.setattr(report, "matrix_diagnostics", lambda *_: {})
    monkeypatch.setattr(report, "toolchain_record", lambda *_: {"synthetic": True})
    return prepared, campaign


def test_all_twenty_process_analysis_and_reload_recompute_global_arrays(
    tmp_path, monkeypatch
):
    report = load_report()
    synthetic_pipeline(tmp_path, monkeypatch, report)
    result = report.analyze(tmp_path, "f" * 64)
    assert not result["errors"]
    assert result["qualification_pass"] is True
    assert len(result["attempts"]) == 20
    assert result["physical_rhs_calls_observed"] == 60
    assert all(case["pass"] for case in result["cases"].values())
    output = tmp_path / "result.json"
    report.write_report(output, result)
    reloaded = report.reload_report(tmp_path, output, "f" * 64)
    assert reloaded["qualification_pass"]
    release = json.loads(output.with_suffix(".release.json").read_text())
    assert release["schema"] == "crucible.correction.verification.v1"
    assert release["qualification_pass"] and release["reload_pass"]


def test_all_success_flags_do_not_hide_missing_raw_requested_output(
    tmp_path, monkeypatch
):
    report = load_report()
    synthetic_pipeline(tmp_path, monkeypatch, report)
    path = tmp_path / "attempts/development-L2-standard/accepted.bin"
    rows = np.fromfile(path, dtype="<f8").reshape(-1, 488)
    rows = rows[rows[:, 0] != 0.005]
    rows.tofile(path)
    result = report.analyze(tmp_path, "f" * 64)
    assert result["qualification_pass"] is False
    assert result["attempts"]["development-L2-standard"]["trajectory"][
        "missing_output"
    ].tolist() == [False, True, False]
    assert any("qualification differs" in error for error in result["errors"])
    assert len(result["attempts"]) == 20


def test_missing_campaign_still_reports_all_twenty_planned_processes(tmp_path):
    report = load_report()
    prepared, *_ = populations()
    write_json(tmp_path / "prepared.json", prepared)
    result = report.analyze(tmp_path, "f" * 64)
    assert len(result["attempts"]) == 20
    assert not result["qualification_pass"]
    assert all(
        record["status"] == "UNATTEMPTED" for record in result["attempts"].values()
    )


def test_fortran_array_layout_reloads_exactly(tmp_path, monkeypatch):
    report = load_report()
    value = {
        "host_identity_sha256": "a" * 64,
        "array": np.asfortranarray(np.arange(12).reshape(3, 4)),
    }
    output = tmp_path / "fortran.json"
    report.write_report(output, value)
    monkeypatch.setattr(report, "analyze", lambda *_: value)
    report.reload_report(tmp_path, output, "a" * 64, release=False)


def test_full_twelve_run_reproduction_and_independently_converged_difference(
    tmp_path, monkeypatch
):
    report = load_report()
    first, repeat = tmp_path / "A", tmp_path / "B"
    first.mkdir()
    repeat.mkdir()
    synthetic_pipeline(first, monkeypatch, report)
    p2, c2 = synthetic_pipeline(repeat, monkeypatch, report)
    p2["build_label"] = "B"
    write_json(repeat / "prepared.json", p2)
    c2.update(build_label="B", prepared_sha256=report.digest(repeat / "prepared.json"))
    write_json(repeat / "campaign.json", c2)
    for case in ("development", "validation"):
        np.savez(
            first / "inputs" / (case + ".npz"),
            species_Z_A=np.column_stack([[0.0] + [1.0] * 159, np.ones(160)]),
        )
    equal = report.compare_campaigns(first, repeat, "f" * 64, "f" * 64)
    assert equal["pass"] and len(equal["attempts"]) == 12, equal["errors"]
    # All levels/controls in B get the same conservative change, so B still
    # independently converges. The separate A/B allowance must reject it.
    for path in (repeat / "attempts").glob("*-L*/accepted.bin"):
        values = np.fromfile(path, dtype="<f8").reshape(-1, 488)
        values[1:, 1] -= 1e-7
        values[1:, 2] += 1e-7
        values.tofile(path)
    different = report.compare_campaigns(first, repeat, "f" * 64, "f" * 64)
    assert (
        different["first_qualification_pass"] and different["repeat_qualification_pass"]
    )
    assert different["pass"] is False and len(different["attempts"]) == 12
    assert all(not item["pass"] for item in different["attempts"].values())


def forensic_fixture(tmp_path, report):
    """A known weak transfer, with sparse physical call ID 9001.

    Only private native container decoding is replaced. The report's call/input/
    original/variant binding and the actual rational polynomial oracle run.
    """
    arithmetic = report.load(
        "_test_report_real_arithmetic", report.HERE / "assembly_arithmetic.py"
    )
    group = {
        "order": 1,
        "participants": [(1, 2, 0, 0, 0)],
        "extended": [(1, 0, -1.0), (2, 0, 1.0)],
    }
    y, f = [0.25, 0.75] + [0.0] * 158, [-1.0, 1.0] + [0.0] * 158
    values = [9001.0, 0.003, 1.0, 1e6, 1.0, 0.75, 0.75, 1.0, 1.0, 1.0] + y + f
    old = {
        "values": values,
        "comparison": b"original-comparison",
        "csect": [[4.0]],
        "b": [[-4.0, 4.0]],
    }

    def q(value):
        return (((int(value < 0) << 127) | (0x3FFF << 112)) if value else 0).to_bytes(
            16, "little"
        )

    total = [-1, 1] + [0] * 158
    quad = {
        "total": b"".join(map(q, total)),
        "classes": b"".join(q(v) for value in total for v in (value, 0, 0, 0)),
        "products": q(-1) + q(1),
        "running": q(-1) + q(1),
        "absolute": q(1) + q(1) + q(0) * 158,
    }
    new = {
        "values": values + f,
        "call": 9001,
        "conditions": values[1:4],
        "Y": y,
        "original": f,
        "variant": f,
        "comparison": b"variant-comparison",
        "quad": quad,
    }
    assembly = SimpleNamespace(
        NB=arithmetic.NB,
        NQ=arithmetic.NQ,
        parse_original=lambda _: old,
        parse_workspace=lambda _: new,
        legacy_reference=SimpleNamespace(parse_maps=lambda _: [group]),
        _same=arithmetic._same,
        _echo=arithmetic._echo,
        verify_workspace=arithmetic.verify_workspace,
    )
    original = tmp_path / "forensic-original-000000009001.bin"
    variant = tmp_path / "forensic-assembly-000000009001.bin"
    original.write_bytes(b"original")
    variant.write_bytes(b"quad")
    (tmp_path / "baseline-001.bin").write_bytes(b"original")
    (tmp_path / "assembly-baseline-001.bin").write_bytes(b"quad")
    (tmp_path / "used-maps.bin").write_bytes(b"synthetic map")
    (tmp_path / "status.txt").write_text("SUCCESS\n")
    row = [
        9001.0,
        10.0,
        1.0,
        *values[1:4],
        *values[4:10],
        1.0,
        1.0,
        1.0,
        1.0,
        *y,
        *f,
        *f,
    ]
    (tmp_path / "assembly-evaluations.bin").write_bytes(
        struct.pack("<8i", 0x43524145, 1, 160, 496, 0, 0, 0, 0)
        + struct.pack("<496d", *row)
    )
    return assembly, new, old, {"A": [1.0] * 160}, original, variant


def test_sparse_forensic_ids_bind_real_polynomial_oracle(tmp_path):
    report = load_report()
    assembly, _, _, data, _, _ = forensic_fixture(tmp_path, report)
    result = report.forensic_arithmetic(tmp_path, data, assembly)
    assert result["pass"]
    pair = result["pairs"]["forensic-original-000000009001.bin"]
    assert pair["call"] == 9001
    verified = result["workspaces"][pair["arithmetic"]]
    assert verified["pass"]
    assert verified["exact_polynomial"]["rounded"][:2].tolist() == [-1.0, 1.0]
    assert "exact" not in verified["exact_polynomial"]


@pytest.mark.parametrize(
    "tamper", ["call", "original", "variant", "quad", "missing-pair"]
)
def test_forensic_raw_binding_and_exact_arithmetic_tampering_refused(tmp_path, tamper):
    report = load_report()
    assembly, new, old, data, _, variant = forensic_fixture(tmp_path, report)
    if tamper == "call":
        new["call"] = 9002
        new["values"][0] = 9002.0
        old["values"][0] = 9002.0
    elif tamper == "original":
        new["original"] = [2.0] + new["original"][1:]
    elif tamper == "variant":
        new["variant"] = [2.0] + new["variant"][1:]
    elif tamper == "quad":
        raw = bytearray(new["quad"]["total"])
        raw[0] ^= 1
        new["quad"]["total"] = bytes(raw)
    else:
        variant.unlink()
    with pytest.raises(ValueError):
        report.forensic_arithmetic(tmp_path, data, assembly)


def test_failed_incomplete_quad_workspace_stays_explicitly_unavailable(tmp_path):
    report = load_report()
    assembly, _, _, data, original, variant = forensic_fixture(tmp_path, report)
    original.rename(tmp_path / "baseline-failure.bin")
    variant.rename(tmp_path / "assembly-failure.bin")
    (tmp_path / "baseline-001.bin").unlink()
    (tmp_path / "assembly-baseline-001.bin").unlink()
    (tmp_path / "assembly-failure.bin").write_bytes(
        struct.pack("<9i", 0x43524157, 1, 160, *assembly.NB, assembly.NQ, 0)
        + bytes(490 * 8 + assembly.NQ * 16)
    )
    assembly.parse_workspace = lambda _: (_ for _ in ()).throw(
        ValueError("incomplete math status")
    )
    (tmp_path / "status.txt").write_text("FAILURE source nonfinite\n")
    result = report.forensic_arithmetic(tmp_path, data, assembly)
    assert result["pass"] is False
    assert result["unavailable_failed_evaluation"] == {
        "baseline-failure.bin": "incomplete math status"
    }
