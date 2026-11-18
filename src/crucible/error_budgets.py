"""Pointwise physical-abundance diagnostics; no fitting, integration or acceptance.

See docs/phase1/ERROR_BUDGETS.md for JSON contracts and scientific limitations.
Inputs are never clipped, normalized, projected, reordered or modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

UNITS = {"Y": "molar_abundance_Y", "F": "molar_abundance_Y/s", "time": "s"}
SAMPLE_SCHEMA = "crucible.rhs_samples.v1"
CONFIG_SCHEMA = "crucible.error_budgets.v1"
IDENTITY = ("sample_id", "history_id", "group_id", "category", "time_s")
REGIMES = {"burning", "near_equilibrium", "freeze_out", "unknown"}


def _finite(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError(
            f"{name} must be {'positive' if positive else 'nonnegative'} and finite"
        )
    return float(value)


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty identity/provenance string")
    return value


def _metadata(data):
    if data.get("schema") != SAMPLE_SCHEMA or data.get("units") != UNITS:
        raise ValueError("unsupported sample schema or units")
    _text(data.get("dataset_id"), "dataset_id")
    species = data.get("species")
    if not isinstance(species, list) or not species:
        raise ValueError("ordered species metadata is required")
    ids = []
    for s in species:
        ids.append(_text(s.get("id"), "species id"))
        a = _finite(s.get("A"), "A", positive=True)
        z = _finite(s.get("Z"), "Z")
        if a != int(a) or z != int(z) or z > a:
            raise ValueError("species require integer A,Z with 0 <= Z <= A")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate species identities")
    return species, ids


def _samples(data, width, *, reference):
    rows = data.get("samples")
    if not isinstance(rows, list) or not rows:
        raise ValueError("nonempty samples required; empty sets are not evaluations")
    identities = []
    for row in rows:
        for key in IDENTITY[:-1]:
            _text(row.get(key), key)
        _finite(row.get("time_s"), "time_s")
        identities.append(row["sample_id"])
        for key in ["Y", "F"] if reference else ["F"]:
            value = row.get(key)
            if not reference and row.get("success", True) is not True and value is None:
                continue
            if not isinstance(value, list) or len(value) != width:
                raise ValueError(f"{key} must have one entry per ordered species")
        regime = row.get("regime")
        if regime is not None:
            if not isinstance(regime, dict) or regime.get("label") not in REGIMES:
                raise ValueError("unsupported regime; use supplied label or unknown")
            _text(regime.get("provenance"), "regime provenance")
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate sample identities")
    return rows


def _vector(value):
    """Nonfinite/missing prediction components are failures, never zero targets."""
    try:
        result = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("array components must be numeric or null failures") from exc
    if any(
        x is not None and (isinstance(x, bool) or not isinstance(x, (int, float)))
        for x in value
    ):
        raise ValueError("array components must be numeric or null failures")
    return result


def _scale(spec, coeff, species, intervals, tau):
    if spec is None or spec.get("mode") is None:
        return None, {"status": "NOT_EVALUATED", "reason": "unresolved change scale"}
    mode = spec.get("mode")
    if mode == "explicit":
        if spec.get("value") is None or spec.get("provenance") is None:
            return None, {
                "status": "NOT_EVALUATED",
                "reason": "unresolved explicit scale/provenance",
            }
        value = _finite(spec.get("value"), "explicit scale")
        _text(spec.get("provenance"), "scale provenance")
        return value, dict(spec, status="SUPPLIED_BOUND")
    if mode != "sampled_max_excursion":
        raise ValueError("unsupported scale mode")
    if spec.get("interval_id") is None:
        return None, {
            "status": "NOT_EVALUATED",
            "reason": "unresolved reference interval identity",
        }
    if (
        spec.get("usage") != "fixed_calibration_interval"
        or spec.get("frozen_before_testing") is not True
    ):
        raise ValueError(
            "sampled scale requires an explicitly frozen fixed calibration interval"
        )
    _text(spec.get("calibration_provenance"), "scale calibration provenance")
    interval_id = _text(spec.get("interval_id"), "interval_id")
    interval = (intervals or {}).get(interval_id)
    if interval is None or interval.get("qualified") is not True:
        return None, {
            "status": "NOT_EVALUATED",
            "reason": "qualified reference interval unavailable",
            "interval_id": interval_id,
        }
    _metadata(interval)
    if interval["species"] != species:
        raise ValueError("interval species identity/order mismatch")
    _text(interval.get("qualification_provenance"), "interval qualification provenance")
    _text(interval.get("history_id"), "interval history_id")
    _text(interval.get("coverage_provenance"), "interval coverage provenance")
    if interval.get("interval_id") != interval_id:
        raise ValueError("interval identity mismatch")
    # Exact sampled endpoints, no interpolation, cadence inference or gap bridging.
    times = _vector(interval.get("times_s", []))
    coverage = interval.get("coverage_s")
    if (
        times.size < 2
        or not np.all(np.isfinite(times))
        or not np.all(np.diff(times) > 0)
        or not isinstance(coverage, list)
        or len(coverage) != 2
        or coverage != [float(times[0]), float(times[-1])]
    ):
        raise ValueError(
            "interval needs increasing finite samples and exact explicit coverage_s"
        )
    if tau is not None and float(times[-1] - times[0]) != tau:
        raise ValueError(
            "sampled reference interval duration must equal physical timescale_s"
        )
    if interval.get("semantics") != "discrete_samples_no_interpolation":
        raise ValueError("interval must explicitly declare discrete sample semantics")
    y = np.asarray(interval.get("Y"), dtype=float)
    if y.shape != (len(times), len(species)) or not np.all(np.isfinite(y)):
        raise ValueError("interval Y shape/nonfinite failure")
    with np.errstate(over="ignore", invalid="ignore"):
        q = y @ coeff
        value = float(np.max(np.abs(q - q[0])))
    if not math.isfinite(value):
        raise ValueError("reference excursion overflow")
    return value, {
        "status": "SAMPLED_MAXIMUM",
        "value": value,
        "interval_id": interval_id,
        "history_id": interval["history_id"],
        "dataset_id": interval["dataset_id"],
        "interval_sha256": hashlib.sha256(
            json.dumps(interval, sort_keys=True, allow_nan=False).encode()
        ).hexdigest(),
        "coverage_s": coverage,
        "sample_count": len(times),
        "coverage_provenance": interval["coverage_provenance"],
        "qualification_provenance": interval["qualification_provenance"],
        "continuous_maximum": False,
        "interpolation": "none",
        "usage": spec["usage"],
        "frozen_before_testing": True,
        "calibration_provenance": spec["calibration_provenance"],
    }


def _summary(records):
    attempted = len(records)
    valid = [r for r in records if r["status"] == "VALID"]
    evaluated = [r for r in valid if r["exceeds"] is not None]
    finite_norm = [
        r["normalized_error"] for r in evaluated if r["normalized_error"] is not None
    ]
    unbounded = sum(r["unbounded"] for r in evaluated)
    errors = [r["absolute_error"] for r in valid]
    failed = attempted - len(valid)
    exceeded = sum(r["exceeds"] for r in evaluated)

    # hypot avoids unnecessary overflow from squaring finite numbers.
    def rms(values):
        return (
            math.hypot(*(v / math.sqrt(len(values)) for v in values))
            if values
            else None
        )

    return {
        "attempted": attempted,
        "valid": len(valid),
        "failed": failed,
        "budget_evaluated": len(evaluated),
        "budget_not_evaluated": attempted - len(evaluated),
        "exceeded": exceeded,
        "unbounded_normalizations": unbounded,
        "normalized_rms": None if unbounded else rms(finite_norm),
        "max_normalized_error": None if unbounded else max(finite_norm, default=None),
        "normalization_status": "UNBOUNDED"
        if unbounded
        else ("FINITE" if finite_norm else "NOT_EVALUATED"),
        "physical_absolute_rms": rms(errors),
        "physical_absolute_max": max(errors, default=None),
        "fraction_exceeding_evaluated": exceeded / len(evaluated)
        if evaluated
        else None,
        "exceed_fraction_denominator": len(evaluated),
        "violations_or_failed_fraction_attempted": (exceeded + failed) / attempted
        if attempted
        else None,
    }


def _strata(samples, records):
    result = {}
    for key in ("history_id", "group_id", "category", "regime"):
        buckets = {}
        for sample, record in zip(samples, records, strict=True):
            label = (
                sample.get("regime", {"label": "unknown"})["label"]
                if key == "regime"
                else sample[key]
            )
            buckets.setdefault(label, []).append(record)
        result[key] = {label: _summary(rows) for label, rows in buckets.items()}
    return result


def _prediction_rows(reference, prediction, samples, width):
    if prediction is None:
        return None
    _metadata(prediction)
    if any(prediction[k] != reference[k] for k in ("dataset_id", "species", "units")):
        raise ValueError("prediction dataset/species identity/order/units mismatch")
    rows = _samples(prediction, width, reference=False)
    if len(rows) != len(samples) or any(
        tuple(p[k] for k in IDENTITY) != tuple(r[k] for k in IDENTITY)
        for p, r in zip(rows, samples, strict=True)
    ):
        raise ValueError(
            "prediction sample/history/group/category/time identity/order mismatch"
        )
    _text(prediction.get("prediction_id"), "prediction_id")
    return rows


def physics_diagnostics(reference, prediction=None):
    """Native closed full-inventory Q/B diagnostics, never constant-charge tests."""
    species, _ = _metadata(reference)
    rows = _samples(reference, len(species), reference=True)
    _prediction_rows(reference, prediction, rows, len(species))
    if reference.get("network_convention") != "closed_full_inventory_no_aux_Q_over_B":
        return {
            "status": "UNAVAILABLE",
            "reason": "unsupported open/external/auxiliary balance",
            "heating": "EXCLUDED_NOT_EVALUATED",
        }
    a = np.array([s["A"] for s in species], dtype=float)
    z = np.array([s["Z"] for s in species], dtype=float)
    result = {
        "status": "DIAGNOSTICS_ONLY",
        "heating": "EXCLUDED_NOT_EVALUATED",
        "samples": [],
    }
    for i, row in enumerate(rows):
        y = _vector(row["Y"])
        entry = {"sample_id": row["sample_id"]}
        if not np.all(np.isfinite(y)):
            entry.update(status="FAILED", reason="nonfinite reference state")
        else:
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                b, q = float(a @ y), float(z @ y)
            if not math.isfinite(b) or not math.isfinite(q) or b <= 0:
                entry.update(
                    status="FAILED", reason="nonpositive/nonfinite baryon moment"
                )
            else:
                entry.update(
                    status="DIAGNOSTICS_ONLY",
                    B=b,
                    Q=q,
                    Ye=q / b,
                    negative_state_species=[
                        s["id"] for s, v in zip(species, y, strict=True) if v < 0
                    ],
                )
                for name, frow in [
                    ("reference", row),
                    ("prediction", prediction["samples"][i] if prediction else None),
                ]:
                    if frow is None:
                        entry[name] = {"status": "NOT_EVALUATED"}
                        continue
                    if frow.get("success", True) is not True:
                        entry[name] = {"status": "FAILED"}
                        continue
                    f = _vector(frow["F"])
                    if frow.get("success", True) is not True or not np.all(
                        np.isfinite(f)
                    ):
                        entry[name] = {"status": "FAILED"}
                        continue
                    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                        bf, zf = float(a @ f), float(z @ f)
                        dye = (zf - (q / b) * bf) / b
                    if not all(math.isfinite(v) for v in (bf, zf, dye)):
                        entry[name] = {
                            "status": "FAILED",
                            "reason": "diagnostic arithmetic overflow",
                        }
                    else:
                        entry[name] = {
                            "status": "DIAGNOSTICS_ONLY",
                            "baryon_rate_residual": bf,
                            "charge_moment_rate": zf,
                            "dYe_dt": dye,
                            "boundary_incompatible_species": [
                                s["id"]
                                for s, yi, fi in zip(species, y, f, strict=True)
                                if yi == 0 and fi < 0
                            ],
                        }
        result["samples"].append(entry)
    return result


def evaluate(config, reference, prediction=None, *, intervals=None):
    """Evaluate supplied pointwise predictions under provisional sensitivity tiers.

    A qualified sampled interval is a caller-supplied evidence assertion, not
    qualification performed here. Never pass raw saved histories as rollout truth.
    """
    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError("unsupported budget schema")
    _text(config.get("config_id"), "config_id")
    species, ids = _metadata(reference)
    if config.get("species") != species:
        raise ValueError("config species identity/order mismatch")
    if config.get("abundance_space") not in {"Y", "X"}:
        raise ValueError("abundance_space must be Y or X")
    tiers = config.get("relative_tiers")
    if not isinstance(tiers, list) or not tiers or len(set(tiers)) != len(tiers):
        raise ValueError("distinct relative tiers required")
    tiers = [_finite(r, "relative tier") for r in tiers]
    critical = config.get("critical_species")
    if critical is not None:
        if (
            not isinstance(critical, list)
            or len(set(critical)) != len(critical)
            or set(critical) - set(ids)
        ):
            raise ValueError("critical selection must contain unique known species")
        _text(
            config.get("critical_selection_provenance"), "critical selection provenance"
        )
    samples = _samples(reference, len(species), reference=True)
    prows = _prediction_rows(reference, prediction, samples, len(species))
    factor = np.array(
        [s["A"] if config["abundance_space"] == "X" else 1 for s in species],
        dtype=float,
    )
    budgets = config.get("species_budgets", {})
    if not isinstance(budgets, dict) or set(budgets) - set(ids):
        raise ValueError("unknown species budget")
    quantities = [
        (sid, np.eye(len(ids))[i] * factor, budgets.get(sid), [sid])
        for i, sid in enumerate(ids)
    ]
    seen = set(ids)
    for group in config.get("groups", []):
        gid = _text(group.get("id"), "group id")
        weights = group.get("coefficients")
        if (
            gid in seen
            or not isinstance(weights, dict)
            or not weights
            or set(weights) - set(ids)
        ):
            raise ValueError("group identity/constituents invalid")
        seen.add(gid)
        values = []
        for sid in ids:
            v = weights.get(sid, 0)
            if (
                isinstance(v, bool)
                or not isinstance(v, (int, float))
                or not math.isfinite(v)
            ):
                raise ValueError("linear group coefficients must be finite")
            values.append(v)
        if not any(values):
            raise ValueError("group must have nonzero constituents")
        quantities.append(
            (
                gid,
                np.array(values) * factor,
                group.get("budget"),
                [sid for sid, v in zip(ids, values, strict=True) if v != 0],
            )
        )
    report = {
        "schema": "crucible.error_budget_report.v1",
        "config_id": config["config_id"],
        "config_sha256": hashlib.sha256(
            json.dumps(config, sort_keys=True, allow_nan=False).encode()
        ).hexdigest(),
        "reference_sample_count": len(samples),
        "prediction_attempt_count": len(prows) if prows else 0,
        "dataset_id": reference["dataset_id"],
        "prediction_id": prediction.get("prediction_id") if prediction else None,
        "scientific_qualified": False,
        "integrated_scientific_accuracy": "NOT_EVALUATED",
        "heating": "EXCLUDED_NOT_EVALUATED",
        "critical_selection": critical,
        "abundance_space": config["abundance_space"],
        "rate_unit": "mass_fraction/s"
        if config["abundance_space"] == "X"
        else UNITS["F"],
        "samples": [
            {k: s[k] for k in IDENTITY}
            | {
                "regime": s.get(
                    "regime", {"label": "unknown", "provenance": "not supplied"}
                )
            }
            for s in samples
        ],
        "pointwise_budget_status": "NOT_EVALUATED"
        if prediction is None
        else "INCOMPLETE",
        "quantities": {},
    }
    for qid, coeff, budget, members in quantities:
        gaps = []
        if budget is None:
            budget = {}
        a, tau = budget.get("absolute_change"), budget.get("timescale_s")
        if a is not None:
            a = _finite(a, "absolute abundance-change allowance")
        else:
            gaps.append("unresolved absolute abundance-change allowance")
        if tau is not None:
            tau = _finite(tau, "physical timescale_s", positive=True)
        else:
            gaps.append("unresolved physical timescale")
        scale, scale_info = _scale(budget.get("scale"), coeff, species, intervals, tau)
        if scale is None:
            gaps.append(scale_info["reason"])
        qresult = {
            "members": members,
            "critical": qid in (critical or []),
            "scale": scale_info,
            "unresolved": gaps,
            "tiers": {},
        }
        for r in tiers:
            limit = None
            if not gaps:
                limit = (a + r * scale) / tau
                if not math.isfinite(limit):
                    raise ValueError("budget arithmetic overflow")
            records = []
            if prows is not None:
                for sample, pred in zip(samples, prows, strict=True):
                    f = _vector(sample["F"])
                    p = (
                        _vector(pred["F"])
                        if pred.get("success", True) is True
                        else np.full(len(ids), np.nan)
                    )
                    record = {
                        "sample_id": sample["sample_id"],
                        "status": "FAILED",
                        "absolute_error": None,
                        "normalized_error": None,
                        "unbounded": False,
                        "exceeds": None,
                    }
                    if (
                        sample.get("success", True) is not True
                        or not np.all(np.isfinite(_vector(sample["Y"])))
                        or pred.get("success", True) is not True
                        or not np.all(np.isfinite(p))
                        or not np.all(np.isfinite(f))
                    ):
                        record["reason"] = (
                            "failed prediction/reference or nonfinite state/RHS"
                        )
                    else:
                        with np.errstate(over="ignore", invalid="ignore"):
                            error = abs(float(coeff @ p) - float(coeff @ f))
                        if not math.isfinite(error):
                            record["reason"] = "physical-error arithmetic overflow"
                        else:
                            record.update(status="VALID", absolute_error=error)
                            if limit is not None:
                                norm = (
                                    error / limit
                                    if limit
                                    else (0.0 if error == 0 else None)
                                )
                                unbounded = norm is None or not math.isfinite(norm)
                                record.update(
                                    normalized_error=None if unbounded else norm,
                                    unbounded=unbounded,
                                    exceeds=error > limit,
                                )
                    records.append(record)
            qresult["tiers"][str(r)] = {
                "rate_budget": limit,
                "status": "NOT_EVALUATED"
                if prows is None
                else ("INCOMPLETE" if gaps else "EVALUATED_PROVISIONAL"),
                "summary": _summary(records),
                "strata": _strata(samples, records) if prows else {},
                "records": records,
            }
        report["quantities"][qid] = qresult
    for qid, _, _, members in quantities:
        if qid not in ids:
            report["quantities"][qid]["constituent_budget_gaps"] = {
                sid: report["quantities"][sid]["unresolved"]
                for sid in members
                if report["quantities"][sid]["unresolved"]
            }
    if prows is not None:
        metrics = [
            t["summary"]
            for q in report["quantities"].values()
            for t in q["tiers"].values()
        ]
        incomplete = (
            critical is None
            or any(q["unresolved"] for q in report["quantities"].values())
            or any(s["failed"] for s in metrics)
        )
        report["pointwise_budget_status"] = (
            "INCOMPLETE"
            if incomplete
            else (
                "VIOLATIONS"
                if any(s["exceeded"] for s in metrics)
                else "NO_VIOLATIONS_PROVISIONAL"
            )
        )
    report["physics"] = physics_diagnostics(reference, prediction)
    # Catch any accidental nonportable report value at the public boundary.
    json.dumps(report, allow_nan=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--prediction", type=Path)
    parser.add_argument("--intervals", type=Path)
    args = parser.parse_args()

    def read(path):
        return json.loads(path.read_text()) if path else None

    print(
        json.dumps(
            evaluate(
                read(args.config),
                read(args.reference),
                read(args.prediction),
                intervals=read(args.intervals),
            ),
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
