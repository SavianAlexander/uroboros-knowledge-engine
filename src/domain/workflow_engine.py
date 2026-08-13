"""
Event Listener Engine and condition rule matching for automated workflow triggers.
Evaluates document_ingested, tag_assigned, and semantic_match events against pattern and score threshold rules.
"""
import re
import json
import fnmatch
import logging
from typing import Dict, Any, List, Optional
from src.infrastructure.repositories.workflows import list_workflow_triggers
from src.infrastructure.webhook_dispatcher import WebhookDispatcher

logger = logging.getLogger(__name__)


def _eval_json_condition(cond_obj: dict, payload: Dict[str, Any]) -> bool:
    for key, expected in cond_obj.items():
        if key in ("min_score", "score_threshold", "score"):
            try:
                val_raw = payload.get("score", payload.get("confidence", 0.0))
                if float(val_raw) < (float(expected) if expected is not None else 0.0):
                    return False
            except (ValueError, TypeError):
                return False
        elif key in ("pattern", "glob", "file_pattern"):
            if not fnmatch.fnmatch(str(payload.get("filepath", payload.get("filename", ""))), str(expected)):
                return False
        elif key == "tag":
            if not fnmatch.fnmatch(str(payload.get("tag", "")), str(expected)):
                return False
        elif key == "mime_type":
            if not fnmatch.fnmatch(str(payload.get("mime_type", "")), str(expected)):
                return False
        else:
            actual_val = payload.get(key)
            if str(actual_val) != str(expected) and not fnmatch.fnmatch(str(actual_val), str(expected)):
                return False
    return True

def evaluate_condition(
    condition_pattern: Optional[str],
    event_type: str,
    payload: Dict[str, Any]
) -> bool:
    """
    Evaluate condition pattern against event type and payload.
    Supports empty conditions (unconditional True), score thresholds (min_score:0.85, score>=0.85),
    glob file/tag patterns (*.pdf, urgent-*), regex, and JSON filter objects.
    """
    if not condition_pattern or not condition_pattern.strip():
        return True

    pattern_str = condition_pattern.strip()

    # Try parsing condition as JSON object
    if pattern_str.startswith("{") and pattern_str.endswith("}"):
        try:
            cond_obj = json.loads(pattern_str)
            if isinstance(cond_obj, dict):
                return _eval_json_condition(cond_obj, payload)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.warning(f"Swallowed error in workflow_engine.py: {e}")

    # Score threshold evaluation for semantic_match
    score_threshold_match = re.search(r'(?:min_score|score)\s*[:>=]+\s*([0-9\.]+)', pattern_str, re.IGNORECASE)
    if score_threshold_match:
        try:
            threshold = float(score_threshold_match.group(1))
            val_raw = payload.get("score", payload.get("confidence", 0.0))
            actual_score = float(val_raw) if val_raw is not None else 0.0
            return actual_score >= threshold
        except (ValueError, TypeError):
            return False

    # Standard numeric pattern (e.g., "0.85") when event is semantic_match
    if event_type == "semantic_match" and re.match(r'^[0-9\.]+$', pattern_str):
        try:
            threshold = float(pattern_str)
            val_raw = payload.get("score", payload.get("confidence", 0.0))
            actual_score = float(val_raw) if val_raw is not None else 0.0
            return actual_score >= threshold
        except (ValueError, TypeError):
            pass

    # Check candidate fields based on event type
    candidate_strings = []
    if "filepath" in payload:
        candidate_strings.append(str(payload["filepath"]))
    if "filename" in payload:
        candidate_strings.append(str(payload["filename"]))
    if "tag" in payload:
        candidate_strings.append(str(payload["tag"]))
    if "query" in payload:
        candidate_strings.append(str(payload["query"]))
    if "mime_type" in payload:
        candidate_strings.append(str(payload["mime_type"]))

    if not candidate_strings:
        candidate_strings.append(json.dumps(payload))

    # Regex evaluation if prefixed with "regex:"
    if pattern_str.startswith("regex:"):
        regex_pat = pattern_str[6:]
        try:
            compiled = re.compile(regex_pat, re.IGNORECASE)
            return any(compiled.search(cand) for cand in candidate_strings)
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception:
            import logging; logging.getLogger(__name__).exception("Swallowed error in workflow_engine.py")
            return False

    # Glob fnmatch pattern (e.g. *.pdf, docs/*, confidential-*)
    if any(c in pattern_str for c in "*?[]"):
        return any(fnmatch.fnmatch(cand, pattern_str) for cand in candidate_strings)

    # Substring / exact match fallback
    pattern_lower = pattern_str.lower()
    return any(pattern_lower in cand.lower() for cand in candidate_strings)


def evaluate_event(event_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query active triggers for event_type and return those that satisfy condition rules."""
    active_triggers = list_workflow_triggers(event_type=event_type, active_only=True)
    matching = []
    for trigger in active_triggers:
        cond = trigger.get("condition_pattern", "")
        if evaluate_condition(cond, event_type, payload):
            matching.append(trigger)
    return matching


def process_event(
    event_type: str,
    payload: Dict[str, Any],
    sync_dispatch: bool = False
) -> List[Dict[str, Any]]:
    """
    Process incoming domain event: evaluate active triggers and dispatch webhooks.
    """
    matching_triggers = evaluate_event(event_type, payload)
    results = []
    for trigger in matching_triggers:
        trigger_id = trigger["id"]
        webhook_url = trigger["webhook_url"]
        secret_header = trigger.get("secret_header", "")
        
        if sync_dispatch:
            res = WebhookDispatcher.dispatch_sync(
                trigger_id=trigger_id,
                webhook_url=webhook_url,
                payload=payload,
                secret_header=secret_header,
                event_type=event_type
            )
            results.append(res)
        else:
            WebhookDispatcher.dispatch_background(
                trigger_id=trigger_id,
                webhook_url=webhook_url,
                payload=payload,
                secret_header=secret_header,
                event_type=event_type
            )
            results.append({
                "trigger_id": trigger_id,
                "event_type": event_type,
                "status": "dispatched",
                "webhook_url": webhook_url
            })
    return results


class WorkflowEngine:
    """Domain service wrapping workflow event listener logic."""

    @staticmethod
    def evaluate_condition(condition_pattern: Optional[str], event_type: str, payload: Dict[str, Any]) -> bool:
        return evaluate_condition(condition_pattern, event_type, payload)

    @staticmethod
    def evaluate_event(event_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        return evaluate_event(event_type, payload)

    @staticmethod
    def process_event(event_type: str, payload: Dict[str, Any], sync_dispatch: bool = False) -> List[Dict[str, Any]]:
        return process_event(event_type, payload, sync_dispatch=sync_dispatch)
