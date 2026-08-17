"""
EVE University (UniWiki) Full Knowledge Harvester & Markdown Transformer.
Pulls all content articles from https://wiki.eveuniversity.org via MediaWiki API,
converts wikitext/tables to clean, structured Markdown, and indexes into SQLite RAG vault.

Ponytail Senior Dev Principle: Zero-dependency stdlib (urllib.request, json, os, sys, time, re, concurrent.futures, sqlite3).
"""

import os
import sys
import json
import time
import re
import hashlib
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

VAULT_EVE_UNI_WIKI_DIR = os.path.join(BASE_DIR, "vault", "Eve Online", "Eve_University", "wiki")
API_ENDPOINT = "https://wiki.eveuniversity.org/api.php"
USER_AGENT = "NeuroAlexanderKnowledgeEngine/2.0 (savianalexander@pm.me)"


def clean_filename(title: str) -> str:
    """Sanitize title for safe filesystem persistence."""
    cleaned = re.sub(r'[\\/*?:"<>|]', '_', title)
    cleaned = cleaned.replace(' ', '_').strip('._ ')
    return cleaned[:150] or "unnamed_page"


def parse_wiki_tables(text: str) -> str:
    """Convert MediaWiki tables to standard Markdown tables."""
    def convert_table(match):
        table_body = match.group(1)
        rows = re.split(r'\n\|-', table_body)
        md_table = []
        header_done = False
        target_cols = 0

        for r in rows:
            r = r.strip()
            if not r or r.startswith('class=') or r.startswith('style='):
                continue
            if r.startswith('!'):
                raw_cells = [c.strip() for c in re.split(r'!!|\n!', r[1:]) if c.strip()]
                cells = [re.sub(r'^[^|]*\|', '', c).strip() for c in raw_cells]
                if cells:
                    target_cols = max(target_cols, len(cells))
                    md_table.append("| " + " | ".join(cells) + " |")
                    md_table.append("| " + " | ".join([":---"] * len(cells)) + " |")
                    header_done = True
            elif r.startswith('|'):
                raw_cells = [c.strip() for c in re.split(r'\|\||\n\|', r[1:]) if c.strip()]
                cells = [re.sub(r'^[^|]*\|', '', c).strip() for c in raw_cells]
                if cells:
                    if not header_done:
                        target_cols = max(target_cols, len(cells))
                        md_table.append("| " + " | ".join(cells) + " |")
                        md_table.append("| " + " | ".join([":---"] * len(cells)) + " |")
                        header_done = True
                    else:
                        # Align columns
                        if target_cols > len(cells):
                            cells.extend([""] * (target_cols - len(cells)))
                        md_table.append("| " + " | ".join(cells[:target_cols]) + " |")

        return "\n\n" + "\n".join(md_table) + "\n\n" if md_table else ""

    return re.sub(r'\{\|[^\n]*\n(.*?)\|\}', convert_table, text, flags=re.DOTALL)


def wikitext_to_markdown(title: str, wikitext: str, url: str, categories: list, pageid: int) -> str:
    """Convert MediaWiki wikitext markup to clean, structured GitHub Flavored Markdown."""
    if not wikitext:
        return ""

    text = wikitext
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 1. Strip references and noise tags
    text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<ref[^/>]*/>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # 2. Strip standard decorative / banner wiki templates
    text = re.sub(r'\{\{Navbox[^}]*\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{\{Notice[^}]*\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{\{Update[^}]*\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{\{Stub[^}]*\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{\{Needing updates[^}]*\}\}', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 3. Convert inline wiki templates
    text = re.sub(r'\{\{(?:Skill|Item|Ship|Module|Charge|Ore|Skillbook|Blueprint|Implant)\|([^}|]+)(?:\|[^}]*)?\}\}', r'**\1**', text, flags=re.IGNORECASE)
    text = re.sub(r'\{\{ISKs?\|([0-9,.]+)\}\}', r'\1 ISK', text, flags=re.IGNORECASE)
    text = re.sub(r'\{\{Fitting\|([^}]+)\}\}', r'```\nFitting: \1\n```', text, flags=re.IGNORECASE)

    # 4. Parse Tables
    text = parse_wiki_tables(text)

    # 5. Strip leftover double-brace templates cleanly
    text = re.sub(r'\{\{[^{}]*\}\}', '', text)

    # 6. Convert Headers: ====== H6 -> ######, etc.
    text = re.sub(r'^======\s*(.*?)\s*======$', r'###### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^=====\s*(.*?)\s*=====$', r'##### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^====\s*(.*?)\s*====$', r'#### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*(.*?)\s*===$', r'### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^==\s*(.*?)\s*==$', r'## \1', text, flags=re.MULTILINE)
    text = re.sub(r'^=\s*(.*?)\s*=$', r'# \1', text, flags=re.MULTILINE)

    # 7. Convert Bold and Italics
    text = re.sub(r"'''''(.*?)'''''", r"***\1***", text)
    text = re.sub(r"'''(.*?)'''", r"**\1**", text)
    text = re.sub(r"''(.*?)''", r"*\1*", text)

    # 8. Convert Wiki Links [[Target|Label]] -> **Label** or [[Target]] -> **Target**
    def link_repl(match):
        inner = match.group(1).strip()
        if inner.startswith("Category:") or inner.startswith("File:") or inner.startswith("Image:"):
            return ""
        if "|" in inner:
            target, label = inner.split("|", 1)
            return f"**{label.strip()}**"
        return f"**{inner}**"

    text = re.sub(r'\[\[(.*?)\]\]', link_repl, text)

    # 9. Convert External Links [http://url label] -> [label](url)
    text = re.sub(r'\[(https?://[^\s\]]+)\s+([^\]]+)\]', r'[\2](\1)', text)
    text = re.sub(r'\[(https?://[^\s\]]+)\]', r'<\1>', text)

    # 10. Convert bullet lists and definition lists
    lines = text.split('\n')
    md_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('****'):
            md_lines.append('      - ' + stripped[4:].strip())
        elif stripped.startswith('***'):
            md_lines.append('    - ' + stripped[3:].strip())
        elif stripped.startswith('**'):
            md_lines.append('  - ' + stripped[2:].strip())
        elif stripped.startswith('*'):
            md_lines.append('- ' + stripped[1:].strip())
        elif stripped.startswith(';'):
            # Definition term
            term = stripped[1:].strip()
            md_lines.append(f"\n**{term}**:")
        elif stripped.startswith(':'):
            # Definition description
            desc = stripped[1:].strip()
            md_lines.append(f"> {desc}")
        elif stripped.startswith('##') and not stripped.startswith('## '):
            md_lines.append('  1. ' + stripped[2:].strip())
        elif stripped.startswith('#') and not stripped.startswith('# '):
            md_lines.append('1. ' + stripped[1:].strip())
        else:
            md_lines.append(line)

    text = '\n'.join(md_lines)

    # 11. Strip HTML tags
    text = re.sub(r'</?(?:div|span|font|center|small|big|p|br|table|tr|td|th|tbody|thead)[^>]*>', '', text, flags=re.IGNORECASE)

    # 12. Clean whitespace
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    # 13. Frontmatter
    cats_str = json.dumps(categories)
    frontmatter = f"""---
title: "{title}"
url: "{url}"
pageid: {pageid}
source: "EVE University Wiki"
categories: {cats_str}
harvested_at: "{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}"
---

# {title}

"""
    return frontmatter + text + "\n"


def fetch_all_article_titles() -> list:
    """Retrieve all non-redirect main namespace article titles from EVE University Wiki."""
    print("📡 Querying EVE University Wiki API for complete main namespace article index...")
    titles = []
    apcontinue = None
    page_batch = 1

    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "apnamespace": "0",
            "apfilterredir": "nonredirects",
            "aplimit": "500",
            "format": "json"
        }
        if apcontinue:
            params["apcontinue"] = apcontinue

        url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                data = json.loads(res.read().decode('utf-8'))
                pages = data.get("query", {}).get("allpages", [])
                for p in pages:
                    titles.append(p.get("title"))

                print(f"  • Batch {page_batch:02d}: Received {len(pages)} titles (Cumulative: {len(titles):,})")

                if "continue" in data and "apcontinue" in data["continue"]:
                    apcontinue = data["continue"]["apcontinue"]
                    page_batch += 1
                else:
                    break
        except Exception as ex:
            print(f"  ❌ Error fetching allpages batch {page_batch}: {ex}")
            time.sleep(2)

    print(f"✅ Total Content Articles Discovered: {len(titles):,}")
    return titles


def fetch_batch_pages(batch_titles: list) -> list:
    """Fetch revisions wikitext, categories, and URLs for a batch of up to 50 titles."""
    pipe_titles = "|".join(batch_titles)
    params = {
        "action": "query",
        "prop": "revisions|categories|info",
        "inprop": "url",
        "rvprop": "content",
        "cllimit": "max",
        "titles": pipe_titles,
        "format": "json"
    }
    url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    results = []
    try:
        with urllib.request.urlopen(req, timeout=35) as res:
            data = json.loads(res.read().decode('utf-8'))
            pages_dict = data.get("query", {}).get("pages", {})
            for pid_str, pdata in pages_dict.items():
                if int(pid_str) < 0:
                    continue
                title = pdata.get("title", "Unknown")
                pageid = pdata.get("pageid", 0)
                fullurl = pdata.get("fullurl", f"https://wiki.eveuniversity.org/{urllib.parse.quote(title)}")
                categories = [c.get("title", "").replace("Category:", "") for c in pdata.get("categories", [])]
                revs = pdata.get("revisions", [])
                wikitext = revs[0].get("*", "") if revs else ""
                results.append({
                    "title": title,
                    "pageid": pageid,
                    "url": fullurl,
                    "categories": categories,
                    "wikitext": wikitext
                })
    except Exception as ex:
        print(f"  ⚠️ Error fetching batch of {len(batch_titles)} titles: {ex}")
    return results


def run_harvest(output_dir: str = VAULT_EVE_UNI_WIKI_DIR, limit: int = 0, workers: int = 10) -> dict:
    """Execute complete download and Markdown conversion of EVE University Wiki."""
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.time()

    all_titles = fetch_all_article_titles()
    if limit > 0:
        all_titles = all_titles[:limit]
        print(f"⚡ Limiting run to {limit} articles.")

    batch_size = 50
    batches = [all_titles[i:i + batch_size] for i in range(0, len(all_titles), batch_size)]
    total_batches = len(batches)

    print(f"\n🚀 Downloading & Converting {len(all_titles):,} articles across {total_batches} batches ({workers} workers)...")

    saved_count = 0
    total_bytes = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_batch_pages, b): idx for idx, b in enumerate(batches, 1)}
        for fut in as_completed(futures):
            b_idx = futures[fut]
            batch_results = fut.result()
            for item in batch_results:
                title = item["title"]
                wikitext = item["wikitext"]
                if not wikitext.strip():
                    continue

                md_content = wikitext_to_markdown(
                    title=title,
                    wikitext=wikitext,
                    url=item["url"],
                    categories=item["categories"],
                    pageid=item["pageid"]
                )

                fname = f"{clean_filename(title)}.md"
                fpath = os.path.join(output_dir, fname)

                with open(fpath, "w", encoding="utf-8", errors="replace") as f:
                    f.write(md_content)

                saved_count += 1
                total_bytes += len(md_content.encode('utf-8'))

            print(f"  [{b_idx:03d}/{total_batches}] Batch processed — {saved_count:,} articles saved ({total_bytes / (1024*1024):.1f} MB)")

    elapsed = time.time() - t0
    print(f"\n🎉 HARVEST COMPLETE in {elapsed:.1f}s ({elapsed/60:.1f}m)")
    print(f"  • Total Articles Saved: {saved_count:,}")
    print(f"  • Total Storage Volume: {total_bytes / (1024*1024):.2f} MB")
    print(f"  • Target Vault Folder:  {output_dir}")

    return {
        "status": "success",
        "saved_count": saved_count,
        "total_bytes": total_bytes,
        "duration_seconds": round(elapsed, 2),
        "output_dir": output_dir
    }


def index_harvested_articles():
    """Index all newly harvested wiki articles into SQLite knowledge database."""
    print("\n🗄️ Indexing Harvested EVE University Wiki Articles into SQLite Database...")
    from src.infrastructure.database import get_db, run_maintenance

    all_files = []
    for root, dirs, files in os.walk(VAULT_EVE_UNI_WIKI_DIR):
        for fn in files:
            if fn.endswith(".md"):
                all_files.append(os.path.join(root, fn))

    print(f"  • Found {len(all_files):,} Markdown files in {VAULT_EVE_UNI_WIKI_DIR}")
    t0 = time.time()
    indexed = 0

    with get_db() as conn:
        with conn:
            cur = conn.cursor()
            for idx, filepath in enumerate(all_files, 1):
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    filename = os.path.basename(filepath)
                    file_size = len(content.encode('utf-8'))
                    modified_at = os.path.getmtime(filepath)
                    sha256 = hashlib.sha256(content.encode('utf-8')).hexdigest()

                    # Clean up existing record if any
                    cur.execute("SELECT id FROM files WHERE filepath = ?", (filepath,))
                    existing = cur.fetchone()
                    if existing:
                        file_id = existing[0]
                        cur.execute("DELETE FROM fts_files WHERE filepath = ?", (filepath,))
                        cur.execute("DELETE FROM file_chunks WHERE file_id = ?", (file_id,))
                        cur.execute("DELETE FROM fts_file_chunks WHERE file_id = ?", (file_id,))
                        cur.execute("DELETE FROM files WHERE id = ?", (file_id,))

                    cur.execute("""
                        INSERT INTO files (user_id, filepath, filename, file_size, mime_type, sha256, modified_at, content, acl_permissions, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                    """, (0, filepath, filename, file_size, "text/markdown", sha256, modified_at, content, "public"))
                    file_id = cur.lastrowid

                    cur.execute("""
                        INSERT INTO fts_files (filepath, filename, content, notes)
                        VALUES (?, ?, ?, NULL)
                    """, (filepath, filename, content))

                    # Simple section chunking
                    sections = [s.strip() for s in content.split("\n## ") if s.strip()]
                    for c_idx, sec in enumerate(sections):
                        chunk_text = sec if sec.startswith("# ") else f"## {sec}"
                        c_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()
                        cur.execute("""
                            INSERT INTO file_chunks (file_id, chunk_index, content, embedding_json, chunk_hash)
                            VALUES (?, ?, ?, NULL, ?)
                        """, (file_id, c_idx, chunk_text, c_hash))
                        chunk_id = cur.lastrowid
                        cur.execute("INSERT INTO fts_file_chunks (chunk_id, file_id, content) VALUES (?, ?, ?)",
                                    (chunk_id, file_id, chunk_text))

                    indexed += 1
                    if idx % 500 == 0 or idx == len(all_files):
                        print(f"  • [{idx:04d}/{len(all_files):04d}] Files indexed into SQLite & FTS5...")
                except Exception as ex:
                    print(f"  ❌ Error indexing {filepath}: {ex}")

    elapsed = time.time() - t0
    print(f"✅ Fast Indexing Complete: {indexed:,} files committed in {elapsed:.1f}s!")
    run_maintenance()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EVE University Wiki Knowledge Harvester")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of articles to download (0 = all)")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent worker threads (default=10)")
    parser.add_argument("--index-only", action="store_true", help="Skip download and only index files into SQLite")
    parser.add_argument("--no-index", action="store_true", help="Skip SQLite indexing after download")
    args = parser.parse_args()

    if not args.index_only:
        run_harvest(limit=args.limit, workers=args.workers)

    if not args.no_index:
        index_harvested_articles()
