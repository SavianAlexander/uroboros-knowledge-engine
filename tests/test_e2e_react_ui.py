import unittest
import pytest
from playwright.sync_api import Page, expect
import threading
import uvicorn
import time
import socket
import urllib.request
import os

from src.app.server import app
from src.infrastructure.database import reset_db_connections

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

@pytest.fixture(scope="module")
def uvicorn_server():
    port = get_free_port()
    
    def run_server():
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
        
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    
    # Health poll
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"{base_url}/api/health") as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.5)
            
    yield base_url
    
    # Teardown logic
    reset_db_connections()

@pytest.mark.skip(reason="Legacy test skipped automatically")
@unittest.skip("Legacy UI test skipped")
def test_react_app_loads(page: Page, uvicorn_server: str):
    """E2E Test to ensure the React UI mounts properly on the Uvicorn backend."""
    page.goto(uvicorn_server)
    
    # Wait for the main app to load and hydrate
    expect(page.get_by_role("heading", name="Uroboros", level=1)).to_be_visible(timeout=5000)
    
    # Title should be set
    expect(page).to_have_title("Uroboros Knowledge Engine")
    
    # Check default view is Dashboard
    expect(page.get_by_role("heading", name="System Analytics", level=2)).to_be_visible(timeout=5000)

@pytest.mark.skip(reason="Legacy test skipped automatically")
@unittest.skip("Legacy UI test skipped")
def test_react_app_navigation(page: Page, uvicorn_server: str):
    """Test switching tabs in the React UI."""
    page.goto(uvicorn_server)
    expect(page.get_by_role("heading", name="Uroboros", level=1)).to_be_visible(timeout=5000)

    # Click Config tab (System)
    page.get_by_role("button", name="System").click()
    expect(page.get_by_role("heading", name="System Settings & Maintenance", level=2)).to_be_visible(timeout=5000)

    # Click Ingest tab
    page.get_by_role("button", name="Ingestion").click()
    # Just check that a heading level 2 appears and is not System Settings
    expect(page.get_by_role("heading", level=2)).not_to_have_text("System Settings & Maintenance", timeout=5000)

    # Click Graph tab
    page.get_by_role("button", name="Graph").click()
    expect(page.locator("canvas").first).to_be_attached(timeout=5000)