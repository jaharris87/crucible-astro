"""Public offline wire/arithmetic oracles; no compiler or producer is invoked."""

import copy
import importlib.util
import json
import os
import struct
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
import pytest

MODULE = (
    Path(__file__).resolve().parents[1]
    / "experiments/trajectory_reference/diagnostic_report.py"
)
SPEC = importlib.util.spec_from_file_location("public_diagnostic_report", MODULE)
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def baseline_bytes(call=1):
    count = 10 + 320 + sum(report.NC) + sum(report.NB)
    values = np.zeros(count, dtype="<f8")
    values[:10] = [call, 0.0, 1.0, 1e6, 0.4, 0.3, 0.75, 1.0, 2.0, 3.0]
    values[10:12] = [0.1, 0.3]
    return (
        struct.pack("<12i", 0x43524442, 1, 160, *report.NC, *report.NB, 10240)
        + values.tobytes()
        + bytes(10240 * 4)
    )


def test_baseline_fixed_header_slices_and_independent_repeated_call_bits():
    parsed = report.parse_baseline(baseline_bytes())
    np.testing.assert_array_equal(parsed["conditions"], [0.0, 1.0, 1e6])
    np.testing.assert_array_equal(parsed["Y"][:2], [0.1, 0.3])
    assert parsed["Y"].shape == (160,) and parsed["F"].shape == (160,)
    assert tuple(map(len, parsed["csect"])) == report.NC
    assert tuple(map(len, parsed["b"])) == report.NB
    assert report.bits_equal(
        parsed["comparison_bytes"],
        report.parse_baseline(baseline_bytes(call=3))["comparison_bytes"],
    )
    changed = bytearray(baseline_bytes())
    changed[48 + 8 * 170] ^= 1
    assert not report.bits_equal(
        parsed["comparison_bytes"], report.parse_baseline(changed)["comparison_bytes"]
    )


@pytest.mark.parametrize(
    "mutation", ["magic", "version", "order", "length", "nan", "call"]
)
def test_baseline_refuses_wrong_layout_and_nonfinite_payload(mutation):
    data = bytearray(baseline_bytes())
    if mutation == "magic":
        struct.pack_into("<i", data, 0, 0)
    elif mutation == "version":
        struct.pack_into("<i", data, 4, 2)
    elif mutation == "order":
        struct.pack_into("<i", data, 12, 1345)
    elif mutation == "length":
        data.pop()
    elif mutation == "nan":
        struct.pack_into("<d", data, 48 + 8 * 200, np.nan)
    else:
        struct.pack_into("<d", data, 48, 1.5)
    with pytest.raises(ValueError):
        report.parse_baseline(data)


def exact_quotient(F0, F1, F2, d1, d2):
    d1, d2 = Q(d1), Q(d2)
    w1 = -d2 / (d1 * (d1 - d2))
    w2 = -d1 / (d2 * (d2 - d1))
    return np.array(
        [
            float(
                w1 * (Q(float(f1)) - Q(float(f0))) + w2 * (Q(float(f2)) - Q(float(f0)))
            )
            for f0, f1, f2 in zip(F0, F1, F2, strict=True)
        ]
    )


def test_nonuniform_difference_quotient_has_independent_quadratic_oracle():
    # f(x)=x^2+3x+2 at x=1: derivative5, on asymmetric nodesx-1/4,x+1/2.
    result = report.difference_quotient(
        np.array([6.0]),
        np.array([0.75**2 + 3 * 0.75 + 2]),
        np.array([1.5**2 + 3 * 1.5 + 2]),
        -0.25,
        0.5,
    )
    assert result["value"][0] == 5.0
    assert result["allowance"][0] > 0
    report.compare_bound(np.array([5.0]), result["value"], result["allowance"])
    with pytest.raises(ValueError):
        report.compare_bound(np.array([5.01]), result["value"], result["allowance"])


def test_quotient_DAZ_loss_is_amplified_by_weights_without_relaxing_scientific_threshold():
    # A native DAZ subtraction can lose this subnormal F before a1e100 weight.
    result = report.difference_quotient(
        np.zeros(1), np.array([-1e-320]), np.array([1e-320]), -1e-100, 1e-100
    )
    assert abs(result["value"][0]) > 1e-221
    assert result["allowance"][0] > abs(result["value"][0])
    report.compare_bound(np.zeros(1), result["value"], result["allowance"])
    with pytest.raises(ValueError):
        report.compare_bound(np.ones(1), result["value"], result["allowance"])


@pytest.mark.parametrize(
    "d1,d2", [(0.0, 1.0), (1.0, 1.0), (1e-320, 2e-320), (np.inf, 1.0), (1e200, 2e200)]
)
def test_unsupported_weight_arithmetic_never_passes(d1, d2):
    with pytest.raises(ValueError):
        report.difference_quotient(np.zeros(1), np.ones(1), np.ones(1), d1, d2)


def fd_fixture():
    y = np.array([0.25, 0.5])
    condition = np.array([0.0, 1.0, 1e6])
    a = np.array([1, 4])

    def f(x):
        return np.array([x[0] ** 2 + 2 * x[1], 3 * x[0] - x[1] ** 2])

    evaluations = []

    def evaluate(x):
        i = len(evaluations) + 1
        F = f(x)
        evaluations.append(np.r_[float(i), condition, x, F])
        return i, F

    evaluate(y)
    matrices = []
    statuses = []
    selections = []
    probes = []
    bases = []
    for k, factor in enumerate((0.1, 1.0, 10.0, 100.0), 1):
        before = len(evaluations)
        _, f0 = evaluate(y)
        matrix = np.zeros((2, 2))
        bases.append(np.r_[float(k), condition, y])
        for col in range(2):
            delta = (
                np.finfo(float).eps ** (1 / 3)
                * max(abs(y[col]), 1e-8 / a[col])
                * factor
            )
            p1, p2 = y.copy(), y.copy()
            p1[col] -= delta
            p2[col] += delta
            d1, d2 = p1[col] - y[col], p2[col] - y[col]
            i1, F1 = evaluate(p1)
            i2, F2 = evaluate(p2)
            matrix[:, col] = exact_quotient(f0, F1, F2, d1, d2)
            probes.append(
                [k, col + 1, 0, delta, d1, d2, p1[col], p2[col], 1, 1, i1, i2]
            )
            selections.append([k, col + 1, 0, 0, d1, d2])
        evaluate(y)
        matrices.append(matrix)
        statuses.append([factor, k, 1, before, len(evaluations)])
    return [
        np.array(v)
        for v in (matrices, statuses, selections, probes, bases, evaluations)
    ] + [a]


def test_all_four_finite_difference_matrices_bind_to_retained_F_and_actual_offsets():
    fixture = fd_fixture()
    checked = report.verify_fd(*fixture)
    assert checked["complete"].tolist() == [True] * 4
    assert checked["next_call"] == 26
    for k in range(4):
        # Independent polynomial derivative remains a scientific comparison, notserialization input.
        np.testing.assert_allclose(fixture[0][k], [[0.5, 2], [3, -1]], rtol=1e-7)


@pytest.mark.parametrize(
    "mutation", ["matrix", "probe_Y", "F_binding", "factor", "FID", "order", "halving"]
)
def test_corrupted_matrix_state_F_and_order_bindings_are_rejected(mutation):
    fixture = fd_fixture()
    if mutation == "matrix":
        fixture[0][0, 0, 0] += 0.01
    elif mutation == "probe_Y":
        fixture[3][0, 6] += 0.001
    elif mutation == "F_binding":
        fixture[5][2, -1] += 0.001
    elif mutation == "factor":
        fixture[1][0, 0] = 1.0
    elif mutation == "FID":
        fixture[3][0, 10] = 1.0
    elif mutation == "order":
        fixture[4][0, 0] = 2.0
    else:
        fixture[2][0, 3] = 9.0
    with pytest.raises(ValueError):
        report.verify_fd(*fixture)


def direction_fixture():
    n = 2
    y = np.array([0.25, 0.5])
    condition = np.array([0.0, 1.0, 1e6])
    a = np.array([1, 4])
    J = np.array([[1.0, 2.0], [-1.0, 3.0]])

    def f(x):
        return np.array([x[0] + 2 * x[1], -x[0] + 3 * x[1]])

    base = {"Y": y, "F": f(y), "conditions": condition}
    matrices = np.array(
        [J, 2 * J, J, J]
    )  # Factor-one is intentionally scientifically wrong.
    scale = np.maximum(abs(y), 1e-8 / a)
    directions = np.array([scale, [scale[0], 0.0], [scale[0], 0.0]])
    evaluations = [np.r_[1.0, condition, y, f(y)]]
    attempts = []
    sweep = np.zeros((3, 9, 6 + 8 * n))
    jv = np.zeros((n, 3, 4))
    for direction, v in enumerate(directions):
        for k, matrix in enumerate(matrices):
            jv[:, direction, k] = matrix @ v
        for mi, m in enumerate(report.metrics.JACOBIAN_MULTIPLIERS):
            p1, p2 = y - m * v, y + m * v
            F1, F2 = f(p1), f(p2)
            for p, F in ((p1, F1), (p2, F2)):
                evaluations.append(np.r_[float(len(evaluations) + 1), condition, p, F])
            attempts.append(np.r_[direction + 1, mi + 1, 0, -m, m, 1, 1, p1, p2])
            dv = exact_quotient(base["F"], F1, F2, -m, m)
            sweep[direction, mi] = np.r_[
                direction + 1,
                mi + 1,
                0,
                1,
                -m,
                m,
                v,
                jv[:, direction, 1],
                dv,
                p1 - y,
                p2 - y,
                base["F"],
                F1,
                F2,
            ]
    evaluations.append(np.r_[float(len(evaluations) + 1), condition, y, f(y)])
    return matrices, sweep, np.array(attempts), jv, base, a, 0, np.array(evaluations), 2


def test_scientific_direction_failure_is_retained_with_all_four_factors():
    checked = report.verify_directions(*direction_fixture())
    outcomes = checked["agreement_by_direction_then_factor"]
    assert len(outcomes) == 3 and all(len(factors) == 4 for factors in outcomes)
    assert all(not factors[1]["pass"] for factors in outcomes)
    assert all(
        factors[0]["pass"] and factors[2]["pass"] and factors[3]["pass"]
        for factors in outcomes
    )
    assert checked["directions"][1, 1] == 0
    assert checked["recomputed_Dv"].shape == (3, 9, 2)


@pytest.mark.parametrize("mutation", ["F", "Y", "direction", "Jv", "baseline", "Dv"])
def test_direction_binding_corruption_rejected(mutation):
    fixture = list(direction_fixture())
    if mutation == "F":
        fixture[1][0, 0, -1] += 0.01
    elif mutation == "Y":
        fixture[2][0, 7] += 0.01
    elif mutation == "direction":
        fixture[1][0, 0, 6] += 0.01
    elif mutation == "Jv":
        fixture[3][0, 0, 0] += 0.01
    elif mutation == "baseline":
        fixture[1][0, 0, 16] += 0.01
    else:
        fixture[1][0, 0, 10] += 0.01
    with pytest.raises(ValueError):
        report.verify_directions(*fixture)


def linear_bytes(n=2, lu_info=0):
    y = np.array([0.25, 0.75])
    old = np.array([0.5, 0.5])
    f = np.array([-0.25, 0.25])
    h = 1.0
    M = np.array([[2.0, 1.0], [1.0, 3.0]])
    rhs = (old - y) / h + f
    delta = np.zeros(n) if lu_info == 0 else np.full(n, np.nan)
    values = np.concatenate(
        [[h], y, old, f, M.ravel(order="F"), rhs, np.eye(n).ravel(order="F"), delta]
    )
    return (
        struct.pack("<5i", 0x4352444C, 1, n, lu_info, 0 if lu_info == 0 else -999)
        + values.astype("<f8").tobytes()
        + np.array([1, 2], dtype="<i4").tobytes()
    )


def test_linear_payload_column_order_and_exact_offline_equation():
    record = report.parse_linear(linear_bytes(), n=2)
    np.testing.assert_array_equal(record["M"], [[2, 1], [1, 3]])
    base = {"Y": record["Y"], "F": record["F"]}
    checked = report.verify_linear(
        record, np.eye(2) - record["M"], base, record["Yold"], 1.0, np.array([1, 4])
    )
    assert checked["lapack_success"]
    assert report.qvalues(checked["linear_arithmetic"]["exact"]) == [0, 0]
    assert report.qvalues(checked["baseline_BE"]["exact"]) == [0, 0]
    assert not checked["linear_arithmetic"]["scientific_accuracy_acceptance"]


@pytest.mark.parametrize(
    "mutation",
    ["magic", "length", "pivot", "nan_M", "nonzero_solve", "missing_correction"],
)
def test_linear_malformed_and_unavailable_outputs_never_pass(mutation):
    data = bytearray(linear_bytes())
    if mutation == "magic":
        struct.pack_into("<i", data, 0, 0)
    elif mutation == "length":
        data.pop()
    elif mutation == "pivot":
        struct.pack_into("<i", data, len(data) - 4, 0)
    elif mutation == "nan_M":
        struct.pack_into("<d", data, 20 + 7 * 8, np.nan)
    elif mutation == "nonzero_solve":
        struct.pack_into("<i", data, 16, 3)
    else:
        struct.pack_into("<d", data, 20 + (1 + 5 * 2 + 2 * 4 - 1) * 8, np.nan)
    with pytest.raises(ValueError):
        report.parse_linear(data, n=2)


def test_finite_singular_LU_is_explicit_outcome_with_unavailable_correction():
    record = report.parse_linear(linear_bytes(lu_info=1), n=2)
    assert (
        record["lu_info"] == 1
        and record["solve_info"] == -999
        and np.isnan(record["delta"]).all()
    )


def test_wrong_species_and_same_sized_wrong_maps_cannot_hide_behind_updated_hashes(
    tmp_path,
):
    work = tmp_path / "attempts" / "public-repeat-1"
    work.mkdir(parents=True)
    input_bytes = bytes(48 + 320 * 8)
    state = {"input": input_bytes}
    spec = {
        "name": "public-repeat-1",
        "input_sha256": report.common.digest_bytes(input_bytes),
    }
    (work / "input.bin").write_bytes(input_bytes)
    (work / "status.txt").write_text("SUCCESS\n")
    (work / "species.bin").write_bytes(bytes([1]) + bytes(320 * 8 - 1))
    (work / "used-maps.bin").write_bytes(b"wrong same-sized map")

    def record():
        saved = {
            "completed": True,
            "returncode": 0,
            "input_sha256": spec["input_sha256"],
            "files": {
                p.name: {
                    "bytes": p.stat().st_size,
                    "sha256": report.common.digest_bytes(p.read_bytes()),
                }
                for p in work.iterdir()
                if p.name != "attempt.json"
            },
        }
        (work / "attempt.json").write_text(json.dumps(saved))
        return saved

    with pytest.raises(ValueError, match="species"):
        report._attempt(tmp_path, spec, record(), state, b"right same-sized map", {})
    (work / "species.bin").write_bytes(input_bytes[48:])
    with pytest.raises(ValueError, match="native map"):
        report._attempt(tmp_path, spec, record(), state, b"right same-sized map", {})


def test_raw_inventory_requires_exact_membership_hashes_and_safe_paths(tmp_path):
    (tmp_path / "input.bin").write_bytes(b"public")
    identity = report.common.digest_bytes(b"public")
    report._checked_inventory(tmp_path, {"input.bin": identity}, exact=["input.bin"])
    with pytest.raises(ValueError):
        report._checked_inventory(tmp_path, {"input.bin": "0" * 64})
    with pytest.raises(ValueError):
        report._checked_inventory(
            tmp_path, {"input.bin": identity}, exact=["input.bin", "missing.bin"]
        )
    with pytest.raises(ValueError):
        report._checked_inventory(tmp_path, {"../outside": identity})


def test_missing_campaign_accounts_for_all_nine_and_never_claims_reference(tmp_path):
    result = report.analyze(tmp_path)
    assert not result["software_pass"] and not result["trajectory_reference_qualified"]
    assert len(result["attempts"]) == 9 and all(
        not x["software_pass"] for x in result["attempts"].values()
    )
    assert result["errors"]


def test_save_reload_compares_numeric_dtype_shape_and_every_byte(tmp_path, monkeypatch):
    expected = {
        "software_pass": False,
        "trajectory_reference_qualified": False,
        "signed": np.array([-0.0, 0.0, np.nan]),
        "mask": np.array([True, False]),
        "index": np.array([1, 2], dtype=np.int32),
    }
    monkeypatch.setattr(report, "analyze", lambda root: copy.deepcopy(expected))
    report.common.artifact_report(tmp_path / "diagnostic-verification.json", expected)
    restored = report.reload_report(tmp_path)
    assert report.bits_equal(restored["signed"], expected["signed"])
    manifest = json.loads((tmp_path / "diagnostic-verification.json").read_text())
    npz = tmp_path / manifest["array_artifact"]["path"]
    npz.write_bytes(npz.read_bytes() + b"corruption")
    with pytest.raises(ValueError):
        report.reload_report(tmp_path)


def test_verify_and_reload_in_separate_python_processes_remain_offline_and_fail_closed(
    tmp_path,
):
    environment = dict(os.environ)
    for command in ("verify", "reload"):
        result = subprocess.run(
            [sys.executable, "-B", str(MODULE), command, str(tmp_path)],
            env=environment,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1, result.stderr
        assert json.loads(result.stdout) == {
            "software_pass": False,
            "trajectory_reference_qualified": False,
        }
    saved = json.loads((tmp_path / "diagnostic-verification.json").read_text())
    assert len(saved["attempts"]) == 9 and not saved["software_pass"]


def test_branch_replay_binds_old_selectors_and_does_not_store_full_per_call_vectors():
    events = np.array([[1, 0.0, 1, 0, 1], [2, 0.0, 2, 0, -1], [3, 0.0, 2, -1, 0]])
    hashes = report.branch_signatures(events, 3, 0.0, size=2)
    assert hashes[1] == hashes[3] != hashes[2]
    assert hashes[1] == report.common.digest_bytes(
        np.array([1, 0], dtype="<i4").tobytes()
    )
    for index in (0, 1, 2):
        bad = events.copy()
        bad[index, 3] = 5
        with pytest.raises(ValueError):
            report.branch_signatures(bad, 3, 0.0, size=2)
    with pytest.raises(ValueError):
        report.branch_signatures(events[::-1], 3, 0.0, size=2)


def test_admissible_FD_probe_cannot_hide_a_branch_crossing():
    fixture = fd_fixture()
    hashes = {int(row[0]): "baseline" for row in fixture[5]}
    hashes[3] = "crossed"
    with pytest.raises(ValueError, match="branch"):
        report.verify_fd(*fixture, branch_hashes=hashes)


def test_admissible_direction_probe_cannot_hide_a_branch_crossing():
    fixture = direction_fixture()
    hashes = {int(row[0]): "baseline" for row in fixture[-2]}
    hashes[2] = "crossed"
    with pytest.raises(ValueError, match="branch"):
        report.verify_directions(*fixture, branch_hashes=hashes)


def test_underflow_RHS_and_Jv_allowances_remain_software_checks_only():
    tiny = report.TINY
    h = 1e-7
    # A DAZ loss of a subnormal numerator is amplified bydivision byh.
    gradual = np.array([1e-310 / h])
    checked = report.arithmetic_comparison(
        np.zeros(1), gradual, abs(gradual), flush_amplification=1 + 1 / h
    )
    assert abs(gradual[0]) > 32 * tiny and checked["allowance"][0] > abs(gradual[0])
    with pytest.raises(ValueError):
        report.arithmetic_comparison(
            np.ones(1), gradual, abs(gradual), flush_amplification=1 + 1 / h
        )
    # With normal nonzero v<=1, each row of Nterms loses at most O(N*NORMAL).
    result = report.arithmetic_comparison(
        np.zeros(1),
        np.array([100 * tiny]),
        np.array([100 * tiny]),
        flush_amplification=160,
    )
    assert result["allowance"][0] >= 100 * tiny


def test_actual_attempt_statuses_survive_an_unavailable_setup(tmp_path):
    name = report.STATES[0] + "-repeat-3"
    (tmp_path / "campaign.json").write_text(
        json.dumps(
            {
                "attempts": [
                    {
                        "name": name,
                        "status": "INTERRUPTED",
                        "files": {"partial.bin": {"sha256": "0" * 64}},
                    }
                ]
            }
        )
    )
    result = report.analyze(tmp_path)
    assert result["attempts"][name]["status"] == "INTERRUPTED"
    assert len(result["attempts"]) == 9 and not result["software_pass"]
