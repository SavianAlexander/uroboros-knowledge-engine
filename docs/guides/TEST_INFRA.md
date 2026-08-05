# E2E Test Infra: Uroboros Knowledge Engine

## Test Philosophy

The Uroboros Knowledge Engine test infrastructure enforces a **Dual-Track Quality Framework** combining deterministic micro-unit isolation, high-throughput integration API verification, Playwright end-to-end browser automation, and stress-tested real-world scenario validation.

### Core Testing Principles

1. **Requirement-Driven & Spec-Anchored**: Every test case directly traces back to functional requirements (R1: Document Intelligence & Analytics Panel, R2: Interactive Knowledge Graph & Wikilink Visualization, R3: Automated Workflow Triggers & Webhook Engine) and system acceptance criteria.
2. **Authoritative Expected Output Derivation**: Expected outputs are derived strictly from formal system specs, mathematical invariants, boundary definitions, or reference oracle execution (stdout/stderr, exact HTTP response schemas, SQLite state checksums).
3. **Progressive Testability & Isolation**: Tests operate in isolated sandbox environments (`tempfile.mkdtemp()`) with dedicated SQLite WAL database instances. No test relies on preceding test execution order, persistent ambient state, or network dependencies.
4. **Ponytail Minimalist Efficiency & Zero Flakiness**: Tests avoid unnecessary framework overhead, poll loops, or arbitrary sleep delays. UI automation relies on deterministic health-polling, explicit element selectors (`#results-list .result-item`), and canvas dirty-flag state verification.
5. **Adversarial & Edge-Case Rigor**: Every module undergoes 25-angle edge-case verification covering Unicode NFC normalization, control characters, path traversal containment, zero-byte extractions, concurrency write-locks under SQLite WAL, and malformed webhook payloads.

---

## Feature Inventory

The test architecture covers three primary feature domains introduced in the Document Intelligence & Analytics Dashboard upgrade (§ 2026-08-04T00:14:37Z):

| Module ID | Feature Description | Core Components & Endpoints | Target SLA / Constraints |
|---|---|---|---|
| **FEAT-R1** | **Document Intelligence & Analytics Panel** | - `GET /api/analytics/summary`<br>- `GET /api/analytics/storage`<br>- `GET /api/analytics/tags`<br>- `GET /api/analytics/search-activity`<br>- UI Widget: High-density stats ribbon & MIME charts | - Sub-5ms endpoint response latency<br>- Real-time cache invalidation on file ingest/edit<br>- Top 5 MIME types + "Other" bundling |
| **FEAT-R2** | **Interactive Knowledge Graph & Wikilink Visualizer** | - `GET /api/graph/nodes`<br>- `GET /api/graph/edges`<br>- `GET /api/graph/wikilinks`<br>- `GET /api/graph/clusters`<br>- Canvas graph renderer with `needsRedraw` dirty-flag | - 1,000-node smooth canvas rendering benchmark (<16.6ms frame time / 60 FPS)<br>- Bidirectional `[[wikilink]]` parsing<br>- Community clustering by tag affinity |
| **FEAT-R3** | **Automated Workflow Triggers & Webhook Engine** | - `POST /api/workflows/rules`<br>- `GET /api/workflows/triggers`<br>- `POST /api/workflows/test-fire`<br>- Asynchronous Event Bus & HTTP Webhook Dispatcher | - HMAC SHA-256 payload signature verification<br>- Exponential backoff retries (1s, 2s, 4s)<br>- Zero-event loss under 100 concurrent triggers |

---

## Test Architecture

The testing suite is structured into four progressive validation tiers:

```text
+-----------------------------------------------------------------------------------+
|                        Tier 4: Real-World Application Scenarios                  |
|          Multi-Step Ingestion Pipelines, 1,000-Node Stress, Webhook Bursts          |
+-----------------------------------------------------------------------------------+
                                          ^
                                          |
+-----------------------------------------------------------------------------------+
|                      Tier 3: Macro-System & UI Browser Automation                |
|           Playwright E2E Scenarios, 60 FPS Canvas Benchmark, Inspector Drawer     |
+-----------------------------------------------------------------------------------+
                                          ^
                                          |
+-----------------------------------------------------------------------------------+
|                      Tier 2: Micro-Integration & API Pipeline Tests              |
|        FastAPI Routers, SQLite WAL Triggers, Async Event Bus, Webhook Dispatch    |
+-----------------------------------------------------------------------------------+
                                          ^
                                          |
+-----------------------------------------------------------------------------------+
|                     Tier 1: Micro-Unit & Component Isolation Tests                |
|      Wikilink Regex Parser, BVA Storage Metrics, HMAC Signatures, Rule Evaluator  |
+-----------------------------------------------------------------------------------+
```

---

### Tier 1: Micro-Unit & Component Isolation Tests

Tier 1 focuses on isolated function logic, mathematical boundary values, regex parsing, and payload formatters without requiring live network or full server initialization.

| Test ID | Test Name & Target Component | Methodology | Test Input Vector / Scenario | Authoritative Expected Output | Assertion Criteria |
|---|---|---|---|---|---|
| **T1.01** | `test_analytics_metrics_calculator_unit`<br>`src/domain/analytics.py` | Category-Partition | Input array of 50 mock document metadata dictionaries with varied MIME types and sizes. | Summary dictionary: `total_docs=50`, `total_bytes=10485760`, `mime_distribution={'pdf': 20, 'text': 15, 'code': 10, 'other': 5}`. | Exact dictionary match; keys exist; non-negative numbers. |
| **T1.02** | `test_analytics_storage_usage_bva`<br>`src/domain/analytics.py` | Boundary Value Analysis (BVA) | Boundary values for byte sizes: `0`, `1`, `1048576` (1MB), `52428800` (50MB limit), `2147483648` (2GB). | Correctly formatted human-readable strings (`"0 B"`, `"1 B"`, `"1.00 MB"`, `"50.00 MB"`, `"2.00 GB"`). | String equality; zero division exception guard verified. |
| **T1.03** | `test_wikilink_parser_regex_isolation`<br>`src/domain/parser.py` | Category-Partition & Boundary | Markdown text strings: `[[StandardLink]]`, `[[Target|Custom Label]]`, `[[unclosed_link`, `[[nested[[link]]`, `[[link_with_#anchor]]`. | Extracted target set: `['StandardLink', 'Target', 'link_with_#anchor']`. Unclosed and malformed brackets safely ignored. | Match count matches oracle array; unclosed brackets raise no exceptions. |
| **T1.04** | `test_graph_adjacency_matrix_builder`<br>`src/domain/graph.py` | Pairwise Combinatorial | Nodes `N={A,B,C}` with edges: direct link `A->B`, wikilink `B->C`, shared tag `[A,C]`. | Adjacency matrix: weight `A-B=1.0`, `B-C=1.0`, `A-C=0.5`. Symmetry verified for undirected projection. | Graph node array length = 3; edge count = 3; weights match expected floating point values. |
| **T1.05** | `test_graph_cluster_algorithm_partition`<br>`src/domain/graph.py` | Category-Partition | Disjoint 10-node graph with 2 distinct dense tag clusters (`cluster_ai`, `cluster_db`). | Modularity matrix partitioning yielding `cluster_id=0` for nodes 1-5 and `cluster_id=1` for nodes 6-10. | High modularity score (>0.4); zero orphaned nodes. |
| **T1.06** | `test_workflow_rule_evaluator_unit`<br>`src/domain/workflows.py` | Decision Table | Condition combinations: `tag=='confidential'` (True/False), `semantic_score>=0.85` (True/False), Operator (`AND`/`OR`). | Evaluates rule execution boolean match matrix with 100% truth table fidelity. | Boolean evaluation result equals expected truth table cell. |
| **T1.07** | `test_webhook_payload_formatter`<br>`src/domain/webhooks.py` | SOC 2 Security & Format | Event `document_ingested`, payload `{id: 42, title: "report.pdf"}`, secret `"sec_key_123"`. | Formatted JSON body + `X-Uroboros-Signature` header equal to `sha256=HMAC_SHA256(secret, body)`. | Signature header format valid; signature re-computation matches. |
| **T1.08** | `test_workflow_trigger_confidence_bva`<br>`src/domain/workflows.py` | Boundary Value Analysis (BVA) | Semantic similarity scores at boundaries: `0.00`, `0.8499` (below threshold), `0.8500` (at threshold), `1.0000`. | Rule fires ONLY for `0.8500` and `1.0000`; suppressed for `0.00` and `0.8499`. | Precise boundary trigger boolean verification. |
| **T1.09** | `test_wikilink_unresolved_target_handling`<br>`src/domain/parser.py` | Error & Ghost Handling | Markdown containing `[[NonExistentDocument]]` wikilink reference. | Node created with status attribute `is_unresolved=True` / `ghost_node=True`. Graph rendering remains stable. | Edge points to ghost node ID; no 404 database error thrown. |
| **T1.10** | `test_analytics_search_activity_ring_buffer`<br>`src/domain/analytics.py` | Real-Time Time-Series | Stream of 100 search query timestamps pushed into 60-second sliding window ring buffer. | Time-series bucket histogram aggregated into 1-second interval slots totaling 100 queries. | Ring buffer length capped at max capacity; oldest entries cleanly evicted. |
| **T1.11** | `test_webhook_retry_backoff_calculator`<br>`src/domain/webhooks.py` | BVA & Algorithmic | Retry iteration indices `attempt in [1, 2, 3, 4]`, base delay 1.0s, max 8.0s. | Delay array: `[1.0, 2.0, 4.0, 8.0]`. Attempt 5 raises `MaxRetriesExceeded`. | Calculated delays match geometric series $2^{(n-1)}$ capped at 8.0s. |
| **T1.12** | `test_graph_dirty_flag_state_manager`<br>`src/domain/graph.py` | State Machine | State mutations: `set_nodes()` -> `needsRedraw=true`, `pan_zoom()` -> `needsRedraw=true`, `render_frame()` -> `needsRedraw=false`. | Dirty flag state transition sequence: `[True, True, False]`. Idle state preserves `False`. | `needsRedraw` boolean matches expected state cycle. |

---

### Tier 2: Micro-Integration & API Pipeline Tests

Tier 2 verifies FastAPI router endpoints, SQLite database state persistence, asynchronous event bus handling, and live webhook dispatches.

| Test ID | Test Name & Target Component | Methodology | Test Input Vector / Scenario | Authoritative Expected Output | Assertion Criteria |
|---|---|---|---|---|---|
| **T2.01** | `test_analytics_endpoints_response_structure`<br>`/api/analytics/summary` | Interface Contract | `GET /api/analytics/summary` HTTP request on populated test database. | HTTP 200 OK, JSON containing `total_documents`, `total_storage_bytes`, `mime_distribution`, `top_tags`. | Response conforms to Pydantic `AnalyticsSummaryResponse` schema. |
| **T2.02** | `test_analytics_tag_distribution_cache_invalidation`<br>`/api/analytics/tags` | Cache Invalidation | 1. `GET /api/analytics/tags`<br>2. `POST /api/tags/assign` (Add tag `"finance"`) | Initial cache returned; second call reflects `"finance"` count incremented by 1 within <5ms. | Tag count updated instantly; cache generation timestamp refreshed. |
| **T2.03** | `test_graph_nodes_edges_api_query`<br>`/api/graph/data` | Endpoint Contract | `GET /api/graph/data` on database with 10 documents and 15 linkages. | HTTP 200 OK, JSON object with `nodes` (list of 10 objects) and `edges` (list of 15 link objects). | `len(nodes) == 10`; `len(edges) == 15`; edge target/source IDs match valid node IDs. |
| **T2.04** | `test_graph_wikilinks_extraction_on_ingest`<br>`/api/files/ingest` | Ingestion Integration | Ingest Markdown file `DocA.md` containing `[[DocB.md]]`. | Endpoint processes file, populates database, and inserts edge `DocA -> DocB` into `document_links` table. | Querying SQLite `document_links` returns relationship `(DocA_id, DocB_id, 'wikilink')`. |
| **T2.05** | `test_graph_cluster_filter_api`<br>`/api/graph/data?tag=ai` | Query Parameter Filter | `GET /api/graph/data?tag=ai&min_weight=2.0` on multi-tag dataset. | HTTP 200 OK, returning subgraph filtered strictly to nodes possessing tag `"ai"` and edges $\ge 2.0$. | All returned nodes contain `"ai"` tag; edge weights $\ge 2.0$. |
| **T2.06** | `test_workflow_rules_crud_api`<br>`/api/workflows/rules` | CRUD Integration | 1. `POST /api/workflows/rules` (Create)<br>2. `GET`<br>3. `PUT` (Update)<br>4. `DELETE` | Full HTTP CRUD sequence lifecycle returning 201 Created, 200 OK, 200 OK, 204 No Content. | Database record persists on creation, updates on PUT, disappears on DELETE. |
| **T2.07** | `test_workflow_trigger_on_document_ingestion`<br>`/api/files/ingest` | Event Bus Integration | Configure rule: On `document_ingested` with tag `"urgent"`, fire webhook. Ingest `"urgent"` document. | Event bus captures event, matches trigger rule, enqueues workflow task for execution. | Workflow execution log created in `workflow_logs` table with status `"success"`. |
| **T2.08** | `test_workflow_webhook_dispatch_success`<br>`src/services/webhook_service.py` | Integration & Network Mock | Trigger workflow targeting local HTTP mock server listening on `http://127.0.0.1:8099/webhook`. | Mock server receives HTTP POST with JSON payload and valid `X-Uroboros-Signature`. | Mock server receives payload within 100ms; HTTP 200 response logged. |
| **T2.09** | `test_workflow_webhook_http_error_retry`<br>`src/services/webhook_service.py` | Fault Recovery Integration | Target mock webhook endpoint configured to return HTTP 500 Internal Server Error 2 times, then 200 OK. | Engine captures 500 error, waits backoff interval, retries, and succeeds on 3rd attempt. | `workflow_logs` contains 2 attempt entries marked `"retrying"` and 1 final `"completed"`. |
| **T2.10** | `test_analytics_search_activity_logger_integration`<br>`/api/search` | Cross-Router Integration | Execute 5 search queries via `GET /api/search?q=test`. | `/api/analytics/search-activity` reflects 5 query events logged with timestamps and hit counts. | Activity log count increases by 5; recent query terms match `"test"`. |
| **T2.11** | `test_wikilink_bidirectional_graph_edges`<br>`/api/graph/data` | Edge Case Integration | Ingest `DocA.md` containing `[[DocB]]` and `DocB.md` containing `[[DocA]]`. | Graph API outputs two distinct directed edge records or one consolidated undirected edge with weight 2.0. | Subgraph representation reflects reciprocal link topology without duplicate key errors. |
| **T2.12** | `test_workflow_tag_assignment_action`<br>`src/services/workflow_service.py` | Database Action Integration | Configure rule: On high-confidence semantic match (>0.90), auto-assign tag `"auto-verified"`. | Trigger rule execution. Target document receives tag `"auto-verified"` in SQLite database. | Tag query confirms tag presence; analytics counter auto-increments. |

---

### Tier 3: Macro-System & UI Browser Automation Tests

Tier 3 uses Playwright headless browser automation to test visual layout rendering, user interactions, D3 canvas graph performance, and mobile viewport responsiveness.

| Test ID | Test Name & Target UI Container | Methodology | Test Input Vector / Scenario | Authoritative Expected Output | Assertion Criteria |
|---|---|---|---|---|---|
| **T3.01** | `test_ui_analytics_panel_rendering`<br>`View 1 / #diagnostics-view` | Playwright E2E | Navigate to Diagnostics tab. Wait for telemetry cards to mount. | Metrics cards, MIME type distribution chart, and storage usage progress bars render cleanly. | Cards visible; no blank containers or NaN values displayed. |
| **T3.02** | `test_ui_knowledge_graph_canvas_mount`<br>`View 2 / #graph-canvas` | Playwright E2E | Navigate to Knowledge Graph view. Verify canvas initialization. | `<canvas id="knowledge-graph-canvas">` element created with non-zero width and height context. | Canvas element visible; WebGL/2D context active; initial nodes rendered. |
| **T3.03** | `test_ui_graph_node_click_inspector_drawer`<br>`#graph-inspector-drawer` | Playwright Interaction | Click on node `#node-doc-42` within canvas graph view. | Slide-over inspector drawer opens smoothly showing file preview, metadata, and connected wikilinks. | Inspector element has CSS class `.open`; document title matches `"doc-42"`. |
| **T3.04** | `test_ui_graph_1000_node_rendering_benchmark`<br>`#knowledge-graph-canvas` | Performance Benchmark | Seed 1,000 document nodes into graph state. Trigger canvas render loop for 10 seconds. | Average frame time remains $< 16.6\text{ ms}$ ($\ge 60\text{ FPS}$); zero frame stutter or browser lockup. | Playwright frame time telemetry confirms $\ge 60\text{ FPS}$; CPU usage stable. |
| **T3.05** | `test_ui_wikilink_click_navigation`<br>`.wikilink-pill` | Playwright Navigation | Click on inline wikilink pill `[[Architecture Overview]]` in split-screen document editor. | Explorer view switches to `Architecture Overview` document; preview pane updates. | Active document title updates to `"Architecture Overview"`; URL/tab state updated. |
| **T3.06** | `test_ui_workflow_rule_builder_form`<br>`#workflow-rule-builder` | Playwright UI Action | Complete rule builder form: Trigger=`Tag Added`, Condition=`"confidential"`, Action=`Dispatch Webhook`. Click Save. | Form validates inputs, sends `POST /api/workflows/rules`, appends rule card to active workflow list. | Success toast notification displayed; new rule card visible in rules grid. |
| **T3.07** | `test_ui_workflow_trigger_live_feed`<br>`#workflow-log-stream` | Real-Time UI Feed | Open Workflow live log tab while triggering document ingestion event. | Live activity feed streams new event log card into DOM container via SSE. | Log card appended; timestamp matches event time; status pill displays `"COMPLETED"`. |
| **T3.08** | `test_ui_analytics_realtime_refresh_toggle`<br>`#analytics-auto-refresh` | Dynamic State Update | Toggle `"Auto-Refresh (5s)"` checkbox on Analytics Dashboard. Ingest file in background. | Analytics cards update document count from 10 to 11 automatically after 5 seconds. | Metric card text updates to `"11 Documents"` without manual page reload. |
| **T3.09** | `test_ui_graph_dirty_flag_cpu_idle_verification`<br>`#knowledge-graph-canvas` | Energy Efficiency Audit | Render graph canvas. Leave mouse cursor still for 5 seconds (no pan/zoom/hover). | Canvas dirty flag `needsRedraw` stays `false`; animation loop pauses frame rendering. | Playwright CPU profiling confirms idle CPU usage $< 1.0\%$. |
| **T3.10** | `test_ui_responsive_analytics_graph_mobile`<br>`Viewport: 375x812` | Responsive Viewport | Set viewport dimensions to `375x812` (Mobile). Load Diagnostics & Graph views. | Layout reflows cleanly: tab bar collapses into mobile hamburger menu; canvas resizes to fit container. | Zero horizontal scrollbar; text labels legible; touch targets $\ge 44\times 44\text{px}$. |

---

## Real-World Application Scenarios (Tier 4)

Tier 4 tests model complex, multi-component enterprise workloads, stress conditions, adversarial security attempts, and SOC 2 Type II audit compliance.

```text
+---------------------------------------------------------------------------------------------------+
| Scenario T4.01: Enterprise Ingest -> Wikilink Graph -> Analytics -> Workflow Webhook              |
|                                                                                                   |
|  [50 Multi-Format Files] ---> (Ingesting Pipeline) ---> [Extract [[Wikilinks]] & Tags]            |
|                                                               |                                   |
|                                                               v                                   |
|  [Webhook HTTP Dispatch] <--- (Event Bus Trigger) <--- [SQLite WAL Update & Analytics Invalidate] |
+---------------------------------------------------------------------------------------------------+
```

| Test ID | Scenario Name & Target Objective | Complex Workflow Sequence | Authoritative Expected Output | Verification & Invalidation Criteria |
|---|---|---|---|---|
| **T4.01** | `test_scenario_enterprise_ingest_analytics_graph_workflow`<br>**End-to-End Enterprise Ingestion & Trigger Pipeline** | 1. Bulk ingest 50 multi-format documents (PDF, DOCX, MD with `[[wikilinks]]`).<br>2. Query `/api/analytics/summary` for storage update.<br>3. Request `/api/graph/data` for graph link generation.<br>4. Trigger event bus workflow to fire HTTP webhook dispatch. | 1. Ingestion completes in <2.0s.<br>2. Analytics reflects 50 new files.<br>3. Graph constructs 50 nodes and extracted wikilink edges.<br>4. Webhook mock receives HTTP POST payload with valid HMAC header within 200ms. | All 4 pipeline stages pass in sequence. If any step fails, entire workflow aborts cleanly with failure logged in `workflow_logs`. |
| **T4.02** | `test_scenario_1000_node_wikilink_mesh_stress`<br>**1,000-Node Mesh Graph Stress & Memory Stability** | 1. Generate 1,000 interconnected markdown documents forming dense mesh graph.<br>2. Execute `/api/graph/data` query under load.<br>3. Trigger 100 consecutive canvas redraw cycles in Playwright. | 1. Graph API response latency $< 50\text{ ms}$.<br>2. Canvas frame time $< 16.6\text{ ms}$ ($\ge 60\text{ FPS}$).<br>3. Browser memory heap growth $< 5.0\text{ MB}$ across 100 redraw cycles. | Heap memory leak check confirms garbage collection stability. Canvas frame rate maintained. |
| **T4.03** | `test_scenario_webhook_burst_concurrency_backpressure`<br>**High-Throughput Webhook Burst & Backpressure** | 1. Fire 100 simultaneous trigger events (`document_ingested`) in parallel threads.<br>2. Task queue handles burst dispatches against local mock webhook server.<br>3. Measure event drop rate and queue latency. | 1. 100/100 webhook payloads successfully delivered.<br>2. Zero dropped events or task worker crashes.<br>3. Peak queue backlog resolved within $< 3.0\text{ seconds}$. | SQLite task queue state returns to 0 pending tasks. Webhook server logs exactly 100 POST requests. |
| **T4.04** | `test_scenario_adversarial_wikilink_injection_and_xss`<br>**Adversarial Wikilink Injection & Security Containment** | 1. Ingest markdown containing malicious wikilinks:<br>   - `[[<script>alert('XSS')</script>]]`<br>   - `[[../../../../etc/passwd]]`<br>   - `[[javascript:eval(atob(...))]]` | 1. Parser sanitizes link targets using HTML entity encoding.<br>2. Path traversal targets contained within sandbox vault directory.<br>3. UI canvas and preview drawer render text safely without executing script tags. | Playwright console logs zero uncaught XSS errors. File system checks confirm no directory escape. |
| **T4.05** | `test_scenario_webhook_hmac_tampering_and_timeout`<br>**Webhook Security Integrity & Latency Timeout Resilience** | 1. Dispatch webhook payload to mock receiver with invalid HMAC key.<br>2. Dispatch webhook to hanging endpoint (30s delay). | 1. Receiver rejects invalid HMAC payload with HTTP 401 Unauthorized.<br>2. Webhook engine times out hanging request after 5.0s, enqueuing retry backoff. | Invalid signature rejected; engine does not block main FastAPI thread during timeout wait. |
| **T4.06** | `test_scenario_tag_cluster_evolution_under_active_editing`<br>**Dynamic Tag Cluster Evolution & Community Recalculation** | 1. Ingest 100 documents with initial tag `"project-alpha"`.<br>2. Rapidly edit 30 documents, re-tagging them to `"project-beta"`.<br>3. Query `/api/graph/clusters`. | 1. Graph community partitioning algorithm recalculates cluster nodes dynamically.<br>2. Two distinct clusters formed with modularity score $> 0.45$. | Subgraph query verifies clean cluster separation; analytics reflects updated tag counts. |
| **T4.07** | `test_scenario_database_wal_concurrency_analytics_writes`<br>**SQLite WAL Concurrency under Heavy Analytics Writes** | 1. Execute 50 parallel search queries, 20 document ingestion writes, and 10 `/api/analytics/summary` calls simultaneously across 8 worker threads. | 1. Zero `sqlite3.OperationalError: database is locked` exceptions.<br>2. Average query response time $< 10\text{ ms}$. | Database integrity check (`PRAGMA integrity_check;`) returns `"ok"`. WAL file size remains under control. |
| **T4.08** | `test_scenario_soc2_audit_trail_for_workflow_executions`<br>**SOC 2 Type II Audit Logging & Hash Attestation** | 1. Execute sequence of 10 automated workflow tasks.<br>2. Export system audit ledger via `/api/workflows/audit-export`. | 1. Immutable audit ledger generated with ISO-8601 timestamps, user IDs, event hashes, and SHA-256 chain signatures.<br>2. Complies with SOC 2 CC6.1 & PI1.1 trust criteria. | Audit log signature verification returns valid; zero plaintext credentials in log output. |

---

## Coverage Thresholds

To maintain software reliability and prevent architectural regression, the following strict coverage thresholds are programmatically enforced across the codebase:

```text
+-----------------------------------------------------------------------------------+
|                            Global Metric Coverage Goals                           |
+-----------------------------------------------------------------------------------+
|  Total Minimum Test Cases Target:  42/42 Tests (100% Executed & Passing)          |
|  Backend Python Code Coverage:     >= 95.0% Line Coverage                         |
|  FastAPI Router Endpoint Coverage: 100.0% Endpoints Verified                      |
|  Clean Architecture Score:         100.0% Compliance Guard                        |
|  UI Canvas Benchmark Target:       >= 60 FPS under 1,000 Nodes (<16.6ms frame)   |
|  Flaky Test Tolerance:             0.0% (Zero Flakiness Threshold)                |
+-----------------------------------------------------------------------------------+
```

### Enforced Coverage Threshold Matrix

| Subsystem Domain | Target Metric | Minimum Threshold | Enforcement Mechanism |
|---|---|---|---|
| **Domain 1: Analytics Engine (`src/domain/analytics.py`)** | Line Coverage | **$\ge 96.0\%$** | `pytest --cov=src/domain/analytics` |
| **Domain 2: Knowledge Graph (`src/domain/graph.py`)** | Line & Branch Coverage | **$\ge 95.0\%$** | `pytest --cov=src/domain/graph` |
| **Domain 3: Webhook & Workflows (`src/domain/workflows.py`)** | Branch Coverage | **$\ge 98.0\%$** | `pytest --cov=src/domain/workflows` |
| **Domain 4: FastAPI Analytics & Graph Routers** | Endpoint Path Coverage | **$100.0\%$** | `python scripts/update_test_ledger.py` |
| **Domain 5: D3 Canvas Knowledge Graph UI** | Frame Rate Benchmark | **$\ge 60\text{ FPS}$** (1,000 Nodes) | Playwright Performance Telemetry |
| **Clean Architecture Compliance** | Architectural Score | **$100.0\%$** | `python architecture_cli.py audit .` |
| **Asset Parity (Root $\leftrightarrow$ `src/assets/`)** | SHA-256 Bitwise Parity | **$100.0\%$** | Bitwise Hash Parity Check |

### Automated Execution & CI/CD Integration Commands

```bash
# 1. Execute Full Domain Test Suite & Update Master Test Ledger (42+ Tests)
python scripts/update_test_ledger.py

# 2. Run Playwright UI & Canvas Benchmark Automation Suite
pytest tests/test_ui_api_endpoints_empirical.py tests/test_empirical_challenger_final.py

# 3. Run Clean Architecture Audit Guard
python architecture_cli.py audit .

# 4. Verify SOC 2 Audit Ledger & SHA-256 Hash Integrity
python scripts/soc2_audit_reporter.py
```
