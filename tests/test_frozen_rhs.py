"""Synthetic callable tests with known numeric weights, never model fitting."""

import copy
from dataclasses import replace

import numpy as np
import pytest
import torch

from crucible import frozen_rhs as f
from crucible import mlp_baseline as m
from crucible.integration import integrate_rhs
from crucible.rhs_data import UNITS


def data_contract():
    return {
        "feature_order": ["Y[0:160]", "T9", "rho"],
        "target": "fresh_rhs",
        "shared": {
            "ordered_species": [{"Z": 0, "A": i + 1} for i in range(160)],
            "units": {k: UNITS[k] for k in ("Y", "fresh_rhs", "T9", "rho")},
        },
    }


def source(conditions=lambda t: (2.0, 1e6)):
    m.configure_cpu()
    model = m.MLP()
    with torch.no_grad():
        for p in model.parameters():
            p.zero_()
        model.weights[0][0, 0] = 0.5
        model.weights[0][1, -2] = 0.75
        model.weights[0][2, -1] = 0.5
        model.weights[0][3, 159] = -0.25
        for i in range(4):
            model.weights[1][i, i] = 1
            model.weights[2][i, i] = -2 if i % 2 == 0 else 3
        model.biases[2].copy_(torch.linspace(-0.5, 0.5, 160, dtype=torch.float64))
    xs = np.ones(162, dtype=np.float64) * 2
    xs[-1] = 1e6
    ys = np.linspace(0.1, 3, 160, dtype=np.float64)
    return f.ModelRHS(model, xs, ys, f.rhs_contract(data_contract()), conditions)


def test_hand_derived_scaling_signed_native_output_and_all_species():
    rhs = source()
    y = np.linspace(-1, 1, 160, dtype=np.float64)
    old = y.copy()
    p = rhs(0.0, y)
    expected = np.linspace(-0.5, 0.5, 160, dtype=np.float64)
    expected[:4] += np.array([-2, 3, -2, 3]) * np.tanh(
        np.tanh([0.5 * y[0] / 2, 0.75, 0.5, -0.25 * y[159] / 2])
    )
    expected *= rhs.y_scale
    np.testing.assert_allclose(p, expected, rtol=2e-15, atol=2e-15)
    assert p.shape == (160,) and p.dtype == np.float64
    assert (p < 0).any() and (p > 0).any()
    assert y.tobytes() == old.tobytes()
    assert p.tobytes() == rhs(1.0, y).tobytes()
    features = np.concatenate((y, [2.0, 1e6]))[None, :]
    one, _ = m._physical_predictions(rhs.model, features, rhs.x_scale, rhs.y_scale)
    assert p.tobytes() == one[0].tobytes()
    changed = y.copy()
    changed[159] += 1
    assert rhs(0.0, changed)[3] != p[3]


def test_analytic_conditioning_uses_each_supplied_time_without_time_feature():
    calls = []

    def conditions(t):
        calls.append(t)
        return (2 + 0.1 * np.sin(t), 1e6 * (1 + 0.05 * np.cos(t)))

    rhs = source(conditions)
    y = np.zeros(160, dtype=np.float64)
    for t in [0.0, 0.3, 1.0]:
        actual = rhs(t, y)
        t9, rho = conditions(t)
        features = np.concatenate((y, [t9, rho]))[None, :]
        expected, _ = m._physical_predictions(
            rhs.model, features, rhs.x_scale, rhs.y_scale
        )
        assert actual.tobytes() == expected[0].tobytes()
    assert calls == [0.0, 0.0, 0.3, 0.3, 1.0, 1.0]


@pytest.mark.parametrize(
    "value",
    [
        np.zeros(159),
        np.zeros((1, 160)),
        np.zeros(160, dtype=np.float32),
        np.zeros(160, dtype=np.complex128),
        [0.0] * 160,
        np.full(160, np.nan),
        np.full(160, np.inf),
    ],
)
def test_bad_states_refuse(value):
    rhs = source()
    assert np.isfinite(rhs(0.0, np.zeros(160))).all()
    with pytest.raises(ValueError):
        rhs(0.0, value)


@pytest.mark.parametrize("t", [np.nan, np.inf, 1j, [0.0], True, np.float32(1)])
def test_bad_time_refuses(t):
    with pytest.raises(ValueError):
        source()(t, np.zeros(160))


@pytest.mark.parametrize(
    "conditions",
    [
        (0.0, 1.0),
        (1.0, -1.0),
        (np.nan, 1.0),
        (1.0, np.inf),
        (1.0,),
        (1.0, 2.0, 3.0),
        (1j, 2.0),
        (np.float32(2), 1.0),
        np.array(1.0),
        np.ones((1, 2)),
    ],
)
def test_bad_conditions_refuse(conditions):
    with pytest.raises(ValueError):
        source(lambda t: conditions)(0.0, np.zeros(160))


@pytest.mark.parametrize(
    "change", ["units", "features", "target", "duplicate", "dimension"]
)
def test_semantic_contract_mutations(change):
    original = data_contract()
    good = f.rhs_contract(original)
    bad = copy.deepcopy(original)
    if change == "units":
        bad["shared"]["units"]["fresh_rhs"] = "mass_fraction/s"
    elif change == "features":
        bad["feature_order"] = ["T9", "rho", "Y[0:160]"]
    elif change == "target":
        bad["target"] = "finite_step"
    elif change == "duplicate":
        bad["shared"]["ordered_species"][0] = bad["shared"]["ordered_species"][1]
    else:
        bad["shared"]["ordered_species"].pop()
    with pytest.raises(ValueError):
        f.rhs_contract(bad)
    reordered = copy.deepcopy(original)
    reordered["shared"]["ordered_species"].reverse()
    assert f.rhs_contract(reordered) != good


@pytest.mark.parametrize(
    "field,value",
    [
        ("state_unit", "mass_fraction"),
        ("rate_unit", "mass_fraction/s"),
        ("time_unit", "ms"),
        ("conditions", ()),
    ],
)
def test_model_constructor_refuses_wrong_semantics(field, value):
    good = source()
    with pytest.raises(ValueError):
        f.ModelRHS(
            good.model,
            good.x_scale,
            good.y_scale,
            replace(good.contract, **{field: value}),
            good.conditions,
        )


def test_frozen_loader_pins_bytes_before_using_model(tmp_path, monkeypatch):
    for name in ("model.npz", "model.json"):
        (tmp_path / name).write_bytes(b"counterfeit")
    called = []
    monkeypatch.setattr(m, "load_model", lambda *args: called.append(args))
    with pytest.raises(ValueError, match="model.npz identity"):
        f.load_frozen_rhs(tmp_path, data_contract(), lambda t: (2.0, 1e6))
    assert called == []


def test_nonfinite_network_output_refuses_and_saved_scales_are_owned():
    rhs = source()
    assert not rhs.x_scale.flags.writeable and not rhs.y_scale.flags.writeable
    with torch.no_grad():
        rhs.model.biases[2][0] = torch.inf
    with pytest.raises(ValueError, match="nonfinite"):
        rhs(0.0, np.zeros(160))


def test_wrapper_rejects_same_shape_reordered_species_before_model_call(monkeypatch):
    rhs = source()
    monkeypatch.setattr(
        rhs.model, "forward", lambda x: pytest.fail("model must not run")
    )
    reordered = replace(rhs.contract, components=rhs.contract.components[::-1])
    with pytest.raises(ValueError, match="identities, units or conditions mismatch"):
        integrate_rhs(
            rhs,
            np.zeros(160),
            np.array([0.0, 1.0]),
            contract=rhs.contract,
            expected_contract=reordered,
            rtol=1e-6,
            atol=1e-9,
        )


def test_non_cpu_model_refuses_before_numpy_conversion():
    rhs = source()
    # Meta tensors exercise the device check without a GPU or device transfer.
    model = m.MLP().to("meta")
    with pytest.raises(ValueError, match="model must reside on CPU"):
        f.ModelRHS(model, rhs.x_scale, rhs.y_scale, rhs.contract, rhs.conditions)
