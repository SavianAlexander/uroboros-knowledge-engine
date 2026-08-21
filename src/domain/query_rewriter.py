"""
Conversational Query Rewriting & Coreference Resolution Module.
De-contextualizes multi-turn follow-up prompts into standalone retrieval queries.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Ambiguous pronouns and elliptical references
PRONOUN_PATTERN = re.compile(
    r'\b(it|that|they|them|this|these|those|its|their|the second one|the first one|the previous one|the latter|the former|there|here|that one|the other one)\b',
    re.IGNORECASE
)

CONTEXTUAL_PHRASES = re.compile(
    r'\b(why|how come|what about|tell me more|expand on that|and then|instead|explain that|fix it|does it|can it|how do I extend it|how to configure it)\b',
    re.IGNORECASE
)


class ConversationalQueryRewriter:
    """
    Analyzes multi-turn dialogue history and rewrites ambiguous conversational prompts
    into entity-complete, self-contained retrieval queries.
    """

    @staticmethod
    def is_contextual_query(query: str, history: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        Heuristic fast-path: returns True if query depends on prior dialogue context.
        Returns False for fully standalone queries to bypass rewriting overhead (0ms latency).
        """
        if not history or len(history) == 0:
            return False

        q_clean = query.strip()
        words = q_clean.split()

        # Very short queries are typically elliptical follow-ups
        if len(words) <= 3 and any(w.lower() in {"why", "how", "what", "where", "who", "when"} for w in words):
            return True

        if PRONOUN_PATTERN.search(q_clean) or CONTEXTUAL_PHRASES.search(q_clean):
            return True

        return False

    @staticmethod
    def extract_recent_entities(history: List[Dict[str, str]], max_turns: int = 4) -> List[str]:
        """
        Extracts salient named entities, technical identifiers, and key noun phrases from recent turns.
        """
        salient_terms: List[str] = []
        recent_turns = history[-max_turns:]

        for turn in reversed(recent_turns):
            content = turn.get("content", "")
            # Extract hyphenated or backticked identifiers (e.g., `cluster-alpha`, `retention-policy`)
            identifiers = re.findall(r'[`"]([a-zA-Z0-9_\-\.]+)["`]', content)
            salient_terms.extend(identifiers)

            # Extract capitalized multi-word phrases or domain terms
            entities = re.findall(r'\b(?:[A-Z][a-z]+|[a-z0-9]+-[a-z0-9]+)\b(?:\s+[a-zA-Z0-9_\-]+)*', content)
            salient_terms.extend(entities)

            # Extract technical phrases like 'retention policy', 'connection pool', etc.
            tech_patterns = re.findall(r'\b(?:[a-zA-Z0-9_\-]+)\s+(?:policy|config|architecture|database|cluster|engine|service|cache|token|pipeline|queue)\b', content, re.IGNORECASE)
            salient_terms.extend(tech_patterns)

        # Preserve order while deduplicating
        deduped = []
        seen = set()
        for term in salient_terms:
            t_lower = term.lower().strip()
            if t_lower and t_lower not in seen and len(t_lower) > 2:
                seen.add(t_lower)
                deduped.append(term.strip())

        return deduped

    @classmethod
    def rewrite_query(
        cls,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        llm_fn: Optional[Callable[[str], str]] = None
    ) -> str:
        """
        De-contextualizes follow-up query against chat history.
        Uses fast LLM pass if provided, otherwise applies deterministic coreference resolution.
        """
        if not cls.is_contextual_query(query, history):
            return query.strip()

        history = history or []

        # 1. LLM-Assisted Rewriting (if callable supplied)
        if llm_fn:
            try:
                history_ctx = "\n".join([f"{t.get('role', 'user')}: {t.get('content', '')}" for t in history[-4:]])
                prompt = (
                    f"Given the conversation history:\n{history_ctx}\n\n"
                    f"Rewrite the follow-up question into an unambiguous, entity-complete standalone search query:\n"
                    f"Follow-up: {query}\n"
                    f"Standalone Query:"
                )
                rewritten = llm_fn(prompt).strip()
                if rewritten and len(rewritten) > 5 and not rewritten.lower().startswith("error"):
                    return rewritten.strip('"`')
            except Exception as e:
                logger.warning("LLM query rewrite failed, falling back to heuristic resolution: %s", e)

        # 2. Deterministic Heuristic Coreference Resolution
        entities = cls.extract_recent_entities(history)
        if not entities:
            return query.strip()

        # Combine primary entity with secondary domain noun if available
        primary_entity = entities[0]
        full_antecedent = primary_entity
        for secondary in entities[1:]:
            if secondary.lower() not in full_antecedent.lower():
                full_antecedent = f"{primary_entity} {secondary}"
                break

        # Replace first pronoun with antecedent
        def _replace_pronoun(match):
            return full_antecedent

        rewritten = PRONOUN_PATTERN.sub(_replace_pronoun, query, count=1)
        
        # If query was elliptical without direct pronoun match (e.g., "How to extend to 30 days?")
        if rewritten == query:
            rewritten = f"{query.rstrip('?')} for {full_antecedent}?"

        return rewritten.strip()

    @classmethod
    async def rewrite_query_async(
        cls,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        llm_fn: Optional[Callable[[str], str]] = None
    ) -> str:
        """Asynchronous entry point for query rewriting."""
        return cls.rewrite_query(query, history, llm_fn)
