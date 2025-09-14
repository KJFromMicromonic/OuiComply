#!/usr/bin/env python3
"""
Test script for MCP and SSE endpoints
"""

import requests
import json

def test_mcp_endpoints():
    """Test the MCP and SSE endpoints."""
    print("🧪 Testing MCP and SSE Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test MCP initialize
    print("\n1. Testing MCP initialize...")
    try:
        response = requests.post(f"{base_url}/mcp", json={
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
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Protocol Version: {data['result']['protocolVersion']}")
            print(f"   Server Name: {data['result']['serverInfo']['name']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test MCP tools/list
    print("\n2. Testing MCP tools/list...")
    try:
        response = requests.post(f"{base_url}/mcp", json={
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/list",
            "params": {}
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tools = data['result']['tools']
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test MCP tools/call
    print("\n3. Testing MCP tools/call...")
    try:
        response = requests.post(f"{base_url}/mcp", json={
            "jsonrpc": "2.0",
            "id": "test-3",
            "method": "tools/call",
            "params": {
                "name": "analyze_document",
                "arguments": {
                    "document_content": "This is a test contract for compliance analysis.",
                    "document_type": "contract",
                    "frameworks": ["gdpr", "sox"]
                }
            }
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tool call successful!")
            if 'result' in data and 'content' in data['result']:
                content = data['result']['content'][0]['text']
                print(f"   Result preview: {str(content)[:100]}...")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test SSE endpoint
    print("\n4. Testing SSE endpoint...")
    try:
        response = requests.get(f"{base_url}/mcp/sse", stream=True)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            print("   SSE connection established!")
            # Read first few events
            count = 0
            for line in response.iter_lines():
                if line:
                    print(f"   Event: {line.decode('utf-8')}")
                    count += 1
                    if count >= 3:  # Read first 3 events
                        break
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ MCP and SSE endpoints test completed!")

if __name__ == "__main__":
    test_mcp_endpoints()
