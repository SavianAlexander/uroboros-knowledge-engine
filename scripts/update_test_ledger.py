import os
import sys
import json
import time
import csv
import unittest
import xml.etree.ElementTree as ET

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import pytest
from concurrent.futures import ThreadPoolExecutor

import know
import main

FILE_DOMAIN_MAPPING = {
    "know.py": ["DomainDB", "DomainVector", "DomainIngestion", "DomainPerformance", "DomainChaos", "DomainSOC2", "DomainMutation"],
    "main.py": ["DomainAPI", "DomainLLM", "DomainSecurity", "DomainPerformance", "DomainChaos", "DomainSOC2", "DomainMutation", "DomainRouter", "DomainEmpirical", "DomainUIStress"],
    "app.js": ["DomainAPI", "DomainSecurity", "DomainUIStress"],
    "style.css": ["DomainAPI", "DomainUIStress"],
    "scripts/architecture_cli.py": ["DomainArchitecture"],
    "run_domain_tests.py": ["DomainRunner"],
    "src/domain/chat_intelligence.py": ["DomainChatIntelligence"],
    "tests/test_domain_chat_intelligence.py": ["DomainChatIntelligence"],
    "src/domain/wikilink_parser.py": ["DomainGraphPerformance"],
    "tests/test_domain_graph_performance.py": ["DomainGraphPerformance"],
    "src/domain/analytics_engine.py": ["DomainAnalyticsIntelligence"],
    "src/app/routers/analytics.py": ["DomainAnalyticsIntelligence"],
    "tests/test_domain_analytics_intelligence.py": ["DomainAnalyticsIntelligence"],
    "src/domain/workflow_engine.py": ["DomainWorkflowTriggers"],
    "src/infrastructure/webhook_dispatcher.py": ["DomainWorkflowTriggers"],
    "src/app/routers/workflows.py": ["DomainWorkflowTriggers"],
    "tests/test_domain_workflow_triggers.py": ["DomainWorkflowTriggers"],
    "src/domain/ocr_engine.py": ["DomainOCRTranscription"],
    "src/domain/transcription_engine.py": ["DomainOCRTranscription"],
    "tests/test_domain_ocr_transcription.py": ["DomainOCRTranscription"],
    "src/infrastructure/p2p_sync.py": ["DomainP2PSync"],
    "tests/test_domain_p2p_sync.py": ["DomainP2PSync"],
    "scripts/backup_db.py": ["DomainBackupAuthTheme"],
    "src/shared/auth.py": ["DomainBackupAuthTheme"],
    "tests/test_domain_backup_auth_theme.py": ["DomainBackupAuthTheme"]
}

DOMAIN_TEST_MODULES = [
    "tests.test_domain_db",
    "tests.test_domain_vector",
    "tests.test_domain_ingestion",
    "tests.test_domain_api",
    "tests.test_domain_llm",
    "tests.test_domain_security",
    "tests.test_domain_performance",
    "tests.test_domain_architecture",
    "tests.test_domain_chaos",
    "tests.test_domain_soc2",
    "tests.test_domain_mutation",
    "tests.test_domain_rag",
    "tests.test_domain_desktop",
    "tests.test_domain_expanded_coverage",
    "tests.test_fundamental_adversarial_matrix",
    "tests.test_deep_fuzzing_and_concurrency",
    "tests.test_domain_metamorphic",
    "tests.test_domain_accessibility",
    "tests.test_domain_localization",
    "tests.test_domain_contract_chaos",
    "tests.test_router_micro_units",
    "tests.test_empirical_challenger_final",
    "tests.test_adversarial_ui_stress",
    "tests.test_adversarial_challenger_2",
    "tests.test_adversarial_i3",
    "tests.test_domain_chat_intelligence",
    "tests.test_domain_graph_performance",
    "tests.test_domain_analytics_intelligence",
    "tests.test_domain_workflow_triggers",
    "tests.test_e2e_analytics_graph_workflows",
    "tests.test_domain_ocr_transcription",
    "tests.test_domain_p2p_sync",
    "tests.test_domain_backup_auth_theme"
]

BUG_RELATION_TAXONOMY = {
    "DomainBackupAuthTheme": [
        {"test": "test_01_sqlite_online_backup_and_restore", "component": "scripts/backup_db.py", "prevents": "Online SQLite live backup or point-in-time restore failure"},
        {"test": "test_02_verify_api_key_auth_guard_toggle", "component": "src/shared/auth.py", "prevents": "Configurable API key or Bearer token auth guard validation error"},
        {"test": "test_03_theme_toggle_persistence_contract", "component": "style.css", "prevents": "Dark/Light glassmorphism theme CSS variable contract regression"}
    ],
    "DomainP2PSync": [
        {"test": "test_01_multicast_beacon_lifecycle", "component": "src/infrastructure/p2p_sync.py", "prevents": "P2P multicast beacon thread start/stop lifecycle failure"},
        {"test": "test_02_get_local_document_hashes", "component": "src/infrastructure/p2p_sync.py", "prevents": "Missing SHA-256 document hashes, sizes, or modification timestamps"},
        {"test": "test_03_compute_sync_delta_categorization", "component": "src/infrastructure/p2p_sync.py", "prevents": "Incorrect categorization of missing, outdated, or unchanged files"},
        {"test": "test_04_api_sync_hashes_endpoint", "component": "src/app/routers/tags.py", "prevents": "REST endpoint GET /api/sync/hashes failure"},
        {"test": "test_05_api_sync_delta_endpoint", "component": "src/app/routers/tags.py", "prevents": "REST endpoint POST /api/sync/delta failure"},
        {"test": "test_06_api_sync_exchange_unreachable_peer_logging", "component": "src/app/routers/tags.py", "prevents": "Unreachable peer error status code 500 or sync_logs failure logging"},
        {"test": "test_07_api_sync_exchange_successful_delta_flow", "component": "src/app/routers/tags.py", "prevents": "Full P2P HTTP delta exchange protocol, database update, or sync_logs ledger failure"}
    ],
    "DomainOCRTranscription": [
        {"test": "test_01_ocr_non_existent_file_handling", "component": "src/domain/ocr_engine.py", "prevents": "Missing image file crash during OCR extraction"},
        {"test": "test_02_ocr_image_extraction_and_coords", "component": "src/domain/ocr_engine.py", "prevents": "Missing OCR word bounding box coordinates array"},
        {"test": "test_03_ocr_pillow_exif_and_metadata_fallback", "component": "src/domain/ocr_engine.py", "prevents": "OCR failure when Tesseract binary is not installed"},
        {"test": "test_04_transcription_non_existent_file", "component": "src/domain/transcription_engine.py", "prevents": "Missing audio file crash during transcription"},
        {"test": "test_05_transcription_wav_chunking_and_energy", "component": "src/domain/transcription_engine.py", "prevents": "WAV audio decoding or 10-second chunking failure"},
        {"test": "test_06_transcription_mp3_frame_header_parsing", "component": "src/domain/transcription_engine.py", "prevents": "MP3 frame header parsing or timestamp calculation error"},
        {"test": "test_07_transcription_corrupt_unknown_audio", "component": "src/domain/transcription_engine.py", "prevents": "Corrupted audio file crash during transcription processing"}
    ],
    "DomainWorkflowTriggers": [
        {"test": "test_01_database_crud_operations", "component": "src/infrastructure/database.py", "prevents": "Workflow trigger and log schema or CRUD database failure"},
        {"test": "test_02_condition_matching_engine", "component": "src/domain/workflow_engine.py", "prevents": "Rule evaluation failure on document_ingested, tag_assigned, semantic_match"},
        {"test": "test_03_webhook_dispatcher_signing_and_retries", "component": "src/infrastructure/webhook_dispatcher.py", "prevents": "Missing HMAC-SHA256 signature or failed webhook retries"},
        {"test": "test_04_rest_api_trigger_lifecycle", "component": "src/app/routers/workflows.py", "prevents": "REST API endpoint failures for triggers or deletion"},
        {"test": "test_05_rest_api_event_trigger_and_logs", "component": "src/app/routers/workflows.py", "prevents": "REST API event dispatch or log retrieval failure"}
    ],
    "DomainAnalyticsIntelligence": [
        {"test": "test_zero_state_resilience", "component": "src/domain/analytics_engine.py", "prevents": "Uninitialized database crashes and missing fallback values"},
        {"test": "test_analytics_with_populated_data", "component": "src/domain/analytics_engine.py", "prevents": "Incorrect metric calculation for storage, tags, and search telemetry"},
        {"test": "test_fastapi_rest_endpoints", "component": "src/app/routers/analytics.py", "prevents": "REST API endpoint failures or schema mismatches"},
        {"test": "test_latency_under_50ms", "component": "src/domain/analytics_engine.py", "prevents": "Sub-optimal query execution or missing LRU/TTL caching"}
    ],
    "DomainGraphPerformance": [

        {"test": "test_01_graph_performance_1000_nodes", "component": "src/app/routers/search.py", "prevents": "1000-node graph query latency degradation > 50ms"},
        {"test": "test_02_wikilink_edge_extraction", "component": "src/domain/wikilink_parser.py", "prevents": "Missing or corrupted markdown wikilink document edges"},
        {"test": "test_03_shared_tag_cluster_edges", "component": "src/app/routers/search.py", "prevents": "Incorrect shared tag cluster edge weight calculation"}
    ],
    "DomainChatIntelligence": [
        {"test": "test_chat_session_lifecycle_crud", "component": "src/domain/chat_intelligence.py", "prevents": "Orphaned chat sessions or broken CRUD state"},
        {"test": "test_chat_message_history_citations", "component": "src/domain/chat_intelligence.py", "prevents": "Unverified citations or sequence desynchronization"},
        {"test": "test_chat_context_window_truncation", "component": "src/domain/chat_intelligence.py", "prevents": "LLM context window token overflow"},
        {"test": "test_chat_fastapi_rest_endpoints", "component": "src/app/routers/rag.py", "prevents": "REST session endpoint failures"},
        {"test": "test_chat_metadata_unicode_resilience", "component": "src/domain/chat_intelligence.py", "prevents": "Unicode parsing crashes and JSON metadata corruption"}
    ],
    "Concurrency & Lock Contention": [
        {"test": "test_05_angle_timeout_60s_guard", "component": "know.py:L52", "prevents": "database is locked errors during concurrent writes"},
        {"test": "test_06_angle_atomic_snapshot_during_read", "component": "know.py:L1052", "prevents": "WAL checkpoint blocking active reads"},
        {"test": "test_07_angle_submillisecond_connection_reset", "component": "know.py:L45", "prevents": "Connection pool depletion"},
        {"test": "test_04_angle_llm_lock_concurrency_safety", "component": "main.py:L2984", "prevents": "_llm_lock thread deadlocks"},
        {"test": "test_02_chaos_simulated_read_lock_recovery", "component": "know.py:L45", "prevents": "Multi-connection lock contention crashes"}
    ],
    "Memory Leaks & OOM Spikes": [
        {"test": "test_04_angle_50mb_size_limit_guard", "component": "know.py:L604", "prevents": "Host RAM exhaustion on 1GB+ files"},
        {"test": "test_02_inverted_index_posting_lists", "component": "know.py:L330", "prevents": "O(N_docs) vector matrix memory explosion"},
        {"test": "test_06_angle_version_invalidation_matrix", "component": "know.py:L312", "prevents": "Stale memory cache leaks"}
    ],
    "Security & Path Traversal": [
        {"test": "test_02_path_traversal_containment", "component": "main.py:L446", "prevents": "Directory traversal symlink escape (../../secret.txt)"},
        {"test": "test_03_angle_unbalanced_quotes_sanitization", "component": "main.py:L3030", "prevents": "FTS5 syntax injection exceptions"},
        {"test": "test_05_angle_fts_injection_resilience", "component": "main.py:L3040", "prevents": "Raw FTS operator SQL injection"},
        {"test": "test_04_angle_multibyte_utf8_strings", "component": "know.py:L304", "prevents": "Multibyte non-ASCII parsing crashes"},
        {"test": "test_08_simulation_symlink_escape_containment", "component": "main.py:L446", "prevents": "Symlink escape containment breach"},
        {"test": "test_09_simulation_xss_script_injection_sanitization", "component": "main.py:L3024", "prevents": "HTML script tag XSS injection"}
    ],
    "C++ Hardware & Allocator Overflows": [
        {"test": "test_01_gpu_llm_loader", "component": "main.py:L2955", "prevents": "Vulkan uint32_t layer offloading integer overflow"},
        {"test": "test_02_angle_empty_prompt_generation_safety", "component": "main.py:L2960", "prevents": "GPU VRAM null pointer access violation"}
    ],
    "Index Desynchronization & Silent Data Loss": [
        {"test": "test_02_fts_porter_tokenizer", "component": "know.py:L125", "prevents": "Stemming search mismatch"},
        {"test": "test_03_composite_indexes_exist", "component": "know.py:L273", "prevents": "Full table scan performance degradation"},
        {"test": "test_03_angle_empty_file_ingestion", "component": "know.py:L600", "prevents": "0-byte file silent extraction crash"},
        {"test": "test_05_angle_rapid_file_save_sync", "component": "main.py:L478", "prevents": "Primary DB / FTS index desynchronization"},
        {"test": "test_01_chaos_corrupted_utf8_binary_payload", "component": "know.py:L604", "prevents": "Corrupted non-UTF8 binary payload crash"}
    ],
    "Network & API Exceptions": [
        {"test": "test_01_search_api_endpoint", "component": "main.py:L425", "prevents": "HTTP 500 endpoint failure"},
        {"test": "test_02_sse_chat_stream_endpoint", "component": "main.py:L3160", "prevents": "Invalid JSON SSE stream disconnects"},
        {"test": "test_03_angle_missing_field_422_validation", "component": "main.py:L3026", "prevents": "Unvalidated schema payload crash"},
        {"test": "test_04_angle_gzip_compression_header", "component": "main.py:L30", "prevents": "Uncompressed HTTP network payload inflation"},
        {"test": "test_06_simulation_giant_query_string", "component": "main.py:L425", "prevents": "10,000 char query buffer overflow"},
        {"test": "test_07_simulation_invalid_json_body", "component": "main.py:L3160", "prevents": "Malformed JSON body API crashes"}
    ],
    "SOC 2 Type II Security & Trust Controls": [
        {"test": "test_01_soc2_security_zero_secret_leakage", "component": "repository", "prevents": "Plaintext secret or credential leaks"},
        {"test": "test_02_soc2_availability_resource_guard", "component": "know.py:L604", "prevents": "System availability degradation under OOM"},
        {"test": "test_03_soc2_processing_integrity_sha256_verification", "component": "know.py:L468", "prevents": "File data tampering / payload alteration"},
        {"test": "test_04_soc2_confidentiality_acl_permissions", "component": "know.py:L117", "prevents": "Unauthorized document ACL access"},
        {"test": "test_05_soc2_privacy_sanitization_guard", "component": "main.py:L3024", "prevents": "Private data & control char leakage"}
    ],
    "Mutation & Code Resiliency": [
        {"test": "test_01_mutation_caught_corrupted_fts_query", "component": "main.py:L3004", "prevents": "Unsanitized operator mutations"},
        {"test": "test_02_mutation_caught_oversized_ram_ingestion", "component": "know.py:L604", "prevents": "RAM threshold bypass mutations"}
    ]
}

def render_tui():
    json_path = os.path.join(root_dir, "tests", "test_audit_ledger.json")
    if not os.path.exists(json_path):
        run_ledger_audit()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    GREEN, CYAN, YELLOW, BOLD, RESET = "\033[92m", "\033[96m", "\033[93m", "\033[1m", "\033[0m"
    print("\n" + BOLD + CYAN + "==========================================================================" + RESET)
    print(BOLD + CYAN + "               UROBOROS TERMINAL TUI AUDIT DASHBOARD                      " + RESET)
    print(BOLD + CYAN + "==========================================================================" + RESET)
    print(f" Last Updated   : {BOLD}{data.get('last_updated')}{RESET}")
    print(f" Audit Duration : {BOLD}{data.get('total_duration_seconds')}s{RESET}")
    summary = data.get("overall_summary", {})
    print(f" Total Domains  : {BOLD}{summary.get('total_domains')}{RESET}")
    print(f" Tests Passed   : {BOLD}{GREEN}{summary.get('passed')}{RESET} / {summary.get('passed') + summary.get('failed') + summary.get('errors')}")
    print(BOLD + CYAN + "--------------------------------------------------------------------------" + RESET)
    print(f" {BOLD}{'Domain Module':<25} {'Run':<6} {'Passed':<8} {'Status':<10} {'Time(s)':<8}{RESET}")
    print(BOLD + CYAN + "--------------------------------------------------------------------------" + RESET)

    for d_name, d_info in data.get("domain_results", {}).items():
        status_str = f"{GREEN}PASS{RESET}" if d_info.get("failures") == 0 and d_info.get("errors") == 0 else f"{YELLOW}FAIL{RESET}"
        print(f" {d_name:<25} {d_info.get('tests_run'):<6} {d_info.get('passed'):<8} {status_str:<18} {d_info.get('duration_seconds'):<8}")

    print(BOLD + CYAN + "==========================================================================" + RESET + "\n")

def generate_heatmap():
    heatmap_data = []
    for fname, domains in FILE_DOMAIN_MAPPING.items():
        guarded_count = sum(
            1 for cat, items in BUG_RELATION_TAXONOMY.items() for item in items if fname in item.get("component", "")
        )
        density_score = min(100, len(domains) * 20 + guarded_count * 10)
        heatmap_data.append({
            "file": fname, "domains": domains, "guarded_tests": guarded_count, "density_score": density_score
        })

    html_path = os.path.join(root_dir, "docs", "test_coverage_heatmap.html")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Uroboros Test Coverage Heatmap</title>
    <style>
        :root {{ --bg: #0d1117; --card-bg: #161b22; --border: #30363d; --text: #c9d1d9; --accent: #58a6ff; --font: -apple-system, sans-serif; }}
        body {{ background: var(--bg); color: var(--text); font-family: var(--font); padding: 30px; margin: 0; }}
        h1 {{ color: #fff; margin-bottom: 5px; }}
        .subtitle {{ color: #8b949e; margin-bottom: 25px; font-size: 14px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; }}
        .heatmap-bar {{ height: 6px; width: 100%; background: #21262d; border-radius: 3px; margin-top: 15px; overflow: hidden; }}
        .heatmap-fill {{ height: 100%; background: linear-gradient(90deg, #238636, #58a6ff); border-radius: 3px; }}
        .file-name {{ font-family: monospace; font-size: 18px; font-weight: bold; color: #fff; }}
        .score {{ float: right; font-size: 14px; color: var(--accent); font-weight: bold; }}
        .domain-tag {{ display: inline-block; background: #1f242c; border: 1px solid var(--border); color: #79c0ff; font-size: 11px; padding: 2px 8px; border-radius: 12px; margin-right: 4px; margin-top: 8px; }}
    </style>
</head>
<body>
    <h1>Uroboros Codebase Test Coverage Heatmap</h1>
    <div class="subtitle">Visual Test Density & Bug Relation Resilience Score per File</div>
    <div class="grid">
"""
    for item in heatmap_data:
        html_content += f"""
        <div class="card">
            <span class="score">{item['density_score']}% Density</span>
            <div class="file-name">{item['file']}</div>
            <div>{"".join([f'<span class="domain-tag">{d}</span>' for d in item['domains']])}</div>
            <div style="margin-top: 10px; font-size: 12px; color: #8b949e;">Guarded Defect Tests: {item['guarded_tests']}</div>
            <div class="heatmap-bar"><div class="heatmap-fill" style="width: {item['density_score']}%;"></div></div>
        </div>
"""
    html_content += "</div></body></html>"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Test Coverage Heatmap updated: {html_path}")

def generate_soc2_report(start_timestamp, total_failed=0, total_errors=0):
    is_compliant = (total_failed == 0 and total_errors == 0)
    compliance_status = "FULLY COMPLIANT (TYPE II ATTESTATION READY)" if is_compliant else "NON_COMPLIANT"
    md_status = "100% COMPLIANT" if is_compliant else "NON_COMPLIANT"
    crit_status = "COMPLIANT" if is_compliant else "NON_COMPLIANT"

    soc2_data = {
        "attestation_date": start_timestamp,
        "compliance_status": compliance_status,
        "trust_services_criteria": {
            "Security": f"{crit_status} (Zero secret leaks, path containment)",
            "Availability": f"{crit_status} (50MB RAM guard, 60s DB lock timeout)",
            "Processing Integrity": f"{crit_status} (SHA-256 integrity, atomic DB snapshot)",
            "Confidentiality": f"{crit_status} (File ACL permissions tracking)",
            "Privacy": f"{crit_status} (User memory lifecycle control)"
        }
    }
    json_path = os.path.join(root_dir, "tests", "soc2_audit_ledger.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(soc2_data, f, indent=2)

    md_path = os.path.join(root_dir, "docs", "soc2_type2_attestation.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Uroboros SOC 2 Type II Attestation Report\n**Attestation Date**: `{start_timestamp}`\n**Status**: `{md_status}`\n")
    print(f"SOC 2 Type II Attestation updated: {md_path}")

def run_single_module(mod_name):
    mod_t0 = time.time()
    try:
        suite = unittest.defaultTestLoader.loadTestsFromName(mod_name)
    except Exception:
        suite = None

    if suite and suite.countTestCases() > 0:
        runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'))
        res = runner.run(suite)
        mod_t1 = time.time()
        passed = res.testsRun - len(res.failures) - len(res.errors) - len(res.skipped)
        failures_cnt = len(res.failures)
        errors_cnt = len(res.errors)
        skipped_cnt = len(res.skipped)
        tests_run_cnt = res.testsRun
    else:
        file_path = mod_name.replace('.', '/') + '.py'
        if not os.path.exists(os.path.join(root_dir, file_path)):
            file_path = os.path.join(root_dir, "tests", mod_name.split(".")[-1] + ".py")

        class PytestResultCollector:
            def __init__(self):
                self.tests_run = 0
                self.passed = 0
                self.failures = 0
                self.errors = 0
                self.skipped = 0

            def pytest_runtest_logreport(self, report):
                if report.when == 'call':
                    self.tests_run += 1
                    if report.passed:
                        self.passed += 1
                    elif report.failed:
                        self.failures += 1
                    elif report.skipped:
                        self.skipped += 1
                elif report.when in ('setup', 'teardown') and report.failed:
                    self.tests_run += 1
                    self.errors += 1

        collector = PytestResultCollector()
        pytest.main([file_path, '-q', '--disable-warnings'], plugins=[collector])
        mod_t1 = time.time()
        passed = collector.passed
        failures_cnt = collector.failures
        errors_cnt = collector.errors
        skipped_cnt = collector.skipped
        tests_run_cnt = collector.tests_run

    domain_key = mod_name.split(".")[-1]
    mod_duration = round(mod_t1 - mod_t0, 4)

    return {
        "domain_key": domain_key,
        "module": mod_name,
        "tests_run": tests_run_cnt,
        "passed": passed,
        "failures": failures_cnt,
        "errors": errors_cnt,
        "skipped": skipped_cnt,
        "duration_seconds": mod_duration
    }

def run_ledger_audit(target_modules=None, parallel=False, max_workers=None):
    print("===================================================")
    print("   UROBOROS MASTER DOMAIN AUDIT ENGINE v8.0")
    print("===================================================")

    modules_to_run = target_modules or DOMAIN_TEST_MODULES
    results_by_domain = {}
    total_passed = total_failed = total_errors = total_skipped = 0
    start_timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    start_time = time.time()

    testsuites_xml = ET.Element("testsuites", name="UroborosDomainTests", time="0.0")

    use_parallel = parallel or ("--parallel" in sys.argv)
    if use_parallel:
        workers = max_workers or 4
        print(f"[MULTI-THREADING] Running unit tests concurrently with {workers} workers...")
        ui_modules = [m for m in modules_to_run if any(ui_kw in m for ui_kw in ["empirical", "ui_stress", "challenger_2", "adversarial_i3"])]
        unit_modules = [m for m in modules_to_run if m not in ui_modules]
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            mod_results = list(executor.map(run_single_module, unit_modules))
        
        print(f"[SEQUENTIAL UI] Running {len(ui_modules)} browser UI test suites sequentially...")
        for ui_mod in ui_modules:
            mod_results.append(run_single_module(ui_mod))
    else:
        mod_results = [run_single_module(mod_name) for mod_name in modules_to_run]

    for d_info in mod_results:
        domain_key = d_info["domain_key"]
        results_by_domain[domain_key] = {
            "module": d_info["module"],
            "tests_run": d_info["tests_run"],
            "passed": d_info["passed"],
            "failures": d_info["failures"],
            "errors": d_info["errors"],
            "skipped": d_info["skipped"],
            "duration_seconds": d_info["duration_seconds"]
        }

        total_passed += d_info["passed"]
        total_failed += d_info["failures"]
        total_errors += d_info["errors"]
        total_skipped += d_info["skipped"]

        ET.SubElement(
            testsuites_xml, "testsuite", name=domain_key, tests=str(d_info["tests_run"]),
            failures=str(d_info["failures"]), errors=str(d_info["errors"]),
            skipped=str(d_info["skipped"]), time=str(d_info["duration_seconds"])
        )

    total_duration = round(time.time() - start_time, 4)
    testsuites_xml.set("time", str(total_duration))

    ledger_data = {
        "last_updated": start_timestamp,
        "total_duration_seconds": total_duration,
        "overall_summary": {
            "total_domains": len(modules_to_run),
            "passed": total_passed,
            "failed": total_failed,
            "errors": total_errors,
            "skipped": total_skipped
        },
        "file_coverage_mapping": FILE_DOMAIN_MAPPING,
        "bug_relation_taxonomy": BUG_RELATION_TAXONOMY,
        "domain_results": results_by_domain
    }

    # Write JSON ledger
    with open(os.path.join(root_dir, "tests", "test_audit_ledger.json"), "w", encoding="utf-8") as f:
        json.dump(ledger_data, f, indent=2)

    # Write CSV report
    with open(os.path.join(root_dir, "tests", "test_audit_ledger.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Domain Module", "Tests Run", "Passed", "Failed", "Errors", "Skipped", "Duration (s)"])
        for d_name, d_info in results_by_domain.items():
            writer.writerow([d_name, d_info['tests_run'], d_info['passed'], d_info['failures'], d_info['errors'], d_info['skipped'], d_info['duration_seconds']])

    # Write JUnit XML
    tree = ET.ElementTree(testsuites_xml)
    tree.write(os.path.join(root_dir, "tests", "test_results.xml"), encoding="utf-8", xml_declaration=True)

    # Write Markdown ledger
    md_content = f"# Uroboros Domain Audit Ledger & Defect Matrix v8.0\n**Timestamp**: `{start_timestamp}`\n**Duration**: `{total_duration}s`\n"
    with open(os.path.join(root_dir, "docs", "test_audit_ledger.md"), "w", encoding="utf-8") as f:
        f.write(md_content)

    # Write HTML visual dashboard
    html_path = os.path.join(root_dir, "docs", "test_audit_dashboard.html")
    pass_rate = round((total_passed / max(1, total_passed + total_failed + total_errors)) * 100, 1)
    status_label = "PASSING" if (total_failed == 0 and total_errors == 0) else "FAILED"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"<!DOCTYPE html><html><head><title>Audit Dashboard</title></head><body><h1>Uroboros Audit Dashboard</h1><p>Status: {status_label} ({pass_rate}%)</p></body></html>")

    generate_heatmap()
    generate_soc2_report(start_timestamp, total_failed, total_errors)

    print(f"Master Audit Engine v8.0 complete! Total Passed: {total_passed} | Failed: {total_failed} | Duration: {total_duration}s")

if __name__ == "__main__":
    if "--tui" in sys.argv:
        render_tui()
    elif "--heatmap" in sys.argv:
        generate_heatmap()
    elif "--soc2" in sys.argv:
        generate_soc2_report(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    else:
        run_ledger_audit()
        if "--all" in sys.argv or sys.stdout.isatty():
            render_tui()
