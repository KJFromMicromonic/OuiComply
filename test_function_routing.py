#!/usr/bin/env python3
"""
Test script for the new function-based routing endpoints in MCP server.
"""

import requests
import json
import time

def test_function_routing():
    """Test the new function-based routing endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing OuiComply MCP Function-Based Routing")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Root endpoint to see available endpoints
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Available endpoints: {data.get('endpoints', {})}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Analyze document endpoint
    print("\n3. Testing /mcp/analyze_document...")
    try:
        test_document = {
            "document_content": "This is a sample contract that may contain compliance issues.",
            "document_type": "contract",
            "frameworks": ["gdpr", "sox"]
        }
        response = requests.post(f"{base_url}/mcp/analyze_document", json=test_document)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Update memory endpoint
    print("\n4. Testing /mcp/update_memory...")
    try:
        memory_data = {
            "team_id": "test_team_123",
            "insight": "Sample compliance insight for testing",
            "category": "testing"
        }
        response = requests.post(f"{base_url}/mcp/update_memory", json=memory_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Get compliance status endpoint
    print("\n5. Testing /mcp/get_compliance_status...")
    try:
        status_data = {
            "team_id": "test_team_123",
            "framework": "gdpr"
        }
        response = requests.post(f"{base_url}/mcp/get_compliance_status", json=status_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 6: Test error handling with missing required fields
    print("\n6. Testing error handling (missing required fields)...")
    try:
        invalid_data = {
            "document_type": "contract"
            # Missing required document_content
        }
        response = requests.post(f"{base_url}/mcp/analyze_document", json=invalid_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Function-based routing test completed!")

if __name__ == "__main__":
    print("Make sure the MCP server is running on localhost:8000")
    print("You can start it with: python mcp_server_proper.py")
    print()
    
    input("Press Enter to start testing...")
    test_function_routing()
