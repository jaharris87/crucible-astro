"""Callable nuclear full-state specialization of Qiosk's separate vector source.

The integrated coordinates are physical molar Y. Saved input/target scales are
optimization transforms, not a change of ODE coordinates. Phase 2C checks this
adapter pointwise only; its existence grants no astrophysical rollout authority.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from crucible import mlp_baseline as mlp
from crucible.integration import RHSContract, checked_vector
from crucible.rhs_data import UNITS

FROZEN_SHA256 = {
    "model.npz": "4d048163a5bd4d256ad7e6ed90be15a48321587525ab94e33ae253bb6cfdd793",
    "model.json": "3d11aca1efcff2e025fa196bf00352ac42477a44eba39f8cd464ac8c3188740e",
    "predictions.npz": "70fc334c873a07791fdcad0a25e7e51f4a71e4235cbd43140ed234613a2c84db",
}


def _require(ok, message):
    if not ok:
        raise ValueError("frozen RHS: " + message)


def _scalar(value, name):
    a = np.asarray(value)
    _require(
        a.ndim == 0
        and a.dtype.kind in "if"
        and (a.dtype.kind != "f" or a.dtype == np.float64),
        name + " must be a real binary64 scalar",
    )
    result = float(a)
    _require(math.isfinite(result), "nonfinite " + name)
    return result


def rhs_contract(data_contract):
    """Derive ordered callable semantics from an independently checked data contract."""
    _require(
        data_contract.get("feature_order") == ["Y[0:160]", "T9", "rho"]
        and data_contract.get("target") == "fresh_rhs",
        "feature order or target",
    )
    shared = data_contract["shared"]
    _require(
        all(
            shared["units"].get(k) == UNITS[k] for k in ("Y", "fresh_rhs", "T9", "rho")
        ),
        "state/rate/conditioning units",
    )
    species = shared["ordered_species"]
    _require(
        isinstance(species, list)
        and len(species) == 160
        and all(
            isinstance(s, dict)
            and all(type(s.get(k)) is int for k in ("Z", "A"))
            and 0 <= s["Z"] <= s["A"]
            and s["A"] > 0
            for s in species
        ),
        "ordered 160 species identities",
    )
    components = tuple(
        json.dumps(s, sort_keys=True, separators=(",", ":"), allow_nan=False)
        for s in species
    )
    _require(len(set(components)) == 160, "duplicate species identity")
    return RHSContract(
        components=components,
        state_unit=UNITS["Y"],
        rate_unit=UNITS["fresh_rhs"],
        time_unit="s",
        conditions=(("T9", UNITS["T9"]), ("rho", UNITS["rho"])),
    )


@dataclass(frozen=True)
class ModelRHS:
    """One loaded source plus fixed scales and explicitly prescribed conditions.

    Synthetic tests construct known weights and declared semantics directly; no
    fit or PCA is involved. The frozen-artifact entry point below additionally
    pins file bytes and validates compatibility against the supplied data contract.
    """

    model: mlp.MLP
    x_scale: np.ndarray
    y_scale: np.ndarray
    contract: RHSContract
    conditions: object

    def __post_init__(self):
        self.contract.validate()
        _require(len(self.contract.components) == 160, "state dimension")
        _require(
            self.contract.state_unit == UNITS["Y"]
            and self.contract.rate_unit == UNITS["fresh_rhs"]
            and self.contract.time_unit == "s"
            and self.contract.conditions == (("T9", "GK"), ("rho", "g/cm^3")),
            "physical Y/s/seconds/T9/rho contract",
        )
        _require(callable(self.conditions), "conditions must be callable")
        _require(type(self.model) is mlp.MLP, "incompatible model type")
        for name, shape in mlp.SHAPES.items():
            if name in ("x_scale", "y_scale"):
                a = getattr(self, name)
                _require(
                    isinstance(a, np.ndarray)
                    and a.dtype == np.float64
                    and a.shape == shape
                    and np.isfinite(a).all()
                    and (a > 0).all(),
                    "invalid " + name,
                )
                a = a.copy()
                a.flags.writeable = False
                object.__setattr__(self, name, a)
        for name, a in mlp.model_arrays(self.model).items():
            _require(
                a.dtype == np.float64
                and a.shape == mlp.SHAPES[name]
                and np.isfinite(a).all(),
                "invalid model array " + name,
            )
        _require(
            all(p.device.type == "cpu" for p in self.model.parameters()),
            "model must reside on CPU",
        )
        self.model.eval()
        self.model.requires_grad_(False)

    def __call__(self, t, y):
        t = _scalar(t, "time")
        y = checked_vector(y, 160, "model state")
        conditions = self.conditions(t)
        _require(
            isinstance(conditions, (tuple, list, np.ndarray)) and len(conditions) == 2,
            "conditions must return (T9, rho)",
        )
        t9, rho = (_scalar(v, name) for v, name in zip(conditions, ("T9", "rho")))
        _require(t9 > 0 and rho > 0, "conditions must be positive")
        features = np.empty((1, 162), dtype=np.float64)
        features[0, :160] = y
        features[0, -2:] = (t9, rho)
        # Exactly the one-row Phase 2B operations, including saved inverse scaling.
        prediction, _ = mlp._physical_predictions(
            self.model, features, self.x_scale, self.y_scale
        )
        _require(
            prediction.dtype == np.float64
            and prediction.shape == (1, 160)
            and np.isfinite(prediction).all(),
            "invalid native RHS output",
        )
        return prediction[0].copy()


def load_frozen_rhs(directory, expected_contract, conditions):
    """Load only the accepted 2B weights against a loader-derived expected contract."""
    directory = Path(directory)
    mlp.configure_cpu()
    for name in ("model.npz", "model.json"):
        _require(
            mlp.sha256(directory / name) == FROZEN_SHA256[name], name + " identity"
        )
    model, xs, ys, _ = mlp.load_model(directory, expected_contract)
    return ModelRHS(model, xs, ys, rhs_contract(expected_contract), conditions)
