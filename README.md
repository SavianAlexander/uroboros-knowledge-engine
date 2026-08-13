# Uroboros Knowledge Database Engine

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Build Status" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18.3.1-61dafb.svg?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/code%20style-ponytail-indigo?style=flat-square" alt="Code Style" />
</p>

---

## Executive Overview

Uroboros Knowledge Engine is an enterprise-grade, zero-dependency, self-contained knowledge management, semantic retrieval, and document indexing platform. Built around a modular FastAPI backend, SQLite FTS5 vector storage, and a React 18 / Vite single-page frontend, Uroboros enables real-time local search, structural parsing, multi-hop RAG reasoning, and graph-based knowledge discovery without requiring external cloud vector database infrastructure or heavy runtime dependencies.

### Target Audience & Operational Use Cases
- **Enterprise Engineering Teams**: Zero-latency searching across multi-repository codebases, technical spec documentation, and architectural decision records.
- **Privacy & Compliance Organizations**: Local-first processing of sensitive PDF documents, OCR image extractions, and PII anonymization without external network transmission.
- **High-Throughput Research Operations**: Automated ingestion, wikilink synthesis, AST code parsing, and multi-agent debate reasoning on local workstations.

---

## Architectural Layout & Modular Core

```
c:\Users\Administrator\Desktop\Neuro Alexander
├── src/
│   ├── app/
│   │   ├── routers/        # Decoupled FastAPI API route handlers (search, rag, files, health, tags, ocr)
│   │   └── server.py       # FastAPI application initialization & middleware
│   ├── core/
│   │   ├── embeddings.py   # Ollama / Nomic embedding generation & LRU caching
│   │   ├── model_manager.py# Local LLM model routing & fallback mechanisms
│   │   ├── state.py        # Shared application state & memory cache
│   │   └── domain/         # Core domain service interfaces
│   ├── domain/             # Specialized Mechanical RAG & Intelligence Engines (100+ domain modules)
│   └── infrastructure/     # SQLite database connection lifecycle, OCR, & multi-format parsers
├── frontend/               # React 18 + Vite + Tailwind CSS Single-Page Web Application
│   ├── src/
│   │   ├── components/     # CommandPalette, SystemControlsCard, Navigation Header
│   │   ├── views/          # Dashboard, Workspace, Search, Graph, Chat, Ingestion, Config, Settings
│   │   └── lib/            # Zero-dependency API client & utility helpers
│   └── package.json
├── tests/                  # 670+ automated domain unit, integration, and fuzzing test suites
├── know.py                 # SQLite database schema, FTS5 indexer, and query interface
├── batch_index.py          # Job-based resumable per-file batch indexer
└── README.md
```

---

## Architectural Summary & Core Engines

### 1. Multi-Stage Mechanical RAG Architecture
Uroboros integrates a multi-pass hybrid retrieval pipeline:
- **Lexical/FTS5 Engine**: SQLite FTS5 index for metadata pushdown (`ext:`, `tag:`, `size:`) and exact phrase matching.
- **Okapi BM25 Probabilistic Ranking**: Length-normalized ($b=0.75$) term frequency saturation ($k_1=1.5$) via `MiniVectorEngine`.
- **Porter Stemmer & Technical Synonyms**: Automated suffix stemming and domain acronym expansions (`db` $\leftrightarrow$ `database`, `auth` $\leftrightarrow$ `authentication`).
- **Recency Decay & Trimming**: Exponential time-decay scoring ($e^{-\lambda \Delta t}$) and punctuation-boundary sentence trimming.

### 2. Specialized Intelligence & Domain Modules (`src/domain/`)
- **Binary ColBERT Late Interaction**: Zero-dependency binary vector quantization and MaxSim late interaction scoring (`binary_colbert.py`).
- **Hierarchical RAPTOR Tree Indexer**: Recursive document clustering and summary tree indexing (`raptor_tree_indexer.py`).
- **AST Code RAG & Diff Synthesizer**: AST-level code parsing, structural cross-referencing, and diff synthesis (`ast_code_rag.py`, `code_diff_synthesizer.py`).
- **Adaptive Context Entropy Compressor**: Entropy-based token density compression and context budget allocation (`adaptive_context_compressor.py`, `context_budget_allocator.py`).
- **Self-RAG Critique & Grounding Guard**: Real-time hallucination prevention, grounding verification, and query re-writing (`self_rag_critique.py`, `rag_grounding_guard.py`).
- **Epistemic Belief Graph & Hypergraph Router**: Multi-hop hypergraph routing, PageRank node centrality, and knowledge graph exports (`epistemic_belief_graph.py`, `hypergraph_router.py`).
- **PII Privacy Guard & ZK Data Masker**: Regex and pattern-based privacy masking with zero-knowledge data auditing (`pii_privacy_guard.py`, `zk_data_masker.py`).
- **Multi-Agent Debate & Consensus**: Multi-persona query debate and consensus synthesis (`multi_agent_debate.py`, `multi_agent_consensus.py`).

### 3. Resumable Batch Indexing & Safe Ingestion
- **Batch Indexer (`batch_index.py`)**: Multi-threaded, per-file resumable ingestion pipeline with SHA-256 duplicate chunk skipping and WAL transaction isolation.
- **Safe Multi-Format Parsers**: PyMuPDF extraction, Tesseract layout analysis, structured OCR parsing, and audio metadata header validation before model transcription (`src/infrastructure/parsers.py`).

### 4. Standalone PyInstaller Desktop Bundle
Executes as a standalone Windows application (`dist/UroborosKnowledgeHub.exe`) with `sys._MEIPASS` dynamic asset loading, single-instance mutex locking, and zero external dependency requirements.

---

## Key Features & Enterprise Capability Matrix

- **Executive Daily Briefings**: Synthesizes active document metrics, tag distributions, and executive summaries (`GET /api/briefing/daily`).
- **Natural Language Filter & SQL Translator**: Converts natural queries into structured SQLite search clauses (`src/domain/intent_router.py`).
- **Knowledge Graph Reasoning & Gap Analysis**: Detects unlinked concept nodes (`[[wikilinks]]`) and isolated document clusters (`src/domain/graph_reasoning.py`).
- **Multi-Model GPU Routing**: Intelligent prompt dispatching between `qwen2.5:7b` (~90 tok/s) and `qwen2.5-coder:14b` on AMD Radeon RX 7900 XTX hardware.
- **Modern React 18 Interface**: Vite-powered SPA with 3D force-graph visualization (`react-force-graph-3d`), spotlight command palette (`Ctrl+K`), system control dashboards, and dark/light glassmorphic styling.
- **Peer-to-Peer Knowledge Synchronization**: Multicast UDP peer discovery and HTTP delta exchange for cloud-free workstation sync (`src/infrastructure/p2p_sync.py`).
- **Non-Blocking Online Backups**: SQLite online WAL database snapshotting (`src/infrastructure/backup_scheduler.py`).

---

## Application User Interface & Views Walkthrough

Below is a visual overview of the Uroboros Knowledge Engine React interface:

### System Architecture Flow
![System Architecture Flow](docs/ux_journey/system_architecture_flow.svg)

### 1. Dashboard View
Real-time database status metrics, ingestion velocity, storage distribution, tag breakdowns, and system health telemetry.
![Main Dashboard](docs/ux_journey/01_dashboard.png)

### 2. Workspace View
Direct inspection of local workspace directories, corpus statistics, and interactive knowledge graph previews.
![Workspace](docs/ux_journey/02_workspace.png)

### 3. Search & Exploration View
Hybrid lexical-semantic search with real-time similarity filtering, file content previews, and multi-tag query stacking.
![Explorer](docs/ux_journey/03_search.png)

### 4. Ingestion Pipeline View
Document extraction, URL scraping, and real-time SSE progress tracking across batch indexing jobs.
![Ingestion Pipeline](docs/ux_journey/04_ingestion.png)

### 5. 3D Interactive Knowledge Graph
Interactive 3D spatial view (`react-force-graph-3d`) visualizing relationships across documents, entity nodes, and wikilinks.
![Knowledge Graph](docs/ux_journey/05_graph.png)

### 6. Conversational RAG Assistant (AI Chat)
Interactive chat interface featuring source citation deep-linking, context budget allocation, and model selection controls.
![Conversational Assistant](docs/ux_journey/06_chat.png)

### 7. Process Configuration View
Manage auto-tag rules, SQLite database snapshots, peer-to-peer sync settings, FTS synonyms, and query aliases.
![Process Config](docs/ux_journey/07_config.png)

### 8. System Settings View
Environment parameter inspection, API key configuration, database maintenance controls, and diagnostic telemetry.
![System Settings](docs/ux_journey/08_settings.png)

### 9. Command Palette Modal (`Ctrl+K`)
Keyboard-driven spotlight modal for instantaneous navigation across views, search execution, and ingestion actions.
![Command Palette](docs/ux_journey/09_command_palette.png)

### 10. WCAG AA Glassmorphism Themes
High-contrast dark and light themes with responsive UI element scaling and WCAG AA accessibility compliance.
![Light Mode UI](docs/ux_journey/10_light_mode.png)

---

## Installation & Developer Setup

### 1. Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies and build bundle
cd frontend
npm install
npm run build
cd ..
```

### 2. Database Initialization & Indexing
```bash
# Initialize SQLite database schema
python know.py init

# Batch index a target document directory
python batch_index.py "C:\path\to\documents"
```

### 3. Start Backend Server
```bash
# Launch Uvicorn FastAPI server
python -m uvicorn src.app.server:app --host 127.0.0.1 --port 8000 --reload
```
Open `http://127.0.0.1:8000` in your web browser.

### 4. Standalone Desktop Build Compilation
```bash
pyinstaller build/UroborosKnowledgeHub.spec
```
Output executable compiled to `dist/UroborosKnowledgeHub.exe`.

---

## Testing & Quality Assurance Framework

Uroboros includes a comprehensive domain test suite with over **670 automated unit, integration, and fuzzing tests**:

```bash
# Run fast non-E2E domain test suite
python -m pytest -q --tb=short -m "not e2e and not slow"

# Run specific domain intelligence test suite
python -m pytest tests/test_deep_fuzzing_and_concurrency.py -v
```

- **Domain Isolation**: Tests run with dynamic OS ephemeral port allocation to prevent socket collisions.
- **Thread Safety**: Complete database thread-local lifecycle reset (`reset_db_connections()`) before pytest teardown to prevent Windows lock issues.
- **Clean Architecture Certification**: Certified **100.0%** compliance (`python scripts/architecture_cli.py audit .`).
- **SOC 2 Type II Attestation**: Generated via `python scripts/update_test_ledger.py --soc2` -> [`docs/soc2_type2_attestation.md`](docs/soc2_type2_attestation.md).

---

## License

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for complete details.
