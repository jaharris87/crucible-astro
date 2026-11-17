#!/usr/bin/env python3
"""Prepare/verify/compare the D-017 three-state experiment; never execute Fortran."""

import argparse
import hashlib
import json
import math
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORDINALS = (1, 676, 741)
NY = 160
NFLUX = 909
NROWS = 742
MAGIC = 0x43525543
PREFIX = struct.Struct("<ii5d")
HEADER = struct.Struct("<4i")
FRESH_PREFIX = struct.Struct("<ii9di")
SOURCE_NAMES = (
    "xnet_types",
    "xnet_constants",
    "xnet_parallel",
    "xnet_util",
    "xnet_controls",
    "xnet_conditions",
    "xnet_ffn",
    "xnet_nnu",
    "xnet_data",
    "xnet_abundances",
    "xnet_timers",
    "xnet_fd",
    "xnet_eos_starkiller",
    "xnet_screening",
    "xnet_integrate",
)
NETWORK_NAMES = (
    "sunet",
    "netwinv",
    "nets3",
    "nets4",
    "netweak",
    "net_desc",
    "match_data",
)
PUBLIC_FILES = (
    "diagnostic.py",
    "rhs_evaluator.f90",
    "build.sh",
    "run.sh",
    "bindings.json",
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def require(test, reason):
    if not test:
        raise ValueError(reason)


def finite(values):
    return all(math.isfinite(x) for x in values)


def records(data):
    """The independently audited pair-B LE/int32-marker framing only."""
    offset = 0
    while offset < len(data):
        require(offset + 4 <= len(data), "Truncated record marker")
        size = struct.unpack_from("<i", data, offset)[0]
        end = offset + 4 + size
        require(size >= 0 and end + 4 <= len(data), "Invalid record extent")
        require(
            data[offset : offset + 4] == data[end : end + 4], "Record marker mismatch"
        )
        yield offset, data[offset + 4 : end]
        offset = end + 4


def extract_states(raw, ev):
    recs = list(records(raw))
    require(len(recs) == 6 + NROWS, "Unexpected pair-B record count")
    require(
        [len(b) for _, b in recs[:6]] == [320, 76, 160, 160, 2564, 7276],
        "Unexpected six-record metadata layout",
    )
    controls = struct.unpack("<5i6d2i", recs[1][1])
    require(
        controls == (99999, 5, 1, 1, 1, 0.1, 1e-6, 1e-4, 1e-8, 1e-20, 2.0, 0, 1),
        "Unsupported physics/solver control metadata",
    )
    species = recs[4][1]
    require(struct.unpack_from("<i", species)[0] == NY, "Expected 160 species")
    za = species[4:]
    z, a = struct.unpack("<160d", za[:1280]), struct.unpack("<160d", za[1280:])
    require(finite(z + a) and len(set(zip(z, a))) == NY, "Invalid/duplicate species")
    require(
        all(0 <= zi <= ai and zi == int(zi) and ai == int(ai) for zi, ai in zip(z, a)),
        "Invalid species identities",
    )
    require(struct.unpack_from("<i", recs[5][1])[0] == NFLUX, "Unexpected flux count")
    lines = ev.decode("ascii").splitlines()
    require(len(lines) == NROWS + 1, "Companion row-count mismatch")
    output = bytearray(HEADER.pack(MAGIC, 1, 3, NY) + za)
    selected = []
    for ordinal, (marker, b) in enumerate(recs[6:]):
        require(len(b) == 9876, "Unexpected pair-B scalar/array record width")
        fields = lines[ordinal + 1].split()
        require(
            fields and int(fields[0]) == struct.unpack_from("<i", b)[0],
            "Companion step alignment mismatch",
        )
        if ordinal not in ORDINALS:
            continue
        require(fields[-1] != "NSE", "Selected row is an NSE placeholder")
        step, *scalars = struct.unpack_from("<i5d", b)
        y = b[44:1324]
        stored = b[8596:9876]
        require(
            step > 0 and finite(scalars + list(struct.unpack("<320d", y + stored))),
            "Nonfinite/invalid selected state",
        )
        require(scalars[1] > 0 and scalars[2] > 0, "Nonpositive T9/density")
        output.extend(struct.pack("<i", ordinal) + b[:44] + y + stored)
        selected.append(
            {
                "ordinal": ordinal,
                "step": step,
                "marker_offset": marker,
                "payload_sha256": digest(b),
                "Y_sha256": digest(y),
                "stored_dY_sha256": digest(stored),
            }
        )
    require(
        tuple(s["ordinal"] for s in selected) == ORDINALS, "Wrong diagnostic selection"
    )
    return bytes(output), selected


def checked_file(entry, expected=None):
    require(
        set(entry) == {"path", "sha256"}, "Each file needs explicit path and sha256"
    )
    path = Path(entry["path"])
    require(
        path.is_absolute() and path.is_file(), "Expected absolute existing input file"
    )
    data = path.read_bytes()
    require(
        digest(data) == entry["sha256"], f"Configured checksum mismatch: {path.name}"
    )
    if expected is not None:
        require(
            entry["sha256"] == expected, f"Unreviewed input substitution: {path.name}"
        )
    return data


def prepare(config_path, output):
    config = load_json(config_path)
    bindings = load_json(HERE / "bindings.json")
    require(
        set(config) == {"files", "raw_ts", "raw_ev", "control"},
        "Unexpected configuration keys",
    )
    require(
        set(config["files"]) == set(bindings["files"]) | {"helm_table.dat"},
        "Missing or unexpected reference build/input files",
    )
    # Validate all inputs before creating the destination. No imports or execution of reference code.
    assets = {
        name: checked_file(entry, bindings["files"].get(name))
        for name, entry in config["files"].items()
    }
    raw = checked_file(config["raw_ts"], bindings["raw_ts"])
    ev = checked_file(config["raw_ev"], bindings["raw_ev"])
    control = checked_file(config["control"], bindings["control"])
    states, selection = extract_states(raw, ev)
    output = Path(output).resolve()
    require(
        ".local" in output.parts,
        "Real snapshots must stay in an ignored .local directory",
    )
    require(not output.exists(), "Refusing to overwrite an existing diagnostic bundle")
    output.mkdir(parents=True)
    for name, data in assets.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (output / "states.bin").write_bytes(states)
    (output / "original-control").write_bytes(control)
    for name in PUBLIC_FILES:
        shutil.copyfile(HERE / name, output / name)
    paths = sorted(p for p in output.rglob("*") if p.is_file())
    manifest = {
        "schema": "crucible.rhs-diagnostic-bundle.v1",
        "status": "prepared; Fortran build/execution require exact-candidate source review",
        "reference_status": "selected new reference; not historical generating-build proof",
        "selection": selection,
        "configuration": config,
        "files": {
            str(p.relative_to(output)): {
                "bytes": p.stat().st_size,
                "sha256": digest(p.read_bytes()),
            }
            for p in paths
        },
    }
    write_json(output / "manifest.json", manifest)
    verify(output)
    return manifest


def verify(root):
    root = Path(root)
    manifest = load_json(root / "manifest.json")
    require(
        manifest["schema"] == "crucible.rhs-diagnostic-bundle.v1",
        "Unknown bundle schema",
    )
    for name, item in manifest["files"].items():
        path = root / name
        require(
            not Path(name).is_absolute() and ".." not in Path(name).parts,
            "Unsafe manifest path",
        )
        data = path.read_bytes()
        require(
            len(data) == item["bytes"] and digest(data) == item["sha256"],
            f"Bound input changed: {name}",
        )
    return manifest


def compare(root):
    root = Path(root)
    manifest = verify(root)
    original = (root / "states.bin").read_bytes()
    fresh = (root / "fresh.bin").read_bytes()
    common = HEADER.size + 2 * NY * 8
    in_size = PREFIX.size + 2 * NY * 8
    out_size = FRESH_PREFIX.size + 4 * NY * 8
    require(len(original) == common + 3 * in_size, "Invalid input size")
    require(len(fresh) == common + 3 * out_size, "Invalid fresh-output size")
    require(fresh[:common] == original[:common], "Output species/header changed")
    require(HEADER.unpack_from(original) == (MAGIC, 1, 3, NY), "Invalid state header")
    z = struct.unpack_from("<160d", original, HEADER.size)
    a = struct.unpack_from("<160d", original, HEADER.size + NY * 8)
    libraries = {}
    for line in (root / "loaded-maps.txt").read_text().splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) == 6 and fields[5].startswith("/") and ".so" in fields[5]:
            path = Path(fields[5])
            require(path.is_file(), f"Unavailable runtime library: {path}")
            libraries[str(path)] = digest(path.read_bytes())
    require(libraries, "No runtime shared-library evidence captured")
    results = []
    for k, ordinal in enumerate(ORDINALS):
        inp = original[common + k * in_size : common + (k + 1) * in_size]
        out = fresh[common + k * out_size : common + (k + 1) * out_size]
        require(
            out[: PREFIX.size] == inp[: PREFIX.size],
            "Output record/scalar identity changed",
        )
        require(struct.unpack_from("<i", inp)[0] == ordinal, "Output ordinal mismatch")
        y_in = inp[PREFIX.size : PREFIX.size + NY * 8]
        stored = inp[PREFIX.size + NY * 8 :]
        scalars_after = out[PREFIX.size : PREFIX.size + 24]
        require(scalars_after == inp[8:32], "Reference changed time/T9/density")
        y_before = out[FRESH_PREFIX.size : FRESH_PREFIX.size + NY * 8]
        y_after = out[FRESH_PREFIX.size + NY * 8 : FRESH_PREFIX.size + 2 * NY * 8]
        stored_echo = out[
            FRESH_PREFIX.size + 2 * NY * 8 : FRESH_PREFIX.size + 3 * NY * 8
        ]
        fresh_bytes = out[FRESH_PREFIX.size + 3 * NY * 8 :]
        require(
            y_in == y_before == y_after and stored == stored_echo,
            "Abundance/label identity changed",
        )
        yy = struct.unpack("<160d", y_in)
        old = struct.unpack("<160d", stored)
        new = struct.unpack("<160d", fresh_bytes)
        eos_ye = struct.unpack_from("<d", out, PREFIX.size + 24)[0]
        weak = struct.unpack_from("<i", out, PREFIX.size + 32)[0]
        require(finite(yy + old + new + (eos_ye,)), "Nonfinite result")
        delta = [n - o for n, o in zip(new, old)]
        require(finite(delta), "Difference overflow")
        results.append(
            {
                "ordinal": ordinal,
                "step": PREFIX.unpack_from(inp)[1],
                "state_unchanged_bits": True,
                "Y": yy,
                "stored_dY": old,
                "fresh_dY": new,
                "difference_fresh_minus_stored": delta,
                "absolute_error": {
                    "L1": math.fsum(map(abs, delta)),
                    "L2": math.hypot(*delta),
                    "Linf": max(map(abs, delta)),
                },
                "sum_A_Y": math.fsum(ai * yi for ai, yi in zip(a, yy)),
                "sum_Z_Y": math.fsum(zi * yi for zi, yi in zip(z, yy)),
                "stored_baryon_rate": math.fsum(ai * di for ai, di in zip(a, old)),
                "fresh_baryon_rate": math.fsum(ai * di for ai, di in zip(a, new)),
                "stored_charge_rate": math.fsum(zi * di for zi, di in zip(z, old)),
                "fresh_charge_rate": math.fsum(zi * di for zi, di in zip(z, new)),
                "composition_EOS_Ye": eos_ye,
                "effective_iweak": weak,
                "Y_before_sha256": digest(y_before),
                "Y_after_sha256": digest(y_after),
                "fresh_dY_sha256": digest(fresh_bytes),
            }
        )
    report = {
        "schema": "crucible.rhs-diagnostic-comparison.v1",
        "scientific_acceptance": "not evaluated; no tolerance accepted",
        "reference_status": manifest["reference_status"],
        "manifest_sha256": digest((root / "manifest.json").read_bytes()),
        "fresh_output_sha256": digest(fresh),
        "executable_sha256": digest((root / "rhs_evaluator").read_bytes()),
        "runtime_shared_libraries_sha256": libraries,
        "results": results,
    }
    require(not (root / "comparison.json").exists(), "Refusing to overwrite comparison")
    write_json(root / "comparison.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("config", type=Path)
    prep.add_argument("output", type=Path)
    for action in ("verify", "compare"):
        cmd = sub.add_parser(action)
        cmd.add_argument("root", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.config, args.output)
    elif args.action == "verify":
        verify(args.root)
    else:
        compare(args.root)


if __name__ == "__main__":
    main()
