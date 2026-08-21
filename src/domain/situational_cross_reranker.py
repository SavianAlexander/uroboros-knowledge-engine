"""
Situational Cross-Encoder Reranker & Relevance Gate (Post-Retrieval Layer)
Evaluates retrieved candidate chunks against the entire multi-variable user situation:
1. Deep Term Coverage & N-Gram Proximity
2. Attribute Congruency (Intent, Environment, Technology alignment)
3. "Answer-First" Leading Factual Alignment
4. Relevance Gating (Discards Low-Confidence Distractors)
"""

import re
import math
import unicodedata
from typing import Dict, List, Any, Optional, Set, Tuple

RE_TOKEN = re.compile(r'\b[a-zA-Z0-9_\-]{2,}\b')


class SituationalCrossReranker:
    """
    Zero-Dependency High-Performance Situational Cross-Encoder Reranking & Relevance Gate.
    """

    @classmethod
    def rerank(
        cls,
        query: str,
        candidates: List[Dict[str, Any]],
        query_plan: Optional[Any] = None,
        min_relevance_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Reranks retrieved candidate chunks against the complete situational prompt,
        scoring deep semantic coverage and attribute congruency, and filtering below threshold.
        """
        if not query or not candidates:
            return candidates or []

        from src.domain.situational_query_analyzer import SituationalQueryAnalyzer, SituationalQueryPlan

        plan: SituationalQueryPlan
        if query_plan is not None and isinstance(query_plan, SituationalQueryPlan):
            plan = query_plan
        else:
            plan = SituationalQueryAnalyzer.analyze_situational_query(query)

        q_terms = [t.lower() for t in RE_TOKEN.findall(plan.core_semantic_query or query)]
        # Filter common stopwords to focus on content-bearing tokens
        stopwords = {"the", "and", "for", "with", "that", "this", "from", "are", "can", "you", "how", "what", "why", "when", "where", "have", "our"}
        content_q_terms = [t for t in q_terms if t not in stopwords and len(t) > 2]
        if not content_q_terms:
            content_q_terms = q_terms or ["query"]

        q_term_set = set(content_q_terms)
        q_bigrams = [" ".join(content_q_terms[i:i+2]) for i in range(len(content_q_terms)-1)] if len(content_q_terms) >= 2 else []

        reranked = []
        for cand in candidates:
            item = dict(cand)
            content = (item.get("content") or item.get("snippet") or "").lower()
            parent_hdr = (item.get("parent_header") or "").lower()
            doc_title = (item.get("doc_title") or item.get("filename") or "").lower()
            intent_type = (item.get("intent_type") or "general").lower()
            domain_scope = (item.get("domain_scope") or "general").lower()

            combined_search_text = f"{doc_title} {parent_hdr} {content}"

            # 1. Term Coverage Density [0.0, 1.0]
            matched_terms = [t for t in q_term_set if t in combined_search_text]
            term_coverage = len(matched_terms) / float(max(1, len(q_term_set)))

            # 2. Exact Bigram / Phrase Proximity Boost [0.0, 0.5]
            matched_bigrams = [b for b in q_bigrams if b in combined_search_text] if q_bigrams else []
            phrase_proximity = (len(matched_bigrams) / float(len(q_bigrams))) * 0.5 if q_bigrams else 0.0

            # 3. Attribute & Situational Congruency [0.0, 1.0]
            attr_score = 0.0

            # 3a. Intent Match
            if plan.intent_type != "general":
                if plan.intent_type == intent_type or plan.intent_type in combined_search_text:
                    attr_score += 0.30
                elif intent_type != "general" and intent_type != plan.intent_type:
                    attr_score -= 0.10  # Slight penalty for conflicting intent

            # 3b. Environment Match
            for env in plan.environments:
                if env in combined_search_text:
                    attr_score += 0.35

            # 3c. Technology Match
            for tech in plan.technologies:
                if tech in combined_search_text:
                    attr_score += 0.35

            # 3d. 5-Pillar Trust Taxonomy & Micro-Moment Boosting
            trust_type = (item.get("trust_type") or "").lower()
            source_type = (item.get("source_type") or "primary_doc").lower()
            
            # Check for doubt/evaluation in query (e.g. "avoid", "not a fit", "downside", "freezing climate", "worth it")
            q_lower = query.lower()
            is_doubt_eval = any(w in q_lower for w in ["avoid", "why shouldn't", "not a fit", "drawback", "limitation", "freezing climate", "climate", "worth", "cost", "problem"])
            
            if is_doubt_eval:
                if trust_type in ["not_a_fit", "environment_context", "problems"]:
                    attr_score += 0.50  # Strong boost for disqualifier and environmental constraints
                elif trust_type in ["pricing", "repair_vs_replace"]:
                    attr_score += 0.35
            elif trust_type != "general":
                attr_score += 0.20

            # 3e. Multi-Source Corroboration Boost
            if source_type == "third_party_corroboration":
                attr_score += 0.25

            # 4. Header & Breadcrumb Context Alignment
            header_alignment = 0.0
            if any(t in doc_title or t in parent_hdr for t in content_q_terms):
                header_alignment = 0.25

            # 5. Answer-First / Actionable Code Presence
            answer_lead_bonus = 0.15 if ("```" in content or "|" in content or "def " in content or "class " in content) else 0.0

            # 6. Composite Situational Score Computation
            base_score = float(item.get("rrf_score") or item.get("score") or 0.1)
            raw_multiplier = 1.0 + (term_coverage * 1.5) + phrase_proximity + attr_score + header_alignment + answer_lead_bonus
            raw_cross_score = max(0.01, base_score * max(0.2, raw_multiplier))

            # Calibrate normalized relevance confidence in [0.0, 1.0]
            relevance_confidence = min(1.0, round((term_coverage * 0.40) + (phrase_proximity * 0.20) + (min(1.0, max(0.0, attr_score)) * 0.30) + (header_alignment * 0.10), 4))

            item["cross_score"] = round(raw_cross_score, 6)
            item["relevance_confidence"] = relevance_confidence
            item["term_coverage"] = round(term_coverage, 4)
            item["attribute_congruency"] = round(attr_score, 4)
            item["rrf_score"] = round(raw_cross_score, 6)
            item["final_score"] = round(raw_cross_score, 6)

            reranked.append(item)

        # Sort descending by cross_score
        reranked.sort(key=lambda x: x["cross_score"], reverse=True)

        # 7. Relevance Gate Threshold Filtering
        gated_results = [r for r in reranked if r["relevance_confidence"] >= min_relevance_threshold]
        
        # Ensure at least the top candidate is preserved if any were provided
        if not gated_results and reranked:
            gated_results = [reranked[0]]

        return gated_results
