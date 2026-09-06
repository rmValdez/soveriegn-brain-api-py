from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BrainDecision(BaseModel):
    action: str = Field(..., description="Action to take: 'answer', 'tool', 'memory_search', 'plan'")
    reasoning: str = Field(..., description="Why this decision was made")
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    search_query: Optional[str] = None

# Scaffold for structured output parsing
def parse_decision_from_llm(llm_output: str) -> BrainDecision:
    lower = llm_output.lower()
    
    # Check for mutating file tools requiring confirmation
    if "write file" in lower or "save file" in lower or "create file" in lower:
        return BrainDecision(
            action="tool",
            reasoning="File creation or modification requested",
            tool_name="write_file",
            tool_args={"filepath": "sandbox_output.txt", "content": "Sample content from Sovereign Brain."}
        )
        
    if "calculate" in lower:
        return BrainDecision(
            action="tool",
            reasoning="Need calculation",
            tool_name="calculator",
            tool_args={"expression": llm_output}
        )
    
    return BrainDecision(action="answer", reasoning="Direct response sufficient")
