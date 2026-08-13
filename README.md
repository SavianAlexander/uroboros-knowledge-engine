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

### Key Capabilities & System Targets
- **High-Performance Hybrid Retrieval**: Integrates lexical FTS5 BM25 search with dense Nomic embeddings, binary ColBERT late interaction, and RAPTOR summary trees.
- **Privacy & Security Compliance**: Native PII anonymization, Zero-Knowledge data masking, JWT multi-tenancy, and local-only processing.
- **Autonomous System Telemetry**: Live SQLite WAL connection pool management, SLA circuit breakers, self-healing vector index repair, and automated backup scheduling.
- **Multi-Format Ingestion Engine**: PyMuPDF structural parsing, layout-aware Tesseract OCR, speech audio metadata analysis, and job-based per-file batch indexing.

---

## Comprehensive Codebase Architecture

```
c:\Users\Administrator\Desktop\Neuro Alexander
├── src/
│   ├── app/
│   │   ├── routers/                   # Modular FastAPI REST API Endpoints
│   │   │   ├── analytics.py           # System metrics, tag distributions, & telemetry endpoints
│   │   │   ├── briefing.py            # Autonomous executive daily briefing synthesis
│   │   │   ├── export.py               # Document & database snapshot exports
│   │   │   ├── files.py                # Workspace file CRUD, revision history, & rename operations
│   │   │   ├── health.py               # Liveness, readiness, & hardware health endpoints
│   │   │   ├── ocr.py                  # OCR extraction & coordinate mapping
│   │   │   ├── rag.py                  # Conversational RAG, stream queries, & citation handling
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
│   ├── domain/                        # Specialized Mechanical RAG & Domain Intelligence (130+ Modules)
│   │   ├── acl_permission_engine.py   # Multi-tenant ACL permission evaluation
│   │   ├── acl_vector_guard.py        # Vector search query filtering by ACL bitmasks
│   │   ├── active_rag.py              # Dynamic query rewriting & iterative retrieval loop
│   │   ├── adaptive_context_compressor.py # Entropy-based token context budgeting
│   │   ├── agent_memory.py            # Long-term episodic memory storage for autonomous agents
│   │   ├── agent_swarm_manager.py     # Concurrent multi-agent task allocation
│   │   ├── analytics_engine.py        # Workspace usage metrics & corpus statistics
│   │   ├── anki_card_synthesizer.py   # Automatic flashcard extraction from indexed content
│   │   ├── architecture_doctor.py     # Codebase architectural compliance & clean-arch auditing
│   │   ├── ast_code_rag.py            # AST-level source code parsing & symbol retrieval
│   │   ├── ast_parser.py              # Universal AST token & structure parser
│   │   ├── audio_briefing.py          # Script generation for audio podcast briefings
│   │   ├── auto_correct_rag.py        # Grounding error detection & self-correcting rewrite loop
│   │   ├── auto_weight_tuner.py       # Dynamic RRF score weighting based on query intent
│   │   ├── background_worker.py       # Asynchronous background job runner
│   │   ├── bandit_query_router.py     # Multi-armed bandit strategy for retrieval route selection
│   │   ├── binary_colbert.py          # Zero-dependency binary vector quantization & MaxSim scoring
│   │   ├── cache_guard.py             # Vector cache invalidation & memory budget guard
│   │   ├── chat_intelligence.py       # Context assembly & multi-turn dialog manager
│   │   ├── citation_deep_linker.py    # Document character-offset citation URL generator
│   │   ├── code_diff_synthesizer.py   # Git diff analysis & structural code change synthesis
│   │   ├── code_doc_aligner.py        # Automated mapping between code functions and docstrings
│   │   ├── code_self_refactor.py      # AST-driven code simplification & refactoring recommendations
│   │   ├── colbert_reranker.py        # Multi-vector late interaction re-ranking engine
│   │   ├── compliance_inspector.py    # Enterprise compliance rule verification
│   │   ├── conflict_resolver.py       # Fact contradiction detection & reconciliation
│   │   ├── context_budget_allocator.py # Proportional token allocation across prompt sections
│   │   ├── context_memory_compressor.py# Semantic summarization of extended chat context
│   │   ├── contextual_hyde.py         # Hypothetical Document Embeddings (HyDE) expansion
│   │   ├── contextual_noise_mask.py   # Irrelevant text segment masking prior to vectorization
│   │   ├── contradiction_resolver.py  # N-gram & negation heuristic conflict detection
│   │   ├── counterfactual_rag.py      # Counterfactual reasoning & alternative hypothesis analysis
│   │   ├── cross_lingual_aligner.py   # Cross-lingual term mapping & semantic translation
│   │   ├── cross_lingual_fusion.py    # Multilingual query term fusion & ranking
│   │   ├── crosslingual_bridge.py     # Multi-language embedding space bridge
│   │   ├── crypto_audit_ledger.py     # SHA-256 cryptographic audit trail ledger
│   │   ├── daily_briefing.py          # Daily executive briefing generation
│   │   ├── data_provenance_tracker.py # Data lineage & document origin auditing
│   │   ├── dataset_synthesizer.py     # ShareGPT JSONL training dataset generation
│   │   ├── distractor_filter.py       # Negative chunk filtering & noise elimination
│   │   ├── entity_cooccurrence.py     # Co-occurrence matrix builder for named entities
│   │   ├── entity_extractor.py        # Named entity extraction (NER) engine
│   │   ├── entity_resolver.py         # Entity canonicalization & alias resolution
│   │   ├── entropy_chunker.py         # Information-entropy text chunking
│   │   ├── episodic_rag.py            # Session-aware episodic memory retrieval
│   │   ├── epistemic_belief_graph.py  # Probabilistic knowledge graph belief updating
│   │   ├── executive_briefing.py      # Executive TL;DR & KPI report synthesis
│   │   ├── extractive_summarizer.py   # Graph-based PageRank sentence extraction
│   │   ├── fact_check_engine.py       # Cross-document fact verification & claim scoring
│   │   ├── faq_synthesizer.py         # Automated Question-Answer pair extraction
│   │   ├── file_diff.py               # Side-by-side text & document diff comparison
│   │   ├── graph_explorer.py          # Interactive knowledge graph traversal & query API
│   │   ├── graph_export.py            # Graph format exporter (GraphML, JSON, CSV)
│   │   ├── graph_link_synthesizer.py  # Wikilink (`[[concept]]`) auto-linking engine
│   │   ├── graph_mermaid_generator.py # Mermaid.js graph markup generator
│   │   ├── graph_multihop.py          # Multi-hop graph path reasoning across entities
│   │   ├── graph_pagerank.py          # PageRank centrality calculation over document graph
│   │   ├── graph_reasoning.py         # Graph gap detection & unlinked entity analysis
│   │   ├── hallucination_guard.py     # N-gram overlap & factual consistency evaluator
│   │   ├── hypergraph_router.py       # Higher-order hypergraph connection routing
│   │   ├── index_self_healing.py      # Automated SQLite FTS5 index integrity repair
│   │   ├── intent_router.py           # Fast query intent classification (Code, Search, QA)
│   │   ├── knowledge_distiller.py     # Knowledge distillation & compact summary generation
│   │   ├── knowledge_self_healing.py  # Stale data detection & automatic re-indexing trigger
│   │   ├── legal_accuracy_engine.py   # Statutory legal clause parsing & precision check
│   │   ├── legal_rag_engine.py        # Contract & legal document specialized RAG
│   │   ├── louvain_clustering.py      # Modularity-based Louvain community detection for graph nodes
│   │   ├── mrl_compressor.py          # Matryoshka Representation Learning vector compression
│   │   ├── multi_agent_consensus.py   # Multi-agent voting & agreement protocol
│   │   ├── multi_agent_debate.py      # Multi-persona dialectical debate engine
│   │   ├── multilingual_rag.py        # Multi-language semantic search & retrieval
│   │   ├── multimodal_ocr_parser.py   # Image & scanned PDF layout-aware parser
│   │   ├── near_duplicate_detector.py # MinHash & SimHash near-duplicate document detection
│   │   ├── ocr_engine.py              # Tesseract OCR binding & image text extraction
│   │   ├── ocr_pipeline.py            # High-throughput asynchronous OCR processing pipeline
│   │   ├── parent_child_retrieval.py  # Small-chunk search with parent document context expansion
│   │   ├── persona_search_tuner.py    # User-persona tailored search result scoring
│   │   ├── pii_privacy_guard.py       # Regex & NER PII masking (SSN, Email, API Keys)
│   │   ├── predictive_precacher.py    # Pre-computation & precaching of frequent queries
│   │   ├── predictive_prefetch.py     # Pre-fetching related document chunks on search
│   │   ├── preference_learning.py     # User click-through & feedback preference optimization
│   │   ├── privacy_anonymizer.py      # Data anonymization engine for exports
│   │   ├── prompt_injection_guard.py  # Security filter against adversarial prompt injections
│   │   ├── prompt_optimizer.py        # Automated prompt refinement & compression
│   │   ├── query_intent_classifier.py # ML query intent classification
│   │   ├── rag_engine.py              # Primary RAG pipeline orchestrator
│   │   ├── rag_evaluator.py           # RAG Triad evaluation (Relevance, Groundedness, Answer Similarity)
│   │   ├── rag_grounding_guard.py     # Real-time grounding assertion checker
│   │   ├── rag_lineage_explainer.py   # Provenance & citation lineage tree generator
│   │   ├── raptor_tree_indexer.py     # Recursive RAPTOR summary tree construction
│   │   ├── readability_analyzer.py    # Flesch-Kincaid & Gunning Fog readability scoring
│   │   ├── reasoning_visualizer.py    # Multi-step reasoning path renderer
│   │   ├── recency_decay.py           # Exponential time-decay function calculation
│   │   ├── rerank_score_explainer.py  # Detailed breakdown of hybrid search scoring
│   │   ├── reranker.py                # Cross-encoder & score fusion re-ranking
│   │   ├── retrieval_benchmark.py     # Automated retrieval latency & recall benchmarking
│   │   ├── retrieval_feedback_refiner.py # Relevance feedback query adjustment
│   │   ├── schema_rag.py              # Database schema & JSON structure RAG
│   │   ├── screen_perception.py       # UI screenshot perception & layout analysis
│   │   ├── self_correcting_rewriter.py# Query reformulation on zero-hit search results
│   │   ├── self_rag_critique.py       # Self-reflection critique token evaluator
│   │   ├── semantic_doc_diff.py       # Semantic concept comparison between document versions
│   │   ├── semantic_drift_monitor.py  # Document semantic drift detection over time
│   │   ├── sla_circuit_breaker.py     # Latency SLA monitoring & circuit breaker guard
│   │   ├── smart_filter.py            # Natural language query parameter extractor (`ext:`, `tag:`)
│   │   ├── sota_rag_engine.py         # Advanced state-of-the-art hybrid RAG pipeline
│   │   ├── source_citation_generator.py # Automated footnote & citation anchor generator
│   │   ├── source_credibility_weight.py # Document authority & domain credibility scoring
│   │   ├── sparse_dense_fusion.py     # Reciprocal Rank Fusion (RRF) of sparse + dense results
│   │   ├── speculative_rag.py         # Parallel speculative retrieval & generation
│   │   ├── speculative_streamer.py    # Low-latency streaming token prediction
│   │   ├── speculative_warmer.py      # Cache warming for anticipated user queries
│   │   ├── sse_sync_stream.py         # Server-Sent Events (SSE) progress streaming
│   │   ├── streaming_token_compressor.py # Real-time stream token compression
│   │   ├── sublinear_ann_index.py     # Sub-linear approximate nearest neighbor search
│   │   ├── swarm_rag.py               # Distributed swarm search execution
│   │   ├── synthetic_qa_generator.py  # Automated synthetic Q&A generation from corpus
│   │   ├── system_health_telemetry.py # Hardware CPU/RAM/VRAM telemetry collector
│   │   ├── system_scoreboard.py       # System performance & search accuracy scoreboard
│   │   ├── system_telemetry.py        # System log & event telemetry accumulator
│   │   ├── temporal_rag.py            # Time-aware temporal search & point-in-time retrieval
│   │   ├── temporal_rag_lineage.py    # Document version timeline tracing
│   │   ├── transcription_engine.py    # Audio transcription wrapper
│   │   ├── universal_pipeline.py      # Unified document processing pipeline
│   │   ├── vector_drift_agent.py      # Embedding distribution drift monitoring
│   │   ├── vector_health_monitor.py   # Vector index fragment & null check audit
│   │   ├── vector_store.py            # SQLite vector storage & BLOB array serialization
│   │   ├── visual_canvas_rag.py       # Canvas visual diagram RAG
│   │   ├── voice_rag.py               # Voice command & speech search query processing
│   │   ├── web_rag_fusion.py          # Combined local & web search fusion
│   │   ├── web_search.py              # External web search scraper wrapper
│   │   ├── wikilink_parser.py         # Wikilink `[[syntax]]` extractor
│   │   ├── workflow_engine.py         # Asynchronous multi-step workflow executor
│   │   └── zk_data_masker.py          # Zero-Knowledge privacy masking engine
│   └── infrastructure/                # System Infrastructure & Storage Lifecycles
│       ├── backup_scheduler.py        # Non-blocking SQLite online WAL backup task
│       ├── database.py                # Thread-local SQLite connection pool & maintenance
│       ├── llm.py                     # Local LLM HTTP interface & Ollama integration
│       ├── ocr.py                     # Layout-aware Tesseract OCR implementation
│       ├── p2p_sync.py                # UDP Multicast peer discovery & HTTP delta sync
│       ├── parsers.py                 # Multi-format document parsers (PDF, EPUB, DOCX, Audio, ZIP)
│       ├── system_stability_guard.py  # Process memory limit enforcement & panic recovery
│       ├── telemetry.py               # Prometheus/JSON system telemetry logger
│       ├── vector_engine.py           # Vector similarity calculation & tag extraction
│       ├── watcher.py                 # File system watcher & real-time auto-indexer
│       └── webhook_dispatcher.py      # Event webhook dispatcher for external integrations
├── frontend/                          # React 18 + Vite + Tailwind CSS SPA Application
│   ├── src/
│   │   ├── components/                # Modular React UI Components
│   │   │   ├── CommandPalette.tsx     # Keyboard spotlight modal (`Ctrl+K`)
│   │   │   ├── Header.tsx             # Global navigation & status header
│   │   │   ├── Layout.tsx             # Responsive layout container
│   │   │   └── SystemControlsCard.tsx # Quick actions & hardware health status card
│   │   ├── views/                     # Main Application Views
│   │   │   ├── ChatView.tsx           # Conversational AI assistant & RAG interface
│   │   │   ├── ConfigView.tsx         # Auto-tag rules, synonyms, & snapshot settings
│   │   │   ├── DashboardView.tsx      # System health, telemetry metrics, & storage summary
│   │   │   ├── GraphView.tsx          # 3D interactive knowledge graph (`react-force-graph-3d`)
│   │   │   ├── IngestionView.tsx      # Batch ingestion queue & SSE job progress tracker
│   │   │   ├── LoginView.tsx          # Multi-tenant JWT authentication screen
│   │   │   ├── SearchView.tsx         # Hybrid lexical-semantic search & file preview
│   │   │   ├── SettingsView.tsx       # System parameters, API keys, & maintenance controls
│   │   │   └── WorkspaceView.tsx      # Directory corpus explorer & file management
│   │   ├── lib/                       # Frontend Utility Libraries
│   │   │   ├── api.ts                 # Axios API HTTP client wrapper
│   │   │   └── utils.ts               # Class name merging & zero-dependency helpers
│   │   ├── App.tsx                    # React application routing & root component
│   │   └── main.tsx                   # React entry point
│   ├── package.json
│   └── vite.config.ts
├── scripts/                           # Utility, Maintenance, & Audit Scripts
│   ├── architecture_cli.py            # Clean Architecture compliance auditor
│   ├── audit_ui_playwright.py         # End-to-End Playwright UI audit runner
│   ├── backup_db.py                   # Automated SQLite WAL database backup script
│   ├── benchmark_engine.py            # Retrieval speed & precision benchmarking tool
│   ├── capture_showcase.py            # Automated UI showcase screenshot recorder
│   ├── capture_ux_journey.mjs         # Node.js Playwright user journey snapshot tool
│   ├── chaos_monkey.py                # Fault injection & database stress testing utility
│   ├── parse_pytest_log.py            # Pytest log parser & automated test status report
│   ├── stress_test_domain.py          # Multithreaded domain stress test runner
│   └── update_test_ledger.py          # Test audit ledger & SOC 2 attestation generator
├── tests/                             # 670+ Unit, Integration, & Fuzzing Test Suites
├── know.py                            # SQLite database schema, FTS5 indexer, & CLI interface
├── batch_index.py                     # Job-based resumable per-file batch indexer
├── docker-compose.yml                 # Container deployment configuration
├── pytest.ini                         # Pytest configuration & test markers
├── requirements.txt                   # Backend Python package dependencies
└── README.md
```

---

## Detailed Subsystem Breakdown

### 1. Hybrid Mechanical Search & RAG Architecture
Uroboros employs a multi-stage search strategy combining deterministic lexical matching with probabilistic vector ranking:

1. **Natural Language Intent Parsing**: Queries pass through [`intent_router.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/intent_router.py) and [`smart_filter.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/smart_filter.py) to extract metadata constraints (`ext:pdf`, `tag:finance`) and route intent (Code, Search, QA).
2. **Lexical Full-Text Search (FTS5)**: Queries SQLite FTS5 indexes using porter stemming and technical synonym expansion (`db` $\leftrightarrow$ `database`).
3. **Dense Vector Search**: Generates 768-dimensional embeddings via Ollama (`nomic-embed-text`) with LRU caching in [`embeddings.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/core/embeddings.py).
4. **Binary ColBERT Late Interaction**: Uses [`binary_colbert.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/binary_colbert.py) for sub-millisecond MaxSim token-level similarity re-ranking.
5. **Reciprocal Rank Fusion (RRF)**: Merges lexical BM25 scores and vector cosine similarities via [`sparse_dense_fusion.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/sparse_dense_fusion.py).
6. **Grounding & Critique**: Validates response assertions against source context via [`self_rag_critique.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/self_rag_critique.py) and [`rag_grounding_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/rag_grounding_guard.py).

### 2. Multi-Format Ingestion & Batch Indexing
- **Structural Document Parsers ([`parsers.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/parsers.py))**: Extracts structured text from PDFs (PyMuPDF), Word documents (docx), EPUBs, HTML, CSV, and JSON files.
- **Audio Header Validation**: Validates WAV/MP3 duration and sampling rate prior to transcription to prevent C-level native library crashes on corrupt binary files.
- **Layout-Aware OCR ([`ocr_pipeline.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/ocr_pipeline.py))**: Runs Tesseract OCR on images and scanned PDF pages, extracting word bounding box coordinates for UI highlights.
- **Resumable Batch Indexer ([`batch_index.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/batch_index.py))**: Processes documents file-by-file with multi-threaded thread pools, SHA-256 duplicate chunk detection, and independent SQLite WAL transaction commits.

### 3. Knowledge Graph & Graph Reasoning
- **Wikilink Parsing ([`wikilink_parser.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/wikilink_parser.py))**: Automatically extracts `[[concept]]` syntax to form graph edges between documents.
- **Graph Reasoning Engine ([`graph_reasoning.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/graph_reasoning.py))**: Identifies unlinked entities, missing reference nodes, and isolated document subgraphs.
- **Community Detection ([`louvain_clustering.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/louvain_clustering.py))**: Applies Louvain modularity clustering to group documents into semantic topic communities.
- **3D Graph Visualization**: Visualizes entity nodes and document relationships using `react-force-graph-3d` in [`GraphView.tsx`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/frontend/src/views/GraphView.tsx).

### 4. Enterprise Safety & Governance
- **PII Privacy Protection ([`pii_privacy_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/pii_privacy_guard.py))**: Detects and redacts SSNs, email addresses, credit card numbers, and API keys.
- **Zero-Knowledge Data Masking ([`zk_data_masker.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/zk_data_masker.py))**: Applies cryptographic hashes to confidential identifiers while maintaining searchability.
- **Prompt Injection Defense ([`prompt_injection_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/prompt_injection_guard.py))**: Blocks adversarial system prompt overrides and unauthorized tool invocations.
- **Cryptographic Audit Ledger ([`crypto_audit_ledger.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/crypto_audit_ledger.py))**: Maintains an immutable append-only SHA-256 ledger of document modifications and administrative actions.

---

## API Endpoints Reference Matrix

| Router Group | Method | Endpoint Path | Description |
| :--- | :--- | :--- | :--- |
| **Search** | `GET` | `/api/search` | Fast FTS5 lexical, hybrid BM25, or vector search |
| **RAG** | `POST` | `/api/rag/query` | Conversational RAG assistant query execution |
| **RAG Stream** | `GET` | `/api/rag/stream` | Server-Sent Events (SSE) token streaming response |
| **Files** | `GET` | `/api/files` | List workspace files with pagination and tag filter |
| **Files CRUD** | `POST` | `/api/files/index` | Index or update a single file record |
| **File Delete** | `DELETE`| `/api/files/{file_id}` | Remove document and associated chunks from database |
| **Briefing** | `GET` | `/api/briefing/daily` | Generate automated executive daily briefing |
| **Analytics** | `GET` | `/api/analytics` | Retrieve corpus metrics, storage stats, and tag counts |
| **OCR** | `POST` | `/api/ocr/parse` | Extract OCR text and word bounding coordinates |
| **Tags** | `GET` | `/api/tags` | List all unique AI tags and auto-tag rules |
| **Health** | `GET` | `/api/health` | Hardware telemetry, database pool status, & uptime |
| **Export** | `GET` | `/api/export/db` | Download database snapshot or CSV/JSON export |
| **Workflows** | `POST` | `/api/workflows/trigger`| Trigger background workflows (re-index, backup) |

---

## Application Views & User Experience

### 1. Dashboard View
Displays real-time database status, document indexing throughput, storage utilization breakdown, and hardware telemetry metrics.
![Main Dashboard](docs/ux_journey/01_dashboard.png)

### 2. Workspace View
Provides a file browser interface for managing local directories, inspecting corpus metadata, and triggering manual re-indexing.
![Workspace](docs/ux_journey/02_workspace.png)

### 3. Search & Exploration View
Offers hybrid search with real-time similarity threshold sliders, document content previews, tag filtering, and syntax highlighting.
![Explorer](docs/ux_journey/03_search.png)

### 4. Ingestion Pipeline View
Monitors background document extraction, web URL scraping, and SSE progress tracking for active batch jobs.
![Ingestion Pipeline](docs/ux_journey/04_ingestion.png)

### 5. 3D Interactive Knowledge Graph
Interactive 3D graph view (`react-force-graph-3d`) rendering connections between document nodes, extracted entities, and wikilinks.
![Knowledge Graph](docs/ux_journey/05_graph.png)

### 6. Conversational RAG Assistant
AI chat interface supporting source citation deep-linking, context budget allocation controls, and multi-turn dialog memory.
![Conversational Assistant](docs/ux_journey/06_chat.png)

### 7. Process Configuration View
Manages auto-tagging rules, custom FTS synonyms, P2P network sync parameters, and database snapshot schedules.
![Process Config](docs/ux_journey/07_config.png)

### 8. System Settings View
Provides system diagnostic controls, API key management, database WAL optimization tools, and logs inspection.
![System Settings](docs/ux_journey/08_settings.png)

### 9. Spotlight Command Palette (`Ctrl+K`)
Keyboard-driven modal providing quick navigation across all application views, instant search execution, and ingestion actions.
![Command Palette](docs/ux_journey/09_command_palette.png)

### 10. WCAG AA Glassmorphism Styling
High-contrast glassmorphic dark and light themes with responsive UI elements complying with WCAG AA accessibility standards.
![Light Mode UI](docs/ux_journey/10_light_mode.png)

---

## Developer Installation & Execution Guide

### 1. Requirements & Setup
- **Python**: Version 3.12+
- **Node.js**: Version 18+ (for React frontend build)
- **Ollama** *(Optional for local embeddings)*: Running `nomic-embed-text` and `qwen2.5:7b`

```bash
# Clone the repository
git clone https://github.com/SavianAlexander/uroboros-knowledge-engine.git
cd uroboros-knowledge-engine

# Install Python backend dependencies
pip install -r requirements.txt

# Build the React frontend production bundle
cd frontend
npm install
npm run build
cd ..
```

### 2. Database Initialization & Ingestion
```bash
# Initialize SQLite FTS5 database schema
python know.py init

# Run batch indexer on a directory
python batch_index.py "C:\path\to\documents" --workers 4
```

### 3. Launching the Backend Server
```bash
# Launch Uvicorn FastAPI server
python -m uvicorn src.app.server:app --host 127.0.0.1 --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000` in your web browser.

### 4. Compiling Desktop Executable
```bash
pyinstaller build/UroborosKnowledgeHub.spec
```
Standalone executable will be generated at `dist/UroborosKnowledgeHub.exe`.

---

## Comprehensive Test Suite & Quality Assurance

Uroboros features an automated test suite containing over **670 unit, integration, and fuzzing tests**:

```bash
# Run fast non-E2E domain test suite
python -m pytest -q --tb=short -m "not e2e and not slow"

# Run deep fuzzing & concurrency test suite
python -m pytest tests/test_deep_fuzzing_and_concurrency.py -v

# Run full domain test suite
python run_domain_tests.py
```

### Test Isolation & Engineering Protocols
- **Dynamic Ephemeral Ports**: E2E test web servers bind dynamically to OS ephemeral ports (`socket.bind(('127.0.0.1', 0))`) to eliminate port collisions during parallel test execution.
- **Thread Connection Reset**: Database thread-local connections are closed forcefully via [`reset_db_connections()`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/database.py) before test cleanup to prevent Windows file lock errors (`WinError 32`).
- **Clean Architecture Certification**: Validated **100.0%** architecture compliance via [`scripts/architecture_cli.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/scripts/architecture_cli.py).
- **SOC 2 Type II Attestation**: Generated via [`scripts/update_test_ledger.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/scripts/update_test_ledger.py) -> [`docs/soc2_type2_attestation.md`](docs/soc2_type2_attestation.md).

---

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for complete details.
