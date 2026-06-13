"""Shared argparse fragments for bug-task CLIs (investigate, experiment)."""

from __future__ import annotations

import argparse
from pathlib import Path


def add_bug_task_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--target-root",
        type=Path,
        required=True,
        help="Path to the buggy project root (subject under data/).",
    )
    parser.add_argument(
        "--test",
        action="append",
        dest="tests",
        metavar="NODEID",
        required=True,
        help="Pytest node id (repeatable), e.g. tests/test_x.py::test_one.",
    )
    parser.add_argument(
        "--symptom",
        default="(see baseline logs)",
        help="Short symptom text for prompts.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="graphdebug repo root (default: cwd).",
    )
    parser.add_argument(
        "--assume-hitl-ack",
        action="store_true",
        help="Ack the HITL interrupt automatically (non-interactive; use with care).",
    )


__all__ = ["add_bug_task_arguments"]
