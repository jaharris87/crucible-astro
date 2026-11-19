"""D-024 exact digital native-RHS scoring, distinct from physical change budgets.

No fitting, qualification, integration or producer execution. All successful
statistics are explicitly conditional on finite whole-vector predictions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import numpy as np

from crucible.error_budgets import (
    IDENTITY,
    _metadata,
    _prediction_rows,
    _samples,
    _text,
    _vector,
    physics_diagnostics,
)

PROFILES = [
    {"id": "0.1%", "numerator": 1, "denominator": 1000},
    {"id": "1%", "numerator": 1, "denominator": 100},
    {"id": "5%", "numerator": 1, "denominator": 20},
]
SCHEMA = "crucible.native_fidelity.v1"


def _digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def _metric(value, *, sqrt=False):
    if value is None:
        return {"value": None, "status": "NOT_APPLICABLE"}
    try:
        if sqrt:
            with localcontext() as context:
                context.prec = 70
                number = Decimal(value.numerator) / Decimal(value.denominator)
                result = float(number.sqrt())
        else:
            result = float(
                value
            )  # Fraction conversion preserves binary64 tie rounding.
    except OverflowError:
        return {"value": None, "status": "UNBOUNDED_BINARY64_REPORT"}
    if not math.isfinite(result):
        return {"value": None, "status": "UNBOUNDED_BINARY64_REPORT"}
    return {
        "value": result,
        "status": "ROUNDED_TO_ZERO" if result == 0 and value != 0 else "FINITE",
    }


def _mean(values):
    return sum(values, Fraction()) / len(values) if values else None


def _summary(rows, population, indices, predictions_present):
    selected = []
    relevant_rows = []
    for row in rows:
        cells = [
            row["cells"][i]
            for i in indices
            if population == "all" or row["cells"][i]["population"] == population
        ]
        if cells:
            relevant_rows.append((row, cells))
            selected.extend((row, cell) for cell in cells)
    valid = [(row, cell) for row, cell in selected if row["valid"]]
    attempted = len(selected) if predictions_present else 0
    failed = attempted - len(valid)
    result = {
        "status": "NOT_APPLICABLE"
        if not selected
        else (
            "NOT_EVALUATED"
            if not predictions_present
            else ("CONDITIONAL_VALID" if failed else "EVALUATED")
        ),
        "reference_components": len(selected),
        "attempted_components": attempted,
        "valid_components": len(valid),
        "failed_components": failed,
        "reference_records_with_components": len(relevant_rows),
        "attempted_records": len(relevant_rows) if predictions_present else 0,
        "valid_records": sum(row["valid"] for row, _ in relevant_rows),
        "failed_records": sum(not row["valid"] for row, _ in relevant_rows)
        if predictions_present
        else 0,
        "conditional_valid_statistics": True,
    }
    errors = [cell["error"] for _, cell in valid]
    squares = [e * e for e in errors]
    relatives = (
        [cell["relative"] for _, cell in valid] if population == "nonzero" else []
    )
    result.update(
        physical_signed_mean=_metric(_mean(errors)),
        physical_signed_min=_metric(min(errors, default=None)),
        physical_signed_max=_metric(max(errors, default=None)),
        physical_absolute_rms=_metric(_mean(squares), sqrt=True),
        physical_absolute_max=_metric(max(map(abs, errors), default=None)),
        relative_rms=_metric(_mean([r * r for r in relatives]), sqrt=True),
        relative_max=_metric(max(relatives, default=None)),
    )
    # One history belongs to one group; this relation is validated before scoring.
    histories = {}
    for row, cell in valid:
        histories.setdefault(row["sample"]["history_id"], []).append(cell)
    declared_histories = {row["sample"]["history_id"] for row, _ in relevant_rows}
    declared_groups = {row["sample"]["group_id"] for row, _ in relevant_rows}
    macro = {
        "total_reference_histories": len({row["sample"]["history_id"] for row in rows}),
        "histories_without_population_components": len(
            {row["sample"]["history_id"] for row in rows} - declared_histories
        ),
        "total_reference_groups": len({row["sample"]["group_id"] for row in rows}),
        "groups_without_population_components": len(
            {row["sample"]["group_id"] for row in rows} - declared_groups
        ),
        "reference_histories": len(declared_histories),
        "valid_histories": len(histories),
        "histories_without_valid_components": len(
            declared_histories - histories.keys()
        ),
        "reference_groups": len(declared_groups),
        "conditional_valid_statistics": True,
        "failed_components": failed,
        "failed_records": result["failed_records"],
    }
    for name, field in [("physical", "error"), ("relative", "relative")]:
        h_mse = (
            {h: _mean([c[field] ** 2 for c in cells]) for h, cells in histories.items()}
            if name == "physical" or population == "nonzero"
            else {}
        )
        group_mse = {}
        for row, _ in relevant_rows:
            h, g = row["sample"]["history_id"], row["sample"]["group_id"]
            if h in h_mse:
                group_mse.setdefault(g, {})[h] = h_mse[h]
        macro[name + "_equal_history_rms"] = _metric(
            _mean(list(h_mse.values())), sqrt=True
        )
        macro[name + "_equal_group_rms"] = _metric(
            _mean([_mean(list(values.values())) for values in group_mse.values()]),
            sqrt=True,
        )
        if name == "physical":
            macro["valid_groups"] = len(group_mse)
            macro["groups_without_valid_components"] = len(
                declared_groups - group_mse.keys()
            )
    result["macro"] = macro
    result["profiles"] = {}
    for profile in PROFILES:
        key = profile["id"]
        met = sum(cell["meets"][key] for _, cell in valid)
        attained = sum(
            row["valid"] and all(c["meets"][key] for c in cells)
            for row, cells in relevant_rows
        )
        valid_records = result["valid_records"]
        result["profiles"][key] = {
            "component_met": met,
            "component_finite_violations": len(valid) - met,
            "component_failed": failed,
            "component_exceedance_denominator_valid": len(valid),
            "component_fraction_exceeding_valid": (len(valid) - met) / len(valid)
            if valid
            else None,
            "component_met_fraction_attempted": met / attempted if attempted else None,
            "record_attained": attained,
            "record_finite_violations": valid_records - attained,
            "record_failed": result["failed_records"],
            "record_attainment_fraction_attempted": attained
            / result["attempted_records"]
            if result["attempted_records"]
            else None,
        }
    if population == "zero":
        nonzero = sum(cell["error"] != 0 for _, cell in valid)
        result["zero_target_nonzero_predictions"] = nonzero
        result["zero_target_nonzero_fraction_valid"] = (
            nonzero / len(valid) if valid else None
        )
    return result


def evaluate_native(config, reference, prediction=None):
    """Compare decoded binary64 predictions with exact retained digital labels.

    Threshold decisions and physical differences use exact rational arithmetic.
    Decimal is used only to render scalar reports; it never decides attainment.
    """
    profiles = config.get("profiles")
    if (
        config.get("schema") != SCHEMA
        or profiles != PROFILES
        or not isinstance(profiles, list)
        or any(
            not isinstance(p, dict)
            or type(p.get("numerator")) is not int
            or type(p.get("denominator")) is not int
            for p in profiles
        )
    ):
        raise ValueError(
            "native schema and fixed D-024 rational integer profiles required"
        )
    _text(config.get("config_id"), "config_id")
    species, ids = _metadata(reference)
    if config.get("species") != species:
        raise ValueError("native config species identity/order mismatch")
    samples = _samples(reference, len(species), reference=True)
    prows = _prediction_rows(reference, prediction, samples, len(species))
    history_groups = {}
    for sample in samples:
        h = sample["history_id"]
        group_category = (sample["group_id"], sample["category"])
        if h in history_groups and history_groups[h] != group_category:
            raise ValueError("one history must have a consistent group/category")
        history_groups[h] = group_category
    rows = []
    records = []
    for index, sample in enumerate(samples):
        target = _vector(sample["F"])
        state = _vector(sample["Y"])
        if not np.all(np.isfinite(target)) or not np.all(np.isfinite(state)):
            raise ValueError("native reference Y/F must be finite binary64 values")
        pred = prows[index] if prows is not None else None
        output = (
            _vector(pred["F"])
            if pred is not None and pred.get("success", True) is True
            else None
        )
        valid = output is not None and bool(np.all(np.isfinite(output)))
        cells, reported_cells = [], []
        for j, s in enumerate(species):
            f = Fraction(float(target[j]))
            population = "nonzero" if f else "zero"
            cell = {"population": population}
            reported = {
                "species_id": s["id"],
                "population": population,
                "status": "VALID"
                if valid
                else ("FAILED" if pred is not None else "NOT_EVALUATED"),
            }
            if valid:
                # Positive A cancels from the relative inequality but not physical error.
                delta = Fraction(float(output[j])) - f
                error = Fraction(s["A"]) * delta
                relative = abs(delta / f) if f else None
                meets = {
                    p["id"]: abs(delta)
                    <= Fraction(p["numerator"], p["denominator"]) * abs(f)
                    for p in PROFILES
                }
                cell.update(error=error, relative=relative, meets=meets)
                reported.update(
                    signed_physical_error=_metric(error),
                    absolute_physical_error=_metric(abs(error)),
                    relative_error=_metric(relative),
                    profiles=meets,
                )
            cells.append(cell)
            reported_cells.append(reported)
        rows.append({"sample": sample, "valid": valid, "cells": cells})
        records.append(
            {
                **{k: sample[k] for k in IDENTITY},
                "regime": sample.get(
                    "regime", {"label": "unknown", "provenance": "not supplied"}
                ),
                "status": "VALID"
                if valid
                else ("FAILED" if pred is not None else "NOT_EVALUATED"),
                "profiles": {
                    p["id"]: all(c["meets"][p["id"]] for c in cells) if valid else None
                    for p in PROFILES
                },
                "components": reported_cells,
            }
        )

    def summarize(subrows, indices):
        return {
            pop: _summary(subrows, pop, indices, prows is not None)
            for pop in ("all", "nonzero", "zero")
        }

    indices = list(range(len(ids)))
    report = {
        "schema": "crucible.native_fidelity_report.v1",
        "config_id": config["config_id"],
        "config_sha256": _digest(config),
        "dataset_id": reference["dataset_id"],
        "prediction_id": prediction.get("prediction_id") if prediction else None,
        "status": "NOT_EVALUATED"
        if prediction is None
        else (
            "FAILED_ATTEMPTS_PRESENT"
            if any(not row["valid"] for row in rows)
            else "EVALUATED_NATIVE_FIDELITY"
        ),
        "scientific_qualified": False,
        "integrated_scientific_accuracy": "NOT_EVALUATED",
        "physical_error_unit": "mass_fraction/s",
        "profiles": [dict(p) for p in PROFILES],
        "summary": summarize(rows, indices),
        "per_species": {sid: summarize(rows, [j]) for j, sid in enumerate(ids)},
        "strata": {},
        "records": records,
        "physics": physics_diagnostics(reference, prediction),
        "assembly_bounds": "SEPARATE_REFERENCE_DIAGNOSTICS_NOT_A_SCORING_ALLOWANCE",
        "heating": "EXCLUDED_NOT_EVALUATED",
    }
    for field in ("history_id", "group_id", "category", "regime"):
        buckets = {}
        for row in rows:
            label = (
                row["sample"].get("regime", {"label": "unknown"})["label"]
                if field == "regime"
                else row["sample"][field]
            )
            buckets.setdefault(label, []).append(row)
        report["strata"][field] = {
            label: summarize(subrows, indices) for label, subrows in buckets.items()
        }
    json.dumps(report, allow_nan=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--prediction", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            evaluate_native(
                json.loads(args.config.read_text()),
                json.loads(args.reference.read_text()),
                json.loads(args.prediction.read_text()) if args.prediction else None,
            ),
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
