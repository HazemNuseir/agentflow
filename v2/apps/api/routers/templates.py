from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import Workflow
from core.security import get_current_user_context, require_role

router = APIRouter(prefix="/templates", tags=["Industry Templates"])

TEMPLATES_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "tpl_lead_qualification",
        "title": "Lead Qualification & Enrichment",
        "industry": "IT Services",
        "category": "Sales",
        "description": "Evaluates inbound web leads with local Gemma 4, scores purchase intent, creates CRM record, and alerts sales team.",
        "required_integrations": ["INTERNAL_CRM"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Lead Intake Form", "category": "TRIGGER", "type": "form_submission", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Evaluate Intent with Gemma", "category": "AI", "type": "classify_text", "position": {"x": 350, "y": 150}, "config": {"categories": ["Enterprise Buyer", "Small Business", "Partner", "Spam"]}},
            {"id": "n3", "name": "Extract Requirements", "category": "AI", "type": "extract_structured", "position": {"x": 600, "y": 150}, "config": {"targetSchema": {"lead_score": "number", "budget": "number", "timeline": "string"}}},
            {"id": "n4", "name": "Record in CRM", "category": "ACTION", "type": "create_crm_lead", "position": {"x": 850, "y": 150}, "config": {}},
            {"id": "n5", "name": "Qualification Success", "category": "COMPLETION", "type": "success", "position": {"x": 1100, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"},
            {"id": "e4-5", "source": "n4", "target": "n5"}
        ]
    },
    {
        "id": "tpl_rfq_extraction",
        "title": "RFQ Extraction & Quotation Preparation",
        "industry": "Manufacturing",
        "category": "Operations",
        "description": "Processes uploaded customer RFQ PDF, extracts alloy specs & quantities, retrieves internal pricing, and drafts quotation for approval.",
        "required_integrations": ["INTERNAL_CRM", "LOCAL_KNOWLEDGE"],
        "required_approvals": True,
        "nodes": [
            {"id": "n1", "name": "RFQ Upload Trigger", "category": "TRIGGER", "type": "manual_trigger", "position": {"x": 100, "y": 200}, "config": {}},
            {"id": "n2", "name": "Extract Technical Specs", "category": "AI", "type": "interpret_document", "position": {"x": 350, "y": 200}, "config": {}},
            {"id": "n3", "name": "Retrieve Pricing Matrix", "category": "AI", "type": "retrieve_knowledge", "position": {"x": 600, "y": 200}, "config": {}},
            {"id": "n4", "name": "Commercial Director Approval", "category": "HUMAN", "type": "request_approval", "position": {"x": 850, "y": 200}, "config": {"assignedRole": "APPROVER"}},
            {"id": "n5", "name": "Generate Quotation PDF", "category": "ACTION", "type": "generate_document", "position": {"x": 1100, "y": 200}, "config": {}},
            {"id": "n6", "name": "RFQ Completed", "category": "COMPLETION", "type": "success", "position": {"x": 1350, "y": 200}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"},
            {"id": "e4-5", "source": "n4", "target": "n5", "condition": "approved"},
            {"id": "e5-6", "source": "n5", "target": "n6"}
        ]
    },
    {
        "id": "tpl_support_routing",
        "title": "Customer Support Routing & RAG Assistance",
        "industry": "Retail",
        "category": "Customer Support",
        "description": "Receives inquiry, searches company knowledge base with local embeddings, drafts grounded reply, and creates ticket.",
        "required_integrations": ["LOCAL_KNOWLEDGE"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Support Ticket Ingest", "category": "TRIGGER", "type": "email_received", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Search Private Knowledge Hub", "category": "AI", "type": "retrieve_knowledge", "position": {"x": 350, "y": 150}, "config": {}},
            {"id": "n3", "name": "Draft Contextual Answer", "category": "AI", "type": "generate_response", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Create Support Task", "category": "ACTION", "type": "create_internal_task", "position": {"x": 850, "y": 150}, "config": {}},
            {"id": "n5", "name": "Support Resolved", "category": "COMPLETION", "type": "success", "position": {"x": 1100, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"},
            {"id": "e4-5", "source": "n4", "target": "n5"}
        ]
    },
    {
        "id": "tpl_maintenance_ticket",
        "title": "Maintenance Ticket & Predictive Sensor Evaluation",
        "industry": "Engineering",
        "category": "Maintenance",
        "description": "Evaluates simulated machine sensor telemetry, checks vibration/temperature limits, retrieves service guide, and creates dispatch task.",
        "required_integrations": ["LOCAL_KNOWLEDGE", "INTERNAL_CRM"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Sensor Event Trigger", "category": "TRIGGER", "type": "manual_trigger", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Evaluate Vibration Threshold (>4.8 mm/s)", "category": "LOGIC", "type": "condition", "position": {"x": 350, "y": 150}, "config": {"field": "vibration_level", "operator": "gte", "value": 4.8}},
            {"id": "n3", "name": "Retrieve Service Protocol", "category": "AI", "type": "retrieve_knowledge", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Create Maintenance Task", "category": "ACTION", "type": "create_internal_task", "position": {"x": 850, "y": 150}, "config": {"priority": "HIGH"}},
            {"id": "n5", "name": "Action Completed", "category": "COMPLETION", "type": "success", "position": {"x": 1100, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3", "condition": "true"},
            {"id": "e3-4", "source": "n3", "target": "n4"},
            {"id": "e4-5", "source": "n4", "target": "n5"}
        ]
    },
    {
        "id": "tpl_logistics_order",
        "title": "Order Inquiry & Shipping Processing",
        "industry": "Logistics",
        "category": "Supply Chain",
        "description": "Validates bill of lading and manifest records, calculates delivery lead times, and notifies dispatch coordinator.",
        "required_integrations": ["REST_API"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Inbound Shipment Notice", "category": "TRIGGER", "type": "webhook", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Extract Shipping Waybill", "category": "AI", "type": "extract_structured", "position": {"x": 350, "y": 150}, "config": {}},
            {"id": "n3", "name": "Create Tracking Task", "category": "ACTION", "type": "create_internal_task", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Order Processed", "category": "COMPLETION", "type": "success", "position": {"x": 850, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"}
        ]
    },
    {
        "id": "tpl_client_onboarding",
        "title": "Client Onboarding & Compliance Verification",
        "industry": "Professional Services",
        "category": "Client Services",
        "description": "Collects legal registrations, verifies tax documentation, and generates engagement welcome letter.",
        "required_integrations": ["INTERNAL_CRM"],
        "required_approvals": True,
        "nodes": [
            {"id": "n1", "name": "Client Questionnaire", "category": "TRIGGER", "type": "form_submission", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Create Client Contact", "category": "ACTION", "type": "create_crm_contact", "position": {"x": 350, "y": 150}, "config": {}},
            {"id": "n3", "name": "Partner Approval", "category": "HUMAN", "type": "request_approval", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Onboarding Complete", "category": "COMPLETION", "type": "success", "position": {"x": 850, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4", "condition": "approved"}
        ]
    },
    {
        "id": "tpl_training_registration",
        "title": "Training Registration & Student Placement",
        "industry": "Education",
        "category": "Academic",
        "description": "Assesses student background, scores course prerequisites, and issues enrollment confirmation.",
        "required_integrations": ["INTERNAL_CRM"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Application Ingest", "category": "TRIGGER", "type": "form_submission", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Classify Placement Level", "category": "AI", "type": "classify_text", "position": {"x": 350, "y": 150}, "config": {}},
            {"id": "n3", "name": "Create Student Record", "category": "ACTION", "type": "create_crm_contact", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Registration Success", "category": "COMPLETION", "type": "success", "position": {"x": 850, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"}
        ]
    },
    {
        "id": "tpl_hospitality_concierge",
        "title": "Guest Request Routing & VIP Priority",
        "industry": "Hospitality",
        "category": "Guest Services",
        "description": "Categorizes guest requests, flags VIP requirements, and assigns immediate room service or housekeeping tickets.",
        "required_integrations": ["INTERNAL_CRM"],
        "required_approvals": False,
        "nodes": [
            {"id": "n1", "name": "Guest Request Inbound", "category": "TRIGGER", "type": "form_submission", "position": {"x": 100, "y": 150}, "config": {}},
            {"id": "n2", "name": "Classify Urgency", "category": "AI", "type": "classify_text", "position": {"x": 350, "y": 150}, "config": {}},
            {"id": "n3", "name": "Create Housekeeping Task", "category": "ACTION", "type": "create_internal_task", "position": {"x": 600, "y": 150}, "config": {}},
            {"id": "n4", "name": "Request Handled", "category": "COMPLETION", "type": "success", "position": {"x": 850, "y": 150}, "config": {}}
        ],
        "edges": [
            {"id": "e1-2", "source": "n1", "target": "n2"},
            {"id": "e2-3", "source": "n2", "target": "n3"},
            {"id": "e3-4", "source": "n3", "target": "n4"}
        ]
    }
]

@router.get("/")
async def list_templates(industry: str = None):
    if industry:
        return [t for t in TEMPLATES_CATALOG if t["industry"].lower() == industry.lower()]
    return TEMPLATES_CATALOG

@router.post("/{template_id}/install", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def install_template(template_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    tpl = next((t for t in TEMPLATES_CATALOG if t["id"] == template_id), None)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    async with AsyncSessionLocal() as session:
        wf = Workflow(
            org_id=org_id,
            name=f"{tpl['title']} (from template)",
            description=tpl["description"],
            category=tpl["category"],
            version=1,
            is_published=False,
            is_active=True,
            nodes_json=tpl["nodes"],
            edges_json=tpl["edges"],
            metadata_json={"installed_from_template": template_id, "industry": tpl["industry"]}
        )
        session.add(wf)
        await session.commit()
        return {"workflow_id": wf.id, "name": wf.name, "status": "INSTALLED"}
