"""
Adversarial AI Debate Auditor & Counter-Argument Engine.
A high-assurance, zero-dependency epistemic analysis system.
"""

from .models import (
    AuditReport,
    Claim,
    PatternMatch,
    Finding,
    CitationCheck,
    BoundaryViolation,
    MechanismFailure,
    CounterProof,
    CounterArgumentSynthesis,
    ScoringMetrics,
    ClaimCategory,
    PatternSeverity,
    PatternType,
    CitationStatus,
    EpistemicVerdict
)
from .engine import DebateAuditorEngine, audit_text, audit_file
from .deconstructor import deconstruct_argument
from .verifier import extract_citations, cross_examine_vault, verify_boundaries
from .patterns import run_full_pattern_scan
from .synthesizer import synthesize_counter_arguments
from .reporter import compute_scoring_metrics, render_markdown_report

__version__ = "1.0.0"
__all__ = [
    "DebateAuditorEngine",
    "audit_text",
    "audit_file",
    "AuditReport",
    "Claim",
    "PatternMatch",
    "Finding",
    "CitationCheck",
    "BoundaryViolation",
    "MechanismFailure",
    "CounterProof",
    "CounterArgumentSynthesis",
    "ScoringMetrics",
    "ClaimCategory",
    "PatternSeverity",
    "PatternType",
    "CitationStatus",
    "EpistemicVerdict",
    "deconstruct_argument",
    "extract_citations",
    "cross_examine_vault",
    "verify_boundaries",
    "run_full_pattern_scan",
    "synthesize_counter_arguments",
    "compute_scoring_metrics",
    "render_markdown_report",
]
