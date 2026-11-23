"""Public provenance tests; physical sources and compilers are not CI inputs.

The actual adapter's polynomial, nonlinear stiff BE and refusal checks live in
synthetic_native.f90 and run with its independent synthetic_modules.f90 closure
on the pinned compiler before any physical control is evaluated.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest


@pytest.fixture
def staging(tmp_path, monkeypatch):
    source = (
        Path(__file__).resolve().parents[1]
        / "experiments/trajectory_reference/stage_native.py"
    )
    spec = importlib.util.spec_from_file_location("trajectory_stage_test", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    public = tmp_path / "public" / "trajectory_reference"
    public.mkdir(parents=True)
    rhs = public.parent / "rhs_reference"
    rhs.mkdir()
    original = tmp_path / "original.dat"
    original.write_bytes(b"immutable synthetic network bytes\x00\xff")
    expected = {"network/synthetic": module.sha(original.read_bytes())}
    (rhs / "bindings.json").write_text(json.dumps({"files": expected}))
    for name in module.PUBLIC:
        (public / name).write_text("synthetic public asset " + name)
    # Supply a native source entry only to make the optional directory derivation
    # well-defined; the independent mocked closure still has an exact hash set.
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "files": {
                    "network/synthetic": {
                        "path": str(original),
                        "sha256": expected["network/synthetic"],
                    }
                }
            }
        )
    )
    monkeypatch.setattr(module, "HERE", public)
    monkeypatch.setattr(module, "EXTRA", {})
    return module, config, original


def test_stage_retains_original_bytes_and_manifest(staging, tmp_path):
    module, config, original = staging
    before = original.read_bytes()
    destination = tmp_path / "new-stage"
    result = module.stage(config, destination, native_source_dir=tmp_path)
    assert original.read_bytes() == before
    assert (destination / "original/network/synthetic").read_bytes() == before
    assert (destination / "network/synthetic").read_bytes() == before
    assert result == module.verify(destination)


def test_changed_original_refused_before_destination_creation(staging, tmp_path):
    module, config, original = staging
    original.write_bytes(b"changed synthetic input")
    destination = tmp_path / "must-not-exist"
    with pytest.raises(ValueError, match="hash mismatch"):
        module.stage(config, destination, native_source_dir=tmp_path)
    assert not destination.exists()


def test_staged_mutation_and_overwrite_refused(staging, tmp_path):
    module, config, _ = staging
    destination = tmp_path / "stage"
    module.stage(config, destination, native_source_dir=tmp_path)
    target = destination / "network/synthetic"
    target.chmod(0o644)
    target.write_bytes(b"same-shape or changed staged data must be detected")
    with pytest.raises(ValueError, match="bytes changed"):
        module.verify(destination)
    with pytest.raises(ValueError, match="immutable staging"):
        module.stage(config, destination, native_source_dir=tmp_path)


def test_unpinned_closure_member_refused(staging, tmp_path):
    module, config, original = staging
    record = json.loads(config.read_text())
    record["files"]["network/unapproved"] = {
        "path": str(original),
        "sha256": module.sha(original.read_bytes()),
    }
    config.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="pinned closure"):
        module.stage(config, tmp_path / "must-not-exist", native_source_dir=tmp_path)


def test_unrecognized_pinned_source_transform_fails_closed(staging):
    module, _, _ = staging
    with pytest.raises(ValueError, match="expected one occurrence"):
        module.adapt(
            "refs/producer/xnet_ffn.f90",
            "Module xnet_ffn\n! changed source\nEnd Module\n",
        )


NATIVE_SOURCE = (
    Path(__file__).resolve().parents[1]
    / "experiments/trajectory_reference/native_adapter.f90"
)


def _subroutine(source, name):
    return re.search(
        rf"^  subroutine {name}\(.*?^  end subroutine {name}$",
        source,
        re.MULTILINE | re.DOTALL,
    ).group()


def _assert_evaluated_snapshot_dataflow(source):
    """Static invariant only: no compiler, native fixture or physical source runs.

    Follow the actual Fortran capture assignments into the serialized prefix.
    A cleanup mutation must not become a snapshot's evaluated physical input.
    """
    fresh = _subroutine(source, "fresh")
    writer = _subroutine(source, "save_failure_workspace")
    captures = []
    for expression in (
        r"state",
        r"\[time,temp,density\]",
        r"\[yet\(1\),cv\(1\),etae\(1\),detaedt9\(1\)\]",
        r"iweak\(1\)",
    ):
        capture = re.search(rf"^    (\w+)\s*=\s*{expression}$", fresh, re.MULTILINE)
        assert capture is not None, f"Missing retained physical field: {expression}"
        captures.append(capture)
    state, conditions, eos, weak = [capture[1] for capture in captures]
    cross = fresh.index("call cross_sect(")
    derivative = fresh.index("call yderiv(")
    assert captures[0].end() < cross
    assert captures[1].end() < cross
    assert cross < captures[2].start() < captures[3].end() < derivative
    # An interrupted coefficient call must not expose uninitialized EOS buffers.
    assert cross < fresh.index("workspace_ready=.true.") < derivative
    prefix = re.search(r"if \(ios==0\) write\(unit,iostat=ios\) ([^\n]+)", writer)[1]
    assert prefix.replace(" ", "").split(",") == [conditions, eos, state]
    assert re.search(rf"save_failure_state\({state},{conditions}\(1\)", writer)
    assert f"int({weak},int32)" in writer


def test_failure_workspace_uses_evaluated_inputs_after_retry_reset():
    _assert_evaluated_snapshot_dataflow(NATIVE_SOURCE.read_text())


@pytest.mark.parametrize("mutation", ["reset_prefix", "reset_fallback", "early_eos"])
def test_snapshot_dataflow_rejects_original_cleanup_regressions(mutation):
    source = NATIVE_SOURCE.read_text()
    if mutation == "reset_prefix":
        source = source.replace(
            "last_evaluated_conditions,last_evaluated_eos,last_evaluated_state",
            "tt,t9t,rhot,yet,cv,etae,detaedt9,yt",
        )
    elif mutation == "reset_fallback":
        source = source.replace(
            "save_failure_state(last_evaluated_state,last_evaluated_conditions(1),",
            "save_failure_state(yt(:,1),last_evaluated_conditions(1),",
        )
    else:
        assignment = "    last_evaluated_eos=[yet(1),cv(1),etae(1),detaedt9(1)]\n"
        source = source.replace(assignment, "").replace(
            "    call cross_sect(mask_in=active)\n",
            assignment + "    call cross_sect(mask_in=active)\n",
        )
    with pytest.raises(AssertionError):
        _assert_evaluated_snapshot_dataflow(source)


def test_native_retention_fixture_checks_tenth_cleanup_and_exact_wire_prefix():
    # This checks fixture coverage only. Its actual execution requires separately
    # authorized native compilation and is not replaced by these Python checks.
    fixture = (NATIVE_SOURCE.parent / "synthetic_native.f90").read_text()
    scenario = fixture.split("case('retry-snapshot')", 1)[1].split("  case(", 1)[0]
    loop = scenario.split("do trial=1,10", 1)[1].split("    enddo", 1)[0]
    for field in ("yt(:,1)", "tt(1)", "t9t(1)", "rhot(1)", "yet(1)"):
        assert re.search(rf"{re.escape(field)}\s*=", loop)
    assert scenario.index("    enddo") < scenario.index("call save_failure_workspace()")
    assert "same_bits(saved_state,[expected_conditions,evaluated])" in scenario
    assert (
        "same_bits(saved_workspace,[expected_conditions,expected_eos,evaluated,expected_f])"
        in scenario
    )


def test_snapshot_matrix_baseline_tracks_matrix_formation_not_started_fd_build():
    source = NATIVE_SOURCE.read_text()
    step = _subroutine(source, "adapted_step")
    writer = _subroutine(source, "save_failure_workspace")
    assert (
        step.index("call jacobian_scale(")
        < step.index("matrix_jacobian_id=jacobian_count")
        < step.index("call jacobian_decomp(")
    )
    assert "matrix_jacobian_id=" not in _subroutine(source, "full_jacobian")
    assert "'FAILURE_WORKSPACE_JACOBIAN_BASE',matrix_jacobian_id" in writer
