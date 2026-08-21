"""
Canonical Dual-Mode Structured Extraction & Constrained Decoding Engine (10-Tool Stack).
1. Hosted Cloud APIs: instructor + Pydantic v2 with auto-retry loops on validation error.
2. Self-Hosted Local Models: outlines token-level logit masking and FSM grammar constraints.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Type, TypeVar
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Safe Import Guard for Instructor
HAS_INSTRUCTOR = False
try:
    import instructor
    HAS_INSTRUCTOR = True
except (ImportError, Exception) as e:
    HAS_INSTRUCTOR = False
    logger.info("Instructor package not active, using fallback structured extractor: %s", e)

# Safe Import Guard for Outlines
HAS_OUTLINES = False
try:
    import outlines
    HAS_OUTLINES = True
except (ImportError, Exception) as e:
    HAS_OUTLINES = False
    logger.info("Outlines package not active, using fallback constrained generator: %s", e)


class StructuredEngine:
    """
    Unified engine for type-safe structured extraction (Cloud) and constrained generation (Local).
    """

    @staticmethod
    def is_instructor_active() -> bool:
        """Checks if instructor is active."""
        return HAS_INSTRUCTOR

    @staticmethod
    def is_outlines_active() -> bool:
        """Checks if outlines is active."""
        return HAS_OUTLINES

    @classmethod
    def extract_cloud_structured(
        cls,
        schema_cls: Type[T],
        prompt: str,
        system_prompt: str = "Extract structured schema-compliant data.",
        model: str = "qwen2.5:7b",
        max_retries: int = 2
    ) -> T:
        """
        Cloud Mode: Type-safe extraction using Instructor with automated validation retries.
        """
        if HAS_INSTRUCTOR:
            try:
                from openai import OpenAI
                client = instructor.from_openai(
                    OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama"),
                    mode=instructor.Mode.JSON
                )
                return client.chat.completions.create(
                    model=model,
                    response_model=schema_cls,
                    max_retries=max_retries,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as e:
                logger.info("Instructor extraction bypassed/fallback: %s", e)

        # Fallback to local constrained generator or schema default
        return cls.generate_local_constrained(schema_cls=schema_cls, prompt=prompt)

    @classmethod
    def generate_local_constrained(
        cls,
        schema_cls: Type[T],
        prompt: str,
        model_name: str = "local"
    ) -> T:
        """
        Local Mode: Token-level logit masking using Outlines for mathematical schema compliance.
        """
        from src.domain.generation.outlines_generator import OutlinesConstrainedGenerator
        return OutlinesConstrainedGenerator.generate_json_constrained(schema_cls=schema_cls, prompt=prompt)

    @classmethod
    def generate_regex_constrained(
        cls,
        regex_pattern: str,
        prompt: str
    ) -> str:
        """
        Token-level regex grammar logit masking.
        """
        from src.domain.generation.outlines_generator import OutlinesConstrainedGenerator
        return OutlinesConstrainedGenerator.generate_regex_constrained(regex_pattern=regex_pattern, prompt=prompt)

    @classmethod
    def generate_choice_constrained(
        cls,
        choices: List[str],
        prompt: str
    ) -> str:
        """
        Token-level finite choice logit masking.
        """
        from src.domain.generation.outlines_generator import OutlinesConstrainedGenerator
        return OutlinesConstrainedGenerator.generate_choice_constrained(choices=choices, prompt=prompt)
