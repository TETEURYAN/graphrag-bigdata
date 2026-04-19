"""Extração de texto de PDF e TXT."""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        doc = fitz.open(file_path)
        try:
            parts: list[str] = []
            for page in doc:
                parts.append(page.get_text())
            return "\n".join(parts)
        finally:
            doc.close()
    raise ValueError(f"Formato não suportado para extração: {suffix}")
