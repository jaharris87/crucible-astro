"""Independent toy arithmetic/stream controls; no Fortran is compiled or called."""

import importlib.util
import math
import struct
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "experiments/rhs_reference"
sys.path.insert(0, str(ROOT))
SPEC = importlib.util.spec_from_file_location("rhs_reference", ROOT / "reference.py")
ref = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ref)
from arithmetic import assemble_check, mapping_terms, product_bound  # noqa: E402


def toy_group(duplicate=False):
    # A(1) -> B(1), or 2A -> A+B with the A destruction/creation separate.
    if duplicate:
        return {
            "order": 2,
            "participants": [(1, 1, 1, 2, 0, 0)],
            "extended": [(1, 0, -1.0), (1, 0, 0.5), (2, 0, 0.5)],
        }
    return {
        "order": 1,
        "participants": [(1, 2, 0, 0, 0)],
        "extended": [(1, 0, -1.0), (2, 0, 1.0)],
    }


def test_independent_hand_known_weak_reaction_and_norms():
    terms = mapping_terms([toy_group()], [1, 1])
    result = assemble_check([0.25, 0.75], [4.0], [-1.0, 1.0], terms, [1, 1])
    assert (
        result["conditional_assembly_check"]
        and not result["scientific_accuracy_acceptance"]
    )
    assert result["fresh_baryon_absolute_residual"] == 0
    # Construct the output wire representation without using the implementation encoder.
    prefix = struct.pack("<5i5d", 1, 2, 3, 4, 5, 0.5, 2.0, 1e6, 0.01, 9.0)
    y = struct.pack("<2d", 0.25, 0.75)
    old = struct.pack("<2d", -4.0, 5.0)
    output = (
        prefix
        + struct.pack("<4di", 0.5, 2.0, 1e6, 0.75, 1)
        + y
        + y
        + old
        + struct.pack("<3d", -1.0, 1.0, 4.0)
    )
    decoded, coeff, _ = ref.decode_record(prefix + y + old, output, [0, 1], [1, 1], 1)
    assert decoded["absolute_difference"] == {"L1": 7.0, "L2": 5.0, "Linf": 4.0}
    assert decoded["fresh_charge_rate"] == 1 and coeff == [4.0]


def test_factorials_are_not_applied_twice_and_separate_terms_cancel():
    terms = mapping_terms([toy_group(True)], [1, 1])
    result = assemble_check([0.5, 0.5], [8.0], [-1.0, 1.0], terms, [1, 1])
    assert result["conditional_assembly_check"]


def test_DAZ_amplification_is_covered_not_just_min_subnormal():
    # A flushed subnormal abundance times a large coefficient loses ~1e-20.
    terms = mapping_terms([toy_group()], [1, 1])
    result = assemble_check([1e-320, 1.0], [1e300], [0.0, 0.0], terms, [1, 1])
    assert result["component_absolute_residual"][0] > 1e-21
    assert (
        result["component_absolute_bound"][0]
        >= result["component_absolute_residual"][0]
    )
    exact, bound = product_bound([Fraction(1), Fraction(1e300), Fraction(1e-320)])
    assert abs(exact) <= bound


@pytest.mark.parametrize("defect", ["factor", "target", "baryon"])
def test_mapping_rejects_corrupt_toy_tables(defect):
    group = toy_group()
    masses = [1, 1]
    if defect == "factor":
        group["extended"][0] = (1, 0, -0.5)
    elif defect == "target":
        group["extended"][0] = (3, 0, -1.0)
    else:
        masses = [1, 2]
    with pytest.raises(ValueError):
        mapping_terms([group], masses)


def test_arithmetic_rejects_wrong_rhs_and_invalid_inputs():
    terms = mapping_terms([toy_group()], [1, 1])
    with pytest.raises(ValueError, match="bound"):
        assemble_check([0.25, 0.75], [4.0], [-2.0, 2.0], terms, [1, 1])
    with pytest.raises(ValueError):
        assemble_check([math.nan, 0.5], [4.0], [0.0, 0.0], terms, [1, 1])


@pytest.mark.parametrize("offset", [0, 20, 60, 96, 112, 128])
def test_decoder_rejects_mutated_identity_echo_or_nonfinite(offset):
    prefix = struct.pack("<5i5d", 1, 2, 3, 4, 5, 0.5, 2.0, 1e6, 0.01, 9.0)
    y = struct.pack("<2d", 0.25, 0.75)
    old = struct.pack("<2d", -4.0, 5.0)
    output = bytearray(
        prefix
        + struct.pack("<4di", 0.5, 2.0, 1e6, 0.75, 1)
        + y
        + y
        + old
        + struct.pack("<3d", -1.0, 1.0, 4.0)
    )
    output[offset] ^= 1
    with pytest.raises(ValueError):
        ref.decode_record(prefix + y + old, output, [0, 1], [1, 1], 1)


def test_marker_and_species_state_checks():
    with pytest.raises(ValueError):
        list(ref.records(struct.pack("<i", 5) + b"x"))
    prefix = struct.pack("<5i5d", 1, 2, 3, 0, 5, 0.5, 2.0, 1e6, 0.01, 9.0)
    with pytest.raises(ValueError):
        ref.validate_state(prefix, struct.pack("<2d", 0.25, 0.75), [0, 1], [1, 1])


def test_bounded_fortran_call_sites_are_preparation_only():
    text = (ROOT / "rhs_evaluator.f90").read_text().lower()
    assert text.count("call cross_sect(") == text.count("call yderiv(") == 1
    assert "nstate /= 5157" in text
    assert "ieee_set_" not in text
    assert not any("call " + x in text for x in ("nse_solve", "timestep", "full_net"))


@pytest.mark.parametrize("defect", ["duplicate", "nonintegral", "nonfinite", "width"])
def test_species_identity_rejects_malformed_namespaces(defect):
    z = [float(i) for i in range(160)]
    a = [float(2 * i + 1) for i in range(160)]
    if defect == "duplicate":
        z[1] = z[0]
        a[1] = a[0]
    elif defect == "nonintegral":
        a[5] = 10.5
    elif defect == "nonfinite":
        z[7] = math.nan
    data = struct.pack("<320d", *(z + a))
    if defect == "width":
        data = data[:-8]
    with pytest.raises(ValueError):
        ref.species_ids(data)


def test_input_reaction_counts_are_checked_before_parsing_maps():
    def framed(b):
        return struct.pack("<i", len(b)) + b + struct.pack("<i", len(b))

    nets4 = b"".join(
        framed(b)
        for b in (struct.pack("<i", 160), bytes(800), struct.pack("<2i", 176, 1))
    )
    with pytest.raises(ValueError, match="FFN/NNU"):
        ref.expected_maps(b"", nets4)


def test_truncated_map_stream_stops():
    with pytest.raises(ValueError, match="Truncated"):
        ref.parse_maps(bytes(4), ny=2)


def test_native_two_identical_pairs_convention_is_preserved_explicitly():
    # Native preprocessing uses factorial(max multiplicity)=2, not 2!*2!=4.
    group = {
        "order": 4,
        "participants": [(1, 1, 2, 2, 3, 0)],
        "extended": [(1, 0, -1.0), (2, 0, -1.0), (3, 0, 0.5)],
    }
    terms = mapping_terms([group], [1, 1, 4])
    assert assemble_check(
        [0.25, 0.25, 0.0], [256.0], [-1.0, -1.0, 0.5], terms, [1, 1, 4]
    )["conditional_assembly_check"]
    with pytest.raises(ValueError, match="bound"):
        assemble_check([0.25, 0.25, 0.0], [256.0], [-0.5, -0.5, 0.25], terms, [1, 1, 4])


def test_retained_controls_are_selected_by_bits_not_real_path_and_reject_bad_echo():
    z = [0.0] + [1.0] * 159
    a = [1] * 160
    y = struct.pack("<160d", 0.0, 0.5, *([0.0] * 158))
    stored = bytes(1280)
    fresh = bytes(1280)
    head = ref.HEADER.pack(ref.MAGIC, 1, 3, 160) + bytes(2560)
    states = bytearray(head)
    output = bytearray(head)
    for i, rho in enumerate((100.0, 200.0, 0.01), 1):
        scalars = (0.5, 2.0, rho, 0.01, 0.0)
        prefix = struct.pack("<ii5d", i, i, *scalars)
        states.extend(prefix + y + stored)
        output.extend(
            struct.pack("<ii9di", i, i, *scalars, *scalars[:3], 0.5, 1)
            + y
            + y
            + stored
            + fresh
        )
    controls = ref.retained_controls(bytes(states), bytes(output), z, a)
    assert len(controls) == 2 and all(len(k) == 2608 for k in controls)
    output[2576 + 84] ^= 1
    with pytest.raises(ValueError, match="echo"):
        ref.retained_controls(bytes(states), bytes(output), z, a)
