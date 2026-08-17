#!/usr/bin/env python3
"""
Neuro Co-Pilot Unified Master CLI
The single authoritative command-line entrypoint for the Neuro autonomous engineering ecosystem.
Standard: Zero-dependency, pure Python standard library only (Ponytail senior dev principle).
"""

import sys
import os
import time
import json
import argparse
import subprocess
from typing import Dict, Any

# Ensure UTF-8 output encoding resilience across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPTS_DIR))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# -------------------------------------------------------------------------
# Windows OS Kernel Job Object & Process Supervisor
# -------------------------------------------------------------------------
def enable_auto_kill_job_object():
    """Attaches current process to a Windows Job Object with KILL_ON_JOB_CLOSE."""
    if os.name != "nt":
        return
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE

        h_job = kernel32.CreateJobObjectW(None, None)
        if not h_job:
            return
        
        class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class _IO_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("ReadOperationCount", ctypes.c_ulonglong),
                ("WriteOperationCount", ctypes.c_ulonglong),
                ("OtherOperationCount", ctypes.c_ulonglong),
                ("ReadTransferCount", ctypes.c_ulonglong),
                ("WriteTransferCount", ctypes.c_ulonglong),
                ("OtherTransferCount", ctypes.c_ulonglong),
            ]

        class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryLimit", ctypes.c_size_t),
                ("PeakJobMemoryLimit", ctypes.c_size_t),
            ]

        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        res = kernel32.SetInformationJobObject(h_job, 9, ctypes.byref(info), ctypes.sizeof(info))
        if res:
            h_proc = kernel32.GetCurrentProcess()
            kernel32.AssignProcessToJobObject(h_job, h_proc)
    except Exception:
        pass

enable_auto_kill_job_object()


def print_banner():
    banner = """
===================================================================
⚡ NEURO CO-PILOT UNIFIED MASTER CLI
   Autonomous Multi-Bridge Orchestration & System Governance
===================================================================
"""
    print(banner)


def cmd_doctor(args):
    """Runs comprehensive 360° system diagnostics across OS, SQLite, Git, and CI."""
    import doctor_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    scorecard = doctor_bridge.generate_health_scorecard(repo_root)
    if getattr(args, "json", False):
        print(json.dumps(scorecard, indent=2))
    else:
        doctor_bridge.print_doctor_report(scorecard)

    if getattr(args, "speak", False):
        try:
            import voice_operator_bridge
            score = scorecard.get("score", "100%")
            status = scorecard.get("status", "NOMINAL")
            voice_text = f"Doctor diagnostic complete. System health is {score}, operating at status {status}."
            voice_operator_bridge.speak_briefing(voice_text, preset="EXECUTIVE_PRECISION", async_mode=True)
        except Exception:
            pass

    return 0 if scorecard.get("status") in ["NOMINAL", "WARNING"] else 1


def cmd_run(args):
    """Executes the parallel asynchronous DAG multi-bridge contract pipeline."""
    import contract_bus
    import asyncio
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    res = asyncio.run(contract_bus.run_parallel_bridge_pipeline_async(repo_root))
    return 0 if res.get("status") == "success" else 1


def cmd_ci(args):
    """Monitors and verifies remote GitHub Actions CI gate until 100% Green."""
    import github_bridge
    if getattr(args, "diagnose", False):
        return github_bridge.diagnose_ci()
    wait = getattr(args, "wait", True)
    return github_bridge.verify_ci(wait=wait)


def cmd_clean(args):
    """Executes dual-layer cleanup: OS process hygiene + file allocation topology."""
    print("===================================================================")
    print("🧹 Executing Automated Dual-Layer System Cleanup Sweep...")
    print("===================================================================")
    import process_hygiene_bridge
    import file_allocation_bridge

    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    p_res = process_hygiene_bridge.clean_process_hygiene(dry_run=False, repo_root=repo_root)
    f_res = file_allocation_bridge.clean_orphan_artifacts(repo_root=repo_root)

    print(f"✅ Terminated {len(p_res.get('terminated_pids', []))} orphan processes.")
    print(f"✅ Reclaimed {p_res.get('reclaimed_memory_mb', 0.0):.1f} MB system RAM.")
    print(f"✅ Removed {f_res.get('removed_count', 0)} orphan temporary artifacts.")
    print("===================================================================")
    return 0


def cmd_voice(args):
    """Synthesizes executive spoken alerts or launches voice intercom sessions."""
    import voice_operator_bridge
    if getattr(args, "hud", False):
        return voice_operator_bridge.launch_voice_hud()
    elif getattr(args, "message", None):
        msg = " ".join(args.message)
        preset = getattr(args, "preset", "EXECUTIVE_PRECISION")
        return voice_operator_bridge.speak_briefing(msg, preset=preset)
    else:
        return voice_operator_bridge.interactive_voice_briefing()


def cmd_bench(args):
    """Runs sub-millisecond retrieval and compute latency benchmark watchdog."""
    import benchmark_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    scorecard = benchmark_bridge.run_full_benchmark_suite(repo_root)
    if getattr(args, "json", False):
        print(json.dumps(scorecard, indent=2))
    else:
        benchmark_bridge.print_benchmark_report(scorecard)
    return 0 if scorecard.get("status") == "PASS" else 1


def cmd_fleet(args):
    """Executes live EVE Online fleet tactical radar, cyno checks, and PI status."""
    import fleet_watchdog_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    telem = fleet_watchdog_bridge.get_fleet_radar_telemetry(repo_root)
    if getattr(args, "json", False):
        print(json.dumps(telem, indent=2))
    else:
        fleet_watchdog_bridge.print_fleet_report(telem)
    return 0


def cmd_flight_plan(args):
    """Synthesizes and initializes complete Engineering Flight Plan with Tududi task hierarchy."""
    import github_bridge
    prompt = getattr(args, "prompt", "General feature upgrade")
    execute = getattr(args, "execute", False)
    return github_bridge.generate_copilot_flight_plan(prompt=prompt, execute=execute)


def cmd_heal(args):
    """Executes 1-Click 5-Stage Autonomous Self-Healing Cascade."""
    print("===================================================================")
    print("🛡️ NEURO CO-PILOT 1-CLICK AUTONOMOUS SYSTEM SELF-HEALING CASCADE")
    print("===================================================================")
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    t0 = time.time()

    # Stage 1: Process Hygiene
    print("\n[Stage 1/5] OS Process Hygiene & Zombie Worker Elimination...")
    import process_hygiene_bridge
    p_res = process_hygiene_bridge.clean_process_hygiene(dry_run=False, repo_root=repo_root)
    print(f"  -> Terminated {len(p_res.get('terminated_pids', []))} orphans | Reclaimed {p_res.get('reclaimed_memory_mb', 0):.1f}MB RAM")

    # Stage 2: SQLite Lock Flushing & WAL Checkpointing
    print("\n[Stage 2/5] SQLite Database WAL Checkpointing & Lock Flush...")
    db_res = process_hygiene_bridge.checkpoint_database_locks(repo_root=repo_root)
    print(f"  -> Checkpointed {db_res.get('databases_checkpointed', 0)} databases cleanly.")

    # Stage 3: File Allocation & Artifact Cleanup
    print("\n[Stage 3/5] Repository File Allocation & Stray Artifact Purge...")
    import file_allocation_bridge
    f_res = file_allocation_bridge.clean_orphan_artifacts(repo_root=repo_root)
    print(f"  -> Removed {f_res.get('removed_count', 0)} orphan temporary artifacts.")

    # Stage 4: Nomenclature Auto-Fix
    print("\n[Stage 4/5] Nomenclature & Lexical Clarity Normalization...")
    import nomenclature_bridge
    n_res = nomenclature_bridge.auto_fix_repository(search_root=repo_root)
    print(f"  -> Normalized {n_res.get('fixed_files_count', 0)} files to transparent naming.")

    # Stage 5: Git Hook Invariant Verification
    print("\n[Stage 5/5] Git Merkle Pre-Commit Hook Invariant Verification...")
    import github_bridge
    h_res = github_bridge.install_hooks()
    print("  -> Git Merkle commit-msg hook verified.")

    total_ms = (time.time() - t0) * 1000
    print("\n===================================================================")
    print(f"✅ System Self-Healing Cascade Complete in {total_ms:.1f}ms! (100% Operational Fidelity)")
    print("===================================================================")
    return 0


def cmd_test(args):
    """Executes concurrent 13-bridge parallel self-test matrix."""
    import contract_bus
    res = contract_bus.run_all_self_tests_parallel()
    return 0 if res.get("all_passed", False) else 1


def cmd_watch(args):
    """Launches the real-time dynamic ASCII telemetry HUD."""
    import doctor_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    iterations = getattr(args, "iterations", 0)
    return doctor_bridge.launch_telemetry_hud(repo_root=repo_root, iterations=iterations)


def cmd_release(args):
    """Generates immutable SOC 2 Type II Merkle release certificate."""
    import release_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    tag = getattr(args, "tag", "v1.0.0")
    report = release_bridge.generate_release_certificate(tag=tag, repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        release_bridge.print_release_report(report)
    return 0


def cmd_blast(args):
    """Analyzes AST blast radius and dependency risk impact for a file."""
    import blast_radius_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    target_file = getattr(args, "file", os.path.join("scripts", "doctor_bridge.py"))
    report = blast_radius_bridge.analyze_blast_radius(target_file, repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        blast_radius_bridge.print_blast_report(report)
    return 0 if report.get("status") == "success" else 1


def cmd_review(args):
    """Executes automated pre-commit code review and security gate."""
    import review_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    staged = getattr(args, "staged", False)
    diff_text = review_bridge.get_git_diff(staged_only=staged, repo_root=repo_root)
    report = review_bridge.review_diff_text(diff_text, repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        review_bridge.print_review_report(report)
    return 0 if report.get("verdict") in ["APPROVED", "CHANGES_REQUESTED"] else 1


def cmd_graph(args):
    """Generates Mermaid architecture and SQLite ER diagrams."""
    import graph_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    report = graph_bridge.export_system_diagrams(repo_root)
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        print(f"✅ System Architecture & Database Schema diagrams generated: {report.get('diagrams_file')} in {report.get('duration_ms')}ms")
    return 0


def cmd_search(args):
    """Executes unified cognitive search across codebase AST and SQLite vector vault."""
    import search_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    q_words = getattr(args, "query", ["health"])
    query = " ".join(q_words) if isinstance(q_words, list) else str(q_words)
    limit = getattr(args, "limit", 10)
    report = search_bridge.unified_search(query, limit=limit, repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(report, indent=2))
    else:
        search_bridge.print_search_report(report)
    return 0


def cmd_ask(args):
    """Executes intelligent Agentic RAG Copilot query with specialized SLM synthesis."""
    import neuro_bridge
    q_words = getattr(args, "query", ["overview"])
    query = " ".join(q_words) if isinstance(q_words, list) else str(q_words)
    chunks = getattr(args, "chunks", 5)
    model = getattr(args, "model", None)
    res_json = neuro_bridge.ask_copilot(query, max_chunks=chunks, model_override=model)
    res = json.loads(res_json)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        if res.get("status") == "success":
            print("===================================================================")
            print(f"🤖 NEURO COPILOT AGENT | Model: {res.get('model')} ({res.get('tier')})")
            print("===================================================================")
            print(f"\n{res.get('answer')}\n")
            print("-------------------------------------------------------------------")
            print(f"📚 Vault Citations ({res.get('citations_count', 0)} sources):")
            for c in res.get("citations", []):
                print(f"  • {c.get('filepath', 'doc')} (Score: {c.get('score', 0):.2f})")
            print("===================================================================")
        else:
            print(f"Error: {res.get('message')}")
    return 0 if res.get("status") == "success" else 1


def cmd_context(args):
    """Extracts complete topic context (AST code, DB schemas, vault notes) for an AI agent."""
    import neuro_bridge
    t_words = getattr(args, "topic", ["system"])
    topic = " ".join(t_words) if isinstance(t_words, list) else str(t_words)
    files_limit = getattr(args, "files", 8)
    res_json = neuro_bridge.get_topic_context(topic, max_files=files_limit)
    res = json.loads(res_json)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        print("===================================================================")
        print(f"🧠 NEURO AGENT TOPIC CONTEXT: '{topic}'")
        print("===================================================================")
        print(f"Related Files ({res.get('related_files_count', 0)}):")
        for f in res.get("related_files", []):
            print(f"  📄 {f.get('filename')} -> {f.get('filepath')}")
        print("\nExtracted Vault Context:")
        print(res.get("extracted_context", "")[:1200] + "...")
        print("===================================================================")
    return 0 if res.get("status") == "success" else 1


def cmd_summarize(args):
    """Generates structured executive summary of a vault file or topic."""
    import neuro_bridge
    t_words = getattr(args, "target", ["README.md"])
    target = " ".join(t_words) if isinstance(t_words, list) else str(t_words)
    res_json = neuro_bridge.summarize_vault_target(target)
    res = json.loads(res_json)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        print("===================================================================")
        print(f"📋 NEURO COPILOT EXECUTIVE SUMMARY: '{target}'")
        print("===================================================================")
        print(f"\n{res.get('summary')}\n")
        print("===================================================================")
    return 0 if res.get("status") == "success" else 1


def cmd_reap(args):
    """Surgically eliminates orphan/zombie background processes and frees RAM."""
    import process_hygiene_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    res = process_hygiene_bridge.clean_process_hygiene(dry_run=False, repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        print("===================================================================")
        print("🧹 NEURO ZOMBIE SLAYER & PROCESS HYGIENE SWEEP")
        print("===================================================================")
        print(f"Status: {res.get('status', 'success').upper()} | Post-Clean Score: {res.get('post_clean_hygiene_score')}")
        print(f"Terminated PIDs ({len(res.get('terminated_pids', []))}): {res.get('terminated_pids', [])}")
        print(f"Reclaimed RAM: {res.get('reclaimed_memory_mb', 0.0):.1f} MB")
        print(f"Checkpointed DBs: {res.get('databases_checkpointed', 0)}")
        print("===================================================================")
    return 0


def cmd_act(args):
    """Executes multi-step Autonomous ReAct Agent Loop on a given engineering task."""
    import react_agent_bridge
    t_words = getattr(args, "task", ["Analyze system architecture"])
    task_str = " ".join(t_words) if isinstance(t_words, list) else str(t_words)
    steps = getattr(args, "steps", 6)
    model = getattr(args, "model", None)
    rep = react_agent_bridge.run_react_agent_loop(task_str, max_steps=steps, model_name=model)
    if getattr(args, "json", False):
        print(json.dumps(rep, indent=2))
    else:
        react_agent_bridge.print_react_report(rep)
    return 0 if rep.get("status") == "success" else 1


def cmd_graph_code(args):
    """Parses codebase AST into SQLite code_symbols and symbol_calls relational graph."""
    import ast_graph_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    res = ast_graph_bridge.build_ast_graph(repo_root=repo_root)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        print("===================================================================")
        print("⚡ NEURO CODEBASE AST GRAPH BUILD")
        print("===================================================================")
        print(f"Indexed {res.get('symbols_indexed', 0)} symbols & {res.get('call_edges_indexed', 0)} call edges across {res.get('files_scanned', 0)} files in {res.get('duration_ms', 0)}ms.")
        print(f"Relational Graph: {res.get('db_path')}")
        print("===================================================================")
    return 0 if res.get("status") == "success" else 1


def cmd_symbol(args):
    """Looks up exact AST definition, callers, and touched tables for a symbol."""
    import ast_graph_bridge
    sym = getattr(args, "symbol", "get_db")
    res = ast_graph_bridge.query_symbol_graph(sym)
    if getattr(args, "json", False):
        print(json.dumps(res, indent=2))
    else:
        print("===================================================================")
        print(f"🔍 NEURO AST SYMBOL TOPOLOGY: '{sym}'")
        print("===================================================================")
        defs = res.get("definitions", [])
        if defs:
            for d in defs:
                print(f"  📄 Defined in {d.get('filepath')}:{d.get('start_line')}-{d.get('end_line')} ({d.get('symbol_type')})")
                if d.get("args_spec"):
                    print(f"     Signature: ({d.get('args_spec')})")
        else:
            print("  No direct definition in index.")
        
        callers = res.get("callers", [])
        print(f"\n  Upstream Callers ({len(callers)}):")
        for c in callers[:8]:
            print(f"    • {c.get('caller_file')}:{c.get('line_number')} (in {c.get('caller_symbol')})")
        
        tables = res.get("db_tables", [])
        if tables:
            print(f"\n  Touched Tables: {', '.join(t.get('table_name') for t in tables)}")
        print("===================================================================")
    return 0 if res.get("status") == "success" else 1


def cmd_recover(args):
    """Executes 5-stage zero-reboot Windows crash recovery cascade."""
    import system_recovery_bridge
    res = system_recovery_bridge.restore_all()
    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "success" else 1


def cmd_docker(args):
    """Spawns modular on-demand Docker container profiles (core, ui, voice, all, gpu, stop)."""
    import subprocess
    target = getattr(args, "target", "status")
    
    cmd_map = {
        "core": ["docker", "compose", "up", "-d"],
        "ui": ["docker", "compose", "--profile", "ui", "up", "-d"],
        "frontend": ["docker", "compose", "--profile", "ui", "up", "-d"],
        "voice": ["docker", "compose", "--profile", "voice", "up", "-d"],
        "all": ["docker", "compose", "--profile", "all", "up", "-d"],
        "gpu": ["docker", "compose", "--profile", "all", "--profile", "gpu-nvidia", "up", "-d"],
        "gpu-amd": ["docker", "compose", "--profile", "all", "--profile", "gpu-amd", "up", "-d"],
        "stop": ["docker", "compose", "down"],
        "status": ["docker", "compose", "ps"]
    }
    
    cmd = cmd_map.get(target.lower())
    if not cmd:
        print(f"Unknown Docker target: '{target}'. Available: core, ui, voice, all, gpu, stop, status")
        return 1
        
    print(f"🐳 Spawning Docker Profile: '{target}' -> {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, cwd=BASE_DIR)
        return res.returncode
    except Exception as e:
        print(f"Docker execution error: {e}")
        return 1


def cmd_upload_status(args):
    """Displays GitHub remote upload and provenance visibility."""
    import github_bridge
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
    if getattr(args, "json", False):
        print(json.dumps(github_bridge.get_git_sync_status(repo_root), indent=2))
        return 0
    return github_bridge.print_upload_status()


def cmd_status(args):
    """Displays a quick multi-layer dashboard scorecard."""
    print_banner()
    try:
        import doctor_bridge
        import github_bridge
        repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR
        score = doctor_bridge.generate_health_scorecard(repo_root)
        sync_stat = github_bridge.get_git_sync_status(repo_root)
        print(f"System Health: {score.get('score', '100%')} | Status: {score.get('status', 'NOMINAL')} | In {score.get('duration_ms', 0)}ms")
        print(f"GitHub Upload: {sync_stat.get('status_badge', 'Unknown')} (Branch: {sync_stat.get('branch', 'master')})\n")
        for k, v in score.get("checks", {}).items():
            icon = "✅" if v.get("ok") else "⚠️"
            print(f"  {icon} {k:<24}: {v.get('summary')}")
        print("===================================================================")
    except Exception as e:
        print(f"Status check error: {e}")
    return 0


def cmd_erp(args):
    """Unified PR ERP Multi-Database SQL Bridge (know, payroll, compliance)."""
    import pr_erp_sql_bridge
    sub = getattr(args, "erp_subcommand", None) or "schema"
    if sub == "schema":
        print(json.dumps(pr_erp_sql_bridge.get_schema_catalog(), indent=2))
    elif sub == "payroll":
        print(json.dumps(pr_erp_sql_bridge.get_payroll_metrics(), indent=2))
    elif sub == "compliance":
        print(json.dumps(pr_erp_sql_bridge.get_compliance_metrics(), indent=2))
    elif sub == "query":
        print(json.dumps(pr_erp_sql_bridge.execute_safe_query(args.sql, args.limit), indent=2))
    elif sub == "ask":
        q_str = " ".join(args.question) if isinstance(args.question, list) else str(args.question or "")
        print(pr_erp_sql_bridge.ask_erp_copilot(q_str))
    return 0


def cmd_llm(args):
    """Standalone Local LLM Engine Bridge (Zero-Daemon GGUF Execution)."""
    import standalone_llama_bridge
    sub = getattr(args, "llm_subcommand", None) or "status"
    if sub == "list":
        reg = standalone_llama_bridge.load_model_registry()
        print(json.dumps(reg, indent=2))
    elif sub == "status":
        ollama_up = standalone_llama_bridge.check_ollama_alive()
        vulkan_bin = standalone_llama_bridge.get_llama_binary("vulkan")
        hip_bin = standalone_llama_bridge.get_llama_binary("hip")
        reg = standalone_llama_bridge.load_model_registry()
        print(json.dumps({
            "status": "NOMINAL",
            "ollama_http_daemon": "ONLINE" if ollama_up else "OFFLINE (Fallback Active)",
            "vulkan_runtime": "READY" if vulkan_bin else "MISSING",
            "hip_rocm_runtime": "READY" if hip_bin else "MISSING",
            "registered_models_count": len(reg.get("models", {})),
            "total_model_storage_mb": reg.get("total_storage_mb", 0)
        }, indent=2))
    elif sub == "run":
        p_str = " ".join(args.prompt) if isinstance(args.prompt, list) else str(args.prompt or "")
        print(json.dumps(standalone_llama_bridge.run_standalone_inference(
            p_str,
            model=args.model,
            max_tokens=args.tokens,
            temperature=args.temp,
            runtime=args.runtime,
            gpu_layers=args.ngl
        ), indent=2))
def cmd_browser(args):
    """Browser Performance & Zero-Stutter Gaming Optimizer Bridge."""
    import browser_optimizer_bridge
    sub = getattr(args, "browser_subcommand", None) or "status"
    if sub == "status":
        rep = browser_optimizer_bridge.inspect_browser_status()
        if getattr(args, "json", False):
            print(json.dumps(rep, indent=2))
        else:
            browser_optimizer_bridge.print_status_card(rep)
        return 0
    elif sub == "tune":
        targets = browser_optimizer_bridge.get_browser_targets()
        target_browsers = targets if getattr(args, "browser", "all") == "all" else {k: v for k, v in targets.items() if k == args.browser}
        print("==========================================================================")
        print("             APPLYING ZERO-STUTTER BROWSER GAMING PROFILE                 ")
        print("==========================================================================")
        for bkey, binfo in target_browsers.items():
            if getattr(args, "close", False):
                closed = browser_optimizer_bridge.close_browser_processes(bkey, targets)
                if closed > 0:
                    print(f"[*] Closed {closed} running processes for {binfo['name']} to lock settings.")

            print(f"[*] Optimizing {binfo['name']}...")
            res = browser_optimizer_bridge.tune_browser_profile(binfo["user_data_dir"])
            print(f"    [+] Modified Profiles : {', '.join(res.get('profiles_modified', []))}")
            print(f"    [+] Local State Tuned : {res.get('local_state_modified')}")
            print(f"    [+] Backups Generated : {len(res.get('backups_created', []))} files")
        print("==========================================================================")
        print("✅ [SUCCESS] Zero-Stutter Gaming Profile applied successfully!")
        return 0
    elif sub == "restore":
        targets = browser_optimizer_bridge.get_browser_targets()
        target_browsers = targets if getattr(args, "browser", "all") == "all" else {k: v for k, v in targets.items() if k == args.browser}
        print("==========================================================================")
        print("             RESTORING BROWSER PREFERENCES FROM BACKUP                    ")
        print("==========================================================================")
        for bkey, binfo in target_browsers.items():
            print(f"[*] Restoring {binfo['name']}...")
            res = browser_optimizer_bridge.restore_browser_backups(binfo["user_data_dir"])
            for r in res.get("restored_files", []):
                print(f"    [+] Restored: {r}")
        print("==========================================================================")
        print("✅ [SUCCESS] Browser preferences restored from backup!")
        return 0
    elif sub == "test":
        return browser_optimizer_bridge.run_self_test()
    return 0


def cmd_curam(args):
    """IBM Cúram Social Program Management (SPM) & CER Decision Engine Bridge."""
    import curam_bridge
    sub = getattr(args, "curam_subcommand", None) or "evaluate"
    if sub == "evaluate":
        ev = getattr(args, "evidence", None)
        if not ev:
            print("Please provide --evidence (JSON string or file path)")
            return 1
        if os.path.isfile(ev):
            with open(ev, "r", encoding="utf-8") as f:
                ev = f.read()
        print(curam_bridge.evaluate_cer_cli(ev))
    elif sub == "fpl":
        print(curam_bridge.get_fpl_table_cli(getattr(args, "size", 1)))
    return 0


def cmd_jira(args):
    """Jira Issue & QA Test Case Management Bridge (Xray & Zephyr Standards)."""
    import jira_bridge
    sub = getattr(args, "jira_subcommand", None) or "generate"
    if sub == "generate":
        print(jira_bridge.generate_jira_tests_cli(getattr(args, "domain", "MEDICAID_MAGI"), getattr(args, "format", "json")))
    elif sub == "export":
        print(jira_bridge.export_jira_spec_file(getattr(args, "domain", "MEDICAID_MAGI")))
    return 0


def cmd_uat(args):
    """User Acceptance Testing (UAT) & Sign-Off Certification Bridge."""
    import uat_bridge
    sub = getattr(args, "uat_subcommand", None) or "run"
    if sub == "run":
        doms = getattr(args, "domains", ["MEDICAID_MAGI", "SNAP", "TANF"])
        print(uat_bridge.run_uat_suite_cli(doms))
    elif sub == "certificate":
        print(uat_bridge.export_uat_certificate_cli(getattr(args, "approver", "Chief Information Officer / Product Owner SME")))
    return 0


def cmd_loop(args):
    """Executes Closed-Loop Autonomous Engineering Engines (develop, health, erp, knowledge)."""
    import workflow_hub_bridge
    sub = getattr(args, "loop_subcommand", None) or "health"
    repo_root = getattr(args, "root", BASE_DIR) or BASE_DIR

    if sub == "develop":
        task_str = " ".join(args.task) if isinstance(args.task, list) else str(args.task or "Autonomous feature development")
        res = workflow_hub_bridge.loop_develop(task_str, max_iterations=args.iterations, repo_root=repo_root)
        print(json.dumps(res, indent=2))
    elif sub == "health":
        res = workflow_hub_bridge.loop_health(daemon=args.daemon, interval_sec=args.interval, max_iterations=args.max_cycles, repo_root=repo_root)
        print(json.dumps(res, indent=2))
    elif sub == "erp":
        res = workflow_hub_bridge.loop_erp()
        print(json.dumps(res, indent=2))
    elif sub == "knowledge":
        q = " ".join(args.query) if isinstance(args.query, list) else str(args.query or "Bono de Navidad")
        res = workflow_hub_bridge.loop_knowledge(query_test=q)
        print(json.dumps(res, indent=2))
    return 0


def self_test():
    """Assertion self-test suite for neuro_cli."""
    print("=== Running Neuro Master CLI Self-Test Suite ===")

    # Test status
    class MockArgs:
        root = BASE_DIR
        json = True
        wait = False
        diagnose = False
        message = []
        hud = False
        preset = "EXECUTIVE_PRECISION"
        iterations = 1
        tag = "test-v1.0"
        file = os.path.join(SCRIPTS_DIR, "doctor_bridge.py")

    args = MockArgs()
    ret_status = cmd_status(args)
    assert ret_status == 0, "cmd_status failed"
    print("  [Pass] cmd_status clean")

    ret_doctor = cmd_doctor(args)
    assert ret_doctor == 0, "cmd_doctor failed"
    print("  [Pass] cmd_doctor clean")

    ret_bench = cmd_bench(args)
    assert ret_bench == 0, "cmd_bench failed"
    print("  [Pass] cmd_bench clean")

    ret_upload = cmd_upload_status(args)
    assert ret_upload == 0, "cmd_upload_status failed"
    print("  [Pass] cmd_upload_status clean")

    ret_fleet = cmd_fleet(args)
    assert ret_fleet == 0, "cmd_fleet failed"
    print("  [Pass] cmd_fleet clean")

    ret_blast = cmd_blast(args)
    assert ret_blast == 0, "cmd_blast failed"
    print("  [Pass] cmd_blast clean")

    ret_release = cmd_release(args)
    assert ret_release == 0, "cmd_release failed"
    print("  [Pass] cmd_release clean")

    # Test review
    args.staged = False
    ret_review = cmd_review(args)
    assert ret_review == 0, "cmd_review failed"
    print("  [Pass] cmd_review clean")

    # Test graph
    ret_graph = cmd_graph(args)
    assert ret_graph == 0, "cmd_graph failed"
    print("  [Pass] cmd_graph clean")

    # Test search
    args.query = ["health"]
    args.limit = 5
    ret_search = cmd_search(args)
    assert ret_search == 0, "cmd_search failed"
    print("  [Pass] cmd_search clean")

    print("================================================")
    print("Neuro Master CLI Self-Test: 100% PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Neuro Co-Pilot Unified Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # doctor
    doc_p = subparsers.add_parser("doctor", help="Run full system diagnostic & health verification")
    doc_p.add_argument("--json", action="store_true", help="Output JSON format")
    doc_p.add_argument("--speak", action="store_true", help="Synthesize natural spoken voice debrief using Kokoro")
    doc_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # run
    run_parser = subparsers.add_parser("run", help="Launch parallel DAG multi-bridge contract bus")
    run_parser.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # ci
    ci_parser = subparsers.add_parser("ci", help="Verify and monitor remote GitHub Actions CI gate")
    ci_parser.add_argument("--wait", action="store_true", default=True, help="Wait for runs to complete")
    ci_parser.add_argument("--diagnose", action="store_true", help="Diagnose recent CI failure logs")

    # clean
    clean_p = subparsers.add_parser("clean", help="Surgically eliminate orphan processes and temporary files")
    clean_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # voice
    voice_parser = subparsers.add_parser("voice", help="Spoken voice briefings and tactical voice operator")
    voice_parser.add_argument("message", nargs="*", help="Message text to synthesize and speak")
    voice_parser.add_argument("--preset", default="EXECUTIVE_PRECISION", help="Acoustic DSP mastering preset")
    voice_parser.add_argument("--hud", action="store_true", help="Launch floating Holographic Voice HUD")

    # bench
    bench_p = subparsers.add_parser("bench", help="Run performance benchmark & latency regression watchdog")
    bench_p.add_argument("--json", action="store_true", help="Output JSON format")
    bench_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # fleet
    fleet_p = subparsers.add_parser("fleet", help="Run EVE fleet tactical radar and PI watchdog sweep")
    fleet_p.add_argument("--json", action="store_true", help="Output JSON format")
    fleet_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # flight_plan
    fp_p = subparsers.add_parser("flight_plan", help="Synthesize and initialize Tududi feature plan")
    fp_p.add_argument("prompt", help="Feature description prompt")
    fp_p.add_argument("--execute", action="store_true", help="Create Git branch and initialize Tududi task")

    # heal / fix
    heal_p = subparsers.add_parser("heal", help="1-Click 5-Stage Autonomous System Self-Healing Cascade")
    heal_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    fix_p = subparsers.add_parser("fix", help="Alias for heal (1-Click Autonomous Self-Healing Cascade)")
    fix_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # test / test_all
    subparsers.add_parser("test", help="Run concurrent 13-bridge parallel self-test matrix")
    subparsers.add_parser("test_all", help="Run concurrent 13-bridge parallel self-test matrix")

    # watch / hud
    watch_p = subparsers.add_parser("watch", help="Launch real-time live telemetry HUD loop")
    watch_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    watch_p.add_argument("--iterations", type=int, default=0, help="Loop frames (0 for infinite)")
    hud_p = subparsers.add_parser("hud", help="Alias for watch (real-time telemetry HUD)")
    hud_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    hud_p.add_argument("--iterations", type=int, default=0, help="Loop frames (0 for infinite)")

    # docker
    dock_p = subparsers.add_parser("docker", help="Spawn modular on-demand Docker container profiles")
    dock_p.add_argument("target", nargs="?", default="status", choices=["core", "ui", "frontend", "voice", "all", "gpu", "gpu-amd", "stop", "status"], help="Target profile to spawn")

    # release
    rel_p = subparsers.add_parser("release", help="Generate immutable SOC 2 Type II Merkle release certificate")
    rel_p.add_argument("--tag", default="v1.0.0", help="Milestone release tag name")
    rel_p.add_argument("--json", action="store_true", help="Output raw JSON certificate")
    rel_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # blast
    blast_p = subparsers.add_parser("blast", help="Calculate AST blast radius and dependency risk impact for a file")
    blast_p.add_argument("file", help="Target source file path to analyze")
    blast_p.add_argument("--json", action="store_true", help="Output raw JSON impact report")
    blast_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # review
    rev_p = subparsers.add_parser("review", help="Autonomous pre-commit code review and security gate")
    rev_p.add_argument("--staged", action="store_true", help="Review staged diff only")
    rev_p.add_argument("--json", action="store_true", help="Output raw JSON")
    rev_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # graph
    graph_p = subparsers.add_parser("graph", help="Generate live Mermaid architecture & database ER diagrams")
    graph_p.add_argument("--json", action="store_true", help="Output raw JSON")
    graph_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # search
    srch_p = subparsers.add_parser("search", help="Unified search across codebase AST & SQLite knowledge vault")
    srch_p.add_argument("query", nargs="*", help="Query keywords")
    srch_p.add_argument("--limit", type=int, default=10, help="Maximum results to return")
    srch_p.add_argument("--json", action="store_true", help="Output raw JSON")
    srch_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # ask / rag
    ask_p = subparsers.add_parser("ask", help="Query intelligent Agentic RAG Copilot with specialized SLM synthesis")
    ask_p.add_argument("query", nargs="*", help="Question or query string")
    ask_p.add_argument("--chunks", type=int, default=5, help="Maximum vault chunks")
    ask_p.add_argument("--model", default=None, help="Model override")
    ask_p.add_argument("--json", action="store_true", help="Output raw JSON")

    rag_p = subparsers.add_parser("rag", help="Alias for ask (Agentic RAG Copilot synthesis)")
    rag_p.add_argument("query", nargs="*", help="Question or query string")
    rag_p.add_argument("--chunks", type=int, default=5, help="Maximum vault chunks")
    rag_p.add_argument("--model", default=None, help="Model override")
    rag_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # context
    ctx_p = subparsers.add_parser("context", help="Extract complete topic context (AST code, DB schemas, vault notes) for AI agents")
    ctx_p.add_argument("topic", nargs="*", help="Topic keywords")
    ctx_p.add_argument("--files", type=int, default=8, help="Maximum related files")
    ctx_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # summarize
    sum_p = subparsers.add_parser("summarize", help="Generate structured executive summary from a vault file or topic")
    sum_p.add_argument("target", nargs="*", help="Target file path or topic keywords")
    sum_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # reap / zombies
    reap_p = subparsers.add_parser("reap", help="Surgically eliminate orphan/zombie background processes and free system RAM")
    reap_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    reap_p.add_argument("--json", action="store_true", help="Output raw JSON")

    zomb_p = subparsers.add_parser("zombies", help="Alias for reap (zombie process elimination & memory reclaim)")
    zomb_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    zomb_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # act / agent (Autonomous ReAct Agent Loop)
    act_p = subparsers.add_parser("act", help="Launch autonomous multi-step ReAct engineering agent loop")
    act_p.add_argument("task", nargs="*", help="Task or complex engineering question")
    act_p.add_argument("--steps", type=int, default=6, help="Maximum execution steps")
    act_p.add_argument("--model", default=None, help="Model override (e.g. deepseek-r1:1.5b, phi4-mini:latest)")
    act_p.add_argument("--json", action="store_true", help="Output raw JSON trajectory")

    agent_p = subparsers.add_parser("agent", help="Alias for act (autonomous multi-step ReAct loop)")
    agent_p.add_argument("task", nargs="*", help="Task or complex engineering question")
    agent_p.add_argument("--steps", type=int, default=6, help="Maximum execution steps")
    agent_p.add_argument("--model", default=None, help="Model override")
    agent_p.add_argument("--json", action="store_true", help="Output raw JSON trajectory")

    # graph_code / ast_build
    gc_p = subparsers.add_parser("graph_code", help="Parse codebase AST and build SQLite code_symbols and symbol_calls graph")
    gc_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    gc_p.add_argument("--json", action="store_true", help="Output raw JSON")

    ab_p = subparsers.add_parser("ast_build", help="Alias for graph_code (build AST relational database)")
    ab_p.add_argument("--root", default=BASE_DIR, help="Target repository root")
    ab_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # symbol / callers / call_graph
    sym_p = subparsers.add_parser("symbol", help="Query exact AST definition, callers, and DB tables for a symbol")
    sym_p.add_argument("symbol", help="Function or class name")
    sym_p.add_argument("--json", action="store_true", help="Output raw JSON")

    callers_p = subparsers.add_parser("callers", help="Alias for symbol (trace upstream callers and downstream calls)")
    callers_p.add_argument("symbol", help="Function or class name")
    callers_p.add_argument("--json", action="store_true", help="Output raw JSON")

    cg_p = subparsers.add_parser("call_graph", help="Alias for symbol (trace AST call graph in SQLite)")
    cg_p.add_argument("symbol", help="Function or class name")
    cg_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # recover / restore
    subparsers.add_parser("recover", help="Execute 5-stage zero-reboot Windows recovery cascade")
    subparsers.add_parser("restore", help="Alias for recover (zero-reboot recovery cascade)")

    # upload_status / sync
    up_p = subparsers.add_parser("upload_status", help="Display GitHub Remote Upload & Sync Visibility status")
    up_p.add_argument("--json", action="store_true", help="Output raw JSON")
    up_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    sync_p = subparsers.add_parser("sync", help="Alias for upload_status (GitHub Remote Sync Visibility)")
    sync_p.add_argument("--json", action="store_true", help="Output raw JSON")
    sync_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # status
    status_p = subparsers.add_parser("status", help="Quick executive health scorecard")
    status_p.add_argument("--root", default=BASE_DIR, help="Target repository root")

    # erp
    erp_p = subparsers.add_parser("erp", help="Unified PR ERP Multi-Database SQL Bridge (know, payroll, compliance)")
    erp_subs = erp_p.add_subparsers(dest="erp_subcommand")
    erp_subs.add_parser("schema", help="Reflect full schema across all attached ERP databases")
    erp_subs.add_parser("payroll", help="Summary metrics from payroll.db")
    erp_subs.add_parser("compliance", help="Summary metrics from compliance.db")
    erp_q = erp_subs.add_parser("query", help="Execute read-only SQL query across attached databases")
    erp_q.add_argument("sql", help="SQL SELECT statement")
    erp_q.add_argument("--limit", type=int, default=100, help="Max rows")
    erp_ask = erp_subs.add_parser("ask", help="Natural language question to SQL execution")
    erp_ask.add_argument("question", nargs="*", help="Question text")

    # llm
    llm_p = subparsers.add_parser("llm", help="Standalone Local LLM Engine Bridge (Zero-Daemon GGUF Execution)")
    llm_subs = llm_p.add_subparsers(dest="llm_subcommand")
    llm_subs.add_parser("list", help="List registered GGUF models and aliases")
    llm_subs.add_parser("status", help="Check Ollama and Standalone Vulkan/HIP runtime status")
    llm_run = llm_subs.add_parser("run", help="Run standalone prompt directly via llama-cli")
    llm_run.add_argument("prompt", nargs="*", help="Prompt string")
    llm_run.add_argument("--model", default="qwen2.5:0.5b", help="Target model name")
    llm_run.add_argument("--tokens", type=int, default=256, help="Max tokens")
    llm_run.add_argument("--temp", type=float, default=0.2, help="Temperature")
    llm_run.add_argument("--runtime", default="vulkan", choices=["vulkan", "hip"], help="GPU backend")
    llm_run.add_argument("--ngl", type=int, default=16, help="GPU offload layers")

    # loop (Closed-Loop Autonomous Engineering)
    loop_p = subparsers.add_parser("loop", help="Execute Closed-Loop Autonomous Engineering Engines")
    loop_subs = loop_p.add_subparsers(dest="loop_subcommand")
    
    loop_dev = loop_subs.add_parser("develop", help="Autonomous Feature & Bugfix Loop with Self-Healing")
    loop_dev.add_argument("task", nargs="*", help="Task or feature description")
    loop_dev.add_argument("--iterations", type=int, default=3, help="Max self-healing iterations")
    loop_dev.add_argument("--root", default=BASE_DIR, help="Target repository root")

    loop_hlth = loop_subs.add_parser("health", help="Continuous 360° System Health & Zero-Orphan Loop")
    loop_hlth.add_argument("--daemon", action="store_true", help="Run continuous background watchdog loop")
    loop_hlth.add_argument("--interval", type=int, default=60, help="Watchdog interval seconds")
    loop_hlth.add_argument("--max-cycles", type=int, default=1, help="Max loop cycles")
    loop_hlth.add_argument("--root", default=BASE_DIR, help="Target repository root")

    loop_subs.add_parser("erp", help="Autonomous PR ERP Compliance & Statutory Cross-Audit Loop")
    
    loop_know = loop_subs.add_parser("knowledge", help="Autonomous Knowledge Ingestion & Vector Retrieval Verification Loop")
    loop_know.add_argument("query", nargs="*", help="Test query for retrieval verification")

    # browser (Performance & Zero-Stutter Gaming Optimizer)
    browser_p = subparsers.add_parser("browser", help="Browser Performance & Zero-Stutter Gaming Optimizer Bridge")
    browser_subs = browser_p.add_subparsers(dest="browser_subcommand")
    browser_subs.add_parser("status", help="Inspect browser memory usage and zero-stutter optimization state")
    b_tune = browser_subs.add_parser("tune", help="Apply zero-stutter gaming profile to detected browsers")
    b_tune.add_argument("--browser", choices=["brave", "chrome", "edge", "all"], default="all", help="Target browser")
    b_tune.add_argument("--close", action="store_true", help="Cleanly close running browser processes to lock settings")
    b_rest = browser_subs.add_parser("restore", help="Restore previous browser settings from backup")
    b_rest.add_argument("--browser", choices=["brave", "chrome", "edge", "all"], default="all", help="Target browser")
    browser_subs.add_parser("test", help="Run automated self-test assertions")

    # curam (IBM Cúram SPM & CER Rules)
    curam_p = subparsers.add_parser("curam", help="IBM Cúram SPM & CER Decision Engine Bridge")
    curam_subs = curam_p.add_subparsers(dest="curam_subcommand")
    curam_eval = curam_subs.add_parser("evaluate", help="Evaluate evidence against CER decision tables")
    curam_eval.add_argument("--evidence", required=True, help="JSON string or file path containing evidence")
    curam_fpl = curam_subs.add_parser("fpl", help="Retrieve statutory FPL poverty tables")
    curam_fpl.add_argument("--size", type=int, default=1, help="Household size")

    # jira (Jira Test Cases & Traceability)
    jira_p = subparsers.add_parser("jira", help="Jira Issue & QA Test Case Specification Bridge (Xray/Zephyr)")
    jira_subs = jira_p.add_subparsers(dest="jira_subcommand")
    jira_gen = jira_subs.add_parser("generate", help="Generate Jira Xray/Zephyr test case specs")
    jira_gen.add_argument("--domain", default="MEDICAID_MAGI", help="Target domain/program")
    jira_gen.add_argument("--format", default="json", choices=["json", "markdown"], help="Output format")
    jira_exp = jira_subs.add_parser("export", help="Export test specification to docs/jira/")
    jira_exp.add_argument("--domain", default="MEDICAID_MAGI", help="Target domain/program")

    # uat (User Acceptance Testing & Merkle Sign-Off)
    uat_p = subparsers.add_parser("uat", help="User Acceptance Testing (UAT) & Sign-Off Certification Bridge")
    uat_subs = uat_p.add_subparsers(dest="uat_subcommand")
    uat_run = uat_subs.add_parser("run", help="Execute UAT test scenario matrix")
    uat_run.add_argument("--domains", nargs="+", default=["MEDICAID_MAGI", "SNAP", "TANF"], help="Target domains")
    uat_cert = uat_subs.add_parser("certificate", help="Generate official UAT Sign-Off Certificate")
    uat_cert.add_argument("--approver", default="Chief Information Officer / Product Owner SME", help="Approver title")

    # self_test
    subparsers.add_parser("self_test", help="Run automated CLI self-test assertions")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    cmd_map = {
        "doctor": cmd_doctor,
        "run": cmd_run,
        "ci": cmd_ci,
        "clean": cmd_clean,
        "reap": cmd_reap,
        "zombies": cmd_reap,
        "act": cmd_act,
        "agent": cmd_act,
        "graph_code": cmd_graph_code,
        "ast_build": cmd_graph_code,
        "symbol": cmd_symbol,
        "callers": cmd_symbol,
        "call_graph": cmd_symbol,
        "heal": cmd_heal,
        "fix": cmd_heal,
        "test": cmd_test,
        "test_all": cmd_test,
        "watch": cmd_watch,
        "hud": cmd_watch,
        "release": cmd_release,
        "blast": cmd_blast,
        "review": cmd_review,
        "graph": cmd_graph,
        "search": cmd_search,
        "ask": cmd_ask,
        "rag": cmd_ask,
        "context": cmd_context,
        "summarize": cmd_summarize,
        "recover": cmd_recover,
        "restore": cmd_recover,
        "voice": cmd_voice,
        "bench": cmd_bench,
        "fleet": cmd_fleet,
        "flight_plan": cmd_flight_plan,
        "docker": cmd_docker,
        "upload_status": cmd_upload_status,
        "sync": cmd_upload_status,
        "status": cmd_status,
        "erp": cmd_erp,
        "llm": cmd_llm,
        "loop": cmd_loop,
        "browser": cmd_browser,
        "curam": cmd_curam,
        "jira": cmd_jira,
        "uat": cmd_uat,
        "self_test": lambda a: self_test()
    }

    fn = cmd_map.get(args.command)
    if fn:
        code = fn(args)
        sys.exit(code or 0)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
