# Original User Request

## Initial Request — 2026-06-30T05:17:19-04:00

Improve the main dashboard panel in Uroboros Knowledge Engine to display high-value, interactive statistics and remove low-value placeholders.

Working directory: c:\Users\Administrator\Desktop\Neuro Alexander
Integrity mode: benchmark

## Requirements

### R1. Dashboard Metrics Overhaul (UI & API)
- Replace "Free Storage Capacity" and "Query Cache Hit Ratio" stats cards with **Total Tags** and **Active Auto-Tag Rules** stats cards.
- Update the `/api/stats` API endpoint on the backend to count distinct tags from the database (`tags` table) and rules count from the `auto_rules` table, sending them to the frontend.
- Display these values dynamically inside the stats grid cards.

### R2. Interactive Recent Search Queries List
- Add a new dashboard container `#recent-searches-panel` showing the 5 most recent search queries.
- Read search history via the `/api/search/history` endpoint.
- Clicking any query item in this list must:
  - Fill the query input `#search-input`
  - Perform the lexical-semantic search immediately
  - Focus/switch the view active tab to the "Search & Graph" tab.

### R3. LAN Peer Nodes List Panel
- Add a dashboard container `#sync-peers-panel` listing all registered sync nodes from the `sync_peers` table (retrieved via `/api/stats`).
- Display each peer's name and address.

## Acceptance Criteria

### Metric Accuracy & API Compliance
- [ ] `/api/stats` returns `total_tags` and `total_rules` counts correctly.
- [ ] The dashboard displays correct total tags and auto-tag rules counts.
- [ ] No layout broken CSS files or styling issues exist on the dashboard grid.

### Interactive Navigation
- [ ] Clicking a recent search query item triggers a search execution.
- [ ] The active view tab switches to "Search & Graph" automatically upon executing a recent search.
- [ ] The sync peer panel correctly shows registered LAN nodes.
