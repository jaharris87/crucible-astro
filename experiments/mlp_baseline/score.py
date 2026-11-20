"""Score local Phase 2B predictions without fitting or final-test access.

Run from the repository checkout with its locked environment, for example:
python -B experiments/mlp_baseline/score.py ACCESS.json RUN_DIR train mlp
Real records, predictions and complete reports remain local.
"""

import argparse
import hashlib
import io
import json
import platform
import resource
import sys
import time
from pathlib import Path

import numpy as np

from crucible import mlp_baseline as mlp
from crucible import rhs_data as wire
from crucible.benchmark import NAME, VERSION, load_benchmark
from crucible.native_fidelity import evaluate_native


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sample_documents(data, values, prediction_id):
    """Join predictions in exact accepted membership order, without new features."""
    target = data["fresh_rhs"]
    if values.dtype != np.float64 or values.shape != target.shape:
        raise ValueError("physical binary64 prediction shape required")
    metadata = data["metadata"]
    if metadata["split"] not in ("train", "validation"):
        raise ValueError("Phase 2B model-based final-test scoring is forbidden")
    reference_rows, prediction_rows = [], []
    for i, rid in enumerate(data["record_id"]):
        identity = {
            "sample_id": str(rid),
            "history_id": str(data["particle0"][i]),
            "group_id": str(data["group"][i]),
            "category": str(data["category"][i]),
            "time_s": float(data["time"][i]),
        }
        reference_rows.append(
            dict(identity, Y=data["Y"][i].tolist(), F=target[i].tolist())
        )
        # Whole-vector nonfinite predictions become explicit failed attempts.
        finite = bool(np.isfinite(values[i]).all())
        prediction_rows.append(
            dict(identity, F=values[i].tolist() if finite else None, success=finite)
        )
    common = {
        "schema": "crucible.rhs_samples.v1",
        "dataset_id": f"{NAME}:{VERSION}:{metadata['split']}",
        "species": metadata["ordered_species"],
        "units": {"Y": "molar_abundance_Y", "F": "molar_abundance_Y/s", "time": "s"},
        "network_convention": "closed_full_inventory_no_aux_Q_over_B",
    }
    return dict(common, samples=reference_rows), dict(
        common, prediction_id=prediction_id, samples=prediction_rows
    )


def bound_predictions(run_dir, split, data, receipt):
    """Verify completed-run provenance without fitting or rerunning inference."""
    result_bytes = (run_dir / "result.json").read_bytes()
    result = wire.json_load(result_bytes)
    wire.require(
        result.get("schema") == "crucible.phase2b-mlp-result.v1"
        and result.get("protocol") == mlp.PROTOCOL
        and isinstance(result.get("selection"), dict)
        and result["selection"].get("complete") is True,
        "completed Phase 2B result schema/protocol/selection required",
    )
    artifacts = result["artifact_sha256"]

    def read_artifact(name):
        return wire.checked(
            {"path": str((run_dir / name).resolve()), "sha256": artifacts[name]}
        )

    manifest = wire.json_load(read_artifact("model.json"))
    read_artifact("model.npz")
    wire.require(
        manifest.get("schema") == mlp.SCHEMA
        and manifest.get("protocol") == mlp.PROTOCOL
        and manifest.get("npz_sha256") == artifacts["model.npz"]
        and manifest.get("selection") == result["selection"]
        and manifest.get("bindings") == result["bindings"]
        and manifest.get("contract") == result["contract"],
        "completed result/model identity or contract mismatch",
    )
    contract = result["contract"]
    shared = contract["shared"]
    rows = len(data["record_id"])
    order_digest = hashlib.sha256(
        mlp._json_bytes(data["record_id"].tolist())
    ).hexdigest()
    wire.require(
        contract.get("feature_order") == ["Y[0:160]", "T9", "rho"]
        and contract.get("target") == "fresh_rhs"
        and {"ordered_species", "overlay_sha256", "payload_sha256", "membership_sha256"}
        <= set(shared)
        and all(data["metadata"].get(k) == v for k, v in shared.items())
        and rows > 0
        and result["prediction_rows"][split] == rows
        and contract["roles"][split]
        == {"rows": rows, "record_order_sha256": order_digest},
        "completed result differs from loaded data/species/role/order",
    )
    prediction_bytes = read_artifact("predictions.npz")
    receipt.update(
        predictions_sha256=artifacts["predictions.npz"],
        model_run={
            "result_sha256": hashlib.sha256(result_bytes).hexdigest(),
            "result_schema": result["schema"],
            "protocol": result["protocol"],
            "selection": result["selection"],
            "model_npz_sha256": artifacts["model.npz"],
            "model_manifest_sha256": artifacts["model.json"],
            "weights_sha256": manifest["weights_sha256"],
        },
    )
    # Load exactly the verified snapshot, even if the original path changes later.
    with np.load(io.BytesIO(prediction_bytes), allow_pickle=False) as arrays:
        values = arrays[f"{split}_prediction"]
        if not np.array_equal(arrays[f"{split}_record_id"], data["record_id"]):
            raise ValueError("prediction record order mismatch")
        if arrays[f"{split}_target"].tobytes() != data["fresh_rhs"].tobytes():
            raise ValueError("prediction target bits mismatch")
    return values


def score(access, run_dir, split, predictor, *, config_path):
    """One complete model/split report using the bound D-026 scorer unchanged."""
    if split not in ("train", "validation") or predictor not in ("mlp", "zero"):
        raise ValueError("only Phase 2B train/validation and mlp/zero are allowed")
    run_dir = Path(run_dir)
    out = run_dir / "scores"
    out.mkdir(exist_ok=True)
    receipt_path = out / f"{predictor}-{split}-receipt.json"
    report_path = out / f"{predictor}-{split}.json"
    if receipt_path.exists() or report_path.exists():
        raise FileExistsError("retain prior scoring attempts; use a new run directory")
    receipt = {
        "status": "RUNNING",
        "split": split,
        "predictor": predictor,
        "adapter_source_sha256": sha256(__file__),
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "scorer_source_sha256": sha256(
            sys.modules[evaluate_native.__module__].__file__
        ),
        "config_file_sha256": sha256(config_path),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    start = time.perf_counter()
    try:
        data = load_benchmark(
            NAME, VERSION, use="rhs_training", split=split, config=access
        )
        receipt["load_seconds"] = time.perf_counter() - start
        metadata = data["metadata"]
        successor = metadata["accepted_scoring_successor"]
        if receipt["scorer_source_sha256"] != successor["source_sha256"]:
            raise ValueError("actual scorer differs from accepted D-026 source")
        if receipt["config_file_sha256"] != metadata["scoring_configuration_sha256"]:
            raise ValueError("scoring configuration differs from accepted binding")
        receipt.update(
            accepted_scoring_successor=successor,
            original_scoring_source_sha256=metadata["original_scoring_source_sha256"],
            overlay_sha256=metadata["overlay_sha256"],
            payload_sha256=metadata["payload_sha256"],
            membership_sha256=metadata["membership_sha256"],
            states=len(data["record_id"]),
            histories=len(set(data["particle0"].tolist())),
            groups=len(set(data["group"].tolist())),
        )
        if predictor == "zero":
            values = np.zeros_like(data["fresh_rhs"])
        else:
            values = bound_predictions(run_dir, split, data, receipt)
        reference, prediction = sample_documents(
            data, values, f"phase2b:{predictor}:{split}"
        )
        scoring = time.perf_counter()
        report = evaluate_native(
            json.loads(Path(config_path).read_bytes()), reference, prediction
        )
        receipt["scoring_seconds"] = time.perf_counter() - scoring
        writing = time.perf_counter()
        with report_path.open("x") as stream:
            json.dump(report, stream, allow_nan=False, separators=(",", ":"))
            stream.write("\n")
        receipt.update(
            status="PASS",
            write_seconds=time.perf_counter() - writing,
            report_bytes=report_path.stat().st_size,
            report_sha256=sha256(report_path),
            arithmetic=report["arithmetic"],
            summary=report["summary"],
        )
    except BaseException as exc:
        receipt.update(status="FAILED", exception=type(exc).__name__, message=str(exc))
        raise
    finally:
        receipt.update(
            elapsed_seconds=time.perf_counter() - start,
            peak_rss_native_units=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            peak_rss_unit="bytes" if sys.platform == "darwin" else "KiB",
        )
        receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("access", type=Path)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("split", choices=("train", "validation"))
    parser.add_argument("predictor", choices=("mlp", "zero"))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/native_fidelity/primary_benchmark.json"),
    )
    args = parser.parse_args()
    result = score(
        args.access, args.run_dir, args.split, args.predictor, config_path=args.config
    )
    print(json.dumps({k: v for k, v in result.items() if k != "summary"}, indent=2))


if __name__ == "__main__":
    main()
