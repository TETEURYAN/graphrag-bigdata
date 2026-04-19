"""Cliente MinIO configurado a partir do ambiente."""

from __future__ import annotations

import os

from minio import Minio


def get_minio_client() -> Minio:
    endpoint = os.environ["MINIO_ENDPOINT"]
    access_key = os.environ["MINIO_ACCESS_KEY"]
    secret_key = os.environ["MINIO_SECRET_KEY"]
    secure = os.environ.get("MINIO_USE_SSL", "false").lower() in ("1", "true", "yes")
    return Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure,
    )
