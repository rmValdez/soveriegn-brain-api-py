from typing import Dict, Callable, Any
from .schemas import ToolDefinition, ToolResult

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def register(self, definition: ToolDefinition, handler: Callable[..., Any]):
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_all_definitions(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    async def execute(self, name: str, **kwargs) -> ToolResult:
        if name not in self._handlers:
            return ToolResult(success=False, error=f"Tool '{name}' not found")
        
        try:
            handler = self._handlers[name]
            # If handler is an async function, await it. Otherwise call synchronously.
            import inspect
            if inspect.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
                result = handler(**kwargs)
                
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

# Global registry instance
registry = ToolRegistry()
