import os
import sys
import time
import threading
import shutil
import uvicorn
from pathlib import Path
from playwright.sync_api import sync_playwright

# Setup paths and environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
import know
import main

PORT = 8035
DB_FILE = "screenshot_temp.db"
SANDBOX_DIR = Path("test_sandbox_screenshot").resolve()

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=PORT, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def cleanup():
    # Cleanup DB
    for suffix in ["", "-wal", "-shm"]:
        fpath = DB_FILE + suffix
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
    # Cleanup Sandbox
    if SANDBOX_DIR.exists():
        try:
            shutil.rmtree(SANDBOX_DIR)
        except Exception:
            pass

def main_capture():
    cleanup()
    SANDBOX_DIR.mkdir(exist_ok=True)
    
    # Configure know.DB_FILE and main.ACTIVE_DIR before initialization
    know.DB_FILE = DB_FILE
    main.ACTIVE_DIR = str(SANDBOX_DIR)
    know.init_db()

    # Pre-populate sandbox and database with some files
    files_data = [
        ("quantum_physics.txt", "This document details quantum mechanics, gravity, planetary orbits, and astrophysics calculations."),
        ("data_report.csv", "mime_type,count,size\ntext/plain,12,12800\napplication/pdf,4,500000"),
        ("ai_algorithms.docx", "Artificial intelligence, machine learning model details and neural networks study.")
    ]
    for fname, content in files_data:
        fpath = SANDBOX_DIR / fname
        fpath.write_text(content, encoding="utf-8")

    # Index them
    know.index_directory(str(SANDBOX_DIR))

    # Add dummy search history, auto rule, sync peer
    conn = know.get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO auto_rules (pattern, tag) VALUES (?, ?)", ("\\bphysics\\b", "Physics"))
    cursor.execute("INSERT INTO sync_peers (address, name) VALUES (?, ?)", ("192.168.1.50:8000", "node-abc-123"))
    conn.commit()
    conn.close()

    # Start FastAPI server
    srv = ServerThread()
    srv.start()
    time.sleep(2.0)  # Wait for server to boot

    screenshots_dir = Path("docs/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            # Launch chromium in a fixed viewport size matching typical display
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            
            # Navigate to web app
            page.goto(f"http://127.0.0.1:{PORT}/")
            time.sleep(2.0) # wait for D3 and timeline rendering

            # Take Workspace Screenshot (Dashboard)
            print("Capturing dashboard_view.png...")
            page.screenshot(path=str(screenshots_dir / "dashboard_view.png"))

            # Navigate to Search & Graph view
            print("Navigating to Search & Graph view...")
            page.click("button:has-text('Search & Graph')")
            time.sleep(1.5) # Wait for animation/d3 rendering
            
            # Fill query and perform search to populate results
            page.fill("input[placeholder*='Search']", "physics")
            page.press("input[placeholder*='Search']", "Enter")
            time.sleep(2.0) # wait for search response and d3 update
            
            print("Capturing search_results_view.png...")
            page.screenshot(path=str(screenshots_dir / "search_results_view.png"))

            # Navigate to Configuration view
            print("Navigating to Configuration view...")
            page.click("button:has-text('Configuration')")
            time.sleep(1.5) # Wait for layout view swap
            
            print("Capturing config_rules_view.png...")
            page.screenshot(path=str(screenshots_dir / "config_rules_view.png"))

            # Navigate to Chat view
            print("Navigating to Chat view...")
            page.click("button:has-text('Chat')")
            time.sleep(1.0) # Wait for chat tab animation
            
            # Send a mock message to show interaction in screenshot
            page.fill("#chat-input", "Show me the database stats")
            page.press("#chat-input", "Enter")
            time.sleep(1.0) # Wait for assistant response text to render
            
            print("Capturing chat_view.png...")
            page.screenshot(path=str(screenshots_dir / "chat_view.png"))

            browser.close()
            print("Screenshots captured successfully.")
    finally:
        srv.stop()
        srv.join(timeout=5.0)
        cleanup()

if __name__ == "__main__":
    main_capture()
