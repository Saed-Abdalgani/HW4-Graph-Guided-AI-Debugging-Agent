"""Map a git-style diff onto graph nodes and refresh ``hot.md`` (FR-E2, T9.2)."""

from __future__ import annotations

import re
from pathlib import Path

from graphdebug.services.graphify.models import CodeGraph
from graphdebug.services.graphify.query import neighbors
from graphdebug.services.vault.hot import update_hot

_DIFF_PATH = re.compile(r"^\+\+\+ [ab]/(.+)$")


def paths_from_diff(diff_text: str) -> tuple[str, ...]:
    """Collect touched file paths from a unified diff."""
    out: list[str] = []
    for line in diff_text.splitlines():
        m = _DIFF_PATH.match(line.strip())
        if m:
            p = m.group(1).strip()
            if p != "/dev/null" and p not in out:
                out.append(p)
    return tuple(out)


def node_ids_for_paths(graph: CodeGraph, rel_paths: tuple[str, ...]) -> tuple[str, ...]:
    """Match graph nodes whose ``source_file`` aligns with a diff path."""
    found: list[str] = []
    for rel in rel_paths:
        r = rel.replace("\\", "/").lower()
        for nid, node in graph.nodes.items():
            sf = (node.source_file or "").replace("\\", "/").lower()
            if sf and (sf == r or sf.endswith("/" + r) or r.endswith(sf)):
                found.append(nid)
    return tuple(dict.fromkeys(found))


def merge_git_diff_into_hot(
    hot_path: Path,
    diff_text: str,
    graph: CodeGraph,
    *,
    max_neighbor_lines: int = 32,
) -> str:
    """Update *hot* ``suspects`` / ``next_action`` from diff paths + 1-hop graph context."""
    paths = paths_from_diff(diff_text)
    seeds = set(node_ids_for_paths(graph, paths))
    hdr = [
        "_Auto-filled from git diff + graph (Phase 9)._",
        "",
        f"**Touched paths** ({len(paths)}): " + ", ".join(f"`{p}`" for p in paths[:8]),
    ]
    if len(paths) > 8:
        hdr.append("_(more paths omitted)_")
    hdr.extend(["", f"**Mapped nodes** ({len(seeds)}): " + ", ".join(sorted(seeds)[:12])])
    if len(seeds) > 12:
        hdr.append("_(more nodes omitted)_")
    hdr.append("")
    hdr.append("**Neighbors (1 hop):**")
    n = 0
    for nid in sorted(seeds):
        for direction in ("in", "out"):
            for nb in neighbors(graph, nid, direction=direction):  # type: ignore[arg-type]
                hdr.append(f"- `{nid}` —{direction}→ `{nb.id}` ({nb.label})")
                n += 1
                if n >= max_neighbor_lines:
                    hdr.append("- _(truncated)_")
                    body = "\n".join(hdr)
                    return update_hot(
                        hot_path,
                        {
                            "suspects": body,
                            "next_action": "Validate diff→node mapping; narrow with investigator.",
                        },
                    )
    if n == 0 and not seeds:
        hdr.append("- _(no graph nodes matched diff paths)_")
    body = "\n".join(hdr)
    return update_hot(
        hot_path,
        {
            "suspects": body,
            "next_action": "Validate diff→node mapping; narrow with investigator.",
        },
    )


__all__ = ["merge_git_diff_into_hot", "node_ids_for_paths", "paths_from_diff"]
