#!/usr/bin/env python3
"""Prepare/verify/decode fixed pilot or primary inputs. Never build or call XNet."""

import argparse
import hashlib
import json
import math
import shutil
import struct
from collections import defaultdict
from pathlib import Path

from arithmetic import assemble_check, mapping_terms

HERE = Path(__file__).resolve().parent
NY, NSTATES = 160, 5157
MAGIC = 0x43525543
COUNTS = (683, 1345, 16, 4)
HEADER = struct.Struct("<4i")
PREFIX = struct.Struct("<5i5d")
FRESH_PREFIX = struct.Struct("<5i9di")
PUBLIC = (
    "reference.py",
    "arithmetic.py",
    "rhs_evaluator.f90",
    "build.sh",
    "run.sh",
    "bindings.json",
)


def require(value, reason):
    if not value:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def write(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def checked(entry, expected=None):
    require(set(entry) == {"path", "sha256"}, "Explicit path/hash required")
    p = Path(entry["path"])
    require(p.is_absolute() and p.is_file(), "Absolute existing file required")

    def stable_stat():
        s = p.stat()
        return s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino, s.st_dev

    before = stable_stat()
    data = p.read_bytes()
    require(stable_stat() == before, "File changed while reading")
    require(digest(data) == entry["sha256"], "Configured checksum mismatch")
    require(
        expected is None or entry["sha256"] == expected,
        "Unreviewed reference substitution",
    )
    return data


def records(data):
    offset = 0
    while offset < len(data):
        require(offset + 4 <= len(data), "Truncated marker")
        n = struct.unpack_from("<i", data, offset)[0]
        end = offset + 4 + n
        require(n >= 0 and end + 4 <= len(data), "Invalid record extent")
        require(data[offset : offset + 4] == data[end : end + 4], "Marker mismatch")
        yield offset, data[offset + 4 : end]
        offset = end + 4


def parse_maps(data, ny=NY):
    """Decode the simple exported stream, independent of producer initialization."""
    offset = 0

    def take(fmt):
        nonlocal offset
        s = struct.Struct("<" + fmt)
        require(offset + s.size <= len(data), "Truncated reaction maps")
        out = s.unpack_from(data, offset)
        offset += s.size
        return out

    la, le = take(f"{4 * ny}i"), take(f"{4 * ny}i")
    groups = []
    for order in range(1, 5):
        actual, count, nan = take("3i")
        require(
            actual == order and 0 <= count <= 100000 and 0 <= nan <= 1000000,
            "Invalid map dimensions",
        )
        width = 5 if order == 1 else 6
        flat = take(f"{width * count}i")
        participants = [flat[i * width : (i + 1) * width] for i in range(count)]
        mu, target, factor = take(f"{nan}i"), take(f"{nan}i"), take(f"{nan}d")
        cursor = 0
        for i in range(ny):
            start, stop = la[4 * i + order - 1], le[4 * i + order - 1]
            require(
                start == cursor + 1 and stop >= cursor, "Noncontiguous extended ranges"
            )
            require(
                stop <= nan and all(x == i + 1 for x in target[cursor:stop]),
                "Extended species identity mismatch",
            )
            cursor = stop
        require(cursor == nan, "Extended map count mismatch")
        groups.append(
            {
                "order": order,
                "participants": participants,
                "extended": list(zip(target, (x - 1 for x in mu), factor, strict=True)),
            }
        )
    require(offset == len(data), "Trailing reaction map bytes")
    return groups


def expected_maps(nets3, nets4):
    """Decode only the exact initialization layout inspected in xnet_data.f90."""
    s3 = [b for _, b in records(nets3)]
    s4 = [b for _, b in records(nets4)]
    require(struct.unpack("<i", s4[0]) == (NY,), "Wrong network size")
    require(struct.unpack("<2i", s4[2]) == (176, 0), "Wrong FFN/NNU counts")
    require(struct.unpack("<4i", s4[3]) == COUNTS, "Wrong reaction counts")
    extents = [struct.unpack("<9i", b) for b in s4[4 : 4 + NY]]
    require(
        [r[0] for r in extents] == list(range(1, NY + 1)), "Wrong map species order"
    )
    out = bytearray()
    for column in (1, 2):
        for r in extents:
            out.extend(struct.pack("<4i", *(r[column + 2 * j] for j in range(4))))
    pos = 0
    participant_groups = []
    for order, count in enumerate(COUNTS, 1):
        width = 5 if order == 1 else 6
        values = []
        for k in range(count):
            b = s3[pos]
            pos += 1
            require(len(b) == 4 * (width + 4) + 64, "Unsupported reaction input width")
            require(struct.unpack_from("<i", b)[0] == k + 1, "Reaction index mismatch")
            values.append(struct.unpack_from(f"<{width}i", b, 4))
            if order == 1:
                require(
                    0 <= struct.unpack_from("<i", b, 4 * (width + 1))[0] <= 4,
                    "Unexpected weak flags",
                )
        participant_groups.append(values)
    for order, values in enumerate(participant_groups, 1):
        nan = extents[-1][2 * order]
        factors, mu = [], []
        for _ in range(nan):
            a, m = struct.unpack("<di", s3[pos])
            pos += 1
            factors.append(a)
            mu.append(m)
        targets = [
            i + 1
            for i, row in enumerate(extents)
            for _ in range(row[2 * order - 1], row[2 * order] + 1)
        ]
        require(len(targets) == nan, "Invalid input map ranges")
        out.extend(struct.pack("<3i", order, len(values), nan))
        out.extend(
            struct.pack(
                "<" + str(sum(map(len, values))) + "i",
                *(v for row in values for v in row),
            )
        )
        out.extend(struct.pack(f"<{nan}i{nan}i{nan}d", *mu, *targets, *factors))
    require(pos == len(s3), "Unused reaction input records")
    # The selected nets4 has one 20-byte trailer ignored by read_reaction_data.
    require(len(s4) == 4 + NY + 1 and len(s4[-1]) == 20, "Unsupported nets4 trailer")
    return bytes(out)


def species_ids(za):
    require(len(za) == 16 * NY, "Invalid species width")
    z = struct.unpack_from("<160d", za)
    aa = struct.unpack_from("<160d", za, 1280)
    require(
        all(math.isfinite(x) and x == int(x) for x in z + aa),
        "Invalid species identities",
    )
    a = [int(x) for x in aa]
    require(
        len(set(zip(z, a))) == NY
        and all(0 <= zi <= ai and ai > 0 for zi, ai in zip(z, a)),
        "Duplicate/invalid species",
    )
    return z, a


def native_ye(y, z, a):
    """Pinned y_moment: Ye=Q/B. Neither raw moment changes supplied Y."""
    baryon = math.fsum(ai * yi for ai, yi in zip(a, y, strict=True))
    charge = math.fsum(zi * yi for zi, yi in zip(z, y, strict=True))
    require(math.isfinite(baryon) and baryon > 0, "Nonpositive/nonfinite baryon sum")
    require(math.isfinite(charge), "Nonfinite raw charge sum")
    ye = charge / baryon
    require(math.isfinite(ye) and ye > 0, "Invalid composition-derived Ye")
    return ye


def validate_state(prefix, y, z, a):
    seq, row, zone, ordinal, step, time, t9, rho, dt, energy = PREFIX.unpack(prefix)
    require(min(seq, row, zone, ordinal, step) > 0, "Invalid ordinary-state identity")
    yy = struct.unpack(f"<{len(z)}d", y)
    require(
        all(math.isfinite(x) for x in (time, t9, rho, dt, energy, *yy)),
        "Nonfinite state",
    )
    require(all(0 <= x <= 1 for x in yy), "Y outside supported assembly envelope")
    require(rho > 0 and 0.01 <= t9 <= 100, "Outside source temperature grid")
    ye = native_ye(yy, z, a)
    require(ye > 0 and 1 <= math.log10(rho * ye) < 11, "Outside source density grid")
    require(all(isinstance(x, int) for x in a), "Invalid mass identities")
    return yy


def extract_states(chosen, fixity, raw_root, *, signed_zero=False):
    by_path = defaultdict(list)
    for seq, r in enumerate(chosen, 1):
        by_path[r["trajectory_locator"]].append((seq, r))
    root = Path(raw_root)
    require(root.is_absolute(), "Absolute raw root required")
    payloads, selection, events = {}, {}, []
    species = None
    za = None
    for name, rows in by_path.items():
        require(
            not Path(name).is_absolute() and ".." not in Path(name).parts,
            "Unsafe raw locator",
        )
        evname = str(Path(name).with_name("ev_" + Path(name).name[3:]))
        raw = checked({"path": str(root / name), "sha256": fixity[name]})
        ev = checked({"path": str(root / evname), "sha256": fixity[evname]})
        recs = list(records(raw))
        lines = ev.decode("ascii").splitlines()
        require(
            [len(b) for _, b in recs[:6]] == [320, 76, 160, 160, 2564, 7276],
            "Unsupported binary layout",
        )
        controls = struct.unpack("<5i6d2i", recs[1][1])
        require(
            controls[2:4] == (1, 1) and controls[-2:] == (0, 1),
            "Raw physics configuration mismatch",
        )
        require(
            len(lines) == len(recs) - 5
            and struct.unpack_from("<i", recs[5][1])[0] == 909,
            "Companion/flux mismatch",
        )
        if species is None:
            species = recs[4][1]
            za = species[4:]
        require(
            species == recs[4][1] and struct.unpack_from("<i", species)[0] == NY,
            "Species order changed",
        )
        z, a = species_ids(za)
        row = int(Path(name).parts[0].rsplit("_", 1)[1])
        zone = int(Path(name).name.split("_")[1])
        for seq, r in rows:
            ordinal = r["ordinal"]
            require(
                isinstance(ordinal, int) and 0 < ordinal < len(recs) - 6,
                "Invalid ordinary ordinal",
            )
            require(r["record_id"] == f"{name}#{ordinal}", "Record identity mismatch")
            offset, b = recs[6 + ordinal]
            require(
                len(b) == 9876 and offset == r["raw_marker_offset"],
                "Wrong record extent/offset",
            )
            header, yy, stored = b[:44], b[44:1324], b[8596:9876]
            require(
                digest(header) == r["header_sha256"]
                and digest(yy) == r["Y_bytes_sha256"],
                "Audited state bits changed",
            )
            h = struct.unpack("<i5d", header)
            fields = lines[ordinal + 1].split()
            expected = [
                str(h[0]),
                f"{h[1]:.8E}",
                f"{h[2]:.3E}",
                f"{h[3]:.3E}",
                f"{h[5]:.2E}",
                f"{h[4]:.2E}",
            ]
            if signed_zero:
                from primary import companion_matches

                aligned, equivalent = companion_matches(fields, expected, h[5])
                if equivalent:
                    events.append(
                        {
                            "trajectory_locator": name,
                            "ordinal": ordinal,
                            "raw_binary64_hex": header[36:44].hex(),
                        }
                    )
            else:
                aligned = fields[-1] != "NSE" and fields[:6] == expected
            require(aligned, "Companion/ordinary identity mismatch")
            prefix = struct.pack("<4i", seq, row, zone, ordinal) + header
            validate_state(prefix, yy, z, a)
            require(
                all(math.isfinite(x) for x in struct.unpack("<160d", stored)),
                "Nonfinite stored audit label",
            )
            payloads[seq] = prefix + yy + stored
            selection[seq] = {
                "sequence": seq,
                "record_id": r["record_id"],
                "raw_ts_sha256": fixity[name],
                "raw_ev_sha256": fixity[evname],
                "ordinal": ordinal,
                "raw_payload_sha256": digest(b),
                "input_state_sha256": digest(prefix + yy),
            }
    return payloads, selection, za, a, events


def prepare(config_path, destination):
    c = load(config_path)
    bindings = load(HERE / "bindings.json")
    require(
        set(c)
        == {"files", "raw_root", "records", "fixity", "d017_states", "d017_fresh"},
        "Unexpected config",
    )
    require(set(c["files"]) == set(bindings["files"]), "Reference closure mismatch")
    assets = {n: checked(e, bindings["files"][n]) for n, e in c["files"].items()}
    audit_bytes = checked(c["records"])
    audit = [json.loads(line) for line in audit_bytes.splitlines()]
    chosen = [r for r in audit if r["inside_candidate_FFN_source_grid_only"]]
    require(
        len(chosen) == NSTATES and len({r["trajectory_locator"] for r in chosen}) == 80,
        "Wrong fixed candidate membership",
    )
    require(
        len({r["record_id"] for r in chosen}) == NSTATES, "Duplicate state selection"
    )
    fix = json.loads(checked(c["fixity"]))
    fixity = {e["path"]: e["sha256"] for e in fix["files"]}
    require(len(fixity) == 166, "Unexpected full raw fixity membership")
    payloads, selection, za, a, _ = extract_states(chosen, fixity, c["raw_root"])
    z, _ = species_ids(za)
    states = (
        HEADER.pack(MAGIC, 2, NSTATES, NY)
        + za
        + b"".join(payloads[i] for i in range(1, NSTATES + 1))
    )
    maps = expected_maps(assets["network/nets3"], assets["network/nets4"])
    mapping_terms(
        parse_maps(maps), a
    )  # independent combinatorial/mass check before any build
    old = checked(c["d017_states"])
    oldfresh = checked(c["d017_fresh"])
    require(
        HEADER.unpack_from(old) == (MAGIC, 1, 3, NY) and old[:2576] == oldfresh[:2576],
        "Invalid D017 controls",
    )
    require(old[16:2576] == za, "D017 species mismatch")
    retained = retained_controls(old, oldfresh, z, a)
    controls = {}
    for seq, r in selection.items():
        control = retained.get(payloads[seq][12:])
        if control is not None:
            controls[str(seq)] = {
                "record_id": r["record_id"],
                "fresh_hex": control.hex(),
            }
    require(len(controls) == 2, "Missing or duplicated two in-grid retained controls")
    dest = Path(destination).resolve()
    require(
        ".local" in dest.parts and not dest.exists(), "New ignored destination required"
    )
    dest.mkdir(parents=True)
    for name, data in {
        **assets,
        "states.bin": states,
        "expected-maps.bin": maps,
    }.items():
        p = dest / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        p.chmod(0o444)
    for n in PUBLIC:
        shutil.copyfile(HERE / n, dest / n)
    write(dest / "selection.json", list(selection.values()))
    write(dest / "d017-controls.json", controls)
    manifest = {
        "schema": "crucible.rhs-reference-preparation.v1",
        "status": "PREPARED ONLY; all producer build/run calls deferred; no scientific masks true",
        "configuration": c,
        "selection_count": NSTATES,
        "files": {
            str(p.relative_to(dest)): {
                "bytes": p.stat().st_size,
                "sha256": digest(p.read_bytes()),
            }
            for p in sorted(dest.rglob("*"))
            if p.is_file()
        },
    }
    write(dest / "manifest.json", manifest)
    verify(dest)
    return manifest


def retained_controls(old, output, z, a):
    require(
        len(old) == 2576 + 3 * 2608 and len(output) == 2576 + 3 * 5204,
        "Invalid retained control lengths",
    )
    controls = {}
    for k in range(3):
        inp = old[2576 + k * 2608 : 2576 + (k + 1) * 2608]
        out = output[2576 + k * 5204 : 2576 + (k + 1) * 5204]
        require(
            out[:48] == inp[:48] and out[48:72] == inp[8:32],
            "Retained control scalar identity mismatch",
        )
        require(
            out[84:1364] == inp[48:1328] == out[1364:2644]
            and out[2644:3924] == inp[1328:],
            "Retained control array echo mismatch",
        )
        yy = struct.unpack("<160d", inp[48:1328])
        h = struct.unpack_from("<ii5d", inp)
        require(
            h[0] > 0
            and h[1] > 0
            and all(
                math.isfinite(v)
                for v in (*h[2:], *yy, *struct.unpack("<160d", out[3924:]))
            ),
            "Invalid retained ordinary control",
        )
        require(
            all(0 <= v <= 1 for v in yy) and h[3] > 0 and h[4] > 0,
            "Invalid retained state",
        )
        ye = native_ye(yy, z, a)
        require(ye > 0, "Invalid retained Ye")
        if 0.01 <= h[3] <= 100 and 1 <= math.log10(h[4] * ye) < 11:
            require(inp not in controls, "Duplicated retained control")
            controls[inp] = out[3924:]
    require(len(controls) == 2, "Expected two retained in-grid controls")
    return controls


def verify(root):
    root = Path(root)
    m = load(root / "manifest.json")
    primary = m["schema"] == "crucible.rhs-primary-preparation.v1"
    count = 19159 if primary else NSTATES
    require(
        (primary or m["schema"] == "crucible.rhs-reference-preparation.v1")
        and m["selection_count"] == count,
        "Wrong bundle schema/count",
    )
    for name, item in m["files"].items():
        require(
            not Path(name).is_absolute() and ".." not in Path(name).parts,
            "Unsafe manifest path",
        )
        b = (root / name).read_bytes()
        require(
            len(b) == item["bytes"] and digest(b) == item["sha256"],
            "Bound bundle input changed",
        )
    state = (root / "states.bin").read_bytes()
    require(
        len(state) == 2576 + count * (PREFIX.size + 2560),
        "Invalid prepared state length",
    )
    require(
        HEADER.unpack_from(state) == (MAGIC, 2, count, NY),
        "Invalid prepared state count/header",
    )
    if primary:
        from primary import verify_metadata

        verify_metadata(root, m, state)
    return m


def decode_record(state, output, z, a, coefficient_count):
    ny = len(z)
    require(len(state) == PREFIX.size + 16 * ny, "Invalid state record width")
    require(
        len(output) == FRESH_PREFIX.size + 32 * ny + 8 * coefficient_count,
        "Invalid output width",
    )
    require(
        output[: PREFIX.size] == state[: PREFIX.size], "Changed state identity/scalars"
    )
    require(
        output[PREFIX.size : PREFIX.size + 24] == state[20:44], "Changed time/T9/rho"
    )
    ye, weak = struct.unpack_from("<di", output, PREFIX.size + 24)
    require(math.isfinite(ye) and weak == 1, "Invalid EOS/weak output")
    yy = state[PREFIX.size : PREFIX.size + 8 * ny]
    stored = state[PREFIX.size + 8 * ny :]
    arrays = output[FRESH_PREFIX.size :]
    require(
        arrays[: 8 * ny] == yy == arrays[8 * ny : 16 * ny]
        and arrays[16 * ny : 24 * ny] == stored,
        "Changed Y/stored echoes",
    )
    fresh_bytes = arrays[24 * ny : 32 * ny]
    y, old, fresh = (
        list(struct.unpack(f"<{ny}d", v)) for v in (yy, stored, fresh_bytes)
    )
    coeff = list(struct.unpack(f"<{coefficient_count}d", arrays[32 * ny :]))
    require(
        all(math.isfinite(v) for v in y + old + fresh + coeff),
        "Nonfinite decoded result",
    )
    delta = [n - o for n, o in zip(fresh, old, strict=True)]
    require(all(math.isfinite(v) for v in delta), "Difference overflow")
    return (
        {
            "Y": y,
            "stored_dY": old,
            "fresh_dY": fresh,
            "difference_fresh_minus_stored": delta,
            "absolute_difference": {
                "L1": math.fsum(map(abs, delta)),
                "L2": math.hypot(*delta),
                "Linf": max(map(abs, delta)),
            },
            "state_bits_unchanged": True,
            "composition_EOS_Ye": ye,
            "sum_A_Y": math.fsum(ai * yi for ai, yi in zip(a, y, strict=True)),
            "sum_Z_Y": math.fsum(zi * yi for zi, yi in zip(z, y, strict=True)),
            "fresh_charge_rate": math.fsum(
                zi * fi for zi, fi in zip(z, fresh, strict=True)
            ),
            "coefficients_sha256": digest(arrays[32 * ny :]),
            "fresh_sha256": digest(fresh_bytes),
            "training_eligibility": False,
        },
        coeff,
        fresh_bytes,
    )


def compare(root):
    root = Path(root)
    manifest = verify(root)
    count = manifest["selection_count"]
    original = (root / "states.bin").read_bytes()
    require(HEADER.unpack_from(original) == (MAGIC, 2, count, NY), "Bad state header")
    require(len(original) == 2576 + count * (PREFIX.size + 2560), "Bad state length")
    expected = (root / "expected-maps.bin").read_bytes()
    require(
        (root / "used-maps.bin").read_bytes()
        == expected
        == (root / "used-maps-after.bin").read_bytes(),
        "Runtime reaction maps changed",
    )
    z, a = species_ids(original[16:2576])
    terms = mapping_terms(parse_maps(expected), a)
    controls = load(root / "d017-controls.json")
    require(
        (root / "fresh.bin").stat().st_size
        == 2576 + count * (FRESH_PREFIX.size + 5120 + 16384),
        "Wrong fresh output count/length",
    )
    control_results = []
    results = root / "components.jsonl"
    require(not results.exists(), "Refusing overwrite")
    with (root / "fresh.bin").open("rb") as inp, results.open("x") as out:
        require(inp.read(2576) == original[:2576], "Changed output species/header")
        for k in range(count):
            state = original[
                2576 + k * (PREFIX.size + 2560) : 2576 + (k + 1) * (PREFIX.size + 2560)
            ]
            b = inp.read(FRESH_PREFIX.size + 5120 + 16384)
            require(
                len(b) == FRESH_PREFIX.size + 5120 + 16384, "Truncated fresh output"
            )
            result, coeff, fresh_bytes = decode_record(state, b, z, a, sum(COUNTS))
            y, fresh = result["Y"], result["fresh_dY"]
            check = assemble_check(y, coeff, fresh, terms, a)
            seq = PREFIX.unpack_from(state)[0]
            if str(seq) in controls:
                require(
                    fresh_bytes.hex() == controls[str(seq)]["fresh_hex"],
                    "D017 exact-bit control mismatch; stop, no tolerance fallback",
                )
                control_results.append(seq)
            result.update(sequence=seq, conditional_assembly=check)
            out.write(json.dumps(result, allow_nan=False) + "\n")
        require(not inp.read(1), "Trailing fresh bytes")
    require(len(control_results) == 2, "Missing D017 output controls")
    libraries = {}
    for line in (root / "loaded-maps.txt").read_text().splitlines():
        f = line.split(maxsplit=5)
        if len(f) == 6 and f[5].startswith("/") and ".so" in f[5]:
            p = Path(f[5])
            require(p.is_file(), "Unavailable runtime library")
            libraries[str(p)] = digest(p.read_bytes())
    require(libraries, "No loaded runtime libraries")
    report = {
        "status": "Completed comparisons only; scientific qualification remains false",
        "manifest_sha256": digest((root / "manifest.json").read_bytes()),
        "executable_sha256": digest((root / "rhs_evaluator").read_bytes()),
        "fresh_sha256": digest((root / "fresh.bin").read_bytes()),
        "components_sha256": digest(results.read_bytes()),
        "D017_exact_bit_controls": control_results,
        "runtime_shared_libraries_sha256": libraries,
        "reference_accuracy": "Coefficient-conditioned assembly verified; rate/EOS/astrophysical accuracy not established",
        "training_eligibility": False,
    }
    require(not (root / "comparison.json").exists(), "Refusing comparison overwrite")
    write(root / "comparison.json", report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest="action", required=True)
    a = s.add_parser("prepare")
    a.add_argument("config", type=Path)
    a.add_argument("destination", type=Path)
    a = s.add_parser("prepare-primary")
    a.add_argument("config", type=Path)
    a.add_argument("destination", type=Path)
    for n in ("verify", "compare"):
        a = s.add_parser(n)
        a.add_argument("root", type=Path)
    args = p.parse_args()
    if args.action == "prepare":
        prepare(args.config, args.destination)
    elif args.action == "prepare-primary":
        from primary import prepare as prepare_primary

        prepare_primary(args.config, args.destination)
    elif args.action == "verify":
        verify(args.root)
    else:
        compare(args.root)


if __name__ == "__main__":
    main()
