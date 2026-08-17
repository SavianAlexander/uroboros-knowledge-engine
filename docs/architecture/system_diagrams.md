# 📐 Uroboros Knowledge Engine & Neuro Co-Pilot Architecture Diagrams

**Generated**: `2026-08-16 20:17:05Z`  
**Standard**: Pure Mermaid JS diagrams rendered in GitHub Flavored Markdown.

---

## 1. Multi-Bridge Parallel Asynchronous Execution DAG

```mermaid
graph TD
    CLI["Unified Master CLI (neuro_cli.py)"] --> Bus["Contract Bus Orchestrator (contract_bus.py)"]

    subgraph Stage1 ["Stage 1: Concurrent Independent DAG Execution"]
        Arch["architecture_bridge"]
        Tududi["tududi_bridge"]
        Git["github_bridge"]
        Doctor["doctor_bridge"]
        Bench["benchmark_bridge"]
        Hygiene["process_hygiene_bridge"]
        VisualQA["visual_audit_bridge"]
        Nomen["nomenclature_bridge"]
        Alloc["file_allocation_bridge"]
        Review["review_bridge"]
        Blast["blast_radius_bridge"]
    end

    subgraph Stage2 ["Stage 2: Context-Informed Parallel Execution"]
        Snapshot["snapshot_bridge"]
        NeuroVault["neuro_bridge"]
        EVE["eve_bridge"]
        Fleet["fleet_watchdog_bridge"]
        Voice["voice_operator_bridge"]
        Release["release_bridge"]
    end

    subgraph Stage3 ["Stage 3: Cryptographic Ledger & Merkle Audit"]
        Ledger["docs/bridge_contracts/execution_ledger.json"]
        Cert["docs/certificates/release_certificate.md"]
    end

    Bus --> Stage1
    Stage1 --> Stage2
    Stage2 --> Stage3
```

---

## 2. SQLite Knowledge Engine Entity-Relationship (ER) Schema

```mermaid
erDiagram
    USERS {
        INTEGER id
        TEXT username
        TEXT password_hash
        TEXT role
    }
    FILE_CHUNKS {
        INTEGER id
        INTEGER file_id
        INTEGER chunk_index
        TEXT content
        TEXT embedding_json
        TEXT chunk_hash
    }
    VEC_FILE_CHUNKS_INFO {
        TEXT key
        ANY value
    }
    VEC_FILE_CHUNKS_CHUNKS {
        INTEGER chunk_id
        INTEGER size
        BLOB validity
        BLOB rowids
    }
    VEC_FILE_CHUNKS_ROWIDS {
        INTEGER rowid
        TEXT id
        INTEGER chunk_id
        INTEGER chunk_offset
    }
    VEC_FILE_CHUNKS_VECTOR_CHUNKS00 {
        TEXT rowid
        BLOB vectors
    }
    TF_IDF_INDEX {
        TEXT term
        INTEGER file_id
        INTEGER term_freq
    }
    FILES {
        INTEGER id
        INTEGER user_id
        TEXT filepath
        TEXT filename
        INTEGER file_size
        TEXT mime_type
        TEXT sha256
        REAL modified_at
    }
    TAGS {
        INTEGER file_id
        TEXT tag
    }
    AUTO_RULES {
        INTEGER id
        TEXT pattern
        TEXT tag
        INTEGER priority
    }
    FILE_REVISIONS {
        INTEGER id
        TEXT filepath
        TEXT content
        TEXT sha256
        TIMESTAMP saved_at
    }
    SYNC_PEERS {
        INTEGER id
        TEXT address
        TEXT name
    }
    OCR_COORDS {
        INTEGER file_id
        TEXT word
        REAL x
        REAL y
        REAL w
        REAL h
    }
    TAG_METADATA {
        TEXT tag
        TEXT color
    }
    QUERY_MACROS {
        TEXT name
        TEXT expansion
    }
```

---

*Diagrams generated automatically by `scripts/graph_bridge.py`.*
