#!/usr/bin/env python3
"""Check D-027 navigation and evidence preservation; requires retained Git history.

Run from the repository root: python -B scripts/check_documentation.py.
This reads public Markdown/Git objects only and executes no scientific producer.
"""

import hashlib
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

SOURCE = "d7e60485b81f6afdc1817c86189acc40f97df7ae"
MOVES = {
    "docs/DESIGN.md": "docs/science/DESIGN.md",
    "docs/VALIDATION.md": "docs/science/VALIDATION.md",
    "docs/EVIDENCE.md": "docs/science/EVIDENCE.md",
    "docs/phase1/NATIVE_BENCHMARK.md": "docs/science/benchmark/NATIVE_RHS.md",
    "docs/phase1/PARTITIONS.md": "docs/science/benchmark/PARTITIONS.md",
    "docs/phase1/S02_READER.md": "docs/science/data/XNET_READER.md",
    "docs/phase1/PRIMARY_RHS_DATASET.md": "docs/science/data/PRIMARY_RHS_DATASET.md",
    "docs/phase1/RHS_DATASET.md": "docs/science/data/PILOT_RHS_DATASET.md",
    "docs/phase1/ERROR_BUDGETS.md": "docs/science/validation/PHYSICAL_ERROR_BUDGETS.md",
    "docs/WORKFLOW.md": "docs/process/WORKFLOW.md",
    "docs/AGENT_BRIEFS.md": "docs/process/AGENT_BRIEFS.md",
    "docs/MEETING_REPORT_TEMPLATE.md": "docs/process/MEETING_REPORT_TEMPLATE.md",
}
CURRENT = {
    "docs/DECISIONS.md",
    "docs/ROADMAP.md",
    "docs/BACKLOG.md",
    "docs/PROGRESS.md",
    "docs/HANDOFF.md",
    "docs/PHASE_2_LAUNCH.md",
}
LINK = re.compile(r"(?<=\]\()([^\s)]+)")


def git(*args):
    return subprocess.check_output(["git", *args])


def original(path):
    return git("show", f"{SOURCE}:{path}").decode()


def prose(text):
    """Ignore fenced examples when inspecting rendered Markdown navigation."""
    fence = None
    for line in text.splitlines():
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            token = m[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield line


def headings(text):
    counts = {}
    result = []
    for line in prose(text):
        m = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if not m:
            continue
        title = m[1]
        raw = re.sub(r"<[^>]+>", "", title).lower()
        slug = "".join(
            c for c in raw if c in "-_ " or unicodedata.category(c)[0] not in "PS"
        )
        slug = slug.replace(" ", "-")
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        candidate = slug if not suffix else f"{slug}-{suffix}"
        # Reserve generated suffixes too (GitHub duplicate heading behavior).
        while candidate in {a for _, a in result}:
            suffix += 1
            counts[slug] = suffix + 1
            candidate = f"{slug}-{suffix}"
        result.append((title, candidate))
    return result


def anchors(text):
    return [a for _, a in headings(text)] + re.findall(
        r'<a\s+(?:id|name)=["\']([^"\']+)["\']', "\n".join(prose(text))
    )


def destination(path, link):
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or link.startswith("/"):
        return None
    target = (
        os.path.normpath(str(Path(path).parent / unquote(parsed.path)))
        if parsed.path
        else path
    )
    return target, unquote(parsed.fragment)


def relink(text, old, new):
    def replace(m):
        link = m[1]
        dest = destination(old, link)
        if dest is None:
            # Update only mutable main-branch links; immutable GitHub refs stay intact.
            prefix = "https://github.com/jaharris87/crucible-astro/blob/main/"
            if link.startswith(prefix):
                path, sep, fragment = link[len(prefix) :].partition("#")
                return prefix + MOVES.get(path, path) + (sep + fragment if sep else "")
            return link
        path, fragment = dest
        path = MOVES.get(path, path)
        if not urlsplit(link).path and old == new:
            return link
        relative = os.path.relpath(path, Path(new).parent)
        return relative + ("#" + fragment if fragment else "")

    return LINK.sub(replace, text)


def migrated(text, old, new):
    text = relink(text, old, new)
    if old == "docs/AGENT_BRIEFS.md":
        text = text.replace(
            "Model-policy reference: WORKFLOW.md#",
            "Model-policy reference: docs/process/WORKFLOW.md#",
        )
        text = text.replace(
            "Model policy: WORKFLOW.md#", "Model policy: docs/process/WORKFLOW.md#"
        )
    return text


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    """Verify the accepted migration against its immutable pre-move Git tree."""
    errors = []
    tracked = git("ls-tree", "-r", "--name-only", SOURCE).decode().splitlines()
    frozen = [
        p
        for p in tracked
        if p.startswith("docs/") and p not in MOVES and p not in CURRENT
    ]
    for path in frozen:
        if not Path(path).is_file() or Path(path).read_bytes() != git(
            "show", f"{SOURCE}:{path}"
        ):
            errors.append(f"Frozen evidence changed or missing: {path}")
    total_anchors = 0
    inbound = 0
    for old, new in MOVES.items():
        source = original(old)
        if Path(new).read_text() != migrated(source, old, new):
            errors.append(f"Moved guide differs beyond navigation substitutions: {new}")
        if headings(Path(new).read_text()) != headings(source):
            errors.append(f"Heading identity/order changed: {new}")
        expected = anchors(source)
        total_anchors += len(expected)
        stub = Path(old).read_text()
        relative = os.path.relpath(new, Path(old).parent)
        for fragment in expected:
            if (
                f'<a id="{fragment}"></a>' not in stub
                or f"]({relative}#{fragment})" not in stub
            ):
                errors.append(f"Missing compatibility forwarding: {old}#{fragment}")
    for path, digest in [
        (
            "52e3895e3d1a6d991a0f91b66a18a90ddf10c502:docs/phase1/PRIMARY_RHS_DATASET.md",
            "cbb4f8fcfaab9caa211c15c15fec15c5f3acd9c855515e7750c96b4267f465c0",
        ),
        (
            "c36d1d3d6698dd216c234f3158b20750487ca6a5:docs/phase1/NATIVE_BENCHMARK.md",
            "839a0ad408406f2547586be4bd23921f29ee13edaa4dd8ebe42ceb2ff65d45c3",
        ),
    ]:
        if sha(git("show", path)) != digest:
            errors.append(f"Accepted bound source not recoverable: {path}")
    checked = 0
    markdown = [p for p in tracked if p.endswith(".md")]
    markdown += list(MOVES.values()) + ["docs/process/DOCUMENTATION_MIGRATION.md"]
    for path in markdown:
        text = "\n".join(prose(Path(path).read_text()))
        for link in LINK.findall(text):
            dest = destination(path, link)
            if dest is None:
                continue
            target, fragment = dest
            checked += 1
            if not Path(target).exists():
                errors.append(f"Missing link target: {path} -> {link}")
            elif (
                fragment
                and target.endswith(".md")
                and fragment not in anchors(Path(target).read_text())
            ):
                errors.append(f"Missing fragment: {path} -> {link}")
    # This includes historical inbound links: they must land on working compatibility anchors.
    for path in tracked:
        if path.endswith(".md"):
            for link in LINK.findall(original(path)):
                dest = destination(path, link)
                if dest and dest[0] in MOVES:
                    inbound += 1
    print(
        f"Source {SOURCE}: {len(MOVES)} exact guide moves, {total_anchors} compatibility anchors, "
        f"{inbound} original Markdown inbound links; {len(frozen)} frozen files, "
        f"{sum(p.startswith('docs/data-cards/') for p in frozen)} cards; {checked} local links/fragments."
    )
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        "PASS: navigation, body/heading preservation, frozen bytes and accepted Git source recovery."
    )


if __name__ == "__main__":
    main()
