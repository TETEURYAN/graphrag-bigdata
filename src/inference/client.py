"""Cliente OpenAI-compatible para servidores vLLM."""

from __future__ import annotations

import logging
import os
from typing import Literal

from openai import OpenAI

logger = logging.getLogger(__name__)


def get_openai_client(
    *,
    role: Literal["llm", "embedding"] = "llm",
) -> OpenAI:
    """
    Retorna um cliente OpenAI apontando para o vLLM.
    Usa VLLM_LLM_BASE_URL ou VLLM_EMBEDDING_BASE_URL conforme o papel.
    Se só existir VLLM_BASE_URL, usa essa URL para ambos.
    """
    api_key = os.environ.get("VLLM_API_KEY", "token-local")
    fallback = os.environ.get("VLLM_BASE_URL")
    if role == "llm":
        base = os.environ.get("VLLM_LLM_BASE_URL") or fallback
    else:
        base = os.environ.get("VLLM_EMBEDDING_BASE_URL") or fallback
    if not base:
        raise ValueError(
            "Defina VLLM_LLM_BASE_URL / VLLM_EMBEDDING_BASE_URL (ou VLLM_BASE_URL) no ambiente.",
        )
    return OpenAI(api_key=api_key, base_url=base.rstrip("/"))


def health_check_vllm(role: Literal["llm", "embedding"] = "llm") -> bool:
    """Verifica se o endpoint responde (lista modelos)."""
    try:
        client = get_openai_client(role=role)
        client.models.list()
        return True
    except Exception as e:
        logger.warning("Health check vLLM (%s) falhou: %s", role, e)
        return False
