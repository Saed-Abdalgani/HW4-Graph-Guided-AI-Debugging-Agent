"""Apply a unified diff to a git working tree (todo T7.2)."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def _git_ok(root: Path) -> bool:
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return r.returncode == 0 and (r.stdout or "").strip() == "true"


def copy_patch_to_reports(diff_text: str, reports_dir: Path) -> Path:
    """Persist ``reports/fix.diff`` (FR-B3)."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    out = reports_dir / "fix.diff"
    out.write_text(diff_text, encoding="utf-8", newline="\n")
    return out


def apply_unified_diff_git(target_root: Path, diff_text: str) -> None:
    """``git apply`` the diff inside *target_root* (must be a git checkout)."""
    root = target_root.resolve()
    if not _git_ok(root):
        raise RuntimeError(
            f"Not a git working tree: {root}. Init or clone the subject so `git apply` works."
        )
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".diff",
        delete=False,
    ) as tmp:
        tmp.write(diff_text)
        tmp_path = Path(tmp.name)
    try:
        chk = subprocess.run(
            ["git", "apply", "--check", str(tmp_path)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if chk.returncode != 0:
            err = (chk.stderr or chk.stdout or "").strip()
            raise RuntimeError(f"git apply --check failed: {err}")
        ap = subprocess.run(
            ["git", "apply", str(tmp_path)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if ap.returncode != 0:
            err = (ap.stderr or ap.stdout or "").strip()
            raise RuntimeError(f"git apply failed: {err}")
    finally:
        tmp_path.unlink(missing_ok=True)


def apply_approved_patch_files(
    *,
    diff_path: Path,
    target_root: Path,
    reports_dir: Path,
) -> Path:
    """Copy diff to ``reports/fix.diff`` then apply via git."""
    text = diff_path.read_text(encoding="utf-8")
    saved = copy_patch_to_reports(text, reports_dir)
    apply_unified_diff_git(target_root, text)
    return saved


__all__ = [
    "apply_approved_patch_files",
    "apply_unified_diff_git",
    "copy_patch_to_reports",
]
