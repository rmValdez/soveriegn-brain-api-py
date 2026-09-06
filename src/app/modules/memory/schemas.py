from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from .models import MemoryType

class MemoryBase(BaseModel):
    user_id: str
    type: MemoryType
    content: str

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    type: Optional[MemoryType] = None
    content: Optional[str] = None

class MemoryResponse(MemoryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
