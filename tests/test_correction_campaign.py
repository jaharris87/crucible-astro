"""Public D-040 scheduling fixtures: no compiler or physical source is invoked."""

import importlib.util
import json
import struct
from pathlib import Path

import pytest


@pytest.fixture
def runner():
    source = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/correction_campaign.py"
    )
    spec = importlib.util.spec_from_file_location("public_correction_campaign", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def wire(mode=0):
    values = [0.0] * 160 + [1.0] * 160 + [0.25] * 160
    values += [0.0, 0.01] + [1.0, 1.0] + [1e6, 1e6]
    grid = [0.0, 0.005, 0.01] if mode else [0.0]
    values += grid + grid
    return struct.pack(
        "<8i2d", 0x43524432, 1, 160, 2, len(grid), len(grid), mode, 7, 1e-15, 1e-13
    ) + struct.pack("<" + str(len(values)) + "d", *values)


def accepted_bytes():
    rows = []
    for index, when in enumerate((0.0, 0.005, 0.01)):
        values = [when] + [0.25 + index * 1e-4] * 160 + [0.0] * 327
        rows.append(struct.pack("<488d", *values))
    return b"".join(rows)


@pytest.fixture
def campaign(runner, tmp_path, monkeypatch):
    root = tmp_path / "campaign"
    root.mkdir()
    inputs = {}
    for case in runner.CASES:
        inputs[case] = {}
        for stage in runner.STAGES[:-1]:
            relative = "inputs/" + case + "-" + stage + ".bin"
            target = root / relative
            target.parent.mkdir(exist_ok=True)
            control = "standard" if stage == "control" else stage[3:]
            target.write_bytes(
                runner.correction_input(wire(int(stage != "control")), control)
            )
            inputs[case][stage] = {"path": relative, "sha256": runner.digest(target)}
    immutable = {}
    for name, source in (
        ("correction_campaign.py", Path(runner.__file__)),
        ("campaign.py", Path(runner.common.__file__)),
        ("diagnostic_campaign.py", Path(runner.diag.__file__)),
    ):
        (root / name).write_bytes(source.read_bytes())
        immutable[name] = runner.digest(root / name)
    prepared = {
        "inputs": inputs,
        "attempts": runner.fixed_plan(inputs),
        "immutable_files": immutable,
        "build_label": "A",
    }
    save(root / "prepared.json", prepared)
    monkeypatch.setattr(runner, "validate_prepared", lambda *a: None)
    monkeypatch.setattr(runner, "build_identities", lambda root: {"frozen": "build"})
    monkeypatch.setattr(runner, "synthetic_checks", lambda root: {"pass": True})
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    return root, prepared


class Gates:
    def __init__(self, ordinary=None, identity=None, aggregate=None):
        self.ordinary = ordinary
        self.identity = identity
        self.aggregate = aggregate
        self.visits = []

    def precision_gate(self, root):
        return {"pass": True}

    def attempt_gate(self, root, spec, result):
        self.visits.append(spec["name"])
        # The native SUCCESS marker cannot override this independent fixture.
        outcome = json.loads(
            (root / "attempts" / spec["name"] / "science.json").read_text()
        )
        assert outcome["science"] == spec["name"]
        return {
            "pass": spec["name"] not in (self.ordinary, self.identity),
            "ordinary_numerical_failure": spec["name"] == self.ordinary,
            "identity_failure": spec["name"] == self.identity,
        }

    def pilot_gate(self, root):
        return {"pass": self.aggregate != "pilot"}

    def trajectory_gate(self, root):
        return {"pass": self.aggregate != "trajectory"}

    def derivative_gate(self, root):
        return {"pass": self.aggregate != "derivative"}


def fake_processes(
    runner,
    monkeypatch,
    *,
    gates=None,
    interrupt_at=None,
    signal_at=None,
    missing_counters=None,
):
    gates = gates or Gates()
    monkeypatch.setattr(runner, "science_gates", lambda root: gates)
    launched = []

    def run(root, spec, executable, launcher, *, resume, arguments):
        assert not resume and arguments == tuple(spec["arguments"])
        launched.append(spec["name"])
        work = root / "attempts" / spec["name"]
        work.mkdir(parents=True, exist_ok=False)
        (work / "input.bin").write_bytes((root / spec["input"]).read_bytes())
        (work / "process.log").write_text("public fake process\n")
        if len(launched) == interrupt_at:
            record = {"name": spec["name"], "status": "RUNNING", "completed": False}
            save(work / "attempt.json", record)
            raise KeyboardInterrupt()
        (work / "status.txt").write_text(
            "SUCCESS\n" if len(launched) != signal_at else ""
        )
        save(work / "science.json", {"science": spec["name"]})
        if len(launched) != missing_counters:
            counts = dict.fromkeys(runner.diag.COUNTERS, 0)
            # Deliberately exceeds D-039's historical resource envelope. D-040
            # authorizes this finite process plan without inheriting that cap.
            counts.update(rhs=11000000, newton=2, accepted=3)
            save(work / "counters.json", counts)
            save(
                work / "assembly-counters.json",
                {
                    "schema": "crucible.assembly-counters.v1",
                    "fresh_requests": 11000001,
                    "rhs": 11000000,
                    "assembly_calls": 11000000,
                },
            )
        if spec["mode"] == 1:
            (work / "accepted.bin").write_bytes(accepted_bytes())
        record = {
            "name": spec["name"],
            "completed": True,
            "status": "RETURNED",
            "returncode": -15 if len(launched) == signal_at else 0,
            "input_sha256": spec["input_sha256"],
            "files": runner.common.snapshot(work),
        }
        save(work / "attempt.json", record)
        return record

    monkeypatch.setattr(runner.common, "run_attempt", run)
    return launched, gates


def test_exact_twenty_process_stage_order_and_conditional_diagnostics(
    campaign, runner, monkeypatch
):
    root, prepared = campaign
    launched, gates = fake_processes(runner, monkeypatch)
    result = runner.execute(root)
    assert result["complete"] and result["qualification_pass"]
    assert len(launched) == 20 and launched == [a["name"] for a in prepared["attempts"]]
    assert len(gates.visits) == 20
    assert result["physical_rhs_calls"] == 20 * 11000000
    assert result["guarded_fresh_requests"] == 20 * 11000001
    assert result["call_accounting_complete"]
    assert result["algorithm"]["newton_iterations_per_attempt"] == 30
    for name in (
        "development-J5",
        "development-J10",
        "validation-J5",
        "validation-J10",
    ):
        attempt = next(a for a in result["attempts"] if a["name"] == name)
        assert attempt["state_binding"]["path"].endswith("state-binding.json")
        assert not any("state_binding" in s for s in prepared["attempts"])
    with pytest.raises(ValueError, match="restart"):
        runner.execute(root)


@pytest.mark.parametrize(
    "stage,index",
    [
        ("L0-standard", 4),
        ("L0-tight", 6),
        ("L1-standard", 8),
        ("L2-standard", 10),
        ("L3-standard", 12),
        ("L3-tight", 14),
        ("derivative", 20),
    ],
)
def test_ordinary_failure_completes_stage_population_and_stops_dependents(
    campaign, runner, monkeypatch, stage, index
):
    root, prepared = campaign
    failed = next(a["name"] for a in prepared["attempts"] if a["stage"] == stage)
    launched, _ = fake_processes(runner, monkeypatch, gates=Gates(ordinary=failed))
    result = runner.execute(root)
    assert len(launched) == index
    assert result["complete"] and not result["qualification_pass"]
    assert all(
        a["status"] == "CONDITIONALLY_UNATTEMPTED" for a in result["attempts"][index:]
    )


@pytest.mark.parametrize(
    "stage,launched_count", [("control", 1), ("L1-standard", 7), ("derivative", 15)]
)
def test_shared_identity_failure_stops_immediately(
    campaign, runner, monkeypatch, stage, launched_count
):
    root, prepared = campaign
    failed = next(a["name"] for a in prepared["attempts"] if a["stage"] == stage)
    launched, _ = fake_processes(runner, monkeypatch, gates=Gates(identity=failed))
    with pytest.raises(ValueError, match="identity/corruption"):
        runner.execute(root)
    assert len(launched) == launched_count
    result = json.loads((root / "campaign.json").read_text())
    assert not result["complete"] and not result["qualification_pass"]
    assert all(
        a["unattempted_reason"] == "IDENTITY_OR_SOFTWARE_FAILURE"
        for a in result["attempts"][launched_count:]
    )


@pytest.mark.parametrize(
    "aggregate,expected", [("pilot", 6), ("trajectory", 14), ("derivative", 20)]
)
def test_aggregate_gates_are_required_despite_all_process_success(
    campaign, runner, monkeypatch, aggregate, expected
):
    root, _ = campaign
    launched, _ = fake_processes(runner, monkeypatch, gates=Gates(aggregate=aggregate))
    result = runner.execute(root)
    assert len(launched) == expected and not result["qualification_pass"]


def test_one_restart_reuses_completed_artifacts_and_identical_original_input(
    campaign, runner, monkeypatch
):
    root, prepared = campaign
    launched, _ = fake_processes(runner, monkeypatch, interrupt_at=4)
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    before = (root / "attempts/development-L0-standard/attempt.json").read_bytes()
    continued, _ = fake_processes(runner, monkeypatch)
    result = runner.execute(
        root,
        infrastructure_restart="scheduler node interruption, original logs retained",
    )
    assert len(launched) == 4 and len(continued) == 17
    assert (
        root / "attempts/development-L0-standard/attempt.json"
    ).read_bytes() == before
    assert (
        result["interrupted_attempts"][0]["record"]["name"] == "validation-L0-standard"
    )
    retained = root / result["interrupted_attempts"][0]["directory"]
    assert (retained / "process.log").read_text() == "public fake process\n"
    original = root / prepared["inputs"]["validation"]["L0-standard"]["path"]
    assert (
        root / "attempts/validation-L0-standard/input.bin"
    ).read_bytes() == original.read_bytes()
    # Missing in-flight counter evidence remains explicitly incomplete after the
    # restart; no false claim of full request accounting may be introduced.
    assert not result["call_accounting_complete"]
    assert result["qualification_pass"] and result["attempt_accounting_complete"]


def test_second_infrastructure_restart_is_refused(campaign, runner, monkeypatch):
    root, _ = campaign
    fake_processes(runner, monkeypatch, interrupt_at=3)
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    fake_processes(runner, monkeypatch, interrupt_at=2)
    with pytest.raises(KeyboardInterrupt):
        runner.execute(
            root, infrastructure_restart="first diagnosed infrastructure failure"
        )
    with pytest.raises(ValueError, match="only one"):
        runner.execute(root, infrastructure_restart="second infrastructure failure")


def test_numerical_failure_cannot_restart(campaign, runner, monkeypatch):
    root, _ = campaign
    fake_processes(runner, monkeypatch, gates=Gates(ordinary="development-L0-standard"))
    runner.execute(root)
    with pytest.raises(ValueError, match="only one"):
        runner.execute(
            root, infrastructure_restart="attempt to relabel numerical failure"
        )


def test_restart_checks_completed_artifacts(campaign, runner, monkeypatch):
    root, _ = campaign
    fake_processes(runner, monkeypatch, interrupt_at=3)
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    (root / "attempts/development-control/process.log").write_text(
        "changed retained output"
    )
    with pytest.raises(ValueError, match="artifact changed"):
        runner.execute(root, infrastructure_restart="node failure")


def test_signal_interruption_is_retained_and_not_a_numerical_retry(
    campaign, runner, monkeypatch
):
    root, _ = campaign
    launched, _ = fake_processes(runner, monkeypatch, signal_at=3)
    with pytest.raises(RuntimeError, match="interrupted"):
        runner.execute(root)
    result = json.loads((root / "campaign.json").read_text())
    assert len(launched) == 3 and result["attempts"][2]["status"] == "INTERRUPTED"
    assert result["stop_kind"] == "INFRASTRUCTURE_INTERRUPTION"
    assert result["physical_rhs_calls"] == 3 * 11000000


def test_missing_counters_never_claims_accounting_or_qualification(
    campaign, runner, monkeypatch
):
    root, _ = campaign
    fake_processes(runner, monkeypatch, missing_counters=3)
    with pytest.raises(ValueError, match="counter accounting missing"):
        runner.execute(root)
    result = json.loads((root / "campaign.json").read_text())
    assert not result["qualification_pass"] and not result["call_accounting_complete"]


def test_diagnostic_binding_extracts_exact_bits_and_refuses_corruption(
    campaign, runner
):
    root, prepared = campaign
    parent = "development-L3-standard"
    work = root / "attempts" / parent
    work.mkdir(parents=True)
    raw = accepted_bytes()
    (work / "accepted.bin").write_bytes(raw)
    save(work / "attempt.json", {"completed": True})
    save(
        root / "campaign.json",
        {
            "attempts": [
                {
                    "name": parent,
                    "completed": True,
                    "qualification_pass": True,
                    "input_sha256": "a" * 64,
                    "files": runner.common.snapshot(work),
                }
            ]
        },
    )
    spec = next(s for s in prepared["attempts"] if s["name"] == "development-J5")
    bound = runner.bind_diagnostic(root, prepared, spec)
    actual = (root / bound["input"]).read_bytes()
    assert actual[2608:3888] == raw[488 * 8 + 8 : 488 * 8 + 161 * 8]
    assert struct.unpack_from("<8i", actual)[4:7] == (1, 1, 0)
    assert struct.unpack_from("<2d", actual, len(actual) - 16) == (0.005, 0.005)
    assert runner.bind_diagnostic(root, prepared, spec) == bound
    (root / bound["input"]).write_bytes(actual[:-1] + bytes([actual[-1] ^ 1]))
    with pytest.raises(ValueError, match="binding differs"):
        runner.bind_diagnostic(root, prepared, spec)


def test_input_derivation_changes_exactly_control_bytes(runner):
    old = wire()
    for control, values in runner.CONTROLS.items():
        new = runner.correction_input(old, control)
        assert new[:32] == old[:32] and new[48:] == old[48:]
        assert struct.unpack_from("<2d", new, 32) == values
    with pytest.raises(ValueError):
        runner.correction_input(b"truncated")


def test_native_prerequisite_population_extends_original_sixteen(
    runner, monkeypatch, tmp_path
):
    received = []
    monkeypatch.setattr(
        runner.common,
        "synthetic_checks",
        lambda root, *, extra_scenarios: received.extend(extra_scenarios),
    )
    runner.synthetic_checks(tmp_path)
    assert len(received) == 14
    assert received[:6] == [("trajectory_synthetic", "retry-snapshot", None)] + [
        ("assembly_synthetic", name, None)
        for name in ("precision", "arithmetic", "malformed", "nonfinite", "overflow")
    ]
    assert {name for executable, name, expected in received[6:]} == {
        "correction-" + name
        for name in (
            "nonlinear",
            "stiff",
            "rounded",
            "current",
            "retry",
            "projection",
            "projection-bound",
            "incomplete",
        )
    }
    assert received[-1] == (
        "trajectory_synthetic",
        "correction-incomplete",
        "FAILURE incomplete horizon",
    )


@pytest.mark.parametrize(
    "mutation",
    ["qualified", "reload", "campaign", "source", "inputs", "closure", "proof"],
)
def test_build_b_requires_fully_bound_a_qualification(campaign, runner, mutation):
    root, bprep = campaign
    bprep.update(
        build_label="B",
        source_commit="commit",
        source_tree="tree",
        protocol_sha256=runner.PROTOCOL_SHA256,
        reference_baselines={},
        source_diff={},
    )
    aprep = {**bprep, "build_label": "A"}
    apath = root / "reference-records/build-a-prepared.json"
    save(apath, aprep)
    cpath = root / "reference-records/build-a-campaign.json"
    acampaign = {
        "qualification_pass": True,
        "complete": True,
        "prepared_sha256": runner.digest(apath),
    }
    save(cpath, acampaign)
    proof = {
        "schema": "crucible.correction.verification.v1",
        "qualification_pass": True,
        "prepared_sha256": runner.digest(apath),
        "campaign_sha256": runner.digest(cpath),
        "source_commit": "commit",
        "source_tree": "tree",
        "protocol_sha256": runner.PROTOCOL_SHA256,
        "build_label": "A",
        "artifact_identity_pass": True,
        "reload_pass": True,
    }
    proof_path = root / "reference-records/build-a-verification.json"
    save(proof_path, proof)
    bprep["build_a"] = {
        "prepared_sha256": runner.digest(apath),
        "campaign_sha256": runner.digest(cpath),
        "verification": {
            "path": "reference-records/build-a-verification.json",
            "sha256": runner.digest(proof_path),
        },
    }
    save(root / "prepared.json", bprep)
    assert runner.build_b_release_gate(root)["pass"]
    if mutation == "qualified":
        proof["qualification_pass"] = False
    elif mutation == "reload":
        proof["reload_pass"] = False
    elif mutation == "campaign":
        proof["campaign_sha256"] = "0" * 64
    elif mutation == "source":
        bprep["source_commit"] = "another-source"
    elif mutation == "inputs":
        bprep["inputs"] = {**bprep["inputs"], "substitute": {}}
    elif mutation == "closure":
        bprep["immutable_files"]["campaign.py"] = "0" * 64
    else:
        proof_path.write_text("modified source-bound proof")
    if mutation in {"qualified", "reload", "campaign"}:
        save(proof_path, proof)
        bprep["build_a"]["verification"]["sha256"] = runner.digest(proof_path)
    save(root / "prepared.json", bprep)
    with pytest.raises(ValueError):
        runner.build_b_release_gate(root)


def test_offline_prepare_binds_originals_and_retained_controls_without_native_calls(
    runner, tmp_path, monkeypatch
):
    import numpy as np

    from crucible import trajectory_reference as ref

    source = tmp_path / "source"
    public = source / "experiments/trajectory_reference"
    public.mkdir(parents=True)
    for name in (*runner.HOST_FILES, *runner.NATIVE_ADDITIONS, "CORRECTION.md"):
        (public / name).write_text("# synthetic staged helper\n")
    (public / "correction_campaign.py").write_bytes(Path(runner.__file__).read_bytes())
    monkeypatch.setattr(
        runner, "PROTOCOL_SHA256", runner.digest(public / "CORRECTION_PROTOCOL.md")
    )
    rhs = public.parent / "rhs_reference"
    rhs.mkdir()
    for name in ("arithmetic.py", "reference.py"):
        (rhs / name).write_text("# synthetic arithmetic dependency\n")
    old_root = tmp_path / "accepted-assembly"
    old_root.mkdir()
    save(old_root / "prepared.json", {"source_commit": runner.D039_SOURCE})
    old_attempts = []
    for case in runner.CASES:
        name = case + "-initial-identity-3"
        work = old_root / "attempts" / name
        work.mkdir(parents=True)
        files = {}
        for filename in runner.REFERENCE_FILES:
            (work / filename).write_bytes((case + filename).encode())
            files[filename] = {"sha256": runner.digest(work / filename)}
        old_attempts.append({"name": name, "files": files})
    save(old_root / "campaign.json", {"complete": True, "attempts": old_attempts})
    monkeypatch.setattr(
        runner, "D039_PREPARED", runner.digest(old_root / "prepared.json")
    )
    monkeypatch.setattr(
        runner, "D039_CAMPAIGN", runner.digest(old_root / "campaign.json")
    )
    annex = tmp_path / "original-annex.json"
    annex.write_text('{"synthetic_original":true}\n')
    monkeypatch.setattr(ref, "ANNEX_SHA256", runner.digest(annex))
    config = tmp_path / "original-config.json"
    save(config, {"annex": str(annex)})
    outer = tmp_path / "correction-config.json"
    save(
        outer,
        {"trajectory_prepare_config": str(config), "assembly_root": str(old_root)},
    )
    species = np.array(
        [(0, 1), (1, 1)] + [(a // 2, a) for a in range(2, 160)], dtype=np.int64
    )
    y = np.zeros(160)
    y[:2] = [0.1, 0.3]
    case_data = {
        "Y0": y,
        "species_Z_A": species,
        "source_time": np.array([0.0, 0.01]),
        "time": np.array([0.0, 0.01]),
        "T9": np.ones(2),
        "rho": np.full(2, 1e6),
        "requested_time": np.array([0.0, 0.005, 0.01]),
    }
    helpers = []

    def original_prepare(config_path, destination, source_root):
        helpers.append((config_path, source_root))
        destination.mkdir()
        (destination / "inputs").mkdir()
        (destination / "bundle").mkdir()
        save(destination / "bundle/source-manifest.json", {"files": {}})
        plans = []
        for case in runner.CASES:
            np.savez(destination / "inputs" / (case + ".npz"), **case_data)
            for suffix, mode, level in [("control", 0, 0)] + [
                ("L" + str(i), 1, i) for i in range(4)
            ]:
                relative = "inputs/" + case + "-" + suffix + ".bin"
                data = ref.wire_input(
                    case_data,
                    mode=mode,
                    mesh=ref.nested_mesh(case_data, level) if mode else np.array([0.0]),
                )
                (destination / relative).write_bytes(data)
                plans.append({"name": case + "-" + suffix, "input": relative})
        original = {
            "source_commit": "new-source",
            "source_tree": "new-tree",
            "attempts": plans,
            "costs": {},
        }
        save(destination / "prepared.json", original)
        return original

    monkeypatch.setattr(ref, "prepare", original_prepare)
    git_calls = []

    def offline_git(command, **kwargs):
        git_calls.append(command)
        assert command[:3] == ["git", "diff", "--binary"]
        return type("Result", (), {"stdout": b"fixed source diff\n"})()

    monkeypatch.setattr(runner.subprocess, "run", offline_git)
    before = {str(p): runner.digest(p) for p in old_root.rglob("*") if p.is_file()}
    destination = tmp_path / "new-preparation"
    prepared = runner.prepare(outer, destination, source)
    monkeypatch.setattr(runner, "ANNEX_SHA256", ref.ANNEX_SHA256)
    monkeypatch.setattr(
        runner,
        "INPUT_SHA256",
        {
            case: runner.digest(destination / "inputs" / (case + ".npz"))
            for case in runner.CASES
        },
    )
    runner.validate_prepared(destination, prepared)
    assert helpers == [(str(config), source)] and len(git_calls) == 1
    assert len(prepared["attempts"]) == 20
    assert (
        prepared["source_commit"] == "new-source"
        and prepared["source_tree"] == "new-tree"
    )
    assert (
        prepared["input_preparation_history"]["status"]
        == "OFFLINE_HELPER_ONLY_OLD_PLAN_NOT_EXECUTED"
    )
    for case in runner.CASES:
        for stage, entry in prepared["inputs"][case].items():
            payload = (destination / entry["path"]).read_bytes()
            base = (
                destination
                / "inputs"
                / (
                    case
                    + (
                        "-control.bin"
                        if stage == "control"
                        else "-" + stage[:2] + ".bin"
                    )
                )
            )
            original = base.read_bytes()
            assert payload[:32] == original[:32] and payload[48:] == original[48:]
            assert prepared["immutable_files"][entry["path"]] == entry["sha256"]
    assert before == {
        str(p): runner.digest(p) for p in old_root.rglob("*") if p.is_file()
    }


@pytest.mark.parametrize("gate_name", ["synthetic", "precision", "B-release"])
def test_prephysical_prerequisite_refusal_starts_no_physical_process(
    campaign, runner, monkeypatch, gate_name
):
    root, prepared = campaign
    launched, gates = fake_processes(runner, monkeypatch)
    if gate_name == "synthetic":

        def refuse(root):
            raise ValueError("synthetic prerequisite failed")

        monkeypatch.setattr(runner, "synthetic_checks", refuse)
    elif gate_name == "precision":
        monkeypatch.setattr(gates, "precision_gate", lambda root: {"pass": False})
    else:
        prepared["build_label"] = "B"
        save(root / "prepared.json", prepared)
        monkeypatch.setattr(
            runner, "build_b_release_gate", lambda root: {"pass": False}
        )
    with pytest.raises(ValueError):
        runner.execute(root)
    assert launched == []


def test_aggregate_identity_corruption_stops_globally(campaign, runner, monkeypatch):
    root, _ = campaign
    launched, gates = fake_processes(runner, monkeypatch)
    monkeypatch.setattr(
        gates, "pilot_gate", lambda root: {"pass": False, "identity_failure": True}
    )
    with pytest.raises(ValueError, match="aggregate identity/corruption"):
        runner.execute(root)
    manifest = json.loads((root / "campaign.json").read_text())
    assert (
        len(launched) == 6 and manifest["stop_kind"] == "IDENTITY_OR_SOFTWARE_FAILURE"
    )


@pytest.fixture
def host_identities(runner):
    return runner.load_module(
        "public_correction_host_identities",
        Path(runner.__file__).parent / "correction_host_identities.py",
    )


def test_host_library_inventory_includes_interrupted_known_hashes(
    host_identities, tmp_path
):
    first, second = tmp_path / "first.so", tmp_path / "second.so"
    first.write_bytes(b"first-library")
    second.write_bytes(b"second-library")
    identity, other = "a" * 64, "b" * 64
    campaign = {
        "build": {"libraries": {str(first): identity}},
        "attempts": [
            {
                "name": "completed",
                "completed": True,
                "loaded_library_unavailable_reason": None,
                "loaded_library_hashes": {str(first): identity},
            }
        ],
        "interrupted_attempts": [
            {
                "record": {
                    "name": "interrupted",
                    "loaded_library_hashes": {str(second): other},
                }
            }
        ],
    }
    expected, completed = host_identities.expected_library_files(campaign)
    assert expected == {str(first): identity, str(second): other} and completed == [
        "completed"
    ]
    campaign["interrupted_attempts"][0]["record"]["loaded_library_hashes"][
        str(first)
    ] = other
    with pytest.raises(ValueError, match="identity differs"):
        host_identities.expected_library_files(campaign)


def test_host_interrupted_maps_are_read_only_later_observations(
    host_identities, runner, tmp_path
):
    work = tmp_path / "interrupted/example-attempt-1"
    work.mkdir(parents=True)
    library = tmp_path / "runtime.so"
    library.write_bytes(b"actual-execution-host-library")
    maps = work / "loaded-maps.txt"
    maps.write_text("1000-2000 r-xp 00000000 00:00 123 " + str(library) + "\n")
    campaign = {
        "attempts": [],
        "interrupted_attempts": [
            {
                "directory": "interrupted/example-attempt-1",
                "record": {
                    "name": "example",
                    "files": {"loaded-maps.txt": {"sha256": runner.digest(maps)}},
                },
            }
        ],
    }
    before = maps.read_bytes()
    evidence = host_identities.interrupted_mapping_evidence(tmp_path, campaign, runner)[
        0
    ]
    assert evidence["mapped_paths"] == [str(library)]
    assert evidence["observed_live_hashes"] == {str(library): runner.digest(library)}
    assert evidence["recorded_hashes"] == {}
    assert "Process-time hashes" in " ".join(evidence["unavailable"])
    assert maps.read_bytes() == before
    maps.write_text("corrupted interrupted raw mapping")
    with pytest.raises(ValueError, match="mapping changed"):
        host_identities.interrupted_mapping_evidence(tmp_path, campaign, runner)


def test_controller_kill_recovery_preserves_original_receipts(
    campaign, runner, monkeypatch
):
    root, prepared = campaign
    launched, _ = fake_processes(runner, monkeypatch, interrupt_at=3)
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    manifest = json.loads((root / "campaign.json").read_text())
    # Model a controller killed before its finally block, leaving the original
    # STARTING/RUNNING receipts rather than the normal handled interruption.
    manifest.pop("stop_kind")
    manifest.pop("exception")
    manifest["attempts"][2] = {
        **prepared["attempts"][2],
        "status": "STARTING",
        "completed": False,
    }
    save(root / "campaign.json", manifest)
    active = root / "attempts" / prepared["attempts"][2]["name"]
    save(
        active / "attempt.json",
        {
            "name": prepared["attempts"][2]["name"],
            "status": "RUNNING",
            "completed": False,
        },
    )
    old_campaign = (root / "campaign.json").read_bytes()
    old_attempt = (active / "attempt.json").read_bytes()
    continued, _ = fake_processes(runner, monkeypatch)
    result = runner.execute(
        root,
        infrastructure_restart="scheduler confirms both old controller and native process terminated",
    )
    assert len(launched) == 3 and len(continued) == 18
    assert result["qualification_pass"] and not result["call_accounting_complete"]
    assert (root / "campaign-before-recovery.json").read_bytes() == old_campaign
    preserved = (
        root
        / result["interrupted_attempts"][0]["directory"]
        / "attempt-before-recovery.json"
    )
    assert preserved.read_bytes() == old_attempt
    for name, identity in result["infrastructure_recovery"][
        "original_receipts"
    ].items():
        assert runner.digest(root / name) == identity


def test_no_physical_attempt_is_needed_for_build_library_receipt(
    host_identities, tmp_path
):
    library = str(tmp_path / "linked.so")
    expected, completed = host_identities.expected_library_files(
        {
            "build": {"libraries": {library: "a" * 64}},
            "attempts": [],
            "interrupted_attempts": [],
        }
    )
    assert expected == {library: "a" * 64} and completed == []
