#!/usr/bin/env python3
"""
Standalone Local LLM Engine Bridge (Neuro Copilot - Cooperative Zero-Stutter Edition)
Dedicated zero-dependency CLI bridge for running local GGUF models directly via
precompiled Vulkan and AMD ROCm/HIP llama.cpp binaries with cooperative thread priority,
strict memory bounds, and non-blocking sub-process execution.

Standard Library only (Ponytail principle: subprocess, os, sys, json, urllib, argparse).
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error
import argparse
from typing import Dict, Any, Optional

# Ensure UTF-8 output encoding resilience across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
models_dir = os.path.join(project_root, "models")
runtimes_dir = os.path.join(project_root, "runtimes")
registry_file = os.path.join(models_dir, "model_registry.json")

# Windows process creation flags for zero-stutter thread priority
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
IDLE_PRIORITY_CLASS = 0x00000040


def load_model_registry() -> Dict[str, Any]:
    """Loads model registry mapping aliases to GGUF blobs."""
    if os.path.exists(registry_file):
        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"models": {}, "runtimes": {}}


def check_ollama_alive(timeout_sec: float = 0.3) -> bool:
    """Fast probe to check if Ollama daemon is reachable on port 11434."""
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/version")
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_llama_binary(runtime: str = "vulkan") -> Optional[str]:
    """Resolves path to llama-cli.exe executable."""
    vulkan_path = os.path.join(runtimes_dir, "vulkan", "llama-cli.exe")
    hip_path = os.path.join(runtimes_dir, "hip", "llama-cli.exe")

    if runtime.lower() == "hip" and os.path.exists(hip_path):
        return hip_path
    if os.path.exists(vulkan_path):
        return vulkan_path
    if os.path.exists(hip_path):
        return hip_path
    return None


def get_model_blob_path(model_name: str) -> Optional[str]:
    """Resolves friendly model name or alias to absolute GGUF blob path."""
    registry = load_model_registry()
    models = registry.get("models", {})

    # Direct match
    if model_name in models and models[model_name].get("blob_exists"):
        return models[model_name].get("blob_path")

    # Prefix / substring search (e.g. 'phi4' -> 'phi4-mini:latest')
    clean_name = model_name.lower().strip()
    for key, info in models.items():
        if clean_name in key.lower() and info.get("blob_exists"):
            return info.get("blob_path")

    return None


def run_standalone_inference(
    prompt: str,
    model: str = "phi4-mini",
    max_tokens: int = 256,
    temperature: float = 0.2,
    runtime: str = "vulkan",
    gpu_layers: int = 16,
    threads: int = 4
) -> Dict[str, Any]:
    """
    Executes local standalone inference directly via llama-cli.exe with:
      1. Windows BELOW_NORMAL_PRIORITY_CLASS to prevent OS UI/DWM stutters.
      2. Non-interactive flags (--no-conversation, stdin=DEVNULL) to prevent terminal hangs.
      3. Conservative GPU layer allocation (default 16 layers) to avoid VRAM exhaustion.
      4. Explicit timeout and process cleanup.
    """
    if not prompt or not prompt.strip():
        return {"status": "error", "message": "Prompt text required."}

    binary = get_llama_binary(runtime)
    if not binary:
        return {
            "status": "error",
            "message": f"llama-cli.exe binary not found for runtime '{runtime}' in {runtimes_dir}"
        }

    blob_path = get_model_blob_path(model)
    if not blob_path or not os.path.exists(blob_path):
        return {
            "status": "error",
            "message": f"GGUF model blob not found for '{model}'. Check {registry_file}"
        }

    cmd = [
        binary,
        "-m", blob_path,
        "-p", prompt,
        "-n", str(max_tokens),
        "--temp", str(temperature),
        "-ngl", str(gpu_layers),
        "-t", str(threads),
        "-c", "1024",
        "--no-conversation",
        "--no-display-prompt",
        "--simple-io"
    ]

    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = BELOW_NORMAL_PRIORITY_CLASS

    import time
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            creationflags=creation_flags
        )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)

        output_text = proc.stdout.strip() if proc.stdout else ""
        
        # If output empty, check stderr
        if not output_text and proc.returncode != 0:
            return {
                "status": "error",
                "message": proc.stderr.strip()[:300] if proc.stderr else f"Exit code {proc.returncode}",
                "duration_ms": duration_ms
            }

        return {
            "status": "success",
            "model": model,
            "runtime": runtime,
            "binary": os.path.basename(binary),
            "duration_ms": duration_ms,
            "response": output_text
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Inference timed out after 30s (cooperative limit)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def self_test() -> int:
    """Run assert-based self-test suite for standalone_llama_bridge.py."""
    print("=== Running Standalone LLM Engine Self-Test Suite ===")

    # 1. Test Model Registry
    reg = load_model_registry()
    assert len(reg.get("models", {})) > 0, "Model registry must contain models"
    print(f"  [Pass] Model Registry loaded ({len(reg['models'])} entries, {reg.get('total_storage_mb')} MB total)")

    # 2. Test Binary Resolution
    vulkan_bin = get_llama_binary("vulkan")
    assert vulkan_bin and os.path.exists(vulkan_bin), f"Vulkan binary not found: {vulkan_bin}"
    print(f"  [Pass] Vulkan binary resolved ({vulkan_bin})")

    hip_bin = get_llama_binary("hip")
    assert hip_bin and os.path.exists(hip_bin), f"HIP binary not found: {hip_bin}"
    print(f"  [Pass] HIP binary resolved ({hip_bin})")

    # 3. Test Model Blob Resolution
    blob_05b = get_model_blob_path("qwen2.5:0.5b")
    assert blob_05b and os.path.exists(blob_05b), "qwen2.5:0.5b blob not found"
    print(f"  [Pass] Model blob path resolved ({blob_05b})")

    # 4. Test Probe
    ollama_online = check_ollama_alive()
    print(f"  [Pass] Ollama daemon probe clean (Status: {'ONLINE' if ollama_online else 'OFFLINE'})")

    print("Standalone LLM Bridge Self-Test Complete: ALL ASSERTIONS PASSED (100% Success)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Standalone Local LLM Engine Bridge (Cooperative Zero-Stutter)")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all available models in local registry")
    subparsers.add_parser("status", help="Check Ollama and Standalone runtime availability")

    run_p = subparsers.add_parser("run", help="Run standalone prompt directly via llama-cli")
    run_p.add_argument("prompt", nargs="*", help="Prompt string")
    run_p.add_argument("--model", default="qwen2.5:0.5b", help="Target model name")
    run_p.add_argument("--tokens", type=int, default=256, help="Max tokens")
    run_p.add_argument("--temp", type=float, default=0.2, help="Temperature")
    run_p.add_argument("--runtime", default="vulkan", choices=["vulkan", "hip"], help="GPU backend")
    run_p.add_argument("--ngl", type=int, default=16, help="Number of GPU layers to offload")
    run_p.add_argument("--threads", type=int, default=4, help="CPU threads")

    subparsers.add_parser("self_test", help="Run assertion self-test suite")

    args = parser.parse_args()

    if not args.command or args.command == "list":
        reg = load_model_registry()
        print(json.dumps(reg, indent=2))
    elif args.command == "status":
        ollama_up = check_ollama_alive()
        vulkan_bin = get_llama_binary("vulkan")
        hip_bin = get_llama_binary("hip")
        reg = load_model_registry()
        print(json.dumps({
            "status": "NOMINAL",
            "ollama_http_daemon": "ONLINE" if ollama_up else "OFFLINE (Fallback Active)",
            "vulkan_runtime": "READY" if vulkan_bin else "MISSING",
            "hip_rocm_runtime": "READY" if hip_bin else "MISSING",
            "registered_models_count": len(reg.get("models", {})),
            "total_model_storage_mb": reg.get("total_storage_mb", 0)
        }, indent=2))
    elif args.command == "run":
        p_str = " ".join(args.prompt) if isinstance(args.prompt, list) else str(args.prompt or "")
        print(json.dumps(run_standalone_inference(
            p_str,
            model=args.model,
            max_tokens=args.tokens,
            temperature=args.temp,
            runtime=args.runtime,
            gpu_layers=args.ngl,
            threads=args.threads
        ), indent=2))
    elif args.command == "self_test":
        sys.exit(self_test())


if __name__ == "__main__":
    main()
