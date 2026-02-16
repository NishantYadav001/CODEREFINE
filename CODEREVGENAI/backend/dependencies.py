from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from security import decode_access_token

# Defines the token source (Bearer token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    verifyToken Middleware equivalent.
    Decodes token and validates user.
    """
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    role: str = payload.get("role", "user")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username, "role": role}

async def get_current_admin(user: dict = Depends(get_current_user)):
    """
    checkRole('admin') Middleware equivalent.
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

def require_role(required_role: str):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] == "admin":
            return user # Admin bypass
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker