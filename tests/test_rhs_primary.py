"""Hand-specified finite primary controls; no private data, compiler or XNet."""

import copy
import json
import math
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "experiments/rhs_reference"
sys.path.insert(0, str(ROOT))
import primary  # noqa: E402
import reference as ref  # noqa: E402


@pytest.fixture
def small_contract(monkeypatch):
    for key, value in {
        "NEW": 3,
        "PILOT": 2,
        "TOTAL": 5,
        "NEW_HISTORIES": 2,
        "PILOT_HISTORIES": 1,
    }.items():
        monkeypatch.setattr(primary, key, value)
    batch = dict(
        primary.BATCH,
        new_states=3,
        proposed_calls=5,
        pilot_states_reused=2,
        pilot_states_not_repeated=0,
        unique_union_states=5,
        new_histories=2,
        pilot_histories=1,
    )
    monkeypatch.setattr(primary, "BATCH", batch)
    return batch


def identity(slab, ordinal):
    path = f"Run_slab_{slab:03d}/Run/ts_0007"
    return {
        "record_id": f"{path}#{ordinal}",
        "trajectory_locator": path,
        "ordinal": ordinal,
    }


@pytest.fixture
def finite_bundle(tmp_path, small_contract):
    new = [identity(1, 1), identity(1, 2), identity(2, 1)]
    pilot = [identity(3, 1), identity(3, 2)]
    pop = {"new": new, "pilot": pilot}
    za = struct.pack("<320d", *range(160), *(2 * i + 1 for i in range(160)))
    head = struct.pack("<4i", 0x43525543, 2, 5, 160) + za
    y = struct.pack("<160d", 0.25, 0.25, *([0.0] * 158))
    rows, states, outputs = [], [], []
    for seq, entry in enumerate(new + pilot, 1):
        slab = [1, 1, 2, 3, 3][seq - 1]
        prefix = struct.pack(
            "<5i5d", seq, slab, 7, entry["ordinal"], 20, 0.5, 2.0, 100.0, 0.01, -0.0
        )
        states.append(prefix + y + bytes(1280))
        rows.append(
            dict(
                entry,
                sequence=seq,
                role="new" if seq <= 3 else "repeat_control",
                input_state_sha256=ref.digest(prefix + y),
            )
        )
        if seq > 3:
            rows[-1]["source_pilot_sequence"] = seq - 3
        # Wire oracle: duplicated Y echoes, unchanged stored vector and zero RHS/coefficient payload.
        outputs.append(
            prefix
            + struct.pack("<4di", 0.5, 2.0, 100.0, 0.25, 1)
            + y
            + y
            + bytes(1280 + 1280 + 16384)
        )
    controls = {
        str(k): {"record_id": rows[k - 1]["record_id"], "fresh_hex": bytes(1280).hex()}
        for k in (4, 5)
    }

    def save():
        for name, data in [
            ("population.json", pop),
            ("selection.json", rows),
            ("d017-controls.json", controls),
        ]:
            (tmp_path / name).write_text(json.dumps(data))

    save()
    return (
        tmp_path,
        {"batch": small_contract},
        head + b"".join(states),
        rows,
        pop,
        controls,
        save,
        head + b"".join(outputs),
    )


def test_finite_positive_control_has_three_new_plus_two_explicit_repeats(finite_bundle):
    root, manifest, states, rows, pop, _, _, _ = finite_bundle
    primary.population(pop["new"], pop["pilot"], pop["new"] + pop["pilot"])
    primary.verify_metadata(root, manifest, states)
    assert len(rows) == 5 and sum(r["role"] == "new" for r in rows) == 3
    # Energy sign bits remain the supplied negative zero.
    assert states[2576 + 52 : 2576 + 60] == bytes.fromhex("0000000000000080")


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("duplicate", "duplicate"),
        ("overlap", "overlap"),
        ("missing", "membership"),
        ("wrong_union", "union"),
        ("identity", "identity"),
        ("histories", "history"),
    ],
)
def test_finite_membership_rejects_wrong_independently_named_sets(
    finite_bundle, defect, reason
):
    _, _, _, _, pop, _, _, _ = finite_bundle
    new, pilot = copy.deepcopy(pop["new"]), copy.deepcopy(pop["pilot"])
    accepted = copy.deepcopy(new + pilot)
    if defect == "duplicate":
        new[1] = new[0]
    elif defect == "overlap":
        new[0] = identity(3, 1)
        new[1] = identity(3, 2)
    elif defect == "missing":
        new.pop()
    elif defect == "wrong_union":
        accepted[0] = identity(1, 3)
    elif defect == "identity":
        new[0]["ordinal"] = 8
    else:
        new[2] = identity(1, 3)
    with pytest.raises(ValueError, match=reason):
        primary.population(new, pilot, accepted)


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("missing_control", "control count"),
        ("wrong_control_identity", "ancestry"),
        ("nan_control", "control vector"),
        ("wrong_role", "membership/order"),
        ("config", "contract"),
        ("ordering", "ordering/identity"),
        ("species", "species"),
        ("nonfinite_state", "Nonfinite state"),
    ],
)
def test_primary_bundle_semantic_failures(finite_bundle, defect, reason):
    root, manifest, states, rows, _, controls, save, _ = finite_bundle
    if defect == "missing_control":
        del controls["4"]
    elif defect == "wrong_control_identity":
        controls["4"]["record_id"] = rows[0]["record_id"]
    elif defect == "nan_control":
        controls["4"]["fresh_hex"] = (struct.pack("<d", math.nan) + bytes(1272)).hex()
    elif defect == "wrong_role":
        rows[0]["role"] = "repeat_control"
    elif defect == "config":
        manifest["batch"] = dict(manifest["batch"], repeat_controls=0)
    elif defect == "ordering":
        states = (
            states[:2576]
            + states[2576 + 2620 : 2576 + 5240]
            + states[2576 : 2576 + 2620]
            + states[2576 + 5240 :]
        )
    elif defect == "species":
        data = bytearray(states)
        data[24:32] = data[16:24]
        data[1304:1312] = data[1296:1304]
        states = bytes(data)
    else:
        states = states[:2636] + struct.pack("<d", math.nan) + states[2644:]
    save()
    with pytest.raises(ValueError, match=reason):
        primary.verify_metadata(root, manifest, states)


@pytest.mark.parametrize(
    "energy,text,other,accepted",
    [
        (-0.0, "0.00E+00", False, True),
        (0.0, "-0.00E+00", False, True),
        (-0.0, "0.00E+00", True, False),
        (1e-300, "0.00E+00", False, False),
        (-0.0, "0E+00", False, False),
    ],
)
def test_only_exact_energy_signed_zero_equivalence(energy, text, other, accepted):
    expected = [
        "20",
        "1.00000000E+00",
        "2.000E+00",
        "1.000E+02",
        f"{energy:.2E}",
        "1.00E-02",
    ]
    fields = expected.copy()
    fields[4] = text
    fields += ["1", "2"]
    if other:
        fields[1] = "1.00000001E+00"
    assert primary.companion_matches(fields, expected, energy)[0] is accepted


@pytest.mark.parametrize("difference", [-1, 1, 21716])
def test_comparator_rejects_missing_extra_or_truncated_output_before_arithmetic(
    finite_bundle, monkeypatch, difference
):
    root, _, states, _, _, _, _, output = finite_bundle
    (root / "states.bin").write_bytes(states)
    for name in ("expected-maps.bin", "used-maps.bin", "used-maps-after.bin"):
        (root / name).write_bytes(b"toy-maps")
    (root / "fresh.bin").write_bytes(
        output[:difference] if difference < 0 else output + bytes(difference)
    )
    monkeypatch.setattr(ref, "verify", lambda _: {"selection_count": 5})
    monkeypatch.setattr(ref, "parse_maps", lambda _: [])
    monkeypatch.setattr(ref, "mapping_terms", lambda *_: [])
    with pytest.raises(ValueError, match="output count/length"):
        ref.compare(root)
    assert not (root / "components.jsonl").exists()


def toy_raw(tmp_path, defect=None):
    name = "Run_slab_001/Run/ts_0007"
    z = list(range(160))
    a = [2 * i + 1 for i in range(160)]
    if defect == "species":
        z[1], a[1] = z[0], a[0]
    species = struct.pack("<i320d", 160, *z, *a)
    config = struct.pack("<5i6d2i", 0, 0, 1, 1, 0, *([0.0] * 6), 0, 1)
    if defect == "configuration":
        config = config[:8] + struct.pack("<i", 0) + config[12:]
    y = struct.pack("<160d", 0.25, 0.25, *([0.0] * 158))
    header = struct.pack("<i5d", 20, 1.0, 2.0, 100.0, 0.01, -0.0)
    ordinary = header + y + bytes(9876 - 44 - 1280)
    payloads = [
        bytes(320),
        config,
        bytes(160),
        bytes(160),
        species,
        struct.pack("<i", 909) + bytes(7272),
        bytes(9876),
        ordinary,
    ]

    def framed(b):
        return struct.pack("<i", len(b)) + b + struct.pack("<i", len(b))

    raw = b"".join(framed(b) for b in payloads)
    companion = b"heading\ninitial\n20 1.00000000E+00 2.000E+00 1.000E+02 0.00E+00 1.00E-02 1 2\n"
    root = tmp_path / "raw"
    path = root / name
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    evname = "Run_slab_001/Run/ev_0007"
    (root / evname).write_bytes(companion)
    chosen = [
        {
            "trajectory_locator": name,
            "record_id": name + "#1",
            "ordinal": 1,
            "raw_marker_offset": sum(len(b) + 8 for b in payloads[:7]),
            "header_sha256": ref.digest(header),
            "Y_bytes_sha256": ref.digest(y),
        }
    ]
    if defect == "state_hash":
        chosen[0]["Y_bytes_sha256"] = "0" * 64
    elif defect == "initial":
        chosen[0]["ordinal"] = 0
    return chosen, {name: ref.digest(raw), evname: ref.digest(companion)}, root


def test_raw_preparation_accepts_only_new_modes_signed_zero_allowance(tmp_path):
    chosen, fixity, root = toy_raw(tmp_path)
    with pytest.raises(ValueError, match="Companion/ordinary"):
        ref.extract_states(chosen, fixity, root)
    payloads, _, _, _, events = ref.extract_states(
        chosen, fixity, root, signed_zero=True
    )
    assert payloads[1][52:60] == bytes.fromhex("0000000000000080")
    assert events == [
        {
            "trajectory_locator": "Run_slab_001/Run/ts_0007",
            "ordinal": 1,
            "raw_binary64_hex": "0000000000000080",
        }
    ]


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("configuration", "physics configuration"),
        ("species", "species"),
        ("state_hash", "state bits"),
        ("initial", "ordinary ordinal"),
    ],
)
def test_raw_primary_preparation_rejects_bad_inputs_before_any_call(
    tmp_path, defect, reason
):
    args = toy_raw(tmp_path, defect)
    with pytest.raises(ValueError, match=reason):
        ref.extract_states(*args, signed_zero=True)


@pytest.mark.parametrize("changed_control", [False, True])
def test_comparator_exact_repeat_control_positive_and_changed_bits(
    finite_bundle, monkeypatch, changed_control
):
    root, _, states, _, _, _, _, output = finite_bundle
    (root / "states.bin").write_bytes(states)
    for name in ("expected-maps.bin", "used-maps.bin", "used-maps-after.bin"):
        (root / name).write_bytes(b"toy-maps")
    if changed_control:
        wire = bytearray(output)
        # Fourth output is the first explicit control; first fresh component becomes +min-subnormal.
        wire[2576 + 3 * 21600 + 3936] = 1
        output = bytes(wire)
    (root / "fresh.bin").write_bytes(output)
    library = root / "libsynthetic.so"
    library.write_bytes(b"synthetic bytes only; never loaded")
    (root / "loaded-maps.txt").write_text(f"0-1 r-xp 00000000 00:00 0 {library}\n")
    (root / "rhs_evaluator").write_bytes(b"synthetic bytes only; never executed")
    (root / "manifest.json").write_text("{}")
    monkeypatch.setattr(ref, "verify", lambda _: {"selection_count": 5})
    monkeypatch.setattr(ref, "parse_maps", lambda _: [])
    monkeypatch.setattr(ref, "mapping_terms", lambda *_: [])
    # Arithmetic has separate hand-known reaction controls. This isolates stream and exact-bit control behavior.
    monkeypatch.setattr(
        ref, "assemble_check", lambda *_: {"synthetic_arithmetic_stub": True}
    )
    if changed_control:
        with pytest.raises(ValueError, match="exact-bit control mismatch"):
            ref.compare(root)
        assert not (root / "comparison.json").exists()
    else:
        result = ref.compare(root)
        assert result["D017_exact_bit_controls"] == [4, 5]
        assert not result["training_eligibility"]
        assert len((root / "components.jsonl").read_text().splitlines()) == 5


def test_primary_rejects_ambiguous_config_before_reading_files(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"unexpected_mode": "evaluate"}')
    with pytest.raises(ValueError, match="Unexpected primary config"):
        primary.prepare(path, tmp_path / ".local" / "never-created")
    assert not (tmp_path / ".local").exists()


def test_harness_admits_only_two_explicit_finite_call_counts():
    import re

    text = (ROOT / "rhs_evaluator.f90").read_text().lower()
    assert set(re.findall(r"nstate\s*/=\s*(\d+)", text)) == {"5157", "19159"}
    assert "(nstate /= 5157 .and. nstate /= 19159)" in text
