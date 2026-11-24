"""Array-only Phase 2D diagnostics; no producer, loading, or model policy.

Coordinates are physical molar Y, rates Y/s and times seconds. Malformed shapes
or types raise ValueError. Well-shaped numerical failures remain explicit. Array
results belong in numeric artifacts, separately from JSON summaries.
"""

from numbers import Real

import numpy as np

JACOBIAN_MULTIPLIERS = np.array(
    [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6], dtype=np.float64
)


def _array(value, name, ndim, *, finite=True):
    if not isinstance(value, np.ndarray) or value.dtype.kind not in "fiu":
        raise ValueError(f"{name} must be a real numeric ndarray")
    if value.ndim != ndim:
        raise ValueError(f"{name} must have {ndim} dimensions")
    result = value.astype(np.float64, copy=True)
    if finite and not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    return result


def _times(value, name, *, minimum=1):
    result = _array(value, name, 1)
    with np.errstate(over="ignore", invalid="ignore"):
        steps = np.diff(result)
    if len(result) < minimum or np.any(~np.isfinite(steps)) or np.any(steps <= 0):
        raise ValueError(
            f"{name} must be strictly increasing with >= {minimum} entries"
        )
    return result


def _species(A, Z):
    A, Z = _array(A, "A", 1), _array(Z, "Z", 1)
    if (
        not len(A)
        or A.shape != Z.shape
        or np.any(A <= 0)
        or np.any(Z < 0)
        or np.any(Z > A)
        or np.any(A != np.floor(A))
        or np.any(Z != np.floor(Z))
    ):
        raise ValueError("A,Z must be equal nonempty ordered nuclear integer arrays")
    return A, Z


def _matrix(value, name, rows, columns, *, finite=True):
    result = _array(value, name, 2, finite=finite)
    if result.shape != (rows, columns):
        raise ValueError(f"{name} must have shape {(rows, columns)}")
    return result


def _flags(value, name, size):
    if (
        not isinstance(value, np.ndarray)
        or value.dtype != np.dtype(bool)
        or value.shape != (size,)
    ):
        raise ValueError(f"{name} must be a boolean ndarray of shape {(size,)}")
    return value.copy()


def trajectory_observables(Y, A, Z):
    """Independent nonnormalized moments and overlapping A-weighted inventories.

    A>=48 is a subset of A>=12. Q and Ye need not remain constant.
    """
    A, Z = _species(A, Z)
    Y = _array(Y, "Y", 2, finite=False)
    if Y.shape[1] != len(A):
        raise ValueError("Y species axis must match A,Z")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        X = Y * A
        B, Q = np.sum(X, axis=1), np.sum(Y * Z, axis=1)
        Ye = np.divide(Q, B, out=np.full_like(Q, np.nan), where=B != 0)
        masks = {
            "neutrons": (A == 1) & (Z == 0),
            "protons": (A == 1) & (Z == 1),
            "alpha": (A == 4) & (Z == 2),
            "A_ge_12": A >= 12,
            "A_ge_48": A >= 48,
        }
        return {
            "B": B,
            "Q": Q,
            "Ye": Ye,
            "total_abundance": np.sum(Y, axis=1),
            "inventory": {k: np.sum(X[:, m], axis=1) for k, m in masks.items()},
        }


def _difference_summary(delta):
    with np.errstate(over="ignore", invalid="ignore"):
        magnitude = np.abs(delta)
        index = np.unravel_index(int(np.argmax(magnitude)), magnitude.shape)
        return {
            "component_rms": np.sqrt(np.mean(delta**2, axis=0)),
            "component_max": np.max(magnitude, axis=0),
            "time_l1": np.sum(magnitude, axis=1),
            "time_l2": np.sqrt(np.sum(delta**2, axis=1)),
            "time_linf": np.max(magnitude, axis=1),
            "pooled_rms": float(np.sqrt(np.mean(delta**2))),
            "maximum": float(magnitude[index]),
            "maximum_location": np.array(index, dtype=np.int64),
            "maximum_locations": np.argwhere(magnitude == magnitude[index]),
            "endpoint": delta[-1].copy(),
        }


def compare_trajectories(times, left_Y, right_Y, A, Z):
    """Right-minus-left errors on an exact complete common grid.

    Relative errors divide by left Y without floors; zero reference values have
    false defined masks and NaN relative values, including zero/zero.
    """
    times, (A, Z) = _times(times, "times"), _species(A, Z)
    left = _matrix(left_Y, "left_Y", len(times), len(A))
    right = _matrix(right_Y, "right_Y", len(times), len(A))
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        dY, defined = right - left, left != 0
        dX = A * dY
        relative = np.divide(dY, left, out=np.full_like(dY, np.nan), where=defined)
        y_summary, x_summary = _difference_summary(dY), _difference_summary(dX)
        left_obs, right_obs = (
            trajectory_observables(left, A, Z),
            trajectory_observables(right, A, Z),
        )
        finite = (
            all(
                np.all(np.isfinite(v))
                for s in (y_summary, x_summary)
                for v in s.values()
            )
            and all(
                np.all(np.isfinite(value))
                for obs in (left_obs, right_obs)
                for key, value in obs.items()
                if key != "inventory"
            )
            and all(
                np.all(np.isfinite(value))
                for obs in (left_obs, right_obs)
                for value in obs["inventory"].values()
            )
        )
        return {
            "times": times,
            "dY": dY,
            "dX": dX,
            "Y": y_summary,
            "X": x_summary,
            "relative": relative,
            "relative_defined": defined,
            "relative_unbounded": defined & ~np.isfinite(relative),
            "zero_reference": ~defined,
            "zero_reference_nonzero_difference": (~defined) & (dY != 0),
            "finite": bool(finite),
            "left_observables": left_obs,
            "right_observables": right_obs,
        }


def _positive_moments(obs):
    return bool(
        all(np.all(np.isfinite(obs[k])) for k in ("B", "Q", "Ye", "total_abundance"))
        and np.all(obs["B"] > 0)
        and np.all(obs["total_abundance"] > 0)
        and np.all(obs["Ye"] > 0)
    )


def trajectory_constraints(
    accepted_t,
    Y,
    F,
    residual,
    scalar_diag,
    A,
    Z,
    Y0,
    requested_t,
    requested_Y,
    *,
    domain_ok,
    final_projection_l1,
    atol=1e-13,
    rtol=1e-11,
):
    """Check accepted/requested states, preserving failed and missing outputs.

    All per-accepted arrays include initial row; scalar_diag columns are native
    B,Q,Ye. Initial residual and projection must be zero. domain_ok has boolean
    'accepted' and 'requested' arrays from native forcing/EOS/probe domain checks.
    Missing outputs may contain NaNs. An empty accepted history fails explicitly.
    The runner separately gates native status and all trial/probe diagnostics.
    """
    accepted = _times(accepted_t, "accepted_t", minimum=0)
    requested = _times(requested_t, "requested_t", minimum=2)
    A, Z = _species(A, Z)
    n, s = len(accepted), len(A)
    Y = _matrix(Y, "Y", n, s, finite=False)
    F = _matrix(F, "F", n, s, finite=False)
    residual = _matrix(residual, "residual", n, s, finite=False)
    native = _matrix(scalar_diag, "scalar_diag", n, 3, finite=False)
    outputs = _matrix(requested_Y, "requested_Y", len(requested), s, finite=False)
    initial = _array(Y0, "Y0", 1)
    projection = _array(final_projection_l1, "final_projection_l1", 1, finite=False)
    if initial.shape != (s,) or projection.shape != (n,):
        raise ValueError("Y0 or final_projection_l1 shape mismatch")
    if not isinstance(domain_ok, dict) or set(domain_ok) != {"accepted", "requested"}:
        raise ValueError("domain_ok must contain accepted and requested boolean arrays")
    accepted_domain = _flags(domain_ok["accepted"], "accepted domain", n)
    requested_domain = _flags(
        domain_ok["requested"], "requested domain", len(requested)
    )
    for value in (atol, rtol):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
            raise ValueError("nonlinear tolerances must be positive finite scalars")
        try:
            converted = float(value)
        except (OverflowError, ValueError) as exc:
            raise ValueError(
                "nonlinear tolerances must be positive finite scalars"
            ) from exc
        if not np.isfinite(converted) or converted <= 0:
            raise ValueError("nonlinear tolerances must be positive finite scalars")
    if (atol, rtol) not in ((1e-13, 1e-11), (1e-14, 1e-12)):
        raise ValueError(
            "only protocol standard or tight nonlinear controls are allowed"
        )
    initial_obs = trajectory_observables(initial[None, :], A, Z)
    B0 = float(initial_obs["B"][0])
    accepted_obs, requested_obs = (
        trajectory_observables(Y, A, Z),
        trajectory_observables(outputs, A, Z),
    )
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        tolerance = 1e-10 * max(1.0, abs(B0))
        accepted_drift = np.abs(accepted_obs["B"] - B0)
        requested_drift = np.abs(requested_obs["B"] - B0)
        native_drift = np.abs(native[:, 0] - B0)
        computed = np.zeros_like(residual)
        computed[1:] = Y[1:] - Y[:-1] - np.diff(accepted)[:, None] * F[1:]
        scale = atol + rtol * np.maximum(np.abs(A * Y[:-1]), np.abs(A * Y[1:]))
        supplied_norm = np.max(np.abs(A * residual[1:]) / scale, axis=1)
        computed_norm = np.max(np.abs(A * computed[1:]) / scale, axis=1)
        residual_l1 = np.sum(np.abs(A * residual), axis=1)
        cumulative_projection = np.cumsum(projection)
        output_finite = np.all(np.isfinite(outputs), axis=1)
        indices = np.searchsorted(accepted, requested)
        landed = indices < n
        corresponding = np.zeros(len(requested), dtype=bool)
        if n:
            landed &= accepted[np.minimum(indices, n - 1)] == requested
            corresponding[landed] = np.all(
                outputs[landed] == Y[indices[landed]], axis=1
            )
        present = output_finite & landed & corresponding
        checks = {
            "initial_state": bool(
                n and accepted[0] == requested[0] and np.array_equal(Y[0], initial)
            ),
            "initial_domain": bool(
                np.all((initial >= 0) & (initial <= 1))
                and _positive_moments(initial_obs)
            ),
            "finite": bool(
                all(
                    np.all(np.isfinite(v))
                    for v in (
                        Y,
                        F,
                        residual,
                        native,
                        projection,
                        computed_norm,
                        supplied_norm,
                        residual_l1,
                        cumulative_projection,
                    )
                )
            ),
            "nonnegative_bounded": bool(
                np.all((Y >= 0) & (Y <= 1)) and np.all((outputs >= 0) & (outputs <= 1))
            ),
            "moments": bool(
                _positive_moments(accepted_obs)
                and _positive_moments(requested_obs)
                and np.all(native[:, 0] > 0)
                and np.all(native[:, 2] > 0)
            ),
            "domain": bool(np.all(accepted_domain) and np.all(requested_domain)),
            "baryon_balance": bool(
                np.all(accepted_drift <= tolerance)
                and np.all(requested_drift <= tolerance)
                and np.all(native_drift <= tolerance)
            ),
            "residual": bool(
                n
                and np.all(residual[0] == 0)
                and np.all(supplied_norm <= 1)
                and np.all(computed_norm <= 1)
            ),
            "projection": bool(
                n
                and projection[0] == 0
                and np.all(projection >= 0)
                and np.all(projection <= 1e-12)
                and np.all(cumulative_projection <= 1e-10)
            ),
            "complete_outputs": bool(np.all(present)),
            "horizon": bool(
                n
                and accepted[-1] == requested[-1]
                and np.all(accepted >= requested[0])
                and np.all(accepted <= requested[-1])
            ),
        }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "B0": B0,
        "B_tolerance": tolerance,
        "accepted_observables": accepted_obs,
        "requested_observables": requested_obs,
        "native_moments": native,
        "native_minus_independent_moments": native
        - np.column_stack([accepted_obs[k] for k in ("B", "Q", "Ye")]),
        "accepted_B_drift": accepted_drift,
        "requested_B_drift": requested_drift,
        "native_B_drift": native_drift,
        "computed_residual": computed,
        "supplied_residual_norm": supplied_norm,
        "computed_residual_norm": computed_norm,
        "residual_l1": residual_l1,
        "final_projection_l1": projection,
        "cumulative_final_projection_l1": cumulative_projection,
        "output_present": present,
        "missing_output": ~present,
        "achieved_endpoint": float(accepted[-1]) if n else None,
    }


def _step_refinement(coarse, fine):
    strict = False
    if len(coarse) > 1 and len(fine) > 1:
        indices = np.searchsorted(coarse, fine[:-1], side="right") - 1
        for j in np.flatnonzero((indices >= 0) & (indices < len(coarse) - 1)):
            i = indices[j]
            if (
                fine[j + 1] <= coarse[i + 1]
                and fine[j + 1] - fine[j] < coarse[i + 1] - coarse[i]
            ):
                strict = True
                break
    return {
        "identical_mesh": np.array_equal(coarse, fine),
        "strict_step_refinement": strict,
        "coarse_step_range": np.array(
            [np.min(np.diff(coarse)), np.max(np.diff(coarse))]
        )
        if len(coarse) > 1
        else None,
        "fine_step_range": np.array([np.min(np.diff(fine)), np.max(np.diff(fine))])
        if len(fine) > 1
        else None,
    }


def assess_refinement(levels, A, Z):
    """All four levels, three comparisons, both reduction tests and mesh activity.

    Each level supplies accepted_t, requested_t, requested_Y. Strict refinement
    means a fine accepted interval is contained in a longer coarse interval;
    native retries may make meshes nonnested. Per-run status/constraints remain
    separate mandatory checks. No order or extrapolation is inferred.
    """
    if not isinstance(levels, (tuple, list)) or len(levels) != 4:
        raise ValueError("exactly four ordered mesh levels are required")
    A, Z = _species(A, Z)
    parsed = []
    for level in levels:
        if not isinstance(level, dict) or not {
            "accepted_t",
            "requested_t",
            "requested_Y",
        } <= set(level):
            raise ValueError(
                "each mesh level must provide accepted_t, requested_t, requested_Y"
            )
        accepted = _times(level["accepted_t"], "accepted_t", minimum=0)
        requested = _times(level["requested_t"], "requested_t", minimum=2)
        output = _matrix(
            level["requested_Y"], "requested_Y", len(requested), len(A), finite=False
        )
        full = bool(
            len(accepted)
            and accepted[0] == requested[0]
            and accepted[-1] == requested[-1]
            and np.all(np.isin(requested, accepted))
            and np.all(np.isfinite(output))
        )
        parsed.append((accepted, requested, output, full))
    same_grid = all(np.array_equal(parsed[0][1], p[1]) for p in parsed)
    comparisons, meshes = [], []
    for left, right in zip(parsed[:-1], parsed[1:]):
        meshes.append(_step_refinement(left[0], right[0]))
        comparisons.append(
            compare_trajectories(left[1], left[2], right[2], A, Z)
            if same_grid and left[3] and right[3]
            else None
        )
    maxima = np.full((3, 2), np.nan)
    for i, comparison in enumerate(comparisons):
        if comparison is not None:
            maxima[i] = [
                np.max(comparison["X"]["time_linf"]),
                np.max(comparison["X"]["time_l1"]),
            ]
    with np.errstate(invalid="ignore"):
        reduction = (maxima[1:] <= 0.75 * maxima[:-1]) | (maxima[:-1] <= 1e-10)
        final = maxima[-1] <= np.array([1e-6, 1e-5])
    passed = bool(
        same_grid
        and all(p[3] for p in parsed)
        and np.all(np.isfinite(maxima))
        and np.all(reduction)
        and np.all(final)
        and all(m["strict_step_refinement"] for m in meshes)
        and all(c is not None and c["finite"] for c in comparisons)
    )
    return {
        "pass": passed,
        "same_requested_grid": same_grid,
        "complete_levels": np.array([p[3] for p in parsed]),
        "comparisons": comparisons,
        "mesh_pairs": meshes,
        "maxima_linf_l1": maxima,
        "reduction_pass": reduction,
        "final_threshold_pass": final,
    }


def compare_nonlinear_controls(times, standard_Y, tight_Y, A, Z):
    """Finest-mesh nonlinear-control allowance, separate from time refinement."""
    result = compare_trajectories(times, standard_Y, tight_Y, A, Z)
    result["pass"] = bool(
        result["finite"]
        and np.max(result["X"]["time_linf"]) <= 1e-9
        and np.max(result["X"]["time_l1"]) <= 1e-8
    )
    return result


def assess_reproduction(times, first_Y, repeat_Y, A, Z):
    """Declared allowance on X, inventory and moments at common requested outputs.

    Runner additionally gates identical grids/masks/status/membership and both
    original/repeat independent numerical passes; these cannot be inferred here.
    """
    comparison = compare_trajectories(times, first_Y, repeat_Y, A, Z)
    A, _ = _species(A, Z)
    with np.errstate(over="ignore", invalid="ignore"):
        allowed = 1e-12 + 1e-10 * np.abs(first_Y * A)
        components = np.abs(comparison["dX"]) <= allowed
        observables = {}
        for key in ("B", "Q", "Ye", "total_abundance"):
            first, repeat = (
                comparison["left_observables"][key],
                comparison["right_observables"][key],
            )
            observables[key] = (
                np.isfinite(first)
                & np.isfinite(repeat)
                & (np.abs(repeat - first) <= 1e-12 + 1e-10 * np.abs(first))
            )
        for key, first in comparison["left_observables"]["inventory"].items():
            repeat = comparison["right_observables"]["inventory"][key]
            observables[key] = (
                np.isfinite(first)
                & np.isfinite(repeat)
                & (np.abs(repeat - first) <= 1e-12 + 1e-10 * np.abs(first))
            )
    return {
        "pass": bool(
            comparison["finite"]
            and np.all(components)
            and all(np.all(v) for v in observables.values())
        ),
        "comparison": comparison,
        "component_allowance": allowed,
        "component_pass": components,
        "observable_pass": observables,
    }


def jacobian_directions(Y, A, initial_Y):
    """Three fixed scaled directions in Y units, without normalization."""
    A, Y, initial = (
        _array(A, "A", 1),
        _array(Y, "Y", 1),
        _array(initial_Y, "initial_Y", 1),
    )
    if (
        not len(A)
        or Y.shape != A.shape
        or initial.shape != A.shape
        or np.any(A <= 0)
        or np.any(Y < 0)
    ):
        raise ValueError("direction inputs must have equal valid species shape")
    scale = np.maximum(np.abs(Y), 1e-8 / A)
    alternating = np.where(np.arange(len(A)) % 2 == 0, 1.0, -1.0)
    alternating[(Y == 0) & (alternating < 0)] = 1.0
    coordinate = np.zeros_like(Y)
    coordinate[int(np.argmax(A * initial))] = 1.0
    return np.array([scale, scale * alternating, scale * coordinate])


def assess_directional_jacobian(A, Jv, estimates, admissible):
    """All nine multipliers and an adjacent stable pair, preserving refusals.

    Independently computed estimates are in Y/s; refused rows may be NaN. Both
    estimates must agree with Jv and each other. Successive estimates use the
    same symmetric componentwise allowance as Jv/Dv. Runner requires all sweeps.
    """
    A, Jv = _array(A, "A", 1), _array(Jv, "Jv", 1, finite=False)
    estimates = _matrix(estimates, "estimates", 9, len(A), finite=False)
    admissible = _flags(admissible, "admissible", 9)
    if not len(A) or Jv.shape != A.shape or np.any(A <= 0):
        raise ValueError("A,Jv need equal species shape and positive A")
    with np.errstate(over="ignore", invalid="ignore"):
        production, directional = A * Jv, estimates * A
        finite_estimates = np.all(np.isfinite(directional), axis=1)
        invalid_admissible = admissible & ~finite_estimates
        usable = admissible & finite_estimates
        allowed = 1e-7 + 1e-3 * np.maximum(np.abs(production), np.abs(directional))
        production_component_pass = np.abs(directional - production) <= allowed
        production_pass = (
            usable
            & np.all(np.isfinite(production))
            & np.all(production_component_pass, axis=1)
        )
        adjacent_allowance = 1e-7 + 1e-3 * np.maximum(
            np.abs(directional[:-1]), np.abs(directional[1:])
        )
        adjacent_component_pass = (
            np.abs(directional[1:] - directional[:-1]) <= adjacent_allowance
        )
        adjacent_pass = (
            usable[:-1] & usable[1:] & np.all(adjacent_component_pass, axis=1)
        )
        stable = adjacent_pass & production_pass[:-1] & production_pass[1:]
    return {
        "pass": bool(np.any(stable) and not np.any(invalid_admissible)),
        "invalid_admissible": invalid_admissible,
        "multipliers": JACOBIAN_MULTIPLIERS.copy(),
        "production_Jv": Jv.copy(),
        "estimates": estimates.copy(),
        "admissible": admissible,
        "usable": usable,
        "production_component_allowance": allowed,
        "production_pass": production_pass,
        "production_component_pass": production_component_pass,
        "adjacent_component_allowance": adjacent_allowance,
        "adjacent_component_pass": adjacent_component_pass,
        "adjacent_pass": adjacent_pass,
        "stable_windows": stable,
        "stable_window_indices": np.flatnonzero(stable),
    }
