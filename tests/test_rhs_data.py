"""Public literal wire/field oracles; no physical producer or private data."""

import hashlib
import json
import struct

import h5py
import pytest

from crucible.rhs_data import materialize


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False) + "\n")


@pytest.fixture
def pilot(tmp_path):
    parent = tmp_path / "immutable"
    parent.mkdir()
    # Synthetic ordered identities; 160 is the fixed wire dimension, no nuclear claim.
    species = [[0, 1], [1, 1]] + [[1, a] for a in range(2, 160)]
    header = struct.pack("<4i", 0x43525543, 2, 2, 160)
    header += struct.pack("<320d", *[s[0] for s in species], *[s[1] for s in species])
    states, results, selection, components = [], [], [], []
    for seq in (1, 2):
        # Hand chosen distinct fields catch shifts/swaps; signed zero must survive.
        prefix = struct.pack(
            "<5i5d", seq, 30, 1099, seq + 10, 73, 0.5, 2.0, 1e6, 0.125, -0.0
        )
        y_values = [0.25, 0.75, -0.0] + [0.0] * 157
        stored_values = [-4.0, 5.0, -0.0] + [0.0] * 157
        new_values = [-1.0, 1.0, -0.0] + [0.0] * 157
        y = struct.pack("<160d", *y_values)
        stored = struct.pack("<160d", *stored_values)
        new = struct.pack("<160d", *new_values)
        coefficient = struct.pack("<2048d", *([4.0] + [0.0] * 2047))
        states.append(prefix + y + stored)
        results.append(
            prefix
            + struct.pack("<4di", 0.5, 2.0, 1e6, 0.75, 1)
            + y
            + y
            + stored
            + new
            + coefficient
        )
        selection.append(
            {
                "sequence": seq,
                "record_id": f"Run_slab_030/Run/ts_1099#{seq + 10}",
                "ordinal": seq + 10,
                "raw_ts_sha256": "a" * 64,
                "raw_ev_sha256": "b" * 64,
                "raw_payload_sha256": "c" * 64,
                "input_state_sha256": sha(prefix + y),
            }
        )
        components.append(
            {
                "sequence": seq,
                "Y": y_values,
                "stored_dY": stored_values,
                "fresh_dY": new_values,
                "composition_EOS_Ye": 0.75,
                "fresh_sha256": sha(new),
                "coefficients_sha256": sha(coefficient),
                "state_bits_unchanged": True,
                "training_eligibility": False,
                "conditional_assembly": {
                    "conditional_assembly_check": True,
                    "scientific_accuracy_acceptance": False,
                    "component_absolute_residual": [0.0] * 160,
                    "component_absolute_bound": [1e-14] * 160,
                    "fresh_baryon_absolute_residual": 0.0,
                    "baryon_absolute_bound": 1e-12,
                },
            }
        )
    (parent / "states").write_bytes(header + b"".join(states))
    (parent / "fresh").write_bytes(header + b"".join(results))
    (parent / "executable").write_bytes(
        b"synthetic executable identity; never executable"
    )
    write_json(parent / "selection", selection)
    (parent / "components").write_text(
        "".join(json.dumps(r) + "\n" for r in components)
    )
    prep = {
        "schema": "crucible.rhs-reference-preparation.v1",
        "selection_count": 2,
        "files": {},
        "configuration": {"source": "public synthetic source/configuration sentinel"},
    }
    write_json(parent / "preparation", prep)
    comparison = {
        "status": "Completed comparisons only; scientific qualification remains false",
        "training_eligibility": False,
        "D017_exact_bit_controls": [1, 2],
        "runtime_shared_libraries_sha256": {"/synthetic/lib-reference.so": "d" * 64},
        "reference_accuracy": "synthetic stream only; no scientific truth",
    }
    write_json(parent / "comparison", comparison)
    evidence_roles = (
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
    for role in evidence_roles:
        (parent / role).write_bytes(
            b"0\n"
            if role in ("build_exit", "run_exit")
            else ("synthetic retained " + role).encode()
        )
    write_json(parent / "execution", {})
    config = {
        "schema": "crucible.native-rhs-materialization.v1",
        "dataset_id": "public-synthetic-native-rhs",
        "dataset_version": "0.1.0",
        "inputs": {
            name: {
                "path": str(parent / name),
                "sha256": sha((parent / name).read_bytes()),
            }
            for name in (
                "preparation",
                "states",
                "fresh",
                "selection",
                "components",
                "comparison",
                "executable",
                "execution",
            )
        },
        "expected": {
            "count": 2,
            "species_Z_A": species,
            "exact_controls": [1, 2],
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
    config_path = tmp_path / "recipe.json"
    output_parent = tmp_path / "derived"
    output_parent.mkdir()

    def bind():
        # Mutations get coherent cryptographic closure so intended semantic checks run.
        p = json.loads((parent / "preparation").read_text())
        p["files"] = {
            filename: {
                "bytes": (parent / key).stat().st_size,
                "sha256": sha((parent / key).read_bytes()),
            }
            for key, filename in (
                ("states", "states.bin"),
                ("selection", "selection.json"),
            )
        }
        write_json(parent / "preparation", p)
        r = json.loads((parent / "comparison").read_text())
        for field, key in (
            ("manifest_sha256", "preparation"),
            ("fresh_sha256", "fresh"),
            ("components_sha256", "components"),
            ("executable_sha256", "executable"),
        ):
            r[field] = sha((parent / key).read_bytes())
        write_json(parent / "comparison", r)
        (parent / "build_manifest").write_bytes((parent / "preparation").read_bytes())
        receipt = {
            "schema": "crucible.rhs-pilot-execution.v1",
            "status": "completed",
            "parents": {
                key: sha((parent / key).read_bytes())
                for key in (
                    "preparation",
                    "executable",
                    "fresh",
                    "components",
                    "comparison",
                )
            },
            "configuration_sha256": sha(
                json.dumps(
                    p["configuration"],
                    sort_keys=True,
                    separators=(",", ":"),
                    allow_nan=False,
                ).encode()
            ),
            "runtime_shared_libraries_sha256": r["runtime_shared_libraries_sha256"],
            "evidence": {
                role: {
                    "path": str(parent / role),
                    "sha256": sha((parent / role).read_bytes()),
                }
                for role in evidence_roles
            },
        }
        write_json(parent / "execution", receipt)
        for key in config["inputs"]:
            config["inputs"][key]["sha256"] = sha((parent / key).read_bytes())
        write_json(config_path, config)

    bind()
    return config_path, output_parent / "candidate", parent, config, bind


def test_literal_fields_dimensions_bits_and_ancestry(pilot):
    config, output, parent, _, _ = pilot
    receipt = json.loads((parent / "execution").read_text())
    assert (
        receipt["configuration_sha256"]
        == "2082ef34a2cbb490c4eb3162f834eaeed4a9f60ecff2496680748c7b539f2458"
    )
    manifest = materialize(config, output)
    with h5py.File(output / "dataset.h5", "r") as h:
        assert h["Y"].shape == h["fresh_rhs"].shape == (2, 160)
        assert h["species_Z_A"][:3].tolist() == [[0, 1], [1, 1], [1, 2]]
        assert h["Y"][0, :3].tolist() == [0.25, 0.75, -0.0]
        assert h["fresh_rhs"][1, :3].tolist() == [-1.0, 1.0, -0.0]
        assert h["stored_dY_unqualified"][0, :2].tolist() == [-4.0, 5.0]
        for key, expected in (
            ("time", 0.5),
            ("T9", 2.0),
            ("rho", 1e6),
            ("internal_dt", 0.125),
            ("native_EOS_Ye", 0.75),
            ("row_id", 30),
            ("tracer_id", 1099),
            ("raw_ordinal", 11),
            ("step", 73),
        ):
            assert h[key][0] == expected
        assert h["fresh_rhs"].attrs["units"] == "molar_abundance_Y/s"
        assert h["raw_provenance/record_id"].asstr()[1] == "Run_slab_030/Run/ts_1099#12"
        # Byte oracles independently locate the source fields, including negative zero.
        raw = (parent / "states").read_bytes()
        result = (parent / "fresh").read_bytes()
        for name, expected in (
            ("Y", raw[2636:3916]),
            ("stored_dY_unqualified", raw[3916:5196]),
            ("fresh_rhs", result[6512:7792]),
        ):
            assert h[name][0].astype("<f8").tobytes() == expected
            assert h[name][0].astype("<f8").tobytes()[16:24] == bytes.fromhex(
                "0000000000000080"
            )
        assert h["stored_energy_unqualified"][0].tobytes() == bytes.fromhex(
            "0000000000000080"
        )
        reasons = set()
        for use in (
            "state_training",
            "rhs_training",
            "energy_training",
            "rollout_reference",
        ):
            assert h["eligibility/" + use][:].tolist() == [False, False]
            reasons.add(h["eligibility/" + use].attrs["reason"])
        assert len(reasons) == 4
        assert "coefficients" not in h and "split" not in h
    assert manifest["new_label_provenance"]["execution"]["sha256"] == sha(
        (parent / "execution").read_bytes()
    )
    assert manifest["recipe"]["inputs"]["execution"]["path"] == str(
        parent / "execution"
    )
    assert manifest["output"]["sha256"] == sha((output / "dataset.h5").read_bytes())
    assert manifest["original_state_provenance"]["selection_parent"]["sha256"] == sha(
        (parent / "selection").read_bytes()
    )
    assert manifest["new_label_provenance"]["comparison"]["sha256"] == sha(
        (parent / "comparison").read_bytes()
    )
    assert json.loads((output / "manifest.json").read_text()) == manifest


@pytest.mark.parametrize(
    "key,mutation,reason",
    [
        ("states", lambda b: b[:-1], "truncated/trailing states"),
        ("fresh", lambda b: b + b"x", "truncated/trailing fresh"),
        ("fresh", lambda b: b[:2576] + struct.pack("<i", 9) + b[2580:], "scalar echo"),
        (
            "fresh",
            lambda b: b[:2668] + struct.pack("<i", 0) + b[2672:],
            "native Ye/weak",
        ),
        (
            "fresh",
            lambda b: b[:6512] + struct.pack("<d", float("nan")) + b[6520:],
            "nonfinite binary64",
        ),
        ("fresh", lambda b: b[:2672] + struct.pack("<d", 0.5) + b[2680:], "array echo"),
    ],
)
def test_binary_failures_with_valid_parent_closure(pilot, key, mutation, reason):
    config, output, parent, _, bind = pilot
    p = parent / key
    p.write_bytes(mutation(p.read_bytes()))
    bind()
    with pytest.raises(ValueError, match=reason):
        materialize(config, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("order", "ordered species mismatch"),
        ("units", "unit contract"),
        ("count", "preparation identity/count"),
        ("duplicate-species", "invalid ordered species"),
        ("comparison", "comparison incomplete/failed"),
        ("controls", "exact controls mismatch"),
        ("component-count", "incomplete/trailing components"),
        ("component-order", "component identity"),
        ("signed-zero", "fresh_dY JSON/binary bits"),
        ("dimension", "Y dimension"),
        ("bound", "failed/nonfinite verification bound"),
        ("flag", "failed conditional verification"),
        ("record", "raw record identity"),
        ("ordinal", "selection sequence/ordinal"),
        ("input-state", "input state ancestry"),
        ("raw-hash", "raw ancestry hashes"),
    ],
)
def test_semantic_failures_are_not_checksum_failures(pilot, defect, reason):
    config_path, output, parent, c, bind = pilot
    rows = [
        json.loads(line) for line in (parent / "components").read_text().splitlines()
    ]
    selection = json.loads((parent / "selection").read_text())
    if defect == "order":
        c["expected"]["species_Z_A"][:2] = c["expected"]["species_Z_A"][1::-1]
    elif defect == "units":
        c["expected"]["units"]["T9"] = "K"
    elif defect == "count":
        c["expected"]["count"] = 3
    elif defect == "duplicate-species":
        c["expected"]["species_Z_A"][1] = [0, 1]
    elif defect in ("comparison", "controls"):
        report = json.loads((parent / "comparison").read_text())
        report["status" if defect == "comparison" else "D017_exact_bit_controls"] = (
            "running" if defect == "comparison" else [2, 1]
        )
        write_json(parent / "comparison", report)
    elif defect == "component-count":
        rows.pop()
    elif defect == "component-order":
        rows.reverse()
    elif defect == "signed-zero":
        rows[0]["fresh_dY"][2] = 0.0
    elif defect == "dimension":
        rows[0]["Y"].pop()
    elif defect == "bound":
        rows[0]["conditional_assembly"]["component_absolute_residual"][0] = 1.0
    elif defect == "flag":
        rows[0]["conditional_assembly"]["conditional_assembly_check"] = False
    elif defect == "record":
        selection[0]["record_id"] = "Run_slab_031/Run/ts_1099#11"
    elif defect == "ordinal":
        selection[0]["ordinal"] = 12
    elif defect == "input-state":
        selection[0]["input_state_sha256"] = "f" * 64
    elif defect == "raw-hash":
        selection[0]["raw_payload_sha256"] = "missing"
    (parent / "components").write_text("".join(json.dumps(r) + "\n" for r in rows))
    write_json(parent / "selection", selection)
    bind()
    with pytest.raises(ValueError, match=reason):
        materialize(config_path, output)
    assert not output.exists()


def test_hash_and_comparison_ancestry_controls(pilot):
    config, output, parent, c, bind = pilot
    original = (parent / "fresh").read_bytes()
    (parent / "fresh").write_bytes(original + b"x")
    with pytest.raises(ValueError, match="input checksum mismatch"):
        materialize(config, output)
    (parent / "fresh").write_bytes(original)
    bind()
    comparison = json.loads((parent / "comparison").read_text())
    comparison["manifest_sha256"] = "f" * 64
    write_json(parent / "comparison", comparison)
    c["inputs"]["comparison"]["sha256"] = sha((parent / "comparison").read_bytes())
    write_json(config, c)
    with pytest.raises(ValueError, match="comparison ancestry: preparation"):
        materialize(config, output)
    bind()
    assert materialize(config, output)["count"] == 2


def test_output_collision_symlink_and_existing_refused(pilot):
    config, output, parent, _, _ = pilot
    for dest in (parent / "new", parent / "fresh"):
        with pytest.raises(ValueError, match="collides|already exists"):
            materialize(config, dest)
    output.symlink_to(output.parent / "missing")
    with pytest.raises(ValueError, match="symlink"):
        materialize(config, output)
    output.unlink()
    materialize(config, output)
    with pytest.raises(ValueError, match="already exists"):
        materialize(config, output)


def test_duplicate_json_and_nonfinite_json_refused(pilot):
    config, output, parent, _, bind = pilot
    original = (parent / "components").read_text()
    (parent / "components").write_text(
        original.replace('"sequence": 1', '"sequence": 1, "sequence": 1', 1)
    )
    bind()
    with pytest.raises(ValueError, match="duplicate JSON key"):
        materialize(config, output)
    (parent / "components").write_text(
        original.replace('"composition_EOS_Ye": 0.75', '"composition_EOS_Ye": NaN', 1)
    )
    bind()
    with pytest.raises(ValueError, match="nonfinite JSON"):
        materialize(config, output)


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("selection-fields", "selection fields"),
        ("inconsistent-parent", "inconsistent raw ancestry"),
        ("component-hash", "component payload identity"),
        ("positive-eligibility", "component identity/verification"),
        ("verification-dimension", "verification dimension"),
        ("json-overflow", "nonfinite JSON number"),
    ],
)
def test_additional_closure_failures(pilot, defect, reason):
    config, output, parent, _, bind = pilot
    selection = json.loads((parent / "selection").read_text())
    rows = [
        json.loads(line) for line in (parent / "components").read_text().splitlines()
    ]
    if defect == "selection-fields":
        selection[1]["extra"] = "unexpected"
    elif defect == "inconsistent-parent":
        selection[1]["raw_ts_sha256"] = "e" * 64
    elif defect == "component-hash":
        rows[0]["fresh_sha256"] = "f" * 64
    elif defect == "positive-eligibility":
        rows[0]["training_eligibility"] = True
    elif defect == "verification-dimension":
        rows[0]["conditional_assembly"]["component_absolute_bound"].pop()
    write_json(parent / "selection", selection)
    text = "".join(json.dumps(r) + "\n" for r in rows)
    if defect == "json-overflow":
        text = text.replace(
            '"composition_EOS_Ye": 0.75', '"composition_EOS_Ye": 1e9999', 1
        )
    (parent / "components").write_text(text)
    bind()
    with pytest.raises(ValueError, match=reason):
        materialize(config, output)
    assert not output.exists()


def test_relative_and_input_symlink_refused(pilot):
    config, output, parent, c, bind = pilot
    with pytest.raises(ValueError, match="absolute paths"):
        materialize("relative.json", output)
    alias = parent / "alias"
    alias.symlink_to(parent / "fresh")
    c["inputs"]["fresh"]["path"] = str(alias)
    bind()
    with pytest.raises(ValueError, match="symlink"):
        materialize(config, output)


def rewrite_execution(pilot, receipt):
    """Bind changed receipt bytes and any comparison change, without blessing evidence."""
    config_path, _, parent, c, _ = pilot
    write_json(parent / "execution", receipt)
    for key in ("execution", "comparison"):
        if key in c["inputs"]:
            c["inputs"][key]["sha256"] = sha((parent / key).read_bytes())
    write_json(config_path, c)


@pytest.mark.parametrize(
    "key", ["preparation", "executable", "fresh", "components", "comparison"]
)
def test_execution_parent_mismatch_after_hash_rebinding(pilot, key):
    config, output, parent, _, _ = pilot
    receipt = json.loads((parent / "execution").read_text())
    receipt["parents"][key] = "f" * 64
    rewrite_execution(pilot, receipt)
    with pytest.raises(ValueError, match=f"execution ancestry: {key}"):
        materialize(config, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "defect,reason",
    [
        ("omitted", "exact audit input closure"),
        ("incomplete", "execution receipt incomplete/schema"),
        ("parent-closure", "execution parent closure"),
        ("configuration", "execution configuration ancestry"),
        ("evidence-closure", "execution evidence closure"),
        ("build-manifest", "execution build manifest ancestry"),
        ("build-exit", "execution build_exit not successful"),
        ("run-exit", "execution run_exit not successful"),
        ("path-collision", "execution evidence path collision"),
        ("relative-path", "execution evidence run_log: absolute paths"),
        ("symlink", "execution evidence run_log: symlink"),
        ("parent-traversal", "execution evidence run_log: parent traversal"),
    ],
)
def test_execution_receipt_failures_reach_intended_gate(pilot, defect, reason):
    config, output, parent, c, _ = pilot
    receipt = json.loads((parent / "execution").read_text())
    if defect == "omitted":
        del c["inputs"]["execution"]
    elif defect == "incomplete":
        del receipt["status"]
    elif defect == "parent-closure":
        del receipt["parents"]["comparison"]
    elif defect == "configuration":
        receipt["configuration_sha256"] = "e" * 64
    elif defect == "evidence-closure":
        del receipt["evidence"]["job_hardware"]
    elif defect in ("build-manifest", "build-exit", "run-exit"):
        role = defect.replace("-", "_")
        (parent / role).write_bytes(b"1\n")
        receipt["evidence"][role]["sha256"] = sha((parent / role).read_bytes())
    elif defect == "path-collision":
        receipt["evidence"]["run_log"] = receipt["evidence"]["build_log"]
    elif defect == "relative-path":
        receipt["evidence"]["run_log"]["path"] = "relative/run.log"
    elif defect == "symlink":
        link = parent / "run_log_symlink"
        link.symlink_to(parent / "run_log")
        receipt["evidence"]["run_log"]["path"] = str(link)
    elif defect == "parent-traversal":
        receipt["evidence"]["run_log"]["path"] = str(
            parent / ".." / "immutable" / "run_log"
        )
    rewrite_execution(pilot, receipt)
    with pytest.raises(ValueError, match=reason):
        materialize(config, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "role",
    [
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
    ],
)
def test_actual_retained_execution_evidence_hashes_are_checked(pilot, role):
    config, output, parent, _, _ = pilot
    # Rebinding the primary execution receipt cannot bless changed referenced evidence.
    receipt = json.loads((parent / "execution").read_text())
    (parent / role).write_bytes((parent / role).read_bytes() + b"changed")
    rewrite_execution(pilot, receipt)
    with pytest.raises(
        ValueError, match=f"execution evidence {role}: input checksum mismatch"
    ):
        materialize(config, output)
    assert not output.exists()


@pytest.mark.parametrize(
    "malformed",
    [
        True,
        "placeholder",
        {},
        {"/lib/fake.so": "not-a-sha256"},
        {"relative.so": "a" * 64},
        {"/lib/fake.so": True},
        {"/lib/fake.so": "A" * 64},
    ],
)
@pytest.mark.parametrize("source", ["comparison", "execution"])
def test_runtime_library_shapes_after_coherent_hash_rebinding(pilot, malformed, source):
    config, output, parent, _, _ = pilot
    receipt = json.loads((parent / "execution").read_text())
    if source == "comparison":
        report = json.loads((parent / "comparison").read_text())
        report["runtime_shared_libraries_sha256"] = malformed
        write_json(parent / "comparison", report)
        receipt["parents"]["comparison"] = sha((parent / "comparison").read_bytes())
    else:
        receipt["runtime_shared_libraries_sha256"] = malformed
    rewrite_execution(pilot, receipt)
    with pytest.raises(ValueError, match="runtime library provenance requires"):
        materialize(config, output)
    assert not output.exists()


def test_valid_remote_library_map_does_not_require_local_files_and_must_match(pilot):
    config, output, parent, _, _ = pilot
    receipt = json.loads((parent / "execution").read_text())
    receipt["runtime_shared_libraries_sha256"] = {
        "/nonexistent-remote-hpc/lib-valid.so": "a" * 64
    }
    rewrite_execution(pilot, receipt)
    with pytest.raises(ValueError, match="execution runtime library ancestry"):
        materialize(config, output)
    report = json.loads((parent / "comparison").read_text())
    report["runtime_shared_libraries_sha256"] = receipt[
        "runtime_shared_libraries_sha256"
    ]
    write_json(parent / "comparison", report)
    receipt["parents"]["comparison"] = sha((parent / "comparison").read_bytes())
    rewrite_execution(pilot, receipt)
    assert materialize(config, output)["count"] == 2


def test_empty_preparation_configuration_is_not_execution_provenance(pilot):
    config, output, parent, _, bind = pilot
    prep = json.loads((parent / "preparation").read_text())
    prep["configuration"] = {}
    write_json(parent / "preparation", prep)
    bind()
    with pytest.raises(ValueError, match="preparation configuration required"):
        materialize(config, output)
    assert not output.exists()


def test_output_cannot_be_inside_retained_execution_evidence_parent(pilot):
    config, output, parent, _, _ = pilot
    separate = output.parent.parent / "separate-evidence"
    separate.mkdir()
    retained = separate / "run.log"
    retained.write_bytes((parent / "run_log").read_bytes())
    receipt = json.loads((parent / "execution").read_text())
    receipt["evidence"]["run_log"]["path"] = str(retained)
    rewrite_execution(pilot, receipt)
    with pytest.raises(
        ValueError, match="destination collides with execution evidence parent"
    ):
        materialize(config, separate / "new-candidate")
    assert not (separate / "new-candidate").exists()


def test_execution_evidence_is_rechecked_before_output(pilot, monkeypatch):
    import crucible.rhs_data as module

    config, output, parent, _, _ = pilot
    original = module.checked
    calls = {}

    def change_evidence_at_final_input_recheck(entry):
        path = entry["path"]
        calls[path] = calls.get(path, 0) + 1
        if path == str(parent / "states") and calls[path] == 2:
            (parent / "run_log").write_bytes(b"changed after initial evidence check")
        return original(entry)

    monkeypatch.setattr(module, "checked", change_evidence_at_final_input_recheck)
    with pytest.raises(ValueError, match="input checksum mismatch: run_log"):
        materialize(config, output)
    assert not output.exists()
