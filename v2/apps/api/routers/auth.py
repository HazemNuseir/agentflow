from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import User, Organization, OrganizationMember
from core.security import hash_password, verify_password, create_access_token, get_current_user_context

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str = "My Organization"

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    async with AsyncSessionLocal() as session:
        # Check if user exists
        existing = await session.execute(select(User).where(User.email == req.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create org
        org = Organization(
            name=req.organization_name,
            industry="General",
            country="Jordan"
        )
        session.add(org)
        await session.flush()

        # Create user
        user = User(
            email=req.email,
            hashed_password=hash_password(req.password),
            full_name=req.full_name
        )
        session.add(user)
        await session.flush()

        # Add member as owner
        member = OrganizationMember(
            org_id=org.id,
            user_id=user.id,
            role="ORGANIZATION_OWNER"
        )
        session.add(member)
        await session.commit()

        token_payload = {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "org_id": org.id,
            "role": "ORGANIZATION_OWNER"
        }
        token = create_access_token(token_payload)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": token_payload
        }

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.email == req.email))
        user = res.scalar_one_or_none()
        if not user or not user.is_active or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Get user's org & role
        mem_res = await session.execute(
            select(OrganizationMember).where(OrganizationMember.user_id == user.id)
            .order_by(OrganizationMember.created_at, OrganizationMember.id).limit(1)
        )
        member = mem_res.scalar_one_or_none()
        org_id = member.org_id if member else "default_org"
        role = member.role if member else "VIEWER"

        token_payload = {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "org_id": org_id,
            "role": role
        }
        token = create_access_token(token_payload)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": token_payload
        }

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user_context)):
    return user
