#!/usr/bin/env python3
"""
Test script for the official MCP server implementation.
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any


class MCPClientTester:
    """Test client for the official MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the test client."""
        self.base_url = base_url
        self.session = requests.Session()
    
    async def test_server_health(self) -> bool:
        """Test if the server is running and healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is healthy: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return False
    
    async def test_mcp_initialize(self) -> bool:
        """Test MCP initialization."""
        try:
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=init_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ MCP initialization successful")
                print(f"   Server: {data.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
                print(f"   Version: {data.get('result', {}).get('serverInfo', {}).get('version', 'unknown')}")
                return True
            else:
                print(f"❌ MCP initialization failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MCP initialization error: {e}")
            return False
    
    async def test_list_tools(self) -> bool:
        """Test listing available tools."""
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=tools_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get('result', {}).get('tools', [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
                return True
            else:
                print(f"❌ List tools failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ List tools error: {e}")
            return False
    
    async def test_list_resources(self) -> bool:
        """Test listing available resources."""
        try:
            resources_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=resources_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                resources = data.get('result', {}).get('resources', [])
                print(f"✅ Found {len(resources)} resources:")
                for resource in resources:
                    print(f"   - {resource.get('uri', 'unknown')}: {resource.get('name', 'No name')}")
                return True
            else:
                print(f"❌ List resources failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ List resources error: {e}")
            return False
    
    async def test_list_prompts(self) -> bool:
        """Test listing available prompts."""
        try:
            prompts_request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "prompts/list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=prompts_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get('result', {}).get('prompts', [])
                print(f"✅ Found {len(prompts)} prompts:")
                for prompt in prompts:
                    print(f"   - {prompt.get('name', 'unknown')}: {prompt.get('description', 'No description')}")
                return True
            else:
                print(f"❌ List prompts failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ List prompts error: {e}")
            return False
    
    async def test_analyze_document_tool(self) -> bool:
        """Test the analyze_document tool."""
        try:
            tool_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "analyze_document",
                    "arguments": {
                        "document_content": "This is a sample contract that may contain compliance issues.",
                        "document_type": "contract",
                        "frameworks": ["gdpr", "sox"]
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=tool_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    print(f"✅ Document analysis completed")
                    result = data['result']
                    if 'content' in result and result['content']:
                        content = result['content'][0].get('text', '')
                        try:
                            analysis = json.loads(content)
                            print(f"   Report ID: {analysis.get('report_id', 'unknown')}")
                            print(f"   Status: {analysis.get('status', 'unknown')}")
                            print(f"   Risk Level: {analysis.get('risk_level', 'unknown')}")
                            print(f"   Issues Count: {analysis.get('issues_count', 0)}")
                        except json.JSONDecodeError:
                            print(f"   Raw result: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Tool call failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Tool call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return False
    
    async def test_update_memory_tool(self) -> bool:
        """Test the update_memory tool."""
        try:
            tool_request = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "update_memory",
                    "arguments": {
                        "team_id": "test_team_123",
                        "insight": "Sample compliance insight for testing",
                        "category": "testing"
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=tool_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    print(f"✅ Memory update completed")
                    result = data['result']
                    if 'content' in result and result['content']:
                        content = result['content'][0].get('text', '')
                        try:
                            memory_result = json.loads(content)
                            print(f"   Team ID: {memory_result.get('team_id', 'unknown')}")
                            print(f"   Stored: {memory_result.get('insight_stored', False)}")
                            print(f"   Memory ID: {memory_result.get('memory_id', 'unknown')}")
                        except json.JSONDecodeError:
                            print(f"   Raw result: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Tool call failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Tool call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return False
    
    async def test_compliance_status_tool(self) -> bool:
        """Test the get_compliance_status tool."""
        try:
            tool_request = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "get_compliance_status",
                    "arguments": {
                        "team_id": "test_team_123",
                        "framework": "gdpr"
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=tool_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    print(f"✅ Compliance status retrieved")
                    result = data['result']
                    if 'content' in result and result['content']:
                        content = result['content'][0].get('text', '')
                        try:
                            status = json.loads(content)
                            print(f"   Team ID: {status.get('team_id', 'unknown')}")
                            print(f"   Framework: {status.get('framework', 'unknown')}")
                            print(f"   Status: {status.get('overall_status', 'unknown')}")
                        except json.JSONDecodeError:
                            print(f"   Raw result: {content[:200]}...")
                    return True
                else:
                    print(f"❌ Tool call failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Tool call failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Testing OuiComply Official MCP Server")
        print("=" * 50)
        
        tests = [
            ("Server Health", self.test_server_health),
            ("MCP Initialize", self.test_mcp_initialize),
            ("List Tools", self.test_list_tools),
            ("List Resources", self.test_list_resources),
            ("List Prompts", self.test_list_prompts),
            ("Analyze Document Tool", self.test_analyze_document_tool),
            ("Update Memory Tool", self.test_update_memory_tool),
            ("Compliance Status Tool", self.test_compliance_status_tool),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}...")
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} error: {e}")
        
        print(f"\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! MCP server is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the server logs for details.")


async def main():
    """Main entry point."""
    print("Make sure the official MCP server is running:")
    print("python mcp_server_official_sdk.py")
    print()
    
    input("Press Enter to start testing...")
    
    tester = MCPClientTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
