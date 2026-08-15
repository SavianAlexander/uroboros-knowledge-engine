"""
Legacy shim for backward-compatibility.
Canonical implementation is in `src.infrastructure.eve_tactical_tables`.
"""
from src.infrastructure.eve_tactical_tables import (
    generate_tactical_tables_markdown,
    generate_omni_tables_markdown
)

__all__ = [
    "generate_tactical_tables_markdown",
    "generate_omni_tables_markdown"
]
