from .schemas import ToolDefinition
from .registry import registry
import os

file_read_definition = ToolDefinition(
    name="read_file",
    description="Read the contents of a local file.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "The absolute or relative path to the file"
            }
        },
        "required": ["filepath"]
    }
)

async def file_read_handler(filepath: str) -> str:
    # Scaffold implementation
    # In a real app, restrict directory access for security!
    try:
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Register the tool
registry.register(file_read_definition, file_read_handler)
