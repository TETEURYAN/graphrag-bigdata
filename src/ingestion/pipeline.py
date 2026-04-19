"""Orquestra upload MinIO + extração para arquivos em data/input."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from minio import Minio

from ingestion.extractor import extract_text
from storage.buckets import BUCKET_PROCESSED, BUCKET_RAW
from storage.operations import upload_file

logger = logging.getLogger(__name__)

RAW_PREFIX = os.environ.get("MINIO_RAW_PREFIX", "raw/")
PROCESSED_PREFIX = os.environ.get("MINIO_PROCESSED_PREFIX", "processed/")

_SUPPORTED = {".pdf", ".txt"}


def run_ingestion(
    client: Minio,
    input_dir: Path,
) -> tuple[int, int]:
    """
    Para cada PDF/TXT em input_dir: envia bruto ao bucket raw, extrai texto,
    grava .txt no mesmo diretório e envia cópia ao bucket processed.
    Retorna (arquivos processados, erros ignorados).
    """
    input_dir.mkdir(parents=True, exist_ok=True)
    processed = 0
    skipped = 0

    for path in sorted(input_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in _SUPPORTED:
            logger.info("Ignorado (extensão): %s", path.name)
            skipped += 1
            continue

        raw_key = f"{RAW_PREFIX.rstrip('/')}/{path.name}"
        upload_file(client, BUCKET_RAW, raw_key, path)

        try:
            text = extract_text(path)
        except Exception as e:
            logger.exception("Falha ao extrair %s: %s", path, e)
            skipped += 1
            continue

        out_txt = path.with_suffix(".txt")
        if path.suffix.lower() == ".pdf":
            out_txt.write_text(text, encoding="utf-8")
            proc_key = f"{PROCESSED_PREFIX.rstrip('/')}/{path.stem}.txt"
        else:
            if out_txt.resolve() != path.resolve():
                out_txt.write_text(text, encoding="utf-8")
            proc_key = f"{PROCESSED_PREFIX.rstrip('/')}/{path.name}"

        upload_file(
            client,
            BUCKET_PROCESSED,
            proc_key,
            out_txt,
            content_type="text/plain; charset=utf-8",
        )
        processed += 1
        logger.info("Ingerido: %s -> MinIO raw + processed", path.name)

    return processed, skipped
