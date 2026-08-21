"""
Dual-LLM Anti-Drift QA Verifier & Fact-Checking Engine:
Phase 1: Drafter LLM generates candidate answer from retrieved XML knowledge.
Phase 2: Verifier LLM / Rule Auditor fact-checks draft against context to eliminate hallucinations,
unsupported numerical claims, and constraint violations.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class VerificationResult:
    status: str  # "PASSED" or "CORRECTED"
    drift_detected: bool
    violations: List[str] = field(default_factory=list)
    hallucinated_claims: List[str] = field(default_factory=list)
    corrected_response: str = ""
    verification_confidence: float = 1.0


class AntiDriftVerifier:
    """
    Two-Phase Anti-Drift Fact-Checking Engine.
    Audits draft responses against retrieved source context for factual fidelity.
    """

    RE_NUMERIC_CLAIM = re.compile(r'\b\d+(?:,\d+)*(?:\.\d+)?\s*(?:writes?/sec|reqs?/sec|tps|rps|ms|seconds|minutes|days|gb|mb|tb|users?|threads?|nodes?|connections?|concurrent)\b', re.IGNORECASE)
    RE_LIMIT_CLAIM = re.compile(r'\b(?:supports?|limits?|maximum|capped at|up to|threshold of)\s+([\d,]+(?:\.\d+)?\s*\w+)', re.IGNORECASE)

    @classmethod
    def verify_response(
        cls,
        retrieved_context: str,
        draft_response: str,
        query: str = ""
    ) -> VerificationResult:
        """
        Audits draft_response against retrieved_context.
        Detects factual drift, unauthorized numerical extrapolations, and corrects discrepancies.
        """
        if not draft_response or not draft_response.strip():
            return VerificationResult(
                status="PASSED",
                drift_detected=False,
                corrected_response=""
            )

        if not retrieved_context or not retrieved_context.strip():
            return VerificationResult(
                status="CORRECTED",
                drift_detected=True,
                violations=["Draft response provided without grounded context"],
                corrected_response="Insufficient verified context: No documents in the knowledge repository support this claim."
            )

        violations = []
        hallucinated_claims = []
        corrected = draft_response

        # 1. Audit Numerical and Capacity Claims
        draft_num_matches = cls.RE_NUMERIC_CLAIM.findall(draft_response)
        
        # Extract all numbers from retrieved context
        context_numbers = set(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', retrieved_context))
        
        for claim in draft_num_matches:
            # Extract the raw number from the claim
            num_part = re.search(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', claim)
            if num_part:
                raw_num = num_part.group(0)
                # Check if this exact number is grounded in context
                if raw_num not in context_numbers:
                    # Find if context has a corresponding metric with a different limit
                    # (e.g. context has "5,000" and draft says "100,000")
                    drift_msg = f"Ungrounded numerical claim: '{claim}' (number '{raw_num}' not found in retrieved source context)"
                    violations.append(drift_msg)
                    hallucinated_claims.append(claim)

                    # Look for actual context limit for this unit
                    unit_match = re.search(r'(?:writes?/sec|reqs?/sec|tps|rps|ms|seconds|minutes|days|gb|mb|tb|users?|threads?|nodes?|connections?|concurrent)', claim, re.IGNORECASE)
                    if unit_match:
                        unit_str = unit_match.group(0)
                        # Find context sentence with this unit
                        context_pattern = re.compile(rf'(\b\d+(?:,\d+)*(?:\.\d+)?\s*{re.escape(unit_str)})', re.IGNORECASE)
                        ctx_match = context_pattern.search(retrieved_context)
                        if ctx_match:
                            actual_limit = ctx_match.group(1)
                            # Replace hallucinated number with actual limit
                            corrected = corrected.replace(claim, actual_limit)
                        else:
                            # If no replacement found, qualify the claim
                            corrected = corrected.replace(claim, f"{claim} (Note: Unverified in source context)")

        # 2. Check Negative Constraints and "Not-a-Fit" Boundaries
        # If context explicitly mentions "avoid" or "not recommended for X", ensure draft does not say "recommended for X"
        if "not recommended" in retrieved_context.lower() or "avoid" in retrieved_context.lower():
            if "fully recommended" in draft_response.lower() or "ideal for" in draft_response.lower():
                violations.append("Constraint violation: Draft recommends configuration that context explicitly flags to avoid.")
                corrected = corrected.replace("fully recommended", "not recommended based on documented constraints")

        drift_detected = len(violations) > 0

        return VerificationResult(
            status="PASSED" if not drift_detected else "CORRECTED",
            drift_detected=drift_detected,
            violations=violations,
            hallucinated_claims=hallucinated_claims,
            corrected_response=corrected if drift_detected else draft_response,
            verification_confidence=0.98 if not drift_detected else 0.85
        )
