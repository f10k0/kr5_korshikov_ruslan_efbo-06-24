from fastapi import Header, HTTPException, status, Depends
from typing import Optional
from app.storage import storage
from app.schemas import User

async def get_current_user(
    x_user_id: Optional[int] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header("user", alias="X-User-Role")
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Id header")
    return User(id=x_user_id, role=x_user_role)

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

def get_storage():
    return storage