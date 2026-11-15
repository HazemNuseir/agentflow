from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import WorkflowExecution, Workflow
from core.security import get_current_user_context, require_role
from engine.executor import execution_engine

router = APIRouter(prefix="/executions", tags=["Workflow Executions"])

class TriggerWorkflowRequest(BaseModel):
    workflow_id: str
    trigger_type: str = "manual_trigger"
    payload: Dict[str, Any] = {}

class DraftTestRequest(BaseModel):
    workflow_id: str
    payload: Dict[str, Any] = {}

@router.get("/")
async def list_executions(workflow_id: Optional[str] = None, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        query = select(WorkflowExecution).where(WorkflowExecution.org_id == org_id)
        if workflow_id:
            query = query.where(WorkflowExecution.workflow_id == workflow_id)
        query = query.order_by(WorkflowExecution.started_at.desc()).limit(100)

        res = await session.execute(query)
        executions = res.scalars().all()
        return [
            {
                "id": e.id,
                "workflow_id": e.workflow_id,
                "workflow_version": e.workflow_version,
                "status": e.status,
                "is_draft_test": e.is_draft_test,
                "trigger_type": e.trigger_type,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
                "duration_ms": e.duration_ms,
                "current_node_id": e.current_node_id,
                "approval_request_id": e.approval_request_id,
                "error_message": e.error_message
            }
            for e in executions
        ]

@router.get("/{execution_id}")
async def get_execution(execution_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id, WorkflowExecution.org_id == org_id)
        )
        e = res.scalar_one_or_none()
        if not e:
            raise HTTPException(status_code=404, detail="Execution not found")

        return {
            "id": e.id,
            "workflow_id": e.workflow_id,
            "workflow_version": e.workflow_version,
            "status": e.status,
            "is_draft_test": e.is_draft_test,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            "duration_ms": e.duration_ms,
            "trigger_type": e.trigger_type,
            "trigger_payload": e.trigger_payload_json or {},
            "current_node_id": e.current_node_id,
            "node_records": e.node_records_json or {},
            "context_data": e.context_data_json or {},
            "error_message": e.error_message,
            "approval_request_id": e.approval_request_id
        }

@router.post("/trigger", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def trigger_execution(req: TriggerWorkflowRequest, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        # Verify workflow exists in org
        res = await session.execute(
            select(Workflow).where(Workflow.id == req.workflow_id, Workflow.org_id == org_id)
        )
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")

        if not wf.is_published:
            raise HTTPException(
                status_code=400,
                detail="Workflow must be published before normal execution. Use /executions/test-draft for evaluation runs."
            )
        if not wf.is_active:
            raise HTTPException(status_code=400, detail="Cannot trigger an inactive workflow")

        execution = WorkflowExecution(
            org_id=org_id,
            workflow_id=wf.id,
            workflow_version=wf.version,
            is_draft_test=False,
            graph_snapshot_json=wf.published_snapshot_json or {"nodes": wf.nodes_json, "edges": wf.edges_json},
            status="QUEUED",
            trigger_type=req.trigger_type,
            trigger_payload_json=req.payload
        )
        session.add(execution)
        await session.commit()

    result = await execution_engine.execute_workflow(execution_id=execution.id)
    return result

@router.post("/test-draft", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def test_draft_execution(req: DraftTestRequest, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(Workflow).where(Workflow.id == req.workflow_id, Workflow.org_id == org_id)
        )
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail="Workflow not found")

        execution = WorkflowExecution(
            org_id=org_id,
            workflow_id=wf.id,
            workflow_version=wf.version,
            is_draft_test=True,
            graph_snapshot_json={"nodes": wf.nodes_json, "edges": wf.edges_json},
            status="QUEUED",
            trigger_type="draft_test",
            trigger_payload_json=req.payload
        )
        session.add(execution)
        await session.commit()

    result = await execution_engine.execute_workflow(execution_id=execution.id, is_draft=True)
    return result

@router.post("/{execution_id}/cancel", dependencies=[Depends(require_role("WORKFLOW_EDITOR"))])
async def cancel_execution(execution_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(WorkflowExecution).where(WorkflowExecution.id == execution_id, WorkflowExecution.org_id == org_id)
        )
        e = res.scalar_one_or_none()
        if not e:
            raise HTTPException(status_code=404, detail="Execution not found")

        e.status = "CANCELLED"
        await session.commit()
        return {"id": e.id, "status": "CANCELLED"}
