"""Hand-computable controls for the local-only Phase 2B scoring adapter."""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

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
