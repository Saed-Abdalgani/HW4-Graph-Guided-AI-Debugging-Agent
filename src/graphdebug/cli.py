"""Thin CLI entrypoint — delegates to the SDK (G.3)."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="graphdebug",
        description="Graph-guided AI debugging agent (HW4).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=_version_string(),
    )
    parser.parse_args()


def _version_string() -> str:
    from graphdebug.sdk.api import get_version

    return get_version()


if __name__ == "__main__":
    main()  # pragma: no cover
