"""
Micro-Moment Query Classifier & Dynamic Prompt Router:
Classifies queries into one of four core micro-moments:
1. WANT_TO_KNOW: Conceptual, educational, informational understanding.
2. WANT_TO_GO_LOCATE: Entity/provider selection, local attributes, specialized capabilities.
3. WANT_TO_DO: Tactical troubleshooting, procedural walkthroughs, step-by-step execution.
4. WANT_TO_BUY_DECIDE: Commercial evaluation, pricing, trade-offs, objection handling, disqualifiers.
"""

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


class MicroMoment(str, Enum):
    WANT_TO_KNOW = "WANT_TO_KNOW"
    WANT_TO_GO_LOCATE = "WANT_TO_GO_LOCATE"
    WANT_TO_DO = "WANT_TO_DO"
    WANT_TO_BUY_DECIDE = "WANT_TO_BUY_DECIDE"


@dataclass
class MomentClassificationResult:
    moment: MicroMoment
    confidence: float
    intent_description: str
    retrieval_strategy: Dict[str, Any] = field(default_factory=dict)
    matched_patterns: List[str] = field(default_factory=list)


class MicroMomentClassifier:
    """
    Sub-millisecond regex & rule-based classifier detecting user Micro-Moments.
    """

    # 1. WANT_TO_GO_LOCATE Patterns (Entity, provider, location, specialist selection)
    GO_LOCATE_PATTERNS = [
        re.compile(r'(?i)\b(?:find|locate|search for|who (?:is|are|provides|supports)|where (?:can I find|is|are)|specialist|dealer|distributor|technician|vendor|provider|shop|contractor|near|in\s+[A-Z][a-z]+)\b'),
        re.compile(r'(?i)\b(?:local\s+(?:specialist|expert|provider|service|shop|repair))\b'),
        re.compile(r'(?i)\b(?:which\s+(?:server|region|datacenter|endpoint|cluster|zone)\s+(?:in|for|supports))\b')
    ]

    # 2. WANT_TO_DO Patterns (Actionable steps, troubleshooting, setup, commands, how-to)
    DO_PATTERNS = [
        re.compile(r'(?i)\b(?:step-by-step|step by step|how\s+to\s+(?:rebuild|fix|repair|install|configure|deploy|setup|reset|unmap|execute|migrate|restore|recover|update|create))\b'),
        re.compile(r'(?i)\b(?:instructions\s+to|guide\s+to|walkthrough|tutorial|runbook|troubleshoot|resolve\s+(?:error|issue|bug|lock))\b'),
        re.compile(r'(?i)\b(?:commands?\s+to|procedure\s+for|workflow\s+for)\b')
    ]

    # 3. WANT_TO_BUY_DECIDE Patterns (Pricing, evaluation, comparison, trade-offs, disqualifiers, doubt)
    BUY_DECIDE_PATTERNS = [
        re.compile(r'(?i)\b(?:is\s+[\w\s\-]+\s+worth\s+(?:the\s+cost|it|the\s+price)|cost|pricing|price|tier|subscription|license|plan|roi|budget)\b'),
        re.compile(r'(?i)\b(?:compare\s+[\w\s\-]+\s+vs|comparison|versus|which\s+(?:is\s+better|should\s+I\s+buy|should\s+I\s+choose))\b'),
        re.compile(r'(?i)\b(?:why\s+shouldn\'?t\s+I|why\s+should\s+I\s+avoid|disqualifier|anti-persona|not\s+a\s+fit|when\s+to\s+avoid|drawback|downside|disadvantages?)\b'),
        re.compile(r'(?i)\b(?:repair\s+vs\s+replace|upgrade\s+vs|build\s+vs\s+buy)\b')
    ]

    # 4. WANT_TO_KNOW Patterns (Conceptual, definition, high-level architecture, overview)
    KNOW_PATTERNS = [
        re.compile(r'(?i)\b(?:how\s+does\s+[\w\s\-]+\s+(?:actually\s+)?work|what\s+is|what\s+are|explain|overview|architecture|concept|theory|principles?|under\s+the\s+hood|background|definition)\b'),
        re.compile(r'(?i)\b(?:why\s+does|meaning\s+of|difference\s+between|fundamentals?)\b')
    ]

    @classmethod
    def classify(cls, query: str) -> MomentClassificationResult:
        """
        Classifies query into one of the 4 micro-moments with strategy payload.
        """
        if not query or not query.strip():
            return MomentClassificationResult(
                moment=MicroMoment.WANT_TO_KNOW,
                confidence=0.50,
                intent_description="Default informational fallback",
                retrieval_strategy={"mode": "hybrid_broad"}
            )

        q_clean = query.strip()

        # Priority 1: GO/LOCATE (Specific entity or geographical targeting)
        go_matches = [p.pattern for p in cls.GO_LOCATE_PATTERNS if p.search(q_clean)]
        if go_matches:
            return MomentClassificationResult(
                moment=MicroMoment.WANT_TO_GO_LOCATE,
                confidence=0.95 if len(go_matches) > 1 else 0.92,
                intent_description="Entity, location, or specialized provider discovery",
                retrieval_strategy={
                    "mode": "attribute_prefiltered",
                    "filter_location": True,
                    "filter_entity": True,
                    "corroborate_reviews": True
                },
                matched_patterns=go_matches
            )

        # Priority 2: BUY/DECIDE (Commercial evaluation, pricing, disqualifiers)
        buy_matches = [p.pattern for p in cls.BUY_DECIDE_PATTERNS if p.search(q_clean)]
        if buy_matches:
            return MomentClassificationResult(
                moment=MicroMoment.WANT_TO_BUY_DECIDE,
                confidence=0.95 if len(buy_matches) > 1 else 0.92,
                intent_description="Commercial evaluation, trade-off matrix, pricing, or objection analysis",
                retrieval_strategy={
                    "mode": "trust_boosted",
                    "boost_trust_pillars": ["pricing", "not_a_fit", "problems", "repair_vs_replace"],
                    "boost_factor": 1.40
                },
                matched_patterns=buy_matches
            )

        # Priority 3: DO (Procedural execution, step-by-step, troubleshooting)
        do_matches = [p.pattern for p in cls.DO_PATTERNS if p.search(q_clean)]
        if do_matches:
            return MomentClassificationResult(
                moment=MicroMoment.WANT_TO_DO,
                confidence=0.95 if len(do_matches) > 1 else 0.92,
                intent_description="Tactical troubleshooting and step-by-step procedural execution",
                retrieval_strategy={
                    "mode": "procedural_prioritized",
                    "prefer_procedural_chunks": True,
                    "boost_trust_pillars": ["problems", "environment_context"],
                    "boost_factor": 1.25
                },
                matched_patterns=do_matches
            )

        # Priority 4: KNOW (Informational, conceptual, educational)
        know_matches = [p.pattern for p in cls.KNOW_PATTERNS if p.search(q_clean)]
        if know_matches:
            return MomentClassificationResult(
                moment=MicroMoment.WANT_TO_KNOW,
                confidence=0.95 if len(know_matches) > 1 else 0.90,
                intent_description="Foundational understanding and conceptual architecture",
                retrieval_strategy={
                    "mode": "hybrid_broad",
                    "prefer_parent_context": True
                },
                matched_patterns=know_matches
            )

        # Fallback default: WANT_TO_KNOW
        return MomentClassificationResult(
            moment=MicroMoment.WANT_TO_KNOW,
            confidence=0.80,
            intent_description="General technical understanding",
            retrieval_strategy={"mode": "hybrid_broad", "prefer_parent_context": True}
        )


class DynamicPromptRouter:
    """
    Renders moment-tailored system prompt templates.
    """

    PROMPT_TEMPLATES = {
        MicroMoment.WANT_TO_KNOW: (
            "You are an authoritative technical educator. Your goal is to explain concepts clearly, "
            "grounding explanations in the provided knowledge base. Structure your response with an "
            "Answer-First core summary followed by conceptual breakdowns, architectural diagrams (if applicable), "
            "and underlying mechanisms."
        ),
        MicroMoment.WANT_TO_GO_LOCATE: (
            "You are an expert directory and capability matching advisor. Provide precise, location-aware, "
            "and attribute-filtered recommendations. Highlight specialized capabilities, supported regions/environments, "
            "and corroborate primary specifications with third-party verification."
        ),
        MicroMoment.WANT_TO_DO: (
            "You are a tactical operations engineer. Provide direct, step-by-step procedural instructions. "
            "Lead immediately with the actionable resolution, exact CLI commands or code blocks, prerequisites, "
            "and known environmental constraints."
        ),
        MicroMoment.WANT_TO_BUY_DECIDE: (
            "You are an objective technology evaluation analyst. Deliver transparent trade-off analyses, "
            "cost/pricing breakdowns, repair vs. replace thresholds, and explicit disqualifiers ('not-a-fit' criteria). "
            "Do not sell or hype; proactively highlight edge-case problems and failure modes."
        )
    }

    @classmethod
    def get_system_prompt(cls, moment: MicroMoment) -> str:
        return cls.PROMPT_TEMPLATES.get(moment, cls.PROMPT_TEMPLATES[MicroMoment.WANT_TO_KNOW])
