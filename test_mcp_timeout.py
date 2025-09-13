#!/usr/bin/env python3
"""
Test MCP server method with timeout to identify hanging issue.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import OuiComplyMCPServer


async def test_mcp_with_timeout():
    """Test MCP server method with timeout."""
    
    print("🔍 Testing MCP Server with Timeout")
    print("=" * 40)
    
    try:
        server = OuiComplyMCPServer()
        print("✅ MCP Server initialized")
        
        # Test with timeout
        print("\n🔄 Testing analyze_with_memory with 30 second timeout...")
        
        async def test_analyze_with_memory():
            return await server._handle_analyze_with_memory({
                "document_content": "Test service agreement content",
                "document_type": "service_agreement",
                "frameworks": ["gdpr"],
                "team_id": "legal_team"
            })
        
        try:
            result = await asyncio.wait_for(test_analyze_with_memory(), timeout=30.0)
            print(f"✅ analyze_with_memory completed: {len(result)} results")
            if result:
                print(f"   Response: {result[0].text[:200]}...")
        except asyncio.TimeoutError:
            print("❌ analyze_with_memory timed out after 30 seconds")
            print("   This indicates the method is hanging")
        except Exception as e:
            print(f"❌ analyze_with_memory failed: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mcp_with_timeout())
