#!/usr/bin/env bash
# Inicia o servidor vLLM de geração (LLM) na porta 8000 por padrão.
# Para embeddings em paralelo, suba outro processo (ex.: porta 8001) — ver config/vllm/serving_args.yaml
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL="${VLLM_LLM_MODEL:-Qwen/Qwen2.5-7B-Instruct}"
PORT="${VLLM_LLM_PORT:-8000}"
TP="${VLLM_TENSOR_PARALLEL:-1}"
MAX_LEN="${VLLM_MAX_MODEL_LEN:-8192}"

if ! command -v vllm >/dev/null 2>&1; then
  echo "vllm não está no PATH. Instale no ambiente (ex.: pip install vllm) ou ative o venv." >&2
  exit 1
fi

echo "ROOT=$ROOT"
echo "Servindo modelo de geração: $MODEL na porta $PORT"
exec vllm serve "$MODEL" \
  --port "$PORT" \
  --tensor-parallel-size "$TP" \
  --max-model-len "$MAX_LEN" \
  --enable-prefix-caching
