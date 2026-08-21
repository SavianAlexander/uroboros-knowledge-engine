"""
Canonical Programmatic DSPy RAG Pipeline & MIPROv2 Compilation Engine (10-Tool Stack).
Defines declarative typed signatures for Query Transformation and Grounded Answer Generation.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Safe Import Guard for DSPy
HAS_DSPY = False
try:
    import dspy
    HAS_DSPY = True
except (ImportError, Exception) as e:
    HAS_DSPY = False
    logger.info("DSPy library not active, using fallback programmatic pipeline: %s", e)

if HAS_DSPY:
    class QueryTransformationSignature(dspy.Signature):
        """Transforms a user inquiry and conversational context into focused sub-queries."""
        context_history: str = dspy.InputField(desc="Prior dialogue turns and entities")
        user_inquiry: str = dspy.InputField(desc="Incoming question from user")
        sub_queries: List[str] = dspy.OutputField(desc="Decomposed atomic search queries")

    class GroundedAnswerSignature(dspy.Signature):
        """Synthesizes a grounded response strictly citing facts with bracketed [Doc: id] anchors."""
        context: str = dspy.InputField(desc="Retrieved context chunks wrapped in XML tags")
        question: str = dspy.InputField(desc="User inquiry requiring resolution")
        rationale: str = dspy.OutputField(desc="Step-by-step chain of thought reasoning")
        cited_answer: str = dspy.OutputField(desc="Factual response strictly citing [Doc: id]")


class DSPyRAGPipeline:
    """
    Programmatic RAG Pipeline coordinating multi-step retrieval, decomposition, and grounded synthesis.
    """

    def __init__(self, compiled_weights_path: Optional[str] = None):
        self.compiled_weights_path = compiled_weights_path
        self.dspy_module = None

        if HAS_DSPY:
            try:
                class InnerRAG(dspy.Module):
                    def __init__(self):
                        super().__init__()
                        self.transform = dspy.ChainOfThought(QueryTransformationSignature)
                        self.generate = dspy.ChainOfThought(GroundedAnswerSignature)

                    def forward(self, user_inquiry: str, context: str, context_history: str = ""):
                        t_res = self.transform(context_history=context_history, user_inquiry=user_inquiry)
                        g_res = self.generate(context=context, question=user_inquiry)
                        return t_res, g_res

                self.dspy_module = InnerRAG()
            except Exception as e:
                logger.warning("Failed to initialize native DSPy module: %s", e)
                self.dspy_module = None

    @staticmethod
    def is_dspy_active() -> bool:
        """Checks if DSPy is active."""
        return HAS_DSPY

    def forward(self, user_inquiry: str, context: str, context_history: str = "") -> Dict[str, Any]:
        """
        Executes forward pass through query transformation and grounded answer synthesis.
        """
        from src.domain.pipeline.dspy_modules import ProgrammaticRAG
        inner = ProgrammaticRAG(compiled_weights_path=self.compiled_weights_path)
        out = inner.forward(user_situation=user_inquiry, context=context, context_history=context_history)
        return {
            "sub_queries": out.sub_queries,
            "rationale": out.rationale,
            "cited_answer": out.cited_answer,
            "citations": out.citations,
            "is_grounded": out.is_grounded
        }

    @classmethod
    def compile_pipeline(
        cls,
        output_path: str = "data/compiled_rag_pipeline.json",
        max_bootstrapped_demos: int = 4
    ) -> Dict[str, Any]:
        """
        Compiles the programmatic pipeline using metric-driven teleprompter optimization.
        """
        from src.domain.optimization.compile_prompts import PromptCompilationHarness
        return PromptCompilationHarness.compile_pipeline(output_path=output_path, max_bootstrapped_demos=max_bootstrapped_demos)
