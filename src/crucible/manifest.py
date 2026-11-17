"""Validate the B04 synthetic manifest, without inferring physical semantics."""

import hashlib
import json
import math
from pathlib import Path

_MAX_BYTES = 1024 * 1024


class ManifestValidationError(ValueError):
    """A validation failure with a stable reason code and readable diagnostic."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"{code}: {message}")


def _read_bytes(path):
    try:
        if not path.is_file():
            raise OSError("not a regular file")
        with path.open("rb") as stream:
            data = stream.read(_MAX_BYTES + 1)
    except OSError as error:
        raise ManifestValidationError(
            "file_read_error", f"cannot read {path.name!r}"
        ) from error
    if len(data) > _MAX_BYTES:
        raise ManifestValidationError("file_too_large", f"{path.name!r} exceeds 1 MiB")
    return data


def _decode_object(data, code):
    try:
        value = json.loads(data.decode("utf-8"))
    except (ValueError, RecursionError) as error:
        raise ManifestValidationError("invalid_json", "expected UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise ManifestValidationError(code, "expected a JSON object")
    return value


def _identities(value, name, code):
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ManifestValidationError(code, f"{name} must be nonempty identity strings")
    if len(set(value)) != len(value):
        raise ManifestValidationError("duplicate_identity", f"duplicate in {name}")
    return value


def validate_manifest(path):
    """Return fixture identity/shape/hash, or raise ManifestValidationError.

    Only synthetic manifest schema v1 is supported. Expected species order is
    declared by the manifest; observed columns are independently in the payload.
    See docs/bootstrap/B04-CONTRACT.md. Success does not establish physical validity.
    """
    path = Path(path)
    manifest = _decode_object(_read_bytes(path), "invalid_manifest")
    version = manifest.get("schema_version")
    if type(version) is not int or version != 1:
        raise ManifestValidationError("unsupported_schema", "schema_version must be 1")
    fixture_id = manifest.get("fixture_id")
    if not isinstance(fixture_id, str) or not fixture_id:
        raise ManifestValidationError("invalid_manifest", "fixture_id must be nonempty")
    species = _identities(manifest.get("species"), "species", "invalid_manifest")
    shape = manifest.get("shape")
    if (
        not isinstance(shape, list)
        or len(shape) != 2
        or any(type(size) is not int or size <= 0 for size in shape)
    ):
        raise ManifestValidationError(
            "invalid_manifest", "shape must be [rows, columns]"
        )
    for field, expected in (
        ("units", "synthetic_dimensionless"),
        ("state_convention", "synthetic_sentinel"),
    ):
        if manifest.get(field) != expected:
            raise ManifestValidationError(
                "invalid_manifest", f"{field} must be {expected}"
            )
    checksum = manifest.get("payload_sha256")
    if (
        not isinstance(checksum, str)
        or len(checksum) != 64
        or any(character not in "0123456789abcdef" for character in checksum)
    ):
        raise ManifestValidationError("invalid_manifest", "invalid payload_sha256")
    filename = manifest.get("payload")
    if (
        not isinstance(filename, str)
        or not filename
        or filename in {".", ".."}
        or any(character in filename for character in ("/", "\\", "\x00"))
        or Path(filename).is_absolute()
    ):
        raise ManifestValidationError(
            "invalid_manifest", "payload must be a sibling name"
        )
    payload_path = path.parent / filename
    if payload_path.is_symlink():
        raise ManifestValidationError(
            "invalid_manifest", "payload must not be a symlink"
        )
    payload_bytes = _read_bytes(payload_path)
    if hashlib.sha256(payload_bytes).hexdigest() != checksum:
        raise ManifestValidationError(
            "checksum_mismatch", "actual payload bytes differ"
        )
    payload = _decode_object(payload_bytes, "invalid_payload")
    columns = _identities(payload.get("columns"), "columns", "invalid_payload")
    missing = [identity for identity in species if identity not in columns]
    unexpected = [identity for identity in columns if identity not in species]
    if missing or unexpected:
        raise ManifestValidationError(
            "identity_mismatch", f"missing={missing!r}; unexpected={unexpected!r}"
        )
    if species != columns:
        mismatches = [
            f"position {index}: expected {expected!r}, observed {observed!r}"
            for index, (expected, observed) in enumerate(zip(species, columns))
            if expected != observed
        ]
        raise ManifestValidationError("order_mismatch", "; ".join(mismatches))
    values = payload.get("values")
    if not isinstance(values, list) or any(not isinstance(row, list) for row in values):
        raise ManifestValidationError("invalid_payload", "values must be a matrix")
    if shape != [len(values), len(columns)] or any(
        len(row) != shape[1] for row in values
    ):
        raise ManifestValidationError(
            "shape_mismatch", "declared and actual shapes differ"
        )
    if any(
        not (type(value) is int or (type(value) is float and math.isfinite(value)))
        for row in values
        for value in row
    ):
        raise ManifestValidationError(
            "invalid_payload", "values must be finite numbers"
        )
    return {
        "fixture_id": fixture_id,
        "species": species,
        "shape": shape,
        "payload_sha256": checksum,
    }
