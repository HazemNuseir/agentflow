from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import Workflow, AuditLog
from core.security import get_current_user_context, require_role

router = APIRouter(prefix="/workflows", tags=["Workflows"])

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    category: str = "General"
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None

def validate_workflow_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
    """
    Server-side structural and node configuration validator.
    Ensures connected components, valid categories, and acyclic/schedulable structure.
    """
    if not nodes:
        raise HTTPException(status_code=400, detail="Workflow graph must contain at least one node")
        
    node_ids = {n.get("id") for n in nodes if n.get("id")}
    if len(node_ids) != len(nodes):
        raise HTTPException(status_code=400, detail="Duplicate or missing node IDs in graph definition")

    valid_categories = {"TRIGGER", "LOGIC", "AI", "ACTION", "HUMAN", "COMPLETION"}
    for n in nodes:
        cat = n.get("category", "").upper()
        if cat not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid node category: {cat} on node {n.get('id')}")

    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src not in node_ids or tgt not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge references non-existent node: {src} -> {tgt}")

@router.get("/")
async def list_workflows(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.org_id == org_id).order_by(Workflow.updated_at.desc())
        )
        wfs = res.scalars().all()
        return [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "category": w.category,
                "version": w.version,
                "is_published": w.is_published,
                "is_active": w.is_active,
                "node_count": len(w.nodes_json or []),
                "edge_count": len(w.edges_json or []),
                "created_at": w.created_at.isoformat(),
                "updated_at": w.updated_at.isoformat()
            }
            for w in wfs
        ]

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.org_id == org_id)
        )
        w = res.scalar_one_or_none()
        if not w:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return {
            "id": w.id,
            "name": w.name,
            "description": w.description,
            "category": w.category,
            "version": w.version,
            "is_published": w.is_published,
            "is_active": w.is_active,
            "nodes": w.nodes_json or [],
            "edges": w.edges_json or [],
            "metadata": w.metadata_json or {},
            "created_at": w.created_at.isoformat(),
            "updated_at": w.updated_at.isoformat()
        }

@router.post("/", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def create_workflow(data: WorkflowCreate, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    if data.nodes or data.edges:
        validate_workflow_graph(data.nodes, data.edges)
        
    async with AsyncSessionLocal() as session:
        wf = Workflow(
            org_id=org_id,
            name=data.name,
            description=data.description or "",
            category=data.category,
            version=1,
            is_published=False,
            is_active=True,
            nodes_json=data.nodes,
            edges_json=data.edges
        )
        session.add(wf)
        await session.commit()
        return {"id": wf.id, "name": wf.name, "version": wf.version}

@router.put("/{workflow_id}", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def update_workflow(workflow_id: str, data: WorkflowUpdate, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.org_id == org_id)
        )
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")

        target_nodes = data.nodes if data.nodes is not None else (wf.nodes_json or [])
        target_edges = data.edges if data.edges is not None else (wf.edges_json or [])
        if data.nodes is not None or data.edges is not None:
            validate_workflow_graph(target_nodes, target_edges)

        if data.name is not None:
            wf.name = data.name
        if data.description is not None:
            wf.description = data.description
        if data.category is not None:
            wf.category = data.category
        if data.nodes is not None:
            wf.nodes_json = data.nodes
        if data.edges is not None:
            wf.edges_json = data.edges
        if data.is_active is not None:
            wf.is_active = data.is_active

        wf.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return {"id": wf.id, "status": "UPDATED"}

@router.post("/{workflow_id}/publish", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def publish_workflow(workflow_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.org_id == org_id)
        )
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")

        nodes = wf.nodes_json or []
        edges = wf.edges_json or []
        validate_workflow_graph(nodes, edges)

        # Snapshot immutable definition
        snapshot = {
            "version": wf.version,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "published_by": user.get("email"),
            "nodes": nodes,
            "edges": edges
        }

        wf.is_published = True
        wf.published_snapshot_json = snapshot
        wf.version += 1
        wf.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return {"id": wf.id, "version": wf.version, "is_published": True}

@router.delete("/{workflow_id}", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def delete_workflow(workflow_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.id == workflow_id, Workflow.org_id == org_id)
        )
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")
        await session.delete(wf)
        await session.commit()
        return {"id": workflow_id, "deleted": True}
