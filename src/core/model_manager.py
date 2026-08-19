import json
import requests
import os
import time
import subprocess
import threading
import logging
import atexit
import signal
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

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
DEFAULT_PID_PATH = os.path.join(MODELS_DIR, ".llama_server.pid")


def is_pid_alive(pid: Optional[int]) -> bool:
    """Checks whether a process with the given PID is actively running."""
    if pid is None or pid <= 0:
        return False
    if os.name == "nt":
        if ctypes and wintypes:
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                ERROR_ACCESS_DENIED = 5
                return ctypes.GetLastError() == ERROR_ACCESS_DENIED
            try:
                exit_code = wintypes.DWORD()
                if kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return exit_code.value == STILL_ACTIVE
                return False
            finally:
                kernel32.CloseHandle(handle)
        try:
            os.kill(pid, 0)
            return True
        except (OSError, PermissionError):
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


class LlamaServerProcessSupervisor:
    """
    Supervised process lifecycle manager for llama-server.exe.
    Maintains an atomic PID lockfile, direct child process handles, graceful SIGTERM/Win32 termination,
    and deterministic cleanup on exit.
    """
    _server_proc: Optional[subprocess.Popen] = None
    _lock: threading.Lock = threading.Lock()
    _last_audit_time: float = 0.0
    _pid_file_path: str = DEFAULT_PID_PATH

    def __init__(self, pid_file_path: Optional[str] = None):
        if pid_file_path:
            self._pid_file_path = pid_file_path

    @property
    def server_proc(self) -> Optional[subprocess.Popen]:
        return self._server_proc

    @server_proc.setter
    def server_proc(self, proc: Optional[subprocess.Popen]):
        self._server_proc = proc

    @classmethod
    def get_pid_path(cls) -> str:
        return cls._pid_file_path

    @classmethod
    def set_pid_path(cls, path: str):
        cls._pid_file_path = path

    @classmethod
    def read_pid(cls) -> Optional[int]:
        """Reads PID from atomic lockfile."""
        path = cls.get_pid_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val.isdigit():
                        return int(val)
        except Exception:
            pass
        return None

    @classmethod
    def write_pid(cls, pid: int) -> bool:
        """Atomically writes PID lockfile."""
        path = cls.get_pid_path()
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            temp_path = f"{path}.tmp.{os.getpid()}"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(str(pid))
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
            os.replace(temp_path, path)
            return True
        except Exception as e:
            logging.debug(f"Failed writing llama_server PID file: {e}")
            return False

    @classmethod
    def remove_pid(cls) -> bool:
        """Safely removes PID lockfile."""
        path = cls.get_pid_path()
        try:
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception:
            pass
        return False

    @classmethod
    def register_process(cls, proc: subprocess.Popen):
        """Directly supervises child process handle and updates atomic PID lockfile."""
        with cls._lock:
            cls._server_proc = proc
            if proc and hasattr(proc, "pid") and proc.pid:
                cls.write_pid(proc.pid)

    @classmethod
    def get_active_pid(cls) -> Optional[int]:
        """Returns the PID of an active supervised or locked llama-server instance."""
        with cls._lock:
            if cls._server_proc is not None:
                if cls._server_proc.poll() is None:
                    return cls._server_proc.pid
                cls._server_proc = None

            pid = cls.read_pid()
            if pid and is_pid_alive(pid):
                return pid
            elif pid:
                cls.remove_pid()
            return None

    @classmethod
    def terminate_process(cls, pid: int, timeout: float = 5.0) -> bool:
        """
        Gracefully terminates a process by PID with configurable timeout before forceful kill.
        Uses native Win32/POSIX signaling without brittle shell command strings.
        """
        if pid <= 0 or pid == os.getpid():
            return False

        if not is_pid_alive(pid):
            return True

        # Check if direct child process
        if cls._server_proc is not None and getattr(cls._server_proc, "pid", None) == pid:
            try:
                cls._server_proc.terminate()
                try:
                    cls._server_proc.wait(timeout=timeout)
                    cls._server_proc = None
                    return True
                except subprocess.TimeoutExpired:
                    cls._server_proc.kill()
                    cls._server_proc.wait(timeout=1.0)
                    cls._server_proc = None
                    return True
            except Exception as e:
                logging.debug(f"Direct child process termination error: {e}")

        # Terminate external PID
        try:
            if os.name == "nt":
                if ctypes and wintypes:
                    PROCESS_TERMINATE = 0x0001
                    SYNCHRONIZE = 0x00100000
                    WAIT_OBJECT_0 = 0x00000000
                    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE | SYNCHRONIZE, False, pid)
                    if handle:
                        try:
                            ctypes.windll.kernel32.TerminateProcess(handle, 1)
                            wait_ms = int(timeout * 1000)
                            ctypes.windll.kernel32.WaitForSingleObject(handle, wait_ms)
                        finally:
                            ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    os.kill(pid, signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM)
        except Exception as e:
            logging.debug(f"Graceful termination signal failed for PID {pid}: {e}")

        # Liveness check loop
        start = time.time()
        while time.time() - start < timeout:
            if not is_pid_alive(pid):
                return True
            time.sleep(0.05)

        # Force kill fallback if still alive
        if is_pid_alive(pid):
            try:
                if os.name != "nt":
                    os.kill(pid, signal.SIGKILL)
                else:
                    if ctypes and wintypes:
                        handle = ctypes.windll.kernel32.OpenProcess(0x0001, False, pid)
                        if handle:
                            try:
                                ctypes.windll.kernel32.TerminateProcess(handle, 9)
                            finally:
                                ctypes.windll.kernel32.CloseHandle(handle)
                    else:
                        os.kill(pid, signal.SIGTERM)
            except Exception:
                pass

        return not is_pid_alive(pid)

    @classmethod
    def stop_server(cls, timeout: float = 5.0) -> bool:
        """Stops the active server instance, terminates child processes, and cleans up PID lockfiles."""
        with cls._lock:
            success = True
            if cls._server_proc is not None:
                pid = getattr(cls._server_proc, "pid", None)
                if pid:
                    success = cls.terminate_process(pid, timeout=timeout)
                cls._server_proc = None

            locked_pid = cls.read_pid()
            if locked_pid and locked_pid != os.getpid():
                if is_pid_alive(locked_pid):
                    success = cls.terminate_process(locked_pid, timeout=timeout) and success
                cls.remove_pid()
            return success

    @classmethod
    def ensure_single_instance(cls, timeout: float = 5.0):
        """
        Supervises active instance state, pruning dead PID locks and terminating duplicate
        or legacy instances to guarantee at most 1 active llama-server process in memory.
        """
        now = time.time()
        if now - cls._last_audit_time < 5.0:
            return

        with cls._lock:
            cls._last_audit_time = now
            active_pid = cls.read_pid()
            if active_pid:
                if not is_pid_alive(active_pid):
                    cls.remove_pid()
                elif cls._server_proc is None or cls._server_proc.pid != active_pid:
                    # External active instance detected, terminate to preserve single-flight Ollama VRAM
                    if active_pid != os.getpid():
                        logging.info(f"Purging external llama-server process (PID: {active_pid}) to preserve VRAM.")
                        cls.terminate_process(active_pid, timeout=timeout)
                        cls.remove_pid()


def cleanup_llama_server():
    """Deterministic exit handler ensuring zero orphaned child processes or stale PID locks."""
    try:
        LlamaServerProcessSupervisor.stop_server(timeout=3.0)
    except Exception:
        pass


# Register deterministic atexit teardown handler
atexit.register(cleanup_llama_server)


def ensure_single_llama_server_instance():
    """Backward-compatible proxy invoking LlamaServerProcessSupervisor."""
    LlamaServerProcessSupervisor.ensure_single_instance()


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
        GpuInferenceGuard.acquire(timeout=5.0)
        try:
            for u in urls:
                try:
                    req = urllib.request.Request(u, data=data_bytes, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=5) as resp:
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
                    logging.debug(f"Ollama stream_chat HTTPError {e.code} on {u}: {err_msg}")
                    if e.code == 404:
                        break
                    continue
                except Exception as e:
                    logging.debug(f"Ollama stream_chat fallback on {u}: {e}")
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

