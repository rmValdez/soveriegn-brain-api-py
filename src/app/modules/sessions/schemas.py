from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    role: str
    content: str

class MessageRead(MessageBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    title: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []

    class Config:
        from_attributes = True

class SessionListRead(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
