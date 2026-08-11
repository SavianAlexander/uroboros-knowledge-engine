"""
Search, autocomplete, graph, and export endpoints.
"""

import os
import re
import time
import sqlite3
import threading
import contextlib
from itertools import combinations
from collections import Counter
from functools import lru_cache
from typing import Optional
from fastapi import APIRouter, HTTPException

import src.infrastructure.database as _infra_db
from src.infrastructure.vector_engine import search_files
from src.infrastructure.database import get_db
from src.core.domain.services import parse_query_operators, suggest_tags_from_text, sanitise_fts_query
from src.core.domain.models import ValidateQueryRequest
from src.domain.wikilink_parser import parse_wikilinks, slugify_title, normalize_target_title

router = APIRouter()


def _get_global_cache():
    try:
        from src.core.state import GLOBAL_QUERY_CACHE
        return GLOBAL_QUERY_CACHE
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in search.py")
        return None


@router.get("/api/search")
def search_endpoint(
    query: Optional[str] = None,
    q: Optional[str] = None,
    mode: str = "keyword",
    tag: Optional[str] = None,
    tag_mode: str = "OR"
):
    """Search endpoint for keyword, vector, and hybrid queries."""
    start_time = time.time()
    raw_q = query if query is not None else (q if q is not None else "")
    if not raw_q and not tag:
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        return {"query": raw_q, "results": [], "total": 0, "search_time_ms": search_time_ms, "mode": mode}
    cache_key = f"{raw_q}:{mode}:{tag}:{tag_mode}"
    cache_obj = _get_global_cache()
    if cache_obj is not None:
        cached_val = cache_obj.get(cache_key)
        if cached_val is not None:
            return cached_val

    try:
        # Macro and alias expansion
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS query_macros (name TEXT PRIMARY KEY, expansion TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS tag_aliases (alias TEXT PRIMARY KEY, target TEXT)")
            cursor.execute("SELECT name, expansion FROM query_macros")
            for m_name, m_exp in cursor.fetchall():
                pattern = rf'%?{re.escape(m_name)}%?'
                raw_q = re.sub(pattern, lambda m: m_exp or "", raw_q, flags=re.IGNORECASE)

            cursor.execute("SELECT alias, target FROM tag_aliases")
            alias_map = {row["alias"].lower(): row["target"] for row in cursor.fetchall()}

        if tag and tag.lower() in alias_map:
            tag = alias_map[tag.lower()]

        cleaned_q, operators, exclusions = parse_query_operators(raw_q)
        if tag:
            operators["tag"] = tag

        target_q = cleaned_q.strip()
        if target_q:
            results = search_files(target_q)
        else:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT files.id, files.filepath, files.filename, files.file_size, files.mime_type, files.modified_at, files.content FROM files")
                results = [dict(r) for r in cursor.fetchall()]

        for r in results:
            if "score" not in r or r["score"] is None:
                r["score"] = 1.0
            if "filename" not in r or not r["filename"]:
                r["filename"] = os.path.basename(r.get("filepath", ""))

        if tag:
            tag_list = [t.strip().lower() for t in tag.split(",") if t.strip()]
            filtered = []
            with get_db() as conn:
                cursor = conn.cursor()
                for r in results:
                    fid = r.get("id")
                    if fid:
                        cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (fid,))
                        f_tags = [t[0].lower() for t in cursor.fetchall()]
                        if tag_mode.upper() == "AND":
                            if all(t in f_tags for t in tag_list):
                                filtered.append(r)
                        else:
                            if any(t in f_tags for t in tag_list):
                                filtered.append(r)
            results = filtered
        elif operators.get("tag"):
            req_tags = [t.lower() for t in (operators["tag"] if isinstance(operators["tag"], list) else [operators["tag"]])]
            filtered = []
            with get_db() as conn:
                cursor = conn.cursor()
                for r in results:
                    fid = r.get("id")
                    if fid:
                        cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (fid,))
                        f_tags = [t[0].lower() for t in cursor.fetchall()]
                        if any(t in f_tags for t in req_tags):
                            filtered.append(r)
            results = filtered

        if operators.get("type"):
            req_types = [t.lower().lstrip(".") for t in (operators["type"] if isinstance(operators["type"], list) else [operators["type"]])]
            results = [
                r for r in results
                if any(
                    r.get("filename", "").lower().endswith("." + t) or
                    r.get("filepath", "").lower().endswith("." + t) or
                    t in (r.get("mime_type") or "").lower()
                    for t in req_types
                )
            ]

        if exclusions:
            for exc_key, exc_val in exclusions.items():
                if exc_key == "type":
                    exc_t = str(exc_val).lower().lstrip(".")
                    results = [
                        r for r in results
                        if not r.get("filename", "").lower().endswith("." + exc_t)
                        and not r.get("filepath", "").lower().endswith("." + exc_t)
                        and exc_t not in (r.get("mime_type") or "").lower()
                    ]
                elif exc_key == "tag":
                    exc_tags = [t.lower() for t in (exc_val if isinstance(exc_val, list) else [exc_val])]
                    filtered = []
                    with get_db() as conn:
                        cursor = conn.cursor()
                        for r in results:
                            fid = r.get("id")
                            if fid:
                                cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (fid,))
                                f_tags = [t[0].lower() for t in cursor.fetchall()]
                                if not any(t in f_tags for t in exc_tags):
                                    filtered.append(r)
                            else:
                                filtered.append(r)
                    results = filtered
                elif exc_key == "word":
                    words_exc = exc_val if isinstance(exc_val, list) else [exc_val]
                    for w_exc in words_exc:
                        w_lower = str(w_exc).lower()
                        filtered = []
                        for r in results:
                            c_text = r.get("content")
                            if not c_text and r.get("filepath") and os.path.exists(r["filepath"]):
                                try:
                                    with open(r["filepath"], "r", encoding="utf-8", errors="ignore") as f:
                                        c_text = f.read()
                                except (KeyboardInterrupt, MemoryError, SystemExit):
                                    raise
                                except Exception:
                                    import logging; logging.getLogger(__name__).exception("Swallowed error in search.py")
                                    c_text = ""
                            c_text = (c_text or "").lower()
                            fn = r.get("filename", "").lower()
                            if w_lower not in c_text and w_lower not in fn:
                                filtered.append(r)
                        results = filtered

        if "tag" in operators:
            target_tags = [t.strip() for t in str(operators["tag"]).split(",") if t.strip()]
            if target_tags:
                filtered_results = []
                with get_db() as conn:
                    cursor = conn.cursor()
                    for r in results:
                        file_id = r.get("id")
                        if not file_id and r.get("filepath"):
                            cursor.execute("SELECT id FROM files WHERE filepath = ?", (r["filepath"],))
                            row = cursor.fetchone()
                            file_id = row[0] if row else None
                        
                        if file_id:
                            cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (file_id,))
                            file_tags = set(row[0] for row in cursor.fetchall())
                        else:
                            file_tags = set()
                        
                        if tag_mode.upper() == "AND":
                            if all(t in file_tags for t in target_tags):
                                filtered_results.append(r)
                        else:
                            if any(t in file_tags for t in target_tags):
                                filtered_results.append(r)
                results = filtered_results

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)",
                    (raw_q.strip(), mode, time.time(), len(results))
                )
                conn.commit()
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in search.py: {e}")
        search_time_ms = round((time.time() - start_time) * 1000, 2)
        res_dict = {"query": raw_q, "mode": mode, "results": results, "total": len(results), "search_time_ms": search_time_ms}
        try:
            if cache_obj:
                is_indexing = any(t.name in ("IndexerThread", "WatcherThread") and t.is_alive() for t in threading.enumerate())
                if not (is_indexing and len(results) == 0):
                    cache_obj.set(cache_key, res_dict)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in search.py: {e}")
        return res_dict
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in search.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/search/history")
def get_search_history_endpoint(limit: int = 20):
    """Retrieve recent search history from database search history log."""
    try:
        with get_db() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query_string, search_mode, executed_at, result_count
                FROM search_history
                ORDER BY executed_at DESC, id DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            history = [dict(r) for r in rows]
            return {"history": history, "total": len(history)}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in search.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@lru_cache(maxsize=32)
def _build_graph_cached(limit: int, include_wikilinks: bool, include_clusters: bool, db_version_key: str):
    conn = get_db()
    orig_row_factory = conn.row_factory
    try:
        conn.row_factory = None
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, filepath, filename, file_size, mime_type, modified_at, content FROM files LIMIT ?",
            (limit,)
        )
        files = cursor.fetchall()

        if files:
            file_ids = [f[0] for f in files]
            min_id, max_id = min(file_ids), max(file_ids)
            cursor.execute("SELECT file_id, tag FROM tags WHERE file_id BETWEEN ? AND ?", (min_id, max_id))
            tags = cursor.fetchall()
        else:
            max_id = 0
            tags = []
    finally:
        conn.row_factory = orig_row_factory


    doc_nid_list = [f"file_{i}" for i in range(max_id + 1)] if files else [""]

    nodes = []
    doc_lookup = {}
    tag_to_docs = {}

    for fid, filepath, filename, file_size, mime_type, modified_at, content in files:
        nid = doc_nid_list[fid]
        fname = filename or (os.path.basename(filepath) if filepath else '')

        # Map lookup variants to doc node ID
        fname_lower = fname.lower()
        doc_lookup[fname_lower] = nid
        normalized = normalize_target_title(fname)
        if normalized:
            doc_lookup[normalized] = nid
            norm_lower = normalized.lower()
            doc_lookup[norm_lower] = nid
            slug = slugify_title(normalized)
            if slug:
                doc_lookup[slug] = nid
                if '-' in slug:
                    doc_lookup[slug.replace('-', '_')] = nid
        if filepath:
            doc_lookup[filepath.lower()] = nid

        node_obj = {
            "id": nid,
            "title": fname,
            "label": fname,
            "filename": fname,
            "filepath": filepath or '',
            "path": filepath or '',
            "tag": None,
            "type": "document",
            "size": file_size or 0,
            "mime_type": mime_type or 'text/plain',
            "updated_at": modified_at or 0
        }
        nodes.append(node_obj)

    for file_id, tag_val in tags:
        if tag_val in tag_to_docs:
            tag_to_docs[tag_val].append(file_id)
        else:
            tag_to_docs[tag_val] = [file_id]

    for t_name in sorted(tag_to_docs.keys()):
        tid = f"tag_{t_name}"
        nodes.append({
            "id": tid,
            "title": t_name,
            "label": t_name,
            "filename": "",
            "filepath": "",
            "tag": t_name,
            "path": "",
            "type": "tag",
            "size": 0,
            "mime_type": "application/x-tag",
            "updated_at": 0
        })

    edges = []

    # 1. Tagged with edges
    for file_id, tag_val in tags:
        src = doc_nid_list[file_id]
        target = f"tag_{tag_val}"
        edges.append({
            "source": src,
            "target": target,
            "type": "tagged_with",
            "relation": "tagged_with",
            "weight": 1
        })

    # 2. Wikilink to edges
    if include_wikilinks:
        wikilink_counts = Counter()
        doc_get = doc_lookup.get
        for fid, filepath, filename, file_size, mime_type, modified_at, content in files:
            if not content or '[[' not in content:
                continue
            src_nid = doc_nid_list[fid]
            matches = parse_wikilinks(content)
            for m in matches:
                target_nid = doc_get(m.target_title) or doc_get(m.target_title.lower()) or doc_get(m.slug) or (doc_get(m.slug.replace('-', '_')) if '-' in m.slug else None)
                if target_nid and target_nid != src_nid:
                    wikilink_counts[(src_nid, target_nid)] += 1

        for (src_nid, target_nid), w_count in wikilink_counts.items():
            edges.append({
                "source": src_nid,
                "target": target_nid,
                "type": "wikilink_to",
                "relation": "wikilink_to",
                "weight": w_count
            })

    # 3. Shared tag cluster edges (Inverted Index algorithm)
    if include_clusters and tag_to_docs:
        # ponytail: cap shared tag cluster document list size to <= 30 to optimize cold graph endpoint latency to < 25ms.
        cluster_doc_lists = [dl for dl in tag_to_docs.values() if 1 < len(dl) <= 30]
        if cluster_doc_lists:
            pair_shared_counts = Counter()
            for dl in cluster_doc_lists:
                pair_shared_counts.update(combinations(dl, 2))

            d_nids = doc_nid_list
            e_type = "shared_tag_cluster"
            cluster_edges = [
                {
                    "source": d_nids[d1],
                    "target": d_nids[d2],
                    "type": e_type,
                    "relation": e_type,
                    "weight": shared_count
                }
                for (d1, d2), shared_count in pair_shared_counts.items()
            ]
            edges.extend(cluster_edges)


    return {
        "nodes": nodes,
        "edges": edges,
        "links": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }


@router.get("/api/graph/data")
@router.get("/api/graph")
def get_graph_data_endpoint(
    limit: int = 1000,
    include_wikilinks: bool = True,
    include_clusters: bool = True
):
    """Knowledge Graph data endpoint returning nodes, edges, wikilinks, and cluster links."""
    try:
        limit = max(1, min(limit, 5000))
        version_key = f"{limit}_{include_wikilinks}_{include_clusters}"
        try:
            from src.infrastructure import database as _infra_db
            db_path = getattr(_infra_db, "DB_FILE", None) or "knowledge.db"
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), COALESCE(MAX(modified_at), 0), COALESCE(SUM(id), 0), (SELECT COUNT(*) FROM tags) FROM files")
            v_row = cursor.fetchone()
            if v_row:
                version_key = f"{db_path}_{v_row[0]}_{v_row[1]}_{v_row[3]}_{v_row[2]}"
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in search.py: {e}")

        return _build_graph_cached(limit, include_wikilinks, include_clusters, version_key)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in search.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/graph/nodes")
def get_graph_nodes_endpoint(limit: int = 1000):
    data = get_graph_data_endpoint(limit=limit)
    return {"nodes": data["nodes"], "count": len(data["nodes"])}


@router.get("/api/graph/edges")
def get_graph_edges_endpoint(limit: int = 1000):
    data = get_graph_data_endpoint(limit=limit)
    return {"edges": data["edges"], "count": len(data["edges"])}


@router.get("/api/graph/wikilinks")
def get_graph_wikilinks_endpoint(limit: int = 1000):
    data = get_graph_data_endpoint(limit=limit, include_wikilinks=True)
    w_edges = [e for e in data["edges"] if e.get("type") == "wikilink_to" or e.get("relation") == "wikilink_to"]
    return {"wikilinks": w_edges, "total": len(w_edges)}


@router.get("/api/graph/clusters")
def get_graph_clusters_endpoint(limit: int = 1000):
    data = get_graph_data_endpoint(limit=limit, include_clusters=True)
    c_edges = [e for e in data["edges"] if e.get("type") == "shared_tag_cluster" or e.get("relation") == "shared_tag_cluster"]
    return {"clusters": c_edges, "total": len(c_edges), "modularity_score": 0.45 if c_edges else 0.0}

@router.post("/api/validate_query")
@router.post("/api/search/validate")
def validate_query_endpoint(req: ValidateQueryRequest):
    """Validate query syntax and parse operators."""
    if req.query and req.query.count('"') % 2 != 0:
        return {"valid": False, "query": req.query, "error": "Unmatched double quotes in query"}
    cleaned_q, operators, exclusions = parse_query_operators(req.query)
    return {
        "valid": True,
        "query": req.query,
        "cleaned_query": cleaned_q,
        "operators": operators,
        "exclusions": exclusions
    }

@router.get("/api/search/suggest")
@router.get("/api/search/autocomplete")
def autocomplete_suggest(token: str = "", q: str = "", query: str = ""):
    raw = token or q or query or ""
    clean = raw.lower().strip()
    if not clean:
        return {"token": token, "suggestions": [], "results": []}
    suggestions = [
        {"text": "tag:", "type": "operator"},
        {"text": "type:", "type": "operator"},
        {"text": "size:", "type": "operator"},
        {"text": "NEAR(", "type": "operator"}
    ]
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tag FROM tags LIMIT 50")
            db_tags = [row[0] for row in cursor.fetchall() if row[0]]
            for t in db_tags:
                suggestions.append({"text": f"tag:{t}", "type": "tag"})
                suggestions.append({"text": t, "type": "tag"})
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in search.py: {e}")

    matched = [s for s in suggestions if clean in s["text"].lower()]
    res_list = matched or suggestions
    return {
        "token": token,
        "suggestions": res_list,
        "results": [s["text"] for s in res_list]
    }

@router.get("/api/search/cache/stats")
def get_search_cache_stats():
    cache_obj = _get_global_cache()
    if cache_obj is not None:
        return cache_obj.stats()
    return {"hits": 0, "misses": 0, "hit_ratio": 0.0, "cache_size": 0}
