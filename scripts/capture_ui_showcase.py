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
            print(f"Opening view: {view_id}...")
            page.goto(f"http://127.0.0.1:{port}/#/{view_id}")
            time.sleep(2)

            if view_id == "chat":
                textarea = page.locator("textarea").first
                if textarea.count() > 0:
                    textarea.fill("Explain SQLite Write-Ahead Logging (WAL) mode with architecture trade-offs.")
                    time.sleep(0.5)

            elif view_id == "workspace":
                time.sleep(2.5)

            elif view_id == "search":
                search_input = page.locator("input[placeholder*='Search']").first
                if search_input.count() > 0:
                    search_input.fill("gallup")
                    page.locator("button[type='submit']").first.click()
                    try:
                        page.wait_for_selector(".font-serif-claude", timeout=12000)
                    except Exception:
                        pass
                    time.sleep(1)

            elif view_id == "graph":
                time.sleep(6)  # Wait for WebGL 3D graph cluster physics simulation

            target_docs = os.path.join(docs_dir, f"{prefix}.png")
            target_artifact = os.path.join(artifact_dir, f"{prefix}.png")
            
            page.screenshot(path=target_docs)
            page.screenshot(path=target_artifact)
            print(f"Captured {prefix}.png")

        browser.close()

if __name__ == "__main__":
    main()
