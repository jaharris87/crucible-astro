"""Run only the fixed accepted 2D native campaign; standard library on the host.

The executable performs the physics. This file supplies no RHS callback or model.
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import struct
import subprocess
import time
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    temporary = path.with_suffix(".pending")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def snapshot(root):
    return {
        str(p.relative_to(root)): {"sha256": digest(p), "bytes": p.stat().st_size}
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name not in {"attempt.json", "attempt.pending"}
    }


def diagnostic_input(template, accepted, when, target):
    """Extract an exact accepted state without any physical evaluation."""
    data = bytearray(template.read_bytes())
    if len(data) < 48:
        raise ValueError("truncated native input header")
    header = list(struct.unpack_from("<8i", data))
    magic, version, n, nk, nr, nm, mode, coordinate = header
    if (
        magic != 0x43524432
        or version != 1
        or n != 160
        or nk < 2
        or nr < 1
        or nm < 1
        or mode != 0
        or not 1 <= coordinate <= n
    ):
        raise ValueError("invalid diagnostic input template header")
    if len(data) != 48 + 8 * (3 * n + 3 * nk + nr + nm):
        raise ValueError("diagnostic input template length differs")
    width = (3 * n + 8) * 8
    raw = accepted.read_bytes()
    if not raw or len(raw) % width:
        raise ValueError("malformed finest trajectory for diagnostic input")
    rows = [raw[i : i + width] for i in range(0, len(raw), width)]
    selected = [r for r in rows if struct.unpack_from("<d", r)[0] == when]
    if len(selected) != 1:
        raise ValueError("missing/duplicate finest diagnostic state")
    # Fixed prefix: header, nonlinear controls, Z, A, Y0, then forcing arrays.
    y_start = 32 + 16 + 2 * n * 8
    data[y_start : y_start + n * 8] = selected[0][8 : (n + 1) * 8]
    grid_start = 32 + 16 + (3 * n + 3 * nk) * 8
    del data[grid_start:]
    data.extend(struct.pack("<2d", when, when))
    header[4:7] = [1, 1, 2]
    struct.pack_into("<8i", data, 0, *header)
    if nr < 1 or nm < 1:
        raise ValueError("invalid template grids")
    target.write_bytes(data)


def synthetic_checks(root):
    """Exercise the actual compiled numerical adapter before physical controls."""
    scenarios = [
        ("trajectory_synthetic", name, None)
        for name in ("polynomial", "nonlinear", "boundary", "projection")
    ]
    scenarios += [
        ("trajectory_synthetic", "failed-lu", "FAILURE LAPACK dgetrf info="),
        (
            "trajectory_synthetic",
            "nonfinite",
            "FAILURE nonfinite computed physical F/assembly workspace",
        ),
        ("forcing_synthetic", "forcing", None),
        ("forcing_synthetic", "outside", "Forcing outside closed coverage"),
        ("forcing_synthetic", "nonfinite", "Nonfinite forcing time"),
        ("forcing_synthetic", "nonincreasing", "Nonincreasing forcing"),
    ]
    record_path = root / "synthetic.json"
    if record_path.exists():
        result = json.loads(record_path.read_text())
        for scenario in result["scenarios"]:
            if (
                digest(root / "bundle" / scenario["executable"])
                != scenario["executable_sha256"]
            ):
                raise ValueError("synthetic executable identity changed")
        for name, identity in result["files"].items():
            if digest(root / name) != identity:
                raise ValueError("completed synthetic evidence changed")
        if not result["pass"]:
            raise ValueError(
                "failed synthetic prerequisite cannot retry as infrastructure"
            )
        return result
    records = []
    for executable, name, expected_failure in scenarios:
        work = root / "synthetic" / (executable + "-" + name)
        work.mkdir(parents=True, exist_ok=False)
        start = time.perf_counter()
        with (work / "process.log").open("xb") as log:
            process = subprocess.run(
                [str(root / "bundle" / executable), name],
                cwd=work,
                stdout=log,
                stderr=log,
            )
        status = work / (
            "status.txt"
            if executable == "trajectory_synthetic"
            else "fixture-status.txt"
        )
        text = (work / "process.log").read_text(errors="replace")
        terminal = status.read_text().splitlines()[-1] if status.exists() else "MISSING"
        passed = (
            process.returncode == 0
            and terminal
            == ("SUCCESS" if executable == "trajectory_synthetic" else "PASS")
            if expected_failure is None
            else process.returncode > 0
            and expected_failure in text
            and "UNEXPECTED" not in text
        )
        records.append(
            {
                "name": name,
                "executable": executable,
                "executable_sha256": digest(root / "bundle" / executable),
                "returncode": process.returncode,
                "terminal_status": terminal,
                "expected_failure": expected_failure,
                "pass": passed,
                "wall_seconds": time.perf_counter() - start,
            }
        )
    result = {
        "pass": all(r["pass"] for r in records),
        "scenarios": records,
        "files": {
            str(p.relative_to(root)): digest(p)
            for p in (root / "synthetic").rglob("*")
            if p.is_file()
        },
    }
    save(record_path, result)
    if not result["pass"]:
        raise ValueError(
            "native synthetic prerequisite failed; no physical control authorized to start"
        )
    return result


def run_attempt(root, spec, executable, launcher, *, resume):
    work = root / "attempts" / spec["name"]
    record_path = work / "attempt.json"
    if record_path.exists():
        old = json.loads(record_path.read_text())
        if resume and old.get("completed"):
            if old["executable_sha256"] != digest(executable):
                raise ValueError("restart executable identity changed")
            for name, identity in old["files"].items():
                p = work / name
                if not p.is_file() or digest(p) != identity["sha256"]:
                    raise ValueError("restart completed artifact changed")
            return old
        raise ValueError("existing incomplete attempt needs a new retained attempt ID")
    work.mkdir(parents=True, exist_ok=True)
    source = root / spec["input"]
    if digest(source) != spec["input_sha256"]:
        raise ValueError("prepared input identity changed")
    (work / "input.bin").write_bytes(source.read_bytes())
    for name in ("network", "helm_table.dat"):
        (work / name).symlink_to(Path("../../bundle") / name)
    record = {
        "name": spec["name"],
        "mode": spec["mode"],
        "executable_sha256": digest(executable),
        "input_sha256": digest(source),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed": False,
        "status": "RUNNING",
    }
    save(record_path, record)
    start = time.perf_counter()
    cpu = time.process_time()
    with (work / "process.log").open("xb") as log:
        try:
            result = subprocess.run(
                [*launcher, str(executable)], cwd=work, stdout=log, stderr=log
            )
            record["returncode"] = result.returncode
            record["status"] = "RETURNED" if result.returncode == 0 else "FAILED"
        except Exception as exc:
            record.update(status="EXCEPTION", exception=repr(exc), returncode=None)
    record.update(
        wall_seconds=time.perf_counter() - start,
        runner_cpu_seconds=time.process_time() - cpu,
        completed=True,
    )
    maps = work / "loaded-maps.txt"
    libraries = {}
    if maps.exists():
        for line in maps.read_text().splitlines():
            columns = line.split(maxsplit=5)
            if len(columns) == 6 and "x" in columns[1] and columns[5].startswith("/"):
                path = Path(columns[5])
                if path.resolve() == executable.resolve():
                    continue
                libraries[str(path)] = digest(path) if path.is_file() else None
    record["loaded_library_hashes"] = libraries
    record["loaded_mapping_hash_scope"] = (
        "executable file-backed mappings, excluding the separately hashed native executable; all mappings retained raw"
    )
    record["loaded_library_unavailable_reason"] = (
        None
        if libraries and all(libraries.values())
        else "loaded mapping absent or named file unavailable; see retained runtime log"
    )
    memory = work / "memory-status.txt"
    record["native_peak_rss_bytes"] = None
    if memory.exists():
        for line in memory.read_text().splitlines():
            if line.startswith("VmHWM:"):
                record["native_peak_rss_bytes"] = int(line.split()[1]) * 1024
    log_file = work / "native.log"
    record["native_timings"] = {}
    if log_file.exists():
        for line in log_file.read_text().splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[0].endswith("_SECONDS"):
                try:
                    record["native_timings"][fields[0]] = float(
                        fields[1].replace("D", "E")
                    )
                except ValueError:
                    pass
    record["timing_scope"] = (
        "parent wall includes launcher; native physical-phase timing includes RHS/Jacobian, nonlinear work and incremental output; post-phase persistence is runtime snapshot only"
    )
    record["files"] = snapshot(work)
    save(record_path, record)
    return record


def execute(root, *, srun=False, resume=False, restart_reason=None):
    root = Path(root).resolve()
    specification = json.loads((root / "prepared.json").read_text())
    if (
        specification.get("protocol_sha256")
        != "966fbff8d2322ae8e6666063f35c1b87cced7d5ccbaf663ccae362613f98fdad"
    ):
        raise ValueError("unaccepted protocol identity")
    for name, expected in specification["immutable_files"].items():
        if digest(root / name) != expected:
            raise ValueError("prepared source/input changed before execution")
    if digest(Path(__file__)) != specification["immutable_files"]["campaign.py"]:
        raise ValueError("running campaign source differs from prepared source")
    executable = root / "bundle/trajectory_driver"
    if not executable.is_file():
        raise ValueError("native executable missing; use the accepted fresh build")
    synthetic = synthetic_checks(root)
    manifest_path = root / "campaign.json"
    if manifest_path.exists() and not resume:
        raise ValueError("campaign already exists")
    if resume:
        if not isinstance(restart_reason, str) or not restart_reason.strip():
            raise ValueError("infrastructure restart requires its retained reason")
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("complete"):
            raise ValueError("a completed campaign cannot restart")
        if manifest.get("restart_count", 0) != 0:
            raise ValueError("single infrastructure restart already used")
        manifest["restart_count"] = 1
        manifest["restart_reason"] = restart_reason
        # An incomplete process is retained rather than silently relaunched.
        for attempt in (root / "attempts").glob("*/attempt.json"):
            record = json.loads(attempt.read_text())
            if not record.get("completed"):
                retained = attempt.parent.with_name(
                    attempt.parent.name + "-interrupted"
                )
                attempt.parent.rename(retained)
    else:
        manifest = {
            "schema": "crucible.phase2d.campaign.v1",
            "prepared_sha256": digest(root / "prepared.json"),
            "executable_sha256": digest(executable),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "threads": {
                k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")
            },
            "restart_count": 0,
            "attempts": [],
            "complete": False,
            "synthetic_pass": synthetic["pass"],
        }
    if manifest["prepared_sha256"] != digest(root / "prepared.json"):
        raise ValueError("campaign prepared identity changed")
    launcher = ["srun", "-n", "1", "-c", "1"] if srun else []
    start = time.perf_counter()
    save(manifest_path, manifest)
    try:
        for spec in specification["attempts"]:
            if spec["mode"] == 2 and spec["time"] != 0.0:
                finest = root / "attempts" / (spec["case"] + "-L3")
                state_file = root / spec["input"]
                if not state_file.exists():
                    try:
                        diagnostic_input(
                            root / specification["templates"][spec["case"]],
                            finest / "accepted.bin",
                            spec["time"],
                            state_file,
                        )
                    except (OSError, ValueError) as exc:
                        manifest["attempts"].append(
                            {
                                "name": spec["name"],
                                "completed": False,
                                "status": "UNAVAILABLE_FINEST_STATE",
                                "exception": str(exc),
                            }
                        )
                        save(manifest_path, manifest)
                        continue
                spec = {**spec, "input_sha256": digest(state_file)}
            result = run_attempt(root, spec, executable, launcher, resume=resume)
            manifest["attempts"] = [
                a for a in manifest["attempts"] if a["name"] != result["name"]
            ] + [result]
            save(manifest_path, manifest)
            if spec["mode"] == 0:
                actual = root / "attempts" / spec["name"] / "control.bin"
                expected = root / spec["expected"]
                native_status = root / "attempts" / spec["name"] / "status.txt"
                if (
                    result["returncode"] != 0
                    or not native_status.exists()
                    or native_status.read_text().splitlines()[-1] != "SUCCESS"
                    or not actual.is_file()
                    or actual.read_bytes() != expected.read_bytes()
                ):
                    raise ValueError(
                        "exact initial RHS control failed; campaign stopped"
                    )
        manifest["complete"] = True  # Attempt completeness, not numerical acceptance.
    except Exception as exc:
        manifest["exception"] = repr(exc)
        raise
    finally:
        manifest["wall_seconds_this_process"] = time.perf_counter() - start
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        manifest["children_cpu_seconds"] = usage.ru_utime + usage.ru_stime
        manifest["children_peak_rss_bytes"] = usage.ru_maxrss * (
            1024 if platform.system() == "Linux" else 1
        )
        manifest["artifact_bytes"] = sum(
            p.stat().st_size
            for p in (root / "attempts").rglob("*")
            if p.is_file() and not p.is_symlink()
        )
        save(manifest_path, manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--srun", action="store_true")
    parser.add_argument("--infrastructure-restart", action="store_true")
    parser.add_argument("--restart-reason")
    args = parser.parse_args()
    execute(
        args.root,
        srun=args.srun,
        resume=args.infrastructure_restart,
        restart_reason=args.restart_reason,
    )
