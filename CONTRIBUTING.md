# Contributing to Uroboros Knowledge Engine

Thank you for your interest in contributing to **Uroboros Knowledge Engine (Neuro Alexander)**! This document provides detailed guidelines for human developers and autonomous AI agents submitting code, documentation, bug fixes, or performance enhancements.

---

## 1. Core Engineering Principles (Ponytail)

Uroboros follows the **Ponytail (lazy developer)** engineering philosophy. Lazy means **efficient**, not careless:

1. **YAGNI (You Aren't Gonna Need It)**: Never build speculative abstractions, unused parameters, or boilerplate nobody requested.
2. **Standard Library First**: Utilize standard library capabilities before introducing third-party dependencies.
3. **Shortest Working Diff Wins**: The smallest change that solves the root cause is superior to monolithic refactorings.
4. **Fix Root Causes, Not Symptoms**: Trace failures back to the source function rather than swallowing exceptions or returning dummy fallbacks.
5. **Deconstruction over Addition**: Deletion of bloated code is prioritized over line additions.

---

## 2. Codebase Architecture & Layer Boundaries

All code contributions must respect the clean architecture layer boundaries:

```
src/
├── app/          # FastAPI routers & HTTP request handling (Imports domain & infrastructure)
├── core/         # System configuration, auth JWT, & model manager (Shared runtime services)
├── domain/       # 135 pure domain intelligence & RAG algorithms (Zero I/O dependencies)
└── infrastructure/ # SQLite connection pool, document parsers, P2P sync, & OS watchers
```

### Layer Dependency Rules:
- Modules in `src/domain/` MUST NOT import from `src/app/` or `src/infrastructure/`.
- All database operations MUST use the centralized thread-local connection pool in [`src/infrastructure/database.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/database.py).
- Verify layer compliance before opening a PR:
  ```bash
  python scripts/architecture_cli.py audit .
  ```

---

## 3. Commit Message & Naming Conventions

All commit messages must adhere to the **Enterprise Naming & Terminology Guard**:

> [!IMPORTANT]
> Never use informal, hype-y, or marketing adjectives (such as "Super", "Magic", "Ultra") in commit messages, pull requests, or code comments. Always use executive technical terms (e.g., "Mechanical RAG Enhancements", "Probabilistic & Syntactic Optimizations").

### Standard Commit Syntax:
- `feat(component)`: New feature or domain module implementation.
- `fix(component)`: Bug fix resolving root cause.
- `docs(component)`: Technical documentation updates or sitemap additions.
- `test(component)`: Unit, integration, or fuzzing test suite additions.
- `refactor(component)`: Structural code simplification without changing external contracts.
- `perf(component)`: Memory footprint or latency optimization.

*Example*: `feat(domain): integrate Matryoshka vector compression and ColBERT MaxSim reranker`

---

## 4. Local Development & Setup

### 4.1 Prerequisites
- **Python 3.12+**
- **Node.js 20+** & **npm 10+** (for frontend development)
- **Ollama** running locally on `http://127.0.0.1:11434` (`nomic-embed-text` & `qwen2.5:7b` models pulled)

### 4.2 Installation Commands
```bash
# 1. Clone repository
git clone https://github.com/SavianAlexander/uroboros-knowledge-engine.git
cd "uroboros-knowledge-engine"

# 2. Install backend Python dependencies
pip install -r requirements.txt

# 3. Build frontend SPA assets
cd frontend
npm install
npm run build
cd ..

# 4. Initialize SQLite database & FTS5 virtual tables
python know.py init
```

---

## 5. Testing & Quality Assurance Protocols

Contributions will only be merged if all verification suites pass with **0 failures**:

```bash
# Run fast domain test suite
python -m pytest tests/test_domain_vector.py -v

# Run full project test suite across all 98 test files
python -m pytest tests/

# Run master domain test runner (244 passed)
python run_domain_tests.py
```

### 5.1 Mandatory Test Engineering Rules:
1. **Dynamic Ephemeral Socket Binding**: When spawning HTTP test servers for Playwright or E2E suites, bind dynamically to an OS ephemeral port (`socket.bind(('127.0.0.1', 0))`) to prevent port collision errors during parallel execution.
2. **Thread Connection Teardown (`WinError 32`)**: On Windows, Uvicorn background threads keep thread-local SQLite connections open. Test fixtures MUST invoke `reset_db_connections()` in [`database.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/database.py) before removing database files (`.db-shm`, `.db-wal`).
3. **No Test Deletion**: Never delete or comment out failing unit tests to pass CI. Resolve the underlying contract breakage.

---

## 6. Task Master Orchestration Rules (Tududi)

All multi-step engineering tasks, checklists, and agentic workflows MUST use the **Task Master (Tududi)** integration:

1. **No Markdown Checklists**: Never create local `task.md` files for task planning.
2. **MCP Tool Usage**: Invoke Tududi MCP tools (`create_task`, `add_subtask`, `update_task`, `complete_task`) under Project #13 (`Neuro Alexander`).
3. **Tagging**: Ensure all created tasks include tag `Antigravity` and sync automatically to `savianalexander@pm.me`.

---

## 7. Submitting a Pull Request (PR)

1. Create a descriptive feature branch (`git checkout -b feat/vector-mrl-compression`).
2. Ensure `python scripts/architecture_cli.py audit .` passes clean.
3. Update SOC 2 test ledgers:
   ```bash
   python scripts/update_test_ledger.py --soc2
   ```
4. Commit your changes with executive technical terminology.
5. Push to your fork and submit a Pull Request targeting `master`.

---

## 8. Pull Request Review Matrix & Verification Checklist

Reviewers and automated CI pipelines evaluate PRs against this verification matrix:

- [ ] **Clean Layer Separation**: No `src/domain/` module imports FastAPI, HTTP engines, or infrastructure databases.
- [ ] **Thread Connection Reset**: Database test fixtures call `reset_db_connections()` before database teardown.
- [ ] **Memory & Resource Bound**: Single-instance process limit is maintained (`OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`).
- [ ] **PII & ZK Data Integrity**: Sensitive strings are passed through [`pii_privacy_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/pii_privacy_guard.py).
- [ ] **Zero Redundant Dependencies**: No new external PyPI packages are added unless explicitly approved by project leads.
- [ ] **SOC 2 Audit Ledger Sync**: `docs/soc2_type2_attestation.md` is updated via `scripts/update_test_ledger.py`.

---

## 9. Performance Benchmark SLA Verification

Before merging pull requests that modify search, vector retrieval, or indexing pipelines, developers must run the benchmark suite to verify sub-5ms SLA compliance:

```bash
# Benchmark retrieval latency across 100 queries
python scripts/benchmark_engine.py --runs 100
```

- **Target SLA**: $P_{50} < 5.0\text{ ms}$, $P_{99} < 15.0\text{ ms}$.

---

## 10. Security Vulnerability Disclosure & Dependency Audit

- **Vulnerability Patching**: Prefer updating package resolutions or overrides over forcing incompatible major upgrades that break clean installs (`npm ci`).
- **Headless Browser Protections**: Wrap browser hardware API promises in a 100ms `Promise.race` timeout to prevent CI deadlocks.
- **Reporting Vulnerabilities**: Send security disclosures directly to `savianalexander@pm.me`.

---

## 11. Code of Conduct

All contributors are expected to adhere to the project [Code of Conduct](CODE_OF_CONDUCT.md).
