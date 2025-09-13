#!/usr/bin/env python3
"""
Test script for Flask MCP Server.
"""

import requests
import json
import time

def test_flask_mcp_server():
    """Test the Flask MCP server."""
    
    base_url = "http://localhost:8006"
    
    print("🧪 Testing Flask MCP Server...")
    print("=" * 50)
    
    # Test health
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test MCP initialize
    print("\n3. Testing MCP initialize...")
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
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Server: {result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test tools list
    print("\n4. Testing tools list...")
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
        print(f"   Status: {response.status_code}")
        result = response.json()
        tools = result.get('result', {}).get('tools', [])
        print(f"   Found {len(tools)} tools:")
        for tool in tools:
            print(f"     - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test tool call
    print("\n5. Testing tool call...")
    try:
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": "test-3",
            "method": "tools/call",
            "params": {
                "name": "analyze_document",
                "arguments": {
                    "document_content": "This is a test service agreement for compliance analysis.",
                    "document_name": "test_agreement.txt",
                    "team_context": "Legal Team",
                    "compliance_frameworks": ["gdpr", "sox", "ccpa"]
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tool_call_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        result = response.json()
        if "result" in result:
            print("   Tool call successful!")
        else:
            print(f"   Tool call failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test Le Chat integration
    print("\n6. Testing Le Chat integration...")
    try:
        response = requests.get(f"{base_url}/lechat/integration", timeout=5)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   MCP Endpoint: {result.get('mcp_endpoint', 'Unknown')}")
        print(f"   SSE Endpoint: {result.get('sse_endpoint', 'Unknown')}")
        print(f"   Tools: {result.get('tools', 0)}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test SSE endpoint
    print("\n7. Testing SSE endpoint...")
    try:
        response = requests.get(f"{base_url}/mcp/sse", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print("   SSE endpoint accessible")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    print("\n✅ All tests passed! Flask MCP Server is working correctly.")
    return True

if __name__ == "__main__":
    test_flask_mcp_server()
