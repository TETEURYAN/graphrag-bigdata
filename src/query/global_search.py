"""Busca global GraphRAG (síntese)."""

from __future__ import annotations

from pathlib import Path

from query.runner import run_graphrag_query


def run_global_search(
    query: str,
    graphrag_root: Path,
    *,
    data_dir: Path | None = None,
    verbose: bool = False,
) -> int:
    return run_graphrag_query(query, "global", graphrag_root, data_dir=data_dir, verbose=verbose)
