"""Before/after vault snapshot diff for Phase 7 (todo T7.7)."""

from __future__ import annotations

import json
from pathlib import Path


def _load_manifest(root: Path) -> dict:
    p = root / "manifest.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def write_vault_before_after_report(
    *,
    before_dir: Path,
    after_dir: Path,
    out_path: Path,
) -> Path:
    """Markdown summary of added/removed markdown files between snapshots."""
    b = _load_manifest(before_dir)
    a = _load_manifest(after_dir)
    bf = set(b.get("files") or [])
    af = set(a.get("files") or [])
    added = sorted(af - bf)
    removed = sorted(bf - af)

    lines = [
        "# Vault knowledge — before vs after fix",
        "",
        f"- **Before**: `{before_dir}`",
        f"- **After**: `{after_dir}`",
        "",
        "## Files added",
        "",
    ]
    if added:
        lines.extend(f"- `{x}`" for x in added)
    else:
        lines.append("- _(none)_")
    lines.extend(["", "## Files removed", ""])
    if removed:
        lines.extend(f"- `{x}`" for x in removed)
    else:
        lines.append("- _(none)_")
    lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def compare_patch_text_files(ours: Path, official: Path, out: Path) -> Path:
    """Stub T7.5: record paths + sizes; human fills analysis in ``reports/``."""
    t = (
        "# Patch comparison (T7.5)\n\n"
        f"- **Ours**: `{ours}` ({ours.stat().st_size} bytes)\n"
        f"- **Official**: `{official}` ({official.stat().st_size} bytes)\n\n"
        "Fill: agreement / valid alternative / justification.\n"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t, encoding="utf-8")
    return out


__all__ = ["compare_patch_text_files", "write_vault_before_after_report"]
