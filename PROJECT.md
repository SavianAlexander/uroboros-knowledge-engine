# Project: Uroboros Knowledge Engine Multi-Agent Autonomous Refactoring Mission

## Architecture
Decoupled Clean Architecture in Python (stdlib-first, zero unneeded dependencies):
- `src/app/routers/`: FastAPI endpoints (`search.py`, `files.py`, `rag.py`, `tags.py`, `voice_ws.py`).
- `src/core/`: Embeddings (`embeddings.py`), Model Manager (`model_manager.py`), Model Router (`model_router.py`), Job Queue (`jobs.py`), Voice Subsystems (`voice_audio_router.py`, `voice_command_parser.py`, `voice_dsp.py`, `voice_persona_blend.py`, `voice_rag_bridge.py`, `voice_sfx.py`, `voice_streaming_pipeline.py`, `voice_normalizer.py`, `voice_tududi_radar.py`, `voice_engine.py`).
- `src/infrastructure/`: Vector search engine & MMR (`vector_engine.py`), document parsers (`parsers.py`).
- `src/antigravity_voice_mcp.py` & `src/mcp_server.py`: FastMCP / JSON-RPC voice & knowledge tool protocol servers.
- `tests/` & `scripts/`: Master domain test runner (`run_domain_tests.py`), inter-bridge contract bus (`contract_bus.py`), architecture hygiene CLI (`architecture_cli.py`), voice audio test suite (`verify_voice_audio_pipeline.py`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1: Search & Filter O(1) Hash Optimization | Convert linear tag/exclusion lists and inner-loop scans in `src/app/routers/search.py` to constant-time set lookups and single-pass file reads | M1 | ORIGINAL_REQUEST §R1 |
| 2 | F2: File Router & Tree Traversal Optimization | Eliminate redundant `os.path.abspath` calls and hoist static ignore sets in `src/app/routers/files.py` | M1 | ORIGINAL_REQUEST §R1 |
| 3 | F3: Core Embeddings OrderedDict LRU Eviction | Replace FIFO dict with `collections.OrderedDict` (`move_to_end`, `popitem(last=False)`) in `src/core/embeddings.py` | M1 | ORIGINAL_REQUEST §R1 |
| 4 | F4: Vector Engine MMR & Autocomplete Set Acceleration | Switch `unselected_indices` in `search_mmr` to set operations and companion seen sets in `src/infrastructure/vector_engine.py` | M1 | ORIGINAL_REQUEST §R1 |
| 5 | F5: Core Jobs, Model Router & Parser Hotspots | Optimize `jobs.py`, `model_router.py`, `rag.py`, and `parsers.py` (slide zip archive lookups, word-set intersections, single-pass job reaping) | M1 | ORIGINAL_REQUEST §R1 |
| 6 | F6: Antigravity Voice MCP Dispatch Table Refactor | Flatten monolithic `handle_tool_call` (depth 39) into O(1) dictionary dispatch table `_TOOL_HANDLERS` + modular single-responsibility helpers in `src/antigravity_voice_mcp.py` | M2 | ORIGINAL_REQUEST §R2 |
| 7 | F7: Voice MCP Main Loop & JSON-RPC Flattening | Extract `_process_jsonrpc_request` with early guard returns in `src/antigravity_voice_mcp.py` reducing depth from 5 to <= 2 | M2 | ORIGINAL_REQUEST §R2 |
| 8 | F8: Downstream Voice/MCP Subsystem Guard Flattening | Refactor deep nesting (>= 4 levels) across `voice_ws.py`, `voice_audio_router.py`, `voice_command_parser.py`, `voice_dsp.py`, `voice_persona_blend.py`, `voice_rag_bridge.py`, `voice_sfx.py`, `voice_streaming_pipeline.py`, `voice_normalizer.py`, `voice_tududi_radar.py`, `voice_engine.py`, and `mcp_server.py` | M2 | ORIGINAL_REQUEST §R2 |
| 9 | F9: 28-Domain Master Matrix Zero-Regression Certification | Execute full `run_domain_tests.py` ensuring 100% pass (419/419 assertions) across all 28 functional domains | M3 | ORIGINAL_REQUEST §R3 |
| 10 | F10: 10-Bridge Contract DAG Integrity Certification | Verify all 10 inter-bridge contracts via `contract_bus.py self_test` with execution time < 25.0s | M3 | ORIGINAL_REQUEST §R3 |
| 11 | F11: Clean Architecture Doctor & Zero Secret Leak | Confirm 100.0% clean compliance score and 0 secrets via `architecture_cli.py doctor .` | M3 | ORIGINAL_REQUEST §R3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Darwinian AST Algorithmic Optimization (O(N^2) -> O(1)) | F1, F2, F3, F4, F5 | none | DONE |
| M2 | Codebase Bloat & Nesting Flattening (Ponytail Rule) | F6, F7, F8 | none | DONE |
| M3 | Zero-Regression Master Matrix & Contract Certification | F9, F10, F11 | M1, M2 | DONE |

## Interface Contracts & Invariant Guarantees

### R1 Algorithmic Hotspot Invariants:
- All function signatures in `src/app/routers/search.py`, `src/app/routers/files.py`, `src/core/embeddings.py`, `src/infrastructure/vector_engine.py`, and `src/infrastructure/parsers.py` must retain 100% backward-compatible argument types and return schemas.
- Output ordering contracts (e.g. search rankings, tag ordering, suggestion sequences) must remain deterministic.
- Embeddings caching must operate in true LRU order using `collections.OrderedDict`.

### R2 Control-Flow & Nesting Invariants:
- All 39 MCP tool calls handled by `src/antigravity_voice_mcp.py` must produce identical response dictionaries and error handling behavior.
- Control-flow nesting depth must be strictly $< 4$ (target $\le 2$) across all refactored voice/MCP functions.
- Pure standard library only: zero external pip dependencies added.

### R3 Certification Invariants:
- `python run_domain_tests.py` must report 419 passed, 0 failed.
- `python .agents/skills/neuro-copilot/scripts/contract_bus.py self_test` must report 100% PASSED in $< 25.0$s.
- `python scripts/architecture_cli.py doctor .` must report 100.0% score and 0 secrets.

## Code Layout
- `src/app/routers/`: Router implementations (`search.py`, `files.py`, `rag.py`, `tags.py`, `voice_ws.py`)
- `src/core/`: Core business logic & voice subsystems
- `src/infrastructure/`: Vector engine & parsers
- `src/antigravity_voice_mcp.py`: Voice MCP server
- `tests/`: 48 modular domain test suites across 28 domains
- `scripts/`: Architecture doctor, test ledger update, voice audio verification
- `.agents/skills/neuro-copilot/scripts/`: Inter-bridge contract bus (`contract_bus.py`)
