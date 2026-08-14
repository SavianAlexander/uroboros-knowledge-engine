---
name: neuro-copilot
description: The master integration skill for bridging the Uroboros Knowledge Engine (Neuro), the Tududi Task Master, and GitHub CLI / Git Provenance into a unified, dependency-efficient automated engineering workflow. Trigger this skill whenever you need to query local knowledge, orchestrate tasks, execute git/GitHub operations, run CI/CD health checks, audit PR diffs, analyze merge conflicts, format commit history, benchmark performance, detect codebase bloat, scan security dependencies, capture high-definition visual UI journeys, document README visual showcases, synthesize flight plans, or render executive dashboards.
---

# Neuro Co-Pilot (Enterprise Tri-Engine Dominance Suite)

This skill dictates how you (the AI Agent) must interact with the **Neuro MCP Server** (`neuro-mcp`), the **Tududi MCP Server** (`tududi`), and the **GitHub CLI / Git Provenance Subsystem** (`gh` CLI & standard git commands) in tandem to execute closed-loop, dependency-efficient automated engineering workflows.

---

## The Tri-Engine Mandate & Autonomous Subagent Protocol

You have access to three primary orchestration engines:
1. **Neuro (`neuro-mcp` & Local RAG Brain)**: The local AI brain. Stores semantic vector embeddings, FTS5 keyword indexes, Binary ColBERT reranking matrices, Knowledge Graph wikilinks, git commit provenance, and cryptographic document provenance signatures.
2. **Tududi (`tududi`)**: The Task Master & Execution Auditor. Serves as the single source of truth for all project execution, subtask checklists, and habit tracking under Project #13 (*Neuro Alexander*).
3. **GitHub (`gh` CLI & Git)**: Codebase Dominance & CI/CD Control. Manages Pull Requests (`gh pr`), Issue synchronization (`gh issue`), GitHub Actions workflow monitoring (`gh run`), Git commit provenance, diff security auditing (`audit_pr_diff`), conflict resolution (`resolve_conflicts`), dependency security scanning (`audit_security_dependencies`), bloat detection (`detect_bloat`), visual showcase audits (`visual_showcase_audit`), terminal dashboard rendering (`dashboard`), and release tagging (`gh release`).

### 🤖 Autonomous Subagent Delegation Protocol (`neuro-copilot-agent`)

When `/neuro-copilot` is activated for deep codebase research, multi-file auditing, or vault document synthesis:
- **Format Prompt**: Run `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_agent_prompt --task "..."` to generate the strict execution constraints.
- **Define / Invoke Subagent**: Use `define_subagent` and `invoke_subagent` to spawn a specialized subagent named `neuro-copilot-agent` (Role: `Local RAG Brain Co-Pilot & Codebase Researcher`).
- **Token Efficiency Standard**: The subagent executes context-heavy lookups using `query_local_brain` (`python .agents/skills/neuro-copilot/scripts/github_bridge.py query_local_brain --query "..."`), `neuro_search`, and file reading in a separate isolated conversation, saving parent model tokens.
- **Executive Synthesis**: The subagent synthesizes findings and reports back with structured Markdown analysis.

---

## Standardized Modular Bridge Architecture (4 Dedicated CLI Bridges)

The skill uses 4 modular, zero-dependency Python CLI bridge scripts located in `scripts/`:

1. **Neuro Knowledge Engine Bridge (`scripts/neuro_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py query --text "..."`: Query local RAG brain with HyDE expansion.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest --path "..."`: Ingest document or directory into vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest_git_history --limit 20`: Index recent git commit provenance into vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest_tududi_roadmap`: Export and index live Tududi roadmap into vector vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py export_note --title "..." --content "..."`: Save architecture note into vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py stats`: Audit knowledge vault size & chunk metrics.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py self_test`: Run Neuro bridge self-tests.

2. **Tududi Task Master Bridge (`scripts/tududi_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py list`: Fetch active Tududi tasks for Project #13.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py metrics`: Query project completion stats & audit metrics.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py burndown`: Render ASCII burndown meter and task velocity.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py export_roadmap`: Generate structured Markdown roadmap for vault indexing.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py self_test`: Run Tududi bridge self-tests.

3. **GitHub & Git Provenance Bridge (`scripts/github_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py copilot --prompt "..." [--execute]`: Synthesize and optionally 1-click initialize Engineering Flight Plan.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py tri_engine_health`: Run 4-engine unified health scorecard.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py auto_commit --scope feat --desc "..."`: Staged-files SHA-256 commit with provenance.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py dashboard`: Render executive terminal dashboard with live Tududi burndown meter.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py visual_showcase_audit`: Audit screenshot assets, README links, and orphan visual files.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py snapshot`: Run 1-click client visual showcase generation.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py run_full_pipeline`: 1-click full Tri-Engine pipeline pass.

4. **Snapshot & Client Showcase Bridge (`scripts/snapshot_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py scan`: Perform full AST & routing sweep to map all views, modals, and tabs.
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py generate_script`: Generate Playwright `scripts/capture_ux_journey.mjs` tailored to views.
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py render_deck`: Generate Glassmorphic Client Showcase HTML presentation deck.
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py sync_readme`: Synchronize README.md visual showcase tables with captured assets.
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py full_showcase`: 1-click end-to-end full client showcase generation.
   - `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py self_test`: Run Snapshot bridge self-tests.

### Comprehensive Tri-Engine Command Matrix

| Command | Subcommand | Purpose |
| :--- | :--- | :--- |
| **1. Flight Plan Generator** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py copilot --prompt "..." [--execute]` | Synthesize developer intent into structured engineering plan and 1-click initialize branch. |
| **2. Tri-Engine Health** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py tri_engine_health` | Unified diagnostic across Neuro, Tududi, GitHub, and Architecture Doctor. |
| **3. Live Burndown Dashboard** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py dashboard` | Render ASCII terminal dashboard with live Tududi progress bar, git state, and CI workflows. |
| **4. Tududi Burndown Meter** | `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py burndown` | Render real-time ASCII completion meter and task ratio. |
| **5. Roadmap RAG Ingestion** | `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest_tududi_roadmap` | Ingest Tududi sprint backlog and roadmaps into local vector brain. |
| **6. Auto Commit Provenance** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py auto_commit --scope S --desc D` | Staged-files Merkle tree digest calculation and auto-commit with task tag. |
| **7. Subagent Prompt Builder** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_agent_prompt --task T` | Format standardized system prompt for autonomous subagent delegation. |
| **8. Full Pipeline Pass** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py run_full_pipeline` | Execute 1-click full Tri-Engine pipeline (dashboard -> health -> diff audit -> bloat -> sec -> conflict -> self test -> domain test). |
| **9. Health Check** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py check_health` | Audit git status, `gh` auth, active PRs, issues, git hooks, CI workflows, and CI runs. |
| **10. Issue Sync** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py sync_issues` | Fetch open GitHub Issues formatted as Tududi Task import JSON. |
| **11. CI Diagnosis** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py diagnose_ci [--run-id ID]` | Auto-detect failed Actions runs, extract tracebacks, & build `neuro_search` query. |
| **12. Provenance Tag** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py provenance_tag --scope S --desc D --task T` | Compute SHA-256 hash of staged files & format executive commit string. |
| **13. PR Automation** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py create_pr --title T --task T --hash H` | Generate & open a Pull Request with embedded Tududi checklists. |
| **14. Hook Guard** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py install_hooks` | Install `.git/hooks/commit-msg` guard enforcing Tududi/Neuro provenance tags. |
| **15. CI Workflow Setup** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py install_ci_workflow` | Generate `.github/workflows/neuro_copilot_ci.yml` for GitHub Actions. |
| **16. PR Diff Security Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_pr_diff [--pr PR_NUM]` | Scan diffs for leaked secrets, anti-patterns, & `AGENTS.md` compliance. |
| **17. Repo Topology Map** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py repo_map` | Discover workspace git remotes and submodules. |
| **18. Conflict Analyzer** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py resolve_conflicts` | Scan working tree for git conflict markers (`<<<<<<<`) and extract RAG context. |
| **19. History Formatter** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_history [--base B]` | Aggregate unpushed commits into a single provenance-tagged commit message. |
| **20. Architecture Mermaid** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py export_architecture_mermaid` | Generate Mermaid JS codebase architecture diagram (`graph TD`). |
| **21. Benchmark Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py benchmark_audit` | Measure domain test duration and performance metrics. |
| **22. Skill Health Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_skills` | Validate YAML frontmatter & SKILL.md integrity across all skills. |
| **23. Dependency Security** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_security_dependencies` | Scan `requirements.txt` and `package.json` for unpinned dependencies or risks. |
| **24. Bloat Detector** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py detect_bloat` | Audit Python codebase for deep nesting (>=5 levels) & over-engineering. |
| **25. Visual Showcase Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py visual_showcase_audit` | Audit `docs/ux_journey/` assets, README visual links, and detect orphan screenshots. |
| **26. Bridge Self-Test** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py self_test` | Run zero-dependency assert-based unit tests for all CLI bridge functions. |
| **27. Blast Radius Analyzer** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py blast_radius --file F` | AST-level cognitive dependency & ripple-effect mapping across modules & SQLite tables. |
| **28. Adversarial Crucible** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py crucible` | Red Team vs Blue Team automated fuzzing & injection exploit arena. |
| **29. Darwin Auto-Optimizer** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py darwin_optimize` | Zero-dependency AST algorithmic complexity evolver and O(N^2) loop detector. |
| **30. Merkle Causal Inspector** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py explain_line --file F --line L` | Cryptographic Merkle causal chain line provenance proof and zero-hallucination audit. |
| **31. The Ghost Loop** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py ghost_loop --prompt P [--pr]` | Autonomous 1-click spec-to-PR self-healing flywheel. |
| **32. Client Snapshot Showcase** | `python .agents/skills/neuro-copilot/scripts/snapshot_bridge.py full_showcase` | 1-click end-to-end full client showcase generation (scan -> script -> HTML deck -> README sync). |


---

## Automated Visual Showcase & UX Journey Protocol (Zero-Drift UI Documentation)

When documenting user experience journeys, capturing high-definition interface screenshots, or verifying front-end visual regression:

### 1. Independent Functionality Search (Discovery Sweep)
Before designing or executing visual capture scripts, perform a complete discovery sweep to ensure no hidden tabs, modal states, or controls are omitted:
- **Codebase Grep Audit**: Search for routing declarations (`<Route`, `path=`, `BrowserRouter`), tab/state controllers (`useState('grid')`, `activeTab`, `currentView`), and modal trigger handles (`setSelectedElement`, `openPanel`, `showModal`).
- **URL State & Query Parameter Audit**: Verify parameters altering UI layouts (`useSearchParams`, `window.location.search`, `?theme=dark`, `?lang=es`).
- **Dependency-Based Visual Audit**: Check `package.json` for dynamic renderers (Canvas, 3D engines, plotting libraries like `chart.js`, `three.js`, `lucide-react`) and confirm DOM mounting hooks.
- **Static Visual Asset Discovery**: Inspect `src/assets/` and `public/` for logos, badges, and illustrations.
- **Feature Matrix Cataloging**: Map trigger selectors (`button:has-text("Search")`), expected content, and hover/transition states.

### 2. Universal Visual App Audit Checklist
- [ ] **Core Routing & Navigation**: Map all root paths (`/`, `/dashboard`, `/search`, `/settings`).
- [ ] **Interactive States & Sub-Panels**: Catalog tab switches, sidebars, drawer panels, filter dropdowns, and modal dialogs.
- [ ] **External & Embedded Media**: Inject stylized local mock placeholders for external embeds (YouTube, Vimeo, cross-origin iframes) to prevent headless timeouts.
- [ ] **Internationalization & Localization**: Verify layouts across configured languages.
- [ ] **Multi-Theme Contrast Snapshots**: Capture key views in both Light and Dark themes to verify contrast and readability.
- [ ] **Gated & Authenticated Views**: Inject pre-authenticated session state (cookies/localStorage) to bypass login screens.
- [ ] **Keyboard Focus & Hover Popovers**: Document focus rings for accessibility (a11y) and pointer hover tooltips.

### 3. Onboarding Sequence & Automation Engine
1. **Directory Structure**: Store visual assets sequentially under `docs/ux_journey/` (e.g. `01_dashboard.png`, `02_search.png`).
2. **Capture Script**: Write a lightweight Playwright script at `scripts/capture_ux_journey.mjs` tailored to the mapped feature matrix.
3. **Execution & CI**: Add script to `package.json` (`"capture-journey": "node scripts/capture_ux_journey.mjs"`).

### 4. Visual Capture Best Practices
- **Dynamic Element Masking & Time Stabilization**: Freeze ticking clocks, timers, and random API quotes via `page.evaluate()` to prevent Git diff noise.
- **Responsive Multi-Viewport Captures**: Capture views in Desktop (`1440x900`) and Mobile (`375x812`) viewports.
- **Font Loading & Transition Synchronization**: Block screenshot capture until `document.fonts.ready` resolves and CSS animations settle (`await delay(500)`).
- **Anti-Aliasing & Rendering Stabilization**: Apply pixel tolerance (`maxDiffPixels: 100`, `maxDiffPixelRatio: 0.02`) for cross-platform compatibility.
- **Security & PII Redaction**: Mask live API tokens, passwords, database connection strings, emails, and private identities before capture.
- **Console & Network Error Audits**: Attach event listeners (`page.on('pageerror')`, `page.on('requestfailed')`) to fail runs on unhandled runtime exceptions.
- **Targeted Element vs Full-Page Screenshots**: Use full-page captures for layouts and targeted locator captures (`locator.screenshot()`) for standalone widgets.

### 5. Documentation Integrity & Quality Control Gates
- **Broken Image Link Guard**: Verify that all image paths referenced in `README.md` (`![Title](docs/ux_journey/filename.png)`) exist on disk.
- **Orphan Screenshot Pruning**: Detect and clean unreferenced assets in `docs/ux_journey/`.
- **Zero Git Diff Noise**: Re-running capture on an unmodified codebase must yield zero git diff.
- **Audit Tool**: Run `python .agents/skills/neuro-copilot/scripts/github_bridge.py visual_showcase_audit` to assert documentation integrity.

---

## Complete End-to-End Operational Workflow Guide

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                CLOSED-LOOP TRI-ENGINE DOMINANCE WORKFLOW                    │
 └─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 1: FLIGHT PLAN & CONTEXT TRIANGULATION                              │
  │ 1. Flight Plan: python .../github_bridge.py copilot --prompt "..."        │
  │ 2. Health Check: python .../github_bridge.py tri_engine_health             │
  │ 3. Vector Search: neuro_search (query architectural rules)                │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 2: TASK MASTER ORCHESTRATION & BRANCHING                            │
  │ 1. Tududi Task Log: create_task / add_subtask under Project #13           │
  │ 2. Git Feature Branch: git checkout -b feat/task-<tududi_id>-description   │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 3: DEPENDENCY-EFFICIENT IMPLEMENTATION & COMMIT PROVENANCE           │
  │ 1. Minimal Working Diff: YAGNI standard library implementation             │
  │ 2. Automated Commit: python .../github_bridge.py auto_commit              │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 4: 1-CLICK PIPELINE PASS & PR DOMINANCE                              │
  │ 1. Full Audit: python .../github_bridge.py run_full_pipeline              │
  │ 2. Security, Bloat & Visual Audit: audit_pr_diff + visual_showcase_audit   │
  │ 3. Open Pull Request: python .../github_bridge.py create_pr               │
  │ 4. Self-Healing CI: diagnose_ci -> neuro_search -> apply fix              │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 5: INGESTION, RELEASE SYNTHESIS & COMPLETION                         │
  │ 1. UX Journey Showcase: Capture screenshots & sync README.md visual links  │
  │ 2. Ingest Git History: python .../neuro_bridge.py ingest_git_history      │
  │ 3. Release Notes: python .../github_bridge.py generate_release_notes      │
  │ 4. Tududi Complete: complete_task (status: 2) with PR # and SHA-256 hash  │
  └───────────────────────────────────────────────────────────────────────────┘
```

---

## References & Templates
- PR Template: [`references/PR_TEMPLATE.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/references/PR_TEMPLATE.md)
- Commit Conventions: [`references/COMMIT_CONVENTION.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/references/COMMIT_CONVENTION.md)
- GitHub CLI Bridge: [`scripts/github_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/github_bridge.py)
- Neuro Bridge: [`scripts/neuro_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/neuro_bridge.py)
- Tududi Bridge: [`scripts/tududi_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/tududi_bridge.py)
- Snapshot Bridge: [`scripts/snapshot_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/snapshot_bridge.py)
