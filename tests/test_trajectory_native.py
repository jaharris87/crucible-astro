"""Public provenance tests; physical sources and compilers are not CI inputs.

The actual adapter's polynomial, nonlinear stiff BE and refusal checks live in
synthetic_native.f90 and run with its independent synthetic_modules.f90 closure
on the pinned compiler before any physical control is evaluated.
"""

import importlib.util
import json
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
