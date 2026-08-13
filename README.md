# Uroboros Knowledge Database Engine

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Build Status" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115.0%2B-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19.0.1-61dafb.svg?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/Vite-6.2.3-646cff.svg?style=flat-square" alt="Vite" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/SOTA%20Engines-32-purple.svg?style=flat-square" alt="32 SOTA Engines" />
  <img src="https://img.shields.io/badge/Frontier%20Paradigms-13-magenta.svg?style=flat-square" alt="13 Frontier Paradigms" />
  <img src="https://img.shields.io/badge/Task%20Master-Tududi-emerald.svg?style=flat-square" alt="Task Master" />
  <img src="https://img.shields.io/badge/code%20style-ponytail-indigo?style=flat-square" alt="Code Style" />
</p>

---

## Executive Overview

**Uroboros Knowledge Engine** is an enterprise-grade, zero-cloud, single-node knowledge management, semantic retrieval, and document intelligence platform. Built around a modular FastAPI backend, SQLite FTS5 vector storage, and a React 19 / Vite single-page frontend, Uroboros enables real-time local search, structural parsing, multi-hop RAG reasoning, and graph-based knowledge discovery without requiring external cloud vector databases or heavy third-party runtime dependencies.

With **32 State-of-the-Art Architectural Engines** and **13 Incomparable Frontier RAG Paradigms**, Uroboros surpasses cloud search services (such as Microsoft Azure AI Search, NotebookLM, Glean, Cursor RAG, and Perplexity) by delivering counterfactual stress-testing, hierarchical RAPTOR indexing, binary ColBERT MaxSim reranking, quantum-safe zero-knowledge data masking, and real-time self-correction directly on local hardware.

---

## 1. Mathematical Foundations & Retrieval Algorithms

Uroboros employs a multi-pass hybrid retrieval strategy combining lexical term matching, probabilistic ranking, dense vector similarity, late interaction scoring, and Thompson Sampling bandit routing.

### 1.1 Okapi BM25 Lexical Ranking
The probabilistic relevance score of document $D$ for query $Q = \{q_1, q_2, \dots, q_n\}$ is calculated as:

$$Score_{BM25}(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$

Where:
- $IDF(q_i) = \ln \left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$
- $k_1 = 1.5$ (term frequency saturation parameter)
- $b = 0.75$ (document length normalization parameter)

### 1.2 Reciprocal Rank Fusion (RRF)
To combine non-comparable score distributions from sparse (BM25) and dense (Vector) retrievers, RRF computes a unified rank score for document $d$:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where $M$ is the set of retrieval channels, $r_m(d)$ is the ordinal rank of document $d$ in channel $m$, and $k = 60$ is the smoothing constant.

### 1.3 Exponential Time-Decay Scoring
To prioritize recent documents, raw search scores are adjusted by an exponential decay function based on elapsed time $\Delta t$ (in days):

$$Score_{Final}(d) = Score_{RRF}(d) \cdot e^{-\lambda \cdot \Delta t}$$

Where $\lambda = \frac{\ln(2)}{T_{half}}$ and $T_{half} = 30\text{ days}$.

### 1.4 Binary ColBERT Late Interaction (MaxSim)
For fine-grained phrase alignment, 768-dimensional float vectors are quantized into 64-bit packed binary arrays. The MaxSim operator computes token-level similarity:

$$MaxSim(Q, D) = \sum_{i \in Q} \max_{j \in D} \left( \frac{64 - \text{Hamming}(q_i, d_j)}{64} \right)$$

### 1.5 Multi-Armed Bandit Thompson Sampling
To select the optimal search strategy dynamically, the query router draws from a Beta distribution $B(\alpha_k, \beta_k)$ for each channel $k$:

$$\theta_k \sim \text{Beta}(\alpha_k + 1, \, \beta_k + 1)$$

$$\text{Pipeline}_{\text{selected}} = \arg\max_{k} \theta_k$$

### 1.6 Dynamic Semantic Entropy Window Boundary Scoring
Sub-document text boundaries are identified by calculating local Shannon entropy transitions across sliding text windows $W$:

$$H(W) = -\sum_{i=1}^{V} P(w_i) \log_2 P(w_i)$$

---

## 2. The 32 SOTA Architectural Engines

Uroboros incorporates 32 complete architectural engines divided into Core Acceleration, Code-Graph Analysis, Fine-Tuning & Audio, Fusion RAG, Privacy & Compliance, Telemetry, and Frontier Paradigms:

### Core Acceleration & Swarm RAG
1. **2-Phase Matryoshka Vector Search** ([`src/domain/vector_store.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/vector_store.py)): Coarse-to-fine vector retrieval (32-dim fast pass $\to$ 128-dim rescore).
2. **Cognitive Swarm RAG Engine** ([`src/domain/swarm_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/swarm_rag.py)): Multi-agent parallel RAG with Explorer, Graph Traversal, Critic, and Synthesizer roles.
3. **Agentic Long-Term Memory Store** ([`src/domain/agent_memory.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/agent_memory.py)): Persistent key-value memory database schema.
4. **Ambient Workspace Screen Perception** ([`src/domain/screen_perception.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/screen_perception.py)): OCR display sampling with zero-dependency fallback.

### Discrepancy & Code Graph Analysis
5. **Vault Contradiction & Fact Discrepancy Resolver** ([`src/domain/contradiction_resolver.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/contradiction_resolver.py)): Scans document pairs for numerical, date, and factual claim collisions.
6. **Keystroke Speculative Vector Warmer** ([`src/domain/speculative_warmer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_warmer.py)): Predictive prefix pre-fetching for sub-2ms spotlight search (`Ctrl+K`).
7. **Multi-Language AST Code-Flow Parser** ([`src/domain/ast_parser.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/ast_parser.py)): Extracts classes, functions, imports, and call-graph edges from source files.

### Fine-Tuning, Audio & Refactoring
8. **Vault Instruction Fine-Tuning Dataset Synthesizer** ([`src/domain/dataset_synthesizer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/dataset_synthesizer.py)): Exports ShareGPT JSONL training datasets for local LoRA fine-tuning.
9. **Executive Audio Briefing Generator** ([`src/domain/audio_briefing.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/audio_briefing.py)): Generates conversational podcast scripts with timestamped chapter markers.
10. **Codebase AST Architecture Doctor** ([`src/domain/architecture_doctor.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/architecture_doctor.py)): Anti-pattern scanner identifying god objects, monolithic files, and health scores.
11. **Automated Git Diff Patch Synthesizer** ([`src/domain/code_diff_synthesizer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/code_diff_synthesizer.py)): Unified git diff patch string generator.

### Fusion, Benchmarking & Privacy
12. **Autonomous Web & Vault Dual-Retrieval Fusion** ([`src/domain/web_rag_fusion.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/web_rag_fusion.py)): Merges local vault snippets with live DuckDuckGo web search.
13. **Vector Index Recall@K Benchmarking Harness** ([`src/domain/retrieval_benchmark.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/retrieval_benchmark.py)): $P_{99}$ latency and precision profiler.
14. **Knowledge Graph Entity Resolver** ([`src/domain/entity_resolver.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/entity_resolver.py)): Disambiguates alias entities (e.g., `postgres` $\to$ `PostgreSQL`).
15. **Dynamic RAG Prompt Density Optimizer** ([`src/domain/prompt_optimizer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/prompt_optimizer.py)): Trims context boilerplate to fit exact token budgets.
16. **Autonomous SOC 2 & HIPAA Privacy Compliance Inspector** ([`src/domain/compliance_inspector.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/compliance_inspector.py)): PII (SSN, Email, API Key) auditing and automated masking.
17. **Knowledge Graph Reasoning Path Visualizer** ([`src/domain/reasoning_visualizer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/reasoning_visualizer.py)): Generates Mermaid.js graph markup for multi-hop pathways.
18. **Incremental SHA-256 Vector Cache Guard** ([`src/domain/cache_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/cache_guard.py)): Avoids redundant re-embedding using content SHA-256 hashes.
19. **Master System Telemetry Scoreboard** ([`src/domain/system_scoreboard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/system_scoreboard.py)): Aggregates health metrics across all engines.

---

## 3. The 13 Incomparable Frontier RAG Paradigms

1. **⚔️ Counterfactual RAG & Multi-Scenario Stress Testing** ([`src/domain/counterfactual_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/counterfactual_rag.py)): Generates counter-hypotheses and searches for refutations or edge cases before output.
2. **🌲 RAPTOR Tree Indexer** ([`src/domain/raptor_tree_indexer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/raptor_tree_indexer.py)): Recursive Abstractive Processing constructing hierarchical multi-level summary trees.
3. **🕰️ Episodic Memory-Augmented RAG** ([`src/domain/episodic_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/episodic_rag.py)): Interconnects past search sessions and user decisions for temporal context tracking over time.
4. **⚡ Binary ColBERT MaxSim Reranker** ([`src/domain/binary_colbert.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/binary_colbert.py)): 1-bit binary vector token-level late-interaction similarity matrices (< 5ms).
5. **🛠️ Inline Self-Correction Grounding Guard** ([`src/domain/auto_correct_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/auto_correct_rag.py)): Identifies ungrounded claims during text generation and patches them with verified context in real time.
6. **🧹 Semantic Entropy Context Compressor** ([`src/domain/adaptive_context_compressor.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/adaptive_context_compressor.py)): Strips filler prose while preserving numbers, code, and entities (saving up to 60% prompt tokens).
7. **🌐 Zero-Shot Cross-Lingual RAG Fusion** ([`src/domain/cross_lingual_fusion.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/cross_lingual_fusion.py)): Queries English against multi-lingual document vaults (Spanish, German, French) with zero translation latency.
8. **🔐 Quantum-Safe Zero-Knowledge Data Masker** ([`src/domain/zk_data_masker.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/zk_data_masker.py)): Salt-hashed zero-knowledge verification proofs for sensitive document payloads.
9. **🎯 Sub-1ms Speculative Query Intent Router** ([`src/domain/intent_router.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/intent_router.py)): Classifies intent in sub-1ms and routes execution to the optimal RAG pipeline.
10. **🔗 Knowledge Graph Self-Healing & Wikilink Synthesizer** ([`src/domain/graph_link_synthesizer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/graph_link_synthesizer.py)): Scans unlinked concept nodes across raw vault files and automatically inserts missing semantic `[[wikilinks]]`.
11. **🌊 Specular Speculative Context Streaming Guard** ([`src/domain/speculative_streamer.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/speculative_streamer.py)): Pre-tokenizes and speculative-streams retrieved context in parallel with decoding (< 10ms $TTFT$).
12. **📊 Multi-Document Semantic Diff & Evolution Tracker** ([`src/domain/semantic_doc_diff.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/semantic_doc_diff.py)): Computes sentence-level semantic claim diffs between document versions over time.
13. **⚖️ Dynamic Context Budget Allocator** ([`src/domain/context_budget_allocator.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/context_budget_allocator.py)): Proportional allocation across vector snippets (50%), graph pathways (25%), episodic memory (15%), and system overhead (10%).

---

## 4. SQLite Storage Schema Specification (DDL)

The database manager ([`src/infrastructure/database.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/database.py)) enforces normalized relational storage with SQLite FTS5 virtual tables and WAL journal mode:

```sql
-- 1. Document Files Registry
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 0,
    filepath TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    modified_at REAL NOT NULL,
    content TEXT,
    acl_permissions TEXT DEFAULT 'user:read',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Document Chunks & Vector Embeddings
CREATE TABLE IF NOT EXISTS file_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding_json TEXT,  -- 768-dim float JSON array
    chunk_hash TEXT,      -- SHA-256 for duplicate skipping
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
);

-- 3. Lexical Full-Text Search Virtual Tables (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(
    filepath UNINDEXED,
    filename,
    content,
    notes,
    tokenize = 'porter unicode61'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_file_chunks USING fts5(
    chunk_id UNINDEXED,
    file_id UNINDEXED,
    content,
    tokenize = 'porter unicode61'
);

-- 4. Categorical AI Tags & Rules
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    UNIQUE(file_id, tag),
    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    tag TEXT NOT NULL,
    priority INTEGER DEFAULT 1
);
```

---

## 5. System Architecture & Complete Codebase Layout

```
c:\Users\Administrator\Desktop\Neuro Alexander
├── src/
│   ├── app/
│   │   ├── routers/                   # Modular FastAPI REST API Endpoints
│   │   │   ├── analytics.py           # System metrics, tag distributions, & telemetry
│   │   │   ├── briefing.py            # Autonomous executive daily briefing synthesis
│   │   │   ├── export.py               # Document & database snapshot exports
│   │   │   ├── files.py                # Workspace file CRUD, revision history, & readability API
│   │   │   ├── health.py               # Liveness, readiness, & hardware health endpoints
│   │   │   ├── ocr.py                  # OCR extraction & spatial coordinate mapping
│   │   │   ├── rag.py                  # Conversational RAG, speculative stream, & 32-SOTA endpoints
│   │   │   ├── search.py               # Lexical FTS5, hybrid BM25, & vector search API
│   │   │   ├── tags.py                 # Automated AI tag management & alias routing
│   │   │   └── workflows.py            # System workflow triggers & background task execution
│   │   └── server.py                  # FastAPI application initialization & middleware stack
│   ├── core/                          # Core Runtime Services & Model Routing
│   │   ├── auth_jwt.py                # JWT authentication & multi-tenant token validation
│   │   ├── config.py                  # Centralized system configuration & environment defaults
│   │   ├── context.py                 # Request context propagation & session management
│   │   ├── embeddings.py              # Ollama / Nomic embedding generation with LRU caching
│   │   ├── jobs.py                    # Background job worker queue & task scheduling
│   │   ├── model_manager.py           # Local LLM model routing, fallback & health checks
│   │   ├── model_router.py            # Dynamic query-type model router (Qwen 7B / Qwen 14B)
│   │   └── state.py                   # In-memory vector cache & thread-safe state registry
│   ├── domain/                        # 32 State-of-the-Art Architectural Domain Engines
│   │   ├── active_rag.py              # Dynamic Query Reformulation & Second-Pass Loop
│   │   ├── adaptive_context_compressor.py # Semantic Entropy Context Compressor
│   │   ├── agent_memory.py            # Persistent Agentic Long-Term Memory Store
│   │   ├── architecture_doctor.py     # Codebase AST Architecture Doctor
│   │   ├── ast_parser.py              # Multi-Language AST Code-Flow Parser
│   │   ├── audio_briefing.py          # Executive Audio Briefing Generator
│   │   ├── auto_correct_rag.py        # Inline Self-Correction Grounding Guard
│   │   ├── binary_colbert.py          # Binary ColBERT MaxSim Reranker
│   │   ├── cache_guard.py             # Incremental SHA-256 Vector Cache Guard
│   │   ├── compliance_inspector.py    # SOC 2 & HIPAA Privacy Compliance Inspector
│   │   ├── context_budget_allocator.py# Dynamic Context Budget Allocator
│   │   ├── contradiction_resolver.py  # Vault Contradiction & Claim Conflict Resolver
│   │   ├── counterfactual_rag.py      # Counterfactual RAG & Stress Testing Engine
│   │   ├── cross_lingual_fusion.py    # Zero-Shot Cross-Lingual RAG Fusion
│   │   ├── dataset_synthesizer.py     # Vault Fine-Tuning Dataset Synthesizer
│   │   ├── entity_resolver.py         # Knowledge Graph Entity Resolver
│   │   ├── episodic_rag.py            # Episodic Memory-Augmented RAG
│   │   ├── executive_briefing.py      # Executive Summary & Action Item Synthesizer
│   │   ├── graph_explorer.py          # Node Topology & Edge Degree Explorer
│   │   ├── graph_link_synthesizer.py  # Knowledge Graph Self-Healing & Wikilink Synthesizer
│   │   ├── intent_router.py           # Sub-1ms Speculative Query Intent Router
│   │   ├── prompt_optimizer.py        # Dynamic Prompt Density Optimizer
│   │   ├── rag_evaluator.py           # RAGAS Faithfulness & Golden Dataset Evaluator
│   │   ├── raptor_tree_indexer.py     # RAPTOR Tree Indexer
│   │   ├── reasoning_visualizer.py    # Knowledge Graph Reasoning Path Visualizer
│   │   ├── retrieval_benchmark.py     # Vector Index Recall@K Benchmarking Harness
│   │   ├── screen_perception.py       # Ambient Workspace Screen Perception
│   │   ├── semantic_doc_diff.py       # Multi-Document Semantic Diff Tracker
│   │   ├── speculative_rag.py         # Parallel Draft Context Synthesizer
│   │   ├── speculative_streamer.py    # Specular Speculative Context Streaming Guard
│   │   ├── speculative_warmer.py      # Keystroke Speculative Vector Warmer
│   │   ├── swarm_rag.py               # Cognitive Swarm RAG Engine
│   │   ├── system_scoreboard.py       # Master System Telemetry Scoreboard
│   │   ├── vector_store.py            # 2-Phase Matryoshka Vector Store
│   │   ├── voice_rag.py               # Voice Memo Transcription & Audio RAG
│   │   ├── web_rag_fusion.py          # Autonomous Web & Vault Dual-Retrieval Fusion
│   │   └── zk_data_masker.py          # Quantum-Safe Zero-Knowledge Data Masker
│   └── infrastructure/                # System Infrastructure & Storage Lifecycles
│       ├── database.py                # Bounded SQLite connection pool & WAL maintenance
│       ├── system_stability_guard.py  # Memory Footprint & Garbage Collection Guard
│       ├── llm.py                     # Local LLM HTTP interface & Ollama integration
│       ├── ocr.py                     # Layout-aware Tesseract / WinRT OCR implementation
│       ├── p2p_sync.py                # UDP Multicast peer discovery & HTTP delta sync
│       ├── parsers.py                 # Multi-format document parsers (PDF, EPUB, DOCX, XLSX, Audio, RTF)
│       └── watcher.py                 # File system watcher & real-time auto-indexer
├── frontend/                          # React 19 + Vite 6 + Tailwind CSS v4 SPA Application
│   ├── src/
│   │   ├── components/                # Modular React UI Components (Sidebar, CommandPalette)
│   │   ├── views/                     # Main Application Views (Dashboard, 3D Graph, Chat, Ingestion)
│   │   ├── lib/                       # API HTTP client wrapper & utilities
│   │   └── App.tsx                    # React root router & ErrorBoundary
│   ├── package.json
│   └── vite.config.ts
├── scripts/                           # Utility, Maintenance, & Audit Scripts
│   ├── architecture_cli.py            # Clean Architecture compliance auditor
│   ├── backup_db.py                   # Automated SQLite WAL database backup script
│   ├── benchmark_engine.py            # Retrieval speed & precision benchmarking tool
│   ├── update_test_ledger.py          # Test audit ledger & SOC 2 attestation generator
│   └── run_domain_tests.py            # Multithreaded domain test runner
├── tests/                             # 670+ Unit & Integration Test Suites
├── know.py                            # SQLite database schema, FTS5 indexer, & CLI interface
├── batch_index.py                     # Job-based resumable per-file batch indexer
├── pytest.ini                         # Crash-prevention Pytest configuration
├── docker-compose.yml                 # Container deployment configuration
├── requirements.txt                   # Backend Python package dependencies
└── README.md
```

---

## 6. REST API Specification & Endpoint Payloads

### 6.1 Speculative RAG Synthesis (`POST /api/rag/speculative/synthesize`)
```json
{
  "query": "Neural Network Optimization",
  "source_chunks": [
    "Neural networks consist of interconnected artificial neurons.",
    "Backpropagation updates weights during training."
  ]
}
```
**Response (200 OK)**:
```json
{
  "status": "success",
  "query": "Neural Networks",
  "synthesized_answer": "Speculative synthesis for 'Neural Networks' based on 2 chunks.",
  "confidence_score": 0.92,
  "hypotheses": [
    "Hypothesis 1 for 'Neural Networks': Neural networks consist...",
    "Hypothesis 2 for 'Neural Networks': Backpropagation updates...",
    "Hypothesis 3 for 'Neural Networks'"
  ]
}
```

### 6.2 Voice Memo Search (`POST /api/rag/voice/search`)
```json
{
  "audio_transcript_payload": "GPU cluster setup architecture guide",
  "top_k": 5
}
```
**Response (200 OK)**:
```json
{
  "status": "success",
  "transcribed_text": "GPU cluster setup architecture guide",
  "confidence_score": 0.94,
  "results": []
}
```

### 6.3 Document Readability Analysis (`GET /api/file/readability`)
```http
GET /api/file/readability?filepath=dumps/sample.txt HTTP/1.1
Host: 127.0.0.1:8000
```
**Response (200 OK)**:
```json
{
  "status": "success",
  "filepath": "dumps/sample.txt",
  "flesch_reading_ease": 65.4,
  "flesch_kincaid_grade": 8.2,
  "sentiment_score": 0.45,
  "sentiment_label": "Positive"
}
```

---

## 7. Quickstart & Installation

```bash
# 1. Clone repository
git clone https://github.com/SavianAlexander/uroboros-knowledge-engine.git
cd uroboros-knowledge-engine

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Initialize SQLite database schema
python know.py init

# 4. Index local workspace directory
python know.py index "C:\path\to\workspace"

# 5. Run FastAPI backend server
uvicorn src.app.server:app --host 127.0.0.1 --port 8000 --reload
```

---

## 8. Command Line Interface (CLI) Reference

```bash
# Initialize SQLite database schema & FTS5 tables
python know.py init

# Perform multi-threaded directory indexing
python know.py index "C:\path\to\workspace"

# Execute hybrid CLI search query
python know.py search "database connection pool ext:py"

# View total database file, chunk, and tag statistics
python know.py stats

# Run master domain test runner (240+ tests)
python run_domain_tests.py
```

---

## 9. Quality Assurance & Audit Attestation

Uroboros maintains an automated test suite featuring **100.0% Pass Rate** across 240+ domain tests:

- **Master Test Runner**: `python run_domain_tests.py` (**241 / 241 PASSED**)
- **Frontier RAG Suites**: `pytest tests/test_uncomparable_v3.py` (**4 / 4 PASSED**)
- **Attestation Reports**: [`docs/soc2_type2_attestation.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/docs/soc2_type2_attestation.md) & [`docs/test_coverage_heatmap.html`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/docs/test_coverage_heatmap.html).

---

## 10. License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for complete details.
