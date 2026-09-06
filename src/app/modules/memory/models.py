from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Enum, Text
from app.core.database import Base
import enum

class MemoryType(str, enum.Enum):
    preference = "preference"
    goal = "goal"
    project = "project"
    context = "context"
    fact = "fact"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), index=True, nullable=False)
    type = Column(Enum(MemoryType), index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
