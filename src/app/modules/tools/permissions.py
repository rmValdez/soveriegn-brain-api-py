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
            "/etc", "/root", "/proc", "/sys", "/dev", "/home",
            "C:\\Windows", "C:\\Program Files"
        ]
        # Deliberately NOT blocking "C:\Users" wholesale - on Windows dev
        # machines the project itself typically lives under there, so that
        # would block ordinary relative-path access to the project's own
        # files. The .env basename check below covers the concrete risk
        # (this project's own secrets file) without that collateral damage.
        # Blocked regardless of directory - a bare relative path like ".env"
        # would otherwise slip past the directory blocklist entirely.
        self.blocked_basename_prefixes = (".env",)

    def evaluate(
        self,
        tool_def: ToolDefinition,
        arguments: Dict[str, Any],
        force_authorized: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines whether the requested tool invocation can execute immediately.
        Returns:
            (is_allowed, reason)
            - If allowed immediately: (True, None)
            - If requires user confirmation: (False, "CONFIRMATION_REQUIRED: <reason>")
            - If blocked for security violation: (False, "BLOCKED: <reason>")
        """
        # 1. Require explicit user confirmation for dangerous/mutating tools (unless human approved)
        if tool_def.permission_level == PermissionLevel.CONFIRMATION_REQUIRED and not force_authorized:
            return False, f"CONFIRMATION_REQUIRED: Execution of '{tool_def.name}' modifies system state and requires explicit approval."

        # 2. Path safety inspection for filesystem tools
        path_arg = arguments.get("filepath") or arguments.get("path") or arguments.get("directory")
        if path_arg and isinstance(path_arg, str):
            # Normalize path
            norm_path = os.path.normpath(path_arg)

            # Detect directory traversal attacks
            if ".." in path_arg.split("/") or ".." in path_arg.split("\\"):
                return False, f"BLOCKED: Directory traversal pattern detected in path: '{path_arg}'"

            # Block env/secret files by name regardless of directory - a bare
            # relative path like ".env" has no ".." and no system-path prefix,
            # so it would otherwise pass through untouched.
            basename = os.path.basename(norm_path)
            if basename.startswith(self.blocked_basename_prefixes):
                return False, f"BLOCKED: Access to environment/secret file '{norm_path}' is denied."

            # Detect root or sensitive system path access. Resolve to an
            # absolute path first - a relative path can still land inside a
            # blocked directory depending on the process's working directory.
            abs_path = os.path.abspath(norm_path)
            for blocked in self.blocked_paths:
                if abs_path.startswith(blocked) or norm_path.startswith(blocked):
                    return False, f"BLOCKED: Access to sensitive system path '{norm_path}' is denied."

        # 3. Read-only and low-risk tools are auto-approved
        return True, None
