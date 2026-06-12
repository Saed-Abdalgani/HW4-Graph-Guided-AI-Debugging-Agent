"""Seeded suspect, finding, and stub navigation markdown pages."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from ._graph_pages import wikilink
from ._paths import FINDINGS_DIR, SUSPECTS_DIR


def write_suspect_pages(vault_root: Path, _focus: Sequence[str]) -> tuple[Path, ...]:
    suspects = vault_root / SUSPECTS_DIR
    suspects.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# Suspect — FileWriter & encoding",
            "",
            "> Ranked hypothesis area for PySnooper bug 1 (UTF-8 / Windows console encoding).",
            "",
            "## Why",
            "",
            "- Red baseline shows `UnicodeEncodeError` when logging non-ASCII values.",
            "- Graph hub around file writing / trace output.",
            "",
            "## Graph anchors",
            "",
            f"- {wikilink('pysnooper_tracer_filewriter')}",
            f"- {wikilink('pysnooper_tracer_filewriter_write')}",
            f"- {wikilink('tests_test_chinese_test_chinese')}",
            "",
            "## Status",
            "",
            "Open — confirm with Phase 6 investigation.",
            "",
        ]
    )
    path = suspects / "FileWriter encoding.md"
    path.write_text(body, encoding="utf-8")
    return (path,)


def write_finding_pages(vault_root: Path) -> tuple[Path, ...]:
    findings = vault_root / FINDINGS_DIR
    findings.mkdir(parents=True, exist_ok=True)
    body = "\n".join(
        [
            "# Finding — UTF-8 log path",
            "",
            "> Seeded *finding* page (Phase 3). Refine after Phase 6 root-cause lock.",
            "",
            "## Summary",
            "",
            (
                "Failure occurs when trace output hits a non-UTF-8 text encoding "
                "(e.g. Windows cp1252)."
            ),
            "",
            "## Evidence links",
            "",
            "- [[hot]]",
            "- Structured metadata: repo file `reports/bug_analysis.md` (outside this vault).",
            f"- {wikilink('pysnooper_tracer_filewriter_write')}",
            "",
            "## Related",
            "",
            "- [[suspects/FileWriter encoding|Suspect — FileWriter & encoding]]",
            "",
        ]
    )
    path = findings / "UTF-8 log path.md"
    path.write_text(body, encoding="utf-8")
    return (path,)


def write_stub_nav_pages(vault_root: Path) -> tuple[Path, ...]:
    arch = vault_root / "Architecture.md"
    arch.write_text(
        "\n".join(
            [
                "# Architecture",
                "",
                "> **Stub (Phase 3)** — block diagram from graph clusters lands in Phase 4.",
                "",
                "Until then, use the persisted Graphify narrative:",
                "",
                "- [[GRAPH_REPORT]]",
                "- Open `artifacts/graphify/graph.html` from the repo (outside Obsidian).",
                "",
                "## Navigation",
                "",
                "- [[index]]",
                "- [[hot]]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    god = vault_root / "God nodes.md"
    god.write_text(
        "\n".join(
            [
                "# God nodes",
                "",
                (
                    "> **Stub (Phase 3)** — quantitative god-node report is Phase 4 "
                    "(`reports/god_nodes.md`)."
                ),
                "",
                "Graphify's qualitative hub list is summarized in:",
                "",
                "- [[GRAPH_REPORT]] (see *God Nodes* section)",
                "",
                "Prominent code hubs from the investigation seed set:",
                "",
                f"- {wikilink('pysnooper_tracer_filewriter')}",
                f"- {wikilink('tests_test_chinese_test_chinese')}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return (arch, god)
