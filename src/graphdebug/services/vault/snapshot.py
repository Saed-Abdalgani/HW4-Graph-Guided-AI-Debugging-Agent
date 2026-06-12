"""Capture a *before* knowledge snapshot of the vault (FR-O4)."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_SNAPSHOT_SUBDIR = "knowledge_snapshots/before"


def capture_knowledge_snapshot(
    vault_root: Path,
    results_root: Path,
    *,
    subdir: str = DEFAULT_SNAPSHOT_SUBDIR,
) -> Path:
    """
    Copy markdown vault content into ``results_root / subdir``.

    Overwrites the same destination on each call so the snapshot stays a stable
    *before-fix* anchor until Phase 7.
    """
    dest = (results_root / subdir).resolve()
    if dest.is_dir():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "captured_at_utc": datetime.now(tz=UTC).isoformat(),
        "vault_root": str(vault_root.resolve()),
        "files": [],
    }

    if not vault_root.is_dir():
        raise FileNotFoundError(f"Vault directory not found: {vault_root}")

    for path in sorted(vault_root.rglob("*.md")):
        rel = path.relative_to(vault_root)
        if rel.parts and rel.parts[0] == ".obsidian":
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        manifest["files"].append(str(rel).replace("\\", "/"))

    manifest_path = dest / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dest
