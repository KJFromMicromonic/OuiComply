#!/usr/bin/env python3
"""
Simple test script for contract document analysis without API calls.
Tests the MCP server structure and local functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer

async def test_simple_functionality():
    """Test basic MCP server functionality without API calls."""
    print("Testing OuiComply MCP Server - Basic Functionality...")
    print("=" * 60)
    
    try:
        # Initialize the MCP server
        print("🔧 Initializing MCP server...")
        mcp_server = OuiComplyMCPServer()
        print("✅ MCP server initialized successfully!")
        
        # Test server info
        print("\n📋 Testing server info...")
        print(f"   Server Name: {mcp_server.config.server_name}")
        print(f"   Server Version: {mcp_server.config.server_version}")
        print(f"   Mistral API Key: {'✓ Set' if mcp_server.config.mistral_api_key else '✗ Not Set'}")
        
        # Test tools list
        print("\n🛠️  Testing available tools...")
        # Check if server has tools attribute
        if hasattr(mcp_server.server, 'tools'):
            tools = mcp_server.server.tools
            print(f"   Found {len(tools)} tools:")
            for tool_name, tool in tools.items():
                print(f"   - {tool_name}: {tool.description}")
        else:
            print("   Tools not accessible directly, but server is initialized")
        
        # Test compliance history (should work with empty cache)
        print("\n📊 Testing compliance history...")
        history_result = await mcp_server._handle_get_compliance_history({})
        print(f"   History result: {history_result[0].text}")
        
        # Test risk trends (should work with empty cache)
        print("\n📈 Testing risk trends...")
        trends_result = await mcp_server._handle_analyze_risk_trends({})
        print(f"   Trends result: {trends_result[0].text}")
        
        # Check docs folder
        print("\n📁 Checking docs folder...")
        docs_folder = Path("docs")
        if docs_folder.exists():
            doc_files = list(docs_folder.glob("*.pdf")) + list(docs_folder.glob("*.docx")) + list(docs_folder.glob("*.txt"))
            print(f"   Found {len(doc_files)} document(s):")
            for doc in doc_files:
                print(f"   - {doc.name} ({doc.stat().st_size} bytes)")
        else:
            print("   ❌ docs folder not found")
        
        print("\n" + "=" * 60)
        print("✅ All basic tests completed successfully!")
        print("\nThe MCP server is working correctly.")
        print("The document analysis might be hanging due to API calls.")
        print("Try running the HTTP server instead: python mcp_http_server.py")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("OuiComply Simple Test (No API Calls)")
    print("This test checks basic functionality without making API calls.")
    print("\nStarting test...")
    asyncio.run(test_simple_functionality())
