"""Load ``config/*.yaml`` with optional ``.env`` overlay. All tunables live here — not in code."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

REQUIRED_YAML_SECTIONS = ("llm", "gatekeeper", "budgets", "paths", "features", "retriever")
REQUIRED_BUDGET_PROFILES = ("naive", "graph")


class ConfigError(ValueError):
    """Raised when configuration files or environment are invalid or incomplete."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(val, dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def _require_keys(obj: Mapping[str, Any], keys: tuple[str, ...], *, where: str) -> None:
    missing = [k for k in keys if k not in obj]
    if missing:
        raise ConfigError(f"Missing required keys in {where}: {', '.join(missing)}")


@dataclass(frozen=True, slots=True)
class BudgetProfile:
    max_tokens: int
    max_tool_calls: int
    max_files: int
    max_iterations: int


@dataclass(frozen=True, slots=True)
class RetrieverConfig:
    max_lines_per_file: int
    max_suspects_fetched: int


@dataclass(frozen=True, slots=True)
class AppConfig:
    raw: dict[str, Any]
    project_root: Path
    llm: dict[str, Any]
    gatekeeper: dict[str, Any]
    budgets: dict[str, BudgetProfile]
    paths: dict[str, Path]
    features: dict[str, Any]
    retriever: RetrieverConfig
    openai_api_key: str | None


def load_config(
    *,
    project_root: Path | None = None,
    config_filename: str = "default.yaml",
    env_file: str | None = ".env",
    require_api_key: bool = True,
) -> AppConfig:
    """Load merged YAML from ``config/<config_filename>`` and optional ``.env``."""
    root = project_root or _project_root()
    load_dotenv(root / env_file) if env_file else None

    main_path = root / "config" / config_filename
    if not main_path.is_file():
        raise ConfigError(f"Configuration file not found: {main_path}")

    with main_path.open(encoding="utf-8") as fh:
        data: dict[str, Any] = yaml.safe_load(fh) or {}

    local_path = root / "config" / "local.yaml"
    if local_path.is_file():
        with local_path.open(encoding="utf-8") as fh:
            local = yaml.safe_load(fh)
        if local is None:
            local = {}
        if not isinstance(local, dict):
            raise ConfigError("config/local.yaml must be a mapping at the top level.")
        data = _deep_merge(data, local)

    _require_keys(data, REQUIRED_YAML_SECTIONS, where=str(main_path))

    budgets_raw = data["budgets"]
    _require_keys(budgets_raw, REQUIRED_BUDGET_PROFILES, where="budgets")
    budgets: dict[str, BudgetProfile] = {}
    for profile in REQUIRED_BUDGET_PROFILES:
        b = budgets_raw[profile]
        _require_keys(
            b,
            ("max_tokens", "max_tool_calls", "max_files", "max_iterations"),
            where=f"budgets.{profile}",
        )
        budgets[profile] = BudgetProfile(
            max_tokens=int(b["max_tokens"]),
            max_tool_calls=int(b["max_tool_calls"]),
            max_files=int(b["max_files"]),
            max_iterations=int(b["max_iterations"]),
        )

    paths_raw = data["paths"]
    _require_keys(
        paths_raw,
        ("graphify_artifacts", "obsidian_vault", "results", "data_root", "reports"),
        where="paths",
    )
    paths = {k: (root / str(v)).resolve() for k, v in paths_raw.items()}

    retriever_raw = data["retriever"]
    _require_keys(
        retriever_raw,
        ("max_lines_per_file", "max_suspects_fetched"),
        where="retriever",
    )
    retriever = RetrieverConfig(
        max_lines_per_file=int(retriever_raw["max_lines_per_file"]),
        max_suspects_fetched=int(retriever_raw["max_suspects_fetched"]),
    )

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GRAPHDEBUG_OPENAI_API_KEY")
    if require_api_key and not (api_key and api_key.strip()):
        raise ConfigError(
            "Missing API key: set OPENAI_API_KEY or GRAPHDEBUG_OPENAI_API_KEY "
            "in the environment or .env file."
        )

    return AppConfig(
        raw=data,
        project_root=root,
        llm=dict(data["llm"]),
        gatekeeper=dict(data["gatekeeper"]),
        budgets=budgets,
        paths=paths,
        features=dict(data["features"]),
        retriever=retriever,
        openai_api_key=api_key.strip() if api_key else None,
    )
