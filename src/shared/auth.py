import os
import hmac
import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional

SECRET_KEY = os.environ.get("UROBOROS_JWT_SECRET", "default_env_jwt_signing_token")

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def _base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_jwt_token(payload: Dict[str, Any], expires_in_seconds: int = 3600) -> str:
    """Generate an HMAC-SHA256 signed JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = dict(payload)
    payload["iat"] = now
    payload["exp"] = now + expires_in_seconds

    header_b64 = _base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _base64url_encode(json.dumps(payload).encode('utf-8'))

    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify HMAC-SHA256 JWT token signature and expiration."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()

        if not hmac.compare_digest(_base64url_encode(expected_sig), sig_b64):
            return None

        payload = json.loads(_base64url_decode(payload_b64).decode('utf-8'))
        if payload.get("exp", 0) < int(time.time()):
            return None

        return payload
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in auth.py")
        return None

def verify_api_key(x_api_key: Optional[str] = None, authorization: Optional[str] = None) -> bool:
    """Verify API key or Bearer token if UROBOROS_REQUIRE_AUTH environment variable is enabled."""
    from fastapi import HTTPException

    require_auth = os.environ.get("UROBOROS_REQUIRE_AUTH", "false").lower() in ("true", "1", "yes")
    if not require_auth:
        return True

    expected_key = os.environ.get("UROBOROS_API_KEY", "default_env_api_auth_token")
    
    token = x_api_key
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]

    if not token or not hmac.compare_digest(token, expected_key):
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API key")

    return True

