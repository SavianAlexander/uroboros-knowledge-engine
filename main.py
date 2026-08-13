"""
Backward-compatibility root entrypoint shim for FastAPI server and test suite re-exports.
"""

import os
import sys
import time
import json
import sqlite3
import threading
from contextlib import contextmanager

from src.app.server import app
from src.infrastructure.database import get_db
import src.infrastructure.database as _infra_db
from src.shared.security import verify_path_containment, get_file_acl
from src.shared.regex import RE_NEAR_SYNTAX, RE_TOKEN_SPLIT, RE_SIZE_OP, RE_FTS_CLEAN, RE_WIKILINKS
from src.core.domain.services import (
    parse_query_operators,
    suggest_tags_from_text,
    generate_summary,
    generate_key_takeaways,
    extract_ai_tags,
    reciprocal_rank_fusion,
    generate_hyde_expansion,
    sanitise_fts_query,
)



from src.core.config import ACTIVE_DIR

from src.core.state import (
    db_conn,
    QueryCache,
    GLOBAL_QUERY_CACHE,
    _llm_lock,
    Llama,
    get_llm,
    get_fallback_llm,
    expand_query_with_llm
)

if __name__ == "__main__":
    import uvicorn
    import socket

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8085))

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
    except OSError:
        print(f"Error: Port {port} is already in use by another instance of Uroboros Knowledge Engine.")
        print(f"Please close the existing server process on port {port} before launching a new instance.")
        sys.exit(1)

    print(f"Starting Uroboros server on http://127.0.0.1:{port}")
    uvicorn.run(app, host=host, port=port)
