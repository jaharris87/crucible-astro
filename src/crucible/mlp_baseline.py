"""Accepted Phase 2B CPU full-state MLP; no final-test execution entry point.

Real artifacts contain private records/weights and must stay local.  The numerical
core also accepts tiny synthetic loader-shaped dictionaries for public tests.
"""

import argparse
import hashlib
import json
import math
import platform
import resource
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch

from crucible import benchmark
from crucible.rhs_data import UNITS

PROTOCOL = {
    "schema": "crucible.phase2b-mlp-protocol.v1",
    "proposal_sha256": "0ce78f0d008f3bf166b4efacabc923a633e7fe6d587fb0984de0b1ba3dba60d8",
    "architecture": [162, 64, 64, 160],
    "activation": "tanh,tanh,linear",
    "dtype": "float64",
    "device": "cpu",
    "seed": 20261120,
    "initialization": "xavier_uniform_gain_1_zero_bias_dedicated_generator",
    "scaling": "train_only_column_maxabs_zero_to_one",
    "batch_size": 256,
    "max_epochs": 500,
    "patience": 30,
    "selection": "strict_validation_pooled_normalized_mse_earliest_tie_epoch_0_eligible",
    "optimizer": {
        "lr": 0.001,
        "betas": [0.9, 0.999],
        "eps": 1e-8,
        "weight_decay": 0,
        "amsgrad": False,
        "maximize": False,
        "capturable": False,
        "differentiable": False,
        "foreach": False,
        "fused": False,
        "decoupled_weight_decay": False,
    },
}
SCHEMA = "crucible.phase2b-mlp-artifact.v1"
ROLES = ("train", "validation")
SHAPES = {
    "w0": (64, 162),
    "b0": (64,),
    "w1": (64, 64),
    "b1": (64,),
    "w2": (160, 64),
    "b2": (160,),
    "x_scale": (162,),
    "y_scale": (160,),
}


def _need(ok, message):
    if not ok:
        raise ValueError("mlp baseline: " + message)


def _finite(array, stage):
    a = array.detach().numpy() if isinstance(array, torch.Tensor) else np.asarray(array)
    bad = ~np.isfinite(a)
    _need(
        not bad.any(),
        f"nonfinite {stage}; components={int(bad.sum())}; "
        f"rows={int(bad.reshape(len(a), -1).any(axis=1).sum()) if a.ndim else int(bad)}",
    )


def _json_bytes(value):
    return (
        json.dumps(value, allow_nan=False, sort_keys=True, indent=2) + "\n"
    ).encode()


def _json_read(path):
    def reject(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    def unique(pairs):
        out = {}
        for k, v in pairs:
            _need(k not in out, "duplicate JSON key")
            out[k] = v
        return out

    return json.loads(
        Path(path).read_bytes(), parse_constant=reject, object_pairs_hook=unique
    )


def _write_json(path, value):
    Path(path).write_bytes(_json_bytes(value))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array_hash(array):
    a = np.ascontiguousarray(array)
    return hashlib.sha256(
        str(a.dtype).encode() + _json_bytes(list(a.shape)) + a.tobytes()
    ).hexdigest()


def configure_cpu():
    """Configure once in the process; never touch a global random generator."""
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)


class MLP(torch.nn.Module):
    """Three affine maps allocated directly in binary64, without default init."""

    def __init__(self):
        super().__init__()
        rng = torch.Generator(device="cpu").manual_seed(PROTOCOL["seed"])
        self.weights = torch.nn.ParameterList()
        self.biases = torch.nn.ParameterList()
        for fan_in, fan_out in zip(
            PROTOCOL["architecture"][:-1], PROTOCOL["architecture"][1:], strict=True
        ):
            w = torch.empty((fan_out, fan_in), dtype=torch.float64, device="cpu")
            w.uniform_(
                -math.sqrt(6 / (fan_in + fan_out)),
                math.sqrt(6 / (fan_in + fan_out)),
                generator=rng,
            )
            self.weights.append(torch.nn.Parameter(w))
            self.biases.append(
                torch.nn.Parameter(torch.zeros(fan_out, dtype=torch.float64))
            )

    def forward(self, x):
        for i, (w, b) in enumerate(zip(self.weights, self.biases, strict=True)):
            x = torch.nn.functional.linear(x, w, b)
            if i < 2:
                x = torch.tanh(x)
        return x


def model_arrays(model):
    return {
        f"{kind}{i}": p.detach().numpy().copy()
        for kind, params in (("w", model.weights), ("b", model.biases))
        for i, p in enumerate(params)
    }


def weights_hash(model):
    arrays = model_arrays(model)
    return hashlib.sha256(
        _json_bytes({k: array_hash(v) for k, v in arrays.items()})
    ).hexdigest()


def fit_scale(values):
    _need(
        values.dtype == np.float64 and values.ndim == 2 and len(values) > 0,
        "scaler requires nonempty binary64 matrix",
    )
    _finite(values, "scaler input")
    scale = np.max(np.abs(values), axis=0)
    return np.where(scale == 0, 1.0, scale)


def transform(values, scale):
    """Check the accepted binary64 roundtrip bound and report underflows."""
    _finite(values, "transform input")
    _need(
        scale.dtype == np.float64
        and scale.shape == (values.shape[1],)
        and np.isfinite(scale).all()
        and (scale > 0).all(),
        "invalid scale",
    )
    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        normalized = values / scale
        restored = normalized * scale
        bound = 4 * np.finfo(np.float64).eps * np.maximum(scale, np.abs(values))
        bound += np.nextafter(np.float64(0), np.float64(1))
        error = np.abs(restored - values)
    _finite(normalized, "transformed values")
    _finite(restored, "inverse transformed values")
    _need((error <= bound).all(), "scaler roundtrip bound failure")
    return normalized, {
        "nonzero_to_zero_underflows": int(((values != 0) & (normalized == 0)).sum()),
        "nonexact_roundtrips": int((restored != values).sum()),
        "max_absolute_roundtrip_error": float(error.max()),
    }


def _data(data, role):
    _need(role in ROLES, "final-test model execution is forbidden in Phase 2B")
    meta = data["metadata"]
    _need(
        meta["name"] == benchmark.NAME
        and meta["version"] == benchmark.VERSION
        and meta["use"] == "rhs_training"
        and meta["split"] == role
        and meta["row_order"] == "exact accepted membership list",
        "data role/order/use",
    )
    _need(
        all(meta["units"].get(k) == UNITS[k] for k in ("Y", "T9", "rho", "fresh_rhs")),
        "data units",
    )
    species = meta["ordered_species"]
    _need(
        isinstance(species, list)
        and len(species) == 160
        and data["species_Z_A"].shape == (160, 2)
        and data["species_Z_A"].tolist() == [[s["Z"], s["A"]] for s in species],
        "ordered species",
    )
    n = len(data["record_id"])
    _need(n > 0 and len(set(data["record_id"].tolist())) == n, "record membership")
    for key, shape in (
        ("Y", (n, 160)),
        ("fresh_rhs", (n, 160)),
        ("T9", (n,)),
        ("rho", (n,)),
    ):
        a = data[key]
        _need(
            isinstance(a, np.ndarray) and a.dtype == np.float64 and a.shape == shape,
            "binary64 shape: " + key,
        )
        _finite(a, key)
    x = np.column_stack((data["Y"], data["T9"], data["rho"]))
    return x, data["fresh_rhs"]


def data_contract(train, validation):
    """Bind both roles, exact membership order and loader-provided acceptance roots."""
    for role, data in zip(ROLES, (train, validation), strict=True):
        _data(data, role)
    shared = (
        "name",
        "version",
        "use",
        "row_order",
        "units",
        "ordered_species",
        "overlay_sha256",
        "payload_sha256",
        "membership_sha256",
        "eligibility_sha256",
        "human_qualification_sha256",
        "human_decision",
        "reference_identities",
        "scoring_configuration_sha256",
        "original_scoring_source_sha256",
        "accepted_scoring_successor",
        "verified_file_sha256",
        "role_counts",
    )
    _need(
        all(train["metadata"][k] == validation["metadata"][k] for k in shared),
        "train/validation provenance or species differs",
    )
    _need(
        not set(train["record_id"].tolist()) & set(validation["record_id"].tolist()),
        "train/validation overlap",
    )
    for key in ("particle0", "group"):
        _need(
            not set(train[key].tolist()) & set(validation[key].tolist()),
            key + " overlap",
        )
    return {
        "shared": {k: train["metadata"][k] for k in shared},
        "roles": {
            role: {
                "rows": len(data["record_id"]),
                "record_order_sha256": hashlib.sha256(
                    _json_bytes(data["record_id"].tolist())
                ).hexdigest(),
            }
            for role, data in zip(ROLES, (train, validation), strict=True)
        },
        "feature_order": ["Y[0:160]", "T9", "rho"],
        "target": "fresh_rhs",
    }


def _optimizer(model):
    options = dict(PROTOCOL["optimizer"])
    options["betas"] = tuple(options["betas"])
    return torch.optim.Adam(model.parameters(), **options)


def normalized_predictions(model, x):
    pieces = []
    with torch.inference_mode():
        for start in range(0, len(x), PROTOCOL["batch_size"]):
            p = model(torch.from_numpy(x[start : start + PROTOCOL["batch_size"]]))
            _finite(p, "prediction")
            pieces.append(p.numpy().copy())
    return np.concatenate(pieces)


def validation_mse(model, x, y):
    total = np.float64(0)
    with torch.inference_mode():
        for start in range(0, len(x), PROTOCOL["batch_size"]):
            sl = slice(start, start + PROTOCOL["batch_size"])
            p = model(torch.from_numpy(x[sl]))
            _finite(p, "validation prediction")
            squared = (p - torch.from_numpy(y[sl])).square()
            _finite(squared, "validation squared error")
            total += np.float64(squared.sum(dtype=torch.float64).item())
    loss = float(total / y.size)
    _need(math.isfinite(loss), "nonfinite validation loss")
    return loss


def _epoch(model, optimizer, x, y, rng):
    order = torch.randperm(len(x), generator=rng).numpy()
    total = np.float64(0)
    for start in range(0, len(x), PROTOCOL["batch_size"]):
        indices = order[start : start + PROTOCOL["batch_size"]]
        optimizer.zero_grad(set_to_none=True)
        prediction = model(torch.from_numpy(x[indices]))
        _finite(prediction, "training prediction")
        loss = (prediction - torch.from_numpy(y[indices])).square().mean()
        _finite(loss, "training loss")
        loss.backward()
        for p in model.parameters():
            _need(p.grad is not None, "missing gradient")
            _finite(p.grad, "gradient")
        optimizer.step()
        for p in model.parameters():
            _finite(p, "parameter")
        total += np.float64(loss.item()) * (len(indices) * y.shape[1])
    loss = float(total / y.size)
    _need(math.isfinite(loss), "nonfinite pooled training loss")
    return loss


def _save_model(
    directory, model, xs, ys, contract, bindings, selection, *, stem="model"
):
    arrays = {**model_arrays(model), "x_scale": xs, "y_scale": ys}
    path = directory / (stem + ".npz")
    np.savez(path, **arrays)
    manifest = {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "contract": contract,
        "bindings": bindings,
        "selection": selection,
        "array_sha256": {k: array_hash(v) for k, v in arrays.items()},
        "npz_sha256": sha256(path),
        "weights_sha256": weights_hash(model),
    }
    _write_json(directory / (stem + ".json"), manifest)
    return manifest


def load_model(directory, expected_contract, *, stem="model"):
    """Reject incompatible models against the independently supplied data contract."""
    directory = Path(directory)
    manifest = _json_read(directory / (stem + ".json"))
    _need(
        set(manifest)
        == {
            "schema",
            "protocol",
            "contract",
            "bindings",
            "selection",
            "array_sha256",
            "npz_sha256",
            "weights_sha256",
        },
        "manifest fields",
    )
    _need(
        manifest["schema"] == SCHEMA and manifest["protocol"] == PROTOCOL,
        "incompatible artifact schema/protocol",
    )
    _need(
        manifest["contract"] == expected_contract,
        "artifact data/species/order/units contract",
    )
    path = directory / (stem + ".npz")
    _need(sha256(path) == manifest["npz_sha256"], "artifact NPZ hash")
    with np.load(path, allow_pickle=False) as saved:
        _need(set(saved.files) == set(SHAPES), "artifact array names")
        arrays = {k: saved[k].copy() for k in SHAPES}
    _need(set(manifest["array_sha256"]) == set(SHAPES), "artifact array digest names")
    for key, a in arrays.items():
        _need(
            a.dtype == np.float64 and a.shape == SHAPES[key],
            "artifact dtype/shape " + key,
        )
        _finite(a, "artifact " + key)
        _need(
            array_hash(a) == manifest["array_sha256"][key], "artifact array hash " + key
        )
    _need(
        (arrays["x_scale"] > 0).all() and (arrays["y_scale"] > 0).all(),
        "artifact scale sign",
    )
    model = MLP()
    with torch.no_grad():
        for i in range(3):
            model.weights[i].copy_(torch.from_numpy(arrays[f"w{i}"]))
            model.biases[i].copy_(torch.from_numpy(arrays[f"b{i}"]))
    _need(weights_hash(model) == manifest["weights_sha256"], "artifact model hash")
    # Compare bytes, including signed zero; numerical equality is insufficient.
    for k, a in model_arrays(model).items():
        _need(a.tobytes() == arrays[k].tobytes(), "artifact reload array bits")
    return model, arrays["x_scale"], arrays["y_scale"], manifest


def _physical_predictions(model, x, xs, ys):
    z, diagnostics = transform(x, xs)
    with np.errstate(over="ignore", invalid="ignore"):
        p = normalized_predictions(model, z) * ys
    _finite(p, "physical prediction")
    return p, diagnostics


def _prepare(train, validation):
    contract = data_contract(train, validation)
    xt, yt = _data(train, "train")
    xv, yv = _data(validation, "validation")
    xs, ys = fit_scale(xt), fit_scale(yt)
    scaled, checks = [], {}
    for key, values, scale in (
        ("train_input", xt, xs),
        ("train_target", yt, ys),
        ("validation_input", xv, xs),
        ("validation_target", yv, ys),
    ):
        z, check = transform(values, scale)
        scaled.append(z)
        checks[key] = check
    return contract, xs, ys, scaled, checks


def diagnostic_epoch_one(train, validation):
    """Independence probe only: fixed protocol initialization and one gradient epoch.

    No checkpoint choice, experiment artifact, or scientific trial is produced.
    Validation is checked/transformed but never supplied to the optimizer.
    """
    configure_cpu()
    _, xs, ys, (xt, yt, _, _), _ = _prepare(train, validation)
    model = MLP()
    rng = torch.Generator(device="cpu").manual_seed(PROTOCOL["seed"])
    _epoch(model, _optimizer(model), xt, yt, rng)
    return {
        "epoch_1_weights_sha256": weights_hash(model),
        "x_scale_sha256": array_hash(xs),
        "y_scale_sha256": array_hash(ys),
    }


def _environment():
    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "h5py": __import__("h5py").__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "torch_build": torch.__config__.show(),
        "intraop_threads": torch.get_num_threads(),
        "interop_threads": torch.get_num_interop_threads(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
    }


def _fit(
    train,
    validation,
    output_dir,
    *,
    source_bindings=None,
    max_epochs=500,
    patience=30,
    _require_source_files=False,
):
    """Numerical core; shorter stopping settings are for synthetic tests only."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    stage, completed = "setup", 0
    log = directory / "progress.jsonl"
    try:
        configure_cpu()
        contract, xs, ys, (xt, yt, xv, yv), checks = _prepare(train, validation)
        bindings = dict(source_bindings or {})
        bindings["module_sha256"] = sha256(__file__)
        project = Path(
            bindings.pop("source_root", Path(__file__).resolve().parents[2])
        ).resolve()
        for filename in (
            "pyproject.toml",
            "uv.lock",
            "configs/mlp_baseline/phase2b.json",
        ):
            path = project / filename
            if path.is_file():
                actual = sha256(path)
                _need(
                    bindings.get(filename + "_sha256", actual) == actual,
                    "source binding differs: " + filename,
                )
                bindings[filename + "_sha256"] = actual
            else:
                _need(not _require_source_files, "missing source binding: " + filename)
        bindings["protocol_sha256"] = hashlib.sha256(_json_bytes(PROTOCOL)).hexdigest()
        model = MLP()
        optimizer = _optimizer(model)
        rng = torch.Generator(device="cpu").manual_seed(PROTOCOL["seed"])
        losses, best_loss, best_epoch, stale, epoch_one = [], math.inf, 0, 0, None
        for epoch in range(max_epochs + 1):
            stage = f"epoch_{epoch}"
            training_loss = (
                None if epoch == 0 else _epoch(model, optimizer, xt, yt, rng)
            )
            if epoch == 1:
                epoch_one = weights_hash(model)
            loss = validation_mse(model, xv, yv)
            losses.append(loss)
            improved = loss < best_loss
            if improved:
                best_loss, best_epoch, stale = loss, epoch, 0
            elif epoch:
                stale += 1
            entry = {
                "epoch": epoch,
                "online_training_normalized_mse": training_loss,
                "validation_normalized_mse": loss,
                "strict_new_best": improved,
            }
            with log.open("a") as stream:
                stream.write(_json_bytes(entry).decode().replace("\n", "") + "\n")
                stream.flush()
            selected = {
                "epoch": epoch,
                "validation_normalized_mse": loss,
                "untrained": epoch == 0,
                "complete": False,
            }
            _save_model(
                directory,
                model,
                xs,
                ys,
                contract,
                bindings,
                selected,
                stem="last_finite",
            )
            if improved:
                _save_model(directory, model, xs, ys, contract, bindings, selected)
            completed = epoch
            if stale >= patience:
                break
        reason = "patience" if stale >= patience else "max_epochs"
        model, loaded_xs, loaded_ys, manifest = load_model(directory, contract)
        _need(
            loaded_xs.tobytes() == xs.tobytes() and loaded_ys.tobytes() == ys.tobytes(),
            "reloaded scaler bits",
        )
        selection = {
            "epoch": best_epoch,
            "validation_normalized_mse": best_loss,
            "untrained": best_epoch == 0,
            "complete": True,
            "completed_epochs": completed,
            "stopping_reason": reason,
        }
        _save_model(directory, model, xs, ys, contract, bindings, selection)
        stage = "physical_predictions"
        predictions = {}
        for role, data in zip(ROLES, (train, validation), strict=True):
            x, y = _data(data, role)
            p, _ = _physical_predictions(model, x, xs, ys)
            predictions[role + "_prediction"] = p
            predictions[role + "_target"] = y
            predictions[role + "_record_id"] = np.asarray(data["record_id"], dtype=str)
        np.savez(directory / "predictions.npz", **predictions)
        ordered = sorted(losses)
        result = {
            "schema": "crucible.phase2b-mlp-result.v1",
            "execution_controls": {
                "max_epochs": max_epochs,
                "patience": patience,
                "accepted_protocol_runner": _require_source_files,
            },
            "protocol": PROTOCOL,
            "contract": contract,
            "bindings": bindings,
            "selection": selection,
            "best_runner_up_gap": ordered[1] - ordered[0] if len(ordered) > 1 else None,
            "epoch_1_weights_sha256": epoch_one,
            "x_scale_sha256": array_hash(xs),
            "y_scale_sha256": array_hash(ys),
            "scaling_checks": checks,
            "environment": _environment(),
            "finished_utc": datetime.now(UTC).isoformat(),
            "runtime_seconds": time.perf_counter() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1 if sys.platform == "darwin" else 1024),
            "prediction_rows": {r: len(predictions[r + "_prediction"]) for r in ROLES},
            "failed_prediction_rows": 0,
            "nonfinite_prediction_components": 0,
            "artifact_sha256": {
                p.name: sha256(p)
                for p in (
                    directory / "model.npz",
                    directory / "model.json",
                    directory / "predictions.npz",
                    log,
                )
            },
        }
        _write_json(directory / "result.json", result)
        stage = "reload_check"
        reload_check(directory, train, validation)
        return result
    except BaseException as exc:
        _write_json(
            directory / "failure.json",
            {
                "schema": "crucible.phase2b-mlp-failure.v1",
                "stage": stage,
                "completed_epochs": completed,
                "exception_type": type(exc).__name__,
                "message": str(exc),
                "utc": datetime.now(UTC).isoformat(),
                "runtime_seconds": time.perf_counter() - started,
            },
        )
        raise


def fit_data(train, validation, output_dir, *, source_bindings=None):
    """Run only the immutable accepted protocol on already loaded train/validation."""
    return _fit(
        train,
        validation,
        output_dir,
        source_bindings=source_bindings,
        _require_source_files=True,
    )


def reload_check(directory, train, validation):
    """Require fixed-batch physical predictions bitwise equal to saved predictions."""
    configure_cpu()
    directory = Path(directory)
    contract = data_contract(train, validation)
    result = _json_read(directory / "result.json")
    _need(
        set(result["artifact_sha256"])
        == {"model.npz", "model.json", "predictions.npz", "progress.jsonl"},
        "result artifact digest names",
    )
    for name, digest in result["artifact_sha256"].items():
        _need(
            name in {"model.npz", "model.json", "predictions.npz", "progress.jsonl"}
            and sha256(directory / name) == digest,
            "result artifact hash",
        )
    model, xs, ys, manifest = load_model(directory, contract)
    _need(result["selection"] == manifest["selection"], "result selection")
    with np.load(directory / "predictions.npz", allow_pickle=False) as saved:
        _need(
            set(saved.files)
            == {
                r + suffix
                for r in ROLES
                for suffix in ("_prediction", "_target", "_record_id")
            },
            "saved prediction names",
        )
        for role, data in zip(ROLES, (train, validation), strict=True):
            x, y = _data(data, role)
            p, _ = _physical_predictions(model, x, xs, ys)
            old = saved[role + "_prediction"]
            _need(
                old.dtype == np.float64
                and old.shape == p.shape
                and old.tobytes() == p.tobytes(),
                "prediction reload bits " + role,
            )
            old_y = saved[role + "_target"]
            _need(
                old_y.dtype == np.float64
                and old_y.shape == y.shape
                and old_y.tobytes() == y.tobytes(),
                "saved target bits " + role,
            )
            _need(
                saved[role + "_record_id"].tolist() == data["record_id"].tolist(),
                "saved prediction record order " + role,
            )
    return {
        "bitwise_train_validation_predictions": True,
        "weights_sha256": manifest["weights_sha256"],
    }


def train_experiment(access_config, output_dir, *, protocol_path, source_bindings=None):
    """Private real runner: load each allowed role once; no test option exists."""
    _need(
        _json_read(protocol_path) == PROTOCOL, "accepted protocol configuration differs"
    )
    import h5py

    _need(
        (
            platform.python_version(),
            torch.__version__.removesuffix("+cpu"),
            np.__version__,
            h5py.__version__,
        )
        == ("3.12.9", "2.9.1", "2.5.5", "3.15.1"),
        "accepted pinned runtime differs",
    )
    start = time.perf_counter()
    train, validation = [
        benchmark.load_benchmark(
            benchmark.NAME,
            benchmark.VERSION,
            use="rhs_training",
            split=role,
            config=access_config,
        )
        for role in ROLES
    ]
    _need(
        (len(train["Y"]), len(validation["Y"])) == (17659, 3220), "accepted role counts"
    )
    bindings = dict(source_bindings or {})
    bindings.update(
        {
            "configuration_file_sha256": sha256(protocol_path),
            "load_seconds": time.perf_counter() - start,
        }
    )
    return fit_data(train, validation, output_dir, source_bindings=bindings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("train", "reload-check"))
    parser.add_argument("access_config", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument(
        "--source-root",
        type=Path,
        help="checkout containing the exact config and lock for an installed-package run",
    )
    args = parser.parse_args()
    if args.command == "train":
        result = train_experiment(
            args.access_config,
            args.output_dir,
            protocol_path=args.protocol,
            source_bindings={"source_root": str(args.source_root)}
            if args.source_root
            else None,
        )
        print(
            json.dumps(
                {
                    "selected_epoch": result["selection"]["epoch"],
                    "stopping_reason": result["selection"]["stopping_reason"],
                }
            )
        )
    else:
        _need(
            _json_read(args.protocol) == PROTOCOL,
            "accepted protocol configuration differs",
        )
        train, validation = [
            benchmark.load_benchmark(
                benchmark.NAME,
                benchmark.VERSION,
                use="rhs_training",
                split=role,
                config=args.access_config,
            )
            for role in ROLES
        ]
        print(json.dumps(reload_check(args.output_dir, train, validation)))


if __name__ == "__main__":
    main()
