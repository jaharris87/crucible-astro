"""Public checked-callable and solver-result mutation controls."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

import crucible.integration as integration
from crucible.integration import RHSContract, integrate_rhs

CONTRACT = RHSContract(("a", "b"), "dimensionless", "1/s")
GRID = np.linspace(0., 1., 21)
INITIAL = np.array([1., 0.])


def rhs(t, y):
    return np.array([-y[0], y[0]])


def run(callback=rhs, initial=INITIAL, grid=GRID, **kwargs):
    return integrate_rhs(callback, initial, grid, contract=CONTRACT,
                         expected_contract=CONTRACT, rtol=1e-6, atol=1e-9, **kwargs)


def test_valid_signed_callback_and_no_caller_mutation():
    before = INITIAL.copy()
    seen = []

    def observed(t, y):
        seen.append((t, y.copy()))
        assert y.dtype == np.float64
        return rhs(t, y)

    result = run(observed)
    assert result.full_success and result.outcome == "complete"
    assert np.array_equal(INITIAL, before)
    assert result.output_y.shape == (21, 2)
    assert result.accepted_y.shape == (len(result.accepted_t), 2)
    assert result.accepted_t[-1] == GRID[-1]
    assert np.all(result.present)
    assert np.allclose(result.output_y[:, 0], np.exp(-GRID), atol=2e-7, rtol=0)
    assert result.diagnostics["callback_calls"] == len(seen)
    assert result.diagnostics["callback_calls"] > result.diagnostics["nfev"]
    assert result.diagnostics["rejected_steps"] is None
    assert result.diagnostics["linear_solves"] is None
    assert any(t not in GRID for t, y in seen)


@pytest.mark.parametrize("changed", [
    replace(CONTRACT, components=("b", "a")),
    replace(CONTRACT, components=("a", "c")),
    replace(CONTRACT, state_unit="mass_fraction"),
    replace(CONTRACT, rate_unit="1/ms"),
    replace(CONTRACT, time_unit="ms"),
    replace(CONTRACT, conditions=(("T9", "GK"),)),
    replace(CONTRACT, components=("a", "a")),
    replace(CONTRACT, conditions=(("T9", "GK"), ("T9", "K"))),
])
def test_contract_mutation_refuses_before_solver(monkeypatch, changed):
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called"))
    with pytest.raises(ValueError):
        integrate_rhs(rhs, INITIAL, GRID, contract=changed, expected_contract=CONTRACT,
                      rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize("initial", [INITIAL.astype(np.float32), INITIAL.astype(complex),
                                      [1., 0.], np.array([[1., 0.]]),
                                      np.array([1.]), np.array([np.nan, 0.]),
                                      np.array([np.inf, 0.])])
def test_initial_mutation_refuses_before_solver(monkeypatch, initial):
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called"))
    with pytest.raises(ValueError):
        run(initial=initial)


@pytest.mark.parametrize("grid", [GRID.astype(np.float32), GRID.astype(complex),
                                  np.array([0., 0., 1.]), np.array([1., 0.]),
                                  np.array([0., np.nan]), np.array([0., np.inf]),
                                  np.array([0.]), np.array([[0., 1.]])])
def test_grid_mutation_refuses_before_solver(monkeypatch, grid):
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called"))
    with pytest.raises(ValueError):
        run(grid=grid)


@pytest.mark.parametrize("value", [np.array([1.]), np.array([1., np.inf]),
                                    np.array([1., np.nan]), np.ones(2, dtype=np.float32),
                                    np.ones(2, dtype=complex), [1., 2.]])
def test_invalid_callback_output_stops(value):
    result = run(lambda t, y: value)
    assert not result.full_success
    assert result.outcome == "invalid_callback_output"
    assert result.accepted_t is None and result.accepted_y is None
    assert not result.present.any()
    assert result.exception["type"] == "ValueError"
    assert result.diagnostics["nfev"] is None


@pytest.mark.parametrize("kind", ["exception", "nonfinite"])
def test_late_failure_has_trial_diagnostics_without_invented_horizon(kind):
    def fail(t, y):
        if t >= .25:
            if kind == "exception":
                raise ArithmeticError("injected failure after .25 s")
            return np.full(2, np.inf)
        return rhs(t, y)

    result = run(fail)
    assert not result.full_success and not result.present.any()
    assert result.accepted_t is None and result.accepted_y is None
    assert result.last_trial_t >= .25
    assert result.last_trial_y.shape == (2,)
    assert result.exception["type"] == ("ArithmeticError" if kind == "exception" else "ValueError")
    assert result.outcome == ("callback_exception" if kind == "exception" else "invalid_callback_output")
    assert result.diagnostics["callback_calls"] > 1
    assert result.diagnostics["nfev"] is None
    assert "without returning" in result.diagnostics["accepted_history_unavailable_reason"]


def test_callback_cannot_mutate_solver_or_caller_state():
    def mutate(t, y):
        y[0] = 9.
        return rhs(t, y)

    result = run(mutate)
    assert result.outcome == "callback_exception"
    assert "read-only" in result.exception["message"]
    assert np.array_equal(INITIAL, [1., 0.])


def test_terminal_event_is_early_stop_even_with_scipy_success():
    result = run(terminal_event=lambda t, y: t - .5)
    assert result.status == 1 and result.outcome == "terminal_event"
    assert not result.full_success
    assert abs(result.event_t[0] - .5) <= 1e-12
    assert result.accepted_t[-1] == result.event_t[0]
    assert not result.present[GRID > .5].any()
    assert np.all(np.isnan(result.output_y[~result.present]))


def fake_solution(**changes):
    solved = SimpleNamespace(status=0, message="success", success=True, nfev=4, njev=1,
                             nlu=2, t=np.array([0., 1.]), y=np.array([[1., .5], [0., .5]]),
                             t_events=None, sol=lambda t: np.vstack((1 - .5 * t, .5 * t)))
    for name, value in changes.items():
        setattr(solved, name, value)
    return solved


@pytest.mark.parametrize("changes,outcome", [
    ({"status": -1, "success": False, "message": "step failed", "t": np.array([0., .5])}, "solver_failure"),
    ({"t": np.array([0., .5])}, "incomplete_horizon"),
    ({"sol": None}, "invalid_solver_result"),
    ({"sol": lambda t: np.ones((2, len(t) - 1))}, "invalid_solver_result"),
    ({"sol": lambda t: np.full((2, len(t)), np.nan)}, "invalid_solver_result"),
    ({"y": np.array([[1., np.inf], [0., .5]])}, "invalid_solver_result"),
    ({"t": np.array([0., 1., .5])}, "invalid_solver_result"),
    ({"y": np.array([[1., .5]])}, "invalid_solver_result"),
    ({"success": False}, "solver_failure"),
])
def test_returned_solver_result_mutations(monkeypatch, changes, outcome):
    # Positive fake result is a compatibility control for each one-field mutation.
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: fake_solution())
    assert run().full_success
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: fake_solution(**changes))
    result = run()
    assert not result.full_success and result.outcome == outcome
    if outcome in {"solver_failure", "incomplete_horizon"} and "t" in changes:
        assert result.present[GRID <= .5].all()
        assert not result.present[GRID > .5].any()
        assert result.diagnostics["nfev"] == 4
