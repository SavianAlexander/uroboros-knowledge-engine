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
        return "", {}
    
    operators = {}
    cleaned_q = []
    
    tokens = re.findall(r'(?:[^\s"]+|"[^"]*")+', q_str)
    for token in tokens:
        if ':' in token:
            key, val = token.split(':', 1)
            val = val.strip('"').strip("'")
            operators[key.lower()] = val
        elif '>' in token or '<' in token:
            match = re.match(r'size([<>])(\d+)(kb|mb|bytes)?', token, re.IGNORECASE)
            if match:
                op, num, unit = match.groups()
                bytes_val = int(num)
                if unit:
                    unit = unit.lower()
                    if unit == 'kb':
                        bytes_val *= 1024
                    elif unit == 'mb':
                        bytes_val *= 1024 * 1024
                operators['size'] = (op, bytes_val)
            else:
                cleaned_q.append(token)
        else:
            cleaned_q.append(token)
            
    return " ".join(cleaned_q).strip(), operators

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
    return {
        "total_files": count or 0,
        "total_size": total_size or 0,
        "mime_breakdown": mime_breakdown,
        "timeline": timeline,
        "active_directory": os.path.abspath(ACTIVE_DIR)
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
        return {"status": "success", "filename": file.filename, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RuleRequest(BaseModel):
    pattern: str
    tag: str

@app.get("/api/search")
def search(q: str = None, tag: str = None, category: str = None, sort_by: str = None, sort_order: str = "asc", date_filter: str = "all", mode: str = "keyword"):
    if mode == "semantic" and q:
        # Run semantic concept retrieval
        results = know.MiniVectorEngine.search_semantic(q)
        
        # Apply filters in Python to keep it fast/lazy without complex SQL
        filtered = []
        import time
        now = time.time()
        
        for r in results:
            # tag filter
            if tag and tag not in r['tags']:
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
            
        return {"results": filtered}

    conn = know.get_db()
    cursor = conn.cursor()
    
    cleaned_q, ops = parse_query_operators(q)
    
    if cleaned_q:
        sql = """
            SELECT f.filepath, f.filename, f.file_size, f.mime_type, f.modified_at, f.id,
                   CASE 
                     WHEN snippet(fts_files, 2, '<mark>', '</mark>', '...', 15) LIKE '%<mark>%' THEN snippet(fts_files, 2, '<mark>', '</mark>', '...', 15)
                     WHEN snippet(fts_files, 3, '<mark>', '</mark>', '...', 15) LIKE '%<mark>%' THEN '[Note Match]: ' || snippet(fts_files, 3, '<mark>', '</mark>', '...', 15)
                     ELSE snippet(fts_files, 2, '<mark>', '</mark>', '...', 15)
                   END as snippet
            FROM fts_files
            JOIN files f ON f.filepath = fts_files.filepath
        """
        wheres = ["fts_files MATCH ?"]
        params = [cleaned_q]
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
        wheres.append("f.id IN (SELECT file_id FROM tags WHERE tag = ?)")
        params.append(tag_filter)
        
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
        
    conn.close()
    return {"results": rows}

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
    return {"status": "success"}

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
    cursor.execute("SELECT tag, COUNT(*) as count FROM tags GROUP BY tag ORDER BY count DESC")
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
    cursor.execute("SELECT id, pattern, tag FROM auto_rules ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"rules": rows}

@app.post("/api/rules")
def create_rule(req: RuleRequest):
    conn = know.get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO auto_rules (pattern, tag) VALUES (?, ?)", (req.pattern, req.tag))
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
def export_pdf_report(tag: str = None, category: str = None, style_template: str = "default", include_notes: bool = True):
    # ponytail: build a formatted PDF compilation of knowledge records using reportlab with category/tag queries
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    import io
    
    conn = know.get_db()
    cursor = conn.cursor()
    
    sql = "SELECT id, filename, filepath, content, notes, mime_type FROM files"
    wheres = []
    params = []
    
    if tag:
        wheres.append("id IN (SELECT file_id FROM tags WHERE tag = ?)")
        params.append(tag)
        
    if category:
        if category == 'documents':
            wheres.append("(mime_type LIKE 'text/%' OR filepath LIKE '%.pdf' OR filepath LIKE '%.docx' OR filepath LIKE '%.rtf')")
        elif category == 'spreadsheets':
            wheres.append("(mime_type LIKE '%spreadsheet%' OR filepath LIKE '%.xlsx' OR filepath LIKE '%.csv')")
        elif category == 'code':
            wheres.append("(filepath LIKE '%.py' OR filepath LIKE '%.js' OR filepath LIKE '%.html' OR filepath LIKE '%.css' OR filepath LIKE '%.json' OR filepath LIKE '%.xml')")
        elif category == 'images':
            wheres.append("(mime_type LIKE 'image/%' OR filepath LIKE '%.png' OR filepath LIKE '%.jpg' OR filepath LIKE '%.jpeg' OR filepath LIKE '%.bmp')")

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
    h2_style = styles['Heading2']
    body_style = styles['BodyText']
    
    title_text = "Uroboros Knowledge Database Summary Report"
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
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#6366f1")),
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
            
    doc.build(story)
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
