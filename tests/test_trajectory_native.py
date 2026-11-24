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


def test_diagnostic_lapack_status_retains_default_fatal_guards(staging):
    stage, _, _ = staging
    # Minimal independent source fixture exercises both optional-status patches
    # and the untouched dgesv guard without requiring proprietary producer code.
    dense = """
Module xnet_jacobian
  Subroutine jacobian_solve(kstep,mask_in)
        Call dgesv(n,nrhs,m,n,p,r,n,info(izb))
  End Subroutine jacobian_solve
  Subroutine jacobian_decomp(kstep,mask_in)
    Logical, Optional, Target, Intent(in) :: mask_in(zb_lo:zb_hi)
        Call dgetrf(n,n,m,n,p,info(izb))
  End Subroutine jacobian_decomp
  Subroutine jacobian_bksub(kstep,yrhs,dy,t9rhs,dt9,mask_in)
    Logical, Optional, Target, Intent(in) :: mask_in(zb_lo:zb_hi)
        Call dgetrs('N',n,1,m,n,p,r,n,info(izb))
  End Subroutine jacobian_bksub
End Module xnet_jacobian
"""
    adapted = stage.adapt("refs/producer/xnet_jacobian_dense.f90", dense)
    assert adapted.count("If (present(status_out)) status_out(izb)=info(izb)") == 2
    assert adapted.count("info(izb)/=0.and..not.present(status_out)") == 2
    assert "If (info(izb)/=0) Call abort_linear(info(izb),'dgesv')" in adapted

    # Compare the independently maintained synthetic module with the staged
    # producer API and the adapter's actual keyword calls. Both runtime branches
    # must resolve during compilation, even when assembly_enabled is false.
    synthetic = (NATIVE_SOURCE.parent / "synthetic_modules.f90").read_text()
    adapter = NATIVE_SOURCE.read_text().lower().replace("&\n", "")
    compact_stub = re.sub(r"\s+", "", synthetic.lower())
    pivot_declaration = re.search(r"integer::indx\(([^)]+)\)=", compact_stub)
    assert pivot_declaration is not None
    assert pivot_declaration[1].split(",") == ["160", "1"]
    for routine, lapack in (
        ("jacobian_decomp", "dgetrf"),
        ("jacobian_bksub", "dgetrs"),
    ):
        signatures = []
        for source in (adapted, synthetic):
            procedure = re.search(
                rf"subroutine {routine}\((.*?)\)(.*?)end subroutine",
                source.lower(),
                re.S,
            )
            arguments = procedure[1].replace(" ", "").split(",")
            declaration = re.search(
                r"integer([^\n]*?)::\s*status_out\(([^)]*)\)", procedure[2]
            )
            assert declaration is not None
            attributes = declaration[1].replace(" ", "")
            assert "optional" in attributes and "intent(out)" in attributes
            assert len(declaration[2].split(",")) == 1
            signatures.append(
                (
                    len(arguments),
                    arguments.index("mask_in"),
                    arguments.index("status_out"),
                )
            )
        assert signatures[0] == signatures[1]
        keyword_call = re.search(rf"call {routine}\([^\n]+status_out=\w+\)", adapter)
        assert keyword_call is not None
        body = (
            synthetic.lower()
            .split(f"subroutine {routine}(", 1)[1]
            .split("end subroutine", 1)[0]
        )
        assert re.search(rf"call {lapack}\([^\n]+indx\(:,1\)", body)
        assert "if (present(status_out)) status_out=info" in body
        assert (
            f"if (info/=0.and..not.present(status_out)) call abort_linear(info,'{lapack}')"
            in body
        )


def test_diagnostic_path_preserves_legacy_direction_and_never_advances_solver():
    adapter = NATIVE_SOURCE.read_text()
    legacy = _subroutine(adapter, "directional_sweep")
    diagnostic = (NATIVE_SOURCE.parent / "diagnostic_native.f90").read_text()
    driver = (NATIVE_SOURCE.parent / "trajectory_driver.f90").read_text()
    assert "if (mod(i,2)==0.and.base(i)>0) v(i)=-v(i)" in legacy
    assert "do i=2,160,2\n          v(i)=0" in diagnostic
    assert "call solve_be" not in diagnostic.lower()
    assert "call adapted_step" not in diagnostic.lower()
    assert "call directional_sweep(initial," in driver
    assert "diagnostic commands require input mode zero" in driver


def test_diagnostic_factor_grid_and_single_unprojected_candidate_are_frozen():
    diagnostic = (NATIVE_SOURCE.parent / "diagnostic_native.f90").read_text()
    run = _subroutine(diagnostic, "run_native_diagnostic")
    assert "factors(4)=[0.1_dp,1.0_dp,10.0_dp,100.0_dp]" in run
    assert "f=base+deltas(:,2)" in run
    assert run.count("call candidate_evaluation(") == 1
    assert "if (.not.domain(f,temp,density,reason))" in run
    assert "max(" not in run[run.index("f=base+deltas(:,2)") :]
    assert "min(" not in run[run.index("f=base+deltas(:,2)") :]


def test_fd_probe_audit_ids_precede_branch_refusal_and_link_raw_f():
    column = _subroutine(NATIVE_SOURCE.read_text(), "column_probe")
    for number, why in ((1, "why1"), (2, "why2")):
        call = column.index(f"call fresh(p{number},")
        capture = column.index(f"probe_id{number}=rhs_count")
        branch = column.index(f"ok{number}=.false.; {why}='branch crossing'")
        assert call < capture < branch
    assert "real(probe_id1,dp),real(probe_id2,dp)" in column
    assert "probe_id1=0; probe_id2=0" in column


def test_diagnostic_incomplete_matrix_is_optional_and_restores_baseline():
    full = _subroutine(NATIVE_SOURCE.read_text(), "full_jacobian")
    failure = full[full.index("if (.not.found) then") :]
    assert "if (present(complete)) then" in failure
    assert "else\n          call fail(" in failure
    assert "complete=.false." in full
    assert full.index("complete=.false.") < full.rindex("call fresh(base,")
    assert "if (present(increment_factor)) delta=delta*increment_factor" in full


def _assert_linear_failure_keeps_unavailable_correction(source):
    """Static status/dataflow contract; no LAPACK or native execution."""
    linear = _subroutine(source, "diagnostic_linear")
    solve = linear.index("call jacobian_bksub(")
    unavailable = "delta=ieee_value(0.0_dp,ieee_quiet_nan)"
    assert unavailable in linear
    assert linear.index(unavailable) < solve
    assert linear.index("correction=ieee_value(0.0_dp,ieee_quiet_nan)") < solve
    success = re.search(
        r"if \(solve_info\(1\)==0\) then\s+"
        r"if \(\.not\.all\(ieee_is_finite\(correction\)\)\) call fail\([^\n]+\)\s+"
        r"delta=correction\(:,1\)\s+endif",
        linear,
    )
    assert success is not None
    assert solve < success.start()
    assert linear.count("delta=correction(:,1)") == 1


def test_failed_diagnostic_solve_persists_nan_and_success_checks_finiteness():
    source = (NATIVE_SOURCE.parent / "diagnostic_native.f90").read_text()
    _assert_linear_failure_keeps_unavailable_correction(source)


@pytest.mark.parametrize(
    "mutation", ["copy_after_failure", "drop_finite_check", "drop_nan_init"]
)
def test_linear_failure_dataflow_rejects_invalid_correction_publication(mutation):
    source = (NATIVE_SOURCE.parent / "diagnostic_native.f90").read_text()
    if mutation == "copy_after_failure":
        source = source.replace("        delta=correction(:,1)\n", "").replace(
            "    ok=lu_info(1)==0.and.solve_info(1)==0",
            "    delta=correction(:,1)\n    ok=lu_info(1)==0.and.solve_info(1)==0",
        )
    elif mutation == "drop_finite_check":
        source = source.replace(
            "        if (.not.all(ieee_is_finite(correction))) call fail('nonfinite diagnostic Newton correction')\n",
            "",
        )
    else:
        source = source.replace("    delta=ieee_value(0.0_dp,ieee_quiet_nan)\n", "")
    with pytest.raises(AssertionError):
        _assert_linear_failure_keeps_unavailable_correction(source)
