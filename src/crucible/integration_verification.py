"""Fixed Phase 2C mathematical fixtures, metrics and retained campaign evidence.

This module does not load models or physical data. Arrays use (time, component).
"""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

import numpy as np

from crucible.integration import RHSContract, integrate_rhs

PROTOCOL_SHA256 = "35bddc1edbffc1a60a86a863e161417aca0543a9d4754a94d3b18e2cb91fc6b2"
LEVELS = (("L0", 1e-4, 1e-7, 5e-4), ("L1", 1e-6, 1e-9, 5e-6), ("L2", 1e-8, 1e-11, 5e-8))


@dataclass(frozen=True)
class Fixture:
    name: str
    contract: RHSContract
    initial: np.ndarray
    times: np.ndarray
    rhs: object
    oracle: object
    description: str


def exchange_oracle(t):
    t = np.asarray(t, dtype=np.float64)
    return np.column_stack(
        (1 / 3 + (2 / 3) * np.exp(-3 * t), -(2 / 3) * np.expm1(-3 * t))
    )


def forced_oracle(t):
    t = np.asarray(t, dtype=np.float64)
    return np.column_stack((np.exp(-t), np.sin(t) + np.exp(-1000 * t)))


def exchange_rhs(t, y):
    return np.array((-2 * y[0] + y[1], 2 * y[0] - y[1]), dtype=np.float64)


def forced_rhs(t, y):
    # Analytic external conditions evaluated at the actual callback time.
    return np.array((-y[0], -1000 * (y[1] - np.sin(t)) + np.cos(t)), dtype=np.float64)


def singularity_oracle(t):
    t = np.asarray(t, dtype=np.float64)
    truth = np.full((len(t), 1), np.nan, dtype=np.float64)
    defined = t < 1
    truth[defined, 0] = 1 / (1 - t[defined])
    return truth


def fixtures():
    return (
        Fixture(
            "exchange",
            RHSContract(("a", "b"), "dimensionless", "1/s"),
            np.array([1.0, 0.0]),
            np.linspace(0.0, 5.0, 201),
            exchange_rhs,
            exchange_oracle,
            "a'=-2*a+b; b'=2*a-b; coefficients 2/s,1/s",
        ),
        Fixture(
            "forced_stiff",
            RHSContract(
                ("u", "v"),
                "dimensionless",
                "1/s",
                conditions=(("sin(t/(1 s))", "1"), ("cos(t/(1 s))", "1")),
            ),
            np.ones(2),
            np.union1d(
                np.linspace(0.0, 2 * np.pi, 257),
                np.arange(101, dtype=np.float64) * 1e-4,
            ),
            forced_rhs,
            forced_oracle,
            "u'=-u; v'=-1000*(v-sin(t))+cos(t); rates 1/s,1000/s",
        ),
    )


def error_metrics(solution, oracle, present, amplitude_scale=2.0):
    """Metrics over every available, mathematically defined entry; expose coverage.

    Missing outputs always count in coverage and block positive acceptance. The
    singularity oracle is deliberately undefined at/after t=1.
    """
    defined = np.all(np.isfinite(oracle), axis=1)
    valid = present & defined
    errors = np.full_like(oracle, np.nan)
    errors[valid] = solution[valid] - oracle[valid]
    summary = {
        "requested_rows": len(present),
        "present_rows": int(present.sum()),
        "oracle_defined_rows": int(defined.sum()),
        "scored_rows": int(valid.sum()),
        "missing_rows": int((~present).sum()),
    }
    if not np.any(valid):
        return errors, summary
    e = errors[valid]
    absolute = np.abs(e)

    # hypot/reduced scaling avoids squaring overflow in failure diagnostics.
    def rms(a, axis=None):
        scale = np.max(np.abs(a), axis=axis, keepdims=True)
        safe = np.where(scale == 0, 1.0, scale)
        value = safe * np.sqrt(np.mean((a / safe) ** 2, axis=axis, keepdims=True))
        return np.squeeze(value, axis=axis) if axis is not None else float(value.item())

    per_max = absolute.max(axis=0)
    per_rms = rms(e, axis=0)
    truth = oracle[valid]
    nonzero = truth != 0
    relative = e[nonzero] / truth[nonzero]
    zero_errors = absolute[~nonzero]
    summary.update(
        {
            "component_rms": per_rms.tolist(),
            "component_max_abs": per_max.tolist(),
            "component_final_error": (errors[-1].tolist() if valid[-1] else None),
            "whole_rms": rms(e),
            "whole_max_abs": float(absolute.max()),
            "max_vector_l2": float(np.max(np.hypot.reduce(e, axis=1))),
            "relative_nonzero_count": int(nonzero.sum()),
            "exact_zero_count": int((~nonzero).sum()),
            "relative_nonzero_rms": rms(relative) if relative.size else None,
            "relative_nonzero_max_abs": float(np.max(np.abs(relative)))
            if relative.size
            else None,
            "zero_max_abs_error": float(zero_errors.max())
            if zero_errors.size
            else None,
            "zero_rms_error": rms(zero_errors) if zero_errors.size else None,
        }
    )
    if amplitude_scale is not None:
        summary.update(
            {
                "amplitude_scale": amplitude_scale,
                "component_amplitude_scaled_rms": (per_rms / amplitude_scale).tolist(),
                "component_amplitude_scaled_max_abs": (
                    per_max / amplitude_scale
                ).tolist(),
                "whole_amplitude_scaled_rms": rms(e) / amplitude_scale,
                "whole_amplitude_scaled_max_abs": float(absolute.max())
                / amplitude_scale,
            }
        )
    return errors, summary


def exchange_constraints(result, atol):
    def measures(values):
        return {
            "max_balance_error": float(np.max(np.abs(values.sum(axis=1) - 1))),
            "minimum_component": float(values.min()),
            "balance_violations": int(
                np.count_nonzero(np.abs(values.sum(axis=1) - 1) > 1e-11)
            ),
            "positivity_violations": int(np.count_nonzero(values < -5 * atol)),
        }

    output = (
        measures(result.output_y[result.present]) if np.any(result.present) else None
    )
    accepted = (
        measures(result.accepted_y)
        if result.accepted_y is not None and np.all(np.isfinite(result.accepted_y))
        else None
    )
    passed = all(
        x is not None
        and x["balance_violations"] == 0
        and x["positivity_violations"] == 0
        for x in (output, accepted)
    )
    return {"output": output, "accepted": accepted, "passed": passed}


def refinement(metrics):
    errors = [m.get("whole_max_abs") for m in metrics]
    if len(errors) != 3 or any(e is None for e in errors):
        return {
            "errors": errors,
            "passed": False,
            "unavailable_reason": "three finite error summaries unavailable; retain failed attempts",
        }
    adjacent = [errors[i + 1] <= 2 * errors[i] + 1e-11 for i in range(2)]
    reduction = errors[2] <= 0.2 * errors[0] or (
        errors[2] <= 1e-11 and errors[0] <= 1e-11
    )
    return {
        "errors": errors,
        "adjacent_ratios": [
            errors[i + 1] / errors[i] if errors[i] else None for i in range(2)
        ],
        "nonmonotonic": [errors[i + 1] > errors[i] for i in range(2)],
        "roundoff_plateau": all(e <= 1e-11 for e in errors),
        "adjacent_passed": adjacent,
        "L2_vs_L0_passed": reduction,
        "passed": all(adjacent) and reduction,
    }


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )


def _arrays(result, oracle, errors):
    arrays = {
        "requested_t": result.requested_t,
        "output_y": result.output_y,
        "present": result.present,
        "oracle": oracle,
        "errors": errors,
        "oracle_defined": np.all(np.isfinite(oracle), axis=1),
        "event_t": result.event_t,
    }
    for key in ("accepted_t", "accepted_y", "last_trial_y"):
        if getattr(result, key) is not None:
            arrays[key] = getattr(result, key)
    return arrays


def _save_attempt(directory, fixture, level, result, limit, atol, expected):
    persistence_start = perf_counter()
    oracle = fixture.oracle(fixture.times)
    amplitude_scale = None if fixture.name == "singularity" else 2.0
    errors, metrics = error_metrics(
        result.output_y, oracle, result.present, amplitude_scale
    )
    arrays = _arrays(result, oracle, errors)
    path = directory / f"{fixture.name}-{level}.npz"
    np.savez(path, **arrays)
    constraint = (
        exchange_constraints(result, atol)
        if fixture.name.startswith("exchange")
        else None
    )
    if expected == "complete":
        passed = (
            result.full_success
            and np.all(result.present)
            and all(x <= limit for x in metrics.get("component_max_abs", [np.inf]))
            and all(x <= limit for x in metrics.get("component_rms", [np.inf]))
            and metrics.get("whole_rms", np.inf) <= limit
            and metrics.get("whole_max_abs", np.inf) <= limit
            and (constraint is None or constraint["passed"])
        )
    elif expected == "terminal_event":
        passed = (
            result.outcome == expected
            and result.status == 1
            and not result.full_success
            and len(result.event_t) == 1
            and abs(result.event_t[0] - 0.5) <= 1e-12
            and result.accepted_t is not None
            and abs(result.accepted_t[-1] - 0.5) <= 1e-12
            and np.any(~result.present)
            and np.all(~result.present[fixture.times > 0.5])
        )
    else:
        numerical_failure = (
            result.outcome == "solver_failure" and result.status == -1
        ) or (
            result.outcome == "invalid_callback_output"
            and result.exception is not None
            and result.exception["message"] == "callback RHS must be finite"
        )
        passed = (
            not result.full_success
            and numerical_failure
            and np.any(~result.present)
            and (result.accepted_t is None or result.accepted_t[-1] < fixture.times[-1])
        )
    metadata = {
        "id": f"{fixture.name}-{level}",
        "expected": expected,
        "passed": bool(passed),
        "equations": fixture.description,
        "contract": asdict(fixture.contract),
        "initial": fixture.initial.tolist(),
        "rtol": next(x[1] for x in LEVELS if x[0] == level),
        "atol": atol,
        "absolute_limit": limit,
        "metrics": metrics,
        "constraints": constraint,
        "outcome": result.outcome,
        "full_success": result.full_success,
        "status": result.status,
        "message": result.message,
        "diagnostics": result.diagnostics,
        "exception": result.exception,
        "last_trial_t": result.last_trial_t,
        "last_trial_semantics": "trial callback, not accepted horizon",
        "achieved_horizon": result.accepted_t[-1].item()
        if result.accepted_t is not None
        else None,
        "integration_seconds": result.elapsed_seconds,
        "peak_rss_bytes": peak_rss_bytes(),
        "artifact": {
            "file": path.name,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "arrays": {
                k: {
                    "dtype": v.dtype.str,
                    "shape": list(v.shape),
                    "bytes": v.nbytes,
                    "sha256": hashlib.sha256(v.tobytes()).hexdigest(),
                }
                for k, v in arrays.items()
            },
        },
    }
    metadata["persistence_seconds"] = perf_counter() - persistence_start
    with (directory / "attempts.log").open("a") as stream:
        stream.write(
            f"{metadata['id']}: {result.outcome}; expected={expected}; passed={passed}; "
            f"status={result.status}; message={result.message!r}\n"
        )
    return metadata


def peak_rss_bytes():
    # macOS reports bytes; Linux reports KiB. This is a cumulative process peak.
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def _git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def run_campaign(
    output_dir, *, protocol_path, lock_path, label="accepted-campaign", source_root=None
):
    """Persist all eight fixed attempts; output_dir must not already exist."""
    total_start = perf_counter()
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": 1,
        "label": label,
        "state": "incomplete",
        "attempts": [],
        "stage_seconds": {},
        "peak_rss_semantics": "cumulative process high-water mark",
    }
    manifest_path = directory / "manifest.json"
    _json(manifest_path, manifest)
    (directory / "attempts.log").write_text(
        f"label={label}; campaign started; no overwrite\n"
    )
    setup_start = perf_counter()
    try:
        # Keep dependency import in the measured loading/setup stage.
        import scipy.integrate  # noqa: F401

        if sha256(protocol_path) != PROTOCOL_SHA256:
            raise ValueError("accepted protocol SHA256 mismatch")
        versions = {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "torch")
        }
        expected_versions = {"numpy": "2.5.5", "scipy": "1.18.1", "torch": "2.9.1"}
        # The pinned Linux CPU wheel uses the local-version suffix +cpu.
        checked_versions = {**versions, "torch": versions["torch"].removesuffix("+cpu")}
        if checked_versions != expected_versions:
            raise ValueError(f"protocol library versions mismatch: {versions}")
        root = Path.cwd() if source_root is None else Path(source_root).resolve()
        for name in ("integration.py", "integration_verification.py"):
            if sha256(root / "src" / "crucible" / name) != sha256(
                Path(__file__).with_name(name)
            ):
                raise ValueError(f"installed/source file identity mismatch: {name}")
        manifest["identities"] = {
            "protocol_sha256": PROTOCOL_SHA256,
            "lock_sha256": sha256(lock_path),
            "source_commit": _git(root, "rev-parse", "HEAD"),
            "source_tree": _git(root, "rev-parse", "HEAD^{tree}"),
            "source_status": _git(root, "status", "--porcelain"),
            "source_files": {
                f: sha256(root / f)
                for f in (
                    "src/crucible/integration.py",
                    "src/crucible/integration_verification.py",
                )
            },
            "python": sys.version,
            "executable": sys.executable,
            "libraries": versions,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "thread_environment": {
                k: os.environ.get(k)
                for k in (
                    "OMP_NUM_THREADS",
                    "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS",
                )
            },
            "distribution_metadata_sha256": {
                name: hashlib.sha256(
                    importlib.metadata.distribution(name).read_text("RECORD").encode()
                ).hexdigest()
                for name in versions
            },
            "wheel_archive_identity": "unavailable after installation; distribution RECORD hashes retained",
        }
        if sys.version_info[:2] != (3, 12):
            raise ValueError("protocol requires Python 3.12")
        manifest["stage_seconds"]["loading_setup"] = perf_counter() - setup_start
        manifest["setup_peak_rss_bytes"] = peak_rss_bytes()
        positive = fixtures()
        # Oracle constraints are independent of numerical integration.
        truth = positive[0].oracle(positive[0].times)
        manifest["exchange_oracle_constraints"] = {
            "max_balance_error": float(np.max(np.abs(truth.sum(axis=1) - 1))),
            "minimum_component": float(truth.min()),
        }

        def attempt(fixture, level, rtol, atol, limit, expected, event=None):
            manifest["active_attempt"] = f"{fixture.name}-{level}"
            _json(manifest_path, manifest)
            with (directory / "attempts.log").open("a") as stream:
                stream.write(f"starting {manifest['active_attempt']}\n")
            result = integrate_rhs(
                fixture.rhs,
                fixture.initial,
                fixture.times,
                contract=fixture.contract,
                expected_contract=fixture.contract,
                rtol=rtol,
                atol=atol,
                terminal_event=event,
            )
            manifest["attempts"].append(
                _save_attempt(directory, fixture, level, result, limit, atol, expected)
            )
            manifest["active_attempt"] = None
            _json(manifest_path, manifest)

        for fixture in positive:
            for level, rtol, atol, limit in LEVELS:
                attempt(fixture, level, rtol, atol, limit, "complete")
        exchange = positive[0]
        terminal = Fixture(
            "exchange_terminal",
            exchange.contract,
            exchange.initial,
            exchange.times,
            exchange.rhs,
            exchange.oracle,
            exchange.description,
        )
        attempt(
            terminal, "L1", 1e-6, 1e-9, None, "terminal_event", lambda t, y: t - 0.5
        )
        singular = Fixture(
            "singularity",
            RHSContract(("z",), "dimensionless", "1/s"),
            np.ones(1),
            np.linspace(0.0, 2.0, 201),
            lambda t, y: y * y,
            singularity_oracle,
            "z'=z*z; z(0)=1; truth undefined at/after 1 s",
        )
        attempt(singular, "L1", 1e-6, 1e-9, None, "failure")
        manifest["refinement"] = {
            f.name: refinement(
                [
                    a["metrics"]
                    for a in manifest["attempts"]
                    if a["id"].startswith(f.name + "-L")
                ]
            )
            for f in positive
        }
        manifest["passed"] = (
            all(a["passed"] for a in manifest["attempts"])
            and all(r["passed"] for r in manifest["refinement"].values())
            and manifest["exchange_oracle_constraints"]["max_balance_error"] <= 1e-11
            and manifest["exchange_oracle_constraints"]["minimum_component"] >= 0
        )
        manifest["state"] = "complete"
    except BaseException as exc:
        manifest["operational_failure"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        with (directory / "attempts.log").open("a") as stream:
            stream.write(f"operational failure: {type(exc).__name__}: {exc}\n")
        manifest["passed"] = False
        raise
    finally:
        if "loading_setup" not in manifest["stage_seconds"]:
            manifest["stage_seconds"]["loading_setup"] = perf_counter() - setup_start
        manifest["stage_seconds"]["integration"] = sum(
            a["integration_seconds"] for a in manifest["attempts"]
        )
        manifest["stage_seconds"]["persistence"] = sum(
            a["persistence_seconds"] for a in manifest["attempts"]
        )
        manifest["stage_seconds"]["total"] = perf_counter() - total_start
        manifest["peak_rss_bytes"] = peak_rss_bytes()
        manifest["artifact_bytes_excluding_manifest"] = sum(
            p.stat().st_size
            for p in directory.iterdir()
            if p != manifest_path and p.is_file()
        )
        _json(manifest_path, manifest)
    return manifest


def reload_campaign(directory):
    """Verify file and exact dtype/shape/bytes, then recompute same-array metrics."""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    for attempt in manifest["attempts"]:
        artifact = attempt["artifact"]
        path = directory / artifact["file"]
        if (
            sha256(path) != artifact["sha256"]
            or path.stat().st_size != artifact["bytes"]
        ):
            raise ValueError("NPZ file identity mismatch")
        with np.load(path, allow_pickle=False) as saved:
            if set(saved.files) != set(artifact["arrays"]):
                raise ValueError("array membership mismatch")
            for name, identity in artifact["arrays"].items():
                value = saved[name]
                if (
                    value.dtype.str != identity["dtype"]
                    or list(value.shape) != identity["shape"]
                    or value.nbytes != identity["bytes"]
                    or hashlib.sha256(value.tobytes()).hexdigest() != identity["sha256"]
                ):
                    raise ValueError("array dtype/shape/byte identity mismatch")
            errors, metrics = error_metrics(
                saved["output_y"],
                saved["oracle"],
                saved["present"],
                attempt["metrics"].get("amplitude_scale"),
            )
            if (
                errors.tobytes() != saved["errors"].tobytes()
                or metrics != attempt["metrics"]
            ):
                raise ValueError("recomputed errors/metrics mismatch")
    return {
        "verified_attempts": len(manifest["attempts"]),
        "state": manifest["state"],
        "passed": manifest.get("passed", False),
    }


def compare_campaigns(first, second):
    """Compare repeated numerical arrays at the accepted 1e-12 tolerances."""
    reload_campaign(first)
    reload_campaign(second)
    left = json.loads((Path(first) / "manifest.json").read_text())
    right = json.loads((Path(second) / "manifest.json").read_text())
    if left["state"] != "complete" or right["state"] != "complete":
        raise ValueError("cannot reproduce an incomplete campaign")
    for key in (
        "protocol_sha256",
        "lock_sha256",
        "source_commit",
        "source_tree",
        "source_files",
        "libraries",
    ):
        if left["identities"][key] != right["identities"][key]:
            raise ValueError(f"campaign identity mismatch: {key}")
    if len(left["attempts"]) != len(right["attempts"]):
        raise ValueError("attempt count mismatch")
    exact = {"requested_t", "present", "oracle_defined", "event_t", "accepted_t"}
    for a, b in zip(left["attempts"], right["attempts"], strict=True):
        for key in (
            "id",
            "expected",
            "passed",
            "outcome",
            "full_success",
            "status",
            "contract",
        ):
            if a[key] != b[key]:
                raise ValueError(f"attempt classification mismatch: {key}")
        with (
            np.load(Path(first) / a["artifact"]["file"], allow_pickle=False) as x,
            np.load(Path(second) / b["artifact"]["file"], allow_pickle=False) as y,
        ):
            if set(x.files) != set(y.files):
                raise ValueError("reproduced array membership mismatch")
            # Grids/masks are exact; numeric states/errors use declared tolerance.
            for key in x.files:
                if (
                    x[key].dtype != y[key].dtype
                    or x[key].shape != y[key].shape
                    or not (
                        np.array_equal(x[key], y[key], equal_nan=True)
                        if key in exact
                        else np.allclose(
                            x[key], y[key], atol=1e-12, rtol=1e-12, equal_nan=True
                        )
                    )
                ):
                    raise ValueError(f"reproduced array mismatch: {key}")
    return {"compared_attempts": len(left["attempts"]), "atol": 1e-12, "rtol": 1e-12}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("output_dir")
    run.add_argument("--protocol", required=True)
    run.add_argument("--lock", required=True)
    run.add_argument("--label", default="accepted-campaign")
    run.add_argument("--source-root", default=None)
    reload = commands.add_parser("reload")
    reload.add_argument("directory")
    compare = commands.add_parser("compare")
    compare.add_argument("first")
    compare.add_argument("second")
    args = parser.parse_args()
    if args.command == "run":
        result = run_campaign(
            args.output_dir,
            protocol_path=args.protocol,
            lock_path=args.lock,
            label=args.label,
            source_root=args.source_root,
        )
        print(json.dumps({"state": result["state"], "passed": result["passed"]}))
        return 0 if result["passed"] else 1
    if args.command == "reload":
        print(json.dumps(reload_campaign(args.directory)))
    else:
        print(json.dumps(compare_campaigns(args.first, args.second)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
