from fastapi import FastAPI
from core.config import settings
from database.session import Base, engine
from sqlalchemy import inspect, text
import database.models
from routers import (
    auth, organizations, onboarding, workflows, executions,
    approvals, agents, inference, knowledge, crm, integrations,
    templates, analytics, licensing, demos
)

# Initialize V2 database tables immediately
Base.metadata.create_all(engine)
with engine.begin() as connection:
    if "graph_snapshot_json" not in {column["name"] for column in inspect(connection).get_columns("workflow_executions")}:
        connection.execute(text("ALTER TABLE workflow_executions ADD COLUMN graph_snapshot_json JSON"))

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="DME AgentFlow V2 — Enterprise Business Automation Platform for Shared Local Network (LAN) Deployments. Powered by Digital Mind Engineering (DME), Jordan.",
    version=settings.VERSION
)

# System Health & Operational Status Probe
@app.get("/health", tags=["System"])
async def health_check():
    from inference.backend import inference_backend
    inf_health = inference_backend.get_health()
    return {
        "status": "healthy",
        "service": "DME AgentFlow V2 API Engine",
        "version": settings.VERSION,
        "company": settings.COMPANY,
        "tagline": settings.TAGLINE,
        "deployment_profile": settings.DEPLOYMENT_PROFILE,
        "lan_shared_mode": True,
        "listen_host": settings.SERVER_HOST,
        "listen_port": settings.SERVER_PORT,
        "database_backend": engine.dialect.name,
        "airgapped_verified": False,
        "inference_engine": inf_health["backend"],
        "inference_mode": inf_health["inference_mode"],
        "is_simulated_inference": inf_health["is_simulated"],
        "max_concurrent_inference": inf_health["max_concurrent_slots"],
        "active_inference_jobs": inf_health["active_inference_jobs"]
    }

# Register all V2 Routers under API_V1_STR
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(organizations.router, prefix=settings.API_V1_STR)
app.include_router(onboarding.router, prefix=settings.API_V1_STR)
app.include_router(workflows.router, prefix=settings.API_V1_STR)
app.include_router(executions.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(inference.router, prefix=settings.API_V1_STR)
app.include_router(knowledge.router, prefix=settings.API_V1_STR)
app.include_router(crm.router, prefix=settings.API_V1_STR)
app.include_router(integrations.router, prefix=settings.API_V1_STR)
app.include_router(templates.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(licensing.router, prefix=settings.API_V1_STR)
app.include_router(demos.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
