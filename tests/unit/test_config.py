"""Tests for ``shared.config`` loading and validation."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from graphdebug.shared.config import ConfigError, load_config

_MINIMAL_YAML = textwrap.dedent(
    """
    llm:
      provider: openai
      model: gpt-4o-mini
      temperature: 0.0
      max_output_tokens: 4096
    gatekeeper:
      requests_per_minute: 1
      tokens_per_minute: 1000
      max_retries: 1
      backoff_base_seconds: 0.1
      max_backoff_seconds: 1.0
      queue_size: 1
    budgets:
      naive:
        max_tokens: 1
        max_tool_calls: 1
        max_files: 1
        max_iterations: 1
      graph:
        max_tokens: 1
        max_tool_calls: 1
        max_files: 1
        max_iterations: 1
    paths:
      graphify_artifacts: g
      obsidian_vault: o
      results: r
      data_root: d
      reports: rep
    retriever:
      max_lines_per_file: 50
      max_suspects_fetched: 2
    features:
      hitl_required: false
      enable_langsmith: false
    """
).strip()


def test_load_repo_default_config_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from graphdebug.shared import config as config_module

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    root = config_module._project_root()
    cfg = load_config(project_root=root, require_api_key=True)
    assert cfg.budgets["graph"].max_files == 30
    assert cfg.retriever.max_lines_per_file == 120
    assert cfg.openai_api_key == "sk-test"


def _write_config(root: Path, name: str, content: str) -> None:
    cfg_dir = root / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / name).write_text(content, encoding="utf-8")


def test_missing_config_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(project_root=tmp_path, require_api_key=False)


def test_missing_yaml_section_raises(tmp_path: Path) -> None:
    bad = _MINIMAL_YAML.replace("features:", "not_features:")
    _write_config(tmp_path, "default.yaml", bad)
    with pytest.raises(ConfigError, match="Missing required keys"):
        load_config(project_root=tmp_path, require_api_key=False)


def test_missing_budget_profile_raises(tmp_path: Path) -> None:
    doc = yaml.safe_load(_MINIMAL_YAML)
    del doc["budgets"]["graph"]
    _write_config(tmp_path, "default.yaml", yaml.dump(doc))
    with pytest.raises(ConfigError, match="Missing required keys"):
        load_config(project_root=tmp_path, require_api_key=False)


def test_missing_api_key_raises(tmp_path: Path) -> None:
    _write_config(tmp_path, "default.yaml", _MINIMAL_YAML)
    with pytest.raises(ConfigError, match="Missing API key"):
        load_config(project_root=tmp_path, require_api_key=True)


def test_local_yaml_invalid_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _write_config(tmp_path, "default.yaml", _MINIMAL_YAML)
    _write_config(tmp_path, "local.yaml", "[]\n")
    with pytest.raises(ConfigError, match="local.yaml"):
        load_config(project_root=tmp_path)


def test_local_yaml_overlay_merges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    _write_config(tmp_path, "default.yaml", _MINIMAL_YAML)
    overlay = "llm:\n  model: gpt-4o\n"
    _write_config(tmp_path, "local.yaml", overlay)
    cfg = load_config(project_root=tmp_path)
    assert cfg.llm["model"] == "gpt-4o"
