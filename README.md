# Uroboros Knowledge Database Engine

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/SavianAlexander/uroboros-knowledge-engine/tests.yml?branch=master&style=flat-square" alt="Build Status" />
  <img src="https://img.shields.io/github/license/SavianAlexander/uroboros-knowledge-engine?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.111.0-teal.svg?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-FTS5-orange.svg?style=flat-square" alt="SQLite" />
  <img src="https://img.shields.io/badge/code%20style-ponytail-indigo?style=flat-square" alt="Code Style" />
</p>

---

## About Uroboros

Uroboros is a lightweight, self-contained knowledge management, indexing, and semantic exploration engine. Built with zero-dependency minimalist core components, it serves as a central brain for search and text extraction on local workspaces. It is designed to automatically ingest, watch, tag, synonym-expand, and query documents without requiring bulky external vector database dependencies or heavy runtime models.

### Target Audience
- **Developers & Researchers**: Searching local codebases, documentation, research papers, and spreadsheets.
- **Privacy-First Teams**: Local processing of annotations, OCR text, and indexing logs without transmitting data outside local subnets.
- **Minimalist Engineers**: Leveraging standard SQLite tools and local indexing pipelines for extreme speed and low CPU footprints.

---

## Architectural Summary & Core Engines

### 1. Hybrid Mechanical RAG Architecture
Uroboros integrates a multi-pass precision mechanical search system:
- **Lexical/FTS5 Engine**: Native SQLite FTS5 indexes files, annotations, and titles with SQL metadata filter pushdown (`ext:`, `tag:`).
- **Okapi BM25 Probabilistic Ranking**: Length normalization ($b=0.75$) and term frequency saturation ($k_1=1.5$) via `MiniVectorEngine`.
- **Porter Stemmer & Technical Synonyms**: Rule-based word suffix stemming and technical acronym expansions (`db` $\leftrightarrow$ `database`, `auth` $\leftrightarrow$ `authentication`).
- **Recency Time-Decay & Sentence Trimming**: Exponential time-decay scoring ($e^{-\lambda \Delta t}$) and punctuation-boundary sentence trimming.

### 2. Standalone PyInstaller Desktop Bundle & Hardware Calibration
Executes as a single standalone Windows binary (`dist/UroborosKnowledgeHub.exe`) with native `sys._MEIPASS` dynamic asset resolution, single-instance lock protection, and zero runtime installation overhead.

### 3. Extended Local OCR & Audio Transcription Engines
Extracts text from images via multi-stage OCR (Tesseract fallback to Pillow layout analysis) and decodes WAV/MP3 audio streams into 10-second timestamped transcript chunks with RMS energy thresholding.

### 4. Local Peer-to-Peer Knowledge Base Synchronization
Discovers workstation peers on local networks using UDP Multicast (ports 5353/5354) and exchanges document delta hashes for cloud-free workstation sync.

---

## Key Features

- **Okapi BM25 & HyDE RAG Extraction**: Multi-hop query decomposition, parent-child chunking, and 2-pass precision re-ranking.
- **Local OCR & Audio Transcript Chunking**: Extract text from images and timestamped WAV/MP3 audio streams.
- **Local Peer-to-Peer Vault Sync**: Sync knowledge bases across LAN peers via UDP discovery and HTTP delta exchange.
- **Online Database Backup & Auth Guard**: Live, non-blocking online SQLite WAL backups (`scripts/backup_db.py`) and configurable API Key/Bearer token auth guard (`src/shared/auth.py`).
- **Dark & Light Glassmorphism Theme Switcher**: 1-click high-contrast UI theme switching with WCAG AA compliance.
- **PDF Report Customizer**: Generate customized ReportLab PDF directories with custom titles and brand accent palettes (*Indigo*, *Crimson*, *Emerald*, *Charcoal*).

---

## System Architecture & Views Walkthrough

Here is a visual guide to the system architecture and views of Uroboros Knowledge Engine:

### System Architecture Flow
![System Architecture Flow](docs/ux_journey/system_architecture_flow.svg)

### 1. Main Dashboard & Document Intelligence Panel
The primary command center showing database status, real-time indexing velocity, storage usage by MIME type, tag distributions, and search activity telemetry.

![Main Dashboard](docs/ux_journey/01_dashboard_main.png)

### 2. Search & Document Explorer
Search files with hybrid lexical-semantic search, filter by similarity thresholds, preview text files in real-time, and stack multi-tag queries.

![Search Explorer](docs/ux_journey/01_explorer_tab.png)

### 3. Conversational RAG Assistant
Query stored knowledge, query statistics, and document summaries with automatic source-citation links and SSE token streaming.

![Conversational Assistant](docs/ux_journey/02_rag_chat_tab.png)

### 4. 1,000-Node Interactive Knowledge Graph
Upgraded D3 canvas graph visualizer rendering up to 1,000 document nodes smoothly using Spatial Grid Partitioning, Energy Cooling ($E < \epsilon$), Viewport Culling, and Wikilink parsing (`[[wikilink]]`).

![Knowledge Graph](docs/ux_journey/03_knowledge_graph_tab.png)

### 5. Automated Rules & Admin Console
Configure regex auto-tagging rules, word synonym mappings, search bookmarks, backup schedulers, and monitor LAN sync peers.

![Admin Console](docs/ux_journey/04_admin_console_tab.png)

---

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database & Scan**:
   Create SQLite tables and scan the local `dumps/` directory:
   ```bash
   python know.py init
   python know.py index dumps
   ```

3. **Start Server**:
   ```bash
   python main.py
   ```
   Open `http://127.0.0.1:8000` inside your browser.

4. **Standalone Desktop Bundle Compilation**:
   ```bash
   pyinstaller build/UroborosKnowledgeHub.spec
   ```
   Output binary generated at `dist/UroborosKnowledgeHub.exe`.

---

## Testing & Audit Engine (v1.0.0-enterprise)

Uroboros features an advanced **31-Domain Allocated Test Suite & Audit Ledger Engine** running 269 core & crash simulation tests with **100% Pass Rate**:

- **Master Domain Audit Suite**: `python run_domain_tests.py`
- **Fast Incremental Mode (100ms)**: `python run_domain_tests.py --fast`
- **Clean Architecture Compliance**: Certified **100.0%** (`python scripts/architecture_cli.py audit .`)
- **SOC 2 Type II Attestation**: `python scripts/update_test_ledger.py --soc2` -> [docs/soc2_type2_attestation.md](docs/soc2_type2_attestation.md)
- **Visual Coverage Heatmap**: `python scripts/update_test_ledger.py --heatmap` -> [docs/test_coverage_heatmap.html](docs/test_coverage_heatmap.html)
- **System Healthcheck Endpoint**: `/api/health`

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Running Automated Tests

Execute the domain test suites via pytest:
```bash
pytest tests/test_domain_rag.py tests/test_domain_vector.py
```
