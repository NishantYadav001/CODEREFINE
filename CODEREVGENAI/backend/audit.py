import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from security import decode_access_token

# In-memory audit log storage (In production, this would be a DB table)
AUDIT_LOGS = []

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Audit Trail Middleware
    Logs every POST/PUT/DELETE action by an Admin.
    Captures: Timestamp, ActorID, Action, Status, Duration.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Filter: Only log state-changing methods
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Attempt to identify user from token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    # Decode token manually since middleware runs before dependency injection
                    payload = decode_access_token(token)
                    role = payload.get("role")
                    username = payload.get("sub")
                    
                    if role == "admin":
                        log_entry = {
                            "timestamp": time.time(),
                            "actor": username,
                            "action": f"{request.method} {request.url.path}",
                            "status": response.status_code,
                            "duration": f"{process_time:.4f}s"
                        }
                        AUDIT_LOGS.append(log_entry)
                except Exception:
                    pass # Invalid token or guest, skip audit logging
                    
        return response