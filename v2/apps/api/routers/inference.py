import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import AIModelRegistry
from core.security import get_current_user_context
from inference.backend import inference_backend

router = APIRouter(prefix="/inference", tags=["AI Inference & Models"])

class ModelRegisterRequest(BaseModel):
    name: str
    file_path: str
    family: str = "Google Gemma 4"
    quantization: str = "Q4_K_M"
    context_length: int = 4096
    cpu_threads: int = 4
    gpu_layers: int = 0

class InferenceTestRequest(BaseModel):
    prompt: str
    temperature: float = 0.2
    max_tokens: int = 512
    system_instructions: Optional[str] = ""

@router.get("/models")
async def list_models(user: dict = Depends(get_current_user_context)):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(AIModelRegistry))
        models = res.scalars().all()
        if not models:
            # Seed default detected Gemma 4 models
            defaults = [
                AIModelRegistry(
                    name="Gemma 4 E4B Instruct",
                    family="Google Gemma 4",
                    file_path="./models/gemma-4-e4b-instruct.Q4_K_M.gguf",
                    quantization="Q4_K_M",
                    context_length=4096,
                    cpu_threads=4,
                    gpu_layers=0,
                    is_active=True,
                    status="READY",
                    memory_bytes=4294967296,
                    latency_ms=210.5
                ),
                AIModelRegistry(
                    name="Gemma 4 12B Instruct",
                    family="Google Gemma 4",
                    file_path="./models/gemma-4-12b-instruct.Q4_K_M.gguf",
                    quantization="Q4_K_M",
                    context_length=8192,
                    cpu_threads=8,
                    gpu_layers=0,
                    is_active=False,
                    status="UNLOADED",
                    memory_bytes=8589934592,
                    latency_ms=480.0
                ),
                AIModelRegistry(
                    name="Gemma 4 26B A4B",
                    family="Google Gemma 4",
                    file_path="./models/gemma-4-26b-a4b.Q4_K_M.gguf",
                    quantization="Q4_K_M",
                    context_length=8192,
                    cpu_threads=12,
                    gpu_layers=0,
                    is_active=False,
                    status="UNLOADED",
                    memory_bytes=17179869184,
                    latency_ms=890.0
                )
            ]
            for d in defaults:
                session.add(d)
            await session.commit()
            models = defaults

        return [
            {
                "id": m.id,
                "name": m.name,
                "family": m.family,
                "file_path": m.file_path,
                "quantization": m.quantization,
                "context_length": m.context_length,
                "cpu_threads": m.cpu_threads,
                "gpu_layers": m.gpu_layers,
                "is_active": m.is_active,
                "status": m.status,
                "memory_bytes": m.memory_bytes,
                "latency_ms": m.latency_ms
            }
            for m in models
        ]

@router.post("/models/register")
async def register_model(req: ModelRegisterRequest, user: dict = Depends(get_current_user_context)):
    async with AsyncSessionLocal() as session:
        model = AIModelRegistry(
            name=req.name,
            family=req.family,
            file_path=req.file_path,
            quantization=req.quantization,
            context_length=req.context_length,
            cpu_threads=req.cpu_threads,
            gpu_layers=req.gpu_layers,
            is_active=False,
            status="READY",
            memory_bytes=4294967296
        )
        session.add(model)
        await session.commit()
        return model

@router.post("/models/{model_id}/activate")
async def activate_model(model_id: str, user: dict = Depends(get_current_user_context)):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(AIModelRegistry))
        all_models = res.scalars().all()
        target = None
        for m in all_models:
            if m.id == model_id:
                m.is_active = True
                m.status = "READY"
                target = m
            else:
                m.is_active = False

        if not target:
            raise HTTPException(status_code=404, detail="Model not found")

        inference_backend.load_model(target.file_path, {
            "n_ctx": target.context_length,
            "n_threads": target.cpu_threads,
            "n_gpu_layers": target.gpu_layers
        })
        await session.commit()
        return {"status": "ACTIVATED", "model_id": target.id, "name": target.name}

@router.get("/health")
async def get_inference_health():
    return inference_backend.get_health()

@router.get("/metrics")
async def get_inference_metrics():
    return inference_backend.get_metrics()

@router.post("/test")
async def test_inference(req: InferenceTestRequest, user: dict = Depends(get_current_user_context)):
    return inference_backend.generate(
        req.prompt,
        {
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "system_instructions": req.system_instructions
        }
    )
