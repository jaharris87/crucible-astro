"""Literal public two-source streams: five unique states and two explicit repeats."""

import copy
import hashlib
import json
import struct

import h5py
import pytest

from crucible import primary_data as union


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def write(path, value):
    path.write_text(json.dumps(value, allow_nan=False) + "\n")


@pytest.fixture
def finite_union(tmp_path, monkeypatch):
    for key, value in {
        "PILOT": 3,
        "NEW": 2,
        "PILOT_HISTORIES": 1,
        "NEW_HISTORIES": 2,
        "PILOT_CONTROLS": (1, 3),
        "COUNTS": {
            "histories": 3,
            "ordinary_records": 6,
            "candidate_records": 5,
            "excluded_records": 1,
            "groups": 3,
        },
    }.items():
        monkeypatch.setattr(union, key, value)
    species = [[0, 1], [1, 1]] + [[1, a] for a in range(2, 160)]
    za = struct.pack("<320d", *[s[0] for s in species], *[s[1] for s in species])
    coefficients = struct.pack("<2048d", 4.0, *([0.0] * 2047))
    Y = struct.pack("<160d", 0.25, 0.75, -0.0, *([0.0] * 157))
    stored = struct.pack("<160d", -4.0, 5.0, -0.0, *([0.0] * 157))
    pilot_states = []
    pilot_results = []
    pilot_rows = []

    def record(seq, row, tracer, ordinal, factor):
        prefix = struct.pack(
            "<5i5d", seq, row, tracer, ordinal, 73, 0.5, 2.0, 1e6, 0.125, -0.0
        )
        F = struct.pack("<160d", -factor, factor, -0.0, *([0.0] * 157))
        state = prefix + Y + stored
        result = (
            prefix
            + struct.pack("<4di", 0.5, 2.0, 1e6, 0.75, 1)
            + Y
            + Y
            + stored
            + F
            + coefficients
        )
        locator = f"Run_slab_{row:03d}/Run/ts_{tracer:04d}"
        selection = {
            "sequence": seq,
            "record_id": f"{locator}#{ordinal}",
            "ordinal": ordinal,
            "raw_ts_sha256": sha((locator + "ts").encode()),
            "raw_ev_sha256": sha((locator + "ev").encode()),
            "raw_payload_sha256": sha((locator + str(ordinal)).encode()),
            "input_state_sha256": sha(prefix + Y),
        }
        return state, result, selection

    # Wire calls deliberately differ from numeric raw-ordinal ordering.
    for seq, ordinal in enumerate((20, 2, 10), 1):
        s, r, sel = record(seq, 30, 445, ordinal, 1.0)
        pilot_states.append(s)
        pilot_results.append(r)
        pilot_rows.append(sel)
    new_states = []
    new_results = []
    new_rows = []
    for seq, row, tracer, ordinal, factor in ((1, 31, 4, 2, 2.0), (2, 32, 17, 3, 3.0)):
        s, r, sel = record(seq, row, tracer, ordinal, factor)
        sel.update(role="new", trajectory_locator=sel["record_id"].split("#")[0])
        new_states.append(s)
        new_results.append(r)
        new_rows.append(sel)
    for seq, original in ((3, 1), (4, 3)):
        s = struct.pack("<i", seq) + pilot_states[original - 1][4:]
        r = struct.pack("<i", seq) + pilot_results[original - 1][4:]
        sel = {
            **pilot_rows[original - 1],
            "sequence": seq,
            "role": "repeat_control",
            "source_pilot_sequence": original,
            "input_state_sha256": sha(s[:1340]),
        }
        new_states.append(s)
        new_results.append(r)
        new_rows.append(sel)
    roles = (
        "build_manifest",
        "build_log",
        "build_exit",
        "build_driver",
        "build_runtime",
        "run_log",
        "job_script",
        "job_status",
        "loaded_maps",
        "job_hardware",
        "job_environment",
        "run_exit",
    )
    core = {
        f"refs/synthetic-{i}": {
            "path": f"/synthetic/reference-{i}",
            "sha256": sha(str(i).encode()),
        }
        for i in range(26)
    }
    configs = {}
    for name, states, results, rows, controls in [
        ("pilot", pilot_states, pilot_results, pilot_rows, [1, 3]),
        ("primary", new_states, new_results, new_rows, [3, 4]),
    ]:
        root = tmp_path / name
        root.mkdir()
        header = struct.pack("<4i", 0x43525543, 2, len(rows), 160) + za
        (root / "states").write_bytes(header + b"".join(states))
        (root / "fresh").write_bytes(header + b"".join(results))
        (root / "executable").write_bytes(
            ("different generating executable " + name).encode()
        )
        write(root / "selection", rows)
        components = []
        for k, (state, result) in enumerate(zip(states, results, strict=True), 1):
            components.append(
                {
                    "sequence": k,
                    "Y": list(struct.unpack("<160d", state[60:1340])),
                    "stored_dY": list(struct.unpack("<160d", state[1340:])),
                    "fresh_dY": list(struct.unpack("<160d", result[3936:5216])),
                    "composition_EOS_Ye": 0.75,
                    "state_bits_unchanged": True,
                    "training_eligibility": False,
                    "fresh_sha256": sha(result[3936:5216]),
                    "coefficients_sha256": sha(result[5216:]),
                    "conditional_assembly": {
                        "conditional_assembly_check": True,
                        "scientific_accuracy_acceptance": False,
                        "component_absolute_residual": [0.0] * 160,
                        "component_absolute_bound": [1e-12] * 160,
                        "fresh_baryon_absolute_residual": 0.0,
                        "baryon_absolute_bound": 1e-10,
                    },
                }
            )
        (root / "components").write_text(
            "".join(json.dumps(c) + "\n" for c in components)
        )
        prep = {
            "schema": "crucible.rhs-reference-preparation.v1"
            if name == "pilot"
            else "crucible.rhs-primary-preparation.v1",
            "selection_count": len(rows),
            "configuration": {
                "files": copy.deepcopy(core),
                "raw_root": "/synthetic/raw",
            },
            "files": {
                key: {"bytes": 1, "sha256": entry["sha256"]}
                for key, entry in core.items()
            },
        }
        if name == "primary":
            prep["batch"] = {
                "new_states": 2,
                "repeat_controls": 2,
                "proposed_calls": 4,
                "pilot_states_reused": 3,
                "pilot_states_not_repeated": 1,
                "unique_union_states": 5,
                "new_histories": 2,
                "pilot_histories": 1,
                "execution_authorized": False,
            }
        write(root / "preparation", prep)
        write(
            root / "comparison",
            {
                "status": "Completed comparisons only; scientific qualification remains false",
                "training_eligibility": False,
                "D017_exact_bit_controls": controls,
                "runtime_shared_libraries_sha256": {
                    f"/remote/{name}.so": sha(name.encode())
                },
                "reference_accuracy": "synthetic stream only",
            },
        )
        for role in roles:
            (root / role).write_bytes(
                b"0\n" if role in ("build_exit", "run_exit") else (name + role).encode()
            )
        write(
            root / "execution",
            {
                "schema": "crucible.rhs-pilot-execution.v1"
                if name == "pilot"
                else "crucible.rhs-primary-execution.v1",
                "status": "completed",
                "parents": {},
                "configuration_sha256": "",
                "runtime_shared_libraries_sha256": {
                    f"/remote/{name}.so": sha(name.encode())
                },
                "evidence": {
                    role: {
                        "path": str(root / role),
                        "sha256": sha((root / role).read_bytes()),
                    }
                    for role in roles
                },
            },
        )
        configs[name] = {
            "inputs": {
                key: {"path": str(root / key), "sha256": ""}
                for key in (
                    "preparation",
                    "states",
                    "selection",
                    "fresh",
                    "components",
                    "comparison",
                    "executable",
                    "execution",
                )
            },
            "expected": {
                "count": len(rows),
                "species_Z_A": copy.deepcopy(species),
                "exact_controls": controls,
                "units": {
                    "time": "s",
                    "T9": "GK",
                    "rho": "g/cm^3",
                    "internal_dt": "s",
                    "Y": "molar_abundance_Y",
                    "fresh_rhs": "molar_abundance_Y/s",
                    "stored_dY_unqualified": "molar_abundance_Y/s",
                    "stored_energy_unqualified": "erg/g/s",
                    "native_EOS_Ye": "dimensionless",
                },
            },
        }
    (tmp_path / "membership").mkdir()
    partition = {
        "schema_version": 1,
        "status": "CANDIDATE_MECHANICAL_PASS_PENDING_SCIENTIFIC_QUALIFICATION",
        "counts": dict(union.COUNTS),
        "metadata": {
            "parent_id": "synthetic-parent",
            "n_species": 160,
            "species": [{"id": f"Z{z}A{a}", "Z": z, "A": a} for z, a in species],
            "species_payload_sha256": sha(struct.pack("<i", 160) + za),
            "reference_config_sha256": "",
            "units": {
                "Y": "molar_abundance_Y",
                "temperature": "GK",
                "density": "g/cm^3",
                "time": "s",
            },
        },
        "groups": [],
        "histories": [],
        "records": [],
    }
    for group, particle, sel, role in (
        (0, 5, new_rows[0], "validation"),
        (1, 10, pilot_rows[0], "train"),
        (2, 20, new_rows[1], "test"),
    ):
        loc = sel["record_id"].split("#")[0]
        partition["groups"].append({"members": [particle], "role": role})
        partition["histories"].append(
            {
                "particle0": particle,
                "parent_id": "synthetic-parent",
                "role": role,
                "group": group,
                "trajectory_locator": loc,
                "stored_row": int(loc[9:12]),
                "raw_paths": [loc, loc.replace("/ts_", "/ev_")],
                "raw_ancestors": [sel["raw_ts_sha256"], sel["raw_ev_sha256"]],
                "known_related": [],
            }
        )
    for s, sel in zip(
        pilot_states + new_states[:2], pilot_rows + new_rows[:2], strict=True
    ):
        h = next(
            h
            for h in partition["histories"]
            if sel["record_id"].startswith(h["trajectory_locator"] + "#")
        )
        partition["records"].append(
            {
                "record_id": sel["record_id"],
                "particle0": h["particle0"],
                "ordinal": sel["ordinal"],
                "parent_id": "synthetic-parent",
                "role": h["role"],
                "group": h["group"],
                "candidate": True,
                "scientific_eligibility": False,
                "exclusion_reasons": [],
                "n_species": 160,
                "species_sha256": sha(encoded(partition["metadata"]["species"])),
                "raw_ancestors": [],
                "derived_from": [],
                "input_sha256": sha(
                    bytes.fromhex(partition["metadata"]["species_payload_sha256"])
                    + s[28:44]
                    + s[60:1340]
                ),
                "time": 0.5,
                "temperature": 2.0,
                "density": 1e6,
            }
        )
    excluded = {
        **partition["records"][-2],
        "record_id": new_rows[0]["trajectory_locator"] + "#3",
        "ordinal": 3,
        "candidate": False,
        "exclusion_reasons": ["synthetic outside grid"],
    }
    partition["records"].append(excluded)
    write(tmp_path / "membership" / "partition", partition)
    c = {
        "schema": "crucible.primary-native-rhs-union.v1",
        "dataset_id": "synthetic-two-source",
        "dataset_version": "0.1.0",
        "packets": configs,
        "working_partition": {
            "path": str(tmp_path / "membership" / "partition"),
            "sha256": "",
        },
    }
    recipe = tmp_path / "recipe.json"
    outdir = tmp_path / "derived"
    outdir.mkdir()

    def bind():
        for name in ("pilot", "primary"):
            root = tmp_path / name
            cfg = configs[name]
            p = json.loads((root / "preparation").read_text())
            if name == "primary":
                for field, key in [
                    ("pilot_bundle", "preparation"),
                    ("pilot_fresh", "fresh"),
                    ("pilot_comparison", "comparison"),
                    ("pilot_receipt", "execution"),
                ]:
                    p["configuration"][field] = dict(configs["pilot"]["inputs"][key])
            p["files"].update(
                {
                    filename: {
                        "bytes": (root / key).stat().st_size,
                        "sha256": sha((root / key).read_bytes()),
                    }
                    for key, filename in [
                        ("states", "states.bin"),
                        ("selection", "selection.json"),
                    ]
                }
            )
            write(root / "preparation", p)
            (root / "build_manifest").write_bytes((root / "preparation").read_bytes())
            comp = json.loads((root / "comparison").read_text())
            for field, key in [
                ("manifest_sha256", "preparation"),
                ("fresh_sha256", "fresh"),
                ("components_sha256", "components"),
                ("executable_sha256", "executable"),
            ]:
                comp[field] = sha((root / key).read_bytes())
            write(root / "comparison", comp)
            ex = json.loads((root / "execution").read_text())
            ex["parents"] = {
                key: sha((root / key).read_bytes())
                for key in (
                    "preparation",
                    "executable",
                    "fresh",
                    "components",
                    "comparison",
                )
            }
            ex["configuration_sha256"] = sha(encoded(p["configuration"]))
            ex["evidence"]["build_manifest"]["sha256"] = sha(
                (root / "build_manifest").read_bytes()
            )
            if name == "primary" and "batch" not in ex:
                ex["batch"] = {
                    "calls": 4,
                    "new_states": 2,
                    "repeat_controls": 2,
                    "new_histories": 2,
                    "call_histories": 3,
                    "repeat_control_sequences": [3, 4],
                    "selection_sha256": "",
                }
            if name == "primary":
                ex["batch"]["selection_sha256"] = sha((root / "selection").read_bytes())
            write(root / "execution", ex)
            for key in cfg["inputs"]:
                cfg["inputs"][key]["sha256"] = sha((root / key).read_bytes())
        part = json.loads((tmp_path / "membership" / "partition").read_text())
        part["metadata"]["reference_config_sha256"] = configs["pilot"]["inputs"][
            "preparation"
        ]["sha256"]
        write(tmp_path / "membership" / "partition", part)
        c["working_partition"]["sha256"] = sha(
            (tmp_path / "membership" / "partition").read_bytes()
        )
        write(recipe, c)

    bind()
    return recipe, outdir / "candidate", tmp_path, c, bind


def test_literal_two_source_union_bits_order_ancestry_and_masks(finite_union):
    recipe, out, root, c, _ = finite_union
    m = union.materialize(recipe, out)
    with h5py.File(out / "dataset.h5", "r") as h:
        assert h["sequence"][:].tolist() == [1, 2, 3, 4, 5]
        assert h["particle0"][:].tolist() == [5, 10, 10, 10, 20]
        assert h["raw_ordinal"][:].tolist() == [2, 2, 10, 20, 3]
        assert h["source/packet"].asstr()[:].tolist() == [
            "primary",
            "pilot",
            "pilot",
            "pilot",
            "primary",
        ]
        assert h["source/call_sequence"][:].tolist() == [1, 2, 3, 1, 2]
        assert h["raw_provenance/record_id"].asstr()[0] == "Run_slab_031/Run/ts_0004#2"
        assert h["fresh_rhs"][:, 0].tolist() == [-2.0, -1.0, -1.0, -1.0, -3.0]
        for j, (packet, k) in enumerate(
            [("primary", 0), ("pilot", 1), ("pilot", 2), ("pilot", 0), ("primary", 1)]
        ):
            s = (root / packet / "states").read_bytes()[
                2576 + k * 2620 : 2576 + (k + 1) * 2620
            ]
            r = (root / packet / "fresh").read_bytes()[
                2576 + k * 21600 : 2576 + (k + 1) * 21600
            ]
            for name, expected in [
                ("Y", s[60:1340]),
                ("stored_dY_unqualified", s[1340:]),
                ("fresh_rhs", r[3936:5216]),
            ]:
                assert h[name][j].astype("<f8").tobytes() == expected
            for name, offset in [
                ("time", 20),
                ("T9", 28),
                ("rho", 36),
                ("internal_dt", 44),
                ("stored_energy_unqualified", 52),
            ]:
                assert h[name][j].tobytes() == s[offset : offset + 8]
            assert h["native_EOS_Ye"][j].tobytes() == r[84:92]
            assert (
                h["source/execution_sha256"].asstr()[j]
                == c["packets"][packet]["inputs"]["execution"]["sha256"]
            )
        assert h["Y"][0, 2].tobytes() == bytes.fromhex("0000000000000080")
        assert h["Y"].shape == h["fresh_rhs"].shape == (5, 160)
        assert all(
            not h["eligibility/" + key][:].any()
            for key in (
                "state_training",
                "rhs_training",
                "energy_training",
                "rollout_reference",
            )
        )
        assert not {"split", "role", "group", "coefficients"} & set(h)
    assert m["count"] == 5 and m["working_membership_proof"][
        "candidate_role_counts"
    ] == {"validation": 1, "train": 3, "test": 1}
    assert (
        m["new_label_provenance"]["pilot"]["executable"]
        != m["new_label_provenance"]["primary"]["executable"]
    )
    assert m["output"]["sha256"] == sha((out / "dataset.h5").read_bytes())


def mutate_json(path, change):
    value = json.loads(path.read_text())
    change(value)
    write(path, value)


def change_call(root, packet, index, state=None, result=None, selection=None):
    """Independent fixture editing, retaining coherent per-packet JSON/echo hashes."""
    folder = root / packet
    sb = bytearray((folder / "states").read_bytes())
    rb = bytearray((folder / "fresh").read_bytes())
    rows = json.loads((folder / "selection").read_text())
    if state is not None:
        sb[2576 + index * 2620 : 2576 + (index + 1) * 2620] = state
    if result is not None:
        rb[2576 + index * 21600 : 2576 + (index + 1) * 21600] = result
    if selection is not None:
        rows[index] = selection
    s = bytes(sb[2576 + index * 2620 : 2576 + (index + 1) * 2620])
    r = bytes(rb[2576 + index * 21600 : 2576 + (index + 1) * 21600])
    rows[index]["input_state_sha256"] = sha(s[:1340])
    comp = [
        json.loads(line) for line in (folder / "components").read_text().splitlines()
    ]
    comp[index].update(
        Y=list(struct.unpack("<160d", s[60:1340])),
        stored_dY=list(struct.unpack("<160d", s[1340:])),
        fresh_dY=list(struct.unpack("<160d", r[3936:5216])),
        composition_EOS_Ye=struct.unpack_from("<d", r, 84)[0],
        fresh_sha256=sha(r[3936:5216]),
        coefficients_sha256=sha(r[5216:]),
    )
    (folder / "states").write_bytes(sb)
    (folder / "fresh").write_bytes(rb)
    write(folder / "selection", rows)
    (folder / "components").write_text("".join(json.dumps(c) + "\n" for c in comp))


def test_input_enumeration_does_not_choose_canonical_order(finite_union):
    recipe, out, root, c, bind = finite_union
    union.materialize(recipe, out)
    mutate_json(
        root / "membership/partition",
        lambda p: (p["records"].reverse(), p["histories"].reverse()),
    )
    c["packets"] = dict(reversed(list(c["packets"].items())))
    bind()
    second = out.with_name("reordered")
    union.materialize(recipe, second)
    with (
        h5py.File(out / "dataset.h5", "r") as a,
        h5py.File(second / "dataset.h5", "r") as b,
    ):
        for key in (
            "sequence",
            "particle0",
            "raw_ordinal",
            "Y",
            "fresh_rhs",
            "stored_dY_unqualified",
            "time",
            "T9",
            "rho",
            "native_EOS_Ye",
        ):
            assert a[key][:].tobytes() == b[key][:].tobytes()
        assert (
            a["raw_provenance/record_id"].asstr()[:].tolist()
            == b["raw_provenance/record_id"].asstr()[:].tolist()
        )
        assert (
            a["source/packet"].asstr()[:].tolist()
            == b["source/packet"].asstr()[:].tolist()
        )


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("new-role", "primary selection role"),
        ("control-role", "primary selection role"),
        ("wrong-pilot", "repeat control identity/pilot sequence"),
        ("missing-control", "selection count"),
        ("extra-control", "selection count"),
        ("repeat-raw", "repeat control raw ancestry"),
        ("repeat-state", "repeat control full-state/condition bits"),
        ("repeat-F", "repeat control native Ye/fresh RHS bits"),
        ("repeat-Ye", "repeat control native Ye/fresh RHS bits"),
        ("overlap", "unexpected new/pilot overlap"),
        ("duplicate-controls", "raw record identity"),
    ],
)
def test_only_the_two_declared_exact_repeats_are_omitted(finite_union, defect, reason):
    recipe, out, root, _, bind = finite_union
    if defect in (
        "new-role",
        "control-role",
        "wrong-pilot",
        "missing-control",
        "extra-control",
        "repeat-raw",
    ):

        def change(rows):
            if defect == "new-role":
                rows[0]["role"] = "repeat_control"
            elif defect == "control-role":
                rows[2]["role"] = "new"
            elif defect == "wrong-pilot":
                rows[3]["source_pilot_sequence"] = 2
            elif defect == "missing-control":
                rows.pop()
            elif defect == "extra-control":
                rows.append(copy.deepcopy(rows[-1]))
            else:
                rows[2]["raw_payload_sha256"] = "f" * 64

        mutate_json(root / "primary/selection", change)
    elif defect in ("repeat-state", "repeat-F", "repeat-Ye"):
        s = bytearray(
            (root / "primary/states").read_bytes()[2576 + 2 * 2620 : 2576 + 3 * 2620]
        )
        r = bytearray(
            (root / "primary/fresh").read_bytes()[2576 + 2 * 21600 : 2576 + 3 * 21600]
        )
        if defect == "repeat-state":
            struct.pack_into("<d", s, 52, 1.0)
            r[:60] = s[:60]
        elif defect == "repeat-F":
            struct.pack_into("<d", r, 3952, 0.0)  # sign-only zero mismatch
        else:
            struct.pack_into("<d", r, 84, 0.5)
        change_call(root, "primary", 2, s, r)
    else:
        oldindex = 1 if defect == "overlap" else 0
        newindex = 0 if defect == "overlap" else 3
        s = (root / "pilot/states").read_bytes()[
            2576 + oldindex * 2620 : 2576 + (oldindex + 1) * 2620
        ]
        r = (root / "pilot/fresh").read_bytes()[
            2576 + oldindex * 21600 : 2576 + (oldindex + 1) * 21600
        ]
        sel = json.loads((root / "pilot/selection").read_text())[oldindex]
        sel["sequence"] = newindex + 1
        if defect == "overlap":
            sel.update(role="new", trajectory_locator=sel["record_id"].split("#")[0])
        else:
            sel.update(role="repeat_control", source_pilot_sequence=1)
        change_call(
            root,
            "primary",
            newindex,
            struct.pack("<i", newindex + 1) + s[4:],
            struct.pack("<i", newindex + 1) + r[4:],
            sel,
        )
    bind()
    with pytest.raises(ValueError, match=reason):
        union.materialize(recipe, out)
    assert not out.exists()


@pytest.mark.parametrize("packet", ["pilot", "primary"])
@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("status", "running", "comparison incomplete/failed"),
        (
            "runtime_shared_libraries_sha256",
            True,
            "runtime library provenance requires",
        ),
        (
            "runtime_shared_libraries_sha256",
            "placeholder",
            "runtime library provenance requires",
        ),
        (
            "runtime_shared_libraries_sha256",
            {"relative.so": "a" * 64},
            "runtime library provenance requires",
        ),
        (
            "runtime_shared_libraries_sha256",
            {"/remote/lib.so": "invalid"},
            "runtime library provenance requires",
        ),
    ],
)
def test_each_comparison_is_complete_and_library_bound(
    finite_union, packet, field, value, reason
):
    recipe, out, root, _, bind = finite_union
    mutate_json(
        root / packet / "comparison", lambda report: report.update({field: value})
    )
    bind()
    with pytest.raises(ValueError, match=reason):
        union.materialize(recipe, out)
    assert not out.exists()


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("primary-schema", "execution receipt incomplete/schema"),
        ("primary-count", "primary execution batch"),
        ("pilot-extra-batch", "execution receipt incomplete/schema"),
        ("primary-extra-key", "execution receipt incomplete/schema"),
        ("build-evidence", "execution evidence build_log"),
        ("run-exit", "execution run_exit not successful"),
        ("units", "unit contract mismatch"),
        ("core", "pinned core reference/configuration mismatch"),
        ("core-manifest", "core reference asset/manifest ancestry"),
        ("primary-prep", "preparation identity/count"),
        ("species", "packet species/order mismatch"),
        ("truncation", "truncated/trailing fresh"),
        ("nonfinite", "nonfinite binary64"),
    ],
)
def test_primary_packet_and_two_source_contracts(finite_union, defect, reason):
    recipe, out, root, c, bind = finite_union
    if defect in (
        "primary-schema",
        "primary-count",
        "pilot-extra-batch",
        "primary-extra-key",
    ):
        packet = "pilot" if defect == "pilot-extra-batch" else "primary"

        def edit(ex):
            if defect == "primary-schema":
                ex["schema"] = "unknown"
            elif defect == "primary-count":
                ex["batch"]["new_histories"] = 3
            elif defect == "pilot-extra-batch":
                ex["batch"] = {}
            else:
                ex["extra"] = "unknown"

        mutate_json(root / packet / "execution", edit)
    elif defect == "build-evidence":
        (root / "primary/build_log").write_bytes(b"changed retained build record")
    elif defect == "run-exit":
        (root / "primary/run_exit").write_bytes(b"1\n")
        mutate_json(
            root / "primary/execution",
            lambda ex: ex["evidence"]["run_exit"].update(sha256=sha(b"1\n")),
        )
    elif defect == "units":
        c["packets"]["primary"]["expected"]["units"]["T9"] = "K"
    elif defect == "core":
        mutate_json(
            root / "primary/preparation",
            lambda p: p["configuration"]["files"]["refs/synthetic-0"].update(
                sha256="e" * 64
            ),
        )
    elif defect == "core-manifest":
        mutate_json(
            root / "primary/preparation",
            lambda p: p["files"]["refs/synthetic-0"].update(sha256="e" * 64),
        )
    elif defect == "primary-prep":
        mutate_json(root / "primary/preparation", lambda p: p.update(schema="unknown"))
    elif defect == "species":
        for key in ("states", "fresh"):
            b = bytearray((root / "primary" / key).read_bytes())
            b[16:24], b[24:32] = b[24:32], b[16:24]
            b[1296:1304], b[1304:1312] = b[1304:1312], b[1296:1304]
            (root / "primary" / key).write_bytes(b)
        expected = c["packets"]["primary"]["expected"]["species_Z_A"]
        expected[:2] = expected[1::-1]
    elif defect == "truncation":
        path = root / "primary/fresh"
        path.write_bytes(path.read_bytes()[:-1])
    else:
        b = bytearray((root / "primary/fresh").read_bytes())
        struct.pack_into("<d", b, 2576 + 3936, float("nan"))
        (root / "primary/fresh").write_bytes(b)
    bind()
    with pytest.raises(ValueError, match=reason):
        union.materialize(recipe, out)
    assert not out.exists()


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("candidate-set", "exact working candidate membership"),
        ("fingerprint", "working full-state input fingerprint"),
        ("time", "working state condition bits"),
        ("history-raw", "working selected raw ancestry"),
        ("record-role", "working record identity/role"),
        ("group-role", "working history/group role"),
        ("known-relative", "working related ancestry"),
        ("derived", "working derived ancestry"),
        ("cycle", "working derived ancestry cycle"),
        ("eligibility", "working exclusion/eligibility"),
        ("species", "working record species"),
        ("duplicate", "working record identities/count"),
    ],
)
def test_exact_working_membership_and_ancestry(finite_union, defect, reason):
    recipe, out, root, _, bind = finite_union

    def edit(p):
        r = p["records"][0]
        if defect == "candidate-set":
            r.update(candidate=False, exclusion_reasons=["synthetic exclusion"])
            p["records"][-1].update(candidate=True, exclusion_reasons=[])
        elif defect == "fingerprint":
            r["input_sha256"] = "f" * 64
        elif defect == "time":
            r["time"] = 0.75
        elif defect == "history-raw":
            p["histories"][1]["raw_ancestors"][0] = "f" * 64
        elif defect == "record-role":
            r["role"] = "test"
        elif defect == "group-role":
            p["groups"][0]["role"] = "train"
        elif defect == "known-relative":
            p["histories"][0]["known_related"] = [10]
        elif defect == "derived":
            r["derived_from"] = ["missing-original-record"]
        elif defect == "cycle":
            r["derived_from"] = [r["record_id"]]
        elif defect == "eligibility":
            r["scientific_eligibility"] = True
        elif defect == "species":
            r["species_sha256"] = "e" * 64
        else:
            p["records"].append(copy.deepcopy(r))

    mutate_json(root / "membership/partition", edit)
    bind()
    with pytest.raises(ValueError, match=reason):
        union.materialize(recipe, out)
    assert not out.exists()


def test_output_and_input_guards_before_hdf(finite_union):
    recipe, out, root, c, bind = finite_union
    with pytest.raises(ValueError, match="collides"):
        union.materialize(recipe, root / "primary/new")
    out.symlink_to(out.parent / "missing")
    with pytest.raises(ValueError, match="symlink"):
        union.materialize(recipe, out)
    out.unlink()
    c["packets"]["third"] = copy.deepcopy(c["packets"]["pilot"])
    bind()
    with pytest.raises(ValueError, match="exact two packet"):
        union.materialize(recipe, out)
    del c["packets"]["third"]
    bind()
    union.materialize(recipe, out)
    with pytest.raises(ValueError, match="already exists"):
        union.materialize(recipe, out)


@pytest.mark.parametrize(
    "key,value", [("calls", 4.0), ("repeat_control_sequences", [3.0, 4.0])]
)
def test_primary_batch_types_are_not_numeric_equivalence(finite_union, key, value):
    recipe, out, root, _, bind = finite_union
    mutate_json(root / "primary/execution", lambda ex: ex["batch"].update({key: value}))
    bind()
    with pytest.raises(ValueError, match="primary execution batch"):
        union.materialize(recipe, out)
    assert not out.exists()


def test_all_declared_inputs_are_rechecked_before_union_output(
    finite_union, monkeypatch
):
    recipe, out, root, _, _ = finite_union
    original = union._membership

    def late_change(*args):
        result = original(*args)
        (root / "primary/job_status").write_bytes(b"changed after packet validation")
        return result

    monkeypatch.setattr(union, "_membership", late_change)
    with pytest.raises(ValueError, match="input checksum mismatch: job_status"):
        union.materialize(recipe, out)
    assert not out.exists()
