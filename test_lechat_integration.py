#!/usr/bin/env python3
"""
Le Chat Integration Test Script

This script tests the OuiComply MCP Server integration with Le Chat.
Server URL: http://localhost:8000
"""

import requests
import json

def test_lechat_integration():
    """Test Le Chat integration endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Le Chat Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing server health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return
    
    # Test 2: Integration info
    print("\n2. Testing integration info...")
    try:
        response = requests.get(f"{base_url}/lechat/integration")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ Integration status: {info.get('integration_status')}")
            print(f"   ✅ Memory MCP: {info.get('memory_mcp')}")
        else:
            print(f"   ❌ Integration info failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Integration info failed: {e}")
        return
    
    # Test 3: Document analysis with memory
    print("\n3. Testing document analysis with memory...")
    try:
        test_request = {
            "document_content": "This is a test service agreement for compliance analysis. The agreement covers data processing, confidentiality, and termination clauses.",
            "document_name": "test_agreement.txt",
            "team_context": "Legal Team",
            "compliance_frameworks": ["gdpr", "sox", "ccpa"]
        }
        
        response = requests.post(
            f"{base_url}/lechat/test",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis completed successfully")
            print(f"   ✅ Document: {result.get('document_name')}")
            print(f"   ✅ Team: {result.get('team_context')}")
            print(f"   ✅ Memory integration: {result.get('memory_integration')}")
            print(f"   ✅ Issues found: {result.get('analysis_result', {}).get('issues_found', 'unknown')}")
            print(f"   ✅ Risk level: {result.get('analysis_result', {}).get('risk_level', 'unknown')}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        return
    
    # Test 4: Memory update
    print("\n4. Testing memory update...")
    try:
        memory_request = {
            "team_id": "legal_team",
            "memory_type": "compliance",
            "updates": {
                "compliance_rules": ["Always check for GDPR compliance", "Verify data retention policies"],
                "risk_tolerance": "low"
            }
        }
        
        response = requests.post(
            f"{base_url}/memory/update",
            json=memory_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Memory update successful")
            print(f"   ✅ Team: {result.get('message')}")
        else:
            print(f"   ❌ Memory update failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Memory update failed: {e}")
        return
    
    print("\n🎉 All Le Chat integration tests passed!")
    print(f"\n📋 Integration Summary:")
    print(f"   Server URL: {base_url}")
    print(f"   Status: Ready for Le Chat integration")
    print(f"   Memory MCP: Enabled")
    print(f"   Endpoints: /lechat/test, /analyze-with-memory, /memory/*")
    print(f"\n🔗 Use this URL in Le Chat: {base_url}")

if __name__ == "__main__":
    test_lechat_integration()
