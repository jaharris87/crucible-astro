"""Fixed Phase 2D input, wire, artifact and verification functions.

No producer is imported and no physical evaluation occurs in this module.
The separately compiled native executable owns the reference integration.
"""

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import shutil
import struct
import subprocess
from pathlib import Path
from time import perf_counter, process_time

import numpy as np

PROTOCOL_SHA256 = "966fbff8d2322ae8e6666063f35c1b87cced7d5ccbaf663ccae362613f98fdad"
ANNEX_SHA256 = "697049acca510794eda3149a2d88a11477f49e4724519cb3ba4fef22e7cdb3b1"
INPUT_SHA256 = {
    "development": "b02862988b83b7412a8a53d40868adf5f6b04cf7eca7798b7bebf6789fc31da6",
    "validation": "bc70b3c75bdb8a5046a310de3a13b125a991fcaf165f70631ce79bf5875a9bb9",
}
HEADER = struct.Struct("<8i2d")
MAGIC = 0x43524432
N = 160


def require(condition, message):
    if not condition:
        raise ValueError("trajectory reference: " + message)


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected):
    data = Path(path).read_bytes()
    require(digest_bytes(data) == expected, "artifact identity differs")
    return data


def save_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def numeric(value, shape=None):
    require(
        isinstance(value, np.ndarray) and value.dtype == np.float64,
        "binary64 array required",
    )
    require(shape is None or value.shape == shape, "array shape differs")
    require(np.all(np.isfinite(value)), "nonfinite array")
    return value


def validate_case(case):
    require(
        set(case)
        == {"Y0", "species_Z_A", "source_time", "time", "T9", "rho", "requested_time"},
        "case fields differ",
    )
    y = numeric(case["Y0"], (N,))
    species = np.asarray(case["species_Z_A"])
    require(
        species.shape == (N, 2) and np.issubdtype(species.dtype, np.integer),
        "ordered integer species required",
    )
    require(len({tuple(x) for x in species.tolist()}) == N, "duplicate species")
    z, a = species.T
    require(np.all((a >= 1) & (z >= 0) & (z <= a)), "invalid species")
    require(np.all((y >= 0) & (y <= 1)), "initial state domain")
    t = numeric(case["time"])
    require(
        t.ndim == 1 and len(t) >= 2 and t[0] == 0 and np.all(np.diff(t) > 0),
        "forcing time coverage",
    )
    for key in ("source_time", "T9", "rho"):
        numeric(case[key], t.shape)
    require(
        np.array_equal(case["source_time"] - case["source_time"][0], t),
        "source clock differs",
    )
    require(
        np.all((case["T9"] >= 0.01) & (case["T9"] <= 100)) and np.all(case["rho"] > 0),
        "forcing domain",
    )
    outputs = numeric(case["requested_time"])
    require(
        outputs.ndim == 1
        and len(outputs) >= 2
        and outputs[0] == 0
        and outputs[-1] == 0.01
        and np.all(np.diff(outputs) > 0),
        "requested interval differs",
    )
    require(t[-1] >= outputs[-1], "missing forcing horizon")
    b, q = np.sum(a * y), np.sum(z * y)
    require(b > 0 and np.sum(y) > 0 and q > 0, "composition moment domain")
    return case


def forcing_at(case, time):
    require(
        isinstance(time, (int, float, np.integer, np.floating))
        and not isinstance(time, (bool, np.bool_))
        and np.isfinite(time),
        "finite real forcing time required",
    )
    t = case["time"]
    require(t[0] <= time <= t[-1], "forcing query outside coverage")
    right = int(np.searchsorted(t, time))
    if t[right] == time:
        return np.array([case["T9"][right], case["rho"][right]])
    fraction = (time - t[right - 1]) / (t[right] - t[right - 1])
    return np.array(
        [
            case[k][right - 1] + fraction * (case[k][right] - case[k][right - 1])
            for k in ("T9", "rho")
        ]
    )


def nested_mesh(case, level):
    require(type(level) is int and level in range(4), "unknown mesh level")
    knots = case["time"]
    base = np.unique(
        np.concatenate(
            (
                np.arange(101) * np.float64(1e-4),
                case["requested_time"],
                knots[(knots > 0) & (knots < 0.01)],
            )
        )
    )
    pieces = 2**level
    mesh = np.concatenate(
        [
            left + (right - left) * (np.arange(pieces) / pieces)
            for left, right in zip(base[:-1], base[1:])
        ]
        + [base[-1:]]
    )
    require(
        mesh[0] == 0 and mesh[-1] == 0.01 and np.all(np.diff(mesh) > 0),
        "unrepresentable refinement mesh",
    )
    require(np.all(np.isin(case["requested_time"], mesh)), "mesh missed an output")
    return mesh


def wire_input(case, *, mode, mesh, tight=False, time=0.0, state=None):
    validate_case(case)
    require(type(mode) is int and mode in (0, 1, 2), "unknown native mode")
    require(type(tight) is bool, "tight must be boolean")
    forcing_at(case, time)
    numeric(mesh)
    require(
        mesh.ndim == 1 and len(mesh) > 0 and np.all(np.diff(mesh) > 0),
        "invalid native mesh",
    )
    y = case["Y0"] if state is None else numeric(state, (N,))
    outputs = (
        case["requested_time"] if mode == 1 else np.array([time], dtype=np.float64)
    )
    z, a = case["species_Z_A"].T
    index = int(np.argmax(a * case["Y0"])) + 1
    an, rn = (1e-14, 1e-12) if tight else (1e-13, 1e-11)
    arrays = (z, a, y, case["time"], case["T9"], case["rho"], outputs, mesh)
    return HEADER.pack(
        MAGIC, 1, N, len(case["time"]), len(outputs), len(mesh), mode, index, an, rn
    ) + b"".join(np.asarray(x, dtype="<f8").tobytes() for x in arrays)


def decode_accepted(data):
    width = 3 * N + 8
    require(
        len(data) % (8 * width) == 0 and len(data) > 0,
        "malformed/empty accepted stream",
    )
    rows = np.frombuffer(data, dtype="<f8").reshape(-1, width).copy()
    return {
        "accepted_t": rows[:, 0],
        "Y": rows[:, 1:161],
        "F": rows[:, 161:321],
        "residual": rows[:, 321:481],
        "scalar_diag": rows[:, 481:484],
        "residual_norm": rows[:, 484],
        "residual_l1": rows[:, 485],
        "final_projection_l1": rows[:, 486],
        "cumulative_final_projection_l1": rows[:, 487],
    }


def domain_flags(case, times, states):
    z, a = case["species_Z_A"].T
    flags = np.zeros(len(times), dtype=bool)
    for i, (t, y) in enumerate(zip(times, states)):
        if (
            not np.isfinite(t)
            or not np.all(np.isfinite(y))
            or np.any((y < 0) | (y > 1))
        ):
            continue
        try:
            temp, rho = forcing_at(case, t)
            b, q = np.sum(a * y), np.sum(z * y)
            ye = q / b if b > 0 else np.nan
            flags[i] = (
                np.sum(y) > 0
                and b > 0
                and ye > 0
                and 0.01 <= temp <= 100
                and 1 <= np.log10(rho * ye) < 11
                and 1e3 <= temp * 1e9 <= 1e13
                and 1e-12 <= rho * ye <= 1e15
            )
        except ValueError:
            pass
    return flags


def split_report(report):
    """Separate numeric detail from a strict finite JSON summary."""
    arrays = {}

    def encode(value, key):
        if isinstance(value, np.ndarray):
            require(
                value.dtype.kind in "biuf", "only numeric non-pickle arrays may persist"
            )
            arrays[key] = value
            return {"array": key}
        if isinstance(value, np.generic):
            return encode(value.item(), key)
        if isinstance(value, dict):
            return {k: encode(v, key + "/" + str(k)) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [encode(v, key + "/" + str(i)) for i, v in enumerate(value)]
        if isinstance(value, float) and not np.isfinite(value):
            return {"value": None, "status": "NONFINITE_DIAGNOSTIC"}
        return value

    return encode(report, "report"), arrays


def artifact_report(path, report):
    path = Path(path)
    encoded, arrays = split_report(report)
    npz = path.with_suffix(".npz")
    require(not path.exists() and not npz.exists(), "derived report already exists")
    np.savez(npz, **arrays)
    encoded["array_artifact"] = {
        "path": npz.name,
        "sha256": digest_bytes(npz.read_bytes()),
        "arrays": {
            k: {
                "dtype": v.dtype.str,
                "shape": list(v.shape),
                "sha256": digest_bytes(v.tobytes()),
            }
            for k, v in arrays.items()
        },
    }
    save_json(path, encoded)
    return encoded


def expected_attempts():
    result = {}
    for label in INPUT_SHA256:
        for suffix, mode, level, tight, time in (
            [("control", 0, 0, False, 0.0)]
            + [("L" + str(k), 1, k, False, 0.0) for k in range(4)]
            + [("tight", 1, 3, True, 0.0)]
            + [("J" + str(k), 2, 3, False, t) for k, t in enumerate((0.0, 0.005, 0.01))]
        ):
            result[label + "-" + suffix] = {
                "mode": mode,
                "case": label,
                "level": level,
                "tight": tight,
                "time": time,
            }
    return result


def validate_plan(prepared):
    require(isinstance(prepared.get("attempts"), list), "missing attempt population")
    actual = prepared["attempts"]
    expected = expected_attempts()
    require(
        len(actual) == len(expected)
        and len({s.get("name") for s in actual}) == len(expected),
        "attempt population differs",
    )
    for spec in actual:
        require(spec.get("name") in expected, "unapproved attempt name")
        require(
            all(
                type(spec.get(k)) is type(v) and spec[k] == v
                for k, v in expected[spec["name"]].items()
            ),
            "attempt contract differs",
        )


def prepare(config_path, destination, source_root):
    from crucible.benchmark import load_benchmark

    started, cpu_started = perf_counter(), process_time()
    source_root, destination = Path(source_root).resolve(), Path(destination).resolve()
    config = json.loads(Path(config_path).read_text())
    require(
        set(config) == {"annex", "benchmark_access", "source_config"},
        "prepare config fields differ",
    )
    annex = json.loads(checked(config["annex"], ANNEX_SHA256))
    checked(
        source_root / "experiments/trajectory_reference/PROTOCOL.md", PROTOCOL_SHA256
    )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    require(
        not dirty, "commit the complete scientific source before preparing a campaign"
    )
    require(
        Path(__file__).read_bytes()
        == (source_root / "src/crucible/trajectory_reference.py").read_bytes(),
        "installed preparation module differs from declared source",
    )
    destination.mkdir(parents=True, exist_ok=False)
    inputs = destination / "inputs"
    inputs.mkdir()
    plans, templates = [], {}
    for label, identity in INPUT_SHA256.items():
        entry = annex["cases"][label]
        raw = checked(entry["npz"], identity)
        path = inputs / (label + ".npz")
        path.write_bytes(raw)
        with np.load(path, allow_pickle=False) as file:
            case = validate_case({k: file[k].copy() for k in file.files})
        data = load_benchmark(
            "ccsn-primary-native-rhs-pointwise",
            "0.1.0",
            use="state_training",
            split=entry["role"],
            config=config["benchmark_access"],
        )
        selected = np.flatnonzero(data["record_id"] == entry["initial_record"])
        require(len(selected) == 1, "initial record missing")
        i = selected[0]
        require(
            np.array_equal(data["Y"][i].view(np.uint64), case["Y0"].view(np.uint64))
            and np.array_equal(data["species_Z_A"], case["species_Z_A"]),
            "initial state/species identity differs",
        )
        expected = "inputs/" + label + "-expected-control.bin"
        (destination / expected).write_bytes(
            data["fresh_rhs"][i].astype("<f8").tobytes()
        )
        for name, mode, level, tight, when in (
            [(label + "-control", 0, 0, False, 0.0)]
            + [(label + "-L" + str(k), 1, k, False, 0.0) for k in range(4)]
            + [(label + "-tight", 1, 3, True, 0.0)]
            + [
                (label + "-J" + str(k), 2, 3, False, t)
                for k, t in enumerate((0.0, 0.005, 0.01))
            ]
        ):
            target = "inputs/" + name + ".bin"
            specification = {
                "name": name,
                "mode": mode,
                "case": label,
                "level": level,
                "tight": tight,
                "time": when,
                "input": target,
            }
            if mode != 2 or when == 0.0:
                mesh = nested_mesh(case, level) if mode == 1 else np.array([when])
                (destination / target).write_bytes(
                    wire_input(case, mode=mode, mesh=mesh, tight=tight, time=when)
                )
                specification["input_sha256"] = digest_bytes(
                    (destination / target).read_bytes()
                )
            if mode == 0:
                specification["expected"] = expected
                templates[label] = target
            plans.append(specification)
    loaded = perf_counter()
    # Both exact controls precede all trajectory/diagnostic evaluations.
    plans.sort(key=lambda p: p["mode"])
    native = source_root / "experiments/trajectory_reference/stage_native.py"
    spec = importlib.util.spec_from_file_location("phase2d_stage", native)
    staging = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(staging)
    staging.stage(config["source_config"], destination / "bundle")
    shutil.copy2(
        source_root / "experiments/trajectory_reference/campaign.py",
        destination / "campaign.py",
    )
    immutable = {
        str(p.relative_to(destination)): digest_bytes(p.read_bytes())
        for p in destination.rglob("*")
        if p.is_file()
    }
    git = subprocess.run(
        ["git", "rev-parse", "HEAD", "HEAD^{tree}"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    record = {
        "schema": "crucible.phase2d.prepared.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "annex_sha256": ANNEX_SHA256,
        "source_commit": git[0],
        "source_tree": git[1],
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "attempts": plans,
        "templates": templates,
        "immutable_files": immutable,
        "costs": {
            "input_loading_and_validation_wall_seconds": loaded - started,
            "source_staging_and_hashing_wall_seconds": perf_counter() - loaded,
            "prepare_total_cpu_seconds": process_time() - cpu_started,
            "prepare_total_wall_seconds": perf_counter() - started,
            "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1024 if platform.system() == "Linux" else 1),
        },
    }
    save_json(destination / "prepared.json", record)
    return record


def retained_trajectory_summary(work, requested):
    """Describe complete retained records without certifying process success.

    An interrupted stream may end within a record. Preserve its byte identity,
    count the trailing bytes, and inspect only its complete prefix.
    """
    path = Path(work) / "accepted.bin"
    raw = path.read_bytes()
    width = (3 * N + 8) * 8
    count, trailing = divmod(len(raw), width)
    times = (
        decode_accepted(raw[: count * width])["accepted_t"] if count else np.empty(0)
    )
    occurrences = np.array([np.count_nonzero(times == t) for t in requested])
    return {
        "diagnostic_only": True,
        "accepted_stream_sha256": digest_bytes(raw),
        "complete_records": count,
        "trailing_bytes": trailing,
        "accepted_times": times,
        "last_retained_time": float(times[-1]) if count else None,
        "requested_output_occurrences": occurrences,
        "requested_output_complete": bool(np.all(occurrences == 1)),
    }


def analyze(root):
    from crucible import trajectory_metrics as metrics

    root = Path(root)
    prepared = json.loads((root / "prepared.json").read_text())
    validate_plan(prepared)
    campaign = json.loads((root / "campaign.json").read_text())
    require(
        prepared["protocol_sha256"] == PROTOCOL_SHA256
        and prepared["annex_sha256"] == ANNEX_SHA256,
        "protocol/annex changed",
    )
    require(
        campaign["prepared_sha256"]
        == digest_bytes((root / "prepared.json").read_bytes()),
        "campaign/preparation identity differs",
    )
    checked(root / "bundle/trajectory_driver", campaign["executable_sha256"])
    for name, identity in prepared["immutable_files"].items():
        checked(root / name, identity)
    output = {
        "schema": "crucible.phase2d.verification.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "prepared_sha256": campaign["prepared_sha256"],
        "attempts": {},
        "cases": {},
        "pass": False,
        "verification_source": {
            "reference_sha256": digest_bytes(Path(__file__).read_bytes()),
            "metrics_sha256": digest_bytes(Path(metrics.__file__).read_bytes()),
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    for label in INPUT_SHA256:
        checked(root / "inputs" / (label + ".npz"), INPUT_SHA256[label])
        with np.load(root / "inputs" / (label + ".npz"), allow_pickle=False) as file:
            case = validate_case({k: file[k].copy() for k in file.files})
        z, a = case["species_Z_A"].T
        levels, all_runs = [], {}
        for spec in [s for s in prepared["attempts"] if s["case"] == label]:
            work = root / "attempts" / spec["name"]
            result = {
                "pass": False,
                "mode": spec["mode"],
                "attempted": work.is_dir(),
            }
            if spec["mode"] == 1 and (work / "accepted.bin").exists():
                result["retained_output"] = retained_trajectory_summary(
                    work, case["requested_time"]
                )
            try:
                record = json.loads((work / "attempt.json").read_text())
                result["process"] = record
                result["process_completed"] = record.get("completed") is True
                inventory = {
                    str(p.relative_to(work))
                    for p in work.rglob("*")
                    if p.is_file() and p.name not in {"attempt.json", "attempt.pending"}
                }
                require(
                    inventory == set(record["files"]), "attempt file inventory differs"
                )
                for name, info in record["files"].items():
                    checked(work / name, info["sha256"])
                statuses = (
                    (work / "status.txt").read_text().splitlines()
                    if (work / "status.txt").exists()
                    else []
                )
                native_complete = (
                    record.get("completed") is True
                    and record.get("returncode") == 0
                    and bool(statuses)
                    and statuses[-1] == "SUCCESS"
                )
                result.update(
                    native_complete=native_complete,
                    native_status=statuses[-1] if statuses else "UNAVAILABLE",
                    process=record,
                )
                require(
                    record.get("loaded_library_hashes")
                    and all(record["loaded_library_hashes"].values()),
                    "actual loaded-library identities unavailable",
                )
                if (work / "counters.json").exists():
                    result["counters"] = json.loads(
                        (work / "counters.json").read_text()
                    )
                else:
                    events = work / "counter-events.bin"
                    event_data = events.read_bytes() if events.exists() else b""
                    result["last_counter_checkpoint"] = (
                        np.frombuffer(event_data[-14 * 8 :], dtype="<i8").copy()
                        if len(event_data) >= 14 * 8
                        else None
                    )
                    result["counters_unavailable_reason"] = (
                        "native process did not emit final counters; retained last checkpoint"
                    )
                require(
                    record["executable_sha256"] == campaign["executable_sha256"],
                    "attempt executable differs",
                )
                actual_input = (work / "input.bin").read_bytes()
                if spec["mode"] != 2 or spec["time"] == 0.0:
                    mesh = (
                        nested_mesh(case, spec["level"])
                        if spec["mode"] == 1
                        else np.array([0.0])
                    )
                    require(
                        actual_input
                        == wire_input(
                            case, mode=spec["mode"], mesh=mesh, tight=spec["tight"]
                        ),
                        "native input differs from fixed case/protocol",
                    )
                if spec["mode"] == 0:
                    require(
                        (work / "control.bin").read_bytes()
                        == (root / spec["expected"]).read_bytes(),
                        "control mismatch",
                    )
                    result["pass"] = native_complete
                elif spec["mode"] == 1:
                    rows = decode_accepted((work / "accepted.bin").read_bytes())
                    conditions = (
                        np.frombuffer(
                            (work / "accepted-forcing.bin").read_bytes(), dtype="<f8"
                        )
                        .copy()
                        .reshape(-1, 3)
                    )
                    require(
                        conditions.shape == (len(rows["accepted_t"]), 3)
                        and np.array_equal(conditions[:, 0], rows["accepted_t"]),
                        "accepted forcing/output alignment differs",
                    )
                    expected_conditions = np.array(
                        [forcing_at(case, t) for t in rows["accepted_t"]]
                    )
                    forcing_error = np.abs(conditions[:, 1:] - expected_conditions)
                    # An arithmetic association allowance, not a forcing sensitivity budget.
                    require(
                        np.all(
                            forcing_error
                            <= 16
                            * np.finfo(float).eps
                            * np.maximum(1, np.abs(expected_conditions))
                        ),
                        "actual forcing differs from declared interpolant",
                    )
                    hits = np.isin(rows["accepted_t"], case["time"])
                    require(
                        np.array_equal(
                            conditions[hits, 1:].view(np.uint64),
                            expected_conditions[hits].view(np.uint64),
                        ),
                        "forcing knot bits changed",
                    )
                    requested = case["requested_time"]
                    y = np.full((len(requested), N), np.nan)
                    for j, t in enumerate(requested):
                        found = np.flatnonzero(rows["accepted_t"] == t)
                        if len(found) == 1:
                            y[j] = rows["Y"][found[0]]
                    constraints = metrics.trajectory_constraints(
                        rows["accepted_t"],
                        rows["Y"],
                        rows["F"],
                        rows["residual"],
                        rows["scalar_diag"],
                        a,
                        z,
                        case["Y0"],
                        requested,
                        y,
                        domain_ok={
                            "accepted": domain_flags(
                                case, rows["accepted_t"], rows["Y"]
                            ),
                            "requested": domain_flags(case, requested, y),
                        },
                        final_projection_l1=rows["final_projection_l1"],
                        atol=1e-14 if spec["tight"] else 1e-13,
                        rtol=1e-12 if spec["tight"] else 1e-11,
                    )
                    result.update(
                        rows,
                        requested_t=requested,
                        requested_Y=y,
                        constraints=constraints,
                        accepted_forcing=conditions,
                        forcing_arithmetic_error=forcing_error,
                    )
                    result["pass"] = bool(native_complete and constraints["pass"])
                    all_runs[spec["name"]] = result
                    if not spec["tight"]:
                        levels.append(result)
                else:
                    raw = np.frombuffer(
                        (work / "directional.bin").read_bytes(), dtype="<f8"
                    ).copy()
                    require(raw.size == 27 * 1286, "directional sweep dimensions")
                    sweep = raw.reshape(3, 9, 1286)
                    jmat = np.frombuffer(
                        (work / "jacobian.bin").read_bytes(), dtype="<f8"
                    ).copy()
                    require(jmat.size == N * N, "Jacobian dimensions")
                    jmat = jmat.reshape(N, N, order="F")
                    state = np.frombuffer(
                        actual_input, dtype="<f8", count=N, offset=48 + 2 * N * 8
                    ).copy()
                    directions = metrics.jacobian_directions(state, a, case["Y0"])
                    require(
                        actual_input
                        == wire_input(
                            case,
                            mode=2,
                            mesh=np.array([spec["time"]]),
                            time=spec["time"],
                            state=state,
                        ),
                        "diagnostic input contract differs",
                    )
                    if spec["time"] != 0:
                        finest = all_runs.get(label + "-L3")
                        require(
                            finest is not None, "diagnostic lacks finest trajectory"
                        )
                        selected = finest["requested_Y"][
                            np.flatnonzero(case["requested_time"] == spec["time"])
                        ]
                        require(
                            selected.shape == (1, N)
                            and np.array_equal(
                                state.view(np.uint64), selected[0].view(np.uint64)
                            ),
                            "diagnostic state is not the declared finest output",
                        )
                    checks = []
                    for direction in range(3):
                        block = sweep[direction]
                        require(
                            np.array_equal(block[:, 0], np.full(9, direction + 1))
                            and np.array_equal(block[:, 1], np.arange(1, 10)),
                            "directional sweep order",
                        )
                        jv = jmat @ directions[direction]
                        estimates = np.full((9, N), np.nan)
                        for k, row in enumerate(block):
                            require(
                                row[3] in (0, 1), "invalid directional admissibility"
                            )
                            if not row[3]:
                                continue
                            require(
                                np.array_equal(row[6:166], directions[direction]),
                                "direction definition differs",
                            )
                            bound = (
                                512
                                * np.finfo(float).eps
                                * (np.abs(jmat) @ np.abs(directions[direction]))
                                + 32 * np.finfo(float).tiny
                            )
                            require(
                                np.all(np.abs(jv - row[166:326]) <= bound),
                                "persisted Jv inconsistent",
                            )
                            p1, p2 = row[4:6]
                            require(
                                p1 != 0
                                and p2 != 0
                                and p1 != p2
                                and np.isfinite(p1 + p2),
                                "invalid directional stencil",
                            )
                            w1 = -p2 / (p1 * (p1 - p2))
                            w2 = -p1 / (p2 * (p2 - p1))
                            term1 = w1 * (row[966:1126] - row[806:966])
                            term2 = w2 * (row[1126:1286] - row[806:966])
                            estimates[k] = term1 + term2
                            allowance = (
                                512
                                * np.finfo(float).eps
                                * (np.abs(term1) + np.abs(term2))
                                + 32 * np.finfo(float).tiny
                            )
                            require(
                                np.all(
                                    np.abs(estimates[k] - row[326:486]) <= allowance
                                ),
                                "directional derivative does not match retained F probes",
                            )
                        checks.append(
                            metrics.assess_directional_jacobian(
                                a, jv, estimates, block[:, 3] == 1
                            )
                        )
                    result.update(sweep=sweep, jacobian=jmat, directional_checks=checks)
                    result["pass"] = native_complete and all(c["pass"] for c in checks)
            except (OSError, ValueError, KeyError, IndexError) as exc:
                result["exception"] = str(exc)
            output["attempts"][spec["name"]] = result
        case_report = {"pass": False}
        if len(levels) == 4 and label + "-tight" in all_runs:
            try:
                case_report["refinement"] = metrics.assess_refinement(levels, a, z)
                case_report["nonlinear"] = metrics.compare_nonlinear_controls(
                    case["requested_time"],
                    levels[-1]["requested_Y"],
                    all_runs[label + "-tight"]["requested_Y"],
                    a,
                    z,
                )
                case_report["pass"] = bool(
                    case_report["refinement"]["pass"]
                    and case_report["nonlinear"]["pass"]
                )
            except ValueError as exc:
                case_report["exception"] = str(exc)
        output["cases"][label] = case_report
    output["pass"] = bool(
        campaign.get("complete")
        and all(x["pass"] for x in output["attempts"].values())
        and all(x["pass"] for x in output["cases"].values())
    )
    return output


def reload_report(root):
    """Recompute against raw artifacts in a fresh process; write nothing."""
    root = Path(root)
    saved = json.loads((root / "verification.json").read_text())
    array_manifest = saved.pop("array_artifact")
    payload = checked(root / array_manifest["path"], array_manifest["sha256"])
    import io

    with np.load(io.BytesIO(payload), allow_pickle=False) as file:
        require(
            set(file.files) == set(array_manifest["arrays"]),
            "derived array membership differs",
        )
        arrays = {name: file[name].copy() for name in file.files}
    for name, a in arrays.items():
        identity = array_manifest["arrays"][name]
        require(
            a.dtype.str == identity["dtype"]
            and list(a.shape) == identity["shape"]
            and digest_bytes(a.tobytes()) == identity["sha256"],
            "derived array identity differs",
        )
    recomputed = analyze(root)
    encoded, new_arrays = split_report(recomputed)
    require(
        encoded == saved and set(new_arrays) == set(arrays),
        "recomputed verification differs",
    )
    for name, a in arrays.items():
        b = new_arrays[name]
        require(
            a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes(),
            "recomputed numeric detail differs",
        )
    return recomputed


def compare_campaigns(first_root, repeat_root):
    """Same source/inputs and all declared passes, plus numerical reproduction."""
    from crucible import trajectory_metrics as metrics

    first_root, repeat_root = Path(first_root), Path(repeat_root)
    first, repeat = reload_report(first_root), reload_report(repeat_root)
    p1, p2 = [
        json.loads((root / "prepared.json").read_text())
        for root in (first_root, repeat_root)
    ]
    for key in (
        "source_commit",
        "source_tree",
        "protocol_sha256",
        "annex_sha256",
        "immutable_files",
    ):
        require(p1[key] == p2[key], "clean reproduction source/input identity differs")
    build1, build2 = [
        (root / "bundle/linked-library-hashes.json").read_bytes()
        for root in (first_root, repeat_root)
    ]
    require(build1 == build2, "clean reproduction linked libraries differ")
    result = {
        "schema": "crucible.phase2d.reproduction.v1",
        "pass": False,
        "first_pass": first["pass"],
        "repeat_pass": repeat["pass"],
        "attempts": {},
    }
    for label in INPUT_SHA256:
        with np.load(
            first_root / "inputs" / (label + ".npz"), allow_pickle=False
        ) as file:
            z, a = file["species_Z_A"].T
        for suffix in ("L0", "L1", "L2", "L3", "tight"):
            key = label + "-" + suffix
            left, right = first["attempts"][key], repeat["attempts"][key]
            item = {
                "pass": False,
                "first_pass": left["pass"],
                "repeat_pass": right["pass"],
            }
            if left["pass"] and right["pass"]:
                require(
                    np.array_equal(left["requested_t"], right["requested_t"]),
                    "reproduction grid differs",
                )
                item.update(
                    metrics.assess_reproduction(
                        left["requested_t"],
                        left["requested_Y"],
                        right["requested_Y"],
                        a,
                        z,
                    )
                )
                item["accepted_mesh_identical"] = np.array_equal(
                    left["accepted_t"], right["accepted_t"]
                )
            result["attempts"][key] = item
    result["pass"] = bool(
        first["pass"]
        and repeat["pass"]
        and all(v["pass"] for v in result["attempts"].values())
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("config", type=Path)
    prep.add_argument("destination", type=Path)
    prep.add_argument("--source-root", type=Path, default=Path.cwd())
    check = sub.add_parser("verify")
    check.add_argument("root", type=Path)
    reload = sub.add_parser("reload")
    reload.add_argument("root", type=Path)
    compare = sub.add_parser("compare")
    compare.add_argument("first", type=Path)
    compare.add_argument("repeat", type=Path)
    compare.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.config, args.destination, args.source_root)
    elif args.command == "verify":
        report = analyze(args.root)
        artifact_report(args.root / "verification.json", report)
        print(json.dumps({"pass": report["pass"], "attempts": len(report["attempts"])}))
        if not report["pass"]:
            raise SystemExit(1)
    elif args.command == "reload":
        report = reload_report(args.root)
        print(json.dumps({"reload": "PASS", "numerical_pass": report["pass"]}))
    else:
        report = compare_campaigns(args.first, args.repeat)
        artifact_report(args.output, report)
        print(json.dumps({"reproduction_pass": report["pass"]}))
        if not report["pass"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
