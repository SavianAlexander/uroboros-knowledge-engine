# Deep System Architecture & Technical Blueprint

**Uroboros Knowledge Engine (Neuro Alexander)** is designed as an air-gapped, zero-cloud, single-node knowledge management, document intelligence, and multi-hop RAG platform. This document outlines the deep architectural design principles, layer separation, data flow models, and hardware isolation mechanisms that power the system.

---

## 1. Architectural Overview & Layer Decoupling

Uroboros follows strict **Clean Architecture** principles across 4 decoupled layers:

```
                  ┌─────────────────────────────────────────┐
                  │    Presentation Layer (React 19 SPA)    │
                  └────────────────────┬────────────────────┘
                                       │ HTTP / SSE / REST
                  ┌────────────────────▼────────────────────┐
                  │    API Router Layer (FastAPI Routers)   │
                  └────────────────────┬────────────────────┘
                                       │ Request Validation / Pydantic
                  ┌────────────────────▼────────────────────┐
                  │  Domain Intelligence Layer (135 Engines)│
                  └────────────────────┬────────────────────┘
                                       │ Business Logic & Algorithms
                  ┌────────────────────▼────────────────────┐
                  │ Infrastructure & Storage (SQLite / Ollama)│
                  └─────────────────────────────────────────┘
```

### Layer Breakdown:
1. **Presentation Layer (`frontend/`)**: Built with React 19, Vite 6, and Tailwind CSS v4. Communicates with backend endpoints using typed Fetch API streams, Server-Sent Events (SSE), and WebGL 3D Graph visualization (`react-force-graph-3d`).
2. **API Router Layer (`src/app/routers/`)**: 10 REST API routers handling request parsing, Pydantic validation, JWT token authentication, and HTTP response serialization.
3. **Domain Intelligence Layer (`src/domain/`)**: 135 specialized Python domain engines executing business logic, hybrid search ranking, AST code parsing, counterfactual reasoning, and GraphRAG traversals.
4. **Infrastructure Layer (`src/infrastructure/`)**: Thread-local SQLite connection pool (`database.py`), real-time Watchdog filesystem monitor (`watcher.py`), local Ollama LLM integration (`llm.py`), multi-format document extractors (`parsers.py`), and P2P mesh sync (`p2p_sync.py`).

---

## 2. Document Ingestion & Vector Indexing Subsystem

```mermaid
sequenceDiagram
    autonumber
    participant FS as Local Filesystem
    participant Watch as Watchdog Observer (`watcher.py`)
    participant Batch as Job Batch Indexer (`batch_index.py`)
    participant Parse as Multi-Format Parsers (`parsers.py`)
    participant DB as SQLite Relational Store (`database.py`)
    participant FTS as FTS5 Full-Text Virtual Tables

    FS->>Watch: File Creation / Modification Event
    Watch->>Watch: 500ms Debounce Buffer
    Watch->>Batch: Dispatch File Paths to Index Worker Queue
    Batch->>Parse: Parse File Structure (PDF/DOCX/IPYNB/Obsidian/PPTX/CSV/Audio/Image)
    Parse->>Parse: Compute Content SHA-256 Digest
    alt File Unchanged (SHA-256 Digest Match)
        Parse-->>Batch: Skip Re-indexing (Zero Cost)
    else File Modified / New
        Parse->>Batch: Return Clean Text & Structural Metadata
        Batch->>DB: Write Record to `files` Table
        Batch->>FTS: Tokenize and Insert Chunks into `fts_file_chunks`
        Batch->>DB: Write Binary Float Embeddings to `file_chunks`
    end
```

---

## 3. Hybrid Retrieval & Multi-Pass RAG Query Resolution

Uroboros uses a multi-pass hybrid retrieval pipeline combining sparse lexical search, dense vector similarity, late-interaction binary ColBERT, and GraphRAG:

```mermaid
flowchart TD
    Query["User Query String"] --> Intent["Intent Classifier & PII Guard"]
    Intent --> Bandit["Multi-Armed Bandit Router"]

    subgraph Channel_Retrieval ["Channel Retrieval"]
        Bandit --> BM25["SQLite FTS5 BM25 Lexical Match"]
        Bandit --> Vector["2-Phase Matryoshka Vector Search"]
        Bandit --> HyDE["Contextual HyDE Expansion"]
        Bandit --> Graph["GraphRAG 2-Hop Wikilink Traversal"]
    end

    BM25 --> RRF["Reciprocal Rank Fusion (k=60)"]
    Vector --> RRF
    HyDE --> RRF
    Graph --> RRF

    RRF --> Decay["Exponential Time-Decay Score Multiplier"]
    Decay --> ACL["ACL Security Permission Filter"]
    ACL --> ColBERT["Binary ColBERT MaxSim 64-bit Hamming Rerank"]
    ColBERT --> Dedupe["MinHash Jaccard Passage Deduplication"]
    Dedupe --> Grounding{"Inline Self-RAG Grounding Guard"}

    Grounding -- "Confidence >= 0.65" --> Output["Verified Answer + Source Line Citations"]
    Grounding -- "Confidence < 0.65" --> Refusal["Refusal Report & Knowledge Gap Summary"]
```

---

## 4. Hardware Single-Instance Process & Memory Isolation

To prevent process bloat, VRAM pagefile exhaustion, and system crashes during high-concurrency workloads, Uroboros enforces hardware isolation:

```python
# Hardware Single-Instance Environment Flags
os.environ["OLLAMA_NUM_PARALLEL"] = "1"
os.environ["OLLAMA_MAX_LOADED_MODELS"] = "1"
os.environ["OLLAMA_KEEP_ALIVE"] = "5m"
```

- **Process Scanning**: Before initiating LLM inference, `model_manager.py` scans OS processes for `llama-server.exe`.
- **Deduplication**: Automatically force-terminates older duplicate PIDs (`taskkill /F /PID`), maintaining **exactly 1 active model process in RAM/VRAM**.
- **Memory Footprint**: Normalizes model memory allocation to ~490 MB VRAM (down from 6.18 GB of duplicate process overhead).

---

## 5. Peer-to-Peer (P2P) Air-Gapped LAN Synchronization Protocol

Uroboros nodes discover and synchronize knowledge indices across local network subnets without cloud dependency:

```
[Node A: 192.168.1.10] ◄────── UDP Multicast Broadcast (Port 5353) ──────► [Node B: 192.168.1.15]
         │                                                                          │
         ├──────────────────── SHA-256 Manifest Compare ──────────────────────────┤
         │                                                                          │
         └── HTTP Compressed Delta Chunk Fetch (`GET /api/sync/delta`) ─────────────┘
```

1. **UDP Multicast Discovery**: Periodic ping packets discover active Uroboros nodes on local LAN interface bounds.
2. **Manifest Comparison**: Nodes exchange document SHA-256 manifests to identify missing or updated file chunks.
3. **Delta Sync**: Incremental HTTP chunk streams download missing vector BLOBs without full database transfers.
