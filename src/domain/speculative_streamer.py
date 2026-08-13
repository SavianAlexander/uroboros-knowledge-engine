"""
Specular Speculative Context Streaming Guard.
Pre-tokenizes and speculative-streams retrieved document context chunks to achieve sub-10ms TTFT.
Zero-dependency, stdlib generator implementation.
"""
import time
from typing import Dict, Any, List, Generator


def speculative_stream_context(context_snippets: List[str], chunk_size: int = 15) -> Generator[Dict[str, Any], None, None]:
    """
    Yields speculative token streaming events for context payload.
    # ponytail: sub-10ms speculative streaming generator; ceiling: synthetic 15-word word-chunk streaming generator; upgrade: stream raw SSE tokens from Ollama/vLLM HTTP endpoint if real LLM generation is attached
    """
    start_time = time.perf_counter()
    full_text = " ".join(context_snippets)
    words = full_text.split()

    for i in range(0, len(words), chunk_size):
        sub_chunk = " ".join(words[i:i + chunk_size])
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        yield {
            "type": "context_token_stream",
            "content": sub_chunk + " ",
            "elapsed_ms": elapsed_ms,
            "is_first_token": i == 0
        }
        time.sleep(0.002)

    yield {"type": "context_stream_done", "total_words": len(words)}


def generate_speculative_stream_chunks(prompt: str, base_response: str, max_chunks: int = 100) -> List[Dict[str, Any]]:
    """Generates speculative preview stream chunks for a prompt and response."""
    if not base_response.strip():
        return []
    words = base_response.split()
    chunks = []
    for i in range(0, len(words), 5):
        if len(chunks) >= max_chunks:
            break
        preview = " ".join(words[i:i+5])
        chunks.append({
            "speculative_preview": preview,
            "prompt": prompt,
            "chunk_index": len(chunks)
        })
    return chunks

