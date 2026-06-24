import os
import re
import time
import uvicorn
import sqlite3
import mimetypes
from collections import Counter
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import know

app = FastAPI(title="Uroboros Knowledge Database")

# Ensure DB is initialized
know.init_db()

# Track active directory
ACTIVE_DIR = "dumps"
if not os.path.exists(ACTIVE_DIR):
    os.makedirs(ACTIVE_DIR, exist_ok=True)

# Start real-time folder watcher
know.start_active_folder_watcher(ACTIVE_DIR)

# ponytail: simple Least Recently Used Query Cache helper
class QueryCache:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.cache = {} # key -> value
        self.order = []
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.order.remove(key)
            self.order.append(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key, value):
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = value
        self.order.append(key)

    def invalidate(self):
        self.cache.clear()
        self.order.clear()

GLOBAL_QUERY_CACHE = QueryCache()

class IndexRequest(BaseModel):
    directory: str

class TagRequest(BaseModel):
    filepath: str
    tag: str

class NotesRequest(BaseModel):
    filepath: str
    notes: str

class RenameRequest(BaseModel):
    filepath: str
    new_name: str

def parse_query_operators(q_str):
    if not q_str:
        return "", {}, {}
    
    operators = {}
    exclusions = {}
    cleaned_q = []
    
    # Detect and preserve NEAR() syntax tokens before splitting tokens
    near_matches = re.findall(r'NEAR\s*\(\s*(?:"[^"]+"|\w+)\s+(?:"[^"]+"|\w+)\s*,\s*\d+\s*\)', q_str, re.IGNORECASE)
    for nm in near_matches:
        q_str = q_str.replace(nm, f'"{nm}"') # temporary quote lock
        
    tokens = re.findall(r'(?:[^\s"]+|"[^"]*")+', q_str)
    for token in tokens:
        is_exclude = False
        t_val = token
        
        # Unlock quoted NEAR expression if matches
        if t_val.startswith('"NEAR') and t_val.endswith('"'):
            t_val = t_val.strip('"')
            
        if t_val.startswith('-') and len(t_val) > 1:
            is_exclude = True
            t_val = t_val[1:]
            
        if ':' in t_val:
            key, val = t_val.split(':', 1)
            val = val.strip('"').strip("'")
            if is_exclude:
                exclusions[key.lower()] = val
            else:
                operators[key.lower()] = val
        elif '>' in t_val or '<' in t_val:
            match = re.match(r'size([<>])(\d+)(kb|mb|bytes)?', t_val, re.IGNORECASE)
            if match:
                op, num, unit = match.groups()
                bytes_val = int(num)
                if unit:
                    unit = unit.lower()
                    if unit == 'kb':
                        bytes_val *= 1024
                    elif unit == 'mb':
                        bytes_val *= 1024 * 1024
                if is_exclude:
                    exclusions['size'] = (op, bytes_val)
                else:
                    operators['size'] = (op, bytes_val)
            else:
                if is_exclude:
                    exclusions['word'] = exclusions.get('word', []) + [t_val]
                else:
                    cleaned_q.append(t_val)
        else:
            if is_exclude:
                exclusions['word'] = exclusions.get('word', []) + [t_val]
            else:
                cleaned_q.append(t_val)
            
    return " ".join(cleaned_q).strip(), operators, exclusions

def suggest_tags_from_text(text):
    if not text:
        return []
    stopwords = {
        'the', 'and', 'of', 'to', 'is', 'in', 'that', 'it', 'for', 'on', 'with', 
        'as', 'this', 'was', 'at', 'by', 'an', 'be', 'are', 'from', 'or', 'your', 
        'have', 'had', 'has', 'but', 'not', 'what', 'all', 'were', 'when', 'we'
    }
    words = re.findall(r'\b[a-z]{3,15}\b', text.lower())
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:4]]

def generate_summary(text):
    # ponytail: extractive TF-IDF summarization using only standard python library algorithms
    if not text or len(text.strip()) < 100:
        return ""
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 3:
        return text.strip()
        
    words = re.findall(r'\b[a-z]{4,15}\b', text.lower())
    word_freq = Counter(words)
    
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        s_words = re.findall(r'\b[a-z]{4,15}\b', sentence.lower())
        for word in s_words:
            score += word_freq.get(word, 0)
        # Length normalization
        length = len(s_words)
        if length > 0:
            score = score / length
        sentence_scores.append((score, i, sentence))
        
    top_sentences = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:3]
    top_sentences = sorted(top_sentences, key=lambda x: x[1])
    return " ".join([s[2] for s in top_sentences]).strip()

@app.get("/")
def get_index():
    return FileResponse("index.html")

@app.get("/style.css")
def get_css():
    return FileResponse("style.css")

@app.get("/api/file/raw")
def get_raw_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)

@app.get("/app.js")
def get_js():
    return FileResponse("app.js")

@app.get("/api/stats")
def get_stats():
    conn = know.get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(file_size) FROM files")
    count, total_size = cursor.fetchone()
    
    cursor.execute("""
        SELECT mime_type, COUNT(*) as count, SUM(file_size) as size 
        FROM files 
        GROUP BY mime_type 
        ORDER BY count DESC 
        LIMIT 10
    """)
    mime_breakdown = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("""
        SELECT date(modified_at, 'unixepoch') as day, COUNT(*) as count 
        FROM files 
        WHERE modified_at IS NOT NULL
        GROUP BY day 
        ORDER BY day DESC 
        LIMIT 7
    """)
    timeline = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    import shutil
    try:
        total, used, free = shutil.disk_usage(ACTIVE_DIR)
    except Exception:
        total, used, free = 0, 0, 0
        
    return {
        "total_files": count or 0,
        "total_size": total_size or 0,
        "mime_breakdown": mime_breakdown,
        "timeline": timeline,
        "active_directory": os.path.abspath(ACTIVE_DIR),
        "disk_storage": {
            "free_bytes": free,
            "total_bytes": total,
            "free_percent": int((free / total) * 100) if total else 0
        }
    }

# Progress channel storage
import queue
progress_queues = []

@app.post("/api/index")
def trigger_index(req: IndexRequest):
    global ACTIVE_DIR
    if not os.path.isdir(req.directory):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    
    ACTIVE_DIR = req.directory
    know.start_active_folder_watcher(ACTIVE_DIR)
    
    # automated server index health check: verify available storage capacity
    import shutil
    total, used, free = shutil.disk_usage(req.directory)
    if free < 10 * 1024 * 1024:  # Alert if less than 10MB free
        raise HTTPException(status_code=507, detail="Insufficient storage capacity on drive")
    
    # Run index in a background thread to prevent blocking FastAPI async thread
    import threading
    def run_indexer():
        def progress_cb(filename, current, total):
            pct = int((current / total) * 100)
            data = f"data: {{\"filename\": \"{filename}\", \"pct\": {pct}, \"current\": {current}, \"total\": {total}}}\n\n"
            for q in list(progress_queues):
                q.put(data)
        
        try:
            know.index_directory(req.directory, progress_callback=progress_cb)
            # Send completion signal
            for q in list(progress_queues):
                q.put("data: {\"done\": true}\n\n")
        except Exception as e:
            for q in list(progress_queues):
                q.put(f"data: {{\"error\": \"{str(e)}\"}}\n\n")

    threading.Thread(target=run_indexer, daemon=True).start()
    return {"status": "success", "message": f"Successfully started indexing {req.directory}"}

from fastapi.responses import StreamingResponse

@app.get("/api/index/events")
def index_events():
    q = queue.Queue()
    progress_queues.append(q)
    
    def event_generator():
        try:
            while True:
                # yield indexing updates
                item = q.get()
                yield item
                if "done" in item or "error" in item:
                    break
        finally:
            if q in progress_queues:
                progress_queues.remove(q)
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists(ACTIVE_DIR):
        os.makedirs(ACTIVE_DIR, exist_ok=True)
        
    filepath = os.path.join(ACTIVE_DIR, file.filename)
    try:
        contents = await file.read()
        with open(filepath, "wb") as f:
            f.write(contents)
            
        stat = os.stat(filepath)
        file_size = stat.st_size
        modified_at = stat.st_mtime
        sha256 = know.calculate_sha256(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'
        
        content = ""
        coords = []
        suffix = os.path.splitext(file.filename)[1].lower()
        text_extensions = {
            '.md', '.py', '.txt', '.json', '.yaml', '.yml', '.ini', '.csv', '.xml', 
            '.html', '.css', '.js', '.pdf', '.docx', '.rtf', '.xlsx',
            '.png', '.jpg', '.jpeg', '.bmp'
        }
        if mime_type.startswith('text/') or suffix in text_extensions:
            content, coords = know.extract_content(filepath, suffix)
            
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
        row = cursor.fetchone()
        
        if row:
            file_id = row['id']
            cursor.execute("""
                UPDATE files 
                SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?
                WHERE filepath = ?
            """, (file.filename, file_size, mime_type, sha256, modified_at, content, filepath))
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))",
                           (filepath, file.filename, content, filepath))
            cursor.execute("DELETE FROM ocr_coords WHERE file_id = ?", (file_id,))
            for coord in coords:
                cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?)",
                               (file_id, coord['word'], coord['x'], coord['y'], coord['w'], coord['h']))
        else:
            cursor.execute("""
                INSERT INTO files (filepath, filename, file_size, mime_type, sha256, modified_at, content, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
            """, (filepath, file.filename, file_size, mime_type, sha256, modified_at, content))
            file_id = cursor.lastrowid
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, NULL)",
                           (filepath, file.filename, content))
            for coord in coords:
                cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?)",
                               (file_id, coord['word'], coord['x'], coord['y'], coord['w'], coord['h']))
            
        conn.commit()
        conn.close()
        # ponytail: invalidate cache on directory content modifications
        GLOBAL_QUERY_CACHE.invalidate()
        return {"status": "success", "filename": file.filename, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RuleRequest(BaseModel):
    pattern: str
    tag: str
    priority: int = 0

@app.get("/api/search")
def search(q: str = None, tag: str = None, category: str = None, sort_by: str = None, sort_order: str = "asc", date_filter: str = "all", mode: str = "keyword", snippet_limit: int = 15, highlight_start: str = "<mark>", highlight_end: str = "</mark>", folder_path: str = None, similarity_threshold: float = 0.0, tag_mode: str = "AND"):
    import time
    start_time = time.time()
    
    # ponytail: build a unique cache key based on query filters, threshold and tag mode
    cache_key = f"{q}:{tag}:{category}:{sort_by}:{sort_order}:{date_filter}:{mode}:{snippet_limit}:{highlight_start}:{highlight_end}:{folder_path}:{similarity_threshold}:{tag_mode}"
    cached_val = GLOBAL_QUERY_CACHE.get(cache_key)
    if cached_val is not None:
        # Update latency metric before returning
        res = dict(cached_val)
        res["search_time_ms"] = round((time.time() - start_time) * 1000, 2)
        res["cached"] = True
        return res

    synonyms_expanded = []
    conn = know.get_db()
    cursor = conn.cursor()
    
    # 1. Expand query macros if present (e.g. %macro_name%)
    if q:
        cursor.execute("SELECT name, expansion FROM query_macros")
        macros = {row['name']: row['expansion'] for row in cursor.fetchall()}
        for m_name, m_exp in macros.items():
            q = q.replace(f"%{m_name}%", m_exp)
            
        # 2. Expand FTS synonyms (expand individual search words using FTS OR)
        cursor.execute("SELECT word, substitutes FROM synonyms")
        syn_map = {row['word'].lower(): row['substitutes'] for row in cursor.fetchall()}
        expanded_words = []
        for w in q.split():
            clean_w = w.strip('"').lower()
            if clean_w in syn_map:
                syn_list = [clean_w] + [s.strip() for s in syn_map[clean_w].split(',')]
                expanded_words.append("(" + " OR ".join(syn_list) + ")")
                synonyms_expanded.append(f"{clean_w} -> {', '.join(syn_list)}")
            else:
                expanded_words.append(w)
        q = " ".join(expanded_words)
            
    if mode == "semantic" and q:
        # Run semantic concept retrieval
        results = know.MiniVectorEngine.search_semantic(q)
        
        # Apply filters in Python to keep it fast/lazy without complex SQL
        filtered = []
        import time
        now = time.time()
        
        for r in results:
            # tag filter (incorporating tag aliases and multi-tag modes)
            if tag:
                tag_list = [t.strip() for t in tag.split(",") if t.strip()]
                match_results = []
                for single_tag in tag_list:
                    cursor.execute("SELECT target FROM tag_aliases WHERE alias = ?", (single_tag,))
                    alias_row = cursor.fetchone()
                    tags_to_check = [single_tag]
                    if alias_row:
                        tags_to_check.append(alias_row['target'])
                    match_results.append(any(t in r['tags'] for t in tags_to_check))
                
                if tag_mode.upper() == "OR":
                    if not any(match_results):
                        continue
                else: # AND
                    if not all(match_results):
                        continue
            # folder path restriction filter
            if folder_path:
                norm_p = os.path.normpath(folder_path).lower()
                norm_f = os.path.normpath(r['filepath']).lower()
                if not norm_f.startswith(norm_p):
                    continue
            # category filter
            if category:
                ext = os.path.splitext(r['filepath'])[1].lower()
                mime = r['mime_type']
                if category == 'documents' and not (mime.startswith('text/') or ext in ['.pdf', '.docx', '.rtf']):
                    continue
                elif category == 'spreadsheets' and not ('spreadsheet' in mime or ext in ['.xlsx', '.csv']):
                    continue
                elif category == 'code' and not (ext in ['.py', '.js', '.html', '.css', '.json', '.xml']):
                    continue
                elif category == 'images' and not (mime.startswith('image/') or ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                    continue
            # date filter
            if date_filter and date_filter != "all":
                mtime = r['modified_at']
                if date_filter == "24h" and mtime < now - 86400:
                    continue
                elif date_filter == "week" and mtime < now - 604800:
                    continue
                elif date_filter == "month" and mtime < now - 2592000:
                    continue
                elif date_filter == "year" and mtime < now - 31536000:
                    continue
            # Filter by semantic cosine similarity threshold
            if similarity_threshold > 0.0 and r.get('score', 0) < similarity_threshold:
                continue
            filtered.append(r)
            
        # apply sorting
        rev = sort_order.lower() == "desc"
        if sort_by == "filename":
            filtered.sort(key=lambda x: x['filename'].lower(), reverse=rev)
        elif sort_by == "file_size":
            filtered.sort(key=lambda x: x['file_size'], reverse=rev)
        elif sort_by == "modified_at":
            filtered.sort(key=lambda x: x['modified_at'], reverse=rev)
        else: # sort by score/rank
            filtered.sort(key=lambda x: x.get('score', 0), reverse=rev)
            
        # ponytail: log search history parameters asynchronously/lazily
        try:
            conn_log = know.get_db()
            cursor_log = conn_log.cursor()
            cursor_log.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", (q, "semantic", time.time(), len(filtered)))
            conn_log.commit()
            conn_log.close()
        except Exception:
            pass

        conn.close()
        search_time = round((time.time() - start_time) * 1000, 2)
        
        # ponytail: generate qualitative query execution plan steps
        plan_steps = ["Macros Expansion"]
        if synonyms_expanded:
            plan_steps.append("Synonym Resolution")
        plan_steps.append("TF-IDF Vector Match")
        if tag:
            plan_steps.append("Tag Alias Resolve & Filter")
        if folder_path:
            plan_steps.append("Directory Tree Scoping")
        if category:
            plan_steps.append("Mime Category Filter")
        if date_filter and date_filter != "all":
            plan_steps.append("Date Modified Filter")
        plan_steps.append(f"In-Memory Sort ({sort_by})")
        
        response_data = {
            "results": filtered,
            "search_time_ms": search_time,
            "mode": "semantic",
            "synonyms_expanded": synonyms_expanded,
            "execution_plan": plan_steps
        }
        # ponytail: cache the query response
        GLOBAL_QUERY_CACHE.set(cache_key, response_data)
        return response_data

    cleaned_q, ops, exclusions = parse_query_operators(q)
    
    if cleaned_q:
        sql = f"""
            SELECT f.filepath, f.filename, f.file_size, f.mime_type, f.modified_at, f.id,
                   CASE 
                     WHEN snippet(fts_files, 2, ?, ?, '...', ?) LIKE ? THEN snippet(fts_files, 2, ?, ?, '...', ?)
                     WHEN snippet(fts_files, 3, ?, ?, '...', ?) LIKE ? THEN '[Note Match]: ' || snippet(fts_files, 3, ?, ?, '...', ?)
                     ELSE snippet(fts_files, 2, ?, ?, '...', ?)
                   END as snippet
            FROM fts_files
            JOIN files f ON f.filepath = fts_files.filepath
        """
        wheres = ["fts_files MATCH ?"]
        params = [
            highlight_start, highlight_end, snippet_limit, f"%{highlight_start}%",
            highlight_start, highlight_end, snippet_limit,
            highlight_start, highlight_end, snippet_limit, f"%{highlight_start}%",
            highlight_start, highlight_end, snippet_limit,
            highlight_start, highlight_end, snippet_limit,
            cleaned_q
        ]
    else:
        sql = """
            SELECT f.filepath, f.filename, f.file_size, f.mime_type, f.modified_at, f.id,
                   SUBSTR(f.content, 1, 120) as snippet
            FROM files f
        """
        wheres = []
        params = []
        
    tag_filter = ops.get('tag') or tag
    if tag_filter:
        tag_list = [t.strip() for t in tag_filter.split(",") if t.strip()]
        tag_wheres = []
        for single_tag in tag_list:
            cursor.execute("SELECT target FROM tag_aliases WHERE alias = ?", (single_tag,))
            alias_row = cursor.fetchone()
            if alias_row:
                tag_wheres.append("(f.id IN (SELECT file_id FROM tags WHERE tag = ?) OR f.id IN (SELECT file_id FROM tags WHERE tag = ?))")
                params.append(single_tag)
                params.append(alias_row['target'])
            else:
                tag_wheres.append("f.id IN (SELECT file_id FROM tags WHERE tag = ?)")
                params.append(single_tag)
        
        if tag_wheres:
            joiner = " OR " if tag_mode.upper() == "OR" else " AND "
            wheres.append("(" + joiner.join(tag_wheres) + ")")
        
    file_type = ops.get('type') or ops.get('ext')
    if file_type:
        wheres.append("f.filepath LIKE ?")
        params.append(f"%.{file_type}")
        
    file_name = ops.get('name')
    if file_name:
        wheres.append("f.filename LIKE ?")
        params.append(f"%{file_name}%")
        
    if 'size' in ops:
        op, bytes_val = ops['size']
        if op == '>':
            wheres.append("f.file_size > ?")
        else:
            wheres.append("f.file_size < ?")
        params.append(bytes_val)
        
    # Subdirectory Path Filter
    if folder_path:
        wheres.append("f.filepath LIKE ?")
        params.append(f"{folder_path}%")
        
    # Apply exclusions to wheres
    if 'tag' in exclusions:
        wheres.append("f.id NOT IN (SELECT file_id FROM tags WHERE tag = ?)")
        params.append(exclusions['tag'])
    if 'type' in exclusions or 'ext' in exclusions:
        wheres.append("f.filepath NOT LIKE ?")
        params.append(f"%.{exclusions.get('type') or exclusions.get('ext')}")
    if 'name' in exclusions:
        wheres.append("f.filename NOT LIKE ?")
        params.append(f"%{exclusions['name']}%")
    if 'size' in exclusions:
        ex_op, ex_val = exclusions['size']
        if ex_op == '>':
            wheres.append("f.file_size <= ?")
        else:
            wheres.append("f.file_size >= ?")
        params.append(ex_val)
    if 'word' in exclusions:
        for w in exclusions['word']:
            wheres.append("f.filepath NOT IN (SELECT filepath FROM fts_files WHERE fts_files MATCH ?)")
            params.append(w)
        
    if category:
        if category == 'documents':
            wheres.append("(f.mime_type LIKE 'text/%' OR f.filepath LIKE '%.pdf' OR f.filepath LIKE '%.docx' OR f.filepath LIKE '%.rtf')")
        elif category == 'spreadsheets':
            wheres.append("(f.mime_type LIKE '%spreadsheet%' OR f.filepath LIKE '%.xlsx' OR f.filepath LIKE '%.csv')")
        elif category == 'code':
            wheres.append("(f.filepath LIKE '%.py' OR f.filepath LIKE '%.js' OR f.filepath LIKE '%.html' OR f.filepath LIKE '%.css' OR f.filepath LIKE '%.json' OR f.filepath LIKE '%.xml')")
        elif category == 'images':
            wheres.append("(f.mime_type LIKE 'image/%' OR f.filepath LIKE '%.png' OR f.filepath LIKE '%.jpg' OR f.filepath LIKE '%.jpeg' OR f.filepath LIKE '%.bmp')")
            
    # Date Filtering
    if date_filter and date_filter != "all":
        now = time.time()
        if date_filter == "24h":
            wheres.append("f.modified_at > ?")
            params.append(now - 86400)
        elif date_filter == "week":
            wheres.append("f.modified_at > ?")
            params.append(now - 604800)
        elif date_filter == "month":
            wheres.append("f.modified_at > ?")
            params.append(now - 2592000)
        elif date_filter == "year":
            wheres.append("f.modified_at > ?")
            params.append(now - 31536000)
            
    if wheres:
        sql += " WHERE " + " AND ".join(wheres)
        
    # Query Sorting
    order_clause = ""
    # Map sorting values
    valid_sorts = {
        "filename": "f.filename",
        "file_size": "f.file_size",
        "modified_at": "f.modified_at",
        "rank": "rank"
    }
    target_sort = valid_sorts.get(sort_by)
    if not target_sort:
        target_sort = "rank" if cleaned_q else "f.filename"
        
    direction = "ASC" if sort_order.lower() == "asc" else "DESC"
    order_clause = f" ORDER BY {target_sort} {direction}"
    
    sql += order_clause + " LIMIT 50"
    
    cursor.execute(sql, params)
    rows = [dict(row) for row in cursor.fetchall()]
    
    for r in rows:
        cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (r['id'],))
        r['tags'] = [t['tag'] for t in cursor.fetchall()]
        
    # ponytail: log search history parameters asynchronously/lazily
    try:
        conn_log = know.get_db()
        cursor_log = conn_log.cursor()
        cursor_log.execute("INSERT INTO search_history (query_string, search_mode, executed_at, result_count) VALUES (?, ?, ?, ?)", (q or "", "keyword" if cleaned_q else "all_files", time.time(), len(rows)))
        conn_log.commit()
        conn_log.close()
    except Exception:
        pass

    conn.close()
    search_time = round((time.time() - start_time) * 1000, 2)
    
    # ponytail: generate qualitative query execution plan steps
    plan_steps = ["Macros Expansion"]
    if synonyms_expanded:
        plan_steps.append("Synonym Resolution")
    if cleaned_q:
        plan_steps.append("FTS5 Match Scan")
    else:
        plan_steps.append("Full Table Scan")
    if tag_filter:
        plan_steps.append("Tag Alias Resolve & Filter")
    if file_type or file_name or 'size' in ops:
        plan_steps.append("Metadata Operators Filter")
    if folder_path:
        plan_steps.append("Directory Path Scoping")
    if category:
        plan_steps.append("Mime Category Filter")
    if date_filter and date_filter != "all":
        plan_steps.append("Date Modified Filter")
    plan_steps.append(f"SQL Index Sort ({sort_by})")
    
    response_data = {
        "results": rows,
        "search_time_ms": search_time,
        "mode": "keyword" if cleaned_q else "all_files",
        "synonyms_expanded": synonyms_expanded,
        "execution_plan": plan_steps
    }
    # ponytail: cache the query response
    GLOBAL_QUERY_CACHE.set(cache_key, response_data)
    return response_data

@app.get("/api/search/history")
def get_search_history():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT query_string, search_mode, executed_at, result_count FROM search_history ORDER BY executed_at DESC LIMIT 10")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"history": rows}

# ponytail: search bookmarks models and endpoints
class BookmarkRequest(BaseModel):
    name: str
    query_string: str
    search_mode: str

@app.post("/api/bookmarks")
def add_bookmark(req: BookmarkRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO query_bookmarks (name, query_string, search_mode, created_at) VALUES (?, ?, ?, ?)",
                       (req.name, req.query_string, req.search_mode, time.time()))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    conn.close()
    return {"status": "ok"}

@app.get("/api/bookmarks")
def get_bookmarks():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, query_string, search_mode FROM query_bookmarks ORDER BY name ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"bookmarks": rows}

@app.delete("/api/bookmarks")
def delete_bookmark(id: int):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM query_bookmarks WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# ponytail: query cache statistics API
@app.get("/api/search/cache/stats")
def get_cache_stats():
    total_requests = GLOBAL_QUERY_CACHE.hits + GLOBAL_QUERY_CACHE.misses
    hit_ratio = round((GLOBAL_QUERY_CACHE.hits / total_requests) * 100, 2) if total_requests > 0 else 0.0
    return {
        "hits": GLOBAL_QUERY_CACHE.hits,
        "misses": GLOBAL_QUERY_CACHE.misses,
        "hit_ratio": hit_ratio,
        "cache_size": len(GLOBAL_QUERY_CACHE.cache)
    }

@app.get("/api/file")
def get_file(path: str):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filepath, filename, file_size, mime_type, sha256, modified_at, content, notes FROM files WHERE filepath = ?", (path,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")
    
    file_id = row['id']
    cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (file_id,))
    tags = [t['tag'] for t in cursor.fetchall()]
    
    # Query bounding coordinates for dynamic preview drawing
    cursor.execute("SELECT word, x, y, w, h FROM ocr_coords WHERE file_id = ?", (file_id,))
    coords = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    res = dict(row)
    res['tags'] = tags
    res['suggested_tags'] = suggest_tags_from_text(row['content'])
    res['coords'] = coords
    
    # Check if audio format
    suffix = os.path.splitext(row['filename'])[1].lower()
    if suffix in ['.mp3', '.wav']:
        res['audio_metadata'] = know.parse_audio_metadata(row['filepath'])
        
    # Calculate text metrics and generate summary
    content = row['content'] or ""
    res['word_count'] = len(content.split())
    res['char_count'] = len(content)
    res['paragraph_count'] = len([p for p in content.split('\n\n') if p.strip()])
    res['summary'] = generate_summary(content)
    
    return res

@app.post("/api/file/tag")
def add_tag(req: TagRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM files WHERE filepath = ?", (req.filepath,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        cursor.execute("INSERT INTO tags (file_id, tag) VALUES (?, ?)", (row['id'], req.tag))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()
    GLOBAL_QUERY_CACHE.invalidate()
    return {"status": "success"}

@app.delete("/api/file/tag")
def remove_tag(filepath: str, tag: str):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")
        
    cursor.execute("DELETE FROM tags WHERE file_id = ? AND tag = ?", (row['id'], tag))
    conn.commit()
    conn.close()
    GLOBAL_QUERY_CACHE.invalidate()
    return {"status": "success"}

@app.post("/api/file/notes")
def update_notes(req: NotesRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM files WHERE filepath = ?", (req.filepath,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="File not found")
        
    cursor.execute("UPDATE files SET notes = ? WHERE filepath = ?", (req.notes, req.filepath))
    cursor.execute("UPDATE fts_files SET notes = ? WHERE filepath = ?", (req.notes, req.filepath))
    conn.commit()
    conn.close()
    GLOBAL_QUERY_CACHE.invalidate()
    return {"status": "success"}

class TagColorRequest(BaseModel):
    tag: str
    color: str

class BulkDeleteRequest(BaseModel):
    filepaths: list[str]

@app.post("/api/tags/color")
def set_tag_color(req: TagColorRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tag_metadata (tag, color) 
        VALUES (?, ?) 
        ON CONFLICT(tag) DO UPDATE SET color = excluded.color
    """, (req.tag, req.color))
    conn.commit()
    conn.close()
    return {"status": "success"}

class MacroRequest(BaseModel):
    name: str
    expansion: str

class AliasRequest(BaseModel):
    alias: str
    target: str

@app.get("/api/macros")
def get_macros():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, expansion FROM query_macros")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"macros": rows}

@app.post("/api/macros")
def set_macro(req: MacroRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO query_macros (name, expansion) VALUES (?, ?)", (req.name, req.expansion))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/api/macros")
def delete_macro(name: str):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM query_macros WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return {"status": "success"}


# ponytail: query syntax validator endpoint
class ValidateQueryRequest(BaseModel):
    query: str

@app.post("/api/search/validate")
def validate_search_query(req: ValidateQueryRequest):
    q = req.query.strip()
    if not q:
        return {"valid": True, "error": None, "suggestion": None}
        
    # Check unmatched quotes
    if q.count('"') % 2 != 0:
        return {
            "valid": False,
            "error": "Unmatched double quotes",
            "suggestion": "Close double quotes to balance string parameters."
        }
        
    # Check malformed operators
    tokens = re.findall(r'(?:[^\s"]+|"[^"]*")+', q)
    for token in tokens:
        if ':' in token:
            key, val = token.split(':', 1)
            if not val.strip():
                return {
                    "valid": False,
                    "error": f"Empty value for operator '{key}'",
                    "suggestion": f"Specify a filter parameter after '{key}:'"
                }
        elif '>' in token or '<' in token:
            if 'size' in token.lower():
                match = re.match(r'size([<>])(\d+)(kb|mb|bytes)?', token, re.IGNORECASE)
                if not match:
                    return {
                        "valid": False,
                        "error": f"Invalid size parameter operator: '{token}'",
                        "suggestion": "Use correct size syntax, e.g., 'size>500kb' or 'size<10mb'"
                    }
    return {"valid": True, "error": None, "suggestion": None}

# ponytail: query completion autosuggest route
@app.get("/api/search/suggest")
def get_search_suggestions(token: str = ""):
    token_clean = token.lower().strip()
    if not token_clean:
        return {"suggestions": []}
        
    suggestions = []
    
    # Suggest Operators/Keywords
    operator_keys = ["tag:", "type:", "ext:", "name:", "size>", "size<", "-tag:", "-type:", "-name:", "-word:"]
    for op in operator_keys:
        if op.startswith(token_clean):
            suggestions.append({"text": op, "type": "operator"})
            
    # Suggest Tags from DB
    conn = know.get_db()
    cursor = conn.cursor()
    if token_clean.startswith("tag:") or token_clean.startswith("-tag:"):
        prefix = token_clean.split("tag:", 1)[1]
        cursor.execute("SELECT DISTINCT tag FROM tags WHERE tag LIKE ?", (f"{prefix}%",))
        for row in cursor.fetchall():
            tag_op = token_clean.split("tag:", 1)[0] + "tag:"
            suggestions.append({"text": f"{tag_op}{row['tag']}", "type": "tag"})
    else:
        cursor.execute("SELECT DISTINCT tag FROM tags WHERE tag LIKE ? LIMIT 5", (f"{token_clean}%",))
        for row in cursor.fetchall():
            suggestions.append({"text": f"tag:{row['tag']}", "type": "tag"})
            
    # Suggest Macros
    cursor.execute("SELECT name FROM query_macros")
    for row in cursor.fetchall():
        macro_text = f"%{row['name']}%"
        if macro_text.lower().startswith(token_clean) or row['name'].lower().startswith(token_clean.strip("%")):
            suggestions.append({"text": macro_text, "type": "macro"})
            
    conn.close()
    return {"suggestions": suggestions[:10]}

class SynonymRequest(BaseModel):
    word: str
    substitutes: str

class BackupScheduleRequest(BaseModel):
    interval_seconds: int

@app.get("/api/synonyms")
def get_synonyms():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word, substitutes FROM synonyms")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"synonyms": rows}

@app.post("/api/synonyms")
def set_synonym(req: SynonymRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO synonyms (word, substitutes) VALUES (?, ?)", (req.word, req.substitutes))
    conn.commit()
    conn.close()
    return {"status": "success"}

import threading
import shutil
import time

backup_thread = None
backup_interval = 0
backup_cancel = threading.Event()

def backup_loop():
    global backup_interval
    while not backup_cancel.is_set():
        if backup_interval > 0:
            try:
                shutil.copy2("knowledge.db", f"knowledge.db.backup-{int(time.time())}")
            except Exception as e:
                print(f"Periodic backup failed: {e}")
            # Sleep in small slices to remain responsive to cancel
            for _ in range(backup_interval):
                if backup_cancel.is_set():
                    break
                time.sleep(1)
        else:
            time.sleep(1)

@app.post("/api/backups/schedule")
def schedule_backup(req: BackupScheduleRequest):
    global backup_thread, backup_interval
    backup_interval = req.interval_seconds
    if backup_thread is None:
        backup_cancel.clear()
        backup_thread = threading.Thread(target=backup_loop, daemon=True)
        backup_thread.start()
    return {"status": "success", "interval_seconds": backup_interval}

@app.get("/api/aliases")
def get_aliases():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT alias, target FROM tag_aliases")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"aliases": rows}

@app.post("/api/aliases")
def set_alias(req: AliasRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tag_aliases (alias, target) VALUES (?, ?)", (req.alias, req.target))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/file/bulk-delete")
def bulk_delete_files(req: BulkDeleteRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    deleted = []
    errors = []
    
    for path in req.filepaths:
        if os.path.exists(path):
            try:
                os.remove(path)
                cursor.execute("DELETE FROM files WHERE filepath = ?", (path,))
                cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (path,))
                deleted.append(path)
            except Exception as e:
                errors.append(f"Failed to delete {path}: {str(e)}")
        else:
            # File missing on disk, clear DB entry anyway
            cursor.execute("DELETE FROM files WHERE filepath = ?", (path,))
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (path,))
            deleted.append(path)
            
    conn.commit()
    conn.close()
    
    if errors:
        raise HTTPException(status_code=207, detail={"status": "partial", "deleted": deleted, "errors": errors})
    return {"status": "success", "deleted": deleted}

@app.delete("/api/file/delete")
def delete_file(path: str):
    if not os.path.exists(path):
         raise HTTPException(status_code=404, detail="Physical file does not exist")
         
    try:
        os.remove(path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete local disk file: {str(e)}")
        
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM files WHERE filepath = ?", (path,))
    cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (path,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/file/rename")
def rename_file(req: RenameRequest):
    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=404, detail="Physical file does not exist")
        
    parent_dir = os.path.dirname(req.filepath)
    new_filepath = os.path.join(parent_dir, req.new_name)
    
    if os.path.exists(new_filepath):
        raise HTTPException(status_code=400, detail="Target filename already exists")
        
    try:
        os.rename(req.filepath, new_filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rename local file: {str(e)}")
        
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE files 
        SET filepath = ?, filename = ? 
        WHERE filepath = ?
    """, (new_filepath, req.new_name, req.filepath))
    cursor.execute("""
        UPDATE fts_files 
        SET filepath = ?, filename = ? 
        WHERE filepath = ?
    """, (new_filepath, req.new_name, req.filepath))
    conn.commit()
    conn.close()
    return {"status": "success", "new_filepath": new_filepath}

@app.get("/api/tags")
def get_all_tags():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.tag, COUNT(*) as count, m.color 
        FROM tags t
        LEFT JOIN tag_metadata m ON t.tag = m.tag
        GROUP BY t.tag 
        ORDER BY count DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"tags": rows}

@app.get("/api/duplicates")
def get_duplicates():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sha256, COUNT(*) as count, group_concat(filepath, '||') as paths, group_concat(filename, '||') as names
        FROM files 
        WHERE sha256 IS NOT NULL AND sha256 != ''
        GROUP BY sha256 
        HAVING count > 1
        ORDER BY count DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    duplicates = []
    for r in rows:
        paths = r['paths'].split('||')
        names = r['names'].split('||')
        files = [{"filename": n, "filepath": p} for n, p in zip(names, paths)]
        duplicates.append({
            "sha256": r['sha256'],
            "count": r['count'],
            "files": files
        })
    return {"duplicates": duplicates}

@app.get("/api/tree")
def get_tree():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, filename FROM files ORDER BY filepath ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"files": rows}

@app.get("/api/rules")
def get_rules():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pattern, tag, priority FROM auto_rules ORDER BY priority DESC, id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"rules": rows}

@app.post("/api/rules")
def create_rule(req: RuleRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO auto_rules (pattern, tag, priority) VALUES (?, ?, ?)", (req.pattern, req.tag, req.priority))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Pattern rule already exists")
    finally:
        conn.close()
    return {"status": "success"}

@app.delete("/api/rules")
def delete_rule(id: int):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM auto_rules WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/rules/test-preview")
def test_rule_preview(req: RuleRequest):
    # ponytail: pre-run pattern match to list affected documents before applying the rule
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, filename, content FROM files")
    files = cursor.fetchall()
    conn.close()
    
    matches = []
    try:
        rx = re.compile(req.pattern, re.IGNORECASE)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid regex pattern: {str(e)}")
        
    for f in files:
        filepath = f['filepath']
        filename = f['filename']
        content = f['content'] or ""
        if rx.search(filepath) or rx.search(content):
            matches.append({"filepath": filepath, "filename": filename})
            
    return {"matches": matches}

class PeerRequest(BaseModel):
    address: str
    name: str

class SyncExchangeRequest(BaseModel):
    target_peer: str

@app.get("/api/sync/peers")
def get_peers():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, address, name FROM sync_peers ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"peers": rows}

@app.post("/api/sync/peers")
def add_peer(req: PeerRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", (req.address, req.name))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Peer address already registered")
    finally:
        conn.close()
    return {"status": "success"}

@app.delete("/api/sync/peers")
def delete_peer(id: int):
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sync_peers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# exchange list files
@app.get("/api/sync/manifest")
def sync_manifest():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filepath, filename, file_size, sha256, modified_at, content FROM files")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"manifest": rows}

@app.post("/api/sync/exchange")
def exchange_payload(req: SyncExchangeRequest):
    # ponytail: lightweight LAN syncing pulling manifest, performing sha256 diff, and uploading missing records.
    import urllib.request
    import json
    
    url = f"{req.target_peer}/api/sync/manifest"
    try:
        req_net = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_net, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            peer_manifest = data.get("manifest", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reach peer: {str(e)}")
        
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT sha256 FROM files WHERE sha256 IS NOT NULL")
    local_hashes = {row['sha256'] for row in cursor.fetchall()}
    
    synced_files = []
    for item in peer_manifest:
        if item['sha256'] and item['sha256'] not in local_hashes:
            # Recreate file locally under ACTIVE_DIR to sync physical disk files
            local_path = os.path.join(ACTIVE_DIR, item['filename'])
            # Note: We index text/raw contents over network in this simple LAN protocol
            try:
                with open(local_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(item['content'] or "")
            except Exception:
                pass
            
            # Insert into database
            try:
                cursor.execute("""
                    INSERT INTO files (filepath, filename, file_size, mime_type, sha256, modified_at, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (local_path, item['filename'], item['file_size'], 'application/octet-stream', item['sha256'], item['modified_at'], item['content']))
                cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, NULL)",
                               (local_path, item['filename'], item['content']))
                synced_files.append(item['filename'])
            except sqlite3.IntegrityError:
                pass
                
    conn.commit()
    conn.close()
    return {"status": "success", "synced": synced_files}

class FileEditRequest(BaseModel):
    filepath: str
    content: str

@app.post("/api/file/edit")
def edit_file(req: FileEditRequest):
    if not os.path.exists(req.filepath):
        raise HTTPException(status_code=404, detail="File does not exist")
    try:
        with open(req.filepath, "w", encoding="utf-8", errors="ignore") as f:
            f.write(req.content)
            
        stat = os.stat(req.filepath)
        file_size = stat.st_size
        modified_at = stat.st_mtime
        sha256 = know.calculate_sha256(req.filepath)
        
        # Extract content & coords tuple
        content_txt, coords = know.extract_content(req.filepath, os.path.splitext(req.filepath)[1].lower())
        
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE files 
            SET file_size = ?, sha256 = ?, modified_at = ?, content = ?
            WHERE filepath = ?
        """, (file_size, sha256, modified_at, content_txt, req.filepath))
        
        cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (req.filepath,))
        cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))",
                       (req.filepath, os.path.basename(req.filepath), content_txt, req.filepath))
        
        cursor.execute("DELETE FROM ocr_coords WHERE file_id = (SELECT id FROM files WHERE filepath = ?)", (req.filepath,))
        for coord in coords:
            cursor.execute("INSERT INTO ocr_coords (file_id, word, x, y, w, h) VALUES ((SELECT id FROM files WHERE filepath = ?), ?, ?, ?, ?, ?)",
                           (req.filepath, coord['word'], coord['x'], coord['y'], coord['w'], coord['h']))
            
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/snapshots")
def get_snapshots():
    return {"snapshots": know.list_db_snapshots()}

@app.post("/api/snapshots")
def create_snapshot():
    ts = know.create_db_snapshot()
    return {"status": "success", "timestamp": ts}

@app.post("/api/snapshots/restore")
def restore_snapshot(timestamp: int):
    ok = know.restore_db_snapshot(timestamp)
    if not ok:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return {"status": "success"}

@app.delete("/api/snapshots")
def delete_snapshot(timestamp: int):
    path = f"knowledge.db.snapshot-{timestamp}"
    if os.path.exists(path):
        os.remove(path)
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Snapshot file not found")

@app.get("/api/graph")
def get_graph():
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filepath, filename, content FROM files")
    files = [dict(row) for row in cursor.fetchall()]
    
    nodes = []
    links = []
    
    file_map = {}
    for f in files:
        nodes.append({"id": f["id"], "label": f["filename"], "filename": f["filename"]})
        file_map[f["filename"].lower()] = f["id"]
        
    for f in files:
        text = f["content"] or ""
        # 1. Wiki link matching: [[Filename]]
        matches = re.findall(r'\[\[([^\]]+)\]\]', text)
        for m in matches:
            target_name = m.strip().lower()
            if target_name in file_map:
                links.append({"source": f["id"], "target": file_map[target_name], "weight": 2})
                
        # 2. Extract matching tag links
        cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (f["id"],))
        file_tags = {t['tag'] for t in cursor.fetchall()}
        
        # Link files sharing same tags
        for f2 in files:
            if f2["id"] <= f["id"]:
                continue
            cursor.execute("SELECT tag FROM tags WHERE file_id = ?", (f2["id"],))
            f2_tags = {t['tag'] for t in cursor.fetchall()}
            shared = file_tags.intersection(f2_tags)
            if shared:
                links.append({"source": f["id"], "target": f2["id"], "weight": len(shared)})
                
    conn.close()
    return {"nodes": nodes, "links": links}

@app.get("/api/report/export")
def export_pdf_report(tag: str = None, category: str = None, style_template: str = "default", include_notes: bool = True, folder_path: str = None, report_title: str = None, theme_palette: str = "indigo"):
    # ponytail: build a formatted PDF compilation of knowledge records using reportlab with category/tag queries
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    import io
    
    palette_map = {
        "indigo": colors.HexColor("#6366f1"),
        "crimson": colors.HexColor("#e11d48"),
        "emerald": colors.HexColor("#059669"),
        "charcoal": colors.HexColor("#374151")
    }
    primary_color = palette_map.get(theme_palette.lower(), colors.HexColor("#6366f1"))

    
    conn = know.get_db()
    cursor = conn.cursor()
    
    # Retrieve tag metadata colors mapping
    cursor.execute("SELECT tag, color FROM tag_metadata WHERE color IS NOT NULL")
    tag_color_map = {row['tag']: row['color'] for row in cursor.fetchall()}
    
    sql = "SELECT id, filename, filepath, content, notes, mime_type FROM files"
    wheres = []
    params = []
    
    if tag:
        tag_list = [t.strip() for t in tag.split(",") if t.strip()]
        if tag_list:
            placeholders = ",".join(["?"] * len(tag_list))
            wheres.append(f"id IN (SELECT file_id FROM tags WHERE tag IN ({placeholders}))")
            params.extend(tag_list)
        
    if category:
        if category == 'documents':
            wheres.append("(mime_type LIKE 'text/%' OR filepath LIKE '%.pdf' OR filepath LIKE '%.docx' OR filepath LIKE '%.rtf')")
        elif category == 'spreadsheets':
            wheres.append("(mime_type LIKE '%spreadsheet%' OR filepath LIKE '%.xlsx' OR filepath LIKE '%.csv')")
        elif category == 'code':
            wheres.append("(filepath LIKE '%.py' OR filepath LIKE '%.js' OR filepath LIKE '%.html' OR filepath LIKE '%.css' OR filepath LIKE '%.json' OR filepath LIKE '%.xml')")
        elif category == 'images':
            wheres.append("(mime_type LIKE 'image/%' OR filepath LIKE '%.png' OR filepath LIKE '%.jpg' OR filepath LIKE '%.jpeg' OR filepath LIKE '%.bmp')")

    if folder_path:
        wheres.append("filepath LIKE ?")
        params.append(f"{folder_path}%")

    if wheres:
        sql += " WHERE " + " AND ".join(wheres)
    sql += " ORDER BY id DESC LIMIT 50"
    
    cursor.execute(sql, params)
    files = cursor.fetchall()
    conn.close()
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.textColor = primary_color
    h2_style = styles['Heading2']
    h2_style.textColor = primary_color
    body_style = styles['BodyText']
    
    title_text = report_title if report_title else "Uroboros Knowledge Database Summary Report"
    if tag or category:
        subparts = []
        if category: subparts.append(f"Category: {category}")
        if tag: subparts.append(f"Tag: {tag}")
        title_text += f" ({', '.join(subparts)})"
        
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 20))
    
    if not files:
        story.append(Paragraph("No files indexed matching selected criteria.", body_style))
    elif style_template == "compact":
        # Renders compact style template as a ReportLab Table
        data = [["#", "Filename", "Annotations Note"]]
        for idx, f in enumerate(files):
            notes_str = (f['notes'] or "[No custom annotations]") if include_notes else "[Notes Excluded]"
            data.append([str(idx + 1), f['filename'], notes_str])
            
        t = Table(data, colWidths=[30, 200, 274])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f4f4f5")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#e4e4e7")),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        story.append(t)
    elif style_template == "descriptive":
        # Renders descriptive cards template
        for idx, f in enumerate(files):
            notes_str = (f['notes'] or "[No annotations recorded]") if include_notes else "[Notes Excluded]"
            snippet_str = (f['content'] or "")[:200] + "..." if len(f['content'] or "") > 200 else (f['content'] or "[Empty]")
            
            card_data = [
                [Paragraph(f"<b>Document #{idx+1}: {f['filename']}</b>", h2_style)],
                [Paragraph(f"<i>Annotations:</i> {notes_str}", body_style)],
                [Paragraph(f"<i>Content Snippet:</i> {snippet_str}", body_style)]
            ]
            t = Table(card_data, colWidths=[504])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
    elif style_template == "gallery":
        # Renders grid gallery layout using a two-column Table
        cards = []
        for idx, f in enumerate(files):
            notes_str = (f['notes'] or "[No annotations]") if include_notes else "[Notes Excluded]"
            snippet_str = (f['content'] or "")[:120] + "..." if len(f['content'] or "") > 120 else (f['content'] or "[Empty]")
            
            card_content = [
                Paragraph(f"<b>#{idx+1}: {f['filename']}</b>", h2_style),
                Paragraph(f"<i>Mime:</i> {f['mime_type']}", body_style),
                Paragraph(f"<i>Notes:</i> {notes_str}", body_style),
                Paragraph(f"<i>Snippet:</i> {snippet_str}", body_style)
            ]
            cell_table = Table([[c] for c in card_content], colWidths=[240])
            cell_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            cards.append(cell_table)
            
        # Group into pairs for two-column grid
        grid_data = []
        for i in range(0, len(cards), 2):
            row = [cards[i]]
            if i + 1 < len(cards):
                row.append(cards[i+1])
            else:
                row.append("") # empty cell for grid alignment
            grid_data.append(row)
            
        if grid_data:
            grid_table = Table(grid_data, colWidths=[250, 250])
            grid_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(grid_table)
    elif style_template == "toc":
        # ponytail: build Table of Contents directory pointing to detailing document paragraphs
        story.append(Paragraph("<b>Table of Contents Directory</b>", h2_style))
        story.append(Spacer(1, 10))
        for idx, f in enumerate(files):
            # Compact TOC layout entry using inline spacing dots
            toc_text = f"• Document #{idx+1}: {f['filename']} ................................................................ Details Section"
            story.append(Paragraph(toc_text, body_style))
        story.append(Spacer(1, 25))
        
        # Details listings section
        for idx, f in enumerate(files):
            story.append(Paragraph(f"Details: #{idx+1} {f['filename']}", h2_style))
            story.append(Spacer(1, 5))
            content_snippet = (f['content'] or "")[:300] + "..." if len(f['content'] or "") > 300 else (f['content'] or "[Empty]")
            story.append(Paragraph(f"Content Summary: {content_snippet}", body_style))
            story.append(Spacer(1, 10))
    else:
        # Default report list paragraphs
        for idx, f in enumerate(files):
            story.append(Paragraph(f"{idx+1}. Document: {f['filename']}", h2_style))
            story.append(Spacer(1, 10))
            
            content_snippet = (f['content'] or "")[:300] + "..." if len(f['content'] or "") > 300 else (f['content'] or "[Empty]")
            story.append(Paragraph(f"Content Summary: {content_snippet}", body_style))
            story.append(Spacer(1, 10))
            
            if include_notes:
                notes_str = f"Personal Annotations: {f['notes']}" if f['notes'] else "Personal Annotations: None"
                story.append(Paragraph(notes_str, body_style))
                story.append(Spacer(1, 15))
            
    # Two-pass canvas page number compiler
    from reportlab.pdfgen import canvas
    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#71717a"))
            text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 54, 36, text)
            self.restoreState()

    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=uroboros-summary-report.pdf"})

@app.get("/api/stats/export")
def export_stats_csv():
    # ponytail: compile mime count stats into a clean exportable CSV download
    import csv
    import io
    from fastapi.responses import StreamingResponse
    
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT mime_type, COUNT(*) as count, SUM(file_size) as size FROM files GROUP BY mime_type ORDER BY count DESC")
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mime Type", "File Count", "Total Size (bytes)"])
    
    for r in rows:
        writer.writerow([r["mime_type"], r["count"], r["size"] or 0])
        
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8')), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=uroboros-db-stats.csv"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
