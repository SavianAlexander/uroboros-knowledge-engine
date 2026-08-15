"""
Backward-compatibility root entrypoint shim re-exporting core infrastructure and domain services.
"""

import sys
from src.shared.regex import (
    URL_PATTERN,
    EMAIL_PATTERN,
    DATE_PATTERN,
    IP_PATTERN,
    MAC_PATTERN
)
from src.shared.security import (
    SECRET_REDACTION_PATTERNS,
    get_active_sandbox_dir,
    get_file_acl,
    redact_sensitive_keys,
    validate_upload_payload,
    verify_path_containment
)
from src.core.domain.models import (
    AddMessageRequest,
    AliasRequest,
    AnalyticsOverviewResponse,
    BackupScheduleRequest,
    BookmarkRequest,
    BulkDeleteRequest,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ContemplateRequest,
    ContemplateResponse,
    CreateSessionRequest,
    DeleteBookmarkRequest,
    DeleteFileRequest,
    FileEditRequest,
    FileInsightsRequest,
    FileInsightsResponse,
    FileSaveRequest,
    IndexRequest,
    MacroRequest,
    NotesRequest,
    OpenFileRequest,
    PeerRequest,
    RAGStreamRequest,
    RenameRequest,
    RevertRequest,
    RuleRequest,
    SearchActivityResponse,
    StorageBreakdownResponse,
    SyncExchangeRequest,
    SynonymRequest,
    TagColorRequest,
    TagDistributionResponse,
    TagRequest,
    UpdateSessionRequest,
    ValidateQueryRequest,
    WorkflowEventTriggerRequest,
    WorkflowLogResponse,
    WorkflowTriggerCreate,
    WorkflowTriggerResponse,
    WorkflowTriggerUpdate
)
from src.core.domain.services import (
    chunk_text,
    chunk_text_hierarchical,
    expand_synonyms,
    extract_ai_tags,
    generate_key_takeaways,
    generate_summary,
    lookup_document_metadata_category,
    lookup_tag_color,
    parse_query_operators,
    reciprocal_rank_fusion,
    sanitise_fts_query,
    sanitize_tag,
    stem_word,
    suggest_tags_from_text
)
from src.infrastructure.ocr import (
    HAS_WINRT,
    extract_ocr_text_structured,
    extract_pdf_ocr
)
from src.infrastructure.parsers import (
    calculate_sha256,
    calculate_sha256_cached,
    extract_content,
    parse_audio_metadata,
    safe_read_file,
    safe_write_file
)
from src.infrastructure.watcher import (
    real_start_active_folder_watcher,
    start_active_folder_watcher
)
from src.infrastructure.llm import (
    HAS_LLAMA,
    MAX_CONTEXT,
    generate_cached_completion,
    get_fallback_llm,
    is_llm_available,
    require_llm,
    stream_completion
)
from src.infrastructure.database import DB_FILE, DB_TIMEOUT, SQLiteConnectionPool, backup_db_online, db_status, get_active_dir, get_db, get_db_connection, get_pool, init_db, migrate_folder_path, reset_db_connections, run_maintenance
from src.infrastructure.vector_engine import MiniVectorEngine, extract_rag_context, index_directory, search_files
from src.infrastructure.repositories.chat import add_chat_message, create_chat_session, delete_chat_session, get_chat_messages, get_chat_session, list_chat_sessions, update_chat_session
from src.infrastructure.repositories.snapshots import create_db_snapshot, delete_db_snapshot, list_db_snapshots, restore_db_snapshot
from src.infrastructure.repositories.workflows import create_workflow_trigger, delete_workflow_trigger, get_workflow_trigger, list_workflow_logs, list_workflow_triggers, log_workflow_execution, update_workflow_trigger
from src.infrastructure.repositories.files import get_file_revisions, revert_file_revision, save_file_revision
import src.infrastructure.database as _infra_db
from src.domain.rag_engine import (
    generate_hyde_expansion,
    rrf_rerank,
    jaccard_deduplicate,
    extract_advanced_rag_context,
    decompose_multihop_query,
    precision_cross_rerank,
    parse_metadata_filters,
    trim_to_sentence_boundary
)
from src.domain.web_search import (
    WebSearchFetcher,
    fetch_web_context
)
from src.domain.pr_legal_engine import PRLegalEngine
from src.infrastructure.pr_legal_repository import (
    init_pr_legal_schema,
    ingest_pr_statutory_corpus,
    lookup_pr_citation_exact,
    query_pr_legal_hybrid
)

def search_knowledge(query: str, limit: int = 10):
    """Primary Hybrid RAG search entrypoint combining FTS5 BM25 and Vector Cosine similarity via RRF."""
    return MiniVectorEngine.search_hybrid_rrf(query, top_k=limit)


def main():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
        from src.infrastructure.crawler_repository import init_crawler_schema
        with get_db() as conn:
            init_crawler_schema(conn)
        print("[OK] Uroboros Knowledge Vault & Sovereign Crawler Matrix Initialized Successfully.")
    elif len(sys.argv) > 1 and sys.argv[1] in ("crawl", "crawler"):
        import subprocess
        # Forward arguments to crawler_cli.py
        crawler_script = os.path.join(os.path.dirname(__file__), "scripts", "crawler_cli.py")
        sys.argv[0] = crawler_script
        sys.argv.pop(1) # Remove 'crawl'
        from scripts.crawler_cli import main as crawler_main
        crawler_main()
    elif len(sys.argv) > 1 and sys.argv[1] == "search":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Puerto Rico"
        results = search_knowledge(q, limit=5)
        print(f"\n[SEARCH] Hybrid RAG Results for '{q}':\n")
        for r in results:
            title = r.get("title") or r.get("filename") or "Document"
            score = r.get("score") or r.get("similarity", 0.0)
            print(f" - [{score:.4f}] {title} ({r.get('path', '')})")
    else:
        print("=====================================================================")
        print("[APEX] UROBOROS KNOWLEDGE ENGINE & SOVEREIGN HARVESTER (APEX FUSION)")
        print("=====================================================================")
        print("Commands:")
        print("  python know.py init                  - Initialize SQLite knowledge & crawler vaults")
        print("  python know.py search <query>        - Execute hybrid RRF search across entire corpus")
        print("  python know.py crawl create ...      - Create an Omni-Sovereign crawler job")
        print("  python know.py crawl swarm ...       - Launch concurrent worker swarm")
        print("  python know.py crawl list            - List active jobs and extraction telemetry")
        print("  python know.py crawl certificate ... - Generate Rule 902 FRE Evidence Certificate")
        print("  python know.py crawl dossier ...     - Generate Cross-Examination Deposition Dossier")
        print("  python know.py crawl genesis ...     - Extract legislative journey milestones")
        print("  python know.py crawl visualizer ...  - Launch interactive HTML5 force-directed graph")
        print("=====================================================================")

if __name__ == "__main__":
    import os
    main()

