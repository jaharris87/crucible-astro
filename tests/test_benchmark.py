"""Public synthetic accepted-view mechanics, with no real records or receipts."""

import copy
import hashlib
import json
import shutil
import struct

import h5py
import numpy as np
import pytest

from crucible import benchmark as bm
from crucible import partitions as part
from crucible import rhs_data as wire

TEST_USES = {
    "state_training": True,
    "rhs_training": True,
    "energy_training": False,
    "rollout_reference": False,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


@pytest.fixture
def local_view(tmp_path, monkeypatch):
    """An independent literal 16-history population with all 160 species.

    The private test pin replaces only the production overlay trust root. There
    is no API allowing arbitrary user-supplied hashes to qualify new data.
    """
    species = [
        {"id": f"Z{z}A{a}", "Z": z, "A": a}
        for z, a in ([[0, 1], [1, 1]] + [[1, a] for a in range(2, 160)])
    ]
    za = [[s["Z"], s["A"]] for s in species]
    species_sha = sha(
        struct.pack("<i", 160)
        + struct.pack("<320d", *[s["Z"] for s in species], *[s["A"] for s in species])
    )
    references = {
        name: {
            key: {
                "path": f"/unneeded/{name}/{key}",
                "sha256": sha(f"{name}-{key}".encode()),
            }
            for key in ("preparation", "execution")
        }
        for name in ("pilot", "primary")
    }
    meta = {
        "pool_id": "synthetic",
        "parent_id": "synthetic-parent",
        "namespace": part.NAMESPACE,
        "protocol_tag": part.TAG,
        "working_scope_acceptance": "synthetic only",
        "units": part.UNITS,
        "reference_config_sha256": references["pilot"]["preparation"]["sha256"],
        "species_payload_sha256": species_sha,
        "species": species,
        "n_species": 160,
        "measured_time_window_s": [1.0, 2.0],
    }
    groups = [[2 * i, 2 * i + 1] for i in range(8)]
    roles = ["train"] * 6 + ["validation", "test"]
    histories, records, vectors, conditions, ye = [], [], [], [], []
    for p in range(16):
        value = 1.0 if p == 0 else 10.0 if p == 1 else 5.0
        y0 = 0.01 if p == 0 else 0.1 if p == 1 else 0.03 + p * 0.001
        y = [y0, 0.75, -0.0] + [0.0] * 157
        native = 0.75 / (y0 + 0.75)
        histories.append(
            {
                "particle0": p,
                "parent_id": "synthetic-parent",
                "stored_row": 2 if p in (2, 3, 4, 5) else 1,
                "category": "synthetic-category",
                "raw_ancestors": [sha(f"ancestor{p}".encode())],
                "known_related": [p ^ 1],
            }
        )
        records.append(
            {
                "record_id": f"r{p}",
                "particle0": p,
                "ordinal": 1,
                "parent_id": "synthetic-parent",
                "n_species": 160,
                "species_sha256": part.digest(species),
                "candidate": True,
                "exclusion_reasons": [],
                "temperature": value,
                "density": value,
                "source_formula_Ye": native,
                "time": 1.5,
                "input_sha256": sha(
                    bytes.fromhex(species_sha) + struct.pack("<162d", value, value, *y)
                ),
                "derived_from": [],
                "raw_ancestors": [],
            }
        )
        vectors.append(y)
        conditions.append(value)
        ye.append(native)
    pool = {
        "metadata": meta,
        "histories": histories,
        "records": records,
        "source_exclusions": [],
    }
    contract = {
        "metadata": copy.deepcopy(meta),
        "pool_sha256": part.pool_digest(pool),
        "counts": {
            "histories": 16,
            "ordinary_records": 16,
            "candidate_records": 16,
            "excluded_records": 0,
            "groups": 8,
        },
        "accepted_groups": [
            {"members": g, "role": r} for g, r in zip(groups, roles, strict=True)
        ],
    }
    data = {
        "pool": pool,
        "contract": contract,
        "groups": groups,
        "scoring": {"species": species},
    }
    payload = tmp_path / "payload.h5"
    strings = h5py.string_dtype("utf-8")
    with h5py.File(payload, "x") as h:
        h.create_dataset("species_Z_A", data=za, dtype="<i4")
        for field, values in {
            "time": [1.5] * 16,
            "T9": conditions,
            "rho": conditions,
            "internal_dt": [0.01] * 16,
            "native_EOS_Ye": ye,
            "stored_energy_unqualified": [-0.0] * 16,
            "Y": vectors,
            "fresh_rhs": [[p, -p, -0.0] + [0.0] * 157 for p in range(16)],
        }.items():
            h.create_dataset(field, data=values, dtype="<f8").attrs["units"] = (
                wire.UNITS[field]
            )
        for field, values in {
            "sequence": range(1, 17),
            "particle0": range(16),
            "raw_ordinal": [1] * 16,
            "row_id": [1] * 16,
            "tracer_id": range(16),
            "step": [10] * 16,
            "source/call_sequence": range(16, 0, -1),
        }.items():
            h.create_dataset(
                field, data=list(values), dtype="<i8" if field == "particle0" else "<i4"
            )
        h.create_dataset(
            "raw_provenance/record_id", data=[f"r{p}" for p in range(16)], dtype=strings
        )
        h.create_dataset(
            "raw_provenance/input_state_sha256",
            data=[
                sha(
                    struct.pack(
                        "<5i5d",
                        16 - p,
                        1,
                        p,
                        1,
                        10,
                        1.5,
                        conditions[p],
                        conditions[p],
                        0.01,
                        -0.0,
                    )
                    + struct.pack("<160d", *vectors[p])
                )
                for p in range(16)
            ],
            dtype=strings,
        )
        names = ["pilot" if p % 2 == 0 else "primary" for p in range(16)]
        h.create_dataset("source/packet", data=names, dtype=strings)
        h.create_dataset(
            "source/execution_sha256",
            data=[references[n]["execution"]["sha256"] for n in names],
            dtype=strings,
        )
        for use in TEST_USES:
            h.create_dataset("eligibility/" + use, data=[False] * 16, dtype="?")

    scope = {
        "benchmark_id": bm.NAME,
        "version": bm.VERSION,
        "qualified_uses": ["state_training", "rhs_training"],
        "excluded_uses": {
            "energy_training": "excluded",
            "rollout_reference": "excluded",
        },
        "limitations": ["synthetic fixture only"],
    }
    data["receipt"] = {
        "html_url": "https://example.invalid/synthetic-only",
        "user": {"login": "jaharris87"},
        "author_association": "OWNER",
    }
    overlay = {
        "schema": "crucible.qualified-native-benchmark-overlay.v1",
        "overlay_id": bm.NAME,
        "overlay_version": bm.VERSION,
        "status": "QUALIFIED_NAMED_NUMERICAL_BENCHMARK_ONLY",
        "scope": scope,
        "accepted_proposal": {"sha256": sha(b"synthetic-proposal")},
        "accepted_packet_manifest": {"sha256": sha(b"synthetic-packet")},
        "native_references": references,
        "scoring_module": {"sha256": sha(b"old-scorer")},
    }

    def save(name, value):
        path = tmp_path / (name + ".json")
        raw = encoded(value)
        path.write_bytes(raw)
        return {"path": path.name, "sha256": sha(raw), "bytes": len(raw)}

    def bind(*, trust=True):
        contract["pool_sha256"] = part.pool_digest(pool)
        candidate = part.construct_candidate(pool, contract, groups)
        membership = {
            role: sorted(
                r["record_id"] for r in candidate["records"] if r["role"] == role
            )
            for role in part.ROLES
        }
        membership["exclusions"] = {}
        data["candidate"], data["membership"] = candidate, membership
        q = {
            "scope": scope,
            "decision": "D-025",
            "human_decision": data["receipt"]["html_url"],
            "human_receipt_source_sha256": sha(encoded(data["receipt"])),
            "accepted_proposal_sha256": overlay["accepted_proposal"]["sha256"],
            "accepted_packet_manifest_sha256": overlay["accepted_packet_manifest"][
                "sha256"
            ],
        }
        qb = save("qualification", q)
        eligibility = {
            r["record_id"]: {
                "eligible": True,
                "qualification_sha256": qb["sha256"],
                "uses": TEST_USES.copy(),
            }
            for r in records
        }
        acceptance = {
            "human_decision": q["human_decision"],
            "human_qualification_sha256": qb["sha256"],
            "accepted_proposal_sha256": q["accepted_proposal_sha256"],
            "candidate_sha256": part.digest(candidate),
            "membership_sha256": part.digest(membership),
            "eligibility_sha256": part.digest(eligibility),
        }
        overlay["files"] = {
            "human-qualification.json": qb,
            "human-receipt-source.json": save("receipt", data["receipt"]),
            "membership.json": save("membership", membership),
            "eligibility.json": save("eligibility", eligibility),
            "final-acceptance.json": save("acceptance", acceptance),
        }
        overlay.update(
            working_candidate=save("candidate", candidate),
            original_groups=save("groups", groups),
            original_mechanical_inputs={
                "pool": save("pool", pool),
                "contract": save("contract", contract),
            },
            scoring_configuration=save("scoring", data["scoring"]),
            role_counts={r: len(membership[r]) for r in part.ROLES},
            payload={
                "path": payload.name,
                "sha256": sha(payload.read_bytes()),
                "bytes": payload.stat().st_size,
            },
        )
        manifest = {
            "output": {"sha256": overlay["payload"]["sha256"]},
            "count": 16,
            "new_label_provenance": references,
            "units": wire.UNITS,
            "species_Z_A": za,
        }
        overlay["payload_manifest"] = save("manifest", manifest)
        save("overlay", overlay)
        if trust:
            monkeypatch.setattr(bm, "_OVERLAY_SHA256", sha(encoded(overlay)))

    bind()
    return tmp_path, data, overlay, bind


def load(view, **kwargs):
    root = view[0]
    return bm.load_benchmark(
        bm.NAME,
        bm.VERSION,
        use="rhs_training",
        split="train",
        config={"overlay": root / "overlay.json"},
        **kwargs,
    )


def test_scientist_arrays_exact_membership_and_distinct_digests(local_view):
    root, data, overlay, _ = local_view
    before = {p.name: sha(p.read_bytes()) for p in root.iterdir()}
    result = load(local_view)
    ids = data["membership"]["train"]
    assert result["record_id"].tolist() == ids
    assert ids != sorted(ids, key=lambda s: int(s[1:]))  # positional joins would fail
    assert result["Y"].shape == result["fresh_rhs"].shape == (12, 160)
    assert result["particle0"].tolist() == [int(r[1:]) for r in ids]
    assert np.signbit(result["Y"][:, 2]).all()
    assert np.signbit(result["fresh_rhs"][:, 2]).all()
    assert result["fresh_rhs"][:, 0].tolist() == result["particle0"].tolist()
    assert result["source_call_sequence"].tolist() == [16 - int(r[1:]) for r in ids]
    assert (result["physical_input_sha256"] != result["source_input_sha256"]).all()
    assert result["metadata"]["units"]["fresh_rhs"] == "molar_abundance_Y/s"
    assert (
        result["metadata"]["original_scoring_source_sha256"]
        == overlay["scoring_module"]["sha256"]
    )
    assert {p.name: sha(p.read_bytes()) for p in root.iterdir()} == before
    for split in ("validation", "test"):
        out = bm.load_benchmark(
            bm.NAME,
            bm.VERSION,
            use="state_training",
            split=split,
            config={"overlay": root / "overlay.json"},
        )
        assert out["record_id"].tolist() == data["membership"][split]
        assert out["Y"].shape == (2, 160)


def test_relocation_uses_content_identity_and_config_relative_paths(
    local_view, tmp_path
):
    root, _, overlay, _ = local_view
    relocated = root / "elsewhere"
    relocated.mkdir()
    digest = overlay["payload"]["sha256"]
    shutil.move(root / "payload.h5", relocated / "renamed.h5")
    config = {
        "overlay": "overlay.json",
        "path_overrides": {digest: "elsewhere/renamed.h5"},
    }
    (root / "config.json").write_bytes(encoded(config))
    out = bm.load_benchmark(
        bm.NAME,
        bm.VERSION,
        use="rhs_training",
        split="test",
        config=root / "config.json",
    )
    assert out["record_id"].tolist() == ["r14", "r15"]
    assert not (root / "payload.h5").exists()


@pytest.mark.parametrize(
    "argument,value,reason",
    [
        ("name", "other", "name/version"),
        ("version", "next", "name/version"),
        ("split", "all", "unknown split"),
        ("split", [], "unknown split"),
        ("use", "energy_training", "unqualified use"),
        ("use", "rollout_reference", "unqualified use"),
        ("use", [], "unqualified use"),
        ("config", {}, "config requires"),
        ("config", {"overlay": "unused", "trust": "anything"}, "config requires"),
        ("config", {"overlay": "unused", "path_overrides": []}, "path_overrides"),
        (
            "config",
            {"overlay": "unused", "path_overrides": {"bad": "file"}},
            "path_overrides",
        ),
    ],
)
def test_unknown_requests_fail_before_reading(argument, value, reason):
    arguments = dict(
        name=bm.NAME,
        version=bm.VERSION,
        use="rhs_training",
        split="train",
        config={"overlay": "unused"},
    )
    arguments[argument] = value
    with pytest.raises(ValueError, match=reason):
        bm.load_benchmark(**arguments)


def test_changed_and_coherently_rebound_artifacts_reject_without_new_acceptance(
    local_view,
):
    root, data, _, bind = local_view
    data["receipt"]["html_url"] = "https://example.invalid/changed-authority"
    bind(
        trust=False
    )  # rebind receipt, Q, eligibility, acceptance, all parents, overlay
    with pytest.raises(ValueError, match="input checksum mismatch: overlay.json"):
        load(local_view)
    assert (root / "overlay.json").exists()


@pytest.mark.parametrize(
    "name", ["payload.h5", "eligibility.json", "membership.json", "pool.json"]
)
def test_changed_consumed_file_rejects(local_view, name):
    root, _, _, _ = local_view
    with (root / name).open("ab") as stream:
        stream.write(b" ")
    with pytest.raises(ValueError, match="input checksum mismatch"):
        load(local_view)


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("species", "ordered species"),
        ("units", "dtype/units"),
        ("shape", "shape: Y"),
        ("nonfinite", "nonfinite"),
        ("masks", "quarantine masks"),
        ("record", "exact payload record join"),
        ("history", "history/ordinal"),
        ("ordering", "canonical payload ordering"),
        ("physical", "physical input fingerprint"),
        ("source", "source call digest"),
        ("execution", "source execution identity"),
    ],
)
def test_semantic_guards_beneath_hash_boundary(local_view, defect, reason):
    root, _, _, bind = local_view
    # Re-pin this synthetic test-only overlay to exercise semantic checks, rather
    # than falsely claiming that updating a production digest is acceptance.
    with h5py.File(root / "payload.h5", "r+") as h:
        if defect == "species":
            h["species_Z_A"][:2] = h["species_Z_A"][:2][::-1]
        elif defect == "units":
            h["Y"].attrs["units"] = "mass fraction"
        elif defect == "shape":
            del h["Y"]
            h.create_dataset("Y", data=np.zeros((16, 159)))
        elif defect == "nonfinite":
            h["Y"][0, 0] = float("nan")
        elif defect == "masks":
            h["eligibility/rhs_training"][0] = True
        elif defect == "record":
            h["raw_provenance/record_id"][0] = "unknown"
        elif defect == "history":
            h["raw_ordinal"][0] = 0
        elif defect == "ordering":
            h["sequence"][0] = 9
        elif defect == "physical":
            h["Y"][0, 0] = 0.02
        elif defect == "source":
            h["source/call_sequence"][0] = 1
        else:
            h["source/execution_sha256"][0] = "f" * 64
    bind()
    with pytest.raises(ValueError, match=reason):
        load(local_view)


def test_signed_zero_physical_duplicate_in_other_roles_rejects_when_loading_train(
    local_view,
):
    root, data, _, bind = local_view
    # Duplicate the validation/test physical input with opposite zero signs;
    # keep distinct exact working fingerprints and source call digests valid.
    # This specifically reaches the loader's numeric physical leakage check.
    pool = data["pool"]
    with h5py.File(root / "payload.h5", "r+") as h:
        y = h["Y"][12]
        y[2] = 0.0
        h["native_EOS_Ye"][14] = h["native_EOS_Ye"][12]
        pool["records"][14]["source_formula_Ye"] = pool["records"][12][
            "source_formula_Ye"
        ]
        h["Y"][14] = y
        r = pool["records"][14]
        r["input_sha256"] = sha(
            bytes.fromhex(pool["metadata"]["species_payload_sha256"])
            + struct.pack("<162d", 5.0, 5.0, *y)
        )
        h["raw_provenance/input_state_sha256"][14] = sha(
            struct.pack("<5i5d", 2, 1, 14, 1, 10, 1.5, 5.0, 5.0, 0.01, -0.0)
            + struct.pack("<160d", *y)
        )
    bind()
    with pytest.raises(ValueError, match="physical input crosses partitions"):
        load(local_view)


def test_duplicate_json_keys_reject(local_view):
    root = local_view[0]
    config = root / "invalid-config.json"
    config.write_text('{"overlay":"a", "overlay":"b"}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        bm.load_benchmark(
            bm.NAME, bm.VERSION, use="rhs_training", split="train", config=config
        )


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("membership", "scientific_membership"),
        ("unknown", "scientific_membership"),
        ("uses", "record qualification/use"),
        ("evidence", "record qualification/use"),
    ],
)
def test_qualified_membership_and_evidence_semantics(
    local_view, monkeypatch, defect, reason
):
    root, _, overlay, _ = local_view
    filename = (
        "membership.json" if defect in ("membership", "unknown") else "eligibility.json"
    )
    binding = overlay["files"][filename]
    path = root / binding["path"]
    value = json.loads(path.read_bytes())
    if defect == "membership":
        value["test"].append(value["train"].pop())
    elif defect == "unknown":
        value["train"][0] = "unknown-record"
    elif defect == "uses":
        value["r0"]["uses"]["energy_training"] = True
    else:
        value["r0"]["qualification_sha256"] = "0" * 64
    raw = encoded(value)
    path.write_bytes(raw)
    binding.update(sha256=sha(raw), bytes=len(raw))
    # Coherently bind serialized final acceptance to reach the semantic guard.
    ab = overlay["files"]["final-acceptance.json"]
    acceptance = json.loads((root / ab["path"]).read_bytes())
    key = "membership_sha256" if filename == "membership.json" else "eligibility_sha256"
    acceptance[key] = part.digest(value)
    raw = encoded(acceptance)
    (root / ab["path"]).write_bytes(raw)
    ab.update(sha256=sha(raw), bytes=len(raw))
    raw = encoded(overlay)
    (root / "overlay.json").write_bytes(raw)
    monkeypatch.setattr(bm, "_OVERLAY_SHA256", sha(raw))
    with pytest.raises(ValueError, match=reason):
        load(local_view)
