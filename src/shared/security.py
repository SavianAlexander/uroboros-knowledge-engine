"""
Security utilities including symlink escape, path traversal guards, and ACL permission inspection.
"""
import re
import os
import sys
from pathlib import Path
from fastapi import HTTPException

BASE_DIR = Path("dumps").resolve()

def get_active_sandbox_dir() -> Path:
    main_mod = sys.modules.get("main")
    if main_mod and hasattr(main_mod, "ACTIVE_DIR") and main_mod.ACTIVE_DIR:
        return Path(main_mod.ACTIVE_DIR).resolve()
    return BASE_DIR

def get_file_acl(filepath: str) -> str:
    """Retrieve File System Access Control List permissions string for a file (Windows / POSIX)."""
    try:
        if os.name == 'nt':
            import win32security
            sd = win32security.GetFileSecurity(filepath, win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                return "Full Control (Everyone)"
            aces = []
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                user, domain, _ = win32security.LookupAccountSid(None, ace[2])
                aces.append(f"{domain}\\{user}")
            return f"ACL: {', '.join(aces)}" if aces else "Restricted"
        else:
            st = os.stat(filepath)
            mode = oct(st.st_mode)[-3:]
            return f"POSIX mode: {mode}"
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception:
        import logging; logging.getLogger(__name__).exception("Swallowed error in security.py")
        return "Standard Permission"

import tempfile

def verify_path_containment(path_str: str, base_dir: str = None) -> Path:
    """Validate that path_str resolves within base_dir (preventing path traversal attacks)."""
    if not path_str:
        return None
    try:
        base = Path(base_dir).resolve() if base_dir else get_active_sandbox_dir()
        import urllib.parse
        decoded_path = urllib.parse.unquote(str(path_str))
        target = Path(decoded_path).resolve()
        
        is_inside_base = False
        try:
            target.relative_to(base)
            is_inside_base = True
        except ValueError:
            pass

        if not is_inside_base and not base_dir and get_active_sandbox_dir() == BASE_DIR:
            temp_dir = Path(tempfile.gettempdir()).resolve()
            try:
                target.relative_to(temp_dir)
                # Ensure no '..' or traversal sequences in original path_str or decoded path
                if ".." not in path_str and ".." not in decoded_path:
                    is_inside_base = True
            except ValueError:
                pass

        if not is_inside_base:
            raise HTTPException(status_code=400, detail="Path traversal detected")
        return target
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in security.py: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid path containment check: {str(e)}")
import re

SECRET_REDACTION_PATTERNS = [
    (re.compile(r'(?i)(aws_access_key_id|aws_secret_access_key|api_key|secret_key|private_key)\s*[:=]\s*["\']?([A-Za-z0-9/+=_-]{16,})["\']?'), r'\1=[REDACTED_SECRET]'),
    (re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'), '[REDACTED_SLACK_TOKEN]'),
    (re.compile(r'ghp_[0-9a-zA-Z]{36}'), '[REDACTED_GITHUB_TOKEN]'),
]

def redact_sensitive_keys(text: str) -> str:
    """Scan and redact detected AWS/GitHub/Slack API keys from text content."""
    if not text:
        return text
    redacted = text
    for pattern, replacement in SECRET_REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted

def validate_upload_payload(content_bytes: bytes, max_size_mb: int = 100) -> bool:
    """Validate upload payload byte size (rejecting zero-byte files and payload bombs)."""
    if not content_bytes or len(content_bytes) == 0:
        raise HTTPException(status_code=400, detail="Cannot process zero-byte empty file upload.")
    if len(content_bytes) > max_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File payload exceeds maximum limit of {max_size_mb}MB.")
    return True


