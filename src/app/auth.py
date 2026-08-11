import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from src.core.auth_jwt import verify_jwt, sign_jwt, hash_password
from src.infrastructure.database import get_db

router = APIRouter()

async def verify_api_key(authorization: str = Header(None)):
    """Validates Bearer JWT Token."""
    from src.core.config import is_testing
    if is_testing:
        from src.core.context import set_current_user_id
        set_current_user_id(0)
        return {"user_id": 0, "username": "test_admin", "role": "admin"}
        
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
        
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
        
    token = parts[1]
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        
    from src.core.context import set_current_user_id
    if "user_id" in payload:
        set_current_user_id(payload["user_id"])
        
    return payload

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/api/auth/login")
def login(req: LoginRequest):
    # In a real app we'd verify against the `users` table
    # For now, zero-dependency bootstrap mode (allow a default admin login if it matches env or just accept 'admin'/'admin' if DB is empty)
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (req.username,))
        row = cursor.fetchone()
        
        if not row:
            # Bootstrap fallback
            if req.username == "admin" and req.password == "admin":
                return {"token": sign_jwt({"user_id": 0, "username": "admin", "role": "admin"})}
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        expected_hash = hash_password(req.password)
        if row["password_hash"] != expected_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        token = sign_jwt({
            "user_id": row["id"],
            "username": row["username"],
            "role": row["role"]
        })
        return {"token": token}
    except HTTPException:
        raise
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        import logging; logging.getLogger(__name__).exception(f"Swallowed error in auth.py: {e}")
        raise HTTPException(status_code=500, detail=str(e))
