import pytest
from app.modules.tools.schemas import ToolDefinition, PermissionLevel, ToolResult
from app.modules.tools.permissions import PermissionGuard
from app.modules.tools.registry import ToolRegistry
import app.modules.tools.files
import app.modules.tools.calculator
import app.modules.tools.git_tool

def test_permission_guard_allows_read_only():
    guard = PermissionGuard()
    tool_def = ToolDefinition(
        name="test_read",
        description="test",
        permission_level=PermissionLevel.READ_ONLY
    )
    is_allowed, reason = guard.evaluate(tool_def, {"filepath": "src/app/main.py"})
    assert is_allowed is True
    assert reason is None

def test_permission_guard_requires_confirmation_for_mutations():
    guard = PermissionGuard()
    tool_def = ToolDefinition(
        name="test_write",
        description="test",
        permission_level=PermissionLevel.CONFIRMATION_REQUIRED
    )
    is_allowed, reason = guard.evaluate(tool_def, {"filepath": "src/app/main.py", "content": "hello"})
    assert is_allowed is False
    assert "CONFIRMATION_REQUIRED" in reason

def test_permission_guard_blocks_path_traversal():
    guard = PermissionGuard()
    tool_def = ToolDefinition(
        name="test_read",
        description="test",
        permission_level=PermissionLevel.READ_ONLY
    )
    is_allowed, reason = guard.evaluate(tool_def, {"filepath": "../../etc/shadow"})
    assert is_allowed is False
    assert "Directory traversal" in reason

@pytest.mark.asyncio
async def test_tool_registry_execution_and_schema():
    reg = ToolRegistry()
    tool_def = ToolDefinition(
        name="echo",
        description="Echo input text",
        parameters={"type": "object", "properties": {"text": {"type": "string"}}},
        permission_level=PermissionLevel.READ_ONLY
    )
    reg.register(tool_def, lambda text: f"Echo: {text}")

    # Verify Ollama schema export
    schema = reg.to_ollama_format()
    assert len(schema) == 1
    assert schema[0]["function"]["name"] == "echo"

    # Execute
    result = await reg.execute("echo", {"text": "Project Sovereign"})
    assert result.success is True
    assert result.data == "Echo: Project Sovereign"
    assert result.requires_confirmation is False

@pytest.mark.asyncio
async def test_confirmation_required_tool_execution():
    reg = ToolRegistry()
    tool_def = ToolDefinition(
        name="delete_database",
        description="Destructive action",
        permission_level=PermissionLevel.CONFIRMATION_REQUIRED
    )
    reg.register(tool_def, lambda: "Deleted")

    result = await reg.execute("delete_database", {})
    assert result.success is False
    assert result.requires_confirmation is True
    assert "CONFIRMATION_REQUIRED" in result.confirmation_reason
