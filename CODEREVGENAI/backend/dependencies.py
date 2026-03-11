# ════════════════════════════════════════════════════════════════════
# CODEREFINE - Enhanced Role-Based Access Control (RBAC)
# ════════════════════════════════════════════════════════════════════
"""
Authentication & Authorization Dependencies for FastAPI

Provides:
- Token validation
- User authentication
- Role-based access control
- Permission checking
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from security import decode_access_token
from routes_config import PERMISSION_MATRIX, can_access_route
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OAUTH2 CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Defines the token source (Bearer token)
# Supports: Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scopes={
        "user:read": "Read user data",
        "user:write": "Modify user data",
        "admin:read": "Read admin data",
        "admin:write": "Modify admin data"
    }
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE AUTHENTICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract and validate current user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        dict: User data with username, role, email
        
    Raises:
        HTTPException: 401 if token invalid or expired
    """
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    role: str = payload.get("role", "user")
    email: str = payload.get("email", "")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "username": username,
        "role": role,
        "email": email,
        "authenticated_at": datetime.utcnow()
    }


async def get_optional_user(
    token: str = Depends(oauth2_scheme.__class__(tokenUrl="/api/auth/login", auto_error=False))
):
    """
    Get current user if authenticated, otherwise return guest.
    
    Used for routes that allow both authenticated and guest access.
    """
    if not token:
        return {"username": "guest", "role": "guest", "authenticated": False}
    
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        role = payload.get("role", "user")
        
        if username:
            return {
                "username": username,
                "role": role,
                "email": payload.get("email", ""),
                "authenticated": True
            }
    except:
        pass
    
    return {"username": "guest", "role": "guest", "authenticated": False}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROLE-BASED ACCESS CONTROL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_current_admin(user: dict = Depends(get_current_user)):
    """
    Verify user has admin role.
    
    Raises:
        HTTPException: 403 if user is not admin
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user


async def get_current_user_or_admin(user: dict = Depends(get_current_user)):
    """
    Accept both users and admins (anyone authenticated).
    """
    if user["role"] not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required"
        )
    return user


def require_role(required_role: str):
    """
    Factory function to create role requirement checker.
    
    Args:
        required_role: Required role ('user', 'admin', etc)
        
    Returns:
        Dependency function for FastAPI
        
    Example:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
        async def admin_endpoint(): ...
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] == "admin":
            return user  # Admin bypass - can access everything
        
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Required role: {required_role}",
                headers={"X-Required-Role": required_role}
            )
        return user
    
    return role_checker


def require_any_role(*roles):
    """
    Accept any of multiple roles.
    
    Example:
        @app.get("/api/data", dependencies=[Depends(require_any_role("user", "admin"))])
    """
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] == "admin":
            return user  # Admin bypass
        
        if user["role"] not in roles:
            role_list = ", ".join(roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted. Allowed roles: {role_list}"
            )
        return user
    
    return role_checker


def require_permission(permission: str):
    """
    Check if user has specific permission.
    
    Example:
        @app.post("/api/review", dependencies=[Depends(require_permission("can_review"))])
    """
    async def permission_checker(user: dict = Depends(get_current_user)):
        role = user["role"]
        permissions = PERMISSION_MATRIX.get(role, {})
        
        if not permissions.get(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return user
    
    return permission_checker

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROUTE ACCESS VERIFICATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def require_route_access(route_name: str):
    """
    Check if user can access a specific named route.
    
    Example:
        @app.get("/dashboard", dependencies=[Depends(require_route_access("dashboard"))])
    """
    async def route_checker(user: dict = Depends(get_current_user)):
        if not can_access_route(user["role"], route_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to route: {route_name}"
            )
        return user
    
    return route_checker


def check_user_limit(limit_type: str):
    """
    Check if user is within usage limits.
    
    Example:
        @app.post("/api/review", dependencies=[Depends(check_user_limit("daily_requests"))])
    """
    async def limit_checker(user: dict = Depends(get_current_user)):
        role = user["role"]
        permissions = PERMISSION_MATRIX.get(role, {})
        limit = permissions.get(limit_type, 0)
        
        if limit == 0 and limit_type != "storage":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature not available for {role} users"
            )
        
        return user
    
    return limit_checker

# ════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def is_admin(user: dict) -> bool:
    """Check if user is admin"""
    return user.get("role") == "admin"


def is_authenticated(user: dict) -> bool:
    """Check if user is authenticated (not guest)"""
    return user.get("role") != "guest"


def get_user_permissions(user: dict) -> dict:
    """Get all permissions for a user"""
    role = user.get("role", "guest")
    return PERMISSION_MATRIX.get(role, {})

# ════════════════════════════════════════════════════════════════════