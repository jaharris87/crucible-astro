"""Materialize the quarantined source-PR-20 v2 native-RHS audit, never execute it."""

import argparse
import hashlib
import json
import math
import platform
import re
import struct
from importlib.metadata import version
from pathlib import Path

SCHEMA = "crucible.native-rhs-materialization.v1"
UNITS = {
    "time": "s",
    "T9": "GK",
    "rho": "g/cm^3",
    "internal_dt": "s",
    "Y": "molar_abundance_Y",
    "fresh_rhs": "molar_abundance_Y/s",
    "stored_dY_unqualified": "molar_abundance_Y/s",
    "stored_energy_unqualified": "erg/g/s",
    "native_EOS_Ye": "dimensionless",
}
REASONS = {
    "state_training": "scientific_state_qualification_not_accepted",
    "rhs_training": "coefficient_conditioned_reference_only_scientific_accuracy_not_accepted",
    "energy_training": "stored_internal_step_diagnostic_not_qualified_energy_target",
    "rollout_reference": "pointwise_reference_no_integration_or_history_qualification",
}
NY, NC, HEADER_SIZE, STATE_SIZE, RESULT_SIZE = 160, 2048, 2576, 2620, 21600
PREFIX = struct.Struct("<5i5d")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_load(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def finite_float(value):
        result = float(value)
        require(math.isfinite(result), "nonfinite JSON number")
        return result

    return json.loads(
        data,
        object_pairs_hook=unique,
        parse_float=finite_float,
        parse_constant=lambda value: require(False, f"nonfinite JSON: {value}"),
    )


def regular_path(value):
    p = Path(value)
    require(p.is_absolute(), "absolute paths required")
    require(".." not in p.parts, "parent traversal refused")
    require(not any(q.is_symlink() for q in (p, *p.parents)), "symlink path refused")
    return p


def checked(entry):
    require(set(entry) == {"path", "sha256"}, "input requires path and sha256")
    p = regular_path(entry["path"])
    require(re.fullmatch("[0-9a-f]{64}", entry["sha256"]) is not None, "invalid sha256")
    require(p.is_file(), f"missing input: {p.name}")
    before = p.stat()
    data = p.read_bytes()
    after = p.stat()
    require(
        (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        == (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns),
        f"input changed during read: {p.name}",
    )
    require(digest(data) == entry["sha256"], f"input checksum mismatch: {p.name}")
    return data


def f64(data):
    require(len(data) % 8 == 0, "invalid binary64 width")
    values = struct.unpack(f"<{len(data) // 8}d", data)
    require(all(math.isfinite(v) for v in values), "nonfinite binary64")
    return values


def json_bits(values, raw, name):
    require(
        isinstance(values, list) and len(values) * 8 == len(raw), f"{name} dimension"
    )
    require(
        all(type(v) in (int, float) and math.isfinite(v) for v in values),
        f"{name} nonfinite/type",
    )
    require(struct.pack(f"<{len(values)}d", *values) == raw, f"{name} JSON/binary bits")


def materialize(config_path, destination):
    """Validate all parents, write one new directory containing HDF5 and manifest.

    Input digests are supplied explicitly, not inferred from whatever files exist.
    Successful verification is engineering evidence; every scientific mask is false.
    """
    config_path = regular_path(config_path)
    config_bytes = config_path.read_bytes()
    c = json_load(config_bytes)
    require(
        set(c) == {"schema", "dataset_id", "dataset_version", "inputs", "expected"}
        and c["schema"] == SCHEMA,
        "unsupported configuration schema/keys",
    )
    require(
        all(isinstance(c[k], str) and c[k] for k in ("dataset_id", "dataset_version")),
        "dataset identity required",
    )
    inputs = c["inputs"]
    require(
        set(inputs)
        == {
            "preparation",
            "states",
            "selection",
            "fresh",
            "components",
            "comparison",
            "executable",
        },
        "exact audit input closure required",
    )
    paths = [regular_path(e["path"]) for e in inputs.values()]
    require(len(set(paths)) == len(paths), "input path collision")
    dest = regular_path(destination)
    require(
        config_path != dest and not config_path.is_relative_to(dest),
        "destination collides with recipe",
    )
    require(not dest.exists(), "destination already exists")
    require(dest.parent.is_dir(), "destination parent must exist")
    require(
        all(
            not dest.is_relative_to(p.parent) and not p.is_relative_to(dest)
            for p in paths
        ),
        "destination collides with immutable input parent",
    )
    data = {key: checked(entry) for key, entry in inputs.items()}
    e = c["expected"]
    require(
        set(e) == {"count", "species_Z_A", "units", "exact_controls"}, "expected keys"
    )
    n = e["count"]
    require(type(n) is int and n > 0, "positive state count required")
    require(e["units"] == UNITS, "unit contract mismatch")
    species = e["species_Z_A"]
    require(
        isinstance(species, list)
        and len(species) == NY
        and all(
            isinstance(s, list)
            and len(s) == 2
            and all(type(v) is int for v in s)
            and 0 <= s[0] <= s[1]
            and s[1] > 0
            for s in species
        )
        and len({tuple(s) for s in species}) == NY,
        "invalid ordered species/dimensions",
    )
    controls = e["exact_controls"]
    require(
        isinstance(controls, list)
        and len(controls) == 2
        and all(type(v) is int and 1 <= v <= n for v in controls)
        and len(set(controls)) == 2,
        "two distinct expected controls required",
    )
    prep = json_load(data["preparation"])
    require(
        prep["schema"] == "crucible.rhs-reference-preparation.v1"
        and prep["selection_count"] == n,
        "preparation identity/count",
    )
    for key, filename in (("states", "states.bin"), ("selection", "selection.json")):
        require(
            prep["files"][filename]
            == {"bytes": len(data[key]), "sha256": inputs[key]["sha256"]},
            f"preparation ancestry: {key}",
        )
    comparison = json_load(data["comparison"])
    require(
        comparison["status"]
        == "Completed comparisons only; scientific qualification remains false"
        and comparison["training_eligibility"] is False,
        "comparison incomplete/failed or eligibility changed",
    )
    for field, key in (
        ("manifest_sha256", "preparation"),
        ("fresh_sha256", "fresh"),
        ("components_sha256", "components"),
        ("executable_sha256", "executable"),
    ):
        require(
            comparison[field] == inputs[key]["sha256"], f"comparison ancestry: {key}"
        )
    require(
        comparison["D017_exact_bit_controls"] == controls, "exact controls mismatch"
    )
    require(
        bool(comparison["runtime_shared_libraries_sha256"]),
        "missing runtime library provenance",
    )
    states, fresh = data["states"], data["fresh"]
    require(len(states) == HEADER_SIZE + n * STATE_SIZE, "truncated/trailing states")
    require(len(fresh) == HEADER_SIZE + n * RESULT_SIZE, "truncated/trailing fresh")
    require(
        struct.unpack_from("<4i", states) == (0x43525543, 2, n, NY),
        "state header/count/version",
    )
    require(
        fresh[:HEADER_SIZE] == states[:HEADER_SIZE], "result header/species mismatch"
    )
    z, a = f64(states[16:1296]), f64(states[1296:2576])
    require(list(zip(z, a)) == [tuple(s) for s in species], "ordered species mismatch")
    selection = json_load(data["selection"])
    lines = data["components"].splitlines()
    require(isinstance(selection, list) and len(selection) == n, "selection count")
    require(len(lines) == n and all(lines), "incomplete/trailing components")
    arrays = {
        name: []
        for name in ("sequence", "row_id", "tracer_id", "raw_ordinal", "step", *UNITS)
    }
    record_ids = set()
    raw_parents = {}
    for k, (sel, line) in enumerate(zip(selection, lines, strict=True), 1):
        state = states[
            HEADER_SIZE + (k - 1) * STATE_SIZE : HEADER_SIZE + k * STATE_SIZE
        ]
        result = fresh[
            HEADER_SIZE + (k - 1) * RESULT_SIZE : HEADER_SIZE + k * RESULT_SIZE
        ]
        seq, row, tracer, ordinal, step, time, t9, rho, dt, energy = PREFIX.unpack_from(
            state
        )
        require(
            seq == k and min(row, tracer, ordinal, step) > 0,
            f"state sequence/identity: {k}",
        )
        f64(state[20:])
        require(
            result[:60] == state[:60] and result[60:84] == state[20:44],
            f"scalar echo: {k}",
        )
        ye = f64(result[84:92])[0]
        require(
            ye > 0 and struct.unpack_from("<i", result, 92)[0] == 1,
            f"native Ye/weak flag: {k}",
        )
        y, stored = state[60:1340], state[1340:2620]
        new, coefficients = result[3936:5216], result[5216:]
        require(
            result[96:1376] == y == result[1376:2656] and result[2656:3936] == stored,
            f"array echo: {k}",
        )
        f64(new)
        require(len(f64(coefficients)) == NC, "coefficient dimension")
        require(
            set(sel)
            == {
                "sequence",
                "ordinal",
                "record_id",
                "raw_ts_sha256",
                "raw_ev_sha256",
                "raw_payload_sha256",
                "input_state_sha256",
            },
            f"selection fields: {k}",
        )
        require(
            type(sel["sequence"]) is int
            and type(sel["ordinal"]) is int
            and sel["sequence"] == k
            and sel["ordinal"] == ordinal,
            f"selection sequence/ordinal: {k}",
        )
        record_id = f"Run_slab_{row:03d}/Run/ts_{tracer}#{ordinal}"
        require(
            sel["record_id"] == record_id and record_id not in record_ids,
            f"raw record identity: {k}",
        )
        record_ids.add(record_id)
        require(
            sel["input_state_sha256"] == digest(state[:1340]),
            f"input state ancestry: {k}",
        )
        require(
            all(
                isinstance(sel[f], str) and re.fullmatch("[0-9a-f]{64}", sel[f])
                for f in ("raw_ts_sha256", "raw_ev_sha256", "raw_payload_sha256")
            ),
            f"raw ancestry hashes: {k}",
        )
        pair = (row, tracer)
        hashes = (sel["raw_ts_sha256"], sel["raw_ev_sha256"])
        require(
            raw_parents.setdefault(pair, hashes) == hashes,
            f"inconsistent raw ancestry: {k}",
        )
        component = json_load(line)
        require(
            type(component["sequence"]) is int
            and component["sequence"] == k
            and component["state_bits_unchanged"] is True
            and component["training_eligibility"] is False,
            f"component identity/verification: {k}",
        )
        for name, raw in (("Y", y), ("stored_dY", stored), ("fresh_dY", new)):
            json_bits(component[name], raw, name)
        json_bits([component["composition_EOS_Ye"]], result[84:92], "native Ye")
        require(
            component["fresh_sha256"] == digest(new)
            and component["coefficients_sha256"] == digest(coefficients),
            f"component payload identity: {k}",
        )
        check = component["conditional_assembly"]
        require(
            check["conditional_assembly_check"] is True
            and check["scientific_accuracy_acceptance"] is False,
            f"failed conditional verification: {k}",
        )
        for rr, bb, length in (
            (
                check["component_absolute_residual"],
                check["component_absolute_bound"],
                NY,
            ),
            (
                [check["fresh_baryon_absolute_residual"]],
                [check["baryon_absolute_bound"]],
                1,
            ),
        ):
            require(
                isinstance(rr, list)
                and isinstance(bb, list)
                and len(rr) == len(bb) == length,
                "verification dimension",
            )
            require(
                all(
                    type(r) in (int, float)
                    and type(b) in (int, float)
                    and math.isfinite(r)
                    and math.isfinite(b)
                    and 0 <= r <= b
                    for r, b in zip(rr, bb, strict=True)
                ),
                "failed/nonfinite verification bound",
            )
        values = (
            k,
            row,
            tracer,
            ordinal,
            step,
            time,
            t9,
            rho,
            dt,
            f64(y),
            f64(new),
            f64(stored),
            energy,
            ye,
        )
        for name, value in zip(arrays, values, strict=True):
            arrays[name].append(value)
    # Verify retained inputs again before committing any output; no kernel/math audit rerun.
    for entry in inputs.values():
        checked(entry)
    import h5py

    dest.mkdir()
    output = dest / "dataset.h5"
    with h5py.File(output, "x") as h:
        h.attrs.update(
            schema=SCHEMA,
            dataset_id=c["dataset_id"],
            dataset_version=c["dataset_version"],
        )
        h.create_dataset("species_Z_A", data=species, dtype="<i4")
        for name, values in arrays.items():
            d = h.create_dataset(
                name,
                data=values,
                dtype="<i4"
                if name in ("sequence", "row_id", "tracer_id", "raw_ordinal", "step")
                else "<f8",
            )
            if name in UNITS:
                d.attrs["units"] = UNITS[name]
        for name in selection[0]:
            if name not in ("sequence", "ordinal"):
                h.create_dataset(
                    "raw_provenance/" + name,
                    data=[s[name] for s in selection],
                    dtype=h5py.string_dtype("utf-8"),
                )
        for use, reason in REASONS.items():
            h.create_dataset("eligibility/" + use, data=[False] * n, dtype="?")
            h["eligibility/" + use].attrs["reason"] = reason
    manifest = {
        "schema": SCHEMA,
        "dataset_id": c["dataset_id"],
        "dataset_version": c["dataset_version"],
        "count": n,
        "species_Z_A": species,
        "units": UNITS,
        "scientific_eligibility": {
            use: {"eligible": False, "reason": reason}
            for use, reason in REASONS.items()
        },
        "recipe": c,
        "recipe_sha256": digest(config_bytes),
        "software": {
            "materializer_sha256": digest(Path(__file__).read_bytes()),
            "python": platform.python_version(),
            "h5py": h5py.__version__,
            "hdf5": h5py.version.hdf5_version,
            "numpy": version("numpy"),
            "distribution": version("crucible-astro"),
        },
        "original_state_provenance": {
            "selection_parent": inputs["selection"],
            "historical_build_association": "unverified; see raw parent card",
        },
        "new_label_provenance": {
            "contract": "D-019 source-PR-20 v2 native pointwise full-Y/T9/rho/Ye=Q/B",
            "preparation": inputs["preparation"],
            "comparison": inputs["comparison"],
            "reference_accuracy": comparison["reference_accuracy"],
        },
        "output": {
            "path": "dataset.h5",
            "bytes": output.stat().st_size,
            "sha256": digest(output.read_bytes()),
        },
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        materialize(args.config, args.destination)
    except (ValueError, KeyError, TypeError, OSError, struct.error) as error:
        parser.exit(1, f"materialization refused: {error}\n")


if __name__ == "__main__":
    main()
