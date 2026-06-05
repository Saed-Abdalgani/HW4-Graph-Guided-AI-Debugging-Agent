"""graphdebug package root."""

from graphdebug.constants import PACKAGE_NAME
from graphdebug.shared.version import __version__, get_version

__all__ = ["PACKAGE_NAME", "__version__", "get_version"]
