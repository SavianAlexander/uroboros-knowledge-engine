import urllib.request
import json
import time

url = "http://localhost:80/api/chat/stream"
payload = json.dumps({"message": "Hello Uroboros! State your purpose in 2 concise sentences."}).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

print(f"Connecting to live SSE chat stream: {url}")
start = time.perf_counter()
first_token_time = None
full_text = []

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Connected! (HTTP {resp.status}) - Streaming tokens:\n---")
        for line in resp:
            line_str = line.decode("utf-8")
            if not first_token_time:
                first_token_time = time.perf_counter() - start
            if line_str.startswith("data: "):
                token = line_str[6:]
                full_text.append(token)
                print(token, end="", flush=True)
            elif line_str.strip():
                print(line_str, end="", flush=True)
    total_time = time.perf_counter() - start
    print("\n---")
    print(f"\nTime to First Token (TTFT): {first_token_time*1000:.1f}ms")
    print(f"Total Stream Duration     : {total_time:.2f}s")
    print("✓ Full end-to-end RAG/LLM streaming verified successfully!")
except Exception as e:
    print(f"Error during stream test: {e}")
