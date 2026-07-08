"""
AgroGuard Authentication Module
Handles JWT tokens, password hashing, and user authentication
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from functools import wraps
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

security = HTTPBearer(auto_error=False)


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


# ============================================================================
# JWT TOKEN GENERATION & VALIDATION
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# DEPENDENCY INJECTION FOR PROTECTED ROUTES
# ============================================================================


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token_cookie: Optional[str] = Cookie(default=None, alias="access_token")
) -> dict:
    """Dependency to extract and validate current user from JWT token (Cookie or Header)"""
    token = None
    
    # 1. Try Cookie
    if token_cookie:
        token = token_cookie
    
    # 2. Try Header
    elif credentials:
        token = credentials.credentials
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    user_type = payload.get("type")  # "farmer" or "aeo"
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "user_type": user_type}


async def get_superadmin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that ensures the JWT token belongs to a Super‑Admin.
    The token payload must contain "type": "superadmin".
    """
    if current_user.get("user_type") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super‑Admin privileges required",
        )
    return current_user


async def get_farmer_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to ensure current user is a farmer"""
    if current_user.get("user_type") != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can access this resource",
        )
    return current_user


async def get_aeo_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to ensure current user is an AEO"""
    if current_user.get("user_type") != "aeo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only AEOs can access this resource",
        )
    return current_user


# ============================================================================
# OPTIONAL: NO AUTH REQUIRED (FOR BACKWARD COMPATIBILITY)
# ============================================================================

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Get current user if token provided, but don't fail if not"""
    if credentials is None:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
        return {
            "user_id": payload.get("sub"),
            "user_type": payload.get("type")
        }
    except HTTPException:
        return None
