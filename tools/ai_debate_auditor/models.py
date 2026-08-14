"""
Data models and contracts for the Adversarial AI Debate Auditor & Counter-Argument Engine.
Zero external dependencies - 100% Python Standard Library.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
import json


class PatternSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PatternType(str, Enum):
    P01_SYCOPHANCY = "P01"
    P02_CONFIRMATION_BIAS = "P02"
    P03_PHANTOM_CITATION = "P03"
    P04_BOUNDARY_VIOLATION = "P04"
    P05_FALSE_DILEMMA = "P05"
    P06_CIRCULAR_LOGIC = "P06"
    P07_QUANTIFIER_INFLATION = "P07"
    P08_PREMISE_CONTRADICTION = "P08"
    P09_SPURIOUS_CAUSATION = "P09"
    P10_REIFICATION = "P10"


class ClaimCategory(str, Enum):
    EMPIRICAL_FACT = "EMPIRICAL_FACT"
    PHYSICAL_SCIENTIFIC = "PHYSICAL_SCIENTIFIC"
    CAUSAL_MECHANISM = "CAUSAL_MECHANISM"
    DEDUCTIVE_LOGICAL = "DEDUCTIVE_LOGICAL"
    NORMATIVE_POLICY = "NORMATIVE_POLICY"
    METAPHORIC_ABSTRACT = "METAPHORIC_ABSTRACT"
    UNCLASSIFIED = "UNCLASSIFIED"


class CitationStatus(str, Enum):
    VERIFIED_LOCAL = "VERIFIED_LOCAL"
    VERIFIED_REMOTE = "VERIFIED_REMOTE"
    PHANTOM_FABRICATED = "PHANTOM_FABRICATED"
    INVALID_IDENTIFIER = "INVALID_IDENTIFIER"
    UNINDEXED_PLAUSIBLE = "UNINDEXED_PLAUSIBLE"


class EpistemicVerdict(str, Enum):
    SOUND = "SOUND"
    QUESTIONABLE = "QUESTIONABLE"
    DEBUNKED = "DEBUNKED"


@dataclass
class Claim:
    """Atomic claim or proposition extracted from input argument."""
    id: str
    text: str
    category: ClaimCategory = ClaimCategory.UNCLASSIFIED
    confidence: float = 1.0
    unsubstantiated: bool = False
    source_sentence: str = ""
    presupposition_echo: bool = False
    line_number: int = 1
    quantifiers: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)


@dataclass
class PatternMatch:
    """Detection finding for one of the 10 hallucination/sycophancy patterns."""
    pattern_id: PatternType
    pattern_name: str
    severity: PatternSeverity
    snippet: str
    explanation: str
    suggested_correction: str
    confidence: float = 1.0
    affected_claim_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# Finding alias for backward compatibility with analysis.md
Finding = PatternMatch


@dataclass
class CitationCheck:
    """Forensic verification result for a scholarly or literature reference."""
    raw_citation: str
    citation_type: str  # 'doi', 'arxiv', 'pmid', 'author_year', 'unstructured'
    identifier: Optional[str] = None
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    status: CitationStatus = CitationStatus.UNINDEXED_PLAUSIBLE
    phantom_score: float = 0.0
    is_valid: bool = True
    is_phantom: bool = False
    vault_grounded: bool = False
    matched_doc: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class BoundaryViolation:
    """Violation of first-principles physics, thermodynamics, or mathematical axioms."""
    domain: str  # 'Thermodynamics', 'Special Relativity', 'Probability', etc.
    law_name: str
    claimed_value: str
    theoretical_limit: str
    delta_violation: str
    explanation: str
    first_principle_law: str
    severity: PatternSeverity = PatternSeverity.CRITICAL
    claim_snippet: str = ""


@dataclass
class MechanismFailure:
    """Structural breakdown of causal chain and failure modes."""
    target_claim: str
    premises: List[str] = field(default_factory=list)
    causal_steps: List[str] = field(default_factory=list)
    fatal_leap: str = ""
    omitted_friction: List[str] = field(default_factory=list)
    scaling_bottlenecks: List[str] = field(default_factory=list)


@dataclass
class CounterProof:
    """Formal deductive refutation derived from first principles."""
    target_claim: str
    implicit_assumption: str
    empirical_axiom: str
    mathematical_derivation: str
    refutation_conclusion: str
    primary_citations: List[str] = field(default_factory=list)


@dataclass
class CounterArgumentSynthesis:
    """Synthesized adversarial counter-arguments and stress tests."""
    mechanism_breakdowns: List[MechanismFailure] = field(default_factory=list)
    friction_points: List[str] = field(default_factory=list)
    socratic_questions: List[str] = field(default_factory=list)
    deductive_counter_proofs: List[CounterProof] = field(default_factory=list)


@dataclass
class ScoringMetrics:
    """Deterministic mathematical epistemic scorecard."""
    hallucination_risk_score: float = 0.0  # HRS in [0.0, 1.0]
    fallacy_severity_index: float = 0.0    # FSI in [0.0, 1.0]
    sycophancy_propensity_score: float = 0.0  # SPS in [0.0, 1.0]
    grounding_confidence_score: float = 0.0   # GCS in [0.0, 1.0]
    phantom_citation_index: float = 0.0       # S_phantom in [0.0, 1.0]
    overall_integrity_score: float = 100.0    # 0.0 - 100.0 scale


@dataclass
class AuditReport:
    """Complete executive audit report ledger."""
    target_subject: str
    timestamp: str
    verdict: EpistemicVerdict
    metrics: ScoringMetrics
    claims: List[Claim] = field(default_factory=list)
    detected_fallacies: List[PatternMatch] = field(default_factory=list)
    boundary_violations: List[BoundaryViolation] = field(default_factory=list)
    citations: List[CitationCheck] = field(default_factory=list)
    counter_argument: CounterArgumentSynthesis = field(default_factory=CounterArgumentSynthesis)
    remediation_steps: List[str] = field(default_factory=list)
    markdown_report: str = ""
    raw_input_length: int = 0
    prompt_context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit report to structured JSON-serializable dictionary."""
        return {
            "target_subject": self.target_subject,
            "timestamp": self.timestamp,
            "verdict": self.verdict.value,
            "metrics": {
                "hallucination_risk_score": round(self.metrics.hallucination_risk_score, 4),
                "fallacy_severity_index": round(self.metrics.fallacy_severity_index, 4),
                "sycophancy_propensity_score": round(self.metrics.sycophancy_propensity_score, 4),
                "grounding_confidence_score": round(self.metrics.grounding_confidence_score, 4),
                "phantom_citation_index": round(self.metrics.phantom_citation_index, 4),
                "overall_integrity_score": round(self.metrics.overall_integrity_score, 2),
            },
            "claims_count": len(self.claims),
            "claims": [
                {
                    "id": c.id,
                    "text": c.text,
                    "category": c.category.value,
                    "unsubstantiated": c.unsubstantiated,
                    "presupposition_echo": c.presupposition_echo,
                }
                for c in self.claims
            ],
            "detected_fallacies": [
                {
                    "pattern_id": f.pattern_id.value,
                    "pattern_name": f.pattern_name,
                    "severity": f.severity.value,
                    "snippet": f.snippet,
                    "explanation": f.explanation,
                    "suggested_correction": f.suggested_correction,
                    "confidence": round(f.confidence, 3),
                }
                for f in self.detected_fallacies
            ],
            "boundary_violations": [
                {
                    "domain": b.domain,
                    "law_name": b.law_name,
                    "claimed_value": b.claimed_value,
                    "theoretical_limit": b.theoretical_limit,
                    "delta_violation": b.delta_violation,
                    "explanation": b.explanation,
                    "first_principle_law": b.first_principle_law,
                    "severity": b.severity.value,
                }
                for b in self.boundary_violations
            ],
            "citations": [
                {
                    "raw_text": c.raw_citation,
                    "citation_type": c.citation_type,
                    "identifier": c.identifier,
                    "title": c.title,
                    "authors": c.authors,
                    "year": c.year,
                    "status": c.status.value,
                    "phantom_score": round(c.phantom_score, 3),
                    "vault_grounded": c.vault_grounded,
                    "matched_doc": c.matched_doc,
                    "notes": c.notes,
                }
                for c in self.citations
            ],
            "counter_argument": {
                "mechanism_breakdowns": [
                    {
                        "target_claim": m.target_claim,
                        "premises": m.premises,
                        "causal_steps": m.causal_steps,
                        "fatal_leap": m.fatal_leap,
                        "omitted_friction": m.omitted_friction,
                        "scaling_bottlenecks": m.scaling_bottlenecks,
                    }
                    for m in self.counter_argument.mechanism_breakdowns
                ],
                "friction_points": self.counter_argument.friction_points,
                "socratic_questions": self.counter_argument.socratic_questions,
                "deductive_counter_proofs": [
                    {
                        "target_claim": cp.target_claim,
                        "implicit_assumption": cp.implicit_assumption,
                        "empirical_axiom": cp.empirical_axiom,
                        "mathematical_derivation": cp.mathematical_derivation,
                        "refutation_conclusion": cp.refutation_conclusion,
                        "primary_citations": cp.primary_citations,
                    }
                    for cp in self.counter_argument.deductive_counter_proofs
                ],
            },
            "remediation_steps": self.remediation_steps,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
