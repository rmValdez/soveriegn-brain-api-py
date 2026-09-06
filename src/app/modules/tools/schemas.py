import enum
from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class PermissionLevel(str, enum.Enum):
    READ_ONLY = "read_only"                          # Auto-approved: safe read operations (file inspect, git status, search)
    LOW_RISK = "low_risk"                            # Auto-approved: safe generation / sandboxed scratchpad
    CONFIRMATION_REQUIRED = "confirmation_required"  # Requires explicit human approval (writes, deletes, git pushes, DB ops)

class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique identifier of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of arguments")
    permission_level: PermissionLevel = Field(default=PermissionLevel.READ_ONLY)

class ToolExecutionRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: str = "default_user"

class ToolResult(BaseModel):
    success: bool
    tool_name: str
    permission_level: PermissionLevel
    data: Optional[Any] = None
    error: Optional[str] = None
    requires_confirmation: bool = False
    confirmation_reason: Optional[str] = None
    execution_id: Optional[str] = None
    status: Optional[str] = None
    duration_ms: Optional[int] = None

class ConfirmationDecisionRequest(BaseModel):
    approved: bool = Field(default=True, description="Whether to approve or reject the tool execution")
    reason: Optional[str] = Field(default=None, description="Optional explanation for rejection or audit notes")
    user_id: Optional[str] = Field(default=None, description="Identifier of the user making this decision, for audit attribution")

class ToolExecutionAuditItem(BaseModel):
    id: str
    session_id: Optional[str] = None
    tool_name: str
    permission_level: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: str
    requires_confirmation: bool
    confirmation_reason: Optional[str] = None
    result_data: Optional[Any] = None
    error: Optional[str] = None
    executed_by: str = "user"
    created_at: datetime
    resolved_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

class PendingConfirmationItem(BaseModel):
    execution_id: str
    session_id: Optional[str] = None
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None
    created_at: datetime
