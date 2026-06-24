# Uroboros Knowledge Database Engine

Uroboros is a lightweight, high-performance, single-folder knowledge indexing and retrieval database system. It features hybrid full-text search (SQLite FTS5), a custom zero-dependency TF-IDF Vector Space Model (MiniVectorEngine) for semantic concept searches, real-time filesystem watchers, dynamic auto-tagging rules, bookmarks, query macros, and custom ReportLab PDF catalog export formatting.

---

## Key Features

- **Hybrid Search Pipelines**: Search via keyword matching (FTS5) or semantic cosine similarity matching (TF-IDF Concept Space) using a lightweight, pure-Python vector search engine.
- **Interactive Similarity Thresholds**: Real-time results filtering via visual matching range sliders on semantic vector scores (0-100%).
- **Multi-tag Intersection/Union Selector**: Stack tag query filters dynamically in active scopes using `AND` (all selected) or `OR` (any selected) logic operators.
- **Query Auto-Completion & Suggestion**: Real-time keyword autosuggestions fetching matching macros, tags, metadata categories, and query filters.
- **Auto-Tagging Rules Priorities Engine**: Configure regex rule patterns mapped to custom tag tags and prioritized to resolve execution precedence on file ingestion.
- **Word Synonym Expander**: Register token equivalence maps to expand FTS query tokens using logic OR operators.
- **Search History & Bookmarks Vault**: Persistently log query history and bookmark custom-configured searches for instant re-execution.
- **Customizable PDF Exporter**: Generate ReportLab PDF summary directories with customized headers, tag exclusion filters, template styles, and color themes (*Indigo*, *Crimson*, *Emerald*, *Charcoal*).
- **Periodic Database Backups**: Keep database snapshots safe with background thread interval snapshots.

---

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn reportlab python-docx openpyxl pytest httpx
   ```

2. **Initialize Database & Scan**:
   Initialize and scan the watch directory (`dumps/` is active by default):
   ```bash
   python know.py init
   python know.py index dumps
   ```

3. **Start the Web Server**:
   ```bash
   python main.py
   ```
   Access the web interface at `http://127.0.0.1:8000`.

---

## Running Automated Tests

Run the full api and database test suites using pytest:
```bash
pytest test_api.py test_db.py
```

---

## Project Structure

- `main.py`: FastAPI server routes, LRU query caching mechanisms, and PDF/CSV exporter scripts.
- `know.py`: SQL tables manager, background filesystem folder watcher, text extractors (WAV wav metadata, Docx, Xlsx, PDF, plain text), and semantic vector searches logic.
- `index.html`: Clean, responsive glassmorphic single-page web user interface.
- `style.css`: Transparent custom scrollbars, animations, and themed UI layout definitions.
- `app.js`: Autocomplete events, tag loaders, concept canvas physics renderers, and server fetch hooks.
- `Progress Reports/`: Quantitative metrics lists tracking LOC parameters and feature updates across evolution versions.
