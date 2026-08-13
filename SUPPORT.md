# Uroboros Knowledge Engine Support Guide

Welcome to the **Uroboros Knowledge Engine (Neuro Alexander)** support guide. Whether you are running a local zero-cloud deployment, developing custom RAG pipelines, or troubleshooting hardware memory bounds, we are here to help.

---

## 1. Primary Support Channels

### 1.1 Project Documentation & SOTA Manual
Before seeking direct assistance, consult our exhaustive 32-section documentation manual:
- **[README.md](README.md)**: Architecture flowcharts, REST API specifications, domain module taxonomy, SQLite DDL schemas, CLI commands, and troubleshooting matrix.
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Coding standards, Ponytail principles, testing protocols, and PR checklist.
- **[SECURITY.md](SECURITY.md)**: Zero-cloud data sovereignty guarantee, PII scrubbing, ZK proofs, and vulnerability reporting.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**: Community standards, AI agent ethics, and enforcement guidelines.

### 1.2 GitHub Issues
- **Bug Reports**: Open a [Bug Report](https://github.com/SavianAlexander/uroboros-knowledge-engine/issues/new?template=bug_report.md) for reproducible errors, tracebacks, or hardware crashes.
- **Feature Requests**: Open a [Feature Request](https://github.com/SavianAlexander/uroboros-knowledge-engine/issues/new?template=feature_request.md) for architectural proposals or new domain module ideas.

### 1.3 Direct Maintainer & Task Master Support
- **Project Lead**: Savian Alexander
- **Email**: `savianalexander@pm.me`
- **Task Master Account**: `savianalexander@pm.me` (Task Master MCP Project #13 `Neuro Alexander`)

---

## 2. Common Troubleshooting Workflows

| Symptom / Error | Underlying Cause | Verified Resolution |
| :--- | :--- | :--- |
| `PermissionError: [WinError 32]` on database teardown | Active SQLite thread connections in Uvicorn background workers | Ensure test fixtures call `reset_db_connections()` in `src/infrastructure/database.py` before unlinking files. |
| `HTTP 500` / Connection Refused on `/api/rag/query` | Local Ollama service not running or missing GGUF weights | Verify Ollama is running (`curl http://127.0.0.1:11434`) and pull required models: `ollama pull nomic-embed-text` & `ollama pull qwen2.5:7b`. |
| Excessive RAM / VRAM consumption (> 6 GB) | Multiple duplicate `llama-server.exe` worker PIDs running concurrently | Run `ensure_single_llama_server_instance()` in `src/core/model_manager.py` or execute `taskkill /F /IM llama-server.exe` to reset memory bounds (~490 MB). |
| Vite / Tailwind build warnings in React SPA | Outdated node modules or missing production bundle | Run `cd frontend && npm install && npm run build` to update static assets in `src/assets/`. |
| SQLite FTS5 search query returns zero accent matches | Query string lacks diacritic normalization | Pass search queries through `unicodedata.normalize("NFC", query)` prior to tokenization. |

---

## 3. Diagnostic Commands

When requesting support, please include the output of these diagnostic commands:

```bash
# 1. System Health & Hardware Telemetry Probe
curl -X GET "http://127.0.0.1:8000/api/health"

# 2. Audit Clean Architecture Compliance
python scripts/architecture_cli.py audit .

# 3. Execute Domain Test Verification Suite
python run_domain_tests.py
```

---

## 4. Security Disclosures

For sensitive security disclosures or zero-day vulnerability reports, **do NOT open a public issue**. Follow our [Security Policy](SECURITY.md) and report findings directly to `savianalexander@pm.me`.
