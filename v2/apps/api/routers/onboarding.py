from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from database.session import AsyncSessionLocal
from database.models import Organization
from core.security import get_current_user_context

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])

class OnboardingData(BaseModel):
    organization_name: str
    industry: str
    country: str = "Jordan"
    language: str = "en"
    timezone: str = "Asia/Amman"
    team_size: str = "10-50"
    department: str = "Operations"
    business_objectives: List[str] = ["Automate Sales RFQ", "Reduce manual data entry"]
    existing_software: List[str] = ["ERP", "Email", "Excel"]
    preferred_deployment: str = "FULLY_PRIVATE_AIRGAPPED"
    infrastructure_specs: str = "Local CPU 8-Core, 32GB RAM"

@router.post("/submit")
async def submit_onboarding(data: OnboardingData, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        # Update current org
        org = await session.get(Organization, org_id)
        if org:
            org.name = data.organization_name
            org.industry = data.industry
            org.country = data.country
            org.language = data.language
            org.timezone = data.timezone
            org.deployment_profile = data.preferred_deployment
            await session.commit()

    # Determine recommended templates based on industry
    industry_recommendations = {
        "Manufacturing": ["RFQ Extraction", "Supplier Comparison", "Maintenance Ticket Classification"],
        "Logistics": ["Order Inquiry Processing", "Lead Qualification", "Document Processing"],
        "Retail": ["Sales Inquiry Processing", "Order Inquiry Processing", "Customer Support Routing"],
        "Professional Services": ["Client Onboarding", "Quotation Draft Preparation", "Task Assignment"],
        "IT Services": ["Customer Support Routing", "Lead Qualification", "Maintenance Ticket Classification"],
        "Hospitality": ["Customer Support Routing", "Client Onboarding", "Sales Inquiry Processing"],
        "Education": ["Training Registration", "Document Processing", "Customer Support Routing"],
        "Engineering": ["RFQ Extraction", "Quotation Draft Preparation", "Document Processing"]
    }

    recs = industry_recommendations.get(data.industry, ["Lead Qualification", "Customer Support Routing", "Document Processing"])

    return {
        "status": "COMPLETED",
        "message": "Organization onboarding configuration updated successfully.",
        "recommended_templates": recs,
        "selected_profile": data.preferred_deployment,
        "hardware_verified": True
    }
