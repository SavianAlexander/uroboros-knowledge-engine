# Uroboros Master Test Ledger & Defect Matrix v8.0

**Timestamp**: `2026-08-19T21:17:00Z`  
**Duration**: `193.1493s`  
**Status**: `FAILED` (99.8%)  
**Total Domains**: `60`  
**Total Passed**: `483`  
**Total Failed**: `0`  
**Total Errors**: `1`  
**Total Skipped**: `42`  

## Domain Test Execution Breakdown

| Domain Module | Tests Run | Passed | Failed | Errors | Skipped | Duration (s) |
|---|---|---|---|---|---|---|
| `test_domain_db` | 13 | 13 | 0 | 0 | 0 | 0.3688s |
| `test_domain_vector` | 28 | 28 | 0 | 0 | 0 | 0.6464s |
| `test_domain_ingestion` | 13 | 13 | 0 | 0 | 0 | 0.3071s |
| `test_domain_api` | 13 | 13 | 0 | 0 | 0 | 1.2132s |
| `test_domain_llm` | 5 | 5 | 0 | 0 | 0 | 0.0731s |
| `test_domain_security` | 9 | 8 | 0 | 0 | 1 | 0.1301s |
| `test_domain_performance` | 4 | 4 | 0 | 0 | 0 | 0.0838s |
| `test_domain_architecture` | 1 | 0 | 0 | 0 | 1 | 0.001s |
| `test_domain_chaos` | 3 | 3 | 0 | 0 | 0 | 0.1326s |
| `test_domain_soc2` | 5 | 5 | 0 | 0 | 0 | 2.5946s |
| `test_domain_mutation` | 2 | 2 | 0 | 0 | 0 | 0.0268s |
| `test_domain_rag` | 13 | 13 | 0 | 0 | 0 | 1.1633s |
| `test_domain_desktop` | 1 | 0 | 0 | 1 | 0 | 0.0543s |
| `test_domain_expanded_coverage` | 25 | 25 | 0 | 0 | 0 | 0.5143s |
| `test_fundamental_adversarial_validation` | 20 | 20 | 0 | 0 | 0 | 0.7189s |
| `test_deep_fuzzing_and_concurrency` | 20 | 20 | 0 | 0 | 0 | 0.6099s |
| `test_domain_metamorphic` | 6 | 6 | 0 | 0 | 0 | 0.2606s |
| `test_domain_accessibility` | 5 | 0 | 0 | 0 | 5 | 0.0014s |
| `test_domain_localization` | 4 | 0 | 0 | 0 | 4 | 0.0005s |
| `test_domain_contract_chaos` | 4 | 0 | 0 | 0 | 4 | 0.0421s |
| `test_router_micro_units` | 18 | 18 | 0 | 0 | 0 | 0.7008s |
| `test_empirical_verification_final` | 8 | 0 | 0 | 0 | 8 | 0.0568s |
| `test_adversarial_ui_stress` | 4 | 0 | 0 | 0 | 4 | 0.0214s |
| `test_playwright_stats_search_interaction` | 2 | 0 | 0 | 0 | 2 | 0.018s |
| `test_adversarial_ui_graph_indexing` | 3 | 1 | 0 | 0 | 2 | 2.0806s |
| `test_domain_chat_intelligence` | 5 | 5 | 0 | 0 | 0 | 0.3764s |
| `test_domain_graph_performance` | 9 | 9 | 0 | 0 | 0 | 0.3839s |
| `test_domain_analytics_intelligence` | 4 | 3 | 0 | 0 | 1 | 0.1602s |
| `test_domain_workflow_triggers` | 5 | 3 | 0 | 0 | 2 | 0.5339s |
| `test_e2e_analytics_graph_workflows` | 21 | 16 | 0 | 0 | 5 | 6.7577s |
| `test_domain_ocr_transcription` | 9 | 9 | 0 | 0 | 0 | 0.2153s |
| `test_domain_p2p_sync` | 7 | 6 | 0 | 0 | 1 | 4.2657s |
| `test_domain_backup_auth_theme` | 3 | 1 | 0 | 0 | 2 | 0.0194s |
| `test_domain_advanced_features` | 28 | 28 | 0 | 0 | 0 | 0.4388s |
| `test_domain_code_ast` | 10 | 10 | 0 | 0 | 0 | 0.0097s |
| `test_domain_merkle_vault` | 10 | 10 | 0 | 0 | 0 | 0.4079s |
| `test_domain_sla_caching` | 10 | 10 | 0 | 0 | 0 | 0.156s |
| `test_domain_agent_consensus` | 10 | 10 | 0 | 0 | 0 | 0.2641s |
| `test_domain_semantic_rag_accuracy` | 10 | 10 | 0 | 0 | 0 | 0.1686s |
| `test_domain_mcp_server` | 10 | 10 | 0 | 0 | 0 | 0.2814s |
| `test_domain_catastrophic_recovery` | 10 | 10 | 0 | 0 | 0 | 0.2491s |
| `test_domain_auth_security_hardening` | 10 | 10 | 0 | 0 | 0 | 0.4573s |
| `test_domain_resource_stability` | 10 | 10 | 0 | 0 | 0 | 1.1589s |
| `test_domain_hallucination_guardrails` | 10 | 10 | 0 | 0 | 0 | 0.1966s |
| `test_universal_crawler` | 10 | 10 | 0 | 0 | 0 | 0.1354s |
| `test_crawler_api` | 7 | 7 | 0 | 0 | 0 | 0.0453s |
| `test_fusion_engine` | 2 | 2 | 0 | 0 | 0 | 0.003s |
| `test_domain_29_frontier_reasoning` | 12 | 12 | 0 | 0 | 0 | 0.2991s |
| `test_domain_sota_rag_dag` | 7 | 7 | 0 | 0 | 0 | 0.3126s |
| `test_rag_chat_e2e_pipeline` | 6 | 6 | 0 | 0 | 0 | 2.5828s |
| `test_user_acceptance_audit` | 6 | 6 | 0 | 0 | 0 | 12.7574s |
| `test_text_utils_and_wal_daemon` | 9 | 9 | 0 | 0 | 0 | 2.0128s |
| `test_speech_normalizer` | 6 | 6 | 0 | 0 | 0 | 0.0115s |
| `test_speech_normalizer_expanded` | 8 | 8 | 0 | 0 | 0 | 0.021s |
| `test_voice_normalization_cadence` | 9 | 9 | 0 | 0 | 0 | 16.6388s |
| `test_primary_source_connectors` | 9 | 9 | 0 | 0 | 0 | 127.1941s |
| `test_llm_inference_benchmark` | 5 | 5 | 0 | 0 | 0 | 0.0358s |
| `test_audio_hardware_calibration` | 4 | 4 | 0 | 0 | 0 | 0.0406s |
| `test_large_scale_stress` | 3 | 3 | 0 | 0 | 0 | 2.618s |
| `test_windows_dist_packaging` | 3 | 3 | 0 | 0 | 0 | 0.1191s |
