"""Tests for ``services/vault/hot.py``."""

from __future__ import annotations

from pathlib import Path

import pytest

from graphdebug.services.vault.hot import (
    HOT_SECTION_KEYS,
    parse_hot,
    render_hot,
    update_hot,
)


def test_parse_render_roundtrip() -> None:
    sections = {k: f"body-{k}" for k in HOT_SECTION_KEYS}
    text = render_hot(sections)
    again = parse_hot(text)
    for key in HOT_SECTION_KEYS:
        assert again[key] == f"body-{key}"


def test_update_hot_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "hot.md"
    update_hot(path, {"symptom": "Same text.\n", "fix": "TBD."})
    first = path.read_text(encoding="utf-8")
    update_hot(path, {"symptom": "Same text.\n", "fix": "TBD."})
    assert path.read_text(encoding="utf-8") == first


def test_update_hot_merges_partial(tmp_path: Path) -> None:
    path = tmp_path / "hot.md"
    update_hot(path, {"symptom": "A", "fix": "B"})
    update_hot(path, {"root_cause": "C"})
    merged = parse_hot(path.read_text(encoding="utf-8"))
    assert merged["symptom"] == "A"
    assert merged["fix"] == "B"
    assert merged["root_cause"] == "C"


def test_update_hot_unknown_key(tmp_path: Path) -> None:
    path = tmp_path / "hot.md"
    with pytest.raises(ValueError, match="Unknown hot section"):
        update_hot(path, {"not_a_section": "x"})


def test_sdk_update_hot_delegates(tmp_path: Path) -> None:
    from graphdebug.sdk.api import update_hot as sdk_update_hot

    path = tmp_path / "hot.md"
    sdk_update_hot(path, {"symptom": "from sdk"})
    assert "from sdk" in path.read_text(encoding="utf-8")


def test_parse_hot_ignores_unknown_sections() -> None:
    md = "\n".join(
        [
            "# hot — active investigation",
            "",
            "## Random",
            "",
            "ignore me",
            "",
            "## Symptom",
            "",
            "only this",
            "",
        ]
    )
    parsed = parse_hot(md)
    assert parsed["symptom"] == "only this"
    assert parsed["suspects"] == ""
