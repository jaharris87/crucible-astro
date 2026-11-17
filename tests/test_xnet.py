"""Public hand-specified sentinels, independent of producer/private data and reader.

Only framing markers are computed. Header/row bytes below are literal IEEE754
sentinels, not packed by the implementation or generated from decoded results.
"""

import copy
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

import h5py
import pytest

from crucible.xnet import USES, IngestionError, extract, read_pair

# Literal 2-species header: ny=2; Z=(0,1); A=(1,2).
SPECIES = bytes.fromhex(
    "02000000 0000000000000000 000000000000f03f 000000000000f03f 0000000000000040"
)
# One flux from species 1 to species 2 (one-based).
FLUX = bytes.fromhex("01000000 01000000 02000000")
ROWS = [
    bytes.fromhex(
        "00000000 000000000000e03f 0000000000000040 0000000000002040 "
        "0000000000000000 0000000000000000 "
        "000000000000d03f 000000000000e03f 0000000000000840 "
        "000000000000c03f 000000000000d0bf"
    ),
    bytes.fromhex(
        "14000000 000000000000f03f 0000000000000040 0000000000002040 "
        "000000000000c03f 00000000000010c0 "
        "000000000000c03f 000000000000e83f 0000000000001040 "
        "0000000000000000 0000000000000000"
    ),
    bytes.fromhex(
        "14000000 0000000000000040 0000000000000040 0000000000002040 "
        "000000000000d03f 0000000000000000 "
        "000000000000e03f 000000000000d03f 0000000000001440 "
        "0000000000000000 0000000000000000"
    ),
]
# Repeated condensed heading is deliberately unreliable. It cannot rename species.
COMPANION = (
    b"k Time T(GK) Density dE/dt Timestep ge64 ge64 It\n"
    b"0 5.00000000E-01 2.000E+00 8.000E+00 0.00E+00 0.00E+00 9 9 0 0\n"
    b"20 1.00000000E+00 2.000E+00 8.000E+00 -4.00E+00 1.25E-01 9 9 1 2\n"
    b"20 2.00000000E+00 2.000E+00 8.000E+00 0.00E+00 2.50E-01 9 9 NSE\n"
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def wrap(payload):
    marker = len(payload).to_bytes(4, "little", signed=True)
    return marker + payload + marker


def binary(species=SPECIES, flux=FLUX, rows=ROWS):
    return b"".join(
        wrap(p)
        for p in [b" " * 320, b" " * 76, b" " * 160, b" " * 160, species, flux, *rows]
    )


def specification(raw, companion=COMPANION):
    # Intentionally independent literals; do not import supported constants.
    return {
        "alias": "synthetic",
        "ts_path": "ts_test",
        "ev_path": "ev_test",
        "layout": "xnet-ts-le-i32-f64-six-v1",
        "units": {
            "time": "s",
            "temperature": "GK",
            "density": "g/cm^3",
            "internal_dt": "s",
            "Y": "molar_abundance_Y",
            "stored_derivative_unqualified": "molar_abundance_Y/s",
            "stored_energy_rate_unqualified": "erg/g/s",
        },
        "ts_sha256": sha(raw),
        "ev_sha256": sha(companion),
        "expected_species": [[0, 1], [1, 2]],
        "species_header_sha256": sha(SPECIES),
        "expected_nflx": 1,
        "expected_records": 3,
    }


def test_independent_binary_scalar_oracle_and_distinct_reasons():
    result = read_pair(binary(), COMPANION, specification(binary()))
    assert result.species == ((0, 1), (1, 2))
    assert result.headers == (
        (0, 0.5, 2.0, 8.0, 0.0, 0.0),
        (20, 1.0, 2.0, 8.0, 0.125, -4.0),
        (20, 2.0, 2.0, 8.0, 0.25, 0.0),
    )
    assert result.abundances == ((0.25, 0.5), (0.125, 0.75), (0.5, 0.25))
    assert result.derivatives == ((0.125, -0.25), (0.0, 0.0), (0.0, 0.0))
    assert result.marker_offsets == (812, 904, 996)
    assert result.payload_sha256 == tuple(sha(row) for row in ROWS)
    assert result.nse == (False, False, True)  # Ordinary zero derivative is not NSE.
    initial, ordinary, nse = [result.reasons(i, "rhs_training") for i in range(3)]
    assert "initial_output_before_rhs_evaluation" in initial
    assert "accepted_state_rhs_alignment_unverified" in ordinary
    assert "explicit_companion_nse_placeholder" in nse
    assert "explicit_companion_nse_placeholder" not in ordinary
    assert all(
        "unknown_generating_provenance" in reasons
        for reasons in [initial, ordinary, nse]
    )
    assert "internal_step_mass_excess_diagnostic_only" in result.reasons(
        1, "energy_training"
    )
    assert "input_history_association_unverified" in result.reasons(
        1, "rollout_reference"
    )


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (lambda b: b[:-1], "truncated record"),
        (lambda b: b + b"x", "truncated/trailing"),
        (lambda b: b + wrap(b"x"), "record count mismatch"),
        (lambda b: b[:324] + bytes(4) + b[328:], "mismatched record markers"),
        (lambda b: b"\xff\xff\xff\xff" + b[4:], "unsupported record marker"),
        (lambda b: b"\x00\x00\x01\x40" + b[4:], "truncated record"),
    ],
)
def test_bad_framing(mutation, reason):
    raw = mutation(binary())
    with pytest.raises(IngestionError, match=reason):
        read_pair(raw, COMPANION, specification(raw))


@pytest.mark.parametrize(
    "key,value,reason",
    [
        ("layout", "auto", "unsupported layout"),
        ("units", {}, "unknown/incompatible units"),
        ("ts_sha256", "0" * 64, "ts identity mismatch"),
        ("ev_sha256", "0" * 64, "ev identity mismatch"),
        ("species_header_sha256", "0" * 64, "species header identity mismatch"),
        ("expected_species", [[1, 2], [0, 1]], "ordered species mismatch"),
        ("expected_nflx", 2, "unexpected flux dimension"),
        ("expected_records", 2, "record count mismatch"),
    ],
)
def test_explicit_contract_failures(key, value, reason):
    spec = specification(binary())
    spec[key] = value
    with pytest.raises(IngestionError, match=reason):
        read_pair(binary(), COMPANION, spec)


@pytest.mark.parametrize(
    "species,flux,rows,reason",
    [
        (b"\x03\x00\x00\x00" + SPECIES[4:], FLUX, ROWS, "species dimension mismatch"),
        (
            SPECIES[:12] + SPECIES[4:12] + SPECIES[20:28] * 2,
            FLUX,
            ROWS,
            "duplicate species",
        ),
        (SPECIES, FLUX[:-1], ROWS, "flux dimension mismatch"),
        (SPECIES, bytes.fromhex("01000000 00000000 02000000"), ROWS, "flux endpoint"),
        (SPECIES, FLUX, [ROWS[0][:-8], *ROWS[1:]], "unsupported data width"),
        (
            SPECIES,
            FLUX,
            [ROWS[0][:44] + struct.pack("<d", float("nan")) + ROWS[0][52:], *ROWS[1:]],
            "nonfinite dynamics",
        ),
        (SPECIES, FLUX, [ROWS[0], ROWS[0], ROWS[2]], "time not strictly increasing"),
    ],
)
def test_payload_failures(species, flux, rows, reason):
    raw = binary(species, flux, rows)
    with pytest.raises(IngestionError, match=reason):
        read_pair(raw, COMPANION, specification(raw))


@pytest.mark.parametrize(
    "companion,reason",
    [
        (
            COMPANION.replace(b"1.00000000E+00", b"1.00000001E+00"),
            "companion alignment: scalar mismatch",
        ),
        (COMPANION.rsplit(b"\n", 2)[0] + b"\n", "companion alignment: row count"),
        (COMPANION.replace(b"NSE", b"unknown"), "unsupported companion row width"),
        (COMPANION.replace(b"NSE", b"NSE 1"), "ambiguous companion NSE marker"),
        (
            COMPANION.replace(b"k Time", b"k Seconds"),
            "unsupported companion scalar headings",
        ),
    ],
)
def test_companion_failures(companion, reason):
    with pytest.raises(IngestionError, match=reason):
        read_pair(binary(), companion, specification(binary(), companion))


@pytest.fixture
def local_recipe(tmp_path):
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    (raw_root / "ts_test").write_bytes(binary())
    (raw_root / "ev_test").write_bytes(COMPANION)
    resolver = {
        "candidate_root": str(raw_root),
        "derived_root": str(tmp_path / "derived"),
    }
    recipe = {
        "dataset_id": "synthetic-control",
        "dataset_version": "0.1.0",
        "acceptance_reference": "synthetic-public-software-control",
        "pairs": [specification(binary())],
    }
    return resolver, recipe


def test_hdf_manifest_values_membership_and_false_scientific_masks(local_recipe):
    resolver, recipe = local_recipe
    destination = extract(resolver, recipe, "control")
    manifest = json.loads((destination / "manifest.json").read_text())
    assert manifest["recipe"] == recipe
    assert manifest["output"]["sha256"] == sha((destination / "data.h5").read_bytes())
    assert manifest["extractor_source_sha256"] == sha(
        Path(__import__("crucible.xnet", fromlist=["x"]).__file__).read_bytes()
    )
    assert manifest["record_membership"]["synthetic"]["ordinals"] == [0, 1, 2]
    assert manifest["raw_identity_rechecked_after_extraction"] is True
    assert str(resolver["candidate_root"]) not in json.dumps(manifest)
    assert (Path(resolver["candidate_root"]) / "ts_test").read_bytes() == binary()
    with h5py.File(destination / "data.h5", "r") as h5:
        group = h5["synthetic"]
        assert group["Y"][:].tolist() == [[0.25, 0.5], [0.125, 0.75], [0.5, 0.25]]
        assert group["stored_derivative_unqualified"][:].tolist() == [
            [0.125, -0.25],
            [0, 0],
            [0, 0],
        ]
        assert group["internal_dt"][:].tolist() == [0, 0.125, 0.25]
        assert group["species_Z_A"][:].tolist() == [[0, 1], [1, 2]]
        assert group["raw_marker_offset"][:].tolist() == [812, 904, 996]
        assert group["explicit_companion_nse"][:].tolist() == [False, False, True]
        assert group["structurally_readable"][:].all()
        for use in USES:
            assert not group[f"{use}_eligible"][:].any()
            reasons = [
                json.loads(s) for s in group[f"{use}_exclusion_reasons"].asstr()[:]
            ]
            assert all("unknown_generating_provenance" in row for row in reasons)
    with pytest.raises(IngestionError, match="already exists"):
        extract(resolver, recipe, "control")


@pytest.mark.parametrize(
    "failure",
    [
        "raw_destination",
        "symlink_destination",
        "traversal_input",
        "symlink_input",
        "too_many",
        "duplicate",
        "acceptance",
        "bad_name",
    ],
)
def test_safe_bounded_destination_and_membership(tmp_path, local_recipe, failure):
    resolver, recipe = copy.deepcopy(local_recipe)
    name = "control"
    if failure == "raw_destination":
        resolver["derived_root"] = resolver["candidate_root"]
        reason = "overlaps raw root"
    elif failure == "symlink_destination":
        link = tmp_path / "link"
        link.symlink_to(resolver["candidate_root"], target_is_directory=True)
        resolver["derived_root"] = str(link)
        reason = "overlaps raw root"
    elif failure == "traversal_input":
        recipe["pairs"][0]["ts_path"] = "../raw/ts_test"
        reason = "unsafe raw locator"
    elif failure == "symlink_input":
        outside = tmp_path / "outside"
        outside.write_bytes(binary())
        (Path(resolver["candidate_root"]) / "escape").symlink_to(outside)
        recipe["pairs"][0]["ts_path"] = "escape"
        reason = "escapes candidate root"
    elif failure == "too_many":
        recipe["pairs"] *= 4
        reason = "one to three"
    elif failure == "duplicate":
        recipe["pairs"] *= 2
        reason = "invalid/duplicate pair aliases"
    elif failure == "acceptance":
        recipe.pop("acceptance_reference")
        reason = "acceptance reference"
    else:
        name, reason = "../raw", "unsafe output name"
    with pytest.raises(IngestionError, match=reason):
        extract(resolver, recipe, name)
    assert (Path(resolver["candidate_root"]) / "ts_test").read_bytes() == binary()


def test_changed_raw_is_detected_and_failed_output_is_removed(
    local_recipe, monkeypatch
):
    resolver, recipe = local_recipe
    original_file = h5py.File
    raw_path = Path(resolver["candidate_root"]) / "ts_test"

    class ChangeSyntheticRawAfterWrite:
        def __enter__(self):
            self.handle = original_file(self.path, self.mode)
            return self.handle

        def __init__(self, path, mode):
            self.path, self.mode = path, mode

        def __exit__(self, *args):
            self.handle.close()
            raw_path.write_bytes(binary() + b"tampered synthetic input")

    monkeypatch.setattr(h5py, "File", ChangeSyntheticRawAfterWrite)
    with pytest.raises(IngestionError, match="raw identity changed during extraction"):
        extract(resolver, recipe, "failure")
    assert list(Path(resolver["derived_root"]).iterdir()) == []


def test_dangling_existing_output_is_not_overwritten(local_recipe):
    resolver, recipe = local_recipe
    derived = Path(resolver["derived_root"])
    derived.mkdir()
    (derived / "existing").symlink_to(derived / "missing")
    with pytest.raises(IngestionError, match="already exists"):
        extract(resolver, recipe, "existing")
    assert (derived / "existing").is_symlink()


def test_documented_cli_and_actionable_bad_json(tmp_path, local_recipe):
    resolver, recipe = local_recipe
    resolver_path, recipe_path = tmp_path / "resolver.json", tmp_path / "recipe.json"
    resolver_path.write_text(json.dumps(resolver))
    recipe_path.write_text(json.dumps(recipe))
    command = [
        sys.executable,
        "-B",
        "-m",
        "crucible.xnet",
        "--resolver",
        str(resolver_path),
        "--recipe",
        str(recipe_path),
        "--output-name",
        "cli",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert (Path(result.stdout.strip()) / "manifest.json").is_file()
    recipe_path.write_text("{")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "extraction failed:" in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "bad_recipe",
    [
        [],
        {"pairs": [None]},
        {"pairs": [1]},
        {"pairs": "auto"},
        {"pairs": [{"alias": []}]},
    ],
)
def test_malformed_recipe_shapes_are_actionable(local_recipe, bad_recipe):
    resolver, recipe = local_recipe
    if isinstance(bad_recipe, dict):
        recipe.update(bad_recipe)
    else:
        recipe = bad_recipe
    with pytest.raises(IngestionError, match="JSON object|pair aliases"):
        extract(resolver, recipe, "bad-shape")
