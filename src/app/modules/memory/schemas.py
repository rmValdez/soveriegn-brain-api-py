from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from .models import MemoryType

class MemoryBase(BaseModel):
    user_id: str = "default_user"
    type: MemoryType = MemoryType.fact
    subject: Optional[str] = None
    content: str
    importance: str = "medium" # low, medium, high, critical
    confidence: float = 1.0
    source_session_id: Optional[str] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    type: Optional[MemoryType] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    importance: Optional[str] = None
    confidence: Optional[float] = None

class MemoryResponse(MemoryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MemorySearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = "default_user"
    type: Optional[MemoryType] = None
    limit: int = 5
