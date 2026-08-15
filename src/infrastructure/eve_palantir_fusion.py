"""
Legacy shim for backward-compatibility.
Canonical implementation is in `src.infrastructure.eve_strategic_fusion`.
"""
from src.infrastructure.eve_strategic_fusion import (
    generate_strategic_fusion_markdown,
    generate_palantir_fusion_markdown
)

__all__ = [
    "generate_strategic_fusion_markdown",
    "generate_palantir_fusion_markdown"
]
