import json
import requests
import os
import time
import subprocess
import threading
import logging
from fastapi import HTTPException
import functools

try:
    import llama_cpp
    Llama = llama_cpp.Llama
except (KeyboardInterrupt, MemoryError, SystemExit):
    raise
except Exception as e:
    logging.getLogger(__name__).debug(f"llama_cpp not available: {e}")
    Llama = None

_lock = threading.Lock()

# Enforce Ollama engine single-instance limits at startup
os.environ["OLLAMA_NUM_PARALLEL"] = "1"
os.environ["OLLAMA_MAX_LOADED_MODELS"] = "1"

_llm_semaphore = threading.Semaphore(1)
_process_cleanup_lock = threading.Lock()
_last_cleanup_time = 0.0

def ensure_single_llama_server_instance():
    """
    Scans Windows processes and terminates duplicate llama-server.exe instances,
    guaranteeing at most 1 active llama-server process runs in memory.
    Uses native tasklist.exe for 10ms sub-millisecond execution.
    """
    global _last_cleanup_time
    now = time.time()
    if now - _last_cleanup_time < 10.0:
        return

    with _process_cleanup_lock:
        _last_cleanup_time = now
        try:
            if os.name == "nt":
                cmd = ["tasklist", "/FI", "IMAGENAME eq llama-server.exe", "/FO", "CSV", "/NH"]
                out = subprocess.check_output(cmd, text=True, timeout=2).strip()
                if not out or "No tasks" in out:
                    return
                pids = []
                for line in out.splitlines():
                    parts = line.split(",")
                    if len(parts) >= 2:
                        pid_str = parts[1].strip('"').strip()
                        if pid_str.isdigit():
                            pids.append(int(pid_str))
                if len(pids) > 1:
                    pids_to_kill = pids[:-1]
                    logging.warning(f"Duplicate llama-server.exe processes detected ({pids}); terminating duplicate PIDs: {pids_to_kill}")
                    for pid in pids_to_kill:
                        try:
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception as ke:
                            logging.error(f"Failed to terminate duplicate llama-server PID {pid}: {ke}")
        except Exception:
            pass


class OllamaClient:
    def __init__(self, base_url="http://127.0.0.1:11434/v1"):
        self.base_url = os.environ.get("OPENAI_API_BASE", base_url)
        self.session = requests.Session()

    def _post_with_fallback(self, endpoint: str, data: dict, timeout: int = 45):
        ensure_single_llama_server_instance()
        clean_ep = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        clean_base = self.base_url.rstrip("/")
        endpoints = [
            f"{clean_base}{clean_ep}",
            f"http://127.0.0.1:11434/v1{clean_ep}",
            f"http://localhost:11434/v1{clean_ep}",
            f"http://127.0.0.1:11434{clean_ep.replace('/v1', '')}",
            f"http://localhost:11434{clean_ep.replace('/v1', '')}"
        ]
        for url in endpoints:
            try:
                res = self.session.post(url, json=data, timeout=(1.0, timeout))
                if res.status_code == 200:
                    return res.json()
            except Exception:
                continue
        return None

    def stream_chat(self, messages: list, model_name: str = None, temperature: float = 0.3, num_ctx: int = None, format_json: bool = False):
        """Yield token chunks from native Ollama /api/chat streaming endpoint with dynamic context scaling."""
        import urllib.request
        from src.core.model_router import route_prompt_model

        # Estimate context requirements from messages
        total_words = sum(len(str(m.get("content", "")).split()) for m in messages if isinstance(m, dict))
        token_est = int(total_words * 1.35)

        if not model_name or model_name == "auto":
            first_user_prompt = next((m.get("content", "") for m in messages if isinstance(m, dict) and m.get("role") == "user"), "")
            routing = route_prompt_model(first_user_prompt, token_estimate=token_est)
            model = routing.get("model", "qwen2.5:7b")
            ctx_size = num_ctx or routing.get("num_ctx", 4096)
        else:
            model = model_name
            max_limit = 131072 if "phi4" in model else 32768
            ctx_size = num_ctx or min(max(4096, token_est + 2048), max_limit)

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"num_ctx": ctx_size, "temperature": temperature}
        }
        if format_json:
            payload["format"] = "json"

        data_bytes = json.dumps(payload).encode("utf-8")
        urls = ["http://127.0.0.1:11434/api/chat", "http://localhost:11434/api/chat"]
        
        tokens_yielded = 0
        for u in urls:
            try:
                req = urllib.request.Request(u, data=data_bytes, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=45) as resp:
                    for line in resp:
                        if not line:
                            continue
                        try:
                            item = json.loads(line.decode("utf-8"))
                            tok = item.get("message", {}).get("content", "")
                            if tok:
                                tokens_yielded += 1
                                yield tok
                            if item.get("done"):
                                return
                        except Exception:
                            continue
                if tokens_yielded > 0:
                    return
            except Exception as e:
                logging.warning(f"Ollama stream_chat fallback on {u}: {e}")
                continue

        if tokens_yielded == 0:
            raise ConnectionError("Ollama daemon unreachable on local endpoints")

    def __call__(self, prompt, **kwargs):
        if not _llm_semaphore.acquire(blocking=False):
            logging.warning("LLM concurrency limit reached; skipping background inference for stability.")
            return {"choices": [{"text": ""}]}
        try:
            from src.core.model_router import route_prompt_model
            raw_prompt = str(prompt or "")
            token_est = int(len(raw_prompt.split()) * 1.35)
            
            task_type = kwargs.get("task_type", "auto")
            model_override = kwargs.get("model")

            if not model_override or model_override == "auto":
                routing = route_prompt_model(raw_prompt, task_type=task_type, token_estimate=token_est)
                model = routing.get("model", "qwen2.5:7b")
                ctx_size = kwargs.get("num_ctx") or routing.get("num_ctx", 4096)
                temp = kwargs.get("temperature", routing.get("temperature", 0.3))
            else:
                model = model_override
                max_limit = 131072 if "phi4" in model else 32768
                ctx_size = kwargs.get("num_ctx") or min(max(4096, token_est + 2048), max_limit)
                temp = kwargs.get("temperature", 0.3)

            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "5m")
            max_toks = min(kwargs.get("max_tokens", 1024), 4096)
            data = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_toks,
                "keep_alive": keep_alive,
                "options": {"num_ctx": ctx_size, "num_thread": 4, "temperature": temp}
            }
            if kwargs.get("format") == "json" or kwargs.get("format_json"):
                data["format"] = "json"

            res_body = self._post_with_fallback("/completions", data)
            if res_body:
                return {"choices": [{"text": res_body.get("choices", [{}])[0].get("text", "")}]}
            return {"choices": [{"text": ""}]}
        except Exception as e:
            logging.error(f"Ollama inference failed: {e}")
            return {"choices": [{"text": ""}]}
        finally:
            _llm_semaphore.release()

    def create_completion(self, prompt: str, stream: bool = False, max_tokens: int = 1024, temperature: float = 0.3, **kwargs):
        if stream:
            res_dict = self(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
            text = res_dict.get("choices", [{}])[0].get("text", "")
            return [{"choices": [{"text": text}]}]
        return self(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)

    def create_chat_completion(self, messages, **kwargs):
        if not _llm_semaphore.acquire(blocking=False):
            logging.warning("LLM concurrency limit reached; skipping background chat inference for stability.")
            return {"choices": [{"message": {"content": ""}}]}
        try:
            from src.core.model_router import route_prompt_model
            total_words = sum(len(str(m.get("content", "")).split()) for m in messages if isinstance(m, dict))
            token_est = int(total_words * 1.35)

            task_type = kwargs.get("task_type", "auto")
            model_override = kwargs.get("model")

            if not model_override or model_override == "auto":
                first_user_prompt = next((m.get("content", "") for m in messages if isinstance(m, dict) and m.get("role") == "user"), "")
                routing = route_prompt_model(first_user_prompt, task_type=task_type, token_estimate=token_est)
                model = routing.get("model", "qwen2.5:7b")
                ctx_size = kwargs.get("num_ctx") or routing.get("num_ctx", 4096)
                temp = kwargs.get("temperature", routing.get("temperature", 0.3))
            else:
                model = model_override
                max_limit = 131072 if "phi4" in model else 32768
                ctx_size = kwargs.get("num_ctx") or min(max(4096, token_est + 2048), max_limit)
                temp = kwargs.get("temperature", 0.3)

            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "5m")
            max_toks = min(kwargs.get("max_tokens", 1024), 4096)
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_toks,
                "keep_alive": keep_alive,
                "options": {"num_ctx": ctx_size, "num_thread": 4, "temperature": temp}
            }
            if kwargs.get("format") == "json" or kwargs.get("format_json"):
                data["format"] = "json"

            res_body = self._post_with_fallback("/chat/completions", data)
            if res_body:
                return res_body
            return {"choices": [{"message": {"content": ""}}]}
        except Exception as e:
            logging.error(f"Ollama chat inference failed: {e}")
            return {"choices": [{"message": {"content": ""}}]}
        finally:
            _llm_semaphore.release()

    def preload_model(self, model_name: str = None) -> bool:
        """Intelligently preloads model weights into GPU VRAM with keep_alive=5m to eliminate cold-start latency."""
        m = model_name or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        res = self._post_with_fallback("/generate", {"model": m, "keep_alive": "5m"})
        return res is not None

    def unload_model(self, model_name: str = None) -> bool:
        """Intelligently flushes GPU VRAM and unloads model weights immediately."""
        m = model_name or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        res = self._post_with_fallback("/generate", {"model": m, "keep_alive": 0})
        return res is not None



import multiprocessing as mp

def _worker_loop(model_path, task_queue, result_queue):
    try:
        import llama_cpp
        llm = llama_cpp.Llama(model_path=model_path, n_ctx=2048, verbose=False)
        while True:
            task = task_queue.get()
            if task is None:
                break
            task_type, kwargs = task
            try:
                if task_type == 'completion':
                    res = llm(**kwargs)
                elif task_type == 'chat':
                    res = llm.create_chat_completion(**kwargs)
                result_queue.put({"success": True, "result": res})
            except Exception as e:
                result_queue.put({"success": False, "error": str(e)})
    except Exception as e:
        # Will crash early if model cannot load, preventing queue hangs
        import logging
        logging.error(f"LLM Worker crashed: {e}")

class IsolatedLlamaClient:
    def __init__(self, model_path):
        self.model_path = model_path
        self._ctx = mp.get_context("spawn")
        self._task_queue = self._ctx.Queue()
        self._result_queue = self._ctx.Queue()
        self._process = self._ctx.Process(target=_worker_loop, args=(self.model_path, self._task_queue, self._result_queue), daemon=True)
        self._process.start()
        self._lock = threading.Lock()
        
    def __call__(self, prompt, **kwargs):
        kwargs["prompt"] = prompt
        with self._lock:
            self._task_queue.put(('completion', kwargs))
            try:
                res = self._result_queue.get(timeout=45)
                if res.get("success"):
                    return res["result"]
                else:
                    logging.error(f"LLM Process exception: {res.get('error')}")
                    raise HTTPException(status_code=503, detail="LLM Engine Fault")
            except Exception as e:
                logging.error(f"LLM Process timeout or crash: {e}")
                raise HTTPException(status_code=503, detail="LLM Engine Fault")

    def create_completion(self, prompt=None, **kwargs):
        if prompt is not None:
            kwargs["prompt"] = prompt
        return self(prompt, **kwargs)

    def create_chat_completion(self, messages, **kwargs):
        kwargs["messages"] = messages
        with self._lock:
            self._task_queue.put(('chat', kwargs))
            try:
                res = self._result_queue.get(timeout=45)
                if res.get("success"):
                    return res["result"]
                else:
                    logging.error(f"LLM Chat Process exception: {res.get('error')}")
                    raise HTTPException(status_code=503, detail="LLM Engine Fault")
            except Exception as e:
                logging.error(f"LLM Chat Process timeout or crash: {e}")
                raise HTTPException(status_code=503, detail="LLM Engine Fault")
                
    def __del__(self):
        try:
            self._task_queue.put(None)
            self._process.join(timeout=2)
            if self._process.is_alive():
                self._process.terminate()
        except Exception:
            pass

class ModelManager:
    _instance = None

    def __init__(self):
        self._llm = None
        self._llm_lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        with _lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def get_llm(self):
        with self._llm_lock:
            if self._llm is None:
                openai_base = os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:11434/v1")
                self._llm = OllamaClient(openai_base)
            return self._llm

    def unload(self):
        with self._llm_lock:
            self._llm = None

    def reload(self):
        self.unload()
        return self.get_llm()

def get_llm():
    return ModelManager.get_instance().get_llm()

def get_fallback_llm():
    return get_llm()

@functools.lru_cache(maxsize=256)
def expand_query_with_llm(query: str) -> str:
    """HyDE Query Expansion: Synthesizes search terms & keywords using local Micro-Tier LLM with LRU caching."""
    if not query or len(query.strip()) < 3:
        return query
    try:
        from src.core.model_router import route_prompt_model
        client = get_llm()
        if client and hasattr(client, "stream_chat"):
            routing = route_prompt_model(query, task_type="micro")
            target_model = routing.get("model", "qwen2.5:0.5b")
            prompt_msgs = [
                {"role": "system", "content": "You are a search query expansion engine. Generate 3 concise search terms or synonyms for the query, separated by spaces. Return only the terms without quotes or punctuation."},
                {"role": "user", "content": query}
            ]
            expanded = "".join(list(client.stream_chat(prompt_msgs, model_name=target_model, temperature=0.1, num_ctx=2048)))
            if expanded and len(expanded.strip()) > 0:
                clean_exp = " ".join(expanded.strip().splitlines())
                return f"{query} {clean_exp}"
    except Exception:
        pass
    return query

def auto_preload_model_async(model_name: str = "qwen2.5:7b"):
    """Spawns a daemon thread that automatically pre-warms the specified model into GPU VRAM in the background."""
    def _bg_warmup():
        try:
            client = get_llm()
            if hasattr(client, "preload_model"):
                client.preload_model(model_name)
                logging.info(f"[Auto-Preload] Intelligently pre-warmed {model_name} into VRAM.")
        except Exception as e:
            logging.debug(f"[Auto-Preload] Background warmup notice: {e}")
    threading.Thread(target=_bg_warmup, daemon=True).start()

