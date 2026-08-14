"""
Temporal Validity & Staleness Decay Module.
Zero-dependency, standard-library implementation for effective date extraction,
superseding/amendment marker detection, and domain half-life exponential staleness decay.
"""

import re
import math
from datetime import datetime, date
from typing import Dict, Any, Optional, Union

# --- Domain Half-Life Constants (in years) ---
DOMAIN_HALF_LIVES: Dict[str, float] = {
    "law": 10.0,            # Statutory law, U.S. Code, CFR, ISO standards
    "iso": 10.0,
    "statutory": 10.0,
    "academic": 5.0,        # Textbooks, curriculum handbooks, published research
    "textbook": 5.0,
    "secondary": 5.0,
    "tech_spec": 2.0,       # Official API specs, vendor whitepapers, protocols
    "specs": 2.0,
    "api": 2.0,
    "technical": 2.0,
    "commentary": 0.5,      # Informal notes, chat logs, forum threads
    "informal": 0.5,
    "notes": 0.5,
    "general": 3.0          # General documentation default
}

# Hard staleness decay caps by status
STATUS_PENALTY_CAPS: Dict[str, float] = {
    "SUPERSEDED": 0.40,
    "DEPRECATED": 0.50,
    "AMENDED": 0.75,
    "ACTIVE": 1.00
}

# --- Superseding & Amendment Marker Patterns ---
SUPERSEDING_PATTERNS = [
    # Explicit forward superseding (Document A is replaced by B)
    (re.compile(r'\b(?:superseded\s+by|obsoleted\s+by|replaced\s+by|rendered\s+obsolete\s+by)\s+([A-Za-z0-9_.\- /#]+)', re.IGNORECASE), "SUPERSEDED"),
    # Explicit deprecation markers
    (re.compile(r'\b(?:deprecated\s+in|deprecated\s+as\s+of|withdrawn\s+by)\s+([A-Za-z0-9_.\- /#]+)', re.IGNORECASE), "DEPRECATED"),
    # Explicit amendment / update markers
    (re.compile(r'\b(?:amended\s+as\s+of|amended\s+by|revised\s+by|modified\s+by)\s+([A-Za-z0-9_.\- /#]+)', re.IGNORECASE), "AMENDED"),
    # Standards Track header formats (RFC / ISO)
    (re.compile(r'\bObsoletes:\s*([0-9,\sA-Za-z_\-]+)', re.IGNORECASE), "SUPERSEDED"),
    (re.compile(r'\bUpdates:\s*([0-9,\sA-Za-z_\-]+)', re.IGNORECASE), "AMENDED")
]

# Date Parsing Patterns
ISO_DATE_REGEX = re.compile(r'\b(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b')
FULL_DATE_REGEX = re.compile(
    r'\b(?:(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})|(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4}))\b',
    re.IGNORECASE
)
YEAR_REGEX = re.compile(r'\b(19\d\d|20\d\d)\b')
EFFECTIVE_DATE_PREFIX = re.compile(
    r'\b(?:effective|dated|amended|promulgated|published|issued)\s*(?:as of|on|date:)?\s*([A-Za-z0-9,\s\-]+?\b(?:19\d\d|20\d\d))\b',
    re.IGNORECASE
)


def compute_temporal_decay(
    document_year_or_date: Optional[Union[int, str, datetime, date]] = None,
    domain: str = "general",
    status: str = "ACTIVE",
    half_life_days: Optional[float] = None
) -> float:
    """
    Computes the exponential temporal staleness decay multiplier:
        Phi_temporal = exp( -lambda * delta_t )
        where lambda = ln(2) / HalfLife

    Args:
        document_year_or_date: Year (int), ISO date string ('YYYY-MM-DD'), or datetime/date object.
        domain: Document domain ('law', 'iso', 'academic', 'tech_spec', 'commentary', 'general').
        status: Temporal validity status ('ACTIVE', 'SUPERSEDED', 'DEPRECATED', 'AMENDED').
        half_life_days: Optional explicit override for half-life in days.

    Returns:
        Staleness decay multiplier in (0.0, 1.0], subject to domain curves and status caps.
    """
    now = datetime.now()
    current_year = now.year

    # 1. Determine Half-Life in years
    if half_life_days is not None and half_life_days > 0:
        half_life_years = half_life_days / 365.25
    else:
        domain_key = (domain or "general").lower()
        half_life_years = DOMAIN_HALF_LIVES.get(domain_key, DOMAIN_HALF_LIVES["general"])

    # 2. Calculate age (delta_t) in years
    delta_years = 0.0
    if document_year_or_date is not None:
        if isinstance(document_year_or_date, (datetime, date)):
            doc_date = document_year_or_date if isinstance(document_year_or_date, date) else document_year_or_date.date()
            delta_days = (now.date() - doc_date).days
            delta_years = max(0.0, delta_days / 365.25)
        elif isinstance(document_year_or_date, int):
            delta_years = max(0.0, float(current_year - document_year_or_date))
        elif isinstance(document_year_or_date, str):
            doc_str = document_year_or_date.strip()
            # Try ISO date parse
            iso_match = ISO_DATE_REGEX.search(doc_str)
            if iso_match:
                try:
                    d = datetime.strptime(iso_match.group(0), "%Y-%m-%d").date()
                    delta_days = (now.date() - d).days
                    delta_years = max(0.0, delta_days / 365.25)
                except ValueError:
                    year_match = YEAR_REGEX.search(doc_str)
                    if year_match:
                        delta_years = max(0.0, float(current_year - int(year_match.group(1))))
            else:
                year_match = YEAR_REGEX.search(doc_str)
                if year_match:
                    delta_years = max(0.0, float(current_year - int(year_match.group(1))))

    # 3. Exponential decay curve: exp(-ln(2)/T_half * delta_t)
    decay_rate = math.log(2) / max(0.1, half_life_years)
    decay = math.exp(-decay_rate * delta_years)

    # 4. Enforce hard penalty caps based on status
    status_normalized = (status or "ACTIVE").upper()
    cap = STATUS_PENALTY_CAPS.get(status_normalized, 1.00)
    decay = min(decay, cap)

    # 5. Apply floor to prevent zeroing out historical artifacts
    floor = 0.05
    decay = max(floor, decay)

    return round(decay, 4)


def detect_temporal_validity(
    content: str,
    publication_year: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extracts publication date, effective date range, and scans for superseding,
    deprecation, or amendment markers within document content and metadata.

    Returns:
        {
            'is_superseded': bool,
            'superseded_by': str | None,
            'publication_year': int | None,
            'effective_date': str | None,
            'temporal_status': str,  # 'ACTIVE', 'SUPERSEDED', 'DEPRECATED', 'AMENDED'
            'staleness_coefficient': float,
            'age_years': float
        }
    """
    now = datetime.now()
    current_year = now.year

    header_snippet = content[:4000] if content else ""
    metadata = metadata or {}

    is_superseded = False
    superseded_by = None
    temporal_status = "ACTIVE"

    # 1. Scan for superseding & amendment markers
    for pattern, status_type in SUPERSEDING_PATTERNS:
        match = pattern.search(header_snippet)
        if match:
            target_identifier = match.group(1).strip()
            # Clean trailing punctuation
            target_identifier = re.sub(r'[\.,;:\(\)]+$', '', target_identifier).strip()
            if status_type == "SUPERSEDED":
                is_superseded = True
                superseded_by = target_identifier
                temporal_status = "SUPERSEDED"
                break
            elif status_type == "DEPRECATED" and temporal_status != "SUPERSEDED":
                temporal_status = "DEPRECATED"
                superseded_by = target_identifier
            elif status_type == "AMENDED" and temporal_status == "ACTIVE":
                temporal_status = "AMENDED"
                superseded_by = target_identifier

    # 2. Extract publication year / effective date
    pub_year = publication_year or metadata.get("publication_year") or metadata.get("effective_year")
    effective_date_str = metadata.get("effective_date")

    if not effective_date_str:
        eff_match = EFFECTIVE_DATE_PREFIX.search(header_snippet)
        if eff_match:
            effective_date_str = eff_match.group(1).strip()

    if not pub_year:
        if effective_date_str:
            y_match = YEAR_REGEX.search(effective_date_str)
            if y_match:
                pub_year = int(y_match.group(1))
        if not pub_year:
            iso_match = ISO_DATE_REGEX.search(header_snippet)
            if iso_match:
                pub_year = int(iso_match.group(1))
                if not effective_date_str:
                    effective_date_str = iso_match.group(0)
            else:
                full_date_match = FULL_DATE_REGEX.search(header_snippet)
                if full_date_match:
                    pub_year = int(full_date_match.group(3) or full_date_match.group(6))
                    if not effective_date_str:
                        effective_date_str = full_date_match.group(0)
                else:
                    year_match = YEAR_REGEX.search(header_snippet)
                    if year_match:
                        candidate_year = int(year_match.group(1))
                        if 1970 <= candidate_year <= current_year + 1:
                            pub_year = candidate_year

    # 3. Calculate age in years
    age_years = max(0.0, float(current_year - pub_year)) if pub_year else 0.0

    # 4. Determine domain
    domain = metadata.get("domain", metadata.get("category", "general"))

    # 5. Compute staleness decay coefficient
    staleness_coeff = compute_temporal_decay(
        document_year_or_date=effective_date_str or pub_year,
        domain=domain,
        status=temporal_status,
        half_life_days=metadata.get("half_life_days")
    )

    return {
        "is_superseded": is_superseded,
        "superseded_by": superseded_by,
        "publication_year": pub_year,
        "effective_date": effective_date_str,
        "temporal_status": temporal_status,
        "staleness_coefficient": staleness_coeff,
        "age_years": age_years
    }
