"""Localiza o executável `graphrag` instalado no ambiente."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def graphrag_executable() -> str:
    w = shutil.which("graphrag")
    if w:
        return w
    sibling = Path(sys.executable).parent / ("graphrag.exe" if sys.platform == "win32" else "graphrag")
    if sibling.is_file():
        return str(sibling)
    raise FileNotFoundError(
        "Executável 'graphrag' não encontrado. Instale as dependências (uv sync) e use o venv do projeto.",
    )
