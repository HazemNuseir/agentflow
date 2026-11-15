import hashlib
import hmac
import os
import base64
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from core.config import settings

security_bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + key).decode('ascii')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        decoded = base64.b64decode(hashed_password.encode('ascii'))
        salt = decoded[:16]
        key = decoded[16:]
        new_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        return None

ROLE_HIERARCHY = {
    "PLATFORM_OWNER": 100,
    "ORGANIZATION_OWNER": 80,
    "ORGANIZATION_ADMIN": 60,
    "WORKFLOW_EDITOR": 40,
    "APPROVER": 30,
    "VIEWER": 10
}

def has_required_role(user_role: str, min_role: str) -> bool:
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(min_role, 0)

def require_role(min_role: str):
    """
    Dependency factory that checks if current user context has minimum role level.
    """
    async def role_checker(user: Dict[str, Any] = Depends(get_current_user_context)):
        user_role = user.get("role", "VIEWER")
        if not has_required_role(user_role, min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: requires {min_role} role"
            )
        return user
    return role_checker

async def get_current_user_context(credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer)) -> Dict[str, Any]:
    """
    Resolves authenticated user and verifies active organization membership server-side.
    Rejects anonymous calls on protected routes with HTTP 401.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("user_id")
    org_id = payload.get("org_id")
    if not user_id or not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token claims: user_id and org_id required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Server-side validation against database
    from database.session import AsyncSessionLocal
    from database.models import User, OrganizationMember
    
    async with AsyncSessionLocal() as session:
        # Check active user
        u_res = await session.execute(select(User).where(User.id == user_id))
        user_rec = u_res.scalar_one_or_none()
        if not user_rec:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account does not exist or has been removed"
            )
        if not user_rec.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
            
        # Check organization membership
        m_res = await session.execute(
            select(OrganizationMember).where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.org_id == org_id
            )
        )
        membership = m_res.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an active member of the specified organization"
            )
        
        # Override token payload role with verified server-side membership role
        return {
            "user_id": user_rec.id,
            "email": user_rec.email,
            "full_name": user_rec.full_name,
            "org_id": org_id,
            "role": membership.role
        }
