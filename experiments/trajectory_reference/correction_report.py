"""Offline D-040 analysis, byte-exact reload and independent-build comparison.

No executable or compiler is invoked. Numerical qualification, serialization and
human reference acceptance are separate claims. Historical failures stay failed.
"""

import argparse
import hashlib
import importlib.util
import json
import platform
import re
import struct
import zipfile
from pathlib import Path

import numpy as np

from crucible import trajectory_metrics as metrics
from crucible import trajectory_reference as artifacts

HERE = Path(__file__).resolve().parent
HOST_IDENTITIES = "host-identity-verification.json"
UNATTEMPTED = {"UNATTEMPTED", "CONDITIONALLY_UNATTEMPTED"}
ERRORS = (
    OSError,
    ValueError,
    KeyError,
    IndexError,
    TypeError,
    struct.error,
    StopIteration,
    OverflowError,
    ZeroDivisionError,
)


def require(condition, message):
    if not condition:
        raise ValueError("correction report: " + message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    def invalid(value):
        raise ValueError("nonfinite JSON token: " + value)

    return json.loads(Path(path).read_text(), parse_constant=invalid)


def safe(root, name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "unsafe artifact path")
    target = root / path
    require(target.resolve().is_relative_to(root.resolve()), "escaped artifact path")
    require(not target.is_symlink(), "symlinked artifact")
    return target


def chunks(array, order="C"):
    """C-order byte chunks without materializing large or strided mmap arrays."""
    for block in np.nditer(
        array,
        flags=["external_loop", "buffered", "zerosize_ok"],
        op_flags=["readonly"],
        order=order,
        buffersize=131072,
    ):
        yield block.tobytes()


def array_digest(array):
    h = hashlib.sha256()
    for block in chunks(array):
        h.update(block)
    return h.hexdigest()


def write_report(output, report):
    """Exclusive strict JSON plus numeric NPZ; the ZIP writer streams mmaps."""
    output = Path(output)
    numeric = output.with_suffix(".npz")
    require(
        output.suffix == ".json" and not output.exists() and not numeric.exists(),
        "new JSON/NPZ destinations required",
    )
    summary, arrays = artifacts.split_report(report)
    with numeric.open("xb") as stream:
        np.savez(stream, **arrays)
    summary["array_artifact"] = {
        "path": numeric.name,
        "sha256": digest(numeric),
        "arrays": {
            key: {
                "dtype": value.dtype.str,
                "shape": list(value.shape),
                "sha256": array_digest(value),
            }
            for key, value in arrays.items()
        },
    }
    with output.open("x") as stream:
        stream.write(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    return summary


def map_rows(path, width, *, offset=0, dtype="<f8", partial=False):
    size = path.stat().st_size - offset
    item = np.dtype(dtype).itemsize
    require(
        size >= 0 and (partial or size % (width * item) == 0),
        "raw stream extent differs: " + path.name,
    )
    count = size // (width * item)
    if not count:
        return np.empty((0, width), dtype=dtype)
    return np.memmap(path, dtype=dtype, mode="r", offset=offset, shape=(count, width))


def newton_arrays(path, *, partial=False):
    with path.open("rb") as stream:
        require(
            stream.read(32)
            == struct.pack("<8i", 0x4352434E, 1, 160, 1936, 12, 0, 0, 0),
            "compact Newton header differs",
        )
    extent, tail = divmod(path.stat().st_size - 32, 15584)
    require(extent >= 0 and (partial or tail == 0), "truncated compact Newton stream")
    if not extent:
        return {
            "ids": np.empty((0, 12), dtype="<i8"),
            "values": np.empty((0, 1936), dtype="<f8"),
        }
    mapping = np.memmap(path, mode="r", dtype=np.uint8)
    return {
        "ids": np.ndarray(
            (extent, 12), dtype="<i8", buffer=mapping, offset=32, strides=(15584, 8)
        ),
        "values": np.ndarray(
            (extent, 1936), dtype="<f8", buffer=mapping, offset=128, strides=(15584, 8)
        ),
    }


def retain_numeric(work):
    """Keep all written binary bytes; decode large regular streams as mmap views.

    Partial tails and unknown layouts remain explicit uint8, never discarded or
    interpreted as completed records. The JSON records which schema was used.
    """
    result = {}
    for path in sorted(work.rglob("*.bin")):
        name = str(path.relative_to(work))
        size = path.stat().st_size
        if path.name == "correction-newton.bin" and size >= 32:
            try:
                result[name] = {**newton_arrays(path), "layout": "D040_NEWTON_V1"}
                continue
            except ValueError:
                pass
        known = {
            "accepted.bin": (488, 0),
            "accepted-forcing.bin": (3, 0),
            "correction-accepted.bin": (496, 32),
            "assembly-evaluations.bin": (496, 32),
        }
        if path.name in known:
            width, offset = known[path.name]
            if size >= offset and (size - offset) % (8 * width) == 0:
                result[name] = {
                    "values": map_rows(path, width, offset=offset),
                    "header": np.frombuffer(
                        path.open("rb").read(offset), dtype=np.uint8
                    ),
                    "layout": "binary64_rows_" + str(width),
                }
                continue
        result[name] = {
            "bytes": np.memmap(path, mode="r", dtype=np.uint8)
            if size
            else np.empty(0, dtype=np.uint8),
            "layout": "raw_bytes_retained_no_invented_decode",
        }
    return result


def verify_retained_build(root, prepared, campaign, contract, expected_host_sha):
    """Check the explicit SHA-bound receipt from actual execution-host paths."""
    require(
        isinstance(expected_host_sha, str)
        and re.fullmatch(r"[0-9a-f]{64}", expected_host_sha),
        "explicit execution-host identity SHA256 required",
    )
    path = root / HOST_IDENTITIES
    require(digest(path) == expected_host_sha, "host identity receipt changed")
    proof = read_json(path)
    helper = load("_correction_report_host", HERE / "correction_host_identities.py")
    expected, completed = helper.expected_library_files(campaign)
    binding = {
        "schema": "crucible.phase2d.correction-host-identities.v1",
        "numerical_source": contract.SOURCE_NAME,
        "source_commit": prepared["source_commit"],
        "source_tree": prepared["source_tree"],
        "protocol_sha256": contract.PROTOCOL_SHA256,
        "build_label": prepared["build_label"],
        "prepared_sha256": digest(root / "prepared.json"),
        "campaign_sha256": digest(root / "campaign.json"),
        "collector_sha256": digest(HERE / "correction_host_identities.py"),
        "build": campaign["build"],
        "campaign_accounting_complete": campaign.get("complete") is True,
        "producer_quiescence_basis": "LEAD_VERIFIED_PRODUCERS_AND_CONTROLLER_TERMINAL",
        "completed_attempts": completed,
    }
    require(
        all(proof.get(k) == v for k, v in binding.items()),
        "execution-host proof binding differs",
    )
    evidence = proof.get("interrupted_library_evidence")
    interrupted = helper.partial_attempts(campaign)
    require(
        isinstance(evidence, list) and len(evidence) == len(interrupted),
        "interrupted host evidence population differs",
    )
    for entry, detail in zip(interrupted, evidence, strict=True):
        record, directory = entry["record"], entry["directory"]
        recorded = {
            k: v
            for k, v in record.get("loaded_library_hashes", {}).items()
            if v is not None
        }
        require(
            detail["name"] == record["name"]
            and detail["directory"] == directory
            and detail["recorded_hashes"] == recorded,
            "interrupted library process binding differs",
        )
        mapped, mapping_sha = set(), None
        if directory is not None:
            maps = safe(root, directory) / "loaded-maps.txt"
            if maps.exists():
                mapping_sha = digest(maps)
                inventory = record.get("files", {}).get("loaded-maps.txt")
                require(
                    inventory is None or inventory["sha256"] == mapping_sha,
                    "interrupted mapping changed",
                )
                require(
                    inventory is not None or bool(detail["unavailable"]),
                    "unflushed mapping inventory lacks disclosure",
                )
                for line in maps.read_text().splitlines():
                    fields = line.split(maxsplit=5)
                    if (
                        len(fields) == 6
                        and "x" in fields[1]
                        and fields[5].startswith("/")
                    ):
                        # The raw process executable can have a different host root.
                        # Match its recorded invocation, never remap a vendor path.
                        if Path(fields[5]).name != "trajectory_driver":
                            mapped.add(fields[5])
        require(
            detail["mapped_paths"] == sorted(mapped)
            and detail["mapping_sha256"] == mapping_sha,
            "interrupted mapped-path proof differs",
        )
        observed = detail["observed_live_hashes"]
        require(
            set(observed) <= mapped and isinstance(detail["unavailable"], list),
            "unexpected interrupted live observation",
        )
        require(
            set(observed) == mapped or bool(detail["unavailable"]),
            "missing interrupted live path has no disclosure",
        )
        for name, identity in observed.items():
            require(
                name not in expected or expected[name] == identity,
                "interrupted observation differs from process-time hash",
            )
            expected[name] = identity
    require(
        proof.get("checked_files") == expected
        and expected
        and all(
            Path(k).is_absolute()
            and isinstance(v, str)
            and re.fullmatch(r"[0-9a-f]{64}", v)
            for k, v in expected.items()
        ),
        "execution-host checked file closure differs",
    )
    build = campaign["build"]
    require(
        read_json(root / "bundle/linked-library-hashes.json") == build["libraries"],
        "retained linked-library receipt differs",
    )
    actual = {
        str(p.relative_to(root)): digest(p)
        for p in sorted((root / "bundle").rglob("*"))
        if p.is_file()
    }
    require(actual == build["build_files"], "retained build file closure differs")
    for executable, receipt in (
        ("trajectory_driver", "executable.sha256"),
        ("trajectory_synthetic", "synthetic-executable.sha256"),
        ("forcing_synthetic", "forcing-executable.sha256"),
        ("assembly_synthetic", "assembly-executable.sha256"),
    ):
        fields = (root / "bundle" / receipt).read_text().split()
        require(
            len(fields) == 2
            and Path(fields[1]).name == executable
            and fields[0]
            == build["executables"][executable]
            == digest(root / "bundle" / executable),
            "retained executable identity differs",
        )
    return {
        "pass": True,
        "sha256": expected_host_sha,
        "checked_files": expected,
        "interrupted_library_evidence": evidence,
        "scope": "explicit actual-execution-host recheck; no local vendor-path substitution",
    }


def verify_counters(work, record, native_keys, *, completed):
    output = {}
    for filename, key in (
        ("counters.json", "native_counters"),
        ("assembly-counters.json", "assembly_counters"),
    ):
        path = work / filename
        if path.exists():
            output[key] = read_json(path)
            require(
                output[key] == record.get(key), "saved/raw counter checkpoint differs"
            )
        else:
            require(
                not completed and key not in record,
                "completed process counter output missing",
            )
    native, guarded = (
        output.get("native_counters", {}),
        output.get("assembly_counters", {}),
    )
    if native:
        require(
            set(native) == set(native_keys)
            and all(type(v) is int and v >= 0 for v in native.values()),
            "invalid native counters",
        )
    if guarded:
        require(
            set(guarded) == {"schema", "fresh_requests", "rhs", "assembly_calls"}
            and guarded["schema"] == "crucible.assembly-counters.v1"
            and all(
                type(guarded[k]) is int and guarded[k] >= 0
                for k in ("rhs", "assembly_calls", "fresh_requests")
            ),
            "invalid guarded counters",
        )
    if native and guarded:
        require(
            native["rhs"]
            == guarded["rhs"]
            == guarded["assembly_calls"]
            <= guarded["fresh_requests"],
            "guarded/physical counter mismatch",
        )
    require(
        not completed
        or (native and guarded and record.get("counter_accounting_complete") is True),
        "completed named process accounting incomplete",
    )
    output["complete"] = bool(completed and native and guarded)
    if not completed:
        output["unavailable"] = record.get("interruption_scope")
        require(
            output["unavailable"]
            and output["unavailable"].get("unflushed_calls") is None,
            "unflushed call interval must remain explicitly unknown",
        )
    return output


def verify_interrupted(root, prepared, campaign, contract):
    entries = campaign.get("interrupted_attempts", [])
    require(len(entries) <= 1, "more than one interrupted restart per build")
    recovery = campaign.get("infrastructure_recovery")
    if recovery is not None:
        require(
            entries
            and bool(recovery.get("reason"))
            and recovery.get("quiescence_basis")
            == "LEAD_VERIFIED_PRODUCER_AND_CONTROLLER_TERMINAL"
            and "campaign-before-recovery.json"
            in recovery.get("original_receipts", {}),
            "controller recovery lacks original receipts/quiescence reason",
        )
        for name, identity in recovery["original_receipts"].items():
            require(
                digest(safe(root, name)) == identity,
                "pre-recovery original receipt changed",
            )
        before = read_json(root / "campaign-before-recovery.json")
        active = [
            record["name"]
            for record in before["attempts"]
            if record["status"] == "STARTING"
        ]
        require(
            active == [entries[0]["record"]["name"]]
            and before["prepared_sha256"] == digest(root / "prepared.json")
            and before.get("complete") is not True,
            "recovery original active process/preparation differs",
        )
    output = []
    for entry in entries:
        record = entry["record"]
        require(
            record.get("completed") is False
            and record["status"] in {"INTERRUPTED", "INTERRUPTED_BEFORE_LAUNCH"}
            and bool(entry.get("infrastructure_reason"))
            and entry.get("restart_from") == "IDENTICAL_ORIGINAL_INPUT_T0_NEW_PROCESS",
            "invalid infrastructure restart record",
        )
        spec = next(s for s in prepared["attempts"] if s["name"] == record["name"])
        require(
            all(record.get(k) == v for k, v in spec.items()),
            "interrupted original input/plan differs",
        )
        replacement = next(
            s for s in campaign["attempts"] if s["name"] == record["name"]
        )
        require(
            replacement.get("restart_of") == entry["directory"],
            "restart predecessor differs",
        )
        detail = dict(entry)
        if entry["directory"] is not None:
            work = safe(root, entry["directory"])
            contract.verify_attempt_files(root, record, directory=entry["directory"])
            actual = {
                str(p.relative_to(work))
                for p in work.rglob("*")
                if p.is_file() and p.name not in {"attempt.json", "attempt.pending"}
            }
            require(
                actual == set(record["files"]), "interrupted raw file closure differs"
            )
            terminal = (
                (work / "status.txt").read_text().splitlines()[-1:]
                if (work / "status.txt").exists()
                else []
            )
            require(
                not terminal or not terminal[-1].startswith(("SUCCESS", "FAILURE")),
                "completed/numerical failure was restarted",
            )
            if (work / "input.bin").exists():
                require(
                    digest(work / "input.bin") == record["input_sha256"],
                    "interrupted input changed",
                )
            detail["counters"] = verify_counters(
                work, record, contract.diag.COUNTERS, completed=False
            )
            detail["raw_numeric"] = retain_numeric(work)
        else:
            require(
                record["status"] == "INTERRUPTED_BEFORE_LAUNCH"
                and not record.get("files"),
                "interrupted raw directory missing",
            )
            detail["counters"] = {
                "complete": False,
                "unavailable": record["interruption_scope"],
            }
        output.append(detail)
    return output


def trajectory_arrays(work, data):
    """Small requested grids plus mmap accepted rows; no old residual gate."""
    accepted = map_rows(work / "accepted.bin", 488)
    times = accepted[:, 0]
    outputs = np.asarray(data["outputs"], dtype="<f8")
    requested = np.full((len(outputs), 160), np.nan, dtype="<f8")
    present = np.zeros(len(outputs), dtype=bool)
    for i, time in enumerate(outputs):
        found = np.flatnonzero(times == time)
        if len(found) == 1:
            requested[i] = accepted[found[0], 1:161]
            present[i] = True
    observables = {}
    for start in range(0, len(accepted), 2048):
        stop = min(start + 2048, len(accepted))
        block = metrics.trajectory_observables(
            accepted[start:stop, 1:161], np.asarray(data["A"]), np.asarray(data["Z"])
        )
        flattened = {k: v for k, v in block.items() if k != "inventory"}
        flattened.update({"inventory_" + k: v for k, v in block["inventory"].items()})
        for key, values in flattened.items():
            if key not in observables:
                observables[key] = np.empty(len(accepted), dtype="<f8")
            observables[key][start:stop] = values
    return {
        "accepted_t": times,
        "accepted_rows": accepted,
        "requested_t": outputs,
        "requested_Y": requested,
        "output_present": present,
        "missing_output": ~present,
        "achieved_endpoint": float(times[-1]) if len(times) else None,
        "accepted_observables": observables,
        "raw_residual_Linf_diagnostic": accepted[:, 484],
        "raw_residual_AL1_diagnostic": accepted[:, 485],
        "final_projection_AL1": accepted[:, 486],
        "cumulative_final_projection_AL1": accepted[:, 487],
    }


def case_metrics(runs, a, z):
    result = {"pass": False}
    for suffix, key in (("L0", "pilot"), ("L3", "nonlinear")):
        standard, tight = runs.get(suffix + "-standard"), runs.get(suffix + "-tight")
        if standard is not None and tight is not None:
            require(
                np.array_equal(standard["requested_t"], tight["requested_t"]),
                "control grids differ",
            )
            if np.all(standard["output_present"]) and np.all(tight["output_present"]):
                result[key] = metrics.compare_nonlinear_controls(
                    standard["requested_t"],
                    standard["requested_Y"],
                    tight["requested_Y"],
                    a,
                    z,
                )
    levels = [runs.get(f"L{i}-standard") for i in range(4)]
    if all(level is not None for level in levels):
        result["refinement"] = metrics.assess_refinement(levels, a, z)
    result["pass"] = all(
        result.get(key, {}).get("pass") is True
        for key in ("pilot", "nonlinear", "refinement")
    )
    return result


def toolchain_record(root):
    """Extract actual compiler/module/flag evidence from the fixed build recipe."""
    lines = (root / "bundle/build.log").read_text().splitlines()
    wrappers = [
        i
        for i, line in enumerate(lines)
        if line.startswith("/") and Path(line).name == "h5pfc"
    ]
    environment_names = {
        "LOADEDMODULES",
        "PE_ENV",
        "CRAYPE_VERSION",
        "CRAY_MPICH_VERSION",
        "MKLROOT",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "LD_LIBRARY_PATH",
    }
    environment = {
        line.split("=", 1)[0]: line.split("=", 1)[1]
        for line in lines
        if "=" in line and line.split("=", 1)[0] in environment_names
    }
    end = next(
        (i for i, line in enumerate(lines) if line.startswith("LOADEDMODULES=")), None
    )
    require(
        len(wrappers) == 1
        and end is not None
        and wrappers[0] < end
        and set(environment) == environment_names,
        "actual compiler/module/environment evidence incomplete",
    )
    commands = [
        line.removeprefix("+ ") for line in lines if line.startswith("+ h5pfc ")
    ]
    require(
        commands
        and any("-fp-model strict" in line for line in commands)
        and environment["OMP_NUM_THREADS"] == environment["MKL_NUM_THREADS"] == "1",
        "actual precision/thread compiler evidence incomplete",
    )
    return {
        "compiler_wrapper_configuration_modules": lines[wrappers[0] : end],
        "environment": environment,
        "compiler_commands": commands,
    }


def forensic_arithmetic(work, data, assembly):
    """Exact rational oracle on retained original/113-bit baseline/post pairs."""
    pairs = []
    for old in sorted(work.glob("forensic-original-*.bin")):
        pairs.append(
            (old, work / old.name.replace("forensic-original-", "forensic-assembly-"))
        )
    for old, new in (
        ("baseline-001.bin", "assembly-baseline-001.bin"),
        ("baseline-accepted.bin", "assembly-accepted.bin"),
        ("baseline-failure.bin", "assembly-failure.bin"),
        (
            "failure-iteration-baseline-original.bin",
            "failure-iteration-baseline-assembly.bin",
        ),
        ("failure-iteration-post-original.bin", "failure-iteration-post-assembly.bin"),
    ):
        if (work / old).exists() or (work / new).exists():
            pairs.append((work / old, work / new))
    expected_new = {new.name for _, new in pairs}
    require(
        {p.name for p in work.glob("forensic-assembly-*.bin")} <= expected_new,
        "orphaned forensic quad workspace",
    )
    groups = assembly.legacy_reference.parse_maps((work / "used-maps.bin").read_bytes())
    evaluations = (
        map_rows(work / "assembly-evaluations.bin", 496, offset=32)
        if (work / "assembly-evaluations.bin").exists()
        else np.empty((0, 496))
    )
    calls = {int(row[0]): i for i, row in enumerate(evaluations)}
    require(len(calls) == len(evaluations), "duplicate sparse forensic call ID")
    compact = (
        newton_arrays(work / "correction-newton.bin", partial=True)
        if (work / "correction-newton.bin").exists()
        else None
    )
    results, cache, unavailable = {}, {}, {}
    terminal = (work / "status.txt").read_text().splitlines()[-1:]
    if terminal == ["SUCCESS"]:
        require(
            pairs and (work / "baseline-001.bin").exists(),
            "successful process initial forensic workspace missing",
        )
        required_calls = {int(row[0]) for row in evaluations if row[1] == 1}
        if compact is not None and len(compact["ids"]):
            first = compact["ids"][compact["ids"][:, 1] == 1]
            required_calls.update(int(v) for v in first[:, 4] if v > 0)
            required_calls.update(int(v) for v in first[:, 6] if v > 0)
            require(
                (work / "baseline-accepted.bin").exists()
                and (work / "assembly-accepted.bin").exists(),
                "successful trajectory terminal forensic workspace missing",
            )
        else:
            required_calls.update(
                int(row[0]) for row in evaluations if row[1] in (3, 10)
            )
        require(
            all(
                (work / f"forensic-original-{call:012d}.bin").exists()
                and (work / f"forensic-assembly-{call:012d}.bin").exists()
                for call in required_calls
            ),
            "first-step/diagnostic baseline/post forensic coverage incomplete",
        )
    for old_path, new_path in pairs:
        key = old_path.name
        require(
            old_path.is_file() and new_path.is_file(),
            "unpaired original/quad workspace",
        )
        try:
            original_raw, variant_raw = old_path.read_bytes(), new_path.read_bytes()
            old, new = (
                assembly.parse_original(original_raw),
                assembly.parse_workspace(variant_raw),
            )
        except ValueError as exc:
            # An actually failed final evaluation can leave a deliberately
            # incomplete workspace; preserve its bytes and disclose the gap.
            expected_extent = 36 + 490 * 8 + assembly.NQ * 16
            failed_header = (0x43524157, 1, 160, *assembly.NB, assembly.NQ, 0)
            require(
                terminal != ["SUCCESS"]
                and len(variant_raw) == expected_extent
                and struct.unpack_from("<9i", variant_raw) == failed_header,
                str(exc),
            )
            unavailable[key] = str(exc)
            continue
        require(
            assembly._same(new["values"][:330], old["values"][:330]),
            "paired forensic evaluation differs",
        )
        call = new["call"]
        require(call >= 1 and new["values"][0] == call, "noninteger forensic call ID")
        if call in calls:
            row = evaluations[calls[call]]
            assembly._echo(
                tuple(row), new["conditions"], new["Y"], new["variant"], new["original"]
            )
            require(
                assembly._same(row[6:12], new["values"][4:10]),
                "forensic EOS/moments differ",
            )
        else:
            require(
                compact is not None, "forensic call has no retained raw/compact record"
            )
            found = np.flatnonzero(compact["ids"][:, 6] == call)
            require(len(found) == 1, "forensic post call absent/duplicated")
            value = compact["values"][found[0]]
            require(
                assembly._same(new["Y"], value[496:656])
                and assembly._same(new["variant"], value[1616:1776])
                and assembly._same(new["original"], value[1776:1936])
                and new["conditions"][0] == value[0],
                "compact post/workspace binding differs",
            )
        identity = hashlib.sha256(old["comparison"] + new["comparison"]).hexdigest()
        if identity not in cache:
            populated = [
                {**g, "csect": c, "b": b}
                for g, c, b in zip(groups, old["csect"], old["b"], strict=True)
            ]
            verified = assembly.verify_workspace(
                populated,
                data["A"],
                new["Y"],
                new["original"],
                new["variant"],
                new["quad"],
            )
            # Raw operands are retained and reload repeats the exact rational
            # oracle. Keep numeric diagnostics here rather than retaining every
            # potentially enormous rational expansion in process memory/JSON.
            cache[identity] = compact_arithmetic(verified)
        require(cache[identity]["pass"], "forensic ordered quad arithmetic failed")
        results[key] = {
            "pass": True,
            "call": call,
            "arithmetic": identity,
            "original_sha256": digest(old_path),
            "variant_sha256": digest(new_path),
        }
    return {
        "pass": not unavailable,
        "pairs": results,
        "workspaces": cache,
        "unavailable_failed_evaluation": unavailable,
        "ordinary_probe_workspace_scope": "Compact ordinary probes have reconstructible inputs/metadata; their F and polynomial workspaces were not retained.",
    }


def compact_arithmetic(value):
    if isinstance(value, dict):
        if set(value) == {"exact", "rounded"}:
            rounded = value["rounded"]
            return {
                "rounded": np.asarray(
                    [np.nan if x is None else x for x in rounded], dtype="<f8"
                ),
                "rounded_defined": np.asarray(
                    [x is not None for x in rounded], dtype=bool
                ),
                "exact_scope": "recomputed from retained original/quad operands on every analysis and reload",
            }
        return {key: compact_arithmetic(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        array = np.asarray(value)
        if array.dtype.kind in "biuf":
            return array
        return [compact_arithmetic(item) for item in value]
    return value


def matrix_diagnostics(work, assembly):
    """Linear backward error from one retained forensic phase at a time.

    This supplies diagnostics only, with no added gate or forward-error claim.
    LU and pivots remain byte-exact raw arrays in the numeric archive.
    """
    path = work / "assembly-newton.bin"
    result = {"scope": "retained first-step/final-failure phases only", "phases": []}
    if not path.exists():
        result["unavailable"] = "No forensic matrix stream was written."
        return result
    try:
        for record in assembly.newton_records(path):
            ids = record["ids"]
            if ids[9] < 3:
                continue
            matrix = np.asarray(record["M"]).reshape((160, 160), order="F")
            delta, rhs = np.asarray(record["delta"]), np.asarray(record["rhs"])
            available = bool(
                ids[7:9] == (0, 0)
                and np.all(np.isfinite(matrix))
                and np.all(np.isfinite(delta))
                and np.all(np.isfinite(rhs))
            )
            item = {"ids": np.asarray(ids, dtype="<i8"), "available": available}
            if available:
                with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                    residual = matrix @ delta - rhs
                    denominator = np.abs(matrix) @ np.abs(delta) + np.abs(rhs)
                    relative = np.divide(
                        np.abs(residual),
                        denominator,
                        out=np.full(160, np.nan),
                        where=denominator != 0,
                    )
                    norm_scale = np.linalg.norm(matrix, ord=np.inf) * np.max(
                        np.abs(delta)
                    ) + np.max(np.abs(rhs))
                item.update(
                    linear_residual=residual,
                    component_denominator=denominator,
                    component_backward_error=relative,
                    component_defined=denominator != 0,
                    normwise_backward_error=float(np.max(np.abs(residual)) / norm_scale)
                    if norm_scale
                    else None,
                )
            else:
                item["unavailable"] = (
                    "Native LU/solve or retained operands did not complete."
                )
            result["phases"].append(item)
    except ERRORS as exc:
        result["unavailable"] = str(exc)
    return result


def stage_checks(root, prepared, campaign, outcomes, aggregate, stages):
    """Recompute execution prerequisites; a saved success flag grants no authority."""
    records = {r["name"]: r for r in campaign["attempts"]}
    previous = True
    failed_stage = None
    result = {}
    for stage in stages:
        specs = [s for s in prepared["attempts"] if s["stage"] == stage]
        attempted = [records[s["name"]]["status"] not in UNATTEMPTED for s in specs]
        require(
            previous or not any(attempted),
            "dependent stage executed after failed prerequisite",
        )
        passed = all(outcomes[s["name"]].get("pass") is True for s in specs)
        key = {
            "L0-tight": "pilot",
            "L3-tight": "trajectory",
            "derivative": "derivative",
        }.get(stage)
        if key:
            passed = passed and aggregate.get(key, {}).get("pass") is True
        for spec in specs:
            record = records[spec["name"]]
            if record["status"] == "CONDITIONALLY_UNATTEMPTED":
                require(
                    failed_stage is not None
                    and record.get("skip_reason")
                    == failed_stage.upper() + "_JOINT_GATE_FAILED",
                    "unsupported conditional skip",
                )
            elif record["status"] == "UNATTEMPTED":
                require(
                    campaign.get("complete") is not True
                    and bool(record.get("unattempted_reason")),
                    "unattempted named process has no incomplete-campaign reason",
                )
        result[stage] = {
            "pass": passed,
            "attempted": sum(attempted),
            "required": len(specs),
        }
        if previous and not passed:
            failed_stage = stage
        previous = previous and passed
    return result


def analyze(root, host_identity_sha):
    root = Path(root).resolve()
    contract = load("_correction_report_campaign", HERE / "correction_campaign.py")
    checks = load("_correction_report_checks", HERE / "correction_checks.py")
    report = {
        "schema": "crucible.correction.analysis.v1",
        "qualification_pass": False,
        "artifact_identity_pass": False,
        "software_pass": False,
        "trajectory_reference_accepted": False,
        "physical_accuracy_qualified": False,
        "numerical_source": contract.SOURCE_NAME,
        "host_identity_sha256": host_identity_sha,
        "attempts": {},
        "cases": {},
        "errors": [],
        "call_accounting_complete": False,
        "call_count_scope": "Unavailable until all completed named counter outputs are independently checked.",
        "analysis_environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "analysis_code_sha256": {
            name: digest(HERE / name)
            for name in (
                "correction_report.py",
                "correction_checks.py",
                "correction_campaign.py",
                "correction_host_identities.py",
                "assembly_arithmetic.py",
            )
        },
        "metrics_sha256": digest(Path(metrics.__file__)),
        "residual_policy": "Raw residuals are finite diagnostic evidence only; D-036 residual<=1 is not a D-040 acceptance gate.",
    }
    prepared = campaign = None
    try:
        prepared = read_json(root / "prepared.json")
        for spec in prepared["attempts"]:
            report["attempts"][spec["name"]] = {
                **spec,
                "status": "UNDETERMINED"
                if (root / "attempts" / spec["name"]).exists()
                else "UNATTEMPTED",
                "completed": False,
                "unattempted_reason": "CAMPAIGN_RECORD_UNAVAILABLE",
            }
        campaign = read_json(root / "campaign.json")
        report.update(
            {
                k: prepared[k]
                for k in (
                    "source_commit",
                    "source_tree",
                    "protocol_sha256",
                    "build_label",
                )
            }
        )
        report.update(
            prepared_sha256=digest(root / "prepared.json"),
            campaign_sha256=digest(root / "campaign.json"),
            executed_report_sha256=prepared["immutable_files"].get(
                "correction_report.py"
            ),
            preparation_costs=prepared.get("costs"),
            execution_invocations=campaign.get("execution_invocations"),
            artifact_bytes=campaign.get("artifact_bytes"),
            campaign_exception=campaign.get("exception"),
            measurement_scope={
                "setup_load": "preparation_costs; no invented per-process loading measurement",
                "integration_persistence": "retained attempt resource/cost records; scopes reported verbatim",
                "unavailable": "Unmeasured load/integration/raw-persistence subintervals are unknown, not zero.",
            },
        )
        contract.validate_prepared(root, prepared)
        require(
            campaign.get("schema") == "crucible.phase2d.correction-campaign.v1"
            and campaign.get("numerical_source") == contract.SOURCE_NAME
            and campaign.get("build_label") == prepared["build_label"]
            and campaign.get("prepared_sha256") == report["prepared_sha256"],
            "campaign source/preparation binding differs",
        )
        # Reporting-only repair can have a new digest without relabelling the
        # committed physical source; all executed checking semantics stay bound.
        for name in (
            "correction_checks.py",
            "correction_campaign.py",
            "correction_host_identities.py",
            "assembly_arithmetic.py",
            "rhs_reference/arithmetic.py",
            "rhs_reference/reference.py",
        ):
            require(
                prepared["immutable_files"].get(name)
                == digest(
                    HERE / name
                    if not name.startswith("rhs_reference/")
                    else HERE.parent / name
                ),
                "offline gate/dependency differs from executed source: " + name,
            )
        require(
            len(prepared["attempts"]) == len(campaign["attempts"]) == 20
            and len({r["name"] for r in campaign["attempts"]}) == 20,
            "twenty distinct named process records required",
        )
        report["host_identity_verification"] = verify_retained_build(
            root, prepared, campaign, contract, host_identity_sha
        )
        report["artifact_identity_pass"] = True
        report["build"] = campaign["build"]
        report["interrupted_attempts"] = verify_interrupted(
            root, prepared, campaign, contract
        )
        report["infrastructure_recovery"] = campaign.get("infrastructure_recovery")
        allowed = {s["name"] for s in prepared["attempts"]}
        if (root / "attempts").exists():
            require(
                {p.name for p in (root / "attempts").iterdir()} <= allowed,
                "undeclared physical attempt directory",
            )
        outcomes, all_runs = {}, {case: {} for case in contract.CASES}
        for spec, record in zip(
            prepared["attempts"], campaign["attempts"], strict=True
        ):
            require(
                all(record.get(k) == v for k, v in spec.items()),
                "named process plan differs",
            )
            work = root / "attempts" / spec["name"]
            detail = {k: v for k, v in record.items() if k != "science_gate"}
            report["attempts"][spec["name"]] = detail
            if record["status"] in UNATTEMPTED:
                require(not work.exists(), "unattempted process hides raw outputs")
                outcomes[spec["name"]] = {"pass": False}
                continue
            bound = {
                **spec,
                **{
                    k: record[k]
                    for k in ("input_sha256", "state_binding")
                    if k in record
                },
            }
            gate = checks.attempt_gate(root, bound, record)
            detail["recomputed"] = gate
            outcomes[spec["name"]] = gate
            require(
                record.get("qualification_pass") is (gate.get("pass") is True),
                "false saved process qualification",
            )
            if "science_gate" in record:
                require(
                    all(
                        record["science_gate"].get(k) == gate.get(k)
                        for k in (
                            "pass",
                            "identity_failure",
                            "ordinary_numerical_failure",
                        )
                    ),
                    "saved/recomputed process decisions differ",
                )
            detail["counter_evidence"] = verify_counters(
                work,
                record,
                contract.diag.COUNTERS,
                completed=record.get("completed") is True,
            )
            data = checks.parse_input((work / "input.bin").read_bytes())
            if (
                spec["stage"] not in {"control", "derivative"}
                and (work / "accepted.bin").exists()
            ):
                arrays = trajectory_arrays(work, data)
                detail["trajectory"] = arrays
                all_runs[spec["case"]][spec["stage"]] = arrays
            detail["forensic_arithmetic"] = forensic_arithmetic(
                work, data, checks.assembly
            )
            detail["matrix_diagnostics"] = matrix_diagnostics(work, checks.assembly)
            if gate.get("pass") is True:
                require(
                    detail["forensic_arithmetic"]["pass"],
                    "successful process forensic arithmetic unavailable",
                )
            detail["raw_numeric"] = retain_numeric(work)
        report["precision"] = checks.precision_gate(root)
        report["toolchain"] = toolchain_record(root)
        if prepared["build_label"] == "B":
            report["build_b_release"] = contract.build_b_release_gate(root)
        aggregate = {
            "pilot": checks.pilot_gate(root),
            "trajectory": checks.trajectory_gate(root),
            "derivative": checks.derivative_gate(root),
        }
        for key, gate in aggregate.items():
            if key in campaign.get("gates", {}):
                require(
                    campaign["gates"][key].get("pass") is gate.get("pass"),
                    "saved aggregate decision differs",
                )
        report["aggregate_gates"] = aggregate
        report["stages"] = stage_checks(
            root, prepared, campaign, outcomes, aggregate, contract.STAGES
        )
        for case in contract.CASES:
            data = checks.parse_input(
                (root / prepared["inputs"][case]["control"]["path"]).read_bytes()
            )
            report["cases"][case] = case_metrics(
                all_runs[case], np.asarray(data["A"]), np.asarray(data["Z"])
            )
        physical = guarded = 0
        complete_counts = True
        for detail in (
            list(report["attempts"].values()) + report["interrupted_attempts"]
        ):
            counters = detail.get("counter_evidence", detail.get("counters"))
            if counters is None:
                continue
            physical += counters.get("native_counters", {}).get("rhs", 0)
            guarded += counters.get("assembly_counters", {}).get("fresh_requests", 0)
            complete_counts &= counters["complete"]
        require(
            physical == campaign.get("physical_rhs_calls")
            and guarded == campaign.get("guarded_fresh_requests")
            and complete_counts is campaign.get("call_accounting_complete"),
            "campaign counter totals/scope differ",
        )
        report.update(
            physical_rhs_calls_observed=physical,
            guarded_fresh_requests_observed=guarded,
            call_accounting_complete=complete_counts,
            call_count_scope=campaign.get("call_count_scope"),
        )
        accounted = all(
            r.get("completed") is True or r["status"] == "CONDITIONALLY_UNATTEMPTED"
            for r in campaign["attempts"]
        )
        require(
            campaign.get("complete") is accounted,
            "campaign completion accounting differs",
        )
        report["software_pass"] = bool(
            report["artifact_identity_pass"]
            and accounted
            and campaign.get("attempt_accounting_complete") is True
            and report["precision"].get("pass") is True
            and not any(o.get("identity_failure") for o in outcomes.values())
        )
        report["qualification_pass"] = bool(
            report["software_pass"]
            and all(o.get("pass") is True for o in outcomes.values())
            and all(g.get("pass") is True for g in aggregate.values())
            and all(c.get("pass") is True for c in report["cases"].values())
        )
        require(
            campaign.get("qualification_pass") is report["qualification_pass"],
            "saved/recomputed campaign qualification differs",
        )
    except ERRORS as exc:
        report["errors"].append(str(exc))
        report["artifact_identity_pass"] = report["software_pass"] = report[
            "qualification_pass"
        ] = False
    # Identity failure never hides the attempted/unattempted manifest or raw data.
    if campaign is not None:
        for record in campaign.get("attempts", []):
            detail = report["attempts"].setdefault(record["name"], dict(record))
            work = root / "attempts" / record["name"]
            if work.is_dir() and "raw_numeric" not in detail:
                detail["raw_numeric"] = retain_numeric(work)
    return report


def reload_report(root, output, host_identity_sha, *, release=True):
    """Fresh CLI process recomputes every metric and streams every array byte."""
    output = Path(output)
    saved = read_json(output)
    manifest = saved.pop("array_artifact")
    require(
        saved.get("host_identity_sha256") == host_identity_sha,
        "reload host proof differs",
    )
    numeric = safe(output.parent, manifest["path"])
    require(
        numeric == output.with_suffix(".npz") and digest(numeric) == manifest["sha256"],
        "NPZ file identity differs",
    )
    report = analyze(root, host_identity_sha)
    summary, arrays = artifacts.split_report(report)
    require(
        summary == saved and set(arrays) == set(manifest["arrays"]),
        "recomputed report/array membership differs",
    )
    with zipfile.ZipFile(numeric) as archive:
        require(
            len(archive.namelist()) == len(arrays)
            and set(archive.namelist()) == {k + ".npy" for k in arrays},
            "NPZ entry membership differs",
        )
        for key, array in arrays.items():
            expected = manifest["arrays"][key]
            require(
                expected
                == {
                    "dtype": array.dtype.str,
                    "shape": list(array.shape),
                    "sha256": array_digest(array),
                },
                "recomputed array identity differs",
            )
            with archive.open(key + ".npy") as stream:
                version = np.lib.format.read_magic(stream)
                if version == (1, 0):
                    shape, fortran, dtype = np.lib.format.read_array_header_1_0(stream)
                elif version == (2, 0):
                    shape, fortran, dtype = np.lib.format.read_array_header_2_0(stream)
                else:
                    raise ValueError("unsupported numeric artifact NPY version")
                require(
                    dtype.kind in "biuf"
                    and dtype.str == expected["dtype"]
                    and list(shape) == expected["shape"],
                    "NPZ dtype/shape/order differs",
                )
                for block in chunks(array, order="F" if fortran else "C"):
                    require(
                        stream.read(len(block)) == block,
                        "recomputed numeric array bytes differ",
                    )
                require(stream.read(1) == b"", "extra numeric array bytes")
    if release:
        receipt = {
            k: report.get(k)
            for k in (
                "qualification_pass",
                "prepared_sha256",
                "campaign_sha256",
                "source_commit",
                "source_tree",
                "protocol_sha256",
                "build_label",
                "artifact_identity_pass",
            )
        }
        receipt.update(
            schema="crucible.correction.verification.v1",
            reload_pass=True,
            report_json_sha256=digest(output),
            report_npz_sha256=digest(numeric),
            host_identity_sha256=host_identity_sha,
        )
        with output.with_suffix(".release.json").open("x") as stream:
            stream.write(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    return report


def compare_runs(left, right, a, z):
    require(
        np.array_equal(left["requested_t"], right["requested_t"])
        and np.array_equal(left["output_present"], right["output_present"])
        and np.array_equal(left["missing_output"], right["missing_output"]),
        "reproduction requested grid/masks differ",
    )
    result = metrics.assess_reproduction(
        left["requested_t"], left["requested_Y"], right["requested_Y"], a, z
    )
    result.update(
        accepted_mesh_identical=np.array_equal(left["accepted_t"], right["accepted_t"]),
        first_accepted_steps=len(left["accepted_t"]) - 1,
        repeat_accepted_steps=len(right["accepted_t"]) - 1,
        first_accepted_t=left["accepted_t"],
        repeat_accepted_t=right["accepted_t"],
    )
    return result


def compare_campaigns(first_root, repeat_root, a_host_sha, b_host_sha):
    first_root, repeat_root = Path(first_root).resolve(), Path(repeat_root).resolve()
    first, repeat = analyze(first_root, a_host_sha), analyze(repeat_root, b_host_sha)
    p1, p2 = (
        read_json(first_root / "prepared.json"),
        read_json(repeat_root / "prepared.json"),
    )
    result = {
        "schema": "crucible.correction.reproduction.v1",
        "pass": False,
        "first_qualification_pass": first["qualification_pass"],
        "repeat_qualification_pass": repeat["qualification_pass"],
        "first_prepared_sha256": digest(first_root / "prepared.json"),
        "repeat_prepared_sha256": digest(repeat_root / "prepared.json"),
        "first_host_identity_sha256": a_host_sha,
        "repeat_host_identity_sha256": b_host_sha,
        "source_commit": p1.get("source_commit"),
        "source_tree": p1.get("source_tree"),
        "protocol_sha256": p1.get("protocol_sha256"),
        "attempts": {},
        "errors": [],
    }
    try:
        require(
            first_root != repeat_root
            and p1["build_label"] == "A"
            and p2["build_label"] == "B",
            "two independent A/B roots required",
        )
        require(
            first["qualification_pass"] and repeat["qualification_pass"],
            "both independent builds must qualify",
        )
        for key in (
            "source_commit",
            "source_tree",
            "protocol_sha256",
            "inputs",
            "reference_baselines",
            "source_diff",
            "attempts",
        ):
            require(
                p1[key] == p2[key],
                "reproduction frozen source/input membership differs: " + key,
            )
        for name, identity in p1["immutable_files"].items():
            if name != "preparation-history/original-prepared.json":
                require(
                    p2["immutable_files"].get(name) == identity,
                    "reproduction immutable source/input differs: " + name,
                )
        require(
            first["build"]["libraries"] == repeat["build"]["libraries"],
            "reproduction linked libraries differ",
        )
        require(
            first["toolchain"] == repeat["toolchain"],
            "reproduction actual compiler/module/flags/environment differs",
        )
        for name, left in first["attempts"].items():
            right = repeat["attempts"][name]
            require(
                left.get("loaded_library_hashes") == right.get("loaded_library_hashes"),
                "reproduction actual runtime library mapping differs: " + name,
            )
        for case in ("development", "validation"):
            with np.load(
                first_root / "inputs" / (case + ".npz"), allow_pickle=False
            ) as data:
                z, a = data["species_Z_A"].T
            for stage in (
                "L0-standard",
                "L0-tight",
                "L1-standard",
                "L2-standard",
                "L3-standard",
                "L3-tight",
            ):
                name = case + "-" + stage
                left, right = first["attempts"][name], repeat["attempts"][name]
                require(
                    left["status"] == right["status"]
                    and left.get("completed") is right.get("completed")
                    and left["recomputed"]["pass"] is right["recomputed"]["pass"],
                    "reproduction status differs",
                )
                item = compare_runs(left["trajectory"], right["trajectory"], a, z)
                item["counter_differences"] = {
                    k: right["native_counters"][k] - left["native_counters"][k]
                    for k in left["native_counters"]
                }
                result["attempts"][name] = item
        result["pass"] = len(result["attempts"]) == 12 and all(
            r["pass"] for r in result["attempts"].values()
        )
    except ERRORS as exc:
        result["errors"].append(str(exc))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "reload"):
        child = sub.add_parser(command)
        child.add_argument("root", type=Path)
        child.add_argument("output", type=Path)
        child.add_argument("--host-identity-sha", required=True)
    child = sub.add_parser("compare")
    child.add_argument("first", type=Path)
    child.add_argument("repeat", type=Path)
    child.add_argument("output", type=Path)
    child.add_argument("--a-host-identity-sha", required=True)
    child.add_argument("--b-host-identity-sha", required=True)
    args = parser.parse_args()
    if args.command == "reload":
        report = reload_report(args.root, args.output, args.host_identity_sha)
    elif args.command == "analyze":
        report = analyze(args.root, args.host_identity_sha)
        write_report(args.output, report)
    else:
        report = compare_campaigns(
            args.first, args.repeat, args.a_host_identity_sha, args.b_host_identity_sha
        )
        write_report(args.output, report)
    passed = report.get("qualification_pass", report.get("pass", False))
    print(
        json.dumps(
            {
                "command": args.command,
                "qualification_pass": passed,
                "errors": report.get("errors", []),
            },
            allow_nan=False,
        )
    )
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
