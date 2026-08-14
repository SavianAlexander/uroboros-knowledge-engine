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
    import webbrowser
    import urllib.request
    from src.core.shutdown import register_shutdown_handlers
    from src.domain.process_manager import check_uroboros_health, is_port_bound

    register_shutdown_handlers()

    host = os.environ.get("HOST", "0.0.0.0")
    requested_port = int(os.environ.get("PORT", 8085))
    target_port = requested_port

    # 1. Multi-instance & Port Failover Check
    if is_port_bound(requested_port):
        if check_uroboros_health(requested_port):
            print(f"===================================================")
            print(f" [INFO] Uroboros Knowledge Engine is already active!")
            print(f" Connecting to running instance on http://127.0.0.1:{requested_port}")
            print(f"===================================================")
            webbrowser.open(f"http://127.0.0.1:{requested_port}")
            sys.exit(0)
        else:
            # Port is occupied by an unresponsive or other process; find next available port
            for candidate in range(requested_port + 1, requested_port + 10):
                if not is_port_bound(candidate):
                    target_port = candidate
                    print(f"[WARN] Port {requested_port} is busy. Failing over to port {target_port}...")
                    break
            else:
                print(f"[ERROR] Unable to bind to ports {requested_port}..{requested_port+9}.")
                sys.exit(1)

    # 2. Spawn browser health poller thread (eliminates Cold-Start Connection Refused race condition)
    def _poll_and_open_browser(port: int):
        for _ in range(40):
            time.sleep(0.15)
            if check_uroboros_health(port):
                webbrowser.open(f"http://127.0.0.1:{port}")
                break

    auto_open = os.environ.get("NO_BROWSER", "").lower() not in ("1", "true", "yes")
    if auto_open:
        b_thread = threading.Thread(target=_poll_and_open_browser, args=(target_port,), daemon=True)
        b_thread.start()

    print(f"Starting Uroboros server on http://127.0.0.1:{target_port}")
    uvicorn.run(app, host=host, port=target_port)
