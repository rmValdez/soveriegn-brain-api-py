from app.modules.tools.registry import registry
from .decisions import BrainDecision

class PlannerService:
    async def execute_plan(self, decision: BrainDecision) -> str:
        if decision.action == "tool":
            if decision.tool_name:
                result = await registry.execute(decision.tool_name, **(decision.tool_args or {}))
                return f"Tool result: {result.data if result.success else result.error}"
            return "Error: Tool name not provided."
        
        elif decision.action == "memory_search":
            return "Scaffold: Memory search not fully implemented."
            
        elif decision.action == "plan":
            return "Scaffold: Multi-step plan not fully implemented."
            
        return "I don't know how to handle this action yet."
