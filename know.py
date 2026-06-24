import os
import sys
import sqlite3
import hashlib
import mimetypes
import asyncio
from pathlib import Path

# Advanced Parsers
import pypdf
import docx
from striprtf.striprtf import rtf_to_text
import openpyxl

# Windows Native OCR
from winrt.windows.storage import StorageFile
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.graphics.imaging import BitmapDecoder

DB_FILE = "knowledge.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    # Core metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE,
            filename TEXT,
            file_size INTEGER,
            mime_type TEXT,
            sha256 TEXT,
            modified_at REAL,
            content TEXT,
            notes TEXT
        )
    """)
    
    # Run migration checks
    cursor.execute("PRAGMA table_info(files)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'notes' not in columns:
        cursor.execute("ALTER TABLE files ADD COLUMN notes TEXT")
        
    cursor.execute("PRAGMA table_info(fts_files)")
    fts_columns = [row[1] for row in cursor.fetchall()]
    if not fts_columns or 'notes' not in fts_columns:
        cursor.execute("DROP TABLE IF EXISTS fts_files")
        cursor.execute("""
            CREATE VIRTUAL TABLE fts_files USING fts5(
                filepath,
                filename,
                content,
                notes
            )
        """)
    else:
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(
                filepath,
                filename,
                content,
                notes
            )
        """)
        
    # Tag association table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            file_id INTEGER,
            tag TEXT,
            PRIMARY KEY(file_id, tag),
            FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception:
        return None

async def _async_ocr(filepath):
    try:
        file = await StorageFile.get_file_from_path_async(filepath)
        stream = await file.open_async(0)
        decoder = await BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = OcrEngine.try_create_from_user_profile_languages()
        if not engine:
            return "[OCR Error: Failed to create WinRT OcrEngine]"
        result = await engine.recognize_async(bitmap)
        return result.text
    except Exception as e:
        return f"[OCR Error: {str(e)}]"

def extract_ocr_text(filepath):
    try:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                def _run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(_async_ocr(filepath))
                    finally:
                        new_loop.close()
                return pool.submit(_run_in_thread).result()
        else:
            return loop.run_until_complete(_async_ocr(filepath))
    except Exception as e:
        return f"[OCR Setup Error: {str(e)}]"

def extract_content(filepath, suffix):
    try:
        if suffix == '.pdf':
            reader = pypdf.PdfReader(filepath)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif suffix == '.docx':
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        elif suffix == '.rtf':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return rtf_to_text(f.read())
        elif suffix == '.xlsx':
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            text_lines = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_str = " ".join([str(v) for v in row if v is not None])
                    if row_str.strip():
                        text_lines.append(row_str)
            return "\n".join(text_lines)
        elif suffix in ['.png', '.jpg', '.jpeg', '.bmp']:
            return extract_ocr_text(filepath)
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(1024 * 1024)
    except Exception as e:
        return f"[Parsing Error: {str(e)}]"

def index_directory(dir_path):
    conn = get_db()
    cursor = conn.cursor()
    
    path = Path(dir_path).resolve()
    if not path.is_dir():
        print(f"Error: {dir_path} is not a directory.")
        return

    indexed_count = 0
    updated_count = 0
    
    text_extensions = {
        '.md', '.py', '.txt', '.json', '.yaml', '.yml', '.ini', '.csv', '.xml', 
        '.html', '.css', '.js', '.pdf', '.docx', '.rtf', '.xlsx',
        '.png', '.jpg', '.jpeg', '.bmp'
    }
    
    for p in path.rglob('*'):
        if not p.is_file():
            continue
        if p.name == DB_FILE:
            continue
            
        filepath = str(p)
        filename = p.name
        stat = p.stat()
        file_size = stat.st_size
        modified_at = stat.st_mtime
        
        cursor.execute("SELECT modified_at, file_size FROM files WHERE filepath = ?", (filepath,))
        row = cursor.fetchone()
        if row and row['modified_at'] == modified_at and row['file_size'] == file_size:
            continue
            
        sha256 = calculate_sha256(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        mime_type = mime_type or 'application/octet-stream'
        
        content = ""
        suffix = p.suffix.lower()
        if mime_type.startswith('text/') or suffix in text_extensions:
            content = extract_content(filepath, suffix)
            
        if row:
            cursor.execute("""
                UPDATE files 
                SET filename = ?, file_size = ?, mime_type = ?, sha256 = ?, modified_at = ?, content = ?
                WHERE filepath = ?
            """, (filename, file_size, mime_type, sha256, modified_at, content, filepath))
            cursor.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, (SELECT notes FROM files WHERE filepath = ?))",
                           (filepath, filename, content, filepath))
            updated_count += 1
        else:
            cursor.execute("""
                INSERT INTO files (filepath, filename, file_size, mime_type, sha256, modified_at, content, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
            """, (filepath, filename, file_size, mime_type, sha256, modified_at, content))
            cursor.execute("INSERT INTO fts_files (filepath, filename, content, notes) VALUES (?, ?, ?, NULL)",
                           (filepath, filename, content))
            indexed_count += 1
            
    conn.commit()
    conn.close()
    print(f"Indexing completed. Indexed: {indexed_count}, Updated: {updated_count}")

def search_files(query):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filepath, filename, rank 
        FROM fts_files 
        WHERE fts_files MATCH ? 
        ORDER BY rank 
        LIMIT 10
    """, (query,))
    rows = cursor.fetchall()
    
    if not rows:
        print("No matches found.")
    else:
        print(f"Results for search: '{query}':")
        for row in rows:
            print(f"- {row['filename']} ({row['filepath']})")
    conn.close()

def db_status():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(file_size) FROM files")
    count, total_size = cursor.fetchone()
    print(f"Total indexed files: {count or 0}")
    print(f"Total index file size: {total_size or 0} bytes")
    conn.close()

def main():
    if not os.path.exists(DB_FILE):
        init_db()

    if len(sys.argv) < 2:
        print("Usage: python know.py [init|index <dir>|search <query>|status]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "init":
        init_db()
    elif cmd == "index":
        if len(sys.argv) < 3:
            print("Usage: python know.py index <dir_path>")
            sys.exit(1)
        index_directory(sys.argv[2])
    elif cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python know.py search <query_string>")
            sys.exit(1)
        search_files(sys.argv[2])
    elif cmd == "status":
        db_status()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
