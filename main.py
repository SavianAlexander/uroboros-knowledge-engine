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

@app.post("/api/index")
def trigger_index(req: IndexRequest):
    global ACTIVE_DIR
    if not os.path.isdir(req.directory):
        raise HTTPException(status_code=400, detail="Invalid directory path")
    try:
        ACTIVE_DIR = req.directory
        know.index_directory(req.directory)
        return {"status": "success", "message": f"Successfully indexed {req.directory}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        suffix = os.path.splitext(file.filename)[1].lower()
        text_extensions = {
            '.md', '.py', '.txt', '.json', '.yaml', '.yml', '.ini', '.csv', '.xml', 
            '.html', '.css', '.js', '.pdf', '.docx', '.rtf', '.xlsx',
            '.png', '.jpg', '.jpeg', '.bmp'
        }
        if mime_type.startswith('text/') or suffix in text_extensions:
            content = know.extract_content(filepath, suffix)
            
        conn = know.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute("""
                UPDATE files 
                SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?
                WHERE filepath = ?
            """, (file.filename, file_size, mime_type, sha256, modified_at, content, filepath))
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))",
                           (filepath, file.filename, content, filepath))
        else:
            cursor.execute("""
                INSERT INTO files (filepath, filename, file_size, mime_type, sha256, modified_at, content, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
            """, (filepath, file.filename, file_size, mime_type, sha256, modified_at, content))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, NULL)",
                           (filepath, file.filename, content))
            
        conn.commit()
        conn.close()
        return {"status": "success", "filename": file.filename, "filepath": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
def search(q: str = None, tag: str = None, category: str = None, sort_by: str = None, sort_order: str = "asc", date_filter: str = "all"):
    conn = know.get_db()
    cursor = conn.cursor()
    
    cleaned_q, ops = parse_query_operators(q)
    
    if cleaned_q:
        sql = """
            SELECT f.filepath, f.filename, f.file_size, f.mime_type, f.modified_at, f.id,
                   snippet(fts_files, 2, '<mark>', '</mark>', '...', 15) as snippet
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
    
    conn.close()
    res = dict(row)
    res['tags'] = tags
    res['suggested_tags'] = suggest_tags_from_text(row['content'])
    
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
