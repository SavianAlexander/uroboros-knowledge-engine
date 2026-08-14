---
name: neuro-copilot
description: The master integration skill for bridging the Uroboros Knowledge Engine (Neuro), the Tududi Task Master, and GitHub CLI / Git Provenance into a unified, dependency-efficient automated engineering workflow. Trigger this skill whenever you need to query local knowledge, orchestrate tasks, execute git/GitHub operations, run CI/CD health checks, audit PR diffs, analyze merge conflicts, format commit history, benchmark performance, detect codebase bloat, scan security dependencies, synthesize flight plans, or render executive dashboards.
---

# Neuro Co-Pilot (Enterprise Tri-Engine Dominance Suite)

This skill dictates how you (the AI Agent) must interact with the **Neuro MCP Server** (`neuro-mcp`), the **Tududi MCP Server** (`tududi`), and the **GitHub CLI / Git Provenance Subsystem** (`gh` CLI & standard git commands) in tandem to execute closed-loop, dependency-efficient automated engineering workflows.

---

## The Tri-Engine Mandate & Autonomous Subagent Protocol

You have access to three primary orchestration engines:
1. **Neuro (`neuro-mcp` & Local RAG Brain)**: The local AI brain. Stores semantic vector embeddings, FTS5 keyword indexes, Binary ColBERT reranking matrices, Knowledge Graph wikilinks, git commit provenance, and cryptographic document provenance signatures.
2. **Tududi (`tududi`)**: The Task Master & Execution Auditor. Serves as the single source of truth for all project execution, subtask checklists, and habit tracking under Project #13 (*Neuro Alexander*).
3. **GitHub (`gh` CLI & Git)**: Codebase Dominance & CI/CD Control. Manages Pull Requests (`gh pr`), Issue synchronization (`gh issue`), GitHub Actions workflow monitoring (`gh run`), Git commit provenance, diff security auditing (`audit_pr_diff`), conflict resolution (`resolve_conflicts`), dependency security scanning (`audit_security_dependencies`), bloat detection (`detect_bloat`), terminal dashboard rendering (`dashboard`), and release tagging (`gh release`).

### 🤖 Autonomous Subagent Delegation Protocol (`neuro-copilot-agent`)

When `/neuro-copilot` is activated for deep codebase research, multi-file auditing, or vault document synthesis:
- **Format Prompt**: Run `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_agent_prompt --task "..."` to generate the strict execution constraints.
- **Define / Invoke Subagent**: Use `define_subagent` and `invoke_subagent` to spawn a specialized subagent named `neuro-copilot-agent` (Role: `Local RAG Brain Co-Pilot & Codebase Researcher`).
- **Token Efficiency Standard**: The subagent executes context-heavy lookups using `query_local_brain` (`python .agents/skills/neuro-copilot/scripts/github_bridge.py query_local_brain --query "..."`), `neuro_search`, and file reading in a separate isolated conversation, saving parent model tokens.
- **Executive Synthesis**: The subagent synthesizes findings and reports back with structured Markdown analysis.

---

## Standardized Modular Bridge Architecture (3 Dedicated CLI Bridges)

The skill uses 3 modular, zero-dependency Python CLI bridge scripts located in `scripts/`:

1. **Neuro Knowledge Engine Bridge (`scripts/neuro_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py query --text "..."`: Query local RAG brain with HyDE expansion.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest --path "..."`: Ingest document or directory into vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py ingest_git_history --limit 20`: Index recent git commit provenance into vault.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py stats`: Audit knowledge vault size & chunk metrics.
   - `python .agents/skills/neuro-copilot/scripts/neuro_bridge.py self_test`: Run Neuro bridge self-tests.

2. **Tududi Task Master Bridge (`scripts/tududi_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py list`: Fetch active Tududi tasks for Project #13.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py metrics`: Query project completion stats & audit metrics.
   - `python .agents/skills/neuro-copilot/scripts/tududi_bridge.py self_test`: Run Tududi bridge self-tests.

3. **GitHub & Git Provenance Bridge (`scripts/github_bridge.py`)**:
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py copilot --prompt "..."`: Synthesize full Engineering Flight Plan.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py tri_engine_health`: Run 4-engine unified health scorecard.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py auto_commit --scope feat --desc "..."`: Staged-files SHA-256 commit with provenance.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py dashboard`: Render executive terminal dashboard.
   - `python .agents/skills/neuro-copilot/scripts/github_bridge.py run_full_pipeline`: 1-click full Tri-Engine pipeline pass.

### Comprehensive Tri-Engine Command Matrix

| Command | Subcommand | Purpose |
| :--- | :--- | :--- |
| **1. Flight Plan Generator** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py copilot --prompt "..."` | Synthesize developer intent into structured engineering plan using local brain. |
| **2. Tri-Engine Health** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py tri_engine_health` | Unified diagnostic across Neuro, Tududi, GitHub, and Architecture Doctor. |
| **3. Auto Commit Provenance** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py auto_commit --scope S --desc D` | Staged-files Merkle tree digest calculation and auto-commit with task tag. |
| **4. Subagent Prompt Builder** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_agent_prompt --task T` | Format standardized system prompt for autonomous subagent delegation. |
| **5. Executive Dashboard** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py dashboard` | Render ASCII terminal dashboard summarizing git state, `gh` auth, hooks, & CI workflows. |
| **6. Full Pipeline Pass** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py run_full_pipeline` | Execute 1-click full Tri-Engine pipeline (dashboard -> health -> diff audit -> bloat -> sec -> conflict -> self test -> domain test). |
| **7. Health Check** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py check_health` | Audit git status, `gh` auth, active PRs, issues, git hooks, CI workflows, and CI runs. |
| **8. Issue Sync** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py sync_issues` | Fetch open GitHub Issues formatted as Tududi Task import JSON. |
| **9. CI Diagnosis** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py diagnose_ci [--run-id ID]` | Auto-detect failed Actions runs, extract tracebacks, & build `neuro_search` query. |
| **10. Provenance Tag** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py provenance_tag --scope S --desc D --task T` | Compute SHA-256 hash of staged files & format executive commit string. |
| **11. PR Automation** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py create_pr --title T --task T --hash H` | Generate & open a Pull Request with embedded Tududi checklists. |
| **12. Hook Guard** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py install_hooks` | Install `.git/hooks/commit-msg` guard enforcing Tududi/Neuro provenance tags. |
| **13. CI Workflow Setup** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py install_ci_workflow` | Generate `.github/workflows/neuro_copilot_ci.yml` for GitHub Actions. |
| **14. PR Diff Security Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_pr_diff [--pr PR_NUM]` | Scan diffs for leaked secrets, anti-patterns, & `AGENTS.md` compliance. |
| **15. Repo Topology Map** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py repo_map` | Discover workspace git remotes and submodules. |
| **16. Conflict Analyzer** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py resolve_conflicts` | Scan working tree for git conflict markers (`<<<<<<<`) and extract RAG context. |
| **17. History Formatter** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py format_history [--base B]` | Aggregate unpushed commits into a single provenance-tagged commit message. |
| **18. Architecture Mermaid** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py export_architecture_mermaid` | Generate Mermaid JS codebase architecture diagram (`graph TD`). |
| **19. Benchmark Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py benchmark_audit` | Measure domain test duration and performance metrics. |
| **20. Skill Health Audit** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_skills` | Validate YAML frontmatter & SKILL.md integrity across all skills. |
| **21. Dependency Security** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py audit_security_dependencies` | Scan `requirements.txt` and `package.json` for unpinned dependencies or risks. |
| **22. Bloat Detector** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py detect_bloat` | Audit Python codebase for deep nesting (>=5 levels) & over-engineering. |
| **23. Release Synthesizer** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py generate_release_notes [--tag T] [--publish]` | Format Markdown release notes & optionally publish GitHub Release (`gh release create`). |
| **24. Bridge Self-Test** | `python .agents/skills/neuro-copilot/scripts/github_bridge.py self_test` | Run zero-dependency assert-based unit tests for all CLI bridge functions. |

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
  │ 2. Security & Bloat Audit: audit_pr_diff + detect_bloat                    │
  │ 3. Open Pull Request: python .../github_bridge.py create_pr               │
  │ 4. Self-Healing CI: diagnose_ci -> neuro_search -> apply fix              │
  └───────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ PHASE 5: INGESTION, RELEASE SYNTHESIS & COMPLETION                         │
  │ 1. Ingest Git History: python .../neuro_bridge.py ingest_git_history      │
  │ 2. Release Notes: python .../github_bridge.py generate_release_notes      │
  │ 3. Tududi Complete: complete_task (status: 2) with PR # and SHA-256 hash  │
  └───────────────────────────────────────────────────────────────────────────┘
```

---

## References & Templates
- PR Template: [`references/PR_TEMPLATE.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/references/PR_TEMPLATE.md)
- Commit Conventions: [`references/COMMIT_CONVENTION.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/references/COMMIT_CONVENTION.md)
- GitHub CLI Bridge: [`scripts/github_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/github_bridge.py)
- Neuro Bridge: [`scripts/neuro_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/neuro_bridge.py)
- Tududi Bridge: [`scripts/tududi_bridge.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/.agents/skills/neuro-copilot/scripts/tududi_bridge.py)
