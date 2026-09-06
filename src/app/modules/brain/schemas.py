from typing import Literal, Optional
from pydantic import BaseModel

class BrainDecision(BaseModel):
    action: Literal[
        "answer",
        "tool",
        "memory_search",
        "knowledge_search",
        "plan",
    ]
    tool_name: Optional[str] = None
    requires_confirmation: bool = False
