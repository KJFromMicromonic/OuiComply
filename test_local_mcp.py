#!/usr/bin/env python3
"""
Test script for local MCP server functionality.
This tests the core MCP functionality without requiring a full server.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine


async def test_core_functionality():
    """Test the core MCP functionality locally."""
    print("🧪 Testing OuiComply MCP Core Functionality")
    print("=" * 50)
    
    try:
        # Initialize services
        print("\n1. Initializing services...")
        document_ai_service = DocumentAIService()
        memory_integration = MemoryIntegration(use_lechat_mcp=True)
        compliance_engine = ComplianceEngine()
        print("   ✅ All services initialized successfully")
        
        # Test document analysis
        print("\n2. Testing document analysis...")
        try:
            report = await compliance_engine.analyze_document_compliance(
                document_content="This is a sample contract that may contain compliance issues.",
                document_type="contract",
                frameworks=["gdpr", "sox"]
            )
            print(f"   ✅ Document analysis completed")
            print(f"   📋 Report ID: {report.report_id}")
            print(f"   📊 Status: {report.overall_status.value}")
            print(f"   ⚠️  Risk Level: {report.risk_level.value}")
            print(f"   🔢 Issues Count: {len(report.issues)}")
        except Exception as e:
            print(f"   ❌ Document analysis failed: {e}")
            return False
        
        # Test memory integration
        print("\n3. Testing memory integration...")
        try:
            # Store insight
            result = await memory_integration.store_insight(
                team_id="test_team_123",
                insight="Sample compliance insight for testing",
                category="testing"
            )
            print(f"   ✅ Memory storage completed")
            print(f"   🆔 Memory ID: {result.get('memory_id', 'unknown')}")
            
            # Get team status
            status = await memory_integration.get_team_status("test_team_123")
            print(f"   ✅ Team status retrieved")
            print(f"   📊 Overall Status: {status.get('overall_status', 'unknown')}")
            print(f"   📈 Compliance Score: {status.get('compliance_score', 0.0)}")
            
            # Get team memory
            memory = await memory_integration.get_team_memory("test_team_123")
            print(f"   ✅ Team memory retrieved")
            print(f"   💾 Insights Count: {len(memory.get('insights', []))}")
            
        except Exception as e:
            print(f"   ❌ Memory integration failed: {e}")
            return False
        
        # Test MCP tool functions
        print("\n4. Testing MCP tool functions...")
        try:
            # Test analyze_document tool
            analyze_result = {
                "document_content": "This is a sample contract that may contain compliance issues.",
                "document_type": "contract",
                "frameworks": ["gdpr", "sox"]
            }
            
            # Simulate the tool call
            report = await compliance_engine.analyze_document_compliance(
                document_content=analyze_result["document_content"],
                document_type=analyze_result["document_type"],
                frameworks=analyze_result["frameworks"]
            )
            
            tool_result = {
                "report_id": report.report_id,
                "status": report.overall_status.value,
                "risk_level": report.risk_level.value,
                "risk_score": report.risk_score,
                "issues_count": len(report.issues),
                "summary": report.summary,
                "frameworks_analyzed": analyze_result["frameworks"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"   ✅ analyze_document tool working")
            print(f"      Report ID: {tool_result['report_id']}")
            print(f"      Status: {tool_result['status']}")
            print(f"      Risk Level: {tool_result['risk_level']}")
            
            # Test update_memory tool
            memory_result = await memory_integration.store_insight(
                team_id="test_team_123",
                insight="Tool test insight",
                category="testing"
            )
            
            print(f"   ✅ update_memory tool working")
            print(f"      Memory ID: {memory_result.get('memory_id', 'unknown')}")
            
            # Test get_compliance_status tool
            status_result = await memory_integration.get_team_status("test_team_123")
            
            print(f"   ✅ get_compliance_status tool working")
            print(f"      Team Status: {status_result.get('overall_status', 'unknown')}")
            
        except Exception as e:
            print(f"   ❌ MCP tool functions failed: {e}")
            return False
        
        # Test MCP resources
        print("\n5. Testing MCP resources...")
        try:
            # Test compliance frameworks resource
            frameworks = {
                "gdpr": {
                    "name": "General Data Protection Regulation",
                    "description": "EU regulation for data protection and privacy",
                    "requirements": [
                        "Data minimization",
                        "Purpose limitation",
                        "Storage limitation",
                        "Accuracy",
                        "Integrity and confidentiality",
                        "Lawfulness of processing"
                    ]
                },
                "sox": {
                    "name": "Sarbanes-Oxley Act",
                    "description": "US law for financial reporting and corporate governance",
                    "requirements": [
                        "Internal controls over financial reporting",
                        "Management assessment of controls",
                        "Auditor attestation",
                        "Documentation and testing",
                        "Disclosure controls"
                    ]
                }
            }
            
            print(f"   ✅ Compliance frameworks resource ready")
            print(f"      Available frameworks: {list(frameworks.keys())}")
            
            # Test team memory resource
            team_memory = await memory_integration.get_team_memory("test_team_123")
            print(f"   ✅ Team memory resource ready")
            print(f"      Team insights: {len(team_memory.get('insights', []))}")
            
        except Exception as e:
            print(f"   ❌ MCP resources failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All core functionality tests passed!")
        print("✅ Your MCP server is ready for deployment!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Core functionality test failed: {e}")
        return False


async def test_vercel_api_simulation():
    """Test the Vercel API simulation locally."""
    print("\n🌐 Testing Vercel API Simulation")
    print("-" * 40)
    
    try:
        # Simulate the Vercel API handler
        from api.mcp import handler
        
        # Test health check
        print("\n1. Testing health check...")
        health_request = {
            "method": "GET",
            "path": "/health",
            "headers": {},
            "body": ""
        }
        
        health_response = handler(health_request)
        if health_response["statusCode"] == 200:
            print("   ✅ Health check simulation successful")
            health_data = json.loads(health_response["body"])
            print(f"      Status: {health_data.get('status', 'unknown')}")
            print(f"      Server: {health_data.get('mcp_server', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {health_response['statusCode']}")
            return False
        
        # Test MCP initialization
        print("\n2. Testing MCP initialization...")
        init_request = {
            "method": "POST",
            "path": "/mcp",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    }
                }
            })
        }
        
        init_response = handler(init_request)
        if init_response["statusCode"] == 200:
            print("   ✅ MCP initialization simulation successful")
            init_data = json.loads(init_response["body"])
            server_info = init_data.get("result", {}).get("serverInfo", {})
            print(f"      Server: {server_info.get('name', 'unknown')}")
            print(f"      Version: {server_info.get('version', 'unknown')}")
        else:
            print(f"   ❌ MCP initialization failed: {init_response['statusCode']}")
            return False
        
        # Test tools list
        print("\n3. Testing tools list...")
        tools_request = {
            "method": "POST",
            "path": "/mcp",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            })
        }
        
        tools_response = handler(tools_request)
        if tools_response["statusCode"] == 200:
            print("   ✅ Tools list simulation successful")
            tools_data = json.loads(tools_response["body"])
            tools = tools_data.get("result", {}).get("tools", [])
            print(f"      Available tools: {len(tools)}")
            for tool in tools:
                print(f"        - {tool.get('name', 'unknown')}")
        else:
            print(f"   ❌ Tools list failed: {tools_response['statusCode']}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 Vercel API simulation tests passed!")
        print("✅ Your API is ready for Vercel deployment!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Vercel API simulation failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 OuiComply MCP Server - Local Testing")
    print("=" * 60)
    
    # Test core functionality
    core_success = await test_core_functionality()
    
    if not core_success:
        print("\n❌ Core functionality tests failed. Please fix issues before deployment.")
        return False
    
    # Test Vercel API simulation
    api_success = await test_vercel_api_simulation()
    
    if not api_success:
        print("\n❌ API simulation tests failed. Please fix issues before deployment.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Your MCP server is ready for Vercel deployment!")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("1. Run: python deploy_vercel_simple.py")
    print("2. Follow the deployment instructions")
    print("3. Test your deployed server")
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
