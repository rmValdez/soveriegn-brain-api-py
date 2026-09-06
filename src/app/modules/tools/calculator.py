from .schemas import ToolDefinition
from .registry import registry

calculator_definition = ToolDefinition(
    name="calculator",
    description="Evaluate a simple mathematical expression.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate (e.g. '2 + 2 * 3')"
            }
        },
        "required": ["expression"]
    }
)

def calculator_handler(expression: str) -> str:
    # A very basic, unsafe eval for scaffolding.
    # In a real app, use a safe math parser like ast.literal_eval or a specific math lib.
    try:
        # Restrict allowed characters to basic math for minimal safety
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# Register the tool
registry.register(calculator_definition, calculator_handler)
