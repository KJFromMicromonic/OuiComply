#!/usr/bin/env python3
"""
Local test script for the Vercel handler function.

This script tests the handler function locally to ensure it works correctly
before deploying to Vercel.

Author: OuiComply Team
Version: 1.0.0
"""

import json
import sys
import os

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from index import handler

def test_handler():
    """
    Test the handler function with various request scenarios.
    
    @returns Dictionary with test results
    """
    print("🧪 Testing Vercel Handler Function Locally")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Root endpoint (GET /)",
            "request": {
                "path": "/",
                "httpMethod": "GET",
                "body": "",
                "headers": {}
            },
            "expected_status": 200
        },
        {
            "name": "Health endpoint (GET /health)",
            "request": {
                "path": "/health",
                "httpMethod": "GET",
                "body": "",
                "headers": {}
            },
            "expected_status": 200
        },
        {
            "name": "MCP endpoint (POST /mcp)",
            "request": {
                "path": "/mcp",
                "httpMethod": "POST",
                "body": json.dumps({"id": "test-123", "method": "test"}),
                "headers": {"Content-Type": "application/json"}
            },
            "expected_status": 200
        },
        {
            "name": "API info endpoint (GET /api)",
            "request": {
                "path": "/api",
                "httpMethod": "GET",
                "body": "",
                "headers": {}
            },
            "expected_status": 200
        },
        {
            "name": "CORS preflight (OPTIONS /mcp)",
            "request": {
                "path": "/mcp",
                "httpMethod": "OPTIONS",
                "body": "",
                "headers": {"Origin": "https://example.com"}
            },
            "expected_status": 200
        },
        {
            "name": "404 endpoint (GET /nonexistent)",
            "request": {
                "path": "/nonexistent",
                "httpMethod": "GET",
                "body": "",
                "headers": {}
            },
            "expected_status": 404
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        try:
            # Call the handler
            response = handler(test_case['request'])
            
            # Check status code
            actual_status = response.get('statusCode', 0)
            expected_status = test_case['expected_status']
            
            # Parse response body
            try:
                body = json.loads(response.get('body', '{}'))
            except:
                body = response.get('body', '')
            
            # Check if test passed
            success = actual_status == expected_status
            
            print(f"   Status: {actual_status} (expected: {expected_status}) {'✅' if success else '❌'}")
            print(f"   Headers: {response.get('headers', {})}")
            print(f"   Body: {json.dumps(body, indent=2) if isinstance(body, dict) else body}")
            
            results.append({
                "name": test_case['name'],
                "success": success,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "response": response
            })
            
        except Exception as e:
            print(f"   Error: {e} ❌")
            results.append({
                "name": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.get('success', False))
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The handler is ready for Vercel deployment.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    return results

if __name__ == "__main__":
    test_handler()
