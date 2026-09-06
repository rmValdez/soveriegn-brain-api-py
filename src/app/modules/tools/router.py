from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from .schemas import (
    ToolDefinition,
    ToolExecutionRequest,
    ToolResult,
    PermissionLevel,
    ConfirmationDecisionRequest,
    ToolExecutionAuditItem,
    PendingConfirmationItem,
)
from .registry import registry
from .models import ToolExecution

# Ensure all built-in tools are registered
import app.modules.tools.files
import app.modules.tools.git_tool
import app.modules.tools.calculator
import app.modules.tools.web

router = APIRouter(prefix="/api/v1/tools", tags=["Tools"])


@router.get("", response_model=List[ToolDefinition])
async def list_tools():
    """List all registered tools available in Sovereign Brain."""
    return registry.get_all_definitions()


@router.get("/ollama-schema", response_model=List[Dict[str, Any]])
async def get_ollama_tools():
    """Export tool definitions formatted for Ollama / LLM function calling."""
    return registry.to_ollama_format()


@router.post("/execute", response_model=ToolResult)
async def execute_tool(
    request: ToolExecutionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a tool under Permission Guardrails.
    - If auto-approved (READ_ONLY or LOW_RISK), executes immediately and creates an audit record.
    - If CONFIRMATION_REQUIRED, gates execution, saves a pending confirmation record in the database,
      and returns requires_confirmation=True with an execution_id.
    """
    tool_def = registry.get(request.tool_name)
    if not tool_def:
        return ToolResult(
            success=False,
            tool_name=request.tool_name,
            permission_level=PermissionLevel.READ_ONLY,
            error=f"Tool '{request.tool_name}' is not registered in Sovereign Brain.",
            status="failed"
        )

    # If the tool requires confirmation, gate execution and record pending request
    if tool_def.permission_level == PermissionLevel.CONFIRMATION_REQUIRED:
        reason = f"CONFIRMATION_REQUIRED: Execution of '{tool_def.name}' modifies system state and requires explicit approval."
        audit_record = ToolExecution(
            session_id=request.session_id,
            tool_name=tool_def.name,
            permission_level=tool_def.permission_level.value,
            arguments=request.arguments,
            status="pending_confirmation",
            requires_confirmation=True,
            confirmation_reason=reason,
            executed_by=request.user_id,
        )
        db.add(audit_record)
        await db.commit()
        await db.refresh(audit_record)

        return ToolResult(
            success=False,
            tool_name=tool_def.name,
            permission_level=tool_def.permission_level,
            requires_confirmation=True,
            confirmation_reason=reason,
            execution_id=audit_record.id,
            status="pending_confirmation"
        )

    # Auto-approved execution (READ_ONLY or LOW_RISK)
    result = await registry.execute(name=request.tool_name, arguments=request.arguments)

    # Create audit record
    result_serializable = result.data if isinstance(result.data, (dict, list, str, int, float, bool)) else str(result.data) if result.data is not None else None
    audit_record = ToolExecution(
        session_id=request.session_id,
        tool_name=tool_def.name,
        permission_level=tool_def.permission_level.value,
        arguments=request.arguments,
        status=result.status or ("executed" if result.success else "failed"),
        requires_confirmation=False,
        result_data={"result": result_serializable} if result_serializable is not None else None,
        error=result.error,
        executed_by=request.user_id,
        resolved_at=datetime.now(timezone.utc),
        duration_ms=result.duration_ms
    )
    db.add(audit_record)
    await db.commit()
    await db.refresh(audit_record)

    result.execution_id = audit_record.id
    return result


@router.post("/confirmations/{execution_id}/approve", response_model=ToolResult)
async def approve_confirmation(
    execution_id: str,
    decision: ConfirmationDecisionRequest = ConfirmationDecisionRequest(approved=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a pending tool execution.
    Executes the gated tool with authorized clearance, records duration and outputs in the audit trail.
    """
    stmt = select(ToolExecution).where(ToolExecution.id == execution_id)
    exec_res = await db.execute(stmt)
    record = exec_res.scalars().first()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool execution '{execution_id}' not found.")

    if record.status != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool execution '{execution_id}' cannot be approved because its status is '{record.status}'."
        )

    # Execute with force_authorized=True (bypasses confirmation check while enforcing structural path safety)
    result = await registry.execute(
        name=record.tool_name,
        arguments=record.arguments,
        force_authorized=True
    )

    # Update audit record
    result_serializable = result.data if isinstance(result.data, (dict, list, str, int, float, bool)) else str(result.data) if result.data is not None else None
    record.status = "executed" if result.success else "failed"
    record.result_data = {"result": result_serializable} if result_serializable is not None else None
    record.error = result.error
    record.resolved_at = datetime.now(timezone.utc)
    record.duration_ms = result.duration_ms
    if decision.user_id:
        record.executed_by = decision.user_id

    await db.commit()
    await db.refresh(record)

    result.execution_id = record.id
    result.status = record.status
    return result


@router.post("/confirmations/{execution_id}/reject", response_model=ToolResult)
async def reject_confirmation(
    execution_id: str,
    decision: ConfirmationDecisionRequest = ConfirmationDecisionRequest(approved=False),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject and cancel a pending tool execution.
    Prevents execution and logs cancellation in the audit trail.
    """
    stmt = select(ToolExecution).where(ToolExecution.id == execution_id)
    exec_res = await db.execute(stmt)
    record = exec_res.scalars().first()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool execution '{execution_id}' not found.")

    if record.status != "pending_confirmation":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool execution '{execution_id}' cannot be rejected because its status is '{record.status}'."
        )

    rejection_msg = decision.reason or "Tool execution rejected by user."
    record.status = "rejected"
    record.error = rejection_msg
    record.resolved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)

    return ToolResult(
        success=False,
        tool_name=record.tool_name,
        permission_level=PermissionLevel(record.permission_level),
        error=rejection_msg,
        execution_id=record.id,
        status="rejected"
    )


@router.get("/confirmations/pending", response_model=List[PendingConfirmationItem])
async def get_pending_confirmations(
    session_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all tool executions waiting for human approval."""
    stmt = select(ToolExecution).where(ToolExecution.status == "pending_confirmation")
    if session_id:
        stmt = stmt.where(ToolExecution.session_id == session_id)
    stmt = stmt.order_by(desc(ToolExecution.created_at))

    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        PendingConfirmationItem(
            execution_id=r.id,
            session_id=r.session_id,
            tool_name=r.tool_name,
            arguments=r.arguments,
            reason=r.confirmation_reason,
            created_at=r.created_at
        )
        for r in records
    ]


@router.get("/audit", response_model=List[ToolExecutionAuditItem])
async def get_audit_trail(
    session_id: Optional[str] = Query(None),
    tool_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the tool execution audit trail."""
    stmt = select(ToolExecution)
    if session_id:
        stmt = stmt.where(ToolExecution.session_id == session_id)
    if tool_name:
        stmt = stmt.where(ToolExecution.tool_name == tool_name)
    if status_filter:
        stmt = stmt.where(ToolExecution.status == status_filter)

    stmt = stmt.order_by(desc(ToolExecution.created_at)).limit(limit)
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        ToolExecutionAuditItem(
            id=r.id,
            session_id=r.session_id,
            tool_name=r.tool_name,
            permission_level=r.permission_level,
            arguments=r.arguments,
            status=r.status,
            requires_confirmation=r.requires_confirmation,
            confirmation_reason=r.confirmation_reason,
            result_data=r.result_data,
            error=r.error,
            executed_by=r.executed_by,
            created_at=r.created_at,
            resolved_at=r.resolved_at,
            duration_ms=r.duration_ms
        )
        for r in records
    ]
