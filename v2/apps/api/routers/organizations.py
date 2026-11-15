from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import Organization, OrganizationMember, User, AuditLog
from core.security import get_current_user_context, require_role, hash_password

router = APIRouter(prefix="/organizations", tags=["Organizations"])

class OrgCreate(BaseModel):
    name: str
    industry: str = "General"
    country: str = "Jordan"
    language: str = "en"
    deployment_profile: str = "FULLY_PRIVATE_AIRGAPPED"

class MemberInviteOrAdd(BaseModel):
    email: str
    full_name: str
    password: Optional[str] = None
    role: str = "WORKFLOW_EDITOR"

class MemberRoleUpdate(BaseModel):
    role: str

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
        return items

@router.get("/current")
async def get_current_organization(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Organization).where(Organization.id == org_id))
        org = res.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return {
            "id": org.id,
            "name": org.name,
            "industry": org.industry,
            "country": org.country,
            "language": org.language,
            "deployment_profile": org.deployment_profile,
            "edition": org.edition,
            "current_user_role": user.get("role")
        }

@router.post("/", dependencies=[Depends(require_role("ORGANIZATION_OWNER"))])
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
        return {"id": org.id, "name": org.name}

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
                "is_active": u.is_active,
                "joined_at": mem.created_at.isoformat()
            })
        return members

@router.post("/members", dependencies=[Depends(require_role("ORGANIZATION_ADMIN"))])
async def add_or_invite_member(data: MemberInviteOrAdd, user: dict = Depends(get_current_user_context)):
    """
    Enables administrators on the local network to provision user accounts and assign roles within their organization.
    """
    org_id = user.get("org_id")
    valid_roles = {"ORGANIZATION_OWNER", "ORGANIZATION_ADMIN", "WORKFLOW_EDITOR", "APPROVER", "VIEWER"}
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role '{data.role}'. Allowed: {sorted(list(valid_roles))}")

    if data.role == "ORGANIZATION_OWNER" and user["role"] != "ORGANIZATION_OWNER":
        raise HTTPException(status_code=403, detail="Only owners may assign the owner role")

    async with AsyncSessionLocal() as session:
        # Check if user already exists
        u_res = await session.execute(select(User).where(User.email == data.email))
        target_user = u_res.scalar_one_or_none()

        if not target_user:
            if not data.password or len(data.password) < 12:
                raise HTTPException(status_code=400, detail="New accounts require a password of at least 12 characters")
            target_user = User(
                email=data.email,
                full_name=data.full_name,
                hashed_password=hash_password(data.password),
                is_active=True,
                is_verified=True
            )
            session.add(target_user)
            await session.flush()

        # Check existing membership in this org
        m_res = await session.execute(
            select(OrganizationMember).where(
                OrganizationMember.org_id == org_id,
                OrganizationMember.user_id == target_user.id
            )
        )
        existing_mem = m_res.scalar_one_or_none()
        if existing_mem:
            raise HTTPException(status_code=409, detail="User is already a member of this organization")

        new_mem = OrganizationMember(
            org_id=org_id,
            user_id=target_user.id,
            role=data.role
        )
        session.add(new_mem)
        await session.commit()

        return {
            "id": new_mem.id,
            "user_id": target_user.id,
            "email": target_user.email,
            "full_name": target_user.full_name,
            "role": new_mem.role,
            "status": "PROVISIONED"
        }

@router.put("/members/{member_id}/role", dependencies=[Depends(require_role("ORGANIZATION_ADMIN"))])
async def update_member_role(member_id: str, data: MemberRoleUpdate, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    valid_roles = {"ORGANIZATION_OWNER", "ORGANIZATION_ADMIN", "WORKFLOW_EDITOR", "APPROVER", "VIEWER"}
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role '{data.role}'. Allowed: {sorted(list(valid_roles))}")

    async with AsyncSessionLocal() as session:
        m_res = await session.execute(
            select(OrganizationMember).where(
                OrganizationMember.id == member_id,
                OrganizationMember.org_id == org_id
            )
        )
        member = m_res.scalar_one_or_none()
        if not member:
            raise HTTPException(status_code=404, detail="Organization member not found")

        if user["role"] != "ORGANIZATION_OWNER" and (member.role == "ORGANIZATION_OWNER" or data.role == "ORGANIZATION_OWNER"):
            raise HTTPException(status_code=403, detail="Only owners may manage the owner role")
        if member.user_id == user["user_id"]:
            raise HTTPException(status_code=400, detail="You cannot change your own role")
        member.role = data.role
        await session.commit()
        return {"id": member.id, "role": member.role, "status": "UPDATED"}
