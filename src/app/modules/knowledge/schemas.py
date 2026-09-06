from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str
    content: str
    source: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    title: str
    source: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    document_id: str
    document_title: str
    chunk_content: str
    similarity: float
