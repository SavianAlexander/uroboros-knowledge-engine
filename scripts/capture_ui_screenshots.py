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
            import logging; logging.getLogger(__name__).exception("Swallowed error in capture_ui_screenshots.py")
            time.sleep(0.2)

    output_dir = os.environ.get("ARTIFACT_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "ux_journey")))
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        page.goto(f"http://127.0.0.1:{port}/")
        page.wait_for_selector(".app-container", timeout=10000)
        time.sleep(1)

        tabs = ["diagnostics", "processes", "explorer", "chat", "settings", "account"]
        for tab in tabs:
            page.click(f".tab-link[data-tab='{tab}']")
            time.sleep(0.5)
            screenshot_path = os.path.join(output_dir, f"view_{tab}.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Captured: {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    main()
