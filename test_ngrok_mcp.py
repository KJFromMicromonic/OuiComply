#!/usr/bin/env python3
"""
Test script for ngrok MCP Server

This script tests the ngrok-exposed MCP server to ensure it's working correctly.
"""

import asyncio
import json
import requests
import sys
import time
from typing import Dict, Any, Optional


class NgrokMCPTester:
    """
    Test suite for ngrok-exposed MCP server.
    
    This class provides comprehensive testing of the MCP server endpoints
    to ensure they're working correctly via ngrok tunnel.
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OuiComply-MCP-Tester/1.0'
        })
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        print("🔍 Testing health endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status', 'unknown')}")
                print(f"   Server: {data.get('server', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_info_endpoint(self) -> bool:
        """Test the info endpoint."""
        print("🔍 Testing info endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/info", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Info endpoint passed")
                print(f"   Server: {data.get('server', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Tools available: {data.get('tools_available', 0)}")
                print(f"   Resources available: {data.get('resources_available', 0)}")
                return True
            else:
                print(f"❌ Info endpoint failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Info endpoint error: {e}")
            return False
    
    def test_mcp_initialize(self) -> bool:
        """Test MCP initialize method."""
        print("🔍 Testing MCP initialize...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
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
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    print("✅ MCP initialize passed")
                    print(f"   Protocol version: {data['result'].get('protocolVersion', 'unknown')}")
                    print(f"   Server name: {data['result'].get('serverInfo', {}).get('name', 'unknown')}")
                    return True
                else:
                    print(f"❌ MCP initialize failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ MCP initialize failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP initialize error: {e}")
            return False
    
    def test_mcp_list_tools(self) -> bool:
        """Test MCP tools/list method."""
        print("🔍 Testing MCP tools/list...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'tools' in data['result']:
                    tools = data['result']['tools']
                    print(f"✅ MCP tools/list passed: {len(tools)} tools available")
                    for tool in tools[:3]:  # Show first 3 tools
                        print(f"   - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')[:50]}...")
                    return True
                else:
                    print(f"❌ MCP tools/list failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ MCP tools/list failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP tools/list error: {e}")
            return False
    
    def test_mcp_list_resources(self) -> bool:
        """Test MCP resources/list method."""
        print("🔍 Testing MCP resources/list...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/list",
                "params": {}
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'resources' in data['result']:
                    resources = data['result']['resources']
                    print(f"✅ MCP resources/list passed: {len(resources)} resources available")
                    for resource in resources:
                        print(f"   - {resource.get('name', 'unknown')}: {resource.get('description', 'No description')[:50]}...")
                    return True
                else:
                    print(f"❌ MCP resources/list failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ MCP resources/list failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP resources/list error: {e}")
            return False
    
    def test_ssc_compatibility(self) -> bool:
        """Test SSC (LeChat) compatibility endpoint."""
        print("🔍 Testing SSC compatibility...")
        try:
            # Test SSC GET endpoint
            response = self.session.get(f"{self.base_url}/ssc", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('lechat_compatible'):
                    print("✅ SSC compatibility passed")
                    print(f"   LeChat compatible: {data.get('lechat_compatible')}")
                    return True
                else:
                    print("❌ SSC compatibility failed: Not LeChat compatible")
                    return False
            else:
                print(f"❌ SSC compatibility failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ SSC compatibility error: {e}")
            return False
    
    def test_document_analysis(self) -> bool:
        """Test document analysis tool."""
        print("🔍 Testing document analysis tool...")
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "analyze_document_compliance",
                    "arguments": {
                        "document_content": "This is a sample privacy policy for testing purposes.",
                        "compliance_frameworks": ["gdpr"],
                        "analysis_depth": "basic"
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/mcp",
                json=payload,
                timeout=30  # Longer timeout for analysis
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    print("✅ Document analysis test passed")
                    print("   Analysis completed successfully")
                    return True
                else:
                    print(f"❌ Document analysis failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Document analysis failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Document analysis error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        print("🧪 Starting comprehensive MCP server tests...")
        print(f"🌐 Testing server at: {self.base_url}")
        print("=" * 60)
        
        tests = {
            "health_endpoint": self.test_health_endpoint,
            "info_endpoint": self.test_info_endpoint,
            "mcp_initialize": self.test_mcp_initialize,
            "mcp_list_tools": self.test_mcp_list_tools,
            "mcp_list_resources": self.test_mcp_list_resources,
            "ssc_compatibility": self.test_ssc_compatibility,
            "document_analysis": self.test_document_analysis
        }
        
        results = {}
        for test_name, test_func in tests.items():
            print()
            results[test_name] = test_func()
            time.sleep(1)  # Small delay between tests
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print test summary."""
        print()
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        print()
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print()
        if passed == total:
            print("🎉 ALL TESTS PASSED! MCP server is working correctly via ngrok.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        print()
        print("🔗 Available endpoints:")
        print(f"   Health: {self.base_url}/health")
        print(f"   Info: {self.base_url}/info")
        print(f"   MCP: {self.base_url}/mcp")
        print(f"   SSC: {self.base_url}/ssc")


def main():
    """Main test function."""
    if len(sys.argv) != 2:
        print("Usage: python test_ngrok_mcp.py <ngrok_url>")
        print("Example: python test_ngrok_mcp.py https://abc123.ngrok.io")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Validate URL format
    if not base_url.startswith(('http://', 'https://')):
        base_url = f"https://{base_url}"
    
    tester = NgrokMCPTester(base_url)
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
