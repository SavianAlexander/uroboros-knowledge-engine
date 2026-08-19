"""
Infrastructure Layer for Uroboros Knowledge Engine.
Handles persistence, filesystem observation, document parsers, process supervision, and LLM bridges.
"""
from src.infrastructure.database import (
    get_db,
    get_db_connection,
    init_db,
    reset_db_connections,
    close_all_connections,
    SQLiteConnectionPool,
    DB_FILE
)
from src.infrastructure.parsers import (
    extract_content,
    calculate_sha256,
    calculate_sha256_cached,
    safe_read_file,
    safe_write_file
)
from src.infrastructure.watcher import (
    start_active_folder_watcher,
    real_start_active_folder_watcher
)
from src.infrastructure.llm import (
    get_fallback_llm,
    is_llm_available,
    require_llm,
    generate_cached_completion,
    stream_completion
)
from src.infrastructure.vector_engine import (
    MiniVectorEngine,
    index_directory,
    search_files,
    extract_rag_context
)
from src.infrastructure.process_supervisor import (
    cleanup_zombie_processes,
    get_system_resource_metrics
)

__all__ = [
    "get_db",
    "get_db_connection",
    "init_db",
    "reset_db_connections",
    "close_all_connections",
    "SQLiteConnectionPool",
    "DB_FILE",
    "extract_content",
    "calculate_sha256",
    "calculate_sha256_cached",
    "safe_read_file",
    "safe_write_file",
    "start_active_folder_watcher",
    "real_start_active_folder_watcher",
    "get_fallback_llm",
    "is_llm_available",
    "require_llm",
    "generate_cached_completion",
    "stream_completion",
    "MiniVectorEngine",
    "index_directory",
    "search_files",
    "extract_rag_context",
    "cleanup_zombie_processes",
    "get_system_resource_metrics"
]
