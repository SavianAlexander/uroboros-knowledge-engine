import os, sys, json
from typing import Dict, Any, Optional

scripts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".agents", "skills", "neuro-copilot", "scripts"))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    import standalone_llama_bridge
except ImportError:
    standalone_llama_bridge = None


def generate_standalone_completion(
    prompt: str,
    model: str = "phi4-mini",
    max_tokens: int = 512,
    temperature: float = 0.2,
    runtime: str = "vulkan"
) -> Dict[str, Any]:
    """
    Fallback completion handler using local Vulkan/HIP standalone binary.
    """
    if standalone_llama_bridge:
        res = standalone_llama_bridge.run_standalone_inference(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            runtime=runtime
        )
        if res.get("status") == "success":
            return {
                "choices": [{"text": res.get("response", "")}],
                "model": f"{model}-standalone-{runtime}",
                "usage": {"total_tokens": max_tokens}
            }
    return {
        "choices": [{"text": "Error: Standalone LLM bridge unavailable."}],
        "model": "error",
        "usage": {}
    }
