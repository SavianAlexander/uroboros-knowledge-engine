import os
import sys
import time
import asyncio
import threading
import shutil
import uvicorn
from playwright.async_api import async_playwright

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import main

# Target directories
DOCS_DIR = os.path.join(root_dir, "docs", "ux_journey")
ARTIFACT_DIR = r"C:\Users\Administrator\.gemini\antigravity\brain\065e5556-24ac-45d3-a2ee-8e2dfc5a2eca"
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def run_server():
    uvicorn.run(main.app, host="127.0.0.1", port=8096, log_level="warning")

async def capture_all_views():
    print("Starting background server on port 8096...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    await asyncio.sleep(2.5)

    async with async_playwright() as p:
        print("Launching Chromium browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        print("Navigating to Uroboros Knowledge Hub UI...")
        await page.goto("http://127.0.0.1:8096", wait_until="networkidle")
        await asyncio.sleep(1.0)

        # Tab 1: Explorer View
        tab1 = page.locator("button.tab-link[data-tab='workspace']").first
        if await tab1.is_visible():
            await tab1.click()
            await asyncio.sleep(0.5)
        s1_path = os.path.join(DOCS_DIR, "01_explorer_tab.png")
        await page.screenshot(path=s1_path)
        shutil.copy(s1_path, os.path.join(ARTIFACT_DIR, "01_explorer_tab.png"))
        print("Captured 01_explorer_tab.png")

        # Close-up 1: Header Brand Logo Asset
        brand_el = page.locator(".brand-badge-container").first
        if await brand_el.is_visible():
            b_path = os.path.join(DOCS_DIR, "asset_01_header_branding.png")
            await brand_el.screenshot(path=b_path)
            shutil.copy(b_path, os.path.join(ARTIFACT_DIR, "asset_01_header_branding.png"))
            print("Captured asset_01_header_branding.png")

        # Tab 2: RAG AI Assistant View
        tab2 = page.locator("button.tab-link[data-tab='chat']").first
        if await tab2.is_visible():
            await tab2.click()
            await asyncio.sleep(0.5)
        s2_path = os.path.join(DOCS_DIR, "02_rag_chat_tab.png")
        await page.screenshot(path=s2_path)
        shutil.copy(s2_path, os.path.join(ARTIFACT_DIR, "02_rag_chat_tab.png"))
        print("Captured 02_rag_chat_tab.png")

        # Tab 3: Knowledge Graph View & Legend Strip Asset
        tab3 = page.locator("button.tab-link[data-tab='search']").first
        if await tab3.is_visible():
            await tab3.click()
            await asyncio.sleep(0.5)
        s3_path = os.path.join(DOCS_DIR, "03_knowledge_graph_tab.png")
        await page.screenshot(path=s3_path)
        shutil.copy(s3_path, os.path.join(ARTIFACT_DIR, "03_knowledge_graph_tab.png"))
        print("Captured 03_knowledge_graph_tab.png")

        legend_el = page.locator(".graph-legend-strip").first
        if await legend_el.is_visible():
            lg_path = os.path.join(DOCS_DIR, "asset_04_graph_legend_strip.png")
            await legend_el.screenshot(path=lg_path)
            shutil.copy(lg_path, os.path.join(ARTIFACT_DIR, "asset_04_graph_legend_strip.png"))
            print("Captured asset_04_graph_legend_strip.png")

        # Tab 4: System Admin Console View
        tab4 = page.locator("button.tab-link[data-tab='config']").first
        if await tab4.is_visible():
            await tab4.click()
            await asyncio.sleep(0.5)
        s4_path = os.path.join(DOCS_DIR, "04_admin_console_tab.png")
        await page.screenshot(path=s4_path)
        shutil.copy(s4_path, os.path.join(ARTIFACT_DIR, "04_admin_console_tab.png"))
        print("Captured 04_admin_console_tab.png")

        await browser.close()
    print("All Playwright live asset inspection screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture_all_views())
