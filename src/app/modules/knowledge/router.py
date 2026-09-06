from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from .schemas import DocumentCreate, DocumentResponse, SearchQuery, SearchResult
from .ingestion import KnowledgeIngestionService
from .retrieval import KnowledgeRetrievalService

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

def get_ingestion_service(db: AsyncSession = Depends(get_db)) -> KnowledgeIngestionService:
    return KnowledgeIngestionService(db)

def get_retrieval_service(db: AsyncSession = Depends(get_db)) -> KnowledgeRetrievalService:
    return KnowledgeRetrievalService(db)

@router.post("/ingest", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    doc: DocumentCreate,
    service: KnowledgeIngestionService = Depends(get_ingestion_service)
):
    return await service.ingest_document(doc)

@router.post("/search", response_model=List[SearchResult])
async def search_knowledge(
    query: SearchQuery,
    service: KnowledgeRetrievalService = Depends(get_retrieval_service)
):
    return await service.search(query.query, query.top_k)
