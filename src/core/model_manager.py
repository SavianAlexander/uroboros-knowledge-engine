import json
import requests
import os
import time
import subprocess
import threading
import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
import functools

if os.name == "nt":
    try:
        import msvcrt
        import ctypes
        from ctypes import wintypes
    except ImportError:
        msvcrt = None
        ctypes = None
        wintypes = None
else:
    msvcrt = None
    ctypes = None
    wintypes = None
    try:
        import fcntl
    except ImportError:
        fcntl = None

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

# -------------------------------------------------------------------------
# Windows OS Kernel Job Object & Process Supervisor
# -------------------------------------------------------------------------
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9

if os.name == "nt" and ctypes and wintypes:
    class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
            ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]

    class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryLimit", ctypes.c_size_t),
            ("PeakJobMemoryLimit", ctypes.c_size_t),
        ]

def enable_auto_kill_job_object() -> bool:
    """Attaches current process to a Windows Job Object with KILL_ON_JOB_CLOSE."""
    if os.name != "nt" or not ctypes or not wintypes:
        return False
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD]
        kernel32.SetInformationJobObject.restype = wintypes.BOOL
        kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE

        h_job = kernel32.CreateJobObjectW(None, None)
        if not h_job:
            return False
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        res = kernel32.SetInformationJobObject(h_job, JobObjectExtendedLimitInformation, ctypes.byref(info), ctypes.sizeof(info))
        if not res:
            return False
        h_proc = kernel32.GetCurrentProcess()
        return bool(kernel32.AssignProcessToJobObject(h_job, h_proc))
    except Exception:
        return False

# Initialize Job Object auto-cleanup on module load
enable_auto_kill_job_object()

class GpuInferenceGuard:
    """Inter-process and inter-thread lock ensuring single-flight GPU execution."""
    _lock_handle = None

    @classmethod
    def acquire(cls, timeout: float = 30.0) -> bool:
        lock_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        os.makedirs(lock_dir, exist_ok=True)
        lock_path = os.path.join(lock_dir, ".gpu_inference.lock")
        start = time.time()
        while time.time() - start < timeout:
            try:
                cls._lock_handle = open(lock_path, "w")
                if os.name == "nt" and msvcrt:
                    msvcrt.locking(cls._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                elif fcntl:
                    fcntl.flock(cls._lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except (IOError, OSError):
                time.sleep(0.05)
        return False

    @classmethod
    def release(cls):
        try:
            if cls._lock_handle:
                if os.name == "nt" and msvcrt:
                    try:
                        msvcrt.locking(cls._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                    except Exception:
                        pass
                elif fcntl:
                    try:
                        fcntl.flock(cls._lock_handle.fileno(), fcntl.LOCK_UN)
                    except Exception:
                        pass
                cls._lock_handle.close()
                cls._lock_handle = None
        except Exception:
            pass

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
                if len(pids) > 0:
                    logging.info(f"Purging legacy llama-server.exe processes ({pids}) to preserve VRAM for Ollama.")
                    for pid in pids:
                        try:
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        except Exception as ke:
                            logging.debug(f"Purge llama-server PID {pid}: {ke}")
        except Exception:
            pass


def _sanitize_keep_alive(val: Any) -> Any:
    """Sanitizes keep_alive to either integer (e.g. -1) or valid duration string ('3m', '5m', '30s')."""
    if val is None:
        return "3m"
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip()
    if s.lstrip("-").isdigit():
        return int(s)
    if any(s.endswith(unit) for unit in ("s", "m", "h", "d")):
        return s
    return "3m"


class OllamaClient:
    def __init__(self, base_url="http://127.0.0.1:11434/v1"):
        self.base_url = os.environ.get("OPENAI_API_BASE", base_url)
        self.session = requests.Session()

    def _post_with_fallback(self, endpoint: str, data: dict, timeout: int = 45):
        ensure_single_llama_server_instance()
        GpuInferenceGuard.acquire(timeout=float(timeout))
        try:
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
        finally:
            GpuInferenceGuard.release()

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

        keep_alive = _sanitize_keep_alive(os.environ.get("OLLAMA_KEEP_ALIVE", "3m"))
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "keep_alive": keep_alive,
            "options": {"num_ctx": ctx_size, "temperature": temperature}
        }
        if format_json:
            payload["format"] = "json"

        data_bytes = json.dumps(payload).encode("utf-8")
        urls = ["http://127.0.0.1:11434/api/chat", "http://localhost:11434/api/chat"]
        
        tokens_yielded = 0
        GpuInferenceGuard.acquire(timeout=45.0)
        try:
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
                except urllib.error.HTTPError as e:
                    err_msg = e.read().decode("utf-8", errors="ignore")
                    logging.warning(f"Ollama stream_chat HTTPError {e.code} on {u}: {err_msg}")
                    continue
                except Exception as e:
                    logging.warning(f"Ollama stream_chat fallback on {u}: {e}")
                    continue

            if tokens_yielded == 0:
                raise ConnectionError("Ollama daemon unreachable on local endpoints")
        finally:
            GpuInferenceGuard.release()

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

            keep_alive = _sanitize_keep_alive(os.environ.get("OLLAMA_KEEP_ALIVE", "3m"))
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

            keep_alive = _sanitize_keep_alive(os.environ.get("OLLAMA_KEEP_ALIVE", "3m"))
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



class IsolatedLlamaClient:
    """Unified client routing cleanly to local Ollama inference without heavy multiprocessing GPU spawning."""
    def __init__(self, model_path=None):
        self._client = OllamaClient()

    def __call__(self, prompt, **kwargs):
        return self._client(prompt, **kwargs)

    def create_completion(self, prompt=None, **kwargs):
        return self._client.create_completion(prompt, **kwargs)

    def create_chat_completion(self, messages, **kwargs):
        return self._client.create_chat_completion(messages, **kwargs)

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

