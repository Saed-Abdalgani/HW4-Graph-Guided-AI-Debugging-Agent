"""Phase 9 extensions (FR-E*, RQ8)."""

from graphdebug.services.extensions.arch_ego import architecture_ego_report
from graphdebug.services.extensions.doc_signals import DocSignal, doc_graph_signals
from graphdebug.services.extensions.hot_diff import (
    merge_git_diff_into_hot,
    node_ids_for_paths,
    paths_from_diff,
)
from graphdebug.services.extensions.impact import impact_of

__all__ = [
    "DocSignal",
    "architecture_ego_report",
    "doc_graph_signals",
    "impact_of",
    "merge_git_diff_into_hot",
    "node_ids_for_paths",
    "paths_from_diff",
]
