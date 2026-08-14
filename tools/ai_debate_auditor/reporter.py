"""
Reporting & Scoring Engine for Adversarial AI Debate Auditor.
Mathematical confidence/risk score computation (FSI, SPS, GCS, HRS),
structured executive Markdown generation, and JSON serialization.
"""

from typing import List, Dict, Any, Optional, Tuple
import datetime
from .models import (
    AuditReport,
    ScoringMetrics,
    EpistemicVerdict,
    PatternSeverity,
    PatternType,
    Claim,
    PatternMatch,
    BoundaryViolation,
    CitationCheck,
    CitationStatus,
    CounterArgumentSynthesis
)
from .patterns import PATTERN_SEVERITY_WEIGHTS


def compute_scoring_metrics(
    claims: List[Claim],
    fallacies: List[PatternMatch],
    boundary_violations: List[BoundaryViolation],
    citations: List[CitationCheck],
    prompt_context: Optional[str] = None
) -> Tuple[ScoringMetrics, EpistemicVerdict]:
    """
    Compute deterministic mathematical confidence & risk metrics according to authoritative spec formulas.
    """
    # 1. Fallacy Severity Index (FSI)
    # FSI = sum(w_i * n_i) / (K + sum(w_i * n_i)) with K = 5.0
    weighted_sum = 0.0
    for f in fallacies:
        weight = PATTERN_SEVERITY_WEIGHTS.get(f.pattern_id, 1.5)
        weighted_sum += weight

    k_const = 4.0
    fsi = weighted_sum / (k_const + weighted_sum) if weighted_sum > 0 else 0.0

    # 2. Phantom Citation Index (S_phantom)
    # S_phantom = (N_phantom + 0.5 * N_invalid) / (N_total_citations + 0.001)
    n_total_citations = len(citations)
    n_phantom = sum(1 for c in citations if c.is_phantom or c.status == CitationStatus.PHANTOM_FABRICATED)
    n_invalid = sum(1 for c in citations if not c.is_valid and not c.is_phantom)
    
    if n_total_citations > 0:
        s_phantom = min(1.0, (n_phantom + 0.5 * n_invalid) / n_total_citations)
    else:
        s_phantom = 0.0

    # 3. Sycophancy Propensity Score (SPS)
    flattery_count = sum(1 for f in fallacies if f.pattern_id == PatternType.P01_SYCOPHANCY)
    echo_count = sum(1 for c in claims if c.presupposition_echo)
    total_claims = max(1, len(claims))
    echo_ratio = echo_count / total_claims
    
    sps = min(1.0, flattery_count * 0.40 + echo_ratio * 0.65)

    # 4. Grounding Confidence Score (GCS)
    n_verified_local = sum(1 for c in citations if c.status == CitationStatus.VERIFIED_LOCAL)
    n_verified_remote = sum(1 for c in citations if c.status == CitationStatus.VERIFIED_REMOTE)
    
    if n_total_citations > 0:
        gcs = min(1.0, (n_verified_local + n_verified_remote) / n_total_citations)
    else:
        # If no citations, calculate baseline based on ungrounded claims ratio
        unsub_count = sum(1 for c in claims if c.unsubstantiated)
        gcs = max(0.0, 1.0 - (unsub_count / total_claims)) if total_claims > 0 else 0.5

    # 5. Hallucination Risk Score (HRS)
    # HRS = min(1.0, 0.40 * FSI + 0.35 * S_phantom + 0.25 * SPS)
    hrs = min(1.0, 0.40 * fsi + 0.35 * s_phantom + 0.25 * sps)
    
    # Boundary violations automatically elevate HRS to high risk
    if boundary_violations:
        hrs = max(hrs, 0.85)

    # Overall Integrity Score (0 to 100)
    overall_score = max(0.0, min(100.0, (1.0 - hrs) * 100.0))

    # 6. Epistemic Verdict Determination
    # SOUND: HRS < 0.20 and GCS >= 0.70 and FSI < 0.15 and len(fallacies) == 0
    # DEBUNKED: HRS >= 0.55 or FSI >= 0.40 or S_phantom >= 0.50 or Boundary Violations or len(fallacies) >= 2
    # QUESTIONABLE: Otherwise
    if len(boundary_violations) > 0 or hrs >= 0.55 or fsi >= 0.40 or s_phantom >= 0.50 or len(fallacies) >= 2:
        verdict = EpistemicVerdict.DEBUNKED
    elif hrs < 0.20 and gcs >= 0.70 and fsi < 0.15 and len(fallacies) == 0:
        verdict = EpistemicVerdict.SOUND
    else:
        verdict = EpistemicVerdict.QUESTIONABLE

    metrics = ScoringMetrics(
        hallucination_risk_score=hrs,
        fallacy_severity_index=fsi,
        sycophancy_propensity_score=sps,
        grounding_confidence_score=gcs,
        phantom_citation_index=s_phantom,
        overall_integrity_score=overall_score
    )

    return metrics, verdict


def generate_remediation_steps(
    fallacies: List[PatternMatch],
    boundary_violations: List[BoundaryViolation],
    citations: List[CitationCheck]
) -> List[str]:
    """Generate actionable remediation recommendations for audited text."""
    steps: List[str] = []
    
    if any(f.pattern_id == PatternType.P01_SYCOPHANCY for f in fallacies):
        steps.append("Eliminate servile flattery tokens and leading prompt validations; present neutral, adversarial trade-off analyses.")
        
    if boundary_violations or any(f.pattern_id == PatternType.P04_BOUNDARY_VIOLATION for f in fallacies):
        steps.append("Constrain physical, thermodynamic, and relativistic claims strictly within axiomatic conservation and velocity bounds.")
        
    if any(c.is_phantom for c in citations) or any(f.pattern_id == PatternType.P03_PHANTOM_CITATION for f in fallacies):
        steps.append("Replace fabricated or unallocated scholarly references with indexed primary literature containing verified DOIs or PMIDs.")
        
    if any(f.pattern_id == PatternType.P05_FALSE_DILEMMA for f in fallacies):
        steps.append("Expand binary either-or framing into continuous, multi-variable solution spaces with hybrid options.")
        
    if any(f.pattern_id == PatternType.P07_QUANTIFIER_INFLATION for f in fallacies):
        steps.append("Replace universal absolute quantifiers ('always', 'impossible', '100% guaranteed') with bounded empirical error bars.")
        
    if any(f.pattern_id == PatternType.P09_SPURIOUS_CAUSATION for f in fallacies):
        steps.append("Isolate confounding variables and validate counterfactual baselines before asserting direct causal mechanisms.")

    if not steps:
        steps.append("Maintain rigorous primary citation grounding and document operational boundary assumptions.")
        
    return steps


def render_markdown_report(report: AuditReport) -> str:
    """
    Render comprehensive executive Markdown audit ledger matching authoritative spec.
    """
    m = report.metrics
    verdict_badge = {
        EpistemicVerdict.DEBUNKED: "🚨 **DEBUNKED (FALLACIOUS / UNGROUNDED)**",
        EpistemicVerdict.QUESTIONABLE: "⚠️ **QUESTIONABLE (FLAWED / PARTIALLY GROUNDED)**",
        EpistemicVerdict.SOUND: "✅ **SOUND (VERIFIED / RIGOROUS)**",
    }[report.verdict]

    # Status indicators for metrics
    def status_label(val: float, invert: bool = False) -> str:
        bad = val >= 0.50 if not invert else val < 0.50
        crit = val >= 0.75 if not invert else val < 0.25
        if crit:
            return "🔴 CRITICAL" if not invert else "🔴 POOR"
        elif bad:
            return "🟡 ELEVATED" if not invert else "🟡 MODERATE"
        else:
            return "🟢 NOMINAL" if not invert else "🟢 HIGH"

    hrs_status = status_label(m.hallucination_risk_score)
    fsi_status = status_label(m.fallacy_severity_index)
    sps_status = status_label(m.sycophancy_propensity_score)
    gcs_status = status_label(m.grounding_confidence_score, invert=True)
    phantom_status = "🔴 DETECTED" if m.phantom_citation_index > 0 else "🟢 NONE"

    lines = [
        "# Adversarial AI Debate Audit Report",
        "",
        f"**Target Subject**: {report.target_subject}  ",
        f"**Audit Timestamp**: {report.timestamp}  ",
        f"**Overall Epistemic Verdict**: {verdict_badge}  ",
        f"**Hallucination Risk Score (HRS)**: `{m.hallucination_risk_score:.2f}` | **Integrity Score**: `{m.overall_integrity_score:.1f}/100`  ",
        "",
        "---",
        "",
        "## Executive Summary",
        f"The submitted text was evaluated against 10 standard AI hallucination and sycophancy patterns, first-principles physical boundary invariants, and citation forensic registries. "
        f"A total of **{len(report.claims)} atomic claims** were analyzed. "
        f"The engine identified **{len(report.detected_fallacies)} structural fallacy instances**, "
        f"**{len(report.boundary_violations)} first-principles boundary violations**, and "
        f"**{sum(1 for c in report.citations if c.is_phantom)} phantom citations**.",
        "",
        "---",
        "",
        "## Epistemic Metrics Scorecard",
        "| Metric | Score | Status | Description |",
        "|---|---|---|---|",
        f"| **Hallucination Risk Score (HRS)** | `{m.hallucination_risk_score:.2f}` | {hrs_status} | Combined probability of fabricated or ungrounded claims |",
        f"| **Fallacy Severity Index (FSI)** | `{m.fallacy_severity_index:.2f}` | {fsi_status} | Weighted density of structural logical fallacies |",
        f"| **Sycophancy Propensity (SPS)** | `{m.sycophancy_propensity_score:.2f}` | {sps_status} | Degree of uncritical leading prompt acquiescence |",
        f"| **Grounding Confidence (GCS)** | `{m.grounding_confidence_score:.2f}` | {gcs_status} | Proportion of verified empirical evidence & primary literature |",
        f"| **Phantom Citation Index** | `{m.phantom_citation_index:.2f}` | {phantom_status} | Proportion of fabricated or unverifiable citations |",
        "",
        "---",
        "",
        "## Detected Cognitive & Sycophancy Fallacies (10-Pattern Scan)",
    ]

    if report.detected_fallacies:
        lines.extend([
            "| # | Pattern ID | Pattern Name | Severity | Evidence Snippet | Epistemic Diagnostic |",
            "|---|---|---|---|---|---|"
        ])
        for idx, f in enumerate(report.detected_fallacies, 1):
            snippet_clean = f.snippet.replace("\n", " ").replace("|", "\\|")
            if len(snippet_clean) > 80:
                snippet_clean = snippet_clean[:77] + "..."
            lines.append(
                f"| {idx} | `{f.pattern_id.value}` | {f.pattern_name} | {f.severity.value} | *\"{snippet_clean}\"* | {f.explanation} |"
            )
    else:
        lines.append("✅ *No standard structural fallacies or sycophancy patterns detected.*")

    lines.extend([
        "",
        "---",
        "",
        "## First-Principles & Boundary Violations",
    ])

    if report.boundary_violations:
        for b in report.boundary_violations:
            lines.append(f"- ❌ **{b.domain} ({b.law_name})**:")
            lines.append(f"  - **Claimed**: `{b.claimed_value}` vs **Theoretical Limit**: `{b.theoretical_limit}`")
            lines.append(f"  - **Discrepancy**: {b.delta_violation}")
            lines.append(f"  - **Axiomatic Grounding**: {b.first_principle_law}")
            lines.append(f"  - **Explanation**: {b.explanation}")
    else:
        lines.append("✅ *No physical, thermodynamic, or mathematical boundary violations detected.*")

    lines.extend([
        "",
        "---",
        "",
        "## Citation Cross-Examination & Verification Table",
    ])

    if report.citations:
        lines.extend([
            "| # | Raw Citation / Target | Extracted ID | Verification Status | Forensic Notes |",
            "|---|---|---|---|---|"
        ])
        for idx, c in enumerate(report.citations, 1):
            ident = c.identifier or c.title or "N/A"
            status_icon = "❌ PHANTOM" if c.is_phantom else ("✅ VERIFIED" if c.vault_grounded else "⚠️ UNINDEXED")
            notes_str = "; ".join(c.notes) if c.notes else "Format valid"
            lines.append(f"| {idx} | {c.raw_citation[:45]} | `{ident}` | {status_icon} | {notes_str} |")
    else:
        lines.append("*No explicit academic citations or DOIs detected in input text.*")

    lines.extend([
        "",
        "---",
        "",
        "## Counter-Argument Synthesis & Stress-Test",
        "",
        "### 1. Structural Mechanism Breakdown",
    ])

    for m_break in report.counter_argument.mechanism_breakdowns:
        lines.append(f"#### Target Claim: *\"{m_break.target_claim[:100]}\"*")
        for p in m_break.premises:
            lines.append(f"- **Premise**: {p}")
        for s in m_break.causal_steps:
            lines.append(f"- **Step**: {s}")
        lines.append(f"- **Fatal Leap**: {m_break.fatal_leap}")

    lines.extend([
        "",
        "### 2. Physical & Real-World Friction Analysis",
    ])
    for fr in report.counter_argument.friction_points:
        lines.append(f"- {fr}")

    lines.extend([
        "",
        "### 3. Socratic Counter-Questions",
    ])
    for idx, q in enumerate(report.counter_argument.socratic_questions, 1):
        lines.append(f"{idx}. *{q}*")

    if report.counter_argument.deductive_counter_proofs:
        lines.extend([
            "",
            "### 4. Deductive First-Principles Counter-Proof",
        ])
        for cp in report.counter_argument.deductive_counter_proofs:
            lines.append(f"#### Refutation of Claim: *{cp.target_claim}*")
            lines.append(f"- **Implicit Assumption ($A$)**: {cp.implicit_assumption}")
            lines.append(f"- **Empirical Axiom ($L$)**: {cp.empirical_axiom}")
            lines.append("- **Derivation of Contradiction**:")
            lines.append("```math")
            lines.append(cp.mathematical_derivation)
            lines.append("```")
            lines.append(f"- **Conclusion**: {cp.refutation_conclusion}")
            if cp.primary_citations:
                lines.append("- **Primary Foundational Literature**:")
                for cit in cp.primary_citations:
                    lines.append(f"  - {cit}")

    lines.extend([
        "",
        "---",
        "",
        "## Recommended Remediation & Balanced Synthesis",
    ])
    for idx, step in enumerate(report.remediation_steps, 1):
        lines.append(f"{idx}. {step}")

    lines.extend([
        "",
        "---",
        "*Generated by Uroboros Knowledge Engine — Adversarial AI Debate Auditor v1.0.0 (Zero-Dependency Stdlib Core)*"
    ])

    return "\n".join(lines)
