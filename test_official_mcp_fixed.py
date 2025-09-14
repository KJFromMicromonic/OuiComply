#!/usr/bin/env python3
"""
Test script for official MCP server - Fixed version
"""

import asyncio
import json
from mcp_server_official import OuiComplyMCPServer

async def test_mcp_server():
    """Test the official MCP server."""
    print("🧪 Testing Official MCP Server...")
    print("=" * 50)
    
    server = OuiComplyMCPServer()
    
    # Test tool listing
    print("\n1. Testing tool listing...")
    try:
        # Create a mock request for tools list
        from mcp.types import ListToolsRequest
        request = ListToolsRequest()
        tools = await server.server._list_tools(request)
        print(f"   Found {len(tools.tools)} tools:")
        for tool in tools.tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"   Error testing tools: {e}")
    
    # Test resource listing
    print("\n2. Testing resource listing...")
    try:
        from mcp.types import ListResourcesRequest
        request = ListResourcesRequest()
        resources = await server.server._list_resources(request)
        print(f"   Found {len(resources.resources)} resources:")
        for resource in resources.resources:
            print(f"   - {resource.name}: {resource.description}")
    except Exception as e:
        print(f"   Error testing resources: {e}")
    
    # Test prompt listing
    print("\n3. Testing prompt listing...")
    try:
        from mcp.types import ListPromptsRequest
        request = ListPromptsRequest()
        prompts = await server.server._list_prompts(request)
        print(f"   Found {len(prompts.prompts)} prompts:")
        for prompt in prompts.prompts:
            print(f"   - {prompt.name}: {prompt.description}")
    except Exception as e:
        print(f"   Error testing prompts: {e}")
    
    # Test tool calling
    print("\n4. Testing tool calling...")
    try:
        from mcp.types import CallToolRequest
        request = CallToolRequest(
            name="analyze_document",
            arguments={
                "document_content": "This is a test contract for compliance analysis.",
                "document_type": "contract",
                "frameworks": ["gdpr", "sox"]
            }
        )
        result = await server.server._call_tool(request)
        print(f"   Tool call successful!")
        print(f"   Result type: {type(result.content)}")
        if hasattr(result, 'content') and result.content:
            print(f"   Content preview: {str(result.content[0])[:100]}...")
    except Exception as e:
        print(f"   Error testing tool call: {e}")
    
    print("\n✅ Official MCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
