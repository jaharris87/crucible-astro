"""Hand-computed mathematical oracles; no nuclear/model/producer evaluation."""

import copy
import json
from pathlib import Path

import pytest

from crucible.error_budgets import UNITS, evaluate, physics_diagnostics

SPECIES = [
    {"id": "n", "A": 1, "Z": 0},
    {"id": "p", "A": 1, "Z": 1},
    {"id": "a", "A": 4, "Z": 2},
]


def inputs():
    reference = {
        "schema": "crucible.rhs_samples.v1",
        "dataset_id": "synthetic-only",
        "species": copy.deepcopy(SPECIES),
        "units": dict(UNITS),
        "network_convention": "closed_full_inventory_no_aux_Q_over_B",
        "samples": [],
    }
    for i in range(3):
        reference["samples"].append(
            {
                "sample_id": f"raw-digest:record:{i}",
                "history_id": "h0" if i < 2 else "h1",
                "group_id": "g0" if i < 2 else "g1",
                "category": "c0" if i < 2 else "c1",
                "time_s": i,
                "Y": [2, 1, 0],
                "F": [0, 0, 0],
            }
        )
    prediction = copy.deepcopy(reference)
    prediction["prediction_id"] = "analytic-test-vector-not-a-model"
    budget = {
        "absolute_change": 0,
        "timescale_s": 2,
        "scale": {"mode": "explicit", "value": 2, "provenance": "synthetic hand bound"},
    }
    config = {
        "schema": "crucible.error_budgets.v1",
        "config_id": "synthetic-only",
        "species": copy.deepcopy(SPECIES),
        "abundance_space": "Y",
        "relative_tiers": [0.001, 0.01, 0.05],
        "critical_species": ["a"],
        "critical_selection_provenance": "synthetic trace sentinel only",
        "species_budgets": {s["id"]: copy.deepcopy(budget) for s in SPECIES},
        "groups": [],
    }
    return config, reference, prediction


def metric(report, species="n", tier="0.01"):
    return report["quantities"][species]["tiers"][tier]


def test_tiers_rms_max_and_physical_timescale():
    c, r, p = inputs()
    for row, value in zip(p["samples"], [0, 0.01, 0.02], strict=True):
        row["F"][0] = value
    report = evaluate(c, r, p)
    m = metric(report)
    assert m["rate_budget"] == 0.01  # (0 + .01*2)/2
    assert m["summary"]["normalized_rms"] == pytest.approx((5 / 3) ** 0.5)
    assert m["summary"]["max_normalized_error"] == 2
    assert m["summary"]["fraction_exceeding_evaluated"] == 1 / 3
    assert m["summary"]["physical_absolute_max"] == 0.02
    assert [
        metric(report, tier=t)["rate_budget"] for t in ["0.001", "0.01", "0.05"]
    ] == [0.001, 0.01, 0.05]
    for row in r["samples"] + p["samples"]:
        row["numerical_solver_dt_s"] = 1e-30
    assert evaluate(c, r, p) == report  # No solver dt in the physical budget.
    assert report["integrated_scientific_accuracy"] == "NOT_EVALUATED"
    assert report["scientific_qualified"] is False


def test_conversion_and_compensating_group_cannot_hide_trace_maximum():
    c, r, p = inputs()
    c["abundance_space"] = "X"
    for row in p["samples"]:
        row["F"] = [-4, 0, 1]
    c["groups"] = [
        {
            "id": "group:cancel",
            "coefficients": {"n": 1, "a": 1},
            "budget": copy.deepcopy(c["species_budgets"]["n"]),
        }
    ]
    report = evaluate(c, r, p)
    assert metric(report, "a")["summary"]["physical_absolute_max"] == 4
    assert metric(report, "group:cancel")["summary"]["physical_absolute_max"] == 0
    assert report["quantities"]["a"]["critical"] is True
    assert metric(report, "a")["summary"]["max_normalized_error"] == 400
    assert report["pointwise_budget_status"] == "VIOLATIONS"


def interval(reference):
    return {
        k: copy.deepcopy(reference[k])
        for k in ("schema", "dataset_id", "species", "units")
    } | {
        "interval_id": "i0",
        "history_id": "separate-reference-history",
        "qualified": True,
        "qualification_provenance": "synthetic analytic oracle only",
        "coverage_provenance": "all three declared samples",
        "coverage_s": [0, 2],
        "times_s": [0, 1, 2],
        "Y": [[0, 0, 0], [3, 0, 0], [0, 0, 0]],
        "semantics": "discrete_samples_no_interpolation",
    }


def test_sampled_interior_excursion_not_endpoint_difference():
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"] = {
        "mode": "sampled_max_excursion",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
        "interval_id": "i0",
    }
    report = evaluate(c, r, p, intervals={"i0": interval(r)})
    scale = report["quantities"]["n"]["scale"]
    assert scale["value"] == 3  # Endpoints cancel to zero, interior does not.
    assert scale["continuous_maximum"] is False
    assert metric(report)["rate_budget"] == 0.015
    c["abundance_space"] = "X"
    iv = interval(r)
    iv["Y"] = [[0, 0, 0], [0, 0, 3], [0, 0, 0]]
    c["species_budgets"]["a"]["scale"] = {
        "mode": "sampled_max_excursion",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
        "interval_id": "i0",
    }
    assert (
        evaluate(c, r, p, intervals={"i0": iv})["quantities"]["a"]["scale"]["value"]
        == 12
    )


@pytest.mark.parametrize("change", ["coverage", "time", "semantics", "order"])
def test_interval_does_not_bridge_or_reorder(change):
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"] = {
        "mode": "sampled_max_excursion",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
        "interval_id": "i0",
    }
    iv = interval(r)
    if change == "coverage":
        iv["coverage_s"] = [0, 3]
    elif change == "time":
        iv["times_s"] = [0, 2, 1]
    elif change == "semantics":
        iv["semantics"] = "interpolate_unknown_gaps"
    else:
        iv["species"].reverse()
    with pytest.raises(ValueError):
        evaluate(c, r, p, intervals={"i0": iv})


def test_unqualified_interval_and_group_member_gaps_cannot_pass():
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"] = {
        "mode": "sampled_max_excursion",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
        "interval_id": "i0",
    }
    c["groups"] = [
        {
            "id": "group:all",
            "coefficients": {"n": 1, "p": 1},
            "budget": copy.deepcopy(c["species_budgets"]["p"]),
        }
    ]
    iv = interval(r)
    iv["qualified"] = False
    report = evaluate(c, r, p, intervals={"i0": iv})
    assert metric(report)["rate_budget"] is None
    assert metric(report)["summary"]["budget_not_evaluated"] == 3
    assert report["quantities"]["group:all"]["constituent_budget_gaps"]["n"]
    assert report["pointwise_budget_status"] == "INCOMPLETE"


@pytest.mark.parametrize("key", ["absolute_change", "timescale_s", "scale"])
def test_null_unresolved_is_not_success(key):
    c, r, p = inputs()
    c["species_budgets"]["n"][key] = None
    report = evaluate(c, r, p)
    assert metric(report)["status"] == "INCOMPLETE"
    assert metric(report)["summary"]["max_normalized_error"] is None
    assert report["pointwise_budget_status"] == "INCOMPLETE"


def test_zero_budget_exact_match_and_nonzero_unbounded_violation():
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"]["value"] = 0
    p["samples"][1]["F"][0] = 1
    report = evaluate(c, r, p)
    m = metric(report)
    assert m["records"][0]["normalized_error"] == 0
    assert m["records"][1]["normalized_error"] is None
    assert m["summary"]["unbounded_normalizations"] == 1
    assert m["summary"]["normalization_status"] == "UNBOUNDED"
    assert m["summary"]["exceeded"] == 1
    assert report["pointwise_budget_status"] == "VIOLATIONS"
    json.dumps(report, allow_nan=False)


def test_failed_and_nonfinite_predictions_keep_all_denominators_and_strata():
    c, r, p = inputs()
    p["samples"][0]["F"][0] = float("nan")
    p["samples"][1]["success"] = False
    p["samples"][2]["F"][0] = 1
    r["samples"][2]["regime"] = {
        "label": "freeze_out",
        "provenance": "synthetic supplied tag",
    }
    report = evaluate(c, r, p)
    m = metric(report)
    assert (
        m["summary"]["attempted"],
        m["summary"]["valid"],
        m["summary"]["failed"],
    ) == (3, 1, 2)
    assert m["summary"]["violations_or_failed_fraction_attempted"] == 1
    assert m["summary"]["exceed_fraction_denominator"] == 1
    assert m["strata"]["history_id"]["h0"]["failed"] == 2
    assert m["strata"]["group_id"]["g1"]["attempted"] == 1
    assert m["strata"]["category"]["c0"]["attempted"] == 2
    assert m["strata"]["regime"]["unknown"]["attempted"] == 2
    assert m["strata"]["regime"]["freeze_out"]["attempted"] == 1
    assert report["samples"][2]["regime"]["provenance"] == "synthetic supplied tag"
    assert report["pointwise_budget_status"] == "INCOMPLETE"
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), None])
def test_other_nonfinite_predictions_fail_not_drop(value):
    c, r, p = inputs()
    p["samples"][0]["F"][0] = value
    assert metric(evaluate(c, r, p))["summary"]["failed"] == 1


def test_no_predictions_and_unknown_critical_selection():
    c, r, p = inputs()
    report = evaluate(c, r)
    assert report["pointwise_budget_status"] == "NOT_EVALUATED"
    assert metric(report)["summary"]["physical_absolute_max"] is None
    c["critical_species"] = None
    assert evaluate(c, r, p)["pointwise_budget_status"] == "INCOMPLETE"


@pytest.mark.parametrize(
    "change",
    [
        "order",
        "sample",
        "history",
        "group",
        "category",
        "time",
        "unit",
        "schema",
        "duplicate",
    ],
)
def test_strict_identity_and_units(change):
    c, r, p = inputs()
    if change == "order":
        p["species"].reverse()
    elif change in {"sample", "history", "group", "category"}:
        p["samples"][0]["category" if change == "category" else change + "_id"] = (
            "wrong"
        )
    elif change == "time":
        p["samples"][0]["time_s"] = 999
    elif change == "unit":
        p["units"]["F"] = "unknown"
    elif change == "schema":
        p["schema"] = "future"
    else:
        p["samples"][1]["sample_id"] = p["samples"][0]["sample_id"]
    with pytest.raises(ValueError):
        evaluate(c, r, p)


def test_weak_ye_quotient_rule_not_fixed_charge_and_no_projection():
    c, r, p = inputs()
    r["samples"][0]["F"] = [1, 1, 0]
    r["samples"][1]["F"] = [1, -1, 0]
    r["samples"][2]["Y"] = [2, 1, -0.1]
    p["samples"][0]["F"] = [0, 0, -1]
    before = copy.deepcopy(r)
    report = evaluate(c, r, p)
    rows = report["physics"]["samples"]
    assert rows[0]["B"] == 3
    assert rows[0]["Ye"] == 1 / 3
    assert rows[0]["reference"]["baryon_rate_residual"] == 2
    assert rows[0]["reference"]["dYe_dt"] == pytest.approx(1 / 9)
    assert rows[1]["reference"]["baryon_rate_residual"] == 0
    assert rows[1]["reference"]["dYe_dt"] == pytest.approx(-1 / 3)
    assert rows[0]["prediction"]["boundary_incompatible_species"] == ["a"]
    assert rows[2]["negative_state_species"] == ["a"]
    assert r == before
    assert report["heating"] == "EXCLUDED_NOT_EVALUATED"


def test_open_network_diagnostics_are_unavailable():
    _, r, _ = inputs()
    r["network_convention"] = "newer_auxiliary_reservoir"
    assert physics_diagnostics(r)["status"] == "UNAVAILABLE"


@pytest.mark.parametrize(
    "key,value",
    [("timescale_s", 0), ("absolute_change", -1), ("timescale_s", float("inf"))],
)
def test_invalid_budgets_rejected(key, value):
    c, r, p = inputs()
    c["species_budgets"]["n"][key] = value
    with pytest.raises(ValueError):
        evaluate(c, r, p)


def test_portable_json_example_report():
    root = Path(__file__).parents[1] / "configs" / "error_budgets"
    c = json.loads((root / "provisional_tiers.json").read_text())
    r = json.loads((root / "synthetic_reference.json").read_text())
    expected = json.loads((root / "synthetic_readiness_report.json").read_text())
    assert evaluate(c, r) == expected


def test_explicit_failed_record_without_array_is_counted():
    c, r, p = inputs()
    p["samples"][0]["success"] = False
    del p["samples"][0]["F"]
    report = evaluate(c, r, p)
    assert metric(report)["summary"]["failed"] == 1
    assert report["physics"]["samples"][0]["prediction"]["status"] == "FAILED"
    assert report["prediction_attempt_count"] == 3


def test_standalone_physics_rejects_misaligned_prediction():
    _, r, p = inputs()
    p["samples"].reverse()
    with pytest.raises(ValueError, match="identity/order mismatch"):
        physics_diagnostics(r, p)


def test_missing_predictions_preserve_declared_reference_population():
    c, r, _ = inputs()
    report = evaluate(c, r)
    assert report["reference_sample_count"] == 3
    assert report["prediction_attempt_count"] == 0
    assert len(report["samples"]) == 3


def test_resolved_synthetic_example_is_reproducible_and_cancellation_visible():
    root = Path(__file__).parents[1] / "configs" / "error_budgets"
    c, r, p, expected = [
        json.loads((root / name).read_text())
        for name in (
            "synthetic_oracle.json",
            "synthetic_reference.json",
            "synthetic_prediction.json",
            "synthetic_diagnostic_report.json",
        )
    ]
    report = evaluate(c, r, p)
    assert report == expected
    assert (
        metric(report, "synthetic_p", "0.001")["summary"]["max_normalized_error"] == 10
    )
    assert (
        metric(report, "group:cancel", "0.001")["summary"]["max_normalized_error"] == 0
    )


def test_null_scale_value_and_provenance_are_unresolved_choices():
    c, r, p = inputs()
    for key in ["value", "provenance"]:
        cc = copy.deepcopy(c)
        cc["species_budgets"]["n"]["scale"][key] = None
        assert metric(evaluate(cc, r, p))["status"] == "INCOMPLETE"


def test_nonfinite_reference_state_is_not_a_successful_comparison():
    c, r, p = inputs()
    r["samples"][0]["Y"][0] = float("inf")
    report = evaluate(c, r, p)
    assert metric(report)["summary"]["failed"] == 1
    assert report["physics"]["samples"][0]["status"] == "FAILED"


def test_sampled_calibration_horizon_must_match_physical_timescale():
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"] = {
        "mode": "sampled_max_excursion",
        "interval_id": "i0",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
    }
    c["species_budgets"]["n"]["timescale_s"] = 1
    with pytest.raises(ValueError, match="duration must equal"):
        evaluate(c, r, p, intervals={"i0": interval(r)})
    c["species_budgets"]["n"]["timescale_s"] = 2
    assert (
        metric(evaluate(c, r, p, intervals={"i0": interval(r)}))["rate_budget"] == 0.015
    )
    c["species_budgets"]["n"]["scale"]["frozen_before_testing"] = False
    with pytest.raises(ValueError, match="frozen fixed calibration"):
        evaluate(c, r, p, intervals={"i0": interval(r)})


@pytest.mark.parametrize("malformed", [True, "3"], ids=["boolean", "numeric-string"])
def test_sampled_interval_rejects_coerced_components_with_numeric_control(malformed):
    c, r, p = inputs()
    c["species_budgets"]["n"]["scale"] = {
        "mode": "sampled_max_excursion",
        "usage": "fixed_calibration_interval",
        "frozen_before_testing": True,
        "calibration_provenance": "synthetic predeclared calibration",
        "interval_id": "i0",
    }
    iv = interval(r)
    iv["Y"][1][0] = 3.0
    control = evaluate(c, r, p, intervals={"i0": iv})
    assert control["quantities"]["n"]["scale"]["value"] == 3
    assert metric(control)["rate_budget"] == 0.015
    assert control["pointwise_budget_status"] == "NO_VIOLATIONS_PROVISIONAL"
    iv["Y"][1][0] = malformed
    with pytest.raises(
        ValueError, match="array components must be numeric or null failures"
    ):
        evaluate(c, r, p, intervals={"i0": iv})
