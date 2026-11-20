"""Finite D-021 candidate partitions; mechanical success never qualifies data.

Explicit JSON/NPZ inputs only. Importing this module reads no data. See
``docs/phase1/PARTITIONS.md`` for the accepted rule and independent final gate.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

NAMESPACE = "Chimera/D9.6-SN160-3D/canonical-zero-based-global-particle-ID"
TAG = "phase1-primary-expanded-operational-allocation-v1"
ROLES = ("train", "validation", "test")
UNITS = {
    "Y": "molar_abundance_Y",
    "temperature": "GK",
    "density": "g/cm^3",
    "time": "s",
}


class PartitionError(ValueError):
    """A mechanical or scientific gate failure with an actionable reason."""

    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")


def _require(condition, code, detail):
    if not condition:
        raise PartitionError(code, detail)


def digest(value):
    """SHA256 of compact sorted-key UTF-8 JSON, rejecting nonfinite numbers."""
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


def _identities(values, label):
    _require(
        isinstance(values, list) and values and all(_text(v) for v in values),
        "identity",
        f"{label}: nonempty identity list required",
    )
    _require(
        len(set(values)) == len(values), "identity", f"{label}: duplicate identity"
    )


def pool_digest(pool):
    """Order-independent binding; only histories/records are unordered collections."""
    return digest(
        {
            **pool,
            "histories": sorted(pool["histories"], key=lambda h: h["particle0"]),
            "records": sorted(pool["records"], key=lambda r: r["record_id"]),
        }
    )


def measured_components(particles, spherical):
    """Nearest undirected closure from measured (frame,history,r/theta/phi).

    Radius is positive cm, angles radians. The metric is median Cartesian
    separation/(r_i+r_j) over every supplied frame; exact ties use numeric IDs.
    No physical cutoff, interpolation, extrapolation or independence is implied.
    """
    import numpy as np

    _require(
        len(particles) >= 2
        and all(type(p) is int and p >= 0 for p in particles)
        and len(set(particles)) == len(particles),
        "position_identity",
        "at least two distinct nonnegative canonical integer IDs required",
    )
    positions = np.asarray(spherical)
    _require(
        positions.ndim == 3
        and positions.shape[0] > 0
        and positions.shape[1:] == (len(particles), 3)
        and positions.dtype.kind == "f"
        and np.isfinite(positions).all(),
        "position_shape",
        "expected finite floating (frames,histories,3) measured positions",
    )
    order = sorted(range(len(particles)), key=particles.__getitem__)
    ids = [particles[i] for i in order]
    r, theta, phi = np.moveaxis(positions[:, order, :], -1, 0)
    _require(
        bool((r > 0).all()), "position_radius", "all measured radii must be positive"
    )
    cart = np.stack(
        (
            r * np.sin(theta) * np.cos(phi),
            r * np.sin(theta) * np.sin(phi),
            r * np.cos(theta),
        ),
        axis=-1,
    )
    distances = np.full((len(ids), len(ids)), np.inf)
    for i in range(len(ids)):
        for j in range(i):
            values = np.linalg.norm(cart[:, i, :] - cart[:, j, :], axis=1) / (
                r[:, i] + r[:, j]
            )
            distances[i, j] = distances[j, i] = np.median(values)
    _require(
        bool(np.isfinite(distances[~np.eye(len(ids), dtype=bool)]).all()),
        "position_metric",
        "nonfinite measured separation; no fallback allowed",
    )
    adjacent = {p: set() for p in ids}
    for i, p in enumerate(ids):
        q = ids[int(np.argmin(distances[i]))]  # columns already canonical: exact ties
        adjacent[p].add(q)
        adjacent[q].add(p)
    groups, remaining = [], set(ids)
    while remaining:
        pending, component = [min(remaining)], set()
        while pending:
            p = pending.pop()
            if p not in component:
                component.add(p)
                pending.extend(adjacent[p] - component)
        remaining -= component
        groups.append(sorted(component))
    return sorted(groups)


def _validated(pool, contract, groups):
    meta = pool["metadata"]
    _require(
        meta == contract["metadata"], "metadata", "pool differs from accepted metadata"
    )
    _require(
        meta.get("namespace") == NAMESPACE and meta.get("protocol_tag") == TAG,
        "metadata",
        "namespace/protocol tag differ from the D-021 rule",
    )
    for key in ("pool_id", "parent_id", "working_scope_acceptance"):
        _require(_text(meta.get(key)), "metadata", f"missing {key}")
    _require(meta.get("units") == UNITS, "units", f"expected {UNITS}")
    for key in ("reference_config_sha256", "species_payload_sha256"):
        _require(_hash(meta.get(key)), "metadata", f"missing/invalid {key}")
    species = meta.get("species")
    _require(
        isinstance(species, list) and species, "species", "ordered species required"
    )
    _identities([s.get("id") for s in species], "ordered species")
    _require(
        meta.get("n_species") == len(species)
        and all(type(s.get("A")) is int and s["A"] > 0 for s in species)
        and all(type(s.get("Z")) is int and 0 <= s["Z"] <= s["A"] for s in species),
        "species",
        "species count or A/Z invalid",
    )
    window = meta.get("measured_time_window_s")
    _require(
        isinstance(window, list)
        and len(window) == 2
        and all(type(x) in (int, float) and math.isfinite(x) for x in window)
        and window[0] < window[1],
        "metadata",
        "explicit finite measured time window required",
    )
    histories = {}
    for h in pool["histories"]:
        p = h["particle0"]
        _require(
            type(p) is int and p >= 0 and p not in histories, "identity", "particle0"
        )
        _require(h.get("parent_id") == meta["parent_id"], "parent", f"history {p}")
        _require(type(h.get("stored_row")) is int, "identity", f"stored row: {p}")
        _require(_text(h.get("category")), "category", f"unknown category: {p}")
        _identities(h.get("raw_ancestors"), f"history {p} raw ancestors")
        _require(
            all(_hash(a) for a in h["raw_ancestors"]), "ancestry", f"raw SHA256: {p}"
        )
        histories[p] = h
    _require(histories, "empty_pool", "no histories")
    _require(
        isinstance(pool.get("source_exclusions"), list)
        and all(
            _text(e.get("source")) and _text(e.get("reason"))
            for e in pool["source_exclusions"]
        ),
        "exclusions",
        "explicit source exclusion inventory required",
    )
    _require(
        all(
            isinstance(g, list) and all(type(p) is int and p >= 0 for p in g)
            for g in groups
        ),
        "group_membership",
        "groups require canonical integer particle IDs",
    )
    normalized = sorted(sorted(g) for g in groups)
    members = [p for g in normalized for p in g]
    _require(
        all(g for g in normalized)
        and len(members) == len(set(members))
        and set(members) == set(histories),
        "group_membership",
        "groups must allocate each known history exactly once",
    )
    group_of = {p: i for i, g in enumerate(normalized) for p in g}
    for p, h in histories.items():
        _require(
            isinstance(h.get("known_related"), list), "ancestry", f"related IDs: {p}"
        )
        for q in h["known_related"]:
            _require(q in histories, "unknown_parent", f"related history {q}")
            _require(group_of[p] == group_of[q], "related_crossover", f"{p} and {q}")
    records, canonical = {}, set()
    species_sha256 = digest(species)
    for r in pool["records"]:
        rid, p, ordinal = r["record_id"], r["particle0"], r["ordinal"]
        _require(_text(rid) and rid not in records, "identity", f"record {rid}")
        _require(
            type(p) is int and p in histories,
            "unknown_parent",
            f"record {rid}: particle0 {p}",
        )
        _require(r.get("parent_id") == meta["parent_id"], "parent", f"record {rid}")
        _require(type(ordinal) is int and ordinal >= 0, "identity", f"ordinal: {rid}")
        identity = (p, ordinal)
        _require(
            identity not in canonical, "duplicate_record", f"canonical state: {rid}"
        )
        canonical.add(identity)
        _require(
            r.get("n_species") == len(species)
            and r.get("species_sha256") == species_sha256,
            "species",
            f"record {rid}: ordered species/count differ",
        )
        _require(
            type(r.get("candidate")) is bool
            and isinstance(r.get("exclusion_reasons"), list)
            and (r["candidate"] == (not r["exclusion_reasons"])),
            "exclusions",
            f"record {rid}: candidate/exclusion reasons inconsistent",
        )
        _require(
            all(_text(v) for v in r["exclusion_reasons"]), "exclusions", f"record {rid}"
        )
        for f in ("temperature", "density", "source_formula_Ye", "time"):
            _require(
                type(r.get(f)) in (int, float) and math.isfinite(r[f]),
                "conditions",
                f"record {rid}: finite {f} required",
            )
        _require(
            r["temperature"] > 0 and r["density"] > 0,
            "conditions",
            f"record {rid}: positive T9/rho required",
        )
        _require(_hash(r.get("input_sha256")), "identity", f"input fingerprint: {rid}")
        _require(isinstance(r.get("derived_from"), list), "ancestry", f"record {rid}")
        _require(isinstance(r.get("raw_ancestors"), list), "ancestry", f"record {rid}")
        _require(all(_hash(a) for a in r["raw_ancestors"]), "ancestry", f"record {rid}")
        records[rid] = r
    _require(records, "empty_pool", "no records")
    _require(
        {r["particle0"] for r in records.values()} == set(histories),
        "incomplete_allocation",
        "histories without records",
    )
    for rid, r in records.items():
        for source in r["derived_from"]:
            _require(
                source in records, "unknown_parent", f"{rid} derived from {source}"
            )
            _require(
                source != rid
                and group_of[r["particle0"]] == group_of[records[source]["particle0"]],
                "derived_crossover",
                f"{rid} derived from {source}: ancestry must stay in one group",
            )
    pending = {rid: len(set(r["derived_from"])) for rid, r in records.items()}
    children = {rid: [] for rid in records}
    for rid, r in records.items():
        for source in set(r["derived_from"]):
            children[source].append(rid)
    ready = [rid for rid, n in pending.items() if n == 0]
    visited = 0
    while ready:
        visited += 1
        for child in children[ready.pop()]:
            pending[child] -= 1
            if pending[child] == 0:
                ready.append(child)
    _require(
        visited == len(records), "ancestry_cycle", "derived ancestry contains a cycle"
    )
    counts = {
        "histories": len(histories),
        "ordinary_records": len(records),
        "candidate_records": sum(r["candidate"] for r in records.values()),
        "excluded_records": sum(not r["candidate"] for r in records.values()),
        "groups": len(normalized),
    }
    _require(counts == contract["counts"], "count", f"observed {counts}")
    _require(
        pool_digest(pool) == contract["pool_sha256"],
        "pool_binding",
        "pool content changed",
    )
    return histories, records, normalized, group_of


def construct_candidate(pool, contract, groups):
    """Recompute anchors/quotas and reject any change from the accepted oracle.

    ``contract`` binds metadata, canonical pool hash/counts, exact groups and
    roles. It is an explicit acceptance input, never inferred from observed data.
    """
    histories, records, groups, group_of = _validated(pool, contract, groups)
    candidates = [r for r in records.values() if r["candidate"]]
    _require(candidates, "empty_candidates", "no source-grid candidates")
    ranks = [digest([NAMESPACE, g, TAG]) for g in groups]
    anchors = set()
    for field in ("temperature", "density", "source_formula_Ye"):
        for direction in (min, max):
            extreme = direction(r[field] for r in candidates)
            r = min(
                (r for r in candidates if r[field] == extreme),
                key=lambda r: (r["particle0"], r["ordinal"]),
            )
            anchors.add(group_of[r["particle0"]])
    strata = [
        ("stored_row", v) for v in sorted({h["stored_row"] for h in histories.values()})
    ]
    strata += [
        ("category", v) for v in sorted({h["category"] for h in histories.values()})
    ]
    for field, value in strata:
        matching = {group_of[p] for p, h in histories.items() if h[field] == value}
        if not anchors & matching:
            anchors.add(min(matching, key=lambda g: (ranks[g], groups[g])))
    roles = {g: "train" for g in anchors}
    for category in sorted({h["category"] for h in histories.values()}):
        category_groups = []
        for g, members in enumerate(groups):
            categories = {histories[p]["category"] for p in members}
            _require(len(categories) == 1, "category", f"mixed categories in group {g}")
            if category in categories:
                category_groups.append(g)
        q = max(1, 15 * len(category_groups) // 100)
        available = sorted(
            set(category_groups) - anchors, key=lambda g: (ranks[g], groups[g])
        )
        _require(
            len(available) >= 2 * q, "quota", f"{category}: insufficient nonanchors"
        )
        for i, g in enumerate(available):
            roles[g] = "validation" if i < q else "test" if i < 2 * q else "train"
    assigned = [{"members": g, "role": roles[i]} for i, g in enumerate(groups)]
    _require(
        assigned == contract["accepted_groups"],
        "accepted_assignment",
        "computed groups/roles differ from accepted oracle; no fallback or retuning",
    )
    ancestry_owner, fingerprint_owner = {}, {}
    for p, h in histories.items():
        g = group_of[p]
        for ancestor in h["raw_ancestors"]:
            owner = ancestry_owner.setdefault(ancestor, g)
            _require(
                owner == g,
                "raw_crossover",
                f"raw ancestor shared across groups: {ancestor}",
            )
    memberships = []
    for rid in sorted(records):
        r = records[rid]
        g, role = group_of[r["particle0"]], roles[group_of[r["particle0"]]]
        for ancestor in r["raw_ancestors"]:
            owner = ancestry_owner.setdefault(ancestor, g)
            _require(
                owner == g,
                "raw_crossover",
                f"record {rid}: raw ancestor crosses groups",
            )
        if r["candidate"]:
            owner = fingerprint_owner.setdefault(r["input_sha256"], role)
            _require(
                owner == role,
                "duplicate_input",
                f"record {rid}: exact input crosses roles",
            )
        memberships.append({**r, "group": g, "role": role})
    for role in ROLES:
        _require(
            any(r["candidate"] and r["role"] == role for r in memberships),
            "empty_role",
            f"no candidate records in {role}",
        )
    return {
        "schema_version": 1,
        "status": "CANDIDATE_MECHANICAL_PASS_PENDING_SCIENTIFIC_QUALIFICATION",
        "metadata": pool["metadata"],
        "contract_sha256": digest(contract),
        "pool_sha256": contract["pool_sha256"],
        "groups": [
            {**g, "training_anchor": i in anchors} for i, g in enumerate(assigned)
        ],
        "histories": [
            {**histories[p], "group": group_of[p], "role": roles[group_of[p]]}
            for p in sorted(histories)
        ],
        "records": memberships,
        "source_exclusions": pool["source_exclusions"],
        "counts": contract["counts"],
    }


def validate_scientific(
    candidate, membership, eligibility, acceptance, *, pool, contract, groups
):
    """Check a separately accepted, nonempty qualified membership in every role.

    First reconstruct from the explicit original bound pool/contract/groups and
    require exact canonical candidate identity. This reuses all mechanical checks
    before interpreting serialized record/group membership or receipt hashes.
    Eligibility maps every candidate ID to a bool plus a qualification-evidence
    SHA256. Membership explicitly partitions all candidate IDs into the three
    roles or reason-bearing exclusions. Receipt authenticity is a human gate;
    this checker verifies its exact content bindings, never manufactures it.
    """
    reconstructed = construct_candidate(pool, contract, groups)
    _require(
        digest(candidate) == digest(reconstructed),
        "candidate_identity",
        "serialized candidate differs from original bound mechanical construction",
    )
    records = {r["record_id"]: r for r in candidate["records"] if r["candidate"]}
    _require(records, "empty_eligible", "no candidate membership")
    _require(
        set(eligibility) == set(records),
        "eligibility_unknown",
        "complete eligibility required",
    )
    for rid, evidence in eligibility.items():
        _require(
            type(evidence.get("eligible")) is bool,
            "eligibility_unknown",
            f"record {rid}: eligibility must be explicitly true/false",
        )
    _require(
        any(v["eligible"] for v in eligibility.values()),
        "empty_eligible",
        "qualification pending: zero eligible records",
    )
    _require(
        set(membership) == {*ROLES, "exclusions"},
        "scientific_membership",
        "three roles and explicit exclusions required",
    )
    allocated = []
    for role in ROLES:
        ids = membership[role]
        _identities(ids, f"scientific {role}")
        for rid in ids:
            _require(rid in records, "scientific_membership", f"unknown record {rid}")
            _require(
                records[rid]["role"] == role,
                "scientific_membership",
                f"changed role: {rid}",
            )
            _require(eligibility[rid]["eligible"], "ineligible", f"record {rid}")
            _require(
                _hash(eligibility[rid].get("qualification_sha256")),
                "qualification",
                f"record {rid}: evidence missing",
            )
        allocated.extend(ids)
    exclusions = membership["exclusions"]
    _require(
        isinstance(exclusions, dict) and all(_text(v) for v in exclusions.values()),
        "scientific_membership",
        "exclusion reasons required",
    )
    allocated.extend(exclusions)
    _require(
        len(allocated) == len(set(allocated)) and set(allocated) == set(records),
        "scientific_membership",
        "complete disjoint membership/exclusions required",
    )
    _require(
        isinstance(acceptance, dict)
        and _text(acceptance.get("human_decision"))
        and acceptance.get("candidate_sha256") == digest(candidate)
        and acceptance.get("membership_sha256") == digest(membership)
        and acceptance.get("eligibility_sha256") == digest(eligibility),
        "scientific_acceptance",
        "human task/reference/domain/metrics/tolerance acceptance with exact bindings required",
    )
    return {
        "status": "SCIENTIFIC_MEMBERSHIP_CHECK_PASS",
        "candidate_sha256": digest(candidate),
    }


def _bound_json(entry, root):
    path = Path(entry["path"])
    if not path.is_absolute():
        path = root / path
    data = path.read_bytes()
    _require(
        hashlib.sha256(data).hexdigest() == entry["sha256"], "file_binding", str(path)
    )
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    root = args.config.parent
    pool = _bound_json(config["pool"], root)
    contract = _bound_json(config["contract"], root)
    # Group construction uses retained audited spherical arrays, not raw outputs.
    import numpy as np

    positions, particles, clocks = [], [], []
    _require(
        config["positions"],
        "position_shape",
        "at least one measured position array required",
    )
    for entry in config["positions"]:
        path = Path(entry["path"])
        if not path.is_absolute():
            path = root / path
        _require(
            hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
            "file_binding",
            str(path),
        )
        with np.load(path, allow_pickle=False) as arrays:
            ids = arrays["trajectory_ids_row_zone_gpid0"]
            position = arrays["positions_r_theta_phi"]
            clock = arrays["times_by_file"]
            _require(
                ids.ndim == 2
                and ids.shape[1] == 3
                and ids.dtype.kind in "iu"
                and position.ndim == 3
                and position.shape[1] == len(ids)
                and clock.ndim == 3
                and clock.shape[0] > 0
                and clock.shape[2] == 2
                and clock.shape[1] == position.shape[0]
                and np.isfinite(clock).all()
                and bool((np.diff(clock[:, :, 0], axis=1) > 0).all()),
                "position_shape",
                "IDs/positions/clocks must have consistent measured shapes and increasing clocks",
            )
            positions.append(position)
            particles.extend(int(v) for v in ids[:, 2])
            clocks.append(clock)
    _require(
        all(np.array_equal(c, clocks[0]) for c in clocks)
        and all(
            np.array_equal(c[:, :, 0], c[0, :, 0][None, :].repeat(len(c), axis=0))
            for c in clocks
        )
        and pool["metadata"]["measured_time_window_s"]
        == [float(clocks[0][0, 0, 0]), float(clocks[0][0, -1, 0])],
        "position_clock",
        "measured clocks/window must agree exactly",
    )
    groups = measured_components(particles, np.concatenate(positions, axis=1))
    result = construct_candidate(pool, contract, groups)
    with args.output.open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "counts": result["counts"],
                "candidate_sha256": digest(result),
            }
        )
    )


if __name__ == "__main__":
    main()
