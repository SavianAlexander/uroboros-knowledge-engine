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
from src.core.shutdown import register_shutdown_handlers, execute_clean_shutdown
from src.domain.process_manager import check_uroboros_health, is_port_bound

register_shutdown_handlers()

DEFAULT_PORT = int(os.environ.get("PORT", 8085))

def launch_server(port=DEFAULT_PORT):
    """Run FastAPI uvicorn server in background thread."""
    uvicorn.run(main.app, host="127.0.0.1", port=port, log_level="warning")

def open_ui(port=DEFAULT_PORT):
    """Open desktop web browser window after polling health check."""
    for _ in range(40):
        time.sleep(0.15)
        if check_uroboros_health(port):
            webbrowser.open(f"http://127.0.0.1:{port}")
            break

def main_desktop(port=DEFAULT_PORT, auto_open=True):
    """Main desktop application entrypoint."""
    print("===================================================", flush=True)
    print("   Launching Uroboros Knowledge Hub Desktop App... ", flush=True)
    print("===================================================", flush=True)

    if is_port_bound(port) and check_uroboros_health(port):
        print(f"[INFO] Uroboros Knowledge Engine already running on port {port}. Opening browser...", flush=True)
        webbrowser.open(f"http://127.0.0.1:{port}")
        return None

    print(f"Backend Server: http://127.0.0.1:{port}", flush=True)
    print("Initializing Database & Web Engine...", flush=True)
    
    server_thread = threading.Thread(target=launch_server, args=(port,), daemon=True)
    server_thread.start()
    
    if auto_open:
        b_thread = threading.Thread(target=open_ui, args=(port,), daemon=True)
        b_thread.start()
    
    print("Ready! Waiting for server ready signal...", flush=True)
    return server_thread

if __name__ == "__main__":
    t = main_desktop(DEFAULT_PORT, auto_open=True)
    if t is None:
        sys.exit(0)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Uroboros Knowledge Hub Desktop App...", flush=True)
        execute_clean_shutdown()
        sys.exit(0)
