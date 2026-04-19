#!/usr/bin/env python3
"""Dispara a indexação GraphRAG e espelha artefatos no MinIO."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app_env  # noqa: F401, E402
from app_env import graphrag_root, local_output_dir  # noqa: E402
from indexing.minio_datasource import pull_processed_from_minio, push_artifacts_to_minio  # noqa: E402
from indexing.runner import run_graphrag_index  # noqa: E402
from storage.client import get_minio_client  # noqa: E402


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    parser = argparse.ArgumentParser(description="GraphRAG index + sincronização MinIO.")
    parser.add_argument(
        "--pull-minio",
        action="store_true",
        help="Baixa texto processado do MinIO para o diretório input do GraphRAG antes de indexar.",
    )
    parser.add_argument(
        "--no-push-minio",
        action="store_true",
        help="Não envia a pasta output/ para o bucket de artefatos após indexar.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Valida configuração sem executar o pipeline completo.")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    root = graphrag_root()
    out = local_output_dir()
    client = get_minio_client()

    if args.pull_minio:
        pull_processed_from_minio(client, root / "input")

    rc = run_graphrag_index(root, verbose=args.verbose, dry_run=args.dry_run)
    if rc != 0:
        return rc
    if args.dry_run or args.no_push_minio:
        return 0
    push_artifacts_to_minio(client, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
