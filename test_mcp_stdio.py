#!/usr/bin/env python3
"""
Test script for MCP server with stdio transport.
"""

import asyncio
import json
import subprocess
import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server using stdio transport."""
    print("🧪 Testing OuiComply MCP Server (STDIO)")
    print("=" * 50)
    
    try:
        # Connect to the MCP server
        from mcp.client.stdio import StdioServerParameters
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server_working.py"]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ MCP server connected successfully")
                
                # Test list tools
                print("\n🔍 Testing list tools...")
                tools = await session.list_tools()
                print(f"✅ Found {len(tools.tools)} tools:")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test list resources
                print("\n🔍 Testing list resources...")
                resources = await session.list_resources()
                print(f"✅ Found {len(resources.resources)} resources:")
                for resource in resources.resources:
                    print(f"   - {resource.uri}: {resource.name}")
                
                # Test list prompts
                print("\n🔍 Testing list prompts...")
                prompts = await session.list_prompts()
                print(f"✅ Found {len(prompts.prompts)} prompts:")
                for prompt in prompts.prompts:
                    print(f"   - {prompt.name}: {prompt.description}")
                
                # Test analyze_document tool
                print("\n🔍 Testing analyze_document tool...")
                result = await session.call_tool(
                    "analyze_document",
                    {
                        "document_content": "This is a sample contract that may contain compliance issues.",
                        "document_type": "contract",
                        "frameworks": ["gdpr", "sox"]
                    }
                )
                print("✅ Document analysis completed")
                if result.content:
                    content = result.content[0].text
                    try:
                        analysis = json.loads(content)
                        print(f"   Report ID: {analysis.get('report_id', 'unknown')}")
                        print(f"   Status: {analysis.get('status', 'unknown')}")
                        print(f"   Risk Level: {analysis.get('risk_level', 'unknown')}")
                        print(f"   Issues Count: {analysis.get('issues_count', 0)}")
                    except json.JSONDecodeError:
                        print(f"   Raw result: {content[:200]}...")
                
                # Test update_memory tool
                print("\n🔍 Testing update_memory tool...")
                result = await session.call_tool(
                    "update_memory",
                    {
                        "team_id": "test_team_123",
                        "insight": "Sample compliance insight for testing",
                        "category": "testing"
                    }
                )
                print("✅ Memory update completed")
                if result.content:
                    content = result.content[0].text
                    try:
                        memory_result = json.loads(content)
                        print(f"   Team ID: {memory_result.get('team_id', 'unknown')}")
                        print(f"   Stored: {memory_result.get('insight_stored', False)}")
                        print(f"   Memory ID: {memory_result.get('memory_id', 'unknown')}")
                    except json.JSONDecodeError:
                        print(f"   Raw result: {content[:200]}...")
                
                # Test get_compliance_status tool
                print("\n🔍 Testing get_compliance_status tool...")
                result = await session.call_tool(
                    "get_compliance_status",
                    {
                        "team_id": "test_team_123",
                        "framework": "gdpr"
                    }
                )
                print("✅ Compliance status retrieved")
                if result.content:
                    content = result.content[0].text
                    try:
                        status = json.loads(content)
                        print(f"   Team ID: {status.get('team_id', 'unknown')}")
                        print(f"   Framework: {status.get('framework', 'unknown')}")
                        print(f"   Status: {status.get('overall_status', 'unknown')}")
                    except json.JSONDecodeError:
                        print(f"   Raw result: {content[:200]}...")
                
                print("\n" + "=" * 50)
                print("🎉 All MCP server tests passed!")
                
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
