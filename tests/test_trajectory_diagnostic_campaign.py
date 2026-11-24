"""Public binary/process oracles: no producer, compiler, SSH or private inputs."""

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
        / "experiments/trajectory_reference/diagnostic_campaign.py"
    )
    spec = importlib.util.spec_from_file_location("test_diagnostic_runner", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path, value):
    path.write_text(json.dumps(value) + "\n")


def maps_bytes(runner):
    # Independently form one extended range on species 1; remaining ranges empty.
    la, le = [], []
    for species in range(160):
        la.extend(1 if species == 0 else n + 1 for n in runner.NB)
        le.extend(runner.NB)
    out = struct.pack("<1280i", *(la + le))
    for order, (nc, nb) in enumerate(zip(runner.NC, runner.NB), 1):
        out += struct.pack("<3i", order, nc, nb)
        out += bytes((5 if order == 1 else 6) * nc * 4)
        out += struct.pack("<" + str(2 * nb) + "i", *([1] * (2 * nb)))
        out += struct.pack("<" + str(nb) + "d", *([1.0] * nb))
    return out


def baseline_bytes(runner, input_data, call=1, wrong_echo=False, wrong_f=False):
    echo = runner.input_echo(input_data)
    when, temp, rho = struct.unpack("<3d", echo["time_T9_rho"])
    y = struct.unpack("<160d", echo["Y"])
    values = [float(call), when, temp, rho, 1.0, 0.5, 0.5, 2.0, 3.0, 4.0]
    values += list(y) + [2.0 if wrong_f else 1.0] * 160
    values += [0.25] * (sum(runner.NC) + sum(runner.NB))
    if wrong_echo:
        values[2] += 1
    return (
        struct.pack("<12i", 0x43524442, 1, 160, *runner.NC, *runner.NB, 10240)
        + struct.pack("<" + str(len(values)) + "d", *values)
        + bytes(10240 * 4)
    )


@pytest.fixture
def prepared(tmp_path, runner, monkeypatch):
    root = tmp_path
    bundle = root / "bundle"
    bundle.mkdir()
    (bundle / "network").mkdir()
    (bundle / "helm_table.dat").write_bytes(b"synthetic table")
    (bundle / "source-manifest.json").write_text("{}\n")
    for name, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
    ):
        (bundle / name).write_bytes(("fake " + name).encode())
        (bundle / receipt).write_text(runner.digest(bundle / name) + "  " + name + "\n")
    lib = tmp_path / "fake-library"
    lib.write_bytes(b"public library identity")
    write_json(bundle / "linked-library-hashes.json", {str(lib): runner.digest(lib)})
    states = []
    z, a, y = [0.0] * 160, [1.0] * 160, [0.0] * 160
    y[0] = 1.0
    for name in runner.STATES:
        path = root / "inputs" / name
        path.mkdir(parents=True)
        when = 1.953125e-7 if name == runner.STATES[2] else 0.0
        raw = struct.pack("<8i2d", 0x43524432, 1, 160, 2, 1, 1, 0, 1, 1e-13, 1e-11)
        values = z + a + y + [0.0, 0.01] + [1.0, 1.0] + [1e6, 1e6] + [when, when]
        raw += struct.pack("<" + str(len(values)) + "d", *values)
        (path / "input.bin").write_bytes(raw)
        companions = {}
        if name == runner.STATES[2]:
            extra = {
                "old-state.bin": struct.pack("<160d", *y),
                "frozen-h.bin": struct.pack("<d", when),
            }
        else:
            extra = {"expected-control.bin": struct.pack("<160d", *([1.0] * 160))}
        for companion, data in extra.items():
            (path / companion).write_bytes(data)
            companions[companion] = {
                "path": str((path / companion).relative_to(root)),
                "sha256": runner.sha(data),
            }
        states.append(
            {
                "name": name,
                "parent_case": "validation"
                if name.startswith("validation")
                else "development",
                "time": when,
                "input": str((path / "input.bin").relative_to(root)),
                "input_sha256": runner.sha(raw),
                "Y_sha256": runner.sha(struct.pack("<160d", *y)),
                "companions": companions,
            }
        )
    for name, source in (
        ("campaign.py", Path(runner.common.__file__)),
        ("diagnostic_campaign.py", Path(runner.__file__)),
    ):
        (root / name).write_bytes(source.read_bytes())
    annex_states = [
        {
            **state,
            "companions": {
                name: entry["sha256"] for name, entry in state["companions"].items()
            },
        }
        for state in states
    ]
    write_json(root / "annex.json", {"states": annex_states})
    (root / "DIAGNOSTIC_PROTOCOL.md").write_bytes(b"public synthetic protocol")
    monkeypatch.setattr(runner, "ANNEX_SHA256", runner.digest(root / "annex.json"))
    monkeypatch.setattr(
        runner, "PROTOCOL_SHA256", runner.digest(root / "DIAGNOSTIC_PROTOCOL.md")
    )
    record = {
        "schema": "crucible.phase2d.diagnostic-prepared.v1",
        "protocol_sha256": runner.PROTOCOL_SHA256,
        "annex_sha256": runner.ANNEX_SHA256,
        "states": states,
        "attempts": runner.fixed_plan(states),
        "immutable_files": {},
    }
    record["immutable_files"] = {
        str(p.relative_to(root)): runner.digest(p)
        for p in root.rglob("*")
        if p.is_file() and ("bundle" not in p.parts or p.name == "source-manifest.json")
    }
    write_json(root / "prepared.json", record)
    monkeypatch.setattr(runner.platform, "platform", lambda: "public synthetic host")
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    return root, record


def install_fake(runner, monkeypatch, *, defect=None):
    launched = []

    def fake(command, *, cwd, stdout, stderr):
        executable = Path(command[0]).name
        name = command[-1]
        if executable != "trajectory_driver":
            trajectory = executable == "trajectory_synthetic"
            failures = {
                "failed-lu": "FAILURE LAPACK dgetrf info=1",
                "nonfinite": "FAILURE nonfinite computed physical F/assembly workspace",
            }
            forcing = {
                "outside": "Forcing outside closed coverage",
                "nonfinite": "Nonfinite forcing time",
                "nonincreasing": "Nonincreasing forcing",
            }
            failed = name in (failures if trajectory else forcing)
            if not (defect == "fixture" and name == "retry-snapshot"):
                (
                    cwd / ("status.txt" if trajectory else "fixture-status.txt")
                ).write_text(
                    (failures.get(name, "SUCCESS") if trajectory else "PASS") + "\n"
                )
            if failed:
                stdout.write((failures[name] if trajectory else forcing[name]).encode())
            return SimpleNamespace(returncode=1 if failed else 0)
        launched.append((cwd.name, name))
        if defect == "interrupt":
            stdout.write(b"retained partial process\n")
            raise KeyboardInterrupt()
        (cwd / "status.txt").write_text(
            "FAILURE public runtime\n" if defect == "runtime" else "SUCCESS\n"
        )
        count = 3 if name == "repeat-3" else 1
        raw = (cwd / "input.bin").read_bytes()
        (cwd / "species.bin").write_bytes(raw[48:2608])
        mapping = maps_bytes(runner)
        if defect == "state-maps" and cwd.name.startswith(runner.STATES[1]):
            mapping = mapping[:-8] + struct.pack("<d", 2.0)
        (cwd / "used-maps.bin").write_bytes(mapping)
        for i in range(1, count + 1):
            (cwd / f"baseline-{i:03}.bin").write_bytes(
                baseline_bytes(
                    runner,
                    raw,
                    i,
                    wrong_echo=defect == "echo",
                    wrong_f=defect == "F"
                    or (defect == "C-change" and name == "diagnose"),
                )
            )
        (cwd / "diagnostic-ieee.bin").write_bytes(
            b"".join(
                struct.pack("<11q", i, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1)
                for i in range(1, count + 1)
            )
        )
        (cwd / "diagnostic-evaluations.bin").write_bytes(bytes(count * 324 * 8))
        if defect == "IEEE-change" and count == 3:
            data = bytearray((cwd / "diagnostic-ieee.bin").read_bytes())
            struct.pack_into("<2q", data, 88 + 4 * 8, 0, 0)
            (cwd / "diagnostic-ieee.bin").write_bytes(data)
        if name == "diagnose":
            (cwd / "matrix-status.bin").write_bytes(
                b"".join(
                    struct.pack(
                        "<5d", f, i, 0 if defect == "incomplete" else 1, 0, count
                    )
                    for i, f in enumerate((0.1, 1.0, 10.0, 100.0), 1)
                )
            )
            for i in range(1, 5):
                (cwd / f"jacobian-factor-{i}.bin").write_bytes(
                    struct.pack("<25600d", *([float("nan")] * 25600))
                    if defect == "incomplete"
                    else bytes(25600 * 8)
                )
                if cwd.name.startswith(runner.STATES[2]) and defect != "incomplete":
                    (cwd / f"linear-factor-{i}.bin").write_bytes(
                        struct.pack("<5i", 0x4352444C, 1, 160, 0, 0)
                        + bytes(52001 * 8 + 160 * 4)
                    )
            for filename, width, nrows in (
                ("fd-probe-attempts.bin", 12, 0),
                ("fd-columns.bin", 6, 0),
                ("jacobian-bases.bin", 164, 4),
                ("directional.bin", 1286, 27),
                ("diagnostic-jv.bin", 1920, 1),
                ("direction-attempts.bin", 327, 0),
                ("fixed-b-jacobian.bin", 25600, 1),
            ):
                (cwd / filename).write_bytes(bytes(width * nrows * 8))
            (cwd / "candidate-status.txt").write_text(
                "REFUSED public domain reason\n"
                if cwd.name.startswith(runner.STATES[2])
                else "SKIPPED no frozen linear state\n"
            )
            if defect == "incomplete":
                (cwd / "candidate-status.txt").write_text(
                    "SKIPPED incomplete factor-one\n"
                )
            if cwd.name.startswith(runner.STATES[2]) and defect != "incomplete":
                (cwd / "candidate-refused.bin").write_bytes(bytes(163 * 8))
            if defect == "missing-C":
                (cwd / "directional.bin").unlink()
        newton = (
            name == "diagnose"
            and cwd.name.startswith(runner.STATES[2])
            and defect != "incomplete"
        )
        counters = dict.fromkeys(runner.COUNTERS, 0)
        counters.update(
            {k: count for k in ("rhs", "coefficient", "eos", "screening", "weak")}
        )
        counters.update(
            jacobian=4 if name == "diagnose" else 0,
            lu=4 if newton else 0,
            linear_solve=4 if newton else 0,
        )
        write_json(cwd / "counters.json", counters)
        if defect == "status":
            (cwd / "status.txt").unlink()
        return SimpleNamespace(returncode=17 if defect == "runtime" else 0)

    monkeypatch.setattr(runner.common.subprocess, "run", fake)
    return launched


def test_fixed_plan_all_six_A_before_any_C_and_no_advance(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch)
    result = runner.execute(root)
    assert result["complete"] and result["stage_a_pass"]
    assert [c for _, c in launched] == ["repeat-3"] * 3 + ["repeat-1"] * 3 + [
        "diagnose"
    ] * 3
    assert result["physical_rhs_calls"] == 15
    assert len(result["synthetic"]["scenarios"]) == 11
    assert all(not list((root / "attempts" / n).glob("accepted*")) for n, _ in launched)
    newton = root / "attempts" / (runner.STATES[2] + "-diagnose")
    assert (newton / "old-state.bin").is_file() and (newton / "frozen-h.bin").is_file()
    assert not (
        root / "attempts" / (runner.STATES[2] + "-repeat-3") / "old-state.bin"
    ).exists()
    with pytest.raises(ValueError, match="restart"):
        runner.execute(root)


@pytest.mark.parametrize(
    "defect", ["status", "echo", "F", "runtime", "fixture", "state-maps", "IEEE-change"]
)
def test_failed_precondition_prevents_C_and_retains_all_planned(
    prepared, runner, monkeypatch, defect
):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch, defect=defect)
    with pytest.raises(ValueError):
        runner.execute(root)
    assert not any(c == "diagnose" for _, c in launched)
    result = json.loads((root / "campaign.json").read_text())
    assert not result["complete"] and not result["stage_a_pass"]
    assert len(result["attempts"]) == 9
    assert result["attempts"][-1]["status"] == "UNATTEMPTED"
    if defect == "runtime":
        assert result["attempts"][0]["returncode"] == 17
        assert (
            (root / "attempts" / result["attempts"][0]["name"] / "status.txt")
            .read_text()
            .startswith("FAILURE")
        )


def test_C_baseline_change_stops_before_next_state(prepared, runner, monkeypatch):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch, defect="C-change")
    with pytest.raises(ValueError):
        runner.execute(root)
    assert len(launched) == 7
    result = json.loads((root / "campaign.json").read_text())
    assert result["stage_a_pass"] and result["attempts"][7]["status"] == "UNATTEMPTED"


def test_interrupt_retains_partial_attempt_and_unattempted_plan(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    install_fake(runner, monkeypatch, defect="interrupt")
    with pytest.raises(KeyboardInterrupt):
        runner.execute(root)
    result = json.loads((root / "campaign.json").read_text())
    assert result["attempts"][0]["status"] == "INTERRUPTED"
    assert not result["attempts"][0]["completed"]
    assert all(a["status"] == "UNATTEMPTED" for a in result["attempts"][1:])
    assert (
        root / "attempts" / result["attempts"][0]["name"] / "process.log"
    ).read_bytes() == b"retained partial process\n"


@pytest.mark.parametrize("change", ["command", "input", "executable"])
def test_changed_identity_or_unknown_command_refused_before_process(
    prepared, runner, monkeypatch, change
):
    root, record = prepared
    launched = install_fake(runner, monkeypatch)
    if change == "command":
        record["attempts"][0]["arguments"] = ["advance"]
        write_json(root / "prepared.json", record)
    elif change == "input":
        (root / record["states"][0]["input"]).write_bytes(b"changed")
    else:
        (root / "bundle/trajectory_driver").write_bytes(b"changed")
    with pytest.raises(ValueError):
        runner.execute(root)
    assert not launched


def test_stale_original_ten_synthetic_results_cannot_satisfy_eleven(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch)
    runner.common.synthetic_checks(root)
    with pytest.raises(ValueError, match="population differs"):
        runner.execute(root)
    assert not launched


def test_baseline_parser_exact_layout_and_refusal_before_unbounded_unpack(
    prepared, runner
):
    root, record = prepared
    raw = baseline_bytes(runner, (root / record["states"][0]["input"]).read_bytes(), 3)
    actual = runner.parse_baseline(raw)
    assert (
        actual["call_id"] == 3 and actual["Y"][0] == 1 and actual["F"] == (1.0,) * 160
    )
    assert (
        tuple(map(len, actual["csect"])) == runner.NC
        and tuple(map(len, actual["b"])) == runner.NB
    )
    for bad in (raw[:-1], raw + b"x", struct.pack("<i", 0) + raw[4:]):
        with pytest.raises(ValueError):
            runner.parse_baseline(bad)
    broken = bytearray(raw)
    struct.pack_into("<i", broken, 28, 2**31 - 1)
    with pytest.raises(ValueError, match="header differs"):
        runner.parse_baseline(broken)


def test_ieee_fatal_flags_rejected_and_underflow_retained(runner):
    valid = [1, 1, 1, 0, -1, -1, 0, 0, 0, 1, 1]
    assert runner.ieee_rows(struct.pack("<11q", *valid))[0][-2:] == (1, 1)
    for index in (1, 2, 6, 7, 8):
        row = valid.copy()
        row[index] = 0 if index < 3 else 1
        with pytest.raises(ValueError):
            runner.ieee_rows(struct.pack("<11q", *row))


def test_offline_prepare_rechecks_qualified_origins_and_rewires_exact_frozen_states(
    tmp_path, runner, monkeypatch
):
    import io

    import numpy as np

    from crucible import benchmark
    from crucible import trajectory_reference as ref

    source, original, destination = (
        tmp_path / "source",
        tmp_path / "original",
        tmp_path / "prepared",
    )
    source_dir = source / "experiments/trajectory_reference"
    source_dir.mkdir(parents=True)
    original.mkdir()
    (source / "src/crucible").mkdir(parents=True)
    (source / "src/crucible/trajectory_reference.py").write_bytes(
        Path(ref.__file__).read_bytes()
    )
    for name, path in (
        ("diagnostic_campaign.py", Path(runner.__file__)),
        ("campaign.py", Path(runner.common.__file__)),
    ):
        (source_dir / name).write_bytes(path.read_bytes())
    (source_dir / "stage_native.py").write_text(
        'def stage(config, destination):\n    destination.mkdir()\n    (destination / "source-manifest.json").write_text("{}\\n")\n'
    )
    (source_dir / "PROTOCOL.md").write_bytes(b"original protocol")
    (source_dir / "DIAGNOSTIC_PROTOCOL.md").write_bytes(b"diagnostic protocol")
    monkeypatch.setattr(ref, "PROTOCOL_SHA256", runner.sha(b"original protocol"))
    monkeypatch.setattr(runner, "PROTOCOL_SHA256", runner.sha(b"diagnostic protocol"))
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
    payload = io.BytesIO()
    np.savez(payload, **case)
    (original / "case.npz").write_bytes(payload.getvalue())
    monkeypatch.setattr(
        ref,
        "INPUT_SHA256",
        dict.fromkeys(("development", "validation"), runner.sha(payload.getvalue())),
    )
    write_json(
        original / "old-annex.json",
        {
            "cases": {
                name: {
                    "npz": str(original / "case.npz"),
                    "role": name,
                    "initial_record": 12,
                }
                for name in ref.INPUT_SHA256
            }
        },
    )
    monkeypatch.setattr(ref, "ANNEX_SHA256", runner.digest(original / "old-annex.json"))
    calls = []

    def qualified(name, version, *, use, split, config):
        calls.append((name, version, use, split))
        return {
            "record_id": np.array([12]),
            "Y": y[None, :],
            "species_Z_A": species,
            "fresh_rhs": np.ones((1, 160)),
        }

    monkeypatch.setattr(benchmark, "load_benchmark", qualified)
    entries = []
    for name in runner.STATES:
        parent = "validation" if name.startswith("validation") else "development"
        when = 1.953125e-7 if name == runner.STATES[2] else 0.0
        state = y.copy()
        if when:
            state[0] += 1e-7
            monkeypatch.setattr(
                runner, "NEWTON_Y_SHA256", runner.sha(state.astype("<f8").tobytes())
            )
        path = original / name
        path.mkdir()
        raw = ref.wire_input(
            case, mode=0, mesh=np.array([when]), time=when, state=state
        )
        (path / "input.bin").write_bytes(raw)
        extras = (
            {
                "old-state.bin": y.astype("<f8").tobytes(),
                "frozen-h.bin": struct.pack("<d", when),
            }
            if when
            else {"expected-control.bin": np.ones(160, dtype="<f8").tobytes()}
        )
        for key, data in extras.items():
            (path / key).write_bytes(data)
        entries.append(
            {
                "name": name,
                "parent_case": parent,
                "source_input_npz_sha256": ref.INPUT_SHA256[parent],
                "time": when,
                "Y_sha256": runner.sha(state.astype("<f8").tobytes()),
                "input": str(path / "input.bin"),
                "input_sha256": runner.sha(raw),
                "companions": {key: runner.sha(data) for key, data in extras.items()},
            }
        )
    write_json(original / "annex.json", {"states": entries})
    monkeypatch.setattr(runner, "ANNEX_SHA256", runner.digest(original / "annex.json"))
    write_json(
        original / "config.json",
        {
            "annex": str(original / "old-annex.json"),
            "benchmark_access": "unused synthetic access",
            "source_config": "unused synthetic sources",
        },
    )

    def fake_git(command, **kwargs):
        assert command[0] == "git"
        return SimpleNamespace(
            stdout=""
            if command[1] == "status"
            else "frozen-source-commit\nfrozen-source-tree\n"
        )

    monkeypatch.setattr(runner.subprocess, "run", fake_git)
    before = {str(p): runner.digest(p) for p in original.rglob("*") if p.is_file()}
    result = runner.prepare(
        original / "config.json", original / "annex.json", destination, source
    )
    assert len(result["attempts"]) == 9 and all(
        s["mode"] == 0 for s in result["attempts"]
    )
    assert (
        result["source_commit"] == "frozen-source-commit"
        and result["source_tree"] == "frozen-source-tree"
    )
    assert [c[-1] for c in calls] == ["development", "validation"]
    assert {
        str(p): runner.digest(p) for p in original.rglob("*") if p.is_file()
    } == before
    runner.validate_prepared(destination, result)
    for entry in entries:
        assert (
            destination / "inputs" / entry["name"] / "input.bin"
        ).read_bytes() == Path(entry["input"]).read_bytes()


def test_incomplete_scientific_matrices_are_retained_and_other_states_attempted(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch, defect="incomplete")
    result = runner.execute(root)
    assert result["complete"] and len(launched) == 9
    assert all(a["native_counters"]["lu"] == 0 for a in result["attempts"])
    raw = (
        root / "attempts" / (runner.STATES[2] + "-diagnose") / "jacobian-factor-1.bin"
    ).read_bytes()
    assert raw == struct.pack("<25600d", *([float("nan")] * 25600))


def test_missing_required_C_stream_stops_with_remaining_states_visible(
    prepared, runner, monkeypatch
):
    root, _ = prepared
    launched = install_fake(runner, monkeypatch, defect="missing-C")
    with pytest.raises(ValueError, match="missing diagnostic output directional.bin"):
        runner.execute(root)
    assert len(launched) == 7
    result = json.loads((root / "campaign.json").read_text())
    assert not result["complete"] and result["attempts"][-1]["status"] == "UNATTEMPTED"
