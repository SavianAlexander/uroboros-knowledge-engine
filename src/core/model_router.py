import re
from typing import Dict, Any

_RE_COMPLEX_CODE = re.compile(r'\b(def |class |import |function|refactor|architecture|sql|fix|bug|algorithm|math|proof|quant)\b', re.IGNORECASE)

def route_prompt_model(prompt: str) -> Dict[str, Any]:
    """
    Intelligent Multi-Model GPU Model Router.
    Selects optimal model based on prompt complexity and domain requirements:
    - Technical/Coding/Architecture -> qwen2.5-coder:14b (14.8B parameters)
    - General Chat/Summarization -> qwen2.5:7b (Ultra-fast ~90 tok/s)
    """
    if not prompt or not str(prompt).strip():
        return {"model": "qwen2.5:7b", "reason": "default_short_prompt"}

    raw = str(prompt).strip()
    is_technical = bool(_RE_COMPLEX_CODE.search(raw)) or len(raw.split()) > 150

    if is_technical:
        return {
            "model": "qwen2.5-coder:14b",
            "reason": "technical_code_and_architecture_reasoning",
            "temperature": 0.2
        }
    else:
        return {
            "model": "qwen2.5:7b",
            "reason": "fast_general_chat",
            "temperature": 0.7
        }
