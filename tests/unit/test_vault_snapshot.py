"""Tests for ``services/vault/snapshot.py``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphdebug.services.vault.snapshot import capture_knowledge_snapshot


def test_capture_knowledge_snapshot_writes_manifest(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "index.md").write_text("# i\n", encoding="utf-8")
    (vault / "nested").mkdir()
    (vault / "nested" / "x.md").write_text("# x\n", encoding="utf-8")
    (vault / ".obsidian").mkdir()
    (vault / ".obsidian" / "ignored.md").write_text("no", encoding="utf-8")

    results = tmp_path / "results"
    dest = capture_knowledge_snapshot(vault, results)

    assert dest.is_dir()
    assert (dest / "index.md").read_text(encoding="utf-8") == "# i\n"
    assert (dest / "nested" / "x.md").is_file()
    assert not (dest / ".obsidian").exists()

    manifest = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    assert "captured_at_utc" in manifest
    assert "index.md" in manifest["files"]


def test_capture_snapshot_overwrites(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "hot.md").write_text("v1", encoding="utf-8")
    results = tmp_path / "results"
    capture_knowledge_snapshot(vault, results)
    (vault / "hot.md").write_text("v2", encoding="utf-8")
    capture_knowledge_snapshot(vault, results)
    snap = results / "knowledge_snapshots" / "before" / "hot.md"
    assert snap.read_text(encoding="utf-8") == "v2"


def test_capture_raises_when_vault_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        capture_knowledge_snapshot(tmp_path / "nope", tmp_path / "results")
