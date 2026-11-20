"""Public analytic/synthetic checks; no accepted local benchmark is accessed."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

from crucible import mlp_baseline as m
from crucible.rhs_data import UNITS


def pair(n=19, nv=7):
    rng = np.random.default_rng(1907)
    species = [{"Z": 0, "A": i + 1} for i in range(160)]
    common = dict(
        name=m.benchmark.NAME,
        version=m.benchmark.VERSION,
        use="rhs_training",
        row_order="exact accepted membership list",
        ordered_species=species,
        units={k: UNITS[k] for k in ("Y", "T9", "rho", "fresh_rhs")},
        overlay_sha256="a" * 64,
        payload_sha256="b" * 64,
        membership_sha256="c" * 64,
        eligibility_sha256="d" * 64,
        human_qualification_sha256="e" * 64,
        human_decision="synthetic",
        reference_identities={"synthetic": True},
        scoring_configuration_sha256="f" * 64,
        original_scoring_source_sha256="0" * 64,
        accepted_scoring_successor={"synthetic": True},
        verified_file_sha256=[],
        role_counts={"train": n, "validation": nv, "test": 0},
    )
    result = []
    for role, count, offset in (("train", n, 0), ("validation", nv, 10000)):
        y = rng.uniform(-1, 1, (count, 160))
        target = np.tile(y[:, :1], (1, 160)) * np.linspace(-2, 2, 160)
        target[:, 0] = 0  # A zero target remains a genuine learned loss term.
        y[:, 1] = -3  # A nonzero constant stays present too.
        result.append(
            dict(
                Y=y,
                fresh_rhs=target,
                T9=rng.uniform(0.1, 2, count),
                rho=rng.uniform(1, 10, count),
                record_id=np.array([f"{role}-{i}" for i in range(count)]),
                particle0=np.arange(count) + offset,
                group=np.arange(count) + offset,
                species_Z_A=np.array([[s["Z"], s["A"]] for s in species]),
                metadata={**copy.deepcopy(common), "split": role},
            )
        )
    return result


def test_fixed_protocol_and_direct_binary64_initialization():
    m.configure_cpu()
    model = m.MLP()
    assert sum(p.numel() for p in model.parameters()) == 24992
    assert all(
        p.dtype == torch.float64 and p.device.type == "cpu" for p in model.parameters()
    )
    assert all(torch.count_nonzero(b) == 0 for b in model.biases)
    generator = torch.Generator().manual_seed(20261120)
    for w in model.weights:
        expected = torch.empty_like(w)
        torch.nn.init.xavier_uniform_(expected, gain=1, generator=generator)
        assert torch.equal(w, expected)
    assert m.weights_hash(model) == m.weights_hash(m.MLP())
    config = Path(__file__).parents[1] / "configs/mlp_baseline/phase2b.json"
    assert m._json_read(config) == m.PROTOCOL


def numpy_forward(model, x):
    arrays = m.model_arrays(model)
    return (
        np.tanh(
            np.tanh(x @ arrays["w0"].T + arrays["b0"]) @ arrays["w1"].T + arrays["b1"]
        )
        @ arrays["w2"].T
        + arrays["b2"]
    )


def test_independent_forward_signed_outputs_and_autograd():
    model = m.MLP()
    x = np.random.default_rng(7).normal(size=(3, 162)).astype(np.float64)
    output = model(torch.from_numpy(x))
    assert np.allclose(
        output.detach().numpy(), numpy_forward(model, x), atol=3e-15, rtol=3e-14
    )
    loss = output.square().mean()
    loss.backward()
    analytic = model.weights[0].grad[2, 4].item()
    delta = 1e-5
    original = model.weights[0][2, 4].item()
    with torch.no_grad():
        model.weights[0][2, 4] = original + delta
        plus = (numpy_forward(model, x) ** 2).mean()
        model.weights[0][2, 4] = original - delta
        minus = (numpy_forward(model, x) ** 2).mean()
        model.weights[0][2, 4] = original
    assert analytic == pytest.approx((plus - minus) / (2 * delta), rel=2e-7, abs=1e-10)
    with torch.no_grad():
        for p in model.parameters():
            p.zero_()
        model.biases[-1][0], model.biases[-1][1] = -7.0, 9.0
    assert np.array_equal(m.normalized_predictions(model, x)[:, :2], [[-7, 9]] * 3)


def test_scales_constants_extremes_roundtrip_and_underflow():
    tiny = np.nextafter(0.0, 1.0)
    values = np.array([[0, -3, tiny, 1e300], [0, -3, 1e300, 1e-300]], dtype=np.float64)
    scale = m.fit_scale(values)
    assert np.array_equal(scale, [1, 3, 1e300, 1e300])
    transformed, check = m.transform(values, scale)
    assert np.array_equal(transformed[:, 0], [0, 0])
    assert np.array_equal(transformed[:, 1], [-1, -1])
    assert check["nonzero_to_zero_underflows"] == 2
    assert check["nonexact_roundtrips"] == 2
    # Nonzero-to-zero underflows are counted, never silently repaired.
    assert transformed[0, 2] == transformed[1, 3] == 0
    with pytest.raises(ValueError, match="nonfinite transformed"):
        m.transform(np.array([[1e308]]), np.array([1e-308]))
    with pytest.raises(ValueError, match="nonfinite scaler"):
        m.fit_scale(np.array([[np.nan]]))


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda t, v: v["metadata"].update(split="test"), "role/order/use"),
        (lambda t, v: v["metadata"]["units"].update(rho="kg/m^3"), "units"),
        (lambda t, v: v["species_Z_A"].__setitem__((0, 1), 99), "ordered species"),
        (lambda t, v: v["metadata"].update(payload_sha256="x" * 64), "provenance"),
        (lambda t, v: v["record_id"].__setitem__(0, t["record_id"][0]), "overlap"),
        (lambda t, v: v["group"].__setitem__(0, t["group"][0]), "group overlap"),
        (lambda t, v: v.update(Y=v["Y"].astype(np.float32)), "binary64"),
    ],
)
def test_split_species_units_and_membership_guards(mutation, match):
    train, val = pair()
    mutation(train, val)
    with pytest.raises(ValueError, match=match):
        m.data_contract(train, val)
    with pytest.raises(ValueError, match="final-test"):
        m._data(val, "test")


def test_validation_extrema_do_not_change_scales_or_epoch_one():
    train, val = pair(n=263)  # Exercises a minibatch tail.
    before = m.diagnostic_epoch_one(train, val)
    changed = copy.deepcopy(val)
    changed["Y"] *= 1000
    changed["fresh_rhs"] += 1000
    after = m.diagnostic_epoch_one(train, changed)
    assert before == after
    # Training data really influence the optimizer; this is not a constant hash.
    changed_train = copy.deepcopy(train)
    changed_train["fresh_rhs"] *= -1
    assert (
        before["epoch_1_weights_sha256"]
        != m.diagnostic_epoch_one(changed_train, val)["epoch_1_weights_sha256"]
    )


def test_validation_pooling_is_equal_element_including_tail():
    model = m.MLP()
    with torch.no_grad():
        for p in model.parameters():
            p.zero_()
    x = np.zeros((257, 162))
    y = np.zeros((257, 160))
    y[-1] = 7
    assert m.validation_mse(model, x, y) == pytest.approx(49 / 257, abs=0)


def test_training_tail_participates_in_gradient():
    m.configure_cpu()
    x = np.zeros((257, 162))
    y = np.zeros((257, 160))
    # Choose the final permuted record, so its signal occurs only in the tail.
    rng = torch.Generator().manual_seed(m.PROTOCOL["seed"])
    order = torch.randperm(257, generator=rng).numpy()
    y[order[-1]] = 1
    model = m.MLP()
    with torch.no_grad():
        for p in model.parameters():
            p.zero_()
    rng = torch.Generator().manual_seed(m.PROTOCOL["seed"])
    m._epoch(model, m._optimizer(model), x, y, rng)
    assert (model.biases[-1].detach().numpy() > 0).all()


@pytest.mark.parametrize(
    "losses,patience,best,completed",
    [
        ([0.5, 0.5, 0.6], 2, 0, 2),
        ([1.0, 0.8, 0.6, 0.6, 0.9], 2, 2, 4),
    ],
)
def test_actual_training_loop_selection_ties_epoch_zero_and_patience(
    tmp_path, monkeypatch, losses, patience, best, completed
):
    train, val = pair()
    values = iter(losses)
    monkeypatch.setattr(m, "validation_mse", lambda *args: next(values))
    captured = {}
    original = m._save_model

    def record(directory, model, xs, ys, contract, bindings, selection, **kwargs):
        captured[selection["epoch"]] = m.weights_hash(model)
        return original(
            directory, model, xs, ys, contract, bindings, selection, **kwargs
        )

    monkeypatch.setattr(m, "_save_model", record)
    out = tmp_path / "run"
    result = m._fit(train, val, out, max_epochs=10, patience=patience)
    assert result["selection"]["epoch"] == best
    assert result["selection"]["completed_epochs"] == completed
    assert result["selection"]["stopping_reason"] == "patience"
    assert result["selection"]["untrained"] == (best == 0)
    _, xs, ys, manifest = m.load_model(out, m.data_contract(train, val))
    assert manifest["weights_sha256"] == captured[best]
    assert (
        result["epoch_1_weights_sha256"]
        == m.diagnostic_epoch_one(train, val)["epoch_1_weights_sha256"]
    )
    assert xs.shape == (162,) and ys.shape == (160,)
    records = [
        json.loads(line) for line in (out / "progress.jsonl").read_text().splitlines()
    ]
    assert [v["epoch"] for v in records] == list(range(completed + 1))
    assert not records[best + 1]["strict_new_best"] if best == 0 else True


def test_real_synthetic_fit_reload_and_clean_reproduction(tmp_path):
    train, val = pair()
    first, second = tmp_path / "first", tmp_path / "second"
    a = m._fit(train, val, first, max_epochs=6, patience=30)
    b = m._fit(train, val, second, max_epochs=6, patience=30)
    assert a["selection"] == b["selection"]
    assert a["selection"]["stopping_reason"] == "max_epochs"
    epochs = [
        json.loads(line) for line in (first / "progress.jsonl").read_text().splitlines()
    ]
    assert (
        epochs[-1]["online_training_normalized_mse"]
        < epochs[1]["online_training_normalized_mse"]
    )
    assert a["epoch_1_weights_sha256"] != m.weights_hash(m.MLP())
    for name in ("model.npz", "predictions.npz"):
        with (
            np.load(first / name, allow_pickle=False) as x,
            np.load(second / name, allow_pickle=False) as y,
        ):
            assert x.files == y.files
            assert all(
                x[k].dtype == y[k].dtype and x[k].tobytes() == y[k].tobytes()
                for k in x.files
            )
    assert m.reload_check(first, train, val)["bitwise_train_validation_predictions"]
    with np.load(first / "predictions.npz", allow_pickle=False) as saved:
        assert saved["validation_prediction"].shape == (7, 160)
        assert saved["train_target"].tobytes() == train["fresh_rhs"].tobytes()
        # Zero training targets retain an unrestricted model output.
        assert np.any(saved["train_prediction"][:, 0] != 0)
    # Cross-process reload uses independently reconstructed synthetic dictionaries.
    input_path = tmp_path / "data.json"
    serial = [
        {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in d.items()}
        for d in (train, val)
    ]
    input_path.write_text(json.dumps(serial))
    code = """
import json,sys,numpy as np
from crucible import mlp_baseline as m
pair=json.load(open(sys.argv[1]))
for d in pair:
    for k in d:
        if k!='metadata': d[k]=np.asarray(d[k])
print(json.dumps(m.reload_check(sys.argv[2], *pair)))
"""
    env = dict(os.environ, PYTHONPATH=str(Path(m.__file__).parents[1]))
    output = subprocess.run(
        [sys.executable, "-B", "-c", code, str(input_path), str(first)],
        check=True,
        text=True,
        capture_output=True,
        env=env,
    )
    assert json.loads(output.stdout)["bitwise_train_validation_predictions"]


def test_artifact_rejects_corruption_contract_permutation_and_forged_shapes(tmp_path):
    train, val = pair()
    out = tmp_path / "run"
    m._fit(train, val, out, max_epochs=0)
    expected = m.data_contract(train, val)
    altered = copy.deepcopy(expected)
    altered["shared"]["ordered_species"].reverse()
    with pytest.raises(ValueError, match="contract"):
        m.load_model(out, altered)
    altered = copy.deepcopy(expected)
    altered["shared"]["units"]["Y"] = "mass_fraction"
    with pytest.raises(ValueError, match="contract"):
        m.load_model(out, altered)
    original = (out / "model.npz").read_bytes()
    (out / "model.npz").write_bytes(original + b"damage")
    with pytest.raises(ValueError, match="NPZ hash"):
        m.load_model(out, expected)
    (out / "model.npz").write_bytes(original)
    with np.load(out / "model.npz", allow_pickle=False) as saved:
        arrays = {k: saved[k] for k in saved.files}
    arrays["w0"] = np.zeros((64, 161))
    np.savez(out / "model.npz", **arrays)
    manifest = m._json_read(out / "model.json")
    manifest["npz_sha256"] = m.sha256(out / "model.npz")
    manifest["array_sha256"]["w0"] = m.array_hash(arrays["w0"])
    m._write_json(out / "model.json", manifest)
    with pytest.raises(ValueError, match="dtype/shape"):
        m.load_model(out, expected)


def test_failure_retains_best_logs_and_explicit_stage(tmp_path, monkeypatch):
    train, val = pair()
    original = m._epoch
    epochs = 0

    def fail_second(*args):
        nonlocal epochs
        epochs += 1
        if epochs == 2:
            raise RuntimeError("synthetic deterministic failure")
        return original(*args)

    monkeypatch.setattr(m, "_epoch", fail_second)
    out = tmp_path / "failed"
    with pytest.raises(RuntimeError, match="synthetic deterministic"):
        m._fit(train, val, out, max_epochs=4)
    failure = m._json_read(out / "failure.json")
    assert failure["stage"] == "epoch_2" and failure["completed_epochs"] == 1
    assert (out / "model.npz").exists() and (out / "last_finite.npz").exists()
    assert len((out / "progress.jsonl").read_text().splitlines()) == 2
    assert not (out / "result.json").exists()
    with pytest.raises(FileExistsError):
        m._fit(train, val, out)


def test_nonfinite_input_and_prediction_are_explicit_failures(tmp_path, monkeypatch):
    train, val = pair()
    train["Y"][0, 0] = np.nan
    with pytest.raises(ValueError, match="nonfinite Y"):
        m._fit(train, val, tmp_path / "bad_input", max_epochs=0)
    assert m._json_read(tmp_path / "bad_input/failure.json")["stage"] == "setup"
    train, val = pair()
    original = m.MLP.forward

    def nonfinite(self, x):
        out = original(self, x)
        out[0, 0] = np.inf
        return out

    monkeypatch.setattr(m.MLP, "forward", nonfinite)
    with pytest.raises(
        ValueError, match="nonfinite validation prediction; components=1; rows=1"
    ):
        m._fit(train, val, tmp_path / "bad_prediction", max_epochs=0)
    assert (tmp_path / "bad_prediction/failure.json").exists()


def test_strict_json_and_config_refusal_before_loading(tmp_path, monkeypatch):
    config = tmp_path / "bad.json"
    config.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError, match="duplicate"):
        m._json_read(config)
    config.write_text('{"a": NaN}')
    with pytest.raises(ValueError, match="nonfinite JSON"):
        m._json_read(config)
    config.write_text("{}")
    monkeypatch.setattr(
        m.benchmark, "load_benchmark", lambda *a, **k: pytest.fail("loader called")
    )
    with pytest.raises(ValueError, match="configuration differs"):
        m.train_experiment("unused", tmp_path / "run", protocol_path=config)
