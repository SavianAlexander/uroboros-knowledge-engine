---
name: neuro-copilot
description: The master integration and orchestration skill for bridging the Uroboros Knowledge Engine (Neuro), the Tududi Task Master, and GitHub CLI / Git Provenance into a unified, dependency-efficient automated engineering workflow. Incorporates universal polyglot clean architecture audits, multi-phase workflow pipeline chaining, parallel asynchronous inter-bridge contracts, PDF/visual layout QA, automated visual UI journeys, client showcase deck generation, security scanning, bloat detection, and executive dashboards.
---

# Neuro Co-Pilot (Master Autonomous Engineering & Orchestration Suite)

This skill equips the agent with the definitive 8-bridge engineering architecture, uniting the **Neuro Local Knowledge Vault** (`neuro-mcp`), the **Tududi Task Master** (`tududi`), and the **GitHub CLI / Git Merkle Provenance Subsystem** (`gh` CLI & standard git commands) into a unified, zero-dependency, parallel asynchronous closed loop.

---

## The 8 Dedicated Modular CLI Bridges

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
└── workflow_hub_bridge.py   # 7. Master Multi-Phase Engineering Pipeline Orchestrator
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

---

## Tri-Engine Unified Command Matrix (42 Operations)

| # | Command | Engine / Bridge | Purpose |
| :-: | :--- | :--- | :--- |
| **1** | `copilot --prompt "..."` | `github_bridge.py` | Generate Tri-Engine Flight Plan |
| **2** | `tri_engine_health` | `github_bridge.py` | 4-Engine Health Scorecard |
| **3** | `auto_commit` | `github_bridge.py` | SHA-256 Provenance Commit |
| **4** | `create_pr` | `github_bridge.py` | Auto-generate GitHub PR with Tududi links |
| **5** | `sync_issues` | `github_bridge.py` | Bidirectional Issue & Task Sync |
| **6** | `diagnose_ci` | `github_bridge.py` | Download & Diagnose CI Failure Logs |
| **7** | `install_hooks` | `github_bridge.py` | Install `commit-msg` Merkle Verification Hook |
| **8** | `install_ci_workflow` | `github_bridge.py` | Install GitHub Actions CI Workflow |
| **9** | `audit_pr_diff` | `github_bridge.py` | Security & Anti-Pattern Diff Audit |
| **10** | `repo_map` | `github_bridge.py` | Generate Clean ASCII Codebase Tree |
| **11** | `resolve_conflicts` | `github_bridge.py` | Scan & Resolve Merge Conflicts |
| **12** | `format_history` | `github_bridge.py` | Format Git History as Markdown Audit Table |
| **13** | `export_architecture_mermaid`| `github_bridge.py` | Generate Mermaid JS Dependency Graph |
| **14** | `benchmark_audit` | `github_bridge.py` | Benchmark Test Suite Execution Duration |
| **15** | `audit_skills` | `github_bridge.py` | Validate All Active Skills Frontmatter & Health |
| **16** | `audit_security_dependencies`| `github_bridge.py`| Scan `requirements.txt` & `package.json` for Unpinned Deps |
| **17** | `detect_bloat` | `github_bridge.py` | Audit Codebase for Overly Nested Functions & Bloat |
| **18** | `visual_showcase_audit` | `github_bridge.py` | Audit Screenshot Assets, README Links & Orphans |
| **19** | `dashboard` | `github_bridge.py` | Executive Terminal Dashboard with Live Burndown |
| **20** | `generate_release_notes` | `github_bridge.py` | Generate Markdown Release Notes & Tag Release |
| **21** | `query --text "..."` | `neuro_bridge.py` | Semantic Query Local Vector Brain |
| **22** | `ingest --path "..."` | `neuro_bridge.py` | Ingest Documents / Code into Vault |
| **23** | `ingest_git_history` | `neuro_bridge.py` | Index Git Commit Provenance into Vault |
| **24** | `ingest_tududi_roadmap`| `neuro_bridge.py` | Index Live Tududi Roadmap into Vector Vault |
| **25** | `export_note` | `neuro_bridge.py` | Save Architecture Markdown Note into Vault |
| **26** | `stats` | `neuro_bridge.py` | Vault Size, Chunks & Embedding Statistics |
| **27** | `list` | `tududi_bridge.py` | Fetch Active Tasks for Project #13 |
| **28** | `metrics` | `tududi_bridge.py` | Query Project Completion Stats |
| **29** | `burndown` | `tududi_bridge.py` | Render ASCII Sprint Burndown Meter |
| **30** | `export_roadmap` | `tududi_bridge.py` | Export Structured Markdown Roadmap |
| **31** | `scan` | `snapshot_bridge.py` | Full AST & Route Discovery Sweep |
| **32** | `generate_script` | `snapshot_bridge.py` | Generate Playwright Capture Engine |
| **33** | `render_deck` | `snapshot_bridge.py` | Render Glassmorphic Client Showcase Deck |
| **34** | `sync_readme` | `snapshot_bridge.py` | Sync README Visual Tables |
| **35** | `export_package` | `snapshot_bridge.py` | Package Client Distribution Bundle (ZIP) |
| **36** | `serve` | `snapshot_bridge.py` | Launch Local Preview Server |
| **37** | `full_showcase` | `snapshot_bridge.py` | 1-Click End-to-End Client Showcase Suite |
| **38** | `audit` (PDF QA) | `visual_audit_bridge.py`| Automated PDF Page Rendering & Layout QA |
| **39** | `audit` (Clean Arch) | `architecture_bridge.py`| Universal Polyglot Clean Architecture Audit |
| **40** | `run` (Pipeline) | `workflow_hub_bridge.py`| Master Multi-Phase Pipeline Execution |
| **41** | `run --parallel` | `workflow_hub_bridge.py`| Parallel Asynchronous Inter-Bridge Execution |
| **42** | `run_parallel` | `contract_bus.py` | Low-Level Parallel Inter-Bridge DAG Runner |

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
