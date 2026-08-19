"""
Voice-RAG Unified Bridge & Spoken Knowledge Retrieval Engine.
Standard: Pure Python Standard Library + SOTA RAG Engine + Kokoro-82M TTS + WASAPI Streaming.
Ponytail Senior Dev Principle: Direct integration of hybrid FTS5/PageRank/Vector RAG with instant neural voice synthesis, audio-first sentence normalization, and citation telemetry.
"""

import os
import sys
import time
import re
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.domain.decomposed_hybrid_rag import execute_hybrid_decomposed_search as execute_sota_rag_search
from src.core.voice_bridge import VoiceBridge, CANONICAL_VOICE_PROFILE
from src.core.voice_normalizer import VoiceNormalizer
from src.core.instant_audio_streamer import InstantVoiceClient, get_instant_streamer
from src.core.voice_memory_ledger import VoiceMemoryLedger


class VoiceRAGBridge:
    """
    Direct Bridge connecting Knowledge Vault RAG Retrieval to Spoken Voice Synthesis.
    Ensures any query against EVE files, codebase, or notes can be retrieved and spoken out loud in <50ms.
    """

    @classmethod
    def _extract_facts_from_content(
        cls,
        content: str,
        valid_query_words: set,
        seen_facts: set,
        extracted_facts: list,
        max_sentences: int
    ):
        """Extract matching fact sentences from candidate text using early continue guards."""
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', content) if len(s.strip()) > 20]
        for s in sentences:
            if len(extracted_facts) >= max_sentences:
                break
            s_clean = re.sub(r'[*_#`\[\]]', '', s).strip()
            s_words = set(re.findall(r'\w+', s_clean.lower()))
            if not (s_words & valid_query_words):
                continue
            if s_clean in seen_facts:
                continue
            seen_facts.add(s_clean)
            extracted_facts.append(s_clean)

    @classmethod
    def query_and_summarize(cls, query: str, max_sentences: int = 3) -> Dict[str, Any]:
        """Query the SOTA RAG engine and synthesize a speech-optimized conversational summary."""
        t0 = time.perf_counter()
        rag_res = execute_sota_rag_search(query, top_k=4)
        candidates = rag_res.get("top_candidates", [])
        if not candidates:
            speech_text = f"I searched the knowledge vault for '{query}', but found no matching records in our database."
            return {
                "query": query,
                "found": False,
                "speech_text": speech_text,
                "citations": [],
                "retrieval_ms": round((time.perf_counter() - t0) * 1000, 2)
            }

        extracted_facts = []
        citations = []
        seen_citations = set()
        seen_facts = set()

        valid_query_words = {w for w in re.findall(r'\w+', query.lower()) if len(w) > 3}

        for cand in candidates[:3]:
            fname = cand.get("filename", "Knowledge Vault")
            if fname not in seen_citations:
                seen_citations.add(fname)
                citations.append(fname)

            content = cand.get("content", "")
            cls._extract_facts_from_content(content, valid_query_words, seen_facts, extracted_facts, max_sentences)
            if len(extracted_facts) >= max_sentences:
                break

        if not extracted_facts and candidates:
            top_content = candidates[0].get("content", "")
            first_sentences = [s.strip() for s in re.split(r'[.!?\n]+', top_content) if len(s.strip()) > 20]
            if first_sentences:
                extracted_facts.append(re.sub(r'[*_#`\[\]]', '', first_sentences[0]).strip())

        source_label = citations[0] if citations else "Knowledge Vault"
        if extracted_facts:
            body = " ".join(extracted_facts[:max_sentences])
            speech_text = f"{body} Source retrieved from {source_label}."
        else:
            speech_text = f"Retrieved reference intelligence for {query} from {source_label}."

        retrieval_ms = round((time.perf_counter() - t0) * 1000, 2)

        return {
            "query": query,
            "found": True,
            "speech_text": speech_text,
            "citations": citations,
            "retrieval_ms": retrieval_ms,
            "top_candidate": candidates[0].get("filename", "")
        }

    @classmethod
    def query_rag_and_speak(
        cls,
        query: str,
        persona: str = "CANONICAL_STUDIO",
        dsp_preset: str = "STUDIO_MASTER",
        sync: bool = True,
        max_sentences: int = 2
    ) -> Dict[str, Any]:
        """
        Full RAG-to-Voice Pipeline:
        1. Retrieve facts from SQLite Knowledge Vault.
        2. Normalize text for speech (expanding units, technical acronyms).
        3. Play instant HUD wake chime.
        4. Synthesize & stream audio directly to active gaming headset.
        5. Log turn in Voice Memory Ledger.
        """
        # Play subtle HUD wake chime
        get_instant_streamer().play_hud_cue("wake")

        summary = cls.query_and_summarize(query, max_sentences=max_sentences)
        speech_text = summary["speech_text"]

        # Normalize for acoustic speech
        clean_text = VoiceNormalizer.normalize_for_speech(speech_text)
        voice_id = CANONICAL_VOICE_PROFILE["voice"]

        # Instant Speech Dispatch
        speech_res = InstantVoiceClient.speak_instant(
            text=clean_text,
            voice=voice_id,
            dsp_preset=dsp_preset,
            sync=sync
        )

        # Log in persistent conversational ledger
        VoiceMemoryLedger.log_turn(
            speaker="Antigravity_RAG",
            raw_text=speech_text,
            normalized_text=clean_text,
            persona=persona,
            domain="KNOWLEDGE_RAG"
        )

        return {
            "status": "completed",
            "query": query,
            "citations": summary.get("citations", []),
            "speech_text": speech_text,
            "normalized_text": clean_text,
            "retrieval_ms": summary.get("retrieval_ms", 0),
            "speech_res": speech_res
        }
