#!/usr/bin/env python3
"""
Test script for Vercel deployment verification.

This script tests the deployed Vercel endpoints to ensure they're working correctly.
Run this after deploying to Vercel to verify the 404 error is fixed.

Author: OuiComply Team
Version: 1.0.0
"""

import requests
import json
from datetime import datetime, UTC

def test_vercel_deployment(base_url: str):
    """
    Test the Vercel deployment endpoints.
    
    @param base_url The base URL of your Vercel deployment
    @returns Dictionary with test results
    """
    results = {
        "base_url": base_url,
        "tests": [],
        "timestamp": datetime.now(UTC).isoformat()
    }
    
    # Test endpoints
    endpoints = [
        {"path": "/", "method": "GET", "expected_status": 200},
        {"path": "/health", "method": "GET", "expected_status": 200},
        {"path": "/mcp", "method": "POST", "expected_status": 200},
        {"path": "/nonexistent", "method": "GET", "expected_status": 404}
    ]
    
    for endpoint in endpoints:
        test_result = {
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "expected_status": endpoint["expected_status"],
            "actual_status": None,
            "response": None,
            "success": False,
            "error": None
        }
        
        try:
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['path']}", timeout=10)
            elif endpoint["method"] == "POST":
                test_data = {"id": "test-123", "method": "test"}
                response = requests.post(
                    f"{base_url}{endpoint['path']}", 
                    json=test_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
            
            test_result["actual_status"] = response.status_code
            test_result["response"] = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            test_result["success"] = response.status_code == endpoint["expected_status"]
            
        except requests.exceptions.RequestException as e:
            test_result["error"] = str(e)
            test_result["success"] = False
        
        results["tests"].append(test_result)
    
    return results

def print_test_results(results: dict):
    """
    Print formatted test results.
    
    @param results Dictionary containing test results
    """
    print("🧪 Vercel Deployment Test Results")
    print("=" * 50)
    print(f"Base URL: {results['base_url']}")
    print(f"Timestamp: {results['timestamp']}")
    print()
    
    for test in results["tests"]:
        status_icon = "✅" if test["success"] else "❌"
        print(f"{status_icon} {test['method']} {test['endpoint']}")
        print(f"   Expected: {test['expected_status']}, Got: {test['actual_status']}")
        
        if test["error"]:
            print(f"   Error: {test['error']}")
        elif test["response"]:
            if isinstance(test["response"], dict):
                print(f"   Response: {json.dumps(test['response'], indent=2)}")
            else:
                print(f"   Response: {test['response']}")
        print()
    
    # Summary
    total_tests = len(results["tests"])
    passed_tests = sum(1 for test in results["tests"] if test["success"])
    print(f"Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your Vercel deployment is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    # Replace with your actual Vercel deployment URL
    # Example: "https://your-app-name.vercel.app"
    VERCEL_URL = input("Enter your Vercel deployment URL: ").strip()
    
    if not VERCEL_URL:
        print("❌ Please provide a valid Vercel URL")
        exit(1)
    
    if not VERCEL_URL.startswith(("http://", "https://")):
        VERCEL_URL = f"https://{VERCEL_URL}"
    
    print(f"Testing deployment at: {VERCEL_URL}")
    print()
    
    try:
        results = test_vercel_deployment(VERCEL_URL)
        print_test_results(results)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
