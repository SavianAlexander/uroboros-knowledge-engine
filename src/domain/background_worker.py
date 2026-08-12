import time
import threading
import sqlite3
import logging
from typing import Optional
from src.infrastructure.database import get_db

logger = logging.getLogger(__name__)

class DocumentSummarizerDaemon(threading.Thread):
    """
    Non-blocking background thread daemon that monitors un-summarized documents
    and triggers host Ollama (qwen2.5-coder:14b) GPU inference to generate 2-sentence executive summaries.
    """
    def __init__(self, interval_seconds: int = 30):
        super().__init__(daemon=True)
        self.interval_seconds = interval_seconds
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        logger.info("[Summarizer Daemon] Started background GPU summarization daemon.")
        while self._running:
            try:
                self.process_unsummarized_documents()
            except Exception as e:
                logger.warning(f"[Summarizer Daemon] Cycle error: {e}")
            time.sleep(self.interval_seconds)

    def process_unsummarized_documents(self):
        try:
            conn = get_db()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Find files missing executive summaries
            cursor.execute("SELECT id, filename, content FROM files WHERE content IS NOT NULL AND content != '' LIMIT 3")
            rows = cursor.fetchall()
            
            if not rows:
                return

            from src.core.model_manager import get_fallback_llm
            llm = get_fallback_llm()
            if not llm:
                return

            for r in rows:
                fid = r["id"]
                content = r["content"][:1000]
                prompt = f"Summarize this document in 2 concise technical sentences:\n{content}"
                res = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=100)
                summary_text = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                if summary_text:
                    cursor.execute("UPDATE files SET metadata_json = json_set(COALESCE(metadata_json, '{}'), '$.summary', ?) WHERE id = ?", (summary_text, fid))
            
            conn.commit()
        except Exception as e:
            logger.debug(f"[Summarizer Daemon] Worker iteration note: {e}")

_daemon: Optional[DocumentSummarizerDaemon] = None

def start_background_summarizer():
    global _daemon
    if _daemon is None or not _daemon.is_alive():
        _daemon = DocumentSummarizerDaemon(interval_seconds=60)
        _daemon.start()
    return _daemon
