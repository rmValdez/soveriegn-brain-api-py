import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from app.modules.tools.schemas import (
    ToolDefinition,
    PermissionLevel,
    ToolResult,
    ToolExecutionRequest,
    ConfirmationDecisionRequest
)
from app.modules.tools.permissions import PermissionGuard
from app.modules.tools.registry import ToolRegistry
from app.modules.tools.models import ToolExecution
from app.modules.brain.planner import PlannerService
from app.modules.brain.decisions import BrainDecision

def test_permission_guard_force_authorized():
    guard = PermissionGuard()
    tool_def = ToolDefinition(
        name="write_file",
        description="Write content to a file",
        permission_level=PermissionLevel.CONFIRMATION_REQUIRED
    )
    
    # Without authorization -> requires confirmation
    is_allowed, reason = guard.evaluate(tool_def, {"filepath": "safe.txt", "content": "hello"}, force_authorized=False)
    assert is_allowed is False
    assert "CONFIRMATION_REQUIRED" in reason

    # With authorization -> allowed immediately
    is_allowed_forced, reason_forced = guard.evaluate(tool_def, {"filepath": "safe.txt", "content": "hello"}, force_authorized=True)
    assert is_allowed_forced is True
    assert reason_forced is None

    # With authorization but dangerous directory traversal -> still blocked!
    is_allowed_traversal, reason_traversal = guard.evaluate(tool_def, {"filepath": "../../etc/shadow", "content": "bad"}, force_authorized=True)
    assert is_allowed_traversal is False
    assert "Directory traversal" in reason_traversal

@pytest.mark.asyncio
async def test_tool_registry_force_authorized_execution():
    reg = ToolRegistry()
    tool_def = ToolDefinition(
        name="dangerous_action",
        description="A mutating action",
        permission_level=PermissionLevel.CONFIRMATION_REQUIRED
    )
    reg.register(tool_def, lambda: "Mutation Completed")

    # Initial execution blocked by confirmation requirement
    res = await reg.execute("dangerous_action", {})
    assert res.success is False
    assert res.requires_confirmation is True
    assert res.status == "pending_confirmation"

    # Authorized execution succeeds
    res_auth = await reg.execute("dangerous_action", {}, force_authorized=True)
    assert res_auth.success is True
    assert res_auth.data == "Mutation Completed"
    assert res_auth.status == "executed"
    assert res_auth.duration_ms is not None

@pytest.mark.asyncio
async def test_planner_creates_confirmation_payload_and_persists_pending():
    planner = PlannerService()
    decision = BrainDecision(
        action="tool",
        reasoning="Test file write",
        tool_name="write_file",
        tool_args={"filepath": "test.txt", "content": "hello"}
    )
    
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    display_msg, confirmation = await planner.execute_plan(decision, db=mock_db, session_id="sess-123")
    
    assert "Confirmation Required" in display_msg
    assert confirmation is not None
    assert confirmation["type"] == "confirmation_required"
    assert confirmation["tool_name"] == "write_file"
    assert confirmation["arguments"]["filepath"] == "test.txt"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
