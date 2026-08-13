# Security Policy & Vulnerability Disclosure

## 1. Security Overview & Air-Gapped Guarantee

**Uroboros Knowledge Engine (Neuro Alexander)** is engineered ground-up for strict enterprise data sovereignty, privacy protection, and zero-cloud execution. 

- **100% Zero-Cloud Execution**: All embeddings (Ollama / Nomic), vector indices (SQLite FTS5), document parsers, and LLM inference run strictly on local hardware. No user documents, text snippets, embeddings, or queries are ever transmitted over external networks or third-party cloud APIs.
- **Local Network Isolation**: Peer-to-peer (P2P) synchronization utilizes localized UDP Multicast (`5353`) and internal HTTP endpoints (`/api/sync/delta`), operating entirely within local subnet boundaries without external cloud bridges.

---

## 2. Supported Versions

Security updates and patches are actively applied to the following versions of Uroboros Knowledge Engine:

| Version | Supported | Security Patch Status |
| :--- | :--- | :--- |
| **v2.5.x (Master)** | :white_check_mark: **Yes** | Active security monitoring & continuous patch releases |
| **v2.0.x** | :white_check_mark: **Yes** | Critical security fixes only |
| **v1.x.x** | :x: No | End of Life (EOL) - Upgrade to v2.5+ recommended |

---

## 3. Reporting a Vulnerability

We take the security of Uroboros Knowledge Engine seriously. If you discover a security vulnerability, potential back-door, data leakage flaw, or permission bypass, please report it responsibly.

### Responsible Disclosure Protocol:
1. **Do NOT open a public GitHub issue** for undisclosed security vulnerabilities.
2. Email your findings directly to the Security Maintainer:
   - **Contact**: Savian Alexander
   - **Security Email**: `savianalexander@pm.me`
   - **Encrypted Transmission**: PGP Key / Signed Email available upon request.
3. Include the following details in your report:
   - Description of the vulnerability and potential impact.
   - Proof of Concept (PoC) script, HTTP request payload, or step-by-step reproduction steps.
   - Affected domain engine, router endpoint, or database table.
4. **Response SLA**: The maintainers will acknowledge receipt of your report within **24 hours** and provide a patch timeline within **72 hours**.

---

## 4. Automated Security Subsystems & Privacy Guards

Uroboros incorporates automated security & privacy engines operating inline during query resolution:

### 4.1 Automated PII Scrubbing (`src/domain/pii_privacy_guard.py`)
- Automatically redacts Social Security Numbers (SSNs), Credit Card numbers, API Keys, Passwords, and Email Addresses locally prior to prompt construction or LLM processing.

### 4.2 Zero-Knowledge Proof Verification (`src/domain/zk_data_masker.py`)
- Salt-hashed Zero-Knowledge proofs verify document payload authenticity without exposing raw plain text data to search indices.

### 4.3 Enterprise Access Control List (ACL) Trimming (`src/domain/acl_permission_engine.py`)
- Filters search candidate hits based on user identity, Active Directory roles (`read_roles`), and clearance levels (`acl_permissions = 'user:read'`).

### 4.4 Cryptographic Append-Only Audit Trail (`src/domain/crypto_audit_ledger.py`)
- Records SHA-256 hash-chained log entries in SQLite table `system_audit_ledger` for every administrative operation, document ingestion, and configuration change.

---

## 5. Hardware Memory Isolation & Denial-of-Service Protection

To prevent VRAM pagefile exhaustion, process hijacking, or denial-of-service (DoS) attacks on single-node hardware:

1. **Single-Instance LLM Process Lock**: `ensure_single_llama_server_instance()` in `src/core/model_manager.py` force-terminates duplicate `llama-server.exe` PIDs, keeping LLM memory footprint capped at ~490 MB.
2. **Semaphore Connection Caps**: `_llm_semaphore = 2` limits concurrent LLM inference streams, avoiding memory starvation.
3. **Database Timeout & Queue Bounding**: `SQLiteConnectionPool` caps active connections to `max_connections = 8` with a strict `DB_TIMEOUT = 30.0s`.

---

## 6. SOC 2 Type II Security Controls

Uroboros maintains compliance with formal SOC 2 Type II trust principles (Security, Confidentiality, Processing Integrity, Availability):

- **Audit Evidence & Attestation**: Documented in [`docs/soc2_type2_attestation.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/docs/soc2_type2_attestation.md).
- **Automated Ledger Generation**: Generated via `python scripts/update_test_ledger.py --soc2`.
