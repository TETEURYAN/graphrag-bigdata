"""
Ponte MinIO ↔ disco local.

O GraphRAG 3.x usa armazenamento `file` ou Azure Blob; não há backend S3 nativo.
Estes helpers espelham `processed-chunks` e `graph-artifacts` no MinIO conforme AGENTS.md.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from minio import Minio

from storage.buckets import BUCKET_ARTIFACTS, BUCKET_PROCESSED
from storage.operations import download_prefix_to_dir, upload_dir_to_bucket

logger = logging.getLogger(__name__)

PROCESSED_PREFIX = os.environ.get("MINIO_PROCESSED_PREFIX", "processed/")
ARTIFACTS_PREFIX = os.environ.get("MINIO_ARTIFACTS_PREFIX", "artifacts/")


def pull_processed_from_minio(
    client: Minio,
    graphrag_input: Path,
) -> int:
    """
    Baixa objetos do prefixo processed/ para o diretório de entrada do GraphRAG
    (útil para recuperar cópias só existentes no MinIO).
    """
    graphrag_input.mkdir(parents=True, exist_ok=True)
    n = download_prefix_to_dir(client, BUCKET_PROCESSED, PROCESSED_PREFIX, graphrag_input)
    logger.info("Objetos processados baixados do MinIO: %s", n)
    return n


def push_artifacts_to_minio(client: Minio, output_dir: Path, prefix: str | None = None) -> int:
    """Envia o conteúdo de output_dir (artefatos GraphRAG) para o bucket de artefatos."""
    prefix = prefix or ARTIFACTS_PREFIX
    if not output_dir.is_dir():
        logger.warning("Diretório de saída inexistente, nada a enviar: %s", output_dir)
        return 0
    n = upload_dir_to_bucket(client, output_dir, BUCKET_ARTIFACTS, prefix)
    logger.info("Artefatos enviados ao MinIO (%s): %s arquivos", BUCKET_ARTIFACTS, n)
    return n
