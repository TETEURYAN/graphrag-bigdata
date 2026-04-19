#!/usr/bin/env python3
"""Consulta o índice GraphRAG (local, global, drift ou basic)."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app_env  # noqa: F401, E402
from app_env import graphrag_root  # noqa: E402
from query.runner import run_graphrag_query  # noqa: E402


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    parser = argparse.ArgumentParser(description="GraphRAG query")
    parser.add_argument(
        "--mode",
        choices=("local", "global", "drift", "basic"),
        default="global",
        help="Algoritmo de busca (default: global).",
    )
    parser.add_argument("--query", "-q", required=True, help="Pergunta em linguagem natural.")
    parser.add_argument(
        "--data",
        "-d",
        type=Path,
        default=None,
        help=(
            "Pasta com o índice já gerado (parquets). "
            "Se omitido, usa output/ dentro do GRAPHRAG_ROOT (ex.: data/output)."
        ),
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    return run_graphrag_query(
        args.query,
        args.mode,
        graphrag_root(),
        data_dir=args.data,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    raise SystemExit(main())
