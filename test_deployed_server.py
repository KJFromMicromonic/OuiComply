#!/usr/bin/env python3
"""
Test script for deployed Alpic server
"""

import requests
import json

def test_deployed_server():
    base_url = "https://ouicomply-test-c0e5dd8e.alpic.live"
    
    print("🧪 Testing Deployed Alpic Server...")
    print("=" * 50)
    
    # Test different endpoints
    endpoints = [
        "/",
        "/health", 
        "/mcp",
        "/mcp/sse",
        "/lechat/integration"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing {endpoint}...")
            url = f"{base_url}{endpoint}"
            
            if endpoint == "/mcp":
                # Test MCP initialize
                response = requests.post(url, json={
                    "jsonrpc": "2.0",
                    "id": "test-1",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"}
                    }
                }, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   Error: {e}")
        except Exception as e:
            print(f"   Unexpected error: {e}")

if __name__ == "__main__":
    test_deployed_server()
