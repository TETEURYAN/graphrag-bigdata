#!/usr/bin/env python3
"""Ingere documentos de data/input/ para MinIO e gera .txt para o GraphRAG."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app_env  # noqa: F401, E402
from app_env import local_input_dir  # noqa: E402
from ingestion.pipeline import run_ingestion  # noqa: E402
from storage.client import get_minio_client  # noqa: E402


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    client = get_minio_client()
    n, skipped = run_ingestion(client, local_input_dir())
    print(f"Ingestão concluída: {n} arquivo(s) processado(s), {skipped} ignorado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
