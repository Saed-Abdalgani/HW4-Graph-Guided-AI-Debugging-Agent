"""Shared parsing of pytest ``-q`` style output."""

from __future__ import annotations


def failed_nodeids_from_pytest_text(blob: str) -> set[str]:
    """Collect ``FAILED path::test`` node ids from pytest stdout/stderr."""
    failed: set[str] = set()
    for line in blob.splitlines():
        if line.startswith("FAILED "):
            parts = line.split()
            if len(parts) >= 2:
                failed.add(parts[1].strip())
    return failed


__all__ = ["failed_nodeids_from_pytest_text"]
