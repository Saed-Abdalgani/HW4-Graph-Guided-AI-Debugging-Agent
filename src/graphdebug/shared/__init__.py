"""Shared utilities: configuration, gatekeeper, version."""

from graphdebug.shared.config import AppConfig, ConfigError, load_config
from graphdebug.shared.version import __version__, get_version

__all__ = ["AppConfig", "ConfigError", "__version__", "get_version", "load_config"]
