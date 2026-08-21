"""
Async Query Transformation Layer:
- HyDE (Hypothetical Document Embeddings): Generates hypothetical answer passages to bridge vocabulary gap.
- Step-Back Abstraction: Generates higher-level conceptual queries for broad architectural context.
- Sub-Query Decomposition: Breaks multi-variable questions into targeted sub-searches.
"""

import asyncio
import json
import logging
import os
import re
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("OPENAI_API_BASE", "http://host.docker.internal:11434/v1")
OLLAMA_CHAT_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:7b")


class AsyncQueryTransformer:
    """Async Query Transformation and Pre-Retrieval Expansion Engine."""

    @staticmethod
    def _generate_deterministic_hyde(prompt: str) -> str:
        """
        Fast, zero-dependency deterministic HyDE generator.
        Constructs an answer-first documentation passage from extracted intent and keywords.
        """
        clean = prompt.strip()
        words = re.findall(r'\b[a-zA-Z0-9_\-]+\b', clean)
        
        # Check for error codes / common issues
        has_error = bool(re.search(r'\b(error|fail|bug|exception|crash|winerror|permission)\b', clean, re.IGNORECASE))
        has_windows = bool(re.search(r'\b(windows|win32|ntfs|os\.remove)\b', clean, re.IGNORECASE))
        has_sqlite = bool(re.search(r'\b(sqlite|database|conn|shm|wal|transaction)\b', clean, re.IGNORECASE))
        
        if has_sqlite and has_windows and has_error:
            return (
                "On Windows environments, SQLite connection handles held by background worker threads "
                "prevent file deletion and raise PermissionError. Connections must be explicitly reset "
                "and closed across all background registries prior to unlinking database files."
            )
        elif has_error:
            return (
                f"To resolve {clean}, ensure proper prerequisite resource cleanup and exception handling. "
                "Inspect system logs and verify file access permissions before executing recovery routines."
            )
        else:
            key_terms = " ".join([w for w in words if len(w) > 3][:6])
            return (
                f"Standard implementation for {clean}: Configure system parameters to support {key_terms}. "
                "Ensure robust resource allocation and state synchronization across execution pipelines."
            )

    @classmethod
    async def generate_hyde_passage_async(cls, prompt: str, timeout: float = 2.0) -> str:
        """
        Generates a 2-3 sentence hypothetical answer passage using local LLM or fallback.
        """
        if not prompt or not prompt.strip():
            return ""

        base = OLLAMA_BASE_URL.replace("/v1", "").replace("host.docker.internal", "127.0.0.1")
        url = f"{base}/api/generate"
        system_inst = "You are a technical knowledge assistant. Write a concise 2-sentence direct factual answer passage that would appear in documentation for this question. Do not include conversational filler."

        payload = json.dumps({
            "model": OLLAMA_CHAT_MODEL,
            "prompt": f"{system_inst}\n\nQuestion: {prompt}\nPassage:",
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 120
            }
        }).encode("utf-8")

        def _call_llm():
            try:
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=timeout) as res:
                    body = json.loads(res.read().decode("utf-8"))
                    return body.get("response", "").strip()
            except Exception as e:
                logger.debug(f"HyDE LLM generation offline ({e}); using deterministic fallback")
                return ""

        loop = asyncio.get_event_loop()
        try:
            hyde_text = await loop.run_in_executor(None, _call_llm)
            if hyde_text and len(hyde_text) > 20:
                return hyde_text
        except Exception:
            pass

        return cls._generate_deterministic_hyde(prompt)

    @staticmethod
    def generate_step_back_query(prompt: str) -> str:
        """
        Abstracts specific error/implementation query into a high-level conceptual inquiry.
        E.g., 'Fix WinError 32 sqlite db-wal' -> 'SQLite database locking architecture and connection lifecycle'
        """
        clean = prompt.strip()
        low = clean.lower()

        # Remove ephemeral error codes and specific parameters
        cleaned = re.sub(r'\b(fix|how to fix|resolve|error|winerror\s*\d+|exception|traceback)\b', '', clean, flags=re.IGNORECASE).strip()
        
        # Tech domain abstractions
        if "sqlite" in low or "database" in low:
            return f"Database architecture and connection lifecycle principles for {cleaned}".strip()
        elif "memory" in low or "leak" in low:
            return f"Memory management and resource lifecycle architecture for {cleaned}".strip()
        elif "network" in low or "socket" in low or "port" in low:
            return f"Network socket lifecycle and connection handling for {cleaned}".strip()
        elif "rag" in low or "retrieval" in low or "search" in low:
            return f"Information retrieval architecture and semantic indexing concepts for {cleaned}".strip()
        
        return f"Core concepts and architectural overview of {cleaned or clean}"

    @classmethod
    def decompose_sub_queries(cls, prompt: str) -> List[str]:
        """
        Decomposes complex multi-variable prompts into distinct search vectors.
        """
        if not prompt or not prompt.strip():
            return []

        sub_queries = [prompt.strip()]
        
        # Split on conjunctions / multi-part clauses
        parts = re.split(r'\b(?:and also|as well as|while maintaining|along with|furthermore)\b', prompt, flags=re.IGNORECASE)
        if len(parts) > 1:
            for p in parts:
                p_clean = p.strip()
                if len(p_clean) > 8 and p_clean not in sub_queries:
                    sub_queries.append(p_clean)

        step_back = cls.generate_step_back_query(prompt)
        if step_back and step_back not in sub_queries:
            sub_queries.append(step_back)

        return sub_queries

    @classmethod
    async def transform_query_async(cls, prompt: str) -> Dict[str, Any]:
        """
        Full async query transformation pipeline.
        Returns: {
            'raw_prompt': str,
            'hyde_passage': str,
            'step_back_query': str,
            'sub_queries': List[str]
        }
        """
        hyde_task = cls.generate_hyde_passage_async(prompt)
        step_back = cls.generate_step_back_query(prompt)
        sub_queries = cls.decompose_sub_queries(prompt)
        
        hyde_passage = await hyde_task
        
        return {
            "raw_prompt": prompt,
            "hyde_passage": hyde_passage,
            "step_back_query": step_back,
            "sub_queries": sub_queries
        }
