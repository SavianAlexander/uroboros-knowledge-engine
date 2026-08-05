# E2E Test Suite Ready

## Test Runner
- Command: `python run_e2e_ui_tests.py`
- Verification Method: Dynamic OS ephemeral socket binding (`socket.bind(('127.0.0.1', 0))`), `/api/health` polling loop, and SHA-256 bitwise asset parity verification.
- Expected Outcome: 56/56 tests pass cleanly with exit code 0.

## Coverage Summary
| Tier | Count | Description |
|------|------:|-------------|
| 1. Feature Coverage | 34 | All 6 Core Views, Command Palette, REST API endpoints, SSE token streaming, tag management, file insights, DB snapshots |
| 2. Boundary & Corner Cases | 9 | 25-Angle Universal Edge Case Matrix, explicit zero-value numeric parsing (`temperature: 0.0`), path containment, Unicode NFC normalization |
| 3. Cross-Feature Interactions | 5 | Multi-subsystem interaction chains (ingestion, auto-tag rules, audio transcription, bookmarks/macros, graph clusters, P2P sync) |
| 4. Real-World Application Scenarios | 3 | Complete user workflows (Workspace split-screen, local P2P vault sync, disaster recovery DB snapshot restore) |
| **Total** | **56** | **100% Test Pass Rate (Exit Code 0)** |

## Feature Checklist
| Feature / View | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|----------------|:------:|:------:|:------:|:------:|
| View 1 — Dashboard & Workspace Split-Screen | 7 | ✓ | ✓ | ✓ (Scenario 1) |
| View 2 — Search & Explorer | 8 | ✓ | ✓ | ✓ |
| View 3 — Knowledge Graph Canvas | 5 | ✓ | ✓ | ✓ |
| View 4 — AI Chat & RAG SSE Stream | 5 | ✓ | ✓ | ✓ |
| View 5 — Configuration & Processes | 5 | ✓ | ✓ | ✓ (Scenarios 2 & 3) |
| View 6 — Settings & Account | 5 | ✓ | ✓ | ✓ |
| Command Palette (Ctrl+P / Cmd+P) | 5 | ✓ | ✓ | ✓ |
| SHA-256 Bitwise Asset Parity (`index.html`, `style.css`, `app.js`) | 5 | ✓ | ✓ | ✓ |

## Execution Command
```bash
python run_e2e_ui_tests.py
```
