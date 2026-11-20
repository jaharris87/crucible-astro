"""Hand-computable controls for the local-only Phase 2B scoring adapter."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path

import numpy as np
import pytest

from crucible import mlp_baseline as mlp
from crucible import native_fidelity

SPEC = importlib.util.spec_from_file_location(
    "mlp_score", Path(__file__).parents[1] / "experiments/mlp_baseline/score.py"
)
scoring = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scoring)


@pytest.fixture
def sample_data(tmp_path, monkeypatch):
    # A test-only loader stand-in. These are mathematical sentinels, not real
    # records or a coherently rewritten qualification fixture.
    config = Path(__file__).parents[1] / "configs/native_fidelity/synthetic_config.json"
    species = json.loads(config.read_bytes())["species"]
    data = {
        "fresh_rhs": np.array([[2.0, 0.0], [-2.0, 1.0]]),
        "Y": np.array([[1.0, 0.0], [0.0, 0.25]]),
        "record_id": np.array(["first", "second"]),
        "particle0": np.array([7, 9]),
        "group": np.array([2, 3]),
        "category": np.array(["mathematical", "mathematical"]),
        "time": np.array([0.0, 1.0]),
        "metadata": {
            "split": "validation",
            "ordered_species": species,
            "accepted_scoring_successor": {
                "source_sha256": scoring.sha256(native_fidelity.__file__),
                "adoption_receipt": "synthetic-test-binding",
            },
            "scoring_configuration_sha256": scoring.sha256(config),
            "original_scoring_source_sha256": "test-only-predecessor",
            "overlay_sha256": "test-only-overlay",
            "payload_sha256": "test-only-payload",
            "membership_sha256": "test-only-membership",
        },
    }
    monkeypatch.setattr(scoring, "load_benchmark", lambda *a, **k: data)
    return data, config, tmp_path


def bind_result(data, root):
    """Public two-species adapter sentinel plus an unfitted epoch-zero artifact.

    This loader stand-in verifies scoring provenance and arithmetic independently;
    it does not claim these synthetic predictions came from model inference.
    """
    selection = {"complete": True, "epoch": 0, "untrained": True}
    contract = {
        "shared": {k: v for k, v in data["metadata"].items() if k != "split"},
        "roles": {
            "validation": {
                "rows": len(data["record_id"]),
                "record_order_sha256": hashlib.sha256(
                    mlp._json_bytes(data["record_id"].tolist())
                ).hexdigest(),
            }
        },
        "feature_order": ["Y[0:160]", "T9", "rho"],
        "target": "fresh_rhs",
    }
    bindings = {"synthetic": "scoring-adapter-control"}
    mlp._save_model(
        root, mlp.MLP(), np.ones(162), np.ones(160), contract, bindings, selection
    )
    result = {
        "schema": "crucible.phase2b-mlp-result.v1",
        "protocol": mlp.PROTOCOL,
        "selection": selection,
        "contract": contract,
        "bindings": bindings,
        "prediction_rows": {"validation": len(data["record_id"])},
        "artifact_sha256": {
            name: scoring.sha256(root / name)
            for name in ("model.npz", "model.json", "predictions.npz")
        },
        "runtime_seconds": 0.0,
        "extra_resource_field": "incidental fields remain permitted",
    }
    (root / "result.json").write_text(json.dumps(result))
    return result


def save_predictions(data, root, values):
    np.savez(
        root / "predictions.npz",
        validation_record_id=data["record_id"],
        validation_target=data["fresh_rhs"],
        validation_prediction=values,
    )


def failed_receipt(root):
    receipt = json.loads((root / "scores/mlp-validation-receipt.json").read_bytes())
    assert receipt["status"] == "FAILED"
    assert not (root / "scores/mlp-validation.json").exists()
    return receipt


def test_adapter_order_sign_and_explicit_nonfinite_failure(sample_data):
    data, _, _ = sample_data
    values = np.array([[-3.0, 4.0], [np.nan, 0.0]])
    ref, pred = scoring.sample_documents(data, values, "analytic")
    assert [r["sample_id"] for r in ref["samples"]] == ["first", "second"]
    assert ref["samples"][1]["F"] == [-2.0, 1.0]
    assert pred["samples"][0]["F"] == [-3.0, 4.0]
    assert pred["samples"][1]["F"] is None
    assert pred["samples"][1]["success"] is False
    assert set(pred["samples"][0]) == {
        "sample_id",
        "history_id",
        "group_id",
        "category",
        "time_s",
        "F",
        "success",
    }


def test_adapter_rejects_final_test(sample_data):
    data, config, root = sample_data
    data["metadata"]["split"] = "test"
    with pytest.raises(ValueError, match="final-test"):
        scoring.sample_documents(data, np.zeros((2, 2)), "forbidden")
    with pytest.raises(ValueError, match="only Phase 2B"):
        scoring.score("unused", root, "test", "zero", config_path=config)


def test_complete_adapter_has_independent_math_oracle(sample_data):
    data, config, root = sample_data
    np.savez(
        root / "predictions.npz",
        validation_record_id=data["record_id"],
        validation_target=data["fresh_rhs"],
        validation_prediction=np.array([[1.0, 0.0], [-2.0, 0.0]]),
    )
    bind_result(data, root)
    receipt = scoring.score("unused", root, "validation", "mlp", config_path=config)
    report = json.loads((root / "scores/mlp-validation.json").read_bytes())
    # A=(1,4): errors=(-1,0,0,-4), so RMS=sqrt(17/4). Relative
    # errors on nonzero labels are (1/2,0,1), giving sqrt(5/12).
    assert report["summary"]["all"]["physical_absolute_rms"]["value"] == pytest.approx(
        (17 / 4) ** 0.5
    )
    assert report["summary"]["nonzero"]["relative_rms"]["value"] == pytest.approx(
        (5 / 12) ** 0.5
    )
    assert report["summary"]["zero"]["zero_target_nonzero_predictions"] == 0
    for profile in report["summary"]["all"]["profiles"].values():
        assert profile["record_attained"] == 0
        assert profile["record_failed"] == 0
    assert len(report["records"]) == 2
    assert all(len(r["components"]) == 2 for r in report["records"])
    assert set(report["strata"]["history_id"]) == {"7", "9"}
    assert receipt["status"] == "PASS"
    assert receipt["model_run"]["result_sha256"] == scoring.sha256(root / "result.json")
    assert receipt["model_run"]["model_npz_sha256"] == scoring.sha256(
        root / "model.npz"
    )
    assert receipt["model_run"]["model_manifest_sha256"] == scoring.sha256(
        root / "model.json"
    )
    assert receipt["model_run"]["selection"]["complete"] is True
    assert receipt["report_sha256"] == scoring.sha256(
        root / "scores/mlp-validation.json"
    )
    with pytest.raises(FileExistsError, match="retain prior scoring attempts"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)


@pytest.mark.parametrize(
    "defect, message", [("order", "record order"), ("target", "target bits")]
)
def test_prediction_join_refuses_same_shape_corruption(sample_data, defect, message):
    data, config, root = sample_data
    ids = data["record_id"].copy()
    target = data["fresh_rhs"].copy()
    if defect == "order":
        ids = ids[::-1]
    else:
        target[0, 1] = -0.0  # Even target zero signs retain original label bits.
    np.savez(
        root / "predictions.npz",
        validation_record_id=ids,
        validation_target=target,
        validation_prediction=np.zeros((2, 2)),
    )
    bind_result(data, root)
    with pytest.raises(ValueError, match=message):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    receipt = json.loads((root / "scores/mlp-validation-receipt.json").read_bytes())
    assert receipt["status"] == "FAILED"
    assert receipt["message"].endswith("mismatch")


def test_wrong_scorer_source_is_not_blessed_by_loader(sample_data):
    data, config, root = sample_data
    data["metadata"]["accepted_scoring_successor"]["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="actual scorer differs"):
        scoring.score("unused", root, "validation", "zero", config_path=config)


def test_mlp_requires_completed_result(sample_data):
    data, config, root = sample_data
    save_predictions(data, root, data["fresh_rhs"].copy())
    with pytest.raises(FileNotFoundError, match="result.json"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


@pytest.mark.parametrize("defect", ["incomplete", "schema", "protocol"])
def test_incomplete_or_incompatible_run_refuses(sample_data, defect):
    data, config, root = sample_data
    save_predictions(data, root, data["fresh_rhs"].copy())
    result = bind_result(data, root)
    if defect == "incomplete":
        result["selection"]["complete"] = False
    else:
        result[defect] = "different"
    (root / "result.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="completed Phase 2B result"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


def test_substituted_predictions_refuse_before_samples(sample_data, monkeypatch):
    data, config, root = sample_data
    save_predictions(data, root, np.zeros_like(data["fresh_rhs"]))
    result = bind_result(data, root)
    save_predictions(data, root, data["fresh_rhs"].copy())
    assert (
        scoring.sha256(root / "predictions.npz")
        != result["artifact_sha256"]["predictions.npz"]
    )
    monkeypatch.setattr(
        scoring, "sample_documents", lambda *a: pytest.fail("samples constructed")
    )
    with pytest.raises(ValueError, match="checksum mismatch: predictions.npz"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


@pytest.mark.parametrize("name", ["model.npz", "model.json"])
def test_changed_model_artifact_refuses(sample_data, name):
    data, config, root = sample_data
    save_predictions(data, root, data["fresh_rhs"].copy())
    bind_result(data, root)
    with (root / name).open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="checksum mismatch: " + name):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


@pytest.mark.parametrize("defect", ["selection", "contract", "bindings", "model_npz"])
def test_result_manifest_inconsistency_refuses(sample_data, defect):
    data, config, root = sample_data
    save_predictions(data, root, data["fresh_rhs"].copy())
    result = bind_result(data, root)
    manifest_path = root / "model.json"
    manifest = json.loads(manifest_path.read_bytes())
    if defect == "model_npz":
        manifest["npz_sha256"] = "0" * 64
    else:
        manifest[defect] = {"different": True}
    manifest_path.write_text(json.dumps(manifest))
    result["artifact_sha256"]["model.json"] = scoring.sha256(manifest_path)
    (root / "result.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="result/model identity or contract mismatch"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


@pytest.mark.parametrize("defect", ["metadata", "rows", "order", "empty"])
def test_loaded_role_contract_mismatch_refuses(sample_data, defect):
    data, config, root = sample_data
    save_predictions(data, root, data["fresh_rhs"].copy())
    result = bind_result(data, root)
    if defect == "metadata":
        data["metadata"]["payload_sha256"] = "changed"
    elif defect == "rows":
        result["prediction_rows"]["validation"] += 1
        (root / "result.json").write_text(json.dumps(result))
    elif defect == "order":
        data["record_id"] = data["record_id"][::-1]
    else:
        for key, value in list(data.items()):
            if isinstance(value, np.ndarray):
                data[key] = value[:0]
    with pytest.raises(ValueError, match="loaded data/species/role/order"):
        scoring.score("unused", root, "validation", "mlp", config_path=config)
    failed_receipt(root)


def test_zero_comparator_independent_of_model_and_result(sample_data):
    _, config, root = sample_data
    receipt = scoring.score("unused", root, "validation", "zero", config_path=config)
    assert receipt["status"] == "PASS"
    assert "model_run" not in receipt and "predictions_sha256" not in receipt
    assert not (root / "model.npz").exists()
    assert not (root / "result.json").exists()


def test_prediction_load_uses_verified_snapshot(sample_data, monkeypatch):
    data, config, root = sample_data
    save_predictions(data, root, np.zeros_like(data["fresh_rhs"]))
    result = bind_result(data, root)
    load = np.load

    def replace_after_verified_read(file, **kwargs):
        assert isinstance(file, io.BytesIO)
        save_predictions(data, root, data["fresh_rhs"].copy())
        return load(file, **kwargs)

    monkeypatch.setattr(scoring.np, "load", replace_after_verified_read)
    receipt = scoring.score("unused", root, "validation", "mlp", config_path=config)
    assert receipt["predictions_sha256"] == result["artifact_sha256"]["predictions.npz"]
    assert receipt["predictions_sha256"] != scoring.sha256(root / "predictions.npz")
    report = json.loads((root / "scores/mlp-validation.json").read_bytes())
    assert report["summary"]["all"]["profiles"]["1%"]["record_attained"] == 0
