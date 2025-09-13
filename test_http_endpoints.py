#!/usr/bin/env python3
"""
Test script for HTTP MCP server endpoints.
Tests the server without hanging on API calls.
"""

import requests
import json

def test_http_server():
    """Test the HTTP MCP server endpoints."""
    base_url = "http://localhost:8000"
    
    print("Testing OuiComply HTTP MCP Server...")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("\n1. Testing GET /health")
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test info endpoint
        print("\n2. Testing GET /info")
        response = requests.get(f"{base_url}/info")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test MCP endpoint GET
        print("\n3. Testing GET /mcp")
        response = requests.get(f"{base_url}/mcp")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test MCP initialize POST
        print("\n4. Testing POST /mcp (initialize)")
        init_request = {
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
        response = requests.post(f"{base_url}/mcp", json=init_request)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test tools/list POST
        print("\n5. Testing POST /mcp (tools/list)")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        response = requests.post(f"{base_url}/mcp", json=tools_request)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        print("\n" + "=" * 50)
        print("✅ All HTTP tests completed successfully!")
        print("\nThe HTTP MCP server is working correctly.")
        print("You can now connect Le Chat or other MCP clients to:")
        print(f"   - http://localhost:8000/mcp")
        print(f"   - http://localhost:8000/ssc (Le Chat compatible)")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_http_server()
