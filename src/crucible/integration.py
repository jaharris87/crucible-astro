"""A small checked binary64 RHS integration path; no physical-model policy."""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

import numpy as np


@dataclass(frozen=True)
class RHSContract:
    """Ordered coordinate semantics consumed by :func:`integrate_rhs`."""

    components: tuple[str, ...]
    state_unit: str
    rate_unit: str
    time_unit: str = "s"
    conditions: tuple[tuple[str, str], ...] = ()

    def validate(self) -> None:
        if (not isinstance(self.components, tuple) or not self.components
                or any(not isinstance(x, str) or not x for x in self.components)
                or len(set(self.components)) != len(self.components)):
            raise ValueError("components must be unique ordered nonempty identities")
        if not all(isinstance(x, str) and x for x in (self.state_unit, self.rate_unit)):
            raise ValueError("state and rate units must be declared")
        if self.time_unit != "s":
            raise ValueError("integration time unit must be seconds (s)")
        if (not isinstance(self.conditions, tuple)
                or any(not isinstance(x, tuple) or len(x) != 2
                       or any(not isinstance(v, str) or not v for v in x)
                       for x in self.conditions)
                or len({x[0] for x in self.conditions}) != len(self.conditions)):
            raise ValueError("conditions must declare unique names and units")


def checked_vector(value: object, size: int, name: str) -> np.ndarray:
    """Refuse implicit precision/shape conversions and return an owned copy."""
    if not isinstance(value, np.ndarray) or value.dtype != np.dtype("float64"):
        raise ValueError(f"{name} must be a CPU binary64 ndarray")
    if value.shape != (size,):
        raise ValueError(f"{name} must have shape ({size},)")
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be finite")
    return value.copy()


@dataclass
class IntegrationResult:
    requested_t: np.ndarray
    output_y: np.ndarray
    present: np.ndarray
    accepted_t: np.ndarray | None
    accepted_y: np.ndarray | None
    outcome: str
    full_success: bool
    status: int | None
    message: str
    diagnostics: dict
    event_t: np.ndarray
    exception: dict | None
    last_trial_t: float | None
    last_trial_y: np.ndarray | None
    elapsed_seconds: float


def solve_ivp(*args, **kwargs):
    """Import the numerical dependency only when this path is exercised."""
    from scipy.integrate import solve_ivp as scipy_solve_ivp

    return scipy_solve_ivp(*args, **kwargs)


class _CallbackFailure(Exception):
    def __init__(self, kind: str, original: Exception):
        self.kind = kind
        self.original = original
        super().__init__(str(original))


def integrate_rhs(
    rhs: Callable, y0: np.ndarray, times: np.ndarray, *,
    contract: RHSContract, expected_contract: RHSContract,
    rtol: float, atol: float, terminal_event: Callable | None = None,
) -> IntegrationResult:
    """Run Radau with checked callbacks and distinguish accepted and trial history.

    Both output_y and accepted_y use (time, component) array order.
    Invalid caller inputs raise before solver work. Callback/solver failures are
    returned with explicit missing outputs. If SciPy raises, its accepted history
    and work counters are unavailable, never inferred from the last trial call.
    """
    contract.validate()
    expected_contract.validate()
    if contract != expected_contract:
        raise ValueError("RHS component identities, units or conditions mismatch")
    size = len(contract.components)
    initial = checked_vector(y0, size, "initial state")
    if not isinstance(times, np.ndarray) or times.dtype != np.dtype("float64"):
        raise ValueError("requested times must be a binary64 ndarray")
    grid = times.copy()
    if (grid.ndim != 1 or len(grid) < 2 or not np.all(np.isfinite(grid))
            or not np.all(np.diff(grid) > 0)):
        raise ValueError("requested times must be finite, increasing, with two endpoints")
    if (not np.isscalar(rtol) or not np.isscalar(atol)
            or not np.isreal(rtol) or not np.isreal(atol)
            or not np.isfinite(rtol) or not np.isfinite(atol)
            or rtol <= 0 or atol <= 0):
        raise ValueError("rtol and component atol must be finite positive scalars")
    calls = 0
    last_t = None
    last_y = None
    event_calls = 0

    def checked(t, y):
        nonlocal calls, last_t, last_y
        calls += 1
        last_t = float(t)
        last_y = np.array(y, copy=True)
        try:
            if not np.isscalar(t) or not np.isreal(t) or not np.isfinite(t):
                raise ValueError("callback time must be a finite scalar")
            state = checked_vector(y, size, "callback state")
            state.flags.writeable = False
            value = rhs(float(t), state)
        except Exception as exc:
            raise _CallbackFailure("callback_exception", exc) from exc
        try:
            return checked_vector(value, size, "callback RHS")
        except Exception as exc:
            raise _CallbackFailure("invalid_callback_output", exc) from exc

    def event(t, y):
        nonlocal event_calls
        event_calls += 1
        state = checked_vector(y, size, "event state")
        state.flags.writeable = False
        try:
            value = terminal_event(float(t), state)
            if not np.isscalar(value) or not np.isreal(value) or not np.isfinite(value):
                raise ValueError("event must return a finite real scalar")
            return float(value)
        except Exception as exc:
            raise _CallbackFailure("event_exception", exc) from exc

    event.terminal = True
    event.direction = 0
    start = perf_counter()
    output = np.full((len(grid), size), np.nan, dtype=np.float64)
    present = np.zeros(len(grid), dtype=bool)
    diagnostics = {"callback_calls": 0, "event_calls": 0, "nfev": None,
                   "njev": None, "nlu": None, "rejected_steps": None,
                   "linear_solves": None,
                   "unavailable_reason": "SciPy does not expose rejected-step/linear-solve counts"}
    result = IntegrationResult(grid, output, present, None, None, "solver_exception",
                               False, None, "", diagnostics, np.empty(0), None,
                               None, None, 0.0)
    try:
        solved = solve_ivp(checked, (float(grid[0]), float(grid[-1])), initial,
                           method="Radau", vectorized=False, jac=None,
                           dense_output=True, t_eval=None, first_step=None,
                           max_step=np.inf, rtol=float(rtol), atol=float(atol),
                           events=event if terminal_event is not None else None)
        result.status = int(solved.status)
        result.message = str(solved.message)
        for name in ("nfev", "njev", "nlu"):
            diagnostics[name] = int(getattr(solved, name))
        accepted_t = np.asarray(solved.t)
        accepted_y = np.asarray(solved.y).T
        # Retain even malformed returned history for diagnosis; never certify it.
        result.accepted_t = accepted_t.copy()
        result.accepted_y = accepted_y.copy()
        if (accepted_t.dtype != np.float64 or accepted_t.ndim != 1
                or len(accepted_t) < 1 or not np.all(np.isfinite(accepted_t))
                or not np.all(np.diff(accepted_t) > 0)
                or accepted_t[0] != grid[0] or accepted_t[-1] > grid[-1]
                or accepted_y.dtype != np.float64
                or accepted_y.shape != (len(accepted_t), size)
                or not np.all(np.isfinite(accepted_y))
                or not np.array_equal(accepted_y[0], initial)):
            raise ValueError("invalid accepted solver history")
        if solved.t_events is not None:
            result.event_t = np.concatenate(solved.t_events).astype(np.float64)
            if not np.all(np.isfinite(result.event_t)):
                raise ValueError("nonfinite event times")
        available = (grid >= accepted_t[0]) & (grid <= accepted_t[-1])
        if solved.sol is None:
            raise ValueError("solver interpolant unavailable")
        values = np.asarray(solved.sol(grid[available])).T
        if values.dtype != np.float64 or values.shape != (np.count_nonzero(available), size):
            raise ValueError("missing or truncated requested outputs")
        if not np.all(np.isfinite(values)):
            raise ValueError("nonfinite requested outputs")
        output[available] = values
        present[available] = True
        if solved.status == 1:
            result.outcome = "terminal_event"
        elif solved.status != 0 or not solved.success:
            result.outcome = "solver_failure"
        elif accepted_t[-1] != grid[-1] or not np.all(present):
            result.outcome = "incomplete_horizon"
        else:
            result.outcome = "complete"
            result.full_success = True
    except Exception as exc:
        original = exc.original if isinstance(exc, _CallbackFailure) else exc
        result.exception = {"type": type(original).__name__, "message": str(original)}
        result.outcome = exc.kind if isinstance(exc, _CallbackFailure) else (
            "invalid_solver_result" if result.status is not None else "solver_exception")
        result.message = str(original)
        if result.status is None:
            diagnostics["accepted_history_unavailable_reason"] = "solve_ivp raised without returning"
    result.last_trial_t = last_t
    result.last_trial_y = last_y
    diagnostics["callback_calls"] = calls
    diagnostics["event_calls"] = event_calls
    result.elapsed_seconds = perf_counter() - start
    return result
