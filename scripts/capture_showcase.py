import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get("FRONTEND_URL", "http://localhost")

def capture_ui_showcase():
    print(f"[Showcase Capture] Connecting to {BASE_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--js-flags=--max-old-space-size=512"
            ]
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        try:
            page.goto(BASE_URL)
            page.evaluate("() => localStorage.setItem('uroboros_api_key', 'test_auth_token')")
            page.reload()
            page.wait_for_selector('h1:has-text("Uroboros")', timeout=5000)

            views = [
                ("dashboard", "01_dashboard.png"),
                ("workspace", "02_workspace.png"),
                ("search", "03_search.png"),
                ("ingestion", "04_ingestion.png"),
                ("graph", "05_graph.png"),
                ("chat", "06_chat.png"),
                ("config", "07_config.png"),
                ("settings", "08_settings.png"),
            ]

            for tab, filename in views:
                page.click(f'button[data-tab="{tab}"]')
                page.wait_for_timeout(400)
                target_path = OUTPUT_DIR / filename
                page.screenshot(path=str(target_path), full_page=False)
                print(f"  + Captured {tab} view -> {target_path.name}")

        except Exception as e:
            print(f"  - Error during showcase capture: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    capture_ui_showcase()
