from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import Organization, OrganizationMember, User, AuditLog
from core.security import get_current_user_context

router = APIRouter(prefix="/organizations", tags=["Organizations"])

class OrgCreate(BaseModel):
    name: str
    industry: str = "General"
    country: str = "Jordan"
    language: str = "en"
    deployment_profile: str = "FULLY_PRIVATE_AIRGAPPED"

class MemberInvite(BaseModel):
    email: str
    role: str = "WORKFLOW_EDITOR"

@router.get("/")
async def list_user_organizations(user: dict = Depends(get_current_user_context)):
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(OrganizationMember, Organization)
            .join(Organization, OrganizationMember.org_id == Organization.id)
            .where(OrganizationMember.user_id == user["user_id"])
        )
        items = []
        for mem, org in res.all():
            items.append({
                "id": org.id,
                "name": org.name,
                "industry": org.industry,
                "country": org.country,
                "language": org.language,
                "deployment_profile": org.deployment_profile,
                "edition": org.edition,
                "role": mem.role
            })
        if not items:
            # Fallback for default admin
            items.append({
                "id": user.get("org_id", "org_default_dme"),
                "name": "Digital Mind Engineering (DME)",
                "industry": "IT Services & AI",
                "country": "Jordan",
                "language": "en",
                "deployment_profile": "FULLY_PRIVATE_AIRGAPPED",
                "edition": "ENTERPRISE_PRIVATE",
                "role": "ORGANIZATION_OWNER"
            })
        return items

@router.get("/current")
async def get_current_organization(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Organization).where(Organization.id == org_id))
        org = res.scalar_one_or_none()
        if not org:
            return {
                "id": org_id,
                "name": "Digital Mind Engineering (DME)",
                "industry": "IT Services & AI",
                "country": "Jordan",
                "language": "en",
                "deployment_profile": "FULLY_PRIVATE_AIRGAPPED",
                "edition": "ENTERPRISE_PRIVATE"
            }
        return org

@router.post("/")
async def create_organization(data: OrgCreate, user: dict = Depends(get_current_user_context)):
    async with AsyncSessionLocal() as session:
        org = Organization(
            name=data.name,
            industry=data.industry,
            country=data.country,
            language=data.language,
            deployment_profile=data.deployment_profile
        )
        session.add(org)
        await session.flush()

        member = OrganizationMember(
            org_id=org.id,
            user_id=user["user_id"],
            role="ORGANIZATION_OWNER"
        )
        session.add(member)
        await session.commit()
        return org

@router.get("/members")
async def list_members(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(OrganizationMember, User)
            .join(User, OrganizationMember.user_id == User.id)
            .where(OrganizationMember.org_id == org_id)
        )
        members = []
        for mem, u in res.all():
            members.append({
                "id": mem.id,
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": mem.role,
                "joined_at": mem.created_at.isoformat()
            })
        if not members:
            members.append({
                "id": "mem_001",
                "user_id": user["user_id"],
                "email": user["email"],
                "full_name": user.get("full_name", "Platform Admin"),
                "role": user.get("role", "ORGANIZATION_OWNER"),
                "joined_at": "2026-11-01T00:00:00Z"
            })
        return members
