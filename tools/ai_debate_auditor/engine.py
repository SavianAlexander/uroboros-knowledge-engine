"""
Master DebateAuditorEngine Orchestrator for Adversarial AI Debate Auditor.
Zero-dependency, stdlib-first high-assurance epistemic analysis engine.
"""

import os
import datetime
import unicodedata
from typing import Optional, Dict, Any, List

from .models import (
    AuditReport,
    Claim,
    PatternMatch,
    BoundaryViolation,
    CitationCheck,
    ScoringMetrics,
    EpistemicVerdict,
    CounterArgumentSynthesis
)
from .deconstructor import deconstruct_argument, normalize_text
from .verifier import extract_citations, cross_examine_vault, verify_boundaries
from .patterns import run_full_pattern_scan
from .synthesizer import synthesize_counter_arguments
from .reporter import compute_scoring_metrics, generate_remediation_steps, render_markdown_report


class DebateAuditorEngine:
    """
    Main orchestration engine for Adversarial AI Debate Auditing & Counter-Proof Generation.
    """

    def __init__(self, default_db_path: Optional[str] = None):
        self.default_db_path = default_db_path

    def audit_text(
        self,
        text: str,
        prompt_context: Optional[str] = None,
        subject: Optional[str] = None,
        strict: bool = False,
        db_path: Optional[str] = None
    ) -> AuditReport:
        """
        Audit a raw text string or debate transcript.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Edge Case 1: Empty or whitespace-only input
        if not text or not text.strip():
            empty_metrics = ScoringMetrics(
                hallucination_risk_score=0.0,
                fallacy_severity_index=0.0,
                sycophancy_propensity_score=0.0,
                grounding_confidence_score=0.0,
                phantom_citation_index=0.0,
                overall_integrity_score=100.0
            )
            empty_report = AuditReport(
                target_subject=subject or "Empty Input",
                timestamp=timestamp,
                verdict=EpistemicVerdict.SOUND,
                metrics=empty_metrics,
                claims=[],
                detected_fallacies=[],
                boundary_violations=[],
                citations=[],
                counter_argument=CounterArgumentSynthesis(),
                remediation_steps=["Input text was empty or whitespace only."],
                markdown_report="# Adversarial AI Debate Audit Report\n\n**Status**: Empty input provided.",
                raw_input_length=0,
                prompt_context=prompt_context
            )
            return empty_report

        # Normalize text
        norm_text = normalize_text(text)
        
        # Determine subject if not explicitly given
        target_subject = subject
        if not target_subject:
            first_line = norm_text.split("\n")[0].strip()
            if len(first_line) > 60:
                target_subject = first_line[:57] + "..."
            else:
                target_subject = first_line or "AI Debate Claim"

        # 1. R1: Deconstruct argument into atomic claims
        claims = deconstruct_argument(norm_text, prompt_context=prompt_context)
        
        # 2. R2: Extract and verify citations
        citations = extract_citations(norm_text)
        active_db = db_path or self.default_db_path
        citations = cross_examine_vault(citations, db_path=active_db)
        
        # 3. R2: Verify first-principles physical & mathematical boundaries
        boundary_violations = verify_boundaries(norm_text)
        
        # 4. Pattern Detection (10 standard hallucination/sycophancy patterns)
        detected_fallacies = run_full_pattern_scan(
            text=norm_text,
            claims=claims,
            citations=citations,
            boundary_violations=boundary_violations,
            prompt_context=prompt_context
        )
        
        # 5. R3: Synthesize adversarial counter-arguments, mechanism failures, and counter-proofs
        counter_argument = synthesize_counter_arguments(
            claims=claims,
            fallacies=detected_fallacies,
            boundary_violations=boundary_violations,
            citations=citations
        )
        
        # 6. Scoring & Metrics
        metrics, verdict = compute_scoring_metrics(
            claims=claims,
            fallacies=detected_fallacies,
            boundary_violations=boundary_violations,
            citations=citations,
            prompt_context=prompt_context
        )
        
        # 7. Remediation recommendations
        remediation_steps = generate_remediation_steps(
            fallacies=detected_fallacies,
            boundary_violations=boundary_violations,
            citations=citations
        )
        
        # Construct AuditReport object
        report = AuditReport(
            target_subject=target_subject,
            timestamp=timestamp,
            verdict=verdict,
            metrics=metrics,
            claims=claims,
            detected_fallacies=detected_fallacies,
            boundary_violations=boundary_violations,
            citations=citations,
            counter_argument=counter_argument,
            remediation_steps=remediation_steps,
            raw_input_length=len(norm_text),
            prompt_context=prompt_context
        )
        
        # Render Markdown report
        report.markdown_report = render_markdown_report(report)
        
        # Strict mode check
        if strict and verdict == EpistemicVerdict.DEBUNKED:
            # Report is generated, caller can inspect verdict
            pass

        return report

    def audit_file(
        self,
        file_path: str,
        prompt_context: Optional[str] = None,
        subject: Optional[str] = None,
        strict: bool = False,
        db_path: Optional[str] = None
    ) -> AuditReport:
        """
        Audit content from a file path.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target audit file not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            
        file_subject = subject or os.path.basename(file_path)
        return self.audit_text(
            text=content,
            prompt_context=prompt_context,
            subject=file_subject,
            strict=strict,
            db_path=db_path
        )


# Global convenience functions
_default_engine = DebateAuditorEngine()

def audit_text(
    text: str,
    prompt_context: Optional[str] = None,
    subject: Optional[str] = None,
    strict: bool = False
) -> AuditReport:
    """Convenience functional API for auditing text."""
    return _default_engine.audit_text(text, prompt_context=prompt_context, subject=subject, strict=strict)

def audit_file(
    file_path: str,
    prompt_context: Optional[str] = None,
    subject: Optional[str] = None,
    strict: bool = False
) -> AuditReport:
    """Convenience functional API for auditing a file."""
    return _default_engine.audit_file(file_path, prompt_context=prompt_context, subject=subject, strict=strict)
