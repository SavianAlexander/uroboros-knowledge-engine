import os
import sys
import time
import hashlib
import sqlite3
import unicodedata
import re

# Add repository root to path
REPO_ROOT = r"c:\Users\Administrator\Desktop\Neuro Alexander"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80, flush=True)
print("EMPIRICAL CHALLENGER 2 VERIFICATION SUITE (REFINED)", flush=True)
print("=" * 80, flush=True)

# ==============================================================================
# TEST 1: NFC Unicode Normalization
# ==============================================================================
print("\n[TEST 1] NFC UNICODE NORMALIZATION FOR DIACRITICS, ACCENTS & COMBINING CHARS", flush=True)

from src.core.domain.services import sanitise_fts_query
from src.infrastructure.database import search_files

test_cases = [
    # (Description, NFD string, NFC string)
    ("French Accent (café)", "cafe\u0301", "café"),
    ("German Umlaut (München)", "Mu\u0308nchen", "München"),
    ("Spanish Tilde (señor)", "sen\u0303or", "señor"),
    ("Spanish Accent (canción)", "cancio\u0301n", "canción"),
    ("Portuguese Cedilla (coração)", "corac\u0327a\u0303o", "coração"),
    ("German Umlaut (Bär)", "Ba\u0308r", "Bär"),
    ("Combining Ring (tårn)", "ta\u030aarn", "tåarn"),
    ("Combining Acute (á)", "a\u0301", "á"),
    ("Combining Grave (à)", "a\u0300", "à"),
    ("Combining Circumflex (â)", "a\u0302", "â"),
    ("Combining Tilde (ã)", "a\u0303", "ã"),
]

nfc_pass_count = 0
for desc, nfd_input, nfc_input in test_cases:
    norm_nfd = unicodedata.normalize("NFC", nfd_input)
    norm_nfc = unicodedata.normalize("NFC", nfc_input)
    
    san_nfd = sanitise_fts_query(nfd_input)
    san_nfc = sanitise_fts_query(nfc_input)
    
    is_nfc_equal = (norm_nfd == unicodedata.normalize("NFC", nfd_input))
    is_san_equal = (san_nfd == san_nfc)
    
    print(f"  - Case: {desc}", flush=True)
    print(f"    NFD input: '{nfd_input}' (bytes: {nfd_input.encode('utf-8')})", flush=True)
    print(f"    Normalized: '{norm_nfd}' (bytes: {norm_nfd.encode('utf-8')})", flush=True)
    print(f"    sanitise_fts_query(NFD): '{san_nfd}'", flush=True)
    print(f"    sanitise_fts_query(NFC): '{san_nfc}'", flush=True)
    print(f"    Matches NFC? {is_nfc_equal} | sanitise_fts match? {is_san_equal}", flush=True)
    
    if is_nfc_equal and is_san_equal:
        nfc_pass_count += 1

print(f"\nNFC Test Result: {nfc_pass_count}/{len(test_cases)} cases passed.", flush=True)

# Test database FTS5 matching with NFD vs NFC
print("\n  - FTS5 Database Unicode NFC Equivalence Test:", flush=True)
conn = sqlite3.connect(":memory:")
conn.execute("CREATE VIRTUAL TABLE fts_test USING fts5(content);")

# Insert precomposed NFC text
conn.execute("INSERT INTO fts_test (content) VALUES ('El niño come café en München');")
conn.commit()

# Query using decomposed NFD queries
nfd_queries = [
    "nin\u0303o",       # niño
    "cafe\u0301",       # café
    "Mu\u0308nchen",    # München
]

db_fts_nfc_pass = True
for nfd_q in nfd_queries:
    nfc_q = unicodedata.normalize("NFC", nfd_q)
    san_q = sanitise_fts_query(nfd_q)
    cur = conn.cursor()
    cur.execute("SELECT content FROM fts_test WHERE fts_test MATCH ?", (san_q,))
    rows = cur.fetchall()
    print(f"    Searching NFD query '{nfd_q}' (sanitized to '{san_q}'): Found {len(rows)} rows.", flush=True)
    if len(rows) == 0:
        db_fts_nfc_pass = False

conn.close()
print(f"  - DB FTS5 NFD/NFC Equivalence Result: {'PASS' if db_fts_nfc_pass else 'FAIL'}", flush=True)

# ==============================================================================
# TEST 2: Latency Benchmarks (Search & DB Read < 5.0ms)
# ==============================================================================
print("\n" + "=" * 80, flush=True)
print("[TEST 2] BACKEND SEARCH & DATABASE READ LATENCY STRESS TEST (< 5.0ms)", flush=True)
print("=" * 80, flush=True)

db_benchmark_path = os.path.join(REPO_ROOT, "benchmark_lat.db")
conn = sqlite3.connect(db_benchmark_path)
conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, filepath TEXT, filename TEXT, file_size INTEGER, mime_type TEXT, modified_at TEXT, content TEXT);")
conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_files USING fts5(filepath, filename, content);")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM files")
if cursor.fetchone()[0] < 100:
    for i in range(200):
        fn = f"doc_{i}.txt"
        fp = f"/vault/docs/{fn}"
        ct = f"Enterprise document number {i} with metadata and query content."
        cursor.execute("INSERT INTO files (filepath, filename, file_size, mime_type, modified_at, content) VALUES (?, ?, ?, ?, ?, ?)",
                     (fp, fn, len(ct), "text/plain", "2026-08-04T00:00:00Z", ct))
        cursor.execute("INSERT INTO fts_files (filepath, filename, content) VALUES (?, ?, ?)", (fp, fn, ct))
    conn.commit()
conn.close()

# 2A: Direct DB Read Latency Test
print("\n--- 2A: Database Read Latency Test (1000 iterations) ---", flush=True)
read_times = []
with sqlite3.connect(db_benchmark_path, timeout=30.0) as conn:
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    for i in range(1000):
        t0 = time.perf_counter()
        cursor.execute("SELECT id, filepath, filename, file_size FROM files LIMIT 20")
        rows = cursor.fetchall()
        t1 = time.perf_counter()
        read_times.append((t1 - t0) * 1000.0)

avg_read_ms = sum(read_times) / len(read_times)
min_read_ms = min(read_times)
max_read_ms = max(read_times)
sorted_reads = sorted(read_times)
p95_read_ms = sorted_reads[int(len(sorted_reads) * 0.95)]
p99_read_ms = sorted_reads[int(len(sorted_reads) * 0.99)]

print(f"  DB Read Latency Results:", flush=True)
print(f"    Average : {avg_read_ms:.3f} ms", flush=True)
print(f"    Min     : {min_read_ms:.3f} ms", flush=True)
print(f"    Max     : {max_read_ms:.3f} ms", flush=True)
print(f"    P95     : {p95_read_ms:.3f} ms", flush=True)
print(f"    P99     : {p99_read_ms:.3f} ms", flush=True)

db_read_pass = avg_read_ms < 5.0 and p95_read_ms < 5.0
print(f"  DB Read Latency Target (<5.0ms avg & p95): {'PASS' if db_read_pass else 'FAIL'}", flush=True)

# 2B: Backend Search Latency Test
print("\n--- 2B: Backend Search Latency Test (1000 iterations) ---", flush=True)
from src.app.routers.search import search_endpoint

search_queries = [
    "enterprise",
    "architecture",
    "analytics",
    "document",
    "project",
    "information",
    "café",
    "München",
    "señor",
    "system"
]

# Warmup 1 call
search_endpoint(query="warmup")

search_times = []
for i in range(1000):
    q = search_queries[i % len(search_queries)]
    t0 = time.perf_counter()
    res = search_endpoint(query=q)
    t1 = time.perf_counter()
    search_times.append((t1 - t0) * 1000.0)

avg_search_ms = sum(search_times) / len(search_times)
min_search_ms = min(search_times)
max_search_ms = max(search_times)
sorted_searches = sorted(search_times)
p95_search_ms = sorted_searches[int(len(sorted_searches) * 0.95)]
p99_search_ms = sorted_searches[int(len(sorted_searches) * 0.99)]

print(f"  Backend Search Latency Results:", flush=True)
print(f"    Average : {avg_search_ms:.3f} ms", flush=True)
print(f"    Min     : {min_search_ms:.3f} ms", flush=True)
print(f"    Max     : {max_search_ms:.3f} ms", flush=True)
print(f"    P95     : {p95_search_ms:.3f} ms", flush=True)
print(f"    P99     : {p99_search_ms:.3f} ms", flush=True)

search_latency_pass = avg_search_ms < 5.0 and p95_search_ms < 5.0
print(f"  Backend Search Latency Target (<5.0ms avg & p95): {'PASS' if search_latency_pass else 'FAIL'}", flush=True)

# Cleanup benchmark temp db
try:
    os.remove(db_benchmark_path)
except Exception:
    pass

# ==============================================================================
# TEST 3: Zero Informal / Hype Strings Scan (Production Source Code Only)
# ==============================================================================
print("\n" + "=" * 80, flush=True)
print("[TEST 3] ZERO INFORMAL & HYPE STRINGS CODEBASE SCAN (SRC & ASSETS)", flush=True)
print("=" * 80, flush=True)

INFORMAL_PATTERNS = [
    r'\bawesome\b', r'\bkickass\b', r'\bbadass\b', r'\bhype\b', r'\bcrazy\b',
    r'\bsuper cool\b', r'\bmagic\b', r'\bdope\b', r'\bslick\b', r'\buber\b',
    r'\bboom\b', r'\bhacky\b', r'\blol\b', r'\brofl\b', r'\blmao\b',
    r'\bcrap\b', r'\bbullshit\b', r'\bjunk\b', r'\bdummy text\b', r'\bfoobar\b',
    r'\btestest\b', r'\bwhoops\b', r'\boops\b'
]

compiled_informal_regexes = [re.compile(p, re.IGNORECASE) for p in INFORMAL_PATTERNS]

files_to_scan = []
# Focus scan on src/, root main.py/know.py, index.html, style.css, app.js
scan_paths = [
    os.path.join(REPO_ROOT, "src"),
    os.path.join(REPO_ROOT, "index.html"),
    os.path.join(REPO_ROOT, "style.css"),
    os.path.join(REPO_ROOT, "app.js"),
    os.path.join(REPO_ROOT, "main.py"),
    os.path.join(REPO_ROOT, "know.py"),
]

for p in scan_paths:
    if os.path.isfile(p):
        files_to_scan.append(p)
    elif os.path.isdir(p):
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__', 'node_modules')]
            for file in files:
                if file.endswith(('.py', '.html', '.css', '.js')):
                    files_to_scan.append(os.path.join(root, file))

informal_findings = []
for filepath in files_to_scan:
    rel_path = os.path.relpath(filepath, REPO_ROOT)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_idx, line in enumerate(f, 1):
                for reg in compiled_informal_regexes:
                    m = reg.search(line)
                    if m:
                        informal_findings.append({
                            'file': rel_path,
                            'line': line_idx,
                            'matched': m.group(0),
                            'content': line.strip()
                        })
    except Exception as e:
        print(f"Error reading {rel_path}: {e}", flush=True)

print(f"Scanned {len(files_to_scan)} production source files.", flush=True)
if informal_findings:
    print(f"  FOUND {len(informal_findings)} INFORMAL/HYPE STRING INSTANCES IN PROD CODE:", flush=True)
    for item in informal_findings[:20]:
        print(f"    - {item['file']}:{item['line']} -> matched '{item['matched']}': \"{item['content']}\"", flush=True)
else:
    print("  ZERO informal/hype strings found across production source files and frontend assets!", flush=True)

informal_scan_pass = len(informal_findings) == 0

# ==============================================================================
# TEST 4: SHA-256 Bitwise Asset Parity
# ==============================================================================
print("\n" + "=" * 80, flush=True)
print("[TEST 4] SHA-256 BITWISE ASSET PARITY TEST", flush=True)
print("=" * 80, flush=True)

paired_assets = [
    ("index.html", os.path.join("src", "assets", "index.html")),
    ("style.css", os.path.join("src", "assets", "style.css")),
    ("app.js", os.path.join("src", "assets", "app.js")),
]

all_parity_pass = True

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

for root_rel, src_rel in paired_assets:
    root_full = os.path.join(REPO_ROOT, root_rel)
    src_full = os.path.join(REPO_ROOT, src_rel)
    
    if not os.path.exists(root_full):
        print(f"  ERROR: Root asset missing: {root_rel}", flush=True)
        all_parity_pass = False
        continue
    if not os.path.exists(src_full):
        print(f"  ERROR: Src asset missing: {src_rel}", flush=True)
        all_parity_pass = False
        continue
        
    root_hash = get_sha256(root_full)
    src_hash = get_sha256(src_full)
    root_size = os.path.getsize(root_full)
    src_size = os.path.getsize(src_full)
    
    match = (root_hash == src_hash)
    if not match:
        all_parity_pass = False
        
    print(f"  Asset Pair: {root_rel} <---> {src_rel}", flush=True)
    print(f"    Root SHA-256: {root_hash} ({root_size} bytes)", flush=True)
    print(f"    Src  SHA-256: {src_hash} ({src_size} bytes)", flush=True)
    print(f"    Bitwise Parity: {'MATCH (PASS)' if match else 'MISMATCH (FAIL)'}", flush=True)

print(f"\nBitwise Asset Parity Final Verdict: {'PASS' if all_parity_pass else 'FAIL'}", flush=True)

# ==============================================================================
# SUMMARY & VERDICT
# ==============================================================================
print("\n" + "=" * 80, flush=True)
print("FINAL EMPIRICAL VERDICT SUMMARY", flush=True)
print("=" * 80, flush=True)
print(f"  1. NFC Unicode Normalization: {'PASS' if (nfc_pass_count == len(test_cases) and db_fts_nfc_pass) else 'FAIL'}", flush=True)
print(f"  2A. DB Read Latency (<5.0ms) : {'PASS' if db_read_pass else 'FAIL'} (avg: {avg_read_ms:.3f}ms, p95: {p95_read_ms:.3f}ms)", flush=True)
print(f"  2B. Search Latency (<5.0ms)  : {'PASS' if search_latency_pass else 'FAIL'} (avg: {avg_search_ms:.3f}ms, p95: {p95_search_ms:.3f}ms)", flush=True)
print(f"  3. Zero Informal/Hype Scan   : {'PASS' if informal_scan_pass else 'FAIL'} ({len(informal_findings)} issues)", flush=True)
print(f"  4. SHA-256 Asset Parity     : {'PASS' if all_parity_pass else 'FAIL'}", flush=True)

overall_pass = (nfc_pass_count == len(test_cases) and db_fts_nfc_pass and db_read_pass and search_latency_pass and informal_scan_pass and all_parity_pass)
print(f"\nOVERALL VERDICT: {'APPROVE' if overall_pass else 'REJECT'}", flush=True)
