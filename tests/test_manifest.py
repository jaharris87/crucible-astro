"""Independent controls for the synthetic B04 contract, not physical validity."""

import hashlib
import json
from pathlib import Path

import pytest

from crucible.manifest import ManifestValidationError, validate_manifest

FIXTURES = Path(__file__).parent / "fixtures" / "manifest"


def write_case(tmp_path, *, manifest_changes=None, payload_changes=None):
    manifest = json.loads((FIXTURES / "valid.json").read_text())
    payload_bytes = (FIXTURES / "payload.json").read_bytes()
    if payload_changes is not None:
        payload = json.loads(payload_bytes)
        payload.update(payload_changes)
        payload_bytes = json.dumps(payload).encode()
        manifest["payload_sha256"] = hashlib.sha256(payload_bytes).hexdigest()
    if manifest_changes:
        manifest.update(manifest_changes)
    (tmp_path / "payload.json").write_bytes(payload_bytes)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest))
    return path


def assert_failure(path, code):
    with pytest.raises(ManifestValidationError) as caught:
        validate_manifest(path)
    assert caught.value.code == code
    return str(caught.value)


def test_valid_manifest():
    assert validate_manifest(FIXTURES / "valid.json") == {
        "fixture_id": "synthetic-sentinels-v1",
        "species": ["sentinel_alpha", "sentinel_beta", "sentinel_gamma"],
        "shape": [2, 3],
        "payload_sha256": "96e260dbc926fff7f3060e3f227ae76d3a5076bc0349258555f642e5430057b7",
    }


def test_manifest_order_mismatch():
    valid = json.loads((FIXTURES / "valid.json").read_text())
    negative = json.loads((FIXTURES / "negative/order-manifest.json").read_text())
    assert {key: value for key, value in negative.items() if key != "species"} == {
        key: value for key, value in valid.items() if key != "species"
    }
    assert negative["species"] != valid["species"]
    assert set(negative["species"]) == set(valid["species"])
    payload = (FIXTURES / "payload.json").read_bytes()
    assert (FIXTURES / "negative/payload.json").read_bytes() == payload
    assert hashlib.sha256(payload).hexdigest() == negative["payload_sha256"]
    assert validate_manifest(FIXTURES / "valid.json")["shape"] == [2, 3]
    message = assert_failure(
        FIXTURES / "negative/order-manifest.json", "order_mismatch"
    )
    assert "position 0: expected 'sentinel_beta', observed 'sentinel_alpha'" in message
    assert "position 1: expected 'sentinel_alpha', observed 'sentinel_beta'" in message


@pytest.mark.parametrize("side", ["manifest", "payload"])
def test_duplicate_identity(tmp_path, side):
    identities = ["sentinel_alpha", "sentinel_alpha", "sentinel_gamma"]
    kwargs = (
        {"manifest_changes": {"species": identities}}
        if side == "manifest"
        else {"payload_changes": {"columns": identities}}
    )
    assert_failure(write_case(tmp_path, **kwargs), "duplicate_identity")


def test_missing_identity(tmp_path):
    path = write_case(tmp_path, manifest_changes={"species": ["sentinel_alpha"]})
    message = assert_failure(path, "identity_mismatch")
    assert "unexpected=['sentinel_beta', 'sentinel_gamma']" in message


def test_checksum_uses_actual_bytes(tmp_path):
    path = write_case(tmp_path)
    with (tmp_path / "payload.json").open("ab") as stream:
        stream.write(b" ")
    assert_failure(path, "checksum_mismatch")


@pytest.mark.parametrize("version", [2, True, "1"])
def test_unsupported_schema(tmp_path, version):
    assert_failure(
        write_case(tmp_path, manifest_changes={"schema_version": version}),
        "unsupported_schema",
    )


@pytest.mark.parametrize(
    "changes, code",
    [
        ({"fixture_id": ""}, "invalid_manifest"),
        ({"species": []}, "invalid_manifest"),
        ({"species": ["sentinel_alpha", "", "sentinel_gamma"]}, "invalid_manifest"),
        ({"shape": [True, 3]}, "invalid_manifest"),
        ({"shape": [2, 0]}, "invalid_manifest"),
        ({"shape": [2, 3, 1]}, "invalid_manifest"),
        ({"shape": [3, 3]}, "shape_mismatch"),
        ({"shape": [2, 2]}, "shape_mismatch"),
        ({"payload": "../payload.json"}, "invalid_manifest"),
        ({"payload": "/payload.json"}, "invalid_manifest"),
        ({"payload": "sub\\payload.json"}, "invalid_manifest"),
        ({"payload_sha256": "bad"}, "invalid_manifest"),
        ({"units": "g/cm3"}, "invalid_manifest"),
        ({"state_convention": "mass_fraction"}, "invalid_manifest"),
    ],
)
def test_manifest_contract(tmp_path, changes, code):
    assert_failure(write_case(tmp_path, manifest_changes=changes), code)


@pytest.mark.parametrize(
    "changes, code",
    [
        (
            {"columns": ["other", "sentinel_beta", "sentinel_gamma"]},
            "identity_mismatch",
        ),
        ({"columns": "sentinel_alpha"}, "invalid_payload"),
        ({"values": [[11, 22, 33], [44, 55]]}, "shape_mismatch"),
        ({"values": [[11, 22, 33]]}, "shape_mismatch"),
        ({"values": "bad"}, "invalid_payload"),
        ({"values": [[True, 22, 33], [44, 55, 66]]}, "invalid_payload"),
        ({"values": [["11", 22, 33], [44, 55, 66]]}, "invalid_payload"),
        ({"values": [[float("inf"), 22, 33], [44, 55, 66]]}, "invalid_payload"),
    ],
)
def test_payload_contract(tmp_path, changes, code):
    assert_failure(write_case(tmp_path, payload_changes=changes), code)


def test_missing_required_field(tmp_path):
    path = write_case(tmp_path)
    manifest = json.loads(path.read_text())
    del manifest["species"]
    path.write_text(json.dumps(manifest))
    assert_failure(path, "invalid_manifest")


def test_missing_payload(tmp_path):
    path = write_case(tmp_path)
    (tmp_path / "payload.json").unlink()
    assert_failure(path, "file_read_error")


def test_symlink_payload(tmp_path):
    path = write_case(tmp_path)
    (tmp_path / "payload.json").rename(tmp_path / "actual.json")
    (tmp_path / "payload.json").symlink_to("actual.json")
    assert_failure(path, "invalid_manifest")


@pytest.mark.parametrize("contents", [b"{", b"\xff", b"[]"])
def test_invalid_manifest_json(tmp_path, contents):
    path = tmp_path / "manifest.json"
    path.write_bytes(contents)
    assert_failure(path, "invalid_json" if contents != b"[]" else "invalid_manifest")


def test_invalid_payload_json(tmp_path):
    path = write_case(tmp_path)
    payload_bytes = b"{"
    (tmp_path / "payload.json").write_bytes(payload_bytes)
    manifest = json.loads(path.read_text())
    manifest["payload_sha256"] = hashlib.sha256(payload_bytes).hexdigest()
    path.write_text(json.dumps(manifest))
    assert_failure(path, "invalid_json")


@pytest.mark.parametrize("filename", ["manifest.json", "payload.json"])
def test_bounded_reads(tmp_path, filename):
    path = write_case(tmp_path)
    (tmp_path / filename).write_bytes(b" " * (1024 * 1024 + 1))
    assert_failure(path, "file_too_large")
