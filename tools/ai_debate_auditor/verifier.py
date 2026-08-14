"""
Verifier Engine (R2) for Adversarial AI Debate Auditor.
Multi-tier citation forensics, physical & mathematical boundary invariant verification,
and local SQLite knowledge vault cross-examination with graceful offline fallback.
"""

import re
import math
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from .models import (
    CitationCheck,
    CitationStatus,
    BoundaryViolation,
    PatternSeverity,
    Claim
)

# Physical constants in SI units
SPEED_OF_LIGHT = 299792458.0  # m/s
BOLTZMANN_K = 1.380649e-23     # J/K
ABSOLUTE_ZERO_C = -273.15      # Celsius
LANDAUER_ROOM_TEMP_J = BOLTZMANN_K * 300.0 * math.log(2)  # ~2.87e-21 J/bit at 300K
CURRENT_YEAR = 2026

# Power unit conversions to Watts
POWER_UNIT_MULTIPLIERS = {
    "w": 1.0,
    "watt": 1.0,
    "watts": 1.0,
    "kw": 1e3,
    "kilowatt": 1e3,
    "kilowatts": 1e3,
    "mw": 1e6,
    "megawatt": 1e6,
    "megawatts": 1e6,
    "gw": 1e9,
    "gigawatt": 1e9,
    "gigawatts": 1e9,
}

# Known fabricated / buzzword journal patterns
FAKE_JOURNAL_KEYWORDS = [
    "hyper-quantum", "over-unity", "free energy", "quantum fluff", "telepathy",
    "infinite scalability", "perpetual motion", "anti-gravity studies", "etheric physics"
]


# ============================================================================
# CITATION VERIFICATION FORENSICS
# ============================================================================

RE_DOI = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b")
RE_ARXIV = re.compile(r"\barXiv:\s*(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})\b", re.IGNORECASE)
RE_PMID = re.compile(r"\b(?:PMID|PubMed ID):\s*(\d{7,9})\b", re.IGNORECASE)
RE_FORMAL_CITATION = re.compile(
    r"([A-Z][a-zA-Z]{0,25}(?:\s+[A-Z][a-zA-Z]{0,25}){0,4}(?:\s+et\s+al\.|\s*&\s*[A-Z][a-zA-Z]{0,25}(?:\s+[A-Z][a-zA-Z]{0,25}){0,4})?),\s*\(?(19\d{2}|20\d{2})\)?,\s*[\"“']([^\"”']{3,120})[\"”'],\s*([A-Za-z0-9\s.,]{3,80})",
    re.IGNORECASE
)
RE_AUTHOR_YEAR = re.compile(
    r"\b([A-Z][a-zA-Z]{1,25}(?:\s+et\s+al\.)?)\s*\(?(19\d{2}|20\d{2})\)?\b"
)


def extract_citations(text: str) -> List[CitationCheck]:
    """
    Extract structured scholarly references, DOIs, arXiv IDs, PMIDs, and author-year citations.
    """
    results: List[CitationCheck] = []
    seen_identifiers = set()
    
    # 1. DOI Extraction
    for m in RE_DOI.finditer(text):
        doi_str = m.group(1).rstrip(".,;)")
        if doi_str in seen_identifiers:
            continue
        seen_identifiers.add(doi_str)
        
        # Validate DOI prefix
        prefix_match = re.match(r"^10\.(\d+)/", doi_str)
        is_valid = True
        is_phantom = False
        notes = []
        phantom_score = 0.0
        
        if prefix_match:
            prefix_num = int(prefix_match.group(1))
            # Standard CrossRef prefixes are >= 1000; 9999 and 0000 are reserved test/bogus
            if prefix_num < 1000 or prefix_num == 9999 or prefix_num == 0:
                is_valid = False
                is_phantom = True
                phantom_score = 0.95
                notes.append(f"Unallocated/invalid DOI registrant prefix 10.{prefix_num}")
        else:
            is_valid = False
            notes.append("Malformed DOI structure")
            
        status = CitationStatus.PHANTOM_FABRICATED if is_phantom else (
            CitationStatus.UNINDEXED_PLAUSIBLE if is_valid else CitationStatus.INVALID_IDENTIFIER
        )
        
        results.append(
            CitationCheck(
                raw_citation=doi_str,
                citation_type="doi",
                identifier=doi_str,
                status=status,
                is_valid=is_valid,
                is_phantom=is_phantom,
                phantom_score=phantom_score,
                notes=notes
            )
        )

    # 2. arXiv ID Extraction
    for m in RE_ARXIV.finditer(text):
        arxiv_id = m.group(1)
        if arxiv_id in seen_identifiers:
            continue
        seen_identifiers.add(arxiv_id)
        
        is_valid = True
        is_phantom = False
        notes = []
        phantom_score = 0.0
        
        # New arXiv format YYMM.number
        if "." in arxiv_id:
            yymm = arxiv_id.split(".")[0]
            if len(yymm) == 4 and yymm.isdigit():
                yy = int(yymm[:2])
                mm = int(yymm[2:])
                current_yy = CURRENT_YEAR % 100
                if yy > current_yy or (yy == current_yy and mm > 12) or mm < 1 or mm > 12:
                    is_phantom = True
                    phantom_score = 0.95
                    notes.append(f"Impossible future arXiv publication date (YYMM={yymm})")
        
        status = CitationStatus.PHANTOM_FABRICATED if is_phantom else CitationStatus.UNINDEXED_PLAUSIBLE
        
        results.append(
            CitationCheck(
                raw_citation=m.group(0),
                citation_type="arxiv",
                identifier=f"arXiv:{arxiv_id}",
                status=status,
                is_valid=is_valid,
                is_phantom=is_phantom,
                phantom_score=phantom_score,
                notes=notes
            )
        )

    # 3. PubMed PMID Extraction
    for m in RE_PMID.finditer(text):
        pmid_str = m.group(1)
        if pmid_str in seen_identifiers:
            continue
        seen_identifiers.add(pmid_str)
        
        results.append(
            CitationCheck(
                raw_citation=m.group(0),
                citation_type="pmid",
                identifier=f"PMID:{pmid_str}",
                status=CitationStatus.UNINDEXED_PLAUSIBLE,
                is_valid=True,
                is_phantom=False,
                phantom_score=0.0,
                notes=["Valid PubMed identifier format"]
            )
        )

    # 4. Formal Citation (Author, Year, Title, Journal)
    for m in RE_FORMAL_CITATION.finditer(text):
        authors_raw = m.group(1).strip()
        year_str = m.group(2).strip()
        title = m.group(3).strip()
        journal = m.group(4).strip()
        year = int(year_str) if year_str.isdigit() else None
        
        is_phantom = False
        phantom_score = 0.0
        notes = []
        
        # Chronological Paradox
        if year and year > CURRENT_YEAR:
            is_phantom = True
            phantom_score = max(phantom_score, 0.95)
            notes.append(f"Chronological paradox: publication year {year} is in the future")
        elif year and year < 1665:
            is_phantom = True
            phantom_score = max(phantom_score, 0.90)
            notes.append(f"Impossible publication year {year} predates modern scientific journals (1665)")

        # Fake Journal Detection
        if any(fk in journal.lower() for fk in FAKE_JOURNAL_KEYWORDS):
            is_phantom = True
            phantom_score = max(phantom_score, 0.98)
            notes.append(f"Fabricated/buzzword journal venue detected: '{journal}'")

        status = CitationStatus.PHANTOM_FABRICATED if is_phantom else CitationStatus.UNINDEXED_PLAUSIBLE
        
        results.append(
            CitationCheck(
                raw_citation=m.group(0),
                citation_type="author_year_title",
                title=title,
                authors=[authors_raw],
                year=year,
                journal=journal,
                status=status,
                is_valid=True,
                is_phantom=is_phantom,
                phantom_score=phantom_score,
                notes=notes
            )
        )

    # 5. Ad-hoc Author-Year (e.g., "Dr. Albus Einstein, Journal of Hyper-Quantum Telepathy, Vol 99, 2028")
    adhoc_fake_pattern = re.compile(
        r"((?:(?:Dr|Prof|Mr|Ms|Mrs)\.?\s+)?[A-Z][a-zA-Z]{0,25}(?:\s+[A-Z][a-zA-Z]{0,25}){0,4}),\s*([A-Za-z0-9\s\-]{0,60}?(?:Journal|Trans(?:actions)?|Review|Letters|Studies|Physics|Proceedings)[A-Za-z0-9\s\-]{0,40}),\s*(?:Vol(?:ume)?\s*(\d+),?\s*)?(20\d{2}|19\d{2})",
        re.IGNORECASE
    )
    for m in adhoc_fake_pattern.finditer(text):
        raw = m.group(0)
        if any(raw in c.raw_citation for c in results):
            continue
        author = m.group(1).strip()
        venue = m.group(2).strip()
        vol_str = m.group(3)
        year_str = m.group(4)
        year = int(year_str) if year_str and year_str.isdigit() else None
        
        is_phantom = False
        phantom_score = 0.0
        notes = []
        
        if year and year > CURRENT_YEAR:
            is_phantom = True
            phantom_score = max(phantom_score, 0.95)
            notes.append(f"Publication year {year} is in the future")
            
        if any(fk in venue.lower() for fk in FAKE_JOURNAL_KEYWORDS):
            is_phantom = True
            phantom_score = max(phantom_score, 0.98)
            notes.append(f"Fake journal venue: '{venue}'")
            
        if vol_str and int(vol_str) > 500:
            is_phantom = True
            phantom_score = max(phantom_score, 0.85)
            notes.append(f"Plausibility failure: absurd volume number {vol_str}")

        if is_phantom:
            results.append(
                CitationCheck(
                    raw_citation=raw,
                    citation_type="adhoc_reference",
                    authors=[author],
                    journal=venue,
                    year=year,
                    status=CitationStatus.PHANTOM_FABRICATED,
                    is_valid=True,
                    is_phantom=True,
                    phantom_score=phantom_score,
                    notes=notes
                )
            )

    return results


def cross_examine_vault(citations: List[CitationCheck], db_path: Optional[str] = None) -> List[CitationCheck]:
    """
    Cross-examine extracted citations against local SQLite knowledge vault (FTS5).
    Falls back gracefully if database is unavailable.
    """
    if not citations:
        return []
    
    conn = None
    try:
        # Check standard database locations
        candidates = [
            db_path,
            "knowledge.db",
            "uroboros.db",
            os.path.join(os.getcwd(), "knowledge.db"),
            os.path.join(os.getcwd(), "uroboros.db")
        ]
        target_db = next((c for c in candidates if c and os.path.isfile(c)), None)
        
        if target_db:
            conn = sqlite3.connect(target_db, timeout=2.0)
            cursor = conn.cursor()
            
            # Check if files or files_fts table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('files', 'files_fts', 'fts_file_chunks')")
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                for cite in citations:
                    if cite.is_phantom:
                        continue
                        
                    query_term = cite.identifier or cite.title
                    if not query_term and cite.authors:
                        query_term = cite.authors[0]
                        
                    if query_term:
                        # Clean query for search
                        clean_query = re.sub(r"[^\w\s]", " ", query_term).strip()
                        if clean_query:
                            try:
                                if "files" in tables:
                                    cursor.execute("SELECT filepath, content FROM files WHERE content LIKE ? LIMIT 1", (f"%{clean_query[:40]}%",))
                                    row = cursor.fetchone()
                                    if row:
                                        cite.status = CitationStatus.VERIFIED_LOCAL
                                        cite.vault_grounded = True
                                        cite.matched_doc = row[0]
                                        cite.notes.append(f"Grounded in local vault document: {row[0]}")
                            except Exception:
                                pass
    except Exception:
        # Graceful fallback: offline mode
        pass
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
                
    return citations


# ============================================================================
# FIRST-PRINCIPLES & PHYSICAL / MATHEMATICAL BOUNDARY INVARIANTS
# ============================================================================

def verify_boundaries(text: str) -> List[BoundaryViolation]:
    """
    Verify first-principles physical, thermodynamic, relativistic, and mathematical boundaries.
    """
    violations: List[BoundaryViolation] = []
    lower = text.lower()

    # -------------------------------------------------------------------------
    # 1. First Law of Thermodynamics: Over-Unity Efficiency (>100% / Free Energy)
    # -------------------------------------------------------------------------
    seen_eff_snippets = set()
    eff_patterns = [
        re.compile(
            r"\b(?:achiev(?:ing|es|ed|e)?|produces?|output|yielding|yields?|reaches?|with|has)\s+(?:(?:an?\s+)?(?:electrical\s+|thermal\s+)?efficiency\s+(?:of\s+)?)?(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?=[^\w]|$)",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:with\s+(?:an?\s+)?)?(?:electrical\s+|thermal\s+)?efficiency\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?=[^\w]|$)",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)\s*(?:efficiency|electrical\s+efficiency|thermal\s+efficiency|energy\s+recovery)(?=[^\w]|$)",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:over-unity|cop|coefficient\s+of\s+performance)\s*(?:=|is|of)?\s*(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?=[^\w]|$)",
            re.IGNORECASE
        )
    ]
    for eff_pat in eff_patterns:
        for m in eff_pat.finditer(lower):
            val = float(m.group(1))
            snippet = m.group(0)
            if val > 100.0 and snippet not in seen_eff_snippets:
                seen_eff_snippets.add(snippet)
                violations.append(
                    BoundaryViolation(
                        domain="Thermodynamics",
                        law_name="First Law of Thermodynamics (Conservation of Energy)",
                        claimed_value=f"{val}%",
                        theoretical_limit="100.0%",
                        delta_violation=f"+{val - 100.0}% over-unity",
                        explanation=f"Claim asserts energy conversion efficiency of {val}%, creating free energy ex nihilo and violating delta U = Q - W.",
                        first_principle_law="First Law of Thermodynamics (Axiom of Energy Conservation)",
                        severity=PatternSeverity.CRITICAL,
                        claim_snippet=snippet
                    )
                )

    # Check for power input vs output with multi-unit support (W, kW, MW, GW) and 0W guard
    power_matches = re.finditer(
        r"\b(?:produces?|yields?|generates?|output\s+of)\s*(\d+(?:\.\d+)?)\s*(gw|gigawatts?|mw|megawatts?|kw|kilowatts?|w|watts?)(?:\s*(?:of\s*)?(?:electrical\s*)?output)?\s*(?:from|with)\s*(\d+(?:\.\d+)?)\s*(gw|gigawatts?|mw|megawatts?|kw|kilowatts?|w|watts?)(?:\s*input)?\b",
        lower
    )
    for power_match in power_matches:
        val_out = float(power_match.group(1))
        unit_out = power_match.group(2).lower()
        val_in = float(power_match.group(3))
        unit_in = power_match.group(4).lower()

        p_out_watts = val_out * POWER_UNIT_MULTIPLIERS.get(unit_out, 1.0)
        p_in_watts = val_in * POWER_UNIT_MULTIPLIERS.get(unit_in, 1.0)

        if p_out_watts > p_in_watts:
            if p_in_watts > 0:
                eff = (p_out_watts / p_in_watts) * 100.0
                claimed_val = f"Output: {val_out} {power_match.group(2)} / Input: {val_in} {power_match.group(4)} (eta = {eff:.1f}%)"
            else:
                eff = float("inf")
                claimed_val = f"Output: {val_out} {power_match.group(2)} / Input: 0 {power_match.group(4)} (eta = Infinite %)"

            violations.append(
                BoundaryViolation(
                    domain="Thermodynamics",
                    law_name="First Law of Thermodynamics (Energy Balance)",
                    claimed_value=claimed_val,
                    theoretical_limit="Output <= Input (eta <= 100%)",
                    delta_violation=f"+{p_out_watts - p_in_watts:g}W ungrounded excess power",
                    explanation=f"Over-unity power extraction ({val_out} {power_match.group(2)} out vs {val_in} {power_match.group(4)} in) with no external heat or mass source.",
                    first_principle_law="Conservation of Energy (First Law)",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=power_match.group(0)
                )
            )

    # -------------------------------------------------------------------------
    # 2. Second Law of Thermodynamics: Carnot Maximum Efficiency
    # -------------------------------------------------------------------------
    for carnot_match in re.finditer(
        r"\b(?:operating|cycle|engine)\s+(?:between\s+)?(\d+)\s*(?:k|kelvin)\s+and\s+(\d+)\s*(?:k|kelvin)[^.\n;]+?(?:achiev(?:ing|es|ed)?|yields?|yielding|produces?|with|of|having)\s+(?:(?:an?\s+)?(?:thermal\s+|electrical\s+)?efficiency\s+(?:of\s+)?)?(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?=[^\w]|$)",
        lower
    ):
        t1 = float(carnot_match.group(1))
        t2 = float(carnot_match.group(2))
        claimed_eff = float(carnot_match.group(3)) / 100.0
        
        t_cold = min(t1, t2)
        t_hot = max(t1, t2)
        
        if t_hot > 0:
            carnot_limit = 1.0 - (t_cold / t_hot)
            if claimed_eff > carnot_limit + 1e-4:
                violations.append(
                    BoundaryViolation(
                        domain="Thermodynamics",
                        law_name="Carnot Maximum Thermodynamic Efficiency",
                        claimed_value=f"{claimed_eff * 100:.1f}%",
                        theoretical_limit=f"{carnot_limit * 100:.1f}% (Carnot Limit at {t_cold}K/{t_hot}K)",
                        delta_violation=f"+{(claimed_eff - carnot_limit) * 100:.1f}% beyond Carnot maximum",
                        explanation=f"Thermal engine claims efficiency ({claimed_eff*100:.1f}%) exceeding the theoretical Carnot ceiling ({carnot_limit*100:.1f}%) for reservoirs {t_cold}K and {t_hot}K.",
                        first_principle_law="Second Law of Thermodynamics (Carnot Theorem)",
                        severity=PatternSeverity.CRITICAL,
                        claim_snippet=carnot_match.group(0)
                    )
                )

    # -------------------------------------------------------------------------
    # 3. Third Law of Thermodynamics: Absolute Zero Temperature
    # -------------------------------------------------------------------------
    sub_zero_k = re.search(r"(?:^|[^\w])(-\d+(?:\.\d+)?)\s*(?:k|kelvin)\b", lower)
    if sub_zero_k:
        val = float(sub_zero_k.group(1))
        if val < 0:
            violations.append(
                BoundaryViolation(
                    domain="Thermodynamics",
                    law_name="Third Law of Thermodynamics (Absolute Zero Bound)",
                    claimed_value=f"{val} K",
                    theoretical_limit="0.0 K",
                    delta_violation=f"{val} K below absolute zero",
                    explanation=f"Temperature {val} K violates absolute zero lower bound.",
                    first_principle_law="Third Law of Thermodynamics",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=sub_zero_k.group(0).strip()
                )
            )

    sub_zero_c = re.search(r"(?:^|[^\w])(-\d+(?:\.\d+)?)\s*(?:c|celsius|°c)\b", lower)
    if sub_zero_c:
        val = float(sub_zero_c.group(1))
        if val < ABSOLUTE_ZERO_C:
            violations.append(
                BoundaryViolation(
                    domain="Thermodynamics",
                    law_name="Third Law of Thermodynamics (Absolute Zero Bound)",
                    claimed_value=f"{val} °C",
                    theoretical_limit=f"{ABSOLUTE_ZERO_C} °C",
                    delta_violation=f"{val - ABSOLUTE_ZERO_C:.2f} °C below absolute zero",
                    explanation=f"Temperature {val} °C is below absolute zero (-273.15 °C).",
                    first_principle_law="Third Law of Thermodynamics",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=sub_zero_c.group(0).strip()
                )
            )

    # -------------------------------------------------------------------------
    # 4. Special Relativity: Speed of Light Constraint
    # -------------------------------------------------------------------------
    superluminal_patterns = [
        re.compile(
            r"\b(?:signals?|data|information|particles?|matter|photons?|neutrinos?|velocity|speed|propagation\s+speed)\s+(?:(?:were|was|is|are|been|being)\s+)?(?:(?:recorded|measured|observed|reported|detected)\s+)?(?:propagating|traveling|moving|transmitted|exceeding|of)\s+(?:at\s+)?(\d+(?:,\d+)*(?:\.\d+)?)\s*(km/s|m/s|times\s+the\s+speed\s+of\s+light|times\s+c|\bc\b)(?=[^\w]|$)",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:transmits?|transmitted|transmitting|sends?|sent|sending|broadcasts?|broadcasting|propagates?|propagated|propagating)\s+(?:[\w\s]{0,30}?\s+)?at\s+(\d+(?:,\d+)*(?:\.\d+)?)\s*(km/s|m/s|times\s+the\s+speed\s+of\s+light|times\s+c|\bc\b)(?=[^\w]|$)",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:velocity|speed|propagation\s+speed)\s+(?:of\s+)?(\d+(?:,\d+)*(?:\.\d+)?)\s*(km/s|m/s)(?=[^\w]|$)",
            re.IGNORECASE
        )
    ]
    seen_superluminal = set()
    for spat in superluminal_patterns:
        for sm in spat.finditer(lower):
            raw_num = sm.group(1).replace(",", "")
            unit = sm.group(2).lower()
            num = float(raw_num)
            snippet = sm.group(0)
            if snippet in seen_superluminal:
                continue
            
            is_violation = False
            claimed_str = ""
            
            if "km/s" in unit and num > 300000.0:
                is_violation = True
                claimed_str = f"{num:g} km/s ({num/300000.0:.2f}c)"
            elif "m/s" in unit and num > SPEED_OF_LIGHT:
                is_violation = True
                claimed_str = f"{num:g} m/s ({num/SPEED_OF_LIGHT:.2f}c)"
            elif ("times the speed of light" in unit or "times c" in unit or unit == "c") and num > 1.0:
                is_violation = True
                claimed_str = f"{num:g}c"
                
            if is_violation:
                seen_superluminal.add(snippet)
                violations.append(
                    BoundaryViolation(
                        domain="Special Relativity",
                        law_name="Einstein Speed of Light Invariant (v <= c)",
                        claimed_value=claimed_str,
                        theoretical_limit="c = 299,792,458 m/s",
                        delta_violation="Superluminal velocity",
                        explanation="Information or matter propagation claims exceeding universal vacuum speed of light c violate Lorentz invariance and local causality.",
                        first_principle_law="Special Relativity (Lorentz Invariance)",
                        severity=PatternSeverity.CRITICAL,
                        claim_snippet=snippet
                    )
                )

    if "instantaneous transmission over" in lower or "faster-than-light communication" in lower:
        violations.append(
            BoundaryViolation(
                domain="Special Relativity",
                law_name="Relativistic Causality & No-Communication Theorem",
                claimed_value="Instantaneous / FTL transmission",
                theoretical_limit="Bounded by c in medium",
                delta_violation="Infinite propagation speed",
                explanation="Superluminal or instantaneous signaling violates relativistic causality and quantum no-communication bounds.",
                first_principle_law="Special Relativity & Quantum Information Theory",
                severity=PatternSeverity.CRITICAL,
                claim_snippet="instantaneous transmission"
            )
        )

    # -------------------------------------------------------------------------
    # 5. Kolmogorov Probability Axioms
    # -------------------------------------------------------------------------
    # Axiom 1: Non-negativity P(E) >= 0
    for m in re.finditer(
        r"\b(?:probability|p(?:\([a-z\s_-]{1,30}\))?)\s*(?:of\s+[\w\s_-]{1,40}?)?\s*(?:is|=|of|equals?|reaches?|calculated\s+(?:as|at|to\s+be))\s*(-\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)?(?=[^\w]|$)",
        lower
    ):
        val = float(m.group(1))
        if val < 0.0:
            violations.append(
                BoundaryViolation(
                    domain="Probability Theory",
                    law_name="Kolmogorov Axiom I (Non-negativity)",
                    claimed_value=f"P = {val}",
                    theoretical_limit="0.0 <= P(E) <= 1.0",
                    delta_violation=f"Negative probability P = {val}",
                    explanation=f"Negative probability value {val} violates foundational measure theory.",
                    first_principle_law="Kolmogorov Axiom 1 (Non-negativity of Probability)",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=m.group(0)
                )
            )

    # Axiom 2: Unit measure P(E) <= 1.0 (Percentage > 100%)
    for m in re.finditer(
        r"\b(?:probability|p(?:\([a-z\s_-]{1,30}\))?)\s*(?:of\s+[\w\s_-]{1,40}?)?\s*(?:is|=|of|equals?|reaches?|calculated\s+(?:as|at|to\s+be))?\s*(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?=[^\w]|$)",
        lower
    ):
        val = float(m.group(1))
        if val > 100.0:
            violations.append(
                BoundaryViolation(
                    domain="Probability Theory",
                    law_name="Kolmogorov Axiom II (Unit Measure)",
                    claimed_value=f"{val}%",
                    theoretical_limit="100.0% (P <= 1.0)",
                    delta_violation=f"+{val - 100.0}% above unit measure",
                    explanation=f"Probability {val}% exceeds universal sample space measure 1.0.",
                    first_principle_law="Kolmogorov Axiom 2",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=m.group(0)
                )
            )

    # Axiom 2: Unit measure P(E) <= 1.0 (Scalar decimal P > 1.0, e.g. P = 1.5, probability is 1.5)
    for m in re.finditer(
        r"\b(?:probability|p(?:\([a-z\s_-]{1,30}\))?)\s*(?:of\s+[\w\s_-]{1,40}?)?\s*(?:is|=|equals?|calculated\s+(?:as|at|to\s+be))\s+(\d+\.\d+)(?=[^\w%]|$)",
        lower
    ):
        val = float(m.group(1))
        if val > 1.0:
            violations.append(
                BoundaryViolation(
                    domain="Probability Theory",
                    law_name="Kolmogorov Axiom II (Unit Measure)",
                    claimed_value=f"P = {val}",
                    theoretical_limit="0.0 <= P(E) <= 1.0",
                    delta_violation=f"Scalar probability P = {val} exceeds unit measure 1.0",
                    explanation=f"Probability scalar value {val} exceeds universal measure maximum 1.0.",
                    first_principle_law="Kolmogorov Axiom 2",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=m.group(0)
                )
            )

    # -------------------------------------------------------------------------
    # 6. Computational Complexity Bounds
    # -------------------------------------------------------------------------
    if re.search(r"\b(comparison\s+sort(?:ing)?|sort\s+arbitrary\s+elements?)\s+in\s+o\(1\)|o\(n\)\s+comparison\s+sort\b", lower):
        violations.append(
            BoundaryViolation(
                domain="Computational Complexity",
                law_name="Comparison-Based Sorting Lower Bound",
                claimed_value="O(n) / O(1) comparison sort",
                theoretical_limit="Omega(n log n)",
                delta_violation="Sub-log-linear comparison sorting",
                explanation="Comparison sort decision tree requires height log2(n!) = Omega(n log n).",
                first_principle_law="Information-Theoretic Decision Tree Lower Bound",
                severity=PatternSeverity.HIGH,
                claim_snippet="O(1) / O(n) comparison sort"
            )
        )

    # -------------------------------------------------------------------------
    # 7. Betz Limit (Wind Energy)
    # -------------------------------------------------------------------------
    betz_matches = re.finditer(
        r"\bwind\s*turbines?\s*(?:extracts?|efficiency|achiev(?:ing|es|ed)?|captures?|producing)\s*(\d+(?:\.\d+)?)\s*(?:%|\bpercent\b)(?:\s*(?:of\s*(?:the\s*)?kinetic\s*wind\s*energy))?(?=[^\w]|$)",
        lower
    )
    for betz_match in betz_matches:
        val = float(betz_match.group(1))
        if val > 59.3:
            violations.append(
                BoundaryViolation(
                    domain="Fluid Dynamics",
                    law_name="Betz Limit for Wind Turbines",
                    claimed_value=f"{val}%",
                    theoretical_limit="16/27 ≈ 59.3%",
                    delta_violation=f"+{val - 59.3:.1f}% beyond Betz ceiling",
                    explanation="No open-flow wind turbine can capture more than 59.3% of the kinetic energy in wind due to mass conservation and back-pressure deceleration.",
                    first_principle_law="Betz's Law (Continuity and Momentum Balance in Open Actuator Disks)",
                    severity=PatternSeverity.HIGH,
                    claim_snippet=betz_match.group(0)
                )
            )

    # -------------------------------------------------------------------------
    # 8. Landauer's Principle (Thermodynamics of Computation & Information Erasure)
    # -------------------------------------------------------------------------
    landauer_patterns = [
        re.compile(
            r"\b(?:irreversible\s+bit\s+erasure|bit\s+erasure|erasing\s+(?:a\s+)?bits?|memory\s+erasure|logical\s+state\s+reset)\s+(?:with\s+)?(?:zero\s+(?:energy(?:\s+dissipation)?|heat(?:\s+generation)?|thermodynamic\s+cost)|without\s+(?:any\s+)?(?:energy(?:\s+dissipation)?|heat(?:\s+generation)?|entropy\s+generation|dissipating\s+heat))\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:zero-dissipation|dissipationless|zero\s+energy)\s+(?:irreversible\s+)?bit\s+erasure\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\bsub-landauer\s+(?:energy\s+dissipation|irreversible\s+computation|bit\s+erasure)\b",
            re.IGNORECASE
        )
    ]
    for lpat in landauer_patterns:
        for lm in lpat.finditer(lower):
            violations.append(
                BoundaryViolation(
                    domain="Information Theory",
                    law_name="Landauer Principle (Thermodynamic Cost of Information Erasure)",
                    claimed_value="Zero energy dissipation during irreversible bit erasure",
                    theoretical_limit=f"E >= k_B * T * ln(2) ≈ {LANDAUER_ROOM_TEMP_J:.2e} J/bit at 300K",
                    delta_violation="Sub-Landauer / zero-dissipation irreversible erasure",
                    explanation="Landauer's Principle mandates that erasing one bit of physical information in an irreversible logical operation increases environmental entropy by at least k_B ln 2, dissipating minimum heat Q >= k_B T ln 2.",
                    first_principle_law="Landauer's Bound & Second Law of Thermodynamics",
                    severity=PatternSeverity.CRITICAL,
                    claim_snippet=lm.group(0)
                )
            )

    return violations
