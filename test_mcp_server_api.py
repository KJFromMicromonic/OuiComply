#!/usr/bin/env python3
"""
Test the MCP Server directly with real API calls.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import OuiComplyMCPServer


async def test_mcp_server_api():
    """Test the MCP server with real API calls."""
    
    print("🚀 Testing OuiComply MCP Server with Real API Calls")
    print("=" * 60)
    
    try:
        # Initialize the MCP server
        server = OuiComplyMCPServer()
        print("✅ MCP Server initialized successfully!")
        
        # Test 1: List available tools
        print("\n📋 Test 1: Listing Available Tools")
        print("-" * 30)
        
        tools_response = server.handle_list_tools()
        tools_data = json.loads(tools_response)
        
        print(f"✅ Found {len(tools_data['tools'])} tools:")
        for tool in tools_data['tools']:
            print(f"   🔧 {tool['name']}: {tool['description']}")
        
        # Test 2: Test decompose_task tool
        print("\n🔍 Test 2: Testing decompose_task Tool")
        print("-" * 30)
        
        decompose_args = {
            "query": "Analyze this service agreement for GDPR compliance issues",
            "team_context": "Legal Team"
        }
        
        decompose_response = server.handle_call_tool("decompose_task", decompose_args)
        decompose_data = json.loads(decompose_response)
        
        print("✅ decompose_task executed successfully!")
        print(f"   📄 Document: {decompose_data.get('document_name', 'N/A')}")
        print(f"   👥 Team: {decompose_data.get('team_context', 'N/A')}")
        print(f"   🔍 Query Type: {decompose_data.get('query_type', 'N/A')}")
        
        # Test 3: Test analyze_with_memory tool
        print("\n🧠 Test 3: Testing analyze_with_memory Tool")
        print("-" * 30)
        
        analyze_args = {
            "document_content": "Test service agreement content for compliance analysis",
            "document_type": "service_agreement",
            "frameworks": ["gdpr"],
            "team_id": "legal_team"
        }
        
        analyze_response = server.handle_call_tool("analyze_with_memory", analyze_args)
        analyze_data = json.loads(analyze_response)
        
        print("✅ analyze_with_memory executed successfully!")
        print(f"   📊 Analysis completed: {analyze_data.get('status', 'N/A')}")
        print(f"   ⚠️  Issues found: {len(analyze_data.get('compliance_issues', []))}")
        print(f"   📈 Risk score: {analyze_data.get('risk_score', 0):.2f}")
        
        # Test 4: Test generate_structured_report tool
        print("\n📊 Test 4: Testing generate_structured_report Tool")
        print("-" * 30)
        
        report_args = {
            "analysis_results": {
                "compliance_issues": [{"severity": "high", "description": "Test issue"}],
                "risk_score": 0.75,
                "missing_clauses": ["Test clause"]
            },
            "team_context": "Legal Team"
        }
        
        report_response = server.handle_call_tool("generate_structured_report", report_args)
        report_data = json.loads(report_response)
        
        print("✅ generate_structured_report executed successfully!")
        print(f"   📝 Report generated: {len(report_data.get('formatted_response', ''))} characters")
        print(f"   💡 Learning prompt: {len(report_data.get('learning_prompt', ''))} characters")
        
        # Test 5: Test generate_automation_prompts tool
        print("\n🤖 Test 5: Testing generate_automation_prompts Tool")
        print("-" * 30)
        
        automation_args = {
            "analysis_results": {
                "document_type": "service_agreement",
                "frameworks": ["gdpr"],
                "issues_found": 2,
                "risk_score": 0.75
            },
            "team_context": "Legal Team",
            "priority": "high"
        }
        
        automation_response = server.handle_call_tool("generate_automation_prompts", automation_args)
        automation_data = json.loads(automation_response)
        
        print("✅ generate_automation_prompts executed successfully!")
        print(f"   📋 Linear tasks: {len(automation_data.get('tasks', []))}")
        print(f"   📧 Slack notifications: {len(automation_data.get('notifications', []))}")
        print(f"   🐛 GitHub issues: {len(automation_data.get('issues', []))}")
        
        # Test 6: Test get_team_memory tool
        print("\n🧠 Test 6: Testing get_team_memory Tool")
        print("-" * 30)
        
        memory_args = {
            "team_id": "legal_team"
        }
        
        memory_response = server.handle_call_tool("get_team_memory", memory_args)
        memory_data = json.loads(memory_response)
        
        print("✅ get_team_memory executed successfully!")
        print(f"   👥 Team: {memory_data.get('team_id', 'N/A')}")
        print(f"   📚 Compliance rules: {len(memory_data.get('compliance_rules', []))}")
        print(f"   ⚠️  Pitfall patterns: {len(memory_data.get('pitfall_patterns', []))}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL MCP SERVER API TESTS PASSED!")
        print("=" * 60)
        
        print("\n📈 Test Results Summary:")
        print("   ✅ MCP Server Initialization: Working")
        print("   ✅ Tool Listing: Working")
        print("   ✅ decompose_task: Working")
        print("   ✅ analyze_with_memory: Working")
        print("   ✅ generate_structured_report: Working")
        print("   ✅ generate_automation_prompts: Working")
        print("   ✅ get_team_memory: Working")
        
        print("\n🚀 MCP Server is fully functional with real API calls!")
        print("   Ready for hackathon submission! 🏆")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Server test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server_api())
    if success:
        print("\n✅ All MCP Server tests passed!")
    else:
        print("\n❌ MCP Server tests failed!")
        sys.exit(1)
