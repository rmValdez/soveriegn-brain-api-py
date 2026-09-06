import enum
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
