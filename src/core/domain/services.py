"""
Pure domain services: RAG hybrid ranking math, wikilinks parsing, tag rules, term normalization, vector engine, summarization.
Zero dependencies on SQLite connection instances or FastAPI request objects.
"""
import unicodedata
import re
import math
import logging
import hashlib
import os
from collections import Counter, defaultdict
from functools import lru_cache
from typing import List, Dict, Tuple, Any, Optional

logger = logging.getLogger(__name__)

from src.shared.regex import (
    RE_NEAR_SYNTAX,
    RE_TOKEN_SPLIT,
    RE_SIZE_OP,
    RE_FTS_CLEAN,
    RE_WIKILINKS,
)

RE_VECTOR_TOKEN = re.compile(r'\b[a-zA-Z0-9]{2,}\b')
RE_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
RE_TAKEAWAY_WORDS = re.compile(r'\b[a-z]{4,15}\b')
RE_REDOS_NESTED_QUANTIFIERS = re.compile(r'(\+|\*|\{[\d,]+\})\s*(\+|\*|\{[\d,]+\})|\([^)]*(\+|\*|\{[\d,]+\})[^)]*\)\s*(\+|\*|\{[\d,]+\})')

def reciprocal_rank_fusion(fts_results: List[Dict[str, Any]], vector_results: List[Dict[str, Any]], k: int = 60, limit: int = 10) -> List[Dict[str, Any]]:
    """RRF formula score(d) = sum(1 / (k + rank)) across ranking channels."""
    scores: Dict[str, float] = defaultdict(float)
    item_map: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(fts_results, start=1):
        key = item.get("filepath") or item.get("id") or str(item)
        scores[key] += 1.0 / (k + rank)
        if key not in item_map:
            item_map[key] = dict(item)

    for rank, item in enumerate(vector_results, start=1):
        key = item.get("filepath") or item.get("id") or str(item)
        scores[key] += 1.0 / (k + rank)
        if key not in item_map:
            item_map[key] = dict(item)

    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    fused_results = []
    for key in sorted_keys[:limit]:
        item = item_map[key]
        item["rrf_score"] = round(scores[key], 6)
        fused_results.append(item)
    return fused_results

def generate_hyde_expansion(query: str) -> str:
    """Generate hypothetical document snippet for vector query expansion."""
    try:
        from src.core.model_manager import get_fallback_llm
        from src.core.config import is_testing
        if is_testing:
            return f"{query} - hypothetical answer context"
        llm = get_fallback_llm()
        if llm:
            prompt = (
                f"Write a concise 2-sentence technical excerpt answering this question: '{query}'. "
                "Do not explain, provide only the factual excerpt."
            )
            completion = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a concise technical excerpt generator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=60,
                temperature=0.3
            )
            excerpt = completion["choices"][0]["message"]["content"].strip()
            if excerpt:
                return f"{query}\n{excerpt}"
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning("Failed to expand query with HyDE in services.py: %s", e)
    return query

def generate_key_takeaways(text: str, num_bullets: int = 3) -> List[str]:
    """Generate key takeaways from text using sentence scoring."""
    if not text or not text.strip():
        return []
    clean_text = text.strip()
    if '.' not in clean_text and '!' not in clean_text and '?' not in clean_text:
        return [f"• {clean_text}"]
    sentences = RE_SENTENCE_SPLIT.split(clean_text)
    if not sentences:
        return []
    if len(sentences) <= num_bullets:
        return [f"• {s}" for s in sentences if s.strip()]
    
    words = RE_TAKEAWAY_WORDS.findall(clean_text.lower())
    word_freq = Counter(words)
    scored_sentences = []
    for idx, s in enumerate(sentences):
        s_words = RE_TAKEAWAY_WORDS.findall(s.lower())
        score = sum(word_freq.get(w, 0) for w in s_words) / (len(s_words) or 1)
        scored_sentences.append((score, idx, s.strip()))
    
    top = sorted(scored_sentences, key=lambda x: x[0], reverse=True)[:num_bullets]
    top_sorted = sorted(top, key=lambda x: x[1])
    return [f"• {s[2]}" for s in top_sorted if s[2]]

RE_REDOS_NESTED_QUANTIFIERS = re.compile(r'(\+|\*|\{[\d,]+\})\s*\)')

@lru_cache(maxsize=512)
def _get_compiled_regex(pat: str):
    return re.compile(pat, re.IGNORECASE)

def _safe_match(pat: str, text: str) -> bool:
    if not pat or not text:
        return False
    if "(" in pat and RE_REDOS_NESTED_QUANTIFIERS.search(pat):
        return pat.lower() in text.lower()
    try:
        return bool(_get_compiled_regex(pat).search(text))
    except re.error:
        import fnmatch
        try:
            regex_pat = fnmatch.translate(pat)
            return bool(re.search(regex_pat, text, re.IGNORECASE))
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            logger.warning("Failed regex fnmatch translation for pattern %s: %s", pat, e)
            return pat.lower() in text.lower()

def extract_ai_tags(content: str, filename: str, rule_matches: Optional[List[Tuple[str, str]]] = None) -> List[str]:
    """Extract AI/rule tags from document filename and content."""
    tags: List[str] = []
    if rule_matches:
        for pat, t_tag in rule_matches:
            if _safe_match(pat, filename) or _safe_match(pat, content):
                if t_tag not in tags:
                    tags.append(t_tag)

    fallback_rules = [
        ("astrophysics", "science"),
        ("physics", "science"),
        ("quantum", "science")
    ]
    for pat, tag in fallback_rules:
        if _safe_match(pat, filename) or _safe_match(pat, content):
            if tag not in tags:
                tags.append(tag)

    try:
        from src.core.config import is_testing
        from src.core.state import get_fallback_llm
        if is_testing:
            return tags
        llm = get_fallback_llm()
        if llm:
            prompt = (
                "Analyze the following document filename and text content.\n"
                "Extract exactly 2-3 concise keyword tags that best represent the topic or domain.\n"
                "Respond ONLY with a comma-separated list of lowercase tags. Do not explain anything.\n\n"
                f"Filename: {filename}\n"
                f"Content: {content[:800]}"
            )
            completion = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": "You are a database tag extractor. Respond only with comma-separated tags."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=0.2
            )
            tags_str = completion["choices"][0]["message"]["content"]
            ai_tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
            for t in ai_tags:
                if t not in tags:
                    tags.append(t)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.warning("Failed to extract AI tags from content: %s", e)
    return tags

import json
import os

RE_INTENT_TROUBLESHOOTING = re.compile(r'\b(error|bug|issue|fail|failed|failure|fix|fixed|resolve|resolved|exception|traceback|crash|timeout|corrupt|corrupted|malformed|panic|debug)\b', re.IGNORECASE)
RE_INTENT_PRICING = re.compile(r'(\$|€|£|¥|\b(price|pricing|cost|costs|tier|tiers|plan|plans|subscription|billing|rate|fee|fees|quota|credits|discount)\b)', re.IGNORECASE)
RE_INTENT_TECH_SPEC = re.compile(r'\b(api|endpoint|endpoints|schema|schemas|interface|interfaces|spec|specification|parameter|parameters|payload|datatype|struct|typedef|signature|contract|protocol|rfc|architecture)\b', re.IGNORECASE)
RE_INTENT_PROCEDURAL = re.compile(r'\b(step|steps|how\s+to|guide|tutorial|install|installation|configure|configuration|setup|deploy|deployment|command|run|build|start|execute|migrate)\b', re.IGNORECASE)
RE_INTENT_DOUBT = re.compile(r'\b(limitation|limitations|caveat|caveats|warning|caution|trade-off|tradeoff|drawback|risk|ceiling|prohibited|forbidden|disadvantage|faq)\b', re.IGNORECASE)
RE_INTENT_CONCEPTUAL = re.compile(r'\b(overview|introduction|concept|concepts|theory|principle|principles|definition|definitions|what\s+is|background|vision|mission|philosophy)\b', re.IGNORECASE)

RE_SCOPE_FRONTEND = re.compile(r'\b(react|frontend|ui|css|html|dom|component|tailwind|layout)\b', re.IGNORECASE)
RE_SCOPE_DEVOPS = re.compile(r'\b(docker|wsl|wsl2|kubernetes|ci|deploy|deployment|server|linux|nginx)\b', re.IGNORECASE)
RE_SCOPE_BACKEND = re.compile(r'\b(fastapi|sqlite|sqlite3|python|backend|api|endpoint|database|engine|service|router)\b', re.IGNORECASE)
RE_SCOPE_SECURITY = re.compile(r'\b(soc2|security|jwt|auth|audit|merkle|acl|hashchain|compliance)\b', re.IGNORECASE)

RE_KNOWN_ENTITIES = re.compile(
    r'\b(windows|linux|macos|darwin|ubuntu|debian|wsl|wsl2|docker|docker-desktop|kubernetes|sqlite|sqlite3|fastapi|uvicorn|python|react|node|nodejs|typescript|javascript|ollama|kokoro|onnx|pytorch|cuda|tensorrt|playwright|jest|pytest|git|github|actions|soc2|iso29119|jwt|rest|graphql|fts5|rrf|bm25|hyde)\b',
    re.IGNORECASE
)

RE_TRUST_PRICING = re.compile(r'(\$|€|£|¥|\b(price|pricing|cost|costs|rate|rates|fee|fees|subscription|tier|tiers|license|licensing|budget|per-user|per-seat|billing|estimation|hidden fees?)\b)', re.IGNORECASE)
RE_TRUST_PROBLEMS = re.compile(r'\b(problem|problems|troubleshoot|failure|failures|failed|failure mode|symptom|symptoms|edge-case|bug|bugs|error|errors|crash|timeout|leak|diagnostic|diagnostics|workaround|issue|issues)\b', re.IGNORECASE)
RE_TRUST_NOT_A_FIT = re.compile(r'\b(not[- ]a[- ]fit|who should avoid|when to avoid|avoid|disqualifier|disqualifiers|anti-persona|anti-personas|limitation|limitations|system limitation|unsupported|not recommended|drawback|drawbacks|downside)\b', re.IGNORECASE)
RE_TRUST_REPAIR_REPLACE = re.compile(r'\b(repair vs replace|repair vs\. replace|replace vs repair|upgrade vs|rebuild vs|migrate vs|trade-off decision|trade-off matrix|lifecycle criteria|migration threshold|when to replace)\b', re.IGNORECASE)
RE_TRUST_ENV_CONTEXT = re.compile(r'\b(environment constraint|environment context|freezing climate|climate|temperature|hardware tier|runtime prerequisite|prerequisite|prerequisites|operating system|windows|linux|macos)\b', re.IGNORECASE)
RE_SOURCE_THIRD_PARTY = re.compile(r'\b(review|reviews|rating|ratings|case-study|case study|post-mortem|user review|customer review|feedback|community)\b', re.IGNORECASE)

def extract_chunk_attributes(chunk_text: str, doc_title: str = "", parent_headers: str = "", filepath: str = "") -> Dict[str, Any]:
    """
    Automatically extracts structured metadata attributes from chunk text and breadcrumb context:
    - intent_type: troubleshooting, pricing, technical_spec, procedural, doubt_objection, conceptual, general
    - trust_type: pricing, problems, not_a_fit, repair_vs_replace, environment_context, general
    - source_type: primary_doc, third_party_corroboration
    - entities: detected technologies, operating systems, frameworks, and system components
    - domain_scope: engineering/backend, frontend/ui, devops/infra, data/security, general
    - answer_summary: concise answer-first synthesis of the primary takeaway
    """
    combined_text = f"{doc_title} {parent_headers} {chunk_text}"
    
    # 1. Intent Classification with multi-pattern density
    intent_scores = {
        "troubleshooting": len(RE_INTENT_TROUBLESHOOTING.findall(combined_text)),
        "pricing": len(RE_INTENT_PRICING.findall(combined_text)),
        "technical_spec": len(RE_INTENT_TECH_SPEC.findall(combined_text)),
        "procedural": len(RE_INTENT_PROCEDURAL.findall(combined_text)),
        "doubt_objection": len(RE_INTENT_DOUBT.findall(combined_text)),
        "conceptual": len(RE_INTENT_CONCEPTUAL.findall(combined_text)),
    }
    
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = sorted_intents[0]
    intent_type = best_intent if best_score > 0 else "general"

    # 1B. 5-Pillar Trust Taxonomy Classification
    trust_scores = {
        "pricing": len(RE_TRUST_PRICING.findall(combined_text)),
        "problems": len(RE_TRUST_PROBLEMS.findall(combined_text)),
        "not_a_fit": len(RE_TRUST_NOT_A_FIT.findall(combined_text)),
        "repair_vs_replace": len(RE_TRUST_REPAIR_REPLACE.findall(combined_text)),
        "environment_context": len(RE_TRUST_ENV_CONTEXT.findall(combined_text)),
    }
    sorted_trust = sorted(trust_scores.items(), key=lambda x: x[1], reverse=True)
    best_trust, best_trust_score = sorted_trust[0]
    trust_type = best_trust if best_trust_score > 0 else "general"

    # 1C. Source Type Detection
    source_type = "third_party_corroboration" if (RE_SOURCE_THIRD_PARTY.search(filepath) or RE_SOURCE_THIRD_PARTY.search(combined_text)) else "primary_doc"

    # 2. Entity & Technology extraction
    raw_entities = RE_KNOWN_ENTITIES.findall(combined_text)
    entities = sorted(list(set(e.lower() for e in raw_entities)))

    # 3. Domain scope classification using token boundary regexes
    scope = "general"
    if RE_SCOPE_BACKEND.search(combined_text):
        scope = "backend_engineering"
    elif RE_SCOPE_FRONTEND.search(combined_text):
        scope = "frontend_ui"
    elif RE_SCOPE_DEVOPS.search(combined_text):
        scope = "devops_infrastructure"
    elif RE_SCOPE_SECURITY.search(combined_text):
        scope = "security_compliance"

    # 4. Answer-First synthesis / leading declaration
    clean_lines = [l.strip() for l in chunk_text.splitlines() if l.strip() and not l.strip().startswith(('#', '|', '```'))]
    answer_lead = clean_lines[0] if clean_lines else ""
    if len(answer_lead) > 200:
        answer_lead = answer_lead[:197] + "..."

    return {
        "intent_type": intent_type,
        "trust_type": trust_type,
        "source_type": source_type,
        "entities": entities,
        "entities_json": json.dumps(entities),
        "domain_scope": scope,
        "answer_lead": answer_lead,
        "attributes": {
            "intent": intent_type,
            "trust_type": trust_type,
            "source_type": source_type,
            "entities": entities,
            "scope": scope,
            "has_code": "```" in chunk_text,
            "has_table": "|" in chunk_text
        },
        "attributes_json": json.dumps({
            "intent": intent_type,
            "trust_type": trust_type,
            "source_type": source_type,
            "entities": entities,
            "scope": scope,
            "has_code": "```" in chunk_text,
            "has_table": "|" in chunk_text
        })
    }

def semantic_markdown_chunker_hierarchical(
    text: str,
    filepath: str = "",
    parent_size: int = 900,
    child_size: int = 250,
    child_overlap: int = 50
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Two-Tier Hierarchical AST Chunker:
    1. Parent Chunks: Section-level comprehensive context (code blocks, tables, and procedural steps intact).
    2. Child Chunks: High-granularity sub-chunks for precise vector embedding and BM25 indexing,
       linked via unique parent_id references.
    """
    if not text or not text.strip():
        return {"parent_chunks": [], "child_chunks": []}
    if len(text) > 10_000_000:
        text = text[:10_000_000]

    raw_lines = text.splitlines(keepends=True)
    header_stack: List[Tuple[int, str]] = []
    doc_title = os.path.splitext(os.path.basename(filepath))[0].replace("_", " ").replace("-", " ").title() if filepath else ""

    parent_sections: List[Dict[str, Any]] = []
    curr_lines: List[str] = []
    curr_size = 0
    in_code_block = False
    in_table = False
    active_breadcrumb = ""

    def flush_parent(lines_buffer: List[str], breadcrumb: str) -> Optional[Dict[str, Any]]:
        if not lines_buffer:
            return None
        raw_body = "".join(lines_buffer).strip()
        if not raw_body:
            return None

        # Generate deterministic parent_id
        parent_hash = hashlib.sha256(f"{filepath}:{len(parent_sections)}:{raw_body[:100]}".encode('utf-8')).hexdigest()[:16]
        parent_id = f"parent_{parent_hash}"
        attrs = extract_chunk_attributes(raw_body, doc_title=doc_title, parent_headers=breadcrumb, filepath=filepath)

        return {
            "id": parent_id,
            "section_header": breadcrumb or doc_title or "General",
            "content": raw_body,
            "doc_title": doc_title or "Document",
            "domain_scope": attrs["domain_scope"],
            "intent_type": attrs["intent_type"],
            "trust_type": attrs.get("trust_type", "general"),
            "source_type": attrs.get("source_type", "primary_doc"),
            "entities": attrs["entities"],
            "entities_json": attrs["entities_json"],
            "attributes_json": attrs["attributes_json"]
        }

    for line in raw_lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block

        is_table_row = stripped.startswith("|") and stripped.endswith("|")
        if is_table_row:
            in_table = True
        elif in_table and not is_table_row:
            in_table = False

        is_header = False
        header_level = 0
        header_text = ""
        if not in_code_block and stripped.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
            if match:
                is_header = True
                header_level = len(match.group(1))
                header_text = match.group(2).strip()
                if header_level == 1:
                    doc_title = header_text

                while header_stack and header_stack[-1][0] >= header_level:
                    header_stack.pop()
                header_stack.append((header_level, header_text))
                active_breadcrumb = " > ".join(h[1] for h in header_stack)

        has_content_before_header = bool(curr_lines and any(not l.strip().startswith('#') and l.strip() for l in curr_lines))
        should_split = (
            (is_header and has_content_before_header and not in_code_block) or
            (curr_size >= parent_size and not in_code_block and not in_table)
        )

        if should_split and curr_lines:
            p_obj = flush_parent(curr_lines, active_breadcrumb)
            if p_obj:
                parent_sections.append(p_obj)
            curr_lines = []
            curr_size = 0

        curr_lines.append(line)
        curr_size += len(line)

    if curr_lines:
        p_obj = flush_parent(curr_lines, active_breadcrumb)
        if p_obj:
            parent_sections.append(p_obj)

    # 2. Generate Granular Child Chunks linked to each Parent
    child_chunks: List[Dict[str, Any]] = []
    for p_idx, parent in enumerate(parent_sections):
        p_text = parent["content"]
        p_hdr = parent["section_header"]
        p_id = parent["id"]
        
        # If parent is already small enough, treat as 1 child
        if len(p_text) <= child_size:
            enriched = f"[Context: {p_hdr}]\n{p_text}" if p_hdr else p_text
            attrs = extract_chunk_attributes(p_text, doc_title=doc_title, parent_headers=p_hdr, filepath=filepath)
            child_chunks.append({
                "parent_id": p_id,
                "chunk_index": len(child_chunks),
                "content": enriched,
                "raw_content": p_text,
                "parent_header": p_hdr,
                "doc_title": doc_title or parent["doc_title"],
                "intent_type": attrs["intent_type"],
                "trust_type": attrs.get("trust_type", "general"),
                "source_type": attrs.get("source_type", "primary_doc"),
                "entities": attrs["entities"],
                "entities_json": attrs["entities_json"],
                "domain_scope": attrs["domain_scope"],
                "attributes_json": attrs["attributes_json"]
            })
            continue

        # Granular sliding window within parent section
        step = max(1, child_size - child_overlap)
        for c_start in range(0, len(p_text), step):
            sub_raw = p_text[c_start : c_start + child_size].strip()
            if not sub_raw:
                continue
            enriched = f"[Context: {p_hdr}]\n{sub_raw}" if p_hdr else sub_raw
            attrs = extract_chunk_attributes(sub_raw, doc_title=doc_title, parent_headers=p_hdr, filepath=filepath)
            child_chunks.append({
                "parent_id": p_id,
                "chunk_index": len(child_chunks),
                "content": enriched,
                "raw_content": sub_raw,
                "parent_header": p_hdr,
                "doc_title": doc_title or parent["doc_title"],
                "intent_type": attrs["intent_type"],
                "trust_type": attrs.get("trust_type", "general"),
                "source_type": attrs.get("source_type", "primary_doc"),
                "entities": attrs["entities"],
                "entities_json": attrs["entities_json"],
                "domain_scope": attrs["domain_scope"],
                "attributes_json": attrs["attributes_json"]
            })

    return {
        "parent_chunks": parent_sections,
        "child_chunks": child_chunks
    }

def semantic_markdown_chunker(
    text: str,
    filepath: str = "",
    max_chunk_size: int = 800,
    overlap: int = 120,
    return_hierarchy: bool = False
) -> Any:
    """
    Markdown-Aware Hierarchical AST & Semantic Boundary Chunker:
    - Returns child chunks linked to parent sections, or full hierarchy if return_hierarchy=True.
    """
    hierarchy = semantic_markdown_chunker_hierarchical(
        text=text,
        filepath=filepath,
        parent_size=max(max_chunk_size, 800),
        child_size=max(200, min(max_chunk_size, 400)),
        child_overlap=overlap
    )
    if return_hierarchy:
        return hierarchy
    return hierarchy["child_chunks"]

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Split text into AST heading-aware and Markdown table-preserving chunks.
    Maintains 100% backward compatibility returning List[str].
    """
    if not text or not str(text).strip():
        return []
    semantic_chunks = semantic_markdown_chunker(text, max_chunk_size=chunk_size, overlap=overlap)
    if semantic_chunks:
        return [c.get("raw_content", c["content"]) for c in semantic_chunks]
    step = max(1, chunk_size - overlap)
    return [text[i:i + chunk_size] for i in range(0, len(text), step)]

def parse_query_operators(q_str: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """Parse search operators (e.g. tag:foo, size:>1mb, -word, NEAR(...))."""
    if not q_str:
        return "", {}, {}

    operators: Dict[str, Any] = {}
    exclusions: Dict[str, Any] = {}
    cleaned_q = []

    near_exprs = re.findall(r'NEAR\([^)]+\)', q_str, re.IGNORECASE)
    for ne in near_exprs:
        cleaned_q.append(ne)
        q_str = q_str.replace(ne, "")

    tokens = q_str.split()
    for token in tokens:
        is_exclude = False
        t_val = token

        if t_val.startswith("-") and len(t_val) > 1:
            is_exclude = True
            t_val = t_val[1:]

        if ":" in t_val:
            key, val = t_val.split(":", 1)
            val = val.strip('"').strip("'")
            if is_exclude:
                exclusions[key.lower()] = val
            else:
                operators[key.lower()] = val
        elif ">" in t_val or "<" in t_val:
            match = RE_SIZE_OP.match(t_val)
            if match:
                op, num, unit = match.groups()
                bytes_val = int(num)
                if unit:
                    unit = unit.lower()
                    if unit == "kb":
                        bytes_val *= 1024
                    elif unit == "mb":
                        bytes_val *= 1024 * 1024
                if is_exclude:
                    exclusions["size"] = (op, bytes_val)
                else:
                    operators["size"] = (op, bytes_val)
            else:
                if is_exclude:
                    exclusions["word"] = exclusions.get("word", []) + [t_val]
                else:
                    cleaned_q.append(t_val)
        else:
            if is_exclude:
                exclusions["word"] = exclusions.get("word", []) + [t_val]
            else:
                cleaned_q.append(t_val)

    return " ".join(cleaned_q).strip(), operators, exclusions

@lru_cache(maxsize=1024)
def suggest_tags_from_text(text: str) -> List[str]:
    """Suggest top tags based on word frequency in text."""
    if not text:
        return []
    stopwords = {
        "the", "and", "of", "to", "is", "in", "that", "it", "for", "on", "with", "as",
        "this", "was", "at", "by", "an", "be", "are", "from", "or", "your", "have",
        "had", "has", "but", "not", "what", "all", "were", "when", "we"
    }
    words = re.findall(r"\b[a-z]{3,15}\b", text.lower())
    freq: Dict[str, int] = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:4]]

def suggest_scored_tags_from_text(text: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """
    Computes confidence-scored tag suggestions with word length normalization and IDF penalty.
    Returns [{'tag': str, 'confidence': float, 'occurrences': int}].
    """
    if not text or not isinstance(text, str):
        return []
    
    stopwords = {
        "the", "and", "of", "to", "is", "in", "that", "it", "for", "on", "with", "as",
        "this", "was", "at", "by", "an", "be", "are", "from", "or", "your", "have",
        "had", "has", "but", "not", "what", "all", "were", "when", "we", "can", "will",
        "about", "into", "more", "their", "which", "there", "would", "they", "been"
    }
    
    words = re.findall(r"\b[a-z]{3,20}\b", text.lower())
    if not words:
        return []
        
    counts = Counter(w for w in words if w not in stopwords)
    if not counts:
        return []
        
    max_count = max(counts.values())
    total_non_stop = sum(counts.values())
    
    scored = []
    for tag, count in counts.most_common(top_k * 2):
        length_bonus = min(1.3, 0.8 + (len(tag) / 10.0))
        raw_conf = min(0.99, (count / float(max_count)) * length_bonus)
        scored.append({
            "tag": tag,
            "confidence": round(raw_conf, 2),
            "occurrences": count
        })
        
    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return scored[:top_k]

@lru_cache(maxsize=1024)
def generate_summary(text: str) -> str:
    """Generate extractive summary using TF-IDF sentence scoring."""
    if not text or len(text.strip()) < 100:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) <= 3:
        return text.strip()

    words = re.findall(r"\b[a-z]{4,15}\b", text.lower())
    word_freq = Counter(words)

    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        s_words = re.findall(r"\b[a-z]{4,15}\b", sentence.lower())
        for word in s_words:
            score += word_freq.get(word, 0)
        length = len(s_words)
        if length > 0:
            score = score / length
        sentence_scores.append((score, i, sentence))

    top_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:3]
    top_sentences = sorted(top_sentences, key=lambda x: x[1])
    return " ".join([s[2] for s in top_sentences]).strip()

_RE_CLEAN_FTS = re.compile(r'[\x00-\x1F\x7F<>]')
_RE_KEYWORD_OPERATORS = re.compile(r'\s*(\b(OR|NOT|AND)\b|NEAR\([^)]*\))\s*', re.IGNORECASE)

from src.core.text_utils import sanitise_fts_query, sanitize_fts_query, sanitize_tag

@lru_cache(maxsize=1024)
def lookup_tag_color(tag: str) -> str:
    """Read-only default tag color lookup by tag name hash."""
    if not tag:
        return "#3b82f6"
    colors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#6366f1"]
    idx = sum(ord(c) for c in tag.lower().strip()) % len(colors)
    return colors[idx]

@lru_cache(maxsize=1024)
def lookup_document_metadata_category(mime_type: str, ext: str) -> str:
    """Read-only pure document metadata lookup for mime and extension category."""
    mime = (mime_type or "").lower()
    extension = (ext or "").lstrip(".").lower()
    if mime.startswith("image/") or extension in ("png", "jpg", "jpeg", "gif", "svg", "webp"):
        return "image"
    if mime.startswith("audio/") or extension in ("wav", "mp3", "flac", "ogg", "m4a"):
        return "audio"
    if mime == "application/pdf" or extension == "pdf":
        return "pdf"
    if extension in ("doc", "docx", "rtf", "txt", "md"):
        return "document"
    if extension in ("xls", "xlsx", "csv"):
        return "spreadsheet"
    return "other"

def chunk_text_hierarchical(text: str, parent_size: int = 600, child_size: int = 150) -> List[Dict[str, Any]]:
    """
    Hierarchical Parent-Child Chunking.
    Splits text into larger Parent Sections (parent_size) and granular Child Snippets (child_size).
    Each child chunk holds a reference to its enclosing parent context block.
    """
    if not text or not text.strip():
        return []

    clean_text = text.strip()
    # Split into paragraphs or major sections
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', clean_text) if p.strip()]
    if not paragraphs:
        paragraphs = [clean_text]

    parent_blocks = []
    current_parent = []
    current_len = 0

    for p in paragraphs:
        if current_len + len(p) <= parent_size or not current_parent:
            current_parent.append(p)
            current_len += len(p)
        else:
            parent_blocks.append("\n\n".join(current_parent))
            current_parent = [p]
            current_len = len(p)
    if current_parent:
        parent_blocks.append("\n\n".join(current_parent))

    hierarchical_chunks = []
    child_idx = 0

    for parent_idx, parent_text in enumerate(parent_blocks):
        # Generate child chunks within this parent block
        sentences = [s.strip() for s in RE_SENTENCE_SPLIT.split(parent_text) if s.strip()]
        if not sentences:
            sentences = [parent_text]

        curr_child_sentences = []
        curr_child_len = 0

        for s in sentences:
            if curr_child_len + len(s) <= child_size or not curr_child_sentences:
                curr_child_sentences.append(s)
                curr_child_len += len(s)
            else:
                child_text = " ".join(curr_child_sentences)
                hierarchical_chunks.append({
                    "child_index": child_idx,
                    "parent_index": parent_idx,
                    "child_content": child_text,
                    "parent_content": parent_text,
                    "child_char_len": len(child_text),
                    "parent_char_len": len(parent_text)
                })
                child_idx += 1
                curr_child_sentences = [s]
                curr_child_len = len(s)

        if curr_child_sentences:
            child_text = " ".join(curr_child_sentences)
            hierarchical_chunks.append({
                "child_index": child_idx,
                "parent_index": parent_idx,
                "child_content": child_text,
                "parent_content": parent_text,
                "child_char_len": len(child_text),
                "parent_char_len": len(parent_text)
            })
            child_idx += 1

    return hierarchical_chunks

_SYNONYM_DICT = {
    "auth": "authentication",
    "authentication": "auth",
    "db": "database",
    "database": "db",
    "cfg": "configuration",
    "config": "configuration",
    "configuration": "config",
    "err": "error",
    "errors": "error",
    "req": "request",
    "requests": "request",
    "doc": "document",
    "docs": "document",
    "documents": "document",
    "func": "function",
    "functions": "function",
    "repo": "repository",
    "repositories": "repository",
    "queue": "buffer",
    "circular": "ring",
    "tasks": "items",
    "task": "item",
    "executors": "workers",
    "executor": "worker",
    "messages": "payloads",
    "message": "payload",
    "asynchronously": "concurrently",
    "concurrent": "asynchronous",
    "concurrency": "threading",
    "deletion": "unlinking",
    "delete": "unlink",
    "lock": "locking",
    "locks": "locking",
    "permission": "lock",
}

@lru_cache(maxsize=2048)
def stem_word(word: str) -> str:
    """
    Lightweight rule-based Porter stemmer for English suffix reduction.
    Reduces plurals and common verbal suffixes without external dependencies.
    """
    if not word or len(word) <= 3:
        return word.lower()
    w = word.lower()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 3 and not w.endswith("ses") and not w.endswith("zes"):
        return w[:-1] if (w.endswith("les") or w.endswith("res") or w.endswith("des") or w.endswith("ves")) else w[:-2]
    if w.endswith("ing") and len(w) > 5:
        return w[:-3]
    if w.endswith("ed") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w

@lru_cache(maxsize=1024)
def expand_synonyms(query: str) -> str:
    """
    Expands query with technical domain synonyms and acronym equivalents.
    """
    if not query:
        return ""
    words = re.findall(r'\b[a-zA-Z0-9_\-]+\b', query)
    expanded = list(words)
    for w in words:
        low = w.lower()
        syn = _SYNONYM_DICT.get(low)
        if syn and syn not in expanded:
            expanded.append(syn)
    return " ".join(expanded)



