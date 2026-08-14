"""
Cross-Document Consensus & Contradiction Resolution Matrix Engine (Milestone M3 / Feature F6).
Zero-dependency, standard-library implementation for assertion extraction, pairwise NLI heuristics,
multi-source consensus confidence boosting, and 4-tier contradiction resolution hierarchy.
"""

import re
import math
import unicodedata
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple, Set, Union

from src.domain.epistemic_tiering import (
    classify_source_epistemic_tier,
    TIER_WEIGHTS,
    TIER_1_PRIMARY,
    TIER_2_TECH_SPEC,
    TIER_3_SECONDARY,
    TIER_4_COMMENTARY
)
from src.domain.temporal_validity import detect_temporal_validity

# --- Consensus Level Constants ---
HIGH_CONSENSUS = "HIGH_CONSENSUS"
MODERATE_CONSENSUS = "MODERATE_CONSENSUS"
NEUTRAL = "NEUTRAL"
SINGLE_SOURCE = "SINGLE_SOURCE"
MINOR_DISCREPANCY = "MINOR_DISCREPANCY"
CONTRADICTION_DETECTED = "CONTRADICTION_DETECTED"
CONTRADICTION_UNRESOLVED = "CONTRADICTION_UNRESOLVED"

# --- Pairwise NLI Relation Constants ---
NLI_ENTAILMENT = "ENTAILMENT"
NLI_CONTRADICTION = "CONTRADICTION"
NLI_NEUTRAL = "NEUTRAL"

# --- Contradiction Types ---
CONFLICT_NUMERICAL_DISCREPANCY = "NUMERICAL_DISCREPANCY"
CONFLICT_POLARITY_INVERSION = "POLARITY_INVERSION"
CONFLICT_STATUS_COLLISION = "STATUS_COLLISION"

# --- Resolution Hierarchy Tiers ---
TIER_1_EPISTEMIC_DOMINANCE = "EPISTEMIC_AUTHORITY_DOMINANCE"
TIER_2_TEMPORAL_DOMINANCE = "TEMPORAL_SUPERSEDING_DOMINANCE"
TIER_3_CONDITION_SCOPE = "CONDITION_SCOPE_SPECIFICITY"
TIER_4_UNRESOLVABLE = "UNRESOLVABLE_EPISTEMIC_CONFLICT"

# Default Boosting Constant
CONSENSUS_GAMMA = 0.15

# Common Stop Words for Context Extraction
STOP_WORDS: Set[str] = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "out", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "nor", "only", "own", "same", "so",
    "than", "too", "very", "can", "will", "just", "should", "now",
    "it", "its", "this", "that", "these", "those", "and", "or", "but", "if",
    "as", "of", "per", "each", "every", "all", "our", "their", "your"
}

# Polarity & Negation Markers
NEGATION_MARKERS: Set[str] = {
    "not", "never", "no", "none", "deprecated", "disabled", "unsupported",
    "forbidden", "prohibited", "disallowed", "cannot", "can't", "won't",
    "will not", "is not", "are not", "without", "incompatible", "removed"
}

AFFIRMATIVE_MARKERS: Set[str] = {
    "supported", "enabled", "allowed", "permitted", "active", "compatible",
    "mandatory", "required", "recommended", "valid", "must", "always", "stable"
}

# Status Keyword Map
STATUS_KEYWORDS: Dict[str, str] = {
    "active": "ACTIVE",
    "stable": "STABLE",
    "production": "PRODUCTION",
    "recommended": "RECOMMENDED",
    "current": "CURRENT",
    "deprecated": "DEPRECATED",
    "superseded": "SUPERSEDED",
    "obsolete": "OBSOLETE",
    "disabled": "DISABLED",
    "forbidden": "FORBIDDEN",
    "prohibited": "PROHIBITED",
    "unsupported": "UNSUPPORTED",
    "experimental": "EXPERIMENTAL",
    "draft": "DRAFT",
    "beta": "BETA",
    "alpha": "ALPHA"
}

# Numerical Assertion Regex Pattern
NUMERICAL_REGEX = re.compile(
    r'(?:(\$|€|£|¥)\s*)?(\b\d+(?:,\d{3})*(?:\.\d+)?)\s*(%|pct|percent|mb|mib|gb|gib|kb|kib|tb|tib|pb|pib|ms|s|sec|secs|seconds|min|mins|minutes|hr|hrs|hours|hz|khz|mhz|ghz|thz|tps|rps|qps|req/s|ops/s|msg/s|bps|kbps|mbps|gbps|usd|eur|gbp|users|nodes|instances|replicas|shards|clusters|cores|threads|connections|retries|hops|bits|bytes|records|files)?(?!\w)',
    re.IGNORECASE
)

# Entity-Attribute-Predicate Copula Pattern
PREDICATE_REGEX = re.compile(
    r'\b(?:the\s+)?([a-zA-Z0-9_\s-]{2,40}?)\s+(is|are|was|were|indicates|means|uses|requires|equals|returns|sets|specifies)\s+([a-zA-Z0-9_\s\-/]{2,50})\b',
    re.IGNORECASE
)

# Condition Scope Patterns
CONDITION_SCOPE_PATTERNS = [
    # Numerical load/throughput thresholds (e.g. load < 50, concurrency >= 100)
    re.compile(r'\b(?:under|when|where|if|for)\s+(?:load|throughput|concurrency|traffic|requests?)\s*(<=|>=|<|>|=|less than|greater than|exceeds|below|above)\s*(\d+(?:\.\d+)?(?:\s*[a-zA-Z%]+)?)\b', re.IGNORECASE),
    # Qualitative load levels (e.g. under high load, at peak traffic)
    re.compile(r'\b(?:under|at|during)\s+(high|low|normal|peak|idle|heavy|light)\s+(?:load|traffic|concurrency|usage)\b', re.IGNORECASE),
    # Environmental / mode scopes (e.g. in development mode, on Linux)
    re.compile(r'\b(?:in|for|under|on)\s+(production|development|testing|staging|debug|release|linux|windows|macos|darwin|arm64|x86_64|docker|kubernetes|standalone|cluster)\s*(?:mode|environment|os|platform)?\b', re.IGNORECASE),
    # Operational switches (e.g. with caching enabled, without compression)
    re.compile(r'\b(with|without)\s+([a-zA-Z_-]+)\s*(?:enabled|disabled|on|off)?\b', re.IGNORECASE),
    # Workload types (e.g. for read operations, for write workloads)
    re.compile(r'\b(?:for|during)\s+(read|write|read-only|write-only|batch|streaming|oltp|olap)\s*(?:operations|workloads|queries|traffic)?\b', re.IGNORECASE)
]


def _normalize_unit(raw_unit: Optional[str], currency_symbol: Optional[str] = None) -> str:
    """Normalizes raw unit and currency strings into canonical uppercase abbreviations."""
    if currency_symbol:
        sym_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY"}
        return sym_map.get(currency_symbol, "CURRENCY")

    if not raw_unit:
        return "SCALAR"

    u = raw_unit.lower().strip()
    if u in ("%", "pct", "percent"):
        return "%"
    if u in ("mb", "mib"):
        return "MB"
    if u in ("gb", "gib"):
        return "GB"
    if u in ("kb", "kib"):
        return "KB"
    if u in ("tb", "tib"):
        return "TB"
    if u in ("pb", "pib"):
        return "PB"
    if u in ("ms", "milliseconds"):
        return "MS"
    if u in ("s", "sec", "secs", "seconds"):
        return "S"
    if u in ("min", "mins", "minutes"):
        return "MIN"
    if u in ("hr", "hrs", "hours"):
        return "HR"
    if u in ("hz", "khz", "mhz", "ghz", "thz"):
        return u.upper()
    if u in ("tps", "rps", "qps", "req/s", "ops/s", "msg/s"):
        return "TPS" if u == "tps" else u.upper()
    if u in ("bps", "kbps", "mbps", "gbps"):
        return u.upper()
    if u in ("usd", "eur", "gbp"):
        return u.upper()
    if u in ("users", "nodes", "instances", "replicas", "shards", "clusters", "cores", "threads", "connections", "retries", "hops", "bits", "bytes", "records", "files"):
        return u.upper()

    return u.upper()


def _extract_condition_scopes(text: str) -> List[Dict[str, str]]:
    """Extracts qualitative and quantitative condition scopes qualifying claims in a text."""
    scopes = []
    for pattern in CONDITION_SCOPE_PATTERNS:
        for match in pattern.finditer(text):
            full_match = match.group(0).strip()
            scopes.append({
                "raw_scope": full_match,
                "scope_key": " ".join(re.findall(r'\b[a-zA-Z0-9<>=%_.-]+\b', full_match.lower()))
            })
    return scopes


def extract_document_assertions(
    content: str,
    filename: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extracts structured numerical, polarity, status, predicate, and condition assertions from a document passage.
    Zero-dependency, stdlib-first implementation.
    """
    text = unicodedata.normalize("NFC", content or "")
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    numerical_assertions = []
    polarity_assertions = []
    status_assertions = []
    predicate_assertions = []

    # Overall topic tokens from entire passage
    words = re.findall(r'\b[a-zA-Z0-9_]{3,}\b', text.lower())
    topic_tokens = set(w for w in words if w not in STOP_WORDS)

    for sentence in sentences:
        s_lower = sentence.lower()
        s_scopes = _extract_condition_scopes(sentence)
        s_scope_str = " | ".join(sc["raw_scope"] for sc in s_scopes) if s_scopes else "UNCONDITIONAL"

        # Check if number is in condition scope (e.g. load < 50)
        condition_span_texts = [sc["raw_scope"].lower() for sc in s_scopes]

        # Sentence context tokens (minus stop words)
        s_words = set(re.findall(r'\b[a-zA-Z0-9_]{3,}\b', s_lower)) - STOP_WORDS

        # 1. Numerical assertions
        for m in NUMERICAL_REGEX.finditer(sentence):
            curr_sym = m.group(1)
            raw_num = m.group(2).replace(",", "")
            raw_unit = m.group(3)
            try:
                val = float(raw_num)
            except ValueError:
                continue

            unit = _normalize_unit(raw_unit, curr_sym)
            raw_text = m.group(0).strip()

            # Check if this numerical match is inside a condition scope qualification (e.g. < 50)
            is_condition_val = any(raw_text.lower() in c_text for c_text in condition_span_texts)

            # Context terms for this specific metric
            metric_context = s_words - {raw_num.lower(), (raw_unit or "").lower(), (curr_sym or "").lower()}

            numerical_assertions.append({
                "value": val,
                "unit": unit,
                "raw_text": raw_text,
                "context_tokens": metric_context,
                "condition_scope": s_scope_str,
                "is_condition_val": is_condition_val,
                "sentence": sentence
            })

        # 2. Polarity / Negation assertions
        has_negation = any(re.search(r'\b' + re.escape(neg) + r'\b', s_lower) for neg in NEGATION_MARKERS)
        has_affirmation = any(re.search(r'\b' + re.escape(aff) + r'\b', s_lower) for aff in AFFIRMATIVE_MARKERS)

        if has_negation or has_affirmation:
            is_positive = not has_negation
            marker = "NEGATION" if has_negation else "AFFIRMATION"
            polarity_assertions.append({
                "is_positive": is_positive,
                "marker": marker,
                "subject_tokens": s_words,
                "condition_scope": s_scope_str,
                "sentence": sentence
            })

        # 3. Status assertions
        for kw, status_name in STATUS_KEYWORDS.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', s_lower):
                status_assertions.append({
                    "status": status_name,
                    "keyword": kw,
                    "entity_tokens": s_words - {kw},
                    "condition_scope": s_scope_str,
                    "sentence": sentence
                })

        # 4. Predicate Assertions (Entity-Attribute-Predicate triples)
        for pm in PREDICATE_REGEX.finditer(sentence):
            raw_subj = pm.group(1).strip()
            verb = pm.group(2).lower()
            raw_pred = pm.group(3).strip()

            subj_tokens = set(re.findall(r'\b[a-zA-Z0-9_]{2,}\b', raw_subj.lower())) - STOP_WORDS
            pred_tokens = set(re.findall(r'\b[a-zA-Z0-9_]{2,}\b', raw_pred.lower())) - STOP_WORDS
            pred_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', raw_pred))

            if len(subj_tokens) >= 1 and len(pred_tokens) >= 1:
                predicate_assertions.append({
                    "raw_subject": raw_subj,
                    "subject_tokens": subj_tokens,
                    "verb": verb,
                    "raw_predicate": raw_pred,
                    "predicate_tokens": pred_tokens,
                    "predicate_nums": pred_nums,
                    "condition_scope": s_scope_str,
                    "sentence": sentence
                })

    return {
        "filename": filename,
        "content": text,
        "topic_tokens": topic_tokens,
        "numerical_assertions": numerical_assertions,
        "polarity_assertions": polarity_assertions,
        "status_assertions": status_assertions,
        "predicate_assertions": predicate_assertions,
        "condition_scopes": _extract_condition_scopes(text)
    }


def compute_consensus_boost(
    epistemic_weights: List[float],
    agreements_count: int,
    gamma: float = CONSENSUS_GAMMA
) -> float:
    """
    Calculates multi-source consensus confidence boosting score:
        S_consensus = min(1.0, W_bar_E * (1.0 + gamma * log2(1 + N_agree)))
    """
    if not epistemic_weights:
        w_bar = 0.70
    else:
        w_bar = sum(epistemic_weights) / max(1, len(epistemic_weights))

    boost_multiplier = 1.0 + gamma * math.log2(1.0 + max(0, agreements_count))
    boosted_score = min(1.0, w_bar * boost_multiplier)
    return round(boosted_score, 4)


def resolve_contradiction_hierarchy(
    contradiction: Dict[str, Any],
    source_a_info: Dict[str, Any],
    source_b_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Applies the 4-Tier Contradiction Resolution Hierarchy:
      1. Epistemic Authority Dominance: |W_E(A) - W_E(B)| >= 0.20 -> Adopt higher tier.
      2. Temporal Superseding Dominance: Superseded / obsoleted or newer by >= 1 year -> Adopt active/newer.
      3. Condition Scope Specificity: Distinct condition scopes -> Harmonize dual-scope.
      4. Unresolvable Epistemic Conflict: Equal tier clash -> Unresolved Dissenting Ledger.
    """
    fname_a = source_a_info.get("filename", "source_a")
    fname_b = source_b_info.get("filename", "source_b")

    tier_a = source_a_info.get("epistemic_tier", TIER_3_SECONDARY)
    w_a = float(source_a_info.get("epistemic_weight", TIER_WEIGHTS.get(tier_a, 0.70)))

    tier_b = source_b_info.get("epistemic_tier", TIER_3_SECONDARY)
    w_b = float(source_b_info.get("epistemic_weight", TIER_WEIGHTS.get(tier_b, 0.70)))

    claim_a = contradiction.get("sentence_a", source_a_info.get("content", ""))
    claim_b = contradiction.get("sentence_b", source_b_info.get("content", ""))
    conflict_type = contradiction.get("conflict_type", CONFLICT_NUMERICAL_DISCREPANCY)

    # --- Tier 1: Epistemic Authority Dominance (|W_E(A) - W_E(B)| >= 0.20) ---
    delta_w = abs(w_a - w_b)
    if delta_w >= 0.20 - 1e-6:
        if w_a > w_b:
            winner_src, winner_tier, winner_w, winner_claim = fname_a, tier_a, w_a, claim_a
            loser_src, loser_tier, loser_w, loser_claim = fname_b, tier_b, w_b, claim_b
        else:
            winner_src, winner_tier, winner_w, winner_claim = fname_b, tier_b, w_b, claim_b
            loser_src, loser_tier, loser_w, loser_claim = fname_a, tier_a, w_a, claim_a

        return {
            "resolution_tier": TIER_1_EPISTEMIC_DOMINANCE,
            "status": "RESOLVED",
            "conflict_type": conflict_type,
            "resolved_source": winner_src,
            "overruled_source": loser_src,
            "adopted_claim": winner_claim,
            "rejected_claim": loser_claim,
            "authority_delta": round(delta_w, 2),
            "winning_tier": winner_tier,
            "losing_tier": loser_tier,
            "rationale": f"Adopted {winner_src} ({winner_tier}, weight {winner_w}) over {loser_src} ({loser_tier}, weight {loser_w}) due to epistemic authority margin {round(delta_w, 2)} >= 0.20."
        }

    # --- Tier 2: Temporal Superseding Dominance ---
    temp_a = source_a_info.get("temporal_validity") or detect_temporal_validity(source_a_info.get("content", ""))
    temp_b = source_b_info.get("temporal_validity") or detect_temporal_validity(source_b_info.get("content", ""))

    status_a = temp_a.get("temporal_status", "ACTIVE")
    status_b = temp_b.get("temporal_status", "ACTIVE")

    is_superseded_a = temp_a.get("is_superseded", False) or status_a in ("SUPERSEDED", "DEPRECATED")
    is_superseded_b = temp_b.get("is_superseded", False) or status_b in ("SUPERSEDED", "DEPRECATED")

    year_a = temp_a.get("publication_year")
    year_b = temp_b.get("publication_year")

    # Explicit superseding or status difference
    if is_superseded_a and not is_superseded_b:
        return {
            "resolution_tier": TIER_2_TEMPORAL_DOMINANCE,
            "status": "RESOLVED",
            "conflict_type": conflict_type,
            "resolved_source": fname_b,
            "overruled_source": fname_a,
            "adopted_claim": claim_b,
            "rejected_claim": claim_a,
            "rationale": f"Adopted active source {fname_b} over superseded/deprecated source {fname_a} ({status_a})."
        }
    elif is_superseded_b and not is_superseded_a:
        return {
            "resolution_tier": TIER_2_TEMPORAL_DOMINANCE,
            "status": "RESOLVED",
            "conflict_type": conflict_type,
            "resolved_source": fname_a,
            "overruled_source": fname_b,
            "adopted_claim": claim_a,
            "rejected_claim": claim_b,
            "rationale": f"Adopted active source {fname_a} over superseded/deprecated source {fname_b} ({status_b})."
        }

    # Year delta check (delta >= 1 year)
    if year_a and year_b and abs(year_a - year_b) >= 1:
        if year_b > year_a and not is_superseded_b:
            return {
                "resolution_tier": TIER_2_TEMPORAL_DOMINANCE,
                "status": "RESOLVED",
                "conflict_type": conflict_type,
                "resolved_source": fname_b,
                "overruled_source": fname_a,
                "adopted_claim": claim_b,
                "rejected_claim": claim_a,
                "publication_year_winner": year_b,
                "publication_year_loser": year_a,
                "rationale": f"Adopted newer source {fname_b} ({year_b}) over older source {fname_a} ({year_a})."
            }
        elif year_a > year_b and not is_superseded_a:
            return {
                "resolution_tier": TIER_2_TEMPORAL_DOMINANCE,
                "status": "RESOLVED",
                "conflict_type": conflict_type,
                "resolved_source": fname_a,
                "overruled_source": fname_b,
                "adopted_claim": claim_a,
                "rejected_claim": claim_b,
                "publication_year_winner": year_a,
                "publication_year_loser": year_b,
                "rationale": f"Adopted newer source {fname_a} ({year_a}) over older source {fname_b} ({year_b})."
            }

    # --- Tier 3: Condition Scope Specificity ---
    scope_a = contradiction.get("scope_a", "UNCONDITIONAL")
    scope_b = contradiction.get("scope_b", "UNCONDITIONAL")

    if scope_a != "UNCONDITIONAL" and scope_b != "UNCONDITIONAL" and scope_a.lower() != scope_b.lower():
        return {
            "resolution_tier": TIER_3_CONDITION_SCOPE,
            "status": "HARMONIZED_DUAL_SCOPE",
            "conflict_type": conflict_type,
            "harmonized_scopes": [
                {"source": fname_a, "scope": scope_a, "claim": claim_a},
                {"source": fname_b, "scope": scope_b, "claim": claim_b}
            ],
            "rationale": f"Harmonized dual-scope claims across distinct operating conditions: '{scope_a}' vs '{scope_b}'."
        }

    # --- Tier 4: Unresolvable Epistemic Conflict ---
    raw_hash = abs(hash(f"{fname_a}_{fname_b}_{conflict_type}_{claim_a[:30]}")) % 1000000
    conflict_id = f"dissent_{raw_hash:06d}"
    return {
        "conflict_id": conflict_id,
        "resolution_tier": TIER_4_UNRESOLVABLE,
        "status": "UNRESOLVED_EPISTEMIC_CONFLICT",
        "conflict_type": conflict_type,
        "source_a": fname_a,
        "source_b": fname_b,
        "tier_a": tier_a,
        "weight_a": w_a,
        "tier_b": tier_b,
        "weight_b": w_b,
        "claim_a": claim_a,
        "claim_b": claim_b,
        "recommended_action": "Manual expert arbitration required due to conflicting factual claims from equal-authority sources without temporal or conditional differentiation."
    }


def evaluate_cross_document_consensus(passages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates cross-document consensus, calculates confidence boost, detects factual contradictions,
    and executes the 4-Tier Contradiction Resolution Hierarchy.
    """
    if not passages or len(passages) < 2:
        return {
            "consensus_level": SINGLE_SOURCE,
            "consensus_score": 0.70,
            "agreements_count": 0,
            "contradictions_count": 0,
            "contradictions": [],
            "resolved_claims": [],
            "dissenting_ledger": [],
            "pairwise_nli": [],
            "assertion_count": 0
        }

    # 1. Parse all documents and extract assertions, epistemic tiers, and temporal metadata
    doc_profiles = []
    total_assertions = 0

    for p in passages:
        content = p.get("content", "")
        filename = p.get("filename", "unknown")
        meta = p.get("metadata", {})

        tier_name, tier_weight = classify_source_epistemic_tier(filename, content, meta)
        temp_info = detect_temporal_validity(content, metadata=meta)

        assertions = extract_document_assertions(content, filename, meta)
        total_assertions += (
            len(assertions["numerical_assertions"]) +
            len(assertions["polarity_assertions"]) +
            len(assertions["status_assertions"]) +
            len(assertions["predicate_assertions"])
        )

        doc_profiles.append({
            "filename": filename,
            "content": content,
            "epistemic_tier": tier_name,
            "epistemic_weight": tier_weight,
            "temporal_validity": temp_info,
            "assertions": assertions,
            "topic_tokens": assertions["topic_tokens"]
        })

    agreements_count = 0
    contradictions = []
    pairwise_nli_records = []

    # 2. Pairwise NLI Comparison
    for i in range(len(doc_profiles)):
        for j in range(i + 1, len(doc_profiles)):
            doc_a = doc_profiles[i]
            doc_b = doc_profiles[j]

            ast_a = doc_a["assertions"]
            ast_b = doc_b["assertions"]

            pair_contradictions_map = {}
            pair_agreements = 0

            # A. Numerical Assertion Comparisons
            matched_b_nums = set()
            for num_a in ast_a["numerical_assertions"]:
                for idx_b, num_b in enumerate(ast_b["numerical_assertions"]):
                    if idx_b in matched_b_nums:
                        continue

                    # Condition threshold numbers (e.g. load < 50) don't count as metric agreements
                    if num_a.get("is_condition_val") or num_b.get("is_condition_val"):
                        continue

                    # Check unit compatibility
                    unit_match = (num_a["unit"] == num_b["unit"]) or (num_a["unit"] == "SCALAR" and num_b["unit"] == "SCALAR")
                    if not unit_match and num_a["unit"] != "SCALAR" and num_b["unit"] != "SCALAR":
                        continue

                    # Check context token overlap
                    shared_ctx = num_a["context_tokens"].intersection(num_b["context_tokens"])
                    is_same_metric = (
                        len(shared_ctx) >= 1 or
                        (unit_match and num_a["unit"] in ("MB", "GB", "KB", "TB", "TPS", "RPS", "QPS", "MS", "S", "MIN", "HR", "HZ", "MHZ", "GHZ", "USD", "EUR", "GBP", "NODES", "USERS", "CORES", "BYTES", "BITS"))
                    )

                    if is_same_metric:
                        matched_b_nums.add(idx_b)
                        val_diff = abs(num_a["value"] - num_b["value"])

                        if val_diff < 1e-5:
                            pair_agreements += 1
                        else:
                            scope_a = num_a["condition_scope"]
                            scope_b = num_b["condition_scope"]
                            c_key = (num_a["sentence"], num_b["sentence"])

                            pair_contradictions_map[c_key] = {
                                "conflict_type": CONFLICT_NUMERICAL_DISCREPANCY,
                                "source_a": doc_a["filename"],
                                "source_b": doc_b["filename"],
                                "unit": num_a["unit"],
                                "value_a": num_a["value"],
                                "value_b": num_b["value"],
                                "raw_a": num_a["raw_text"],
                                "raw_b": num_b["raw_text"],
                                "values_a": [num_a["raw_text"]],
                                "values_b": [num_b["raw_text"]],
                                "scope_a": scope_a,
                                "scope_b": scope_b,
                                "sentence_a": num_a["sentence"],
                                "sentence_b": num_b["sentence"],
                                "context": list(shared_ctx)
                            }

            # B. Predicate Assertion Comparisons (Entity-Attribute-Predicate)
            matched_b_preds = set()
            for pred_a in ast_a["predicate_assertions"]:
                for idx_b, pred_b in enumerate(ast_b["predicate_assertions"]):
                    if idx_b in matched_b_preds:
                        continue

                    shared_subj = pred_a["subject_tokens"].intersection(pred_b["subject_tokens"])
                    subj_match = (
                        len(shared_subj) >= 2 or
                        (len(shared_subj) >= 1 and len(pred_a["subject_tokens"]) <= 2 and len(pred_b["subject_tokens"]) <= 2)
                    )

                    if subj_match:
                        matched_b_preds.add(idx_b)
                        # Check if numbers inside predicates clash
                        if pred_a["predicate_nums"] and pred_b["predicate_nums"]:
                            if pred_a["predicate_nums"] != pred_b["predicate_nums"]:
                                c_key = (pred_a["sentence"], pred_b["sentence"])
                                if c_key not in pair_contradictions_map:
                                    pair_contradictions_map[c_key] = {
                                        "conflict_type": CONFLICT_POLARITY_INVERSION,
                                        "source_a": doc_a["filename"],
                                        "source_b": doc_b["filename"],
                                        "polarity_a": pred_a["raw_predicate"],
                                        "polarity_b": pred_b["raw_predicate"],
                                        "scope_a": pred_a["condition_scope"],
                                        "scope_b": pred_b["condition_scope"],
                                        "sentence_a": pred_a["sentence"],
                                        "sentence_b": pred_b["sentence"],
                                        "subject": list(shared_subj)
                                    }
                                continue

                        shared_pred_val = pred_a["predicate_tokens"].intersection(pred_b["predicate_tokens"])
                        if len(shared_pred_val) >= 1 and len(shared_pred_val) >= max(len(pred_a["predicate_tokens"]), len(pred_b["predicate_tokens"])) // 2:
                            pair_agreements += 1
                        else:
                            c_key = (pred_a["sentence"], pred_b["sentence"])
                            if c_key not in pair_contradictions_map:
                                pair_contradictions_map[c_key] = {
                                    "conflict_type": CONFLICT_POLARITY_INVERSION,
                                    "source_a": doc_a["filename"],
                                    "source_b": doc_b["filename"],
                                    "polarity_a": pred_a["raw_predicate"],
                                    "polarity_b": pred_b["raw_predicate"],
                                    "scope_a": pred_a["condition_scope"],
                                    "scope_b": pred_b["condition_scope"],
                                    "sentence_a": pred_a["sentence"],
                                    "sentence_b": pred_b["sentence"],
                                    "subject": list(shared_subj)
                                }

            # C. Polarity Assertion Comparisons
            matched_b_pols = set()
            for pol_a in ast_a["polarity_assertions"]:
                for idx_b, pol_b in enumerate(ast_b["polarity_assertions"]):
                    if idx_b in matched_b_pols:
                        continue

                    shared_sub = pol_a["subject_tokens"].intersection(pol_b["subject_tokens"])
                    if len(shared_sub) >= 2 or (len(shared_sub) >= 1 and len(pol_a["subject_tokens"]) <= 2):
                        matched_b_pols.add(idx_b)
                        if pol_a["is_positive"] == pol_b["is_positive"]:
                            pair_agreements += 1
                        else:
                            c_key = (pol_a["sentence"], pol_b["sentence"])
                            if c_key not in pair_contradictions_map:
                                pair_contradictions_map[c_key] = {
                                    "conflict_type": CONFLICT_POLARITY_INVERSION,
                                    "source_a": doc_a["filename"],
                                    "source_b": doc_b["filename"],
                                    "polarity_a": "AFFIRMATIVE" if pol_a["is_positive"] else "NEGATIVE",
                                    "polarity_b": "AFFIRMATIVE" if pol_b["is_positive"] else "NEGATIVE",
                                    "scope_a": pol_a["condition_scope"],
                                    "scope_b": pol_b["condition_scope"],
                                    "sentence_a": pol_a["sentence"],
                                    "sentence_b": pol_b["sentence"],
                                    "subject": list(shared_sub)
                                }

            # D. Status Assertion Comparisons
            matched_b_stats = set()
            for stat_a in ast_a["status_assertions"]:
                for idx_b, stat_b in enumerate(ast_b["status_assertions"]):
                    if idx_b in matched_b_stats:
                        continue

                    shared_ent = stat_a["entity_tokens"].intersection(stat_b["entity_tokens"])
                    if len(shared_ent) >= 1:
                        matched_b_stats.add(idx_b)
                        if stat_a["status"] == stat_b["status"]:
                            pair_agreements += 1
                        else:
                            c_key = (stat_a["sentence"], stat_b["sentence"])
                            pair_contradictions_map[c_key] = {
                                "conflict_type": CONFLICT_STATUS_COLLISION,
                                "source_a": doc_a["filename"],
                                "source_b": doc_b["filename"],
                                "status_a": stat_a["status"],
                                "status_b": stat_b["status"],
                                "scope_a": stat_a["condition_scope"],
                                "scope_b": stat_b["condition_scope"],
                                "sentence_a": stat_a["sentence"],
                                "sentence_b": stat_b["sentence"],
                                "entity": list(shared_ent)
                            }

            # E. Fallback: High lexical topic overlap agreement if no assertions collided
            pair_contradictions = list(pair_contradictions_map.values())
            if pair_agreements == 0 and not pair_contradictions:
                shared_topics = doc_a["topic_tokens"].intersection(doc_b["topic_tokens"])
                if len(shared_topics) >= 4:
                    pair_agreements += 1

            agreements_count += pair_agreements
            contradictions.extend(pair_contradictions)

            # Record Pairwise NLI evaluation
            if pair_contradictions:
                nli_rel = NLI_CONTRADICTION
            elif pair_agreements > 0:
                nli_rel = NLI_ENTAILMENT
            else:
                nli_rel = NLI_NEUTRAL

            pairwise_nli_records.append({
                "doc_a": doc_a["filename"],
                "doc_b": doc_b["filename"],
                "relation": nli_rel,
                "agreements": pair_agreements,
                "contradictions_count": len(pair_contradictions)
            })

    # 3. Apply 4-Tier Contradiction Resolution Hierarchy
    doc_map = {d["filename"]: d for d in doc_profiles}
    resolved_claims = []
    dissenting_ledger = []

    for c in contradictions:
        src_a_info = doc_map.get(c["source_a"], {"filename": c["source_a"], "content": c.get("sentence_a", "")})
        src_b_info = doc_map.get(c["source_b"], {"filename": c["source_b"], "content": c.get("sentence_b", "")})

        res = resolve_contradiction_hierarchy(c, src_a_info, src_b_info)
        if res.get("status") in ("RESOLVED", "HARMONIZED_DUAL_SCOPE"):
            resolved_claims.append(res)
        else:
            dissenting_ledger.append(res)

    # 4. Consensus Confidence Boosting & Consensus Level Assignment
    all_weights = [d["epistemic_weight"] for d in doc_profiles]
    boost_score = compute_consensus_boost(all_weights, agreements_count, gamma=CONSENSUS_GAMMA)

    # Majority consensus determination across multi-party sources
    has_majority_agreement = (
        agreements_count >= 1 and (
            (len(doc_profiles) > 2 and (agreements_count >= len(contradictions) or agreements_count >= len(doc_profiles) // 2)) or
            (len(doc_profiles) == 2 and agreements_count >= len(contradictions) and len(dissenting_ledger) == 0 and not any(r.get("resolution_tier") == TIER_3_CONDITION_SCOPE for r in resolved_claims))
        )
    )

    if has_majority_agreement:
        consensus_level = HIGH_CONSENSUS
        consensus_score = 1.00 if (boost_score >= 0.99 and agreements_count >= 3) else 0.95
    elif contradictions:
        all_harmonized = all(r.get("resolution_tier") == TIER_3_CONDITION_SCOPE for r in resolved_claims)
        if all_harmonized and resolved_claims:
            consensus_level = MINOR_DISCREPANCY
            consensus_score = 0.50
        elif resolved_claims and len(dissenting_ledger) == 0 and all(r.get("resolution_tier") in (TIER_1_EPISTEMIC_DOMINANCE, TIER_2_TEMPORAL_DOMINANCE) for r in resolved_claims):
            consensus_level = MODERATE_CONSENSUS
            consensus_score = 0.85
        else:
            consensus_level = CONTRADICTION_DETECTED
            consensus_score = 0.45
    elif agreements_count >= 1:
        consensus_level = HIGH_CONSENSUS
        consensus_score = 1.00 if (boost_score >= 0.99 and agreements_count >= 3) else 0.95
    else:
        consensus_level = NEUTRAL
        consensus_score = 0.70

    return {
        "consensus_level": consensus_level,
        "consensus_score": round(consensus_score, 2),
        "agreements_count": agreements_count,
        "contradictions_count": len(contradictions),
        "contradictions": contradictions,
        "resolved_claims": resolved_claims,
        "dissenting_ledger": dissenting_ledger,
        "pairwise_nli": pairwise_nli_records,
        "assertion_count": total_assertions
    }
