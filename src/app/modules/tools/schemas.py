from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Callable

class ToolDefinition(BaseModel):
    name: str = Field(..., description="Unique name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for parameters")

class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
