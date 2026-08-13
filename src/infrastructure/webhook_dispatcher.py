"""
Async Webhook Dispatcher with HMAC-SHA256 payload signing, exponential retry backoff, 3s timeout protection, and execution audit logging.
"""

import time
import json
import hmac
import hashlib
import asyncio
import threading
import urllib.request
import urllib.error
import socket
import ipaddress
import urllib.parse
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.infrastructure.repositories.workflows import log_workflow_execution


def is_ssrf_safe_url(url: str) -> bool:
    """
    Validates target URL against Server-Side Request Forgery (SSRF) risks.
    Blocks loopback (127.0.0.1/8), private RFC1918 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16),
    link-local metadata (169.254.169.254), and multicast/reserved IP ranges.
    """
    if not url or not isinstance(url, str):
        return False
    try:
        parsed = urllib.parse.urlparse(url.strip())
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False

        # In test environments, allow localhost testing
        from src.core.config import is_testing
        if is_testing and hostname.lower() in ("localhost", "127.0.0.1", "testserver"):
            return True

        # Resolve IP addresses
        ip_list = socket.getaddrinfo(hostname, None)
        for item in ip_list:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
        return True
    except Exception:
        return False


def compute_hmac_signature(secret: str, payload_bytes: bytes) -> str:
    """Compute HMAC-SHA256 signature for payload bytes."""
    if not secret:
        return ""
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def dispatch_webhook_sync(
    trigger_id: Optional[int],
    webhook_url: str,
    payload: Dict[str, Any],
    secret_header: Optional[str] = "",
    event_type: str = "custom",
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_multiplier: float = 2.0,
    timeout_sec: float = 3.0
) -> Dict[str, Any]:
    """
    Synchronously dispatch HTTP POST payload to target webhook URL with HMAC signing, retries, 3s timeout, and DB audit logging.
    """
    payload_str = json.dumps(payload, default=str)
    payload_bytes = payload_str.encode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Uroboros-Webhook-Engine/1.0",
    }
    
    if secret_header:
        sig = compute_hmac_signature(secret_header, payload_bytes)
        headers["X-Signature-256"] = f"sha256={sig}"
        headers["X-Uroboros-Signature"] = f"sha256={sig}"
        headers["Authorization"] = f"Bearer {secret_header}"

    start_time = time.time()
    last_status_code = None
    last_response_body = ""
    success = False
    retry_count = 0

    if not is_ssrf_safe_url(webhook_url):
        log_id = log_workflow_execution(
            trigger_id=trigger_id,
            event_type=event_type,
            payload_json=payload_str,
            status="blocked_ssrf",
            response_status_code=403,
            response_body="Blocked: SSRF protection policy rejected target host IP/subnet",
            execution_time_ms=0.0,
            retry_count=0
        )
        return {
            "log_id": log_id,
            "trigger_id": trigger_id,
            "event_type": event_type,
            "status": "blocked_ssrf",
            "response_status_code": 403,
            "response_body": "Blocked: SSRF protection policy rejected target host IP/subnet",
            "execution_time_ms": 0.0,
            "retry_count": 0
        }

    for attempt in range(max_retries):
        retry_count = attempt
        try:
            req = urllib.request.Request(webhook_url, data=payload_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                last_status_code = resp.status
                last_response_body = resp.read().decode("utf-8", errors="replace")
                if 200 <= last_status_code < 300:
                    success = True
                    break
        except urllib.error.HTTPError as e:
            last_status_code = e.code
            try:
                last_response_body = e.read().decode("utf-8", errors="replace")
            except (KeyboardInterrupt, MemoryError, SystemExit):
                raise
            except Exception:
                import logging; logging.getLogger(__name__).exception("Swallowed error in webhook_dispatcher.py")
                last_response_body = str(e)
        except urllib.error.URLError as e:
            last_status_code = None
            last_response_body = f"URLError: {e.reason}"
        except (KeyboardInterrupt, MemoryError, SystemExit):
            raise
        except Exception as e:
            import logging; logging.getLogger(__name__).exception(f"Swallowed error in webhook_dispatcher.py: {e}")
            last_status_code = None
            last_response_body = f"Error: {str(e)}"

        if attempt < max_retries - 1:
            sleep_time = initial_delay * (backoff_multiplier ** attempt)
            time.sleep(sleep_time)

    execution_time_ms = (time.time() - start_time) * 1000.0
    status_str = "success" if success else "failed"

    log_id = log_workflow_execution(
        trigger_id=trigger_id,
        event_type=event_type,
        payload_json=payload_str,
        status=status_str,
        response_status_code=last_status_code,
        response_body=last_response_body,
        execution_time_ms=execution_time_ms,
        retry_count=retry_count
    )

    return {
        "log_id": log_id,
        "trigger_id": trigger_id,
        "event_type": event_type,
        "status": status_str,
        "response_status_code": last_status_code,
        "response_body": last_response_body,
        "execution_time_ms": execution_time_ms,
        "retry_count": retry_count
    }


async def dispatch_webhook_async(
    trigger_id: Optional[int],
    webhook_url: str,
    payload: Dict[str, Any],
    secret_header: Optional[str] = "",
    event_type: str = "custom",
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_multiplier: float = 2.0,
    timeout_sec: float = 3.0
) -> Dict[str, Any]:
    """Async wrapper for non-blocking webhook delivery via asyncio threadpool."""
    return await asyncio.to_thread(
        dispatch_webhook_sync,
        trigger_id,
        webhook_url,
        payload,
        secret_header,
        event_type,
        max_retries,
        initial_delay,
        backoff_multiplier,
        timeout_sec
    )


def dispatch_webhook_background(
    trigger_id: Optional[int],
    webhook_url: str,
    payload: Dict[str, Any],
    secret_header: Optional[str] = "",
    event_type: str = "custom"
):
    """Fire-and-forget non-blocking webhook dispatcher."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(dispatch_webhook_async(trigger_id, webhook_url, payload, secret_header, event_type))
    except RuntimeError:
        thread = threading.Thread(
            target=dispatch_webhook_sync,
            args=(trigger_id, webhook_url, payload, secret_header, event_type),
            daemon=True
        )
        thread.start()


class WebhookDispatcher:
    """Class interface wrapping webhook delivery logic."""

    @staticmethod
    def dispatch_sync(*args, **kwargs):
        return dispatch_webhook_sync(*args, **kwargs)

    @staticmethod
    async def dispatch_async(*args, **kwargs):
        return await dispatch_webhook_async(*args, **kwargs)

    @staticmethod
    def dispatch_background(*args, **kwargs):
        return dispatch_webhook_background(*args, **kwargs)
