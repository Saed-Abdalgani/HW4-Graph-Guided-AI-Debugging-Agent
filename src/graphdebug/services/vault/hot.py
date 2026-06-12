"""Parse and update ``hot.md`` section bodies (FR-O2)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

# Order preserved when rendering a full document from scratch.
HOT_SECTION_KEYS: tuple[str, ...] = (
    "symptom",
    "suspects",
    "checked",
    "root_cause",
    "fix",
    "next_action",
)

HOT_SECTION_TITLES: dict[str, str] = {
    "symptom": "Symptom",
    "suspects": "Suspects (ranked)",
    "checked": "Checked",
    "root_cause": "Root cause",
    "fix": "Fix",
    "next_action": "Next action",
}

_TITLE_TO_KEY = {v.lower(): k for k, v in HOT_SECTION_TITLES.items()}

_SECTION_HEADER_RE = re.compile(
    r"^(?P<hash>#{1,6})\s+(?P<title>.+?)\s*$",
    re.MULTILINE,
)


def parse_hot(markdown: str) -> dict[str, str]:
    """Split *hot* markdown into section bodies keyed by stable ids."""
    sections: dict[str, str] = {k: "" for k in HOT_SECTION_KEYS}
    matches = list(_SECTION_HEADER_RE.finditer(markdown))
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        key = _TITLE_TO_KEY.get(title.lower())
        if key is None:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip("\n")
        sections[key] = body.strip()
    return sections


def render_hot(sections: Mapping[str, str]) -> str:
    """Build *hot* markdown from section bodies (titles fixed)."""
    parts: list[str] = ["# hot — active investigation", ""]
    parts.append(
        "> Short, high-signal working notes. Update every iteration (per `todo.md` **T3.2**)."
    )
    parts.append("")
    for key in HOT_SECTION_KEYS:
        title = HOT_SECTION_TITLES[key]
        body = (sections.get(key) or "").strip()
        parts.append(f"## {title}")
        parts.append("")
        if body:
            parts.append(body)
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def update_hot(path: Path, updates: Mapping[str, str]) -> str:
    """Merge *updates* into ``hot.md`` and write *path*. Returns final text."""
    current = path.read_text(encoding="utf-8") if path.is_file() else render_hot({})
    merged = parse_hot(current)
    for key, value in updates.items():
        if key not in HOT_SECTION_TITLES:
            raise ValueError(f"Unknown hot section key: {key!r}")
        merged[key] = value.strip()
    text = render_hot(merged)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text
