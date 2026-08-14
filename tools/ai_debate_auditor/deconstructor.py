"""
Argument Deconstructor (R1) for Adversarial AI Debate Auditor.
Sentence & proposition segmentation, claim classification, sycophancy echo detection,
leading prompt presupposition extraction, and bare assertion isolation.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple, Set
from .models import Claim, ClaimCategory, PatternSeverity


# Common abbreviations that should NOT trigger sentence splitting
ABBREVIATIONS = {
    "dr.", "mr.", "mrs.", "ms.", "prof.", "sr.", "jr.", "vs.", "etc.", "e.g.", "i.e.",
    "fig.", "vol.", "no.", "al.", "inc.", "ltd.", "co.", "corp.", "dept.", "u.s.",
    "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sep.", "oct.", "nov.", "dec."
}

# Linguistic category markers
RE_DEDUCTIVE = re.compile(
    r"\b(therefore|thus|hence|consequently|implies|proves|follows that|as a result|by definition|deduces|must replace|must conclude)\b",
    re.IGNORECASE
)
RE_CAUSAL = re.compile(
    r"\b(causes|caused|causing|drives|leads to|results in|produces|transfers|generates|impacts|triggers|provokes|because)\b",
    re.IGNORECASE
)
RE_PHYSICAL = re.compile(
    r"\b(energy|joules?|watts?|efficiency|carnot|thermodynamics?|entropy|speed of light|temperature|kelvin|"
    r"celsius|velocity|momentum|mass|conservation|friction|heat|quantum|power|voltage|amperes?|"
    r"fusion|magnetic|electricity|superconductor|motion|relativity|gravity)\b",
    re.IGNORECASE
)
RE_EMPIRICAL = re.compile(
    r"(\b\d+(\.\d+)?%|\b\d+\s*(?:kg|meters?|seconds?|ms|mw|kw|watts?|joules?|k|v|hz|ghz|tb|gb|mb)\b|\b\d{4}\b|\bstudy\b|\bexperiment\b|\bmeasured\b|\bobserved\b|\bdataset\b|\bdatabase\b|\bb-tree\b|\bindex(?:es)?\b|\bstorage\b|\btechnology\b|\butilizes\b|\bstructures?\b|\bservers?\b|\bhardware\b|\bqueries\b|\bquerying\b|\brelational\b|\bsqlite\b|\bwal\b|\bconcurrency\b|\bmulti-reader\b|\breader\b|\bwriter\b|\bformat\b|\bprotocol\b)",
    re.IGNORECASE
)
RE_EMPIRICAL_DATA = re.compile(
    r"(\b\d+(\.\d+)?%|\b\d+\s*(?:kg|meters?|seconds?|ms|mw|kw|watts?|joules?|k|v|hz|ghz|tb|gb|mb)\b|\bstudy\b|\bexperiment\b|\bmeasured\b|\bobserved\b|\bdataset\b)",
    re.IGNORECASE
)
RE_NORMATIVE = re.compile(
    r"\b(should|ought to|mandatory|imperative|prohibit|ban|require|essential|necessary)\b",
    re.IGNORECASE
)

RE_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", re.UNICODE)


def normalize_text(text: str) -> str:
    """Normalize unicode NFC, strip null bytes and ANSI escape sequences, clean consecutive spaces."""
    if not text:
        return ""
    # Strip null bytes and control chars
    clean = text.replace("\x00", "")
    # Strip ANSI escape codes
    clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", clean)
    normalized = unicodedata.normalize("NFC", clean)
    return re.sub(r"[ \t]+", " ", normalized).strip()


def split_sentences(text: str) -> List[str]:
    """
    High-performance, high-precision sentence splitting handling scholarly and technical abbreviations.
    """
    if not text or not text.strip():
        return []
    
    clean = normalize_text(text)
    paragraphs = [p.strip() for p in clean.split("\n") if p.strip()]
    sentences: List[str] = []
    
    for para in paragraphs:
        raw_splits = RE_SENTENCE_BOUNDARY.split(para)
        current = ""
        for part in raw_splits:
            if not part:
                continue
            if current:
                current = current + " " + part
            else:
                current = part
                
            words = current.split()
            if words:
                last_word = words[-1].lower()
                if last_word in ABBREVIATIONS or (len(words[-1]) <= 2 and words[-1].endswith(".")):
                    continue
            
            trimmed = current.strip()
            if trimmed and len(trimmed) > 3:
                sentences.append(trimmed)
            current = ""
            
        if current.strip() and len(current.strip()) > 3:
            sentences.append(current.strip())
            
    return sentences


def classify_claim_category(sentence: str) -> ClaimCategory:
    """Classify the primary epistemological category of a claim sentence."""
    if RE_DEDUCTIVE.search(sentence):
        return ClaimCategory.DEDUCTIVE_LOGICAL
    elif RE_CAUSAL.search(sentence):
        return ClaimCategory.CAUSAL_MECHANISM
    elif RE_PHYSICAL.search(sentence):
        return ClaimCategory.PHYSICAL_SCIENTIFIC
    elif RE_EMPIRICAL.search(sentence):
        return ClaimCategory.EMPIRICAL_FACT
    elif RE_NORMATIVE.search(sentence):
        return ClaimCategory.NORMATIVE_POLICY
    else:
        return ClaimCategory.UNCLASSIFIED


def extract_presuppositions(prompt_text: str) -> List[str]:
    """
    Extract loaded presuppositions and leading premises from a user prompt.
    E.g. 'Given that X is flawed, why do people use it?' -> 'X is flawed'
    """
    if not prompt_text:
        return []
    
    presuppositions = []
    norm = normalize_text(prompt_text)
    
    patterns = [
        re.compile(r"\b(?:given that|since|because)\s+([^,?.!]+)", re.IGNORECASE),
        re.compile(r"\bwhy (?:is|are|does|do)\s+([^,?.!]+)\s+(?:so|inherently|obviously|fatally)", re.IGNORECASE),
        re.compile(r"\bdon't you agree that\s+([^,?.!]+)", re.IGNORECASE),
        re.compile(r"\bisn't it (?:true|obvious|clear) that\s+([^,?.!]+)", re.IGNORECASE),
        re.compile(r"\bproves that\s+([^,?.!]+)", re.IGNORECASE),
    ]
    
    for pat in patterns:
        for m in pat.finditer(norm):
            extracted = m.group(1).strip()
            if len(extracted) > 5:
                presuppositions.append(extracted)
                
    # If no specific regex matched but prompt is short and assertive
    if not presuppositions and len(norm.split()) < 25 and "?" in norm:
        # Strip question wrapper
        clean_q = re.sub(r"^(why|how|don't you agree that|isn't it true that)\s+", "", norm, flags=re.IGNORECASE)
        clean_q = clean_q.rstrip("?").strip()
        if len(clean_q) > 8:
            presuppositions.append(clean_q)
            
    return presuppositions


def compute_word_overlap(s1: str, s2: str) -> float:
    """Compute Jaccard token overlap between two strings."""
    stop_words = {"the", "a", "an", "and", "or", "is", "are", "was", "were", "of", "to", "in", "that", "this", "it", "for", "with", "on", "as"}
    tokens1 = set(re.findall(r"\b[a-zA-Z]{3,}\b", s1.lower())) - stop_words
    tokens2 = set(re.findall(r"\b[a-zA-Z]{3,}\b", s2.lower())) - stop_words
    
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1 & tokens2) / len(tokens1 | tokens2)


def is_bare_unsubstantiated_assertion(sentence: str, category: ClaimCategory) -> bool:
    """
    Check if a claim makes a strong factual/scientific/causal claim with zero citations, numbers, or deductive reasoning.
    """
    has_metrics = bool(RE_EMPIRICAL_DATA.search(sentence))
    has_citation = bool(re.search(r"(\b10\.\d{4,}/|\barxiv:|\bpmid:|et al\.|\(\d{4}\))", sentence, re.IGNORECASE))
    has_deductive_proof = bool(RE_DEDUCTIVE.search(sentence))
    
    # If it is physical, causal, empirical, or unclassified assertion but contains zero data/metrics/citations/proofs
    if category in (ClaimCategory.PHYSICAL_SCIENTIFIC, ClaimCategory.CAUSAL_MECHANISM, ClaimCategory.EMPIRICAL_FACT, ClaimCategory.UNCLASSIFIED):
        if not has_metrics and not has_citation and not has_deductive_proof:
            return True
            
    return False


def deconstruct_argument(text: str, prompt_context: Optional[str] = None) -> List[Claim]:
    """
    Main R1 deconstruction pipeline. Segments text into structured atomic claims,
    extracts presuppositions, tags categories, and isolates unsubstantiated assertions.
    """
    if not text or not text.strip():
        return []
        
    sentences = split_sentences(text)
    presuppositions = extract_presuppositions(prompt_context) if prompt_context else []
    
    claims: List[Claim] = []
    
    for idx, sentence in enumerate(sentences):
        claim_id = f"CLM-{idx+1:03d}"
        category = classify_claim_category(sentence)
        
        # Check presupposition echo
        echo_found = False
        if presuppositions:
            for prep in presuppositions:
                overlap = compute_word_overlap(prep, sentence)
                if overlap >= 0.25 or prep.lower() in sentence.lower():
                    echo_found = True
                    break
                    
        # Check unsubstantiated assertion
        unsubstantiated = is_bare_unsubstantiated_assertion(sentence, category)
        
        # Extract quantifiers in sentence
        quantifiers = re.findall(
            r"\b(always|never|every|all|impossible|guaranteed|undeniably|invariably|universally|zero|100%)\b",
            sentence,
            re.IGNORECASE
        )
        
        # Extract named entities / capitalized terms
        entities = re.findall(r"\b[A-Z][a-zA-Z0-9_-]+(?:\s+[A-Z][a-zA-Z0-9_-]+)*\b", sentence)
        
        claims.append(
            Claim(
                id=claim_id,
                text=sentence,
                category=category,
                confidence=1.0,
                unsubstantiated=unsubstantiated,
                source_sentence=sentence,
                presupposition_echo=echo_found,
                line_number=idx + 1,
                quantifiers=[q.lower() for q in quantifiers],
                entities=entities,
            )
        )
        
    return claims
