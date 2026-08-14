"""
Epistemic Evidentiary Tiering & Mathematical RRF Fusion Module.
Zero-dependency, standard-library implementation for authority hierarchy
classification and authority-weighted Reciprocal Rank Fusion (RRF).
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple

# --- Authority Hierarchy Constants ---
TIER_1_PRIMARY = "TIER_1_PRIMARY"
TIER_2_TECH_SPEC = "TIER_2_TECH_SPEC"
TIER_3_SECONDARY = "TIER_3_SECONDARY"
TIER_4_COMMENTARY = "TIER_4_COMMENTARY"

TIER_WEIGHTS: Dict[str, float] = {
    TIER_1_PRIMARY: 1.00,       # Statutory law, ISO/IEC/RFC specs, SEC 10-K, Git Merkle provenance, source code
    TIER_2_TECH_SPEC: 0.85,     # Official API specs, vendor whitepapers, datasheets, system architecture
    TIER_3_SECONDARY: 0.70,     # Textbooks, curriculum guides, academic case studies, published literature
    TIER_4_COMMENTARY: 0.35     # Informal notes, chat transcripts, scratchpads, forum blurbs, unverified blogs
}

# Precompiled Regex Patterns for Epistemic Classification
# Uses lookaround delimiters (?<![a-zA-Z0-9]) and (?![a-zA-Z0-9]) to match across underscores, hyphens, and dots
TIER_1_REGEX = re.compile(
    r'(?<![a-zA-Z0-9])(rfc\d*|iso\d*|iec\d*|ieee\d*|sec|10-k|10-q|statute|statutory|law|uscode|cfr|ansi|merkle|nist)(?![a-zA-Z0-9])',
    re.IGNORECASE
)
STATUTORY_CITATION_REGEX = re.compile(
    r'(\b\d+\s+u\.s\.c\.|\btitle\s+\d+\s+of\s+the\s+code\b|\bpublic\s+law\s+\d+-\d+\b|\b\d+\s+cfr\s+§?\s*\d+)',
    re.IGNORECASE
)

TIER_2_REGEX = re.compile(
    r'(?<![a-zA-Z0-9])(spec|specification|specs|api|documentation|whitepaper|datasheet|protocol|architecture|manual|rfc-draft|reference|schema|rfc\s*draft)(?![a-zA-Z0-9])',
    re.IGNORECASE
)

TIER_3_REGEX = re.compile(
    r'(?<![a-zA-Z0-9])(textbook|guide|handbook|edition|accounting|management|course|journal|curriculum|syllabus|dissertation|monograph|peer-reviewed|academic)(?![a-zA-Z0-9])',
    re.IGNORECASE
)

COMMENTARY_REGEX = re.compile(
    r'(?<![a-zA-Z0-9])(scratch|notes|note|memo|chat|blog|forum|commentary|draft|temp|todo|discussion|meeting|transcript|opinion|unverified)(?![a-zA-Z0-9])',
    re.IGNORECASE
)

CODE_EXTENSIONS = (
    '.py', '.sql', '.json', '.c', '.rs', '.go', '.ts', '.proto', '.yaml',
    '.yml', '.cpp', '.h', '.hpp', '.java', '.kt', '.rb', '.sh'
)


def classify_source_epistemic_tier(
    filename: str,
    content_snippet: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> Tuple[str, float]:
    """
    Classifies the epistemic evidentiary tier and mathematical authority weight of a document source.

    Returns:
        (tier_name: str, authority_weight: float)
        where tier_name in ('TIER_1_PRIMARY', 'TIER_2_TECH_SPEC', 'TIER_3_SECONDARY', 'TIER_4_COMMENTARY')
        and weights are 1.00, 0.85, 0.70, 0.35 respectively.
    """
    # 1. Metadata override check
    if metadata:
        explicit_tier = metadata.get("epistemic_tier")
        if explicit_tier and explicit_tier in TIER_WEIGHTS:
            explicit_weight = float(metadata.get("authority_weight", metadata.get("epistemic_weight", TIER_WEIGHTS[explicit_tier])))
            return explicit_tier, explicit_weight

    fname_norm = unicodedata.normalize("NFC", filename or "").lower().replace("\\", "/")
    base_name = fname_norm.rsplit("/", 1)[-1] if "/" in fname_norm else fname_norm
    snippet_norm = unicodedata.normalize("NFC", content_snippet[:1000] if content_snippet else "").lower()

    # 2. File extension priority check for source code & formal data schemas
    if base_name.endswith(CODE_EXTENSIONS):
        # Unless filename explicitly marks it as scratch/draft/temp notes
        if not COMMENTARY_REGEX.search(base_name):
            return TIER_1_PRIMARY, TIER_WEIGHTS[TIER_1_PRIMARY]

    # 3. Filename analysis (Filename carries priority over body snippets to prevent commentary citing statutes from being elevated)
    is_filename_commentary = bool(COMMENTARY_REGEX.search(base_name))

    if TIER_1_REGEX.search(base_name) or STATUTORY_CITATION_REGEX.search(base_name):
        return TIER_1_PRIMARY, TIER_WEIGHTS[TIER_1_PRIMARY]

    if TIER_2_REGEX.search(base_name):
        return TIER_2_TECH_SPEC, TIER_WEIGHTS[TIER_2_TECH_SPEC]

    if TIER_3_REGEX.search(base_name):
        return TIER_3_SECONDARY, TIER_WEIGHTS[TIER_3_SECONDARY]

    # 4. If filename explicitly marked as commentary, do not elevate based on body citations
    if is_filename_commentary:
        return TIER_4_COMMENTARY, TIER_WEIGHTS[TIER_4_COMMENTARY]

    # 5. Content snippet analysis for non-commentary files
    if snippet_norm:
        if TIER_1_REGEX.search(snippet_norm) or STATUTORY_CITATION_REGEX.search(snippet_norm):
            return TIER_1_PRIMARY, TIER_WEIGHTS[TIER_1_PRIMARY]
        if TIER_2_REGEX.search(snippet_norm):
            return TIER_2_TECH_SPEC, TIER_WEIGHTS[TIER_2_TECH_SPEC]
        if TIER_3_REGEX.search(snippet_norm):
            return TIER_3_SECONDARY, TIER_WEIGHTS[TIER_3_SECONDARY]
        if COMMENTARY_REGEX.search(snippet_norm):
            return TIER_4_COMMENTARY, TIER_WEIGHTS[TIER_4_COMMENTARY]

    # 6. Default fallback
    return TIER_4_COMMENTARY, TIER_WEIGHTS[TIER_4_COMMENTARY]


def compute_authority_weighted_rrf(
    lexical_ranks: List[Dict[str, Any]],
    dense_ranks: List[Dict[str, Any]],
    k: int = 60,
    intent_weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Computes Reciprocal Rank Fusion (RRF) scores weighted by epistemic authority
    and temporal validity staleness coefficients:

        S_grounded(d) = W_E(d) * Phi_temporal(d) * sum_m ( omega_m * 1 / (k + r_m(d)) )

    Args:
        lexical_ranks: Ranked candidate list from lexical (FTS5 BM25) search.
        dense_ranks: Ranked candidate list from dense vector / semantic search.
        k: RRF smoothing constant (default: 60).
        intent_weights: Optional channel weights (e.g. {'lexical': 0.5, 'dense': 0.5}).

    Returns:
        Sorted list of candidate dictionaries with grounded and normalized scores.
    """
    # Normalize channel weights
    channel_weights = {"lexical": 0.5, "dense": 0.5}
    if intent_weights:
        w_lex = float(intent_weights.get("lexical", intent_weights.get("fts", 0.5)))
        w_dense = float(intent_weights.get("dense", intent_weights.get("vector", 0.5)))
        total_w = w_lex + w_dense
        if total_w > 0:
            channel_weights["lexical"] = w_lex / total_w
            channel_weights["dense"] = w_dense / total_w

    # Index candidates by unique document identifier
    doc_map: Dict[str, Dict[str, Any]] = {}

    def get_doc_key(doc: Dict[str, Any]) -> str:
        return str(doc.get("id") or doc.get("file_id") or doc.get("filepath") or doc.get("filename") or id(doc))

    # Process lexical channel
    n_lex = len(lexical_ranks)
    for idx, doc in enumerate(lexical_ranks):
        key = get_doc_key(doc)
        rank = int(doc.get("rank", idx + 1))
        if key not in doc_map:
            doc_map[key] = {"data": doc, "ranks": {}}
        doc_map[key]["ranks"]["lexical"] = rank

    # Process dense channel
    n_dense = len(dense_ranks)
    for idx, doc in enumerate(dense_ranks):
        key = get_doc_key(doc)
        rank = int(doc.get("rank", idx + 1))
        if key not in doc_map:
            doc_map[key] = {"data": doc, "ranks": {}}
        doc_map[key]["ranks"]["dense"] = rank

    results: List[Dict[str, Any]] = []

    for key, item in doc_map.items():
        doc = item["data"]
        ranks = item["ranks"]

        # If document is missing from a channel, assign (channel_len + 1) smoothing rank
        r_lex = ranks.get("lexical", n_lex + 1 if n_lex > 0 else 100)
        r_dense = ranks.get("dense", n_dense + 1 if n_dense > 0 else 100)

        # Compute raw weighted RRF
        lex_rrf = channel_weights["lexical"] / (float(k) + float(r_lex))
        dense_rrf = channel_weights["dense"] / (float(k) + float(r_dense))
        raw_rrf = lex_rrf + dense_rrf

        # Extract or compute epistemic authority weight
        filename = str(doc.get("filename") or doc.get("filepath") or "")
        content = str(doc.get("content") or doc.get("snippet") or "")
        metadata = doc.get("metadata") or {}

        if "epistemic_tier" in doc and "epistemic_weight" in doc:
            tier = doc["epistemic_tier"]
            tier_weight = float(doc["epistemic_weight"])
        else:
            tier, tier_weight = classify_source_epistemic_tier(filename, content, metadata)

        # Extract temporal validity staleness coefficient
        staleness_coeff = 1.0
        if "staleness_coefficient" in doc:
            staleness_coeff = float(doc["staleness_coefficient"])
        elif "temporal_validity" in doc and isinstance(doc["temporal_validity"], dict):
            staleness_coeff = float(doc["temporal_validity"].get("staleness_coefficient", 1.0))

        # Grounded RRF score
        grounded_score = raw_rrf * tier_weight * staleness_coeff
        # Normalized score relative to theoretical maximum single-item score (k + 1)
        normalized_score = min(1.0, max(0.0, grounded_score * (float(k) + 1.0)))

        merged_record = {
            **doc,
            "id": doc.get("id"),
            "filename": filename,
            "filepath": doc.get("filepath", ""),
            "epistemic_tier": tier,
            "epistemic_weight": tier_weight,
            "staleness_coefficient": staleness_coeff,
            "channel_ranks": {"lexical": r_lex, "dense": r_dense},
            "raw_rrf_score": round(raw_rrf, 6),
            "grounded_score": round(grounded_score, 6),
            "normalized_score": round(normalized_score, 4)
        }
        results.append(merged_record)

    # Sort descending by grounded score
    results.sort(key=lambda x: (x["grounded_score"], x["raw_rrf_score"]), reverse=True)

    # Attach final rank
    for rank_idx, record in enumerate(results):
        record["final_rank"] = rank_idx + 1

    return results
