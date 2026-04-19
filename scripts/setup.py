#!/usr/bin/env python3
"""Cria buckets MinIO e valida conectividade (opcionalmente vLLM)."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app_env  # noqa: F401, E402
from inference.client import health_check_vllm  # noqa: E402
from storage.buckets import BUCKET_ARTIFACTS, BUCKET_PROCESSED, BUCKET_RAW  # noqa: E402
from storage.client import get_minio_client  # noqa: E402
from storage.operations import ensure_bucket  # noqa: E402


def main() -> int:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    parser = argparse.ArgumentParser(description="Buckets MinIO e checagens de ambiente.")
    parser.add_argument("--skip-vllm", action="store_true", help="Não testar endpoints OpenAI do vLLM.")
    args = parser.parse_args()

    client = get_minio_client()
    for name in (BUCKET_RAW, BUCKET_PROCESSED, BUCKET_ARTIFACTS):
        ensure_bucket(client, name)
        print(f"Bucket OK: {name}")

    if not args.skip_vllm:
        llm_ok = health_check_vllm("llm")
        emb_ok = health_check_vllm("embedding")
        print(f"vLLM (geração): {'OK' if llm_ok else 'indisponível'}")
        print(f"vLLM (embeddings): {'OK' if emb_ok else 'indisponível'}")
        if not llm_ok or not emb_ok:
            print(
                "(Suba os servidores conforme config/vllm/serving_args.yaml e .env; use --skip-vllm para ignorar.)",
                file=sys.stderr,
            )

    print("Setup concluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
