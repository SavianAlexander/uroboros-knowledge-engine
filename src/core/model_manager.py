import os
import threading
import logging

try:
    import llama_cpp
    Llama = llama_cpp.Llama
except (KeyboardInterrupt, MemoryError, SystemExit):
    raise
except Exception as e:
    import logging; logging.getLogger(__name__).exception(f"Swallowed error in model_manager.py: {e}")
    Llama = None
    logging.warning(f"llama_cpp not available: {e}")

_lock = threading.Lock()

import time
import subprocess

# Enforce Ollama engine single-instance limits at startup
os.environ["OLLAMA_NUM_PARALLEL"] = "1"
os.environ["OLLAMA_MAX_LOADED_MODELS"] = "1"

_llm_semaphore = threading.Semaphore(2)
_process_cleanup_lock = threading.Lock()
_last_cleanup_time = 0.0

def ensure_single_llama_server_instance():
    """
    Scans Windows processes and terminates duplicate llama-server.exe instances,
    guaranteeing at most 1 active llama-server process runs in memory.
    """
    global _last_cleanup_time
    now = time.time()
    if now - _last_cleanup_time < 10.0:
        return

    with _process_cleanup_lock:
        _last_cleanup_time = now
        try:
            cmd = ["powershell", "-NoProfile", "-Command", "Get-Process -Name 'llama-server' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"]
            out = subprocess.check_output(cmd, text=True, timeout=5).strip()
            if not out:
                return
            pids = [int(p.strip()) for p in out.splitlines() if p.strip().isdigit()]
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
        import requests
        self.session = requests.Session()

    def _post_with_fallback(self, endpoint: str, data: dict, timeout: int = 15):
        ensure_single_llama_server_instance()
        endpoints = [
            f"{self.base_url}{endpoint}",
            f"http://127.0.0.1:11434/v1{endpoint}",
            f"http://localhost:11434/v1{endpoint}"
        ]
        for url in endpoints:
            try:
                res = self.session.post(url, json=data, timeout=timeout)
                if res.status_code == 200:
                    return res.json()
            except Exception:
                continue
        return None

    def __call__(self, prompt, **kwargs):
        if not _llm_semaphore.acquire(blocking=False):
            logging.warning("LLM concurrency limit reached; skipping background inference for stability.")
            return {"choices": [{"text": ""}]}
        try:
            model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "2m")
            data = {
                "model": model,
                "prompt": prompt,
                "max_tokens": min(kwargs.get("max_tokens", 256), 512),
                "keep_alive": keep_alive,
                "options": {"num_ctx": 2048, "num_thread": 4, "low_vram": True}
            }
            res_body = self._post_with_fallback("/completions", data)
            if res_body:
                return {"choices": [{"text": res_body.get("choices", [{}])[0].get("text", "")}]}
            return {"choices": [{"text": ""}]}
        except Exception as e:
            logging.error(f"Ollama inference failed: {e}")
            return {"choices": [{"text": ""}]}
        finally:
            _llm_semaphore.release()
            
    def create_chat_completion(self, messages, **kwargs):
        if not _llm_semaphore.acquire(blocking=False):
            logging.warning("LLM concurrency limit reached; skipping background chat inference for stability.")
            return {"choices": [{"message": {"content": ""}}]}
        try:
            model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
            keep_alive = os.environ.get("OLLAMA_KEEP_ALIVE", "2m")
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": min(kwargs.get("max_tokens", 256), 512),
                "keep_alive": keep_alive,
                "options": {"num_ctx": 2048, "num_thread": 4, "low_vram": True}
            }
            res_body = self._post_with_fallback("/chat/completions", data)
            if res_body:
                return res_body
            return {"choices": [{"message": {"content": ""}}]}
        except Exception as e:
            logging.error(f"Ollama chat inference failed: {e}")
            return {"choices": [{"message": {"content": ""}}]}
        finally:
            _llm_semaphore.release()



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
        import logging
        from fastapi import HTTPException
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

    def create_chat_completion(self, messages, **kwargs):
        import logging
        from fastapi import HTTPException
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
                openai_base = os.environ.get("OPENAI_API_BASE")
                if openai_base:
                    self._llm = OllamaClient(openai_base)
                    return self._llm

                if Llama is not None:
                    try:
                        model_path = os.environ.get("LLM_MODEL_PATH", "models/llama-2-7b.Q4_K_M.gguf")
                        self._llm = IsolatedLlamaClient(model_path)
                    except Exception as e:
                        logging.error(f"Failed to setup LLM isolation in model_manager.py: {e}")
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

def expand_query_with_llm(query: str) -> str:
    return query
