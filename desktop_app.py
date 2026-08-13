import os
import sys
import time
import threading
import webbrowser

# Enable immediate console output flushing
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in desktop_app.py: {e}")
        print(f"Swallowed error in desktop_app.py: {e}")

if getattr(sys, 'frozen', False):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import uvicorn
import main

DEFAULT_PORT = int(os.environ.get("PORT", 8085))

def launch_server(port=DEFAULT_PORT):
    """Run FastAPI uvicorn server in background thread."""
    uvicorn.run(main.app, host="127.0.0.1", port=port, log_level="warning")

def open_ui(port=DEFAULT_PORT):
    """Open desktop web browser window to Knowledge Hub UI."""
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)

def main_desktop(port=DEFAULT_PORT, auto_open=True):
    """Main desktop application entrypoint."""
    print("===================================================", flush=True)
    print("   Launching Uroboros Knowledge Hub Desktop App... ", flush=True)
    print("===================================================", flush=True)
    print(f"Backend Server: http://127.0.0.1:{port}", flush=True)
    print("Initializing Database & Web Engine...", flush=True)
    
    server_thread = threading.Thread(target=launch_server, args=(port,), daemon=True)
    server_thread.start()
    
    if auto_open:
        timer = threading.Timer(1.2, lambda: open_ui(port))
        timer.start()
    
    print("Ready! Opening web application interface...", flush=True)
    return server_thread

if __name__ == "__main__":
    main_desktop(DEFAULT_PORT, auto_open=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Uroboros Knowledge Hub Desktop App...", flush=True)
        sys.exit(0)
