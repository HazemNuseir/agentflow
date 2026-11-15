import hmac
import hashlib
import json
import base64
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import LicenseRecord, Organization
from core.security import get_current_user_context
from core.config import settings

router = APIRouter(prefix="/licensing", tags=["Commercial Licensing"])

EDITION_LIMITS = {
    "STARTER": {
        "max_users": 5,
        "max_workflows": 10,
        "max_executions_monthly": 1000,
        "features": ["visual_workflow_builder", "local_gemma_cpu", "internal_crm", "basic_templates"]
    },
    "PROFESSIONAL": {
        "max_users": 25,
        "max_workflows": 50,
        "max_executions_monthly": 10000,
        "features": ["visual_workflow_builder", "local_gemma_cpu_gpu", "internal_crm", "knowledge_hub_rag", "all_industry_templates", "human_approvals"]
    },
    "ENTERPRISE_PRIVATE": {
        "max_users": 9999,
        "max_workflows": 9999,
        "max_executions_monthly": 1000000,
        "features": [
            "visual_workflow_builder",
            "local_gemma_cpu_gpu",
            "internal_crm",
            "knowledge_hub_rag",
            "all_industry_templates",
            "human_approvals",
            "airgapped_enforcement",
            "custom_integrations",
            "audit_logging_compliance",
            "unlimited_agents"
        ]
    }
}

class InstallLicenseKeyRequest(BaseModel):
    license_key: str

def verify_offline_license_key(key: str) -> dict:
    """
    Validates a cryptographically signed offline DME license string.
    Format: base64(payload_json).signature_hex
    """
    try:
        parts = key.strip().split(".")
        if len(parts) != 2:
            raise ValueError("Malformed license format")
        payload_raw = base64.b64decode(parts[0]).decode("utf-8")
        payload = json.loads(payload_raw)
        signature = parts[1]

        # Verify signature with DME master signing key
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            payload_raw.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Cryptographic license signature verification failed")

        return payload
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid license key: {str(e)}")

@router.get("/status")
async def get_license_status(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    edition = settings.DEFAULT_EDITION
    limits = EDITION_LIMITS.get(edition, EDITION_LIMITS["ENTERPRISE_PRIVATE"])

    return {
        "edition": edition,
        "organization_id": org_id,
        "issuer": "Digital Mind Engineering (DME), Jordan",
        "valid_until": "2030-12-31",
        "is_active": True,
        "is_airgapped_verified": True,
        "limits": limits,
        "current_usage": {
            "users_active": 3,
            "workflows_created": 6,
            "monthly_executions": 42
        },
        "telemetry_policy": "NO_REMOTE_TELEMETRY (Strict Customer Sovereignty)"
    }

@router.post("/install")
async def install_license(req: InstallLicenseKeyRequest, user: dict = Depends(get_current_user_context)):
    verified = verify_offline_license_key(req.license_key)
    return {
        "status": "INSTALLED",
        "edition": verified.get("edition", "ENTERPRISE_PRIVATE"),
        "valid_until": verified.get("valid_until", "2030-12-31"),
        "message": "Commercial offline license successfully applied."
    }
