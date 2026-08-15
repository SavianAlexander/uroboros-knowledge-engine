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

## 5. Tri-Engine Autonomous Orchestration

```mermaid
graph TB
    subgraph Engine1["1. Neuro Knowledge Engine"]
        FTS5[("SQLite FTS5 Lexical Vault")]
        ColBERT["Binary ColBERT Vector Engine"]
        GraphDB["SQLite HyperGraph Engine"]
        Ollama["Local Ollama Neural Router"]
    end

    subgraph Engine2["2. Tududi Task Master"]
        TaskDB[("Task Store & Burndown")]
        SprintEngine["Project #13 Sprint Tracker"]
        Habits["Habit & Goal Synchronizer"]
        AuditTrail["Autonomous Execution Audit Trail"]
    end

    subgraph Engine3["3. GitHub & Merkle Provenance"]
        GitCLI["GitHub CLI Bridge"]
        MerkleEngine["SHA-256 Merkle Provenance Engine"]
        CIWorkflows["GitHub Actions Automated Matrix"]
        ReleaseCert["SOC 2 Provenance Attestation"]
    end

    Agent["Antigravity AI Agent / Senior Dev"] -->|FastAPI REST & MCP| Engine1
    Agent -->|Tududi MCP & REST| Engine2
    Agent -->|Git / GitHub Bridge CLI| Engine3

    Engine1 <-->|Context-Informed Flight Plans| Engine2
    Engine2 <-->|Automated Issue & Task Sync| Engine3
    Engine3 <-->|SOC 2 Cryptographic Root Signatures| Engine1
```

---

## 6. 10-Bridge Neuro Co-Pilot Asynchronous DAG Pipeline

```mermaid
graph TD
    subgraph Stage1["Stage 1: Concurrent Independent Discovery (Parallel Gather)"]
        B1["Architecture Bridge<br/>(AST & Clean Arch Doctor)"]
        B2["Tududi Bridge<br/>(Task Master Burndown)"]
        B3["GitHub Bridge<br/>(Git & Merkle Hash)"]
        B4["Visual Audit Bridge<br/>(Layout QA & CSS Sync)"]
        B5["Process Hygiene Bridge<br/>(OS Memory & Process Audit)"]
    end

    subgraph Stage2["Stage 2: Context-Informed Verification (Parallel Async)"]
        B6["Snapshot Bridge<br/>(Client Showcase & Deck Generator)"]
        B7["Neuro Bridge<br/>(ColBERT Vector Vault Verification)"]
        B8["EVE Online Fleet Bridge<br/>(ESI Telemetry & Physics Model)"]
        B9["System Recovery Bridge<br/>(Zero-Reboot Windows Recovery)"]
    end

    subgraph Stage3["Stage 3: Verification & Provenance Ledger"]
        Ledger[("Persistent Execution Ledger<br/>docs/bridge_contracts/execution_ledger.json")]
        Cert["SOC 2 Type II Merkle Certificate<br/>docs/release_certificate_v1.0.0.json"]
    end

    Trigger["Co-Pilot Execution Trigger"] --> Stage1
    B1 & B2 & B3 & B4 & B5 --> Stage2
    B6 & B7 & B8 & B9 --> Stage3
    Stage3 --> Ledger
    Stage3 --> Cert
```

---

## 7. Universal Crawler & Puerto Rico Statutory Legal Ingestion Engine

```mermaid
flowchart LR
    subgraph Input["Job Configuration"]
        TargetURL["Target URL / Legal Portal"]
        SessionMode{"Session Mode"}
    end

    subgraph CrawlerEngine["Crawler Orchestration Engine"]
        Frontier["Priority Frontier Queue"]
        RateLimiter["Adaptive Domain Rate Limiter"]
        
        subgraph SessionEngines["Session Harvesting Engines"]
            S1["Adaptive Session"]
            S2["Browser Automation"]
            S3["Proxy Rotation"]
            S4["Async Worker Pool"]
            S5["Rotating Headers"]
            S6["Direct Session"]
        end

        Extractor["Deep Content Extractor"]
        Forensic["Forensic Ingestion Vault"]
    end

    subgraph LegalDomain["Puerto Rico Legal & Knowledge Core"]
        Statutory["Statutory Anatomy Parser"]
        Constitucion["Constitucion ELA 1952"]
        CodCivil["Codigo Civil 2020"]
        CodPenal["Codigo Penal 2012"]
        PDFExtract["OCR & PDF Text Extraction"]
    end

    subgraph OutputVault["Knowledge Engine Integration"]
        VectorMatrix["Vector Semantic Matrix"]
        HyperGraph["SQLite HyperGraph Concordance"]
        AutoRAG["Auto-RAG Search Bridge"]
    end

    TargetURL --> Frontier
    SessionMode --> Frontier
    Frontier --> RateLimiter
    RateLimiter --> S1 & S2 & S3 & S4 & S5 & S6
    S1 & S2 & S3 & S4 & S5 & S6 --> Extractor
    Extractor --> Forensic
    Forensic --> Statutory
    Statutory --> Constitucion & CodCivil & CodPenal & PDFExtract
    Constitucion & CodCivil & CodPenal & PDFExtract --> VectorMatrix & HyperGraph & AutoRAG
```

---

## 8. Zero-Knowledge Privacy, PII Redaction & SOC 2 Cryptographic Ledger

```mermaid
graph TD
    InputText["Raw Document / Search Query"] --> Inspector["Privacy Compliance Inspector"]
    
    subgraph Inspection["Pattern Audit & Entity Identification"]
        PII1["Email Addresses (`RE_EMAIL`)"]
        PII2["Social Security Numbers (`RE_SSN`)"]
        PII3["Secret API Keys (`RE_API_KEY`)"]
        PII4["JWT Bearer Tokens (`RE_JWT`)"]
        PII5["Private Keys (`RE_PRIVATE_KEY`)"]
        PII6["HIPAA Medical Identifiers"]
    end

    Inspector --> Inspection

    Inspection --> Masking{"Violations Found?"}
    Masking -->|Yes| Redaction["Deterministic Cryptographic Redaction<br/>[REDACTED_EMAIL], [REDACTED_SSN], etc."]
    Masking -->|No| CleanPass["Pass Content Unchanged"]

    Redaction --> VaultIndex[("SQLite Knowledge Vault Indexer")]
    CleanPass --> VaultIndex

    VaultIndex --> MerkleGen["Merkle Tree Root SHA-256 Engine"]
    MerkleGen --> Cert["SOC 2 Type II Cryptographic Attestation"]
```

---

## 9. Resilient SQLite WAL & Self-Healing Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DatabaseBoot: FastAPI Server Startup
    
    state DatabaseBoot {
        VerifyHeader: Inspect SQLite DB Header
        CheckFTS5: Validate FTS5 Virtual Table Parity
        ThreadRegistry: Initialize Global _local_connections
    }

    VerifyHeader --> CorruptionDetected: Header Corrupted / Unreadable
    CorruptionDetected --> ColdRestore: Automatic Backup Cold-Restore & Rebuild
    ColdRestore --> CheckFTS5

    VerifyHeader --> NormalBoot: Header Valid
    NormalBoot --> CheckFTS5
    CheckFTS5 --> ThreadRegistry

    state Operation {
        WALMode: PRAGMA journal_mode=WAL
        BusyTimeout: PRAGMA busy_timeout=5000
        Synchronous: PRAGMA synchronous=NORMAL
    }

    ThreadRegistry --> Operation

    state SelfHealing {
        PruneOrphans: Delete Orphaned Chunk Records
        FixLinks: Reconcile Broken Wikilinks
        RebuildFTS: Rebuild Desynchronized Search Indexes
    }

    Operation --> SelfHealing: Triggered via /api/system/self-heal or CLI
    SelfHealing --> Operation

    state Teardown {
        CloseThreadLocal: Iterate _local_connections & Close Connections
        CheckpointWAL: PRAGMA wal_checkpoint(TRUNCATE)
        SafeRemoval: os.remove without WinError 32
    }

    Operation --> Teardown: Server Shutdown / Pytest Fixture Teardown
    Teardown --> [*]
```

---

## 10. Peer-to-Peer (P2P) Air-Gapped LAN Synchronization Protocol

```mermaid
sequenceDiagram
    autonumber
    participant NodeA as Node Alpha (Local Primary)
    participant Network as LAN Broadcast (UDP 8765)
    participant NodeB as Node Beta (Secondary Node)

    NodeA->>Network: UDP Beacon Announcement (NodeID, DB Revision, Merkle Root)
    NodeB->>Network: UDP Beacon Announcement (NodeID, DB Revision, Merkle Root)
    
    NodeA->>NodeB: TCP Connect (HTTP /api/p2p/handshake)
    NodeB-->>NodeA: Handshake Ack (Supported Versions, Capabilities)

    NodeA->>NodeB: GET /api/p2p/merkle-diff (Local Merkle Tree)
    NodeB->>NodeB: Calculate Set Difference (Missing Chunk Hashes)
    NodeB-->>NodeA: Delta Manifest (List of Missing Chunks & Embeddings)

    NodeA->>NodeB: POST /api/p2p/sync-payload (Compressed Chunk Stream)
    NodeB->>NodeB: Atomic SQLite Transaction (Insert Chunks & Vectors)
    NodeB->>NodeB: Recalculate Local Merkle Root
    NodeB-->>NodeA: Sync Acknowledged (100% Vector Parity Verified)
```

---

## 11. React 19 Frontend SPA Component & Telemetry Topology

```mermaid
graph TB
    subgraph FrontendSPA["React 19 SPA Frontend (Vite)"]
        App["App Root Container"]
        NavBar["Glassmorphic Navigation Bar"]
        
        subgraph Views["Active Studio Views"]
            V1["Dashboard & Health Metrics View"]
            V2["Interactive Chat Studio (Streaming LLM)"]
            V3["Workspace Document Manager"]
            V4["Knowledge Search & Filter Explorer"]
            V5["Document Ingestion & Dropzone Pipeline"]
            V6["2D/3D Knowledge Graph Visualizer"]
            V7["System Config & Orchestration Studio"]
            V8["Settings, Backups & Maintenance"]
            V9["Universal Crawler & Legal Studio"]
            V10["EPUB Reader & Document Studio"]
        end

        App --> NavBar
        NavBar --> Views
    end

    subgraph BackendAPI["FastAPI Backend (/api)"]
        R_Chat["/api/chat/*"]
        R_Search["/api/search/*"]
        R_File["/api/file/*"]
        R_Crawler["/api/crawler/*"]
        R_Graph["/api/graph/*"]
        R_System["/api/system/*"]
    end

    subgraph HardwareLocal["Local Hardware & Engine Layer"]
        OllamaLocal["Local Ollama Daemon (host.docker.internal:11434)"]
        SQLiteLocal[("SQLite ColBERT DB & FTS5 Index")]
    end

    V2 --> R_Chat
    V4 --> R_Search
    V3 & V5 --> R_File
    V9 --> R_Crawler
    V6 --> R_Graph
    V1 & V7 & V8 --> R_System

    BackendAPI --> HardwareLocal
```

---

## 12. Complete Visual Reference & Diagrams Guide
For the full standalone catalog of high-resolution diagrams, visit [`docs/system_architecture_diagrams.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/docs/system_architecture_diagrams.md).

