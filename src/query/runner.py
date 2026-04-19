"""Executa `graphrag query` como subprocesso."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from graphrag_cli import graphrag_executable

logger = logging.getLogger(__name__)


def run_graphrag_query(
    query: str,
    method: str,
    graphrag_root: Path,
    *,
    data_dir: Path | None = None,
    verbose: bool = False,
) -> int:
    graphrag_root = graphrag_root.resolve()
    exe = graphrag_executable()
    cmd = [
        exe,
        "query",
        "--root",
        str(graphrag_root),
        "--method",
        method,
    ]
    if data_dir is not None:
        cmd.extend(["--data", str(data_dir.resolve())])
    if verbose:
        cmd.append("--verbose")
    cmd.append(query)

    logger.info("Executando: %s", " ".join(cmd[:6]) + f' ... "{query[:40]}..."')
    env = os.environ.copy()
    proc = subprocess.run(cmd, cwd=str(graphrag_root), env=env)
    return proc.returncode
