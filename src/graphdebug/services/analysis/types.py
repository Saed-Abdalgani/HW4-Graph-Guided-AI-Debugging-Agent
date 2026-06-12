"""Typed results for centrality and Phase 4 exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CentralityRow:
    node_id: str
    label: str
    degree_in: int
    degree_out: int
    betweenness: float
    closeness: float


@dataclass(frozen=True, slots=True)
class GodNode:
    node_id: str
    label: str
    betweenness: float
    degree_total: int
    rationale: str


@dataclass(frozen=True, slots=True)
class Phase4ExportResult:
    god_nodes_report: Path
    obsidian_god_nodes: Path
    architecture_png: Path
    architecture_mmd: Path
    oop_png: Path
    oop_mmd: Path
    architecture_report: Path
