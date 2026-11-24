"""Independent rational answers for compiled fixtures, plus forensic dataflow checks.

These tests never compile or execute Fortran. The actual native fixture run on the
accepted host remains mandatory; verifying its expected answers is not that run.
"""

import re
import struct
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "experiments/trajectory_reference"


def power2(exponent):
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2**-exponent)


def decode_quad(bits):
    sign = -1 if bits >> 127 else 1
    field = (bits >> 112) & 0x7FFF
    fraction = bits & (2**112 - 1)
    assert field not in (0, 0x7FFF)
    return sign * Fraction(2**112 + fraction) * power2(field - 16383 - 112)


def rounded_quad(value):
    if not value:
        return value
    sign = -1 if value < 0 else 1
    value = abs(value)
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if value < power2(exponent):
        exponent -= 1
    scaled = value / power2(exponent - 112)
    integer, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder > scaled.denominator or (
        2 * remainder == scaled.denominator and integer % 2
    ):
        integer += 1
    return sign * integer * power2(exponent - 112)


def test_native_fixture_quad_answers_are_independent_exact_polynomials():
    text = (HERE / "assembly113_math.f90").read_text()
    block = re.search(r"expected_totals=\[(.*?)\]", text, re.S)[1]
    words = [int(x, 16) for x in re.findall(r"z'([0-9a-f]+)'", block)]
    observed = [decode_quad(words[i] | (words[i + 1] << 64)) for i in (0, 2)]
    x = Fraction.from_float(float.fromhex("0x1.fffffffffffffp-1"))
    expected = [power2(113) - power2(113) + 1 + power2(-112), x * x]
    assert observed == expected
    # A double product promoted only after multiplication loses the tiny term.
    assert observed[1] != Fraction.from_float(float(x * x))
    # A different class association loses the final quad ULP in this fixture.
    wrong_join = rounded_quad(
        power2(113) + rounded_quad(-power2(113) + rounded_quad(1 + power2(-112)))
    )
    assert wrong_join != observed[0]


def test_conversion_fixture_ties_match_binary64_nearest_even():
    text = (HERE / "assembly113_math.f90").read_text()
    block = re.search(r"expected=\[(.*?)\]\s+open", text, re.S)[1]
    tokens = re.findall(r"int\(z'([0-9a-f]+)',int64\)|([0-9]+)_int64", block)
    expected_bits = [
        int(hexdigits, 16) if hexdigits else int(decimal)
        for hexdigits, decimal in tokens
    ]
    smallest = power2(-1074)
    maximum_subnormal = (2**52 - 1) * smallest
    values = [
        smallest / 2,
        -smallest / 2,
        3 * smallest / 2,
        -3 * smallest / 2,
        maximum_subnormal + smallest / 2,
        -(maximum_subnormal + smallest / 2),
        1 + power2(-53),
        1 + 3 * power2(-53),
    ]
    actual = [
        struct.unpack("<Q", struct.pack("<d", float(value)))[0] for value in values
    ]
    assert actual == expected_bits


def test_finite_native_operands_fit_binary128_without_assuming_host_quad():
    # Five binary64 operands, at most four abundance factors in [0,1].
    minimum_term = power2(-1074 * 5)
    maximum_total = 6794 * Fraction.from_float(float.fromhex("0x1.fffffffffffffp+1023"))
    assert minimum_term > power2(-16382)
    assert maximum_total < power2(16383)
    assert 5 * 6794 + 3 == 33973
    assert (33973 * power2(-113)) < 1


def test_only_new_numerical_module_receives_strict_fp_option():
    script = (HERE / "build.sh").read_text()
    strict = [line for line in script.splitlines() if "-fp-model strict" in line]
    assert (
        len(strict) == 3
    )  # physical object, legacy-fixture dependency, standalone fixture
    assert all("assembly113_math.f90" in line for line in strict)
    assert "fp-model" not in next(
        line for line in script.splitlines() if line.startswith("flags=")
    )


def test_newton_wire_header_matches_serialized_shapes_and_integer_blocks():
    source = (HERE / "native_adapter.f90").read_text()
    writer = source.split("  subroutine write_assembly_newton(", 1)[1].split(
        "  end subroutine write_assembly_newton", 1
    )[0]
    payload = re.search(
        r"write\(assembly_newton_unit\) (.*?)\n    flush", writer, re.S
    )[1]
    names = payload.replace("&", "").replace("\n", "").replace(" ", "").split(",")
    dimensions = {}
    for line in source.splitlines():
        if line.startswith("  real(dp) ::") or line.startswith("  integer(int"):
            for name, shape in re.findall(r"(an_\w+)\((\d+(?:,\d+)*)\)", line):
                count = 1
                for value in shape.split(","):
                    count *= int(value)
                dimensions[name] = count
    assert names[0] == "an_ids" and dimensions[names[0]] == 10
    assert names[-1] == "an_pivots" and dimensions[names[-1]] == 160
    assert sum(dimensions[name] for name in names[1:-1]) == 78568
    assert "78568_int32,10_int32,160_int32" in source


def test_first_step_entry_calls_solver_once_without_continuation():
    source = (HERE / "trajectory_driver.f90").read_text()
    step = source.split("  subroutine qualification_first_step()", 1)[1].split(
        "  end subroutine qualification_first_step", 1
    )[0]
    assert step.count("call solve_be(") == 1
    assert "do while" not in step.lower()
    assert "1e-4_dp" in step
    assert "call fail('first native step failed')" in step
