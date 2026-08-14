#!/usr/bin/env python3
"""
EVE Online News & Knowledge Ingestion Engine (Uroboros Knowledge Vault)

Fetches historical and live news articles, dev blogs, patch notes, expansion details,
and game updates directly from the official EVE Online Contentful GraphQL API.
Transforms Contentful RichText AST into clean, structured Markdown and indexes
everything into the Uroboros Knowledge Engine (knowledge.db).

Ponytail: Zero-dependency stdlib implementation (urllib, json, re, os, sys, time).
"""

import os
import sys
import json
import time
import re
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 output across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPACE_ID = "7lhcm73ukv5p"
ACCESS_TOKEN = "BSl3tP6oZ_X_T7kAwXhGF_UB30oG4Hvt03lxol2ENB4"
GRAPHQL_URL = f"https://graphql.contentful.com/content/v1/spaces/{SPACE_ID}/environments/master"

DEFAULT_VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vault", "Eve Online", "News")

def rich_text_to_markdown(node, indent=0):
    """Recursively convert Contentful RichText AST nodes into clean GitHub Markdown."""
    if not isinstance(node, dict):
        return ""
    
    node_type = node.get("nodeType", "")
    
    if node_type == "text":
        val = node.get("value", "")
        marks = [m.get("type") for m in node.get("marks", [])]
        if "bold" in marks and "italic" in marks:
            val = f"***{val}***"
        elif "bold" in marks:
            val = f"**{val}**"
        elif "italic" in marks:
            val = f"*{val}*"
        if "code" in marks:
            val = f"`{val}`"
        return val
        
    children = node.get("content", [])
    
    if node_type == "document":
        chunks = [rich_text_to_markdown(c) for c in children]
        return "\n\n".join(c for c in chunks if c.strip()).strip()
    
    elif node_type.startswith("heading-"):
        level = node_type.split("-")[1]
        inner_text = "".join(rich_text_to_markdown(c) for c in children).strip()
        return f"\n{'#' * int(level)} {inner_text}\n"
    
    elif node_type == "paragraph":
        return "".join(rich_text_to_markdown(c) for c in children)
    
    elif node_type == "unordered-list":
        items = []
        for c in children:
            item_text = rich_text_to_markdown(c, indent + 2).strip()
            items.append(f"{' ' * indent}- {item_text}")
        return "\n" + "\n".join(items) + "\n"
    
    elif node_type == "ordered-list":
        items = []
        for idx, c in enumerate(children):
            item_text = rich_text_to_markdown(c, indent + 2).strip()
            items.append(f"{' ' * indent}{idx + 1}. {item_text}")
        return "\n" + "\n".join(items) + "\n"
    
    elif node_type == "list-item":
        chunks = [rich_text_to_markdown(c, indent) for c in children]
        return " ".join(c.strip() for c in chunks if c.strip())
    
    elif node_type == "hyperlink":
        uri = node.get("data", {}).get("uri", "")
        inner_text = "".join(rich_text_to_markdown(c) for c in children).strip()
        if not inner_text:
            inner_text = uri
        return f"[{inner_text}]({uri})"
    
    elif node_type == "blockquote":
        inner_text = "".join(rich_text_to_markdown(c) for c in children).strip()
        lines = inner_text.split("\n")
        return "\n" + "\n".join(f"> {l}" for l in lines) + "\n"
    
    elif node_type == "table":
        rows = []
        for row_idx, r in enumerate(children):
            row_md = rich_text_to_markdown(r)
            rows.append(row_md)
            if row_idx == 0 and r.get("nodeType") == "table-row":
                cell_count = len(r.get("content", []))
                rows.append("| " + " | ".join(["---"] * max(1, cell_count)) + " |")
        return "\n" + "\n".join(rows) + "\n"
    
    elif node_type == "table-row":
        cells = [rich_text_to_markdown(c).strip() for c in children]
        return "| " + " | ".join(cells) + " |"
    
    elif node_type in ("table-cell", "table-header-cell"):
        inner = "".join(rich_text_to_markdown(c) for c in children)
        return inner.replace("\n", " ")
    
    elif node_type == "hr":
        return "\n---\n"
    
    elif node_type == "embedded-asset-block":
        target = node.get("data", {}).get("target", {})
        title = target.get("fields", {}).get("title", "")
        url = target.get("fields", {}).get("file", {}).get("url", "")
        if url:
            if url.startswith("//"):
                url = "https:" + url
            return f"\n![{title}]({url})\n"
        return ""
    
    return "".join(rich_text_to_markdown(c) for c in children)


def sanitize_filename(name):
    """Sanitize string for Windows and Unix filesystem filenames."""
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name.strip()[:100]


def fetch_graphql_batch(limit=100, skip=0, retries=3):
    """Fetch a single paginated batch of articles from Contentful GraphQL API."""
    query = """
    query GetArticlesBatch($limit: Int, $skip: Int) {
      articleCollection(limit: $limit, skip: $skip, order: publishingDate_DESC) {
        total
        limit
        skip
        items {
          title
          slug
          category
          publishingDate
          author
          metaDescription
          tags
          richText {
            json
          }
        }
      }
    }
    """
    payload = {
        "query": query,
        "variables": {"limit": limit, "skip": skip}
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Uroboros-Ingest/1.0"
        }
    )
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("data", {}).get("articleCollection", {})
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def format_article_markdown(item):
    """Format article item into structured Markdown with rich metadata."""
    title = (item.get("title") or "Untitled").strip()
    slug = item.get("slug") or sanitize_filename(title).lower()
    pub_date = item.get("publishingDate") or ""
    category = item.get("category") or "news"
    author = item.get("author") or "EVE Online Team"
    meta_desc = (item.get("metaDescription") or "").strip()
    tags = item.get("tags") or []
    if category and category not in tags:
        tags.append(category)
    
    rt_json = item.get("richText", {}).get("json", {}) if item.get("richText") else {}
    body_md = rich_text_to_markdown(rt_json) if rt_json else ""
    
    source_url = f"https://www.eveonline.com/news/view/{slug}"
    tag_str = ", ".join(f"#{t}" for t in tags) if tags else "#eveonline"
    
    md = f"""# {title}

- **Date**: {pub_date}
- **Category**: {category}
- **Author**: {author}
- **Source**: {source_url}
- **Tags**: {tag_str}

## Overview
{meta_desc if meta_desc else 'Official EVE Online update.'}

---

{body_md}
"""
    return md, title, slug, pub_date, category


def run_ingestion(out_dir=DEFAULT_VAULT_DIR, max_articles=None, force=False, trigger_indexing=True):
    """Run full EVE Online knowledge ingestion pipeline."""
    print("=" * 70)
    print("[EVE ONLINE KNOWLEDGE INGESTION PIPELINE]")
    print(f"Target Vault Directory: {out_dir}")
    print("=" * 70)
    
    os.makedirs(out_dir, exist_ok=True)
    
    print("[1/3] Probing EVE Online Contentful Master Graph...")
    initial_batch = fetch_graphql_batch(limit=1, skip=0)
    total_articles = initial_batch.get("total", 0)
    print(f"-> Total available articles in source repository: {total_articles:,}")
    
    target_count = min(total_articles, max_articles) if max_articles else total_articles
    print(f"-> Target articles to process: {target_count:,}\n")
    
    batch_size = 100
    skip = 0
    saved_count = 0
    skipped_count = 0
    error_count = 0
    start_time = time.time()
    
    print("[2/3] Downloading and transforming article records into Markdown...")
    while skip < target_count:
        cur_limit = min(batch_size, target_count - skip)
        print(f"  Fetching batch [skip: {skip:,} - {skip + cur_limit:,} of {target_count:,}]...", end="", flush=True)
        t_batch_start = time.time()
        
        try:
            batch_data = fetch_graphql_batch(limit=cur_limit, skip=skip)
            items = batch_data.get("items", [])
            t_batch_elapsed = time.time() - t_batch_start
            print(f" ({len(items)} items received in {t_batch_elapsed:.2f}s)")
            
            for item in items:
                try:
                    md_content, title, slug, pub_date, category = format_article_markdown(item)
                    
                    year = pub_date[:4] if len(pub_date) >= 4 else "Archive"
                    year_dir = os.path.join(out_dir, year)
                    os.makedirs(year_dir, exist_ok=True)
                    
                    date_prefix = pub_date[:10] if len(pub_date) >= 10 else "undated"
                    safe_slug = sanitize_filename(slug)
                    filename = f"{date_prefix}_{safe_slug}.md"
                    filepath = os.path.join(year_dir, filename)
                    
                    if os.path.exists(filepath) and not force:
                        skipped_count += 1
                        continue
                    
                    with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(md_content)
                    
                    saved_count += 1
                except Exception as ex:
                    error_count += 1
                    print(f"\n[Warning] Error saving article '{item.get('title')}': {ex}")
            
            skip += len(items)
            if not items:
                break
                
        except Exception as e:
            print(f"\n[Error] Failed to fetch batch at skip {skip}: {e}")
            error_count += 1
            skip += batch_size
    
    total_elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("INGESTION SUMMARY")
    print(f"  - Total Time:     {total_elapsed:.2f} seconds")
    print(f"  - Newly Saved:    {saved_count:,} markdown files")
    print(f"  - Existing/Skip:  {skipped_count:,} files")
    print(f"  - Errors:         {error_count:,}")
    print(f"  - Output Path:    {out_dir}")
    print("=" * 70)
    
    if trigger_indexing and (saved_count > 0 or force):
        print("\n[3/3] Triggering Uroboros Knowledge Vault Indexing into SQLite & Vector Engine...")
        try:
            from batch_index import index_single_file, get_indexed_filepaths
            from src.infrastructure.database import get_db, run_maintenance
            
            with get_db() as conn:
                existing_indexed = get_indexed_filepaths(conn)
            
            indexed_count = 0
            all_files = []
            for root, _, files in os.walk(out_dir):
                for f in files:
                    if f.endswith(".md"):
                        all_files.append(os.path.join(root, f))
            
            print(f"-> Found {len(all_files):,} Markdown documents to index.")
            t_idx_start = time.time()
            for idx, fp in enumerate(all_files):
                norm = os.path.normcase(os.path.normpath(fp))
                if norm not in existing_indexed or force:
                    index_single_file(fp)
                    indexed_count += 1
                    if indexed_count % 100 == 0:
                        print(f"  Indexed {indexed_count:,}/{len(all_files):,} files...")
            
            print(f"-> Indexed {indexed_count:,} new documents into knowledge.db in {time.time() - t_idx_start:.2f}s")
            run_maintenance()
            print("-> Knowledge Engine FTS5 and Vector Maintenance complete!")
        except Exception as ex:
            print(f"[Notice] Indexing trigger notice: {ex}")
            print("You can manually index anytime via: python batch_index.py \"vault/Eve Online\"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest EVE Online News & Dev Blogs into Uroboros Knowledge Engine")
    parser.add_argument("--out-dir", default=DEFAULT_VAULT_DIR, help="Destination directory in vault")
    parser.add_argument("--limit", type=int, default=None, help="Max articles to fetch (default: all 2,705+)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--no-index", action="store_true", help="Skip immediate database indexing")
    
    args = parser.parse_args()
    run_ingestion(
        out_dir=args.out_dir,
        max_articles=args.limit,
        force=args.force,
        trigger_indexing=not args.no_index
    )
