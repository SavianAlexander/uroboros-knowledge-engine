import urllib.request
import json
import time

token = "tt_e6a9eb4aea4f1437387cd78fd836d78a5570cdb67bbff9908314a521cfef2daa"
endpoints = [
    ("Health", "http://localhost:3002/api/health"),
    ("Profile", "http://localhost:3002/api/profile"),
    ("Projects", "http://localhost:3002/api/projects"),
    ("Tasks (Default)", "http://localhost:3002/api/tasks"),
    ("Tasks (Today)", "http://localhost:3002/api/tasks?type=today"),
    ("Tasks (Upcoming)", "http://localhost:3002/api/tasks?type=upcoming"),
    ("Areas", "http://localhost:3002/api/areas"),
    ("Habits", "http://localhost:3002/api/habits"),
    ("Notes", "http://localhost:3002/api/notes"),
    ("Notifications", "http://localhost:3002/api/notifications/unread-count")
]

print("=" * 60)
print("   TUDUDI FRONTEND API ENDPOINT DIAGNOSTIC")
print("=" * 60)

for name, url in endpoints:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            elapsed_ms = (time.perf_counter() - start) * 1000
            print(f"[{resp.status}] {name:<20} | {elapsed_ms:>6.2f}ms | Size: {len(data):>7} bytes")
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[{e.code}] {name:<20} | {elapsed_ms:>6.2f}ms | Error: {e.reason}")
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[ERR] {name:<20} | {elapsed_ms:>6.2f}ms | Exception: {e}")

print("=" * 60)
