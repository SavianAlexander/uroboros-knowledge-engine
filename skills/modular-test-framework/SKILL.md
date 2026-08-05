---
name: modular-test-framework
description: >
  Standardized protocol for converting monolithic test suites into domain-allocated,
  parallelized test modules with persistent JSON/Markdown/CSV audit log ledgers, SOC 2 Type II
  trust controls, mutation testing guards, visual coverage heatmaps, and 25-angle edge case matrix coverage.
---

# Modular Domain-Allocated Test Framework & SOC 2 Audit Protocol (Master Test Skill)

Use this skill whenever building, restructuring, or auditing software testing pipelines to ensure fast, isolated, multi-domain test execution with transparent audit ledgers, coverage heatmaps, mutation guards, and SOC 2 Type II compliance.

---

## 1. Domain Allocation Architecture (11 Test Modules)

Partition test logic into discrete, domain-specific modules with isolated temporary sandbox directories (`tempfile.mkdtemp()`):

```text
tests/
  ├── test_domain_db.py            # Domain 1: Database Kernel, WAL mode, PRAGMA MMap, Porter Stemmer
  ├── test_domain_vector.py        # Domain 2: Inverted Index Posting Lists, TF-IDF, RRF Rank Fusion
  ├── test_domain_ingestion.py     # Domain 3: File extractions (PDF/DOCX/OCR), 50MB RAM guards, Auto-Tagging
  ├── test_domain_api.py           # Domain 4: REST Endpoints, GZip Middleware, SSE Token Streaming
  ├── test_domain_llm.py           # Domain 5: GPU Offloading, KV-Cache, Thread Lock Safety
  ├── test_domain_security.py      # Domain 6: Input Query Sanitization, Path Traversal Containment, UTF-8
  ├── test_domain_performance.py   # Domain 7: Sub-5ms Database & FTS Search Latency Guards
  ├── test_domain_architecture.py  # Domain 8: Programmatic 100.0% Clean Architecture Score Guard
  ├── test_domain_chaos.py         # Domain 9: Corrupt Binary Payloads, Read Lock Recovery, Multi-Thread Race
  ├── test_domain_soc2.py          # Domain 10: Zero Secret Leakage, SHA-256 Integrity, File ACL Permissions
  ├── test_domain_mutation.py      # Domain 11: Programmatic Fault Mutation Invalidation Guards
  ├── test_audit_ledger.json       # Machine-readable persistent JSON audit ledger
  ├── test_audit_ledger.csv        # Spreadsheet CSV export report
  └── test_results.xml             # JUnit XML CI/CD export report
```

---

## 2. Sandbox Allocation Standard (`setUp` / `tearDown`)

Every domain test module MUST allocate its own independent temporary directory in `setUp` and clean it up in `tearDown`:

```python
class TestDomainModule(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_name_")
        know.DB_FILE = os.path.join(self.test_dir, "test.db")
        know.reset_db_connections()
        know.init_db()

    def tearDown(self):
        know.reset_db_connections()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
```

---

## 3. The 25-Angle Edge Case Test Matrix Checklist

1. **Unbalanced Quotes**: String inputs with unclosed single/double quotes.
2. **Control Byte Safety**: Null byte (`\x00`) and escape sequence injection.
3. **50MB File Limits**: File size guard enforcement on giant files.
4. **0-Byte Extractions**: Empty files return valid structure without crashing.
5. **Path Traversal Escape**: Directory traversal attempts (`../../secret.txt`).
6. **Concurrent DB WAL Locks**: Multi-thread database write contention.
7. **Double-Close Safety**: Idempotent connection close handling.
8. **60-Second Timeout Guards**: Connection timeout parameters.
9. **Atomic Snapshots**: Snapshot backups during active read transactions.
10. **Multibyte UTF-8**: Non-ASCII unicode text tokenization and indexing.
11. **Sub-Millisecond Pool Resets**: Connection pool recycling speed.
12. **Missing HTTP Fields**: 422 HTTP validation errors on missing payload keys.
13. **GZip Stream Integrity**: HTTP payload compression headers.
14. **FTS Operator Injection**: Raw `MATCH` injection query resilience.
15. **Rapid Save Sync**: Live file updates refreshing search indexes instantly.
16. **Zero Match Fallbacks**: Vector queries with non-existent terms returning empty lists.
17. **Empty String Inputs**: Whitespace-only query handling.
18. **Matrix Version Invalidation**: DB version increments invalidating vector caches.
19. **Microsecond MTime**: MTime resolution on rapid file overwrites.
20. **Unicode Whitespace**: Zero-width space and non-breaking space tokenization.
21. **LLM CPU Fallback**: Non-crashing fallback when GPU initialization fails.
22. **Lock Concurrency**: Multithreaded lock safety on global model locks.
23. **HyDE Expansion**: Query expansion fallback on zero retriever hits.
24. **DOM Fragment Rendering**: UI node batching rendering stability.
25. **Audio Metadata Parsing**: Fallback handling for corrupt audio headers.

---

## 4. Bug Relation & Defect Prevention Taxonomy

Assign every test method to a guarded component and failure mode across 8 categories:

```python
BUG_RELATION_TAXONOMY = {
    "Concurrency & Lock Contention": [
        {"test": "test_05_angle_timeout_60s_guard", "component": "know.py:L52", "prevents": "database is locked errors"}
    ],
    "Memory Leaks & OOM Spikes": [
        {"test": "test_04_angle_50mb_size_limit_guard", "component": "know.py:L604", "prevents": "Host RAM exhaustion"}
    ],
    "Security & Path Traversal": [
        {"test": "test_02_path_traversal_containment", "component": "main.py:L446", "prevents": "Directory traversal escape"}
    ],
    "SOC 2 Type II Security & Trust Controls": [
        {"test": "test_01_soc2_security_zero_secret_leakage", "component": "repository", "prevents": "Plaintext secret leaks"}
    ],
    "Performance & Architecture Guards": [
        {"test": "test_01_db_read_latency_guard", "component": "know.py:L45", "prevents": "Database read latency exceeding 5.0ms"}
    ],
    "Mutation & Code Resiliency": [
        {"test": "test_01_mutation_caught_corrupted_fts_query", "component": "main.py:L3004", "prevents": "Unsanitized operator mutations"}
    ]
}
```

---

## 5. SOC 2 Type II Trust Services Criteria (TSC) Test Protocol

Enforce test coverage across all 5 Trust Services Criteria:

1. **Security (CC6.1 - CC6.8)**: Zero secret leakage test, path containment test, FTS query sanitization test.
2. **Availability (A1.1 - A1.3)**: 50MB RAM guard test, 60s lock timeout test, GPU failover recovery test.
3. **Processing Integrity (PI1.1 - PI1.5)**: SHA-256 checksum verification test, atomic database snapshot test.
4. **Confidentiality (C1.1 - C1.2)**: File ACL permissions metadata tracking test.
5. **Privacy (P1.1 - P8.1)**: User memory deletion lifecycle test, non-ASCII control char sanitization test.

---

## 6. Auto-Healing, Chaos & Coverage Heatmap Suite

- **Coverage Heatmap Generator (`scripts/generate_coverage_heatmap.py`)**: Renders visual density bars per file in `docs/test_coverage_heatmap.html`.
- **Auto-Healing Engine (`scripts/auto_heal_tests.py`)**: Detects and repairs database schema drift, missing virtual tables, or missing composite indexes.
- **Chaos Profiler (`scripts/stress_test_domain.py`)**: Verifies 0 race conditions, zero memory leaks, and 100% deterministic test pass stability.

---

## 7. Multi-Format Audit Ledger & Dashboard Suite

Automated scripts generate:
- **JSON Ledger**: `tests/test_audit_ledger.json`
- **CSV Export**: `tests/test_audit_ledger.csv`
- **JUnit XML**: `tests/test_results.xml`
- **Markdown Ledger**: `docs/test_audit_ledger.md`
- **SOC 2 Attestation**: `docs/soc2_type2_attestation.md`
- **HTML Visual Dashboard**: `docs/test_audit_dashboard.html`
- **HTML Coverage Heatmap**: `docs/test_coverage_heatmap.html`
- **Terminal TUI Dashboard**: `scripts/tui_audit_dashboard.py`

---

## 8. Test Execution Commands

```bash
# 1. Full 11-Domain Audit & Ledger Update
python scripts/update_test_ledger.py

# 2. Incremental Fast Target Mode (100ms)
python run_domain_tests.py --fast

# 3. Terminal TUI Visual Dashboard
python scripts/tui_audit_dashboard.py

# 4. Coverage Heatmap Generator
python scripts/generate_coverage_heatmap.py

# 5. Chaos & Flaky Test Profiler
python scripts/stress_test_domain.py

# 6. Auto-Healing Audit Engine
python scripts/auto_heal_tests.py

# 7. SOC 2 Type II Compliance Reporter
python scripts/soc2_audit_reporter.py
```
