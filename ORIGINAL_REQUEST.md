# Original User Request

## 2026-08-05T00:09:36Z

Complete visual redesign of the **Uroboros Knowledge Engine** web UI — a single-page application served by a FastAPI backend. The current UI is functional but visually dated. The goal is to create a **premium, modern, dark-mode-first glassmorphic interface** that rivals products like Linear, Raycast, Notion, and Arc Browser in visual polish. The backend API is fully built and must NOT be modified — this is a pure frontend redesign of three files: `index.html`, `style.css`, and `app.js`. Every existing backend capability must remain fully wired and functional.

Working directory: `c:\Users\Administrator\Desktop\Neuro Alexander`

Integrity mode: development

---

## Requirements

### R1. Premium Visual Design System

The UI must feel premium, modern, and alive. Dark-mode-first with an optional light theme toggle. The design should use:
- A cohesive glassmorphic design language with frosted-glass panels, subtle backdrop blurs, and layered depth
- A curated color palette anchored around deep navy/charcoal backgrounds with vibrant accent colors (electric indigo, cyan, amber highlights)
- Premium typography using Google Fonts (Inter or similar clean sans-serif)
- Smooth micro-animations: hover transitions, panel slides, fade-ins, loading skeleton shimmers, progress pulses
- A polished icon system using the existing SVG assets in `src/assets/` and `src/assets/icons/`
- Responsive layout that works well on 1080p through 4K displays

The interface should feel like an enterprise-grade intelligence platform, not a basic CRUD dashboard.

### R2. Complete View Architecture (6 Core Views + Command Palette)

The application has **6 navigable views** plus a keyboard-activated command palette. Every view must be fully redesigned and fully functional, wired to the real backend API endpoints listed below. No mock data — all data comes from live API calls.

**View 1 — Dashboard & Workspace (default landing)**
- System health gauge and status indicators (`GET /api/health`, `GET /api/stats`)
- Storage analytics with MIME distribution charts (`GET /api/analytics/storage`)
- Tag distribution visualization and co-occurrence matrix (`GET /api/analytics/tags`)
- Search activity telemetry panel (`GET /api/analytics/search-activity`)
- Indexing timeline sparkline visualization
- Recent searches list (`GET /api/search/history`)
- Active directory tree sidebar (`GET /api/file/tree`) with file selection opening a split-screen workspace
- Workspace split-screen: left pane = file preview (PDF iframe, images with OCR overlay, video/audio players, markdown render, code with syntax highlighting), right pane = text editor with markdown toolbar, word/char counts, and document AI insights panel (`GET /api/file/insights`)
- Workflow triggers panel with webhook execution logs (`GET /api/workflows/triggers`, `GET /api/workflows/logs`)
- Quick action tiles for common operations

**View 2 — Search & Explorer**
- Drag-and-drop file upload zone (`POST /api/upload`)
- Audio memo recorder using browser MediaRecorder API → uploads to `dumps/voice_memos` (`POST /api/upload`, `POST /api/transcribe`)
- Search input with autocomplete dropdown (`GET /api/search/autocomplete`) supporting operators (`tag:`, `type:`, `size:`, `NEAR()`)
- Real-time query syntax validation (`POST /api/search/validate`)
- Search mode switcher: Keyword (FTS5) vs Semantic (TF-IDF BM25) with similarity threshold slider
- Search results with file extension badges, match score indicators, tag pills, highlighted snippet text (`GET /api/search`)
- Sort controls (relevance, filename, size, date), date filters (24h, week, month, year), category tabs (All, Documents, Spreadsheets, Code, Images, Duplicates)
- PDF export configuration drawer (`GET /api/report/export`) with style templates and theme selection
- CSV export (`GET /api/export`)
- Bulk selection and bulk delete (`POST /api/bulk_delete`)
- Search bookmark save/load (`GET/POST/DELETE /api/bookmarks`)
- FTS snippet customization controls
- Floating file inspector drawer with metadata, audio/video players, annotation notes (`GET/POST /api/notes`), tags management (`POST/DELETE /api/file/tag`), suggested tags (`GET /api/suggested_tags`), and file actions (open, rename, edit, delete)

**View 3 — Knowledge Graph**
- Full-screen interactive 2D canvas graph visualization
- Force-directed, circular, grid, and tree layout presets
- Zoom/pan controls and minimap
- Node category filters (documents, tags, concepts)
- Search-to-highlight node filter
- Node glyphs using graph SVG icons from `src/assets/icons/graph_node_*.svg`
- Edge types: `tagged_with`, `wikilink_to` (dashed purple), `shared_tag_cluster` (dotted amber)
- Data from `GET /api/graph/data` (nodes + edges), `GET /api/graph/wikilinks`, `GET /api/graph/clusters`
- Click node → open file inspector

**View 4 — AI Chat & RAG**
- Left sidebar: chat sessions list with search filter, create/delete sessions (`GET/POST/DELETE /api/chat/sessions`)
- GGUF model configuration panel: model path, temperature slider (0.0-1.0), context window, web search toggle
- Chat message stream with SSE streaming (`POST /api/chat/stream`), markdown rendering with code block copy buttons
- Grounded citation chips: local vault document citations and web search source chips
- Prompt starter chips (Summarize Docs, Audit Tagged Files, etc.)
- Typing indicator animation during streaming

**View 5 — Configuration & Processes**
- Automated tagging rules engine: table of regex rules, add/edit/test-preview (`GET/POST /api/rules`, `POST /api/rules/test-preview`)
- FTS synonyms manager (`GET/POST /api/synonyms`)
- Query macros manager (`GET/POST /api/macros`)
- Tag aliases manager (`GET/POST /api/aliases`)
- Search history vault (`GET /api/search/history`)
- Search bookmarks vault (`GET/POST/DELETE /api/bookmarks`)
- Periodic backup scheduler
- P2P LAN sync peers: discovered + manual peers, sync trigger, sync logs (`GET/POST /api/sync/peers`, `POST /api/sync/exchange`, `GET /api/sync/logs`)
- DB snapshot vault: capture, list, restore, delete (`POST/GET/DELETE /api/snapshots`, `POST /api/snapshots/restore`)

**View 6 — Settings & Account**
- System configuration summary (WAL mode, FTS tokenizer, active theme, DB size, indexed files)
- Database maintenance actions: re-index directory (`POST /api/index`), VACUUM & FTS rebuild, capture snapshot, export audit CSV
- Theme toggle (dark/light)
- Export controls (CSV stats, PDF report)
- Enterprise profile card with SOC 2 certification badge
- Storage usage progress bar
- Recent activity timeline
- System environment table (`GET /api/system/env`)

**Command Palette (Ctrl+P / Cmd+P)**
- Keyboard-navigable spotlight modal for switching views, toggling theme, triggering exports, jumping to files

### R3. Full API Wiring — Zero Dead UI

Every button, form, toggle, slider, and interactive element must be connected to a real backend API call. No placeholder buttons. No `console.log("TODO")`. The three frontend files (`index.html`, `style.css`, `app.js`) must produce a fully operational application when served by the existing FastAPI backend at `http://127.0.0.1:8000`.

### R4. Asset Utilization & Generation

The project has extensive SVG and image assets in `src/assets/` and `src/assets/icons/` (75+ files). These must be used throughout the UI for navigation icons, file type badges, graph node glyphs, and branding. Key assets include:
- Navigation: `nav_explorer.svg`, `nav_chat.svg`, `nav_diagnostics.svg`, `nav_processes.svg`, `nav_settings.svg`, `nav_account.svg`
- File types: `ext_audio.svg`, `ext_code.svg`, `ext_doc.svg`, `ext_image.svg`, `ext_spreadsheet.svg`, `ext_video.svg`
- Actions: `icon_search_brain.svg`, `icon_pencil_edit.svg`, `icon_trash_delete.svg`, `icon_camera_snapshot.svg`, `icon_database_backup.svg`, `icon_tag_audit.svg`, `icon_shield_rule.svg`, `icon_lightbulb.svg`, `icon_folder.svg`
- Graph nodes: `graph_node_audio.svg`, `graph_node_code.svg`, `graph_node_concept.svg`, `graph_node_doc.svg`, `graph_node_image.svg`, `graph_node_spreadsheet.svg`, `graph_node_video.svg`, `node_concept.svg`, `node_document.svg`, `node_peer.svg`, `node_tag.svg`
- Branding: `uroboros_logo.svg`, `brand_logo.svg`, `favicon.svg`, `logo.png`
- Hero images: `uroboros_hero_banner.jpg`, `rag_assistant_avatar.jpg`, `system_admin_shield.jpg`, `uroboros_empty_state.jpg`

If additional images are needed for the redesign (e.g., new hero banners, background textures), generate them using the `generate_image` tool.

### R5. File Parity Enforcement

After modifying the root `index.html`, `style.css`, and `app.js`, the corresponding copies in `src/assets/` must be updated to maintain 100% content parity. The build spec file at `build/UroborosKnowledgeHub.spec` references `src/assets/` for PyInstaller bundling.

---

## Acceptance Criteria

### Visual Quality
- [ ] The UI uses a dark-mode-first glassmorphic design with frosted-glass panels, subtle backdrop blurs, and layered depth
- [ ] Typography uses a premium web font (Inter, Outfit, or similar) loaded from Google Fonts
- [ ] At least 10 distinct micro-animations exist (hover effects, transitions, loading states, fade-ins, skeleton shimmers)
- [ ] The color palette is cohesive — no raw browser-default colors (no plain red, blue, green)
- [ ] Light theme toggle works and produces a visually coherent light mode

### Functional Completeness
- [ ] All 6 views render and are navigable via the tab/navigation system
- [ ] Command palette opens with Ctrl+P / Cmd+P and allows view switching
- [ ] Search returns real results from the backend and displays them with highlighted snippets
- [ ] RAG/Chat streaming works via SSE with real-time token-by-token rendering
- [ ] Knowledge graph renders interactive nodes and edges from `/api/graph/data`
- [ ] File tree loads and selecting a file opens the workspace split-screen preview
- [ ] File upload via drag-and-drop successfully indexes new files
- [ ] Tag management (add/remove tags on files) works through the inspector
- [ ] Dashboard health gauge and analytics charts render real data from `/api/stats` and `/api/analytics/*`
- [ ] Auto-tag rules can be created, listed, and test-previewed
- [ ] Chat sessions can be created, listed, selected, and deleted
- [ ] DB snapshots can be captured, listed, and restored

### Code Quality
- [ ] The output consists of exactly 3 files: `index.html`, `style.css`, `app.js` (no additional framework dependencies beyond what's loaded via CDN)
- [ ] All JavaScript uses vanilla JS or lightweight CDN libraries (no npm/build step required)
- [ ] `src/assets/index.html`, `src/assets/style.css`, `src/assets/app.js` are updated to match root files

### Verification
- [ ] Starting the server with `python main.py` and opening `http://127.0.0.1:8000` renders the new UI
- [ ] No JavaScript console errors on page load
- [ ] Every navigation tab renders its view without blank screens

## 2026-08-11T21:23:03Z

Create a unified deployment script (`setup.ps1`) for the Uroboros Knowledge Engine that strictly leverages Docker, re-integrating Ollama with AMD GPU passthrough, automatically pulling required models, and verifying the architecture via automated E2E tests.

Working directory: `c:\Users\Administrator\Desktop\Neuro Alexander`
Integrity mode: development

## Requirements

### R1. Re-Dockerize Ollama
Modify `docker-compose.yml` to include the `ollama/ollama` image. Configure the deployment to use GPU passthrough utilizing the `amd` driver.

### R2. Automated Setup Lifecycle
Create a `setup.ps1` script that executes `docker-compose up -d --build` to spin up the Nginx, FastAPI, and Ollama containers.

### R3. Pre-fetch LLM Models
The `setup.ps1` script must automatically execute `docker exec` against the running Ollama container to pull the `qwen2.5:7b` model immediately after startup.

### R4. Automated E2E Verification
The script must conclude by running the isolated test runner (`docker-compose -f docker-compose.test.yml up --abort-on-container-exit --build`) to guarantee the deployment is healthy.

## Acceptance Criteria

### Execution & Validation
- [ ] `docker-compose.yml` is successfully updated with Ollama and AMD GPU configurations.
- [ ] A `setup.ps1` script exists and handles the full deployment lifecycle.
- [ ] The `setup.ps1` script successfully pre-fetches `qwen2.5:7b` automatically.
- [ ] The `setup.ps1` script triggers the E2E tests which pass with an exit code of 0.
- [ ] All required containers (Nginx, API, Ollama) start successfully without native host dependencies.

