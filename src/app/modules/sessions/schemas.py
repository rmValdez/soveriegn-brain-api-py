from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class MessageBase(BaseModel):
    role: str
    content: str

class MessageRead(MessageBase):
    id: str
    session_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    title: Optional[str] = None
    user_id: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionRead(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = []

    model_config = ConfigDict(from_attributes=True)

class SessionListRead(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
