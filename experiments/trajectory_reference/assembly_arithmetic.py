"""Exact, offline D-039 assembly arithmetic and host-safe qualification gates.

Only Python's standard library is used. No producer, compiler, native executable
or physical callback is imported or invoked. IEEE operands are decoded from
retained bytes. Hexadecimal fraction strings cover the full binary128 range
without changing Python's integer-string limits or floating-point environment.
"""

import hashlib
import importlib.util
import json
import math
import struct
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL_SHA256 = "ff5515f04ecfdb9cb75f284882dc88d5beef30a25d1a4a8b9e9a18ba741abf02"
ANNEX_SHA256 = "dbb954afac144d9305a87e483c0c08833a8cdf2487d390f2d6532e5e72a814eb"
SOURCE = "native-XNet-b64-productsum113-b64-v1"
STATES = ("development-initial", "validation-initial", "development-newton300")
CASES = ("development", "validation")
NC, NB = (683, 1345, 16, 4), (1862, 4860, 53, 19)
N, NQ, MAX_CALLS = 160, 14548, 10398034
UQ, U64 = Q(1, 2**113), Q(1, 2**53)
MIN_Q, MAX_Q = Q(1, 2**16382), Q(2**113 - 1) * 2 ** (16383 - 112)
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


def require(condition, message):
    if not condition:
        raise ValueError("assembly qualification: " + message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _legacy():
    folder = HERE / "rhs_reference"
    if not folder.is_dir():
        folder = HERE.parent / "rhs_reference"
    arithmetic = load_module("_assembly_legacy_arithmetic", folder / "arithmetic.py")
    prior = sys.modules.get("arithmetic")
    sys.modules["arithmetic"] = arithmetic
    try:
        reference = load_module("_assembly_legacy_reference", folder / "reference.py")
    finally:
        if prior is None:
            del sys.modules["arithmetic"]
        else:
            sys.modules["arithmetic"] = prior
    return arithmetic, reference


legacy_arithmetic, legacy_reference = _legacy()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe artifact path")
    return Path(root) / path


def checked(root, name, identity):
    payload = safe(root, name).read_bytes()
    require(sha(payload) == identity, "artifact identity differs: " + name)
    return payload


def rational(q):
    return {
        "numerator_hex": format(q.numerator, "x"),
        "denominator_hex": format(q.denominator, "x"),
    }


def from_rational(value):
    return Q(int(value["numerator_hex"], 16), int(value["denominator_hex"], 16))


def quantity(values):
    values = list(values)
    rounded = []
    for value in values:
        try:
            approximation = float(value)
        except OverflowError:
            approximation = None
        rounded.append(
            approximation
            if approximation is not None and math.isfinite(approximation)
            else None
        )
    return {"exact": [rational(v) for v in values], "rounded": rounded}


def power2(exponent):
    return Q(2**exponent) if exponent >= 0 else Q(1, 2**-exponent)


def _log2_floor(value):
    n, d = value.numerator, value.denominator
    exponent = n.bit_length() - d.bit_length()
    if value < power2(exponent):
        exponent -= 1
    return exponent


def _nearest_integer(value):
    integer, remainder = divmod(value.numerator, value.denominator)
    return integer + (
        2 * remainder > value.denominator
        or (2 * remainder == value.denominator and integer % 2 == 1)
    )


def _round_bits(value, precision, emin, emax, exponent_bits, negative_zero=False):
    require(
        isinstance(value, Q) and type(negative_zero) is bool,
        "exact Fraction and explicit zero sign required",
    )
    sign = int(value < 0 or (value == 0 and negative_zero))
    width = precision + exponent_bits
    value = abs(value)
    if value == 0:
        return sign << (width - 1)
    exponent = _log2_floor(value)
    ulp = max(exponent, emin) - (precision - 1)
    significand = _nearest_integer(value / power2(ulp))
    if exponent < emin:
        if significand < 2 ** (precision - 1):
            return (sign << (width - 1)) | significand
        exponent = emin
    elif significand == 2**precision:
        significand //= 2
        exponent += 1
    require(exponent <= emax, "nearest conversion overflows the target format")
    exponent_field = exponent + 1 - emin
    fraction = significand - 2 ** (precision - 1)
    return (sign << (width - 1)) | (exponent_field << (precision - 1)) | fraction


def round_binary64_bits(value, negative_zero=False):
    """Independently round an exact rational to IEEE binary64, ties to even.

    Returns the uint64 encoding, including signed zero. Overflow is refused.
    No binary64 arithmetic is used to make rounding decisions.
    """
    return _round_bits(value, 53, -1022, 1023, 11, negative_zero)


def round_binary128_bits(value, negative_zero=False):
    """Exact nearest-even IEEE binary128 encoding; no host long-double assumption."""
    return _round_bits(value, 113, -16382, 16383, 15, negative_zero)


def decode_binary128(data):
    """Decode little-endian 16-byte IEEE binary128 values to exact fractions."""
    require(
        isinstance(data, (bytes, bytearray, memoryview)) and len(data) % 16 == 0,
        "binary128 stream extent differs",
    )
    result = []
    for offset in range(0, len(data), 16):
        bits = int.from_bytes(data[offset : offset + 16], "little")
        sign, exponent, fraction = (
            bits >> 127,
            (bits >> 112) & 0x7FFF,
            bits & (2**112 - 1),
        )
        require(exponent != 0x7FFF, "nonfinite binary128 value")
        significand = fraction if exponent == 0 else 2**112 + fraction
        value = Q(significand) * power2(
            (1 - 16383 if exponent == 0 else exponent - 16383) - 112
        )
        if sign:
            value = -value
        result.append(
            {
                "value": value,
                "negative_zero": bool(sign and significand == 0),
                "bits": bits,
            }
        )
    return result


def _quad(bits):
    return decode_binary128(bits.to_bytes(16, "little"))[0]


def _float64(value):
    require(not isinstance(value, bool), "boolean is not a binary64 operand")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("assembly qualification: invalid binary64 operand") from exc
    require(math.isfinite(value), "nonfinite binary64 operand")
    return value


def _sign64(value):
    return struct.unpack("<Q", struct.pack("<d", value))[0] >> 63


def _add(left, right):
    value = left["value"] + right["value"]
    negative_zero = value == 0 and left["negative_zero"] and right["negative_zero"]
    return _quad(round_binary128_bits(value, negative_zero))


def _multiply(left, right, right_negative):
    value = left["value"] * right
    sign = (left["value"] < 0 or left["negative_zero"]) ^ right_negative
    return _quad(round_binary128_bits(value, bool(sign and value == 0)))


def verify_workspace(groups, A, Y, F_original, F_variant, quad_blocks):
    """Independently verify ordered products/sums, support and D-039 envelopes.

    groups use the existing Phase 1 participant/extended mapping plus csect,b.
    quad_blocks contains raw little-endian bytes under keys total,classes,
    products,running,absolute. Classes use Fortran (4,n) order; entry arrays
    concatenate orders1..4 in native extended-entry order. No derivative matrix
    or per-probe rational report is constructed.
    """
    n = len(A)
    require(
        n > 0 and all(len(v) == n for v in (Y, F_original, F_variant)),
        "workspace species shape differs",
    )
    masses = [Q(_float64(v)) for v in A]
    require(all(v > 0 and v.denominator == 1 for v in masses), "invalid nuclear masses")
    y, original, variant = [
        [_float64(v) for v in vector] for vector in (Y, F_original, F_variant)
    ]
    require(all(0 <= v <= 1 for v in y), "abundance outside [0,1]")
    require(
        [g["order"] for g in groups] == sorted(set(g["order"] for g in groups))
        and all(type(g["order"]) is int and g["order"] in range(1, 5) for g in groups),
        "reaction order differs",
    )
    legacy_arithmetic.mapping_terms(groups, masses)
    count = sum(len(g["extended"]) for g in groups)
    require(count <= 6794, "extended-entry count exceeds accepted support")
    expected_shapes = {
        "total": n,
        "classes": 4 * n,
        "products": count,
        "running": count,
        "absolute": n,
    }
    require(set(quad_blocks) == set(expected_shapes), "quad block population differs")
    decoded = {key: decode_binary128(raw) for key, raw in quad_blocks.items()}
    require(
        all(len(decoded[k]) == size for k, size in expected_shapes.items()),
        "quad block shape differs",
    )
    P, W = [Q(0) for _ in A], [Q(0) for _ in A]
    sums = [[_quad(0) for _ in A] for _ in range(4)]
    absolutes = [_quad(0) for _ in A]
    counts = [[0] * 4 for _ in A]
    ordering = [True] * n
    supported = [True] * n
    entry = 0
    for group in groups:
        order = group["order"]
        require(
            len(group["csect"]) == len(group["participants"])
            and len(group["b"]) == len(group["extended"]),
            "coefficient shape differs",
        )
        require(
            all(math.isfinite(_float64(v)) for v in group["csect"]),
            "nonfinite coefficient",
        )
        for ei, (target, mu, _) in enumerate(group["extended"]):
            i = target - 1
            b = _float64(group["b"][ei])
            term = Q(b)
            product = _quad(round_binary128_bits(term, bool(term == 0 and _sign64(b))))
            for reactant in group["participants"][mu][:order]:
                operand = y[reactant - 1]
                exact_product = product["value"] * Q(operand)
                supported[i] &= (
                    exact_product == 0 or MIN_Q <= abs(exact_product) <= MAX_Q
                )
                product = _multiply(product, Q(operand), bool(_sign64(operand)))
                term *= Q(operand)
            P[i] += term
            W[i] += abs(term)
            counts[i][order - 1] += 1
            supported[i] &= (
                product["value"] == 0 or MIN_Q <= abs(product["value"]) <= MAX_Q
            )
            supported[i] &= all(
                record["value"] == 0 or MIN_Q <= abs(record["value"]) <= MAX_Q
                for record in (decoded["products"][entry], decoded["running"][entry])
            )
            ordering[i] &= decoded["products"][entry]["bits"] == product["bits"]
            sums[order - 1][i] = _add(sums[order - 1][i], product)
            supported[i] &= (
                sums[order - 1][i]["value"] == 0
                or MIN_Q <= abs(sums[order - 1][i]["value"]) <= MAX_Q
            )
            ordering[i] &= (
                decoded["running"][entry]["bits"] == sums[order - 1][i]["bits"]
            )
            absolute_product = _quad(product["bits"] & (2**127 - 1))
            absolutes[i] = _add(absolutes[i], absolute_product)
            entry += 1
    quad_error, quad_bounds, combined_bounds, variant_error, converted, total_match = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for i in range(n):
        for order in range(4):
            observed_class = decoded["classes"][4 * i + order]["value"]
            supported[i] &= observed_class == 0 or MIN_Q <= abs(observed_class) <= MAX_Q
            ordering[i] &= (
                decoded["classes"][4 * i + order]["bits"] == sums[order][i]["bits"]
            )
            supported[i] &= (
                sums[order][i]["value"] == 0
                or MIN_Q <= abs(sums[order][i]["value"]) <= MAX_Q
            )
        total = sums[0][i]
        for order in range(1, 4):
            total = _add(total, sums[order][i])
            supported[i] &= total["value"] == 0 or MIN_Q <= abs(total["value"]) <= MAX_Q
        total_match.append(decoded["total"][i]["bits"] == total["bits"])
        observed_absolute = decoded["absolute"][i]["value"]
        supported[i] &= (
            observed_absolute == 0 or MIN_Q <= abs(observed_absolute) <= MAX_Q
        )
        ordering[i] &= decoded["absolute"][i]["bits"] == absolutes[i]["bits"]
        m = sum((order + 2) * number for order, number in enumerate(counts[i])) + 3
        require(
            m <= 33973 and m * UQ < 1, "operation envelope exceeds accepted support"
        )
        bound = (m * UQ / (1 - m * UQ)) * W[i]
        observed = decoded["total"][i]
        supported[i] &= (
            observed["value"] == 0 or MIN_Q <= abs(observed["value"]) <= MAX_Q
        )
        quad_error.append(observed["value"] - P[i])
        quad_bounds.append(bound)
        combined_bounds.append(bound + U64 * (abs(P[i]) + bound) + Q(1, 2**1075))
        variant_error.append(Q(variant[i]) - P[i])
        try:
            expected_bits = round_binary64_bits(
                observed["value"], observed["negative_zero"]
            )
            converted.append(
                expected_bits == struct.unpack("<Q", struct.pack("<d", variant[i]))[0]
            )
        except ValueError:
            converted.append(False)
    quad_pass = [abs(e) <= b for e, b in zip(quad_error, quad_bounds, strict=True)]
    final_pass = [
        abs(e) <= b for e, b in zip(variant_error, combined_bounds, strict=True)
    ]
    all_pass = (
        all(supported)
        and all(ordering)
        and all(total_match)
        and all(quad_pass)
        and all(converted)
        and all(final_pass)
    )
    return {
        "pass": bool(all_pass),
        "source": SOURCE,
        "trajectory_reference_qualified": False,
        "operand_support": supported,
        "ordered_intermediates_pass": ordering,
        "total_order_pass": total_match,
        "quad_bound_pass": quad_pass,
        "correct_binary64_conversion": converted,
        "combined_bound_pass": final_pass,
        "class_entry_counts": counts,
        "operation_counts": [
            sum((j + 2) * v for j, v in enumerate(row)) + 3 for row in counts
        ],
        "zero_masks": {
            "polynomial": [v == 0 for v in P],
            "quad": [v["value"] == 0 for v in decoded["total"]],
            "quad_negative_zero": [v["negative_zero"] for v in decoded["total"]],
            "variant": [v == 0 for v in variant],
            "variant_negative_zero": [v == 0 and bool(_sign64(v)) for v in variant],
        },
        "exact_polynomial": quantity(P),
        "quad_total": quantity(v["value"] for v in decoded["total"]),
        "exact_positive_term_sum": quantity(
            (w + p) / 2 for w, p in zip(W, P, strict=True)
        ),
        "exact_negative_term_sum": quantity(
            (p - w) / 2 for w, p in zip(W, P, strict=True)
        ),
        "conversion_relative_bound": quantity(
            U64 * (abs(p) + e) for p, e in zip(P, quad_bounds, strict=True)
        ),
        "conversion_half_subnormal_bound": rational(Q(1, 2**1075)),
        "absolute_term_sum": quantity(W),
        "quad_minus_polynomial": quantity(quad_error),
        "quad_error_bound": quantity(quad_bounds),
        "variant_minus_polynomial": quantity(variant_error),
        "combined_error_bound": quantity(combined_bounds),
        "original_minus_variant": quantity(
            Q(a) - Q(b) for a, b in zip(original, variant, strict=True)
        ),
        "baryon_rate": {
            key: rational(
                sum((mass * v for mass, v in zip(masses, values, strict=True)), Q(0))
            )
            for key, values in (
                ("original", map(Q, original)),
                ("variant", map(Q, variant)),
                ("polynomial", P),
            )
        },
    }


# One bounded cache for unique frozen/terminal workspaces, not every physical probe.
# Reports refer to these content identities instead of duplicating rational tables.
WORKSPACES = {}


def _read_json(path):
    return json.loads(Path(path).read_text())


def _same(left, right):
    return len(left) == len(right) and struct.pack(
        "<" + str(len(left)) + "d", *left
    ) == struct.pack("<" + str(len(right)) + "d", *right)


def _rows(path, width, code="d", offset=0):
    """Yield one fixed-width row, using bounded buffered reads rather than mmap RSS."""
    size = struct.calcsize("<" + str(width) + code)
    with Path(path).open("rb") as stream:
        stream.seek(offset)
        while True:
            data = stream.read(size)
            if not data:
                break
            require(len(data) == size, "truncated stream: " + Path(path).name)
            yield struct.unpack("<" + str(width) + code, data)


def file_sha(path):
    path = Path(path)
    before = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    after = path.stat()
    require(
        tuple(
            getattr(before, k)
            for k in ("st_size", "st_mtime_ns", "st_ctime_ns", "st_ino", "st_dev")
        )
        == tuple(
            getattr(after, k)
            for k in ("st_size", "st_mtime_ns", "st_ctime_ns", "st_ino", "st_dev")
        ),
        "file changed during streamed hash",
    )
    return digest.hexdigest(), after.st_size


def _inventory(root, entries, exact=None):
    require(isinstance(entries, dict), "missing file inventory")
    if exact is not None:
        require(set(entries) == set(exact), "file inventory membership differs")
    for name, entry in entries.items():
        actual, size = file_sha(safe(root, name))
        require(
            actual == (entry["sha256"] if isinstance(entry, dict) else entry),
            "artifact identity differs: " + name,
        )
        if isinstance(entry, dict) and "bytes" in entry:
            require(size == entry["bytes"], "file extent differs")


def _context(root):
    root = Path(root).resolve()
    prepared = _read_json(root / "prepared.json")
    require(
        prepared.get("protocol_sha256") == PROTOCOL_SHA256
        and prepared.get("schema") == "crucible.phase2d.assembly-prepared.v1"
        and prepared.get("numerical_source") == SOURCE,
        "unrecognized assembly preparation",
    )
    contract_path = root / "assembly_campaign.py"
    if not contract_path.is_file():
        contract_path = HERE / "assembly_campaign.py"
    contract = load_module("_assembly_gate_contract", contract_path)
    contract.validate_prepared(root, prepared)
    require(len(prepared["attempts"]) == 13, "thirteen attempts required")
    return root, prepared, contract


def parse_input(raw):
    require(len(raw) >= 48, "truncated input header")
    header = struct.unpack_from("<8i2d", raw)
    require(
        header[:3] == (0x43524432, 1, N)
        and header[6] in (0, 1)
        and header[3] >= 2
        and header[4] >= 1
        and header[5] >= 1
        and 1 <= header[7] <= N,
        "input header differs",
    )
    nk, nr, nm = header[3:6]
    count = 3 * N + 3 * nk + nr + nm
    require(len(raw) == 48 + count * 8, "input extent differs")
    values = struct.unpack_from("<" + str(count) + "d", raw, 48)
    require(all(math.isfinite(v) for v in values), "nonfinite input")
    z, a, y = values[:N], values[N : 2 * N], values[2 * N : 3 * N]
    require(
        all(v >= 1 and v == int(v) for v in a)
        and all(0 <= v <= m and v == int(v) for v, m in zip(z, a, strict=True))
        and len(set(zip(z, a))) == N,
        "ordered nuclear species invalid",
    )
    cursor = 3 * N
    knots = values[cursor : cursor + nk]
    cursor += nk
    temp = values[cursor : cursor + nk]
    cursor += nk
    rho = values[cursor : cursor + nk]
    cursor += nk
    outputs = values[cursor : cursor + nr]
    cursor += nr
    mesh = values[cursor:]
    require(
        all(b > a for a, b in zip(knots, knots[1:]))
        and knots[0] == 0
        and knots[-1] >= 0.01,
        "forcing coverage differs",
    )
    require(
        all(0.01 <= v <= 100 for v in temp) and all(v > 0 for v in rho),
        "forcing domain differs",
    )
    require(
        all(b > a for a, b in zip(outputs, outputs[1:]))
        and all(b > a for a, b in zip(mesh, mesh[1:])),
        "input grids differ",
    )
    require(
        tuple(header[8:]) in ((1e-13, 1e-11), (1e-14, 1e-12)),
        "nonlinear controls differ",
    )
    return {
        "header": header,
        "Z": z,
        "A": a,
        "Y0": y,
        "knots": knots,
        "T9": temp,
        "rho": rho,
        "outputs": outputs,
        "mesh": mesh,
        "coordinate": header[7] - 1,
        "controls": header[8:],
    }


def forcing(data, time):
    knots = data["knots"]
    require(
        math.isfinite(time) and knots[0] <= time <= knots[-1],
        "forcing query outside coverage",
    )
    right = next(i for i, t in enumerate(knots) if t >= time)
    if knots[right] == time:
        return data["T9"][right], data["rho"][right]
    fraction = (time - knots[right - 1]) / (knots[right] - knots[right - 1])
    return tuple(
        q[right - 1] + fraction * (q[right] - q[right - 1])
        for q in (data["T9"], data["rho"])
    )


def domain(y, temp, rho, z, a):
    require(
        all(math.isfinite(v) and 0 <= v <= 1 for v in y), "composition domain differs"
    )
    B = math.fsum(m * v for m, v in zip(a, y, strict=True))
    Qc = math.fsum(m * v for m, v in zip(z, y, strict=True))
    require(
        B > 0
        and Qc > 0
        and math.fsum(y) > 0
        and math.isfinite(rho)
        and rho > 0
        and 0.01 <= temp <= 100,
        "moment/condition domain differs",
    )
    Ye = Qc / B
    require(
        1 <= math.log10(rho * Ye) < 11
        and 1e3 <= temp * 1e9 <= 1e13
        and 1e-12 <= rho * Ye <= 1e15,
        "EOS/table domain differs",
    )
    return B, Qc, Ye


def _kind(raw):
    require(
        len(raw) == 32
        and struct.unpack("<8i", raw) == (0x4352514B, 1, 2, 113, 128, -16381, 16384, 1),
        "binary128 kind/representation differs",
    )


def parse_original(raw):
    require(
        len(raw) >= 48
        and struct.unpack_from("<12i", raw) == (0x43524442, 1, N, *NC, *NB, 10240),
        "original baseline header differs",
    )
    count = 10 + 2 * N + sum(NC) + sum(NB)
    require(len(raw) == 48 + count * 8 + 10240 * 4, "original baseline extent differs")
    values = struct.unpack_from("<" + str(count) + "d", raw, 48)
    require(all(math.isfinite(v) for v in values), "nonfinite original baseline")
    cursor = 10 + 2 * N
    csect = []
    b = []
    for counts, output in ((NC, csect), (NB, b)):
        for size in counts:
            output.append(values[cursor : cursor + size])
            cursor += size
    return {
        "values": values,
        "call": int(values[0]),
        "conditions": values[1:4],
        "Y": values[10:170],
        "F": values[170:330],
        "csect": csect,
        "b": b,
        "branches": raw[48 + count * 8 :],
        "comparison": raw[:48] + raw[56:],
    }


def parse_workspace(raw):
    require(len(raw) == 36 + 490 * 8 + NQ * 16, "assembly workspace extent differs")
    require(
        struct.unpack_from("<9i", raw) == (0x43524157, 1, N, *NB, NQ, 1),
        "assembly workspace header/math status differs",
    )
    values = struct.unpack_from("<490d", raw, 36)
    require(all(math.isfinite(v) for v in values), "nonfinite assembly workspace")
    offset = 36 + 490 * 8
    blocks = {}
    for key, count in (
        ("total", N),
        ("classes", 4 * N),
        ("products", sum(NB)),
        ("running", sum(NB)),
        ("absolute", N),
    ):
        blocks[key] = raw[offset : offset + 16 * count]
        offset += 16 * count
    return {
        "values": values,
        "call": int(values[0]),
        "conditions": values[1:4],
        "Y": values[10:170],
        "original": values[170:330],
        "variant": values[330:490],
        "quad": blocks,
        "comparison": raw[:36] + raw[44:],
    }


class Evaluations:
    """One bounded random-access reader for retained 496-value records."""

    def __init__(self, path):
        self.file = Path(path).open("rb")
        try:
            header = self.file.read(32)
            require(
                len(header) == 32
                and struct.unpack("<8i", header) == (0x43524145, 1, N, 496, 0, 0, 0, 0),
                "assembly evaluation header differs",
            )
            size = Path(path).stat().st_size - 32
            require(
                size >= 0 and size % (496 * 8) == 0,
                "assembly evaluation extent differs",
            )
            self.count = size // (496 * 8)
        except BaseException:
            self.file.close()
            raise

    def row(self, call):
        require(
            type(call) is int and 1 <= call <= self.count,
            "physical call ID outside stream",
        )
        self.file.seek(32 + (call - 1) * 496 * 8)
        return struct.unpack("<496d", self.file.read(496 * 8))

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def _echo(row, conditions, y, variant=None, original=None, role=None, context=None):
    require(
        _same(row[3:6], conditions) and _same(row[16:176], y),
        "physical input binding differs",
    )
    if variant is not None:
        require(_same(row[336:496], variant), "variant F binding differs")
    if original is not None:
        require(_same(row[176:336], original), "original F binding differs")
    if role is not None:
        require(row[1] == role, "physical role differs")
    if context is not None:
        require(row[2] == context, "physical context differs")


def _workspace_check(work, assembly_name, original_name, static, evaluations):
    new_raw = (work / assembly_name).read_bytes()
    old_raw = (work / original_name).read_bytes()
    new, old = parse_workspace(new_raw), parse_original(old_raw)
    require(
        _same(new["values"][:330], old["values"][:330]),
        "paired workspace does not describe one evaluation",
    )
    require(
        new["call"] >= 1 and new["values"][0] == new["call"],
        "noninteger workspace call",
    )
    row = evaluations.row(new["call"])
    _echo(row, new["conditions"], new["Y"], new["variant"], new["original"])
    require(
        _same(row[6:12], new["values"][4:10]),
        "workspace EOS/moments differ from physical record",
    )
    key = sha(
        static["map_bytes"] + static["species"] + old["comparison"] + new["comparison"]
    )
    if key not in WORKSPACES:
        groups = [
            {**g, "csect": c, "b": b}
            for g, c, b in zip(static["groups"], old["csect"], old["b"], strict=True)
        ]
        WORKSPACES[key] = verify_workspace(
            groups,
            static["input"]["A"],
            new["Y"],
            new["original"],
            new["variant"],
            new["quad"],
        )
    require(WORKSPACES[key]["pass"], "ordered quad assembly arithmetic gate failed")
    return {"workspace": key, "pass": True, "call": new["call"]}, new, old


def _inspect(root, spec, result, allow_failure=False):
    root, prepared, contract = _context(root)
    require(spec in prepared["attempts"], "undeclared attempt")
    work = root / "attempts" / spec["name"]
    record = _read_json(work / "attempt.json")
    require(
        all(result.get(k) == v for k, v in record.items()),
        "campaign/attempt record differs",
    )
    inventory = [
        str(p.relative_to(work))
        for p in work.rglob("*")
        if p.is_file() and p.name not in ("attempt.json", "attempt.pending")
    ]
    _inventory(work, record["files"], exact=inventory)
    terminal = (work / "status.txt").read_text().splitlines()[-1:]
    ordinary = terminal == ["FAILURE first native step failed"] and allow_failure
    require(
        record.get("completed") is True
        and (
            (record.get("returncode") == 0 and terminal == ["SUCCESS"])
            or (
                ordinary
                and type(record.get("returncode")) is int
                and record["returncode"] > 0
            )
        ),
        "incomplete/fatal native status",
    )
    require(
        record["executable_sha256"]
        == sha((root / "bundle/trajectory_driver").read_bytes()),
        "native executable differs",
    )
    raw = checked(root, spec["input"], spec["input_sha256"])
    require((work / "input.bin").read_bytes() == raw, "attempt input differs")
    parsed = parse_input(raw)
    require(parsed["header"][6] == spec["mode"], "attempt mode differs")
    species = (work / "species.bin").read_bytes()
    maps = (work / "used-maps.bin").read_bytes()
    require(species == raw[48 : 48 + 2 * N * 8], "ordered species echo differs")
    expected = legacy_reference.expected_maps(
        (root / "bundle/network/nets3").read_bytes(),
        (root / "bundle/network/nets4").read_bytes(),
    )
    require(maps == expected, "static mappings differ from pinned network")
    groups = legacy_reference.parse_maps(maps)
    _kind((work / "assembly-kind.bin").read_bytes())
    counters = _read_json(work / "counters.json")
    assembly_counts = _read_json(work / "assembly-counters.json")
    require(
        set(counters) == set(COUNTERS)
        and all(type(v) is int and v >= 0 for v in counters.values()),
        "legacy counters differ",
    )
    require(
        set(assembly_counts) == {"schema", "fresh_requests", "rhs", "assembly_calls"}
        and assembly_counts["schema"] == "crucible.assembly-counters.v1"
        and all(
            type(assembly_counts[k]) is int and assembly_counts[k] >= 0
            for k in ("fresh_requests", "rhs", "assembly_calls")
        ),
        "assembly counters differ",
    )
    require(
        assembly_counts["rhs"] == assembly_counts["assembly_calls"] == counters["rhs"]
        and counters["rhs"] <= assembly_counts["fresh_requests"] <= MAX_CALLS,
        "guarded/physical call scope differs",
    )
    static = {"input": parsed, "species": species, "map_bytes": maps, "groups": groups}
    return root, prepared, work, record, static, counters, assembly_counts, ordinary


def _check_streams(work, static, counters, assembly_counts):
    """Stream all physical/IEEE/branch evidence; retain one branch-equality byte/call."""
    signature = [0] * 10240
    baseline = None
    branch_iter = iter(_rows(work / "branch-events.bin", 5))
    event = next(branch_iter, None)
    ieee = iter(_rows(work / "diagnostic-ieee.bin", 11, "q"))
    original = iter(_rows(work / "diagnostic-evaluations.bin", 324))
    data = static["input"]
    branch_same = bytearray(counters["rhs"] + 1)
    workspace_hash = {}
    ids = set()
    for path in work.glob("assembly-*.bin"):
        if path.name.startswith("assembly-baseline-") or path.name in (
            "assembly-accepted.bin",
            "assembly-failure.bin",
        ):
            with path.open("rb") as file:
                prefix = file.read(44)
            if len(prefix) == 44:
                call = struct.unpack_from("<d", prefix, 36)[0]
                if math.isfinite(call) and call == int(call):
                    ids.add(int(call))
    flag_path = work / "assembly-ieee.bin"
    with flag_path.open("rb") as file:
        header = file.read(16)
    require(
        len(header) == 16 and struct.unpack("<4i", header) == (0x43524149, 1, 21, 0),
        "module IEEE header differs",
    )
    flags = iter(_rows(flag_path, 21, "q", 16))
    with Evaluations(work / "assembly-evaluations.bin") as stream:
        require(
            stream.count == counters["rhs"] and stream.count >= 1,
            "physical evaluation count differs",
        )
        for call in range(1, stream.count + 1):
            row = stream.row(call)
            require(
                all(math.isfinite(v) for v in row)
                and row[0] == call
                and row[1] in range(1, 11)
                and row[2] >= 0
                and row[2] == int(row[2]),
                "nonfinite/unknown physical metadata",
            )
            require(
                row[12:16] == (1.0, 1.0, 1.0, 1.0),
                "assembly rounding/gradual mode differs",
            )
            require(_same(row[4:6], forcing(data, row[3])), "physical forcing differs")
            domain(row[16:176], row[4], row[5], data["Z"], data["A"])
            old = next(original, None)
            mode = next(ieee, None)
            flag = next(flags, None)
            require(
                old is not None and _same(old, (row[0], *row[3:6], *row[16:336])),
                "original/variant stream association differs",
            )
            require(
                mode is not None
                and mode[:6] == (call, 1, 1, 1, 1, 1)
                and mode[6:9] == (0, 0, 0)
                and all(v in (0, 1) for v in mode[9:]),
                "original IEEE evidence differs",
            )
            require(
                flag is not None
                and flag[0] == call
                and all(v in (0, 1) for v in flag[1:])
                and all(
                    flag[start : start + 3] == (0, 0, 0) for start in (1, 6, 11, 16)
                ),
                "module/kernel exceptional arithmetic observed",
            )
            while event is not None and event[0] == call:
                require(
                    event[1] == row[3]
                    and event[2] == int(event[2])
                    and 1 <= event[2] <= 10240
                    and event[3] == int(event[3])
                    and event[4] == int(event[4]),
                    "branch metadata differs",
                )
                index = int(event[2]) - 1
                require(
                    signature[index] == event[3] and event[3] != event[4],
                    "branch transition differs",
                )
                signature[index] = int(event[4])
                event = next(branch_iter, None)
            if row[1] in (1, 3):
                baseline = signature.copy()
            branch_same[call] = int(signature == baseline)
            if row[1] in (6, 9):
                require(branch_same[call], "baseline branch restore differs")
            if call in ids:
                workspace_hash[call] = sha(struct.pack("<10240i", *signature))
        require(
            next(original, None) is None
            and next(ieee, None) is None
            and next(flags, None) is None
            and event is None,
            "unaccounted physical/IEEE/branch rows",
        )
    require(
        all(
            counters[k] == counters["rhs"]
            for k in ("coefficient", "eos", "screening", "weak")
        ),
        "kernel accounting differs",
    )
    return branch_same, workspace_hash


def _identity_files(root, prepared, spec, work, static, evaluations, workspace_hash):
    state = spec["state"]
    reference = prepared["reference_baselines"][state]
    old_expected = parse_original(checked(root, reference["path"], reference["sha256"]))
    for name in ("used-maps.bin", "species.bin"):
        ref = prepared["reference_controls"][state][name]
        require(
            (work / name).read_bytes() == checked(root, ref["path"], ref["sha256"]),
            "D-038 static control differs",
        )
    suffix = spec["arguments"][0]
    repeats = 3 if suffix == "assembly-repeat-3" else 1
    require(
        sorted(p.name for p in work.glob("assembly-baseline-*.bin"))
        == [f"assembly-baseline-{i:03}.bin" for i in range(1, repeats + 1)],
        "assembly baseline population differs",
    )
    require(
        sorted(p.name for p in work.glob("baseline-[0-9]*.bin"))
        == [f"baseline-{i:03}.bin" for i in range(1, repeats + 1)],
        "original baseline population differs",
    )
    links = []
    first = None
    for i in range(1, repeats + 1):
        link, new, old = _workspace_check(
            work,
            f"assembly-baseline-{i:03}.bin",
            f"baseline-{i:03}.bin",
            static,
            evaluations,
        )
        require(
            old["comparison"] == old_expected["comparison"],
            "original frozen workspace differs from D-038",
        )
        require(
            workspace_hash[new["call"]] == sha(old["branches"]),
            "workspace branch signature differs",
        )
        if first is not None:
            require(first == new["comparison"], "variant/quad repeat bits differ")
        first = new["comparison"]
        links.append(link)
    return links


def _failure(exc):
    return {
        "pass": False,
        "software_pass": False,
        "fatal": True,
        "ordinary_numerical_failure": False,
        "error": str(exc),
        "trajectory_reference_qualified": False,
    }


def identity_attempt_gate(root, spec, result):
    try:
        root, prepared, work, record, static, counts, requests, _ = _inspect(
            root, spec, result
        )
        require(spec["stage"] == "identity", "not an identity attempt")
        repeats = 3 if spec["arguments"] == ["assembly-repeat-3"] else 1
        require(
            spec["arguments"] in (["assembly-repeat-3"], ["assembly-repeat-1"]),
            "unknown identity command",
        )
        require(
            counts["rhs"] == requests["fresh_requests"] == repeats
            and all(counts[k] == 0 for k in COUNTERS[5:]),
            "identity scope differs",
        )
        _, hashes = _check_streams(work, static, counts, requests)
        with Evaluations(work / "assembly-evaluations.bin") as evaluations:
            require(
                [evaluations.row(i)[1] for i in range(1, repeats + 1)]
                == [1] + [2] * (repeats - 1),
                "identity roles differ",
            )
            links = _identity_files(
                root, prepared, spec, work, static, evaluations, hashes
            )
        return {
            "pass": True,
            "software_pass": True,
            "fatal": False,
            "identity_pass": True,
            "arithmetic_pass": True,
            "workspaces": links,
            "physical_rhs_calls": counts["rhs"],
            "fresh_requests": requests["fresh_requests"],
            "trajectory_reference_qualified": False,
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        return _failure(exc)


def _stage_gate(root, stage, attempt_gate):
    try:
        root, prepared, _ = _context(root)
        planned = [s for s in prepared["attempts"] if s["stage"] == stage]
        require(
            len(planned) == (6 if stage == "identity" else 3),
            "stage population differs",
        )
        outputs = {}
        for spec in planned:
            path = root / "attempts" / spec["name"] / "attempt.json"
            outputs[spec["name"]] = (
                attempt_gate(root, spec, _read_json(path))
                if path.exists()
                else _failure("UNATTEMPTED")
            )
        return {
            "pass": all(v["pass"] for v in outputs.values()),
            "software_pass": all(v["software_pass"] for v in outputs.values()),
            "fatal": any(v["fatal"] for v in outputs.values()),
            "attempts": outputs,
            "trajectory_reference_qualified": False,
        }
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        return _failure(exc)


def identity_gate(root):
    result = _stage_gate(root, "identity", identity_attempt_gate)
    if not result["pass"]:
        return result
    try:
        for state in STATES:
            first = parse_workspace(
                (
                    Path(root)
                    / "attempts"
                    / (state + "-identity-3")
                    / "assembly-baseline-001.bin"
                ).read_bytes()
            )
            fresh = parse_workspace(
                (
                    Path(root)
                    / "attempts"
                    / (state + "-identity-1")
                    / "assembly-baseline-001.bin"
                ).read_bytes()
            )
            require(
                first["comparison"] == fresh["comparison"],
                "fresh-process variant/quad repeat differs",
            )
        result["variant_repeatability_pass"] = True
        return result
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        return {**result, **_failure(exc)}


def precision_values_gate(folder):
    folder = Path(folder)
    _kind((folder / "assembly-kind.bin").read_bytes())
    data = (folder / "precision-values.bin").read_bytes()
    require(
        len(data) == 16 + 10 * 32
        and struct.unpack_from("<4i", data) == (0x43525150, 1, 10, 0),
        "promotion fixture extent/header differs",
    )
    originals = (
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
    for i, expected in enumerate(originals):
        offset = 16 + 32 * i
        original = struct.unpack_from("<Q", data, offset)[0]
        returned = struct.unpack_from("<Q", data, offset + 24)[0]
        quad = decode_binary128(data[offset + 8 : offset + 24])[0]
        value = struct.unpack("<d", struct.pack("<Q", expected))[0]
        require(
            original == returned == expected
            and quad["value"] == Q(value)
            and quad["bits"]
            == round_binary128_bits(Q(value), bool(value == 0 and expected >> 63)),
            "exact promotion/subnormal/signed-zero fixture failed",
        )
    data = (folder / "rounding-values.bin").read_bytes()
    require(
        len(data) == 16 + 8 * 32
        and struct.unpack_from("<4i", data) == (0x43525154, 1, 8, 0),
        "rounding fixture extent/header differs",
    )
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
    for i, (value, expected) in enumerate(cases):
        offset = 16 + 32 * i
        quad = decode_binary128(data[offset : offset + 16])[0]
        actual, declared = struct.unpack_from("<2Q", data, offset + 16)
        require(
            quad["value"] == value
            and actual == declared == expected == round_binary64_bits(value),
            "nearest-even fixture failed",
        )
    return {
        "pass": True,
        "software_pass": True,
        "kind": [2, 113, 128, -16381, 16384],
        "promotions": 10,
        "ties": 8,
        "trajectory_reference_qualified": False,
    }


def precision_gate(root):
    try:
        root, _, contract = _context(root)
        saved = _read_json(root / "synthetic.json")
        expected = {
            (executable, name)
            for executable, name in (
                [
                    ("trajectory_synthetic", n)
                    for n in (
                        "polynomial",
                        "nonlinear",
                        "boundary",
                        "projection",
                        "failed-lu",
                        "nonfinite",
                        "retry-snapshot",
                    )
                ]
                + [
                    ("forcing_synthetic", n)
                    for n in ("forcing", "outside", "nonfinite", "nonincreasing")
                ]
                + [
                    ("assembly_synthetic", n)
                    for n in (
                        "precision",
                        "arithmetic",
                        "malformed",
                        "nonfinite",
                        "overflow",
                    )
                ]
            )
        }
        require(
            saved.get("pass") is True
            and {(r["executable"], r["name"]) for r in saved["scenarios"]} == expected
            and len(saved["scenarios"]) == 16
            and all(r.get("pass") is True for r in saved["scenarios"]),
            "compiled prerequisite population/result differs",
        )
        _inventory(root, saved["files"])
        for record in saved["scenarios"]:
            require(
                record["executable_sha256"]
                == sha((root / "bundle" / record["executable"]).read_bytes()),
                "fixture executable differs",
            )
        return precision_values_gate(root / "synthetic/assembly_synthetic-precision")
    except (OSError, ValueError, KeyError, IndexError, TypeError, struct.error) as exc:
        return _failure(exc)


EPS, NORMAL = 2.0**-52, 2.0**-1022
MULTIPLIERS = (1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6)


def _close(actual, expected, magnitude, amplification=1.0):
    require(
        len(actual) == len(expected) == len(magnitude), "recomputation shape differs"
    )
    for observed, reference, scale in zip(actual, expected, magnitude, strict=True):
        bound = 512 * EPS * scale + 32 * NORMAL * amplification
        require(
            all(math.isfinite(v) for v in (observed, reference, bound))
            and abs(observed - reference) <= bound,
            "retained arithmetic recomputation differs",
        )


def _difference(f0, f1, f2, d1, d2):
    intermediates = (d1, d2, d1 - d2, d1 * (d1 - d2), d2 * (d2 - d1))
    require(
        all(math.isfinite(v) and abs(v) >= NORMAL for v in intermediates),
        "unsupported finite-difference weights",
    )
    w1, w2 = -d2 / intermediates[3], -d1 / intermediates[4]
    require(
        all(math.isfinite(v) and abs(v) >= NORMAL for v in (w1, w2)),
        "unsupported finite-difference weights",
    )
    values = []
    bounds = []
    for a, b, c in zip(f0, f1, f2, strict=True):
        t1, t2 = w1 * (b - a), w2 * (c - a)
        value = t1 + t2
        bound = 512 * EPS * (abs(t1) + abs(t2)) + 32 * NORMAL * (abs(w1) + abs(w2) + 1)
        require(
            math.isfinite(value) and math.isfinite(bound),
            "unsupported quotient arithmetic",
        )
        values.append(value)
        bounds.append(bound)
    return values, bounds


class GroupedRows:
    """One lookahead row for sequential Jacobian-ID groups in a retained stream."""

    def __init__(self, path, width):
        self.iterator = iter(_rows(path, width))
        self.current = next(self.iterator, None)

    def group(self, identifier):
        require(
            self.current is None or self.current[0] >= identifier,
            "out-of-order Jacobian record",
        )
        output = []
        while self.current is not None and self.current[0] == identifier:
            output.append(self.current)
            self.current = next(self.iterator, None)
        return output

    def finish(self):
        require(self.current is None, "undeclared trailing Jacobian records")


def _fd_block(
    matrix,
    jid,
    conditions,
    y,
    f0,
    base_call,
    restore_call,
    selected,
    attempts,
    evaluations,
    branch_same,
    A,
):
    """Verify one factor-one matrix using actual offsets and retained variant-F IDs."""
    require(
        len(matrix) == N * N
        and len(selected) <= N
        and len({r[1] for r in selected}) == len(selected),
        "selected column population differs",
    )
    require(
        all(
            r[0] == jid and r[1] == int(r[1]) and 1 <= r[1] <= N
            for r in (*selected, *attempts)
        ),
        "Jacobian/column identifier differs",
    )
    base = evaluations.row(base_call)
    restore = evaluations.row(restore_call)
    _echo(base, conditions, y, f0, role=3, context=jid)
    _echo(restore, conditions, y, f0, role=6, context=jid)
    require(_same(base[3:], restore[3:]), "baseline/restore workspace differs")
    cursor = base_call + 1
    complete = True
    request_count = 0
    for column in range(1, N + 1):
        probes = [p for p in attempts if p[1] == column]
        chosen = [s for s in selected if s[1] == column]
        require(0 < len(probes) <= 27, "missing/excess column attempts")
        nominal = EPS ** (1 / 3) * max(abs(y[column - 1]), 1e-8 / A[column - 1])
        if y[column - 1] + nominal == y[column - 1]:
            nominal = math.nextafter(y[column - 1], math.inf) - y[column - 1]
        order = []
        for probe in probes:
            require(
                all(math.isfinite(v) for v in probe)
                and probe[2] in (0, 1, -1)
                and probe[3] > 0
                and all(v in (0, 1) for v in probe[8:10]),
                "invalid probe metadata",
            )
            reduction = round(math.log2(nominal / probe[3]))
            require(0 <= reduction <= 8, "undeclared halving")
            _close([probe[3]], [nominal / 2**reduction], [nominal / 2**reduction])
            order.append((reduction, int(probe[2])))
            delta = probe[3]
            pair = (
                (-delta, delta)
                if probe[2] == 0
                else ((delta, 2 * delta) if probe[2] == 1 else (-delta, -2 * delta))
            )
            require(
                _same(probe[6:8], tuple(y[column - 1] + v for v in pair)),
                "probe does not match stencil",
            )
            representable = probe[4] != 0 and probe[5] != 0 and probe[4] != probe[5]
            if representable:
                request_count += 2
            for side in range(2):
                call = probe[10 + side]
                require(
                    call == int(call)
                    and call >= 0
                    and (not probe[8 + side] or call > 0),
                    "invalid probe call ID",
                )
                if call:
                    require(
                        representable and int(call) == cursor and cursor < restore_call,
                        "probe call order differs",
                    )
                    state = list(y)
                    state[column - 1] = probe[6 + side]
                    require(
                        state[column - 1] - y[column - 1] == probe[4 + side],
                        "representable probe offset differs",
                    )
                    _echo(
                        evaluations.row(cursor),
                        conditions,
                        state,
                        role=4 + side,
                        context=jid,
                    )
                    require(
                        bool(probe[8 + side]) == bool(branch_same[cursor]),
                        "probe branch predicate differs",
                    )
                    cursor += 1
        expected = []
        for reduction in range(9):
            delta = nominal / 2**reduction
            expected.extend(
                (reduction, stencil)
                for stencil in (0, 1, -1)
                if stencil != -1 or y[column - 1] + 2 * delta > 1
            )
        require(order == expected[: len(order)], "probe preference/order differs")
        actual = matrix[(column - 1) * N : column * N]
        finite = all(math.isfinite(v) for v in actual)
        require(
            finite or all(math.isnan(v) for v in actual),
            "partially nonfinite Jacobian column",
        )
        require(bool(chosen) == finite, "column availability differs")
        if not finite:
            require(order == expected, "incomplete column missing declared attempts")
            complete = False
            continue
        selection = chosen[0]
        probe = probes[-1]
        require(
            selection[2] == probe[2]
            and selection[3] == order[-1][0]
            and _same(selection[4:6], probe[4:6])
            and probe[8:10] == (1.0, 1.0),
            "selected column/probe differs",
        )
        p1 = evaluations.row(int(probe[10]))[336:496]
        p2 = evaluations.row(int(probe[11]))[336:496]
        reference, bounds = _difference(f0, p1, p2, selection[4], selection[5])
        require(
            all(
                abs(a - b) <= bound
                for a, b, bound in zip(actual, reference, bounds, strict=True)
            ),
            "variant Jacobian recomputation differs",
        )
    require(cursor == restore_call, "unaccounted Jacobian physical call")
    return {
        "complete": complete,
        "selected_columns": len(selected),
        "probe_attempts": len(attempts),
        "probe_requests": request_count,
        "base_call": base_call,
        "restore_call": restore_call,
    }


def _directional(
    work, matrix, complete, base, evaluations, cursor, branch_same, A, coordinate
):
    rows = list(_rows(work / "directional.bin", 1286))
    attempts = list(_rows(work / "direction-attempts.bin", 327))
    jv_rows = list(_rows(work / "diagnostic-jv.bin", N * 3 * 4))
    require(len(rows) == 27 and len(jv_rows) == 1, "direction/Jv stream extent differs")
    saved = jv_rows[0]
    require(
        all(
            math.isnan(saved[i])
            for factor in (0, 2, 3)
            for i in range(factor * N * 3, (factor + 1) * N * 3)
        ),
        "undeclared factor sweep result",
    )
    scale = [max(abs(y), 1e-8 / m) for y, m in zip(base["Y"], A, strict=True)]
    require(all(NORMAL <= v <= 1 for v in scale), "unsupported direction scale")
    directions = [
        scale,
        [v if i % 2 == 0 else 0.0 for i, v in enumerate(scale)],
        [v if i == coordinate else 0.0 for i, v in enumerate(scale)],
    ]
    agreements = []
    attempt_cursor = 0
    for direction, v in enumerate(directions, 1):
        jv = saved[N * 3 + (direction - 1) * N : N * 3 + direction * N]
        if complete:
            calculated = [
                sum(matrix[i + N * j] * v[j] for j in range(N)) for i in range(N)
            ]
            magnitude = [
                sum(abs(matrix[i + N * j] * v[j]) for j in range(N)) for i in range(N)
            ]
            _close(jv, calculated, magnitude, N)
        else:
            require(
                all(math.isnan(q) for q in jv), "incomplete matrix has available Jv"
            )
        estimates = []
        admissible = []
        for mi, multiplier in enumerate(MULTIPLIERS, 1):
            row = rows[(direction - 1) * 9 + mi - 1]
            require(
                row[:2] == (direction, mi) and row[3] in (0, 1),
                "direction sweep order/flag differs",
            )
            require(
                _same(row[6:166], v)
                and _same(row[166:326], jv)
                and _same(row[806:966], base["F"]),
                "direction/baseline/Jv binding differs",
            )
            own = []
            while attempt_cursor < len(attempts) and attempts[attempt_cursor][:2] == (
                direction,
                mi,
            ):
                own.append(attempts[attempt_cursor])
                attempt_cursor += 1
            require(
                1 <= len(own) <= 3 and [r[2] for r in own] == [0, 1, -1][: len(own)],
                "direction stencil order differs",
            )
            last = [None, None]
            for attempt in own:
                stencil = attempt[2]
                h = (
                    (-multiplier, multiplier)
                    if stencil == 0
                    else (
                        (multiplier, 2 * multiplier)
                        if stencil == 1
                        else (-multiplier, -2 * multiplier)
                    )
                )
                require(
                    _same(attempt[3:5], h) and all(v in (0, 1) for v in attempt[5:7]),
                    "direction multiplier/flags differ",
                )
                for side in range(2):
                    state = attempt[7 + side * N : 7 + (side + 1) * N]
                    expected = [
                        y + h[side] * delta
                        for y, delta in zip(base["Y"], v, strict=True)
                    ]
                    _close(
                        state,
                        expected,
                        [
                            abs(y) + abs(h[side] * delta)
                            for y, delta in zip(base["Y"], v, strict=True)
                        ],
                    )
                    candidate = (
                        evaluations.row(cursor) if cursor <= evaluations.count else None
                    )
                    context = 100 * direction + 10 * mi + int(stencil) + 1
                    matches = (
                        candidate is not None
                        and candidate[1:3] == (7 + side, context)
                        and _same(candidate[16:176], state)
                    )
                    require(
                        not attempt[5 + side] or matches,
                        "admissible directional probe missing F",
                    )
                    last[side] = candidate[336:496] if matches else None
                    if matches:
                        _echo(
                            candidate,
                            base["conditions"],
                            state,
                            role=7 + side,
                            context=context,
                        )
                        require(
                            bool(attempt[5 + side]) == bool(branch_same[cursor]),
                            "direction branch predicate differs",
                        )
                        cursor += 1
                require(
                    attempt is own[-1] or attempt[5:7] != (1.0, 1.0),
                    "direction continued after admissible stencil",
                )
            valid = own[-1][5:7] == (1.0, 1.0)
            require(
                bool(row[3]) == valid
                and row[2] == own[-1][2]
                and _same(row[4:6], own[-1][3:5]),
                "selected directional record differs",
            )
            admissible.append(valid)
            if valid:
                require(
                    _same(row[966:1126], last[0]) and _same(row[1126:1286], last[1]),
                    "direction F binding differs",
                )
                for side in range(2):
                    state = own[-1][7 + side * N : 7 + (side + 1) * N]
                    expected = [p - y for p, y in zip(state, base["Y"], strict=True)]
                    _close(
                        row[486 + side * N : 646 + side * N],
                        expected,
                        [
                            abs(p) + abs(y)
                            for p, y in zip(state, base["Y"], strict=True)
                        ],
                    )
                estimate, bounds = _difference(
                    base["F"], last[0], last[1], row[4], row[5]
                )
                require(
                    all(
                        abs(a - b) <= e
                        for a, b, e in zip(row[326:486], estimate, bounds, strict=True)
                    ),
                    "direction quotient differs",
                )
                estimates.append(estimate)
            else:
                require(
                    len(own) == 3
                    and all(math.isnan(x) for x in (*row[326:806], *row[966:])),
                    "refused direction lacks unavailable masks",
                )
                estimates.append(None)
        production = []
        for valid, dv in zip(admissible, estimates, strict=True):
            production.append(
                bool(
                    complete
                    and valid
                    and all(
                        abs(m * (j - d)) <= 1e-7 + 1e-3 * max(abs(m * j), abs(m * d))
                        for m, j, d in zip(A, jv, dv, strict=True)
                    )
                )
            )
        windows = []
        for i in range(8):
            agree = production[i] and production[i + 1]
            if agree:
                agree = all(
                    abs(m * (x - y)) <= 1e-7 + 1e-3 * max(abs(m * x), abs(m * y))
                    for m, x, y in zip(A, estimates[i], estimates[i + 1], strict=True)
                )
            windows.append(bool(agree))
        agreements.append(
            {
                "pass": any(windows),
                "admissible": admissible,
                "production_agreement": production,
                "stable_windows": windows,
            }
        )
    require(attempt_cursor == len(attempts), "undeclared directional attempts")
    _echo(evaluations.row(cursor), base["conditions"], base["Y"], base["F"], role=9)
    return {
        "pass": all(r["pass"] for r in agreements),
        "directions": agreements,
        "probe_requests": 2 * len(attempts),
        "next_call": cursor + 1,
    }


def derivative_attempt_gate(root, spec, result):
    try:
        root, prepared, work, record, static, counts, requests, _ = _inspect(
            root, spec, result
        )
        require(
            spec["stage"] == "derivative"
            and spec["arguments"] == ["assembly-diagnose"],
            "not the fixed derivative command",
        )
        require(
            counts["jacobian"] == 1
            and all(
                counts[k] == 0
                for k in (
                    "lu",
                    "linear_solve",
                    "newton",
                    "retry",
                    "step_attempt",
                    "projection",
                    "accepted",
                )
            ),
            "derivative scope differs",
        )
        require(
            not list(work.glob("linear-factor-*.bin"))
            and not (work / "candidate.bin").exists()
            and not (work / "fixed-b-jacobian.bin").exists(),
            "undeclared derivative work",
        )
        same, hashes = _check_streams(work, static, counts, requests)
        matrix_rows = list(_rows(work / "jacobian-factor-1.bin", N * N))
        statuses = list(_rows(work / "matrix-status.bin", 5))
        require(
            len(matrix_rows) == len(statuses) == 1
            and statuses[0][:2] == (1.0, 1.0)
            and statuses[0][2] in (0, 1),
            "factor-one matrix population differs",
        )
        require(
            sorted(p.name for p in work.glob("jacobian-factor-*.bin"))
            == ["jacobian-factor-1.bin"],
            "undeclared FD factor",
        )
        bases = list(_rows(work / "jacobian-bases.bin", 164))
        require(len(bases) == 1 and bases[0][0] == 1, "Jacobian baseline differs")
        selected = list(_rows(work / "fd-columns.bin", 6))
        attempts = list(_rows(work / "fd-probe-attempts.bin", 12))
        with Evaluations(work / "assembly-evaluations.bin") as evaluations:
            links = _identity_files(
                root, prepared, spec, work, static, evaluations, hashes
            )
            variant = parse_workspace((work / "assembly-baseline-001.bin").read_bytes())
            base = {
                "Y": variant["Y"],
                "F": variant["variant"],
                "conditions": variant["conditions"],
            }
            status = statuses[0]
            require(
                status[3] == 1 and status[4] == int(status[4]),
                "Jacobian call bounds differ",
            )
            require(
                _same(bases[0][1:4], base["conditions"])
                and _same(bases[0][4:], base["Y"]),
                "Jacobian frozen state differs",
            )
            fd = _fd_block(
                matrix_rows[0],
                1,
                base["conditions"],
                base["Y"],
                base["F"],
                2,
                int(status[4]),
                selected,
                attempts,
                evaluations,
                same,
                static["input"]["A"],
            )
            require(
                fd["complete"] == bool(status[2]), "matrix completeness flag differs"
            )
            direction = _directional(
                work,
                matrix_rows[0],
                fd["complete"],
                base,
                evaluations,
                int(status[4]) + 1,
                same,
                static["input"]["A"],
                static["input"]["coordinate"],
            )
            require(
                direction["next_call"] == evaluations.count + 1,
                "undeclared derivative physical calls",
            )
        expected_requests = 4 + fd["probe_requests"] + direction["probe_requests"]
        require(
            requests["fresh_requests"] == expected_requests
            and counts["probe"] == expected_requests - 4,
            "derivative request accounting differs",
        )
        return {
            "pass": fd["complete"] and direction["pass"],
            "software_pass": True,
            "fatal": False,
            "workspaces": links,
            "matrix": fd,
            "directional": direction,
            "physical_rhs_calls": counts["rhs"],
            "fresh_requests": requests["fresh_requests"],
            "trajectory_reference_qualified": False,
        }
    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        struct.error,
        ZeroDivisionError,
        OverflowError,
    ) as exc:
        return _failure(exc)


def derivative_gate(root):
    return _stage_gate(root, "derivative", derivative_attempt_gate)


NEWTON_FIELDS = (
    ("old", N),
    ("pre", N),
    ("F_variant", N),
    ("F_original", N),
    ("J", N * N),
    ("M", N * N),
    ("rhs", N),
    ("LU", N * N),
    ("delta", N),
    ("unprojected", N),
    ("post", N),
    ("weights", N),
    ("residual", N),
    ("projection_delta", N),
)


def newton_records(path):
    """Read at most one 0.63 MB forensic phase at a time, never the entire file."""
    with Path(path).open("rb") as stream:
        header = stream.read(32)
        require(
            len(header) == 32
            and struct.unpack("<8i", header) == (0x4352414E, 1, N, 78568, 10, N, 0, 0),
            "Newton header differs",
        )
        size = 80 + 78568 * 8 + N * 4
        while True:
            raw = stream.read(size)
            if not raw:
                break
            require(len(raw) == size, "partial Newton phase record")
            ids = struct.unpack_from("<10q", raw)
            values = struct.unpack_from("<78568d", raw, 80)
            record = {
                "ids": ids,
                "scalars": values[:8],
                "pivots": struct.unpack_from("<160i", raw, 80 + 78568 * 8),
            }
            cursor = 8
            for name, count in NEWTON_FIELDS:
                record[name] = values[cursor : cursor + count]
                cursor += count
            yield record


def _finite(values):
    return all(math.isfinite(v) for v in values)


def _unavailable(values):
    return all(math.isnan(v) for v in values)


def verify_newton_phase(record):
    """Reject unexplained available/unavailable fields without assuming success."""
    ids = record["ids"]
    phase = ids[9]
    scalars = record["scalars"]
    require(
        phase in (1, 2, 3, 4)
        and ids[0] >= 1
        and ids[1] == 1
        and 1 <= ids[2] <= 30
        and ids[3] >= 1
        and ids[4] >= 1
        and ids[5] >= ids[4]
        and _finite((scalars[0], scalars[1], *scalars[5:]))
        and scalars[1] > 0,
        "Newton metadata differs",
    )
    require(
        _finite(
            tuple(
                v
                for name in ("old", "pre", "F_variant", "F_original", "J", "M")
                for v in record[name]
            )
        ),
        "required Newton baseline operands unavailable",
    )
    if phase == 1:
        require(
            ids[6] == 0
            and ids[7:9] == (-999, -999)
            and all(v == 0 for v in record["pivots"])
            and _unavailable(scalars[2:5]),
            "pre-LU metadata availability differs",
        )
    else:
        if phase == 2:
            require(
                _unavailable(scalars[2:5]),
                "post-LU residual/projection unexpectedly available",
            )
        require(
            0 <= ids[7] <= N
            and all(1 <= v <= N for v in record["pivots"])
            and _finite(record["LU"]),
            "LU status/availability differs",
        )
    if phase < 3:
        require(
            ids[6] == 0
            and ids[8] == -999
            and all(
                _unavailable(record[k])
                for k in (
                    "delta",
                    "unprojected",
                    "post",
                    "weights",
                    "residual",
                    "projection_delta",
                )
            ),
            "early Newton fields unexpectedly available",
        )
    if phase == 1:
        require(
            _unavailable(record["rhs"]) and _unavailable(record["LU"]),
            "pre-LU fields unexpectedly available",
        )
    elif ids[7] == 0:
        require(_finite(record["rhs"]), "native RHS unavailable after successful LU")
    if phase >= 3:
        require(
            ids[7:9] == (0, 0)
            and _finite(
                tuple(
                    v
                    for k in ("delta", "unprojected", "post", "projection_delta")
                    for v in record[k]
                )
            )
            and math.isfinite(scalars[4]),
            "post-solve availability/status differs",
        )
    if phase == 3:
        require(
            ids[6] == 0
            and _unavailable(scalars[2:4])
            and _unavailable(record["weights"])
            and _unavailable(record["residual"]),
            "pre-post-F fields unexpectedly available",
        )
    if phase == 4:
        require(
            ids[6] > ids[5]
            and _finite(scalars)
            and _finite(record["weights"])
            and _finite(record["residual"]),
            "final Newton fields unavailable",
        )


def _verify_newton_algebra(record, post_row, A):
    scalars = record["scalars"]
    time, h, norm, l1, projection, cumulative, an, rn = scalars
    require(
        (an, rn) in ((1e-13, 1e-11), (1e-14, 1e-12)) and cumulative == 0,
        "Newton nonlinear controls/cumulative scope differs",
    )
    pre, old = record["pre"], record["old"]
    expected = [p + d for p, d in zip(pre, record["delta"], strict=True)]
    _close(
        record["unprojected"],
        expected,
        [abs(p) + abs(d) for p, d in zip(pre, record["delta"], strict=True)],
    )
    projected = tuple(0.0 if v < 0 else v for v in record["unprojected"])
    require(_same(record["post"], projected), "unrecorded projection/repair")
    delta = [p - u for p, u in zip(projected, record["unprojected"], strict=True)]
    _close(
        record["projection_delta"],
        delta,
        [
            abs(p) + abs(u)
            for p, u in zip(projected, record["unprojected"], strict=True)
        ],
    )
    projection_recomputed = sum(m * abs(d) for m, d in zip(A, delta, strict=True))
    _close([projection], [projection_recomputed], [projection_recomputed])
    row = post_row
    _echo(row, row[3:6], projected, role=10, context=record["ids"][0])
    require(row[3] == time, "post-update F time differs")
    expected = [
        p - o - h * f for p, o, f in zip(projected, old, row[336:496], strict=True)
    ]
    _close(
        record["residual"],
        expected,
        [
            abs(p) + abs(o) + abs(h * f)
            for p, o, f in zip(projected, old, row[336:496], strict=True)
        ],
    )
    weights = [
        an + rn * max(abs(m * o), abs(m * p))
        for m, o, p in zip(A, old, projected, strict=True)
    ]
    _close(record["weights"], weights, weights)
    require(all(v > 0 for v in record["weights"]), "nonpositive nonlinear weights")
    normalized = max(
        abs(m * r) / w
        for m, r, w in zip(A, record["residual"], record["weights"], strict=True)
    )
    residual_l1 = sum(abs(m * r) for m, r in zip(A, record["residual"], strict=True))
    _close([norm, l1], [normalized, residual_l1], [abs(normalized), residual_l1])
    return {
        "norm": norm,
        "recomputed_norm": normalized,
        "projection": projection,
        "projection_recomputed": projection_recomputed,
        "negative_iterates": sum(v < 0 for v in record["unprojected"]),
    }


def _step_forensics(work, static, evaluations, same, counts, controls):
    with (work / "native-step-attempts.bin").open("rb") as file:
        header = file.read(16)
    require(
        len(header) == 16 and struct.unpack("<4i", header) == (0x43524154, 1, 7, 0),
        "step attempt header differs",
    )
    attempts = list(_rows(work / "native-step-attempts.bin", 7, offset=16))
    require(
        1 <= len(attempts) <= 10
        and counts["step_attempt"] == len(attempts)
        and counts["retry"] == len(attempts) - 1,
        "native step/retry scope differs",
    )
    data = static["input"]
    A = data["A"]
    old = data["Y0"]
    for i, attempt in enumerate(attempts, 1):
        expected_h = 1e-4 / 2 ** (i - 1)
        require(
            attempt[:2] == (1.0, float(i))
            and _same(attempt[2:4], (expected_h, expected_h))
            and _same(attempt[4:6], forcing(data, expected_h))
            and attempt[6] == int(attempt[6]),
            "native retry request/forcing differs",
        )
    selected = GroupedRows(work / "fd-columns.bin", 6)
    probes = GroupedRows(work / "fd-probe-attempts.bin", 12)
    bases = iter(_rows(work / "jacobian-bases.bin", 164))
    legacy = iter(_rows(work / "newton-residuals.bin", 167))
    iterations = []
    index = 0
    phases = {}
    prefix = None
    previous = None
    last = None
    next_call = 2
    requests = 1
    projection_events = 0
    per_attempt = [0] * len(attempts)
    for record in newton_records(work / "assembly-newton.bin"):
        verify_newton_phase(record)
        ids = record["ids"]
        phase = ids[9]
        scalar = record["scalars"]
        if phase == 1:
            require(
                not phases
                and ids[0] == index + 1
                and ids[3] == index + 1
                and ids[4] == next_call,
                "Newton/Jacobian/call order differs",
            )
            index += 1
            prefix = record
            ai = next((i for i, a in enumerate(attempts) if a[3] == scalar[1]), None)
            require(
                ai is not None
                and ids[2] == per_attempt[ai] + 1
                and scalar[0] == scalar[1]
                and _same(record["old"], old)
                and scalar[6:8] == tuple(controls),
                "Newton old/time/control binding differs",
            )
            require(
                ai == 0 or all(v == 30 for v in per_attempt[:ai]),
                "retry before exhausting prior Newton iterations",
            )
            expected_pre = old if ids[2] == 1 else previous["post"]
            require(
                _same(record["pre"], expected_pre),
                "Newton iterate changed without recorded correction",
            )
            if ids[2] == 1:
                require(
                    attempts[ai][6] == next_call - 1, "step entry RHS counter differs"
                )
            per_attempt[ai] += 1
            b = next(bases, None)
            require(
                b is not None
                and b[0] == ids[3]
                and _same(b[1:4], (scalar[0], *forcing(data, scalar[0])))
                and _same(b[4:], record["pre"]),
                "Jacobian baseline record differs",
            )
            condition = b[1:4]
            _echo(
                evaluations.row(ids[5]),
                condition,
                record["pre"],
                record["F_variant"],
                record["F_original"],
                6,
                ids[3],
            )
            fd = _fd_block(
                record["J"],
                ids[3],
                condition,
                record["pre"],
                record["F_variant"],
                ids[4],
                ids[5],
                selected.group(ids[3]),
                probes.group(ids[3]),
                evaluations,
                same,
                A,
            )
            require(fd["complete"], "first-step has incomplete Jacobian")
            requests += 2 + fd["probe_requests"]
            matrix = [-v for v in record["J"]]
            for i in range(N):
                matrix[i + N * i] += 1 / scalar[1]
            magnitude = [
                abs(v) + (1 / scalar[1] if j // N == j % N else 0.0)
                for j, v in enumerate(record["J"])
            ]
            _close(record["M"], matrix, magnitude)
        else:
            require(
                prefix is not None
                and ids[:6] == prefix["ids"][:6]
                and phase == len(phases) + 1
                and _same(record["scalars"][:2], prefix["scalars"][:2])
                and _same(record["scalars"][5:], prefix["scalars"][5:])
                and all(
                    _same(record[k], prefix[k])
                    for k in ("old", "pre", "F_variant", "F_original", "J", "M")
                ),
                "Newton phase baseline/matrix changed",
            )
        phases[phase] = record
        if phase >= 2:
            require(ids[7] == 0, "nonzero LAPACK factorization info")
            expected_rhs = [
                (o - p) / scalar[1] + f
                for o, p, f in zip(old, record["pre"], record["F_variant"], strict=True)
            ]
            _close(
                record["rhs"],
                expected_rhs,
                [
                    abs((o - p) / scalar[1]) + abs(f)
                    for o, p, f in zip(
                        old, record["pre"], record["F_variant"], strict=True
                    )
                ],
                1 + 1 / scalar[1],
            )
            if phase > 2:
                require(
                    _same(record["rhs"], phases[2]["rhs"])
                    and _same(record["LU"], phases[2]["LU"])
                    and record["pivots"] == phases[2]["pivots"],
                    "Newton LU/RHS/pivots changed",
                )
        if phase == 4:
            require(
                ids[6] == ids[5] + 1,
                "unaccounted call between Jacobian and post-update F",
            )
            post = evaluations.row(ids[6])
            _echo(
                post,
                (scalar[0], *forcing(data, scalar[0])),
                record["post"],
                role=10,
                context=ids[0],
            )
            algebra = _verify_newton_algebra(record, post, A)
            expected_legacy = (
                float(ids[1]),
                float(ids[2]),
                scalar[0],
                scalar[1],
                *record["residual"],
                scalar[2],
                scalar[3],
                scalar[4],
            )
            actual = next(legacy, None)
            require(
                actual is not None and _same(actual, expected_legacy),
                "legacy/four-phase residual correspondence differs",
            )
            if last is not None:
                require(
                    last["scalars"][2] > 1,
                    "solver continued after a converged residual",
                )
            projection_events += algebra["negative_iterates"]
            requests += 1
            next_call = ids[6] + 1
            iterations.append(
                {
                    "newton": ids[0],
                    "jacobian": ids[3],
                    "iteration": ids[2],
                    "time": scalar[0],
                    "h": scalar[1],
                    "baseline_call": ids[4],
                    "restore_call": ids[5],
                    "post_call": ids[6],
                    **algebra,
                }
            )
            previous = record
            last = record
            phases = {}
            prefix = None
    require(
        not phases
        and last is not None
        and index
        == counts["newton"]
        == counts["jacobian"]
        == counts["lu"]
        == counts["linear_solve"]
        and index <= 300
        and counts["projection"] == projection_events,
        "Newton phase/scope accounting differs",
    )
    require(
        all(v > 0 for v in per_attempt)
        and next(bases, None) is None
        and next(legacy, None) is None,
        "missing/extra Newton baseline/residual",
    )
    selected.finish()
    probes.finish()
    require(next_call == evaluations.count + 1, "unaccounted first-step physical calls")
    require(
        counts["probe"] == requests - 1 - 3 * index, "probe/request accounting differs"
    )
    return {
        "iterations": iterations,
        "per_attempt_iterations": per_attempt,
        "attempts": [list(r) for r in attempts],
        "fresh_requests": requests,
        "last": last,
        "last_physical_call": next_call - 1,
    }


def first_step_gate(root, spec, result):
    try:
        root, prepared, work, record, static, counts, requests, ordinary = _inspect(
            root, spec, result, True
        )
        require(
            spec["stage"] in ("standard", "tight")
            and spec["arguments"] == ["assembly-step"]
            and spec["mode"] == 1,
            "not a fixed first-step process",
        )
        require(counts["accepted"] in (0, 1), "more than one accepted endpoint")
        same, hashes = _check_streams(work, static, counts, requests)
        controls = (1e-13, 1e-11) if spec["stage"] == "standard" else (1e-14, 1e-12)
        require(static["input"]["controls"] == controls, "first-step controls differ")
        with Evaluations(work / "assembly-evaluations.bin") as evaluations:
            links = _identity_files(
                root, prepared, spec, work, static, evaluations, hashes
            )
            initial = parse_workspace((work / "assembly-baseline-001.bin").read_bytes())
            _echo(
                evaluations.row(1),
                initial["conditions"],
                static["input"]["Y0"],
                initial["variant"],
                initial["original"],
                1,
            )
            forensic = _step_forensics(
                work, static, evaluations, same, counts, controls
            )
            require(
                requests["fresh_requests"] == forensic["fresh_requests"],
                "first-step guarded request total differs",
            )
            raw = (work / "first-step.bin").read_bytes()
            require(
                len(raw) == 16 + (6 + N) * 8
                and struct.unpack_from("<4i", raw) == (0x43524153, 1, N, 0),
                "first-step result header/extent differs",
            )
            values = struct.unpack_from("<166d", raw, 16)
            requested, achieved, accepted, attempts, norm, projection = values[:6]
            endpoint = values[6:]
            require(
                _finite(values)
                and requested == 1e-4
                and accepted in (0.0, 1.0)
                and bool(accepted) == (not ordinary)
                and accepted == counts["accepted"]
                and attempts == len(forensic["attempts"]),
                "first-step outcome/scope differs",
            )
            last = forensic["last"]
            require(
                norm == last["scalars"][2], "first-step final residual summary differs"
            )
            kind = "accepted" if accepted else "failure"
            link, terminal, original = _workspace_check(
                work,
                "assembly-" + kind + ".bin",
                "baseline-" + kind + ".bin",
                static,
                evaluations,
            )
            links.append(link)
            require(
                terminal["call"] == forensic["last_physical_call"]
                and _same(terminal["Y"], last["post"])
                and terminal["conditions"][0] == last["scalars"][0]
                and hashes[terminal["call"]] == sha(original["branches"]),
                "terminal workspace does not bind the actual last evaluation",
            )
            accepted_rows = list(_rows(work / "accepted.bin", 488))
            conditions = list(_rows(work / "accepted-forcing.bin", 3))
            require(
                len(accepted_rows) == len(conditions) == 1 + int(accepted),
                "accepted output population differs",
            )
            require(
                accepted_rows[0][0] == 0
                and _same(accepted_rows[0][1:161], static["input"]["Y0"])
                and _same(accepted_rows[0][161:321], initial["variant"])
                and _same(conditions[0], initial["conditions"]),
                "initial accepted output differs",
            )
            if accepted:
                require(
                    achieved == last["scalars"][0]
                    and 0 < achieved <= requested
                    and _same(endpoint, last["post"])
                    and norm <= 1
                    and forensic["iterations"][-1]["recomputed_norm"] <= 1
                    and projection == last["scalars"][4] <= 1e-12
                    and last["scalars"][5] + projection <= 1e-10,
                    "accepted endpoint/residual/projection criterion failed",
                )
                output = accepted_rows[-1]
                require(
                    output[0] == achieved
                    and _same(output[1:161], endpoint)
                    and _same(output[161:321], terminal["variant"])
                    and _same(output[321:481], last["residual"])
                    and _same(conditions[-1], terminal["conditions"]),
                    "accepted endpoint F/residual/forcing binding differs",
                )
                _close(
                    output[481:484],
                    original["values"][4:7],
                    [abs(v) for v in original["values"][4:7]],
                )
                _close(
                    output[484:488],
                    [norm, last["scalars"][3], projection, projection],
                    [abs(norm), abs(last["scalars"][3]), projection, projection],
                )
                B0 = parse_original((work / "baseline-001.bin").read_bytes())["values"][
                    4
                ]
                bound = 1e-10 * max(1, abs(B0))
                B = math.fsum(
                    m * y for m, y in zip(static["input"]["A"], endpoint, strict=True)
                )
                exact_B0 = sum(
                    (
                        Q(m) * Q(y)
                        for m, y in zip(
                            static["input"]["A"], static["input"]["Y0"], strict=True
                        )
                    ),
                    Q(0),
                )
                exact_B = sum(
                    (
                        Q(m) * Q(y)
                        for m, y in zip(static["input"]["A"], endpoint, strict=True)
                    ),
                    Q(0),
                )
                require(
                    abs(original["values"][4] - B0) <= bound
                    and abs(B - B0) <= bound
                    and abs(exact_B - exact_B0) <= Q(bound),
                    "accepted nonunit baryon inventory changed beyond criterion",
                )
                domain(
                    endpoint,
                    *forcing(static["input"], achieved),
                    static["input"]["Z"],
                    static["input"]["A"],
                )
            else:
                require(
                    achieved == 0
                    and _same(endpoint, static["input"]["Y0"])
                    and len(forensic["attempts"]) == 10
                    and forensic["per_attempt_iterations"] == [30] * 10
                    and norm > 1
                    and projection == 0,
                    "ordinary nonlinear failure is not a complete exhausted attempt",
                )
        forensic.pop("last")
        return {
            "pass": bool(accepted),
            "software_pass": True,
            "fatal": False,
            "ordinary_numerical_failure": ordinary,
            "requested_h": requested,
            "achieved_time": achieved,
            "requested_interval_complete": achieved == requested,
            "workspaces": links,
            "forensics": forensic,
            "physical_rhs_calls": counts["rhs"],
            "fresh_requests": requests["fresh_requests"],
            "trajectory_reference_qualified": False,
        }
    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        struct.error,
        ZeroDivisionError,
        OverflowError,
    ) as exc:
        return _failure(exc)
