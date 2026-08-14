import os
import sys
import time
import shutil
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
                time.sleep(2)
                session_item = page.locator("p:has-text('SQLite WAL Architecture')").first
                if session_item.count() > 0:
                    session_item.click()
                    time.sleep(1.5)
                canvas_btn = page.locator("button:has-text('Open Canvas')").first
                if canvas_btn.count() > 0:
                    canvas_btn.click()
                    time.sleep(1.5)
                time.sleep(1)

            elif view_id == "workspace":
                time.sleep(3)

            elif view_id == "search":
                search_input = page.locator("input[placeholder*='Search']").first
                if search_input.count() > 0:
                    search_input.fill("gallup")
                    page.locator("button[type='submit']").first.click()
                    try:
                        page.wait_for_selector(".font-serif-claude", timeout=8000)
                    except Exception:
                        pass
                    time.sleep(1)

            elif view_id == "graph":
                time.sleep(5)  # Wait for WebGL 3D graph cluster physics simulation

            target_docs = os.path.join(docs_dir, f"{prefix}.png")
            target_artifact = os.path.join(artifact_dir, f"{prefix}.png")
            
            page.screenshot(path=target_docs)
            page.screenshot(path=target_artifact)
            print(f"Captured {prefix}.png")

        # 9. Command Palette Modal
        print("Opening view: command_palette...")
        page.goto(f"http://127.0.0.1:{port}/#/dashboard")
        time.sleep(1.5)
        palette_btn = page.locator("[data-testid='command-palette-btn'], button:has-text('⌘K')").first
        if palette_btn.count() > 0:
            palette_btn.click()
            time.sleep(1)
        else:
            page.keyboard.press("Control+k")
            time.sleep(1)
        
        target_docs_09 = os.path.join(docs_dir, "09_command_palette.png")
        target_artifact_09 = os.path.join(artifact_dir, "09_command_palette.png")
        page.screenshot(path=target_docs_09)
        page.screenshot(path=target_artifact_09)
        print("Captured 09_command_palette.png")
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 10. Light Mode Theme
        print("Opening view: light_mode...")
        page.evaluate("() => { localStorage.setItem('uroboros_theme', 'light'); window.location.reload(); }")
        time.sleep(3.5)
        
        target_docs_10 = os.path.join(docs_dir, "10_light_mode.png")
        target_artifact_10 = os.path.join(artifact_dir, "10_light_mode.png")
        page.screenshot(path=target_docs_10)
        page.screenshot(path=target_artifact_10)
        print("Captured 10_light_mode.png")

        # Synchronize legacy aliases for complete GitHub & documentation backwards-compatibility
        aliases = [
            ("03_workspace_studio.png", "02_workspace.png"),
            ("04_search_explorer.png", "03_search.png"),
            ("05_ingestion_pipeline.png", "04_ingestion.png"),
            ("06_knowledge_graph.png", "05_graph.png"),
            ("02_chat_studio.png", "06_chat.png"),
            ("07_config_orchestration.png", "07_config.png"),
            ("08_settings_maintenance.png", "08_settings.png"),
        ]
        for src, dst in aliases:
            src_path = os.path.join(docs_dir, src)
            dst_path = os.path.join(docs_dir, dst)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
                print(f"Synchronized alias {dst} -> {src}")

        browser.close()
    print("Snapshot capture and synchronization complete.")

if __name__ == "__main__":
    main()
