"""
Base tool class for OuiComply MCP Server tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from mcp.types import TextContent


class BaseTool(ABC):
    """
    Base class for all MCP tools in the OuiComply server.
    
    All tools should inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Return the JSON schema for this tool's input parameters.
        
        Returns:
            Dict containing the JSON schema for tool inputs
        """
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Execute the tool with the given arguments.
        
        Args:
            arguments: Dictionary of input arguments
            
        Returns:
            List of TextContent responses
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """
        Validate the input arguments against the tool's schema.
        
        Args:
            arguments: Dictionary of input arguments
            
        Returns:
            True if arguments are valid, False otherwise
        """
        # Basic validation - can be extended with jsonschema validation
        schema = self.get_schema()
        required_fields = schema.get("required", [])
        
        for field in required_fields:
            if field not in arguments:
                return False
        
        return True


class PlaceholderTool(BaseTool):
    """
    Placeholder tool implementation for demonstration purposes.
    Replace this with actual tool implementations.
    """
    
    def __init__(self):
        super().__init__(
            name="placeholder_tool",
            description="A placeholder tool for demonstration"
        )
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input_text": {
                    "type": "string",
                    "description": "Input text to process"
                }
            },
            "required": ["input_text"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        input_text = arguments.get("input_text", "")
        
        result = f"""
        Placeholder Tool Result:
        
        Input: {input_text}
        
        This is a placeholder implementation. Replace with actual tool logic.
        """
        
        return [TextContent(type="text", text=result)]
