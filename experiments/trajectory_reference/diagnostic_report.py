"""Offline verification of the fixed proposed D-038 diagnostic population.

This module reads retained bytes and does NumPy/exact arithmetic only. It never
loads a producer, invokes an executable, evaluates a physical source, or grants
trajectory/reference acceptance. A failed derivative study remains an outcome.
"""

import argparse
import importlib.util
import io
import json
import re
import struct
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from crucible import trajectory_metrics as metrics
from crucible import trajectory_reference as common

HERE = Path(__file__).resolve().parent
STATES = ("development-initial", "validation-initial", "development-newton300")
COMMANDS = ("repeat-3", "repeat-1", "diagnose")
FACTORS = np.array([0.1, 1.0, 10.0, 100.0])
NC, NB = (683, 1345, 16, 4), (1862, 4860, 53, 19)
N, BRANCHES, MAX_RHS = 160, 10240, 104209
COUNTERS = (
    "rhs",
    "coefficient",
    "eos",
    "screening",
    "weak",
    "jacobian",
    "lu",
    "linear_solve",
    "newton",
    "retry",
    "step_attempt",
    "projection",
    "probe",
    "accepted",
)
EPS, TINY = np.finfo(np.float64).eps, np.finfo(np.float64).tiny


def require(condition, message):
    if not condition:
        raise ValueError("diagnostic report: " + message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


campaign_contract = load_module(
    "_diagnostic_report_campaign", HERE / "diagnostic_campaign.py"
)
ANNEX_SHA256, PROTOCOL_SHA256 = (
    campaign_contract.ANNEX_SHA256,
    campaign_contract.PROTOCOL_SHA256,
)

arithmetic = load_module(
    "_diagnostic_conditioned_arithmetic", HERE / "conditioned_arithmetic.py"
)
# reference.py imports only its small arithmetic dependency; no producer import.
_prior = sys.modules.get("arithmetic")
sys.modules["arithmetic"] = load_module(
    "arithmetic", HERE.parent / "rhs_reference/arithmetic.py"
)
try:
    reference = load_module(
        "_diagnostic_legacy_reference", HERE.parent / "rhs_reference/reference.py"
    )
finally:
    if _prior is None:
        del sys.modules["arithmetic"]
    else:
        sys.modules["arithmetic"] = _prior


def safe(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe artifact path")
    return root / path


def bits_equal(left, right):
    left, right = np.asarray(left), np.asarray(right)
    return (
        left.dtype == right.dtype
        and left.shape == right.shape
        and left.tobytes() == right.tobytes()
    )


def rows(data, width, *, dtype="<f8", finite=True, empty=False):
    item = np.dtype(dtype).itemsize
    require(
        len(data) % (item * width) == 0 and (empty or len(data) > 0),
        "stream extent differs",
    )
    result = np.frombuffer(data, dtype=dtype).reshape(-1, width).copy()
    require(not finite or np.all(np.isfinite(result)), "nonfinite stream")
    return result


def integer(value, lower=0, upper=None):
    require(
        np.isfinite(value)
        and value == int(value)
        and value >= lower
        and (upper is None or value <= upper),
        "noninteger/out-of-range identifier",
    )
    return int(value)


def parse_baseline(data):
    require(len(data) >= 48, "truncated baseline header")
    header = struct.unpack_from("<12i", data)
    require(header == (0x43524442, 1, N, *NC, *NB, BRANCHES), "baseline header differs")
    count = 10 + 2 * N + sum(NC) + sum(NB)
    require(len(data) == 48 + 8 * count + 4 * BRANCHES, "baseline extent differs")
    values = rows(data[48 : 48 + 8 * count], count)[0]
    call = integer(values[0], 1)
    cursor, csect, b = 10 + 2 * N, [], []
    for counts, target in ((NC, csect), (NB, b)):
        for count in counts:
            target.append(values[cursor : cursor + count].copy())
            cursor += count
    return {
        "call_id": call,
        "conditions": values[1:4],
        "moments_eos": values[4:10],
        "Y": values[10 : 10 + N],
        "F": values[10 + N : 10 + 2 * N],
        "csect": csect,
        "b": b,
        "branches": np.frombuffer(data[48 + 8 * cursor :], dtype="<i4").copy(),
        "comparison_bytes": np.frombuffer(data[:48] + data[56:], dtype=np.uint8).copy(),
    }


def evaluation_index(evaluations):
    require(
        isinstance(evaluations, np.ndarray)
        and evaluations.ndim == 2
        and evaluations.shape[1] >= 6,
        "evaluation dimensions differ",
    )
    n = (evaluations.shape[1] - 4) // 2
    require(
        evaluations.ndim == 2
        and evaluations.shape[1] == 4 + 2 * n
        and n > 0
        and np.all(np.isfinite(evaluations)),
        "evaluation dimensions/finiteness differ",
    )
    require(
        np.array_equal(evaluations[:, 0], np.arange(1, len(evaluations) + 1)),
        "evaluation IDs/order differ",
    )
    return {int(row[0]): row for row in evaluations}


def echo_evaluation(evaluation, conditions, Y, F=None):
    n = len(Y)
    require(
        bits_equal(evaluation[1:4], conditions)
        and bits_equal(evaluation[4 : 4 + n], Y),
        "physical evaluation is not bound to its input state/conditions",
    )
    if F is not None:
        require(
            bits_equal(evaluation[4 + n :], F), "physical evaluation F binding differs"
        )


def arithmetic_comparison(actual, expected, magnitude, flush_amplification=1):
    """Declared allowance for independent binary64 association only, not fidelity."""
    with np.errstate(over="ignore", invalid="ignore"):
        allowance = 512 * EPS * np.asarray(magnitude) + 32 * TINY * flush_amplification
        difference = np.asarray(actual) - np.asarray(expected)
    require(
        np.all(np.isfinite(expected))
        and np.all(np.isfinite(actual))
        and np.all(np.isfinite(allowance)),
        "unsupported/nonfinite recomputation",
    )
    require(
        np.all(np.abs(difference) <= allowance),
        "retained arithmetic recomputation differs",
    )
    return {"difference": difference, "allowance": allowance}


def compare_bound(actual, expected, allowance):
    require(
        np.all(np.isfinite(actual))
        and np.all(np.isfinite(expected))
        and np.all(np.isfinite(allowance)),
        "nonfinite comparison envelope",
    )
    difference = np.asarray(actual) - expected
    require(
        np.all(np.abs(difference) <= allowance),
        "retained arithmetic recomputation differs",
    )
    return {"difference": difference, "allowance": allowance}


def difference_quotient(F0, F1, F2, d1, d2):
    """Independent difference form with a DAZ/FTZ-amplification envelope.

    Normal finite offsets, their difference, denominator products and weights
    permit relative-error treatment of weight arithmetic. 512 epsilon covers
    these operations and the two abundance-free F differences/products/sum;
    32 NORMAL per weighted subtraction/product path and final addition covers
    DAZ/FTZ losses. This is serialization arithmetic, not a rate-error floor.
    """
    with np.errstate(over="ignore", invalid="ignore", divide="ignore", under="ignore"):
        difference = d1 - d2
        product1, product2 = d1 * difference, d2 * (d2 - d1)
        denominators = np.array([d1, d2, difference, product1, product2])
        require(
            np.all(np.isfinite(denominators)) and np.all(abs(denominators) >= TINY),
            "unsupported nonnormal difference-weight arithmetic",
        )
        w1, w2 = -d2 / product1, -d1 / product2
        intermediates = np.array([d1, d2, difference, product1, product2, w1, w2])
        require(
            np.all(np.isfinite(intermediates)) and np.all(abs(intermediates) >= TINY),
            "unsupported nonnormal difference-weight arithmetic",
        )
        term1, term2 = w1 * (F1 - F0), w2 * (F2 - F0)
        expected = term1 + term2
        allowance = 512 * EPS * (abs(term1) + abs(term2)) + 32 * TINY * (
            abs(w1) + abs(w2) + 1
        )
    require(
        np.all(np.isfinite(expected)) and np.all(np.isfinite(allowance)),
        "nonfinite difference quotient/envelope",
    )
    return {"value": expected, "allowance": allowance, "weights": np.array([w1, w2])}


def verify_fd(
    matrices, status, selected, attempts, bases, evaluations, A, branch_hashes=None
):
    """Bind all four matrices and every selected column to actual retained F IDs."""
    n = len(A)
    require(
        matrices.shape == (4, n, n)
        and status.shape == (4, 5)
        and bases.shape == (4, 4 + n),
        "Jacobian shapes differ",
    )
    require(
        np.array_equal(status[:, 0], FACTORS)
        and np.array_equal(status[:, 1], np.arange(1, 5))
        and np.array_equal(bases[:, 0], np.arange(1, 5))
        and np.isin(status[:, 2], [0.0, 1.0]).all(),
        "Jacobian factors/order differ",
    )
    lookup = evaluation_index(evaluations)
    require(
        selected.shape[1] == 6
        and attempts.shape[1] == 12
        and np.isin(selected[:, 1], np.arange(1, n + 1)).all(),
        "column/probe dimensions differ",
    )
    used, comparisons = {1}, []
    for k, matrix in enumerate(matrices):
        jid, before, after = k + 1, integer(status[k, 3], 1), integer(status[k, 4], 1)
        require(
            before == (1 if k == 0 else status[k - 1, 4]) and after > before + 1,
            "Jacobian physical-call interval differs",
        )
        require(before + 1 in lookup and after in lookup, "missing baseline/restore F")
        base_row, restore = lookup[before + 1], lookup[after]
        condition, base = bases[k, 1:4], bases[k, 4:]
        require(bits_equal(bases[k, 1:], bases[0, 1:]), "Jacobian baseline changed")
        echo_evaluation(lookup[1], condition, base, base_row[4 + n :])
        echo_evaluation(base_row, condition, base)
        echo_evaluation(restore, condition, base, base_row[4 + n :])
        used.update((before + 1, after))
        physical_cursor = before + 2
        own = attempts[attempts[:, 0] == jid]
        require(
            len(own) > 0 and np.all(np.isin(own[:, 1], np.arange(1, n + 1))),
            "missing/unknown probe columns",
        )
        chosen = selected[selected[:, 0] == jid]
        require(
            len(chosen) <= n and len(set(chosen[:, 1])) == len(chosen),
            "duplicate selected columns",
        )
        column_checks = []
        for col in range(1, n + 1):
            probes = own[own[:, 1] == col]
            require(
                0 < len(probes) <= 27
                and np.isin(probes[:, 2], [0.0, 1.0, -1.0]).all()
                and np.isin(probes[:, 8:10], [0.0, 1.0]).all(),
                "probe population/flags differ",
            )
            nominal = (
                EPS ** (1 / 3) * max(abs(base[col - 1]), 1e-8 / A[col - 1]) * FACTORS[k]
            )
            if base[col - 1] + nominal == base[col - 1]:
                nominal = np.nextafter(base[col - 1], np.inf) - base[col - 1]
            observed_order = []
            for probe in probes:
                require(probe[3] > 0, "nonpositive nominal probe increment")
                halvings = np.log2(nominal / probe[3])
                require(0 <= round(halvings) <= 8, "undeclared increment halving")
                observed_order.append((round(halvings), int(probe[2])))
                expected_delta = nominal / 2 ** round(halvings)
                arithmetic_comparison(
                    np.array(probe[3]), np.array(expected_delta), abs(expected_delta)
                )
                delta = probe[3]
                pair = (
                    (-delta, delta)
                    if probe[2] == 0
                    else ((delta, 2 * delta) if probe[2] == 1 else (-delta, -2 * delta))
                )
                require(
                    bits_equal(probe[6:8], np.array([base[col - 1] + v for v in pair])),
                    "probe state does not match declared stencil",
                )
                for side in range(2):
                    call = integer(probe[10 + side], 0)
                    require(
                        not probe[8 + side] or call > 0,
                        "admissible probe missing physical F",
                    )
                    if call:
                        require(
                            before + 1 < call < after
                            and call in lookup
                            and call not in used
                            and call == physical_cursor,
                            "probe F ID reused/outside matrix",
                        )
                        actual = base.copy()
                        actual[col - 1] = probe[6 + side]
                        require(
                            actual[col - 1] - base[col - 1] == probe[4 + side],
                            "probe representable offset differs",
                        )
                        echo_evaluation(lookup[call], condition, actual)
                        if branch_hashes is not None:
                            require(
                                bool(probe[8 + side])
                                == (branch_hashes[call] == branch_hashes[before + 1]),
                                "probe branch-admissibility flag differs",
                            )
                        used.add(call)
                        physical_cursor += 1
            expected_order = []
            for halving in range(9):
                delta = nominal / 2**halving
                expected_order.extend(
                    (halving, stencil)
                    for stencil in (0, 1, -1)
                    if stencil != -1 or base[col - 1] + 2 * delta > 1.0
                )
            require(
                observed_order == expected_order[: len(observed_order)],
                "probe stencil preference/order differs",
            )
            select = chosen[chosen[:, 1] == col]
            finite = np.all(np.isfinite(matrix[:, col - 1]))
            require(
                finite or np.all(np.isnan(matrix[:, col - 1])),
                "partially nonfinite Jacobian column",
            )
            require(
                bool(len(select)) == finite,
                "matrix/selected-column completeness differs",
            )
            if not finite:
                require(
                    observed_order == expected_order
                    and len(np.unique(probes[:, 3])) == 9,
                    "incomplete column did not retain all nine increments",
                )
                column_checks.append({"complete": False})
                continue
            s = select[0]
            require(
                integer(s[3], 0, 8) == round(np.log2(nominal / probes[-1, 3])),
                "selected halving count differs",
            )
            matches = probes[
                (probes[:, 2] == s[2])
                & (probes[:, 4] == s[4])
                & (probes[:, 5] == s[5])
                & (probes[:, 8] == 1)
                & (probes[:, 9] == 1)
            ]
            require(
                len(matches) == 1 and np.array_equal(matches[0], probes[-1]),
                "selected probe not last unique admissible attempt",
            )
            p = matches[0]
            quotient = difference_quotient(
                base_row[4 + n :],
                lookup[int(p[10])][4 + n :],
                lookup[int(p[11])][4 + n :],
                s[4],
                s[5],
            )
            column_checks.append(
                {
                    "complete": True,
                    "recomputed": quotient["value"],
                    **compare_bound(
                        matrix[:, col - 1], quotient["value"], quotient["allowance"]
                    ),
                }
            )
        require(
            physical_cursor == after, "Jacobian restore does not follow all probe calls"
        )
        require(
            bool(status[k, 2]) == np.all(np.isfinite(matrix)),
            "matrix completeness flag differs",
        )
        comparisons.append(column_checks)
    require(
        np.all(np.isin(attempts[:, 0], [1, 2, 3, 4]))
        and np.all(np.isin(selected[:, 0], [1, 2, 3, 4])),
        "unknown Jacobian IDs",
    )
    require(
        used == set(range(1, int(status[-1, 4]) + 1)),
        "unaccounted physical calls in matrix work",
    )
    return {
        "column_recomputation": comparisons,
        "complete": status[:, 2].astype(bool),
        "next_call": int(status[-1, 4]) + 1,
    }


def verify_directions(
    matrices,
    sweep,
    attempts,
    saved_jv,
    base,
    A,
    coordinate,
    evaluations,
    next_call,
    branch_hashes=None,
):
    n = len(A)
    require(
        sweep.shape == (3, 9, 6 + 8 * n)
        and attempts.shape[1] == 7 + 2 * n
        and saved_jv.shape == (n, 3, 4),
        "direction dimensions differ",
    )
    require(
        np.isin(attempts[:, 0], [1, 2, 3]).all()
        and np.isin(attempts[:, 1], np.arange(1, 10)).all(),
        "undeclared direction sample",
    )
    lookup = evaluation_index(evaluations)
    scale = np.maximum(abs(base["Y"]), 1e-8 / A)
    directions = np.array([scale, scale.copy(), np.zeros(n)])
    require(np.all((scale >= TINY) & (scale <= 1)), "unsupported direction scaling")
    directions[1, 1::2] = 0.0
    directions[2, coordinate] = scale[coordinate]
    cursor, recomputed, all_checks = next_call, np.full((3, 9, n), np.nan), []
    for direction in range(3):
        for mi, multiplier in enumerate(metrics.JACOBIAN_MULTIPLIERS):
            row = sweep[direction, mi]
            require(
                row[0] == direction + 1 and row[1] == mi + 1 and row[3] in (0.0, 1.0),
                "direction sweep order/flags differ",
            )
            arithmetic_comparison(
                row[6 : 6 + n], directions[direction], abs(directions[direction])
            )
            own = attempts[
                (attempts[:, 0] == direction + 1) & (attempts[:, 1] == mi + 1)
            ]
            require(
                1 <= len(own) <= 3
                and np.array_equal(own[:, 2], np.array([0.0, 1.0, -1.0])[: len(own)])
                and np.isin(own[:, 5:7], [0.0, 1.0]).all(),
                "direction attempt order/flags differ",
            )
            last_F = [None, None]
            for attempt in own:
                stencil = attempt[2]
                expected_h = (
                    (-multiplier, multiplier)
                    if stencil == 0
                    else (
                        (multiplier, 2 * multiplier)
                        if stencil == 1
                        else (-multiplier, -2 * multiplier)
                    )
                )
                require(
                    bits_equal(attempt[3:5], np.array(expected_h)),
                    "direction multipliers differ",
                )
                for side in range(2):
                    state = attempt[7 + side * n : 7 + (side + 1) * n]
                    arithmetic_comparison(
                        state,
                        base["Y"] + attempt[3 + side] * directions[direction],
                        abs(base["Y"]) + abs(attempt[3 + side] * directions[direction]),
                    )
                    matches = (
                        cursor in lookup
                        and bits_equal(lookup[cursor][1:4], base["conditions"])
                        and bits_equal(lookup[cursor][4 : 4 + n], state)
                    )
                    require(
                        not attempt[5 + side] or matches,
                        "admissible direction probe lacks bound F",
                    )
                    last_F[side] = lookup[cursor][4 + n :].copy() if matches else None
                    if matches:
                        if branch_hashes is not None:
                            require(
                                bool(attempt[5 + side])
                                == (branch_hashes[cursor] == branch_hashes[1]),
                                "direction branch-admissibility flag differs",
                            )
                        cursor += 1
                require(
                    not (
                        np.all(attempt[5:7] == 1)
                        and not np.array_equal(attempt, own[-1])
                    ),
                    "direction continued after admissible stencil",
                )
            valid = np.all(own[-1, 5:7] == 1)
            require(
                bool(row[3]) == valid
                and np.array_equal(row[2:3], own[-1, 2:3])
                and bits_equal(row[4:6], own[-1, 3:5]),
                "selected direction stencil differs",
            )
            require(
                bits_equal(row[6 + 5 * n : 6 + 6 * n], base["F"]),
                "direction baseline F differs",
            )
            if not valid:
                require(
                    len(own) == 3
                    and np.all(np.isnan(row[6 + 2 * n : 6 + 5 * n]))
                    and np.all(np.isnan(row[6 + 6 * n :])),
                    "refused direction missing explicit unavailable values",
                )
                continue
            for side in range(2):
                require(
                    bits_equal(
                        row[6 + (6 + side) * n : 6 + (7 + side) * n], last_F[side]
                    ),
                    "direction F payload binding differs",
                )
                arithmetic_comparison(
                    row[6 + (3 + side) * n : 6 + (4 + side) * n],
                    own[-1, 7 + side * n : 7 + (side + 1) * n] - base["Y"],
                    abs(own[-1, 7 + side * n : 7 + (side + 1) * n]) + abs(base["Y"]),
                )
            require(
                bits_equal(row[6 + 5 * n : 6 + 6 * n], base["F"]),
                "direction baseline F differs",
            )
            quotient = difference_quotient(
                base["F"], last_F[0], last_F[1], row[4], row[5]
            )
            compare_bound(
                row[6 + 2 * n : 6 + 3 * n], quotient["value"], quotient["allowance"]
            )
            recomputed[direction, mi] = quotient["value"]
        factor_checks = []
        for k, matrix in enumerate(matrices):
            if np.all(np.isfinite(matrix)):
                expected = matrix @ directions[direction]
                arithmetic_comparison(
                    saved_jv[:, direction, k],
                    expected,
                    abs(matrix) @ abs(directions[direction]),
                    flush_amplification=n,
                )
            else:
                require(
                    np.all(np.isnan(saved_jv[:, direction, k])),
                    "incomplete matrix has available Jv",
                )
            factor_checks.append(
                metrics.assess_directional_jacobian(
                    A,
                    saved_jv[:, direction, k],
                    recomputed[direction],
                    sweep[direction, :, 3].astype(bool),
                )
            )
        for row in sweep[direction]:
            require(
                bits_equal(row[6 + n : 6 + 2 * n], saved_jv[:, direction, 1]),
                "legacy factor-one Jv differs",
            )
        all_checks.append(factor_checks)
    require(cursor in lookup, "missing directional baseline restore")
    echo_evaluation(lookup[cursor], base["conditions"], base["Y"], base["F"])
    return {
        "directions": directions,
        "recomputed_Dv": recomputed,
        "agreement_by_direction_then_factor": all_checks,
        "next_call": cursor + 1,
    }


def parse_linear(data, n=N):
    require(len(data) >= 20, "truncated linear header")
    header = struct.unpack_from("<5i", data)
    require(header[:3] == (0x4352444C, 1, n), "linear header differs")
    count = 1 + 5 * n + 2 * n * n
    require(len(data) == 20 + 8 * count + 4 * n, "linear extent differs")
    values = rows(data[20 : 20 + 8 * count], count, finite=False)[0]
    cursor = 1
    result = {"h": values[0], "lu_info": header[3], "solve_info": header[4]}
    for key, size in (
        ("Y", n),
        ("Yold", n),
        ("F", n),
        ("M", n * n),
        ("rhs", n),
        ("LU", n * n),
        ("delta", n),
    ):
        value = values[cursor : cursor + size]
        cursor += size
        result[key] = (
            value.reshape((n, n), order="F")
            if size == n * n and key in ("M", "LU")
            else value
        )
    result["pivots"] = np.frombuffer(data[20 + 8 * count :], dtype="<i4").copy()
    require(
        np.isfinite(result["h"])
        and result["h"] > 0
        and all(
            np.isfinite(result[k]).all() for k in ("Y", "Yold", "F", "M", "rhs", "LU")
        ),
        "nonfinite linear operands",
    )
    require(
        np.isin(result["pivots"], np.arange(1, n + 1)).all()
        and 0 <= header[3] <= n
        and (header[4] == 0 if header[3] == 0 else header[4] == -999),
        "LAPACK status/pivots differ",
    )
    require(
        np.isfinite(result["delta"]).all()
        if header[4] == 0
        else np.isnan(result["delta"]).all(),
        "linear correction availability differs",
    )
    return result


def qvalues(quantity):
    return [
        Fraction(int(q["numerator"]), int(q["denominator"])) for q in quantity["exact"]
    ]


def qpack(values):
    values = list(values)
    return {
        "exact": [
            {"numerator": str(q.numerator), "denominator": str(q.denominator)}
            for q in values
        ],
        "rounded": np.array([float(q) for q in values]),
    }


def normalized_assembly_contribution(A, h, differences, scales):
    """Signed A*h*dF contribution to D-036's mass-weighted BE residual scale."""
    return qpack(
        Fraction(float(a)) * Fraction(float(h)) * d / s
        for a, d, s in zip(A, differences, scales, strict=True)
    )


def verify_linear(record, J, base, old, h, A):
    require(
        record["h"] == h
        and bits_equal(record["Y"], base["Y"])
        and bits_equal(record["Yold"], old)
        and bits_equal(record["F"], base["F"]),
        "linear operands differ from frozen state",
    )
    expected = -J.copy()
    expected[np.diag_indices(len(A))] += 1 / h
    matrix_check = arithmetic_comparison(
        record["M"], expected, abs(J) + np.eye(len(A)) / h
    )
    expected_rhs = (old - base["Y"]) / h + base["F"]
    require(
        h >= TINY and np.isfinite(1 / h) and abs(1 / h) >= TINY,
        "unsupported division arithmetic",
    )
    rhs_check = arithmetic_comparison(
        record["rhs"],
        expected_rhs,
        abs((old - base["Y"]) / h) + abs(base["F"]),
        flush_amplification=1 + 1 / h,
    )
    be = arithmetic.exact_be_residual(old, base["Y"], base["F"], h, A)
    alternate = [-r / Fraction(h) for r in qvalues(be["exact"])]
    report = {
        "M_recomputation": matrix_check,
        "rhs_recomputation": rhs_check,
        "baseline_BE": be,
        "alternate_exact_BE_rhs": qpack(alternate),
        "native_rhs_minus_alternate_exact": qpack(
            Fraction(float(v)) - r
            for v, r in zip(record["rhs"], alternate, strict=True)
        ),
        "lapack_success": record["lu_info"] == record["solve_info"] == 0,
    }
    if report["lapack_success"]:
        report["linear_arithmetic"] = arithmetic.linear_residual(
            record["M"], record["rhs"], record["delta"], A
        )
    return report


def _checked_inventory(root, inventory, *, exact=None):
    require(isinstance(inventory, dict), "missing hash inventory")
    if exact is not None:
        require(set(inventory) == set(exact), "raw file membership differs")
    for name, identity in inventory.items():
        path = safe(root, name)
        digest = identity["sha256"] if isinstance(identity, dict) else identity
        data = common.checked(path, digest)
        if isinstance(identity, dict) and "bytes" in identity:
            require(len(data) == identity["bytes"], "raw extent differs")


def _configuration(root):
    prepared = json.loads((root / "prepared.json").read_text())
    require(
        prepared.get("schema") == "crucible.phase2d.diagnostic-prepared.v1"
        and prepared.get("protocol_sha256") == PROTOCOL_SHA256
        and prepared.get("annex_sha256") == ANNEX_SHA256,
        "unrecognized diagnostic preparation",
    )
    require(
        prepared.get("original_protocol_sha256") == common.PROTOCOL_SHA256
        and prepared.get("original_annex_sha256") == common.ANNEX_SHA256,
        "original qualification binding differs",
    )
    require(
        all(
            isinstance(prepared.get(k), str)
            and re.fullmatch("[0-9a-f]{40}", prepared[k])
            for k in ("source_commit", "source_tree")
        ),
        "missing source commit/tree",
    )
    _checked_inventory(root, prepared["immutable_files"])
    annex = json.loads(common.checked(root / "annex.json", ANNEX_SHA256))
    common.checked(root / "DIAGNOSTIC_PROTOCOL.md", PROTOCOL_SHA256)
    require(
        [s["name"] for s in prepared["states"]] == list(STATES)
        and [s["name"] for s in annex["states"]] == list(STATES),
        "fixed state population differs",
    )
    states, plan = {}, []
    for state, frozen in zip(prepared["states"], annex["states"], strict=True):
        name = state["name"]
        require(
            all(
                state[k] == v
                for k, v in frozen.items()
                if k not in ("input", "companions")
            ),
            "frozen state metadata differs",
        )
        require(state["input"] == "inputs/" + name + "/input.bin", "state path differs")
        raw = common.checked(safe(root, state["input"]), state["input_sha256"])
        require(len(raw) >= 48 + 480 * 8, "truncated input")
        Y = np.frombuffer(raw, dtype="<f8", count=N, offset=48 + 2 * N * 8).copy()
        require(
            common.digest_bytes(Y.tobytes()) == state["Y_sha256"],
            "frozen Y identity differs",
        )
        payload = common.checked(
            root / "inputs" / (state["parent_case"] + ".npz"),
            common.INPUT_SHA256[state["parent_case"]],
        )
        with np.load(io.BytesIO(payload), allow_pickle=False) as file:
            case = common.validate_case({k: file[k].copy() for k in file.files})
        require(
            raw
            == common.wire_input(
                case,
                mode=0,
                mesh=np.array([state["time"]]),
                time=state["time"],
                state=Y,
            ),
            "input wire/species/forcing differs",
        )
        require(
            set(state["companions"]) == set(frozen["companions"]),
            "companion population differs",
        )
        companions = {}
        for key, identity in frozen["companions"].items():
            entry = state["companions"][key]
            require(
                entry == {"path": "inputs/" + name + "/" + key, "sha256": identity},
                "companion metadata differs",
            )
            companions[key] = common.checked(safe(root, entry["path"]), identity)
        coordinate = struct.unpack_from("<8i", raw)[7] - 1
        condition = np.array([state["time"], *common.forcing_at(case, state["time"])])
        states[name] = {
            "state": state,
            "input": raw,
            "Y": Y,
            "case": case,
            "conditions": condition,
            "coordinate": coordinate,
            "companions": companions,
        }
    for command in COMMANDS:
        for name in STATES:
            state = states[name]["state"]
            plan.append(
                {
                    "name": name + "-" + command,
                    "state": name,
                    "mode": 0,
                    "arguments": [command],
                    "input": state["input"],
                    "input_sha256": state["input_sha256"],
                    "companions": state["companions"]
                    if command == "diagnose" and name == STATES[2]
                    else {},
                }
            )
    require(prepared["attempts"] == plan, "fixed nine-process plan differs")
    campaign = json.loads((root / "campaign.json").read_text())
    require(
        campaign.get("schema") == "crucible.phase2d.diagnostic-campaign.v1"
        and campaign.get("prepared_sha256")
        == common.digest_bytes((root / "prepared.json").read_bytes()),
        "campaign/preparation identity differs",
    )
    require(
        [p["name"] for p in campaign["attempts"]] == [p["name"] for p in plan],
        "campaign attempt population differs",
    )
    for record, spec in zip(campaign["attempts"], plan, strict=True):
        require(
            all(record.get(k) == v for k, v in spec.items()),
            "recorded attempt contract differs",
        )
    present = (
        {p.name for p in (root / "attempts").iterdir() if p.is_dir()}
        if (root / "attempts").exists()
        else set()
    )
    require(present <= set(p["name"] for p in plan), "undeclared process directory")
    build = campaign["build"]
    _checked_inventory(
        root,
        build["build_files"],
        exact=[
            str(p.relative_to(root))
            for p in (root / "bundle").rglob("*")
            if p.is_file()
        ],
    )
    require(
        build["executables"]["trajectory_driver"]
        == common.digest_bytes((root / "bundle/trajectory_driver").read_bytes()),
        "executable identity differs",
    )
    require(
        build["libraries"]
        == json.loads((root / "bundle/linked-library-hashes.json").read_text()),
        "library receipt differs",
    )
    source = json.loads((root / "bundle/source-manifest.json").read_text())
    _checked_inventory(root / "bundle", source["files"])
    synthetic = json.loads((root / "synthetic.json").read_text())
    require(
        campaign.get("synthetic") == synthetic
        and synthetic.get("pass") is True
        and len(synthetic.get("scenarios", [])) == 11
        and all(r.get("pass") is True for r in synthetic.get("scenarios", []))
        and len(
            {
                (r.get("executable"), r.get("name"))
                for r in synthetic.get("scenarios", [])
            }
        )
        == 11,
        "compiled prerequisite evidence incomplete",
    )
    _checked_inventory(root, synthetic["files"])
    return prepared, campaign, states, plan


def branch_signatures(events, calls, time, size=BRANCHES):
    require(events.ndim == 2 and events.shape[1] == 5, "branch event dimensions differ")
    signature = np.zeros(size, dtype="<i4")
    cursor = 0
    digests = {}
    for call in range(1, calls + 1):
        while cursor < len(events) and events[cursor, 0] == call:
            row = events[cursor]
            require(row[1] == time, "branch event advanced time")
            index = integer(row[2], 1, size) - 1
            old, new = (
                integer(row[3], -(2**31), 2**31 - 1),
                integer(row[4], -(2**31), 2**31 - 1),
            )
            require(
                signature[index] == old and old != new,
                "branch transition not bound to previous selector",
            )
            signature[index] = new
            cursor += 1
        digests[call] = common.digest_bytes(signature.tobytes())
    require(cursor == len(events), "branch event call/order differs")
    return digests


def conditional_check(groups, baseline, A):
    conditioned = arithmetic.coefficient_conditioned(
        [
            {**g, "csect": c, "b": b}
            for g, c, b in zip(groups, baseline["csect"], baseline["b"], strict=True)
        ],
        A,
        baseline["Y"],
        baseline["F"],
    )
    require(
        conditioned["b_formation"]["within_roundoff_envelope"].all()
        and conditioned["assembly"]["within_roundoff_envelope"].all(),
        "conditional software arithmetic outside declared envelope",
    )
    return conditioned


def _attempt(root, spec, record, state, expected_maps, output):
    work = root / "attempts" / spec["name"]
    saved = json.loads((work / "attempt.json").read_text())
    for key, value in saved.items():
        require(record.get(key) == value, "campaign/attempt record differs")
    require(
        saved.get("completed") is True
        and saved.get("returncode") == 0
        and (work / "status.txt").read_text().splitlines()[-1:] == ["SUCCESS"],
        "native process incomplete/failed",
    )
    inventory = [
        str(p.relative_to(work))
        for p in work.rglob("*")
        if p.is_file() and p.name not in ("attempt.json", "attempt.pending")
    ]
    _checked_inventory(work, saved["files"], exact=inventory)
    require(
        (work / "input.bin").read_bytes() == state["input"]
        and saved["input_sha256"] == spec["input_sha256"],
        "attempt input identity differs",
    )
    require(
        (work / "species.bin").read_bytes() == state["input"][48 : 48 + 2 * N * 8],
        "species order differs",
    )
    map_bytes = (work / "used-maps.bin").read_bytes()
    require(
        map_bytes == expected_maps,
        "native map differs from hash-bound network initialization",
    )
    groups = reference.parse_maps(map_bytes)
    counts = json.loads((work / "counters.json").read_text())
    require(
        set(counts) == set(COUNTERS)
        and all(type(v) is int and v >= 0 for v in counts.values()),
        "counter population/types differ",
    )
    require(
        all(
            counts[k] == 0
            for k in ("newton", "retry", "accepted", "projection", "step_attempt")
        ),
        "covert integration/repair work",
    )
    require(
        all(
            counts[k] == counts["rhs"]
            for k in ("coefficient", "eos", "screening", "weak")
        ),
        "physical work accounting differs",
    )
    output["counters"] = counts
    require(
        not (work / "accepted.bin").exists()
        and not (work / "accepted-forcing.bin").exists(),
        "undeclared accepted trajectory output",
    )
    require(
        (work / "newton-residuals.bin").is_file()
        and (work / "newton-residuals.bin").stat().st_size == 0,
        "undeclared Newton iteration output",
    )
    evaluations = rows((work / "diagnostic-evaluations.bin").read_bytes(), 324)
    require(len(evaluations) == counts["rhs"], "physical evaluation count differs")
    lookup = evaluation_index(evaluations)
    ieee = rows((work / "diagnostic-ieee.bin").read_bytes(), 11, dtype="<i8")
    require(
        len(ieee) == counts["rhs"]
        and np.array_equal(ieee[:, 0], evaluations[:, 0])
        and np.all(ieee[:, 1:3] == 1)
        and np.all(ieee[:, 6:9] == 0)
        and np.isin(ieee[:, 3], [0, 1]).all()
        and np.isin(ieee[:, 9:11], [0, 1]).all()
        and np.array_equal(ieee[:, 4], ieee[:, 5])
        and np.all(ieee[:, 3] == ieee[0, 3])
        and np.all(ieee[:, 4] == ieee[0, 4])
        and np.all(
            np.where(ieee[:, 3] == 0, ieee[:, 4] == -1, np.isin(ieee[:, 4], [0, 1]))
        ),
        "IEEE modes/flags/counts differ",
    )
    command = spec["arguments"][0]
    repeats = 3 if command == "repeat-3" else 1
    require(
        sorted(p.name for p in work.glob("baseline-*.bin"))
        == [f"baseline-{i:03}.bin" for i in range(1, repeats + 1)],
        "baseline population differs",
    )
    bases = []
    for i in range(1, repeats + 1):
        base = parse_baseline((work / f"baseline-{i:03}.bin").read_bytes())
        require(
            bits_equal(base["conditions"], state["conditions"])
            and bits_equal(base["Y"], state["Y"]),
            "baseline input echo differs",
        )
        require(base["call_id"] in lookup, "baseline F ID missing")
        echo_evaluation(
            lookup[base["call_id"]], base["conditions"], base["Y"], base["F"]
        )
        if bases:
            require(
                bits_equal(base["comparison_bytes"], bases[0]["comparison_bytes"]),
                "within-process repeat changed",
            )
        if "expected-control.bin" in state["companions"]:
            require(
                base["F"].tobytes() == state["companions"]["expected-control.bin"],
                "D-019 initial control changed",
            )
        bases.append(base)
    base = bases[0]
    echo_evaluation(lookup[1], state["conditions"], state["Y"], base["F"])
    output.update(
        baselines=bases,
        counters=counts,
        evaluations=evaluations,
        ieee=ieee,
        branch_events=rows((work / "branch-events.bin").read_bytes(), 5, empty=True),
    )
    branch_hashes = branch_signatures(
        output["branch_events"], counts["rhs"], state["state"]["time"]
    )
    for baseline in bases:
        require(
            branch_hashes[baseline["call_id"]]
            == common.digest_bytes(baseline["branches"].tobytes()),
            "baseline branch signature differs from event replay",
        )
    output["branch_signature_sha256_by_call"] = {
        str(k): v for k, v in branch_hashes.items()
    }
    checkpoints = rows(
        (work / "counter-events.bin").read_bytes(), 14, dtype="<i8", empty=True
    )
    require(
        np.all(checkpoints >= 0)
        and np.all(checkpoints <= np.array([counts[k] for k in COUNTERS]))
        and np.all(np.diff(checkpoints, axis=0) >= 0),
        "counter checkpoints exceed final scope",
    )
    output["counter_events"] = checkpoints
    z, A = state["case"]["species_Z_A"].T
    require(
        np.all(evaluations[:, 1:4] == state["conditions"])
        and np.all(
            common.domain_flags(state["case"], evaluations[:, 1], evaluations[:, 4:164])
        ),
        "evaluated state/forcing/domain differs",
    )
    conditioned = conditional_check(groups, base, A)
    output["conditional_arithmetic"] = conditioned
    if command != "diagnose":
        require(
            counts["rhs"] == repeats
            and counts["jacobian"]
            == counts["lu"]
            == counts["linear_solve"]
            == counts["probe"]
            == 0,
            "repeat scope differs",
        )
        require(
            [b["call_id"] for b in bases] == list(range(1, repeats + 1)),
            "repeat baseline IDs differ",
        )
        output["software_pass"] = True
        return
    matrices = np.array(
        [
            rows((work / f"jacobian-factor-{i}.bin").read_bytes(), N * N, finite=False)[
                0
            ].reshape(N, N, order="F")
            for i in range(1, 5)
        ]
    )
    require(
        all(
            (work / f"jacobian-factor-{i}.bin").stat().st_size == 8 * N * N
            for i in range(1, 5)
        ),
        "matrix extent differs",
    )
    status = rows((work / "matrix-status.bin").read_bytes(), 5)
    columns = rows((work / "fd-columns.bin").read_bytes(), 6, empty=True)
    attempts = rows((work / "fd-probe-attempts.bin").read_bytes(), 12)
    jac_bases = rows((work / "jacobian-bases.bin").read_bytes(), 164)
    require(counts["jacobian"] == 4, "full-F Jacobian count differs")
    output.update(
        matrices=matrices,
        matrix_status=status,
        columns=columns,
        probe_attempts=attempts,
        jacobian_bases=jac_bases,
    )
    fd = verify_fd(
        matrices,
        status,
        columns,
        attempts,
        jac_bases,
        evaluations,
        A,
        branch_hashes=branch_hashes,
    )
    require(
        base["call_id"] == status[-1, 4], "fixed-b workspace not last Jacobian restore"
    )
    output.update(
        matrices=matrices,
        matrix_status=status,
        columns=columns,
        probe_attempts=attempts,
        jacobian_bases=jac_bases,
        fd_recomputation=fd,
    )
    require(
        (work / "native.log")
        .read_text()
        .count("DIAGNOSTIC_FIXED_B_MATRIX_BUILDS 1 (not a full-F Jacobian)")
        == 1,
        "fixed-b build accounting differs",
    )
    fixed = rows((work / "fixed-b-jacobian.bin").read_bytes(), N * N)[0].reshape(
        N, N, order="F"
    )
    exact = qvalues(conditioned["fixed_b_jacobian"])
    bounds = qvalues(conditioned["fixed_b_jacobian_arithmetic"]["roundoff_bound"])
    diff = [Fraction(float(v)) - q for v, q in zip(fixed.ravel(), exact, strict=True)]
    require(
        conditioned["fixed_b_jacobian_arithmetic"]["bound_supported"].all()
        and all(abs(d) <= b for d, b in zip(diff, bounds, strict=True)),
        "fixed-b native derivative outside exact arithmetic envelope",
    )
    output.update(
        conditional_arithmetic=conditioned,
        fixed_b_jacobian=fixed,
        fixed_b_minus_exact=qpack(diff),
    )
    sweep = rows((work / "directional.bin").read_bytes(), 1286, finite=False).reshape(
        3, 9, 1286
    )
    dir_attempts = rows((work / "direction-attempts.bin").read_bytes(), 327)
    jv = rows((work / "diagnostic-jv.bin").read_bytes(), N * 3 * 4, finite=False)[
        0
    ].reshape(N, 3, 4, order="F")
    output.update(directional_sweep=sweep, direction_attempts=dir_attempts, saved_jv=jv)
    directions = verify_directions(
        matrices,
        sweep,
        dir_attempts,
        jv,
        base,
        A,
        state["coordinate"],
        evaluations,
        fd["next_call"],
        branch_hashes=branch_hashes,
    )
    representable = (
        (attempts[:, 4] != 0)
        & (attempts[:, 5] != 0)
        & (attempts[:, 4] != attempts[:, 5])
    )
    require(
        counts["probe"] == 2 * (int(np.sum(representable)) + len(dir_attempts)),
        "probe/refusal counter differs",
    )
    output.update(
        directional_sweep=sweep,
        direction_attempts=dir_attempts,
        saved_jv=jv,
        directional_recomputation=directions,
    )
    pairs = []
    for left in range(4):
        for right in range(left + 1, 4):
            delta = matrices[right] - matrices[left]
            scaled = A[:, None] * delta / A[None, :]
            complete = bool(fd["complete"][left] and fd["complete"][right])
            norms = {}
            if complete:
                for label, array in (("raw", delta), ("mass_scaled", scaled)):
                    require(np.isfinite(array).all(), "unsupported matrix difference")
                    norm = {
                        "entry_l1": float(np.sum(abs(array))),
                        "frobenius_l2": float(np.linalg.norm(array)),
                        "entry_linf": float(np.max(abs(array))),
                        "pooled_rms": float(np.sqrt(np.mean(array**2))),
                        "row_sum_linf": float(np.max(np.sum(abs(array), axis=1))),
                        "column_sum_linf": float(np.max(np.sum(abs(array), axis=0))),
                    }
                    require(
                        all(np.isfinite(v) for v in norm.values()),
                        "unsupported matrix norm",
                    )
                    norms[label] = norm
            pairs.append(
                {
                    "factors": [float(FACTORS[left]), float(FACTORS[right])],
                    "complete": complete,
                    "norms": norms,
                    "difference": delta,
                    "mass_scaled_difference": scaled,
                    "mass_scaled_row_sum_linf": float(
                        np.max(np.sum(abs(scaled), axis=1))
                    )
                    if complete
                    else None,
                }
            )
    output["matrix_comparisons"] = pairs
    output["full_F_minus_fixed_b"] = matrices - fixed
    linear = {}
    if spec["state"] == STATES[2]:
        old = rows(state["companions"]["old-state.bin"], N)[0]
        h = rows(state["companions"]["frozen-h.bin"], 1)[0, 0]
        require(
            h == state["state"]["time"] == 1.953125e-7, "frozen linear h/time differs"
        )
        output["signed_h_assembly_difference_over_D036_scale"] = (
            normalized_assembly_contribution(
                A,
                h,
                qvalues(conditioned["assembly"]["native_F_minus_exact"]),
                qvalues(
                    arithmetic.exact_be_residual(old, base["Y"], base["F"], h, A)[
                        "nonlinear_scale"
                    ]
                ),
            )
        )
        for k in range(4):
            path = work / f"linear-factor-{k + 1}.bin"
            require(
                path.exists() == bool(fd["complete"][k]),
                "linear population does not match complete matrices",
            )
            if path.exists():
                record = parse_linear(path.read_bytes())
                linear[str(k + 1)] = {
                    "raw": record,
                    **verify_linear(record, matrices[k], base, old, h, A),
                }
        require(
            counts["lu"] == len(linear)
            and counts["linear_solve"]
            == sum(r["raw"]["lu_info"] == 0 for r in linear.values()),
            "linear counter scope differs",
        )
    else:
        require(
            not list(work.glob("linear-factor-*.bin"))
            and counts["lu"] == counts["linear_solve"] == 0,
            "undeclared linear stage",
        )
    output["linear"] = linear
    candidate = (work / "candidate-status.txt").read_text().strip()
    next_call = directions["next_call"]
    if spec["state"] != STATES[2]:
        require(candidate == "SKIPPED no frozen linear state", "undeclared candidate")
    elif "2" not in linear or not linear["2"]["lapack_success"]:
        require(
            candidate == "SKIPPED incomplete or failed factor-one linear solve",
            "candidate after failed factor one",
        )
    else:
        Y = base["Y"] + linear["2"]["raw"]["delta"]
        if candidate == "EVALUATED":
            candidate_base = parse_baseline((work / "candidate.bin").read_bytes())
            require(
                candidate_base["call_id"] == next_call
                and bits_equal(candidate_base["Y"], Y)
                and bits_equal(candidate_base["conditions"], base["conditions"]),
                "candidate advanced/repaired state",
            )
            echo_evaluation(
                lookup[next_call], base["conditions"], Y, candidate_base["F"]
            )
            require(
                branch_hashes[next_call]
                == common.digest_bytes(candidate_base["branches"].tobytes()),
                "candidate branch signature differs",
            )
            output["candidate"] = {
                "conditional_arithmetic": conditional_check(groups, candidate_base, A),
                "baseline": candidate_base,
                "BE": arithmetic.exact_be_residual(old, Y, candidate_base["F"], h, A),
            }
            next_call += 1
        else:
            require(
                candidate.startswith("REFUSED ") and len(candidate) > 8,
                "unknown candidate status",
            )
            refused = rows((work / "candidate-refused.bin").read_bytes(), 163)
            require(
                refused.shape == (1, 163)
                and bits_equal(refused[0, :3], base["conditions"])
                and bits_equal(refused[0, 3:], Y),
                "refused candidate missing or repaired",
            )
            output["candidate"] = {"refused": refused}
    require(
        (work / "candidate.bin").exists() == (candidate == "EVALUATED")
        and (work / "candidate-refused.bin").exists()
        == candidate.startswith("REFUSED "),
        "candidate output membership differs",
    )
    require(
        next_call == len(evaluations) + 1,
        "unaccounted physical source calls after directions/candidate",
    )
    output.update(candidate_status=candidate, software_pass=True)


def analyze(root):
    root = Path(root).resolve()
    report = {
        "schema": "crucible.phase2d.diagnostic-verification.v1",
        "software_pass": False,
        "trajectory_reference_qualified": False,
        "scientific_accuracy_acceptance": False,
        "attempts": {
            s + "-" + c: {"software_pass": False, "status": "UNAVAILABLE"}
            for c in COMMANDS
            for s in STATES
        },
        "errors": [],
        "analysis_code_sha256": {
            "diagnostic_report": common.digest_bytes(Path(__file__).read_bytes()),
            "conditioned_arithmetic": common.digest_bytes(
                Path(arithmetic.__file__).read_bytes()
            ),
            "campaign_contract": common.digest_bytes(
                Path(campaign_contract.__file__).read_bytes()
            ),
            "trajectory_reference": common.digest_bytes(
                Path(common.__file__).read_bytes()
            ),
            "trajectory_metrics": common.digest_bytes(
                Path(metrics.__file__).read_bytes()
            ),
            "rhs_reference": common.digest_bytes(Path(reference.__file__).read_bytes()),
        },
    }
    try:
        recorded = json.loads((root / "campaign.json").read_text())
        for item in recorded.get("attempts", []):
            if item.get("name") in report["attempts"]:
                report["attempts"][item["name"]].update(
                    status=item.get("status", "UNKNOWN"),
                    raw_files=item.get("files", {}),
                )
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    try:
        prepared, campaign, states, plan = _configuration(root)
        report.update(
            protocol_sha256=PROTOCOL_SHA256,
            annex_sha256=ANNEX_SHA256,
            source_commit=prepared["source_commit"],
            source_tree=prepared["source_tree"],
            prepared_sha256=campaign["prepared_sha256"],
        )
        expected_maps = reference.expected_maps(
            (root / "bundle/network/nets3").read_bytes(),
            (root / "bundle/network/nets4").read_bytes(),
        )
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        report["errors"].append(str(exc))
        return report
    baseline_by_state = {}
    mode_by_state = {}
    total = 0
    for spec, record in zip(plan, campaign["attempts"], strict=True):
        output = report["attempts"][spec["name"]]
        output.update(
            status=record.get("status", "UNKNOWN"), raw_files=record.get("files", {})
        )
        try:
            require(
                record.get("executable_sha256")
                == campaign["build"]["executables"]["trajectory_driver"],
                "attempt executable differs",
            )
            _attempt(root, spec, record, states[spec["state"]], expected_maps, output)
            baseline = output["baselines"][0]["comparison_bytes"]
            mode = output["ieee"][0, 1:6]
            if spec["state"] in mode_by_state:
                require(
                    bits_equal(mode, mode_by_state[spec["state"]]),
                    "IEEE modes changed across fresh processes",
                )
            else:
                mode_by_state[spec["state"]] = mode.copy()
            if spec["state"] in baseline_by_state:
                require(
                    bits_equal(baseline, baseline_by_state[spec["state"]]),
                    "fresh-process/stage C baseline differs",
                )
            else:
                baseline_by_state[spec["state"]] = baseline
        except (
            OSError,
            ValueError,
            KeyError,
            IndexError,
            TypeError,
            struct.error,
        ) as exc:
            output["software_pass"] = False
            output["error"] = str(exc)
        if "counters" in output:
            total += output["counters"]["rhs"]
    report["physical_rhs_calls_observed"] = total
    report["call_counts_complete"] = all(
        "counters" in v for v in report["attempts"].values()
    )
    report["software_pass"] = bool(
        campaign.get("complete") is True
        and campaign.get("stage_a_pass") is True
        and total <= MAX_RHS
        and total == campaign.get("physical_rhs_calls")
        and all(o["software_pass"] for o in report["attempts"].values())
    )
    return report


def reload_report(root):
    root = Path(root).resolve()
    saved = json.loads((root / "diagnostic-verification.json").read_text())
    manifest = saved.pop("array_artifact")
    payload = common.checked(safe(root, manifest["path"]), manifest["sha256"])
    with np.load(io.BytesIO(payload), allow_pickle=False) as file:
        require(
            set(file.files) == set(manifest["arrays"]),
            "derived array membership differs",
        )
        arrays = {k: file[k].copy() for k in file.files}
    for key, value in arrays.items():
        identity = manifest["arrays"][key]
        require(
            value.dtype.str == identity["dtype"]
            and list(value.shape) == identity["shape"]
            and common.digest_bytes(value.tobytes()) == identity["sha256"],
            "derived array identity differs",
        )
    report = analyze(root)
    encoded, recomputed = common.split_report(report)
    require(
        encoded == saved and set(arrays) == set(recomputed),
        "recomputed diagnostic metadata differs",
    )
    for key, value in arrays.items():
        require(
            bits_equal(value, recomputed[key]),
            "recomputed diagnostic array bytes differ",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("verify", "reload"):
        sub.add_parser(command).add_argument("root", type=Path)
    args = parser.parse_args()
    report = (
        analyze(args.root) if args.command == "verify" else reload_report(args.root)
    )
    if args.command == "verify":
        common.artifact_report(args.root / "diagnostic-verification.json", report)
    print(
        json.dumps(
            {
                "software_pass": report["software_pass"],
                "trajectory_reference_qualified": False,
            }
        )
    )
    if not report["software_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
