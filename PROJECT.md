# Project: Uroboros Knowledge Engine UI Redesign

## Architecture
- FastAPI backend serving single-page web application (`index.html`, `style.css`, `app.js`).
- Glassmorphic UI design system with CSS custom properties, Google Fonts Inter, micro-animations, light/dark themes.
- Parity requirement: root `index.html`, `style.css`, `app.js`, `src/assets/`, and `assets/` must match 100% SHA-256 bitwise parity.

## Code Layout
- Root Application UI: `c:\Users\Administrator\Desktop\Neuro Alexander\index.html`, `style.css`, `app.js`
- Asset Mirror 1: `c:\Users\Administrator\Desktop\Neuro Alexander\src\assets\index.html`, `style.css`, `app.js`
- Asset Mirror 2: `c:\Users\Administrator\Desktop\Neuro Alexander\assets\index.html`, `style.css`, `app.js`
- SVG & Image Assets: `src\assets\*`, `src\assets\icons\*`, `assets\*`

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Premium Visual Design System | Frosted glass panels, Google Fonts Inter, micro-animations, cohesive colors, dark/light theme toggle | M1 | R1 |
| 2 | Core Layout & Navigation | Responsive container, sidebar navigation, top app bar, notification toast system | M1 | R1, R2 |
| 3 | View 1: System Health & Stats | System health gauge, file counts, database stats (`/api/health`, `/api/stats`) | M2 | R2 View 1 |
| 4 | View 1: Storage Analytics | Storage MIME & extension breakdown charts (`/api/analytics/storage`) | M2 | R2 View 1 |
| 5 | View 1: Tag Co-occurrence Matrix | Tag distribution & co-occurrence visualization (`/api/analytics/tags`) | M2 | R2 View 1 |
| 6 | View 1: Telemetry & Indexing Timeline | Search activity telemetry & indexing timeline (`/api/analytics/search-activity`) | M2 | R2 View 1 |
| 7 | View 1: Recent Searches | Recent query execution history (`/api/search/history`) | M2 | R2 View 1 |
| 8 | View 1: Directory Tree Sidebar | Interactive vault directory tree (`/api/file/tree`) | M2 | R2 View 1 |
| 9 | View 1: Split-Screen Workspace | Left pane preview (PDF, Image/OCR, Audio/Video, Markdown/Code), right pane editor with toolbar & AI insights (`/api/file/insights`) | M2 | R2 View 1 |
| 10 | View 1: Webhook Workflows Panel | Workflow trigger rules & execution log table (`/api/workflows/triggers`, `/api/workflows/logs`) | M2 | R2 View 1 |
| 11 | View 2: Drag & Drop File Upload | Drag & drop dropzone for workspace uploads (`/api/upload`) | M3 | R2 View 2 |
| 12 | View 2: Audio Memo Recorder | In-browser MediaRecorder → voice memo upload & transcription (`/api/upload`, `/api/transcribe`) | M3 | R2 View 2 |
| 13 | View 2: Search Autocomplete & Validator | Search bar with syntax autocomplete (`/api/search/autocomplete`) & real-time syntax validation (`/api/search/validate`) | M3 | R2 View 2 |
| 14 | View 2: Search Mode Switcher | Keyword (FTS5) vs Semantic (BM25) mode toggle + similarity threshold slider | M3 | R2 View 2 |
| 15 | View 2: Search Results List | Badges, match score, tag pills, highlighted snippets, sort/filter controls (`/api/search`) | M3 | R2 View 2 |
| 16 | View 2: Floating File Inspector Drawer | Metadata, audio/video players, notes (`/api/notes`), tags management (`/api/file/tag`), suggested tags (`/api/suggested_tags`), file actions | M3 | R2 View 2 |
| 17 | View 2: Export Controls & Bookmarks | PDF export drawer (`/api/report/export`), CSV export (`/api/export`), bulk delete (`/api/bulk_delete`), bookmarks vault (`/api/bookmarks`) | M3 | R2 View 2 |
| 18 | View 3: Knowledge Graph Canvas | Full-screen interactive 2D canvas force-directed graph with pan, zoom, minimap | M4 | R2 View 3 |
| 19 | View 3: Graph Layout Presets | Force-directed, Circular, Grid, Tree layout presets | M4 | R2 View 3 |
| 20 | View 3: Node Filtering & Search | Category filters (documents, tags, concepts) + search-to-highlight node filter | M4 | R2 View 3 |
| 21 | View 3: Node Glyphs & Edge Types | Custom node SVG glyphs + `tagged_with`, `wikilink_to` (dashed purple), `shared_tag_cluster` (dotted amber) edge rendering (`/api/graph/*`) | M4 | R2 View 3 |
| 22 | View 4: AI Chat Sidebar & Sessions | Chat sessions list, create/select/delete session (`/api/chat/sessions`) | M5 | R2 View 4 |
| 23 | View 4: GGUF Model Config Panel | Model path, temperature slider (0.0-1.0), context window, web search toggle | M5 | R2 View 4 |
| 24 | View 4: SSE Streaming Chat Stream | Real-time token streaming (`/api/chat/stream`), markdown rendering, code block copy, typing indicator | M5 | R2 View 4 |
| 25 | View 4: Citation Chips & Starter Chips | Grounded document citations, web search chips, prompt starter chips | M5 | R2 View 4 |
| 26 | View 5: Auto-Tag Rules Engine | Regex rules table, add/edit/delete, test preview (`/api/rules`, `/api/rules/test-preview`) | M6 | R2 View 5 |
| 27 | View 5: Synonyms, Macros & Aliases | FTS Synonyms (`/api/synonyms`), Search Macros (`/api/macros`), Tag Aliases (`/api/aliases`) managers | M6 | R2 View 5 |
| 28 | View 5: P2P LAN Peer Synchronization | Discovered/manual peer list (`/api/sync/peers`), delta exchange (`/api/sync/exchange`), sync audit logs (`/api/sync/logs`) | M6 | R2 View 5 |
| 29 | View 5: DB Snapshot Vault | Capture backup, list timestamps, restore snapshot, delete snapshot (`/api/snapshots*`) | M6 | R2 View 5 |
| 30 | View 6: Settings & System Maintenance | DB info (WAL mode, FTS, size), re-index directory (`/api/index`), VACUUM, export CSV stats | M6 | R2 View 6 |
| 31 | View 6: Account Profile & Env Table | Enterprise profile card, SOC 2 badge, storage progress bar, activity timeline, environment table (`/api/system/env`) | M6 | R2 View 6 |
| 32 | Command Palette (Ctrl+P / Cmd+P) | Keyboard-activated spotlight modal for view switching, theme toggle, export, file jumping | M7 | R2 Command Palette |
| 33 | Bitwise Asset Parity Enforcement | Maintain 100% SHA-256 bitwise parity between root `index.html`, `style.css`, `app.js` and copies in `src/assets/` and `assets/` | M7 | R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Design System & Layout Framework | CSS design tokens, glassmorphic layout, sidebar nav, top bar, theme toggle engine, toast system | none | PLANNED |
| M2 | View 1: Dashboard & Workspace | Health gauge, storage analytics, tag matrix, recent search telemetry, directory tree sidebar, split-screen workspace preview/editor, webhook workflows | M1 | PLANNED |
| M3 | View 2: Search & Explorer | Drag-and-drop upload, voice memo recorder, autocomplete/validator search bar, mode switcher, results list, floating inspector, CSV/PDF export, bookmarks, bulk delete | M1 | PLANNED |
| M4 | View 3: Knowledge Graph Canvas | 2D Canvas graph renderer, 4 layout presets (Force, Circular, Grid, Tree), zoom/pan/minimap, node/edge styling, click inspector trigger | M1 | PLANNED |
| M5 | View 4: AI Chat & RAG Streaming | Chat session management, model config panel, SSE token stream, markdown & code copy, citation chips, prompt starters | M1 | PLANNED |
| M6 | View 5 & 6: Config, Processes & Settings | Auto-tag rules, synonyms/macros/aliases, LAN P2P sync, DB snapshot manager, system settings & env table | M1 | PLANNED |
| M7 | Command Palette & Bitwise Parity | Spotlight modal (Ctrl+P / Cmd+P) and 3-way file parity synchronization (`root`, `src/assets/`, `assets/`) | M1-M6 | PLANNED |
| M8 | E2E Test Suite Pass & Final Gate | 100% E2E test suite pass rate + Forensic audit clean verdict | M1-M7 | PLANNED |

## Interface Contracts
### UI Event Bus & State Manager (app.js)
- `state`: Global application state object `{ activeView, theme, search: { query, mode, threshold }, chat: { activeSessionId, isStreaming }, workspace: { activeFile, isDirty }, graph: { layout, selectedNode } }`
- `switchView(viewId)`: Navigates to specified view tab, updates URL hash, triggers view-specific data refresh.
- `toggleTheme()`: Toggles dark/light theme mode, updates `data-theme` attribute on `<html>`, persists setting in `localStorage`.
- `showToast(message, type, duration)`: Displays floating toast notification (success, info, warning, error).
- `openInspector(filePath)`: Fetches file raw data (`GET /api/file/raw`) and opens floating inspector drawer overlay.
