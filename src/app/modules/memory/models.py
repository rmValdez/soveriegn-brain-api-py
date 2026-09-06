from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, DateTime, Enum, Text, Float, ForeignKey
from pgvector.sqlalchemy import Vector
from app.core.database import Base
import enum

class MemoryType(str, enum.Enum):
    preference = "preference"
    goal = "goal"
    project = "project"
    context = "context"
    fact = "fact"
    decision = "decision"

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), index=True, nullable=False, default="default_user")
    type = Column(Enum(MemoryType), index=True, nullable=False, default=MemoryType.fact)
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    importance = Column(String(20), default="medium") # low, medium, high, critical
    confidence = Column(Float, default=1.0)
    source_session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    embedding = Column(Vector(768), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
