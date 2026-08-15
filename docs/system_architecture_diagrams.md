# Uroboros Knowledge Engine: Comprehensive System Architecture Diagrams

This document contains architectural diagrams rendered natively via GitHub Flavored Markdown (Mermaid.js), modeling the complete topology, asynchronous pipelines, data flows, and security controls across the **Uroboros Knowledge Engine (Neuro Alexander)**.

---

## Table of Contents
1. [Sovereign Tri-Engine Autonomous Orchestration](#1-sovereign-tri-engine-autonomous-orchestration)
2. [10-Bridge Neuro Co-Pilot Asynchronous DAG Pipeline](#2-10-bridge-neuro-co-pilot-asynchronous-dag-pipeline)
3. [Universal Crawler & Legal Intelligence Subsystem](#3-universal-crawler--legal-intelligence-subsystem)
4. [5-Pass Hybrid Retrieval Pipeline](#4-5-pass-hybrid-retrieval-pipeline)
5. [Zero-Knowledge Privacy, PII Redaction & SOC 2 Ledger](#5-zero-knowledge-privacy-pii-redaction--soc-2-ledger)
6. [Resilient SQLite WAL & Self-Healing Lifecycle](#6-resilient-sqlite-wal--self-healing-lifecycle)
7. [Peer-to-Peer LAN Mesh Knowledge Replication Protocol](#7-peer-to-peer-lan-mesh-knowledge-replication-protocol)
8. [React 19 Frontend SPA Component & Telemetry Topology](#8-react-19-frontend-spa-component--telemetry-topology)

---

## 1. Sovereign Tri-Engine Autonomous Orchestration

The Uroboros Knowledge Engine is powered by a synchronized Tri-Engine architecture binding local semantic intelligence, autonomous task management, and cryptographic source control:

```mermaid
graph TB
    subgraph Engine1["1. Neuro Knowledge Engine"]
        FTS5[("SQLite FTS5 Lexical Vault")]
        ColBERT["Binary ColBERT Vector Engine"]
        GraphDB["SQLite HyperGraph Engine"]
        Ollama["Local Ollama Neural Router"]
    end

    subgraph Engine2["2. Tududi Task Master"]
        TaskDB[("PostgreSQL / SQLite Task Store")]
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

## 2. 10-Bridge Neuro Co-Pilot Asynchronous DAG Pipeline

The Neuro Co-Pilot executes an asynchronous 3-stage dependency graph to validate code, contracts, visual assets, and system hygiene in parallel:

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

## 3. Universal Crawler & Legal Intelligence Subsystem

The Universal Crawler provides multi-session stealth crawling, legal document parsing, and automatic ingestion into the local knowledge vault:

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

## 4. 5-Pass Hybrid Retrieval Pipeline

The search engine executes a multi-pass retrieval pipeline combining lexical, probabilistic, vector, interaction, and graph ranking:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / API Client
    participant Router as Model Router & HyDE
    participant BM25 as Okapi BM25 Lexical Index
    participant ColBERT as Binary ColBERT Vector Vault
    participant Graph as HyperGraph Traversal
    participant RRF as Reciprocal Rank Fusion (RRF)
    participant Cross as Cross-Encoder MaxSim Reranker
    participant Synth as LLM Synthesis Stream

    User->>Router: Search Query / Question
    Router->>Router: Sub-50ms HyDE Query Expansion (qwen2.5:0.5b)
    
    par Multi-Channel Search
        Router->>BM25: Lexical Search (SQLite FTS5 + Unicode NFC)
        Router->>ColBERT: Dense Semantic Retrieval (Embedding Dot Product)
        Router->>Graph: Multi-Hop Entity & Wikilink Traversal
    end

    BM25-->>RRF: Ranked Lexical Candidates
    ColBERT-->>RRF: Ranked Vector Candidates
    Graph-->>RRF: Ranked Graph Candidates

    RRF->>RRF: Multi-Channel Reciprocal Rank Fusion
    RRF->>Cross: Top 50 Unified Candidates
    Cross->>Cross: MaxSim Interaction Scoring & Temporal Decay
    Cross-->>Synth: Top K Grounded Context Chunks
    Synth->>Synth: Grounded Citation Generation & Verification
    Synth-->>User: Streaming Response with Verified Citations
```

---

## 5. Zero-Knowledge Privacy, PII Redaction & SOC 2 Ledger

All incoming content is inspected and sanitized before indexing to guarantee zero privacy leakage:

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

## 6. Resilient SQLite WAL & Self-Healing Lifecycle

The database subsystem provides corruption detection, automatic schema self-healing, and thread-local connection lifecycle guarantees:

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

## 7. Peer-to-Peer LAN Mesh Knowledge Replication Protocol

Multiple local nodes synchronize knowledge vector deltas across local area networks without internet connectivity:

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

## 8. React 19 Frontend SPA Component & Telemetry Topology

The single-page web client provides responsive glassmorphic interfaces connected to local backend endpoints:

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
