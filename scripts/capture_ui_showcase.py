import os
import sys
import time
import urllib.request
import threading
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_server(port):
    import uvicorn
    from src.app.server import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")

def main():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for server to start
    for _ in range(30):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "ux_journey"))
    artifact_dir = r"C:\Users\Administrator\.gemini\antigravity\brain\1b9d44a0-d032-41d6-a13b-f18a94b6a3cf"
    os.makedirs(docs_dir, exist_ok=True)
    os.makedirs(artifact_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(f"http://127.0.0.1:{port}/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        views = [
            ("01_dashboard", "dashboard"),
            ("02_chat_studio", "chat"),
            ("03_workspace_studio", "workspace"),
            ("04_search_explorer", "search"),
            ("05_ingestion_pipeline", "ingestion"),
            ("06_knowledge_graph", "graph"),
            ("07_config_orchestration", "config"),
            ("08_settings_maintenance", "settings"),
        ]

        for prefix, view_id in views:
            print(f"Capturing view: {view_id}...")
            # Click sidebar button or evaluate navigation
            page.evaluate(f"""() => {{
                const btn = document.querySelector('button[title*="{view_id}"], button:has-text("{view_id}")');
                if (window.dispatchEvent) {{
                    window.location.hash = '#/{view_id}';
                }}
            }}""")
            
            # Click specific sidebar link if available
            sidebar_btn = page.locator(f"aside button:has-text('{view_id}'), aside button[data-view='{view_id}']").first
            if sidebar_btn.count() > 0:
                sidebar_btn.click()
            else:
                # Try clicking sidebar button by text or icon
                nav_map = {
                    "dashboard": "System Analytics",
                    "chat": "AI Assistant",
                    "workspace": "Document Studio",
                    "search": "Semantic Search",
                    "ingestion": "Ingestion Pipeline",
                    "graph": "3D Knowledge Graph",
                    "config": "Process & Rules",
                    "settings": "System Settings"
                }
                label = nav_map.get(view_id, "")
                if label:
                    loc = page.locator(f"aside button:has-text('{label}')").first
                    if loc.count() > 0:
                        loc.click()

            time.sleep(1.5)

            # Special actions per view to show rich state
            if view_id == "workspace":
                first_file = page.locator("div:has-text('.md'), div:has-text('.pdf'), div:has-text('.txt')").first
                if first_file.count() > 0:
                    first_file.click()
                    time.sleep(1)
            elif view_id == "search":
                search_input = page.locator("input[placeholder*='Search']").first
                if search_input.count() > 0:
                    search_input.fill("knowledge engine")
                    search_btn = page.locator("button:has-text('Explore'), button:has-text('Search')").first
                    if search_btn.count() > 0:
                        search_btn.click()
                        time.sleep(1.5)

            # Capture to docs and artifact dir
            target_docs = os.path.join(docs_dir, f"{prefix}.png")
            target_artifact = os.path.join(artifact_dir, f"{prefix}.png")
            
            page.screenshot(path=target_docs)
            page.screenshot(path=target_artifact)
            print(f"Captured: {target_docs} & {target_artifact}")

        browser.close()

if __name__ == "__main__":
    main()
