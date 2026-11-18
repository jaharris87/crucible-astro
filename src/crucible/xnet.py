"""Strict, quarantined ingestion of the single S02 XNet sequential layout.

No producer code is imported. Successful decoding establishes structure only.
See docs/phase1/S02_READER.md for the supported contract and local recipe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import struct
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

LAYOUT = "xnet-ts-le-i32-f64-six-v1"
UNITS = {
    "time": "s",
    "temperature": "GK",
    "density": "g/cm^3",
    "internal_dt": "s",
    "Y": "molar_abundance_Y",
    "stored_derivative_unqualified": "molar_abundance_Y/s",
    "stored_energy_rate_unqualified": "erg/g/s",
}
USES = ("state_training", "rhs_training", "energy_training", "rollout_reference")


class IngestionError(ValueError):
    """An explicit identity, format or companion-association check failed."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IngestionError(message)


def _records(raw: bytes) -> list[tuple[int, bytes]]:
    records = []
    offset = 0
    while offset < len(raw):
        _require(len(raw) - offset >= 8, f"truncated/trailing framing at byte {offset}")
        size = struct.unpack_from("<i", raw, offset)[0]
        _require(size > 0, f"unsupported record marker at byte {offset}")
        end = offset + 4 + size
        _require(end + 4 <= len(raw), f"truncated record at byte {offset}")
        _require(
            struct.unpack_from("<i", raw, end)[0] == size,
            f"mismatched record markers at byte {offset}",
        )
        records.append((offset, raw[offset + 4 : end]))
        offset = end + 4
    return records


@dataclass(frozen=True)
class DecodedPair:
    """Original binary64 values and verified ordinal companion regime evidence."""

    species: tuple[tuple[int, int], ...]
    species_header_sha256: str
    nflx: int
    marker_offsets: tuple[int, ...]
    payload_sha256: tuple[str, ...]
    headers: tuple[tuple, ...]
    abundances: tuple[tuple[float, ...], ...]
    derivatives: tuple[tuple[float, ...], ...]
    nse: tuple[bool, ...]

    def reasons(self, ordinal: int, use: str) -> list[str]:
        _require(use in USES, "unknown scientific use")
        reasons = ["unknown_generating_provenance", "unverified_physical_conditions"]
        if use == "rollout_reference":
            reasons += [
                "input_history_association_unverified",
                "unverified_parent_grouping",
            ]
        if use in ("rhs_training", "energy_training"):
            if ordinal == 0:
                reasons.append("initial_output_before_rhs_evaluation")
            if self.nse[ordinal]:
                reasons.append("explicit_companion_nse_placeholder")
            if use == "rhs_training" and ordinal != 0 and not self.nse[ordinal]:
                reasons.append("accepted_state_rhs_alignment_unverified")
            if use == "energy_training":
                reasons.append("internal_step_mass_excess_diagnostic_only")
        return reasons


def read_pair(raw: bytes, companion: bytes, specification: dict) -> DecodedPair:
    """Validate explicit identities/layout/units/order; fail on ambiguous companions.

    The six companion scalar columns are compared at their writer's exact printed
    precision, allowing either sign for exactly zero energy. Condensed species
    headings/columns never determine binary identity.
    """
    _require(
        isinstance(specification, dict), "pair specification must be a JSON object"
    )
    _require(specification.get("layout") == LAYOUT, "unsupported layout")
    _require(specification.get("units") == UNITS, "unknown/incompatible units")
    _require(digest(raw) == specification.get("ts_sha256"), "ts identity mismatch")
    _require(
        digest(companion) == specification.get("ev_sha256"), "ev identity mismatch"
    )
    records = _records(raw)
    _require(len(records) >= 7, "six metadata records and data required")
    _require(
        [len(p) for _, p in records[:4]] == [320, 76, 160, 160],
        "unsupported first four metadata widths",
    )
    species_header = records[4][1]
    _require(len(species_header) >= 4, "truncated species header")
    ny = struct.unpack_from("<i", species_header)[0]
    _require(
        ny > 0 and len(species_header) == 4 + 16 * ny, "species dimension mismatch"
    )
    values = struct.unpack_from(f"<{2 * ny}d", species_header, 4)
    _require(
        all(math.isfinite(x) and x.is_integer() for x in values),
        "nonintegral/nonfinite species identity",
    )
    species = tuple(zip(map(int, values[:ny]), map(int, values[ny:]), strict=True))
    _require(
        all(0 <= z <= a <= 2**31 - 1 and a > 0 for z, a in species),
        "invalid Z/A identity",
    )
    _require(len(set(species)) == ny, "duplicate species identity")
    _require(
        [list(s) for s in species] == specification.get("expected_species"),
        "ordered species mismatch",
    )
    _require(
        digest(species_header) == specification.get("species_header_sha256"),
        "species header identity mismatch",
    )
    flux_header = records[5][1]
    _require(len(flux_header) >= 4, "truncated flux header")
    nflx = struct.unpack_from("<i", flux_header)[0]
    _require(
        nflx >= 0 and len(flux_header) == 4 + 8 * nflx,
        "flux dimension mismatch",
    )
    _require(nflx == specification.get("expected_nflx"), "unexpected flux dimension")
    endpoints = struct.unpack_from(f"<{2 * nflx}i", flux_header, 4)
    _require(all(1 <= i <= ny for i in endpoints), "flux endpoint outside species")
    data = records[6:]
    _require(
        len(data) == specification.get("expected_records"), "record count mismatch"
    )
    headers, abundances, derivatives = [], [], []
    for ordinal, (_, payload) in enumerate(data):
        _require(
            len(payload) == 44 + 8 * (2 * ny + nflx),
            f"unsupported data width at ordinal {ordinal}",
        )
        header = struct.unpack_from("<i5d", payload)
        vector = struct.unpack_from(f"<{2 * ny + nflx}d", payload, 44)
        _require(
            all(math.isfinite(x) for x in (*header[1:], *vector)),
            f"nonfinite dynamics at ordinal {ordinal}",
        )
        _require(header[0] >= 0, f"negative step at ordinal {ordinal}")
        _require(header[2] > 0 and header[3] > 0, "nonpositive temperature/density")
        _require(header[4] >= 0, "negative internal dt")
        _require(
            not headers or header[1] > headers[-1][1],
            f"time not strictly increasing at ordinal {ordinal}",
        )
        headers.append(header)
        abundances.append(vector[:ny])
        derivatives.append(vector[ny + nflx :])
    _require(headers[0][0] == 0, "missing initial step-zero output")
    try:
        lines = companion.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise IngestionError("non-ASCII companion") from exc
    _require(len(lines) == len(data) + 1, "companion alignment: row count mismatch")
    _require(
        lines[0].split()[:6] == ["k", "Time", "T(GK)", "Density", "dE/dt", "Timestep"],
        "unsupported companion scalar headings",
    )
    headings = lines[0].split()
    _require(
        len(headings) >= 7 and headings[-1] == "It",
        "unsupported companion tail heading",
    )
    condensed_count = len(headings) - 7
    nse = []
    for ordinal, (h, line) in enumerate(zip(headers, lines[1:], strict=True)):
        fields = line.split()
        expected = [
            str(h[0]),
            f"{h[1]:.8E}",
            f"{h[2]:.3E}",
            f"{h[3]:.3E}",
            f"{h[5]:.2E}",
            f"{h[4]:.2E}",
        ]
        # The text writer can discard the sign of an exactly zero energy value.
        # Accept only its two zero spellings; retain the binary header unchanged.
        if h[5] == 0.0 and len(fields) > 4 and fields[4] in {"0.00E+00", "-0.00E+00"}:
            expected[4] = fields[4]
        _require(
            fields[:6] == expected,
            f"companion alignment: scalar mismatch at ordinal {ordinal}",
        )
        _require("NSE" not in fields[:-1], "ambiguous companion NSE marker")
        is_nse = fields[-1] == "NSE"
        _require(
            len(fields) == 6 + condensed_count + (1 if is_nse else 2),
            f"unsupported companion row width at ordinal {ordinal}",
        )
        try:
            condensed = [float(v) for v in fields[6 : 6 + condensed_count]]
            _require(
                all(math.isfinite(v) for v in condensed), "nonfinite companion values"
            )
            if not is_nse:
                _require(
                    all(int(v) >= 0 for v in fields[-2:]),
                    "invalid companion iteration counts",
                )
        except ValueError as exc:
            raise IngestionError(
                f"unsupported companion tail at ordinal {ordinal}"
            ) from exc
        nse.append(is_nse)
    return DecodedPair(
        species,
        digest(species_header),
        nflx,
        tuple(o for o, _ in data),
        tuple(digest(p) for _, p in data),
        tuple(headers),
        tuple(abundances),
        tuple(derivatives),
        tuple(nse),
    )


def _relative_input(root: Path, name: str) -> Path:
    _require(isinstance(name, str), "raw locator must be a relative string")
    relative = Path(name)
    _require(
        not relative.is_absolute() and ".." not in relative.parts, "unsafe raw locator"
    )
    path = (root / relative).resolve()
    _require(path.is_relative_to(root), "raw locator escapes candidate root")
    _require(path.is_file(), "raw input is not a file")
    return path


def extract(resolver: dict, recipe: dict, output_name: str) -> Path:
    """Extract at most the explicitly selected three pairs to a fresh local folder.

    The resolver supplies candidate_root and derived_root. Only relative raw
    locators enter the recipe/manifest. Existing outputs are never overwritten.
    """
    import h5py
    import numpy as np

    _require(
        re.fullmatch(r"[A-Za-z0-9_-]+", output_name) is not None, "unsafe output name"
    )
    _require(
        isinstance(resolver, dict)
        and all(
            isinstance(resolver.get(k), str) and Path(resolver[k]).is_absolute()
            for k in ("candidate_root", "derived_root")
        ),
        "resolver must provide absolute candidate_root and derived_root strings",
    )
    _require(isinstance(recipe, dict), "recipe must be a JSON object")
    root = Path(resolver["candidate_root"]).resolve(strict=True)
    derived = Path(resolver["derived_root"]).resolve()
    destination = derived / output_name
    _require(
        not destination.is_relative_to(root) and not root.is_relative_to(destination),
        "derived destination overlaps raw root",
    )
    _require(
        not destination.exists() and not destination.is_symlink(),
        "derived destination already exists",
    )
    _require(
        all(
            isinstance(recipe.get(k), str) and recipe[k]
            for k in ("dataset_id", "dataset_version")
        ),
        "derived dataset identity/version required",
    )
    pairs = recipe.get("pairs", [])
    _require(
        isinstance(pairs, list)
        and 1 <= len(pairs) <= 3
        and all(isinstance(pair, dict) for pair in pairs),
        "bounded extraction requires one to three pairs as JSON objects",
    )
    aliases = [p.get("alias", "") for p in pairs]
    _require(
        all(isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_-]+", x) for x in aliases)
        and len(set(aliases)) == len(pairs),
        "invalid/duplicate pair aliases",
    )
    _require(
        isinstance(recipe.get("acceptance_reference"), str)
        and bool(recipe["acceptance_reference"]),
        "acceptance reference required",
    )
    inputs, decoded = [], []
    for pair in pairs:
        ts = _relative_input(root, pair["ts_path"])
        ev = _relative_input(root, pair["ev_path"])
        raw, companion = ts.read_bytes(), ev.read_bytes()
        decoded.append(read_pair(raw, companion, pair))
        inputs.extend([(ts, digest(raw)), (ev, digest(companion))])
    _require(
        len({p for p, _ in inputs}) == len(inputs), "duplicate raw pair membership"
    )
    derived.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_name}-", dir=derived))
    try:
        output = temporary / "data.h5"
        with h5py.File(output, "x") as h5:
            h5.attrs["schema"] = "crucible-quarantined-xnet-v1"
            h5.attrs["scientific_qualification"] = "none"
            h5.attrs["energy_semantics"] = (
                "signed internal-step mass-excess change rate"
            )
            for pair, result in zip(pairs, decoded, strict=True):
                group = h5.create_group(pair["alias"])
                group.attrs["physical_parent_identity"] = "unknown"
                group.attrs["nflx"] = result.nflx
                group.attrs["ts_sha256"] = pair["ts_sha256"]
                group.attrs["ev_sha256"] = pair["ev_sha256"]
                group.attrs["generating_provenance"] = "unknown"
                group.attrs["physical_conditioning_contract"] = "unqualified"
                group.attrs["species_header_sha256"] = result.species_header_sha256
                group.create_dataset("species_Z_A", data=result.species, dtype="<i4")
                count = len(result.headers)
                group.create_dataset("record_ordinal", data=range(count), dtype="<i8")
                group.create_dataset(
                    "raw_marker_offset", data=result.marker_offsets, dtype="<i8"
                )
                group.create_dataset(
                    "step", data=[h[0] for h in result.headers], dtype="<i4"
                )
                for column, name in enumerate(
                    [
                        "time",
                        "temperature",
                        "density",
                        "internal_dt",
                        "stored_energy_rate_unqualified",
                    ],
                    1,
                ):
                    ds = group.create_dataset(
                        name, data=[h[column] for h in result.headers], dtype="<f8"
                    )
                    ds.attrs["units"] = UNITS[name]
                for name, values in [
                    ("Y", result.abundances),
                    ("stored_derivative_unqualified", result.derivatives),
                ]:
                    ds = group.create_dataset(name, data=values, dtype="<f8")
                    ds.attrs["units"] = UNITS[name]
                group.create_dataset(
                    "explicit_companion_nse", data=result.nse, dtype="?"
                )
                group.create_dataset(
                    "companion_scalar_aligned", data=[True] * count, dtype="?"
                )
                group.create_dataset(
                    "structurally_readable", data=[True] * count, dtype="?"
                )
                string_type = h5py.string_dtype("utf-8")
                group.create_dataset(
                    "raw_payload_sha256", data=result.payload_sha256, dtype=string_type
                )
                for use in USES:
                    group.create_dataset(
                        f"{use}_eligible", data=[False] * count, dtype="?"
                    )
                    group.create_dataset(
                        f"{use}_exclusion_reasons",
                        data=[json.dumps(result.reasons(i, use)) for i in range(count)],
                        dtype=string_type,
                    )
        for path, expected in inputs:
            _require(
                digest(path.read_bytes()) == expected,
                "raw identity changed during extraction",
            )
        manifest = {
            "schema": "crucible-quarantined-xnet-v1",
            "dataset_id": recipe["dataset_id"],
            "dataset_version": recipe["dataset_version"],
            "scientific_qualification": "none",
            "validity_policy": "all scientific eligibility false; structural checks are separate",
            "unknowns": [
                "generating_source_build",
                "physical_parent_identity",
                "generating_input_association",
                "dataset_rights",
            ],
            "extractor_source_sha256": digest(Path(__file__).read_bytes()),
            "environment": {
                "python": sys.version.split()[0],
                "h5py": h5py.__version__,
                "numpy": np.__version__,
            },
            "recipe": recipe,
            "recipe_sha256": digest(
                json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
            ),
            "record_membership": {
                p["alias"]: {
                    "ordinals": list(range(len(d.headers))),
                    "ts_sha256": p["ts_sha256"],
                }
                for p, d in zip(pairs, decoded, strict=True)
            },
            "output": {"path": "data.h5", "sha256": digest(output.read_bytes())},
            "raw_identity_rechecked_after_extraction": True,
        }
        (temporary / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        _require(
            not destination.exists() and not destination.is_symlink(),
            "derived destination appeared during extraction",
        )
        temporary.rename(destination)
    except BaseException:
        shutil.rmtree(temporary)
        raise
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolver", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--output-name", required=True)
    args = parser.parse_args()
    try:
        result = extract(
            json.loads(args.resolver.read_text()),
            json.loads(args.recipe.read_text()),
            args.output_name,
        )
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"extraction failed: {exc}\n")
    print(result)


if __name__ == "__main__":
    main()
