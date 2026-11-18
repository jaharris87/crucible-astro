"""Synthetic mathematical oracles; no real particle records or private files."""

import copy
import hashlib
import json

import numpy as np
import pytest

from crucible.partitions import (
    NAMESPACE,
    TAG,
    UNITS,
    PartitionError,
    construct_candidate,
    digest,
    measured_components,
    pool_digest,
    validate_scientific,
)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


@pytest.fixture
def finite_pool():
    # Eight hand-defined groups. Scalar extrema are entirely in group 0;
    # row 2 occurs in groups 1/2, whose frozen hashes begin 668f/e563.
    # Thus anchors are 0/1; the remaining rank begins 3ac4 (6),7c05 (7).
    groups = [[2 * i, 2 * i + 1] for i in range(8)]
    roles = ["train"] * 8
    roles[6], roles[7] = "validation", "test"
    species = [
        {"id": "synthetic-a", "A": 1, "Z": 0},
        {"id": "synthetic-b", "A": 2, "Z": 1},
    ]
    metadata = {
        "pool_id": "mathematical-v1",
        "parent_id": "synthetic-parent",
        "namespace": NAMESPACE,
        "protocol_tag": TAG,
        "working_scope_acceptance": "synthetic acceptance only",
        "reference_config_sha256": sha("synthetic-reference"),
        "species_payload_sha256": sha("synthetic-species-payload"),
        "units": UNITS,
        "species": species,
        "n_species": 2,
        "measured_time_window_s": [1.0, 2.0],
    }
    histories, records = [], []
    for p in range(16):
        histories.append(
            {
                "particle0": p,
                "parent_id": "synthetic-parent",
                "stored_row": 2 if p in (2, 3, 4, 5) else 1,
                "category": "synthetic-category",
                "raw_ancestors": [sha(f"raw{p}")],
                "known_related": [p ^ 1],
            }
        )
        value = 1.0 if p == 0 else 10.0 if p == 1 else 5.0
        records.append(
            {
                "record_id": f"r{p}",
                "particle0": p,
                "ordinal": 1,
                "parent_id": "synthetic-parent",
                "n_species": 2,
                "species_sha256": digest(species),
                "candidate": True,
                "exclusion_reasons": [],
                "temperature": value,
                "density": value,
                "source_formula_Ye": value / 20,
                "time": 1.5,
                "input_sha256": sha(f"input{p}"),
                "derived_from": [],
                "raw_ancestors": [],
            }
        )
    pool = {
        "metadata": metadata,
        "histories": histories,
        "records": records,
        "source_exclusions": [
            {"source": "synthetic-unparsed", "reason": "unknown-layout"}
        ],
    }
    contract = {
        "metadata": copy.deepcopy(metadata),
        "pool_sha256": pool_digest(pool),
        "counts": {
            "histories": 16,
            "ordinary_records": 16,
            "candidate_records": 16,
            "excluded_records": 0,
            "groups": 8,
        },
        "accepted_groups": [{"members": g, "role": r} for g, r in zip(groups, roles)],
    }
    return pool, contract, groups


def rebind(pool, contract):
    contract["pool_sha256"] = pool_digest(pool)


def test_independent_allocation_oracle(finite_pool):
    result = construct_candidate(*finite_pool)
    assert [g["role"] for g in result["groups"]] == ["train"] * 6 + [
        "validation",
        "test",
    ]
    assert [i for i, g in enumerate(result["groups"]) if g["training_anchor"]] == [0, 1]
    assert result["source_exclusions"] == finite_pool[0]["source_exclusions"]
    assert "PENDING_SCIENTIFIC" in result["status"]
    # Independent standard-library encoding check, with a fixed expected hash.
    encoded = json.dumps([NAMESPACE, [12, 13], TAG], separators=(",", ":")).encode()
    assert (
        hashlib.sha256(encoded).hexdigest()
        == "3ac44757739df415de4c56c4af88dc2b4dcae974ae1765e5340e572cf0100dc5"
    )


def test_input_order_invariant(finite_pool):
    pool, contract, groups = finite_pool
    control = construct_candidate(pool, contract, groups)
    pool["histories"].reverse()
    pool["records"].reverse()
    assert (
        construct_candidate(pool, contract, [g[::-1] for g in groups[::-1]]) == control
    )


def test_measured_group_oracle_and_ties():
    # Collinear positive radii: (1,1.1) and (10,11) are two nearest pairs.
    radii = [1.0, 1.1, 10.0, 11.0]
    positions = np.array([[[r, 0.0, 0.0] for r in radii]] * 3)
    assert measured_components([0, 1, 2, 3], positions) == [[0, 1], [2, 3]]
    assert measured_components([3, 1, 0, 2], positions[:, [3, 1, 0, 2]]) == [
        [0, 1],
        [2, 3],
    ]
    # Coincident points: every nearest tie selects lowest distinct canonical ID.
    assert measured_components([8, 2, 5], np.ones((2, 3, 3))) == [[2, 5, 8]]


@pytest.mark.parametrize(
    "case,code",
    [
        ("missing", "group_membership"),
        ("unknown", "group_membership"),
        ("duplicate", "group_membership"),
    ],
)
def test_bad_groups(finite_pool, case, code):
    pool, contract, groups = finite_pool
    if case == "missing":
        groups.pop()
    elif case == "unknown":
        groups[-1][-1] = 100
    else:
        groups[-1][-1] = 0
    with pytest.raises(PartitionError, match=code):
        construct_candidate(pool, contract, groups)


@pytest.mark.parametrize(
    "case,code",
    [
        ("species_order", "species"),
        ("species_count", "species"),
        ("parent", "parent"),
        ("unknown_parent", "unknown_parent"),
        ("duplicate_canonical", "duplicate_record"),
        ("wrong_count", "count"),
        ("unknown_related", "unknown_parent"),
        ("related_crossover", "related_crossover"),
        ("raw_overlap", "raw_crossover"),
        ("record_raw_overlap", "raw_crossover"),
        ("derived_copy", "derived_crossover"),
        ("unknown_derived", "unknown_parent"),
        ("duplicate_input", "duplicate_input"),
        ("missing_record", "incomplete_allocation"),
        ("changed_role", "accepted_assignment"),
        ("missing_species", "identity"),
        ("unbound_change", "pool_binding"),
        ("no_candidates", "empty_candidates"),
        ("empty_role", "empty_role"),
        ("wrong_units", "units"),
    ],
)
def test_negative_control_has_targeted_failure(finite_pool, case, code):
    pool, contract, groups = finite_pool
    construct_candidate(pool, contract, groups)  # valid control in every case
    if case == "species_order":
        pool["records"][0]["species_sha256"] = digest(pool["metadata"]["species"][::-1])
    elif case == "species_count":
        pool["records"][0]["n_species"] = 3
    elif case == "parent":
        pool["records"][0]["parent_id"] = "other-parent"
    elif case == "unknown_parent":
        pool["records"][0]["particle0"] = 100
    elif case == "duplicate_canonical":
        record = copy.deepcopy(pool["records"][0])
        record["record_id"] = "renamed-copy"
        pool["records"].append(record)
    elif case == "wrong_count":
        contract["counts"]["candidate_records"] += 1
    elif case == "unknown_related":
        pool["histories"][0]["known_related"] = [100]
    elif case == "related_crossover":
        pool["histories"][0]["known_related"] = [12]
    elif case == "raw_overlap":
        pool["histories"][12]["raw_ancestors"] = pool["histories"][0]["raw_ancestors"][
            :
        ]
    elif case == "record_raw_overlap":
        pool["records"][12]["raw_ancestors"] = pool["histories"][0]["raw_ancestors"][:]
    elif case == "derived_copy":
        # New IDs/fingerprints cannot hide an explicitly declared derived copy.
        pool["records"][12]["derived_from"] = ["r0"]
    elif case == "unknown_derived":
        pool["records"][12]["derived_from"] = ["unlisted-parent"]
    elif case == "duplicate_input":
        pool["records"][12]["input_sha256"] = pool["records"][0]["input_sha256"]
    elif case == "missing_record":
        pool["records"].pop()
    elif case == "changed_role":
        contract["accepted_groups"][6]["role"] = "train"
    elif case == "missing_species":
        pool["metadata"]["species"][0]["id"] = ""
        contract["metadata"] = copy.deepcopy(pool["metadata"])
    elif case == "unbound_change":
        pool["records"][2]["time"] += 0.01
    elif case in ("no_candidates", "empty_role"):
        excluded = (
            pool["records"] if case == "no_candidates" else pool["records"][12:14]
        )
        for r in excluded:
            r["candidate"] = False
            r["exclusion_reasons"] = ["synthetic-exclusion"]
        contract["counts"]["candidate_records"] -= len(excluded)
        contract["counts"]["excluded_records"] += len(excluded)
    elif case == "wrong_units":
        pool["metadata"]["units"] = {**UNITS, "temperature": "K"}
        contract["metadata"] = copy.deepcopy(pool["metadata"])
    if case != "unbound_change":
        rebind(pool, contract)
    with pytest.raises(PartitionError) as error:
        construct_candidate(pool, contract, groups)
    assert error.value.code == code


def test_insufficient_support_has_no_fallback(finite_pool):
    pool, contract, groups = finite_pool
    # Every group has its own row and must be a training anchor.
    for h in pool["histories"]:
        h["stored_row"] = h["particle0"] // 2
    rebind(pool, contract)
    with pytest.raises(PartitionError, match="quota"):
        construct_candidate(pool, contract, groups)


def scientific_control(finite_pool):
    candidate = construct_candidate(*finite_pool)
    membership = {
        role: [r["record_id"] for r in candidate["records"] if r["role"] == role]
        for role in ("train", "validation", "test")
    }
    membership["exclusions"] = {}
    eligibility = {
        r["record_id"]: {
            "eligible": True,
            "qualification_sha256": sha("synthetic-qualified"),
        }
        for r in candidate["records"]
    }
    acceptance = {
        "human_decision": "synthetic accepted task/reference/domain/metrics/tolerances",
        "candidate_sha256": digest(candidate),
        "membership_sha256": digest(membership),
        "eligibility_sha256": digest(eligibility),
    }
    return candidate, membership, eligibility, acceptance


@pytest.mark.parametrize(
    "case,code",
    [
        ("zero", "empty_eligible"),
        ("unknown", "eligibility_unknown"),
        ("ineligible", "ineligible"),
        ("missing", "eligibility_unknown"),
        ("empty", "identity"),
        ("no_acceptance", "scientific_acceptance"),
        ("unknown_member", "scientific_membership"),
        ("incomplete", "scientific_membership"),
        ("no_evidence", "qualification"),
    ],
)
def test_scientific_gate_requires_actual_qualification_and_acceptance(
    finite_pool, case, code
):
    args = scientific_control(finite_pool)
    assert validate_scientific(*args)["status"] == "SCIENTIFIC_MEMBERSHIP_CHECK_PASS"
    candidate, membership, eligibility, acceptance = copy.deepcopy(args)
    if case == "zero":
        for evidence in eligibility.values():
            evidence["eligible"] = False
    elif case == "unknown":
        eligibility["r0"]["eligible"] = None
    elif case == "ineligible":
        eligibility["r0"]["eligible"] = False
    elif case == "missing":
        eligibility.pop("r0")
    elif case == "empty":
        membership["test"] = []
    elif case == "no_acceptance":
        acceptance = None
    elif case == "unknown_member":
        membership["test"].append("unknown")
    elif case == "incomplete":
        membership["train"].remove("r0")
    elif case == "no_evidence":
        eligibility["r0"].pop("qualification_sha256")
    with pytest.raises(PartitionError) as error:
        validate_scientific(candidate, membership, eligibility, acceptance)
    assert error.value.code == code


def test_fixed_fraction_quota_uses_total_category_groups(finite_pool):
    pool, contract, groups = finite_pool
    for p in range(16, 40):
        h = copy.deepcopy(pool["histories"][6])
        h.update(particle0=p, raw_ancestors=[sha(f"raw{p}")], known_related=[p ^ 1])
        r = copy.deepcopy(pool["records"][6])
        r.update(record_id=f"r{p}", particle0=p, input_sha256=sha(f"input{p}"))
        pool["histories"].append(h)
        pool["records"].append(r)
    groups = [[2 * i, 2 * i + 1] for i in range(20)]
    # Independent fixed hash oracle: first three nonanchors 15/6/10;
    # next three 19/12/18. q=floor(.15*20)=3, computed before removing anchors.
    contract["accepted_groups"] = [
        {
            "members": g,
            "role": "validation"
            if i in (15, 6, 10)
            else "test"
            if i in (19, 12, 18)
            else "train",
        }
        for i, g in enumerate(groups)
    ]
    contract["counts"].update(
        histories=40, ordinary_records=40, candidate_records=40, groups=20
    )
    rebind(pool, contract)
    result = construct_candidate(pool, contract, groups)
    assert [g["role"] for g in result["groups"]].count("validation") == 3
    assert [g["role"] for g in result["groups"]].count("test") == 3


def test_second_category_has_separate_support_and_quotas(finite_pool):
    pool, contract, groups = finite_pool
    # Category B's minimum hash is group 6, making it a training anchor.
    # Its remaining order is group 7 then group 4 then group 5.
    for h in pool["histories"]:
        if h["particle0"] >= 8:
            h["category"] = "synthetic-second-category"
    # Category A's nonanchor rank starts group 3 then group 2.
    expected = [
        "train",
        "train",
        "test",
        "validation",
        "test",
        "train",
        "train",
        "validation",
    ]
    contract["accepted_groups"] = [
        {"members": g, "role": r} for g, r in zip(groups, expected)
    ]
    rebind(pool, contract)
    result = construct_candidate(pool, contract, groups)
    assert [g["role"] for g in result["groups"]] == expected
    assert result["groups"][6]["training_anchor"]


def test_derived_cycle_is_not_valid_provenance(finite_pool):
    pool, contract, groups = finite_pool
    construct_candidate(pool, contract, groups)
    pool["records"][0]["derived_from"] = ["r1"]
    pool["records"][1]["derived_from"] = ["r0"]
    rebind(pool, contract)
    with pytest.raises(PartitionError, match="ancestry_cycle"):
        construct_candidate(pool, contract, groups)


@pytest.mark.parametrize(
    "case,code",
    [
        ("identity", "position_identity"),
        ("shape", "position_shape"),
        ("nan", "position_shape"),
        ("radius", "position_radius"),
    ],
)
def test_measured_position_negative_controls(case, code):
    particles = [0, 1]
    positions = np.ones((3, 2, 3))
    assert measured_components(particles, positions) == [[0, 1]]
    if case == "identity":
        particles = [0, 0]
    elif case == "shape":
        positions = positions[:, :, :2]
    elif case == "nan":
        positions[0, 0, 1] = np.nan
    elif case == "radius":
        positions[0, 0, 0] = 0
    with pytest.raises(PartitionError, match=code):
        measured_components(particles, positions)


def test_cli_bound_inputs_and_exclusive_output(
    finite_pool, tmp_path, monkeypatch, capsys
):
    from crucible.partitions import main

    pool, contract, _ = finite_pool

    def write_json(name, value):
        path = tmp_path / name
        path.write_text(json.dumps(value))
        return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    # Radius pairs separated by factors of ten produce the eight hand groups.
    spherical = np.zeros((2, 16, 3))
    spherical[:, :, 0] = [
        10.0 ** (p // 2) * (1.0001 if p % 2 else 1.0) for p in range(16)
    ]
    position_path = tmp_path / "positions.npz"
    np.savez(
        position_path,
        positions_r_theta_phi=spherical,
        trajectory_ids_row_zone_gpid0=np.array([[0, 0, p] for p in range(16)]),
        times_by_file=np.array([[[1.0, 0.0], [2.0, 1.0]]]),
    )
    config = {
        "pool": write_json("pool.json", pool),
        "contract": write_json("contract.json", contract),
        "positions": [
            {
                "path": "positions.npz",
                "sha256": hashlib.sha256(position_path.read_bytes()).hexdigest(),
            }
        ],
    }
    write_json("config.json", config)
    output = tmp_path / "candidate.json"
    monkeypatch.setattr(
        "sys.argv", ["partitions", str(tmp_path / "config.json"), str(output)]
    )
    main()
    assert json.loads(output.read_text())["counts"]["candidate_records"] == 16
    assert "PENDING_SCIENTIFIC" in capsys.readouterr().out
    with pytest.raises(FileExistsError):
        main()
    (tmp_path / "pool.json").write_text("{}")
    with pytest.raises(PartitionError, match="file_binding"):
        main()
