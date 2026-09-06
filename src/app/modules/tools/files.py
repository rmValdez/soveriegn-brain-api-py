import os
from typing import Dict, Any, List
from .schemas import ToolDefinition, PermissionLevel
from .registry import registry

# --- 1. read_file ---
read_file_definition = ToolDefinition(
    name="read_file",
    description="Read the contents of a text file with safety limits.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Relative or absolute path of the file to inspect"
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to return (default: 200)",
                "default": 200
            }
        },
        "required": ["filepath"]
    },
    permission_level=PermissionLevel.READ_ONLY
)

async def read_file_handler(filepath: str, max_lines: int = 200) -> str:
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        if os.path.isdir(filepath):
            return f"Error: '{filepath}' is a directory, not a file."

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            content = "".join(lines)
            if f.readline():
                content += f"\n... [Truncated after {max_lines} lines]"
            return content
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"

# --- 2. list_directory ---
list_dir_definition = ToolDefinition(
    name="list_directory",
    description="List files and directories within a given directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to inspect (defaults to current directory)",
                "default": "."
            }
        }
    },
    permission_level=PermissionLevel.READ_ONLY
)

async def list_dir_handler(path: str = ".") -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(path):
            return [{"error": f"Path '{path}' does not exist"}]
        if not os.path.isdir(path):
            return [{"error": f"Path '{path}' is not a directory"}]

        entries = []
        for entry in os.scandir(path):
            entries.append({
                "name": entry.name,
                "is_dir": entry.is_dir(),
                "size_bytes": entry.stat().st_size if entry.is_file() else None
            })
        return sorted(entries, key=lambda x: (not x["is_dir"], x["name"]))
    except Exception as e:
        return [{"error": f"Error listing directory '{path}': {str(e)}"}]

# --- 3. write_file (Dangerous - Confirmation Required) ---
write_file_definition = ToolDefinition(
    name="write_file",
    description="Write or overwrite content into a local file. Requires explicit user confirmation.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Target file path to write"
            },
            "content": {
                "type": "string",
                "description": "Text content to write into the file"
            }
        },
        "required": ["filepath", "content"]
    },
    permission_level=PermissionLevel.CONFIRMATION_REQUIRED
)

async def write_file_handler(filepath: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{filepath}'."
    except Exception as e:
        return f"Error writing file '{filepath}': {str(e)}"

# Register all file tools
registry.register(read_file_definition, read_file_handler)
registry.register(list_dir_definition, list_dir_handler)
registry.register(write_file_definition, write_file_handler)
