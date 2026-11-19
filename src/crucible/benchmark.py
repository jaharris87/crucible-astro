"""Load the exact D-025 local benchmark. See docs/science/data/LOADING.md."""

import io
import struct
from pathlib import Path

from crucible import partitions
from crucible import rhs_data as wire

NAME = "ccsn-primary-native-rhs-pointwise"
VERSION = "0.1.0"
# Independent acceptance root; deliberately not configurable by the caller.
_OVERLAY_SHA256 = "e1bcd8b3cceabf252c1307ad008cdbc4a1da1cd556e84bf923d742ce3cf2ce0c"
_USES = {
    "state_training": True,
    "rhs_training": True,
    "energy_training": False,
    "rollout_reference": False,
}


def _need(value, message):
    wire.require(value, "benchmark: " + message)


def _configuration(config):
    root = Path.cwd()
    if isinstance(config, (str, Path)):
        path = Path(config).resolve()
        root = path.parent
        config = wire.json_load(path.read_bytes())
    _need(
        isinstance(config, dict)
        and set(config) <= {"overlay", "path_overrides"}
        and isinstance(config.get("overlay"), (str, Path)),
        "config requires overlay and optional path_overrides only",
    )
    overrides = config.get("path_overrides", {})
    _need(
        isinstance(overrides, dict)
        and all(
            isinstance(k, str)
            and len(k) == 64
            and all(c in "0123456789abcdef" for c in k)
            and isinstance(v, (str, Path))
            for k, v in overrides.items()
        ),
        "path_overrides must map SHA256 strings to local paths",
    )
    return config, root, overrides


def load_benchmark(name, version, *, use, split, config):
    """Return arrays and metadata for an exact qualified membership list.

    Name/version must match NAME/VERSION. Use is state_training or rhs_training;
    split is train, validation or test. Config is a mapping or JSON file with
    overlay and optional path_overrides (SHA256 -> relocated local file path).
    Relative config paths resolve beside its JSON file, or from cwd for mappings.
    All roles are validated before selecting one. No fitting/conversion occurs.
    """
    _need(name == NAME and version == VERSION, "unknown benchmark name/version")
    _need(isinstance(use, str) and _USES.get(use) is True, "unqualified use")
    _need(isinstance(split, str) and split in partitions.ROLES, "unknown split")
    config, root, overrides = _configuration(config)
    overlay_path = (root / config["overlay"]).resolve()
    consumed = {}

    def read(entry, base):
        _need(
            isinstance(entry, dict)
            and {"path", "sha256"} <= set(entry)
            and isinstance(entry["path"], str),
            "malformed file binding",
        )
        locator = overrides.get(entry["sha256"])
        path = (
            root / locator if locator is not None else base / entry["path"]
        ).resolve()
        data = wire.checked({"path": str(path), "sha256": entry["sha256"]})
        _need("bytes" not in entry or entry["bytes"] == len(data), "file size mismatch")
        consumed[entry["sha256"]] = len(data)
        return data

    def json_read(entry, base=overlay_path.parent):
        return wire.json_load(read(entry, base))

    m = json_read({"path": str(overlay_path), "sha256": _OVERLAY_SHA256})
    _need(
        m.get("schema") == "crucible.qualified-native-benchmark-overlay.v1"
        and m.get("overlay_id") == name
        and m.get("overlay_version") == version
        and m.get("status") == "QUALIFIED_NAMED_NUMERICAL_BENCHMARK_ONLY",
        "overlay schema/name/version/status",
    )
    scope = m["scope"]
    _need(
        scope["benchmark_id"] == name
        and scope["version"] == version
        and scope["qualified_uses"] == ["state_training", "rhs_training"]
        and set(scope["excluded_uses"]) == {"energy_training", "rollout_reference"},
        "qualified scope/use mismatch",
    )
    files = m["files"]
    qualification = json_read(files["human-qualification.json"])
    receipt = json_read(files["human-receipt-source.json"])
    acceptance = json_read(files["final-acceptance.json"])
    qsha = files["human-qualification.json"]["sha256"]
    _need(
        qualification["scope"] == scope
        and qualification["decision"] == "D-025"
        and qualification["human_decision"] == receipt["html_url"]
        and receipt["user"]["login"] == "jaharris87"
        and receipt["author_association"] == "OWNER"
        and qualification["human_receipt_source_sha256"]
        == files["human-receipt-source.json"]["sha256"]
        and qualification["accepted_proposal_sha256"]
        == m["accepted_proposal"]["sha256"]
        and qualification["accepted_packet_manifest_sha256"]
        == m["accepted_packet_manifest"]["sha256"]
        and acceptance["human_decision"] == qualification["human_decision"]
        and acceptance["human_qualification_sha256"] == qsha
        and acceptance["accepted_proposal_sha256"] == m["accepted_proposal"]["sha256"],
        "human qualification/acceptance identity",
    )
    membership = json_read(files["membership.json"])
    eligibility = json_read(files["eligibility.json"])
    for evidence in eligibility.values():
        _need(
            evidence.get("eligible") is True
            and evidence.get("qualification_sha256") == qsha
            and evidence.get("uses") == _USES
            and all(type(v) is bool for v in evidence["uses"].values()),
            "record qualification/use mismatch",
        )
    candidate = json_read(m["working_candidate"])
    pool = json_read(m["original_mechanical_inputs"]["pool"])
    contract = json_read(m["original_mechanical_inputs"]["contract"])
    groups = json_read(m["original_groups"])
    partitions.validate_scientific(
        candidate,
        membership,
        eligibility,
        acceptance,
        pool=pool,
        contract=contract,
        groups=groups,
    )
    records = {r["record_id"]: r for r in candidate["records"] if r["candidate"]}
    _need(not membership["exclusions"], "accepted view must include every candidate")
    _need(
        {role: len(membership[role]) for role in partitions.ROLES} == m["role_counts"],
        "split counts differ",
    )
    manifest = json_read(m["payload_manifest"])
    scoring = json_read(m["scoring_configuration"])
    meta = pool["metadata"]
    _need(
        manifest["output"]["sha256"] == m["payload"]["sha256"]
        and manifest["count"] == len(records)
        and manifest["new_label_provenance"] == m["native_references"]
        and manifest["units"] == wire.UNITS
        and meta["species"] == scoring["species"]
        and meta["n_species"] == 160
        and meta["reference_config_sha256"]
        == m["native_references"]["pilot"]["preparation"]["sha256"],
        "payload/reference/species/unit identity mismatch",
    )

    # Consume a verified byte snapshot, avoiding a second open of a changed path.
    import h5py
    import numpy as np

    n = len(records)
    scalars = (
        "time",
        "T9",
        "rho",
        "internal_dt",
        "native_EOS_Ye",
        "stored_energy_unqualified",
    )
    integers = (
        "sequence",
        "row_id",
        "tracer_id",
        "raw_ordinal",
        "step",
        "particle0",
        "source/call_sequence",
    )
    texts = (
        "raw_provenance/record_id",
        "raw_provenance/input_state_sha256",
        "source/packet",
        "source/execution_sha256",
    )
    with h5py.File(io.BytesIO(read(m["payload"], overlay_path.parent)), "r") as h:
        za = h["species_Z_A"][:]
        _need(
            za.shape == (160, 2)
            and za.dtype == np.dtype("<i4")
            and za.tolist()
            == [[s["Z"], s["A"]] for s in meta["species"]]
            == manifest["species_Z_A"],
            "ordered species mismatch",
        )
        arrays = {}
        for field in (*scalars, "Y", "fresh_rhs", *integers):
            d = h[field]
            _need(
                d.shape == ((n, 160) if field in ("Y", "fresh_rhs") else (n,)),
                f"shape: {field}",
            )
            if field in integers:
                _need(d.dtype.kind == "i", f"integer dtype: {field}")
            else:
                _need(
                    d.dtype == np.dtype("<f8")
                    and d.attrs.get("units") == wire.UNITS[field],
                    f"dtype/units: {field}",
                )
            arrays[field] = d[:]
            _need(bool(np.isfinite(arrays[field]).all()), f"nonfinite field: {field}")
        for field in texts:
            _need(h[field].shape == (n,), f"shape: {field}")
            arrays[field] = h[field].asstr()[:]
        _need(set(h["eligibility"]) == set(_USES), "payload masks missing/unknown")
        for field in _USES:
            d = h["eligibility/" + field]
            _need(
                d.shape == (n,) and d.dtype.kind == "b" and not d[:].any(),
                "quarantine masks changed",
            )

    ids = arrays["raw_provenance/record_id"].tolist()
    _need(len(set(ids)) == n and set(ids) == set(records), "exact payload record join")
    order = [
        (int(p), int(o))
        for p, o in zip(arrays["particle0"], arrays["raw_ordinal"], strict=True)
    ]
    _need(
        order == sorted(order) and arrays["sequence"].tolist() == list(range(1, n + 1)),
        "canonical payload ordering",
    )
    species_bytes = struct.pack("<i", 160) + struct.pack("<320d", *za[:, 0], *za[:, 1])
    _need(
        wire.digest(species_bytes) == meta["species_payload_sha256"],
        "species payload digest",
    )
    prefix = bytes.fromhex(meta["species_payload_sha256"])
    role_for = {rid: role for role in partitions.ROLES for rid in membership[role]}
    physical_owner = {}
    fingerprints = []
    for i, rid in enumerate(ids):
        r = records[rid]
        _need(order[i] == (r["particle0"], r["ordinal"]), "history/ordinal join")
        for field, key in (("time", "time"), ("T9", "temperature"), ("rho", "density")):
            _need(
                struct.pack("<d", arrays[field][i]) == struct.pack("<d", r[key]),
                "condition bits differ",
            )
        vector = [arrays["T9"][i], arrays["rho"][i], *arrays["Y"][i]]
        fingerprint = wire.digest(prefix + struct.pack("<162d", *vector))
        _need(fingerprint == r["input_sha256"], "physical input fingerprint mismatch")
        fingerprints.append(fingerprint)
        # Normalize signed zero for leakage detection only; output bits stay intact.
        duplicate_key = wire.digest(
            prefix + struct.pack("<162d", *(0.0 if v == 0 else v for v in vector))
        )
        _need(
            physical_owner.setdefault(duplicate_key, role_for[rid]) == role_for[rid],
            "physical input crosses partitions",
        )
        source = arrays["source/packet"][i]
        _need(source in m["native_references"], "unknown source packet")
        _need(
            arrays["source/execution_sha256"][i]
            == m["native_references"][source]["execution"]["sha256"],
            "source execution identity",
        )
        call = int(arrays["source/call_sequence"][i])
        _need(call > 0, "source call sequence")
        call_prefix = struct.pack(
            "<5i5d",
            call,
            *(
                int(arrays[k][i])
                for k in ("row_id", "tracer_id", "raw_ordinal", "step")
            ),
            *(
                arrays[k][i]
                for k in (
                    "time",
                    "T9",
                    "rho",
                    "internal_dt",
                    "stored_energy_unqualified",
                )
            ),
        )
        source_digest = wire.digest(call_prefix + struct.pack("<160d", *arrays["Y"][i]))
        _need(
            source_digest == arrays["raw_provenance/input_state_sha256"][i],
            "source call digest mismatch",
        )

    index = {rid: i for i, rid in enumerate(ids)}
    selected = np.array([index[rid] for rid in membership[split]], dtype=np.int64)
    result = {
        field: arrays[field][selected]
        for field in (
            "Y",
            "fresh_rhs",
            "T9",
            "rho",
            "time",
            "native_EOS_Ye",
            "particle0",
            "raw_ordinal",
        )
    }
    histories = {h["particle0"]: h for h in candidate["histories"]}
    result.update(
        record_id=np.array(membership[split]),
        group=np.array(
            [records[rid]["group"] for rid in membership[split]], dtype=np.int64
        ),
        category=np.array(
            [
                histories[records[rid]["particle0"]]["category"]
                for rid in membership[split]
            ]
        ),
        physical_input_sha256=np.array(fingerprints)[selected],
        source_input_sha256=arrays["raw_provenance/input_state_sha256"][selected],
        source_packet=arrays["source/packet"][selected],
        source_call_sequence=arrays["source/call_sequence"][selected],
        species_Z_A=za,
        metadata={
            "name": name,
            "version": version,
            "use": use,
            "split": split,
            "row_order": "exact accepted membership list",
            "units": {
                field: wire.UNITS[field] for field in result if field in wire.UNITS
            },
            "ordered_species": meta["species"],
            "qualification_scope": scope,
            "overlay_sha256": _OVERLAY_SHA256,
            "payload_sha256": m["payload"]["sha256"],
            "membership_sha256": files["membership.json"]["sha256"],
            "eligibility_sha256": files["eligibility.json"]["sha256"],
            "human_qualification_sha256": qsha,
            "human_decision": qualification["human_decision"],
            "reference_identities": m["native_references"],
            "scoring_configuration_sha256": m["scoring_configuration"]["sha256"],
            "original_scoring_source_sha256": m["scoring_module"]["sha256"],
            "accepted_scoring_successor": {
                "arithmetic_identity": "crucible.native_fidelity.relative-decimal80.v1",
                "source_sha256": "c287f873ede888c12128552046176fd6618556081dc907c4fccadb491bd056b7",
                "adoption_receipt": "https://github.com/jaharris87/crucible-astro/pull/37#issuecomment-7017529239",
            },
            "verified_file_sha256": sorted(consumed),
            "role_counts": m["role_counts"],
        },
    )
    return result
