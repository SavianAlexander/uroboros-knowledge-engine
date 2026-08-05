import sys, os, socket, threading, time, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
import know, main, uvicorn
from playwright.sync_api import sync_playwright

know.DB_FILE = 'diag_test.db'
know.reset_db_connections()
know.init_db()

sock = socket.socket(); sock.bind(('127.0.0.1', 0)); port = sock.getsockname()[1]; sock.close()
config = uvicorn.Config(main.app, host='127.0.0.1', port=port, log_level='error')
server = uvicorn.Server(config)
t = threading.Thread(target=server.run, daemon=True); t.start()
for _ in range(30):
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health', timeout=1)
        break
    except: time.sleep(0.2)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(f'http://127.0.0.1:{port}/')
    page.wait_for_selector('.app-container', timeout=5000)
    
    # List ALL elements with IDs inside config-tab-view
    ids = page.evaluate('''() => {
        const v = document.getElementById("config-tab-view");
        if (!v) return ["VIEW NOT FOUND"];
        return Array.from(v.querySelectorAll("[id]")).map(el => el.id);
    }''')
    print("Elements with IDs in config-tab-view:")
    for id in ids:
        print(f"  {id}")
    print(f"Total: {len(ids)}")
    
    browser.close()
server.should_exit = True
for s in ['', '-wal', '-shm']:
    try: os.remove('diag_test.db' + s)
    except: pass
