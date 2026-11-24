"""Independent public synthetic oracles for Phase 2D array diagnostics."""

import numpy as np
import pytest

from crucible.trajectory_metrics import (
    JACOBIAN_MULTIPLIERS,
    assess_directional_jacobian,
    assess_refinement,
    assess_reproduction,
    compare_nonlinear_controls,
    compare_trajectories,
    jacobian_directions,
    trajectory_constraints,
    trajectory_observables,
)

A = np.array([1, 1])
Z = np.array([0, 1])


def nonlinear_exchange(steps):
    """BE for n'=-10 n^2, p'=10 n^2, from the independent quadratic root."""
    t = np.linspace(0.0, 0.01, steps + 1)
    n = np.empty(steps + 1)
    n[0] = 0.1
    for j, h in enumerate(np.diff(t)):
        n[j + 1] = 2 * n[j] / (1 + np.sqrt(1 + 40 * h * n[j]))
    y = np.column_stack([n, 0.4 - n])
    f = np.column_stack([-10 * n**2, 10 * n**2])
    residual = np.zeros_like(y)
    residual[1:] = y[1:] - y[:-1] - np.diff(t)[:, None] * f[1:]
    requested = t[[0, steps // 2, steps]]
    obs = trajectory_observables(y, A, Z)
    return dict(
        accepted_t=t,
        Y=y,
        F=f,
        residual=residual,
        scalar_diag=np.column_stack([obs[k] for k in ("B", "Q", "Ye")]),
        A=A,
        Z=Z,
        Y0=y[0],
        requested_t=requested,
        requested_Y=y[[0, steps // 2, steps]],
        domain_ok={
            "accepted": np.ones(len(t), dtype=bool),
            "requested": np.ones(3, dtype=bool),
        },
        final_projection_l1=np.zeros(len(t)),
    )


def levels_from_oracle():
    return [
        {k: run[k] for k in ("accepted_t", "requested_t", "requested_Y")}
        for run in [nonlinear_exchange(10 * 2**j) for j in range(4)]
    ]


def constant_levels(errors):
    requested = np.array([0.0, 1.0])
    return [
        {
            "accepted_t": np.linspace(0, 1, 2**j + 1),
            "requested_t": requested.copy(),
            "requested_Y": np.full((2, 2), 0.1 + error),
        }
        for j, error in enumerate(errors)
    ]


def test_signed_errors_full_norms_locations_and_relative_zeros():
    t = np.array([0.0, 1.0])
    left = np.array([[0.0, 2.0], [1.0, 0.0]])
    right = np.array([[1.0, 1.0], [-1.0, 0.0]])
    result = compare_trajectories(t, left, right, np.array([1, 4]), np.array([0, 2]))
    np.testing.assert_array_equal(result["dY"], [[1, -1], [-2, 0]])
    np.testing.assert_array_equal(result["dX"], [[1, -4], [-2, 0]])
    np.testing.assert_allclose(result["X"]["component_rms"], np.sqrt([2.5, 8]))
    np.testing.assert_array_equal(result["X"]["component_max"], [2, 4])
    np.testing.assert_array_equal(result["X"]["time_l1"], [5, 2])
    np.testing.assert_allclose(result["X"]["time_l2"], [np.sqrt(17), 2])
    assert result["X"]["pooled_rms"] == np.sqrt(21 / 4)
    np.testing.assert_array_equal(result["X"]["maximum_locations"], [[0, 1]])
    np.testing.assert_array_equal(result["X"]["endpoint"], [-2, 0])
    np.testing.assert_array_equal(
        result["relative_defined"], [[False, True], [True, False]]
    )
    assert np.isnan(result["relative"][0, 0]) and np.isnan(result["relative"][1, 1])
    assert result["relative"][0, 1] == -0.5
    assert result["zero_reference_nonzero_difference"].sum() == 1
    assert result["finite"]


def test_observables_nonnormalized_inventory_and_weak_charge():
    a, z = np.array([1, 1, 4, 12, 48]), np.array([0, 1, 2, 6, 24])
    y = np.array([[0.1, 0.2, 0.01, 0.001, 0.002], [0.05, 0.25, 0.01, 0.001, 0.002]])
    obs = trajectory_observables(y, a, z)
    np.testing.assert_allclose(obs["B"], [0.448, 0.448])
    np.testing.assert_allclose(obs["Q"], [0.274, 0.324])
    np.testing.assert_allclose(obs["Ye"], np.array([0.274, 0.324]) / 0.448)
    np.testing.assert_allclose(obs["inventory"]["A_ge_12"], [0.108, 0.108])
    np.testing.assert_allclose(obs["inventory"]["A_ge_48"], [0.096, 0.096])
    np.testing.assert_allclose(obs["inventory"]["alpha"], [0.04, 0.04])


def test_nonlinear_oracle_constraints_preserve_nonunit_b_and_charge_evolution():
    run = nonlinear_exchange(10)
    result = trajectory_constraints(**run)
    assert result["pass"] and all(result["checks"].values())
    assert result["B0"] == 0.4
    assert run["F"][-1, 0] < 0 < run["F"][-1, 1]
    assert (
        result["accepted_observables"]["Ye"][-1]
        > result["accepted_observables"]["Ye"][0]
    )
    exact = 0.1 / (1 + 0.1 * 10 * 0.01)
    assert run["Y"][-1, 0] > exact  # BE is not silently called exact truth.


@pytest.mark.parametrize(
    "failure",
    [
        "residual",
        "computed_residual",
        "domain",
        "projection",
        "native_nan",
        "negative",
        "native_b",
        "initial",
    ],
)
def test_constraints_refuse_each_independent_failure(failure):
    run = nonlinear_exchange(10)
    if failure == "residual":
        run["residual"][-1, 0] = 1e-5
    elif failure == "computed_residual":
        run["F"][-1, 0] += (
            1e-4  # Supplied residual lies; independent residual catches it.
        )
    elif failure == "domain":
        run["domain_ok"]["accepted"][2] = False
    elif failure == "projection":
        run["final_projection_l1"][-1] = np.nextafter(1e-12, np.inf)
    elif failure == "native_nan":
        run["scalar_diag"][2, 1] = np.nan
    elif failure == "negative":
        run["Y"][2, 0] = -1e-20
    elif failure == "native_b":
        run["scalar_diag"][2, 0] += 2e-10
    elif failure == "initial":
        run["Y0"] = np.array([0.11, 0.29])
    assert not trajectory_constraints(**run)["pass"]


def test_projection_per_step_and_cumulative_bounds():
    run = nonlinear_exchange(100)
    run["final_projection_l1"][1:] = 1e-12
    assert trajectory_constraints(**run)["pass"]
    run = nonlinear_exchange(102)
    run["final_projection_l1"][1:] = 1e-12
    result = trajectory_constraints(**run)
    assert not result["pass"] and not result["checks"]["projection"]


def test_baryon_tolerance_uses_actual_large_nonunit_initial_inventory():
    run = nonlinear_exchange(10)
    run["Y"] *= 5
    run["Y0"] = run["Y"][0].copy()
    run["requested_Y"] *= 5
    run["F"] *= 5
    run["residual"] *= 5
    obs = trajectory_observables(run["Y"], A, Z)
    run["scalar_diag"] = np.column_stack([obs[k] for k in ("B", "Q", "Ye")])
    # Composition exceeds Y<=1 for p; baryon check still has its own valid scale.
    run["scalar_diag"][1, 0] += 1.5e-10
    result = trajectory_constraints(**run)
    assert result["B0"] == 2.0 and result["B_tolerance"] == 2e-10
    assert result["checks"]["baryon_balance"]
    run["scalar_diag"][1, 0] += 1e-10
    assert not trajectory_constraints(**run)["checks"]["baryon_balance"]


@pytest.mark.parametrize(
    "kind", ["truncated", "empty", "missing", "unlanded", "wrong_output"]
)
def test_status_cannot_hide_missing_outputs_or_horizon(kind):
    run = nonlinear_exchange(10)
    if kind in ("truncated", "empty"):
        keep = 0 if kind == "empty" else 6
        for key in (
            "accepted_t",
            "Y",
            "F",
            "residual",
            "scalar_diag",
            "final_projection_l1",
        ):
            run[key] = run[key][:keep]
        run["domain_ok"]["accepted"] = run["domain_ok"]["accepted"][:keep]
    elif kind == "missing":
        run["requested_Y"][-1] = np.nan
    elif kind == "unlanded":
        run["requested_t"][1] = 0.0051
    elif kind == "wrong_output":
        run["requested_Y"][-1, 0] += 1e-12
    result = trajectory_constraints(**run)
    assert not result["pass"] and result["missing_output"].any()
    if kind in ("truncated", "empty"):
        assert not result["checks"]["horizon"]


def test_refinement_independent_nonlinear_solution_and_active_mesh():
    result = assess_refinement(levels_from_oracle(), A, Z)
    assert result["pass"]
    assert result["reduction_pass"].all()
    assert all(p["strict_step_refinement"] for p in result["mesh_pairs"])
    levels = levels_from_oracle()
    levels[1]["accepted_t"] = levels[0]["accepted_t"].copy()
    result = assess_refinement(levels, A, Z)
    assert not result["pass"] and result["mesh_pairs"][0]["identical_mesh"]


def test_refinement_requires_both_norms_and_each_reduction_unless_plateau():
    assert assess_refinement(constant_levels([7e-7, 3e-7, 1e-7, 0]), A, Z)["pass"]
    assert not assess_refinement(constant_levels([1e-6, 6e-7, 3e-7, 0]), A, Z)["pass"]
    assert assess_refinement(constant_levels([1e-11, 0, 2e-7, 3e-7]), A, Z)["pass"]
    assert not assess_refinement(constant_levels([7e-5, 3e-5, 1e-5, 0]), A, Z)["pass"]
    # Per-component Linf passes, but 20 species together fail the L1 bound.
    levels = constant_levels([7e-6, 3e-6, 7e-7, 0])
    for level in levels:
        level["requested_Y"] = np.repeat(level["requested_Y"][:, :1], 20, axis=1)
    result = assess_refinement(levels, np.ones(20), np.ones(20))
    assert result["final_threshold_pass"][0] and not result["final_threshold_pass"][1]
    assert not result["pass"]


@pytest.mark.parametrize("kind", ["nan", "grid", "truncated", "empty"])
def test_refinement_does_not_drop_failed_level(kind):
    levels = levels_from_oracle()
    if kind == "nan":
        levels[1]["requested_Y"][-1] = np.nan
    elif kind == "grid":
        levels[1]["requested_t"][1] = 0.0051
    elif kind == "truncated":
        levels[1]["accepted_t"] = levels[1]["accepted_t"][:-1]
    else:
        levels[1]["accepted_t"] = np.array([])
    assert not assess_refinement(levels, A, Z)["pass"]


def test_nonlinear_control_thresholds_are_distinct_and_inclusive():
    t, first = np.array([0.0, 1.0]), np.array([[0.0, 0.2], [0.0, 0.2]])
    repeat = first.copy()
    repeat[-1, 0] = 1e-9
    assert compare_nonlinear_controls(t, first, repeat, A, Z)["pass"]
    repeat[-1, 0] = np.nextafter(1e-9, np.inf)
    assert not compare_nonlinear_controls(t, first, repeat, A, Z)["pass"]
    repeat = np.full((2, 20), 1e-9)
    assert not compare_nonlinear_controls(
        t, np.zeros_like(repeat), repeat, np.ones(20), np.ones(20)
    )["pass"]


def test_reproduction_absolute_zero_scale_and_inventory_aggregate():
    t, first = np.array([0.0, 1.0]), np.array([[0.0, 0.2], [0.0, 0.2]])
    repeat = first.copy()
    repeat[:, 0] = 1e-12
    assert assess_reproduction(t, first, repeat, A, Z)["pass"]
    repeat[:, 0] = np.nextafter(1e-12, np.inf)
    assert not assess_reproduction(t, first, repeat, A, Z)["pass"]
    first = np.full((2, 20), 0.01)
    result = assess_reproduction(t, first, first + 1.1e-12, np.ones(20), np.ones(20))
    assert result["component_pass"].all()
    assert not result["observable_pass"]["B"].all() and not result["pass"]


def test_fixed_directions_zero_boundary_initial_coordinate_and_tie():
    a = np.array([1, 4, 12, 48])
    y, initial = np.array([0.1, 0.0, 0.02, 0.01]), np.array([0.2, 0.05, 0.0, 0.0])
    directions = jacobian_directions(y, a, initial)
    np.testing.assert_array_equal(directions[0], [0.1, 2.5e-9, 0.02, 0.01])
    np.testing.assert_array_equal(directions[1], [0.1, 2.5e-9, 0.02, -0.01])
    np.testing.assert_array_equal(directions[2], [0.1, 0.0, 0.0, 0.0])


def test_jacobian_independent_polynomial_derivative_oracle():
    y, a = np.array([0.2, 0.3]), np.array([1, 4])

    def f(x):
        return np.array([x[0] ** 3 + 2 * x[0] * x[1], x[0] ** 2 - x[1] ** 3])

    jac = np.array([[3 * y[0] ** 2 + 2 * y[1], 2 * y[0]], [2 * y[0], -3 * y[1] ** 2]])
    for direction in jacobian_directions(y, a, y):
        estimates = np.array(
            [
                (f(y + d * direction) - f(y - d * direction)) / (2 * d)
                for d in JACOBIAN_MULTIPLIERS
            ]
        )
        result = assess_directional_jacobian(
            a, jac @ direction, estimates, np.ones(9, dtype=bool)
        )
        assert result["pass"] and result["stable_windows"].any()
        broken = jac.copy()
        broken[0, 1] = 0  # Omitting a real dependence must fail relevant directions.
        if direction[1]:
            assert not assess_directional_jacobian(
                a, broken @ direction, estimates, np.ones(9, dtype=bool)
            )["pass"]


def test_jacobian_refusals_nonfinite_and_nonadjacent_agreement_are_not_windows():
    estimates = np.zeros((9, 2))
    allowed = np.zeros(9, dtype=bool)
    allowed[[1, 3]] = True
    result = assess_directional_jacobian(A, np.zeros(2), estimates, allowed)
    assert not result["pass"]
    np.testing.assert_array_equal(result["admissible"], allowed)
    allowed[2] = True
    assert assess_directional_jacobian(A, np.zeros(2), estimates, allowed)["pass"]
    estimates[2] = np.nan
    assert not assess_directional_jacobian(A, np.zeros(2), estimates, allowed)["pass"]
    assert not assess_directional_jacobian(A, np.full(2, np.inf), estimates, allowed)[
        "pass"
    ]
    assert not assess_directional_jacobian(
        A, np.zeros(2), estimates, np.zeros(9, dtype=bool)
    )["pass"]


def test_jacobian_successive_estimates_must_agree_not_only_production():
    estimates = np.full((9, 2), np.nan)
    estimates[2, :] = 0.9e-7
    estimates[3, :] = -0.9e-7
    admissible = np.zeros(9, dtype=bool)
    admissible[2:4] = True
    result = assess_directional_jacobian(A, np.zeros(2), estimates, admissible)
    assert result["production_pass"][2:4].all()
    assert not result["adjacent_pass"][2] and not result["pass"]


@pytest.mark.parametrize(
    "bad",
    [
        np.array([True, False]),
        np.array([1 + 0j, 1 + 0j]),
        np.array(["1", "1"]),
        np.array([object(), object()]),
    ],
)
def test_numeric_contract_refuses_boolean_complex_string_object(bad):
    with pytest.raises(ValueError):
        compare_trajectories(
            np.array([0.0, 1.0]), np.zeros((2, 2)), np.zeros((2, 2)), bad, Z
        )


@pytest.mark.parametrize("change", ["shape", "nan", "unordered", "species", "flags"])
def test_malformed_contracts_fail_loudly(change):
    run = nonlinear_exchange(10)
    if change == "shape":
        run["Y"] = run["Y"].T
    elif change == "nan":
        run["accepted_t"][1] = np.nan
    elif change == "unordered":
        run["accepted_t"][1] = run["accepted_t"][0]
    elif change == "species":
        run["A"] = np.array([1.0, 0.0])
    else:
        run["domain_ok"]["accepted"] = np.ones(11)
    with pytest.raises(ValueError):
        trajectory_constraints(**run)


@pytest.mark.parametrize(
    "bad", [True, "1", 0.0, -1.0, np.nan, np.inf, 1 + 0j, 10**400, 1e-5]
)
def test_tolerances_cannot_be_malformed_or_relax_protocol(bad):
    run = nonlinear_exchange(10)
    with pytest.raises(ValueError):
        trajectory_constraints(**run, atol=bad)
    assert trajectory_constraints(**run, atol=1e-14, rtol=1e-12)["pass"]


def test_residual_component_bound_is_inclusive_and_cannot_cancel():
    run = nonlinear_exchange(10)
    scale = 1e-13 + 1e-11 * np.maximum(np.abs(run["Y"][-2]), np.abs(run["Y"][-1]))
    run["residual"][-1] = scale
    assert trajectory_constraints(**run)["checks"]["residual"]
    run["residual"][-1] = [2 * scale[0], -2 * scale[0]]
    assert np.sum(A * run["residual"][-1]) == 0
    assert not trajectory_constraints(**run)["checks"]["residual"]


def test_jacobian_admitted_nonfinite_quotient_cannot_hide_behind_stable_window():
    estimates = np.zeros((9, 2))
    estimates[0, 0] = np.nan
    result = assess_directional_jacobian(
        A, np.zeros(2), estimates, np.ones(9, dtype=bool)
    )
    assert result["stable_windows"].any()
    assert result["invalid_admissible"][0] and not result["pass"]
    admitted = np.ones(9, dtype=bool)
    admitted[0] = (
        False  # Explicit refusal remains visible; a later stable window can pass.
    )
    assert assess_directional_jacobian(A, np.zeros(2), estimates, admitted)["pass"]


def test_jacobian_component_threshold_is_mass_weighted():
    a, jv = np.array([1, 4]), np.zeros(2)
    boundary = 1e-7 / (1 - 1e-3)
    estimates = np.tile(np.array([0.0, boundary * (1 - 1e-8) / 4]), (9, 1))
    assert assess_directional_jacobian(a, jv, estimates, np.ones(9, dtype=bool))["pass"]
    estimates[:, 1] = boundary * (1 + 1e-8) / 4
    assert not assess_directional_jacobian(a, jv, estimates, np.ones(9, dtype=bool))[
        "pass"
    ]


def test_numerical_overflow_and_undefined_moments_are_explicit_failure():
    t = np.array([0.0, 1.0])
    y = np.full((2, 2), 1e308)
    result = compare_trajectories(t, y, y, np.array([1, 4]), Z)
    assert not result["finite"]
    result = compare_trajectories(t, np.zeros((2, 2)), np.zeros((2, 2)), A, Z)
    assert not result["finite"]  # Undefined Ye is not a fabricated zero diagnostic.
    with pytest.raises(ValueError):
        compare_trajectories(np.array([-1e308, 1e308]), y, y, A, Z)


def test_empty_or_malformed_refinement_population_is_not_success():
    with pytest.raises(ValueError):
        assess_refinement([], A, Z)
    with pytest.raises(ValueError):
        assess_refinement([{}, {}, {}, {}], A, Z)
