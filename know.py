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
    generate_hyde_expansion,
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
from src.infrastructure.database import (
    DB_FILE,
    DB_TIMEOUT,
    MiniVectorEngine,
    SQLiteConnectionPool,
    add_chat_message,
    backup_db_online,
    create_chat_session,
    create_db_snapshot,
    create_workflow_trigger,
    db_status,
    delete_chat_session,
    delete_db_snapshot,
    delete_workflow_trigger,
    extract_rag_context,
    get_active_dir,
    get_chat_messages,
    get_chat_session,
    get_db,
    get_db_connection,
    get_file_revisions,
    get_pool,
    get_workflow_trigger,
    index_directory,
    init_db,
    list_chat_sessions,
    list_db_snapshots,
    list_workflow_logs,
    list_workflow_triggers,
    log_workflow_execution,
    migrate_folder_path,
    reset_db_connections,
    restore_db_snapshot,
    revert_file_revision,
    run_maintenance,
    save_file_revision,
    search_files,
    update_chat_session,
    update_workflow_trigger
)
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


class _KnowModule(sys.modules[__name__].__class__):
    @property
    def DB_FILE(self):
        return _infra_db.DB_FILE

    @DB_FILE.setter
    def DB_FILE(self, value):
        _infra_db.DB_FILE = value

    @property
    def _db_version(self):
        return _infra_db._db_version

    @_db_version.setter
    def _db_version(self, value):
        _infra_db._db_version = value

    @property
    def _cached_doc_vectors(self):
        return _infra_db.MiniVectorEngine._cached_doc_vectors

    @_cached_doc_vectors.setter
    def _cached_doc_vectors(self, value):
        _infra_db.MiniVectorEngine._cached_doc_vectors = value

    @property
    def _cached_inverted_index(self):
        return _infra_db.MiniVectorEngine._cached_inverted_index

    @_cached_inverted_index.setter
    def _cached_inverted_index(self, value):
        _infra_db.MiniVectorEngine._cached_inverted_index = value

sys.modules[__name__].__class__ = _KnowModule

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
    else:
        print("Uroboros Knowledge Engine CLI")

if __name__ == "__main__":
    main()
