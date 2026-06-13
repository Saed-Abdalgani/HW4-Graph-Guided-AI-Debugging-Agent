"""YAML merge + key checks for ``config.load_config`` (keeps ``config.py`` small)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


def project_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(val, dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def require_keys(
    obj: Mapping[str, Any],
    keys: tuple[str, ...],
    *,
    where: str,
    exc_cls: type[Exception],
) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise exc_cls(f"Missing required keys in {where}: {', '.join(missing)}")


__all__ = ["deep_merge", "project_root_from_here", "require_keys"]
