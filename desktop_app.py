import os
import sys
import time
import threading
import webbrowser
import uvicorn

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import main

DEFAULT_PORT = 8000

def launch_server(port=DEFAULT_PORT):
    """Run FastAPI uvicorn server in background thread."""
    uvicorn.run(main.app, host="127.0.0.1", port=port, log_level="warning")

def open_ui(port=DEFAULT_PORT):
    """Open desktop web browser window to Knowledge Hub UI."""
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)

def main_desktop(port=DEFAULT_PORT, auto_open=True):
    """Main desktop application entrypoint."""
    print("===================================================")
    print("   Launching Uroboros Knowledge Hub Desktop App... ")
    print("===================================================")
    print(f"Backend Server: http://127.0.0.1:{port}")
    
    server_thread = threading.Thread(target=launch_server, args=(port,), daemon=True)
    server_thread.start()
    
    if auto_open:
        timer = threading.Timer(1.2, lambda: open_ui(port))
        timer.start()
    
    return server_thread

if __name__ == "__main__":
    main_desktop(DEFAULT_PORT, auto_open=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Uroboros Knowledge Hub Desktop App...")
        sys.exit(0)
