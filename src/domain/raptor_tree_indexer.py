"""
RAPTOR Tree Indexer (Recursive Abstractive Processing for Tree-Organized Retrieval).
Constructs a multi-tier semantic summary tree enabling simultaneous macro (executive) and micro (granular) RAG retrieval.
Zero-dependency, stdlib implementation.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional, Set, Tuple


def _tokenize_words(text: str) -> Set[str]:
    """Tokenizes normalized alphanumeric tokens from text."""
    if not text:
        return set()
    norm = unicodedata.normalize("NFC", str(text).lower())
    return set(re.findall(r'\b\w{3,}\b', norm))


def _jaccard_token_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return float(intersection) / float(union) if union > 0 else 0.0


def _extract_extractive_summary(text: str, max_sentences: int = 3) -> str:
    """
    Extracts high-entropy salient sentences from text without external LLM dependencies.
    Ranks sentences by term frequency and entity capitalization.
    """
    if not text:
        return ""
    norm = unicodedata.normalize("NFC", text.strip())
    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', norm) if len(s.strip()) > 10]
    if len(raw_sentences) <= max_sentences:
        return " ".join(raw_sentences)

    # Compute word frequency dictionary across the paragraph
    words = re.findall(r'\b\w+\b', norm.lower())
    freq = {}
    for w in words:
        if len(w) > 3:
            freq[w] = freq.get(w, 0) + 1

    # Score each sentence
    scored_sentences = []
    for idx, s in enumerate(raw_sentences):
        s_words = re.findall(r'\b\w+\b', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        # Prioritize opening and concluding thesis statements
        if idx == 0:
            score *= 1.3
        elif idx == len(raw_sentences) - 1:
            score *= 1.1
        scored_sentences.append((score, idx, s))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = sorted(scored_sentences[:max_sentences], key=lambda x: x[1])
    return " ".join(s[2] for s in top_sentences)


def build_raptor_tree(doc_chunks: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Constructs a 3-tier RAPTOR semantic summary tree:
      - Level 0: Granular micro-chunks
      - Level 1: Semantic cluster summaries (thematic clusters)
      - Level 2: Executive corpus abstraction (macro summary)
    """
    if not doc_chunks or not isinstance(doc_chunks, list):
        return {"status": "empty", "tree_depth": 0, "level_0": [], "level_1": [], "level_2": []}

    level_0 = [
        {
            "chunk_id": f"l0_{i}",
            "text": c.get("text", "") if isinstance(c, dict) else str(c),
            "source": c.get("source", "") if isinstance(c, dict) else "",
            "tokens": _tokenize_words(c.get("text", "") if isinstance(c, dict) else str(c))
        }
        for i, c in enumerate(doc_chunks)
    ]

    if not level_0:
        return {"status": "empty", "tree_depth": 0, "level_0": [], "level_1": [], "level_2": []}

    # Step 1: Cluster Level 0 nodes into thematic clusters based on token overlap
    clusters: List[List[Dict[str, Any]]] = []
    unclustered = list(level_0)

    while unclustered:
        seed = unclustered.pop(0)
        current_cluster = [seed]
        seed_tokens = seed["tokens"]

        # Find closest unclustered neighbors (threshold Jaccard >= 0.12 or max 4 chunks per cluster)
        remaining = []
        for cand in unclustered:
            sim = _jaccard_token_similarity(seed_tokens, cand["tokens"])
            if sim >= 0.12 and len(current_cluster) < 4:
                current_cluster.append(cand)
            else:
                remaining.append(cand)
        unclustered = remaining
        clusters.append(current_cluster)

    # Step 2: Build Level 1 Summary Nodes
    level_1 = []
    for c_idx, cluster in enumerate(clusters):
        combined_text = " ".join(node["text"] for node in cluster)
        summary_text = _extract_extractive_summary(combined_text, max_sentences=3)
        node_id = f"l1_cluster_{c_idx}"
        level_1.append({
            "node_id": node_id,
            "summary_text": summary_text,
            "child_ids": [n["chunk_id"] for n in cluster],
            "tokens": _tokenize_words(summary_text)
        })

    # Step 3: Build Level 2 Executive Abstraction Node
    level_2 = []
    if level_1:
        combined_l1_text = " ".join(node["summary_text"] for node in level_1)
        executive_summary = _extract_extractive_summary(combined_l1_text, max_sentences=4)
        level_2.append({
            "node_id": "l2_executive_0",
            "summary_text": executive_summary,
            "child_ids": [n["node_id"] for n in level_1],
            "tokens": _tokenize_words(executive_summary)
        })

    # Clean internal token sets for clean serialization
    clean_l0 = [{"chunk_id": n["chunk_id"], "text": n["text"], "source": n["source"]} for n in level_0]
    clean_l1 = [{"node_id": n["node_id"], "summary_text": n["summary_text"], "child_ids": n["child_ids"]} for n in level_1]
    clean_l2 = [{"node_id": n["node_id"], "summary_text": n["summary_text"], "child_ids": n["child_ids"]} for n in level_2]

    return {
        "status": "success",
        "tree_depth": 3 if level_2 else (2 if level_1 else 1),
        "total_nodes": len(clean_l0) + len(clean_l1) + len(clean_l2),
        "level_0_count": len(clean_l0),
        "level_1_count": len(clean_l1),
        "level_2_count": len(clean_l2),
        "level_0": clean_l0,
        "level_1": clean_l1,
        "level_2": clean_l2
    }


def search_raptor_tree(raptor_tree: Dict[str, Any], query: str, target_level: int = 1, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Searches the RAPTOR tree at a target abstraction level (0 = granular, 1 = cluster, 2 = executive)
    scoring relevant nodes by token relevance.
    """
    if not raptor_tree or not isinstance(raptor_tree, dict):
        return []

    q_tokens = _tokenize_words(query)

    if target_level == 2:
        candidates = raptor_tree.get("level_2", [])
    elif target_level == 1:
        candidates = raptor_tree.get("level_1", [])
    else:
        candidates = raptor_tree.get("level_0", [])

    if not candidates:
        return []

    scored = []
    for cand in candidates:
        text = cand.get("summary_text", "") or cand.get("text", "")
        cand_tokens = _tokenize_words(text)
        sim = _jaccard_token_similarity(q_tokens, cand_tokens) if q_tokens else 1.0
        scored.append((sim, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_k]]
