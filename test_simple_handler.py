#!/usr/bin/env python3
"""
Test script for the simple Vercel handler function.
"""

import json
import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from simple_index import handler

def test_simple_handler():
    """Test the simple handler function."""
    print("🧪 Testing Simple Vercel Handler Function")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Root endpoint (GET /)",
            "request": {"path": "/", "httpMethod": "GET", "body": ""},
            "expected_status": 200
        },
        {
            "name": "Health endpoint (GET /health)",
            "request": {"path": "/health", "httpMethod": "GET", "body": ""},
            "expected_status": 200
        },
        {
            "name": "MCP endpoint (POST /mcp)",
            "request": {
                "path": "/mcp",
                "httpMethod": "POST",
                "body": json.dumps({"id": "test-123"})
            },
            "expected_status": 200
        },
        {
            "name": "404 endpoint (GET /nonexistent)",
            "request": {"path": "/nonexistent", "httpMethod": "GET", "body": ""},
            "expected_status": 404
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        try:
            response = handler(test_case['request'])
            actual_status = response.get('statusCode', 0)
            expected_status = test_case['expected_status']
            success = actual_status == expected_status
            
            print(f"   Status: {actual_status} (expected: {expected_status}) {'✅' if success else '❌'}")
            
            try:
                body = json.loads(response.get('body', '{}'))
                print(f"   Response: {json.dumps(body, indent=2)}")
            except:
                print(f"   Response: {response.get('body', '')}")
                
        except Exception as e:
            print(f"   Error: {e} ❌")

if __name__ == "__main__":
    test_simple_handler()
