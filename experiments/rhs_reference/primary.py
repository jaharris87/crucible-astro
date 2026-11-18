"""Finite remaining-primary preparation. This module never builds or calls XNet."""

import json
import math
import shutil
import struct
from pathlib import Path

import reference as ref
from arithmetic import mapping_terms

NEW, PILOT, TOTAL = 19157, 5157, 24314
NEW_HISTORIES, PILOT_HISTORIES = 300, 80
WIDTH = ref.PREFIX.size + 2560
OUT_WIDTH = ref.FRESH_PREFIX.size + 5120 + 16384
PILOT_MANIFEST = "10cf0d3250c83ff9c57c65adeb6ce4f323d7c9efadebf97f5b87013dd2f386e6"
PILOT_STATES = "aa0d6fe52420183601e8c3301b19e497058397621eb66c64a2c4ffc6c6dc290f"
PILOT_FRESH = "cbb9b6c90e5d3cd7e5cf1e14134c543aedb1acd83970c17dc2e894924fc681a2"
PILOT_COMPARISON = "e21a5aa979fb633fdb400f8ee61800cd8b9880d7e437827a47e90a8eedd1858b"
PILOT_RECEIPT = "84c21a6f3d19331b99a3442d4be094136c337f0931e75249ec359b43086f1e47"
AUDITS = {
    "records": "8b171ec2b0b071ffc08f2cf682e1381c3de4582732cbb46566780e29e0257767",
    "pilot_records": "1ebcbbfb171659455a458b83c776bac3255f51c41b3cb33f504512c2c564250b",
    "selection_manifest": "5adbf36d00dc3bce951d0164e2935098b0b1c7e18feeb3a7dbced622d8618d68",
    "expansion_report": "99af765baaaf5b487a0035b8a1f883690adce4bd37b291f32a5cf17b5d422a4a",
}
BATCH = {
    "new_states": NEW,
    "repeat_controls": 2,
    "proposed_calls": NEW + 2,
    "pilot_states_reused": PILOT,
    "pilot_states_not_repeated": PILOT - 2,
    "unique_union_states": TOTAL,
    "new_histories": NEW_HISTORIES,
    "pilot_histories": PILOT_HISTORIES,
    "execution_authorized": False,
}


def companion_matches(fields, expected, binary_energy):
    """Only exact IEEE energy zero may differ in the sign of its printed zero."""
    if not fields or fields[-1] == "NSE" or len(fields) < 6:
        return False, False
    if fields[:6] == expected:
        return True, False
    equivalent = (
        binary_energy == 0.0
        and fields[:4] == expected[:4]
        and fields[5] == expected[5]
        and fields[4] in {"0.00E+00", "-0.00E+00"}
        and expected[4] in {"0.00E+00", "-0.00E+00"}
    )
    return equivalent, equivalent


def population(new, pilot, accepted):
    """Finite identity/history proof, also used with hand-specified toy counts."""
    groups = []
    for rows, count, histories in (
        (new, NEW, NEW_HISTORIES),
        (pilot, PILOT, PILOT_HISTORIES),
        (accepted, TOTAL, NEW_HISTORIES + PILOT_HISTORIES),
    ):
        ids = {r["record_id"] for r in rows}
        paths = {r["trajectory_locator"] for r in rows}
        ref.require(len(rows) == len(ids) == count, "Wrong/duplicate finite membership")
        ref.require(len(paths) == histories, "Wrong finite history membership")
        ref.require(
            all(
                r["record_id"] == f"{r['trajectory_locator']}#{r['ordinal']}"
                for r in rows
            ),
            "Invalid population identity",
        )
        groups.append((ids, paths))
    n, p, all_ids = groups
    ref.require(not n[0] & p[0] and not n[1] & p[1], "Pilot/new overlap")
    ref.require(n[0] | p[0] == all_ids[0], "Accepted union mismatch")


def retained_pilot(c):
    """Bind the immutable reviewed pilot and its completed output, without a call."""
    manifest_bytes = ref.checked(c["pilot_bundle"], PILOT_MANIFEST)
    root = Path(c["pilot_bundle"]["path"]).parent
    m = ref.verify(root)
    ref.require(
        ref.digest((root / "states.bin").read_bytes()) == PILOT_STATES,
        "Pilot state substitution",
    )
    old = (root / "states.bin").read_bytes()
    fresh = ref.checked(c["pilot_fresh"], PILOT_FRESH)
    comparison = json.loads(ref.checked(c["pilot_comparison"], PILOT_COMPARISON))
    receipt = json.loads(ref.checked(c["pilot_receipt"], PILOT_RECEIPT))
    ref.require(
        receipt["status"] == "completed"
        and receipt["parents"]["preparation"] == ref.digest(manifest_bytes)
        and receipt["parents"]["fresh"] == ref.digest(fresh)
        and receipt["parents"]["comparison"] == PILOT_COMPARISON
        and comparison["manifest_sha256"] == PILOT_MANIFEST
        and comparison["fresh_sha256"] == PILOT_FRESH,
        "Pilot execution ancestry mismatch",
    )
    ref.require(
        len(fresh) == 2576 + PILOT * OUT_WIDTH and fresh[:2576] == old[:2576],
        "Wrong pilot output count/species",
    )
    z, a = ref.species_ids(old[16:2576])
    selection = ref.load(root / "selection.json")
    controls = ref.load(root / "d017-controls.json")
    ref.require(
        len(selection) == PILOT and len(controls) == 2, "Missing pilot controls"
    )
    retained = []
    for k, row in enumerate(selection):
        state = old[2576 + k * WIDTH : 2576 + (k + 1) * WIDTH]
        out = fresh[2576 + k * OUT_WIDTH : 2576 + (k + 1) * OUT_WIDTH]
        _, _, vector = ref.decode_record(state, out, z, a, sum(ref.COUNTS))
        ref.require(row["sequence"] == k + 1, "Pilot selection ordering mismatch")
        if str(k + 1) in controls:
            control = controls[str(k + 1)]
            ref.require(
                row["record_id"] == control["record_id"]
                and vector.hex() == control["fresh_hex"],
                "Changed retained pilot control",
            )
            retained.append((state, row, vector))
    ref.require(len(retained) == 2, "Missing/duplicated retained pilot controls")
    return m, old, selection, retained


def prepare(config_path, destination):
    c = ref.load(config_path)
    ref.require(
        set(c)
        == {
            "files",
            "raw_root",
            "fixity",
            "pilot_bundle",
            "pilot_fresh",
            "pilot_comparison",
            "pilot_receipt",
            *AUDITS,
        },
        "Unexpected primary config",
    )
    bindings = ref.load(ref.HERE / "bindings.json")["files"]
    ref.require(set(c["files"]) == set(bindings), "Reference closure mismatch")
    assets = {n: ref.checked(e, bindings[n]) for n, e in c["files"].items()}
    inputs = {n: ref.checked(c[n], h) for n, h in AUDITS.items()}
    audit = [json.loads(line) for line in inputs["records"].splitlines()]
    pilot_audit = [json.loads(line) for line in inputs["pilot_records"].splitlines()]
    chosen = [r for r in audit if r["source_grid_inside"]]
    pilot_rows = [r for r in pilot_audit if r["source_grid_inside"]]
    population(chosen, pilot_rows, chosen + pilot_rows)
    frozen = json.loads(inputs["selection_manifest"])
    report = json.loads(inputs["expansion_report"])
    ref.require(
        report["frozen_selection_sha256"] == AUDITS["selection_manifest"]
        and report["new_records_sha256"] == AUDITS["records"]
        and report["pilot_recheck_records_sha256"] == AUDITS["pilot_records"],
        "Expanded audit ancestry mismatch",
    )
    declared_paths = {r["ts_path"] for r in frozen["new_wave_pairs"]}
    familiar_paths = {
        r["trajectory_locator"]
        for r in report["new_history_reports"]
        if set(r["data_payload_width_counts"]) == {"9876"}
    }
    ref.require(
        len(declared_paths) == 312
        and familiar_paths <= declared_paths
        and {r["trajectory_locator"] for r in chosen} == familiar_paths,
        "Expanded history selection mismatch",
    )
    fix = json.loads(ref.checked(c["fixity"]))
    fixity = {e["relative_path"]: e["sha256"] for e in fix["files"]}
    ref.require(
        len(fixity) == len(fix["files"]) == 624
        and fix["frozen_selection_sha256"] == AUDITS["selection_manifest"]
        and fix["prior_coverage_report_sha256"] == AUDITS["expansion_report"],
        "Wrong expanded full fixity",
    )
    ref.require(
        set(fixity)
        == {n for r in frozen["new_wave_pairs"] for n in (r["ts_path"], r["ev_path"])},
        "Full fixity/frozen selection mismatch",
    )
    pilot_manifest, old, old_selection, controls = retained_pilot(c)
    ref.require(
        c["files"] == pilot_manifest["configuration"]["files"]
        and c["raw_root"] == pilot_manifest["configuration"]["raw_root"],
        "Changed pinned reference configuration",
    )
    ref.require(
        {r["record_id"] for r in old_selection} == {r["record_id"] for r in pilot_rows},
        "Pilot accepted membership changed",
    )
    payloads, selection, za, a, events = ref.extract_states(
        chosen, fixity, c["raw_root"], signed_zero=True
    )
    ref.require(za == old[16:2576], "Pilot/primary species order mismatch")
    expected_events = [
        {k: e[k] for k in ("trajectory_locator", "ordinal", "raw_binary64_hex")}
        for e in report["signed_zero_disposition"]["events"]
    ]
    ref.require(events == expected_events, "Signed-zero disposition changed")
    for seq, row in selection.items():
        row.update(role="new", trajectory_locator=chosen[seq - 1]["trajectory_locator"])
    for seq, (state, source, vector) in enumerate(controls, NEW + 1):
        payloads[seq] = struct.pack("<i", seq) + state[4:]
        selection[seq] = dict(
            source,
            sequence=seq,
            role="repeat_control",
            source_pilot_sequence=source["sequence"],
            input_state_sha256=ref.digest(payloads[seq][: ref.PREFIX.size + 1280]),
        )
    states = (
        ref.HEADER.pack(ref.MAGIC, 2, NEW + 2, ref.NY)
        + za
        + b"".join(payloads[i] for i in range(1, NEW + 3))
    )
    maps = ref.expected_maps(assets["network/nets3"], assets["network/nets4"])
    mapping_terms(ref.parse_maps(maps), a)
    dest = Path(destination).resolve()
    ref.require(
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
    for name in (*ref.PUBLIC, "primary.py"):
        shutil.copyfile(ref.HERE / name, dest / name)
    ref.write(dest / "selection.json", list(selection.values()))
    ref.write(
        dest / "d017-controls.json",
        {
            str(seq): {"record_id": row["record_id"], "fresh_hex": vector.hex()}
            for seq, (_, row, vector) in enumerate(controls, NEW + 1)
        },
    )
    ref.write(
        dest / "population.json",
        {
            "new": [
                {k: r[k] for k in ("record_id", "trajectory_locator", "ordinal")}
                for r in chosen
            ],
            "pilot": [
                {k: r[k] for k in ("record_id", "trajectory_locator", "ordinal")}
                for r in pilot_rows
            ],
            "signed_zero_equivalence_events": events,
        },
    )
    manifest = {
        "schema": "crucible.rhs-primary-preparation.v1",
        "status": "PREPARED ONLY; no producer build/run authority or scientific eligibility",
        "configuration": c,
        "selection_count": NEW + 2,
        "batch": BATCH,
        "files": {
            str(p.relative_to(dest)): {
                "bytes": p.stat().st_size,
                "sha256": ref.digest(p.read_bytes()),
            }
            for p in sorted(dest.rglob("*"))
            if p.is_file()
        },
    }
    ref.write(dest / "manifest.json", manifest)
    ref.verify(dest)
    return manifest


def verify_metadata(root, manifest, state):
    ref.require(manifest["batch"] == BATCH, "Wrong primary finite batch contract")
    pop = ref.load(root / "population.json")
    population(pop["new"], pop["pilot"], pop["new"] + pop["pilot"])
    rows = ref.load(root / "selection.json")
    controls = ref.load(root / "d017-controls.json")
    ref.require(
        len(rows) == NEW + 2 and set(controls) == {str(NEW + 1), str(NEW + 2)},
        "Wrong primary selection/control count",
    )
    z, a = ref.species_ids(state[16:2576])
    ids = set()
    for k, row in enumerate(rows, 1):
        b = state[2576 + (k - 1) * WIDTH : 2576 + k * WIDTH]
        prefix, y = b[: ref.PREFIX.size], b[ref.PREFIX.size : ref.PREFIX.size + 1280]
        seq, slab, zone, ordinal, *_ = ref.PREFIX.unpack(prefix)
        ref.validate_state(prefix, y, z, a)
        ref.require(
            all(math.isfinite(v) for v in struct.unpack("<160d", b[-1280:])),
            "Nonfinite stored audit label",
        )
        ref.require(
            seq == row["sequence"] == k
            and row["ordinal"] == ordinal
            and row["record_id"] == f"Run_slab_{slab:03d}/Run/ts_{zone:04d}#{ordinal}"
            and row["input_state_sha256"] == ref.digest(prefix + y),
            "Primary state ordering/identity/bits mismatch",
        )
        ref.require(row["record_id"] not in ids, "Duplicate primary state")
        ids.add(row["record_id"])
        if k <= NEW:
            ref.require(
                row["role"] == "new"
                and row["record_id"] == pop["new"][k - 1]["record_id"],
                "Primary new-state membership/order mismatch",
            )
        else:
            control = controls[str(k)]
            ref.require(
                row["role"] == "repeat_control"
                and 1 <= row["source_pilot_sequence"] <= PILOT
                and row["record_id"] in {r["record_id"] for r in pop["pilot"]}
                and row["record_id"] == control["record_id"],
                "Invalid repeat-control ancestry",
            )
            vector = bytes.fromhex(control["fresh_hex"])
            ref.require(
                len(vector) == 1280
                and all(math.isfinite(x) for x in struct.unpack("<160d", vector)),
                "Invalid retained control vector",
            )
