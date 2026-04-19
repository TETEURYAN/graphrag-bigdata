"""Upload, download e listagem em buckets MinIO."""

from __future__ import annotations

import logging
from pathlib import Path

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


def ensure_bucket(client: Minio, bucket: str) -> None:
    if client.bucket_exists(bucket):
        return
    client.make_bucket(bucket)
    logger.info("Bucket criado: %s", bucket)


def upload_file(
    client: Minio,
    bucket: str,
    object_name: str,
    file_path: Path,
    content_type: str | None = None,
) -> None:
    client.fput_object(
        bucket,
        object_name,
        str(file_path),
        content_type=content_type or "application/octet-stream",
    )
    logger.debug("Upload %s -> %s/%s", file_path, bucket, object_name)


def list_object_names(client: Minio, bucket: str, prefix: str = "") -> list[str]:
    out: list[str] = []
    try:
        for obj in client.list_objects(bucket, prefix=prefix, recursive=True):
            if obj.object_name:
                out.append(obj.object_name)
    except S3Error as e:
        logger.error("Erro ao listar %s: %s", bucket, e)
        raise
    return sorted(out)


def download_prefix_to_dir(
    client: Minio,
    bucket: str,
    prefix: str,
    dest_dir: Path,
) -> int:
    """Baixa todos os objetos com prefixo para dest_dir, preservando nomes relativos ao prefixo."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for obj in client.list_objects(bucket, prefix=prefix, recursive=True):
        if not obj.object_name or obj.object_name.endswith("/"):
            continue
        rel = obj.object_name[len(prefix) :].lstrip("/") if prefix else obj.object_name
        if not rel:
            rel = Path(obj.object_name).name
        local_path = dest_dir / rel
        local_path.parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(bucket, obj.object_name, str(local_path))
        count += 1
        logger.debug("Download %s/%s -> %s", bucket, obj.object_name, local_path)
    return count


def upload_dir_to_bucket(
    client: Minio,
    local_dir: Path,
    bucket: str,
    key_prefix: str = "",
) -> int:
    """Envia todos os arquivos sob local_dir para bucket com prefixo opcional."""
    count = 0
    key_prefix = key_prefix.strip("/")
    for path in local_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(local_dir).as_posix()
        object_name = f"{key_prefix}/{rel}" if key_prefix else rel
        upload_file(client, bucket, object_name, path)
        count += 1
    return count
