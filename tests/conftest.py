
# --- Patch for WinError 32 File Locks ---
import os
import sys
import shutil
import functools
from src.infrastructure.database import reset_db_connections

_orig_os_remove = os.remove
_orig_shutil_rmtree = shutil.rmtree
_orig_os_unlink = getattr(os, 'unlink', _orig_os_remove)

def _patch_action(func, path, *args, **kwargs):
    try:
        func(path, *args, **kwargs)
    except (PermissionError, OSError) as e:
        if getattr(e, "winerror", None) == 32 or "being used by another process" in str(e):
            reset_db_connections()
            func(path, *args, **kwargs)
        else:
            raise

@functools.wraps(_orig_os_remove)
def _patched_os_remove(path, *args, **kwargs):
    _patch_action(_orig_os_remove, path, *args, **kwargs)

@functools.wraps(_orig_shutil_rmtree)
def _patched_shutil_rmtree(path, *args, **kwargs):
    def on_exc(func, p, exc_info):
        exc_value = exc_info[1] if isinstance(exc_info, tuple) else exc_info
        if isinstance(exc_value, (PermissionError, OSError)) and getattr(exc_value, "winerror", None) == 32:
            reset_db_connections()
            func(p)
        else:
            raise exc_value
    
    if sys.version_info >= (3, 12):
        kwargs["onexc"] = on_exc
    else:
        kwargs["onerror"] = on_exc
    _orig_shutil_rmtree(path, *args, **kwargs)

@functools.wraps(_orig_os_unlink)
def _patched_os_unlink(path, *args, **kwargs):
    _patch_action(_orig_os_unlink, path, *args, **kwargs)

os.remove = _patched_os_remove
os.unlink = _patched_os_unlink
shutil.rmtree = _patched_shutil_rmtree

import pytest
import os
import sys

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.infrastructure.database import reset_db_connections

@pytest.fixture(autouse=True)
def clear_db_pools_after_test():
    """Ensure database connection pools are cleared after each test so Windows file locks don't block teardown."""
    yield
    reset_db_connections()
