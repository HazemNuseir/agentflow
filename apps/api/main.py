from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from database.session import init_db
from routers import (
    auth, organizations, onboarding, workflows, executions,
    approvals, agents, inference, knowledge, crm, integrations,
    templates, analytics, licensing, demos
)
import asyncio

# Ensure database tables exist immediately
import database.models
from database.session import Base, engine
Base.metadata.create_all(engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Business Automation Platform by Digital Mind Engineering (DME), Jordan. Your Business. Your Data. Your AI.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & System Status
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "DME AgentFlow API Engine",
        "company": settings.COMPANY,
        "tagline": settings.TAGLINE,
        "deployment_profile": settings.DEPLOYMENT_PROFILE,
        "airgapped_verified": True,
        "local_ai_inference": "ACTIVE"
    }

# Register all Routers under API_V1_STR
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
