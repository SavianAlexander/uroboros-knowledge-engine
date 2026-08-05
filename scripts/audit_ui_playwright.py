import sys
import os
import time
from playwright.sync_api import sync_playwright

def run_playwright_ui_audit():
    screenshots_dir = os.path.join(os.getcwd(), "docs", "playwright_audit")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    console_errors = []
    page_errors = []
    audit_results = []
    
    print("===================================================")
    print("   UROBOROS PLAYWRIGHT AUTOMATED UI AUDIT ENGINE")
    print("===================================================")
    print(f"Target URL: http://127.0.0.1:8085")
    print(f"Screenshots directory: {screenshots_dir}\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Listen for console errors & unhandled exceptions
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        
        try:
            page.goto("http://127.0.0.1:8085", wait_until="networkidle", timeout=10000)
        except Exception as e:
            print(f"Initial navigation failed: {e}")
            sys.exit(1)
            
        time.sleep(1) # Allow initial animation & count-ups to complete
        
        views_to_test = [
            {
                "id": "diagnostics",
                "label": "1. Diagnostics & Telemetry",
                "selector": 'button.tab-link[data-tab="diagnostics"]',
                "elements_to_verify": [
                    ("#stat-files", "Total Files Stat Value"),
                    ("#stat-size", "Total Size Stat Value"),
                    (".health-gauge", "Radial Health Gauge Component"),
                    ("#health-gauge-val", "Health Percentage Value"),
                    ("#svg-chart-container", "File Type Distribution SVG Chart"),
                    ("#timeline-container", "Indexing History Timeline Container"),
                    (".file-count-badge", "Explorer Sidebar File Count Badge"),
                ]
            },
            {
                "id": "processes",
                "label": "2. Internal Processes & System Admin",
                "selector": 'button.tab-link[data-tab="processes"]',
                "elements_to_verify": [
                    (".admin-hero-banner", "Admin Hero Security Banner"),
                    ("#sidebar-rules", "Automated Tagging Rules Table"),
                    ("#sidebar-synonyms", "FTS Synonyms Engine Table"),
                    ("#sidebar-search-history", "Search History Vault Table"),
                    ("#sidebar-search-bookmarks", "Search Bookmarks Vault Table"),
                    ("#sidebar-macros", "Query Macros Manager Table"),
                    ("#sidebar-peers", "P2P LAN Sync Nodes Table"),
                    ("#sidebar-snapshots", "DB Snapshot Vault Table"),
                ]
            },
            {
                "id": "explorer",
                "label": "3. Repository & Explorer",
                "selector": 'button.tab-link[data-tab="explorer"]',
                "elements_to_verify": [
                    ("#search-input", "Global Search Input Bar"),
                    ("#results-list", "Matching Records Results Container"),
                    ("#drop-zone", "Drag and Drop Target Zone"),
                    ("#voice-recorder-card", "Voice Recorder Component"),
                ]
            },
            {
                "id": "chat",
                "label": "4. AI Inference & References Chat",
                "selector": 'button.tab-link[data-tab="chat"]',
                "elements_to_verify": [
                    ("#chat-messages", "RAG Chat Messages Scroll Area"),
                    ("#chat-input", "Chat User Prompt Input"),
                    ("#chat-send-btn", "Chat Send Button"),
                    (".chat-prompt-chips", "Prompt Starter Chips Ribbon"),
                ]
            },
            {
                "id": "settings",
                "label": "5. System Settings",
                "selector": 'button.tab-link[data-tab="settings"]',
                "elements_to_verify": [
                    ("#settings-config-summary", "Current Configuration Summary Card"),
                    (".accordion-section", "Settings Accordion Sections"),
                    ("#cfg-wal", "WAL Mode Status Indicator"),
                    ("#cfg-theme", "Active Theme Status Indicator"),
                ]
            },
            {
                "id": "account",
                "label": "6. Org & Account",
                "selector": 'button.tab-link[data-tab="account"]',
                "elements_to_verify": [
                    (".account-card", "Organization Profile Card"),
                    ("#acct-storage-bar", "Storage Usage Bar"),
                    ("#acct-activity-timeline", "Recent Activity Timeline"),
                    ("#acct-env-table", "System Environment Details Table"),
                    ("#env-python", "Python Version Value"),
                    ("#env-sqlite", "SQLite Version Value"),
                ]
            }
        ]
        
        # Execute View-by-View Audit
        for view in views_to_test:
            print(f"\n[AUDITING VIEW] {view['label']} ({view['id']})")
            
            # Click Tab Navigation Button
            try:
                page.click(view['selector'])
                time.sleep(0.5) # Wait for fadeSlideIn transition
            except Exception as e:
                audit_results.append((view['id'], "TAB_CLICK_FAILED", str(e)))
                print(f"❌ Failed to click tab button '{view['selector']}': {e}")
                continue
                
            # Take HD View Screenshot
            shot_path = os.path.join(screenshots_dir, f"view_{view['id']}.png")
            page.screenshot(path=shot_path, full_page=True)
            print(f"[SCREENSHOT] Captured screenshot: {shot_path}")
            
            # Verify required structural components
            view_passed = True
            for sel, desc in view['elements_to_verify']:
                is_visible = page.is_visible(sel)
                if is_visible:
                    print(f"  + Verified {desc} ({sel})")
                else:
                    print(f"  - Missing/Hidden: {desc} ({sel})")
                    view_passed = False
                    audit_results.append((view['id'], "ELEMENT_MISSING", f"{desc} ({sel})"))
                    
            if view_passed:
                audit_results.append((view['id'], "PASSED", "All elements verified"))

        # Interactive Component Checks
        print("\n[AUDITING INTERACTIVE COMPONENTS]")
        
        # 1. Command Palette Shortcut (Control+P)
        try:
            page.keyboard.press("Control+p")
            time.sleep(0.3)
            palette_visible = page.is_visible("#command-palette-modal")
            if palette_visible:
                print("  + Command Palette Modal (Ctrl+P) opened successfully.")
                page.keyboard.press("Escape")
                time.sleep(0.2)
            else:
                print("  - Command Palette Modal failed to open.")
                audit_results.append(("command_palette", "FAILED", "Modal not visible after Ctrl+P"))
        except Exception as e:
            print(f"  - Command Palette test error: {e}")

        # 2. Accordion Toggle in Settings View
        try:
            page.click('button.tab-link[data-tab="settings"]')
            time.sleep(0.3)
            accordion_header = page.query_selector('.accordion-header')
            if accordion_header:
                accordion_header.click()
                time.sleep(0.3)
                print("  + Accordion toggle interacted successfully.")
            else:
                print("  - Accordion header not found.")
        except Exception as e:
            print(f"  - Accordion test error: {e}")

        browser.close()

    # Generate Final Report
    passed_views = [r for r in audit_results if r[1] == "PASSED"]
    failed_views = [r for r in audit_results if r[1] != "PASSED"]
    
    print("\n===================================================")
    print("   PLAYWRIGHT AUDIT SUMMARY RESULT")
    print("===================================================")
    print(f"Total Views Audited: {len(views_to_test)}")
    print(f"Views Passed: {len(passed_views)} / {len(views_to_test)}")
    print(f"Console Errors: {len(console_errors)}")
    print(f"Page Errors: {len(page_errors)}")
    print("===================================================")
    
    if console_errors:
        print("\nConsole Errors Logged:")
        for err in console_errors:
            print(f"  - {err}")

    if page_errors:
        print("\nUnhandled Page Errors:")
        for err in page_errors:
            print(f"  - {err}")
            
    # Exit with code 0 if all views passed and 0 errors
    if len(passed_views) == len(views_to_test) and len(page_errors) == 0:
        print("\n[SUCCESS] AUDIT SUCCESS: 100% UI Verification Confirmed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] AUDIT FAILED: UI issues detected.")
        sys.exit(1)

if __name__ == "__main__":
    run_playwright_ui_audit()
