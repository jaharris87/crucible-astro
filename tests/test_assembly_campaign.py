"""Public orchestration fixtures; fake processes never import a physical source.

The gate fixture deliberately uses a tiny independent raw success/failure signal.
Exact arithmetic and full native wire correctness have separate gate-module tests.
These tests check that the runner obeys science results even with native SUCCESS.
"""

import importlib.util
import json
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def runner():
    path = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/assembly_campaign.py"
    )
    spec = importlib.util.spec_from_file_location("public_assembly_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def maps_bytes(runner):
    la, le = [], []
    for species in range(160):
        la.extend(1 if species == 0 else n + 1 for n in runner.diag.NB)
        le.extend(runner.diag.NB)
    data = struct.pack("<1280i", *(la + le))
    for order, (nc, nb) in enumerate(zip(runner.diag.NC, runner.diag.NB), 1):
        data += struct.pack("<3i", order, nc, nb) + bytes(
            (5 if order == 1 else 6) * nc * 4
        )
        data += struct.pack("<" + str(2 * nb) + "i", *([1] * (2 * nb)))
        data += struct.pack("<" + str(nb) + "d", *([1.0] * nb))
    return data


def baseline_bytes(runner, wire, call=1):
    echo = runner.diag.input_echo(wire)
    values = [
        float(call),
        *struct.unpack("<3d", echo["time_T9_rho"]),
        1.0,
        0.5,
        0.5,
        2.0,
        3.0,
        4.0,
    ]
    values += list(struct.unpack("<160d", echo["Y"])) + [1.0] * 160
    values += [0.25] * (sum(runner.diag.NC) + sum(runner.diag.NB))
    return (
        struct.pack("<12i", 0x43524442, 1, 160, *runner.diag.NC, *runner.diag.NB, 10240)
        + struct.pack("<" + str(len(values)) + "d", *values)
        + bytes(40960)
    )


def wire_input(time=0.0, *, mode=0):
    y = [1.0] + [0.0] * 159
    if mode:
        values = (
            [0.0] * 160
            + [1.0] * 160
            + y
            + [0.0, 0.01]
            + [1.0, 1.0]
            + [1e6, 1e6]
            + [0.0, 0.01]
            + [0.0, 0.0001]
        )
    else:
        values = (
            [0.0] * 160
            + [1.0] * 160
            + y
            + [0.0, 0.01]
            + [1.0, 1.0]
            + [1e6, 1e6]
            + [time, time]
        )
    return struct.pack(
        "<8i2d",
        0x43524432,
        1,
        160,
        2,
        2 if mode else 1,
        2 if mode else 1,
        mode,
        1,
        1e-13,
        1e-11,
    ) + struct.pack("<" + str(len(values)) + "d", *values)


GATE_FIXTURE = '''"""Tiny raw gate oracle for runner control-flow tests only."""
import json

def precision_gate(root):
    raw=(root/'synthetic/assembly_synthetic-precision/raw-proof.txt').read_text()
    return {'pass':raw=='EXACT'}

def signal(root, spec):
    work = root / 'attempts' / spec['name']
    data = json.loads((work / 'science.json').read_text())
    return data, work

def identity_attempt_gate(root, spec, result):
    data, work = signal(root, spec)
    return {'pass':data['arithmetic'], 'software_pass':True, 'fatal':False}

def identity_gate(root):
    data = json.loads((root / 'campaign.json').read_text())
    selected = [a for a in data['attempts'] if a['stage']=='identity']
    passed = len(selected)==6 and all(a.get('science_gate',{}).get('pass') for a in selected)
    return {'pass':passed, 'software_pass':True}

def derivative_attempt_gate(root, spec, result):
    data, work = signal(root, spec)
    return {'pass':data['directional'], 'software_pass':not data['fatal'], 'fatal':data['fatal']}

def derivative_gate(root):
    data = json.loads((root / 'campaign.json').read_text())
    selected = [a for a in data['attempts'] if a['stage']=='derivative']
    return {'pass':len(selected)==3 and all(a.get('science_gate',{}).get('pass') for a in selected), 'software_pass':True}

def first_step_gate(root, spec, result):
    data, work = signal(root,spec)
    terminal=(work / 'status.txt').read_text().strip()
    ordinary=data['outcome']=='ordinary' and terminal=='FAILURE first native step failed' and (work/'failure-forensics.bin').is_file()
    passed=data['outcome']=='pass' and terminal=='SUCCESS' and result['returncode']==0
    fatal=not (passed or ordinary)
    return {'pass':passed, 'software_pass':not fatal, 'fatal':fatal, 'ordinary_numerical_failure':ordinary, 'achieved_time':0.0001 if passed else None, 'requested_h':0.0001}
'''


@pytest.fixture
def prepared(tmp_path, runner, monkeypatch):
    root = tmp_path
    bundle = root / "bundle"
    bundle.mkdir()
    (bundle / "network").mkdir()
    (bundle / "helm_table.dat").write_bytes(b"public synthetic table")
    (bundle / "source-manifest.json").write_text("{}\n")
    for name, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
        ("assembly_synthetic", "assembly-executable.sha256"),
    ):
        (bundle / name).write_bytes(("fake " + name).encode())
        (bundle / receipt).write_text(runner.digest(bundle / name) + "  " + name + "\n")
    library = root / "fake-library"
    library.write_bytes(b"public library")
    write_json(
        bundle / "linked-library-hashes.json", {str(library): runner.digest(library)}
    )
    states, references, controls, old_attempts, baseline_hashes = [], {}, {}, [], {}
    for name in runner.diag.STATES:
        path = root / "inputs" / name
        path.mkdir(parents=True)
        when = 1.953125e-7 if name == runner.diag.STATES[2] else 0.0
        wire = wire_input(when)
        (path / "input.bin").write_bytes(wire)
        companions = {}
        extra = (
            {"old-state.bin": wire[2608:3888], "frozen-h.bin": struct.pack("<d", when)}
            if when
            else {"expected-control.bin": struct.pack("<160d", *([1.0] * 160))}
        )
        for key, payload in extra.items():
            (path / key).write_bytes(payload)
            companions[key] = {
                "path": str((path / key).relative_to(root)),
                "sha256": runner.diag.sha(payload),
            }
        states.append(
            {
                "name": name,
                "parent_case": "validation"
                if name.startswith("validation")
                else "development",
                "time": when,
                "input": str((path / "input.bin").relative_to(root)),
                "input_sha256": runner.diag.sha(wire),
                "Y_sha256": runner.diag.sha(wire[2608:3888]),
                "companions": companions,
            }
        )
        target = root / "reference-baselines" / name
        target.mkdir(parents=True)
        (target / "baseline-001.bin").write_bytes(baseline_bytes(runner, wire))
        baseline_hashes[name] = runner.digest(target / "baseline-001.bin")
        references[name] = {
            "path": str((target / "baseline-001.bin").relative_to(root)),
            "sha256": baseline_hashes[name],
        }
        payloads = {
            "used-maps.bin": maps_bytes(runner),
            "species.bin": wire[48:2608],
            "diagnostic-ieee.bin": struct.pack("<11q", 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1),
        }
        controls[name], files = {}, {}
        for key, payload in payloads.items():
            (target / key).write_bytes(payload)
            identity = runner.diag.sha(payload)
            controls[name][key] = {
                "path": str((target / key).relative_to(root)),
                "sha256": identity,
            }
            files[key] = {"sha256": identity, "bytes": len(payload)}
        old_attempts.append({"name": name + "-repeat-3", "files": files})
    old_prepared = {"source_commit": runner.D038_SOURCE_COMMIT}
    write_json(root / "reference-records/prepared.json", old_prepared)
    write_json(
        root / "reference-records/campaign.json",
        {"complete": True, "stage_a_pass": True, "attempts": old_attempts},
    )
    monkeypatch.setattr(
        runner,
        "D038_PREPARED_SHA256",
        runner.digest(root / "reference-records/prepared.json"),
    )
    monkeypatch.setattr(
        runner,
        "D038_CAMPAIGN_SHA256",
        runner.digest(root / "reference-records/campaign.json"),
    )
    monkeypatch.setattr(runner, "BASELINE_SHA256", baseline_hashes)
    first_steps, standard_hashes, tight_hashes = {}, {}, {}
    for case in runner.STANDARD_SHA256:
        first_steps[case] = {}
        for stage in ("standard", "tight"):
            data = wire_input(mode=1)
            if stage == "tight":
                data = runner.tight_input(data)
            path = root / "inputs" / (case + "-" + stage + "-L0.bin")
            path.write_bytes(data)
            identity = runner.diag.sha(data)
            first_steps[case][stage] = {
                "path": str(path.relative_to(root)),
                "sha256": identity,
            }
            (standard_hashes if stage == "standard" else tight_hashes)[case] = identity
    monkeypatch.setattr(runner, "STANDARD_SHA256", standard_hashes)
    monkeypatch.setattr(runner, "TIGHT_SHA256", tight_hashes)
    write_json(
        root / "annex.json",
        {
            "states": [
                {
                    **s,
                    "companions": {n: c["sha256"] for n, c in s["companions"].items()},
                }
                for s in states
            ]
        },
    )
    (root / "DIAGNOSTIC_PROTOCOL.md").write_bytes(b"D038 public protocol")
    (root / "ASSEMBLY_QUALIFICATION_PROTOCOL.md").write_bytes(b"D039 public protocol")
    monkeypatch.setattr(runner.diag, "ANNEX_SHA256", runner.digest(root / "annex.json"))
    monkeypatch.setattr(
        runner.diag, "PROTOCOL_SHA256", runner.digest(root / "DIAGNOSTIC_PROTOCOL.md")
    )
    monkeypatch.setattr(
        runner,
        "PROTOCOL_SHA256",
        runner.digest(root / "ASSEMBLY_QUALIFICATION_PROTOCOL.md"),
    )
    for name, source in (
        ("assembly_campaign.py", Path(runner.__file__)),
        ("diagnostic_campaign.py", Path(runner.diag.__file__)),
        ("campaign.py", Path(runner.common.__file__)),
    ):
        (root / name).write_bytes(source.read_bytes())
    (root / "assembly_arithmetic.py").write_text(GATE_FIXTURE)
    for name in ("arithmetic.py", "reference.py"):
        (root / "rhs_reference").mkdir(exist_ok=True)
        (root / "rhs_reference" / name).write_text("# public dependency fixture\n")
    record = {
        "schema": "crucible.phase2d.assembly-prepared.v1",
        "protocol_sha256": runner.PROTOCOL_SHA256,
        "numerical_source": runner.SOURCE_NAME,
        "annex_sha256": runner.diag.ANNEX_SHA256,
        "diagnostic_protocol_sha256": runner.diag.PROTOCOL_SHA256,
        "diagnostic_source": {
            "source_commit": runner.D038_SOURCE_COMMIT,
            "prepared_sha256": runner.D038_PREPARED_SHA256,
            "campaign_sha256": runner.D038_CAMPAIGN_SHA256,
            "raw_archive_sha256": runner.D038_ARCHIVE_SHA256,
            "archive_checked": False,
        },
        "states": states,
        "reference_baselines": references,
        "reference_controls": controls,
        "first_step_inputs": first_steps,
        "attempts": runner.fixed_plan(states, first_steps),
        "immutable_files": {},
    }
    record["immutable_files"] = {
        str(p.relative_to(root)): runner.digest(p)
        for p in root.rglob("*")
        if p.is_file() and ("bundle" not in p.parts or p.name == "source-manifest.json")
    }
    write_json(root / "prepared.json", record)
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    monkeypatch.setattr(runner.platform, "platform", lambda: "public synthetic host")
    return root, record


def install_fake(runner, monkeypatch, *, defect=None):
    launched, fixtures = [], []

    def fake(command, *, cwd, stdout, stderr):
        executable, name = Path(command[-2]).name, command[-1]
        if executable != "trajectory_driver":
            fixtures.append((executable, name))
            if executable == "trajectory_synthetic":
                failures = {
                    "failed-lu": "FAILURE LAPACK dgetrf info=1",
                    "nonfinite": "FAILURE nonfinite computed physical F/assembly workspace",
                }
                status = failures.get(name, "SUCCESS")
                (cwd / "status.txt").write_text(status + "\n")
                return SimpleNamespace(returncode=int(name in failures))
            forcing = (
                {
                    "outside": "Forcing outside closed coverage",
                    "nonfinite": "Nonfinite forcing time",
                    "nonincreasing": "Nonincreasing forcing",
                }
                if executable == "forcing_synthetic"
                else {}
            )
            (cwd / "fixture-status.txt").write_text(
                "PASS\n"
                if not (
                    defect == "precision"
                    and executable == "assembly_synthetic"
                    and name == "precision"
                )
                else "FAILURE\n"
            )
            if executable == "assembly_synthetic" and name == "precision":
                (cwd / "raw-proof.txt").write_text(
                    "WRONG" if defect == "precision-raw" else "EXACT"
                )
            if name in forcing:
                stdout.write(forcing[name].encode())
            return SimpleNamespace(returncode=1 if name in forcing else 0)
        launched.append((cwd.name, name, tuple(command)))
        if defect == "interrupt":
            stdout.write(b"retained interrupted bytes\n")
            raise KeyboardInterrupt()
        first_step = name == "assembly-step"
        outcome = (
            "ordinary"
            if defect == "ordinary-standard"
            and cwd.name == "development-standard"
            or defect == "ordinary-tight"
            and cwd.name == "development-tight"
            else "pass"
        )
        if defect == "forensic" and cwd.name == "development-standard":
            outcome = "fatal"
        status = (
            "FAILURE first native step failed"
            if outcome in ("ordinary", "fatal")
            else "SUCCESS"
        )
        (cwd / "status.txt").write_text(status + "\n")
        write_json(
            cwd / "science.json",
            {
                "arithmetic": not (defect == "arithmetic" and len(launched) == 1),
                "directional": not (
                    defect == "directional" and cwd.name.endswith("-derivative")
                ),
                "fatal": defect == "derivative-fatal"
                and cwd.name.endswith("-derivative"),
                "outcome": outcome,
            },
        )
        count = 3 if name == "assembly-repeat-3" else 1
        wire = (cwd / "input.bin").read_bytes()
        if not first_step:
            (cwd / "species.bin").write_bytes(wire[48:2608])
            (cwd / "used-maps.bin").write_bytes(maps_bytes(runner))
            for i in range(1, count + 1):
                (cwd / f"baseline-{i:03}.bin").write_bytes(
                    baseline_bytes(runner, wire, i)
                )
            (cwd / "diagnostic-ieee.bin").write_bytes(
                b"".join(
                    struct.pack("<11q", i, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1)
                    for i in range(1, count + 1)
                )
            )
            (cwd / "diagnostic-evaluations.bin").write_bytes(bytes(count * 324 * 8))
        if outcome == "ordinary":
            (cwd / "failure-forensics.bin").write_bytes(b"retained scientific failure")
        counters = dict.fromkeys(runner.diag.COUNTERS, 0)
        counters.update(
            {k: count for k in ("rhs", "coefficient", "eos", "screening", "weak")}
        )
        write_json(cwd / "counters.json", counters)
        write_json(
            cwd / "assembly-counters.json",
            {
                "schema": "crucible.assembly-counters.v1",
                "fresh_requests": runner.MAX_RHS + 1 if defect == "scope" else count,
                "rhs": count,
                "assembly_calls": count,
            },
        )
        return SimpleNamespace(returncode=1 if status.startswith("FAILURE") else 0)

    monkeypatch.setattr(runner.common.subprocess, "run", fake)
    return launched, fixtures


def test_all_thirteen_and_all_precision_fixtures_follow_fixed_stages(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched, fixtures = install_fake(runner, monkeypatch)
    result = runner.execute(root)
    assert result["complete"] and result["qualification_pass"]
    assert (
        result["guarded_fresh_requests"] == result["physical_rhs_calls"] == 19
        and result["call_accounting_complete"]
    )
    assert [c for _, c, _ in launched] == ["assembly-repeat-3"] * 3 + [
        "assembly-repeat-1"
    ] * 3 + ["assembly-diagnose"] * 3 + ["assembly-step"] * 4
    assert len(fixtures) == 16 and len(result["attempts"]) == 13
    assert [name for exe, name in fixtures if exe == "assembly_synthetic"] == [
        "precision",
        "arithmetic",
        "malformed",
        "nonfinite",
        "overflow",
    ]
    assert all(len(command) == 2 for _, _, command in launched)
    assert all(not a["companions"] for a in result["attempts"])
    with pytest.raises(ValueError, match="restart"):
        runner.execute(root)


def test_native_success_does_not_bypass_arithmetic_gate(prepared, runner, monkeypatch):
    root, _ = prepared
    launched, _ = install_fake(runner, monkeypatch, defect="arithmetic")
    with pytest.raises(ValueError, match="arithmetic attempt gate"):
        runner.execute(root)
    assert len(launched) == 1
    result = json.loads((root / "campaign.json").read_text())
    assert result["attempts"][0]["returncode"] == 0
    assert not result["complete"] and all(
        a["status"] == "UNATTEMPTED" for a in result["attempts"][1:]
    )


def test_directional_failure_completes_three_states_but_starts_no_steps(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched, _ = install_fake(runner, monkeypatch, defect="directional")
    result = runner.execute(root)
    assert (
        len(launched) == 9 and result["complete"] and not result["qualification_pass"]
    )
    assert all(
        a["status"] == "CONDITIONALLY_UNATTEMPTED" for a in result["attempts"][9:]
    )
    assert all(
        a["skip_reason"] == "DERIVATIVE_GATES_FAILED" for a in result["attempts"][9:]
    )


@pytest.mark.parametrize("defect", ["ordinary-standard", "ordinary-tight"])
def test_ordinary_nonlinear_failure_retains_other_case_and_conditions_tight(
    prepared, runner, monkeypatch, defect
):
    root, _ = prepared
    launched, _ = install_fake(runner, monkeypatch, defect=defect)
    result = runner.execute(root)
    assert result["complete"] and not result["qualification_pass"]
    assert len(launched) == (11 if defect.endswith("standard") else 13)
    failed = next(
        a
        for a in result["attempts"]
        if a.get("science_gate", {}).get("ordinary_numerical_failure")
    )
    assert (
        failed["returncode"] == 1
        and (root / "attempts" / failed["name"] / "failure-forensics.bin").is_file()
    )
    if defect.endswith("standard"):
        assert result["attempts"][10]["qualification_pass"]
        assert all(
            a["status"] == "CONDITIONALLY_UNATTEMPTED" for a in result["attempts"][11:]
        )
    else:
        assert result["attempts"][-1]["qualification_pass"]


@pytest.mark.parametrize(
    "defect,expected",
    [
        ("forensic", 10),
        ("derivative-fatal", 7),
        ("precision", 0),
        ("precision-raw", 0),
        ("scope", 1),
    ],
)
def test_fatal_or_precision_failure_stops_remaining_physical_plan(
    prepared, runner, monkeypatch, defect, expected
):
    root, _ = prepared
    launched, _ = install_fake(runner, monkeypatch, defect=defect)
    with pytest.raises(ValueError):
        runner.execute(root)
    assert len(launched) == expected
    result = json.loads((root / "campaign.json").read_text())
    assert not result["complete"] and result["attempts"][-1]["status"] == "UNATTEMPTED"


def test_interrupt_retains_partial_and_all_thirteen_statuses(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    install_fake(runner, monkeypatch, defect="interrupt")
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    result = json.loads((root / "campaign.json").read_text())
    assert (
        len(result["attempts"]) == 13
        and result["attempts"][0]["status"] == "INTERRUPTED"
    )
    assert not result["attempts"][0]["completed"]
    assert (
        root / "attempts" / result["attempts"][0]["name"] / "process.log"
    ).read_bytes() == b"retained interrupted bytes\n"


@pytest.mark.parametrize(
    "change", ["command", "input", "gate-source", "baseline", "precision-executable"]
)
def test_identity_mutation_refuses_before_physical_process(
    prepared, runner, monkeypatch, change
):
    root, record = prepared
    launched, _ = install_fake(runner, monkeypatch)
    if change == "command":
        record["attempts"][0]["arguments"] = ["continue-10ms"]
        write_json(root / "prepared.json", record)
    else:
        target = {
            "input": record["attempts"][0]["input"],
            "gate-source": "assembly_arithmetic.py",
            "baseline": record["reference_baselines"][runner.diag.STATES[0]]["path"],
            "precision-executable": "bundle/assembly_synthetic",
        }[change]
        (root / target).write_bytes(b"changed identity")
    with pytest.raises(ValueError):
        runner.execute(root)
    assert not launched


def test_tight_derivation_changes_only_the_declared_sixteen_bytes(runner):
    original = wire_input(mode=1)
    tight = runner.tight_input(original)
    assert tight[:32] == original[:32] and tight[48:] == original[48:]
    assert struct.unpack_from("<2d", tight, 32) == (1e-14, 1e-12)
    with pytest.raises(ValueError):
        runner.tight_input(tight)


def test_offline_prepare_preserves_helper_history_and_derives_only_tight_controls(
    prepared, runner, monkeypatch, tmp_path
):
    import shutil

    import numpy as np

    from crucible import trajectory_reference as ref

    root, existing = prepared
    source = tmp_path / "source"
    public = source / "experiments/trajectory_reference"
    public.mkdir(parents=True)
    for name, module in (
        ("assembly_campaign.py", runner),
        ("diagnostic_campaign.py", runner.diag),
        ("campaign.py", runner.common),
    ):
        (public / name).write_bytes(Path(module.__file__).read_bytes())
    (public / "assembly_arithmetic.py").write_text(GATE_FIXTURE)
    (public / "ASSEMBLY_QUALIFICATION_PROTOCOL.md").write_bytes(
        (root / "ASSEMBLY_QUALIFICATION_PROTOCOL.md").read_bytes()
    )
    (public.parent / "rhs_reference").mkdir()
    for name in ("arithmetic.py", "reference.py"):
        (public.parent / "rhs_reference" / name).write_text(
            "# public dependency fixture\n"
        )
    previous = tmp_path / "previous-diagnostic"
    previous.mkdir()
    for name in ("prepared.json", "campaign.json"):
        shutil.copy2(root / "reference-records" / name, previous / name)
    for state in runner.diag.STATES:
        shutil.copytree(
            root / "reference-baselines" / state,
            previous / "attempts" / (state + "-repeat-3"),
        )
    species = np.array(
        [(0, 1), (1, 1)] + [(a // 2, a) for a in range(2, 160)], dtype=np.int64
    )
    y = np.zeros(160)
    y[:2] = [0.1, 0.3]
    case = {
        "Y0": y,
        "species_Z_A": species,
        "source_time": np.array([0.0, 0.01]),
        "time": np.array([0.0, 0.01]),
        "T9": np.ones(2),
        "rho": np.full(2, 1e6),
        "requested_time": np.array([0.0, 0.01]),
    }
    standard = ref.wire_input(case, mode=1, mesh=ref.nested_mesh(case, 0))
    identity = runner.diag.sha(standard)
    monkeypatch.setattr(
        runner,
        "STANDARD_SHA256",
        dict.fromkeys(("development", "validation"), identity),
    )
    monkeypatch.setattr(
        runner,
        "TIGHT_SHA256",
        dict.fromkeys(
            ("development", "validation"), runner.diag.sha(runner.tight_input(standard))
        ),
    )
    originals = tmp_path / "original-inputs"
    originals.mkdir()
    for label in runner.STANDARD_SHA256:
        (originals / (label + ".bin")).write_bytes(standard)
    config = {
        "trajectory_prepare_config": "public helper config",
        "diagnostic_root": str(previous),
        "standard_inputs": {
            label: str(originals / (label + ".bin")) for label in runner.STANDARD_SHA256
        },
    }
    write_json(tmp_path / "prepare-config.json", config)
    helper_calls = []

    def offline_helper(config_path, annex_path, destination, source_root):
        # This unit test isolates only the new preparation wrapper. The accepted
        # helper's real qualified-loader and frozen-wire checks have their own
        # end-to-end public test in test_trajectory_diagnostic_campaign.py.
        helper_calls.append((config_path, annex_path))
        destination.mkdir()
        shutil.copytree(root / "inputs", destination / "inputs")
        for label in runner.STANDARD_SHA256:
            np.savez(destination / "inputs" / (label + ".npz"), **case)
        for name in (
            "annex.json",
            "DIAGNOSTIC_PROTOCOL.md",
            "diagnostic_campaign.py",
            "campaign.py",
        ):
            shutil.copy2(root / name, destination / name)
        (destination / "bundle").mkdir()
        (destination / "bundle/source-manifest.json").write_text("{}\n")
        result = {
            "schema": "crucible.phase2d.diagnostic-prepared.v1",
            "source_commit": "new-committed-source",
            "source_tree": "new-committed-tree",
            "states": existing["states"],
            "attempts": runner.diag.fixed_plan(existing["states"]),
            "costs": {},
            "annex_sha256": runner.diag.ANNEX_SHA256,
        }
        write_json(destination / "prepared.json", result)
        return result

    monkeypatch.setattr(runner.diag, "prepare", offline_helper)
    before = {
        str(p): runner.digest(p)
        for parent in (previous, originals)
        for p in parent.rglob("*")
        if p.is_file()
    }
    destination = tmp_path / "new-assembly-preparation"
    result = runner.prepare(
        tmp_path / "prepare-config.json", root / "annex.json", destination, source
    )
    assert helper_calls == [("public helper config", root / "annex.json")]
    assert (
        result["schema"] == "crucible.phase2d.assembly-prepared.v1"
        and len(result["attempts"]) == 13
    )
    history = result["input_preparation_history"]
    assert history["status"] == "OFFLINE_HELPER_ONLY_NINE_PLANS_NOT_EXECUTED"
    old = json.loads((destination / history["path"]).read_text())
    assert (
        old["schema"] == "crucible.phase2d.diagnostic-prepared.v1"
        and len(old["attempts"]) == 9
    )
    assert old["source_commit"] == result["source_commit"] == "new-committed-source"
    runner.validate_prepared(destination, result)
    for label in runner.STANDARD_SHA256:
        standard_path = (
            destination / result["first_step_inputs"][label]["standard"]["path"]
        )
        tight_path = destination / result["first_step_inputs"][label]["tight"]["path"]
        assert standard_path.read_bytes() == standard
        assert tight_path.read_bytes() == runner.tight_input(standard)
    assert {
        str(p): runner.digest(p)
        for parent in (previous, originals)
        for p in parent.rglob("*")
        if p.is_file()
    } == before


def test_cached_original_eleven_fixtures_cannot_qualify_new_source(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched, _ = install_fake(runner, monkeypatch)
    runner.common.synthetic_checks(
        root, extra_scenarios=(("trajectory_synthetic", "retry-snapshot", None),)
    )
    with pytest.raises(ValueError, match="prerequisite population differs"):
        runner.execute(root)
    assert not launched
    result = json.loads((root / "campaign.json").read_text())
    assert not result["complete"] and all(
        a["status"] == "UNATTEMPTED" for a in result["attempts"]
    )
