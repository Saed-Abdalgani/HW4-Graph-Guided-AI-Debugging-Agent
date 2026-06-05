"""Smoke tests for SDK surface and version metadata."""

from importlib.metadata import PackageNotFoundError

import pytest

from graphdebug import __version__
from graphdebug.sdk.api import get_version, load_config


def test_get_version_matches_package() -> None:
    assert get_version() == __version__
    assert len(__version__) > 0


def test_sdk_reexports_load_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    cfg = load_config(require_api_key=True)
    assert "naive" in cfg.budgets


def test_stub_service_packages_importable() -> None:
    import importlib

    modules = (
        "graphdebug.services.agents",
        "graphdebug.services.agents.workers",
        "graphdebug.services.analysis",
        "graphdebug.services.experiment",
        "graphdebug.services.graphify",
        "graphdebug.services.ledger",
        "graphdebug.services.vault",
    )
    for name in modules:
        importlib.import_module(name)


def test_get_version_fallback_when_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    import graphdebug.shared.version as version_module

    def _raise(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(version_module, "pkg_version", _raise)
    assert version_module.get_version() == "0.0.0"


def test_gatekeeper_module_importable() -> None:
    import importlib

    importlib.import_module("graphdebug.shared.gatekeeper")
