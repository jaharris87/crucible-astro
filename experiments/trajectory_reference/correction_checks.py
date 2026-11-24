"""D-040 raw numerical checks, usable with only the host Python standard library.

No producer is imported or invoked. Numerical failure remains distinct from
artifact corruption. The native producer owns all integration and physical calls.
"""

import hashlib
import importlib.util
import json
import math
import struct
from bisect import bisect_right
from pathlib import Path

HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "_correction_assembly_arithmetic", HERE / "assembly_arithmetic.py"
)
assembly = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(assembly)
PROTOCOL_SHA256 = "a7eac47716dc710780469b4f107adec59e3fd6e60d435cd62ef60560f13be0a8"
SOURCE = "native-XNet-b64-productsum113-b64-v1"
N = 160
EPS = 2.0**-52
NEWTON_HEADER = (0x4352434E, 1, N, 1936, 12, 0, 0, 0)
ACCEPTED_HEADER = (0x43524341, 1, N, 496, 0, 0, 0, 0)
NEWTON_RECORD = struct.Struct("<12q1936d")
CONTROLS = {"standard": (1e-15, 1e-13), "tight": (1e-16, 1e-14)}


def require(condition, message):
    if not condition:
        raise ValueError("correction reference: " + message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def same(left, right):
    return len(left) == len(right) and struct.pack(
        "<" + str(len(left)) + "d", *left
    ) == struct.pack("<" + str(len(right)) + "d", *right)


def close(left, right, magnitude=None, factor=128):
    require(len(left) == len(right), "numeric extent differs")
    if magnitude is None:
        magnitude = [max(abs(a), abs(b)) for a, b in zip(left, right, strict=True)]
    require(
        all(
            math.isfinite(a)
            and math.isfinite(b)
            and abs(a - b) <= factor * EPS * m + 32 * math.ulp(0.0)
            for a, b, m in zip(left, right, magnitude, strict=True)
        ),
        "retained numerical calculation differs",
    )


def rows(path, width, *, header=None, partial=False):
    """Stream complete records; a partial prefix is diagnostic only."""
    record = struct.Struct("<" + str(width) + "d")
    with Path(path).open("rb") as stream:
        if header is not None:
            require(
                stream.read(4 * len(header))
                == struct.pack("<" + str(len(header)) + "i", *header),
                "binary header differs: " + Path(path).name,
            )
        while raw := stream.read(record.size):
            if partial and len(raw) != record.size:
                break
            require(len(raw) == record.size, "truncated record: " + Path(path).name)
            yield record.unpack(raw)


def parse_input(raw):
    """The old wire layout with explicitly different correction-control fields.

    Delegate unchanged structural/physical checks to the D-039 decoder after
    supplying its historical control header in memory. Never mutate an input
    artifact; return the actual new controls under their new meaning.
    """
    require(len(raw) >= 48, "truncated correction input")
    controls = struct.unpack_from("<2d", raw, 32)
    require(controls in CONTROLS.values(), "unapproved correction controls")
    data = assembly.parse_input(raw[:32] + struct.pack("<2d", 1e-13, 1e-11) + raw[48:])
    data["header"] = struct.unpack_from("<8i2d", raw)
    data["controls"] = controls
    data["control_meaning"] = "raw_Newton_correction"
    data["correction_controls"] = controls
    data["residual_controls"] = (1e-13, 1e-11)
    return data


def newton_rows(path, *, partial=False):
    with Path(path).open("rb") as stream:
        require(
            stream.read(32) == struct.pack("<8i", *NEWTON_HEADER),
            "Newton header differs",
        )
        while raw := stream.read(NEWTON_RECORD.size):
            if partial and len(raw) != NEWTON_RECORD.size:
                break
            require(len(raw) == NEWTON_RECORD.size, "truncated compact Newton row")
            values = NEWTON_RECORD.unpack(raw)
            yield {
                "ids": values[:12],
                "scalars": values[12:28],
                **{
                    name: values[28 + i * N : 28 + (i + 1) * N]
                    for i, name in enumerate(
                        (
                            "old",
                            "pre",
                            "unprojected",
                            "post",
                            "delta",
                            "previous",
                            "applied",
                            "weight",
                            "residual",
                            "projection",
                            "variant",
                            "original",
                        )
                    )
                },
            }


def verify_newton(row, a, controls, previous=None):
    """Independently check one completed raw update, never a rounded-change test."""
    ids, scalars = row["ids"], row["scalars"]
    require(ids[9] == 4 and ids[7:9] == (0, 0), "incomplete/failed Newton solve")
    require(
        all(math.isfinite(v) for v in scalars[:11] + scalars[12:])
        and all(
            math.isfinite(v)
            for key, vector in row.items()
            if key not in {"ids", "scalars", "previous"}
            for v in vector
        ),
        "nonfinite completed Newton record",
    )
    time, h, residual_inf, residual_l1, projection_l1, cumulative = scalars[:6]
    require(h > 0 and time >= h and cumulative >= 0, "invalid Newton time/projection")
    require(
        tuple(scalars[6:10]) == (1e-13, 1e-11, *controls), "changed Newton controls"
    )
    old, pre, post, delta = (row[k] for k in ("old", "pre", "post", "delta"))
    unprojected = [y + d for y, d in zip(pre, delta, strict=True)]
    close(
        row["unprojected"],
        unprojected,
        [abs(y) + abs(d) for y, d in zip(pre, delta, strict=True)],
    )
    require(
        same(post, [0.0 if y < 0 else y for y in row["unprojected"]]),
        "changed projection policy",
    )
    close(row["applied"], [y - p for y, p in zip(post, pre, strict=True)])
    close(
        row["projection"],
        [y - u for y, u in zip(post, row["unprojected"], strict=True)],
    )
    weight = [
        controls[0] + controls[1] * max(abs(m * x), abs(m * y))
        for m, x, y in zip(a, old, post, strict=True)
    ]
    close(row["weight"], weight)
    residual = [
        y - x - h * f for x, y, f in zip(old, post, row["variant"], strict=True)
    ]
    close(
        row["residual"],
        residual,
        [
            abs(x) + abs(y) + abs(h * f)
            for x, y, f in zip(old, post, row["variant"], strict=True)
        ],
    )
    current = max(abs(m * d) / w for m, d, w in zip(a, delta, weight, strict=True))
    close([scalars[10]], [current])
    if previous is None:
        require(
            ids[2] == 1
            and all(math.isnan(v) for v in row["previous"])
            and math.isnan(scalars[11]),
            "retry did not reset correction history",
        )
        previous_norm = None
    else:
        require(
            same(row["previous"], previous["delta"]), "previous raw correction changed"
        )
        require(ids[2] == previous["ids"][2] + 1, "Newton iteration gap")
        require(
            same(pre, previous["post"]) and same(old, previous["old"]),
            "Newton state continuity differs",
        )
        previous_norm = max(
            abs(m * d) / w for m, d, w in zip(a, row["previous"], weight, strict=True)
        )
        close([scalars[11]], [previous_norm])
    w_residual = [
        1e-13 + 1e-11 * max(abs(m * x), abs(m * y))
        for m, x, y in zip(a, old, post, strict=True)
    ]
    close(
        [residual_inf, residual_l1],
        [
            max(
                abs(m * r) / w
                for m, r, w in zip(a, row["residual"], w_residual, strict=True)
            ),
            sum(abs(m * r) for m, r in zip(a, row["residual"], strict=True)),
        ],
        factor=1024,
    )
    close(
        [projection_l1],
        [sum(abs(m * p) for m, p in zip(a, row["projection"], strict=True))],
        factor=1024,
    )
    close(
        list(scalars[12:]),
        [
            max(abs(m * d) for m, d in zip(a, delta, strict=True)),
            sum(abs(m * d) for m, d in zip(a, delta, strict=True)),
            max(abs(m * d) for m, d in zip(a, row["applied"], strict=True)),
            sum(abs(m * d) for m, d in zip(a, row["applied"], strict=True)),
        ],
        factor=1024,
    )
    require(ids[11] == int(same(pre, post)), "bitwise stagnation flag differs")
    return {
        "small_pair": previous_norm is not None and current <= 1 and previous_norm <= 1,
        "current": current,
        "previous": previous_norm,
        "residual_norm": residual_inf,
        "projection": projection_l1,
        "cumulative_before": cumulative,
    }


def trajectory_data(work, data, *, validate=True):
    work = Path(work)
    accepted = list(rows(work / "accepted.bin", 488))
    physical = list(rows(work / "correction-accepted.bin", 496, header=ACCEPTED_HEADER))
    require(
        len(accepted) == len(physical) and accepted,
        "accepted physical record alignment differs",
    )
    a, z = data["A"], data["Z"]
    times = [r[0] for r in accepted]
    require(
        times[0] == 0
        and times[-1] == 0.01
        and all(y > x for x, y in zip(times, times[1:])),
        "incomplete/nonincreasing accepted horizon",
    )
    require(same(accepted[0][1:161], data["Y0"]), "initial state changed")
    requested = []
    for time in data["outputs"]:
        indices = [i for i, value in enumerate(times) if value == time]
        require(len(indices) == 1, "requested output missing/duplicated")
        requested.append(accepted[indices[0]][1:161])
    require(
        all(time in times for time in data["mesh"]),
        "requested integration mesh incomplete",
    )
    drift = 0.0
    b0 = math.fsum(m * y for m, y in zip(a, data["Y0"], strict=True))
    for ordinal, (row, native) in enumerate(zip(accepted, physical, strict=True)):
        require(
            all(math.isfinite(v) for v in row + native), "nonfinite accepted record"
        )
        y, f = row[1:161], row[161:321]
        require(
            native[1] == 11
            and native[3] == row[0]
            and same(native[16:176], y)
            and same(native[336:496], f),
            "accepted source association differs",
        )
        require(
            native[12:16] == (1.0, 1.0, 1.0, 1.0), "accepted precision mode differs"
        )
        conditions = assembly.forcing(data, row[0])
        require(same(native[4:6], conditions), "accepted forcing/interpolant differs")
        b, charge, ye = assembly.domain(y, *conditions, z, a)
        close(native[6:9], (b, charge, ye), factor=2048)
        close(row[481:484], (b, charge, ye), factor=2048)
        drift = max(drift, abs(b - b0))
        require(
            abs(b - b0) <= 1e-10 * max(1, abs(b0)), "accepted baryon inventory drift"
        )
        require(
            0 <= row[486] <= 1e-12 and 0 <= row[487] <= 1e-10,
            "accepted projection bound",
        )
        if ordinal == 0:
            require(row[486] == row[487] == 0, "initial projection nonzero")
    if validate:
        completed = {}
        previous = None
        key = None
        count = 0
        max_residual = 0.0
        stagnations = 0
        for row in newton_rows(work / "correction-newton.bin"):
            ids = row["ids"]
            this_key = (ids[1], ids[10])
            if this_key != key:
                previous, key = None, this_key
            check = verify_newton(row, a, data["correction_controls"], previous)
            require(ids[0] == count + 1, "global Newton counter gap")
            step = ids[1]
            require(
                1 <= step < len(accepted), "Newton step outside accepted trajectory"
            )
            require(
                same(row["old"], accepted[step - 1][1:161]),
                "Newton old state is not preceding accepted state",
            )
            if check["small_pair"]:
                require(step not in completed, "Newton continued after accepted pair")
                endpoint = accepted[step]
                require(
                    row["scalars"][0] == endpoint[0]
                    and same(row["post"], endpoint[1:161])
                    and same(row["variant"], endpoint[161:321])
                    and same(row["residual"], endpoint[321:481]),
                    "accepted endpoint not converged Newton iterate",
                )
                close(
                    [endpoint[484], endpoint[485], endpoint[486], endpoint[487]],
                    [
                        row["scalars"][2],
                        row["scalars"][3],
                        check["projection"],
                        check["cumulative_before"] + check["projection"],
                    ],
                )
                completed[step] = check
            max_residual = max(max_residual, check["residual_norm"])
            stagnations += ids[11]
            previous = row
            count += 1
        require(
            set(completed) == set(range(1, len(accepted))),
            "accepted step lacks two-correction evidence",
        )
    else:
        count, max_residual, stagnations = None, None, None
    return {
        "times": times,
        "accepted_Y": [r[1:161] for r in accepted],
        "requested_time": data["outputs"],
        "requested_Y": requested,
        "accepted_rows": accepted,
        "max_baryon_drift": drift,
        "newton_iterations": count,
        "max_residual_norm_diagnostic": max_residual,
        "bitwise_stagnations": stagnations,
    }


def compare_values(left, right, a):
    require(len(left) == len(right) and left, "comparison output extent differs")
    linf = l1 = 0.0
    location = None
    for j, (x, y) in enumerate(zip(left, right, strict=True)):
        require(len(x) == len(y) == N, "comparison species extent differs")
        difference = [abs(m * (v - u)) for m, u, v in zip(a, x, y, strict=True)]
        require(all(math.isfinite(v) for v in difference), "nonfinite comparison")
        if max(difference) > linf:
            location = [j, difference.index(max(difference))]
        linf, l1 = max(linf, max(difference)), max(l1, sum(difference))
    return {"linf": linf, "l1": l1, "linf_location": location}


def strict_refinement(coarse, fine):
    """Same containment criterion as the checked 2D array scorer, including retries."""
    for left, right in zip(fine, fine[1:]):
        index = bisect_right(coarse, left) - 1
        if 0 <= index < len(coarse) - 1 and right <= coarse[index + 1]:
            if right - left < coarse[index + 1] - coarse[index]:
                return True
    return False


def verify_work_counters(work, counters):
    """Validate ordinary-step diagnostic coverage without inventing probe F."""
    n = counters["rhs"]
    original_flags = assembly._rows(work / "diagnostic-ieee.bin", 11, "q")
    module_flags = assembly._rows(work / "assembly-ieee.bin", 21, "q", 16)
    with (work / "assembly-ieee.bin").open("rb") as stream:
        require(
            stream.read(16) == struct.pack("<4i", 0x43524149, 1, 21, 0),
            "IEEE header differs",
        )
    for identifier in range(1, n + 1):
        old, variant = next(original_flags, None), next(module_flags, None)
        require(
            old is not None
            and old[:9] == (identifier, 1, 1, 1, 1, 1, 0, 0, 0)
            and all(v in (0, 1) for v in old[9:]),
            "original IEEE/request coverage differs",
        )
        require(
            variant is not None
            and variant[0] == identifier
            and all(v in (0, 1) for v in variant[1:])
            and all(variant[i : i + 3] == (0, 0, 0) for i in (1, 6, 11, 16)),
            "assembly IEEE/request coverage differs",
        )
    require(
        next(original_flags, None) is None and next(module_flags, None) is None,
        "undeclared IEEE evaluations",
    )
    expected_jacobian = 0
    for row in rows(work / "jacobian-bases.bin", 164):
        expected_jacobian += 1
        require(
            row[0] == expected_jacobian and all(math.isfinite(v) for v in row),
            "Jacobian baseline coverage differs",
        )
    require(
        expected_jacobian == counters["jacobian"], "Jacobian baseline count differs"
    )
    columns = 0
    for row in rows(work / "fd-columns.bin", 6):
        require(
            row[:2] == (columns // N + 1, columns % N + 1)
            and row[2] in (-1, 0, 1)
            and row[3] in range(9)
            and all(math.isfinite(v) for v in row)
            and row[4] != 0
            and row[5] != 0
            and row[4] != row[5],
            "selected FD column coverage differs",
        )
        columns += 1
    require(columns == N * counters["jacobian"], "selected column count differs")
    attempts = guarded_probes = 0
    for row in rows(work / "fd-probe-attempts.bin", 12):
        require(
            all(math.isfinite(v) for v in row)
            and 1 <= row[0] <= counters["jacobian"]
            and 1 <= row[1] <= N
            and row[2] in (-1, 0, 1)
            and row[8] in (0, 1)
            and row[9] in (0, 1)
            and all(v == int(v) and 0 <= v <= n for v in row[10:]),
            "FD attempt metadata differs",
        )
        attempts += 1
        # Erased/duplicate representable increments are recorded before fresh()
        # and therefore make no guarded physical probe request.
        if row[4] != 0 and row[5] != 0 and row[4] != row[5]:
            guarded_probes += 2
    require(guarded_probes == counters["probe"], "FD guarded-probe counter differs")
    signature = [0] * 10240
    last_call = 0
    for call, time, index, before, after in rows(work / "branch-events.bin", 5):
        require(
            call == int(call)
            and last_call <= call <= n
            and 1 <= index <= len(signature)
            and index == int(index)
            and before == int(before)
            and after == int(after)
            and before != after
            and math.isfinite(time),
            "branch transition metadata differs",
        )
        index = int(index) - 1
        require(signature[index] == before, "branch transition history differs")
        signature[index], last_call = int(after), int(call)
    return {"ieee_calls": n, "selected_columns": columns, "probe_attempts": attempts}


def inspect_attempt(root, spec, result):
    """Verify completed raw process identity without requiring numerical success."""
    root = Path(root)
    work = root / "attempts" / spec["name"]
    record = read_json(work / "attempt.json")
    require(
        all(result.get(k) == value for k, value in record.items()),
        "campaign/attempt record differs",
    )
    inventory = {
        str(p.relative_to(work))
        for p in work.rglob("*")
        if p.is_file() and p.name not in {"attempt.json", "attempt.pending"}
    }
    require(inventory == set(record["files"]), "attempt output inventory differs")
    for name, info in record["files"].items():
        require(
            digest(work / name) == info["sha256"]
            and (work / name).stat().st_size == info["bytes"],
            "attempt artifact changed",
        )
    require(
        record["executable_sha256"] == digest(root / "bundle/trajectory_driver"),
        "attempt executable differs",
    )
    require(
        digest(root / spec["input"]) == spec["input_sha256"]
        and (work / "input.bin").read_bytes() == (root / spec["input"]).read_bytes(),
        "attempt input differs",
    )
    require(
        record.get("loaded_library_hashes")
        and all(record["loaded_library_hashes"].values()),
        "actual runtime library identities unavailable",
    )
    data = parse_input((work / "input.bin").read_bytes())
    require(
        (work / "species.bin").read_bytes()
        == (work / "input.bin").read_bytes()[48 : 48 + 2 * N * 8],
        "species echo changed",
    )
    maps = (work / "used-maps.bin").read_bytes()
    expected = assembly.legacy_reference.expected_maps(
        (root / "bundle/network/nets3").read_bytes(),
        (root / "bundle/network/nets4").read_bytes(),
    )
    require(maps == expected, "actual network mapping differs")
    if spec["stage"] == "derivative" and spec["time"] != 0:
        source = root / "attempts" / (spec["case"] + "-L3-standard")
        source_data = parse_input((source / "input.bin").read_bytes())
        selected = [
            row for row in rows(source / "accepted.bin", 488) if row[0] == spec["time"]
        ]
        require(
            len(selected) == 1 and same(data["Y0"], selected[0][1:161]),
            "diagnostic state is not exact L3 output",
        )
        require(
            data["outputs"] == data["mesh"] == (spec["time"],),
            "frozen diagnostic clock differs",
        )
        for key in ("Z", "A", "knots", "T9", "rho", "coordinate"):
            require(
                data[key] == source_data[key],
                "frozen diagnostic forcing/species binding differs",
            )
    assembly._kind((work / "assembly-kind.bin").read_bytes())
    static = {
        "input": data,
        "species": (work / "species.bin").read_bytes(),
        "map_bytes": maps,
        "groups": assembly.legacy_reference.parse_maps(maps),
    }
    terminal = (work / "status.txt").read_text().splitlines()[-1:]
    success = (
        record.get("completed") is True
        and record.get("returncode") == 0
        and terminal == ["SUCCESS"]
    )
    return work, record, static, success, terminal


def control_check(root, spec, work, static):
    prepared = read_json(Path(root) / "prepared.json")
    references = prepared["reference_baselines"][spec["case"] + "-initial"]
    for name in (
        "baseline-001.bin",
        "assembly-baseline-001.bin",
        "species.bin",
        "used-maps.bin",
        "assembly-kind.bin",
    ):
        entry = references[name]
        expected = Path(root) / entry["path"]
        require(digest(expected) == entry["sha256"], "retained D-039 control changed")
        actual = work / name
        if name == "baseline-001.bin":
            require(
                assembly.parse_original(actual.read_bytes())["comparison"]
                == assembly.parse_original(expected.read_bytes())["comparison"],
                "original control workspace differs",
            )
        elif name == "assembly-baseline-001.bin":
            require(
                assembly.parse_workspace(actual.read_bytes())["comparison"]
                == assembly.parse_workspace(expected.read_bytes())["comparison"],
                "variant control workspace differs",
            )
        else:
            require(
                actual.read_bytes() == expected.read_bytes(),
                "control static/precision identity differs",
            )
    baseline = assembly.parse_original((work / "baseline-001.bin").read_bytes())
    require(
        struct.pack("<160d", *baseline["F"])
        == (
            Path(root) / "inputs" / (spec["case"] + "-expected-control.bin")
        ).read_bytes(),
        "D-019 original F control differs",
    )
    with assembly.Evaluations(work / "assembly-evaluations.bin") as evaluations:
        require(evaluations.count == 1, "control physical-call count differs")
        check, _, _ = assembly._workspace_check(
            work, "assembly-baseline-001.bin", "baseline-001.bin", static, evaluations
        )
    return {"arithmetic": check}


def derivative_check(work, static, counts, requests):
    same_branch, hashes = assembly._check_streams(work, static, counts, requests)
    require(counts["jacobian"] == 1, "diagnostic must use exactly one full Jacobian")
    matrix = list(assembly._rows(work / "jacobian-factor-1.bin", N * N))
    statuses = list(assembly._rows(work / "matrix-status.bin", 5))
    require(
        len(matrix) == len(statuses) == 1 and statuses[0][:3] == (1, 1, 1),
        "incomplete diagnostic matrix",
    )
    with assembly.Evaluations(work / "assembly-evaluations.bin") as evaluations:
        check, variant, _ = assembly._workspace_check(
            work, "assembly-baseline-001.bin", "baseline-001.bin", static, evaluations
        )
        base = {
            "Y": variant["Y"],
            "F": variant["variant"],
            "conditions": variant["conditions"],
        }
        selected = list(assembly._rows(work / "fd-columns.bin", 6))
        attempts = list(assembly._rows(work / "fd-probe-attempts.bin", 12))
        fd = assembly._fd_block(
            matrix[0],
            1,
            base["conditions"],
            base["Y"],
            base["F"],
            2,
            int(statuses[0][4]),
            selected,
            attempts,
            evaluations,
            same_branch,
            static["input"]["A"],
        )
        direction = assembly._directional(
            work,
            matrix[0],
            fd["complete"],
            base,
            evaluations,
            int(statuses[0][4]) + 1,
            same_branch,
            static["input"]["A"],
            static["input"]["coordinate"],
        )
        require(
            direction["next_call"] == evaluations.count + 1,
            "undeclared diagnostic evaluations",
        )
    require(
        requests["fresh_requests"]
        == 4 + fd["probe_requests"] + direction["probe_requests"],
        "diagnostic guarded-request accounting differs",
    )
    require(
        fd["complete"] and direction["pass"], "Jacobian directional agreement fails"
    )
    return {
        "arithmetic": check,
        "finite_difference": fd,
        "directional": direction,
        "branch_workspace_hashes": hashes,
    }


def attempt_gate(root, spec, result):
    """Return a failure record; never invoke the producer to repair evidence."""
    summary = {"pass": False, "passed": False, "identity_failure": False}
    try:
        work, record, static, success, terminal = inspect_attempt(root, spec, result)
        summary.update(
            native_status=terminal[-1] if terminal else "UNAVAILABLE",
            completed=record.get("completed") is True,
        )
        if not success:
            return {
                **summary,
                "reason": "native process did not complete successfully",
                "ordinary_numerical_failure": True,
            }
        counts = read_json(work / "counters.json")
        requests = read_json(work / "assembly-counters.json")
        require(
            set(counts) == set(assembly.COUNTERS)
            and all(type(v) is int and v >= 0 for v in counts.values()),
            "counter population differs",
        )
        require(
            requests["rhs"]
            == requests["assembly_calls"]
            == counts["rhs"]
            <= requests["fresh_requests"],
            "physical/guarded call accounting differs",
        )
        require(
            all(
                counts[key] == counts["rhs"]
                for key in ("coefficient", "eos", "screening", "weak")
            ),
            "kernel call counters differ",
        )
        summary.update(counters=counts, assembly_counters=requests)
        if spec["stage"] == "control":
            require(
                counts["rhs"] == 1
                and all(
                    counts[key] == 0
                    for key in ("jacobian", "newton", "accepted", "step_attempt")
                ),
                "control scope differs",
            )
            summary.update(control_check(root, spec, work, static))
            assembly._check_streams(work, static, counts, requests)
            summary["complete_control_streams_verified"] = True
        elif spec["stage"] == "derivative":
            summary.update(derivative_check(work, static, counts, requests))
        else:
            summary["work_coverage"] = verify_work_counters(work, counts)
            data = trajectory_data(work, static["input"])
            require(
                counts["newton"]
                == data["newton_iterations"]
                == counts["jacobian"]
                == counts["lu"]
                == counts["linear_solve"],
                "trajectory Newton/J/LU accounting differs",
            )
            require(
                counts["accepted"] == len(data["times"]) - 1,
                "accepted-step accounting differs",
            )
            summary.update(
                {
                    k: v
                    for k, v in data.items()
                    if k
                    not in {
                        "times",
                        "accepted_Y",
                        "requested_time",
                        "requested_Y",
                        "accepted_rows",
                    }
                }
            )
            summary.update(
                achieved_horizon=data["times"][-1],
                requested_outputs=len(data["requested_time"]),
                output_complete=True,
            )
        summary.update({"pass": True, "passed": True})
    except (
        OSError,
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        struct.error,
        ZeroDivisionError,
        OverflowError,
    ) as exc:
        summary.update(identity_failure=True, reason=str(exc))
    return summary


def load_run(root, case, suffix):
    root = Path(root)
    name = case + "-" + suffix
    prepared, campaign = (
        read_json(root / "prepared.json"),
        read_json(root / "campaign.json"),
    )
    spec = next(s for s in prepared["attempts"] if s["name"] == name)
    record = next(s for s in campaign["attempts"] if s["name"] == name)
    gate = record.get("science_gate", {})
    require(
        record.get("qualification_pass") is True and gate.get("pass") is True,
        "required trajectory did not pass: " + name,
    )
    _, _, _, success, _ = inspect_attempt(root, spec, record)
    require(success, "required trajectory native success changed")
    work = root / "attempts" / name
    data = parse_input((work / "input.bin").read_bytes())
    return trajectory_data(work, data, validate=False), data


def pilot_gate(root):
    output = {"pass": False, "passed": False, "identity_failure": False, "cases": {}}
    try:
        for case in ("development", "validation"):
            standard, data = load_run(root, case, "L0-standard")
            tight, _ = load_run(root, case, "L0-tight")
            difference = compare_values(
                standard["requested_Y"], tight["requested_Y"], data["A"]
            )
            difference["pass"] = difference["linf"] <= 1e-9 and difference["l1"] <= 1e-8
            output["cases"][case] = difference
        output["pass"] = all(c["pass"] for c in output["cases"].values())
        output["passed"] = output["pass"]
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        output["reason"] = str(exc)
    return output


def trajectory_gate(root):
    output = {"pass": False, "passed": False, "identity_failure": False, "cases": {}}
    try:
        require(pilot_gate(root)["pass"], "joint L0 pilot failed")
        for case in ("development", "validation"):
            runs = [load_run(root, case, f"L{i}-standard") for i in range(4)]
            a = runs[0][1]["A"]
            comparisons = [
                compare_values(x[0]["requested_Y"], y[0]["requested_Y"], a)
                for x, y in zip(runs, runs[1:])
            ]
            active = [
                strict_refinement(x[0]["times"], y[0]["times"])
                for x, y in zip(runs, runs[1:])
            ]
            contraction = all(
                previous[norm] <= 1e-10 or following[norm] <= 0.75 * previous[norm]
                for previous, following in zip(comparisons, comparisons[1:])
                for norm in ("linf", "l1")
            )
            tight, _ = load_run(root, case, "L3-tight")
            nonlinear = compare_values(
                runs[-1][0]["requested_Y"], tight["requested_Y"], a
            )
            passed = (
                all(active)
                and contraction
                and comparisons[-1]["linf"] <= 1e-6
                and comparisons[-1]["l1"] <= 1e-5
                and nonlinear["linf"] <= 1e-9
                and nonlinear["l1"] <= 1e-8
            )
            output["cases"][case] = {
                "pass": passed,
                "refinement": comparisons,
                "active_refinement": active,
                "contraction": contraction,
                "finest_nonlinear": nonlinear,
            }
        output["pass"] = all(c["pass"] for c in output["cases"].values())
        output["passed"] = output["pass"]
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        output["reason"] = str(exc)
    return output


def derivative_gate(root):
    prepared = read_json(Path(root) / "prepared.json")
    campaign = read_json(Path(root) / "campaign.json")
    records = {r["name"]: r for r in campaign["attempts"]}
    specs = [s for s in prepared["attempts"] if s["stage"] == "derivative"]
    passed = len(specs) == 6 and all(
        records.get(s["name"], {}).get("qualification_pass") is True for s in specs
    )
    return {
        "pass": passed,
        "passed": passed,
        "identity_failure": False,
        "required_states": 6,
    }


def evaluate_stage(root, stage, *, prepared=None):
    if stage == "L0-tight":
        return pilot_gate(root)
    if stage == "L3-tight":
        return trajectory_gate(root)
    if stage == "derivative":
        return derivative_gate(root)
    prepared = read_json(Path(root) / "prepared.json") if prepared is None else prepared
    campaign = read_json(Path(root) / "campaign.json")
    records = {r["name"]: r for r in campaign["attempts"]}
    specs = [s for s in prepared["attempts"] if s["stage"] == stage]
    passed = len(specs) == 2 and all(
        records.get(s["name"], {}).get("qualification_pass") is True for s in specs
    )
    return {"pass": passed, "passed": passed, "identity_failure": False}
