import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from database.session import AsyncSessionLocal
from database.models import KnowledgeDocument, KnowledgeChunk
from core.security import get_current_user_context
from core.config import settings
from knowledge.engine import knowledge_engine

router = APIRouter(prefix="/knowledge", tags=["Private Knowledge Hub"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 4

@router.get("/documents")
async def list_documents(user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.org_id == org_id).order_by(KnowledgeDocument.created_at.desc())
        )
        docs = res.scalars().all()
        if not docs:
            # Seed standard knowledge document
            sample_path = os.path.join(settings.DOCUMENTS_DIR, "dme_operations_manual.txt")
            if not os.path.exists(sample_path):
                with open(sample_path, "w", encoding="utf-8") as f:
                    f.write(
                        "Digital Mind Engineering (DME) Jordan - Standard Pricing & SLA 2026\n"
                        "Industrial Grade 6061-T6 aluminum valve component pricing is set at $24.50 per unit for bulk orders (>1000 units).\n"
                        "Delivery timeframe across MENA region: 15 business days standard, 7 business days expedited.\n"
                        "Preventive Maintenance Protocol: Industrial Motor Bearings require vibration threshold inspection (<4.8 mm/s peak) and quarterly grease application."
                    )
            await knowledge_engine.index_document(
                org_id=org_id,
                title="DME Operations & Pricing SOP 2026",
                file_name="dme_operations_manual.txt",
                file_path=sample_path,
                file_type="txt"
            )
            res2 = await session.execute(select(KnowledgeDocument).where(KnowledgeDocument.org_id == org_id))
            docs = res2.scalars().all()

        return [
            {
                "id": d.id,
                "title": d.title,
                "file_name": d.file_name,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "chunk_count": d.chunk_count,
                "status": d.status,
                "created_at": d.created_at.isoformat()
            }
            for d in docs
        ]

@router.post("/upload")
async def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user_context)
):
    org_id = user.get("org_id")
    file_ext = os.path.splitext(file.filename)[1].replace(".", "").lower()
    if file_ext not in ["pdf", "docx", "txt", "md", "csv"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Supported: PDF, DOCX, TXT, MD, CSV.")

    save_path = os.path.join(settings.UPLOADS_DIR, f"{org_id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc_id = await knowledge_engine.index_document(
        org_id=org_id,
        title=title,
        file_name=file.filename,
        file_path=save_path,
        file_type=file_ext
    )

    return {"document_id": doc_id, "title": title, "status": "INDEXED"}

@router.post("/search")
async def search_knowledge(req: SearchRequest, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    results = await knowledge_engine.search(org_id=org_id, query=req.query, top_k=req.top_k)
    return {"query": req.query, "results": results}

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, user: dict = Depends(get_current_user_context)):
    org_id = user.get("org_id")
    async with AsyncSessionLocal() as session:
        doc_res = await session.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id, KnowledgeDocument.org_id == org_id)
        )
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Delete associated chunks
        chunks_res = await session.execute(
            select(KnowledgeChunk).where(KnowledgeChunk.document_id == doc.id)
        )
        for ch in chunks_res.scalars().all():
            await session.delete(ch)

        await session.delete(doc)
        await session.commit()
        return {"id": doc_id, "deleted": True}
