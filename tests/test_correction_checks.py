"""Independent small mathematical and failure oracles for the D-040 checker."""

import importlib.util
import math
import struct
from fractions import Fraction
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "correction_checks_tests",
    Path(__file__).resolve().parents[1]
    / "experiments/trajectory_reference/correction_checks.py",
)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)


def stiff_record(iteration, controls, previous=None):
    """Affine stiff BE has a rational root whose nearest float is exactly 0.5."""
    h, rate, source = Fraction(1, 10000), 10**12, Fraction(1, 100000)
    exact = Fraction(1, 2) + h * source / (1 + h * rate)
    assert float(exact) == 0.5
    delta = float(h * source / (1 + h * rate))
    y = (0.5,) * 160
    raw = (delta,) + (0.0,) * 159
    applied = (0.0,) * 160
    weight = (controls[0] + controls[1] * 0.5,) * 160
    residual = (-float(h) * float(source),) + (0.0,) * 159
    f = (float(source),) + (0.0,) * 159
    current = delta / weight[0]
    prior = current if previous is not None else math.nan
    scalars = (
        float(h),
        float(h),
        abs(residual[0]) / (1e-13 + 1e-11 * 0.5),
        abs(residual[0]),
        0.0,
        0.0,
        1e-13,
        1e-11,
        *controls,
        current,
        prior,
        delta,
        delta,
        0.0,
        0.0,
    )
    return {
        "ids": (iteration, 1, iteration, iteration, 1, 2, 3, 0, 0, 4, 1, 1),
        "scalars": scalars,
        "old": y,
        "pre": y,
        "unprojected": y,
        "post": y,
        "delta": raw,
        "previous": raw if previous is not None else (math.nan,) * 160,
        "applied": applied,
        "weight": weight,
        "residual": residual,
        "projection": applied,
        "variant": f,
        "original": f,
    }


@pytest.mark.parametrize("controls", checks.CONTROLS.values())
def test_correctly_rounded_stiff_be_can_have_large_residual(controls):
    first = stiff_record(1, controls)
    second = stiff_record(2, controls, first)
    assert not checks.verify_newton(first, (1.0,) * 160, controls)["small_pair"]
    result = checks.verify_newton(second, (1.0,) * 160, controls, first)
    assert result["small_pair"]
    assert result["residual_norm"] > 100
    assert second["post"] == second["pre"]
    assert second["delta"][0] != 0


def test_rounded_applied_update_cannot_replace_raw_correction_test():
    # Stricter SYNTHETIC weights make a lost raw correction unacceptable.
    controls = (1e-20, 0.0)
    first = stiff_record(1, controls)
    second = stiff_record(2, controls, first)
    result = checks.verify_newton(second, (1.0,) * 160, controls, first)
    assert all(v == 0 for v in second["applied"])
    assert result["current"] > 100
    assert not result["small_pair"]


def test_retry_requires_unavailable_previous_correction():
    row = stiff_record(1, checks.CONTROLS["standard"])
    row["previous"] = (0.0,) * 160
    with pytest.raises(ValueError, match="reset correction history"):
        checks.verify_newton(row, (1.0,) * 160, checks.CONTROLS["standard"])


def test_previous_correction_norm_cannot_be_forged():
    first = stiff_record(1, checks.CONTROLS["standard"])
    second = stiff_record(2, checks.CONTROLS["standard"], first)
    scalars = list(second["scalars"])
    scalars[11] *= 0.1
    second["scalars"] = tuple(scalars)
    with pytest.raises(ValueError, match="numerical calculation differs"):
        checks.verify_newton(second, (1.0,) * 160, checks.CONTROLS["standard"], first)


def test_recomputed_raw_residual_refuses_fabricated_zero():
    row = stiff_record(1, checks.CONTROLS["standard"])
    row["residual"] = (0.0,) * 160
    with pytest.raises(ValueError, match="numerical calculation differs"):
        checks.verify_newton(row, (1.0,) * 160, checks.CONTROLS["standard"])


def test_negative_zero_survives_declared_projection():
    row = stiff_record(1, checks.CONTROLS["standard"])
    # No repair applies to an already signed-zero coordinate.
    for key in ("old", "pre", "unprojected", "post"):
        row[key] = row[key][:-1] + (-0.0,)
    row["weight"] = row["weight"][:-1] + (1e-15,)
    checks.verify_newton(row, (1.0,) * 160, checks.CONTROLS["standard"])


def test_strict_refinement_handles_nonnested_native_retries():
    assert checks.strict_refinement([0, 0.4, 1], [0, 0.2, 0.5, 1])
    assert not checks.strict_refinement([0, 0.4, 1], [0, 0.4, 1])
    assert not checks.strict_refinement([0, 0.4, 1], [0, 1])


def test_difference_uses_every_component_and_all_requested_times():
    first = [(0.5,) * 160] * 3
    second = list(first)
    changed = list(second[1])
    changed[159] += 1e-5
    second[1] = tuple(changed)
    result = checks.compare_values(first, second, (2.0,) * 160)
    assert result["linf"] == result["l1"] > 1e-5
    assert result["linf_location"] == [1, 159]


def constant_trajectory(tmp_path, times):
    """A zero-source IVP independently fixes every requested state exactly."""
    a = tuple(float(i) for i in range(1, 161))
    z = tuple(float(i // 2) for i in range(1, 161))
    y = tuple(1 / (160 * m) for m in a)
    zeros = (0.0,) * 160
    b = math.fsum(m * v for m, v in zip(a, y, strict=True))
    charge = math.fsum(m * v for m, v in zip(z, y, strict=True))
    accepted, physical = [], []
    for i, time in enumerate(times):
        accepted.extend((time, *y, *zeros, *zeros, b, charge, charge / b, 0, 0, 0, 0))
        physical.extend(
            (
                i + 1,
                11,
                i,
                time,
                1,
                100,
                b,
                charge,
                charge / b,
                0,
                0,
                0,
                1,
                1,
                1,
                1,
                *y,
                *zeros,
                *zeros,
            )
        )
    (tmp_path / "accepted.bin").write_bytes(
        struct.pack("<" + str(len(accepted)) + "d", *accepted)
    )
    (tmp_path / "correction-accepted.bin").write_bytes(
        struct.pack("<8i", *checks.ACCEPTED_HEADER)
        + struct.pack("<" + str(len(physical)) + "d", *physical)
    )
    return {
        "A": a,
        "Z": z,
        "Y0": y,
        "knots": (0, 0.01),
        "T9": (1, 1),
        "rho": (100, 100),
        "outputs": (0, 0.005, 0.01),
        "mesh": (0, 0.005, 0.01),
    }


def test_successful_full_constant_solution_has_all_requested_outputs(tmp_path):
    data = constant_trajectory(tmp_path, [0, 0.005, 0.01])
    result = checks.trajectory_data(tmp_path, data, validate=False)
    assert result["requested_Y"] == [data["Y0"]] * 3
    assert result["max_baryon_drift"] == 0


def test_requested_output_hole_refused_even_when_endpoint_completed(tmp_path):
    data = constant_trajectory(tmp_path, [0, 0.01])
    with pytest.raises(ValueError, match="output missing"):
        checks.trajectory_data(tmp_path, data, validate=False)


def test_short_horizon_cannot_be_trajectory_success(tmp_path):
    data = constant_trajectory(tmp_path, [0, 0.005, 0.009])
    with pytest.raises(ValueError, match="accepted horizon"):
        checks.trajectory_data(tmp_path, data, validate=False)
