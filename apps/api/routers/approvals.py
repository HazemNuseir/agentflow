from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import ApprovalRequest, WorkflowExecution, Workflow
from core.security import get_current_user_context, require_role, has_required_role
from engine.executor import execution_engine

router = APIRouter(prefix="/approvals", tags=["Human Approval Center"])

class ApprovalDecisionRequest(BaseModel):
    decision: str  # "APPROVED", "REJECTED", "CLARIFICATION_REQUESTED"
    comments: Optional[str] = ""

@router.get("/")
async def list_approvals(status: Optional[str] = None, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        query = select(ApprovalRequest).where(ApprovalRequest.org_id == org_id)
        if status:
            query = query.where(ApprovalRequest.status == status)
        query = query.order_by(ApprovalRequest.created_at.desc())

        res = await session.execute(query)
        approvals = res.scalars().all()
        return [
            {
                "id": a.id,
                "workflow_id": a.workflow_id,
                "execution_id": a.execution_id,
                "node_id": a.node_id,
                "title": a.title,
                "description": a.description,
                "action_type": a.action_type,
                "payload": a.payload_json or {},
                "status": a.status,
                "assigned_role": a.assigned_role,
                "requested_by": a.requested_by,
                "decided_by": a.decided_by,
                "decided_at": a.decided_at.isoformat() if a.decided_at else None,
                "comments": a.comments,
                "created_at": a.created_at.isoformat()
            }
            for a in approvals
        ]

@router.post("/{approval_id}/decision", dependencies=[Depends(require_role("APPROVER"))])
async def decide_approval(
    approval_id: str,
    req: ApprovalDecisionRequest,
    user: dict = Depends(get_current_user_context)
):
    valid_decisions = {"APPROVED", "REJECTED", "CLARIFICATION_REQUESTED"}
    decision_clean = req.decision.strip().upper()
    if decision_clean not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision '{req.decision}'. Allowed values: {sorted(list(valid_decisions))}"
        )

    org_id = user.get("org_id")
    user_role = user.get("role", "VIEWER")

    async with AsyncSessionLocal() as session:
        # Atomic lock/fetch of approval request scoped to org
        res = await session.execute(
            select(ApprovalRequest).where(
                ApprovalRequest.id == approval_id,
                ApprovalRequest.org_id == org_id
            )
        )
        approval = res.scalar_one_or_none()
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")

        # Atomic transition guard: prevent race condition on competing decisions
        if approval.status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Approval request has already been decided as {approval.status} by {approval.decided_by} at {approval.decided_at}"
            )

        # Enforce approver role eligibility
        required_role = approval.assigned_role or "APPROVER"
        if not has_required_role(user_role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Approver eligibility check failed: requires at least {required_role} role"
            )

        # Atomic update
        approval.status = decision_clean
        approval.decided_by = user.get("email", "approver@dme.jo")
        approval.decided_at = datetime.now(timezone.utc)
        approval.comments = req.comments or ""

        execution_id = approval.execution_id
        node_id = approval.node_id

        # Verify execution is still bound to this exact approval request and node
        ex_res = await session.execute(
            select(WorkflowExecution).where(
                WorkflowExecution.id == execution_id,
                WorkflowExecution.org_id == org_id
            )
        )
        execution = ex_res.scalar_one_or_none()
        if not execution:
            raise HTTPException(status_code=404, detail="Bound workflow execution not found")

        if execution.status == "CANCELLED":
            raise HTTPException(
                status_code=400,
                detail="Cannot decide approval for an execution that has already been cancelled"
            )

        if execution.current_node_id != node_id:
            raise HTTPException(
                status_code=400,
                detail=f"Approval node mismatch: approval is bound to node {node_id}, but execution is at node {execution.current_node_id}"
            )

        await session.commit()

    # If APPROVED, resume the execution from the exact paused node
    if decision_clean == "APPROVED":
        resume_res = await execution_engine.execute_workflow(
            execution_id=execution_id,
            resume_from_node_id=node_id,
            approval_decision="APPROVED"
        )
        return {
            "approval_id": approval_id,
            "status": "APPROVED",
            "execution_status": resume_res.get("status"),
            "resume_result": resume_res
        }
    elif decision_clean == "REJECTED":
        async with AsyncSessionLocal() as session:
            ex_res = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            ex = ex_res.scalar_one_or_none()
            if ex:
                ex.status = "CANCELLED"
                ex.error_message = f"Approval rejected by {user.get('email')}: {req.comments}"
                ex.completed_at = datetime.now(timezone.utc)
                await session.commit()
        return {"approval_id": approval_id, "status": "REJECTED", "execution_status": "CANCELLED"}
    else:
        # CLARIFICATION_REQUESTED: stays in waiting state with clarification note
        async with AsyncSessionLocal() as session:
            ex_res = await session.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            ex = ex_res.scalar_one_or_none()
            if ex:
                ex.error_message = f"Clarification requested by {user.get('email')}: {req.comments}"
                await session.commit()
        return {"approval_id": approval_id, "status": "CLARIFICATION_REQUESTED", "execution_status": "WAITING_APPROVAL"}
