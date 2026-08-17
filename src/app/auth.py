import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from src.core.auth_jwt import verify_jwt, sign_jwt, hash_password, verify_password
from src.infrastructure.database import get_db
from src.core.config import is_testing

router = APIRouter()

async def verify_api_key(authorization: str = Header(None)):
    """Validates Bearer JWT Token."""
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

import secrets

@router.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?", (req.username,))
            row = cursor.fetchone()
            
            if not row:
                admin_pw = os.environ.get("ADMIN_PASSWORD", "admin" if is_testing else "")
                if admin_pw and secrets.compare_digest(req.username, "admin") and secrets.compare_digest(req.password, admin_pw):
                    return {"token": sign_jwt({"user_id": 0, "username": "admin", "role": "admin"})}
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
            stored_hash = str(row["password_hash"] or "")
            if not verify_password(req.password, stored_hash):
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
