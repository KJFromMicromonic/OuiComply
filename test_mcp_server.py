#!/usr/bin/env python3
"""
Test script for MCP Server.
"""

import requests
import json
import time

def test_mcp_server():
    """Test the MCP server endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing MCP Server...")
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
    
    # Test MCP endpoint
    print("\n3. Testing MCP endpoint...")
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
        print(f"   Response: {response.json()}")
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
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test Le Chat integration
    print("\n5. Testing Le Chat integration...")
    try:
        response = requests.get(f"{base_url}/lechat/integration", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    print("\n✅ All tests completed!")
    return True

if __name__ == "__main__":
    test_mcp_server()