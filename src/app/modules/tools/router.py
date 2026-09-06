from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from .schemas import ToolDefinition, ToolExecutionRequest, ToolResult
from .registry import registry

# Ensure all built-in tools are imported and registered
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
async def execute_tool(request: ToolExecutionRequest):
    """
    Execute a tool under Permission Guardrails.
    Returns ToolResult with execution output or indicates if user confirmation is required.
    """
    result = await registry.execute(name=request.tool_name, arguments=request.arguments)
    return result
