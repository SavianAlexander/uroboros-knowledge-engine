"""
Adaptive Multi-Dimensional Semantic Query Analyzer & Cognitive Prompt Synthesizer.
Standard: Pure Python Standard Library (math, re, unicodedata, dataclasses, typing).
Ponytail Senior Dev Principle: Continuous mathematical affinity scoring over rigid keyword matching.
"""

import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class SemanticAffinityProfile:
    """Continuous multi-dimensional cognitive affinity profile for a query and context."""
    conversational: float = 0.0
    code_engineering: float = 0.0
    quantitative_math: float = 0.0
    legal_statutory: float = 0.0
    grounded_retrieval: float = 0.0
    primary_mode: str = "GENERAL_RAG"
    lexical_entropy: float = 0.0
    interrogative_ratio: float = 0.0


class AdaptivePromptSynthesizer:
    """
    Dynamically analyzes query semantics, information density, and retrieval grounding
    to synthesize tailored system prompts and cognitive instructions.
    """

    # Compiled structural syntax patterns
    RE_CODE_SYNTAX = re.compile(
        r'(\b(def|class|import|from|async|await|return|function|const|let|var|SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|JOIN|GROUP\s+BY|ORDER\s+BY|python|typescript|javascript|react|rust|sql|endpoint|api|bug|fix|error|exception|traceback|refactor|compile|git|npm|pip|cargo|docker|kubectl|frontend|backend|json|yaml|html|css)\b|[{}\[\]();=><+\-*\/]|\b[a-z0-9]+_[a-z0-9]+\b|\b[a-zA-Z0-9]+\.[a-zA-Z0-9]+\b)',
        re.IGNORECASE
    )
    RE_MATH_SYNTAX = re.compile(
        r'(\b\d+(\.\d+)?%?\b|[$€£¥§=+\-*\/^<>]|\b(sum|avg|mean|median|std|variance|ratio|percentage|calculate|formula|matrix|integral|derivative|equation|algebra|margin|revenue|quarterly|floating\s*point)\b)',
        re.IGNORECASE
    )
    RE_STATUTORY_SYNTAX = re.compile(
        r'(\b§|\b\d+\s*(cfr|usc|sec|iso|iec|rfc)\b|\b(statute|statutory|regulation|regulatory|compliance|fiduciary|liability|article|clause|subpart|provision|audit\s*rule)\b)',
        re.IGNORECASE
    )
    RE_INTERROGATIVES = re.compile(
        r'\b(what|how|why|who|where|when|can|could|would|is|are|tell|explain|summarize|help|hi|hello|hey|introduce|good\s+morning|good\s+evening)\b',
        re.IGNORECASE
    )

    @classmethod
    def compute_lexical_entropy(cls, text: str) -> float:
        """Calculates Shannon information entropy of word token distribution in bits."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        n = len(words)
        freqs: Dict[str, int] = {}
        for w in words:
            freqs[w] = freqs.get(w, 0) + 1
        entropy = -sum((count / n) * math.log2(count / n) for count in freqs.values())
        return round(entropy, 4)

    @classmethod
    def analyze_query(
        cls,
        query: str,
        grounding_confidence: float = 0.0,
        candidate_count: int = 0
    ) -> SemanticAffinityProfile:
        """
        Computes continuous multi-dimensional cognitive affinities from query text
        and retrieval grounding signals.
        """
        q_norm = unicodedata.normalize("NFC", query or "").strip()
        tokens = re.findall(r'\b\w+\b', q_norm.lower())
        total_tokens = max(1, len(tokens))

        # 1. Structural pattern density
        code_matches = len(cls.RE_CODE_SYNTAX.findall(q_norm))
        math_matches = len(cls.RE_MATH_SYNTAX.findall(q_norm))
        legal_matches = len(cls.RE_STATUTORY_SYNTAX.findall(q_norm))
        interrogative_matches = len(cls.RE_INTERROGATIVES.findall(q_norm))

        # 2. Grounding score based on candidate count and confidence
        # G approaches grounding_confidence as candidate_count grows
        grounding_score = grounding_confidence * (1.0 - math.exp(-max(0, candidate_count) / 2.0))
        grounding_score = min(1.0, max(0.0, grounding_score))

        # 3. Interrogative ratio and entropy
        interrogative_ratio = interrogative_matches / total_tokens
        entropy = cls.compute_lexical_entropy(q_norm)

        # 4. Continuous affinity scoring [0.0, 1.0]
        a_code = min(1.0, (code_matches * 0.40) / max(1.0, math.sqrt(total_tokens)))
        a_math = min(1.0, (math_matches * 0.40) / max(1.0, math.sqrt(total_tokens)))
        a_legal = min(1.0, (legal_matches * 0.50) / max(1.0, math.sqrt(total_tokens)))

        # Conversational affinity is highest when query is short and non-technical
        technical_presence = max(a_code, a_math, a_legal)
        raw_conv = (interrogative_ratio * 0.8) + (0.6 if total_tokens <= 4 and interrogative_matches > 0 else 0.0)
        a_conv = min(1.0, max(0.0, (raw_conv - 0.5 * technical_presence) * (1.0 - 0.7 * grounding_score)))

        # 5. Determine primary operational mode dynamically
        affinities = {
            "GENERAL_RAG": max(0.01, grounding_score),
            "TECHNICAL_CODE": a_code,
            "MATHEMATICAL_ANALYTIC": a_math,
            "LEGAL_STATUTORY": a_legal,
            "GREETING_CONVERSATIONAL": a_conv
        }
        primary_mode = max(affinities.keys(), key=lambda k: affinities[k])
        if primary_mode == "GREETING_CONVERSATIONAL" and (grounding_score > 0.40 or technical_presence > 0.30 or a_conv <= 0.05):
            primary_mode = max([("TECHNICAL_CODE", a_code), ("MATHEMATICAL_ANALYTIC", a_math), ("LEGAL_STATUTORY", a_legal), ("GENERAL_RAG", max(0.01, grounding_score))], key=lambda x: x[1])[0]

        return SemanticAffinityProfile(
            conversational=round(a_conv, 3),
            code_engineering=round(a_code, 3),
            quantitative_math=round(a_math, 3),
            legal_statutory=round(a_legal, 3),
            grounded_retrieval=round(grounding_score, 3),
            primary_mode=primary_mode,
            lexical_entropy=entropy,
            interrogative_ratio=round(interrogative_ratio, 3)
        )

    @classmethod
    def synthesize_adaptive_system_prompt(
        cls,
        profile: SemanticAffinityProfile,
        domain_guidelines: Optional[str] = None
    ) -> str:
        """
        Dynamically constructs an adaptive system prompt by composing modular cognitive facets
        weighted by the query's continuous affinity profile.
        """
        prompt_parts: List[str] = [
            "You are Uroboros AI, an advanced senior staff AI research assistant and cognitive operating engine."
        ]

        # Conversational / System Awareness Facet
        if profile.conversational > 0.35 and profile.grounded_retrieval < 0.30:
            prompt_parts.append(
                "You have direct access to the Uroboros Knowledge Vault, 3D Graph & Wikilink Explorer, Kokoro Neural Voice Engine, "
                "SQLite WAL Search Index with FTS5, and Real-time Multi-Hop RAG Pipeline. "
                "Engage helpfully, concisely, and warmly, guiding the user to explore the vault and capabilities when appropriate."
            )
        else:
            prompt_parts.append(
                "Provide clear, thorough, highly analytical, and well-structured answers using Markdown headings, "
                "bullet points, and technical precision."
            )

        # Code Architecture Facet
        if profile.code_engineering > 0.25:
            prompt_parts.append(
                "Focus on writing clean, modular, production-grade code adhering to zero-dependency and clean architecture principles. "
                "Include complete type annotations, docstrings, and robust error handling."
            )

        # Quantitative & Math Facet
        if profile.quantitative_math > 0.25:
            prompt_parts.append(
                "Format mathematical equations and algorithmic notation using standard LaTeX ($...$ for inline, $$...$$ for block). "
                "Present tabular metrics and calculations in clean Markdown tables."
            )

        # Statutory & Legal Facet
        if profile.legal_statutory > 0.25:
            prompt_parts.append(
                "Ground regulatory and statutory analysis strictly in authoritative provisions, citing specific titles, parts, and sections."
            )

        # Grounded Attribution Facet
        if profile.grounded_retrieval > 0.30:
            prompt_parts.append(
                "When synthesizing facts from the Document Vault Context, explicitly reference source file names and line ranges."
            )

        if domain_guidelines:
            prompt_parts.append(f"Domain Guidelines: {domain_guidelines}")

        return " ".join(prompt_parts)

    @classmethod
    def synthesize_fallback_response(
        cls,
        query: str,
        profile: SemanticAffinityProfile,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesizes an intelligent, contextually aware assistant response in offline/fallback mode
        without relying on brittle static text templates.
        """
        if citations:
            resp = "**Retrieved Vault Evidence**:\n\n"
            for c in citations:
                fn = c.get("filename") or c.get("title") or "Document"
                snip = c.get("snippet") or c.get("text") or ""
                resp += f"- **{fn}**: {snip.strip()}\n"
            return resp

        # Zero-retrieval fallback dynamically adapted to intent profile
        if profile.conversational > 0.30:
            return (
                "Hello! I am Uroboros AI, your local cognitive knowledge assistant.\n\n"
                "I am connected to your document vault, 3D knowledge graph, and full-duplex neural voice engine. "
                "You can ask me to search indexed files, analyze legal statutes, review code architectures, or explore semantic clusters."
            )
        elif profile.code_engineering > 0.30:
            return (
                f"I analyzed your code query: `{query}`.\n\n"
                "No matching AST nodes or files were found in the current index. "
                "You can index your workspace directory via the Workspace Explorer or configure auto-rules to ingest specific source files."
            )
        elif profile.legal_statutory > 0.30:
            return (
                f"I processed your regulatory query regarding: *{query}*.\n\n"
                "No statutory provisions are currently indexed for this specific query in the local vault. "
                "You can sync primary sources via `python scripts/neuro_cli.py sync_sources` or ingest CFR/statute records."
            )
        else:
            return (
                f"I processed your query: *{query}*.\n\n"
                "No direct document context was found in the indexed vault for this topic. "
                "Try searching with different keywords or indexing your target folder in the Workspace Explorer."
            )
