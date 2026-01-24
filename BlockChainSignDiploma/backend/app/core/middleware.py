"""
Authentication and Authorization Middleware
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.Utils.jwt_utils import verify_token
import time


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log requests and add user info to request state
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start time for request
        start_time = time.time()
        
        # Public endpoints that don't require authentication
        public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/verify-otp",
            "/api/v1/auth/request-password-reset",
            "/api/v1/auth/reset-password",
        ]
        
        # Check if path is public
        if request.url.path in public_paths:
            response = await call_next(request)
            return response
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)
            
            if payload:
                # Add user info to request state
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
        
        # Continue processing request
        response = await call_next(request)
        
        # Add processing time header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
