"""Independent D-024 mathematical oracles, never model or producer outcomes."""

import copy
import json
import math
from fractions import Fraction
from pathlib import Path

import pytest

from crucible.error_budgets import UNITS
from crucible.native_fidelity import PROFILES, evaluate_native

SPECIES = [{"id": "s1", "A": 1, "Z": 0}, {"id": "s4", "A": 4, "Z": 2}]


def case(targets=None, predictions=None):
    targets = targets if targets is not None else [[1000, 0], [100, 2]]
    predictions = predictions if predictions is not None else [[1001, 0], [101, 3]]
    config = {
        "schema": "crucible.native_fidelity.v1",
        "config_id": "synthetic-only",
        "species": copy.deepcopy(SPECIES),
        "profiles": copy.deepcopy(PROFILES),
    }
    ref = {
        "schema": "crucible.rhs_samples.v1",
        "dataset_id": "synthetic-only",
        "species": copy.deepcopy(SPECIES),
        "units": dict(UNITS),
        "network_convention": "closed_full_inventory_no_aux_Q_over_B",
        "samples": [],
    }
    for i, target in enumerate(targets):
        ref["samples"].append(
            {
                "sample_id": f"synthetic:{i}",
                "history_id": f"h{i}",
                "group_id": f"g{i}",
                "category": "synthetic",
                "time_s": i,
                "Y": [1, 0],
                "F": target,
            }
        )
    pred = copy.deepcopy(ref)
    pred["prediction_id"] = "analytic-vector-not-model"
    for row, values in zip(pred["samples"], predictions, strict=True):
        row["F"] = values
    return config, ref, pred


def value(metric):
    return metric["value"]


def test_independent_physical_conversion_signed_and_nonzero_relative_oracle():
    c, r, p = case()
    before = copy.deepcopy((c, r, p))
    report = evaluate_native(c, r, p)
    all_values = report["summary"]["all"]
    assert value(all_values["physical_absolute_rms"]) == pytest.approx(
        math.sqrt(Fraction(9, 2))
    )  # 1,0,1,4 -> 18/4
    assert value(all_values["physical_absolute_max"]) == 4
    assert value(report["per_species"]["s4"]["all"]["physical_signed_mean"]) == 2
    nz = report["summary"]["nonzero"]
    assert nz["reference_components"] == 3
    assert value(nz["relative_rms"]) == pytest.approx(
        math.sqrt(
            float(
                (Fraction(1, 1000) ** 2 + Fraction(1, 100) ** 2 + Fraction(1, 2) ** 2)
                / 3
            )
        )
    )
    assert nz["profiles"]["0.1%"]["component_finite_violations"] == 2
    assert nz["profiles"]["5%"]["component_finite_violations"] == 1
    assert report["records"][0]["profiles"]["0.1%"] is True
    assert report["records"][1]["profiles"]["5%"] is False
    assert (c, r, p) == before


@pytest.mark.parametrize(
    "target,at,profile",
    [(1000.0, 1001.0, "0.1%"), (100.0, 101.0, "1%"), (20.0, 21.0, "5%")],
)
def test_exact_fixed_fraction_threshold_and_adjacent_binary64(target, at, profile):
    c, r, p = case([[target, target]], [[at, at]])
    assert evaluate_native(c, r, p)["records"][0]["profiles"][profile] is True
    p["samples"][0]["F"][1] = math.nextafter(at, math.inf)
    assert evaluate_native(c, r, p)["records"][0]["profiles"][profile] is False
    # Same decision for A=1 and A=4: the positive mass factor cancels exactly.
    p["samples"][0]["F"] = [math.nextafter(at, math.inf), at]
    assert (
        evaluate_native(c, r, p)["records"][0]["components"][0]["profiles"][profile]
        is False
    )


def test_subnormal_reference_cannot_underflow_into_zero_allowance_or_drop_error():
    tiny = math.ulp(0.0)
    c, r, p = case([[tiny, -tiny]], [[tiny, 0]])
    report = evaluate_native(c, r, p)
    nz = report["summary"]["nonzero"]
    assert nz["reference_components"] == 2
    assert value(nz["relative_max"]) == 1
    assert all(v["component_finite_violations"] == 1 for v in nz["profiles"].values())
    assert report["summary"]["zero"]["status"] == "NOT_APPLICABLE"
    assert (
        value(report["per_species"]["s4"]["all"]["physical_absolute_max"]) == 4 * tiny
    )


def test_zero_targets_separate_strict_exactness_and_empty_nonzero_population():
    c, r, p = case([[0, -0.0]], [[0, math.ulp(0.0)]])
    report = evaluate_native(c, r, p)
    zero = report["summary"]["zero"]
    assert zero["zero_target_nonzero_predictions"] == 1
    assert zero["zero_target_nonzero_fraction_valid"] == 0.5
    assert zero["relative_rms"] == {"value": None, "status": "NOT_APPLICABLE"}
    assert all(
        v["component_met"] == 1 and v["record_finite_violations"] == 1
        for v in zero["profiles"].values()
    )
    assert report["summary"]["nonzero"]["reference_components"] == 0
    assert report["summary"]["nonzero"]["status"] == "NOT_APPLICABLE"
    p["samples"][0]["F"] = [0.0, -0.0]
    assert all(evaluate_native(c, r, p)["records"][0]["profiles"].values())


def test_exact_difference_not_rounded_subtraction_controls_thresholds():
    # A large and tiny signed pair has a nonzero exact difference even when a
    # binary64 subtraction would lose the tiny term. Compare to independent Fraction.
    target, pred = 1.0, math.nextafter(1.0, 2.0)
    c, r, p = case([[target, 1]], [[pred, 1]])
    report = evaluate_native(c, r, p)
    expected = Fraction.from_float(pred) - Fraction.from_float(target)
    assert value(
        report["records"][0]["components"][0]["absolute_physical_error"]
    ) == float(expected)


def test_overflow_is_explicit_json_safe_but_finite_vectors_still_score_exactly():
    tiny, huge = math.ulp(0.0), float.fromhex("0x1.fffffffffffffp+1023")
    c, r, p = case([[tiny, huge]], [[huge, -huge]])
    report = evaluate_native(c, r, p)
    assert report["summary"]["all"]["valid_components"] == 2
    assert report["summary"]["all"]["failed_components"] == 0
    assert (
        report["summary"]["nonzero"]["relative_max"]["status"]
        == "UNBOUNDED_BINARY64_REPORT"
    )
    assert (
        report["summary"]["all"]["physical_absolute_max"]["status"]
        == "UNBOUNDED_BINARY64_REPORT"
    )
    assert all(
        v["component_finite_violations"] == 2
        for v in report["summary"]["all"]["profiles"].values()
    )
    json.dumps(report, allow_nan=False)


def test_report_underflow_marked_without_changing_exact_decision():
    huge = float.fromhex("0x1.fffffffffffffp+1023")
    tiny = math.ulp(0.0)
    c, r, p = case([[tiny, huge]], [[0, huge]])
    report = evaluate_native(c, r, p)
    assert (
        report["summary"]["all"]["profiles"]["5%"]["component_finite_violations"] == 1
    )
    # The RMS of [tiny,0] is below the smallest binary64 number and rounds to tiny,
    # while an aggregate signed mean rounds to zero and says so explicitly.
    assert (
        report["summary"]["all"]["physical_signed_mean"]["status"] == "ROUNDED_TO_ZERO"
    )


def test_equal_history_then_equal_group_mse_weights_not_pooled_rows():
    c, r, p = case([[1, 1]] * 4, [[1, 1], [1, 1], [4, 4], [5, 5]])
    # Per-cell relative errors: h0=[0,0,0,0], h1=[3,3], h2=[4,4].
    # h0,h1 in gA: mean history MSE=9/2; gB=16. Group macro MSE=41/4.
    for obj in (r, p):
        for i, row in enumerate(obj["samples"]):
            row["history_id"] = ["h0", "h0", "h1", "h2"][i]
            row["group_id"] = ["gA", "gA", "gA", "gB"][i]
    macro = evaluate_native(c, r, p)["summary"]["nonzero"]["macro"]
    assert value(macro["relative_equal_history_rms"]) == pytest.approx(5 / math.sqrt(3))
    assert value(macro["relative_equal_group_rms"]) == pytest.approx(math.sqrt(41) / 2)
    assert macro["reference_histories"] == 3 and macro["reference_groups"] == 2


@pytest.mark.parametrize("failure", [None, float("nan"), float("inf"), "explicit"])
def test_failed_whole_vectors_keep_component_record_and_stratum_denominators(failure):
    c, r, p = case()
    if failure == "explicit":
        p["samples"][0]["success"] = False
        del p["samples"][0]["F"]
    else:
        p["samples"][0]["F"][1] = failure
    r["samples"][1]["regime"] = {"label": "freeze_out", "provenance": "synthetic tag"}
    report = evaluate_native(c, r, p)
    totals = report["summary"]["all"]
    assert (
        totals["attempted_components"],
        totals["valid_components"],
        totals["failed_components"],
    ) == (4, 2, 2)
    assert totals["failed_records"] == 1
    assert totals["profiles"]["5%"]["component_finite_violations"] == 1
    assert totals["profiles"]["5%"]["component_failed"] == 2
    assert totals["profiles"]["5%"]["record_attainment_fraction_attempted"] == 0
    assert report["strata"]["history_id"]["h0"]["all"]["failed_components"] == 2
    assert report["strata"]["regime"]["unknown"]["all"]["failed_records"] == 1
    assert report["summary"]["zero"]["macro"]["histories_without_valid_components"] == 1
    assert report["physics"]["samples"][0]["prediction"]["status"] == "FAILED"
    json.dumps(report, allow_nan=False)


def test_no_predictions_not_zero_error_or_profile_success():
    c, r, _ = case()
    report = evaluate_native(c, r)
    assert report["status"] == "NOT_EVALUATED"
    assert report["summary"]["all"]["reference_components"] == 4
    assert report["summary"]["all"]["attempted_components"] == 0
    assert report["summary"]["all"]["physical_absolute_rms"]["value"] is None
    assert (
        report["summary"]["all"]["profiles"]["1%"]["component_met_fraction_attempted"]
        is None
    )
    assert report["heating"] == "EXCLUDED_NOT_EVALUATED"


@pytest.mark.parametrize(
    "change", ["species", "sample", "group", "history_consistency", "units", "profiles"]
)
def test_identity_and_fixed_contract_rejections(change):
    c, r, p = case()
    if change == "species":
        p["species"].reverse()
    elif change == "sample":
        p["samples"].reverse()
    elif change == "group":
        p["samples"][0]["group_id"] = "other"
    elif change == "history_consistency":
        for obj in (r, p):
            obj["samples"][1]["history_id"] = "h0"
    elif change == "units":
        p["units"]["F"] = "unknown"
    else:
        c["profiles"][0]["denominator"] = 999
    with pytest.raises(ValueError):
        evaluate_native(c, r, p)


def test_public_synthetic_report_reproduces():
    root = Path(__file__).parents[1] / "configs" / "native_fidelity"

    def load(name):
        return json.loads((root / name).read_text())

    assert evaluate_native(
        load("synthetic_config.json"),
        load("synthetic_reference.json"),
        load("synthetic_prediction.json"),
    ) == load("synthetic_report.json")


@pytest.mark.parametrize(
    "field,malformed",
    [("numerator", True), ("numerator", 1.0), ("denominator", 1000.0)],
)
def test_fixed_profile_integer_types_reject_coherent_numeric_coercions(
    field, malformed
):
    c, r, p = case()
    assert evaluate_native(c, r, p)["status"] == "EVALUATED_NATIVE_FIDELITY"
    c["profiles"][0][field] = malformed
    with pytest.raises(ValueError, match="rational integer profiles"):
        evaluate_native(c, r, p)


def test_empty_population_macro_strata_and_report_cannot_mutate_fixed_profiles():
    c, r, p = case()
    report = evaluate_native(c, r, p)
    macro = report["summary"]["zero"]["macro"]
    assert macro["total_reference_histories"] == 2
    assert macro["histories_without_population_components"] == 1
    assert macro["groups_without_population_components"] == 1
    report["profiles"][0]["numerator"] = 9
    assert evaluate_native(c, r, p)["profiles"][0]["numerator"] == 1


def test_subnormal_threshold_rounding_cannot_turn_violation_into_attainment():
    tiny = math.ulp(0.0)
    c, r, p = case([[999 * tiny, 999 * tiny]], [[1000 * tiny, 1000 * tiny]])
    # Exact relative error 1/999 exceeds 1/1000. A binary64 threshold product
    # rounds 0.999*tiny up to tiny and would incorrectly accept this component.
    report = evaluate_native(c, r, p)
    assert (
        report["summary"]["nonzero"]["profiles"]["0.1%"]["component_finite_violations"]
        == 2
    )
    assert report["records"][0]["profiles"]["0.1%"] is False
    assert report["records"][0]["profiles"]["1%"] is True


def test_whole_vector_attainment_in_every_subset_with_failed_and_successful_controls():
    c, r, p = case([[0, 100]] * 3, [[0, 200], [0, 100], [0, 100]])
    p["samples"][2]["F"][1] = None
    report = evaluate_native(c, r, p)
    assert report["records"][0]["profiles"] == {
        profile["id"]: False for profile in PROFILES
    }
    assert report["records"][1]["profiles"] == {
        profile["id"]: True for profile in PROFILES
    }
    summaries = [report["summary"], *report["per_species"].values()]
    for summary in summaries:
        for population in summary.values():
            if population["reference_records_with_components"]:
                for profile in population["profiles"].values():
                    assert profile["record_attained"] == 1
                    assert profile["record_finite_violations"] == 1
                    assert profile["record_failed"] == 1
                    assert profile["record_attainment_fraction_attempted"] == 1 / 3
    agreeing_subset = report["per_species"]["s1"]["zero"]
    assert agreeing_subset["profiles"]["1%"]["component_met"] == 2
    assert agreeing_subset["profiles"]["1%"]["component_finite_violations"] == 0
    assert agreeing_subset["profiles"]["1%"]["component_failed"] == 1
    for field in report["strata"]:
        for summary in report["strata"][field].values():
            if summary["zero"]["reference_records_with_components"] == 3:
                assert summary["zero"]["profiles"]["1%"]["record_attained"] == 1
    assert (
        report["strata"]["history_id"]["h0"]["zero"]["profiles"]["1%"][
            "record_attained"
        ]
        == 0
    )
    assert (
        report["strata"]["history_id"]["h1"]["zero"]["profiles"]["1%"][
            "record_attained"
        ]
        == 1
    )
    assert (
        report["strata"]["history_id"]["h2"]["zero"]["profiles"]["1%"]["record_failed"]
        == 1
    )


def test_nonfinite_physics_output_is_unavailable_without_erasing_native_scoring():
    from crucible.error_budgets import physics_diagnostics

    c, r, p = case([[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]])
    species = [
        {"id": "a", "A": 1, "Z": 0},
        {"id": "b", "A": 4, "Z": 2},
        {"id": "c", "A": 1, "Z": 0},
    ]
    c["species"] = copy.deepcopy(species)
    for obj in (r, p):
        obj["species"] = copy.deepcopy(species)
        obj["samples"][0]["Y"] = [-4.0, 1.0, math.ulp(0.0)]
        obj["samples"][1]["Y"] = [1.0, 0.0, 0.0]
    before = copy.deepcopy((c, r, p))
    report = evaluate_native(c, r, p)
    assert report["summary"]["zero"]["valid_components"] == 6
    assert report["summary"]["zero"]["profiles"]["0.1%"]["record_attained"] == 2
    assert report["physics"]["samples"][0] == {
        "sample_id": r["samples"][0]["sample_id"],
        "status": "UNAVAILABLE",
        "reason": "nonfinite physics diagnostic output",
    }
    assert report["physics"]["samples"][1] == physics_diagnostics(r, p)["samples"][1]
    assert (c, r, p) == before
    json.dumps(report, allow_nan=False)
    r["network_convention"] = "unsupported_auxiliary_reservoir"
    assert evaluate_native(c, r, p)["physics"] == physics_diagnostics(r, p)
