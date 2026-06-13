"""Serializable task value types and dict/dataclass bridges (FR-A4)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from graphdebug.services.agents.state_typed import PatchTD, SuspectNodeTD


@dataclass(frozen=True, slots=True)
class BugTask:
    """Subject repo + failing tests + observed symptom (FR-A4)."""

    target_root: str
    failing_tests: tuple[str, ...]
    symptom: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_root": self.target_root,
            "failing_tests": list(self.failing_tests),
            "symptom": self.symptom,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> BugTask:
        ft = data.get("failing_tests") or ()
        return BugTask(
            target_root=str(data["target_root"]),
            failing_tests=tuple(str(x) for x in ft),
            symptom=str(data.get("symptom", "")),
        )


@dataclass(frozen=True, slots=True)
class SuspectNode:
    node_id: str
    score: float
    why: str
    betweenness: float
    test_proximity: float


@dataclass(frozen=True, slots=True)
class Patch:
    unified_diff: str
    rationale: str


@dataclass(frozen=True, slots=True)
class StepRecord:
    role: str
    action: str
    detail: str


def suspect_to_td(s: SuspectNode) -> SuspectNodeTD:
    return SuspectNodeTD(
        node_id=s.node_id,
        score=s.score,
        why=s.why,
        betweenness=s.betweenness,
        test_proximity=s.test_proximity,
    )


def suspect_from_td(row: SuspectNodeTD) -> SuspectNode:
    return SuspectNode(
        node_id=row["node_id"],
        score=float(row["score"]),
        why=str(row["why"]),
        betweenness=float(row["betweenness"]),
        test_proximity=float(row["test_proximity"]),
    )


def patch_to_td(p: Patch) -> PatchTD:
    return PatchTD(unified_diff=p.unified_diff, rationale=p.rationale)


def patch_from_td(row: PatchTD | None) -> Patch | None:
    if not row:
        return None
    return Patch(
        unified_diff=str(row.get("unified_diff", "")),
        rationale=str(row.get("rationale", "")),
    )


__all__ = [
    "BugTask",
    "Patch",
    "StepRecord",
    "SuspectNode",
    "patch_from_td",
    "patch_to_td",
    "suspect_from_td",
    "suspect_to_td",
]
