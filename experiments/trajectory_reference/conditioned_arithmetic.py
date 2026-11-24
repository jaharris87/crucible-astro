"""Offline exact-binary diagnostics, conditional on exported native operands.

No producer, EOS, rate evaluator, solver or private-data loader is imported or
called. These diagnostics do not establish physical truth or trajectory accuracy.
The existing Phase 1 arithmetic supplies mapping validation and DAZ/FTZ bounds.
Exact quantities use numerator/denominator strings; rounded arrays are displays.
"""

import importlib.util
import math
from fractions import Fraction as Q
from numbers import Integral, Real
from pathlib import Path

import numpy as np

_SPEC = importlib.util.spec_from_file_location(
    "_crucible_rhs_arithmetic",
    Path(__file__).resolve().parents[1] / "rhs_reference/arithmetic.py",
)
_ARITHMETIC = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_ARITHMETIC)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _array(value, name, ndim, shape=None):
    _require(
        isinstance(value, np.ndarray) and value.dtype == np.float64,
        name + " must be a binary64 ndarray",
    )
    _require(
        value.ndim == ndim and (shape is None or value.shape == shape),
        name + " shape differs",
    )
    _require(np.all(np.isfinite(value)), name + " must be finite")
    return value.copy()


def _integer(value, name):
    _require(
        isinstance(value, Integral) and not isinstance(value, (bool, np.bool_)),
        name + " must be an integer",
    )
    return int(value)


def _masses(value):
    _require(
        isinstance(value, np.ndarray)
        and value.ndim == 1
        and value.dtype.kind in "ifu"
        and len(value) > 0,
        "A must be a nonempty real numeric vector",
    )
    _require(
        np.all(np.isfinite(value))
        and np.all(value > 0)
        and np.all(value == np.floor(value)),
        "A must contain positive nuclear integers",
    )
    return [Q(int(x)) for x in value]


def _scalar(value, name):
    _require(
        isinstance(value, Real) and not isinstance(value, (bool, np.bool_)),
        name + " must be a finite real scalar",
    )
    try:
        converted = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(name + " must be finite") from exc
    _require(math.isfinite(converted), name + " must be finite")
    return Q(converted)


def _float(value):
    try:
        return float(value)
    except OverflowError:
        return math.inf if value > 0 else -math.inf


def _rational(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _quantity(values, shape=None):
    """Exact flat fractions with an explicit shape and rounded numeric displays."""
    values = list(values)
    shape = (len(values),) if shape is None else tuple(shape)
    rounded = np.array([_float(v) for v in values], dtype=np.float64).reshape(shape)
    return {
        "exact": [_rational(v) for v in values],
        "shape": list(shape),
        "rounded": rounded,
        "rounded_finite": np.isfinite(rounded),
    }


def _ratio(numerator, denominator):
    if denominator == 0:
        if numerator == 0:
            return {
                "status": "ZERO_OVER_ZERO_DEFINED_AS_ZERO",
                "exact": _rational(Q(0)),
                "rounded": 0.0,
            }
        return {"status": "UNBOUNDED_NONZERO_OVER_ZERO", "exact": None, "rounded": None}
    quotient = numerator / denominator
    return {
        "status": "DEFINED",
        "exact": _rational(quotient),
        "rounded": _float(quotient),
    }


def _sum_envelope(operands, extra_additions=0):
    """Reuse product_bound, then a count-derived nearest/DAZ/FTZ sum envelope.

    One counted addition per term covers zero-initialized sums. Extra additions
    cover the three native additions joining four reaction-order sums.
    Unsupported finite-intermediate envelopes are labeled, never treated as a pass.
    """
    terms, errors = [], []
    for factors in operands:
        term, error = _ARITHMETIC.product_bound(factors)
        terms.append(term)
        errors.append(error)
    magnitude = sum((abs(t) + e for t, e in zip(terms, errors, strict=True)), Q(0))
    n = len(terms) + extra_additions
    summation = _ARITHMETIC.gamma(n) * magnitude + 4 * n * _ARITHMETIC.NORMAL / (
        1 - n * _ARITHMETIC.U
    )
    bound = sum(errors, Q(0)) + summation
    supported = magnitude + summation < _ARITHMETIC.MAXIMUM
    return terms, bound, supported


def _operation_counts(operands, extra_additions=0):
    sizes = [len(factors) for factors in operands]
    additions = len(sizes) + extra_additions
    return {
        "product_multiplications": sum(size - 1 for size in sizes),
        "product_operand_occurrences": sum(sizes),
        "product_flush_allowance_events": 4 * sum(sizes),
        "summation_additions": additions,
        "summation_flush_allowance_events": 4 * additions,
    }


def _groups(groups, masses):
    _require(
        isinstance(groups, (list, tuple)) and len(groups) > 0,
        "groups must be a nonempty native-order sequence",
    )
    checked, seen = [], []
    for group in groups:
        _require(
            isinstance(group, dict)
            and set(group) == {"order", "participants", "extended", "csect", "b"},
            "group fields differ",
        )
        order = _integer(group["order"], "reaction order")
        _require(order in (1, 2, 3, 4), "unsupported reaction order")
        seen.append(order)
        participants = group["participants"]
        if isinstance(participants, np.ndarray):
            _require(participants.ndim == 2, "participants must be a matrix")
        _require(
            isinstance(participants, (list, tuple, np.ndarray)),
            "participants must be a sequence",
        )
        width = 5 if order == 1 else 6
        rows = []
        for row in participants:
            if isinstance(row, np.ndarray):
                _require(row.ndim == 1, "participant row must be a vector")
            _require(
                isinstance(row, (list, tuple, np.ndarray)) and len(row) == width,
                "participant width differs",
            )
            rows.append(tuple(_integer(x, "participant") for x in row))
        csect = _array(group["csect"], "csect", 1, (len(rows),))
        _require(
            isinstance(group["extended"], (list, tuple)), "extended must be a sequence"
        )
        extended = []
        for entry in group["extended"]:
            _require(
                isinstance(entry, (list, tuple)) and len(entry) == 3,
                "extended entry differs",
            )
            target, mu, factor = entry
            target, mu = _integer(target, "target"), _integer(mu, "mu")
            factor = float(_scalar(factor, "a"))
            extended.append((target, mu, factor))
        b = _array(group["b"], "b", 1, (len(extended),))
        checked.append(
            {
                "order": order,
                "participants": rows,
                "extended": extended,
                "csect": csect,
                "b": b,
            }
        )
    _require(seen == sorted(set(seen)), "reaction orders must be unique and increasing")
    # This exact existing validator checks multiplicities, symmetry and baryons.
    _ARITHMETIC.mapping_terms(checked, masses)
    return checked


def coefficient_conditioned(groups, A, Y, F):
    """Compare native b with a*csect, then F with the fixed-b abundance polynomial.

    Each group has native-order participant rows (one-based species, product zero
    padding), extended (target one-based, reaction mu zero-based, a binary64)
    entries, csect per reaction and b per extended entry. A follows species order.
    All exports are ordinary finite arrays; Y remains unchanged in [0,1].

    F differences combine abundance multiplications and summation: no empirical
    separation is possible without the producer's actual rounded term ledger.
    The analytic derivative holds exported b fixed, excluding all coefficient/
    EOS/rate dependence on composition. Neither comparison tests those physics.
    """
    masses = _masses(A)
    n = len(masses)
    y = _array(Y, "Y", 1, (n,))
    fresh = _array(F, "F", 1, (n,))
    _require(np.all((y >= 0) & (y <= 1)), "Y outside [0,1]")
    groups = _groups(groups, masses)
    yy, ff = [Q(float(v)) for v in y], [Q(float(v)) for v in fresh]
    products, coefficient_differences, coefficient_bounds, coefficient_supported = (
        [],
        [],
        [],
        [],
    )
    combinatorial_differences, term_values, entries = [], [], []
    species_indices = [[] for _ in masses]
    operands = [[] for _ in masses]
    jacobian = [[Q(0) for _ in masses] for _ in masses]
    jacobian_operands = [[[] for _ in masses] for _ in masses]
    reaction_base = 0
    for gi, group in enumerate(groups):
        # Retrieve validated rational combinatorial factors in native species order.
        mapped = _ARITHMETIC.mapping_terms([group], masses)
        rational_factors = [iter(row) for row in mapped]
        for ei, (target, mu, factor) in enumerate(group["extended"]):
            species = target - 1
            _, reactants, _, combinatorial = next(rational_factors[species])
            b, csect = Q(float(group["b"][ei])), Q(float(group["csect"][mu]))
            product, bound = _ARITHMETIC.product_bound([Q(factor), csect])
            products.append(product)
            coefficient_differences.append(b - product)
            coefficient_bounds.append(bound)
            coefficient_supported.append(abs(product) + bound < _ARITHMETIC.MAXIMUM)
            combinatorial_differences.append(Q(factor) - combinatorial)
            factors = [b, *(yy[i - 1] for i in reactants)]
            term = math.prod(factors)
            index = len(entries)
            entries.append(
                {
                    "group": gi,
                    "order": group["order"],
                    "extended_index": ei,
                    "reaction_index": reaction_base + mu,
                    "target": target,
                    "reactants": list(reactants),
                }
            )
            species_indices[species].append(index)
            operands[species].append(factors)
            term_values.append(term)
            for position, reactant in enumerate(reactants):
                # Remove one factor, not divide by Y: repeated/zero reactants work.
                derivative_factors = [
                    b,
                    *(yy[i - 1] for j, i in enumerate(reactants) if j != position),
                ]
                jacobian[species][reactant - 1] += math.prod(derivative_factors)
                jacobian_operands[species][reactant - 1].append(derivative_factors)
        reaction_base += len(group["participants"])
    exact, bounds, supported, positive, negative, absolute, cancellation, rankings = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for i in range(n):
        terms, bound, valid = _sum_envelope(operands[i], extra_additions=3)
        total = sum(terms, Q(0))
        pos = sum((v for v in terms if v > 0), Q(0))
        neg = sum((v for v in terms if v < 0), Q(0))
        abs_total = pos - neg
        exact.append(total)
        bounds.append(bound)
        supported.append(valid)
        positive.append(pos)
        negative.append(neg)
        absolute.append(abs_total)
        if total == 0:
            cancellation.append(
                {
                    "status": "UNDEFINED_NO_NONZERO_TERMS"
                    if abs_total == 0
                    else "UNBOUNDED_EXACT_CANCELLATION",
                    "exact": None,
                    "rounded": None,
                }
            )
        else:
            cancellation.append(_ratio(abs_total, abs(total)))
        rankings.append(sorted(species_indices[i], key=lambda j: -abs(term_values[j])))
    differences = [
        actual - expected for actual, expected in zip(ff, exact, strict=True)
    ]
    jacobian_bounds, jacobian_supported = [], []
    for row in jacobian_operands:
        for contributions in row:
            _, bound, valid = _sum_envelope(contributions)
            jacobian_bounds.append(bound)
            jacobian_supported.append(valid)
    baryon_exact = sum((m * v for m, v in zip(masses, exact, strict=True)), Q(0))
    baryon_native = sum((m * v for m, v in zip(masses, ff, strict=True)), Q(0))
    return {
        "scope": "binary64 coefficient-conditioned arithmetic; not EOS/rate or physical truth",
        "assembly_difference_scope": "combined abundance-product and summation discrepancy; no rounded native term ledger",
        "scientific_accuracy_acceptance": False,
        "b_formation": {
            "exact_a_csect": _quantity(products),
            "native_b_minus_exact": _quantity(coefficient_differences),
            "native_a_minus_combinatorial": _quantity(combinatorial_differences),
            "roundoff_bound": _quantity(coefficient_bounds),
            "product_multiplications_per_entry": 1,
            "product_flush_allowance_events_per_entry": 8,
            "bound_supported": np.array(coefficient_supported, dtype=bool),
            "within_roundoff_envelope": np.array(
                [
                    ok and abs(d) <= b
                    for ok, d, b in zip(
                        coefficient_supported,
                        coefficient_differences,
                        coefficient_bounds,
                        strict=True,
                    )
                ],
                dtype=bool,
            ),
        },
        "assembly": {
            "exact_fixed_b_F": _quantity(exact),
            "native_F_minus_exact": _quantity(differences),
            "roundoff_bound": _quantity(bounds),
            "operation_counts": [
                _operation_counts(row, extra_additions=3) for row in operands
            ],
            "bound_supported": np.array(supported, dtype=bool),
            "within_roundoff_envelope": np.array(
                [
                    ok and abs(d) <= b
                    for ok, d, b in zip(supported, differences, bounds, strict=True)
                ],
                dtype=bool,
            ),
            "positive_term_total": _quantity(positive),
            "negative_term_total": _quantity(negative),
            "absolute_term_total": _quantity(absolute),
            "cancellation_ratio_absolute_over_net": cancellation,
            "dominant_term_indices": rankings,
        },
        "terms": {"entries": entries, "exact_fixed_b_values": _quantity(term_values)},
        "fixed_b_jacobian": _quantity((v for row in jacobian for v in row), (n, n)),
        "fixed_b_jacobian_arithmetic": {
            "roundoff_bound": _quantity(jacobian_bounds, (n, n)),
            "bound_supported": np.array(jacobian_supported, dtype=bool).reshape(n, n),
            "operation_counts": [
                [_operation_counts(contributions) for contributions in row]
                for row in jacobian_operands
            ],
            "scope": "native fixed-b monomial derivative only; each repeated reactant contributes separately; no coefficient derivatives",
        },
        "baryon": {
            "exact_fixed_b_rate": _rational(baryon_exact),
            "native_rate": _rational(baryon_native),
            "native_minus_fixed_b": _rational(baryon_native - baryon_exact),
        },
        "bound_assumptions": "nearest rounding, optional DAZ/FTZ; finite intermediate envelope required; not an empirical error decomposition",
    }


def _residual_report(exact, operands, reported, masses):
    bounds, supported = [], []
    for row in operands:
        _, bound, valid = _sum_envelope(row)
        bounds.append(bound)
        supported.append(valid)
    output = {
        "exact": _quantity(exact),
        "roundoff_bound": _quantity(bounds),
        "bound_supported": np.array(supported, dtype=bool),
        "operation_counts": [_operation_counts(row) for row in operands],
        "bound_assumptions": "nearest rounding with optional DAZ/FTZ; unsupported finite-intermediate envelopes are flagged",
        "mass_weighted_exact": _quantity(
            m * r for m, r in zip(masses, exact, strict=True)
        ),
        "mass_weighted_l1": _rational(
            sum((abs(m * r) for m, r in zip(masses, exact, strict=True)), Q(0))
        ),
    }
    if reported is not None:
        measured = [Q(float(v)) for v in reported]
        differences = [v - e for v, e in zip(measured, exact, strict=True)]
        output.update(
            reported=reported.copy(),
            reported_minus_exact=_quantity(differences),
            within_roundoff_envelope=np.array(
                [
                    ok and abs(d) <= b
                    for ok, d, b in zip(supported, differences, bounds, strict=True)
                ],
                dtype=bool,
            ),
        )
    return output


def exact_be_residual(Yold, Y, F, h, A, reported=None, *, atol=1e-13, rtol=1e-11):
    """Exact Y-Yold-h*F from retained binary64 operands, not an exact physical F.

    reported, when available, is the actual retained native residual. The separate
    NumPy subtraction/product display is explicitly an offline evaluation, not a
    reconstruction of native operation ordering, contraction, or its term ledger.
    D-036 mass weights and standard/tight nonlinear scales are reported unchanged;
    no threshold-based acceptance is returned.
    """
    masses = _masses(A)
    n = len(masses)
    old, new, f = (
        _array(v, k, 1, (n,)) for v, k in ((Yold, "Yold"), (Y, "Y"), (F, "F"))
    )
    step = _scalar(h, "h")
    _require(step > 0, "h must be positive")
    an, rn = _scalar(atol, "atol"), _scalar(rtol, "rtol")
    _require(
        (float(an), float(rn)) in ((1e-13, 1e-11), (1e-14, 1e-12)),
        "non-protocol nonlinear controls",
    )
    reported = None if reported is None else _array(reported, "reported", 1, (n,))
    oo, yy, ff = ([Q(float(v)) for v in array] for array in (old, new, f))
    operands = [
        [[y], [-o], [-step, rate]] for o, y, rate in zip(oo, yy, ff, strict=True)
    ]
    exact = [y - o - step * rate for o, y, rate in zip(oo, yy, ff, strict=True)]
    result = _residual_report(exact, operands, reported, masses)
    scales = [
        an + rn * max(abs(m * o), abs(m * y))
        for m, o, y in zip(masses, oo, yy, strict=True)
    ]
    normalized = [
        abs(m * r) / scale for m, r, scale in zip(masses, exact, scales, strict=True)
    ]
    with np.errstate(over="ignore", invalid="ignore"):
        offline = new - old - float(step) * f
    offline_difference = [
        Q(float(v)) - r if np.isfinite(v) else None
        for v, r in zip(offline, exact, strict=True)
    ]
    result.update(
        scope="exact BE algebra conditional on retained binary64 Yold,Y,F,h; not a new RHS evaluation",
        scientific_accuracy_acceptance=False,
        nonlinear_scale=_quantity(scales),
        normalized_absolute_residual=_quantity(normalized),
        normalized_linf=_rational(max(normalized)),
        offline_separate_operations=offline,
        offline_minus_exact=[
            None if v is None else _rational(v) for v in offline_difference
        ],
        offline_finite=np.isfinite(offline),
    )
    return result


def linear_residual(M, rhs, delta, A, reported=None):
    """Exact M*delta-rhs and componentwise/normwise backward errors.

    Mass scaling is D M D^-1, D delta, D rhs with D=diag(A). Componentwise
    denominators are |M| |delta| + |rhs| (equivalently after D scaling).
    Normwise infinity denominator is ||D M D^-1||inf ||D delta||inf + ||D rhs||inf.
    Explicit zero/zero convention is zero; nonzero/zero is labeled unbounded.
    A supplied retained residual uses the same sign, M*delta-rhs. Its errors and
    backward errors are kept separate from the exact equation's residual.
    """
    masses = _masses(A)
    n = len(masses)
    matrix = _array(M, "M", 2, (n, n))
    rhs, delta = _array(rhs, "rhs", 1, (n,)), _array(delta, "delta", 1, (n,))
    reported = None if reported is None else _array(reported, "reported", 1, (n,))
    mm = [[Q(float(v)) for v in row] for row in matrix]
    rr, dd = [Q(float(v)) for v in rhs], [Q(float(v)) for v in delta]
    products = [[m * d for m, d in zip(row, dd, strict=True)] for row in mm]
    exact = [sum(row, Q(0)) - b for row, b in zip(products, rr, strict=True)]
    operands = [
        [[m, d] for m, d in zip(row, dd, strict=True)] + [[-b]]
        for row, b in zip(mm, rr, strict=True)
    ]
    result = _residual_report(exact, operands, reported, masses)
    denominator = [
        sum((abs(v) for v in row), Q(0)) + abs(b)
        for row, b in zip(products, rr, strict=True)
    ]
    scaled_matrix_norm = max(
        sum((abs(masses[i] * v / masses[j]) for j, v in enumerate(row)), Q(0))
        for i, row in enumerate(mm)
    )
    scaled_delta_norm = max(abs(m * d) for m, d in zip(masses, dd, strict=True))
    scaled_rhs_norm = max(abs(m * r) for m, r in zip(masses, rr, strict=True))
    norm_denominator = scaled_matrix_norm * scaled_delta_norm + scaled_rhs_norm
    weighted_exact_norm = max(abs(m * r) for m, r in zip(masses, exact, strict=True))
    result.update(
        scope="exact linear algebra conditional on retained binary64 M,rhs,delta; not physical or trajectory acceptance",
        scientific_accuracy_acceptance=False,
        componentwise_denominator=_quantity(denominator),
        componentwise_backward_error=[
            _ratio(abs(r), d) for r, d in zip(exact, denominator, strict=True)
        ],
        mass_scaled_matrix_linf=_rational(scaled_matrix_norm),
        mass_scaled_delta_linf=_rational(scaled_delta_norm),
        mass_scaled_rhs_linf=_rational(scaled_rhs_norm),
        normwise_denominator=_rational(norm_denominator),
        mass_scaled_residual_linf=_rational(weighted_exact_norm),
        normwise_backward_error=_ratio(weighted_exact_norm, norm_denominator),
    )
    if reported is not None:
        values = [Q(float(v)) for v in reported]
        reported_norm = max(abs(m * v) for m, v in zip(masses, values, strict=True))
        result.update(
            reported_componentwise_backward_error=[
                _ratio(abs(v), d) for v, d in zip(values, denominator, strict=True)
            ],
            reported_normwise_backward_error=_ratio(reported_norm, norm_denominator),
        )
    return result
