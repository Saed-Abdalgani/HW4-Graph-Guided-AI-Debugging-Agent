"""Single source for the installed distribution version."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

__all__ = ["__version__", "get_version"]


def get_version() -> str:
    """Return ``graphdebug`` package version from distribution metadata."""
    try:
        return pkg_version("graphdebug")
    except PackageNotFoundError:
        return "0.0.0"


__version__: str = get_version()
