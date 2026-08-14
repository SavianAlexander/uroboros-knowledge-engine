import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DOCS_DIR = path.resolve(__dirname, '..', 'docs', 'ux_journey');
const VIEWS = [
  {
    "id": "modal_logs",
    "title": "Logs Modal Overlay",
    "path": "/#modal",
    "category": "Interactive Overlays",
    "selector": null,
    "description": "Logs modal dialog view"
  },
  {
    "id": "modal_lineage",
    "title": "Lineage Modal Overlay",
    "path": "/#modal",
    "category": "Interactive Overlays",
    "selector": null,
    "description": "Lineage modal dialog view"
  },
  {
    "id": "captured_01_dashboard",
    "title": "Dashboard",
    "path": "/01_dashboard",
    "category": "Core Application",
    "selector": null,
    "description": "Captured interface showcase for Dashboard"
  },
  {
    "id": "captured_02_chat_studio",
    "title": "Chat Studio",
    "path": "/02_chat_studio",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Chat Studio"
  },
  {
    "id": "captured_02_workspace",
    "title": "Workspace",
    "path": "/02_workspace",
    "category": "Core Application",
    "selector": null,
    "description": "Captured interface showcase for Workspace"
  },
  {
    "id": "captured_03_search",
    "title": "Search",
    "path": "/03_search",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Search"
  },
  {
    "id": "captured_03_workspace_studio",
    "title": "Workspace Studio",
    "path": "/03_workspace_studio",
    "category": "Core Application",
    "selector": null,
    "description": "Captured interface showcase for Workspace Studio"
  },
  {
    "id": "captured_04_ingestion",
    "title": "Ingestion",
    "path": "/04_ingestion",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Ingestion"
  },
  {
    "id": "captured_04_search_explorer",
    "title": "Search Explorer",
    "path": "/04_search_explorer",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Search Explorer"
  },
  {
    "id": "captured_05_graph",
    "title": "Graph",
    "path": "/05_graph",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Graph"
  },
  {
    "id": "captured_05_ingestion_pipeline",
    "title": "Ingestion Pipeline",
    "path": "/05_ingestion_pipeline",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Ingestion Pipeline"
  },
  {
    "id": "captured_06_chat",
    "title": "Chat",
    "path": "/06_chat",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Chat"
  },
  {
    "id": "captured_06_knowledge_graph",
    "title": "Knowledge Graph",
    "path": "/06_knowledge_graph",
    "category": "Knowledge & RAG Studio",
    "selector": null,
    "description": "Captured interface showcase for Knowledge Graph"
  },
  {
    "id": "captured_07_config",
    "title": "Config",
    "path": "/07_config",
    "category": "Configuration & Maintenance",
    "selector": null,
    "description": "Captured interface showcase for Config"
  },
  {
    "id": "captured_07_config_orchestration",
    "title": "Config Orchestration",
    "path": "/07_config_orchestration",
    "category": "Configuration & Maintenance",
    "selector": null,
    "description": "Captured interface showcase for Config Orchestration"
  },
  {
    "id": "captured_08_settings",
    "title": "Settings",
    "path": "/08_settings",
    "category": "Configuration & Maintenance",
    "selector": null,
    "description": "Captured interface showcase for Settings"
  },
  {
    "id": "captured_08_settings_maintenance",
    "title": "Settings Maintenance",
    "path": "/08_settings_maintenance",
    "category": "Configuration & Maintenance",
    "selector": null,
    "description": "Captured interface showcase for Settings Maintenance"
  },
  {
    "id": "captured_09_command_palette",
    "title": "Command Palette",
    "path": "/09_command_palette",
    "category": "Interactive Overlays",
    "selector": null,
    "description": "Captured interface showcase for Command Palette"
  },
  {
    "id": "captured_10_light_mode",
    "title": "Light Mode",
    "path": "/10_light_mode",
    "category": "Theme & Mobile Variants",
    "selector": null,
    "description": "Captured interface showcase for Light Mode"
  }
];

async function runCapture() {
  if (!fs.existsSync(DOCS_DIR)) fs.mkdirSync(DOCS_DIR, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const baseURL = process.env.BASE_URL || 'http://localhost:5173';

  for (let i = 0; i < VIEWS.length; i++) {
    const v = VIEWS[i];
    const prefix = String(i + 1).padStart(2, '0');
    const safeName = v.id.replace(/[^a-zA-Z0-9_]/g, '_');
    const filename = `${prefix}_${safeName}.png`;
    try {
      await page.goto(`${baseURL}${v.path}`, { waitUntil: 'domcontentloaded', timeout: 8000 });
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(DOCS_DIR, filename) });
    } catch (e) {}
  }
  await browser.close();
}
runCapture();
