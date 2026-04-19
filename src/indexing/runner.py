"""Executa `graphrag index` como subprocesso."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from graphrag_cli import graphrag_executable

logger = logging.getLogger(__name__)


def run_graphrag_index(
    graphrag_root: Path,
    *,
    verbose: bool = False,
    dry_run: bool = False,
) -> int:
    graphrag_root = graphrag_root.resolve()
    cmd = [
        graphrag_executable(),
        "index",
        "--root",
        str(graphrag_root),
    ]
    if verbose:
        cmd.append("--verbose")
    if dry_run:
        cmd.append("--dry-run")

    logger.info("Executando: %s", " ".join(cmd))
    env = os.environ.copy()
    proc = subprocess.run(cmd, cwd=str(graphrag_root), env=env)
    return proc.returncode
