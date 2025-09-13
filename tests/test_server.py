"""
Tests for the OuiComply MCP Server.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import MCPConfig, validate_config
from src.tools.base import BaseTool, PlaceholderTool
from src.resources.base import BaseResource, PlaceholderResource


class TestMCPConfig:
    """Test configuration management."""
    
    def test_config_creation(self):
        """Test creating a config with default values."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}):
            config = MCPConfig()
            assert config.mistral_api_key == 'test_key'
            assert config.server_name == 'ouicomply-mcp'
            assert config.server_version == '0.1.0'
    
    def test_config_validation_success(self):
        """Test successful config validation."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'valid_key'}):
            assert validate_config() is True
    
    def test_config_validation_failure(self):
        """Test config validation failure."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'your_mistral_api_key_here'}, clear=True):
            # Create a new config instance to test validation
            test_config = MCPConfig()
            # Temporarily replace the global config for validation
            with patch('src.config.config', test_config):
                assert validate_config() is False


class TestBaseTool:
    """Test base tool functionality."""
    
    def test_placeholder_tool_creation(self):
        """Test creating a placeholder tool."""
        tool = PlaceholderTool()
        assert tool.name == "placeholder_tool"
        assert tool.description == "A placeholder tool for demonstration"
    
    def test_tool_schema(self):
        """Test tool schema generation."""
        tool = PlaceholderTool()
        schema = tool.get_schema()
        assert schema["type"] == "object"
        assert "input_text" in schema["properties"]
        assert "input_text" in schema["required"]
    
    def test_argument_validation(self):
        """Test argument validation."""
        tool = PlaceholderTool()
        
        # Valid arguments
        valid_args = {"input_text": "test"}
        assert tool.validate_arguments(valid_args) is True
        
        # Invalid arguments (missing required field)
        invalid_args = {}
        assert tool.validate_arguments(invalid_args) is False
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution."""
        tool = PlaceholderTool()
        arguments = {"input_text": "test input"}
        
        result = await tool.execute(arguments)
        assert len(result) == 1
        assert result[0].type == "text"
        assert "test input" in result[0].text


class TestBaseResource:
    """Test base resource functionality."""
    
    def test_placeholder_resource_creation(self):
        """Test creating a placeholder resource."""
        resource = PlaceholderResource()
        assert resource.uri == "resource://placeholder"
        assert resource.name == "Placeholder Resource"
        assert resource.mime_type == "application/json"
    
    def test_resource_to_mcp_resource(self):
        """Test converting to MCP Resource object."""
        resource = PlaceholderResource()
        mcp_resource = resource.to_resource()
        
        assert str(mcp_resource.uri) == resource.uri
        assert mcp_resource.name == resource.name
        assert mcp_resource.description == resource.description
        assert mcp_resource.mimeType == resource.mime_type
    
    def test_uri_validation(self):
        """Test URI validation."""
        resource = PlaceholderResource()
        
        # Valid URI
        assert resource.validate_uri("resource://placeholder") is True
        
        # Invalid URI
        assert resource.validate_uri("resource://other") is False
    
    @pytest.mark.asyncio
    async def test_resource_read(self):
        """Test resource reading."""
        resource = PlaceholderResource()
        content = await resource.read()
        
        assert isinstance(content, str)
        assert "placeholder" in content.lower()


class TestOuiComplyMCPServer:
    """Test the main MCP server."""
    
    def test_server_creation(self):
        """Test creating the MCP server."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            # Create a new config instance for testing
            test_config = MCPConfig()
            with patch('src.mcp_server.get_config', return_value=test_config):
                server = OuiComplyMCPServer()
                assert server.config.mistral_api_key == 'test_key'
                assert server.server is not None
    
    @pytest.mark.asyncio
    async def test_list_resources(self):
        """Test listing resources."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "resources/list" in handlers:
                handler = handlers["resources/list"]
                resources = await handler()
                assert len(resources) >= 2
                assert any(r.name == "Legal Document Templates" for r in resources)
                assert any(r.name == "Compliance Frameworks" for r in resources)
    
    @pytest.mark.asyncio
    async def test_read_resource(self):
        """Test reading a resource."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "resources/read" in handlers:
                handler = handlers["resources/read"]
                content = await handler("resource://legal-templates")
                assert isinstance(content, str)
                assert "templates" in content
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test listing tools."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "tools/list" in handlers:
                handler = handlers["tools/list"]
                tools = await handler()
                assert len(tools) >= 3
                tool_names = [t.name for t in tools]
                assert "analyze_document" in tool_names
                assert "check_clause_presence" in tool_names
                assert "risk_assessment" in tool_names
    
    @pytest.mark.asyncio
    async def test_call_tool_analyze_document(self):
        """Test calling the analyze_document tool."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "tools/call" in handlers:
                handler = handlers["tools/call"]
                arguments = {
                    "document_text": "Sample document text",
                    "compliance_framework": "gdpr"
                }
                result = await handler("analyze_document", arguments)
                
                assert len(result) == 1
                assert result[0].type == "text"
                assert "GDPR" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_check_clause_presence(self):
        """Test calling the check_clause_presence tool."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "tools/call" in handlers:
                handler = handlers["tools/call"]
                arguments = {
                    "document_text": "Sample contract text",
                    "required_clauses": ["termination", "liability"]
                }
                result = await handler("check_clause_presence", arguments)
                
                assert len(result) == 1
                assert result[0].type == "text"
                assert "Clause Presence Check" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_risk_assessment(self):
        """Test calling the risk_assessment tool."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "tools/call" in handlers:
                handler = handlers["tools/call"]
                arguments = {
                    "document_text": "Sample agreement text",
                    "document_type": "contract"
                }
                result = await handler("risk_assessment", arguments)
                
                assert len(result) == 1
                assert result[0].type == "text"
                assert "Risk Assessment Report" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_unknown_tool(self):
        """Test calling an unknown tool."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'test_key'}, clear=True):
            server = OuiComplyMCPServer()
            
            # Test the handler directly through the server's registered handlers
            handlers = server.server.request_handlers
            if "tools/call" in handlers:
                handler = handlers["tools/call"]
                with pytest.raises(ValueError, match="Unknown tool"):
                    await handler("unknown_tool", {})


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_server_startup_with_valid_config(self):
        """Test server startup with valid configuration."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'valid_test_key'}, clear=True):
            # Create a new config instance for testing
            test_config = MCPConfig()
            with patch('src.mcp_server.get_config', return_value=test_config):
                server = OuiComplyMCPServer()
                # Test that server can be created without errors
                assert server is not None
                assert server.config.mistral_api_key == 'valid_test_key'
    
    def test_server_startup_with_invalid_config(self):
        """Test server startup with invalid configuration."""
        with patch.dict('os.environ', {'MISTRAL_KEY': 'your_mistral_api_key_here'}, clear=True):
            # Create a new config instance for testing
            test_config = MCPConfig()
            with patch('src.mcp_server.get_config', return_value=test_config):
                # This should not raise an exception during creation
                server = OuiComplyMCPServer()
                assert server is not None
                # But validation should fail
                with patch('src.config.config', test_config):
                    assert validate_config() is False


if __name__ == "__main__":
    pytest.main([__file__])
