"""Private all-train/validation callable equivalence; never fit or integrate a model."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import resource
import sys
import time
import traceback
from pathlib import Path

import numpy as np

from crucible import benchmark
from crucible import frozen_rhs as f
from crucible import mlp_baseline as m

PROTOCOL_SHA256 = "35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2"


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n")


def check(access, output, source_root):
    """Retain every prediction/violation locally, with a preflight failure receipt."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    report = {
        "schema": "crucible.phase2c-frozen-callable.v1",
        "status": "RUNNING",
        "protocol_sha256": PROTOCOL_SHA256,
        "completed_roles": [],
        "last_record_index": None,
        "roles": {},
    }
    write_json(output / "report.json", report)
    arrays = {}
    try:
        m.configure_cpu()
        config = m._json_read(access)
        if set(config) != {"benchmark_access", "frozen_run"}:
            raise ValueError("private access requires benchmark_access and frozen_run")
        run = Path(config["frozen_run"])
        original_hashes = {k: m.sha256(run / k) for k in f.FROZEN_SHA256}
        if original_hashes != f.FROZEN_SHA256:
            raise ValueError("frozen model/manifest/prediction identity mismatch")
        report["original_sha256"] = original_hashes
        root = Path(source_root)
        report["source_sha256"] = {
            name: m.sha256(root / name)
            for name in (
                "src/crucible/frozen_rhs.py",
                "src/crucible/integration.py",
                "src/crucible/mlp_baseline.py",
                "experiments/integration/check_frozen.py",
                "pyproject.toml",
                "uv.lock",
            )
        }
        report["installed_module_sha256"] = {
            "frozen_rhs": m.sha256(f.__file__),
            "mlp_baseline": m.sha256(m.__file__),
        }
        if (
            report["installed_module_sha256"]["frozen_rhs"]
            != report["source_sha256"]["src/crucible/frozen_rhs.py"]
        ):
            raise ValueError("installed adapter differs from declared source")
        if (
            report["installed_module_sha256"]["mlp_baseline"]
            != report["source_sha256"]["src/crucible/mlp_baseline.py"]
        ):
            raise ValueError("installed inference differs from declared source")
        report["environment"] = {
            k: importlib.metadata.version(k)
            for k in ("numpy", "torch", "scipy", "h5py")
        }
        report["environment"].update(
            python=platform.python_version(),
            platform=platform.platform(),
            machine=platform.machine(),
            cpu_threads=1,
        )
        data = {}
        loading_start = time.perf_counter()
        for role in ("train", "validation"):
            data[role] = benchmark.load_benchmark(
                benchmark.NAME,
                benchmark.VERSION,
                use="rhs_training",
                split=role,
                config=config["benchmark_access"],
            )
        report["loading_seconds"] = time.perf_counter() - loading_start
        setup_start = time.perf_counter()
        contract = m.data_contract(data["train"], data["validation"])
        condition_values = [2.0, 1e6]
        condition_calls = []

        def conditions(t):
            condition_calls.append((t, *condition_values))
            return tuple(condition_values)

        rhs = f.load_frozen_rhs(run, contract, conditions)
        original_weights = m.weights_hash(rhs.model)
        report["data_contract_sha256"] = hashlib.sha256(
            m._json_bytes(contract)
        ).hexdigest()
        report["setup_seconds"] = time.perf_counter() - setup_start
        with np.load(run / "model.npz", allow_pickle=False) as saved_model:
            for key, value in {
                **m.model_arrays(rhs.model),
                "x_scale": rhs.x_scale,
                "y_scale": rhs.y_scale,
            }.items():
                old = saved_model[key]
                if (
                    old.dtype != value.dtype
                    or old.shape != value.shape
                    or old.tobytes() != value.tobytes()
                ):
                    raise ValueError("loaded model/scale bytes differ: " + key)
        report["weights_scales_bitwise"] = True
        arrays["y_scale"] = rhs.y_scale
        with np.load(run / "predictions.npz", allow_pickle=False) as saved:
            for role in ("train", "validation"):
                role_start = time.perf_counter()
                records = data[role]
                x, _ = m._data(records, role)
                old_ids = saved[role + "_record_id"]
                if old_ids.tolist() != records["record_id"].tolist():
                    raise ValueError("saved record order differs: " + role)
                batch, _ = m._physical_predictions(
                    rhs.model, x, rhs.x_scale, rhs.y_scale
                )
                original = saved[role + "_prediction"]
                batch_bits = (
                    batch.dtype == original.dtype
                    and batch.shape == original.shape
                    and batch.tobytes() == original.tobytes()
                )
                count = len(x)
                single = np.full((count, 160), np.nan, dtype=np.float64)
                direct = np.full_like(single, np.nan)
                failures = []
                first_condition = len(condition_calls)
                callback_start = time.perf_counter()
                for i in range(count):
                    report["last_record_index"] = i
                    condition_values[:] = (
                        float(records["T9"][i]),
                        float(records["rho"][i]),
                    )
                    try:
                        single[i] = rhs(records["time"][i], records["Y"][i])
                        reference, _ = m._physical_predictions(
                            rhs.model, x[i : i + 1], rhs.x_scale, rhs.y_scale
                        )
                        direct[i] = reference[0]
                    except Exception as exc:
                        failures.append(
                            {
                                "index": i,
                                "type": type(exc).__name__,
                                "message": str(exc),
                            }
                        )
                elapsed = time.perf_counter() - callback_start
                actual_conditions = np.array(
                    condition_calls[first_condition:], dtype=np.float64
                )
                expected_conditions = np.column_stack(
                    (records["time"], records["T9"], records["rho"])
                )
                condition_bits = (
                    actual_conditions.shape == expected_conditions.shape
                    and actual_conditions.tobytes() == expected_conditions.tobytes()
                )
                finite = np.isfinite(single) & np.isfinite(direct)
                with np.errstate(over="ignore", invalid="ignore", under="ignore"):
                    normalized_difference = np.abs((single - batch) / rhs.y_scale)
                    allowance = (
                        2048
                        * np.finfo(np.float64).eps
                        * np.maximum(1, np.abs(batch / rhs.y_scale))
                    )
                bad = (
                    (~finite)
                    | (~np.isfinite(normalized_difference))
                    | (normalized_difference > allowance)
                )
                singleton_bits = single.tobytes() == direct.tobytes()
                role_report = {
                    "records": count,
                    "components": int(single.size),
                    "saved_batch_bitwise": batch_bits,
                    "singleton_reference_bitwise": singleton_bits,
                    "time_conditions_bitwise": condition_bits,
                    "failed_records": failures,
                    "violating_components": int(bad.sum()),
                    "violating_records": int(bad.any(axis=1).sum()),
                    "max_normalized_difference": float(normalized_difference.max())
                    if np.isfinite(normalized_difference).all()
                    else None,
                    "max_allowance_fraction": float(
                        (normalized_difference / allowance).max()
                    )
                    if np.isfinite(normalized_difference).all()
                    else None,
                    "callback_seconds_including_direct_reference": elapsed,
                    "total_seconds": time.perf_counter() - role_start,
                    "passed": bool(
                        batch_bits
                        and singleton_bits
                        and condition_bits
                        and not failures
                        and not bad.any()
                    ),
                }
                report["roles"][role] = role_report
                report["completed_roles"].append(role)
                for key, value in {
                    "single": single,
                    "single_reference": direct,
                    "batch": batch,
                    "record_id": records["record_id"],
                    "conditions": actual_conditions,
                    "expected_conditions": expected_conditions,
                    "normalized_difference": normalized_difference,
                    "violations": bad,
                }.items():
                    arrays[role + "_" + key] = value
                np.savez_compressed(output / "predictions.npz", **arrays)
                write_json(output / "report.json", report)
        if m.weights_hash(rhs.model) != original_weights:
            raise ValueError("model weights changed during callable check")
        if {k: m.sha256(run / k) for k in f.FROZEN_SHA256} != original_hashes:
            raise ValueError("original frozen files changed")
        report["originals_unchanged"] = True
        report["array_sha256"] = {k: m.array_hash(v) for k, v in arrays.items()}
        report["predictions_sha256"] = m.sha256(output / "predictions.npz")
        report["status"] = (
            "PASS" if all(r["passed"] for r in report["roles"].values()) else "FAIL"
        )
    except BaseException as exc:
        report["status"] = "FAIL"
        report["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        (output / "exception.txt").write_text(traceback.format_exc())
        if arrays:
            np.savez_compressed(output / "partial-predictions.npz", **arrays)
    finally:
        report["total_seconds"] = time.perf_counter() - start
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report["process_peak_rss_bytes"] = (
            rss if sys.platform == "darwin" else rss * 1024
        )
        report["artifact_bytes_excluding_report"] = sum(
            p.stat().st_size
            for p in output.iterdir()
            if p.is_file() and p.name != "report.json"
        )
        write_json(output / "report.json", report)
    return report


def reload(directory):
    """Fresh-process exact serialization and callable discrepancy recomputation."""
    directory = Path(directory)
    report = m._json_read(directory / "report.json")
    if m.sha256(directory / "predictions.npz") != report["predictions_sha256"]:
        raise ValueError("callable predictions NPZ identity")
    with np.load(directory / "predictions.npz", allow_pickle=False) as saved:
        if set(saved.files) != set(report["array_sha256"]):
            raise ValueError("callable array names")
        for name in saved.files:
            if m.array_hash(saved[name]) != report["array_sha256"][name]:
                raise ValueError("callable array identity: " + name)
        for role in ("train", "validation"):
            single, direct, batch = (
                saved[role + "_" + key]
                for key in ("single", "single_reference", "batch")
            )
            r = report["roles"][role]
            if (single.tobytes() == direct.tobytes()) != r[
                "singleton_reference_bitwise"
            ]:
                raise ValueError("singleton bit equivalence report")
            difference = saved[role + "_normalized_difference"]
            computed = np.abs((single - batch) / saved["y_scale"])
            if computed.tobytes() != difference.tobytes():
                raise ValueError("normalized difference recomputation")
            if float(difference.max()) != r["max_normalized_difference"]:
                raise ValueError("singleton discrepancy report")
            allowance = (
                2048
                * np.finfo(np.float64).eps
                * np.maximum(1, np.abs(batch / saved["y_scale"]))
            )
            bad = (
                (~np.isfinite(single))
                | (~np.isfinite(direct))
                | (~np.isfinite(difference))
                | (difference > allowance)
            )
            if not np.array_equal(bad, saved[role + "_violations"]):
                raise ValueError("callable violations recomputation")
            if (
                int(bad.sum()) != r["violating_components"]
                or int(bad.any(axis=1).sum()) != r["violating_records"]
            ):
                raise ValueError("singleton violation report")
            if float((difference / allowance).max()) != r["max_allowance_fraction"]:
                raise ValueError("singleton allowance report")
            if (
                saved[role + "_conditions"].tobytes()
                == saved[role + "_expected_conditions"].tobytes()
            ) != r["time_conditions_bitwise"]:
                raise ValueError("time/condition report")
            if not np.isfinite(batch).all():
                raise ValueError("nonfinite saved batch")
    return {"serialization": "PASS", "status": report["status"]}


def compare(first, second):
    """Numerical reproduction, separately from serialization and callable tolerance."""
    a, b = (Path(p) for p in (first, second))
    ra, rb = (m._json_read(p / "report.json") for p in (a, b))
    reload(a)
    reload(b)
    for key in ("status", "protocol_sha256", "original_sha256", "data_contract_sha256"):
        if ra[key] != rb[key]:
            raise ValueError("callable reproduction binding/outcome: " + key)
    with (
        np.load(a / "predictions.npz", allow_pickle=False) as aa,
        np.load(b / "predictions.npz", allow_pickle=False) as bb,
    ):
        if set(aa.files) != set(bb.files):
            raise ValueError("callable reproduction array names")
        for name in aa.files:
            x, y = aa[name], bb[name]
            if x.dtype != y.dtype or x.shape != y.shape:
                raise ValueError("callable reproduction dtype/shape")
            matches = (
                np.allclose(x, y, atol=1e-12, rtol=1e-12, equal_nan=True)
                if x.dtype.kind == "f"
                else np.array_equal(x, y)
            )
            if not matches:
                raise ValueError("callable reproduction values: " + name)
    return {"reproduction": "PASS", "rtol": 1e-12, "atol": 1e-12}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "reload", "compare"))
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        if len(args.paths) != 2 or args.source_root is None:
            parser.error("check needs access.json output_dir --source-root")
        result = check(*args.paths, args.source_root)
    elif args.command == "reload":
        result = reload(*args.paths)
    else:
        result = compare(*args.paths)
    print(json.dumps(result, allow_nan=False, sort_keys=True))
    if result.get("status") == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
