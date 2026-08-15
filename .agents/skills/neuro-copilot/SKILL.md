---
name: neuro-copilot
description: The master integration and orchestration skill for bridging the Uroboros Knowledge Engine (Neuro), the Tududi Task Master, and GitHub CLI / Git Provenance into a unified, dependency-efficient automated engineering workflow. Incorporates universal polyglot clean architecture audits, multi-phase workflow pipeline chaining, parallel asynchronous inter-bridge contracts, PDF/visual layout QA, automated visual UI journeys, client showcase deck generation, security scanning, bloat detection, and executive dashboards.
---

# Neuro Co-Pilot (Master Autonomous Engineering & Orchestration Suite)

This skill equips the agent with the definitive 10-bridge engineering architecture, uniting the **Neuro Local Knowledge Vault** (`neuro-mcp`), the **Tududi Task Master** (`tududi`), the **GitHub CLI / Git Merkle Provenance Subsystem** (`gh` CLI & standard git commands), the **EVE Online Tactical Telemetry Engine**, and the **OS Process Hygiene & System Perfection Engine** into a unified, zero-dependency, parallel asynchronous closed loop.

---

## The 10 Dedicated Modular CLI Bridges

All bridges are zero-dependency standard library Python scripts located in `scripts/`:

```
.agents/skills/neuro-copilot/scripts/
├── contract_bus.py          # 0. Inter-Bridge Contract Bus & Asynchronous Parallel Orchestrator
├── neuro_bridge.py          # 1. Local Vector Vault, Knowledge Ingestion & Ollama RAG
├── tududi_bridge.py         # 2. Tududi Task Master Tracking, Burndown & 4-Tier Auditing
├── github_bridge.py         # 3. GitHub CLI, Git Merkle Root Provenance & CI Audits
├── snapshot_bridge.py       # 4. Enterprise Client Snapshot Showcases & Interactive Decks
├── visual_audit_bridge.py   # 5. Automated PDF Page Rendering & Layout QA Engine
├── architecture_bridge.py   # 6. Universal Polyglot Clean Architecture Engine (0-100% Score)
├── workflow_hub_bridge.py   # 7. Master Multi-Phase Engineering Pipeline Orchestrator
├── eve_bridge.py            # 8. EVE Online Tactical Intelligence & Live Telemetry Bridge
├── system_recovery_bridge.py# 9. Windows System Resilience & Zero-Reboot Crash Recovery Bridge
└── process_hygiene_bridge.py# 10. OS Process Hygiene, Zombie Elimination & System Perfection Bridge
```


### 0. Inter-Bridge Contract Bus (`scripts/contract_bus.py`)
- `python .../contract_bus.py run_parallel`: Execute all bridges concurrently using asynchronous DAG scheduling with cryptographic SHA-256 Merkle contracts.
- `python .../contract_bus.py self_test`: Run contract bus self-tests.

### 1. Neuro Knowledge Engine Bridge (`scripts/neuro_bridge.py`)
- `python .../neuro_bridge.py query --text "..."`: Query local RAG brain with HyDE expansion.
- `python .../neuro_bridge.py ingest --path "..."`: Ingest document or directory into vault.
- `python .../neuro_bridge.py ingest_git_history --limit 20`: Index recent git commit provenance into vault.
- `python .../neuro_bridge.py ingest_tududi_roadmap`: Export and index live Tududi roadmap into vector vault.
- `python .../neuro_bridge.py export_note --title "..." --content "..."`: Save architecture note into vault.
- `python .../neuro_bridge.py stats`: Audit knowledge vault size & chunk metrics.
- `python .../neuro_bridge.py self_test`: Run Neuro bridge self-tests.

### 2. Tududi Task Master Bridge (`scripts/tududi_bridge.py`)
- `python .../tududi_bridge.py list`: Fetch active Tududi tasks for Project #13.
- `python .../tududi_bridge.py metrics`: Query project completion stats & audit metrics.
- `python .../tududi_bridge.py burndown`: Render ASCII burndown meter and task velocity.
- `python .../tududi_bridge.py export_roadmap`: Generate structured Markdown roadmap for vault indexing.
- `python .../tududi_bridge.py self_test`: Run Tududi bridge self-tests.

### 3. GitHub & Git Provenance Bridge (`scripts/github_bridge.py`)
- `python .../github_bridge.py copilot --prompt "..." [--execute]`: Synthesize and 1-click initialize Engineering Flight Plan.
- `python .../github_bridge.py tri_engine_health`: Run unified health scorecard across all engines.
- `python .../github_bridge.py auto_commit --scope feat --desc "..."`: Staged-files SHA-256 commit with provenance.
- `python .../github_bridge.py dashboard`: Render executive terminal dashboard with live Tududi burndown meter.
- `python .../github_bridge.py visual_showcase_audit`: Audit screenshot assets, README links, and orphan visual files.
- `python .../github_bridge.py snapshot`: Run 1-click client visual showcase generation.
- `python .../github_bridge.py run_full_pipeline`: 1-click full Tri-Engine pipeline pass.
- `python .../github_bridge.py self_test`: Run GitHub bridge self-tests.

### 4. Snapshot & Client Showcase Bridge (`scripts/snapshot_bridge.py`)
- `python .../snapshot_bridge.py scan`: Perform full AST & routing sweep to map all views, modals, and tabs.
- `python .../snapshot_bridge.py generate_script`: Generate Playwright `scripts/capture_ux_journey.mjs` tailored to views.
- `python .../snapshot_bridge.py render_deck`: Generate interactive glassmorphic Client Showcase HTML presentation deck.
- `python .../snapshot_bridge.py sync_readme`: Synchronize README.md visual tables with screenshots in `docs/ux_journey/`.
- `python .../snapshot_bridge.py export_package`: Compress HTML deck, view catalog, and all assets into a standalone ZIP package.
- `python .../snapshot_bridge.py serve [--port 8088]`: Launch local lightweight preview server.
- `python .../snapshot_bridge.py full_showcase`: 1-Click end-to-end client showcase sweep and packaging.
- `python .../snapshot_bridge.py self_test`: Run Snapshot bridge self-tests.

### 5. Visual Layout & PDF QA Bridge (`scripts/visual_audit_bridge.py`)
- `python .../visual_audit_bridge.py audit [--pdf doc.pdf]`: Render PDF pages at 150 DPI into PNGs, check layout flaws (orphan headers, pagination leaks, table cuts, excessive blank space), and generate `docs/visual_audit/visual_page_audit.md`.
- `python .../visual_audit_bridge.py self_test`: Run Visual Audit bridge self-tests.

### 6. Universal Clean Architecture Bridge (`scripts/architecture_bridge.py`)
- `python .../architecture_bridge.py audit`: Calculate clean architecture compliance score (0–100%) across 9 languages.
- `python .../architecture_bridge.py doctor`: Run comprehensive architecture & root hygiene diagnostics.
- `python .../architecture_bridge.py check-secrets`: Scan code for exposed OpenAI/Stripe/JWT/AWS/GitHub API keys and secrets.
- `python .../architecture_bridge.py db-backup`: 1-Click automated database backup snapshot for SQLite/DB files.
- `python .../architecture_bridge.py deploy-check`: Production launch readiness scorecard.
- `python .../architecture_bridge.py self_test`: Run Clean Architecture bridge self-tests.

### 7. Workflow Hub Pipeline Orchestrator (`scripts/workflow_hub_bridge.py`)
- `python .../workflow_hub_bridge.py run [--phase all|audit|optimize|test|showcase]`: Coordinate and chain multi-phase engineering passes sequentially.
- `python .../workflow_hub_bridge.py run --parallel`: Execute full parallel asynchronous contract pipeline.
- `python .../workflow_hub_bridge.py self_test`: Run Workflow Hub bridge self-tests.

### 8. EVE Online Tactical Bridge (`scripts/eve_bridge.py`)
- `python .../eve_bridge.py telemetry`: Query live empirical telemetry for all 8 fleet pilots (SP, active ships, queues, ISK).
- `python .../eve_bridge.py search --query "..."`: Sub-5ms Reciprocal Rank Fusion (RRF) search across 2,947 EVE intelligence vault files.
- `python .../eve_bridge.py remap`: Calculate optimal neural attribute remaps (+45% training acceleration).
- `python .../eve_bridge.py audit`: Execute 38-assertion zero-assumption mathematical and ESI validation suite.
- `python .../eve_bridge.py self_test`: Run automated contract assertions for EVE Online tactical bridge.

### 9. Windows System Resilience & Zero-Reboot Recovery Bridge (`scripts/system_recovery_bridge.py`)
- `python .../system_recovery_bridge.py restore_all`: Execute 5-stage non-reboot recovery cascade (Explorer shell, DWM, Audio services, DNS flush, hung processes).
- `python .../system_recovery_bridge.py restart_shell`: Restart Windows Explorer shell (`explorer.exe`) to resolve taskbar/Start menu/desktop freeze.
- `python .../system_recovery_bridge.py restart_dwm`: Refresh Desktop Window Manager (`dwm.exe`) for window rendering/display glitch recovery.
- `python .../system_recovery_bridge.py restart_audio`: Restart Windows Audio services (`Audiosrv` & `AudioEndpointBuilder`).
- `python .../system_recovery_bridge.py flush_dns`: Flush DNS resolver cache and reset network stack state.
- `python .../system_recovery_bridge.py clear_hung`: Identify and terminate unresponsive/hung background processes.
- `python .../system_recovery_bridge.py self_test`: Run automated contract assertions for system recovery bridge.

---

## Integrated Execution Protocols

### I. Tududi Task Master Tracking & 4-Tier Audit Protocol
Whenever executing multi-step work or in planning mode:
1. **Zero `task.md` Rule**: Never create local markdown files for task tracking. Use the connected Tududi MCP server.
2. **4-Tier Subtask Breakdown**:
   - `[PLAN]` Requirements & Architectural Discovery
   - `[BUILD]` Implementation & Source Code Edits
   - `[TEST]` Unit & Hardware Verification Suite
   - `[AUDIT]` E2E Visual & Documentation Audit
3. **Rich Parameter Population**: Populate `note` with exact paths (`[FILES]`), test results (`[TESTS]`), and benchmark metrics (`[BENCHMARKS]`). Always tag with `Antigravity` and link to Project #13 (*Neuro Alexander*).
4. **Mandatory Automatic Completion (`complete_task`)**: Immediately upon finishing any phase, call `complete_task` (`id: <task_id>, status: 2`) in real time.

### II. Universal Polyglot Clean Architecture Protocol
1. **Pre-Edit Audit**: `python .../architecture_bridge.py audit` (Baseline score 0–100%).
2. **Layer Assignment**: Core Domain (`src/core/domain`), Infrastructure (`src/infrastructure`), Presentation (`src/app`), Shared (`src/shared`), Assets (`public/`, `src/assets/`).
3. **Minimal Edit & Root Hygiene**: Zero floating source files in the root folder.
4. **Secret Scanning**: `python .../architecture_bridge.py check-secrets`.
5. **Deployment Gate**: `python .../architecture_bridge.py deploy-check` (Must be 100% verified before shipping).

### III. Automated Visual Showcase & UX Journey Protocol
1. **Discovery Sweep**: Scan AST and routes (`snapshot_bridge.py scan`).
2. **Playwright Capture Script**: Generate font-stabilized, clock-frozen screenshot runner (`snapshot_bridge.py generate_script`).
3. **Multi-Viewport Retinas**: Capture Desktop (`1440x900`) and Mobile (`375x812`) viewports.
4. **Interactive Client Deck**: Render glassmorphic presentation deck with category tabs, live search, and theme comparison slider (`snapshot_bridge.py render_deck`).
5. **Client Distribution Package**: Package deck and assets into standalone ZIP archive (`snapshot_bridge.py export_package`).
6. **README Parity**: Synchronize README.md tables with zero broken links (`snapshot_bridge.py sync_readme`).

### IV. Visual Layout & PDF Document QA Protocol
1. **Render Pages to PNG**: Extract pages at 150 DPI using `visual_audit_bridge.py`.
2. **Report Card**: Compile `docs/visual_audit/visual_page_audit.md`.
3. **Flaw Detection Matrix**:
   - *Orphan Headers*: Section header at bottom of page without at least 3 lines of following text.
   - *Pagination Leakage*: Single trailing sentence or 1-2 list items leaking onto a new page.
   - *Table Page Cuts*: Table headers separated from data rows across page boundaries.
   - *Excessive Blank Space*: Large white gaps from premature page breaks.

### V. Parallel Asynchronous Inter-Bridge Contract Protocol
1. **Contract Handshake**: Every bridge invocation produces a `BridgeContract` with duration, outputs, shared context, and SHA-256 Merkle hash.
2. **Parallel DAG Scheduling**:
   - **Stage 1 (Concurrent Independent Execution)**: Architecture, Tududi, GitHub, and Visual Audit execute simultaneously via `asyncio.gather` and thread pools.
   - **Stage 2 (Context-Informed Parallel Execution)**: Snapshot Showcase (consuming architecture routes and sprint burndown) and Neuro Vault (consuming git commit hashes) execute concurrently.
   - **Stage 3 (Ledger Compilation)**: Persistent audit trail written to `docs/bridge_contracts/execution_ledger.json` and `docs/bridge_contracts/contract_audit_ledger.md`.

### VI. Continuous Integration & Remote CI Health Verification Protocol
1. **Pre-Push Local Gate**:
   - Run domain tests: `python run_domain_tests.py` (Must report `0 failed, 0 errors`).
   - Run architecture doctor: `python scripts/architecture_cli.py doctor .`.
   - Run security fuzzing: `python .agents/skills/neuro-copilot/scripts/github_bridge.py crucible`.
2. **Post-Push Remote Monitoring & Confirmation**:
   - Immediately after `git push`, invoke `python .agents/skills/neuro-copilot/scripts/github_bridge.py verify_ci --wait`.
   - Actively watch all 4 remote GitHub Actions workflows:
      - `CI Pipeline` (Matrix Test Python 3.11 & 3.12)
      - `Domain Integration CI Suite` (Domain Test Matrix & Security Controls)
      - `Security & Static Analysis Audit` (Static Blast Radius & Dependency Security Audit)
      - `Build & Package` (Desktop Artifacts, Web Dist & GHCR Container Image)
3. **Zero-Failure Completion Guarantee**:
   - Never declare work complete or mark Tududi milestones done until 100% of remote workflows conclude with `SUCCESS (Green)`.
   - If any workflow fails, immediately execute `github_bridge.py diagnose_ci --run-id <id>`, apply root-cause fixes, re-verify locally, push, and confirm all pipelines pass green.

### VII. Branching, Pull Request & Semantic Release Protocol
1. **Semantic Branch Naming Hierarchy**:
   - `feat/<name>`: New capabilities or architectural expansions (e.g. `feat/graph-physics`).
   - `fix/<name>`: Bug fixes, vulnerability patches, or lock resolutions (e.g. `fix/sqlite-timeout`).
   - `perf/<name>`: Zero-dependency algorithmic speedups (e.g. `perf/fts5-bm25-cache`).
   - `chore/<name>`: Maintenance, CI, and tooling upgrades (e.g. `chore/bump-deps`).
2. **Autonomous Ghost Loop Flywheel**:
   - For rapid end-to-end feature delivery: `python .../github_bridge.py ghost_loop --prompt "..." --pr`.
   - Automatically creates branch, implements minimal diff, verifies domain tests, commits with SHA-256 Merkle root, and opens a linked Pull Request.
3. **Pre-Merge PR Security & Diff Audit**:
   - Execute `python .../github_bridge.py audit_pr_diff` before merging any PR to ensure zero API key leaks or anti-patterns.
4. **Master Branch Protection Invariant**:
   - `master` is strictly protected: All 5 CI workflows (`CI Pipeline`, `Domain Integration CI Suite`, `Security & Static Analysis Audit`, `Build & Package`, `GitHub Pages`) must be 100% Green before merging.

### VIII. Dynamic, Autonomous & Self-Calibrating Engine Architecture Protocol
All retrieval, domain, and bridge engines in the system are architected to operate on **dynamic, autonomous, and automatic values**, eliminating brittle hardcoded assumptions, static port binds, and manual calibration:

1. **Dynamic Runtime Values & Adaptive Calibration**:
   - **Dynamic Socket & Port Allocation**: Network and E2E servers bind to dynamic OS ephemeral ports (`socket.bind(('127.0.0.1', 0))` / `get_free_port()`) rather than static ports to guarantee zero collisions across parallel worker threads.
   - **Dynamic Context Budgeting & Token Compression**: Context managers (`adaptive_context_compressor.py`, `context_budget_allocator.py`, `mrl_compressor.py`) dynamically calculate token capacity per active LLM context window limits and dynamically compress or truncate embeddings and prompts without hardcoded slice lengths.
   - **Dynamic Retrieval Fusion ($\alpha$-Tuning)**: Hybrid retrieval engines (`auto_weight_tuner.py`, `sparse_dense_fusion.py`) balance dense semantic vectors and lexical BM25/FTS5 indexes via dynamically adjusted reciprocal rank fusion weights calculated from query entropy.
   - **Dynamic Hardware Sizing**: Model management engines (`model_manager.py`) detect available GPU VRAM and CPU core topologies to size batching and select quantization tiers automatically; audio DSP pipelines dynamically calibrate sample rates, chunk sizes, and jitter buffers.

2. **Autonomous Decision Loops & Self-Healing**:
   - **Autonomous Multi-Tier Model Routing**: The model router (`model_router.py`) dynamically discovers available inference providers (local Ollama, vLLM, GGUF runtimes, or in-memory fallback embeddings) and routes queries without operator intervention.
   - **Autonomous Storage & Index Healing**: Database health services (`database_self_healer.py`, `index_self_healing.py`, `knowledge_self_healing.py`) continuously monitor SQLite WAL states, detect deadlocks or corrupted virtual tables, and rebuild indexes automatically.
   - **Autonomous Parallel DAG Scheduling**: The contract bus (`contract_bus.py`, `workflow_hub_bridge.py`) resolves bridge dependency graphs dynamically, scheduling independent bridges concurrently via asynchronous task groups with SHA-256 Merkle contract verification.
   - **Autonomous OS Process Hygiene**: Process management engines (`process_hygiene_bridge.py`) execute automated pre-flight and post-flight sweeps to identify and terminate orphan browser workers and dead console hosts while protecting core OS whitelists.

3. **Automatic Configuration & Invariant Preservation**:
   - **Automatic Zero-Configuration Defaults**: All modular bridges and CLI commands auto-resolve project directories, task IDs, database paths, and environment settings.
   - **Automatic Database Pragma Initialization**: SQLite managers (`know.py`) automatically ensure WAL mode, synchronous=NORMAL, cache sizing, FTS5 virtual table schemas, and indexing triggers on boot.
   - **Automatic NFC Unicode Normalization**: Query parsers and legal retrieval engines automatically apply NFC Unicode normalization and word-boundary tokenization before database indexing.
   - **Automatic Zero-Reboot System Recovery**: Recovery daemons (`system_recovery_bridge.py`) automatically cascade through non-reboot restorative phases (Explorer shell -> DWM -> Audio services -> DNS resolver -> process pruning) during platform degradation.

### IX. Automated OS Process Hygiene & System Perfection Protocol
To maintain a high-performance, clutter-free operating system environment:
1. **Automated Dual-Hook Guarantee**: Process hygiene executes automatically as a **Pre-Flight sweep** before any Neuro workflow begins, and as a **Post-Flight sweep** upon pipeline conclusion.
2. **Surgical Orphan Elimination**:
   - Detects and terminates orphaned WebKit/browser test workers (`WebKitNetworkProcess.exe`, `MiniBrowser.exe`, `playwright.exe`).
   - Clears orphaned background `conhost.exe` consoles and dead `cmd.exe` process trees.
   - Cleans duplicate server instances (`llama-server.exe`) to reclaim VRAM/RAM.
3. **Core OS Whitelist Protection**:
   - Preserves critical OS kernel services, Desktop Window Manager, Explorer shell, active IDE sessions (`Antigravity.exe`, `language_server.exe`), Discord, WSL2 VM hosts (`vmmemWSL`), Docker Desktop, and active hardware driver daemons (AMD Adrenalin, Corsair iCUE, Logitech Options+).
4. **Standalone Invocation**:
   - Audit: `python .../process_hygiene_bridge.py scan`
   - Clean: `python .../process_hygiene_bridge.py clean`
   - Pre-Flight: `python .../process_hygiene_bridge.py preflight`
   - Post-Flight: `python .../process_hygiene_bridge.py postflight`

### X. Production-Grade Technical Precision & Domain-Driven Naming Standard
To ensure immediate readability, executive clarity, and frictionless collaboration:
1. **Strict Anti-Hyperbole Rule**: Never introduce or use marketing, hype-y, sensationalist, or fictional adjectives (e.g., *"supremacy"*, *"incomparable"*, *"singularity"*, *"omniscient"*, *"crucible matrix"*, *"omni-perfection"*, *"magic"*).
2. **Self-Descriptive Test Naming Invariant**: Every test suite file must clearly name the exact subsystem and verification method being tested:
   - Pattern: `test_<subsystem>_<verification_type>.py`
   - Examples: `test_rag_metamorphic_validation.py`, `test_crawler_browser_automation.py`, `test_developer_ast_rag.py`, `test_voice_synthesis_audio_processing.py`.
3. **Descriptive Operational Script Naming**: Operational utilities must use clear functional verbs and nouns:
   - Examples: `scripts/fault_injection_harness.py`, `scripts/verify_system_integrity.py`, `scripts/verify_voice_audio_matrix.py`, `scripts/verify_empirical_models.py`.
4. **Self-Descriptive Domain & Crawler Mode Aliasing**: All multi-mode engines (e.g. web crawlers, RAG routers) must expose clear, human-understandable session mode aliases:
   - `adaptive_session`, `browser_automation`, `proxy_rotation`, `async_pool`, `rotating_headers`, `direct`.
5. **Clean CI/CD Workflow & Documentation Nomenclature**: GitHub Actions workflows and documentation badges/headings must reflect clear technical operations (e.g. *Domain Integration CI Suite*, *Security & Static Analysis Audit*, *Core Retrieval Subsystems*).

---

## Tri-Engine Unified Command Matrix (53 Operations)

| # | Command | Engine / Bridge | Purpose |
| :-: | :--- | :--- | :--- |
| **1** | `copilot --prompt "..."` | `github_bridge.py` | Generate Tri-Engine Flight Plan |
| **2** | `tri_engine_health` | `github_bridge.py` | 4-Engine Health Scorecard |
| **3** | `auto_commit` | `github_bridge.py` | SHA-256 Provenance Commit |
| **4** | `create_pr` | `github_bridge.py` | Auto-generate GitHub PR with Tududi links |
| **5** | `sync_issues` | `github_bridge.py` | Bidirectional Issue & Task Sync |
| **6** | `diagnose_ci` | `github_bridge.py` | Download & Diagnose CI Failure Logs |
| **7** | `verify_ci [--wait]` | `github_bridge.py` | Verify Remote CI Workflows & 100% Green Health |
| **8** | `install_hooks` | `github_bridge.py` | Install `commit-msg` Merkle Verification Hook |
| **9** | `install_ci_workflow` | `github_bridge.py` | Install GitHub Actions CI Workflow |
| **10** | `audit_pr_diff` | `github_bridge.py` | Security & Anti-Pattern Diff Audit |
| **11** | `repo_map` | `github_bridge.py` | Generate Clean ASCII Codebase Tree |
| **12** | `resolve_conflicts` | `github_bridge.py` | Scan & Resolve Merge Conflicts |
| **13** | `format_history` | `github_bridge.py` | Format Git History as Markdown Audit Table |
| **14** | `export_architecture_mermaid`| `github_bridge.py` | Generate Mermaid JS Dependency Graph |
| **15** | `benchmark_audit` | `github_bridge.py` | Benchmark Test Suite Execution Duration |
| **16** | `audit_skills` | `github_bridge.py` | Validate All Active Skills Frontmatter & Health |
| **17** | `audit_security_dependencies`| `github_bridge.py`| Scan `requirements.txt` & `package.json` for Unpinned Deps |
| **18** | `detect_bloat` | `github_bridge.py` | Audit Codebase for Overly Nested Functions & Bloat |
| **19** | `visual_showcase_audit` | `github_bridge.py` | Audit Screenshot Assets, README Links & Orphans |
| **20** | `dashboard` | `github_bridge.py` | Executive Terminal Dashboard with Live Burndown |
| **21** | `generate_release_notes` | `github_bridge.py` | Generate Markdown Release Notes & Tag Release |
| **22** | `query --text "..."` | `neuro_bridge.py` | Semantic Query Local Vector Brain |
| **23** | `ingest --path "..."` | `neuro_bridge.py` | Ingest Documents / Code into Vault |
| **24** | `ingest_git_history` | `neuro_bridge.py` | Index Git Commit Provenance into Vault |
| **25** | `ingest_tududi_roadmap`| `neuro_bridge.py` | Index Live Tududi Roadmap into Vector Vault |
| **26** | `export_note` | `neuro_bridge.py` | Save Architecture Markdown Note into Vault |
| **27** | `stats` | `neuro_bridge.py` | Vault Size, Chunks & Embedding Statistics |
| **28** | `list` | `tududi_bridge.py` | Fetch Active Tasks for Project #13 |
| **29** | `metrics` | `tududi_bridge.py` | Query Project Completion Stats |
| **30** | `burndown` | `tududi_bridge.py` | Render ASCII Sprint Burndown Meter |
| **31** | `export_roadmap` | `tududi_bridge.py` | Export Structured Markdown Roadmap |
| **32** | `scan` | `snapshot_bridge.py` | Full AST & Route Discovery Sweep |
| **33** | `generate_script` | `snapshot_bridge.py` | Generate Playwright Capture Engine |
| **34** | `render_deck` | `snapshot_bridge.py` | Render Glassmorphic Client Showcase Deck |
| **35** | `sync_readme` | `snapshot_bridge.py` | Sync README Visual Tables |
| **36** | `export_package` | `snapshot_bridge.py` | Package Client Distribution Bundle (ZIP) |
| **37** | `serve` | `snapshot_bridge.py` | Launch Local Preview Server |
| **38** | `full_showcase` | `snapshot_bridge.py` | 1-Click End-to-End Client Showcase Suite |
| **39** | `audit` (PDF QA) | `visual_audit_bridge.py`| Automated PDF Page Rendering & Layout QA |
| **40** | `audit` (Clean Arch) | `architecture_bridge.py`| Universal Polyglot Clean Architecture Audit |
| **41** | `run` (Pipeline) | `workflow_hub_bridge.py`| Master Multi-Phase Pipeline Execution |
| **42** | `run --parallel` | `workflow_hub_bridge.py`| Parallel Asynchronous Inter-Bridge Execution |
| **43** | `run_parallel` | `contract_bus.py` | Low-Level Parallel Inter-Bridge DAG Runner |
| **44** | `restore_all` | `system_recovery_bridge.py`| 5-Stage Zero-Reboot Windows Recovery Cascade |
| **45** | `restart_shell` | `system_recovery_bridge.py`| Restart Windows Explorer Desktop Shell |
| **46** | `restart_dwm` | `system_recovery_bridge.py`| Refresh Desktop Window Manager (DWM) |
| **47** | `restart_audio` | `system_recovery_bridge.py`| Restart Windows Audio Services |
| **48** | `flush_dns` | `system_recovery_bridge.py`| Flush Windows DNS Resolver Cache |
| **49** | `clear_hung` | `system_recovery_bridge.py`| Terminate Unresponsive Windows Processes |
| **50** | `scan` (Hygiene) | `process_hygiene_bridge.py`| Full OS Process Hygiene Audit & Orphan Scan |
| **51** | `clean` (Hygiene) | `process_hygiene_bridge.py`| Surgical Elimination of Orphan & Zombie Processes |
| **52** | `preflight` | `process_hygiene_bridge.py`| Automated Pre-Flight Process Sanitization Sweep |
| **53** | `postflight` | `process_hygiene_bridge.py`| Automated Post-Flight Process Cleanup Sweep |

---

## References & Bridge Index
- Contract Bus Orchestrator: [`scripts/contract_bus.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/contract_bus.py)
- GitHub CLI Bridge: [`scripts/github_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/github_bridge.py)
- Neuro Vault Bridge: [`scripts/neuro_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/neuro_bridge.py)
- Tududi Master Bridge: [`scripts/tududi_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/tududi_bridge.py)
- Snapshot Showcase Bridge: [`scripts/snapshot_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/snapshot_bridge.py)
- Visual Layout Audit Bridge: [`scripts/visual_audit_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/visual_audit_bridge.py)
- Clean Architecture Bridge: [`scripts/architecture_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/architecture_bridge.py)
- Workflow Hub Bridge: [`scripts/workflow_hub_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/workflow_hub_bridge.py)
- System Recovery Bridge: [`scripts/system_recovery_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/system_recovery_bridge.py)
- Process Hygiene Bridge: [`scripts/process_hygiene_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/process_hygiene_bridge.py)

