#!/usr/bin/env python3
"""
Simple test for MCP server
"""

import requests
import json

def test_simple():
    """Test basic server functionality."""
    print("🧪 Testing Simple MCP Server...")
    
    base_url = "http://localhost:8000"
    
    # Test health
    print("\n1. Testing health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test root
    print("\n2. Testing root...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint works")
            print(f"   Endpoints: {data.get('endpoints', {})}")
        else:
            print(f"   ❌ Root failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test MCP endpoint
    print("\n3. Testing MCP endpoint...")
    try:
        response = requests.post(f"{base_url}/mcp", json={
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize",
            "params": {}
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ MCP endpoint works")
        else:
            print(f"   ❌ MCP failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_simple()
