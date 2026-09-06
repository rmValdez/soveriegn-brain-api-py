import inspect
from typing import Dict, Callable, Any, List, Optional
from .schemas import ToolDefinition, ToolResult, PermissionLevel
from .permissions import PermissionGuard

class ToolRegistry:
    """
    Centralized tool registry for Sovereign Brain.
    Manages tool discovery, metadata export for model dispatch,
    and secure permission-guarded execution.
    """

    def __init__(self, guard: Optional[PermissionGuard] = None):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}
        self.guard = guard or PermissionGuard()

    def register(self, definition: ToolDefinition, handler: Callable[..., Any]):
        """Register a new tool and its execution handler."""
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve tool metadata by name."""
        return self._tools.get(name)

    def get_all_definitions(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def to_ollama_format(self) -> List[Dict[str, Any]]:
        """
        Export all registered tools in the standard function schema
        supported by Ollama and OpenAI-compatible tool calling.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": f"[{tool.permission_level.value.upper()}] {tool.description}",
                    "parameters": tool.parameters
                }
            }
            for tool in self._tools.values()
        ]

    async def execute(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        custom_guard: Optional[PermissionGuard] = None,
        force_authorized: bool = False
    ) -> ToolResult:
        """
        Execute a registered tool under permission guard enforcement.
        If force_authorized is True (e.g. from human approval), the CONFIRMATION_REQUIRED
        check is bypassed while keeping structural security checks (e.g. directory traversal).
        """
        import time
        start_time = time.perf_counter()
        args = arguments or {}

        if name not in self._tools or name not in self._handlers:
            return ToolResult(
                success=False,
                tool_name=name,
                permission_level=PermissionLevel.READ_ONLY,
                error=f"Tool '{name}' is not registered in Sovereign Brain."
            )

        tool_def = self._tools[name]
        active_guard = custom_guard or self.guard

        # Evaluate execution safety through PermissionGuard
        is_allowed, reason = active_guard.evaluate(tool_def, args, force_authorized=force_authorized)

        if not is_allowed:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            if reason and reason.startswith("CONFIRMATION_REQUIRED"):
                return ToolResult(
                    success=False,
                    tool_name=name,
                    permission_level=tool_def.permission_level,
                    requires_confirmation=True,
                    confirmation_reason=reason,
                    status="pending_confirmation",
                    duration_ms=elapsed_ms
                )
            else:
                return ToolResult(
                    success=False,
                    tool_name=name,
                    permission_level=tool_def.permission_level,
                    error=reason or "Tool execution rejected by security policy.",
                    status="blocked",
                    duration_ms=elapsed_ms
                )

        # Authorized to execute
        try:
            handler = self._handlers[name]
            if inspect.iscoroutinefunction(handler):
                result = await handler(**args)
            else:
                result = handler(**args)

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                success=True,
                tool_name=name,
                permission_level=tool_def.permission_level,
                data=result,
                status="executed",
                duration_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return ToolResult(
                success=False,
                tool_name=name,
                permission_level=tool_def.permission_level,
                error=f"Runtime error during '{name}' execution: {str(e)}",
                status="failed",
                duration_ms=elapsed_ms
            )

# Global registry instance
registry = ToolRegistry()
