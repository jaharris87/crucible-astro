"""One quarantined D-021 union from complete D-020 and D-023 native-RHS packets."""

import argparse
import json
import re
import struct
from collections import Counter
from pathlib import Path

from crucible import rhs_data as wire
from crucible.partitions import digest as json_digest

SCHEMA = "crucible.primary-native-rhs-union.v1"
PILOT, NEW, PILOT_HISTORIES, NEW_HISTORIES = 5157, 19157, 80, 300
PILOT_CONTROLS = (58, 62)
COUNTS = {
    "histories": 380,
    "ordinary_records": 30472,
    "candidate_records": 24314,
    "excluded_records": 6158,
    "groups": 94,
}
CORE_ASSETS = 26
RAW_FIELDS = (
    "sequence",
    "ordinal",
    "record_id",
    "raw_ts_sha256",
    "raw_ev_sha256",
    "raw_payload_sha256",
    "input_state_sha256",
)


def _state(packet, k):
    return packet["states"][2576 + k * 2620 : 2576 + (k + 1) * 2620]


def _result(packet, k):
    return packet["fresh"][2576 + k * 21600 : 2576 + (k + 1) * 21600]


def _membership(partition, packets, selected):
    """Join the bound working construction; never copy its roles into HDF5."""
    require = wire.require
    meta = partition["metadata"]
    require(
        partition["schema_version"] == 1
        and partition["status"]
        == "CANDIDATE_MECHANICAL_PASS_PENDING_SCIENTIFIC_QUALIFICATION",
        "working partition schema/status",
    )
    require(
        partition["counts"] == COUNTS
        and all(type(value) is int for value in partition["counts"].values()),
        "working partition counts",
    )
    p = packets["pilot"]
    species = [{"id": f"Z{z}A{a}", "Z": z, "A": a} for z, a in p["species"]]
    species_bytes = struct.pack("<i", 160) + p["states"][16:2576]
    require(
        meta["n_species"] == 160
        and meta["species"] == species
        and meta["species_payload_sha256"] == wire.digest(species_bytes),
        "working partition species/order",
    )
    require(
        meta["units"]
        == {
            "Y": "molar_abundance_Y",
            "temperature": "GK",
            "density": "g/cm^3",
            "time": "s",
        },
        "working partition units",
    )
    require(
        meta["reference_config_sha256"] == p["inputs"]["preparation"]["sha256"],
        "working partition reference ancestry",
    )
    histories = {h["particle0"]: h for h in partition["histories"]}
    require(
        len(histories) == len(partition["histories"]) == COUNTS["histories"]
        and all(type(k) is int and 0 <= k < 2**63 for k in histories),
        "working history identities",
    )
    groups = partition["groups"]
    require(len(groups) == COUNTS["groups"], "working group count")
    allocated = [v for g in groups for v in g["members"]]
    require(
        len(allocated) == len(set(allocated)) and set(allocated) == set(histories),
        "working group allocation",
    )
    raw_owner = {}
    for particle, h in histories.items():
        require(
            h["parent_id"] == meta["parent_id"]
            and h["role"] in ("train", "validation", "test")
            and type(h["group"]) is int
            and 0 <= h["group"] < len(groups),
            "working history parent/role",
        )
        g = groups[h["group"]]
        require(
            particle in g["members"] and h["role"] == g["role"],
            "working history/group role",
        )
        require(
            isinstance(h["known_related"], list)
            and all(
                q in histories and histories[q]["group"] == h["group"]
                for q in h["known_related"]
            ),
            "working related ancestry",
        )
        require(
            isinstance(h["raw_ancestors"], list)
            and len(h["raw_ancestors"]) == 2
            and all(
                isinstance(v, str) and re.fullmatch("[0-9a-f]{64}", v)
                for v in h["raw_ancestors"]
            ),
            "working raw ancestry",
        )
        for ancestor in h["raw_ancestors"]:
            require(
                raw_owner.setdefault(ancestor, h["group"]) == h["group"],
                "working raw crossover",
            )
    records = {r["record_id"]: r for r in partition["records"]}
    require(
        len(records) == len(partition["records"]) == COUNTS["ordinary_records"],
        "working record identities/count",
    )
    canonical = set()
    for rid, r in records.items():
        particle = r["particle0"]
        require(
            particle in histories and type(r["ordinal"]) is int and r["ordinal"] > 0,
            "working record parent/ordinal",
        )
        h = histories[particle]
        require(
            (particle, r["ordinal"]) not in canonical,
            "working duplicate canonical identity",
        )
        canonical.add((particle, r["ordinal"]))
        require(
            rid == f"{h['trajectory_locator']}#{r['ordinal']}"
            and r["parent_id"] == meta["parent_id"]
            and r["group"] == h["group"]
            and r["role"] == h["role"],
            "working record identity/role",
        )
        require(
            type(r["candidate"]) is bool
            and r["scientific_eligibility"] is False
            and isinstance(r["exclusion_reasons"], list)
            and bool(r["exclusion_reasons"]) != r["candidate"],
            "working exclusion/eligibility",
        )
        require(
            r["n_species"] == 160 and r["species_sha256"] == json_digest(species),
            "working record species",
        )
        require(
            isinstance(r["raw_ancestors"], list)
            and all(
                isinstance(v, str) and re.fullmatch("[0-9a-f]{64}", v)
                for v in r["raw_ancestors"]
            ),
            "working record ancestry",
        )
        for ancestor in r["raw_ancestors"]:
            require(
                raw_owner.setdefault(ancestor, h["group"]) == h["group"],
                "working record raw crossover",
            )
        require(
            isinstance(r["derived_from"], list)
            and all(
                source in records
                and records[source]["group"] == r["group"]
                and records[source]["role"] == r["role"]
                for source in r["derived_from"]
            ),
            "working derived ancestry",
        )
    # The bound format supports known derivations; reject cycles as well as crossover.
    pending = {rid: set(r["derived_from"]) for rid, r in records.items()}
    children = {rid: [] for rid in records}
    for rid, parents in pending.items():
        for source in parents:
            children[source].append(rid)
    ready = [rid for rid, parents in pending.items() if not parents]
    seen = 0
    while ready:
        rid = ready.pop()
        seen += 1
        for child in children[rid]:
            pending[child].remove(rid)
            if not pending[child]:
                ready.append(child)
    require(seen == len(records), "working derived ancestry cycle")
    candidates = {rid: r for rid, r in records.items() if r["candidate"]}
    require(
        len(candidates) == COUNTS["candidate_records"]
        and len(records) - len(candidates) == COUNTS["excluded_records"],
        "working candidate/exclusion counts",
    )
    require(set(candidates) == set(selected), "exact working candidate membership")
    for rid, (source, k) in selected.items():
        packet = packets[source]
        sel = packet["selection"][k]
        r = candidates[rid]
        h = histories[r["particle0"]]
        state = _state(packet, k)
        row, tracer = struct.unpack_from("<2i", state, 4)
        locator = rid.split("#")[0]
        require(
            h["trajectory_locator"] == locator
            and h["stored_row"] == row
            and h["raw_paths"] == [locator, locator.replace("/ts_", "/ev_")]
            and set(h["raw_ancestors"]) == {sel["raw_ts_sha256"], sel["raw_ev_sha256"]},
            "working selected raw ancestry",
        )
        require(
            locator == f"Run_slab_{row:03d}/Run/ts_{tracer:04d}",
            "working selected locator",
        )
        require(
            r["input_sha256"]
            == wire.digest(
                bytes.fromhex(meta["species_payload_sha256"])
                + state[28:44]
                + state[60:1340]
            ),
            "working full-state input fingerprint",
        )
        require(
            all(
                struct.pack("<d", r[key]) == state[offset : offset + 8]
                for key, offset in (("time", 20), ("temperature", 28), ("density", 36))
            ),
            "working state condition bits",
        )
    return candidates, {
        "candidate_records": len(candidates),
        "histories": len(histories),
        "groups": len(groups),
        "candidate_role_counts": dict(Counter(r["role"] for r in candidates.values())),
        "history_role_counts": dict(Counter(h["role"] for h in histories.values())),
        "group_role_counts": dict(Counter(g["role"] for g in groups)),
        "known_ancestry_and_roles_unchanged": True,
        "scientific_eligibility": False,
    }


def materialize(config_path, destination):
    """Validate exactly two finite packets, deduplicate only their declared controls."""
    require = wire.require
    config_path = wire.regular_path(config_path)
    dest = wire.regular_path(destination)
    config_bytes = config_path.read_bytes()
    c = wire.json_load(config_bytes)
    require(
        set(c)
        == {"schema", "dataset_id", "dataset_version", "packets", "working_partition"}
        and c["schema"] == SCHEMA,
        "primary union recipe schema/keys",
    )
    require(
        all(isinstance(c[k], str) and c[k] for k in ("dataset_id", "dataset_version")),
        "dataset identity required",
    )
    require(set(c["packets"]) == {"pilot", "primary"}, "exact two packet identities")
    require(
        all(set(v) == {"inputs", "expected"} for v in c["packets"].values()),
        "packet recipe fields",
    )
    require(
        c["packets"]["pilot"]["expected"]["count"] == PILOT
        and c["packets"]["pilot"]["expected"]["exact_controls"] == list(PILOT_CONTROLS),
        "pilot finite count/controls",
    )
    selection_sha = c["packets"]["primary"]["inputs"]["selection"]["sha256"]
    batch = {
        "calls": NEW + 2,
        "new_states": NEW,
        "repeat_controls": 2,
        "new_histories": NEW_HISTORIES,
        "call_histories": NEW_HISTORIES + 1,
        "repeat_control_sequences": [NEW + 1, NEW + 2],
        "selection_sha256": selection_sha,
    }
    packets = {}
    for name in ("pilot", "primary"):
        recipe = c["packets"][name]
        packets[name] = wire._read_packet(
            recipe["inputs"],
            recipe["expected"],
            dest,
            config_path,
            primary_batch=batch if name == "primary" else None,
            pilot_count=PILOT,
            pilot_histories=PILOT_HISTORIES,
        )
        packets[name]["inputs"] = recipe["inputs"]
    old, new = packets["pilot"], packets["primary"]
    require(old["species"] == new["species"], "packet species/order mismatch")
    oc, nc = old["preparation"]["configuration"], new["preparation"]["configuration"]
    require(
        isinstance(oc.get("files"), dict)
        and len(oc["files"]) == CORE_ASSETS
        and oc["files"] == nc.get("files")
        and oc.get("raw_root") == nc.get("raw_root")
        and isinstance(oc.get("raw_root"), str)
        and Path(oc["raw_root"]).is_absolute(),
        "pinned core reference/configuration mismatch",
    )
    for name, entry in oc["files"].items():
        require(
            set(entry) == {"path", "sha256"}
            and isinstance(entry["path"], str)
            and Path(entry["path"]).is_absolute()
            and isinstance(entry["sha256"], str)
            and re.fullmatch("[0-9a-f]{64}", entry["sha256"]),
            "core reference asset identity",
        )
        for packet in (old, new):
            declared = packet["preparation"]["files"].get(name)
            require(
                isinstance(declared, dict)
                and set(declared) == {"bytes", "sha256"}
                and type(declared["bytes"]) is int
                and declared["bytes"] > 0
                and declared["sha256"] == entry["sha256"],
                "core reference asset/manifest ancestry",
            )
    for field, key in (
        ("pilot_bundle", "preparation"),
        ("pilot_fresh", "fresh"),
        ("pilot_comparison", "comparison"),
        ("pilot_receipt", "execution"),
    ):
        require(
            nc[field]["sha256"] == old["inputs"][key]["sha256"],
            f"primary declared pilot ancestry: {key}",
        )
    selected = {
        row["record_id"]: ("pilot", k) for k, row in enumerate(old["selection"])
    }
    old_histories = {rid.split("#")[0] for rid in selected}
    new_histories = set()
    for k, row in enumerate(new["selection"]):
        rid = row["record_id"]
        if k < NEW:
            require(
                rid not in selected and rid.split("#")[0] not in old_histories,
                "unexpected new/pilot overlap",
            )
            selected[rid] = ("primary", k)
            new_histories.add(rid.split("#")[0])
        else:
            control = PILOT_CONTROLS[k - NEW]
            require(
                row["source_pilot_sequence"] == control
                and rid == old["selection"][control - 1]["record_id"],
                "repeat control identity/pilot sequence",
            )
            original = old["selection"][control - 1]
            require(
                all(
                    row[field] == original[field]
                    for field in (
                        "record_id",
                        "ordinal",
                        "raw_ts_sha256",
                        "raw_ev_sha256",
                        "raw_payload_sha256",
                    )
                ),
                "repeat control raw ancestry",
            )
            require(
                _state(new, k)[4:] == _state(old, control - 1)[4:],
                "repeat control full-state/condition bits",
            )
            require(
                _result(new, k)[84:92] == _result(old, control - 1)[84:92]
                and _result(new, k)[3936:5216] == _result(old, control - 1)[3936:5216],
                "repeat control native Ye/fresh RHS bits",
            )
    require(
        len(selected) == PILOT + NEW
        and len(old_histories) == PILOT_HISTORIES
        and len(new_histories) == NEW_HISTORIES,
        "union finite state/history counts",
    )
    partition_bytes = wire.checked(c["working_partition"])
    partition_path = wire.regular_path(c["working_partition"]["path"])
    require(
        not dest.is_relative_to(partition_path.parent)
        and not partition_path.is_relative_to(dest),
        "destination collides with working partition",
    )
    candidates, proof = _membership(wire.json_load(partition_bytes), packets, selected)
    require(
        len({(r["particle0"], r["ordinal"]) for r in candidates.values()})
        == len(selected),
        "union canonical duplicate",
    )
    ordered = sorted(
        selected,
        key=lambda rid: (candidates[rid]["particle0"], candidates[rid]["ordinal"]),
    )
    arrays = {name: [] for name in old["arrays"]}
    selection = []
    sources = []
    calls = []
    receipts = []
    particles = []
    for seq, rid in enumerate(ordered, 1):
        name, k = selected[rid]
        packet = packets[name]
        for field in arrays:
            arrays[field].append(
                seq if field == "sequence" else packet["arrays"][field][k]
            )
        selection.append({field: packet["selection"][k][field] for field in RAW_FIELDS})
        sources.append(name)
        calls.append(k + 1)
        receipts.append(packet["inputs"]["execution"]["sha256"])
        particles.append(candidates[rid]["particle0"])
    entries = [
        c["working_partition"],
        *(entry for packet in packets.values() for entry in packet["entries"]),
    ]
    for entry in entries:
        wire.checked(entry)
    import h5py

    dest.mkdir()
    output = dest / "dataset.h5"
    wire._write_hdf(output, c, arrays, old["species"], selection)
    with h5py.File(output, "r+") as h:
        h.create_dataset("particle0", data=particles, dtype="<i8")
        h.create_dataset("source/call_sequence", data=calls, dtype="<i4")
        for name, values in (("packet", sources), ("execution_sha256", receipts)):
            h.create_dataset(
                "source/" + name, data=values, dtype=h5py.string_dtype("utf-8")
            )
    manifest = {
        "schema": SCHEMA,
        "dataset_id": c["dataset_id"],
        "dataset_version": c["dataset_version"],
        "count": len(ordered),
        "species_Z_A": old["species"],
        "units": wire.UNITS,
        "recipe": c,
        "recipe_sha256": wire.digest(config_bytes),
        "scientific_eligibility": {
            use: {"eligible": False, "reason": reason}
            for use, reason in wire.REASONS.items()
        },
        "working_membership_proof": proof,
        "canonical_order": "numeric particle0, raw ordinal; packet call_sequence is separate",
        "repeated_controls_omitted": list(PILOT_CONTROLS),
        "original_state_provenance": {
            "selection_parents": {
                name: packet["inputs"]["selection"] for name, packet in packets.items()
            },
            "historical_build_association": "unverified; see raw parent card",
        },
        "new_label_provenance": {
            name: {
                key: packet["inputs"][key]
                for key in (
                    "preparation",
                    "executable",
                    "fresh",
                    "components",
                    "comparison",
                    "execution",
                )
            }
            for name, packet in packets.items()
        },
        "software": {
            "union_source_sha256": wire.digest(Path(__file__).read_bytes()),
            "packet_reader_sha256": wire.digest(Path(wire.__file__).read_bytes()),
            "h5py": h5py.__version__,
            "hdf5": h5py.version.hdf5_version,
        },
        "output": {
            "path": "dataset.h5",
            "bytes": output.stat().st_size,
            "sha256": wire.digest(output.read_bytes()),
        },
    }
    with (dest / "manifest.json").open("x") as stream:
        stream.write(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        materialize(args.config, args.destination)
    except (ValueError, KeyError, TypeError, OSError, struct.error) as error:
        parser.exit(1, f"primary union refused: {error}\n")


if __name__ == "__main__":
    main()
