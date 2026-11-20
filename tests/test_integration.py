"""Public checked-callable and solver-result mutation controls."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

import crucible.integration as integration
from crucible.integration import RHSContract, integrate_rhs

CONTRACT = RHSContract(("a", "b"), "dimensionless", "1/s")
GRID = np.linspace(0.0, 1.0, 21)
INITIAL = np.array([1.0, 0.0])


def rhs(t, y):
    return np.array([-y[0], y[0]])


def run(callback=rhs, initial=INITIAL, grid=GRID, **kwargs):
    return integrate_rhs(
        callback,
        initial,
        grid,
        contract=CONTRACT,
        expected_contract=CONTRACT,
        rtol=1e-6,
        atol=1e-9,
        **kwargs,
    )


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


@pytest.mark.parametrize(
    "changed",
    [
        replace(CONTRACT, components=("b", "a")),
        replace(CONTRACT, components=("a", "c")),
        replace(CONTRACT, state_unit="mass_fraction"),
        replace(CONTRACT, rate_unit="1/ms"),
        replace(CONTRACT, time_unit="ms"),
        replace(CONTRACT, conditions=(("T9", "GK"),)),
        replace(CONTRACT, components=("a", "a")),
        replace(CONTRACT, conditions=(("T9", "GK"), ("T9", "K"))),
    ],
)
def test_contract_mutation_refuses_before_solver(monkeypatch, changed):
    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called")
    )
    with pytest.raises(ValueError):
        integrate_rhs(
            rhs,
            INITIAL,
            GRID,
            contract=changed,
            expected_contract=CONTRACT,
            rtol=1e-6,
            atol=1e-9,
        )


@pytest.mark.parametrize(
    "initial",
    [
        INITIAL.astype(np.float32),
        INITIAL.astype(complex),
        [1.0, 0.0],
        np.array([[1.0, 0.0]]),
        np.array([1.0]),
        np.array([np.nan, 0.0]),
        np.array([np.inf, 0.0]),
    ],
)
def test_initial_mutation_refuses_before_solver(monkeypatch, initial):
    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called")
    )
    with pytest.raises(ValueError):
        run(initial=initial)


@pytest.mark.parametrize(
    "grid",
    [
        GRID.astype(np.float32),
        GRID.astype(complex),
        np.array([0.0, 0.0, 1.0]),
        np.array([1.0, 0.0]),
        np.array([0.0, np.nan]),
        np.array([0.0, np.inf]),
        np.array([0.0]),
        np.array([[0.0, 1.0]]),
    ],
)
def test_grid_mutation_refuses_before_solver(monkeypatch, grid):
    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called")
    )
    with pytest.raises(ValueError):
        run(grid=grid)


@pytest.mark.parametrize(
    "value",
    [
        np.array([1.0]),
        np.array([1.0, np.inf]),
        np.array([1.0, np.nan]),
        np.ones(2, dtype=np.float32),
        np.ones(2, dtype=complex),
        [1.0, 2.0],
    ],
)
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
        if t >= 0.25:
            if kind == "exception":
                raise ArithmeticError("injected failure after .25 s")
            return np.full(2, np.inf)
        return rhs(t, y)

    result = run(fail)
    assert not result.full_success and not result.present.any()
    assert result.accepted_t is None and result.accepted_y is None
    assert result.last_trial_t >= 0.25
    assert result.last_trial_y.shape == (2,)
    assert result.exception["type"] == (
        "ArithmeticError" if kind == "exception" else "ValueError"
    )
    assert result.outcome == (
        "callback_exception" if kind == "exception" else "invalid_callback_output"
    )
    assert result.diagnostics["callback_calls"] > 1
    assert result.diagnostics["nfev"] is None
    assert (
        "without returning" in result.diagnostics["accepted_history_unavailable_reason"]
    )


def test_callback_cannot_mutate_solver_or_caller_state():
    def mutate(t, y):
        y[0] = 9.0
        return rhs(t, y)

    result = run(mutate)
    assert result.outcome == "callback_exception"
    assert "read-only" in result.exception["message"]
    assert np.array_equal(INITIAL, [1.0, 0.0])


def test_terminal_event_is_early_stop_even_with_scipy_success():
    result = run(terminal_event=lambda t, y: t - 0.5)
    assert result.status == 1 and result.outcome == "terminal_event"
    assert not result.full_success
    assert abs(result.event_t[0] - 0.5) <= 1e-12
    assert result.accepted_t[-1] == result.event_t[0]
    assert not result.present[GRID > 0.5].any()
    assert np.all(np.isnan(result.output_y[~result.present]))


def fake_solution(**changes):
    solved = SimpleNamespace(
        status=0,
        message="success",
        success=True,
        nfev=4,
        njev=1,
        nlu=2,
        t=np.array([0.0, 1.0]),
        y=np.array([[1.0, 0.5], [0.0, 0.5]]),
        t_events=None,
        sol=lambda t: np.vstack((1 - 0.5 * t, 0.5 * t)),
    )
    for name, value in changes.items():
        setattr(solved, name, value)
    return solved


@pytest.mark.parametrize(
    "changes,outcome",
    [
        (
            {
                "status": -1,
                "success": False,
                "message": "step failed",
                "t": np.array([0.0, 0.5]),
            },
            "solver_failure",
        ),
        ({"t": np.array([0.0, 0.5])}, "incomplete_horizon"),
        ({"sol": None}, "invalid_solver_result"),
        ({"sol": lambda t: np.ones((2, len(t) - 1))}, "invalid_solver_result"),
        ({"sol": lambda t: np.full((2, len(t)), np.nan)}, "invalid_solver_result"),
        ({"y": np.array([[1.0, np.inf], [0.0, 0.5]])}, "invalid_solver_result"),
        ({"t": np.array([0.0, 1.0, 0.5])}, "invalid_solver_result"),
        ({"y": np.array([[1.0, 0.5]])}, "invalid_solver_result"),
        ({"success": False}, "solver_failure"),
    ],
)
def test_returned_solver_result_mutations(monkeypatch, changes, outcome):
    # Positive fake result is a compatibility control for each one-field mutation.
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: fake_solution())
    assert run().full_success
    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: fake_solution(**changes)
    )
    result = run()
    assert not result.full_success and result.outcome == outcome
    if outcome in {"solver_failure", "incomplete_horizon"} and "t" in changes:
        assert result.present[GRID <= 0.5].all()
        assert not result.present[GRID > 0.5].any()
        assert result.diagnostics["nfev"] == 4


@pytest.mark.parametrize("event", [lambda t, y: t, lambda t, y: y[0] - 1.0])
def test_initial_terminal_event_retains_raw_history_and_only_initial_output(event):
    result = run(terminal_event=event)
    assert result.outcome == "terminal_event" and result.status == 1
    assert result.exception is None and not result.full_success
    np.testing.assert_array_equal(result.event_t, GRID[:1])
    np.testing.assert_array_equal(result.accepted_t, [GRID[0], GRID[0]])
    np.testing.assert_array_equal(result.accepted_y, np.tile(INITIAL, (2, 1)))
    np.testing.assert_array_equal(result.output_y[0], INITIAL)
    assert result.present[0] and not result.present[1:].any()
    assert np.isnan(result.output_y[1:]).all()


@pytest.mark.parametrize("event_times", [None, [np.array([])], [np.array([0.1])]])
def test_duplicate_initial_time_requires_matching_terminal_root(
    monkeypatch, event_times
):
    def solution(events):
        return fake_solution(
            status=1,
            t=np.array([0.0, 0.0]),
            y=np.tile(INITIAL[:, None], (1, 2)),
            t_events=events,
        )

    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: solution([np.array([0.0])])
    )
    assert run().outcome == "terminal_event"
    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: solution(event_times))
    result = run()
    assert result.outcome == "invalid_solver_result" and not result.full_success


def test_actual_first_step_radau_failure_retains_initial_output():
    # At large t0 the fast decay needs a step below binary64 time spacing.
    # Pinned SciPy returns a non-None OdeSolution with zero usable intervals.
    contract = RHSContract(("x",), "dimensionless", "1/s")
    times = np.array([1e12, 1e12 + 1])
    result = integrate_rhs(
        lambda t, y: -1e6 * y,
        np.ones(1),
        times,
        contract=contract,
        expected_contract=contract,
        rtol=1e-6,
        atol=1e-9,
    )
    assert result.outcome == "solver_failure" and result.status == -1
    assert result.exception is None and not result.full_success
    assert "step size" in result.message
    np.testing.assert_array_equal(result.accepted_t, times[:1])
    np.testing.assert_array_equal(result.output_y[0], [1.0])
    assert result.present.tolist() == [True, False]
    assert np.isnan(result.output_y[1]).all()
    assert result.diagnostics["nfev"] > 0


@pytest.mark.parametrize(
    "interpolant", [None, lambda t: pytest.fail("no accepted interval")]
)
def test_initial_failure_does_not_require_or_call_interpolant(monkeypatch, interpolant):
    def solution(status):
        return fake_solution(
            status=status,
            success=status == 0,
            message="first step failed",
            t=GRID[:1],
            y=INITIAL[:, None],
            sol=interpolant,
        )

    monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: solution(-1))
    result = run()
    assert result.outcome == "solver_failure" and result.exception is None
    assert result.present.tolist() == [True] + [False] * (len(GRID) - 1)
    np.testing.assert_array_equal(result.output_y[0], INITIAL)
    if interpolant is None:
        monkeypatch.setattr(integration, "solve_ivp", lambda *a, **k: solution(0))
        assert run().outcome == "invalid_solver_result"


@pytest.mark.parametrize(
    "kwargs", [{"rtol": True}, {"atol": True}, {"rtol": np.bool_(True)}]
)
def test_boolean_tolerances_refuse_before_solver(monkeypatch, kwargs):
    monkeypatch.setattr(
        integration, "solve_ivp", lambda *a, **k: pytest.fail("solver called")
    )
    controls = {"rtol": 1e-6, "atol": 1e-9, **kwargs}
    with pytest.raises(ValueError, match="finite positive scalars"):
        integrate_rhs(
            rhs,
            INITIAL,
            GRID,
            contract=CONTRACT,
            expected_contract=CONTRACT,
            **controls,
        )


@pytest.mark.parametrize("value", [True, False, np.bool_(True)])
def test_boolean_event_refuses(value):
    result = run(terminal_event=lambda t, y: value)
    assert result.outcome == "event_exception" and not result.full_success
    assert result.exception["type"] == "ValueError"


@pytest.mark.parametrize("time", ["invalid", np.nan])
def test_invalid_solver_callback_time_is_a_callback_exception(monkeypatch, time):
    def solve(callback, *args, **kwargs):
        callback(time, INITIAL)
        pytest.fail("invalid callback must stop")

    monkeypatch.setattr(integration, "solve_ivp", solve)
    result = run()
    assert result.outcome == "callback_exception" and not result.full_success
    assert result.last_trial_t is None
    assert result.diagnostics["callback_calls"] == 1


@pytest.mark.parametrize("time,state", [(np.nan, INITIAL), (0.0, np.ones(1))])
def test_invalid_solver_event_input_is_an_event_exception(monkeypatch, time, state):
    def solve(callback, *args, events, **kwargs):
        events(time, state)
        pytest.fail("invalid event input must stop")

    monkeypatch.setattr(integration, "solve_ivp", solve)
    result = run(terminal_event=lambda t, y: pytest.fail("invalid event was forwarded"))
    assert result.outcome == "event_exception" and not result.full_success
    assert result.exception["type"] == "ValueError"
    assert result.diagnostics["event_calls"] == 1
