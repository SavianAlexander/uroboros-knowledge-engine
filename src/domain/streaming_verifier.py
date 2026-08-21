"""
Streaming Anti-Drift Tokenizer Verification Filter:
Audits token streams incrementally with sub-10ms latency.
Buffers numerical claims and capacity metrics to prevent mid-stream hallucinations,
remediating discrepancies before tokens are yielded to the client.
"""

import re
import asyncio
from typing import AsyncIterator, Iterator, List, Set, Dict, Any, Optional


class StreamingAntiDriftFilter:
    """
    Incremental streaming filter that audits token streams in real time.
    """

    RE_DIGIT_OR_UNIT = re.compile(r'(\d+[\d,.]*|\b(?:writes?/sec|reqs?/sec|tps|rps|ms|seconds|minutes|gb|mb|tb|users?|threads?|nodes?)\b)', re.IGNORECASE)
    RE_FULL_NUMERIC_CLAIM = re.compile(r'\b(\d+(?:,\d+)*(?:\.\d+)?)\s*(writes?/sec|reqs?/sec|tps|rps|ms|seconds|minutes|gb|mb|tb|users?|threads?|nodes?)\b', re.IGNORECASE)

    @classmethod
    def filter_stream_sync(
        cls,
        token_generator: Iterator[str],
        retrieved_context: str
    ) -> Iterator[str]:
        """
        Synchronously filters a token generator, buffering assertion windows
        and remediating factual drift before emitting tokens.
        """
        if not retrieved_context:
            for token in token_generator:
                yield token
            return

        context_numbers = set(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', retrieved_context))
        buffer = []

        for token in token_generator:
            buffer.append(token)
            accumulated = "".join(buffer)

            # Check if accumulated text contains a complete numeric claim
            claim_match = cls.RE_FULL_NUMERIC_CLAIM.search(accumulated)
            has_pending_num = bool(re.search(r'\b\d+(?:,\d+)*(?:\.\d+)?\s*$', accumulated))

            if claim_match:
                full_claim = claim_match.group(0)
                claim_num = claim_match.group(1)
                unit_str = claim_match.group(2)

                if claim_num not in context_numbers:
                    ctx_pattern = re.compile(rf'(\b\d+(?:,\d+)*(?:\.\d+)?)\s*{re.escape(unit_str)}', re.IGNORECASE)
                    ctx_match = ctx_pattern.search(retrieved_context)
                    if ctx_match:
                        correct_num = ctx_match.group(1)
                        accumulated = accumulated.replace(claim_num, correct_num)
                    else:
                        accumulated = accumulated.replace(full_claim, f"{full_claim} (unverified)")

                yield accumulated
                buffer = []
            elif has_pending_num and len(buffer) <= 4:
                # Buffer trailing numbers to wait for possible unit arrival in next tokens
                continue
            else:
                while buffer:
                    yield buffer.pop(0)

        # Flush any remaining tokens in buffer
        if buffer:
            accumulated = "".join(buffer)
            claim_match = cls.RE_FULL_NUMERIC_CLAIM.search(accumulated)
            if claim_match:
                full_claim = claim_match.group(0)
                claim_num = claim_match.group(1)
                unit_str = claim_match.group(2)
                if claim_num not in context_numbers:
                    ctx_pattern = re.compile(rf'(\b\d+(?:,\d+)*(?:\.\d+)?)\s*{re.escape(unit_str)}', re.IGNORECASE)
                    ctx_match = ctx_pattern.search(retrieved_context)
                    if ctx_match:
                        correct_num = ctx_match.group(1)
                        accumulated = accumulated.replace(claim_num, correct_num)
                yield accumulated
            else:
                while buffer:
                    yield buffer.pop(0)

    @classmethod
    async def filter_stream_async(
        cls,
        async_token_generator: AsyncIterator[str],
        retrieved_context: str
    ) -> AsyncIterator[str]:
        """
        Asynchronously filters an async token stream with real-time factual remediation.
        """
        if not retrieved_context:
            async for token in async_token_generator:
                yield token
            return

        context_numbers = set(re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', retrieved_context))
        buffer = []

        async for token in async_token_generator:
            buffer.append(token)
            accumulated = "".join(buffer)

            claim_match = cls.RE_FULL_NUMERIC_CLAIM.search(accumulated)
            has_pending_num = bool(re.search(r'\b\d+(?:,\d+)*(?:\.\d+)?\s*$', accumulated))

            if claim_match:
                full_claim = claim_match.group(0)
                claim_num = claim_match.group(1)
                unit_str = claim_match.group(2)

                if claim_num not in context_numbers:
                    ctx_pattern = re.compile(rf'(\b\d+(?:,\d+)*(?:\.\d+)?)\s*{re.escape(unit_str)}', re.IGNORECASE)
                    ctx_match = ctx_pattern.search(retrieved_context)
                    if ctx_match:
                        correct_num = ctx_match.group(1)
                        accumulated = accumulated.replace(claim_num, correct_num)
                    else:
                        accumulated = accumulated.replace(full_claim, f"{full_claim} (unverified)")

                yield accumulated
                buffer = []
            elif has_pending_num and len(buffer) <= 4:
                continue
            else:
                while buffer:
                    yield buffer.pop(0)

        if buffer:
            accumulated = "".join(buffer)
            claim_match = cls.RE_FULL_NUMERIC_CLAIM.search(accumulated)
            if claim_match:
                full_claim = claim_match.group(0)
                claim_num = claim_match.group(1)
                unit_str = claim_match.group(2)
                if claim_num not in context_numbers:
                    ctx_pattern = re.compile(rf'(\b\d+(?:,\d+)*(?:\.\d+)?)\s*{re.escape(unit_str)}', re.IGNORECASE)
                    ctx_match = ctx_pattern.search(retrieved_context)
                    if ctx_match:
                        correct_num = ctx_match.group(1)
                        accumulated = accumulated.replace(claim_num, correct_num)
                yield accumulated
            else:
                while buffer:
                    yield buffer.pop(0)
