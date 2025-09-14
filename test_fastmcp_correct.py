#!/usr/bin/env python3
"""
Correct test for OuiComply FastMCP Server

This script tests the FastMCP server using the correct API methods.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_fastmcp_server import app

async def test_fastmcp_correct():
    """Test the FastMCP server using correct API methods."""
    print("Testing OuiComply FastMCP Server (Correct API Methods)...")
    
    # Test data
    test_document = """
    This is a sample privacy policy for our company. We collect personal data 
    from users including names, email addresses, and browsing behavior. We use 
    this data to improve our services and may share it with third parties.
    """
    
    test_team_id = "test-team-123"
    test_insight = "GDPR compliance requires explicit consent for data processing"
    
    try:
        # List available tools
        print("\n1. Listing available tools...")
        tools = await app.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # List available resources
        print("\n2. Listing available resources...")
        resources = await app.list_resources()
        print(f"Available resources: {[resource.name for resource in resources]}")
        
        # Test document analysis using call_tool
        print("\n3. Testing document analysis...")
        result = await app.call_tool(
            "analyze_document",
            {
                "document_content": test_document,
                "document_type": "privacy_policy",
                "frameworks": ["gdpr", "ccpa"]
            }
        )
        print(f"Document analysis result: {result}")
        
        # Test memory update using call_tool
        print("\n4. Testing memory update...")
        result = await app.call_tool(
            "update_memory",
            {
                "team_id": test_team_id,
                "insight": test_insight,
                "category": "compliance",
                "priority": "high"
            }
        )
        print(f"Memory update result: {result}")
        
        # Test compliance status using call_tool
        print("\n5. Testing compliance status...")
        result = await app.call_tool(
            "get_compliance_status",
            {
                "team_id": test_team_id,
                "framework": "gdpr",
                "include_history": True
            }
        )
        print(f"Compliance status result: {result}")
        
        # Test workflow automation using call_tool
        print("\n6. Testing workflow automation...")
        result = await app.call_tool(
            "automate_compliance_workflow",
            {
                "document_content": test_document,
                "workflow_type": "privacy_policy_review",
                "team_id": test_team_id,
                "priority": "high"
            }
        )
        print(f"Workflow automation result: {result}")
        
        # Test compliance frameworks resource
        print("\n7. Testing compliance frameworks resource...")
        result = await app.add_resource("mcp://compliance_frameworks")
        print(f"Compliance frameworks result: {result}")
        
        # Test legal templates resource
        print("\n8. Testing legal templates resource...")
        result = await app.add_resource("mcp://legal_templates")
        print(f"Legal templates result: {result}")
        
        # Test team memory resource
        print("\n9. Testing team memory resource...")
        result = await app.add_resource(f"mcp://team_memory/{test_team_id}")
        print(f"Team memory result: {result}")
        
        print("\n✅ FastMCP server test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastmcp_correct())
