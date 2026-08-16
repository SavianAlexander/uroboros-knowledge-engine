"""
Centralized Configuration & Parameter Specification for Uroboros Knowledge Engine.
Standard: Pure Python standard library (dataclasses, os, typing).
Zero external dependencies.
"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class SearchConfig:
    """Configurable parameters for multi-channel hybrid search & ranking."""
    bm25_weight: float = 0.4
    vector_weight: float = 0.6
    rrf_k: int = 60
    colbert_hamming_threshold: int = 18
    recency_decay_half_life_days: float = 90.0
    recency_decay_multiplier: float = 0.05
    default_top_k: int = 20
    max_top_k: int = 100
    fts_min_token_length: int = 2

@dataclass
class RAGConfig:
    """Configurable parameters for RAG retrieval and generation."""
    chunk_size_chars: int = 500
    chunk_overlap_chars: int = 60
    max_context_chars: int = 16000
    grounding_confidence_threshold: float = 0.65
    min_citations_required: int = 1
    hallucination_penalty_score: float = 0.35
    temperature: float = 0.0
    max_generation_tokens: int = 1024
    enable_counterfactual_check: bool = True

@dataclass
class OllamaConfig:
    """Configurable parameters for local Ollama SLM engine."""
    base_url: str = os.getenv("OLLAMA_API_BASE", "http://host.docker.internal:11434/v1")
    model_name: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    timeout_seconds: float = 60.0
    num_parallel: int = 1
    keep_alive: str = "5m"
    max_loaded_models: int = 1

@dataclass
class DatabaseConfig:
    """Configurable parameters for SQLite database engine."""
    db_file: str = os.path.join(BASE_DIR, "knowledge.db")
    busy_timeout_ms: int = 5000
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = -64000  # 64MB cache
    mmap_size: int = 268435456  # 256MB mmap
    pool_size: int = 10

@dataclass
class VoiceConfig:
    """Configurable parameters for Kokoro Neural TTS & Voice Pipeline."""
    voice_id: str = "af_heart"
    sample_rate: int = 24000
    buffer_size_ms: int = 100
    enable_audio_cache: bool = True

@dataclass
class SystemConfig:
    """Master system configuration registry."""
    base_dir: str = BASE_DIR
    active_dir: str = os.path.join(BASE_DIR, "dumps")
    uploads_dir: str = os.path.join(BASE_DIR, "data", "uploads")
    jwt_secret: str = os.getenv("JWT_SECRET", "uroboros-insecure-dev-secret-key-change-in-prod")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 72
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    is_testing: bool = True
    
    search: SearchConfig = field(default_factory=SearchConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)

# Global singleton configuration instance
settings = SystemConfig()

# Backward-compatibility alias attributes
ACTIVE_DIR = settings.active_dir
is_testing = settings.is_testing
