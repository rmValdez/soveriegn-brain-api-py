import json
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tools.registry import registry
from app.modules.tools.schemas import PermissionLevel
from app.modules.tools.models import ToolExecution
from .decisions import BrainDecision

class PlannerService:
    async def execute_plan(
        self,
        decision: BrainDecision,
        db: Optional[AsyncSession] = None,
        session_id: Optional[str] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Executes a planned action.
        Returns:
            (display_text, confirmation_payload_or_none)
        """
        if decision.action == "tool":
            if not decision.tool_name:
                return "Error: Tool name not provided.", None

            tool_def = registry.get(decision.tool_name)
            args = decision.tool_args or {}

            # Check if this tool requires human confirmation
            if tool_def and tool_def.permission_level == PermissionLevel.CONFIRMATION_REQUIRED:
                reason = f"CONFIRMATION_REQUIRED: Execution of '{tool_def.name}' modifies system state and requires explicit approval."
                execution_id = None
                if db:
                    audit_record = ToolExecution(
                        session_id=session_id,
                        tool_name=tool_def.name,
                        permission_level=tool_def.permission_level.value,
                        arguments=args,
                        status="pending_confirmation",
                        requires_confirmation=True,
                        confirmation_reason=reason,
                        executed_by="user",
                    )
                    db.add(audit_record)
                    await db.commit()
                    await db.refresh(audit_record)
                    execution_id = audit_record.id

                confirmation_payload = {
                    "type": "confirmation_required",
                    "execution_id": execution_id or "pending",
                    "tool_name": tool_def.name,
                    "arguments": args,
                    "reason": reason
                }
                display_msg = f"⚠️ Confirmation Required: Sovereign Brain requested to execute '{tool_def.name}'. Please approve or reject this action."
                return display_msg, confirmation_payload

            # Auto-approved execution (READ_ONLY or LOW_RISK)
            result = await registry.execute(decision.tool_name, arguments=args)
            if db:
                result_serializable = result.data if isinstance(result.data, (dict, list, str, int, float, bool)) else str(result.data) if result.data is not None else None
                audit_record = ToolExecution(
                    session_id=session_id,
                    tool_name=decision.tool_name,
                    permission_level=tool_def.permission_level.value if tool_def else "read_only",
                    arguments=args,
                    status=result.status or ("executed" if result.success else "failed"),
                    requires_confirmation=False,
                    result_data={"result": result_serializable} if result_serializable is not None else None,
                    error=result.error,
                    executed_by="user",
                    resolved_at=datetime.now(timezone.utc),
                    duration_ms=result.duration_ms
                )
                db.add(audit_record)
                await db.commit()

            return f"Tool result: {result.data if result.success else result.error}", None

        elif decision.action == "memory_search":
            return "Scaffold: Memory search not fully implemented.", None

        elif decision.action == "plan":
            return "Scaffold: Multi-step plan not fully implemented.", None

        return "I don't know how to handle this action yet.", None
