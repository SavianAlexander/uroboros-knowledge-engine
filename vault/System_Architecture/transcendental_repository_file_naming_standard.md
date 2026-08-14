---
title: Transcendental Repository File Naming & Architectural Topology Standard
category: System Architecture
tags: [Standard, FileNaming, CleanArchitecture, Python, TestSuite, Scripts, Vault]
last_updated: 2026-08-14
---

# 📐 Transcendental Repository File Naming & Architecture Standard

This standard establishes the canonical directory structure and naming conventions across the entire Uroboros Knowledge Engine, Neuro Co-Pilot, and Antigravity tooling ecosystem.

---

## 🏛️ 1. Core Directives

1. **No Transient Phase Naming (`phaseXX`, `milestone_mX`, `sota_phaseX`)**: 
   - Files MUST NEVER be named after transient development phases, tickets, or iterations.
   - All modules, tests, scripts, and documentation MUST be named strictly after their **semantic capability and functional domain**.
2. **Deterministic `snake_case` for Python & Shell Scripts**:
   - All Python scripts and modules must use lowercase `snake_case` (e.g. `voice_audio_router.py`, `eve_market_arbitrage.py`).
3. **Structured Domain Prefixes for Tooling (`scripts/`)**:
   - `audit_*.py`: Static/dynamic security, code, and UI audit harnesses.
   - `verify_*.py`: Deterministic system verification and diagnostic suites.
   - `capture_*.py`: Automated screenshots, UX journeys, and showcase recorders.
   - `benchmark_*.py`: Performance benchmarking and latency testing.
   - `harvest_*.py` / `ingest_*.py`: Data pipeline and knowledge ingestion tools.
4. **Standard Test Topology (`tests/`)**:
   - Unit & Domain Tests: `tests/test_<domain>_<capability>.py` (e.g., `tests/test_domain_chat_intelligence.py`, `tests/test_voice_omniscient_matrix.py`).
   - E2E Tests: `tests/test_e2e_<scenario>.py`.
5. **Standard Source Architecture (`src/`)**:
   - `src/core/`: Domain-agnostic business logic, models, authentication, state, and voice DSP engines.
   - `src/infrastructure/`: Low-level database drivers, ESI adapters, SDE caches, and vector backends.
   - `src/domain/`: Pure domain algorithms, AST extractors, wikilink graphs, and RAG pipelines.
   - `src/app/routers/`: FastAPI endpoint route controllers.

---

## 📂 2. Directory Hierarchy Reference

```
UROBOROS-KNOWLEDGE-ENGINE/
├── .agents/                    # Agent specifications and skills
├── .github/workflows/          # CI/CD Matrix and GitHub Actions pipelines
├── docs/                       # Architectural documentation, diagrams, attestations
├── frontend/                   # Modern React / Vite frontend SPA
├── models/                     # Local ONNX & neural model weights
├── scripts/                    # CLI tooling & verification suites
│   ├── audit_*.py
│   ├── benchmark_*.py
│   ├── capture_*.py
│   ├── ingest_*.py
│   └── verify_*.py
├── src/                        # Core Python application packages
│   ├── app/routers/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   ├── antigravity_voice_mcp.py
│   └── mcp_server.py
├── tests/                      # Domain-allocated pytest suite
│   ├── test_domain_*.py
│   ├── test_e2e_*.py
│   └── test_*.py
└── vault/                      # Markdown knowledge database
    ├── DevOps/
    ├── Eve Online/
    └── System_Architecture/
```
