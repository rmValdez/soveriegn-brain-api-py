import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    tool_name = Column(String(100), nullable=False, index=True)
    permission_level = Column(String(50), nullable=False)
    arguments = Column(JSON, nullable=False, default=dict)
    
    # Status: pending_confirmation, approved, rejected, executed, failed, auto_approved
    status = Column(String(50), nullable=False, default="pending_confirmation", index=True)
    requires_confirmation = Column(Boolean, nullable=False, default=False)
    confirmation_reason = Column(Text, nullable=True)
    
    result_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    executed_by = Column(String(50), nullable=False, default="user")
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Relationships
    session = relationship("Session", backref="tool_executions", lazy="selectin")
