#!/usr/bin/env python3
"""
Test script to verify ALPIC MCP endpoints are working correctly.
"""

import requests
import json
import sys

def test_endpoint(base_url, endpoint, method="GET", data=None, headers=None):
    """Test a specific endpoint."""
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}...")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Test all MCP endpoints."""
    # Test both local and ALPIC URLs
    test_urls = [
        "http://localhost:8000",
        "https://ouicomplytest-f83c8aad.alpic.live"
    ]
    
    endpoints_to_test = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/auth", "GET"),
        ("/mcp", "GET"),
        ("/mcp", "POST", {"jsonrpc": "2.0", "method": "initialize", "id": 1}),
        ("/ssc", "GET"),
        ("/ssc", "POST", {"jsonrpc": "2.0", "method": "initialize", "id": 1}),
    ]
    
    for base_url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {base_url}")
        print(f"{'='*60}")
        
        success_count = 0
        total_tests = len(endpoints_to_test)
        
        for endpoint_info in endpoints_to_test:
            if len(endpoint_info) == 2:
                endpoint, method = endpoint_info
                data = None
            else:
                endpoint, method, data = endpoint_info
                
            if test_endpoint(base_url, endpoint, method, data):
                success_count += 1
            print()
        
        print(f"✅ {success_count}/{total_tests} tests passed for {base_url}")

if __name__ == "__main__":
    main()
