import logging
import subprocess
from .schemas import ToolDefinition, PermissionLevel
from .registry import registry

logger = logging.getLogger(__name__)

git_status_definition = ToolDefinition(
    name="git_status",
    description="Inspect the current working tree and staged status of the Git repository.",
    parameters={
        "type": "object",
        "properties": {}
    },
    permission_level=PermissionLevel.READ_ONLY
)

async def git_status_handler() -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout.strip()
        return output if output else "Working tree clean. No changes."
    except Exception as e:
        logger.exception("git_status tool failed")
        return f"Error executing git status: {str(e)}"

git_log_definition = ToolDefinition(
    name="git_log",
    description="Inspect recent commit history in the Git repository.",
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Maximum number of commits to retrieve (default: 5)",
                "default": 5
            }
        }
    },
    permission_level=PermissionLevel.READ_ONLY
)

async def git_log_handler(limit: int = 5) -> str:
    try:
        result = subprocess.run(
            ["git", "log", f"-n{limit}", "--oneline"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.exception("git_log tool failed")
        return f"Error executing git log: {str(e)}"

# Register git tools
registry.register(git_status_definition, git_status_handler)
registry.register(git_log_definition, git_log_handler)
