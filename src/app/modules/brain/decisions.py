from pydantic import BaseModel, Field
from typing import Optional, List

class BrainDecision(BaseModel):
    action: str = Field(..., description="Action to take: 'answer', 'tool', 'memory_search', 'plan'")
    reasoning: str = Field(..., description="Why this decision was made")
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
    search_query: Optional[str] = None

# Scaffold for structured output parsing
def parse_decision_from_llm(llm_output: str) -> BrainDecision:
    # In a real app, this would use Ollama's structured output format or parse JSON
    # Scaffold: always default to simple answer unless there's a specific trigger word
    if "calculate" in llm_output.lower():
        return BrainDecision(action="tool", reasoning="Need calculation", tool_name="calculator", tool_args={"expression": llm_output})
    
    return BrainDecision(action="answer", reasoning="Direct response sufficient")
