# Uroboros Knowledge Engine Feature Roadmap

This document outlines the strategic vision, planned engineering milestones, and feature roadmap for the **Uroboros Knowledge Engine (Neuro Alexander)**.

---

## 1. Release Timeline & Vision Overview

```
v3.3.0 (Current Stable) ──► v3.4.0 (Q3 2026) ──► v3.5.0 (Q4 2026) ──► v4.0.0 (2027)
  [Full-Duplex Voice]       [Louvain Graph 3D]      [Bulletproofs ZK]       [Distributed P2P Mesh]
  [4-Pillar Epistemic]      [Anki .apkg Export]     [Native ROCm GPU]       [Quantum Proof Ledger]
  [Streaming 20ms VAD]      [Multimodal Vision]     [Sub-1ms Swarm RAG]     [Global Air-Gapped Sync]
```

---

## 2. Near-Term Roadmap (v3.4.0 — Q3 2026)

### 2.1 GraphRAG 2-Hop Visualizer Enhancements
- **Interactive Node Clustering**: Expand 3D WebGL Graph (`react-force-graph-3d`) to render Louvain community cluster boundaries with dynamic color coding.
- **Wikilink Path Highlighting**: Highlight multi-hop shortest paths between target entity nodes in real time.

### 2.2 Direct Anki SRS Deck Exporter
- Export generated Anki flashcards (`POST /api/knowledge/generate-flashcards`) directly into `.apkg` files for native Anki Desktop & AnkiMobile import.

### 2.3 Local Multimodal Vision Integration
- Support local vision models (`llava:7b`, `qwen2-vl:7b`) via Ollama for automatic chart, diagram, and PDF OCR visual question answering.

---

## 3. Mid-Term Roadmap (v3.0.0 — Q4 2026)

### 3.1 Photonic Wave Interferometry Simulation Scorer
- Implement native C++ wave interference vector scoring in `src/domain/binary_colbert.py` for sub-femtosecond vector dot product simulation.

### 3.2 Native AMD ROCm 6.2 GPU Passthrough Engine
- Direct HIP runtime driver binding to eliminate sub-process latency overhead on AMD Radeon RX 7000 and Instinct GPUs.

### 3.3 Zero-Knowledge Encrypted Mesh Verification
- Extend `zk_data_masker.py` to support zero-knowledge range proofs (Bulletproofs) for verifying numeric document claims without revealing payload data.

---

## 4. Long-Term Vision (v3.5.0+ — 2027)

### 4.1 Distributed P2P Mesh Knowledge Swarm
- Multi-node UDP Multicast peer discovery with decentralized consensus for enterprise team knowledge synchronization across air-gapped LAN environments.

### 4.2 Sub-1ms Swarm RAG
- Distributed speculative context synthesis across local network peers with sub-millisecond Thompson Sampling routing.

---

## 5. Community RFC Process

Community members and maintainers can submit proposals for new roadmap items by opening an Issue using the [Feature Request Template](.github/issue_template/feature_request.md).
