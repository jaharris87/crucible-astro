"""Public exclusion and recomputation oracles; no native or private input use."""

import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def load_report():
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/assembly_report.py"
    )
    spec = importlib.util.spec_from_file_location("assembly_report_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def population(tmp_path):
    plan = []
    for command, stage in (
        ("identity-3", "identity"),
        ("identity-1", "identity"),
        ("derivative", "derivative"),
    ):
        for state in (
            "development-initial",
            "validation-initial",
            "development-newton300",
        ):
            plan.append({"name": state + "-" + command, "stage": stage, "state": state})
    for stage in ("standard", "tight"):
        for case in ("development", "validation"):
            plan.append(
                {"name": case + "-" + stage, "stage": stage, "state": case + "-initial"}
            )
    records = [{**s, "status": "RETURNED", "completed": True} for s in plan]
    outcomes = {s["name"]: {"pass": True, "software_pass": True} for s in plan}
    return {"attempts": plan}, {"attempts": records, "_root": str(tmp_path)}, outcomes


def test_conditional_tight_exclusion_keeps_failed_standard_case(tmp_path):
    report = load_report()
    prepared, campaign, outcomes = population(tmp_path)
    outcomes["development-standard"]["pass"] = False
    for record in campaign["attempts"][-2:]:
        record.update(
            status="CONDITIONALLY_UNATTEMPTED",
            completed=False,
            skip_reason="BOTH_STANDARD_ATTEMPTS_DID_NOT_PASS",
        )
        outcomes[record["name"]]["pass"] = False
    assert report._stage_checks(prepared, campaign, outcomes) == {
        "identity": True,
        "derivative": True,
        "standard": False,
    }
    assert len(outcomes) == 13
    assert outcomes["development-standard"]["software_pass"]


@pytest.mark.parametrize("failed_stage", ["identity", "derivative", "standard"])
def test_successful_exit_records_cannot_bypass_scientific_prerequisite(
    tmp_path, failed_stage
):
    report = load_report()
    prepared, campaign, outcomes = population(tmp_path)
    first = next(s for s in prepared["attempts"] if s["stage"] == failed_stage)
    outcomes[first["name"]]["pass"] = False
    with pytest.raises(ValueError, match="before|without"):
        report._stage_checks(prepared, campaign, outcomes)


def test_conditional_record_cannot_hide_executed_directory(tmp_path):
    report = load_report()
    prepared, campaign, outcomes = population(tmp_path)
    outcomes["development-standard"]["pass"] = False
    for record in campaign["attempts"][-2:]:
        record.update(
            status="CONDITIONALLY_UNATTEMPTED",
            completed=False,
            skip_reason="BOTH_STANDARD_ATTEMPTS_DID_NOT_PASS",
        )
    (tmp_path / "attempts/development-tight").mkdir(parents=True)
    with pytest.raises(ValueError, match="execution directory"):
        report._stage_checks(prepared, campaign, outcomes)


def test_exact_display_masks_and_signed_zero_remain_numeric():
    report = load_report()
    result = report.numeric_details(
        {
            "exact": [{"numerator_hex": "0", "denominator_hex": "1"}] * 3,
            "rounded": [-0.0, None, 0.5],
        }
    )
    assert result["rounded"].dtype == np.float64
    assert result["rounded_finite"].tolist() == [True, False, True]
    assert np.signbit(result["rounded"][0])
    assert np.isnan(result["rounded"][1])
    assert result["exact"][0]["denominator_hex"] == "1"


def test_missing_campaign_keeps_all_declared_unattempted_processes(tmp_path):
    report = load_report()
    prepared, _, _ = population(tmp_path)
    (tmp_path / "prepared.json").write_text(json.dumps(prepared))
    actual = report.analyze(tmp_path)
    assert actual["software_pass"] is actual["qualification_pass"] is False
    assert actual["call_counts_complete"] is False
    assert len(actual["attempts"]) == 13
    assert {a["status"] for a in actual["attempts"].values()} == {"UNATTEMPTED"}
    assert "campaign.json" in actual["errors"][0]


def oracle():
    return {
        "software_pass": True,
        "qualification_pass": False,
        "trajectory_reference_qualified": False,
        "values": np.array([0.0, -0.0, 0.5], dtype="<f8"),
        "finite": np.array([True, True, True]),
    }


def test_fresh_reload_preserves_numeric_bits_and_refuses_overwrite(
    tmp_path, monkeypatch
):
    report = load_report()
    monkeypatch.setattr(report, "analyze", lambda root: oracle())
    report.artifacts.artifact_report(tmp_path / report.REPORT, oracle())
    actual = report.reload_report(tmp_path)
    assert actual["values"].tobytes() == oracle()["values"].tobytes()
    assert actual["trajectory_reference_qualified"] is False
    with pytest.raises(ValueError, match="already exists"):
        report.artifacts.artifact_report(tmp_path / report.REPORT, oracle())


def test_updated_serialization_hashes_do_not_replace_raw_recomputation(
    tmp_path, monkeypatch
):
    report = load_report()
    monkeypatch.setattr(report, "analyze", lambda root: oracle())
    report.artifacts.artifact_report(tmp_path / report.REPORT, oracle())
    path = tmp_path / report.REPORT
    metadata = json.loads(path.read_text())
    artifact = metadata["array_artifact"]
    npz = tmp_path / artifact["path"]
    with np.load(npz, allow_pickle=False) as file:
        arrays = {key: file[key].copy() for key in file.files}
    arrays["report/values"][0] = 1.0
    np.savez(npz, **arrays)
    artifact["sha256"] = report.artifacts.digest_bytes(npz.read_bytes())
    artifact["arrays"]["report/values"]["sha256"] = report.artifacts.digest_bytes(
        arrays["report/values"].tobytes()
    )
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="recomputed array bytes"):
        report.reload_report(tmp_path)


def test_saved_claim_cannot_promote_unqualified_result(tmp_path, monkeypatch):
    report = load_report()
    monkeypatch.setattr(report, "analyze", lambda root: oracle())
    report.artifacts.artifact_report(tmp_path / report.REPORT, oracle())
    path = tmp_path / report.REPORT
    metadata = json.loads(path.read_text())
    metadata["trajectory_reference_qualified"] = True
    path.write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="recomputed report"):
        report.reload_report(tmp_path)


@pytest.mark.parametrize("ordinary_failure", [False, True])
@pytest.mark.parametrize("dependency_tamper", [False, True])
def test_report_aggregates_all_plans_and_keeps_software_separate_from_qualification(
    tmp_path, monkeypatch, ordinary_failure, dependency_tamper
):
    """Mock only already-tested science gates; this is no native workflow claim."""
    report = load_report()
    prepared, campaign, _ = population(tmp_path)
    source = "native-XNet-b64-productsum113-b64-v1"

    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    prepared.update(
        protocol_sha256="f" * 64,
        annex_sha256="a" * 64,
        source_commit="1" * 40,
        source_tree="2" * 40,
        immutable_files={
            "assembly_arithmetic.py": digest(report.HERE / "assembly_arithmetic.py"),
            "rhs_reference/arithmetic.py": digest(
                report.HERE.parent / "rhs_reference/arithmetic.py"
            ),
            "rhs_reference/reference.py": digest(
                report.HERE.parent / "rhs_reference/reference.py"
            ),
        },
    )
    if dependency_tamper:
        prepared["immutable_files"]["rhs_reference/arithmetic.py"] = "0" * 64
    (tmp_path / "prepared.json").write_text(json.dumps(prepared))
    decisions = {}
    calls = 0
    for record in campaign["attempts"]:
        if ordinary_failure and record["stage"] == "tight":
            record.update(
                status="CONDITIONALLY_UNATTEMPTED",
                completed=False,
                skip_reason="BOTH_STANDARD_ATTEMPTS_DID_NOT_PASS",
            )
            continue
        fail = ordinary_failure and record["name"] == "development-standard"
        decision = {
            "pass": not fail,
            "software_pass": True,
            "fatal": False,
            "ordinary_numerical_failure": fail,
        }
        decisions[record["name"]] = decision
        record["science_gate"] = decision
        work = tmp_path / "attempts" / record["name"]
        work.mkdir(parents=True)
        (work / "counters.json").write_text('{"rhs":1}')
        (work / "assembly-counters.json").write_text('{"fresh_requests":1}')
        calls += 1
    campaign.pop("_root")
    campaign.update(
        schema="crucible.phase2d.assembly-campaign.v1",
        numerical_source=source,
        prepared_sha256=digest(tmp_path / "prepared.json"),
        build={},
        complete=True,
        qualification_pass=not ordinary_failure,
        physical_rhs_calls=calls,
        guarded_fresh_requests=calls,
    )
    (tmp_path / "campaign.json").write_text(json.dumps(campaign))
    contract = SimpleNamespace(
        SOURCE_NAME=source,
        MAX_RHS=10398034,
        digest=digest,
        validate_prepared=lambda root, prepared: None,
        build_identities=lambda root: {},
    )

    def gate(root, spec, result):
        return decisions[spec["name"]].copy()

    gates = SimpleNamespace(
        WORKSPACES={},
        precision_gate=lambda root: {"software_pass": True, "pass": True},
        identity_attempt_gate=gate,
        derivative_attempt_gate=gate,
        first_step_gate=gate,
    )
    monkeypatch.setattr(
        report,
        "load_module",
        lambda name, path: gates if path.name == "assembly_arithmetic.py" else contract,
    )
    actual = report.analyze(tmp_path)
    if dependency_tamper:
        assert actual["software_pass"] is actual["qualification_pass"] is False
        assert "arithmetic dependency differs" in actual["errors"][0]
        assert len(actual["attempts"]) == 13
        return
    assert actual["errors"] == []
    assert actual["software_pass"] is True
    assert actual["qualification_pass"] is not ordinary_failure
    assert actual["trajectory_reference_qualified"] is False
    assert actual["physical_rhs_calls_observed"] == calls
    assert len(actual["attempts"]) == 13
    if ordinary_failure:
        assert actual["attempts"]["development-standard"]["recomputed"]["pass"] is False
        assert (
            actual["attempts"]["validation-tight"]["status"]
            == "CONDITIONALLY_UNATTEMPTED"
        )
