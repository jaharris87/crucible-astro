"""Public 160-species I/O oracles; no producer or private data is needed."""

import importlib.util
import json
import struct
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from crucible import trajectory_reference as reference


@pytest.fixture
def case():
    species = np.array(
        [(0, 1), (1, 1)] + [(a // 2, a) for a in range(2, 160)], dtype=np.int64
    )
    y = np.zeros(160)
    y[:2] = [0.1, 0.3]  # Nonunit B=0.4, Q=0.3, Ye=0.75.
    time = np.array([0.0, 0.0037, 0.01, 0.012])
    outputs = np.unique(np.concatenate([np.arange(11) * 0.001, time[1:2]]))
    return {
        "Y0": y,
        "species_Z_A": species,
        "time": time,
        "source_time": time.copy(),
        "T9": np.array([1.0, 2.0, 4.0, 8.0]),
        "rho": np.array([1e6, 2e6, 4e6, 8e6]),
        "requested_time": outputs,
    }


def accepted_rows(case, times):
    rows = np.zeros((len(times), 488), dtype="<f8")
    rows[:, 0], rows[:, 1:161] = times, case["Y0"]
    z, a = case["species_Z_A"].T
    b, q = np.sum(a * case["Y0"]), np.sum(z * case["Y0"])
    rows[:, 481:484] = [b, q, q / b]
    return rows


def load_campaign():
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/campaign.py"
    )
    spec = importlib.util.spec_from_file_location("synthetic_phase2d_campaign", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("wrong_status", [False, True])
def test_synthetic_gate_uses_native_failure_status_and_refuses_wrong_reason(
    tmp_path, monkeypatch, wrong_status
):
    campaign = load_campaign()
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for name in ("trajectory_synthetic", "forcing_synthetic"):
        (bundle / name).write_bytes(b"public synthetic executable identity")

    def fake_run(command, *, cwd, stdout, stderr):
        executable, name = Path(command[0]).name, command[1]
        if executable == "trajectory_synthetic":
            status = "SUCCESS"
            if name == "failed-lu":
                status = "FAILURE LAPACK dgetrf info=1"
            elif name == "nonfinite":
                status = (
                    "FAILURE another reason"
                    if wrong_status
                    else "FAILURE nonfinite computed physical F/assembly workspace"
                )
            (cwd / "status.txt").write_text(status + "\n")
            # Intel's ERROR STOP console output need not contain the status text.
            stdout.write(b"1\n" if status != "SUCCESS" else b"")
            return SimpleNamespace(returncode=int(status != "SUCCESS"))
        (cwd / "fixture-status.txt").write_text(
            "PASS\n" if name == "forcing" else "RUNNING\n"
        )
        refusal = {
            "outside": "Forcing outside closed coverage",
            "nonfinite": "Nonfinite forcing time",
            "nonincreasing": "Nonincreasing forcing",
        }.get(name)
        if refusal:
            stdout.write(refusal.encode() + b"\n")
        return SimpleNamespace(returncode=128 if refusal else 0)

    monkeypatch.setattr(campaign.subprocess, "run", fake_run)
    if wrong_status:
        with pytest.raises(ValueError, match="synthetic prerequisite failed"):
            campaign.synthetic_checks(tmp_path)
    else:
        assert campaign.synthetic_checks(tmp_path)["pass"]
    record = json.loads((tmp_path / "synthetic.json").read_text())
    assert len(record["scenarios"]) == 10
    assert record["pass"] is (not wrong_status)


def test_forcing_exact_stored_bits_at_every_knot_and_independent_linear_interior(case):
    reference.validate_case(case)
    for i, t in enumerate(case["time"]):
        actual = reference.forcing_at(case, t)
        expected = np.array([case["T9"][i], case["rho"][i]])
        np.testing.assert_array_equal(actual.view(np.uint64), expected.view(np.uint64))
    t = 0.002
    fraction = (t - 0.0) / (0.0037 - 0.0)
    np.testing.assert_array_equal(
        reference.forcing_at(case, t),
        [1.0 + fraction * (2.0 - 1.0), 1e6 + fraction * (2e6 - 1e6)],
    )


@pytest.mark.parametrize(
    "time", [True, np.bool_(False), np.nan, np.inf, -1e-9, 0.01200001, "0.005", 1 + 0j]
)
def test_forcing_refuses_invalid_queries_without_endpoint_hold(case, time):
    with pytest.raises(ValueError):
        reference.forcing_at(case, time)


@pytest.mark.parametrize(
    "change",
    [
        "bool",
        "nonfinite",
        "unordered",
        "coverage",
        "negative_condition",
        "clock",
        "duplicate_species",
        "empty_outputs",
    ],
)
def test_case_contract_rejects_invalid_forcing_identity_and_coverage(case, change):
    if change == "bool":
        case["T9"] = np.ones(4, dtype=bool)
    elif change == "nonfinite":
        case["rho"][2] = np.inf
    elif change == "unordered":
        case["time"][2] = case["time"][1]
    elif change == "coverage":
        for key in ("time", "source_time", "T9", "rho"):
            case[key] = case[key][:2]
    elif change == "negative_condition":
        case["rho"][1] = -1.0
    elif change == "clock":
        case["source_time"][1] += 1e-8
    elif change == "duplicate_species":
        case["species_Z_A"][2] = case["species_Z_A"][1]
    else:
        case["requested_time"] = np.array([])
    with pytest.raises(ValueError):
        reference.validate_case(case)


def test_nested_mesh_exact_outputs_knots_horizon_and_uniform_local_subdivision(case):
    base = reference.nested_mesh(case, 0)
    assert base[0] == 0.0 and base[-1] == 0.01
    assert 0.012 not in base
    assert np.isin(case["requested_time"], base).all()
    assert 0.0037 in base
    for level in range(4):
        mesh = reference.nested_mesh(case, level)
        assert np.all(np.diff(mesh) > 0)
        assert np.isin(base, mesh).all()
        assert len(mesh) == (len(base) - 1) * 2**level + 1
        for left, right in zip(base[:-1], base[1:]):
            actual = mesh[(mesh >= left) & (mesh <= right)]
            expected = np.array(
                [left + (right - left) * (j / 2**level) for j in range(2**level)]
                + [right]
            )
            np.testing.assert_array_equal(actual, expected)


@pytest.mark.parametrize("level", [True, np.int64(1), -1, 4, 1.0, "1"])
def test_unknown_mesh_levels_refuse(case, level):
    with pytest.raises(ValueError):
        reference.nested_mesh(case, level)


def test_wire_layout_header_controls_order_and_exact_arrays(case):
    mesh = reference.nested_mesh(case, 2)
    raw = reference.wire_input(case, mode=1, mesh=mesh, tight=True)
    header = struct.unpack_from("<8i2d", raw)
    assert header[:8] == (
        0x43524432,
        1,
        160,
        4,
        len(case["requested_time"]),
        len(mesh),
        1,
        2,
    )
    assert header[8:] == (1e-14, 1e-12)
    values = np.frombuffer(raw, dtype="<f8", offset=48)
    z, a = case["species_Z_A"].T
    expected = np.concatenate(
        [
            z,
            a,
            case["Y0"],
            case["time"],
            case["T9"],
            case["rho"],
            case["requested_time"],
            mesh,
        ]
    )
    np.testing.assert_array_equal(
        values.view(np.uint64), expected.astype("<f8").view(np.uint64)
    )
    assert len(raw) == 48 + expected.size * 8
    control = reference.wire_input(case, mode=0, mesh=np.array([0.0]))
    assert struct.unpack_from("<8i2d", control)[8:] == (1e-13, 1e-11)


@pytest.mark.parametrize(
    "changes",
    [
        dict(mode=True),
        dict(mode=3),
        dict(mesh=np.array([0.0, 0.0])),
        dict(mesh=np.array([False, True])),
        dict(time=True),
        dict(time=np.nan),
        dict(tight="yes"),
    ],
)
def test_wire_refuses_malformed_modes_grids_and_boolean_controls(case, changes):
    kwargs = dict(mode=0, mesh=np.array([0.0]))
    kwargs.update(changes)
    with pytest.raises(ValueError):
        reference.wire_input(case, **kwargs)


def test_accepted_binary_stream_slices_are_independently_known_and_owned(case):
    rows = np.arange(3 * 488, dtype="<f8").reshape(3, 488)
    source = bytearray(rows.tobytes())
    decoded = reference.decode_accepted(source)
    for key, indices in {
        "accepted_t": 0,
        "Y": slice(1, 161),
        "F": slice(161, 321),
        "residual": slice(321, 481),
        "scalar_diag": slice(481, 484),
        "residual_norm": 484,
        "residual_l1": 485,
        "final_projection_l1": 486,
        "cumulative_final_projection_l1": 487,
    }.items():
        np.testing.assert_array_equal(decoded[key], rows[:, indices])
    source[:] = b"\0" * len(source)
    assert decoded["accepted_t"][1] == 488


@pytest.mark.parametrize(
    "raw", [b"", b"0", bytes(488 * 8 - 1), bytes(488 * 8 + 1), bytes(487 * 8)]
)
def test_accepted_binary_stream_refuses_truncation_or_trailing_bytes(raw):
    with pytest.raises(ValueError):
        reference.decode_accepted(raw)


@pytest.mark.parametrize("trailing", [b"", b"partial row"])
def test_interrupted_stream_summary_counts_only_complete_records(
    case, tmp_path, trailing
):
    times = np.array([0.0, 0.0001, 0.0002])
    raw = accepted_rows(case, times).tobytes() + trailing
    (tmp_path / "accepted.bin").write_bytes(raw)
    result = reference.retained_trajectory_summary(tmp_path, case["requested_time"])
    assert result["diagnostic_only"] and result["complete_records"] == 3
    assert result["trailing_bytes"] == len(trailing)
    assert result["last_retained_time"] == 0.0002
    np.testing.assert_array_equal(result["accepted_times"], times)
    assert result["requested_output_occurrences"].tolist() == [1] + [0] * 11
    assert not result["requested_output_complete"]
    assert result["accepted_stream_sha256"] == reference.digest_bytes(raw)
    assert (tmp_path / "accepted.bin").read_bytes() == raw


def test_interrupted_stream_without_complete_row_has_no_achieved_time(case, tmp_path):
    (tmp_path / "accepted.bin").write_bytes(b"incomplete initial row")
    result = reference.retained_trajectory_summary(tmp_path, case["requested_time"])
    assert result["complete_records"] == 0 and result["last_retained_time"] is None
    assert not result["requested_output_complete"]


def test_domain_uses_Q_over_actual_nonunit_B_and_not_raw_Q(case):
    y = case["Y0"].copy()
    # Q=.3, B=.4 -> rho*Ye=15 passes; treating Q as Ye gives6 and fails.
    case["rho"][:] = 20.0
    assert reference.domain_flags(case, np.array([0.0]), y[None, :]).tolist() == [True]
    # With a larger inventory Q=1.125, B=2 -> rho*Ye=8.4375 fails;
    # treating Q as Ye gives16.875 and passes.
    y = np.zeros(160)
    y[1], y[4] = 0.25, 0.4375  # index4 is A4,Z2: B2,Q1.125,Ye.5625.
    case["rho"][:] = 15.0
    assert np.sum(case["species_Z_A"][:, 1] * y) == 2.0
    assert reference.domain_flags(case, np.array([0.0]), y[None, :]).tolist() == [False]


@pytest.mark.parametrize(
    "change", ["negative", "above_one", "nan", "outside_time", "low_T", "rhoYe_upper"]
)
def test_domain_flags_refuse_numerical_and_table_domain_failures(case, change):
    y, t = case["Y0"].copy(), 0.0
    if change == "negative":
        y[3] = -1e-30
    elif change == "above_one":
        y[3] = np.nextafter(1.0, np.inf)
    elif change == "nan":
        y[3] = np.nan
    elif change == "outside_time":
        t = 0.013
    elif change == "low_T":
        case["T9"][0] = np.nextafter(0.01, 0.0)
    else:
        case["rho"][0] = 1e11 / 0.75
    assert not reference.domain_flags(case, np.array([t]), y[None, :])[0]


def test_artifact_manifest_and_reload_preserve_dtype_shape_and_every_byte(tmp_path):
    report = {
        "pass": False,
        "zero_mask": np.array([True, False]),
        "nested": {"signed": np.array([-0.0, 0.0, np.nan], dtype=np.float64)},
        "unavailable": float("inf"),
        "index": np.array([1, 2], dtype=np.int32),
    }
    path = tmp_path / "report.json"
    encoded = reference.artifact_report(path, report)
    assert json.loads(path.read_text()) == encoded
    assert "NaN" not in path.read_text() and "Infinity" not in path.read_text()
    assert encoded["unavailable"] == {"value": None, "status": "NONFINITE_DIAGNOSTIC"}
    artifact = tmp_path / encoded["array_artifact"]["path"]
    assert (
        reference.digest_bytes(artifact.read_bytes())
        == encoded["array_artifact"]["sha256"]
    )
    expected = {
        "report/zero_mask": report["zero_mask"],
        "report/nested/signed": report["nested"]["signed"],
        "report/index": report["index"],
    }
    with np.load(artifact, allow_pickle=False) as file:
        assert set(file.files) == set(expected)
        for key, value in expected.items():
            actual, identity = file[key], encoded["array_artifact"]["arrays"][key]
            assert actual.dtype == value.dtype and actual.shape == value.shape
            assert actual.tobytes() == value.tobytes()
            assert identity == {
                "dtype": value.dtype.str,
                "shape": list(value.shape),
                "sha256": reference.digest_bytes(value.tobytes()),
            }
    reference.checked(path, reference.digest_bytes(path.read_bytes()))
    with pytest.raises(ValueError):
        reference.checked(path, "0" * 64)


def test_artifact_refuses_pickle_dependent_arrays_before_any_persistence(tmp_path):
    path = tmp_path / "unsafe.json"
    with pytest.raises(ValueError):
        reference.artifact_report(path, {"bad": np.array([{"a": 1}], dtype=object)})
    assert not path.exists() and not path.with_suffix(".npz").exists()


def test_campaign_diagnostic_input_uses_exact_requested_state_not_nearest(
    case, tmp_path
):
    campaign = load_campaign()
    template, accepted, target = [
        tmp_path / name for name in ("template.bin", "accepted.bin", "diagnostic.bin")
    ]
    template.write_bytes(reference.wire_input(case, mode=0, mesh=np.array([0.0])))
    rows = accepted_rows(case, np.array([0.0, 0.005, 0.01]))
    rows[1, 1:161] *= 0.5
    accepted.write_bytes(rows.tobytes())
    campaign.diagnostic_input(template, accepted, 0.005, target)
    data = target.read_bytes()
    header = struct.unpack_from("<8i2d", data)
    assert header[4:7] == (1, 1, 2)
    values = np.frombuffer(data, dtype="<f8", offset=48)
    np.testing.assert_array_equal(
        values[320:480].view(np.uint64), rows[1, 1:161].view(np.uint64)
    )
    np.testing.assert_array_equal(values[-2:], [0.005, 0.005])
    before = target.read_bytes()
    with pytest.raises(ValueError):
        campaign.diagnostic_input(template, accepted, np.nextafter(0.005, 1.0), target)
    assert target.read_bytes() == before
    accepted.write_bytes(np.concatenate([rows, rows[1:2]]).tobytes())
    with pytest.raises(ValueError):
        campaign.diagnostic_input(template, accepted, 0.005, target)


def test_mock_process_attempt_retains_logs_and_verifies_completed_bytes_on_resume(
    tmp_path, monkeypatch
):
    campaign = load_campaign()
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "network").mkdir()
    (bundle / "helm_table.dat").write_bytes(b"public synthetic table placeholder")
    executable = bundle / "trajectory_driver"
    executable.write_bytes(b"never executed")
    source = tmp_path / "input.bin"
    source.write_bytes(b"public synthetic input")
    spec = {
        "name": "development-control",
        "mode": 0,
        "input": source.name,
        "input_sha256": campaign.digest(source),
    }
    calls = []

    def fake_run(command, *, cwd, stdout, stderr):
        calls.append(command)
        stdout.write(b"synthetic process output\n")
        (cwd / "control.bin").write_bytes(b"public synthetic control")
        (cwd / "status.txt").write_text("SUCCESS\n")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(campaign.subprocess, "run", fake_run)
    record = campaign.run_attempt(tmp_path, spec, executable, [], resume=False)
    assert record["completed"] and record["returncode"] == 0 and len(calls) == 1
    assert "control.bin" in record["files"] and "process.log" in record["files"]
    assert campaign.run_attempt(tmp_path, spec, executable, [], resume=True) == record
    assert len(calls) == 1
    (tmp_path / "attempts/development-control/control.bin").write_bytes(b"changed")
    with pytest.raises(ValueError, match="artifact changed"):
        campaign.run_attempt(tmp_path, spec, executable, [], resume=True)
    assert len(calls) == 1


def test_analyzer_cannot_pass_when_all_controls_and_jacobians_are_omitted(
    case, tmp_path
):
    """Success-looking trajectory files cannot replace the accepted population."""
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    specs, immutable = [], {}
    for label in ("development", "validation"):
        case_path = inputs / (label + ".npz")
        np.savez(case_path, **case)
        immutable[str(case_path.relative_to(tmp_path))] = reference.digest_bytes(
            case_path.read_bytes()
        )
        for level, tight in [(j, False) for j in range(4)] + [(3, True)]:
            name = label + ("-tight" if tight else "-L" + str(level))
            mesh = reference.nested_mesh(case, level)
            work = tmp_path / "attempts" / name
            work.mkdir(parents=True)
            (work / "accepted.bin").write_bytes(accepted_rows(case, mesh).tobytes())
            (work / "status.txt").write_text("SUCCESS\n")
            files = {
                p.name: {
                    "sha256": reference.digest_bytes(p.read_bytes()),
                    "bytes": p.stat().st_size,
                }
                for p in work.iterdir()
            }
            reference.save_json(
                work / "attempt.json",
                {"returncode": 0, "completed": True, "files": files},
            )
            specs.append(
                {"name": name, "case": label, "mode": 1, "level": level, "tight": tight}
            )
    prepared = {
        "protocol_sha256": reference.PROTOCOL_SHA256,
        "annex_sha256": reference.ANNEX_SHA256,
        "attempts": specs,
        "immutable_files": immutable,
    }
    reference.save_json(tmp_path / "prepared.json", prepared)
    reference.save_json(
        tmp_path / "campaign.json",
        {
            "complete": True,
            "prepared_sha256": reference.digest_bytes(
                (tmp_path / "prepared.json").read_bytes()
            ),
        },
    )
    try:
        report = reference.analyze(tmp_path)
    except ValueError as exc:
        assert "population" in str(exc)
        return  # Refusing the invalid declared population is also fail-closed.
    assert not report["pass"], (
        "omitted controls/Jacobian diagnostics must prevent a campaign pass"
    )


def public_plan():
    attempts = []
    for case in ("development", "validation"):
        for suffix, mode, level, tight, when in (
            [("control", 0, 0, False, 0.0)]
            + [("L" + str(j), 1, j, False, 0.0) for j in range(4)]
            + [("tight", 1, 3, True, 0.0)]
            + [("J" + str(j), 2, 3, False, t) for j, t in enumerate((0.0, 0.005, 0.01))]
        ):
            attempts.append(
                {
                    "name": case + "-" + suffix,
                    "case": case,
                    "mode": mode,
                    "level": level,
                    "tight": tight,
                    "time": when,
                }
            )
    return {"attempts": attempts}


def test_plan_requires_both_cases_exact_nine_attempts_each_and_frozen_controls():
    plan = public_plan()
    reference.validate_plan(plan)
    assert len(plan["attempts"]) == 18
    for key, value in [
        ("mode", True),
        ("level", 1.0),
        ("tight", 0),
        ("time", 0.001),
        ("case", "test"),
    ]:
        changed = public_plan()
        changed["attempts"][0][key] = value
        with pytest.raises(ValueError):
            reference.validate_plan(changed)
    changed = public_plan()
    changed["attempts"][-1] = changed["attempts"][0].copy()
    with pytest.raises(ValueError, match="population"):
        reference.validate_plan(changed)


@pytest.mark.parametrize(
    "field,value", [(0, 0), (1, 9), (2, 159), (3, 0), (4, 0), (5, 0)]
)
def test_diagnostic_input_rejects_corrupt_template_headers_before_write(
    case, tmp_path, field, value
):
    campaign = load_campaign()
    data = bytearray(reference.wire_input(case, mode=0, mesh=np.array([0.0])))
    struct.pack_into("<i", data, field * 4, value)
    template, accepted, target = [
        tmp_path / name for name in ("bad.bin", "accepted.bin", "target.bin")
    ]
    template.write_bytes(data)
    accepted.write_bytes(accepted_rows(case, np.array([0.0, 0.005, 0.01])).tobytes())
    with pytest.raises(ValueError):
        campaign.diagnostic_input(template, accepted, 0.005, target)
    assert not target.exists()


def test_diagnostic_input_rejects_truncated_template_header(case, tmp_path):
    campaign = load_campaign()
    template, accepted, target = [
        tmp_path / name for name in ("bad.bin", "accepted.bin", "target.bin")
    ]
    template.write_bytes(b"bad")
    accepted.write_bytes(accepted_rows(case, np.array([0.0, 0.005, 0.01])).tobytes())
    with pytest.raises(ValueError):
        campaign.diagnostic_input(template, accepted, 0.005, target)
    assert not target.exists()


@pytest.mark.parametrize("failure", ["nonzero", "exception"])
def test_mock_failed_process_preserves_partial_outputs_without_reexecution(
    tmp_path, monkeypatch, failure
):
    campaign = load_campaign()
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "network").mkdir()
    (bundle / "helm_table.dat").write_bytes(b"public placeholder")
    executable = bundle / "trajectory_driver"
    executable.write_bytes(b"not executed")
    source = tmp_path / "input.bin"
    source.write_bytes(b"synthetic input")
    spec = {
        "name": "development-L0",
        "mode": 1,
        "input": source.name,
        "input_sha256": campaign.digest(source),
    }
    calls = []

    def fake_run(command, *, cwd, stdout, stderr):
        calls.append(command)
        stdout.write(b"partial public diagnostic\n")
        (cwd / "accepted.bin").write_bytes(b"partial stream retained")
        if failure == "exception":
            raise OSError("synthetic process launch failure")
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(campaign.subprocess, "run", fake_run)
    result = campaign.run_attempt(tmp_path, spec, executable, [], resume=False)
    assert result[
        "completed"
    ]  # Process accounting completion is not numerical success.
    assert result["status"] == ("EXCEPTION" if failure == "exception" else "FAILED")
    assert result["returncode"] == (None if failure == "exception" else 7)
    accepted = tmp_path / "attempts/development-L0/accepted.bin"
    assert accepted.read_bytes() == b"partial stream retained"
    assert result["files"]["accepted.bin"]["sha256"] == campaign.digest(accepted)
    assert campaign.run_attempt(tmp_path, spec, executable, [], resume=True) == result
    assert len(calls) == 1
