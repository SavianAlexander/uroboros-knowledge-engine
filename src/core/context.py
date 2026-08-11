import contextvars
from typing import Optional

# Context variable to hold the current user ID
current_user_id: contextvars.ContextVar[Optional[int]] = contextvars.ContextVar("current_user_id", default=None)

def get_current_user_id() -> Optional[int]:
    return current_user_id.get()

def set_current_user_id(user_id: int):
    current_user_id.set(user_id)
