"""Low-level Graphify schema validation helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class GraphLoadError(ValueError):
    """Raised when a Graphify artifact is missing or malformed."""


def sequence(data: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise GraphLoadError(f"Graph artifact key '{key}' must be a list.")
    return value


def text(raw: Mapping[str, Any], keys: tuple[str, ...], *, where: str) -> str:
    for key in keys:
        value = raw.get(key)
        if value is not None and str(value).strip():
            return str(value)
    raise GraphLoadError(f"Missing required id endpoint {keys!r} in {where}.")


def optional_text(raw: Mapping[str, Any], key: str) -> str | None:
    value = raw.get(key)
    return str(value) if value is not None else None


def optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
