"""Nomes dos buckets MinIO (via variáveis de ambiente)."""

from __future__ import annotations

import os

BUCKET_RAW = os.environ.get("MINIO_BUCKET_RAW", "raw-documents")
BUCKET_PROCESSED = os.environ.get("MINIO_BUCKET_PROCESSED", "processed-chunks")
BUCKET_ARTIFACTS = os.environ.get("MINIO_BUCKET_ARTIFACTS", "graph-artifacts")
