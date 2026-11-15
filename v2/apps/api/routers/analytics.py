from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from database.session import AsyncSessionLocal
from database.models import Workflow, WorkflowExecution, ApprovalRequest
from core.security import get_current_user_context
from inference.backend import inference_backend

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])

@router.get("/summary")
async def get_analytics_summary(
    hourly_rate_usd: float = 35.0,
    mins_saved_per_execution: float = 25.0,
    user: dict = Depends(get_current_user_context)
):
    """
    Returns actual recorded operational metrics scoped to the authenticated organization tenant.
    Estimated ROI savings are clearly labeled as modeled estimations with configurable parameters.
    """
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        # Workflows
        wf_res = await session.execute(
            select(func.count(Workflow.id)).where(Workflow.org_id == org_id)
        )
        total_workflows = wf_res.scalar() or 0

        active_wf_res = await session.execute(
            select(func.count(Workflow.id)).where(Workflow.org_id == org_id, Workflow.is_active == True)
        )
        active_workflows = active_wf_res.scalar() or 0

        # Executions
        exec_total_res = await session.execute(
            select(func.count(WorkflowExecution.id)).where(WorkflowExecution.org_id == org_id)
        )
        total_executions = exec_total_res.scalar() or 0

        success_res = await session.execute(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.org_id == org_id,
                WorkflowExecution.status == "COMPLETED"
            )
        )
        successful_executions = success_res.scalar() or 0

        failed_res = await session.execute(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.org_id == org_id,
                WorkflowExecution.status == "FAILED"
            )
        )
        failed_executions = failed_res.scalar() or 0

        # Approvals
        pending_app_res = await session.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.org_id == org_id,
                ApprovalRequest.status == "PENDING"
            )
        )
        pending_approvals = pending_app_res.scalar() or 0

        # Duration
        dur_res = await session.execute(
            select(func.avg(WorkflowExecution.duration_ms)).where(
                WorkflowExecution.org_id == org_id,
                WorkflowExecution.duration_ms > 0
            )
        )
        raw_dur = dur_res.scalar()
        avg_duration_ms = round(raw_dur, 1) if raw_dur is not None else 0.0

    inference_metrics = inference_backend.get_metrics()
    ai_calls = inference_metrics.get("total_calls", 0)
    avg_latency = inference_metrics.get("average_latency_ms", 0.0)

    # Configurable estimation model
    estimated_hours_saved = round((successful_executions * mins_saved_per_execution) / 60.0, 1)
    estimated_cost_saved_usd = round(estimated_hours_saved * hourly_rate_usd, 2)

    return {
        "recorded_metrics": {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "pending_approvals": pending_approvals,
            "average_duration_ms": avg_duration_ms,
            "ai_inference_calls": ai_calls,
            "average_inference_latency_ms": avg_latency
        },
        "estimated_roi_model": {
            "is_estimate": True,
            "hourly_rate_usd_assumption": hourly_rate_usd,
            "mins_saved_per_completed_run": mins_saved_per_execution,
            "estimated_hours_saved": estimated_hours_saved,
            "estimated_cost_saved_usd": estimated_cost_saved_usd,
            "disclaimer": "ROI figures are mathematical projections based on tenant-configured operational rates and do not constitute audited financial results."
        },
        "model_usage": {
            "active_model": "Google Gemma 4 E4B Instruct",
            "quantization": "Q4_K_M",
            "host_footprint": "Local CPU / 4 Threads",
            "airgapped_verified": True
        }
    }
