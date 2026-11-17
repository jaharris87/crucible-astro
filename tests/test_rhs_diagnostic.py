"""Independent synthetic framing, unchanged-state and numerical comparison oracles."""

import importlib.util
import json
import math
import struct
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "experiments/rhs_alignment/diagnostic.py"
SPEC = importlib.util.spec_from_file_location("rhs_diagnostic", SOURCE)
diag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diag)


def framed(payload):
    marker = struct.pack("<i", len(payload))
    return marker + payload + marker


def synthetic_raw():
    z = [0.0] + [float(i) for i in range(1, 160)]
    a = [1.0] + [float(2 * i) for i in range(1, 160)]
    headers = [
        b" " * 320,
        struct.pack(
            "<5i6d2i", 99999, 5, 1, 1, 1, 0.1, 1e-6, 1e-4, 1e-8, 1e-20, 2.0, 0, 1
        ),
        b" " * 160,
        b" " * 160,
        struct.pack("<i320d", 160, *(z + a)),
        struct.pack("<i", 909) + bytes(909 * 8),
    ]
    data = bytearray(b"".join(framed(h) for h in headers))
    ev = ["k Time T9 rho edot dt"]
    for i in range(742):
        row = struct.pack("<i5d", i + 1, 0.5 + i, 2.0, 3.0, 0.01, 9.0)
        row += struct.pack("<160d", -0.0, 0.5, *([0.0] * 158))
        row += bytes(909 * 8)
        row += struct.pack("<160d", *([0.0] * 160))
        data.extend(framed(row))
        ev.append(f"{i + 1} .5 2 3 9 .01 ordinary")
    return bytes(data), ("\n".join(ev) + "\n").encode()


def test_extract_exact_bytes_and_signed_zero():
    raw, ev = synthetic_raw()
    states, selection = diag.extract_states(raw, ev)
    assert [s["ordinal"] for s in selection] == [1, 676, 741]
    # Header16 + Z/A2560 + ordinal/step/scalars48; signed zero survives unchanged.
    assert states[2624:2632] == struct.pack("<d", -0.0)
    assert len(states) == 10400
    assert struct.unpack_from("<ii5d", states, 2576)[:2] == (1, 2)


@pytest.mark.parametrize("defect", ["marker", "NSE", "control", "nonfinite"])
def test_extract_rejects_independent_corruptions(defect):
    raw, ev = synthetic_raw()
    if defect == "marker":
        raw = b"\x01\0\0\0" + raw[4:]
    elif defect == "NSE":
        rows = ev.decode().splitlines()
        rows[2] = "2 .5 2 3 9 .01 NSE"
        ev = ("\n".join(rows) + "\n").encode()
    elif defect == "control":
        raw = raw.replace(
            struct.pack(
                "<5i6d2i", 99999, 5, 1, 1, 1, 0.1, 1e-6, 1e-4, 1e-8, 1e-20, 2.0, 0, 1
            ),
            struct.pack(
                "<5i6d2i", 99999, 5, 0, 1, 1, 0.1, 1e-6, 1e-4, 1e-8, 1e-20, 2.0, 0, 1
            ),
            1,
        )
    else:
        marker = list(diag.records(raw))[7][0]
        raw = raw[: marker + 48] + struct.pack("<d", math.nan) + raw[marker + 56 :]
    with pytest.raises(ValueError):
        diag.extract_states(raw, ev)


def setup_comparison(root):
    raw, ev = synthetic_raw()
    states, _ = diag.extract_states(raw, ev)
    (root / "states.bin").write_bytes(states)
    (root / "rhs_evaluator").write_bytes(b"synthetic non-executable fixture")
    shared = root / "synthetic.so"
    shared.write_bytes(b"library identity fixture")
    (root / "loaded-maps.txt").write_text(f"0 0 0 0 0 {shared}\n")
    manifest = {
        "schema": "crucible.rhs-diagnostic-bundle.v1",
        "reference_status": "synthetic only",
        "files": {"states.bin": {"bytes": len(states), "sha256": diag.digest(states)}},
    }
    (root / "manifest.json").write_text(json.dumps(manifest))
    output = bytearray(states[:2576])
    for k in range(3):
        row = states[2576 + k * 2608 : 2576 + (k + 1) * 2608]
        ordinal, step, *scalars = struct.unpack_from("<ii5d", row)
        yy, old = row[48:1328], row[1328:]
        fresh = struct.pack("<160d", 3.0, -4.0, *([0.0] * 158))
        output.extend(
            struct.pack("<ii9di", ordinal, step, *scalars, *scalars[:3], 0.5, 1)
        )
        output.extend(yy + yy + old + fresh)
    (root / "fresh.bin").write_bytes(output)


def test_comparison_absolute_metrics_and_constraints(tmp_path):
    setup_comparison(tmp_path)
    result = diag.compare(tmp_path)["results"][0]
    assert result["absolute_error"] == {"L1": 7.0, "L2": 5.0, "Linf": 4.0}
    assert result["fresh_baryon_rate"] == -5.0
    assert result["fresh_charge_rate"] == -4.0
    assert result["Y_before_sha256"] == result["Y_after_sha256"]
    assert result["fresh_dY"][:2] == (3.0, -4.0)


@pytest.mark.parametrize("offset", [2576 + 8, 2576 + 48, 2576 + 84 + 1280])
def test_comparison_rejects_state_scalar_or_echo_change(tmp_path, offset):
    setup_comparison(tmp_path)
    payload = bytearray((tmp_path / "fresh.bin").read_bytes())
    payload[offset] ^= 1
    (tmp_path / "fresh.bin").write_bytes(payload)
    with pytest.raises(ValueError):
        diag.compare(tmp_path)


def test_verify_rejects_mutated_bound_input(tmp_path):
    setup_comparison(tmp_path)
    (tmp_path / "states.bin").write_bytes(b"changed")
    with pytest.raises(ValueError, match="Bound input changed"):
        diag.verify(tmp_path)
