"""Exact offline arithmetic oracles; never compile or call a producer."""

import copy
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location(
    "phase2d_conditioned_arithmetic",
    Path(__file__).resolve().parents[1]
    / "experiments/trajectory_reference/conditioned_arithmetic.py",
)
arithmetic = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(arithmetic)


def rational(value):
    return Q(int(value["numerator"]), int(value["denominator"]))


def values(quantity):
    return [rational(v) for v in quantity["exact"]]


def weak_group(rate=4.0):
    return {
        "order": 1,
        "participants": [(1, 2, 0, 0, 0)],
        "extended": [(1, 0, -1.0), (2, 0, 1.0)],
        "csect": np.array([rate]),
        "b": np.array([-rate, rate]),
    }


def cancellation_group(rate=float(2**54), middle=1.0):
    return {
        "order": 1,
        "participants": [(2, 1, 0, 0, 0), (2, 1, 0, 0, 0), (1, 2, 0, 0, 0)],
        "extended": [
            (1, 0, 1.0),
            (1, 1, 1.0),
            (1, 2, -1.0),
            (2, 0, -1.0),
            (2, 1, -1.0),
            (2, 2, 1.0),
        ],
        "csect": np.array([rate, middle, rate]),
        "b": np.array([rate, middle, -rate, -rate, -middle, rate]),
    }


def test_exact_weak_assembly_and_fixed_b_derivative_without_eos_or_rates():
    report = arithmetic.coefficient_conditioned(
        [weak_group()], np.array([1, 1]), np.array([0.25, 0.75]), np.array([-1.0, 1.0])
    )
    assert values(report["b_formation"]["exact_a_csect"]) == [-4, 4]
    assert values(report["b_formation"]["native_b_minus_exact"]) == [0, 0]
    assert values(report["assembly"]["exact_fixed_b_F"]) == [-1, 1]
    assert values(report["assembly"]["native_F_minus_exact"]) == [0, 0]
    assert values(report["fixed_b_jacobian"]) == [-4, 0, 4, 0]
    assert report["fixed_b_jacobian"]["shape"] == [2, 2]
    assert rational(report["baryon"]["exact_fixed_b_rate"]) == 0
    assert report["b_formation"]["within_roundoff_envelope"].all()
    assert report["assembly"]["within_roundoff_envelope"].all()
    assert not report["scientific_accuracy_acceptance"]
    assert "combined" in report["assembly_difference_scope"]
    json.dumps(report["fixed_b_jacobian"]["exact"], allow_nan=False)


def test_repeated_reactants_keep_separate_native_entries_and_correct_multiplicity():
    group = {
        "order": 2,
        "participants": [(1, 1, 1, 2, 0, 0)],
        "extended": [(1, 0, -1.0), (1, 0, 0.5), (2, 0, 0.5)],
        "csect": np.array([8.0]),
        "b": np.array([-8.0, 4.0, 4.0]),
    }
    report = arithmetic.coefficient_conditioned(
        [group], np.ones(2), np.array([0.5, 0.5]), np.array([-1.0, 1.0])
    )
    assert values(report["terms"]["exact_fixed_b_values"]) == [-2, 1, 1]
    assert values(report["assembly"]["positive_term_total"]) == [1, 1]
    assert values(report["assembly"]["negative_term_total"]) == [-2, 0]
    assert values(report["assembly"]["absolute_term_total"]) == [3, 1]
    assert (
        rational(report["assembly"]["cancellation_ratio_absolute_over_net"][0]["exact"])
        == 3
    )
    assert report["assembly"]["dominant_term_indices"] == [[0, 1], [2]]
    assert values(report["fixed_b_jacobian"]) == [-4, 0, 4, 0]
    # At zero, repeated reactants give zero derivative without any 0/0 division.
    zero = arithmetic.coefficient_conditioned(
        [group], np.ones(2), np.array([0.0, 1.0]), np.zeros(2)
    )
    assert values(zero["fixed_b_jacobian"]) == [0, 0, 0, 0]
    # A linear reaction still has its nonzero derivative at zero abundance.
    zero_linear = arithmetic.coefficient_conditioned(
        [weak_group()], np.ones(2), np.array([0.0, 1.0]), np.zeros(2)
    )
    assert values(zero_linear["fixed_b_jacobian"]) == [-4, 0, 4, 0]


def test_four_body_two_pairs_preserve_native_max_factorial_not_product_factorials():
    group = {
        "order": 4,
        "participants": [(1, 1, 2, 2, 3, 0)],
        "extended": [(1, 0, -1.0), (2, 0, -1.0), (3, 0, 0.5)],
        "csect": np.array([256.0]),
        "b": np.array([-256.0, -256.0, 128.0]),
    }
    report = arithmetic.coefficient_conditioned(
        [group],
        np.array([1, 1, 4]),
        np.array([0.25, 0.25, 0.0]),
        np.array([-1.0, -1.0, 0.5]),
    )
    assert values(report["assembly"]["exact_fixed_b_F"]) == [-1, -1, Q(1, 2)]
    assert values(report["fixed_b_jacobian"]) == [-8, -8, 0, -8, -8, 0, 4, 4, 0]
    assert rational(report["baryon"]["exact_fixed_b_rate"]) == 0


def test_binary64_a_times_csect_is_separate_from_exact_combinatorial_fraction():
    factor, rate = 1 / 6, 0.1
    b = np.array([-0.5 * rate, factor * rate])
    group = {
        "order": 3,
        "participants": [(1, 1, 1, 3, 0, 0)],
        "extended": [(1, 0, -0.5), (3, 0, factor)],
        "csect": np.array([rate]),
        "b": b,
    }
    report = arithmetic.coefficient_conditioned(
        [group],
        np.array([1, 1, 3]),
        np.array([0.5, 0.5, 0.0]),
        np.array([b[0] / 8, 0.0, b[1] / 8]),
    )
    coefficient = report["b_formation"]
    assert (
        values(coefficient["native_a_minus_combinatorial"])[1]
        == Q(factor) - Q(1, 6)
        != 0
    )
    exact_product = Q(factor) * Q(rate)
    assert values(coefficient["exact_a_csect"])[1] == exact_product
    assert (
        values(coefficient["native_b_minus_exact"])[1]
        == Q(float(b[1])) - exact_product
        != 0
    )
    assert coefficient["within_roundoff_envelope"].all()


def test_b_formation_failure_does_not_change_what_fixed_b_assembly_conditions_on():
    group = weak_group()
    group["b"] = np.array([-3.0, 5.0])
    report = arithmetic.coefficient_conditioned(
        [group], np.ones(2), np.array([0.5, 0.5]), np.array([-1.5, 2.5])
    )
    assert not report["b_formation"]["within_roundoff_envelope"].any()
    assert report["assembly"]["within_roundoff_envelope"].all()
    assert values(report["assembly"]["exact_fixed_b_F"]) == [Q(-3, 2), Q(5, 2)]
    assert rational(report["baryon"]["exact_fixed_b_rate"]) == 1


def test_large_cancellation_reports_combined_error_and_every_dominant_contributor():
    report = arithmetic.coefficient_conditioned(
        [cancellation_group()], np.ones(2), np.ones(2), np.zeros(2)
    )
    assembly = report["assembly"]
    assert values(assembly["exact_fixed_b_F"]) == [1, -1]
    assert values(assembly["native_F_minus_exact"]) == [-1, 1]
    assert values(assembly["positive_term_total"]) == [2**54 + 1, 2**54]
    assert values(assembly["negative_term_total"]) == [-(2**54), -(2**54 + 1)]
    assert values(assembly["absolute_term_total"]) == [2**55 + 1, 2**55 + 1]
    assert (
        rational(assembly["cancellation_ratio_absolute_over_net"][0]["exact"])
        == 2**55 + 1
    )
    assert assembly["dominant_term_indices"] == [[0, 2, 1], [3, 5, 4]]
    assert assembly["within_roundoff_envelope"].all()
    assert not report["scientific_accuracy_acceptance"]


def test_exact_zero_cancellation_and_no_nonzero_terms_have_distinct_labels():
    report = arithmetic.coefficient_conditioned(
        [cancellation_group(middle=0.0)], np.ones(3), np.ones(3), np.zeros(3)
    )
    ratios = report["assembly"]["cancellation_ratio_absolute_over_net"]
    assert ratios[0]["status"] == "UNBOUNDED_EXACT_CANCELLATION"
    assert ratios[2]["status"] == "UNDEFINED_NO_NONZERO_TERMS"
    assert ratios[0]["exact"] is None and ratios[2]["rounded"] is None


def test_DAZ_amplification_envelope_covers_loss_of_subnormal_input():
    report = arithmetic.coefficient_conditioned(
        [weak_group(rate=1e300)], np.ones(2), np.array([1e-320, 1.0]), np.zeros(2)
    )
    error = values(report["assembly"]["native_F_minus_exact"])
    bound = values(report["assembly"]["roundoff_bound"])
    assert abs(error[0]) > Q(1e-21)
    assert abs(error[0]) <= bound[0]
    assert report["assembly"]["within_roundoff_envelope"].all()


def test_overflow_envelope_and_rounded_display_are_labeled_without_losing_exact_result():
    report = arithmetic.coefficient_conditioned(
        [cancellation_group(rate=1e308, middle=1e308)],
        np.ones(2),
        np.ones(2),
        np.zeros(2),
    )
    assert not report["assembly"]["bound_supported"].any()
    assert not report["assembly"]["within_roundoff_envelope"].any()
    assert not report["assembly"]["absolute_term_total"]["rounded_finite"].any()
    assert values(report["assembly"]["absolute_term_total"])[0] == 3 * Q(1e308)


@pytest.mark.parametrize(
    "defect",
    [
        "factor",
        "baryon",
        "target",
        "mu",
        "reactant",
        "duplicate_order",
        "bool_order",
        "bool_participant",
        "nonfinite_b",
        "b_shape",
        "float32_Y",
        "negative_Y",
        "bool_A",
    ],
)
def test_coefficient_inputs_fail_closed_before_exact_arithmetic(defect):
    groups, a, y, f = (
        [weak_group()],
        np.ones(2),
        np.array([0.25, 0.75]),
        np.array([-1.0, 1.0]),
    )
    if defect == "factor":
        groups[0]["extended"][0] = (1, 0, -0.5)
    elif defect == "baryon":
        a = np.array([1, 2])
    elif defect == "target":
        groups[0]["extended"][0] = (3, 0, -1.0)
    elif defect == "mu":
        groups[0]["extended"][0] = (1, 3, -1.0)
    elif defect == "reactant":
        groups[0]["participants"][0] = (0, 2, 0, 0, 0)
    elif defect == "duplicate_order":
        groups *= 2
    elif defect == "bool_order":
        groups[0]["order"] = True
    elif defect == "bool_participant":
        groups[0]["participants"][0] = (True, 2, 0, 0, 0)
    elif defect == "nonfinite_b":
        groups[0]["b"][0] = np.nan
    elif defect == "b_shape":
        groups[0]["b"] = np.zeros(3)
    elif defect == "float32_Y":
        y = y.astype(np.float32)
    elif defect == "negative_Y":
        y[0] = -1e-30
    else:
        a = np.ones(2, dtype=bool)
    with pytest.raises(ValueError):
        arithmetic.coefficient_conditioned(groups, a, y, f)


def test_all_operand_inputs_are_preserved():
    groups, y, f, a = (
        [weak_group()],
        np.array([0.25, 0.75]),
        np.array([-1.0, 1.0]),
        np.ones(2),
    )
    before = copy.deepcopy((groups, y, f, a))
    arithmetic.coefficient_conditioned(groups, a, y, f)
    for key in ("csect", "b"):
        assert groups[0][key].tobytes() == before[0][0][key].tobytes()
    assert groups[0]["participants"] == before[0][0]["participants"]
    for actual, old in zip((y, f, a), before[1:], strict=True):
        assert actual.tobytes() == old.tobytes()


def test_exact_BE_residual_reveals_subtraction_loss_and_uses_actual_mass_scale():
    report = arithmetic.exact_be_residual(
        np.array([1e-20]),
        np.array([1.0]),
        np.array([1.0]),
        1.0,
        np.array([4]),
        reported=np.array([0.0]),
    )
    assert values(report["exact"]) == [-Q(1e-20)]
    assert values(report["reported_minus_exact"]) == [Q(1e-20)]
    assert values(report["mass_weighted_exact"]) == [-4 * Q(1e-20)]
    scale = Q(1e-13) + Q(1e-11) * 4
    assert values(report["nonlinear_scale"]) == [scale]
    assert values(report["normalized_absolute_residual"]) == [4 * Q(1e-20) / scale]
    assert report["offline_separate_operations"][0] == 0.0
    assert rational(report["offline_minus_exact"][0]) == Q(1e-20)
    assert report["within_roundoff_envelope"].all()
    assert not report["scientific_accuracy_acceptance"]


def test_nonlinear_exchange_has_hand_exact_BE_solution_and_reported_residual_cannot_cancel():
    # n'=-4n^2,p'=4n^2: (n,p)=(1/4,3/4) solves BE from(1/2,1/2),h=1.
    report = arithmetic.exact_be_residual(
        np.array([0.5, 0.5]),
        np.array([0.25, 0.75]),
        np.array([-0.25, 0.25]),
        1.0,
        np.array([4, 4]),
        reported=np.array([1e-8, -1e-8]),
        atol=1e-14,
        rtol=1e-12,
    )
    assert values(report["exact"]) == [0, 0]
    assert rational(report["mass_weighted_l1"]) == 0
    assert values(report["reported_minus_exact"]) == [Q(1e-8), -Q(1e-8)]
    assert not report["within_roundoff_envelope"].any()


def test_BE_overflow_preserves_exact_rational_and_reports_unavailable_offline_difference():
    report = arithmetic.exact_be_residual(
        np.array([0.0]), np.array([1.0]), np.array([1e308]), 1e308, np.array([1])
    )
    assert values(report["exact"]) == [1 - Q(1e308) ** 2]
    assert not report["offline_finite"][0] and report["offline_minus_exact"] == [None]
    assert not report["bound_supported"][0]


@pytest.mark.parametrize("h", [True, 0.0, -1.0, np.nan, np.inf, "1", 1 + 0j, 10**400])
def test_BE_refuses_invalid_step(h):
    with pytest.raises(ValueError):
        arithmetic.exact_be_residual(np.zeros(2), np.ones(2), np.ones(2), h, np.ones(2))


def test_BE_refuses_relaxed_nonlinear_control_pair():
    with pytest.raises(ValueError, match="non-protocol"):
        arithmetic.exact_be_residual(
            np.zeros(2), np.ones(2), np.ones(2), 1.0, np.ones(2), atol=1e-5
        )


def test_linear_equation_componentwise_and_mass_scaled_normwise_hand_oracle():
    report = arithmetic.linear_residual(
        np.array([[2.0, 1.0], [1.0, 3.0]]),
        np.array([0.5, -0.25]),
        np.array([0.5, -0.25]),
        np.array([1, 4]),
        reported=np.array([0.25, 0.0]),
    )
    assert values(report["exact"]) == [Q(1, 4), 0]
    assert values(report["componentwise_denominator"]) == [Q(7, 4), Q(3, 2)]
    assert rational(report["componentwise_backward_error"][0]["exact"]) == Q(1, 7)
    assert rational(report["componentwise_backward_error"][1]["exact"]) == 0
    # D M D^-1=[[2,1/4],[4,3]],||.||inf=7;||Ddelta||inf=||Drhs||inf=1.
    assert rational(report["mass_scaled_matrix_linf"]) == 7
    assert rational(report["mass_scaled_delta_linf"]) == 1
    assert rational(report["mass_scaled_rhs_linf"]) == 1
    assert rational(report["normwise_denominator"]) == 8
    assert rational(report["normwise_backward_error"]["exact"]) == Q(1, 32)
    assert values(report["reported_minus_exact"]) == [0, 0]
    assert not report["scientific_accuracy_acceptance"]


def test_linear_large_cancellation_retains_exact_residual_instead_of_false_zero():
    matrix = np.array(
        [[float(2**54), 1.0, -float(2**54)], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )
    report = arithmetic.linear_residual(
        matrix, np.zeros(3), np.ones(3), np.ones(3), reported=np.zeros(3)
    )
    assert values(report["exact"]) == [1, 0, 0]
    assert values(report["reported_minus_exact"]) == [-1, 0, 0]
    assert rational(report["normwise_backward_error"]["exact"]) == Q(1, 2**55 + 1)
    assert report["within_roundoff_envelope"].all()


def test_zero_backward_error_convention_and_inconsistent_reported_residual_unbounded():
    report = arithmetic.linear_residual(
        np.zeros((2, 2)),
        np.zeros(2),
        np.ones(2),
        np.array([1, 4]),
        reported=np.array([1.0, 0.0]),
    )
    assert (
        report["normwise_backward_error"]["status"] == "ZERO_OVER_ZERO_DEFINED_AS_ZERO"
    )
    assert rational(report["normwise_backward_error"]["exact"]) == 0
    assert (
        report["reported_normwise_backward_error"]["status"]
        == "UNBOUNDED_NONZERO_OVER_ZERO"
    )
    assert report["reported_componentwise_backward_error"][0]["rounded"] is None
    assert not report["within_roundoff_envelope"][0]


@pytest.mark.parametrize(
    "defect",
    ["matrix_shape", "matrix_nan", "rhs_inf", "delta_bool", "reported_shape", "A_zero"],
)
def test_linear_contract_shape_type_and_finiteness(defect):
    matrix, rhs, delta, a, reported = (
        np.eye(2),
        np.ones(2),
        np.ones(2),
        np.ones(2),
        np.zeros(2),
    )
    if defect == "matrix_shape":
        matrix = np.ones((2, 3))
    elif defect == "matrix_nan":
        matrix[0, 0] = np.nan
    elif defect == "rhs_inf":
        rhs[0] = np.inf
    elif defect == "delta_bool":
        delta = np.ones(2, dtype=bool)
    elif defect == "reported_shape":
        reported = np.zeros(3)
    else:
        a[0] = 0.0
    with pytest.raises(ValueError):
        arithmetic.linear_residual(matrix, rhs, delta, a, reported=reported)


def test_reported_operation_counts_follow_native_four_class_assembly():
    report = arithmetic.coefficient_conditioned(
        [weak_group()], np.ones(2), np.array([0.25, 0.75]), np.array([-1.0, 1.0])
    )
    assert (
        report["assembly"]["operation_counts"]
        == [
            {
                "product_multiplications": 1,
                "product_operand_occurrences": 2,
                "product_flush_allowance_events": 8,
                "summation_additions": 4,
                "summation_flush_allowance_events": 16,
            }
        ]
        * 2
    )
    be = arithmetic.exact_be_residual(
        np.array([0.0]), np.array([1.0]), np.array([1.0]), 1.0, np.array([1])
    )
    assert be["operation_counts"][0] == {
        "product_multiplications": 1,
        "product_operand_occurrences": 4,
        "product_flush_allowance_events": 16,
        "summation_additions": 3,
        "summation_flush_allowance_events": 12,
    }
    linear = arithmetic.linear_residual(np.eye(2), np.ones(2), np.ones(2), np.ones(2))
    assert (
        linear["operation_counts"]
        == [
            {
                "product_multiplications": 2,
                "product_operand_occurrences": 5,
                "product_flush_allowance_events": 20,
                "summation_additions": 3,
                "summation_flush_allowance_events": 12,
            }
        ]
        * 2
    )


def test_empty_native_reaction_class_preserves_numeric_shapes_and_boolean_status():
    group = {
        "order": 1,
        "participants": np.empty((0, 5), dtype=np.int32),
        "extended": [],
        "csect": np.array([]),
        "b": np.array([]),
    }
    report = arithmetic.coefficient_conditioned(
        [group], np.ones(2), np.array([0.25, 0.75]), np.zeros(2)
    )
    assert report["b_formation"]["exact_a_csect"]["shape"] == [0]
    assert report["b_formation"]["within_roundoff_envelope"].dtype == bool
    assert values(report["assembly"]["exact_fixed_b_F"]) == [0, 0]
    assert values(report["fixed_b_jacobian"]) == [0, 0, 0, 0]
    assert all(
        v["status"] == "UNDEFINED_NO_NONZERO_TERMS"
        for v in report["assembly"]["cancellation_ratio_absolute_over_net"]
    )


@pytest.mark.parametrize(
    "participants",
    [np.array(1), [np.array(1)], [1], [(1, 2)], np.ones((1, 5), dtype=bool)],
)
def test_malformed_participant_container_is_a_validation_error(participants):
    group = weak_group()
    group["participants"] = participants
    with pytest.raises(ValueError):
        arithmetic.coefficient_conditioned(
            [group], np.ones(2), np.array([0.25, 0.75]), np.array([-1.0, 1.0])
        )
