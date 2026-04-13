
<h1 align="center">Arquitetura de GraphRAG e vLLM — Bi Data</h1>

<p align="center">
  <img src="https://user-images.githubusercontent.com/91018438/204195385-acc6fcd4-05a7-4f25-87d1-cb7d5cc5c852.png" alt="logo" width="220" />
</p>
> Pipeline local para indexação e consulta baseada em grafos usando MinIO, GraphRAG e vLLM.

**Grupo:** Matheus Ryan | Rafael Santana

---

## Sumário

- **Arquitetura**
- **Principais funcionalidades**
- **Como executar (rápido)**
- **Estrutura do projeto**

---

## Arquitetura

O projeto implementa um pipeline de recuperação e síntese de conhecimento baseado em grafos. Resumidamente:

- **MinIO** — object storage S3‑compatible para documentos brutos, chunks processados e artefatos do grafo.
- **GraphRAG** — indexação, extração de entidades e construção do knowledge graph a partir dos chunks.
- **vLLM** — servidor OpenAI‑compatible utilizado para geração e embeddings (duas instâncias recomendadas).
- **CLI / Scripts** — orquestram ingestão, pré‑processamento, indexação e consultas via terminal.

Fluxo principal:

1. Usuário adiciona documentos em `data/input/`.
2. Script de ingestão processa e envia objetos para MinIO (`raw-documents`).
3. Pré-processamento gera `processed-chunks` prontos para indexação.
4. GraphRAG consome os chunks, chama vLLM para embeddings e constrói as tabelas/parquets de entidades, relações e comunidades.
5. Consultas são respondidas por GraphRAG com suporte a geração via vLLM.

---

## Principais funcionalidades

- Editor/gestão de base de conhecimento (regras e fatos) — estrutura para representar conhecimento.
- Motor de inferência com suporte a encadeamento:
	- Encadeamento para Trás (Backward Chaining)
	- Encadeamento para Frente (Forward Chaining)
	- Encadeamento Misto
- Explicações do raciocínio (`Como?` / `Por quê?`) para inspecionar decisões do sistema.
- Pipeline reproducível para ingestão → pré‑processamento → indexação → consulta.
- Integração OpenAI‑compatible com o vLLM (geração + embeddings).

---

## Como executar (resumo rápido)

1. Copie `.env.example` para `.env` e preencha as variáveis (MinIO, vLLM, buckets):

```bash
cp .env.example .env
# editar .env com seu editor preferido
```

2. Inicie o MinIO localmente (exemplo):

```bash
minio server ./minio-data --console-address ":9001"
```

3. Inicie o(s) servidor(es) vLLM (exemplos recomendados):

```bash
# Geração (porta 8000)
bash scripts/start_vllm.sh

# (ou) exemplo direto:
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000 --tensor-parallel-size 1 --max-model-len 8192 --enable-prefix-caching

# Embeddings (porta 8001)
vllm serve BAAI/bge-m3 --port 8001 --task embedding --max-model-len 8192
```

4. Crie buckets MinIO e valide a configuração (uma vez):

```bash
python scripts/setup.py
```

5. Adicione documentos em `data/input/` e execute a ingestão:

```bash
# copiar documentos para data/input/
python scripts/ingest.py
```

6. Execute a indexação completa com GraphRAG:

```bash
python scripts/index.py
```

7. Faça consultas ao grafo (modo local ou global):

```bash
python scripts/query.py --mode local --query "Quais são as principais entidades?"
python scripts/query.py --mode global --query "Qual é o tema central dos documentos?"
```

---

## Estrutura do projeto (visão rápida)

Principais diretórios:

- `config/` — configurações do GraphRAG e vLLM.
- `data/` — `input/` e `output/` (artefatos, cache).
- `src/storage/` — abstração MinIO.
- `src/ingestion/` — extração e pipeline de ingestão.
- `src/indexing/` — integração com GraphRAG.
- `src/inference/` — cliente OpenAI‑compatible para vLLM.
- `scripts/` — scripts executáveis (`setup.py`, `ingest.py`, `index.py`, `query.py`, `start_vllm.sh`).

---

## Contribuição

Siga o padrão de commits Conventional Commits e o formato de PR definido em `AGENTS.md`.

Título de PR sugerido: `DAT-01: Descrição curta` (ex.: `DAT-01: Adiciona template de Pull Request`)

---

## Licença

Ver [LICENSE](LICENSE) para informações sobre a licença do projeto.

