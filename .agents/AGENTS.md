# Project Coding Rules (Uroboros Knowledge Engine)

## Technology Stack & Architectural Guidelines
- **FastAPI / Uvicorn backend**: Keep endpoints simple and lightweight. Rely on standard JSON structures and validate requests using Pydantic.
- **SQLite Database Integration**: Use `know.py` as the singular database manager. Always close connections or use context manager blocks (`with sqlite3.connect(...)`).
- **Glassmorphic frontend layout**: Modify UI features inside `index.html`, styling details in `style.css` (using CSS variables), and DOM interactions inside `app.js`.

## Ponytail coding principles
- Question complex features and implement the shortest functional diff possible (YAGNI).
- Run unit test checks on any database schema or route changes.
- **Decouple Post-processing from Optimization**: When utilizing modification checks (size/timestamp checks) to optimize indexing or parsing runs, ensure that auto-tagging, metadata expansion, or search index updates are decoupled so they run on all matches (even unmodified records) to capture new rules/configurations.
