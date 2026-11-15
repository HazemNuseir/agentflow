from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import CRMContact, CRMLead, CRMOpportunity, CRMTask
from core.security import get_current_user_context, require_role

router = APIRouter(prefix="/crm", tags=["Internal CRM"])

class ContactCreate(BaseModel):
    first_name: str
    last_name: str = ""
    email: str
    phone: Optional[str] = ""
    company_name: Optional[str] = ""
    status: str = "LEAD"

class LeadCreate(BaseModel):
    title: str
    contact_name: str
    contact_email: str
    source: str = "Inbound Web"
    score: int = 50
    estimated_value: float = 0.0
    notes: Optional[str] = ""

class OpportunityCreate(BaseModel):
    title: str
    stage: str = "DISCOVERY"
    amount: float = 0.0
    probability: int = 50
    close_date: Optional[str] = ""

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: str = "NORMAL"
    assigned_to: str = "AgentFlow Operator"

# CONTACTS
@router.get("/contacts")
async def list_contacts(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(CRMContact).where(CRMContact.org_id == org_id).order_by(CRMContact.created_at.desc())
        )
        items = res.scalars().all()
        return [
            {
                "id": c.id,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "email": c.email,
                "phone": c.phone,
                "company_name": c.company_name,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            }
            for c in items
        ]

@router.post("/contacts", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def create_contact(req: ContactCreate, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        contact = CRMContact(
            org_id=org_id,
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            phone=req.phone or "",
            company_name=req.company_name or "",
            status=req.status
        )
        session.add(contact)
        await session.commit()
        return {"id": contact.id, "email": contact.email, "status": "CREATED"}

# LEADS
@router.get("/leads")
async def list_leads(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(CRMLead).where(CRMLead.org_id == org_id).order_by(CRMLead.created_at.desc())
        )
        items = res.scalars().all()
        return [
            {
                "id": l.id,
                "title": l.title,
                "contact_name": l.contact_name,
                "contact_email": l.contact_email,
                "source": l.source,
                "score": l.score,
                "estimated_value": l.estimated_value,
                "notes": l.notes,
                "created_at": l.created_at.isoformat()
            }
            for l in items
        ]

@router.post("/leads", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def create_lead(req: LeadCreate, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        lead = CRMLead(
            org_id=org_id,
            title=req.title,
            contact_name=req.contact_name,
            contact_email=req.contact_email,
            source=req.source,
            score=req.score,
            estimated_value=req.estimated_value,
            notes=req.notes or ""
        )
        session.add(lead)
        await session.commit()
        return {"id": lead.id, "title": lead.title, "status": "CREATED"}

# OPPORTUNITIES
@router.get("/opportunities")
async def list_opportunities(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(CRMOpportunity).where(CRMOpportunity.org_id == org_id).order_by(CRMOpportunity.created_at.desc())
        )
        items = res.scalars().all()
        return [
            {
                "id": o.id,
                "title": o.title,
                "stage": o.stage,
                "amount": o.amount,
                "probability": o.probability,
                "created_at": o.created_at.isoformat()
            }
            for o in items
        ]

# TASKS
@router.get("/tasks")
async def list_tasks(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(CRMTask).where(CRMTask.org_id == org_id).order_by(CRMTask.created_at.desc())
        )
        items = res.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "priority": t.priority,
                "assigned_to": t.assigned_to,
                "is_completed": t.is_completed,
                "created_at": t.created_at.isoformat()
            }
            for t in items
        ]
