#!/usr/bin/env python3
"""
Test script for Alpic deployment verification

This script tests the deployed MCP server to ensure all tools and resources
are working correctly after Alpic deployment.

Usage: python test_alpic_deployment.py https://your-app.alpic.com
"""

import asyncio
import json
import sys
import httpx
from datetime import datetime, UTC
from typing import Dict, Any

class AlpicDeploymentTester:
    """Test suite for Alpic MCP server deployment."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def test_health_check(self) -> bool:
        """Test health check endpoint."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_mcp_initialize(self) -> bool:
        """Test MCP initialize request."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-init",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "serverInfo" in data["result"]:
                    server_name = data["result"]["serverInfo"]["name"]
                    print(f"✅ MCP initialize passed: {server_name}")
                    return True
                else:
                    print(f"❌ MCP initialize failed: Invalid response format")
                    return False
            else:
                print(f"❌ MCP initialize failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP initialize error: {e}")
            return False
    
    async def test_tools_list(self) -> bool:
        """Test tools/list request."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-tools",
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    tools = data["result"]["tools"]
                    print(f"✅ Found {len(tools)} tools")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                    return True
                else:
                    print(f"❌ Tools list failed: Invalid response format")
                    return False
            else:
                print(f"❌ Tools list failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Tools list error: {e}")
            return False
    
    async def test_analyze_document(self) -> bool:
        """Test analyze_document tool."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-analyze",
                "method": "tools/call",
                "params": {
                    "name": "analyze_document",
                    "arguments": {
                        "document_content": "This is a test privacy policy for our website.",
                        "document_type": "privacy_policy",
                        "frameworks": ["gdpr"],
                        "team_context": "Test Team"
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    print("✅ Document analysis completed successfully")
                    return True
                else:
                    print(f"❌ Document analysis failed: Invalid response format")
                    return False
            else:
                print(f"❌ Document analysis failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Document analysis error: {e}")
            return False
    
    async def test_update_memory(self) -> bool:
        """Test update_memory tool."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-memory",
                "method": "tools/call",
                "params": {
                    "name": "update_memory",
                    "arguments": {
                        "team_id": "test-team",
                        "insight": "Test insight for deployment verification",
                        "category": "test",
                        "document_type": "test_document"
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    print("✅ Memory update completed successfully")
                    return True
                else:
                    print(f"❌ Memory update failed: Invalid response format")
                    return False
            else:
                print(f"❌ Memory update failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Memory update error: {e}")
            return False
    
    async def test_get_compliance_status(self) -> bool:
        """Test get_compliance_status tool."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-status",
                "method": "tools/call",
                "params": {
                    "name": "get_compliance_status",
                    "arguments": {
                        "team_id": "test-team",
                        "include_recommendations": True
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "content" in data["result"]:
                    print("✅ Compliance status retrieved successfully")
                    return True
                else:
                    print(f"❌ Compliance status failed: Invalid response format")
                    return False
            else:
                print(f"❌ Compliance status failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Compliance status error: {e}")
            return False
    
    async def test_resources_list(self) -> bool:
        """Test resources/list request."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": "test-resources",
                "method": "resources/list",
                "params": {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "resources" in data["result"]:
                    resources = data["result"]["resources"]
                    print(f"✅ Found {len(resources)} resources")
                    for resource in resources:
                        print(f"  - {resource['name']}: {resource['description']}")
                    return True
                else:
                    print(f"❌ Resources list failed: Invalid response format")
                    return False
            else:
                print(f"❌ Resources list failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Resources list error: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all deployment tests."""
        print(f"🧪 Testing Alpic deployment at: {self.base_url}")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("MCP Initialize", self.test_mcp_initialize),
            ("Tools List", self.test_tools_list),
            ("Analyze Document", self.test_analyze_document),
            ("Update Memory", self.test_update_memory),
            ("Get Compliance Status", self.test_get_compliance_status),
            ("Resources List", self.test_resources_list)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = await test_func()
                if result:
                    passed += 1
                    self.test_results.append((test_name, True, None))
                else:
                    self.test_results.append((test_name, False, "Test failed"))
            except Exception as e:
                print(f"❌ {test_name} error: {e}")
                self.test_results.append((test_name, False, str(e)))
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! Deployment is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Check the deployment.")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python test_alpic_deployment.py <alpic_url>")
        print("Example: python test_alpic_deployment.py https://your-app.alpic.com")
        sys.exit(1)
    
    alpic_url = sys.argv[1]
    tester = AlpicDeploymentTester(alpic_url)
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
