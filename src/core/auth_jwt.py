import os
import base64
import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional

# Dynamic JWT Secret Key loaded from environment with local fallback
SECRET_KEY = os.environ.get("JWT_SECRET", "uroboros_secure_runtime_key_2026").encode("utf-8")

def encode_base64_url(data: bytes) -> str:
    """Encode bytes to base64url format string."""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def decode_base64_url(data: str) -> bytes:
    """Decode base64url format string to bytes."""
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def sign_jwt(payload: Dict[str, Any], exp_seconds: int = 86400) -> str:
    """Create a signed JWT token."""
    header = {"alg": "HS256", "typ": "JWT"}
    
    # Add expiration
    payload_copy = dict(payload)
    payload_copy["exp"] = int(time.time()) + exp_seconds
    
    encoded_header = encode_base64_url(json.dumps(header).encode('utf-8'))
    encoded_payload = encode_base64_url(json.dumps(payload_copy).encode('utf-8'))
    
    message = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    signature = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    encoded_signature = encode_base64_url(signature)
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return payload if valid, None otherwise."""
    if not token or token.count('.') != 2:
        return None
        
    encoded_header, encoded_payload, encoded_signature = token.split('.')
    message = f"{encoded_header}.{encoded_payload}".encode('utf-8')
    
    # Verify signature
    expected_signature = hmac.new(SECRET_KEY, message, hashlib.sha256).digest()
    if not hmac.compare_digest(encode_base64_url(expected_signature), encoded_signature):
        return None
        
    try:
        payload = json.loads(decode_base64_url(encoded_payload).decode('utf-8'))
        # Check expiration
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None
        return payload
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in auth_jwt.py")
        return None

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash password using standard-library PBKDF2-HMAC-SHA256 (100,000 iterations).
    Format: pbkdf2:sha256:100000$<salt>$<hash>
    """
    if not salt:
        salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Constant-time password verification supporting PBKDF2-HMAC and legacy SHA-256 fallback.
    """
    if not plain_password or not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_hash.split("$")
            if len(parts) == 3:
                salt = parts[1]
                expected_hash = hash_password(plain_password, salt=salt)
                return hmac.compare_digest(expected_hash, stored_hash)
        except Exception:
            return False
    # Legacy SHA-256 fallback
    legacy_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_hash, stored_hash)
