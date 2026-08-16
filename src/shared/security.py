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
    try:
        import src.core.config as config
        if hasattr(config, "ACTIVE_DIR") and config.ACTIVE_DIR:
            return Path(config.ACTIVE_DIR).resolve()
    except Exception:
        pass
    main_mod = sys.modules.get("main")
    if main_mod and hasattr(main_mod, "ACTIVE_DIR") and main_mod.ACTIVE_DIR:
        return Path(main_mod.ACTIVE_DIR).resolve()
    return BASE_DIR

def get_file_acl(filepath: str) -> str:
    """Retrieve File System Access Control List permissions string for a file (Windows / POSIX)."""
    try:
        if not os.path.exists(filepath):
            return "File Not Found"
        if os.name == "nt":
            import win32security
            sd = win32security.GetFileSecurity(filepath, win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()
            return f"DACL_ACE_COUNT:{dacl.GetAceCount()}" if dacl else "NO_DACL"
        else:
            stat_info = os.stat(filepath)
            mode = oct(stat_info.st_mode)[-3:]
            return f"POSIX_PERM_{mode}"
    except Exception as e:
        import logging; logging.warning(f"Swallowed error in security.py: {e}")
        return "ACL_UNAVAILABLE"

import tempfile

def verify_path_containment(path_str: str, base_dir: str = None) -> Path:
    """Strictly verifies that a given file path resolves inside the active sandbox directory or temp directory.

    Prevents directory traversal, UNC pathing, Windows device name tricks, and null-byte injections.
    Raises HTTPException(400) on violations.
    """
    if not path_str:
        return None

    if "\x00" in path_str:
        raise HTTPException(status_code=400, detail="Null byte in path detected")

    try:
        base = Path(base_dir).resolve() if base_dir else get_active_sandbox_dir()
        import urllib.parse
        decoded_path = urllib.parse.unquote(str(path_str))
        
        # Check Windows reserved device names cross-platform
        path_base_name = Path(decoded_path).name.split('.')[0].upper()
        if path_base_name in {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}:
            raise HTTPException(status_code=400, detail="Reserved system device name detected")

        # Check Windows drive letter or UNC paths on POSIX/Linux
        if os.name != 'nt':
            if re.match(r'^[a-zA-Z]:', decoded_path) or decoded_path.startswith("\\\\") or decoded_path.startswith("//"):
                raise HTTPException(status_code=400, detail="External system path traversal detected")

        normalized = decoded_path.replace("\\", "/")
        target = Path(normalized).resolve()
        
        is_inside_base = False
        allowed_bases = [base, Path("dumps").resolve(), BASE_DIR]
        for b in allowed_bases:
            try:
                target.relative_to(b)
                if ".." not in path_str and ".." not in decoded_path:
                    is_inside_base = True
                    break
            except ValueError:
                pass

        if not is_inside_base:
            temp_dirs = [Path(tempfile.gettempdir()).resolve(), Path("/tmp").resolve(), Path("/var/tmp").resolve()]
            for td in temp_dirs:
                try:
                    target.relative_to(td)
                    if ".." not in path_str and ".." not in decoded_path:
                        is_inside_base = True
                        break
                except ValueError:
                    pass

        if not is_inside_base or ".." in path_str or ".." in decoded_path:
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


