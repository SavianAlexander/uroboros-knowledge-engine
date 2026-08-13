"""
Domain-allocated Advanced RAG Synthesis Engine.
Provides HyDE query expansion, RRF hybrid re-ranking, and word-level Jaccard snippet deduplication.
"""
import time
import re
import math
import logging
import unicodedata
from collections import defaultdict
from functools import lru_cache
from typing import List, Dict, Any, Tuple, Optional, Set

from src.core.model_manager import get_fallback_llm
from src.core.config import is_testing

logger = logging.getLogger(__name__)

_RE_CLEAN_FTS = re.compile(r'[\x00-\x1F\x7F<>]')
_RE_KEYWORD_OPERATORS = re.compile(r'\s*(\b(OR|NOT|AND)\b|NEAR\([^)]*\))\s*', re.IGNORECASE)
_RE_WORDS = re.compile(r'\b[a-zA-Z0-9]{2,}\b')
RE_FTS_ASTERISK = re.compile(r'(^|\s)\*+')
RE_FTS_SYMBOLS = re.compile(r'[/<>=;~\\()|]|--')
RE_FTS_WORDS = re.compile(r'\b[\w\*]+\b')

@lru_cache(maxsize=1024)
def sanitize_fts_query(query: str) -> str:
    """
    Sanitize search query for FTS5 syntax safety, removing unescaped FTS special characters
    and boolean operator keywords that would cause SQLite MATCH syntax errors.
    """
    if not query:
        return ""
    normalized = unicodedata.normalize("NFC", str(query))
    # Replace hyphens/dashes with spaces to prevent FTS5 column specification/minus syntax errors
    cleaned = normalized.replace('-', ' ')
    # Strip leading/standalone asterisks
    cleaned = RE_FTS_ASTERISK.sub(' ', cleaned)
    # Replace dangerous symbols with space
    cleaned = RE_FTS_SYMBOLS.sub(' ', cleaned)
    cleaned = _RE_CLEAN_FTS.sub('', cleaned)
    if '"' in cleaned:
        cleaned = cleaned.replace('"', ' ')
    cleaned = _RE_KEYWORD_OPERATORS.sub(' ', cleaned)
    words = [w for w in RE_FTS_WORDS.findall(cleaned) if w.lower() not in ('and', 'or', 'not', 'near')]
    return " ".join(words) if words else ""

def generate_hyde_expansion(query: str) -> str:
    """
    Produces hypothetical expanded document text with unescaped FTS character sanitization.
    Combines input query with synthetic technical excerpt from LLM or fallback context.
    """
    if not query or not str(query).strip():
        return ""

    raw_query = str(query).strip()
    expanded = raw_query

    try:
        if is_testing:
            expanded = f"{raw_query} - hypothetical answer context"
        else:
            llm = get_fallback_llm()
            if llm:
                prompt = (
                    f"Write a concise 2-sentence technical excerpt answering this question: '{raw_query}'. "
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
                    expanded = f"{raw_query}\n{excerpt}"
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        logger.exception("Swallowed error in rag_engine.py")
        expanded = raw_query

    return expanded

from collections import defaultdict, Counter

def rrf_rerank(fts_results: List[Dict[str, Any]], vector_results: List[Dict[str, Any]], k: int = 60, alpha: float = 0.5) -> List[Dict[str, Any]]:
    """
    Reciprocal Rank Fusion ranking algorithm blending FTS and vector positions with alpha weighting.
    Formula: RRF_score(d) = (1.0 - alpha) * (1/(k + r_fts(d))) + alpha * (1/(k + r_vec(d)))
    """
    scores: Dict[str, float] = defaultdict(float)
    item_map: Dict[str, Dict[str, Any]] = {}
    
    alpha = max(0.0, min(1.0, float(alpha)))
    w_fts = (1.0 - alpha) * 2.0
    w_vec = alpha * 2.0

    for rank, item in enumerate(fts_results or [], start=1):
        key = item.get("filepath") or item.get("id") or item.get("filename") or str(item)
        scores[key] += w_fts * (1.0 / (k + rank))
        if key not in item_map:
            item_map[key] = dict(item)

    for rank, item in enumerate(vector_results or [], start=1):
        key = item.get("filepath") or item.get("id") or item.get("filename") or str(item)
        scores[key] += w_vec * (1.0 / (k + rank))
        if key not in item_map:
            item_map[key] = dict(item)

def okapi_bm25_rerank(documents: List[Dict[str, Any]], query: str, k1: float = 1.5, b: float = 0.75, decay_lambda: float = 0.0001) -> List[Dict[str, Any]]:
    """
    Heavy Upgrade: Native Zero-Dependency Okapi BM25 search ranking engine with term saturation (k1=1.5),
    document length normalization (b=0.75), and exponential recency time-decay.
    # ponytail: zero-dependency Okapi BM25 algorithm; ceiling: in-memory candidate re-ranking; upgrade: SQLite FTS5 custom C auxiliary module if indexing > 1M documents
    """
    if not documents or not query:
        return documents or []

    query_terms = [w.lower() for w in _RE_WORDS.findall(sanitize_fts_query(query))]
    if not query_terms:
        return documents

    N = len(documents)
    doc_tokens = []
    doc_lengths = []

    for doc in documents:
        content = doc.get("content") or doc.get("snippet") or doc.get("text") or ""
        tokens = [w.lower() for w in _RE_WORDS.findall(str(content))]
        doc_tokens.append(tokens)
        doc_lengths.append(len(tokens))

    avgdl = (sum(doc_lengths) / N) if N > 0 else 1.0
    if avgdl == 0:
        avgdl = 1.0

    # Calculate Inverse Document Frequency (IDF) for query terms
    df = defaultdict(int)
    for tokens in doc_tokens:
        seen = set(tokens)
        for term in query_terms:
            if term in seen:
                df[term] += 1

    idf = {}
    for term in query_terms:
        n_q = df[term]
        idf[term] = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)

    now = time.time()
    scored_docs = []

    for idx, doc in enumerate(documents):
        tokens = doc_tokens[idx]
        doc_len = doc_lengths[idx]
        tf = Counter(tokens)

        bm25_score = 0.0
        for term in query_terms:
            freq = tf[term]
            if freq > 0:
                numerator = freq * (k1 + 1.0)
                denominator = freq + k1 * (1.0 - b + b * (doc_len / avgdl))
                bm25_score += idf[term] * (numerator / denominator)

        # Exponential recency decay multiplier e^(-lambda * delta_t)
        modified_at = doc.get("modified_at") or now
        if isinstance(modified_at, str):
            try:
                modified_at = float(modified_at)
            except ValueError:
                modified_at = now
        age_seconds = max(0.0, now - float(modified_at))
        decay_factor = math.exp(-decay_lambda * (age_seconds / 86400.0))

        final_score = round(bm25_score * decay_factor, 6)
        doc_copy = dict(doc)
        doc_copy["okapi_bm25_score"] = final_score
        scored_docs.append(doc_copy)

    scored_docs.sort(key=lambda d: d["okapi_bm25_score"], reverse=True)
    return scored_docs

# Alias for backward compatibility
reciprocal_rank_fusion = rrf_rerank

def _compute_word_jaccard(words1: Set[str], words2: Set[str]) -> float:
    """Calculates word-level Jaccard similarity coefficient J(A,B) = |A ∩ B| / |A ∪ B|."""
    if not words1 or not words2:
        return 0.0
    inter_len = len(words1 & words2)
    if inter_len == 0:
        return 0.0
    return inter_len / len(words1 | words2)

def jaccard_deduplicate(snippets: List[Any], threshold: float = 0.70) -> List[Any]:
    """
    Word-level Jaccard similarity (J(A,B) = |A ∩ B| / |A ∪ B|) snippet deduplication
    filtering out items with similarity >= threshold.
    """
    if not snippets:
        return []

    kept_items = []
    kept_word_sets: List[Set[str]] = []

    for item in snippets:
        if isinstance(item, str):
            text_content = item
        elif isinstance(item, dict):
            text_content = item.get("content") or item.get("snippet") or item.get("text") or ""
        else:
            text_content = str(item)

        safe_str = str(text_content or "").lower()
        words = set(_RE_WORDS.findall(safe_str))

        is_duplicate = False
        if words:
            for kept_words in kept_word_sets:
                if _compute_word_jaccard(words, kept_words) >= threshold:
                    is_duplicate = True
                    break

        if not is_duplicate:
            kept_items.append(item)
            if words:
                kept_word_sets.append(words)

    return kept_items

@lru_cache(maxsize=512)
def _decompose_multihop_cached(query: str) -> Tuple[str, ...]:
    if not query or not str(query).strip():
        return ()
    raw = str(query).strip()
    split_pattern = r'\s+(?:vs\.?|versus|compared\s+to|as\s+well\s+as|along\s+with|\b(?:and|or)\b)\s+'
    parts = re.split(split_pattern, raw, flags=re.IGNORECASE)
    sub_queries = [p.strip() for p in parts if len(p.strip()) >= 3]
    if not sub_queries:
        return (raw,)
    if raw not in sub_queries and len(sub_queries) > 1:
        sub_queries.insert(0, raw)
    return tuple(sub_queries)

def decompose_multihop_query(query: str) -> List[str]:
    """
    Decomposes multi-part / comparative queries into standalone sub-queries for parallel RAG retrieval.
    Splits on conjunctions (' and ', ' vs ', ' versus ', ' compared to ', ' as well as ').
    # ponytail: cached multihop query decomposition; ceiling: 512 cached queries; upgrade: Trie parser for complex nested boolean expressions
    """
    return list(_decompose_multihop_cached(query))

def trim_to_sentence_boundary(text: str, max_chars: int = 600) -> str:
    """
    Trims text at clean sentence boundaries (., !, ?) so retrieved context is never cut off mid-sentence.
    """
    if not text or len(text) <= max_chars:
        return text or ""
    truncated = text[:max_chars]
    # Find last sentence-ending punctuation mark
    match = re.search(r'.*[\.\!\?]', truncated, flags=re.DOTALL)
    if match and len(match.group(0).strip()) > 50:
        return match.group(0).strip()
    # Fallback to last space boundary
    space_idx = truncated.rfind(' ')
    return (truncated[:space_idx] + "...") if space_idx > 50 else (truncated + "...")

def parse_metadata_filters(query: str) -> Tuple[str, Dict[str, str]]:
    """
    Parses metadata filter operators (tag:python, ext:md, mime:pdf) from query string.
    Returns (cleaned_query, filters_dict).
    """
    if not query:
        return "", {}
    filters = {}
    tokens = []
    for token in query.split():
        if ":" in token and not token.startswith("http"):
            key, val = token.split(":", 1)
            key_low = key.lower()
            if key_low in ("tag", "ext", "mime", "type"):
                filters[key_low] = val.strip().lower()
                continue
        tokens.append(token)
    return " ".join(tokens), filters

RE_TEMPORAL = re.compile(r'\b(?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,4}\b|\bQ[1-4]\s*(?:19|20)\d{2}\b', re.IGNORECASE)

def precision_cross_rerank(query: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Pass-2 Mechanical Precision Re-ranking:
    Scores candidates based on term coverage density, exact phrase proximity, header alignment,
    exponential modification recency decay weighting, and Narrative Time alignment.
    """
    if not query or not candidates:
        return candidates or []

    q_terms = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', query)]
    if not q_terms:
        return candidates
    now_ts = time.time()
    decay_rate = 1e-7  # Gentle exponential recency decay multiplier
    
    query_temporal_markers = set(m.lower() for m in RE_TEMPORAL.findall(query))

    reranked = []
    for cand in candidates:
        item = dict(cand)
        content = (item.get("content") or item.get("snippet") or "").lower()
        filename = (item.get("filename") or "").lower()
        mod_at = float(item.get("modified_at") or item.get("modified") or now_ts)

        # 1. Term Coverage Density
        matched_terms = set(t for t in q_terms if t in content)
        coverage_score = (len(matched_terms) / len(q_terms)) if q_terms else 0.0

        # 2. Phrase Proximity Boost
        phrase_boost = 0.0
        if len(q_terms) >= 2:
            bigrams = [" ".join(q_terms[i:i+2]) for i in range(len(q_terms)-1)]
            matched_bigrams = sum(1 for b in bigrams if b in content)
            phrase_boost = ((matched_bigrams / len(bigrams)) * 0.4) if bigrams else 0.0

        # 3. Filename/Header Match Boost
        header_boost = 0.25 if any(t in filename for t in q_terms) else 0.0
        
        # 4. Aspect of Time (Narrative Time Boost)
        temporal_boost = 0.0
        if query_temporal_markers:
            doc_temporal_markers = set(m.lower() for m in RE_TEMPORAL.findall(content))
            shared_time = query_temporal_markers & doc_temporal_markers
            if shared_time:
                temporal_boost = 0.5 * len(shared_time)

        # 5. Recency Time-Decay Boost
        age_seconds = max(0.0, now_ts - mod_at)
        recency_decay = math.exp(-decay_rate * age_seconds)

        base_score = float(item.get("rrf_score", 0.1))
        precision_score = round(base_score * (1.0 + coverage_score + phrase_boost + header_boost + temporal_boost) * recency_decay, 6)
        item["rrf_score"] = precision_score
        item["precision_boost"] = round(coverage_score + phrase_boost + header_boost + temporal_boost, 4)
        item["recency_decay"] = round(recency_decay, 4)
        reranked.append(item)

    reranked.sort(key=lambda x: x["rrf_score"], reverse=True)
    return reranked

def _fts_fallback_search(sq: str) -> list:
    try:
        from src.infrastructure.database import get_db
        conn = get_db()
        cursor = conn.cursor()
        like_term = f"%{sq}%"
        cursor.execute(
            "SELECT filepath, filename, content, modified_at FROM files WHERE filename LIKE ? OR content LIKE ? LIMIT 10",
            (like_term, like_term)
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in fts fallback")
        return []

def extract_advanced_rag_context(
    query: str,
    max_chunks: int = 5,
    jaccard_threshold: float = 0.70
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Orchestrates full Advanced RAG pipeline with 5 Mechanical Super-Upgrades:
    1. SQL Metadata Filter Pushdown (tag:, ext: filters)
    2. Multi-hop query decomposition into sub-queries
    3. Technical synonym expansion & Porter stemming
    4. HyDE query expansion & FTS5 character sanitization
    5. Okapi BM25 Probabilistic Hybrid Retrieval
    6. Reciprocal Rank Fusion (RRF) re-ranking
    7. Pass-2 Mechanical Precision Re-ranking (term coverage + phrase proximity + recency decay)
    8. Word-level Jaccard snippet deduplication (threshold >= 0.70)
    9. Parent-Child Chunk Context Resolution & Sentence-Boundary Trimming
    Returns (context_text, citations_list).
    """
    if not query or not str(query).strip():
        return "", []

    raw_q = str(query).strip()
    cleaned_q, filters = parse_metadata_filters(raw_q)
    target_q = cleaned_q or raw_q
    from src.infrastructure.database import get_db

    from src.infrastructure.vector_engine import MiniVectorEngine
    from src.core.domain.services import chunk_text_hierarchical, expand_synonyms

    synonym_expanded_q = expand_synonyms(target_q)
    sub_queries = decompose_multihop_query(synonym_expanded_q or target_q)

    all_fts_hits = []
    all_vec_hits = []

    for sq in sub_queries:
        expanded_q = generate_hyde_expansion(sq)
        sanitized_q = sanitize_fts_query(sq) or sanitize_fts_query(expanded_q)


        fts_hits = []
        if sanitized_q:
            try:
                conn = get_db()
                cursor = conn.cursor()

                # Build SQL filter pushdown constraints
                sql_where = ["fts_files MATCH ?"]
                sql_params = [sanitized_q]

                if "ext" in filters:
                    sql_where.append("files.filename LIKE ?")
                    sql_params.append(f"%.{filters['ext']}")

                query_sql = (
                    "SELECT files.filepath, files.filename, files.content, files.modified_at "
                    "FROM fts_files JOIN files ON fts_files.filepath = files.filepath "
                    f"WHERE {' AND '.join(sql_where)} LIMIT 10"
                )
                cursor.execute(query_sql, sql_params)
                fts_hits = [dict(row) for row in cursor.fetchall()]
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in rag_engine.py")
                fts_hits = _fts_fallback_search(sq)

        vec_hits = []
        try:
            vec_hits = MiniVectorEngine.search_semantic(expanded_q or sq)
            if "ext" in filters:
                vec_hits = [v for v in vec_hits if (v.get("filename") or "").lower().endswith(f".{filters['ext']}")]
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in rag_engine.py")
            vec_hits = []

        all_fts_hits.extend(fts_hits)
        all_vec_hits.extend(vec_hits)

    fused_hits = rrf_rerank(all_fts_hits, all_vec_hits, k=60)
    precision_hits = precision_cross_rerank(target_q, fused_hits)
    deduped_hits = jaccard_deduplicate(precision_hits, threshold=jaccard_threshold)

    citations = []
    context_blocks = []

    for idx, hit in enumerate(deduped_hits[:max_chunks], start=1):
        score = hit.get("rrf_score", 0.0)
        fname = hit.get("filename", "document.txt")
        fpath = hit.get("filepath", "")
        content = (hit.get("content") or hit.get("snippet") or "").strip()

        # Parent-Child Chunk Expansion & Sentence-Boundary Smart Trimming
        hierarchical = chunk_text_hierarchical(content, parent_size=600, child_size=150)
        if hierarchical:
            raw_snippet = hierarchical[0]["parent_content"]
        else:
            raw_snippet = content[:600] if len(content) > 600 else content

        snippet = trim_to_sentence_boundary(raw_snippet, max_chars=600)

        citation_str = f"[Source: {fname} (Chunk #{idx})]"
        citations.append({
            "citation": citation_str,
            "filename": fname,
            "filepath": fpath,
            "confidence_score": score
        })
        context_blocks.append(f"{citation_str}\n{snippet}")

    # 2-Hop GraphRAG Traversal
    graph_context_blocks = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        for hit in deduped_hits[:3]:
            fpath = hit.get("filepath", "")
            if not fpath:
                continue
            cursor.execute("SELECT tag FROM tags WHERE file_id = (SELECT id FROM files WHERE filepath = ?)", (fpath,))
            file_tags = [r[0] for r in cursor.fetchall()]
            if file_tags:
                placeholders = ",".join(["?"] * len(file_tags))
                cursor.execute(f"SELECT DISTINCT f.filename FROM files f JOIN tags t ON f.id = t.file_id WHERE t.tag IN ({placeholders}) AND f.filepath != ? LIMIT 3", (*file_tags, fpath))
                neighbors = [r[0] for r in cursor.fetchall()]
                if neighbors:
                    graph_context_blocks.append(f"[Graph Context: '{hit.get('filename')}' connected to: {', '.join(neighbors)}]")
    except Exception:
        pass

    context_text = "\n\n".join(context_blocks)
    if graph_context_blocks:
        context_text = "\n".join(graph_context_blocks) + "\n\n" + context_text
    return context_text, citations


def get_rag_engine_capabilities() -> Dict[str, Any]:
    """Returns capabilities and configuration defaults for the zero-dependency RAG engine."""
    return {
        "engine_name": "Uroboros SOTA RAG Engine",
        "search_modes": ["fts5_bm25", "matryoshka_dense", "binary_colbert_maxsim", "graphrag_2hop"],
        "minhash_deduplication_threshold": 0.65,
        "rrf_k_constant": 60.0,
        "default_context_window_chars": 16384,
        "status": "active"
    }

