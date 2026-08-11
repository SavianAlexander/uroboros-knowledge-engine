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

import json
import urllib.request
import urllib.error

class OllamaClient:
    def __init__(self, base_url="http://host.docker.internal:11434/v1"):
        self.base_url = base_url
        import requests
        self.session = requests.Session()

    def __call__(self, prompt, **kwargs):
        try:
            url = f"{self.base_url}/completions"
            data = {"model": "qwen2.5:7b", "prompt": prompt, "max_tokens": kwargs.get("max_tokens", 256)}
            res = self.session.post(url, json=data, timeout=30)
            res.raise_for_status()
            res_body = res.json()
            return {"choices": [{"text": res_body.get("choices", [{}])[0].get("text", "")}]}
        except Exception as e:
            logging.error(f"Ollama inference failed: {e}")
            return {"choices": [{"text": ""}]}
            
    def create_chat_completion(self, messages, **kwargs):
        try:
            url = f"{self.base_url}/chat/completions"
            data = {"model": "qwen2.5:7b", "messages": messages, "max_tokens": kwargs.get("max_tokens", 256)}
            res = self.session.post(url, json=data, timeout=30)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logging.error(f"Ollama chat inference failed: {e}")
            return {"choices": [{"message": {"content": ""}}]}


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
