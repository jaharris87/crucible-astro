"""Prepare and run only the frozen D-038 diagnostic plan.

Preparation is offline. Execution requires separate scientific/producer authority;
this module never builds a producer. The execution host needs only the stdlib.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import platform
import resource
import shutil
import struct
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANNEX_SHA256 = "dbb954afac144d9305a87e483c0c08833a8cdf2487d390f2d6532e5e72a814eb"
PROTOCOL_SHA256 = "ea722cbabf71d79453a30c35f6f07de7a2c065fe14a9a2e1f442160ada4be7a1"
NEWTON_Y_SHA256 = "5d571931e428b4ede04e61c7d3b8bb0d940d3fabb35da0e8363e1cc5b4ce4c39"
STATES = ("development-initial", "validation-initial", "development-newton300")
NC = (683, 1345, 16, 4)
NB = (1862, 4860, 53, 19)
MAX_RHS = 104209
COUNTERS = {
    "rhs",
    "coefficient",
    "eos",
    "screening",
    "weak",
    "jacobian",
    "lu",
    "linear_solve",
    "newton",
    "retry",
    "step_attempt",
    "projection",
    "probe",
    "accepted",
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


common = load_module("phase2d_common_campaign", HERE / "campaign.py")
digest, save = common.digest, common.save


def require(condition, message):
    if not condition:
        raise ValueError("diagnostic campaign: " + message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_file(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe artifact path")
    return root / path


def fixed_plan(states):
    """Exactly six A processes, then three C processes; never a trajectory."""
    require([s["name"] for s in states] == list(STATES), "state population differs")
    plans = []
    for command in ("repeat-3", "repeat-1", "diagnose"):
        for state in states:
            plans.append(
                {
                    "name": state["name"] + "-" + command,
                    "state": state["name"],
                    "mode": 0,
                    "arguments": [command],
                    "input": state["input"],
                    "input_sha256": state["input_sha256"],
                    "companions": state["companions"]
                    if command == "diagnose" and state["name"] == STATES[2]
                    else {},
                }
            )
    return plans


def prepare(config_path, diagnostic_annex, destination, source_root):
    """Verify qualified frozen inputs and stage a new bundle without native calls."""
    import numpy as np

    from crucible import trajectory_reference as ref
    from crucible.benchmark import load_benchmark

    started, cpu = time.perf_counter(), time.process_time()
    source_root, destination = Path(source_root).resolve(), Path(destination).resolve()
    config = json.loads(Path(config_path).read_text())
    require(
        set(config) == {"annex", "benchmark_access", "source_config"},
        "config fields differ",
    )
    old = json.loads(ref.checked(config["annex"], ref.ANNEX_SHA256))
    annex_bytes = ref.checked(diagnostic_annex, ANNEX_SHA256)
    annex = json.loads(annex_bytes)
    require(
        [s["name"] for s in annex["states"]] == list(STATES),
        "annex state population differs",
    )
    ref.checked(
        source_root / "experiments/trajectory_reference/PROTOCOL.md",
        ref.PROTOCOL_SHA256,
    )
    protocol = ref.checked(
        source_root / "experiments/trajectory_reference/DIAGNOSTIC_PROTOCOL.md",
        PROTOCOL_SHA256,
    )
    dirty = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    require(not dirty, "commit the complete source before preparation")
    require(
        Path(__file__).read_bytes()
        == (
            source_root / "experiments/trajectory_reference/diagnostic_campaign.py"
        ).read_bytes(),
        "running preparation source differs",
    )
    require(
        Path(ref.__file__).read_bytes()
        == (source_root / "src/crucible/trajectory_reference.py").read_bytes(),
        "installed trajectory preparation source differs",
    )
    require(
        common.__file__
        and Path(common.__file__).read_bytes()
        == (source_root / "experiments/trajectory_reference/campaign.py").read_bytes(),
        "running common campaign source differs",
    )
    cases, controls = {}, {}
    for label, identity in ref.INPUT_SHA256.items():
        entry = old["cases"][label]
        payload = ref.checked(entry["npz"], identity)
        import io

        with np.load(io.BytesIO(payload), allow_pickle=False) as file:
            case = ref.validate_case({k: file[k].copy() for k in file.files})
        data = load_benchmark(
            "ccsn-primary-native-rhs-pointwise",
            "0.1.0",
            use="state_training",
            split=entry["role"],
            config=config["benchmark_access"],
        )
        selected = np.flatnonzero(data["record_id"] == entry["initial_record"])
        require(len(selected) == 1, "qualified initial record missing")
        i = selected[0]
        require(
            np.array_equal(data["Y"][i].view(np.uint64), case["Y0"].view(np.uint64))
            and np.array_equal(data["species_Z_A"], case["species_Z_A"]),
            "qualified initial Y/species differ",
        )
        cases[label] = (case, payload)
        controls[label] = data["fresh_rhs"][i].astype("<f8").tobytes()
    loaded = time.perf_counter()
    # Validate every private input before creating a destination or copying sources.
    staged_states = []
    payloads = {}
    for entry in annex["states"]:
        label = entry["parent_case"]
        require(
            label in cases
            and entry["source_input_npz_sha256"] == ref.INPUT_SHA256[label],
            "parent case differs",
        )
        case = cases[label][0]
        raw = ref.checked(entry["input"], entry["input_sha256"])
        # The exact reserialization binds every wire byte, including forcing and controls.
        require(len(raw) >= ref.HEADER.size + 3 * 160 * 8, "truncated frozen input")
        yraw = raw[ref.HEADER.size + 2 * 160 * 8 : ref.HEADER.size + 3 * 160 * 8]
        require(sha(yraw) == entry["Y_sha256"], "frozen Y differs")
        y = np.frombuffer(yraw, dtype="<f8").copy()
        when = entry["time"]
        require(
            when == (1.953125e-7 if entry["name"] == STATES[2] else 0.0),
            "frozen state time differs",
        )
        if entry["name"] == STATES[2]:
            require(sha(yraw) == NEWTON_Y_SHA256, "Newton300 Y differs")
        else:
            require(yraw == case["Y0"].astype("<f8").tobytes(), "initial Y differs")
        expected = ref.wire_input(
            case, mode=0, mesh=np.array([when], dtype=np.float64), time=when, state=y
        )
        require(raw == expected, "frozen mode-zero wire differs")
        relative = "inputs/" + entry["name"] + "/input.bin"
        payloads[relative] = raw
        companions = {}
        expected_names = (
            {"old-state.bin", "frozen-h.bin"}
            if entry["name"] == STATES[2]
            else {"expected-control.bin"}
        )
        require(
            set(entry["companions"]) == expected_names, "companion population differs"
        )
        for name, identity in entry["companions"].items():
            data = ref.checked(Path(entry["input"]).parent / name, identity)
            if name == "expected-control.bin":
                require(data == controls[label], "original D-019 F differs")
            elif name == "old-state.bin":
                require(
                    data == case["Y0"].astype("<f8").tobytes(), "old BE state differs"
                )
            else:
                require(data == struct.pack("<d", 1.953125e-7), "frozen h differs")
            target = "inputs/" + entry["name"] + "/" + name
            payloads[target] = data
            companions[name] = {"path": target, "sha256": identity}
        staged_states.append({**entry, "input": relative, "companions": companions})
    destination.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    for label, (_, payload) in cases.items():
        (destination / "inputs" / (label + ".npz")).write_bytes(payload)
    (destination / "annex.json").write_bytes(annex_bytes)
    (destination / "DIAGNOSTIC_PROTOCOL.md").write_bytes(protocol)
    stage = load_module(
        "diagnostic_stage",
        source_root / "experiments/trajectory_reference/stage_native.py",
    )
    stage.stage(config["source_config"], destination / "bundle")
    for name in ("campaign.py", "diagnostic_campaign.py"):
        shutil.copy2(
            source_root / "experiments/trajectory_reference" / name, destination / name
        )
    identities = {
        str(p.relative_to(destination)): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    git = subprocess.run(
        ["git", "rev-parse", "HEAD", "HEAD^{tree}"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    prepared = {
        "schema": "crucible.phase2d.diagnostic-prepared.v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "annex_sha256": ANNEX_SHA256,
        "original_annex_sha256": ref.ANNEX_SHA256,
        "original_protocol_sha256": ref.PROTOCOL_SHA256,
        "source_commit": git[0],
        "source_tree": git[1],
        "states": staged_states,
        "attempts": fixed_plan(staged_states),
        "immutable_files": identities,
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "costs": {
            "input_loading_validation_wall_seconds": loaded - started,
            "prepare_total_wall_seconds": time.perf_counter() - started,
            "prepare_total_cpu_seconds": time.process_time() - cpu,
            "process_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1024 if platform.system() == "Linux" else 1),
        },
    }
    save(destination / "prepared.json", prepared)
    return prepared


def parse_baseline(data):
    """Decode one bounded baseline; preserve comparison bytes and component bits."""
    require(len(data) >= 48, "truncated baseline header")
    header = struct.unpack_from("<12i", data)
    require(
        header[:3] == (0x43524442, 1, 160)
        and header[3:7] == NC
        and header[7:11] == NB
        and header[11] == 10240,
        "baseline header differs",
    )
    floats = 10 + 320 + sum(NC) + sum(NB)
    require(len(data) == 48 + floats * 8 + 10240 * 4, "baseline length differs")
    values = struct.unpack_from("<" + str(floats) + "d", data, 48)
    require(all(math.isfinite(x) for x in values), "nonfinite baseline")
    require(values[0] >= 1 and values[0].is_integer(), "invalid baseline call ID")
    cursor = 330
    csect, b = [], []
    for count in NC:
        csect.append(values[cursor : cursor + count])
        cursor += count
    for count in NB:
        b.append(values[cursor : cursor + count])
        cursor += count
    return {
        "header": header,
        "call_id": int(values[0]),
        "time": values[1],
        "T9": values[2],
        "rho": values[3],
        "moments_eos": values[4:10],
        "Y": values[10:170],
        "F": values[170:330],
        "csect": tuple(csect),
        "b": tuple(b),
        "branches": struct.unpack_from("<10240i", data, 48 + floats * 8),
        "comparison_bytes": data[:48] + data[56:],
        "Y_bytes": data[128:1408],
        "F_bytes": data[1408:2688],
    }


def input_echo(data):
    require(len(data) >= 48, "truncated input")
    h = struct.unpack_from("<8i2d", data)
    require(
        h[:3] == (0x43524432, 1, 160) and h[6] == 0 and h[3] >= 2 and h[4:6] == (1, 1),
        "diagnostic input header differs",
    )
    nk = h[3]
    require(len(data) == 48 + 8 * (480 + 3 * nk + 2), "input length differs")
    vals = struct.unpack_from("<" + str(480 + 3 * nk + 2) + "d", data, 48)
    require(all(math.isfinite(x) for x in vals), "nonfinite diagnostic input")
    knots, temp, rho = (
        vals[480 : 480 + nk],
        vals[480 + nk : 480 + 2 * nk],
        vals[480 + 2 * nk : 480 + 3 * nk],
    )
    when = vals[-1]
    require(
        vals[-2] == when
        and knots[0] <= when <= knots[-1]
        and all(b > a for a, b in zip(knots, knots[1:])),
        "diagnostic input grid differs",
    )
    right = next(i for i, t in enumerate(knots) if t >= when)
    if knots[right] == when:
        forcing = temp[right], rho[right]
    else:
        fraction = (when - knots[right - 1]) / (knots[right] - knots[right - 1])
        forcing = tuple(
            x[right - 1] + fraction * (x[right] - x[right - 1]) for x in (temp, rho)
        )
    return {
        "time_T9_rho": struct.pack("<3d", when, *forcing),
        "Y": data[2608:3888],
        "species": data[48:2608],
    }


def validate_maps(data):
    """Check fixed map dimensions and exact stream extent before comparisons."""
    require(len(data) >= 5120, "truncated static maps")
    la = struct.unpack_from("<640i", data)
    le = struct.unpack_from("<640i", data, 2560)
    offset = 5120
    for k, (nc, nb) in enumerate(zip(NC, NB)):
        require(offset + 12 <= len(data), "truncated static map dimensions")
        require(
            struct.unpack_from("<3i", data, offset) == (k + 1, nc, nb),
            "static map dimensions differ",
        )
        offset += 12 + (5 if k == 0 else 6) * nc * 4
        require(offset + nb * 16 <= len(data), "truncated static map payload")
        mu = struct.unpack_from("<" + str(nb) + "i", data, offset)
        target = struct.unpack_from("<" + str(nb) + "i", data, offset + nb * 4)
        factors = struct.unpack_from("<" + str(nb) + "d", data, offset + nb * 8)
        require(
            all(1 <= x <= nc for x in mu) and all(math.isfinite(x) for x in factors),
            "invalid static map entries",
        )
        cursor = 0
        for i in range(160):
            start, stop = la[4 * i + k], le[4 * i + k]
            require(
                start == cursor + 1
                and cursor <= stop <= nb
                and all(x == i + 1 for x in target[cursor:stop]),
                "static map species ranges differ",
            )
            cursor = stop
        require(cursor == nb, "static map coverage differs")
        offset += nb * 16
    require(offset == len(data), "static map trailing bytes")


def ieee_rows(data):
    require(data and len(data) % 88 == 0, "IEEE evidence missing/truncated")
    rows = list(struct.iter_unpack("<11q", data))
    require(
        all(
            r[0] >= 1
            and r[1] == r[2] == 1
            and r[3] in (0, 1)
            and r[4] == r[5]
            and (r[4] in (0, 1) if r[3] else r[4] == -1)
            and r[6:9] == (0, 0, 0)
            and r[9] in (0, 1)
            and r[10] in (0, 1)
            for r in rows
        ),
        "unsupported/nonfinite IEEE arithmetic",
    )
    return rows


def check_process(root, spec, result, *, baseline=None):
    work = root / "attempts" / spec["name"]
    status = work / "status.txt"
    require(
        result.get("returncode") == 0
        and status.is_file()
        and status.read_text().splitlines()[-1:] == ["SUCCESS"],
        "native process failed/missing SUCCESS",
    )
    counts = json.loads((work / "counters.json").read_text())
    require(
        set(counts) == COUNTERS
        and all(type(v) is int and v >= 0 for v in counts.values())
        and all(
            counts[k] == counts["rhs"]
            for k in ("coefficient", "eos", "screening", "weak")
        ),
        "invalid native counters",
    )
    require(
        all(
            counts.get(k) == 0
            for k in ("newton", "retry", "accepted", "projection", "step_attempt")
        ),
        "forbidden trajectory/repair work",
    )
    echo = input_echo((root / spec["input"]).read_bytes())
    species, maps = (
        (work / "species.bin").read_bytes(),
        (work / "used-maps.bin").read_bytes(),
    )
    require(species == echo["species"], "ordered species echo differs")
    validate_maps(maps)
    rows = ieee_rows((work / "diagnostic-ieee.bin").read_bytes())
    evaluated = work / "diagnostic-evaluations.bin"
    require(
        evaluated.is_file() and evaluated.stat().st_size == counts["rhs"] * 324 * 8,
        "evaluated-state call accounting differs",
    )
    command = spec["arguments"][0]
    repeats = 3 if command == "repeat-3" else 1
    names = sorted(p.name for p in work.glob("baseline-*.bin"))
    require(
        names == [f"baseline-{i:03}.bin" for i in range(1, repeats + 1)],
        "baseline population differs",
    )
    base = None
    for name in names:
        raw = (work / name).read_bytes()
        parsed = parse_baseline(raw)
        require(
            raw[56:80] == echo["time_T9_rho"] and parsed["Y_bytes"] == echo["Y"],
            "native input echo differs",
        )
        require(
            base is None or parsed["comparison_bytes"] == base,
            "within-process repeat differs",
        )
        base = parsed["comparison_bytes"]
        expected = root / "inputs" / spec["state"] / "expected-control.bin"
        if expected.exists():
            require(
                parsed["F_bytes"] == expected.read_bytes(),
                "original D-019 F control differs",
            )
    require(
        baseline is None or (base, species, maps, rows[0][1:6]) == baseline,
        "fresh-process baseline/static maps differ",
    )
    if command != "diagnose":
        require(
            counts["rhs"] == repeats
            and len(rows) == repeats
            and all(
                counts[k] == 0 for k in ("jacobian", "lu", "linear_solve", "probe")
            ),
            "repeat call accounting differs",
        )
    require(
        len(rows) == counts["rhs"]
        and [r[0] for r in rows] == list(range(1, counts["rhs"] + 1)),
        "IEEE/call accounting differs",
    )
    if command == "diagnose":
        check_diagnostic_files(work, spec, counts)
    require(counts["rhs"] <= MAX_RHS, "process physical-call envelope exceeded")
    require(all(r[1:6] == rows[0][1:6] for r in rows), "IEEE modes differ across calls")
    return (base, species, maps, rows[0][1:6]), counts


def check_diagnostic_files(work, spec, counts):
    """Structural completeness only; numerical failures remain declared outcomes."""
    require(counts.get("jacobian") == 4, "four matrix attempts not accounted for")
    required_rows = {
        "diagnostic-evaluations.bin": (324, None),
        "matrix-status.bin": (5, 4),
        "fd-probe-attempts.bin": (12, None),
        "fd-columns.bin": (6, None),
        "jacobian-bases.bin": (164, 4),
        "directional.bin": (1286, 27),
        "diagnostic-jv.bin": (160 * 3 * 4, 1),
        "direction-attempts.bin": (327, None),
        "fixed-b-jacobian.bin": (160 * 160, 1),
    }
    for name, (width, rows) in required_rows.items():
        path = work / name
        require(path.is_file(), "missing diagnostic output " + name)
        size = path.stat().st_size
        require(
            size % (width * 8) == 0 and (rows is None or size == rows * width * 8),
            "diagnostic stream extent differs: " + name,
        )
    require(
        (work / "diagnostic-evaluations.bin").stat().st_size == counts["rhs"] * 324 * 8,
        "evaluated-state call accounting differs",
    )
    status = struct.unpack("<20d", (work / "matrix-status.bin").read_bytes())
    require(all(math.isfinite(x) for x in status), "nonfinite matrix-status record")
    complete = 0
    for i, factor in enumerate((0.1, 1.0, 10.0, 100.0), 1):
        row = status[(i - 1) * 5 : i * 5]
        require(
            row[0] == factor
            and row[1] == i
            and row[2] in (0.0, 1.0)
            and 0 <= row[3] <= row[4] <= counts["rhs"],
            "matrix-status fields differ",
        )
        path = work / f"jacobian-factor-{i}.bin"
        require(
            path.is_file() and path.stat().st_size == 160 * 160 * 8,
            "matrix payload missing/truncated",
        )
        if row[2] == 1:
            values = struct.unpack("<25600d", path.read_bytes())
            require(
                all(math.isfinite(x) for x in values), "nonfinite complete Jacobian"
            )
            complete += 1
        linear = work / f"linear-factor-{i}.bin"
        if spec["state"] == STATES[2] and row[2] == 1:
            require(
                linear.is_file() and linear.stat().st_size == 20 + 52001 * 8 + 160 * 4,
                "complete matrix missing/truncated frozen linear outcome",
            )
            header = struct.unpack_from("<5i", linear.read_bytes())
            require(
                header[:3] == (0x4352444C, 1, 160)
                and (header[4] != -999 if header[3] == 0 else header[4] == -999),
                "linear status header differs",
            )
        else:
            require(not linear.exists(), "undeclared frozen linear solve")
    fixed_b = struct.unpack("<25600d", (work / "fixed-b-jacobian.bin").read_bytes())
    require(all(math.isfinite(x) for x in fixed_b), "nonfinite fixed-b matrix")
    candidate = work / "candidate-status.txt"
    require(
        candidate.is_file() and candidate.read_text().strip(),
        "candidate status missing",
    )
    text = candidate.read_text().strip()
    require(
        text.startswith(("SKIPPED ", "REFUSED ")) or text == "EVALUATED",
        "unrecognized candidate outcome",
    )
    if text == "EVALUATED":
        require(spec["state"] == STATES[2], "undeclared candidate evaluation")
        parse_baseline((work / "candidate.bin").read_bytes())
        require(
            not (work / "candidate-refused.bin").exists(),
            "conflicting candidate outcomes",
        )
    elif text.startswith("REFUSED "):
        refused = work / "candidate-refused.bin"
        require(
            spec["state"] == STATES[2]
            and refused.is_file()
            and refused.stat().st_size == 163 * 8
            and not (work / "candidate.bin").exists(),
            "refused candidate payload differs",
        )
    else:
        require(
            not (work / "candidate.bin").exists()
            and not (work / "candidate-refused.bin").exists(),
            "unexpected skipped candidate payload",
        )
    if spec["state"] != STATES[2]:
        require(
            text.startswith("SKIPPED ")
            and counts.get("lu") == counts.get("linear_solve") == 0,
            "undeclared linear/candidate work",
        )
    else:
        require(
            counts.get("lu") == complete
            and 0 <= counts.get("linear_solve", -1) <= complete,
            "frozen linear attempt accounting differs",
        )


def build_identities(root):
    """Require the retained build hashes; never compile or infer a fresh build."""
    identities = {}
    for executable, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
    ):
        fields = (root / "bundle" / receipt).read_text().split()
        require(
            len(fields) == 2
            and Path(fields[1]).name == executable
            and fields[0] == digest(root / "bundle" / executable),
            "native executable receipt differs",
        )
        identities[executable] = fields[0]
    libraries = json.loads((root / "bundle/linked-library-hashes.json").read_text())
    require(
        libraries
        and all(Path(p).is_absolute() and digest(p) == h for p, h in libraries.items()),
        "linked library identity differs",
    )
    return {
        "executables": identities,
        "libraries": libraries,
        "build_files": {
            str(p.relative_to(root)): digest(p)
            for p in sorted((root / "bundle").rglob("*"))
            if p.is_file()
        },
    }


def validate_prepared(root, prepared):
    """Bind the execution plan back to the exact frozen annex and copied bytes."""
    require(
        digest(root / "annex.json") == ANNEX_SHA256
        and digest(root / "DIAGNOSTIC_PROTOCOL.md") == PROTOCOL_SHA256,
        "annex/protocol bytes differ",
    )
    annex = json.loads((root / "annex.json").read_text())
    require(
        [s["name"] for s in annex["states"]] == list(STATES),
        "frozen annex state population differs",
    )
    expected_states = []
    for entry in annex["states"]:
        prefix = "inputs/" + entry["name"] + "/"
        companions = {
            name: {"path": prefix + name, "sha256": identity}
            for name, identity in entry["companions"].items()
        }
        state = {**entry, "input": prefix + "input.bin", "companions": companions}
        expected_states.append(state)
        mandatory = {
            state["input"]: entry["input_sha256"],
            **{c["path"]: c["sha256"] for c in companions.values()},
        }
        for name, identity in mandatory.items():
            require(
                prepared["immutable_files"].get(name) == identity,
                "immutable frozen input binding differs",
            )
            require(
                digest(safe_file(root, name)) == identity, "frozen input bytes differ"
            )
    require(
        prepared["states"] == expected_states,
        "prepared states differ from frozen annex",
    )
    for name in (
        "campaign.py",
        "diagnostic_campaign.py",
        "annex.json",
        "DIAGNOSTIC_PROTOCOL.md",
        "bundle/source-manifest.json",
    ):
        require(
            name in prepared["immutable_files"], "mandatory immutable source absent"
        )


def execute(root, *, srun=False):
    """Run fixed commands once; interruptions and all unattempted plans stay visible."""
    root = Path(root).resolve()
    prepared = json.loads((root / "prepared.json").read_text())
    require(
        prepared.get("schema") == "crucible.phase2d.diagnostic-prepared.v1"
        and prepared.get("protocol_sha256") == PROTOCOL_SHA256
        and prepared.get("annex_sha256") == ANNEX_SHA256,
        "unrecognized diagnostic preparation",
    )
    require(
        prepared["attempts"] == fixed_plan(prepared["states"]),
        "fixed nine-process plan differs",
    )
    validate_prepared(root, prepared)
    for name, identity in prepared["immutable_files"].items():
        require(
            digest(safe_file(root, name)) == identity, "immutable source/input changed"
        )
    for name, actual in (
        ("diagnostic_campaign.py", Path(__file__)),
        ("campaign.py", Path(common.__file__)),
    ):
        require(
            digest(actual) == prepared["immutable_files"][name],
            "running host script differs",
        )
    # Structural validation occurs before even the compiled synthetic fixtures.
    for state in prepared["states"]:
        require(
            digest(safe_file(root, state["input"])) == state["input_sha256"],
            "state input differs",
        )
        input_echo((root / state["input"]).read_bytes())
    path = root / "campaign.json"
    require(
        not path.exists() and not (root / "attempts").exists(),
        "no diagnostic restart/repetition authorized",
    )
    manifest = {
        "schema": "crucible.phase2d.diagnostic-campaign.v1",
        "prepared_sha256": digest(root / "prepared.json"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "threads": {
            k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
        "attempts": [
            {**s, "status": "UNATTEMPTED", "completed": False}
            for s in prepared["attempts"]
        ],
        "complete": False,
        "stage_a_pass": False,
        "physical_rhs_calls": 0,
    }
    started = time.perf_counter()
    save(path, manifest)
    try:
        require(
            all(
                os.environ.get(k) == "1" for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")
            ),
            "one-thread environment required",
        )
        build = build_identities(root)
        manifest["build"] = build
        save(path, manifest)
        manifest["synthetic"] = common.synthetic_checks(
            root, extra_scenarios=(("trajectory_synthetic", "retry-snapshot", None),)
        )
        save(path, manifest)
        launcher = ["srun", "-n", "1", "-c", "1"] if srun else []
        bases = {}
        static = None
        for i, spec in enumerate(prepared["attempts"]):
            require(
                digest(root / "prepared.json") == manifest["prepared_sha256"],
                "prepared record changed",
            )
            for name, identity in prepared["immutable_files"].items():
                require(
                    digest(safe_file(root, name)) == identity,
                    "immutable source/input changed during campaign",
                )
            require(
                build_identities(root) == build,
                "build identity changed during campaign",
            )
            manifest["attempts"][i]["status"] = "STARTING"
            save(path, manifest)
            companions = tuple(
                (name, entry["path"], entry["sha256"])
                for name, entry in spec["companions"].items()
            )
            result = common.run_attempt(
                root,
                spec,
                root / "bundle/trajectory_driver",
                launcher,
                resume=False,
                arguments=tuple(spec["arguments"]),
                companions=companions,
            )
            manifest["attempts"][i] = {**spec, **result}
            save(path, manifest)
            counts_path = root / "attempts" / spec["name"] / "counters.json"
            if counts_path.is_file():
                counts = json.loads(counts_path.read_text())
                manifest["attempts"][i]["native_counters"] = counts
                if type(counts.get("rhs")) is int and counts["rhs"] >= 0:
                    manifest["physical_rhs_calls"] += counts["rhs"]
                save(path, manifest)
            baseline, counts = check_process(
                root, spec, result, baseline=bases.get(spec["state"])
            )
            require(
                static is None or baseline[1:] == static,
                "static maps/species/IEEE modes differ across states",
            )
            static = baseline[1:]
            bases.setdefault(spec["state"], baseline)
            require(
                manifest["physical_rhs_calls"] <= MAX_RHS,
                "total physical-call envelope exceeded",
            )
            manifest["attempts"][i]["validation_pass"] = True
            if i == 5:
                manifest["stage_a_pass"] = True
            if i >= 6:
                require(manifest["stage_a_pass"], "stage A incomplete before C")
            save(path, manifest)
        manifest["complete"] = (
            True  # Diagnostic process completeness, never reference acceptance.
        )
    except BaseException as exc:
        manifest["exception"] = repr(exc)
        for item in manifest["attempts"]:
            record_path = root / "attempts" / item["name"] / "attempt.json"
            if item["status"] == "STARTING":
                if record_path.exists():
                    record = json.loads(record_path.read_text())
                    if not record.get("completed"):
                        record["status"] = "INTERRUPTED"
                        record["files"] = common.snapshot(record_path.parent)
                        save(record_path, record)
                    item.update(record)
                else:
                    item["status"] = "INTERRUPTED_BEFORE_LAUNCH"
                    if record_path.parent.exists():
                        item["files"] = common.snapshot(record_path.parent)
        raise
    finally:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        manifest["wall_seconds_this_process"] = time.perf_counter() - started
        manifest["children_cpu_seconds"] = usage.ru_utime + usage.ru_stime
        manifest["children_peak_rss_bytes"] = usage.ru_maxrss * (
            1024 if platform.system() == "Linux" else 1
        )
        manifest["artifact_bytes"] = sum(
            p.stat().st_size
            for p in root.rglob("*")
            if p.is_file() and not p.is_symlink()
        )
        save(path, manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    for name in ("config", "annex", "destination"):
        prep.add_argument(name, type=Path)
    prep.add_argument("--source-root", type=Path, default=Path.cwd())
    run = commands.add_parser("execute")
    run.add_argument("root", type=Path)
    run.add_argument("--srun", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.config, args.annex, args.destination, args.source_root)
    else:
        execute(args.root, srun=args.srun)


if __name__ == "__main__":
    main()
