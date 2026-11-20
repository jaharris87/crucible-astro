"""Synthetic evidence checks for the private all-role-bounded callable runner."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from test_mlp_baseline import pair

from crucible import frozen_rhs as f
from crucible import mlp_baseline as m

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location(
    "check_frozen", ROOT / "experiments/integration/check_frozen.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def fixture(tmp_path, monkeypatch):
    m.configure_cpu()
    train, validation = pair(3, 2)
    for data in (train, validation):
        data["time"] = np.linspace(0.1, 0.7, len(data["Y"]))
    model = m.MLP()
    xs, ys = np.ones(162), np.ones(160)
    run = tmp_path / "synthetic-artifact"
    run.mkdir()
    m._save_model(run, model, xs, ys, m.data_contract(train, validation), {}, {})
    predictions = {}
    for role, data in (("train", train), ("validation", validation)):
        x, _ = m._data(data, role)
        p, _ = m._physical_predictions(model, x, xs, ys)
        predictions[role + "_prediction"] = p
        predictions[role + "_record_id"] = data["record_id"]
    np.savez(run / "predictions.npz", **predictions)
    monkeypatch.setattr(
        f, "FROZEN_SHA256", {k: m.sha256(run / k) for k in f.FROZEN_SHA256}
    )
    calls = []

    def load(name, version, *, use, split, config):
        calls.append(split)
        assert name == m.benchmark.NAME and version == m.benchmark.VERSION
        assert use == "rhs_training"
        return {"train": train, "validation": validation}[split]

    monkeypatch.setattr(runner.benchmark, "load_benchmark", load)
    access = tmp_path / "access.json"
    access.write_text(
        json.dumps({"benchmark_access": "synthetic-config", "frozen_run": str(run)})
    )
    return access, calls


def test_all_allowed_rows_once_no_test_role_and_recompute_mutation(
    tmp_path, monkeypatch
):
    access, calls = fixture(tmp_path, monkeypatch)
    output = tmp_path / "callable"
    report = runner.check(access, output, ROOT)
    assert report["status"] == "PASS", report
    assert calls == ["train", "validation"]
    assert [report["roles"][k]["records"] for k in calls] == [3, 2]
    assert all(report["roles"][k]["time_conditions_bitwise"] for k in calls)
    assert runner.reload(output)["status"] == "PASS"
    assert runner.compare(output, output)["reproduction"] == "PASS"
    with pytest.raises(FileExistsError):
        runner.check(access, output, ROOT)
    report["roles"]["train"]["max_normalized_difference"] = 1
    runner.write_json(output / "report.json", report)
    with pytest.raises(ValueError, match="discrepancy report"):
        runner.reload(output)


def test_preflight_failure_is_retained_without_loading(tmp_path, monkeypatch):
    access, calls = fixture(tmp_path, monkeypatch)
    path = Path(json.loads(access.read_text())["frozen_run"]) / "model.npz"
    path.write_bytes(path.read_bytes() + b"corruption")
    output = tmp_path / "failed"
    report = runner.check(access, output, ROOT)
    assert report["status"] == "FAIL" and calls == []
    assert (
        report["exception"]["message"]
        == "frozen model/manifest/prediction identity mismatch"
    )
    assert (output / "exception.txt").is_file()
    assert json.loads((output / "report.json").read_text())["status"] == "FAIL"
