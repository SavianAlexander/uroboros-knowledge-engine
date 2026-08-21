"""
Situational Query Analyzer (Pre-Retrieval Analysis & Transformation Layer)
Deconstructs complex, paragraph-length, multi-variable situational queries into:
1. Core semantic query vector representation
2. Extracted filter attributes (environments, technologies, constraints, intents)
3. Sub-queries for multi-hop / multi-variable retrieval
4. Dynamic SQL metadata filter predicates
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple

# Pre-compiled Regex patterns for situational intent and entity extraction
RE_CONVERSATIONAL_FILLERS = re.compile(
    r'\b(hello|hi\s+team|hi|hey|greetings|please|could you please|can you please|can you tell me|i am wondering|i want to know|i need help with|how do i|what is the best way to|help us understand|we are seeing|we have an issue where|our team encountered)\b\s*,?\s*',
    re.IGNORECASE
)

RE_INTENT_PATTERNS = {
    "troubleshooting": re.compile(r'\b(error|bug|issue|fail|failed|failure|crash|timeout|corrupt|corrupted|malformed|panic|exception|traceback|winerror|locked|busy|hang|freeze|unresponsive|fix|debug)\b', re.IGNORECASE),
    "pricing": re.compile(r'(\$|€|£|\b(price|pricing|cost|tier|plan|subscription|billing|fee|quota|rate)\b)', re.IGNORECASE),
    "technical_spec": re.compile(r'\b(api|endpoint|schema|interface|spec|specification|parameter|signature|contract|protocol|rfc|architecture|ast|json|yaml)\b', re.IGNORECASE),
    "procedural": re.compile(r'\b(step|steps|how\s+to|guide|tutorial|install|configure|configuration|setup|deploy|start|run|build|execute|migrate)\b', re.IGNORECASE),
    "doubt_objection": re.compile(r'\b(limitation|caveat|warning|caution|trade-off|drawback|risk|ceiling|disadvantage|faq)\b', re.IGNORECASE),
    "conceptual": re.compile(r'\b(overview|introduction|concept|theory|principle|definition|what\s+is|background|philosophy)\b', re.IGNORECASE)
}

RE_ENVIRONMENTS = {
    "windows": re.compile(r'\b(windows|win10|win11|win32|powershell|cmd\.exe|ntfs)\b', re.IGNORECASE),
    "linux": re.compile(r'\b(linux|ubuntu|debian|centos|alpine|posix|bash)\b', re.IGNORECASE),
    "macos": re.compile(r'\b(macos|darwin|osx|apple|homebrew)\b', re.IGNORECASE),
    "wsl": re.compile(r'\b(wsl|wsl2|virtualization)\b', re.IGNORECASE),
    "docker": re.compile(r'\b(docker|docker-desktop|container|compose|k8s|kubernetes)\b', re.IGNORECASE)
}

RE_TECHNOLOGIES = {
    "sqlite": re.compile(r'\b(sqlite|sqlite3|wal|shm|fts5)\b', re.IGNORECASE),
    "fastapi": re.compile(r'\b(fastapi|uvicorn|starlette|pydantic)\b', re.IGNORECASE),
    "python": re.compile(r'\b(python|pytest|unittest|pip|venv)\b', re.IGNORECASE),
    "react": re.compile(r'\b(react|typescript|javascript|frontend|ui|tailwind|webpack)\b', re.IGNORECASE),
    "kokoro": re.compile(r'\b(kokoro|tts|voice|onnx|audio)\b', re.IGNORECASE),
    "ollama": re.compile(r'\b(ollama|llm|qwen|llama)\b', re.IGNORECASE),
    "tududi": re.compile(r'\b(tududi|taskmaster|mcp)\b', re.IGNORECASE)
}


@dataclass
class SituationalQueryPlan:
    """Structured situational retrieval query plan with extracted attributes and sub-queries."""
    raw_query: str
    core_semantic_query: str
    intent_type: str = "general"
    extracted_filters: Dict[str, Any] = field(default_factory=dict)
    environments: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    sub_queries: List[str] = field(default_factory=list)
    attribute_weights: Dict[str, float] = field(default_factory=dict)
    sql_filter_clauses: List[str] = field(default_factory=list)
    sql_filter_params: List[Any] = field(default_factory=list)


class SituationalQueryAnalyzer:
    """
    Analyzes complex user prompts and decomposes them into attribute-aware search plans.
    """

    @classmethod
    def analyze_situational_query(cls, query: str) -> SituationalQueryPlan:
        """
        Main entry point: decomposes query into core semantic vector query,
        extracted filter attributes, detected technologies/environments, and sub-queries.
        """
        if not query or not str(query).strip():
            return SituationalQueryPlan(raw_query="", core_semantic_query="")

        norm_q = unicodedata.normalize("NFC", str(query).strip())

        # 1. Detect Intent Type
        intent_scores = {intent: len(pat.findall(norm_q)) for intent, pat in RE_INTENT_PATTERNS.items()}
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        best_intent, best_score = sorted_intents[0]
        intent_type = best_intent if best_score > 0 else "general"

        # 2. Extract Environments & Technologies
        environments = [env for env, pat in RE_ENVIRONMENTS.items() if pat.search(norm_q)]
        technologies = [tech for tech, pat in RE_TECHNOLOGIES.items() if pat.search(norm_q)]

        # 3. Extract Explicit Key-Value Filters (e.g. env:windows, ext:py, tag:sqlite, intent:troubleshooting)
        extracted_filters = {}
        cleaned_for_semantic = norm_q

        kv_matches = re.findall(r'\b(env|os|tech|tag|ext|intent|scope):([a-zA-Z0-9_\-]+)\b', norm_q, re.IGNORECASE)
        for key, val in kv_matches:
            extracted_filters[key.lower()] = val.lower()
            cleaned_for_semantic = re.sub(rf'\b{key}:{val}\b', '', cleaned_for_semantic, flags=re.IGNORECASE)

        if environments and "env" not in extracted_filters:
            extracted_filters["env"] = environments[0]
        if technologies and "tech" not in extracted_filters:
            extracted_filters["tech"] = technologies[0]
        if intent_type != "general" and "intent" not in extracted_filters:
            extracted_filters["intent"] = intent_type

        # 4. Synthesize Core Semantic Query (stripped of conversational filler)
        core_sem = RE_CONVERSATIONAL_FILLERS.sub('', cleaned_for_semantic).strip()
        # Remove repeated whitespace and punctuation clutter
        core_sem = re.sub(r'[\r\n\t]+', ' ', core_sem)
        core_sem = re.sub(r'\s{2,}', ' ', core_sem).strip()
        if not core_sem:
            core_sem = norm_q

        # 5. Decompose into Multi-Hop / Situational Sub-Queries
        sub_queries = cls._decompose_situational_subqueries(
            raw_query=norm_q,
            core_query=core_sem,
            intent=intent_type,
            environments=environments,
            technologies=technologies
        )

        # 6. Build SQL metadata filter clauses
        sql_clauses = []
        sql_params = []
        if "ext" in extracted_filters:
            sql_clauses.append("files.filename LIKE ?")
            sql_params.append(f"%.{extracted_filters['ext']}")

        # 7. Compute Attribute Importance Weights
        attr_weights = {
            "intent_match_weight": 0.25 if intent_type != "general" else 0.0,
            "environment_match_weight": 0.35 if environments else 0.0,
            "technology_match_weight": 0.40 if technologies else 0.0,
        }

        return SituationalQueryPlan(
            raw_query=norm_q,
            core_semantic_query=core_sem,
            intent_type=intent_type,
            extracted_filters=extracted_filters,
            environments=environments,
            technologies=technologies,
            sub_queries=sub_queries,
            attribute_weights=attr_weights,
            sql_filter_clauses=sql_clauses,
            sql_filter_params=sql_params
        )

    @classmethod
    def _decompose_situational_subqueries(
        cls,
        raw_query: str,
        core_query: str,
        intent: str,
        environments: List[str],
        technologies: List[str]
    ) -> List[str]:
        """
        Decomposes complex multi-sentence or multi-variable queries into focused sub-queries.
        """
        sub_queries = [core_query]

        # If multiple sentences, extract distinct actionable phrases
        sentences = [s.strip() for s in re.split(r'[.!?;\n]+', raw_query) if s.strip() and len(s.strip().split()) >= 3]
        for s in sentences[:3]:
            clean_s = RE_CONVERSATIONAL_FILLERS.sub('', s).strip()
            if clean_s and clean_s != core_query and clean_s not in sub_queries:
                sub_queries.append(clean_s)

        # Technology + Intent focused variations
        for tech in technologies[:2]:
            variant = f"{tech} {intent} {core_query}" if intent != "general" else f"{tech} {core_query}"
            if variant not in sub_queries:
                sub_queries.append(variant)

        # Environment + Technology combination
        if environments and technologies:
            env_tech_variant = f"{environments[0]} {technologies[0]} {core_query}"
            if env_tech_variant not in sub_queries:
                sub_queries.append(env_tech_variant)

        return sub_queries[:5]
