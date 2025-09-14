#!/usr/bin/env python3
"""
Test script for official MCP server
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
    tools = await server.server._handlers["tools/list"]()
    print(f"   Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test resource listing
    print("\n2. Testing resource listing...")
    resources = await server.server._handlers["resources/list"]()
    print(f"   Found {len(resources)} resources:")
    for resource in resources:
        print(f"   - {resource.name}: {resource.description}")
    
    # Test prompt listing
    print("\n3. Testing prompt listing...")
    prompts = await server.server._handlers["prompts/list"]()
    print(f"   Found {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"   - {prompt.name}: {prompt.description}")
    
    # Test tool call
    print("\n4. Testing tool call...")
    try:
        result = await server.server._handlers["tools/call"](
            name="analyze_document",
            arguments={
                "document_content": "This is a test document for compliance analysis.",
                "document_name": "test_document.txt"
            }
        )
        print(f"   Tool call result: {result}")
    except Exception as e:
        print(f"   Tool call error: {e}")
    
    print("\n✅ Official MCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
