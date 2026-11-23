"""Independent binary-format and small-polynomial D-039 oracles; no native calls."""

import importlib.util
import json
import math
import struct
from fractions import Fraction as Q
from pathlib import Path

import pytest

PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments/trajectory_reference/assembly_arithmetic.py"
)
SPEC = importlib.util.spec_from_file_location("public_assembly_arithmetic", PATH)
a = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(a)


def exact_quad(value, negative_zero=False):
    """Encode exactly representable normals independently, never round a value."""
    value = Q(value)
    sign = int(value < 0 or (value == 0 and negative_zero))
    value = abs(value)
    if not value:
        return (sign << 127).to_bytes(16, "little")
    numerator, denominator = value.numerator, value.denominator
    assert denominator & (denominator - 1) == 0
    while numerator % 2 == 0:
        numerator //= 2
        denominator = Q(denominator, 2)
    # denominator may be a fractional power of two after removing numerator zeros.
    shift = denominator.numerator.bit_length() - denominator.denominator.bit_length()
    exponent = numerator.bit_length() - 1 - shift
    assert -16382 <= exponent <= 16383 and numerator.bit_length() <= 113
    significand = numerator << (113 - numerator.bit_length())
    bits = (sign << 127) | ((exponent + 16383) << 112) | (significand - (1 << 112))
    return bits.to_bytes(16, "little")


def weak_workspace(rate=4.0, abundance=0.25):
    group = {
        "order": 1,
        "participants": [(1, 2, 0, 0, 0)],
        "extended": [(1, 0, -1.0), (2, 0, 1.0)],
        "csect": [rate],
        "b": [-rate, rate],
    }
    product = Q(rate) * Q(abundance)
    products = [-product, product]
    quad = {
        "total": b"".join(map(exact_quad, products)),
        "classes": b"".join(
            exact_quad(v) for total in products for v in (total, 0, 0, 0)
        ),
        "products": b"".join(
            exact_quad(value, bool(value == 0 and i == 0))
            for i, value in enumerate(products)
        ),
        "running": b"".join(map(exact_quad, products)),
        "absolute": exact_quad(product) * 2,
    }
    return (
        [group],
        [1, 1],
        [abundance, 0.75],
        [-float(product) if product else 0.0, float(product)],
        [-float(product) if product else 0.0, float(product)],
        quad,
    )


def test_exact_binary128_known_bit_patterns_signed_zero_and_extreme_finite():
    encodings = [
        0,
        1 << 127,
        0x3FFF << 112,
        (1 << 127) | (0x4000 << 112),
        1,
        (1 << 112) - 1,
        1 << 112,
        (0x7FFE << 112) | ((1 << 112) - 1),
    ]
    decoded = a.decode_binary128(b"".join(v.to_bytes(16, "little") for v in encodings))
    assert [v["value"] for v in decoded[:4]] == [0, 0, 1, -2]
    assert decoded[1]["negative_zero"] and not decoded[0]["negative_zero"]
    assert decoded[4]["value"] == Q(1, 2**16494)
    assert decoded[5]["value"] == Q(2**112 - 1, 2**16494)
    assert decoded[6]["value"] == Q(1, 2**16382)
    assert decoded[7]["value"] == Q(2**113 - 1) * 2**16271
    for encoding, record in zip(encodings, decoded, strict=True):
        assert (
            a.round_binary128_bits(record["value"], record["negative_zero"]) == encoding
        )
    # Full-range fractions serialize without changing Python's decimal-string limit.
    assert (
        a.from_rational(json.loads(json.dumps(a.rational(decoded[4]["value"]))))
        == decoded[4]["value"]
    )


@pytest.mark.parametrize(
    "encoding", [(0x7FFF << 112), (0xFFFF << 112), (0x7FFF << 112) | 1]
)
def test_binary128_nonfinite_refusal(encoding):
    with pytest.raises(ValueError):
        a.decode_binary128(encoding.to_bytes(16, "little"))


def test_binary128_truncated_payload_refusal():
    with pytest.raises(ValueError):
        a.decode_binary128(bytes(15))


def test_binary64_nearest_even_normal_ties_and_carry():
    assert a.round_binary64_bits(Q(1)) == 0x3FF0000000000000
    assert a.round_binary64_bits(Q(1) + Q(1, 2**53)) == 0x3FF0000000000000
    assert a.round_binary64_bits(Q(1) + Q(3, 2**53)) == 0x3FF0000000000002
    assert a.round_binary64_bits(Q(2) - Q(1, 2**53)) == 0x4000000000000000
    assert a.round_binary64_bits(-Q(1) - Q(1, 2**53)) == 0xBFF0000000000000


def test_binary64_subnormal_ties_signed_zero_and_normal_boundary():
    unit = Q(1, 2**1074)
    assert a.round_binary64_bits(unit / 2) == 0
    assert a.round_binary64_bits(-unit / 2) == 1 << 63
    assert a.round_binary64_bits(Q(0), negative_zero=True) == 1 << 63
    assert a.round_binary64_bits(3 * unit / 2) == 2
    assert a.round_binary64_bits(-3 * unit / 2) == (1 << 63) | 2
    assert a.round_binary64_bits(Q(1, 2**1022) - unit / 2) == 0x0010000000000000
    assert a.round_binary64_bits(Q(1, 2**1022) - 3 * unit / 2) == 0x000FFFFFFFFFFFFE
    for bits in (
        1,
        2,
        0x000FFFFFFFFFFFFF,
        0x0010000000000000,
        0x7FEFFFFFFFFFFFFF,
        0x8000000000000001,
    ):
        value = struct.unpack("<d", struct.pack("<Q", bits))[0]
        assert a.round_binary64_bits(Q(value)) == bits


def test_binary64_overflow_midpoint_is_refused_not_saturated():
    maximum = Q(2**53 - 1) * 2**971
    assert a.round_binary64_bits(maximum + 2**969) == 0x7FEFFFFFFFFFFFFF
    with pytest.raises(ValueError):
        a.round_binary64_bits(maximum + 2**970)
    with pytest.raises(ValueError):
        a.round_binary64_bits(-(maximum + 2**970))


def test_exact_small_workspace_counts_bounds_and_zero_charge_not_imposed():
    report = a.verify_workspace(*weak_workspace())
    assert report["pass"] and not report["trajectory_reference_qualified"]
    assert [a.from_rational(q) for q in report["exact_polynomial"]["exact"]] == [-1, 1]
    assert report["class_entry_counts"] == [[1, 0, 0, 0], [1, 0, 0, 0]]
    assert report["operation_counts"] == [5, 5]
    assert a.from_rational(report["baryon_rate"]["variant"]) == 0
    assert all(report["correct_binary64_conversion"])


def test_promotion_before_product_rejects_sum_only_promotion_even_when_final_F64_matches():
    fixture = list(weak_workspace(1.0 + 2**-52, 1.0 - 2**-52))
    assert a.verify_workspace(*fixture)["pass"]
    assert float(Q(fixture[0][0]["b"][1]) * Q(fixture[2][0])) == 1.0
    wrong = fixture[-1].copy()
    wrong["total"] = exact_quad(-1) + exact_quad(1)
    wrong["products"] = wrong["running"] = wrong["total"]
    wrong["classes"] = b"".join(
        exact_quad(v) for sign in (-1, 1) for v in (sign, 0, 0, 0)
    )
    wrong["absolute"] = exact_quad(1) * 2
    fixture[-1] = wrong
    result = a.verify_workspace(*fixture)
    assert all(result["correct_binary64_conversion"])
    assert not result["pass"] and not all(result["quad_bound_pass"])


def cancellation_workspace(exponent):
    big = 2.0**exponent
    group = {
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
        "csect": [big, 1.0, big],
        "b": [big, 1.0, -big, -big, -1.0, big],
    }
    retained = Q(big) + 1 if exponent <= 112 else Q(big)
    total = Q(1) if exponent <= 112 else Q(0)
    absolute = 2 * Q(big) + 1 if exponent <= 111 else 2 * Q(big)
    products = [Q(big), Q(1), -Q(big), -Q(big), Q(-1), Q(big)]
    running = [Q(big), retained, total, -Q(big), -retained, -total]
    quad = {
        "total": exact_quad(total) + exact_quad(-total),
        "classes": b"".join(
            exact_quad(v) for t in (total, -total) for v in (t, 0, 0, 0)
        ),
        "products": b"".join(map(exact_quad, products)),
        "running": b"".join(map(exact_quad, running)),
        "absolute": exact_quad(absolute) * 2,
    }
    return (
        [group],
        [1, 1],
        [1.0, 1.0],
        [0.0, 0.0],
        [float(total), -float(total) if total else 0.0],
        quad,
    )


def test_binary128_cancellation_improves_digital_F_without_claiming_truth():
    result = a.verify_workspace(*cancellation_workspace(100))
    assert result["pass"]
    assert [a.from_rational(q) for q in result["original_minus_variant"]["exact"]] == [
        -1,
        1,
    ]


def test_binary128_can_still_lose_a_term_and_pass_its_derived_envelope():
    result = a.verify_workspace(*cancellation_workspace(120))
    assert result["pass"]
    assert a.from_rational(result["exact_polynomial"]["exact"][0]) == 1
    assert a.from_rational(result["quad_minus_polynomial"]["exact"][0]) == -1
    assert a.from_rational(result["quad_error_bound"]["exact"][0]) > 1
    assert not result["trajectory_reference_qualified"]


@pytest.mark.parametrize(
    "mutation",
    ["total", "class", "running", "product", "absolute", "variant", "zero_sign"],
)
def test_corrupted_intermediates_conversion_and_zero_sign_fail_qualification(mutation):
    fixture = weak_workspace()
    if mutation == "variant":
        fixture[4][0] += 0.001
    elif mutation == "zero_sign":
        fixture = weak_workspace(rate=0.0)
        fixture[4][0] = -0.0
    else:
        key = {
            "total": "total",
            "class": "classes",
            "running": "running",
            "product": "products",
            "absolute": "absolute",
        }[mutation]
        value = bytearray(fixture[-1][key])
        value[0] ^= 1
        fixture[-1][key] = bytes(value)
    result = a.verify_workspace(*fixture)
    assert not result["pass"]


@pytest.mark.parametrize(
    "mutation",
    [
        "Ynegative",
        "Fnan",
        "b_nan",
        "shape",
        "A_zero",
        "maps",
        "nonfinite_quad",
        "truncated",
    ],
)
def test_invalid_workspace_refusal(mutation):
    fixture = weak_workspace()
    if mutation == "Ynegative":
        fixture[2][0] = -1e-30
    elif mutation == "Fnan":
        fixture[3][0] = math.nan
    elif mutation == "b_nan":
        fixture[0][0]["b"][0] = math.nan
    elif mutation == "shape":
        fixture[4].append(0.0)
    elif mutation == "A_zero":
        fixture[1][0] = 0
    elif mutation == "maps":
        fixture[0][0]["extended"][0] = (2, 0, -1.0)
    elif mutation == "nonfinite_quad":
        fixture[-1]["total"] = (0x7FFF << 112).to_bytes(16, "little") + exact_quad(1)
    else:
        fixture[-1]["products"] = bytes(31)
    with pytest.raises(ValueError):
        a.verify_workspace(*fixture)


def test_repeated_reactants_and_higher_orders_have_independent_products_and_counts():
    cases = [
        (
            {
                "order": 2,
                "participants": [(1, 1, 1, 2, 0, 0)],
                "extended": [(1, 0, -1.0), (1, 0, 0.5), (2, 0, 0.5)],
                "csect": [8.0],
                "b": [-8.0, 4.0, 4.0],
            },
            [1, 1],
            [0.5, 0.5],
            [-2, 1, 1],
            [-2, -1, 1],
            [-1, 1],
            [3, 1],
            [9, 6],
        ),
        (
            {
                "order": 3,
                "participants": [(1, 1, 1, 2, 0, 0)],
                "extended": [(1, 0, -0.5), (2, 0, 1 / 6)],
                "csect": [6.0],
                "b": [-3.0, 1.0],
            },
            [1, 3],
            [0.5, 0.5],
            [Q(-3, 8), Q(1, 8)],
            [Q(-3, 8), Q(1, 8)],
            [Q(-3, 8), Q(1, 8)],
            [Q(3, 8), Q(1, 8)],
            [7, 7],
        ),
        (
            {
                "order": 4,
                "participants": [(1, 1, 2, 2, 3, 0)],
                "extended": [(1, 0, -1.0), (2, 0, -1.0), (3, 0, 0.5)],
                "csect": [256.0],
                "b": [-256.0, -256.0, 128.0],
            },
            [1, 1, 4],
            [0.25, 0.25, 0.0],
            [-1, -1, Q(1, 2)],
            [-1, -1, Q(1, 2)],
            [-1, -1, Q(1, 2)],
            [1, 1, Q(1, 2)],
            [8, 8, 8],
        ),
    ]
    for group, masses, y, products, running, totals, absolute, counts in cases:
        classes = [
            total if order == group["order"] else 0
            for total in totals
            for order in range(1, 5)
        ]
        blocks = {
            "products": b"".join(map(exact_quad, products)),
            "running": b"".join(map(exact_quad, running)),
            "total": b"".join(map(exact_quad, totals)),
            "classes": b"".join(map(exact_quad, classes)),
            "absolute": b"".join(map(exact_quad, absolute)),
        }
        result = a.verify_workspace(
            [group],
            masses,
            y,
            list(map(float, totals)),
            list(map(float, totals)),
            blocks,
        )
        assert result["pass"] and result["operation_counts"] == counts


def precision_files(tmp_path):
    (tmp_path / "assembly-kind.bin").write_bytes(
        struct.pack("<8i", 0x4352514B, 1, 2, 113, 128, -16381, 16384, 1)
    )
    bits = (
        0,
        1 << 63,
        1,
        (1 << 63) | 1,
        2**52 - 1,
        (1 << 63) | (2**52 - 1),
        1 << 52,
        (1 << 63) | (1 << 52),
        0x3FF0000000000000,
        0xBFF0000000000000,
    )
    data = bytearray(struct.pack("<4i", 0x43525150, 1, 10, 0))
    for value in bits:
        f = struct.unpack("<d", struct.pack("<Q", value))[0]
        data.extend(
            struct.pack("<Q", value)
            + exact_quad(Q(f), f == 0 and bool(value >> 63))
            + struct.pack("<Q", value)
        )
    (tmp_path / "precision-values.bin").write_bytes(data)
    unit = Q(1, 2**1074)
    cases = (
        (unit / 2, 0),
        (-unit / 2, 1 << 63),
        (3 * unit / 2, 2),
        (-3 * unit / 2, (1 << 63) | 2),
        (Q(1, 2**1022) - unit / 2, 1 << 52),
        (-Q(1, 2**1022) + unit / 2, (1 << 63) | (1 << 52)),
        (Q(1) + Q(1, 2**53), 0x3FF0000000000000),
        (Q(1) + Q(3, 2**53), 0x3FF0000000000002),
    )
    data = bytearray(struct.pack("<4i", 0x43525154, 1, 8, 0))
    for value, expected in cases:
        data.extend(exact_quad(value) + struct.pack("<2Q", expected, expected))
    (tmp_path / "rounding-values.bin").write_bytes(data)


def test_compiled_precision_bytes_are_independently_checked_without_running_a_fixture(
    tmp_path,
):
    precision_files(tmp_path)
    result = a.precision_values_gate(tmp_path)
    assert result["pass"] and result["promotions"] == 10 and result["ties"] == 8
    assert not result["trajectory_reference_qualified"]


@pytest.mark.parametrize(
    "mutation", ["kind", "daz", "signed_zero", "tie", "expected", "truncated"]
)
def test_precision_proof_corruption_refused(tmp_path, mutation):
    precision_files(tmp_path)
    path = tmp_path / (
        "assembly-kind.bin"
        if mutation == "kind"
        else "precision-values.bin"
        if mutation in ("daz", "signed_zero")
        else "rounding-values.bin"
    )
    data = bytearray(path.read_bytes())
    if mutation == "kind":
        struct.pack_into("<i", data, 12, 64)
    elif mutation == "daz":
        data[16 + 2 * 32 + 8 : 16 + 2 * 32 + 24] = exact_quad(0)
    elif mutation == "signed_zero":
        struct.pack_into("<Q", data, 16 + 32 + 24, 0)
    elif mutation == "tie":
        struct.pack_into("<Q", data, 16 + 16, 1)
    elif mutation == "expected":
        struct.pack_into("<Q", data, 16 + 24, 1)
    else:
        data.pop()
    path.write_bytes(data)
    with pytest.raises(ValueError):
        a.precision_values_gate(tmp_path)


def phase_record(phase=4):
    n = 160
    old = (0.5, 0.5) + tuple(0.0 for _ in range(n - 2))
    pre = old
    post = (0.25, 0.75) + old[2:]
    F = (-1.0, 1.0) + old[2:]
    zeros = tuple(0.0 for _ in range(n))
    unavailable = tuple(math.nan for _ in range(n))
    matrix = tuple(float(i == j) for j in range(n) for i in range(n))
    weights = tuple(
        1e-13 + 1e-11 * max(abs(4 * o), abs(4 * p))
        for o, p in zip(old, post, strict=True)
    )
    rec = {
        "ids": (1, 1, 1, 1, 2, 323, 324, 0, 0, 4),
        "scalars": (0.25, 0.25, 0.0, 0.0, 0.0, 0.0, 1e-13, 1e-11),
        "old": old,
        "pre": pre,
        "F_variant": (-2.0, 2.0) + old[2:],
        "F_original": (-2.0, 2.0) + old[2:],
        "J": matrix,
        "M": matrix,
        "rhs": zeros,
        "LU": matrix,
        "delta": (-0.25, 0.25) + old[2:],
        "unprojected": post,
        "post": post,
        "weights": weights,
        "residual": zeros,
        "projection_delta": zeros,
        "pivots": tuple(range(1, n + 1)),
    }
    if phase < 4:
        ids = list(rec["ids"])
        ids[6] = 0
        ids[9] = phase
        scalars = list(rec["scalars"])
        scalars[2:4] = [math.nan, math.nan]
        rec["weights"] = rec["residual"] = unavailable
        if phase < 3:
            ids[8] = -999
            scalars[4] = math.nan
            for key in ("delta", "unprojected", "post", "projection_delta"):
                rec[key] = unavailable
        if phase == 1:
            ids[7] = -999
            rec["rhs"] = unavailable
            rec["LU"] = (math.nan,) * (n * n)
            rec["pivots"] = (0,) * n
        rec["ids"] = tuple(ids)
        rec["scalars"] = tuple(scalars)
    return rec, F


def test_newton_phase_availability_and_exact_linear_exchange_BE_oracle():
    for phase in range(1, 5):
        a.verify_newton_phase(phase_record(phase)[0])
    record, F = phase_record()
    row = (
        324.0,
        10.0,
        1.0,
        0.25,
        1.0,
        1e6,
        4.0,
        2.0,
        0.5,
        1.0,
        2.0,
        3.0,
        1.0,
        1.0,
        1.0,
        1.0,
        *record["post"],
        *F,
        *F,
    )
    result = a._verify_newton_algebra(record, row, [4.0] * 160)
    assert result["norm"] == result["recomputed_norm"] == 0.0
    assert result["projection"] == result["projection_recomputed"] == 0.0


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_post_call",
        "LU_info",
        "early_available",
        "weights",
        "projection",
        "post_F",
        "residual",
    ],
)
def test_newton_forensic_and_residual_corruption_refused(mutation):
    record, F = phase_record()
    if mutation == "early_available":
        record = phase_record(1)[0]
        record["rhs"] = (0.0,) * 160
    elif mutation == "missing_post_call":
        ids = list(record["ids"])
        ids[6] = 0
        record["ids"] = tuple(ids)
    elif mutation == "LU_info":
        ids = list(record["ids"])
        ids[7] = 1
        record["ids"] = tuple(ids)
    elif mutation == "weights":
        record["weights"] = (1e-4,) + record["weights"][1:]
    elif mutation == "projection":
        record["post"] = (0.0,) + record["post"][1:]
    elif mutation == "post_F":
        F = (0.0, 0.0) + F[2:]
    else:
        record["residual"] = (1e-4,) + record["residual"][1:]
    row = (
        324.0,
        10.0,
        1.0,
        0.25,
        1.0,
        1e6,
        4.0,
        2.0,
        0.5,
        1.0,
        2.0,
        3.0,
        1.0,
        1.0,
        1.0,
        1.0,
        *record["post"],
        *F,
        *F,
    )
    with pytest.raises(ValueError):
        a.verify_newton_phase(record)
        a._verify_newton_algebra(record, row, [4.0] * 160)


def test_newton_stream_header_and_partial_phase_refused(tmp_path):
    path = tmp_path / "assembly-newton.bin"
    path.write_bytes(
        struct.pack("<8i", 0x4352414E, 1, 160, 78568, 10, 160, 0, 0) + bytes(100)
    )
    with pytest.raises(ValueError):
        list(a.newton_records(path))
    path.write_bytes(bytes(32))
    with pytest.raises(ValueError):
        list(a.newton_records(path))


def test_absent_or_unattempted_host_inputs_are_never_a_pass(tmp_path):
    for function in (a.precision_gate, a.identity_gate, a.derivative_gate):
        result = function(tmp_path)
        assert not result["pass"] and not result["software_pass"] and result["fatal"]
    result = a.first_step_gate(tmp_path, {"stage": "standard"}, {})
    assert not result["pass"] and not result["ordinary_numerical_failure"]


class MemoryEvaluations:
    """Ordinary public byte-equivalent records, backed by analytic test vectors."""

    def __init__(self, y):
        self.rows = []
        self.y = tuple(y)

    @property
    def count(self):
        return len(self.rows)

    def row(self, call):
        return self.rows[call - 1]

    def add(self, y, role, context):
        y = tuple(y)
        F = tuple((i + 1) * v for i, v in enumerate(y))
        call = self.count + 1
        self.rows.append(
            (
                float(call),
                float(role),
                float(context),
                0.0,
                1.0,
                1e6,
                1.0,
                0.5,
                0.5,
                1.0,
                2.0,
                3.0,
                1.0,
                1.0,
                1.0,
                1.0,
                *y,
                *F,
                *F,
            )
        )
        return call, F


def fixed_fd_fixture():
    n = 160
    y = tuple(0.01 + (0.25 if i == 0 else 0.5 if i == 1 else 0) for i in range(n))
    masses = [1.0] * n
    evaluations = MemoryEvaluations(y)
    evaluations.add(y, 1, 0)
    _, F0 = evaluations.add(y, 3, 1)
    matrix = [0.0] * (n * n)
    selected = []
    probes = []
    for col in range(n):
        nominal = a.EPS ** (1 / 3) * max(abs(y[col]), 1e-8)
        p1, p2 = list(y), list(y)
        p1[col] -= nominal
        p2[col] += nominal
        d1, d2 = p1[col] - y[col], p2[col] - y[col]
        id1, F1 = evaluations.add(p1, 4, 1)
        id2, F2 = evaluations.add(p2, 5, 1)
        q1, q2 = Q(d1), Q(d2)
        w1, w2 = -q2 / (q1 * (q1 - q2)), -q1 / (q2 * (q2 - q1))
        # Exact independent rational quotient of the serialized analytic outputs.
        matrix[col + n * col] = float(
            w1 * (Q(F1[col]) - Q(F0[col])) + w2 * (Q(F2[col]) - Q(F0[col]))
        )
        selected.append((1.0, float(col + 1), 0.0, 0.0, d1, d2))
        probes.append(
            (
                1.0,
                float(col + 1),
                0.0,
                nominal,
                d1,
                d2,
                p1[col],
                p2[col],
                1.0,
                1.0,
                float(id1),
                float(id2),
            )
        )
    restore, _ = evaluations.add(y, 6, 1)
    same = bytearray([1]) * (evaluations.count + 1)
    return [
        matrix,
        1,
        (0.0, 1.0, 1e6),
        y,
        F0,
        2,
        restore,
        selected,
        probes,
        evaluations,
        same,
        masses,
    ]


def test_variant_factor_one_columns_have_independent_observed_F_oracle():
    fixture = fixed_fd_fixture()
    result = a._fd_block(*fixture)
    assert (
        result["complete"]
        and result["selected_columns"] == 160
        and result["probe_requests"] == 320
    )
    assert result["restore_call"] == 323
    for i in (0, 1, 70, 159):
        assert abs(fixture[0][i + 160 * i] - (i + 1)) < 1e-7


@pytest.mark.parametrize(
    "mutation", ["J", "offset", "F", "role", "call", "branch", "halving"]
)
def test_variant_J_binding_corruptions_fail(mutation):
    fixture = fixed_fd_fixture()
    if mutation == "J":
        fixture[0][0] += 0.1
    elif mutation == "offset":
        row = list(fixture[8][0])
        row[4] *= 2
        fixture[8][0] = tuple(row)
    elif mutation == "F":
        row = list(fixture[9].rows[2])
        row[336] += 0.1
        fixture[9].rows[2] = tuple(row)
    elif mutation == "role":
        row = list(fixture[9].rows[2])
        row[1] = 5
        fixture[9].rows[2] = tuple(row)
    elif mutation == "call":
        row = list(fixture[8][0])
        row[10] = 1.0
        fixture[8][0] = tuple(row)
    elif mutation == "branch":
        fixture[10][3] = 0
    else:
        row = list(fixture[7][0])
        row[3] = 1.0
        fixture[7][0] = tuple(row)
    with pytest.raises(ValueError):
        a._fd_block(*fixture)


def direction_files(tmp_path, wrong=False):
    n = 160
    y = tuple(0.01 + (0.25 if i == 0 else 0.5 if i == 1 else 0) for i in range(n))
    masses = [1.0] * n
    evaluations = MemoryEvaluations(y)
    _, F0 = evaluations.add(y, 1, 0)
    base = {"Y": y, "F": F0, "conditions": (0.0, 1.0, 1e6)}
    matrix = [0.0] * (n * n)
    for i in range(n):
        matrix[i + n * i] = (i + 1) * (1.1 if wrong else 1.0)
    directions = (
        y,
        tuple(v if i % 2 == 0 else 0.0 for i, v in enumerate(y)),
        tuple(v if i == 0 else 0.0 for i, v in enumerate(y)),
    )
    jv_all = [math.nan] * (n * 3 * 4)
    rows = []
    attempts = []
    for direction, v in enumerate(directions, 1):
        jv = tuple(matrix[i + n * i] * v[i] for i in range(n))
        jv_all[n * 3 + (direction - 1) * n : n * 3 + direction * n] = jv
        for mi, m in enumerate(a.MULTIPLIERS, 1):
            p1 = tuple(p - m * d for p, d in zip(y, v, strict=True))
            p2 = tuple(p + m * d for p, d in zip(y, v, strict=True))
            context = 100 * direction + 10 * mi + 1
            _, F1 = evaluations.add(p1, 7, context)
            _, F2 = evaluations.add(p2, 8, context)
            dv = tuple(
                float((Q(f2) - Q(f1)) / (2 * Q(m)))
                for f1, f2 in zip(F1, F2, strict=True)
            )
            rows.append(
                (
                    float(direction),
                    float(mi),
                    0.0,
                    1.0,
                    -m,
                    m,
                    *v,
                    *jv,
                    *dv,
                    *(p - q for p, q in zip(p1, y, strict=True)),
                    *(p - q for p, q in zip(p2, y, strict=True)),
                    *F0,
                    *F1,
                    *F2,
                )
            )
            attempts.append(
                (float(direction), float(mi), 0.0, -m, m, 1.0, 1.0, *p1, *p2)
            )
    evaluations.add(y, 9, 0)
    (tmp_path / "directional.bin").write_bytes(
        b"".join(struct.pack("<1286d", *row) for row in rows)
    )
    (tmp_path / "direction-attempts.bin").write_bytes(
        b"".join(struct.pack("<327d", *row) for row in attempts)
    )
    (tmp_path / "diagnostic-jv.bin").write_bytes(struct.pack("<1920d", *jv_all))
    return (
        tmp_path,
        matrix,
        True,
        base,
        evaluations,
        2,
        bytearray([1]) * (evaluations.count + 1),
        masses,
        0,
    )


def test_exact_three_variant_direction_windows_and_unattempted_factor_slots(tmp_path):
    result = a._directional(*direction_files(tmp_path))
    assert result["pass"] and len(result["directions"]) == 3
    assert all(
        len(r["stable_windows"]) == 8 and any(r["stable_windows"])
        for r in result["directions"]
    )
    assert result["probe_requests"] == 54 and result["next_call"] == 57


def test_failed_variant_direction_agreement_is_a_retained_scientific_outcome(tmp_path):
    result = a._directional(*direction_files(tmp_path, wrong=True))
    assert not result["pass"]
    assert len(result["directions"]) == 3 and all(
        not r["pass"] for r in result["directions"]
    )
    assert all(all(r["admissible"]) for r in result["directions"])


def test_undeclared_factor_result_is_not_silently_accepted(tmp_path):
    fixture = direction_files(tmp_path)
    path = tmp_path / "diagnostic-jv.bin"
    raw = bytearray(path.read_bytes())
    struct.pack_into("<d", raw, 0, 0.0)
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="undeclared factor"):
        a._directional(*fixture)


def test_raw_inventory_hashing_is_streamed_and_never_uses_read_bytes(
    tmp_path, monkeypatch
):
    import hashlib

    payload = b"public fixed stream\0" * 120000
    path = tmp_path / "large.bin"
    path.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()

    def forbidden(self):
        raise AssertionError("unbounded read_bytes used for raw inventory")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    a._inventory(
        tmp_path,
        {"large.bin": {"sha256": expected, "bytes": len(payload)}},
        exact=["large.bin"],
    )
    with pytest.raises(ValueError):
        a._inventory(tmp_path, {"large.bin": "0" * 64})
    with pytest.raises(ValueError):
        a._inventory(tmp_path, {"large.bin": expected}, exact=[])


def test_zero_masks_and_separate_conversion_bound_are_explicit():
    result = a.verify_workspace(*weak_workspace(rate=0.0))
    assert result["pass"] and result["zero_masks"]["polynomial"] == [True, True]
    assert result["zero_masks"]["variant_negative_zero"] == [False, False]
    half = a.from_rational(result["conversion_half_subnormal_bound"])
    assert half == Q(1, 2**1075)
    for quad, conversion, combined in zip(
        result["quad_error_bound"]["exact"],
        result["conversion_relative_bound"]["exact"],
        result["combined_error_bound"]["exact"],
        strict=True,
    ):
        assert a.from_rational(quad) + a.from_rational(
            conversion
        ) + half == a.from_rational(combined)
