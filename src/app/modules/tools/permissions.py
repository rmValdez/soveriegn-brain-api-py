from typing import Tuple, Optional, Dict, Any, List
import os
from .schemas import ToolDefinition, PermissionLevel

class PermissionGuard:
    """
    Security boundary for Sovereign Brain Tool Execution.
    Ensures the LLM cannot authorize itself.
    Backend evaluation is the definitive authority.
    """

    def __init__(self, blocked_paths: Optional[List[str]] = None):
        self.blocked_paths = blocked_paths or [
            "/etc", "/root", "/proc", "/sys", "/dev",
            "C:\\Windows", "C:\\Program Files"
        ]

    def evaluate(self, tool_def: ToolDefinition, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Determines whether the requested tool invocation can execute immediately.
        Returns:
            (is_allowed, reason)
            - If allowed immediately: (True, None)
            - If requires user confirmation: (False, "CONFIRMATION_REQUIRED: <reason>")
            - If blocked for security violation: (False, "BLOCKED: <reason>")
        """
        # 1. Require explicit user confirmation for dangerous/mutating tools
        if tool_def.permission_level == PermissionLevel.CONFIRMATION_REQUIRED:
            return False, f"CONFIRMATION_REQUIRED: Execution of '{tool_def.name}' modifies system state and requires explicit approval."

        # 2. Path safety inspection for filesystem tools
        path_arg = arguments.get("filepath") or arguments.get("path") or arguments.get("directory")
        if path_arg and isinstance(path_arg, str):
            # Normalize path
            norm_path = os.path.normpath(path_arg)
            
            # Detect directory traversal attacks
            if ".." in path_arg.split("/") or ".." in path_arg.split("\\"):
                return False, f"BLOCKED: Directory traversal pattern detected in path: '{path_arg}'"

            # Detect root or sensitive system path access
            for blocked in self.blocked_paths:
                if norm_path.startswith(blocked):
                    return False, f"BLOCKED: Access to sensitive system path '{norm_path}' is denied."

        # 3. Read-only and low-risk tools are auto-approved
        return True, None
