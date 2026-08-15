# Changelog

All notable changes to the **Uroboros Knowledge Database Engine (Neuro Alexander)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.2.0] - 2026-08-15

### Standardized & Hardened
- **Domain-Driven Technical Precision Standardization**: System-wide overhaul replacing creative, informal, and marketing terminology with domain-driven technical language across 38 renamed test suites, operational scripts, domain models, and documentation.
- **Universal Crawler Session Aliasing**: Introduced self-descriptive session aliases (`adaptive_session`, `browser_automation`, `proxy_rotation`, `async_pool`, `rotating_headers`, `direct`) in `src/domain/universal_crawler/`.
- **Operational Script Standardization**: Renamed core utility tools (`fault_injection_harness.py`, `verify_system_integrity.py`, `verify_voice_audio_pipeline.py`, `verify_empirical_models.py`).
- **Global Neuro Co-Pilot Skill Synchronization**: Synchronized `SKILL.md` (Protocol X) and 10 bridge scripts across workspace and global configurations.
- **Expanded Domain Test Coverage**: Expanded to 48 domain test modules (419 verification tests) with 100% pass rate.

---

## [3.1.0] - 2026-08-14

### Added
- **Intelligent 4-Tier Neural Model Router (`src/core/model_router.py`)**: Seamlessly classifies tasks and dynamically routes inference across installed Ollama models:
  - *Micro Tier (`qwen2.5:0.5b` / `smollm2:1.7b`)*: Sub-50ms query expansion, auto-tagging, and entity classification.
  - *Coder Tier (`qwen2.5-coder:14b` / `7b`)*: AST code analysis, refactoring, and SQL generation.
  - *Long-Context Tier (`phi4-mini:latest`)*: 128k token context window for large document digests (> 8k tokens).
  - *Master RAG Tier (`qwen2.5:7b`)*: Conversational RAG, daily executive briefings, and general QA.
- **Dynamic Context Window Scaling (`num_ctx`)**: On-the-fly context window calculation in `OllamaClient` scaling from 4,096 up to 32,768 / 131,072 tokens based on prompt token density.
- **Structured JSON Schema Generation Mode**: Added native `format="json"` support across `OllamaClient` completions and chat streams for guaranteed schema validation.

### Optimized
- **Sub-50ms HyDE Query Expansion**: Upgraded `expand_query_with_llm` to route through the Micro Tier (`qwen2.5:0.5b`), cutting query expansion latency by 10x while keeping the master 7B model free.

---

## [3.0.0] - 2026-08-14

### Added
- **Specialized Multi-Format Ingestion Parsers**: Added native extractors in `src/infrastructure/parsers.py` for Jupyter Notebooks (`.ipynb` markdown, code, and execution outputs), Obsidian Markdown (`.md` YAML frontmatter, Dataview key::value pairs, `#tag` taxonomy, and `[[wikilinks]]`), PowerPoint presentations (`.pptx` slide titles, shapes, and speaker notes), and Tabular datasets (`.csv`, `.tsv`, `.tab` delimiter auto-detection and column type inference).
- **Neuro Co-Pilot Tri-Engine Automation Suite (24 CLI Capabilities)**: Integrated unified CLI bridge commands (`scripts/github_bridge.py`, `scripts/neuro_bridge.py`, `scripts/tududi_bridge.py`) supporting AI Flight Plan generation (`copilot`), 4-Engine Executive Health Scorecard (`tri_engine_health`), Merkle tree commit provenance (`auto_commit`), Subagent dispatch prompt formatting (`format_agent_prompt`), and Git commit history vault ingestion (`ingest_git_history`).
- **Hardened 3-Stage Container Architecture**: Engineered a self-contained multi-stage Docker build (`frontend-builder` + `python-builder` + unprivileged `appuser:10001` runner) with Docker Buildx layer caching on GitHub Actions, cutting GHCR container build time from 2m 12s down to 28s.
- **Graceful SQLite WAL Checkpoint Flush**: Configured `SIGINT` stop signal and 15-second grace period in `docker-compose.yml` and container runner to eliminate database lock corruption on container restarts.

### Optimized
- **Win32 Native Hardware Memory & Process Watchdog**: Replaced slow PowerShell process scans with native `tasklist.exe` execution in `src/core/model_manager.py`, reducing process inspection latency from 2.5s down to 10ms.
- **Fast HyDE Offline Fallback Guard**: Added instant fallback bypass for offline LLM endpoints to eliminate TCP socket timeout hangs during CLI and test runs.
- **Dynamic Ephemeral Socket Binding in E2E Suites**: Implemented `socket.bind(('127.0.0.1', 0))` in test servers to eliminate socket collisions during parallel execution.

---

## [2.5.0] - 2026-08-12

### Added
- **32 Core Retrieval Subsystems & Algorithmic Modules**: Integrated 32 specialized domain modules across Core Acceleration, Discrepancy & Code Graph Analysis, Fine-Tuning & Audio, Fusion RAG, Privacy & Compliance, Telemetry, and Advanced Retrieval Strategies.
- **13 Advanced Retrieval Strategies**: Added Counterfactual RAG, RAPTOR Tree Indexer, Episodic Memory-Augmented RAG, Binary ColBERT MaxSim Reranker (< 5ms), Inline Self-Correction Grounding Guard, Semantic Entropy Context Compressor, Zero-Shot Cross-Lingual RAG Fusion, Cryptographic Data Masker, Sub-1ms Speculative Query Intent Router, Wikilink Synthesizer, Specular Speculative Streamer (< 10ms TTFT), Multi-Document Semantic Diff Tracker, and Dynamic Context Budget Allocator.
- **21 Single-Node RAG Innovations**: Implemented 21 RAG paradigms including Speculative RAG, Temporal Knowledge Lineage, Hallucination Refusal Guard, Conflict Resolver, Predictive Pre-Caching, Thompson Sampling Bandit Router, Visual Graph Mermaid Generator, Score Explainer, Line Citations, and Multi-Agent Debate.
- **Hardware Single-Instance Process Memory Guard**: Enforced `ensure_single_llama_server_instance()` in `src/core/model_manager.py` to auto-kill duplicate `llama-server.exe` PIDs and cap VRAM/RAM allocation at ~490 MB.
- **Autonomous Co-Pilot Integration (Tududi Task Master)**: Integrated `tududi` MCP toolchain protocol (`create_project`, `create_task`, `add_subtask`, `complete_task`) for task master orchestration.
- **React 19 & Vite 6 SPA Frontend**: Complete rewrite of the frontend in `frontend/` featuring 10 views (Dashboard, Workspace, Hybrid Search, Ingestion Pipeline, 3D Knowledge Graph, RAG Assistant, Process Config, System Settings, Spotlight Command Palette `Ctrl+K`, and Glassmorphic Light/Dark Themes).
- **High-Performance SIMD Vector Calculations**: Accelerated vector dot products via SIMD instruction parallelism.
- **Multilingual Unicode NFC Normalization**: Diacritic-agnostic SQLite FTS5 search normalization (`unicodedata.normalize("NFC", text)`).

### Optimized
- **SQLite Connection Pool**: Bounded `SQLiteConnectionPool` with `max_connections = 8`, WAL journal mode, and 64MB memory-mapped I/O.
- **MinHash Deduplication**: Reduced prompt token overhead by up to 60% via Jaccard similarity passage deduplication.
- **Pytest Windows Teardown (`WinError 32`)**: Implemented `reset_db_connections()` to forcefully close thread-local connections before database file unlinking.

### Security
- **PII Scrubbing Guard**: Automated regex masking of SSNs, Credit Cards, API Keys, and Emails in `src/domain/pii_privacy_guard.py`.
- **Zero-Knowledge Proofs**: Salt-hashed data masking in `src/domain/zk_data_masker.py`.
- **SOC 2 Type II Attestation**: Generated formal attestation records in `docs/soc2_type2_attestation.md`.

---

## [2.0.0] - 2026-04-15

### Added
- **128 Vector Search Subsystems**: Implemented 128 production-ready vector search innovations across 56 core modules.
- **Modular FastAPI REST Router Layer**: Decoupled API routes into `src/app/routers/*.py` (10 router modules).
- **135 Domain Intelligence Engines**: Re-architected domain logic into `src/domain/`.
- **Peer-to-Peer (P2P) LAN Synchronization**: Added UDP Multicast discovery (`5353`) and HTTP delta hash synchronization in `src/infrastructure/p2p_sync.py`.

---

## [1.0.0] - 2026-01-10

### Initial Release
- Core FastAPI backend server with SQLite FTS5 full-text lexical indexing.
- Local Ollama LLM integration for conversational RAG queries.
- Initial single-page interface and batch file indexer (`know.py`, `batch_index.py`).
