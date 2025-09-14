#!/usr/bin/env python3
"""
Test script for HTTP MCP server
"""

import requests
import json

def test_http_mcp_server():
    """Test the HTTP MCP server."""
    print("🧪 Testing HTTP MCP Server...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test tools endpoint
    print("\n3. Testing tools endpoint...")
    try:
        response = requests.get(f"{base_url}/tools")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('tools', []))} tools:")
            for tool in data.get('tools', []):
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test resources endpoint
    print("\n4. Testing resources endpoint...")
    try:
        response = requests.get(f"{base_url}/resources")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('resources', []))} resources:")
            for resource in data.get('resources', []):
                print(f"   - {resource['name']}: {resource['description']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test tool calling
    print("\n5. Testing tool calling...")
    try:
        response = requests.post(f"{base_url}/call_tool", json={
            "name": "analyze_document",
            "arguments": {
                "document_content": "This is a test contract for compliance analysis.",
                "document_type": "contract",
                "frameworks": ["gdpr", "sox"]
            }
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tool call successful!")
            print(f"   Result: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ HTTP MCP Server test completed!")

if __name__ == "__main__":
    test_http_mcp_server()
