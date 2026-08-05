# E2E Test Infra: Uroboros Knowledge Engine UI Redesign

## Test Philosophy
- Opaque-box, requirement-driven automated test suite verifying the Uroboros Knowledge Engine web UI redesign and backend API capabilities.
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Testing.
- Compliance: Dynamic OS Ephemeral Socket Binding, Bitwise SHA-256 Asset Parity, Headless Browser Protection, Explicit Numeric Parsing.

## Feature Inventory & Coverage Matrix

| # | View / Component | Feature Description | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Cross) | Tier 4 (Workload) |
|---|------------------|---------------------|:----------------:|:-----------------:|:--------------:|:-----------------:|
| 1 | View 1 (Dashboard) | Health Gauge & Telemetry (`/api/health`, `/api/stats`) | >=5 | ✓ | ✓ | ✓ |
| 2 | View 1 (Dashboard) | Storage Analytics & MIME Distribution (`/api/analytics/storage`) | >=5 | ✓ | ✓ | ✓ |
| 3 | View 1 (Dashboard) | Tag Co-occurrence Matrix (`/api/analytics/tags`) | >=5 | ✓ | ✓ | ✓ |
| 4 | View 1 (Dashboard) | Search Telemetry Sparkline (`/api/analytics/search-activity`) | >=5 | ✓ | ✓ | ✓ |
| 5 | View 1 (Dashboard) | Workspace Split-Screen & File Preview (`/api/file/tree`, `/api/file/raw`) | >=5 | ✓ | ✓ | ✓ (Scenario 1) |
| 6 | View 1 (Dashboard) | Document AI Insights (`/api/file/insights`) | >=5 | ✓ | ✓ | ✓ |
| 7 | View 1 (Dashboard) | Workflow Triggers & Webhook Logs (`/api/workflows/*`) | >=5 | ✓ | ✓ | ✓ |
| 8 | View 2 (Explorer) | File Drag & Drop Upload (`POST /api/upload`) | >=5 | ✓ | ✓ | ✓ |
| 9 | View 2 (Explorer) | Voice Memo Recorder & Transcriber (`/api/transcribe`) | >=5 | ✓ | ✓ | ✓ |
| 10 | View 2 (Explorer) | Autocomplete & Operator Validation (`/api/search/validate`) | >=5 | ✓ | ✓ | ✓ |
| 11 | View 2 (Explorer) | FTS5 Keyword vs BM25 Semantic Switcher (`/api/search`) | >=5 | ✓ | ✓ | ✓ |
| 12 | View 2 (Explorer) | Category Tabs & Sorting Controls | >=5 | ✓ | ✓ | ✓ |
| 13 | View 2 (Explorer) | CSV & PDF Export Generation (`/api/export`, `/api/report/export`) | >=5 | ✓ | ✓ | ✓ |
| 14 | View 2 (Explorer) | Bulk Delete Controller (`POST /api/bulk_delete`) | >=5 | ✓ | ✓ | ✓ |
| 15 | View 2 (Explorer) | Floating File Inspector & Notes/Tags (`/api/notes`, `/api/file/tag`) | >=5 | ✓ | ✓ | ✓ |
| 16 | View 3 (Graph) | Force-Directed Canvas Data (`/api/graph/data`) | >=5 | ✓ | ✓ | ✓ |
| 17 | View 3 (Graph) | Layout Presets (force, circular, grid, tree) & Minimap | >=5 | ✓ | ✓ | ✓ |
| 18 | View 3 (Graph) | Node Category & Search Filter | >=5 | ✓ | ✓ | ✓ |
| 19 | View 3 (Graph) | Wikilinks & Cluster Edges (`/api/graph/wikilinks`, `/api/graph/clusters`) | >=5 | ✓ | ✓ | ✓ |
| 20 | View 4 (AI Chat) | Chat Session Management (`/api/chat/sessions`) | >=5 | ✓ | ✓ | ✓ |
| 21 | View 4 (AI Chat) | GGUF Model Parameter Control (`temperature: 0.0`) | >=5 | ✓ | ✓ | ✓ |
| 22 | View 4 (AI Chat) | SSE Token Streaming (`POST /api/chat/stream`) | >=5 | ✓ | ✓ | ✓ |
| 23 | View 4 (AI Chat) | Grounded Citations Chips (Local & Web) | >=5 | ✓ | ✓ | ✓ |
| 24 | View 5 (Config) | Auto-Tag Rules Engine & Test Preview (`/api/rules`, `/api/rules/test-preview`)| >=5 | ✓ | ✓ | ✓ |
| 25 | View 5 (Config) | FTS Synonyms Manager (`/api/synonyms`) | >=5 | ✓ | ✓ | ✓ |
| 26 | View 5 (Config) | Macros & Tag Aliases Manager (`/api/macros`, `/api/aliases`) | >=5 | ✓ | ✓ | ✓ |
| 27 | View 5 (Config) | Local P2P LAN Sync Engine (`/api/sync/*`) | >=5 | ✓ | ✓ | ✓ (Scenario 2) |
| 28 | View 5 (Config) | Database Snapshot Vault (`/api/snapshots`, `/api/snapshots/restore`) | >=5 | ✓ | ✓ | ✓ (Scenario 3) |
| 29 | View 6 (Settings)| System Environment Table (`/api/system/env`) | >=5 | ✓ | ✓ | ✓ |
| 30 | View 6 (Settings)| Directory Re-index & Storage Guard (`/api/index`) | >=5 | ✓ | ✓ | ✓ |
| 31 | View 6 (Settings)| Dark/Light Glassmorphic Theme Toggle | >=5 | ✓ | ✓ | ✓ |
| 32 | View 6 (Settings)| Enterprise Profile & SOC 2 Badge | >=5 | ✓ | ✓ | ✓ |
| 33 | Command Palette | Keyboard Spotlight Modal (Ctrl+P / Cmd+P) & Navigation | >=5 | ✓ | ✓ | ✓ |
| 34 | System Infra | SHA-256 Bitwise Asset Parity (`index.html`, `style.css`, `app.js`) | >=5 | ✓ | ✓ | ✓ |

## Test Architecture & Runner Specification
- **Test Runner Script**: `run_e2e_ui_tests.py` (located at project root).
- **Execution Mechanism**:
  1. Spins up FastAPI test server bound to an OS ephemeral socket (`socket.bind(('127.0.0.1', 0))`).
  2. Executes health polling loop (`/api/health`) before starting test suites.
  3. Evaluates 4 distinct test modules:
     - `tests/test_e2e_t1_feature_coverage.py` (Tier 1: Feature & API Endpoints)
     - `tests/test_e2e_t2_boundary_corner.py` (Tier 2: 25-Angle Edge Case Matrix)
     - `tests/test_e2e_t3_cross_feature.py` (Tier 3: 5 Multi-System Interaction Chains)
     - `tests/test_e2e_t4_realworld_workloads.py` (Tier 4: 3 Real-World User Scenarios)
  4. Evaluates SHA-256 bitwise file parity between root `index.html`, `style.css`, `app.js` and `src/assets/`.
  5. Cleans up background test server and temporary test sandboxes cleanly.
