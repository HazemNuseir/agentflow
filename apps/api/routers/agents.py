from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import AIAgent
from core.security import get_current_user_context, require_role
from inference.backend import inference_backend

router = APIRouter(prefix="/agents", tags=["AI Agent Studio"])

class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    instructions: str
    model_id: str = "gemma-4-e4b-instruct"
    temperature: float = 0.3
    max_tokens: int = 1024
    output_schema: Dict[str, Any] = {}
    knowledge_base_ids: List[str] = []
    tools: List[str] = []
    budget_tokens: int = 50000
    approval_required: bool = False

class AgentChatTestRequest(BaseModel):
    message: str
    output_schema: Optional[Dict[str, Any]] = None

@router.get("/")
async def list_agents(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(AIAgent).where(AIAgent.org_id == org_id).order_by(AIAgent.created_at.desc())
        )
        agents = res.scalars().all()
        return [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "model_id": a.model_id,
                "instructions": a.instructions,
                "temperature": a.temperature,
                "max_tokens": a.max_tokens,
                "output_schema": a.output_schema_json or {},
                "tools": a.tools_json or [],
                "approval_required": a.approval_required,
                "created_at": a.created_at.isoformat()
            }
            for a in agents
        ]

@router.post("/", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def create_agent(req: AgentCreateRequest, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        agent = AIAgent(
            org_id=org_id,
            name=req.name,
            description=req.description or "",
            instructions=req.instructions,
            model_id=req.model_id,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            output_schema_json=req.output_schema,
            knowledge_base_ids_json=req.knowledge_base_ids,
            tools_json=req.tools,
            budget_tokens=req.budget_tokens,
            approval_required=req.approval_required
        )
        session.add(agent)
        await session.commit()
        return {"id": agent.id, "name": agent.name, "status": "ACTIVE"}

@router.post("/{agent_id}/test", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def test_agent(agent_id: str, req: AgentChatTestRequest, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(AIAgent).where(AIAgent.id == agent_id, AIAgent.org_id == org_id)
        )
        agent = res.scalar_one_or_none()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found in this organization")

        # Compile agent prompt
        prompt = f"System: {agent.instructions}\nUser Message: {req.message}"
        schema = req.output_schema or agent.output_schema_json

        if schema:
            gen_res = inference_backend.generate_structured(prompt, schema)
            return {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "model_used": agent.model_id,
                "structured_output": gen_res.get("structured", {}),
                "is_emulated": gen_res.get("is_emulated", True),
                "latency_ms": gen_res.get("latency_ms", 120.0)
            }
        else:
            gen_res = inference_backend.generate(prompt, temperature=agent.temperature, max_tokens=agent.max_tokens)
            return {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "model_used": agent.model_id,
                "text_output": gen_res.get("text", ""),
                "is_emulated": gen_res.get("is_emulated", True),
                "latency_ms": gen_res.get("latency_ms", 120.0)
            }
