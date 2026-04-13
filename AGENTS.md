# AGENTS.md — GraphRAG Knowledge Platform

> Guia de referência para agentes de IA e desenvolvedores do projeto.  
> Stack principal: **MinIO · GraphRAG · vLLM**  
> Contexto: **Projeto acadêmico — execução local via terminal**

---

## 1. Visão Geral da Arquitetura

Este projeto implementa um pipeline de recuperação e síntese de conhecimento baseado em grafos, executado inteiramente via terminal. O fluxo principal é:

```
Dados Brutos (texto, PDFs, docs)
        │
        ▼
  ┌─────────────┐
  │    MinIO    │  ← Object Storage local (input/, processed/, artifacts/)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  GraphRAG   │  ← Indexação, extração de entidades, construção do grafo
  └──────┬──────┘
         │  usa
         ▼
  ┌─────────────┐
  │    vLLM     │  ← Servidor de inferência (embeddings + geração)
  └──────┬──────┘
         │
         ▼
  ┌──────────────────┐
  │  CLI / Terminal  │  ← Consultas e interação via linha de comando
  └──────────────────┘
```

### 1.1 Componentes

| Componente | Papel | Tecnologia |
|---|---|---|
| **Object Storage** | Armazena documentos brutos e artefatos de grafo | MinIO |
| **Graph Indexer** | Extrai entidades, relações e comunidades; constrói o knowledge graph | Microsoft GraphRAG |
| **Inference Engine** | Serve LLMs para embeddings e geração de texto | vLLM |
| **CLI** | Interface de execução do pipeline e consultas | Scripts Python |
| **Config Layer** | Centraliza configurações de modelos, paths e credenciais | YAML + `.env` |

### 1.2 Fluxo de Dados Detalhado

```
1. INGESTÃO
   Usuário coloca documentos em data/input/
   └── script de ingestão faz upload para MinIO bucket raw-documents/

2. PRÉ-PROCESSAMENTO
   Script lê de MinIO raw-documents/
   └── extrai texto (PDF, TXT)
   └── grava em MinIO processed-chunks/

3. INDEXAÇÃO (GraphRAG)
   GraphRAG lê de MinIO processed-chunks/
   └── chama vLLM para embeddings e extração de entidades
   └── constrói grafo (entidades, relações, comunidades)
   └── grava artefatos em MinIO graph-artifacts/
       ├── entities.parquet
       ├── relationships.parquet
       ├── communities.parquet
       └── community_reports.parquet

4. CONSULTA
   Usuário executa script de query no terminal
   └── GraphRAG query engine (local ou global search)
   └── GraphRAG chama vLLM para geração da resposta
   └── resposta impressa no terminal
```

---

## 2. Estrutura de Diretórios

```
project-root/
│
├── AGENTS.md                   # Este arquivo
├── README.md                   # Overview e instruções de uso
├── .env.example                # Template de variáveis de ambiente
├── .gitignore
├── pyproject.toml              # Dependências do projeto (uv ou pip)
│
├── config/                     # Configurações do projeto
│   ├── settings.yaml           # Config principal (MinIO endpoints, modelos, paths)
│   ├── graphrag/
│   │   ├── settings.yaml       # Config nativa do GraphRAG (gerada por `graphrag init`)
│   │   └── prompts/            # Prompts customizados do GraphRAG
│   │       ├── entity_extraction.txt
│   │       ├── summarize_descriptions.txt
│   │       ├── claim_extraction.txt
│   │       └── community_report.txt
│   └── vllm/
│       └── serving_args.yaml   # Args do servidor vLLM (model, porta, tensor-parallel)
│
├── data/                       # Dados locais do pipeline
│   ├── input/                  # Documentos a serem ingeridos
│   └── output/                 # Saída do GraphRAG
│       ├── artifacts/          # Parquets gerados (entidades, relações, comunidades)
│       └── cache/              # Cache de chamadas LLM (evita reprocessamento)
│
├── src/                        # Código-fonte principal
│   ├── __init__.py
│   │
│   ├── storage/                # Camada de abstração do MinIO
│   │   ├── __init__.py
│   │   ├── client.py           # Cliente MinIO configurado
│   │   ├── buckets.py          # Nomes dos buckets como constantes
│   │   └── operations.py       # Upload, download, list
│   │
│   ├── ingestion/              # Pipeline de ingestão de documentos
│   │   ├── __init__.py
│   │   ├── extractor.py        # Extração de texto (PDF, TXT)
│   │   └── pipeline.py         # Orquestra extração + upload para MinIO
│   │
│   ├── indexing/               # Integração com GraphRAG
│   │   ├── __init__.py
│   │   ├── runner.py           # Executa `graphrag index` programaticamente
│   │   └── minio_datasource.py # DataSource custom do GraphRAG para ler do MinIO
│   │
│   ├── inference/              # Integração com vLLM
│   │   ├── __init__.py
│   │   └── client.py           # Cliente OpenAI-compatible para o servidor vLLM
│   │
│   └── query/                  # Interface de consulta ao grafo
│       ├── __init__.py
│       ├── local_search.py     # GraphRAG Local Search (específico, factual)
│       └── global_search.py    # GraphRAG Global Search (síntese holística)
│
├── scripts/                    # Scripts de execução via terminal
│   ├── setup.py                # Cria buckets MinIO e valida configuração
│   ├── ingest.py               # Ingere documentos de data/input/ para MinIO
│   ├── index.py                # Dispara indexação GraphRAG completa
│   ├── query.py                # Interface de consulta interativa no terminal
│   └── start_vllm.sh           # Inicia o servidor vLLM com os args corretos
│
└── docs/                       # Documentação adicional
    ├── architecture.md         # Diagramas e decisões de arquitetura (ADRs)
    └── setup.md                # Passo a passo de configuração do ambiente
```

---

## 3. Configuração do Ambiente

### 3.1 Variáveis de Ambiente (`.env`)

Copie `.env.example` para `.env` e preencha:

```dotenv
# === MinIO ===
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_USE_SSL=false
MINIO_BUCKET_RAW=raw-documents
MINIO_BUCKET_PROCESSED=processed-chunks
MINIO_BUCKET_ARTIFACTS=graph-artifacts

# === vLLM ===
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
VLLM_EMBEDDING_MODEL=BAAI/bge-m3
VLLM_API_KEY=token-local

# === GraphRAG ===
GRAPHRAG_ROOT=./data/output
GRAPHRAG_INPUT_DIR=./data/input

# === Geral ===
LOG_LEVEL=INFO
```

### 3.2 Buckets MinIO

| Bucket | Propósito |
|---|---|
| `raw-documents` | Documentos originais enviados para o pipeline |
| `processed-chunks` | Texto extraído pronto para indexação |
| `graph-artifacts` | Parquets gerados pelo GraphRAG |

### 3.3 Execução Passo a Passo

```bash
# 1. Inicia o MinIO localmente
minio server ./minio-data --console-address ":9001"

# 2. Inicia o servidor vLLM
bash scripts/start_vllm.sh

# 3. Cria os buckets e valida a configuração (só precisa rodar uma vez)
python scripts/setup.py

# 4. Ingere documentos de data/input/
python scripts/ingest.py

# 5. Executa a indexação GraphRAG
python scripts/index.py

# 6. Consulta no terminal
python scripts/query.py --mode local  --query "Quais são as principais entidades?"
python scripts/query.py --mode global --query "Qual é o tema central dos documentos?"
```

---

## 4. Integração vLLM com GraphRAG

O GraphRAG usa por padrão a API OpenAI. O vLLM expõe uma API OpenAI-compatible, tornando a integração direta via `config/graphrag/settings.yaml`:

```yaml
# config/graphrag/settings.yaml

llm:
  api_key: ${VLLM_API_KEY}
  type: openai_chat
  model: ${VLLM_LLM_MODEL}
  api_base: ${VLLM_BASE_URL}
  max_tokens: 4096
  temperature: 0
  concurrent_requests: 4

embeddings:
  async_mode: threaded
  llm:
    api_key: ${VLLM_API_KEY}
    type: openai_embedding
    model: ${VLLM_EMBEDDING_MODEL}
    api_base: ${VLLM_BASE_URL}
    batch_size: 16

storage:
  type: blob
  connection_string: ${MINIO_CONNECTION_STRING}
  container_name: ${MINIO_BUCKET_ARTIFACTS}
```

### 4.1 Servidor vLLM — Argumentos Recomendados

Duas instâncias separadas: uma para geração, outra para embeddings.

```bash
# Instância 1: LLM de geração (porta 8000)
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --enable-prefix-caching

# Instância 2: Modelo de embeddings (porta 8001)
vllm serve BAAI/bge-m3 \
  --port 8001 \
  --task embedding \
  --max-model-len 8192
```

---

## 5. Padrão de Commits — Obrigatório

Este projeto adota **Conventional Commits** (https://www.conventionalcommits.org). Todo commit deve seguir o formato:

```
<tipo>(<escopo>): <descrição curta>

[corpo opcional — explica o "porquê"]
```

### 5.1 Tipos Permitidos

| Tipo | Quando usar |
|---|---|
| `feat` | Nova funcionalidade ou script |
| `fix` | Correção de bug |
| `docs` | Mudanças apenas em documentação |
| `style` | Formatação, sem mudança de lógica |
| `refactor` | Refatoração sem novo feature nem fix |
| `perf` | Melhoria de performance |
| `chore` | Manutenção, dependências, configuração |
| `revert` | Reverte um commit anterior |

### 5.2 Escopos Recomendados

`storage`, `ingestion`, `indexing`, `inference`, `query`, `config`, `docs`, `scripts`, `deps`

### 5.3 Exemplos

```bash
# ✅ CORRETO
feat(ingestion): add PDF text extraction via pymupdf
fix(storage): handle MinIO connection timeout with retry
docs(setup): add step-by-step vLLM installation guide
refactor(indexing): extract MinIO datasource into separate module
chore(deps): bump graphrag to 1.1.0

# ❌ ERRADO
fix bug
update stuff
WIP
ajustes
```

### 5.4 Breaking Changes

Use `!` após o tipo/escopo:

```
feat(query)!: change CLI args for query script

BREAKING CHANGE: --type flag renamed to --mode (local | global).
```

---

## 6. Boas Práticas

### 6.1 Configurações

- **Nunca hardcode** endpoints de MinIO, vLLM ou nomes de modelos no código. Use variáveis de ambiente lidas via `config/settings.yaml`.
- **Nunca commite `.env`** — está no `.gitignore`. Use `.env.example` como template versionado.
- Nomes de buckets MinIO devem ser constantes em `src/storage/buckets.py`, nunca strings literais espalhadas.

### 6.2 Modelos vLLM

- O modelo carregado **não muda em runtime**. Para trocar o modelo, pare o servidor, atualize o `.env` e reinicie com `scripts/start_vllm.sh`.
- Parâmetros de serving ficam em `config/vllm/serving_args.yaml` e no script `scripts/start_vllm.sh`. Não passe flags diretamente em código Python.

### 6.3 GraphRAG e Cache

- O cache em `data/output/cache/` evita reprocessar chamadas LLM já feitas — **não delete durante experimentos** a menos que queira forçar reindexação completa.
- Ao reindexar com configurações diferentes, limpe `data/output/artifacts/` antes de rodar `scripts/index.py` para evitar mistura de artefatos de runs distintos.

---

## 7. Decisões de Arquitetura (ADRs)

### ADR-001: vLLM como servidor de inferência

**Decisão**: Usar vLLM para servir tanto o LLM de geração quanto o modelo de embeddings.  
**Justificativa**: O vLLM expõe uma API OpenAI-compatible, encaixando diretamente na configuração padrão do GraphRAG sem adaptadores. PagedAttention garante uso eficiente de VRAM mesmo em hardware acadêmico.  
**Trade-off**: Requer GPU. Em máquinas sem GPU, usar Ollama como alternativa.

### ADR-002: MinIO como object storage

**Decisão**: Usar MinIO (S3-compatible) para armazenar todos os dados do pipeline.  
**Justificativa**: O GraphRAG suporta blob storage S3-compatible nativamente. MinIO roda localmente sem custo e usa o mesmo protocolo S3, o que permite migração futura para AWS S3 sem mudança de código.  
**Trade-off**: Adiciona um serviço extra para subir localmente. Para experimentos muito simples, o filesystem local também funcionaria, mas perderia a rastreabilidade por bucket.

### ADR-003: Interface exclusivamente via terminal

**Decisão**: Não há API REST, UI web ou serviço de background. Todo o pipeline é acionado via scripts Python no terminal.  
**Justificativa**: O objetivo é acadêmico — reprodutibilidade e clareza do pipeline importam mais que usabilidade. Scripts explícitos tornam cada etapa do fluxo auditável e fácil de depurar.  
**Trade-off**: Sem API, não há como integrar com outras ferramentas sem adaptação manual.

---

## 8. Fluxo de Trabalho Completo no Terminal

Sequência típica do começo ao fim:

```bash
# 0. Ativa o ambiente Python
source .venv/bin/activate

# 1. Sobe MinIO e vLLM em background
minio server ./minio-data --console-address ":9001" &
bash scripts/start_vllm.sh &

# 2. Configura os buckets (só precisa rodar uma vez)
python scripts/setup.py

# 3. Adiciona documentos e ingere
cp meus_documentos/*.pdf data/input/
python scripts/ingest.py

# 4. Indexa (pode demorar dependendo do volume e do modelo)
python scripts/index.py

# 5. Consulta
python scripts/query.py --mode local  --query "Quem são os autores mencionados?"
python scripts/query.py --mode global --query "Resuma os temas centrais dos documentos."
```