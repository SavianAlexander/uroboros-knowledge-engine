"""
Multi-Source Consensus & Review Corroborator:
Corroborates technical claims, operational limits, and failure rates across
primary documentation and third-party reviews / post-mortems.
"""

import re
from typing import Dict, List, Any, Tuple, Optional


class MultiSourceCorroborator:
    """
    Synthesizes and correlates primary technical specifications with third-party corroborations.
    """

    @classmethod
    def corroborate(
        cls,
        candidates: List[Dict[str, Any]],
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Categorizes chunks into primary and third-party sources, calculates consensus score,
        and generates structured multi-tier context with citations.
        """
        primary_docs = []
        corroborations = []

        for c in candidates:
            s_type = (c.get("source_type") or "primary_doc").lower()
            if s_type == "third_party_corroboration":
                corroborations.append(c)
            else:
                primary_docs.append(c)

        has_primary = len(primary_docs) > 0
        has_corroboration = len(corroborations) > 0
        
        # Consensus multiplier
        if has_primary and has_corroboration:
            consensus_level = "HIGH_CONSENSUS"
            consensus_multiplier = 1.35
        elif has_primary:
            consensus_level = "PRIMARY_ONLY"
            consensus_multiplier = 1.0
        elif has_corroboration:
            consensus_level = "CORROBORATION_ONLY"
            consensus_multiplier = 1.15
        else:
            consensus_level = "NO_SOURCES"
            consensus_multiplier = 0.0

        # Assembled structured multi-source text
        context_blocks = []
        
        if primary_docs:
            context_blocks.append("## Primary Technical Specifications")
            for doc in primary_docs:
                title = doc.get("doc_title") or doc.get("filename") or "Primary Doc"
                header = doc.get("parent_header") or doc.get("section_header") or "General"
                content = (doc.get("content") or doc.get("snippet") or "").strip()
                context_blocks.append(f"### [Tier 1: Primary Spec | {title} > {header}]\n{content}\n")

        if corroborations:
            context_blocks.append("## Third-Party Field Corroboration & Community Reviews")
            for rev in corroborations:
                title = rev.get("doc_title") or rev.get("filename") or "Field Review"
                header = rev.get("parent_header") or rev.get("section_header") or "Field Observation"
                content = (rev.get("content") or rev.get("snippet") or "").strip()
                context_blocks.append(f"### [Tier 2: Third-Party Review | {title} > {header}]\n{content}\n")

        full_context = "\n\n".join(context_blocks)

        citations = []
        for p in primary_docs:
            citations.append({
                "tier": "primary_doc",
                "filename": p.get("filename", ""),
                "title": p.get("doc_title", ""),
                "score": p.get("cross_score", p.get("score", 0.0))
            })
        for c in corroborations:
            citations.append({
                "tier": "third_party_corroboration",
                "filename": c.get("filename", ""),
                "title": c.get("doc_title", ""),
                "score": c.get("cross_score", c.get("score", 0.0))
            })

        return {
            "status": "CORROBORATED" if (has_primary and has_corroboration) else "UNILATERAL",
            "consensus_level": consensus_level,
            "consensus_multiplier": consensus_multiplier,
            "primary_count": len(primary_docs),
            "corroboration_count": len(corroborations),
            "assembled_context": full_context,
            "citations": citations
        }
