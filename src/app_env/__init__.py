"""Carrega .env e expõe caminhos raiz do projeto."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# src/app_env/__init__.py -> parents[1] = src, parents[2] = raiz do repositório
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env")


def project_root() -> Path:
    return _PROJECT_ROOT


def graphrag_root() -> Path:
    rel = os.environ.get("GRAPHRAG_ROOT", "data")
    return (_PROJECT_ROOT / rel).resolve()


def local_input_dir() -> Path:
    rel = os.environ.get("GRAPHRAG_INPUT_DIR", "data/input")
    return (_PROJECT_ROOT / rel).resolve()


def local_output_dir() -> Path:
    return graphrag_root() / "output"
