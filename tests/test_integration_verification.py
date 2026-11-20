"""Independent analytic identities, declared refinement, and serialization checks."""

import json
import subprocess
import sys

import numpy as np
import pytest

from crucible.integration import integrate_rhs
from crucible.integration_verification import (
    LEVELS,
    _save_attempt,
    compare_campaigns,
    error_metrics,
    exchange_constraints,
    exchange_oracle,
    fixtures,
    forced_oracle,
    refinement,
    reload_campaign,
    singularity_oracle,
)


def test_oracle_initial_values_and_off_grid_derivative_identities():
    # Derivatives below are differentiated closed forms, not another ODE solve.
    times = np.array([.00037, .0137, .311, 1.337, 4.993])
    a, b = exchange_oracle(times).T
    da = -2 * np.exp(-3 * times)
    db = 2 * np.exp(-3 * times)
    assert np.allclose(da, -2 * a + b, atol=5e-16, rtol=1e-12)
    assert np.allclose(db, 2 * a - b, atol=5e-16, rtol=1e-12)
    assert np.allclose(a + b, 1., atol=2e-16, rtol=0)
    assert np.array_equal(exchange_oracle(np.array([0.])), [[1., 0.]])
    u, v = forced_oracle(times).T
    du = -np.exp(-times)
    dv = np.cos(times) - 1000 * np.exp(-1000 * times)
    assert np.allclose(du, -u, atol=1e-14, rtol=1e-14)
    assert np.allclose(dv, -1000 * (v - np.sin(times)) + np.cos(times), atol=2e-13, rtol=1e-12)
    assert np.array_equal(forced_oracle(np.array([0.])), [[1., 1.]])
    assert np.isnan(singularity_oracle(np.array([1., 2.]))).all()


def test_fixed_grids():
    exchange, forced = fixtures()
    assert np.array_equal(exchange.times, np.linspace(0., 5., 201))
    assert len(forced.times) == 357
    assert np.array_equal(forced.times, np.union1d(np.linspace(0., 2 * np.pi, 257),
                                                np.arange(101) * 1e-4))
    assert np.all(np.diff(forced.times) > 0)


@pytest.mark.parametrize("fixture", fixtures(), ids=lambda x: x.name)
def test_positive_fixtures_all_three_predeclared_levels(fixture):
    summaries = []
    for level, rtol, atol, limit in LEVELS:
        result = integrate_rhs(fixture.rhs, fixture.initial, fixture.times,
                               contract=fixture.contract, expected_contract=fixture.contract,
                               rtol=rtol, atol=atol)
        assert result.full_success, result.message
        errors, metrics = error_metrics(result.output_y, fixture.oracle(fixture.times), result.present)
        assert errors.shape == result.output_y.shape
        assert all(x <= limit for x in metrics["component_max_abs"])
        assert all(x <= limit for x in metrics["component_rms"])
        assert metrics["whole_max_abs"] <= limit
        assert metrics["whole_rms"] <= limit
        assert metrics["missing_rows"] == 0
        summaries.append(metrics)
        if fixture.name == "exchange":
            assert exchange_constraints(result, atol)["passed"]
    assert refinement(summaries)["passed"]


def test_forcing_is_evaluated_at_actual_callback_time():
    fixture = fixtures()[1]
    observed = []

    def measured(t, y):
        expected = np.array([-y[0], -1000 * y[1] + 1000 * np.sin(t) + np.cos(t)])
        value = fixture.rhs(t, y)
        assert np.allclose(value, expected, atol=1e-12, rtol=1e-12)
        observed.append(t)
        return value

    result = integrate_rhs(measured, fixture.initial, fixture.times,
                           contract=fixture.contract, expected_contract=fixture.contract,
                           rtol=1e-6, atol=1e-9)
    assert result.full_success
    assert any(t not in fixture.times for t in observed)
    assert result.output_y[:, 1].min() < -.9


def test_singularity_has_explicit_partial_failure():
    times = np.linspace(0., 2., 201)
    fixture = fixtures()[0]
    contract = type(fixture.contract)(("z",), "dimensionless", "1/s")
    result = integrate_rhs(lambda t, y: y * y, np.ones(1), times, contract=contract,
                           expected_contract=contract, rtol=1e-6, atol=1e-9)
    assert not result.full_success
    assert result.outcome == "solver_failure"
    assert result.status == -1
    assert result.accepted_t[-1] < 2.
    assert result.present.any() and not result.present.all()
    # A numerical trajectory may pass t=1 slightly; analytic truth remains undefined.
    errors, metrics = error_metrics(result.output_y, singularity_oracle(times), result.present)
    assert metrics["oracle_defined_rows"] == 100
    assert metrics["missing_rows"] > 0
    assert np.isfinite(errors[result.present & (times < 1)]).all()
    assert np.isnan(errors[times >= 1]).all()


def test_metrics_hand_calculated_and_missing_coverage():
    truth = np.array([[0., 2.], [2., 0.], [4., 4.]])
    solution = np.array([[1., 3.], [0., -2.], [np.nan, np.nan]])
    errors, result = error_metrics(solution, truth, np.array([True, True, False]))
    assert np.array_equal(errors[:2], [[1., 1.], [-2., -2.]])
    assert result["whole_rms"] == np.sqrt(2.5)
    assert result["component_max_abs"] == [2., 2.]
    assert result["relative_nonzero_count"] == 2
    assert result["exact_zero_count"] == 2
    assert result["zero_max_abs_error"] == 2.
    assert result["missing_rows"] == 1
    assert result["component_final_error"] is None


def retained_test_fixture(directory):
    fixture = fixtures()[0]
    result = integrate_rhs(fixture.rhs, fixture.initial, fixture.times,
                           contract=fixture.contract, expected_contract=fixture.contract,
                           rtol=1e-6, atol=1e-9)
    record = _save_attempt(directory, fixture, "L1", result, 5e-6, 1e-9, "complete")
    manifest = {"state": "complete", "passed": True, "attempts": [record],
                "identities": dict.fromkeys(("protocol_sha256", "lock_sha256", "source_commit",
                                             "source_tree", "source_files", "libraries"), "test")}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return manifest


def test_exact_serialization_fresh_process_and_repeat_comparison(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    retained_test_fixture(first)
    retained_test_fixture(second)
    assert reload_campaign(first) == {"verified_attempts": 1, "state": "complete", "passed": True}
    process = subprocess.run([sys.executable, "-m", "crucible.integration_verification", "reload", str(first)],
                             capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout)["verified_attempts"] == 1
    assert compare_campaigns(first, second)["compared_attempts"] == 1


@pytest.mark.parametrize("mutation", ["file", "dtype", "shape", "bytes", "metrics"])
def test_serialization_mutations_refuse(tmp_path, mutation):
    manifest = retained_test_fixture(tmp_path)
    attempt = manifest["attempts"][0]
    if mutation == "file":
        path = tmp_path / attempt["artifact"]["file"]
        path.write_bytes(path.read_bytes() + b"corruption")
    elif mutation in {"dtype", "shape", "bytes"}:
        identity = attempt["artifact"]["arrays"]["output_y"]
        identity[mutation] = {"dtype": "<f4", "shape": [1, 2], "bytes": 1}[mutation]
    else:
        attempt["metrics"]["whole_max_abs"] += 1.
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        reload_campaign(tmp_path)


def test_refinement_detects_failed_reduction_and_nonmonotonicity():
    result = refinement([{"whole_max_abs": x} for x in [1e-4, 3e-4, 5e-5]])
    assert not result["passed"] and result["nonmonotonic"] == [True, False]
    assert refinement([{"whole_max_abs": 1e-12}] * 3)["passed"]


def test_operational_failure_is_retained_and_never_overwritten(tmp_path):
    from crucible.integration_verification import run_campaign

    wrong_protocol = tmp_path / "wrong-protocol.txt"
    wrong_protocol.write_text("wrong identity")
    output = tmp_path / "preserved-failure"
    with pytest.raises(ValueError, match="protocol SHA256"):
        run_campaign(output, protocol_path=wrong_protocol, lock_path=wrong_protocol,
                     label="unit-test-setup-failure-no-numerical-attempts")
    failed = json.loads((output / "manifest.json").read_text())
    assert failed["state"] == "incomplete"
    assert not failed["passed"] and failed["attempts"] == []
    assert failed["operational_failure"]["type"] == "ValueError"
    assert "operational failure" in (output / "attempts.log").read_text()
    with pytest.raises(FileExistsError):
        run_campaign(output, protocol_path=wrong_protocol, lock_path=wrong_protocol,
                     label="unit-test-must-not-overwrite")


def test_failed_positive_metrics_make_refinement_unavailable():
    result = refinement([{"whole_max_abs": 1e-4}, {"missing_rows": 201}, {"whole_max_abs": 1e-8}])
    assert not result["passed"]
    assert result["errors"] == [1e-4, None, 1e-8]
    assert "unavailable" in result["unavailable_reason"]
