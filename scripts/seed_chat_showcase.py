import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.database import DB_FILE, init_db, get_db_connection

def seed_chat():
    init_db()
    
    sess_id = "session_wal_architecture_demo"
    now = time.time()
    now_iso = "2026-08-14T04:11:00Z"

    with get_db_connection(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (sess_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (sess_id,))

        cursor.execute("""
            INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at, model_path, temperature, context_window, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sess_id, 0, "SQLite WAL Architecture & Trade-Offs", now + 10000, now + 10000, "qwen2.5:7b", 0.7, 4096, None))

        # User Message
        user_msg = "Explain SQLite Write-Ahead Logging (WAL) mode with architecture trade-offs and production configuration code."
        cursor.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("msg_user_wal_1", sess_id, "user", user_msg, None, None, 22, now_iso, None))

        # Assistant Message with <think> tag, markdown, comparison table, code block, citations
        assistant_content = """<think>
Evaluating Write-Ahead Logging (WAL) vs traditional Rollback Journal.
- Concurrency: Readers do not block writers; writers do not block readers.
- I/O Performance: Inverted write pattern; changes append sequentially to the -wal file.
- Trade-offs: Increased read complexity (scanning WAL index in -shm shared memory), periodic checkpointing requirements, and lack of support on network filesystems (NFS).
- Formatting executive response with comparison table, Python setup artifact, and grounded citations.
</think>

### 1. Write-Ahead Logging (WAL) Overview

In traditional SQLite rollback journaling, writing requires exclusive database locks. **Write-Ahead Logging (WAL)** fundamentally decouples read and write locks by appending changes to a separate `-wal` file while preserving the original `.db` file for concurrent read transactions.

| Architectural Dimension | Traditional Rollback Journal | Write-Ahead Logging (WAL) |
| :--- | :--- | :--- |
| **Concurrency** | 1 Writer blocks all Readers | **Readers never block Writers; Writers never block Readers** |
| **Write Performance** | Random disk writes + sync overhead | **High sequential I/O appends to `-wal`** |
| **Index Mechanism** | Direct B-Tree page lock | **Memory-mapped `-shm` hash index table** |
| **Disk Overhead** | Creates / deletes temporary journal | **Persistent `-wal` & `-shm` with checkpointing** |

---

### 2. Production Python Configuration

To configure high-throughput SQLite in Python with auto-checkpointing and connection pooling:

```python
import sqlite3

def init_high_throughput_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
    # Enable Write-Ahead Logging
    conn.execute("PRAGMA journal_mode = WAL;")
    # Normal synchronous mode balances speed and durability
    conn.execute("PRAGMA synchronous = NORMAL;")
    # Auto-checkpoint every 1,000 pages (~4MB)
    conn.execute("PRAGMA wal_autocheckpoint = 1000;")
    conn.execute("PRAGMA cache_size = -64000;") # 64MB memory cache
    return conn
```

> **Key Architectural Insight**: By setting `PRAGMA synchronous = NORMAL`, WAL mode ensures complete durability against application crashes and operating system crashes, while only undergoing a full fsync on checkpoint intervals.
"""

        citations = [
            {
                "filename": "database.py",
                "path": "src/infrastructure/database.py",
                "score": 0.99,
                "snippet": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA wal_autocheckpoint=1000;"
            },
            {
                "filename": "server.py",
                "path": "src/app/server.py",
                "score": 0.94,
                "snippet": "execute_clean_shutdown() -> db_manager.checkpoint_wal()"
            }
        ]

        cursor.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, citations_json, web_sources_json, tokens_used, created_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("msg_asst_wal_1", sess_id, "assistant", assistant_content, json.dumps(citations), None, 385, now_iso, None))

        conn.commit()
    print("Successfully seeded responded chat session in DB_FILE.")

if __name__ == "__main__":
    seed_chat()
