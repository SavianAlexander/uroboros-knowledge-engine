import base64
import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional

# In a real system, this would be loaded from env vars
SECRET_KEY = b"zero_dependency_super_secret_key_12345"

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

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (in real prod use pbkdf2 or bcrypt)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
