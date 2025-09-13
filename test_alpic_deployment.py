#!/usr/bin/env python3
'''
Test script for deployed OuiComply MCP Server on Alpic.
'''

import requests
import json
import sys

def test_mcp_server(base_url):
    '''Test the deployed MCP server.'''
    
    print(f"🧪 Testing MCP Server at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test MCP endpoint
    print("\n2. Testing MCP endpoint...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "test-1",
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
        
        response = requests.post(
            f"{base_url}/mcp",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP initialize successful")
            print(f"   Server: {result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ MCP initialize failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP test error: {e}")
        return False
    
    # Test tools list
    print("\n3. Testing tools list...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/list"
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools test error: {e}")
        return False
    
    # Test Le Chat integration
    print("\n4. Testing Le Chat integration...")
    try:
        response = requests.get(f"{base_url}/lechat/integration", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Le Chat integration ready")
            print(f"   MCP Endpoint: {result.get('mcp_endpoint', 'Unknown')}")
            print(f"   SSE Endpoint: {result.get('sse_endpoint', 'Unknown')}")
            print(f"   Tools: {result.get('tools', 0)}")
        else:
            print(f"❌ Le Chat integration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Le Chat test error: {e}")
        return False
    
    print("\n🎉 All tests passed! MCP Server is ready for Le Chat integration.")
    return True

def main():
    '''Main test function.'''
    if len(sys.argv) != 2:
        print("Usage: python test_alpic_deployment.py <BASE_URL>")
        print("Example: python test_alpic_deployment.py https://your-app.alpic.ai")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    if test_mcp_server(base_url):
        print("\n📋 Next steps:")
        print(f"1. Configure Le Chat to use: {base_url}/mcp")
        print(f"2. Use SSE endpoint: {base_url}/mcp/sse")
        print("3. Test document analysis through Le Chat")
    else:
        print("\n❌ Some tests failed. Check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
