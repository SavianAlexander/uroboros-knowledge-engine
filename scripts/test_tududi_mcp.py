import subprocess
import json
import time

cmd = [
    r"C:\Users\Administrator\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe",
    "exec",
    "-i",
    "-w",
    "/app/backend",
    "-e",
    "NODE_ENV=production",
    "-e",
    "DB_FILE=/app/db/production.sqlite3",
    "-e",
    "TUDUDI_API_TOKEN=tt_e6a9eb4aea4f1437387cd78fd836d78a5570cdb67bbff9908314a521cfef2daa",
    "tududi",
    "node",
    "modules/mcp/server.js"
]

print("Launching Tududi MCP process over stdio...")
proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

# Send JSON-RPC initialize request
init_req = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
}) + "\n"

proc.stdin.write(init_req)
proc.stdin.flush()

time.sleep(1)

# Read response line from stdout
out_line = proc.stdout.readline()
print(f"STDOUT Response: {out_line.strip()[:200]}")

# Validate if response is valid JSON
try:
    data = json.loads(out_line)
    print("✓ Success! Output is valid JSON-RPC:", data.get("result", {}).get("serverInfo"))
except Exception as e:
    print(f"✗ Failed to parse JSON-RPC: {e}")

proc.terminate()
