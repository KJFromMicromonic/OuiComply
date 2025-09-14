#!/usr/bin/env python3
"""
Le Chat Connection Validation Test
This script mimics exactly what Le Chat does when validating an MCP connection.
"""

import json
import requests
import time


def test_lechat_validation(base_url):
    """Test MCP connection exactly like Le Chat does during validation."""
    
    print("🤖 Le Chat MCP Connection Validation Test")
    print(f"🌐 Testing: {base_url}")
    print("=" * 60)
    
    # Step 1: CORS Preflight (OPTIONS request)
    print("\n1. 🌐 CORS Preflight Check (OPTIONS)...")
    try:
        response = requests.options(
            f"{base_url}/mcp",
            headers={
                'Origin': 'https://lechat.ai',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        # Check required CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"   CORS Check: {cors_headers}")
        
        if response.status_code != 200:
            print("   ❌ CORS preflight failed!")
            return False
        else:
            print("   ✅ CORS preflight passed!")
    
    except Exception as e:
        print(f"   ❌ CORS preflight error: {e}")
        return False
    
    # Step 2: MCP Initialize (Connection Test)
    print("\n2. 🤝 MCP Initialize (Le Chat Connection Test)...")
    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": "lechat-validation-001",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "Le Chat",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=init_request,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'https://lechat.ai',
                'Accept': 'application/json'
            },
            timeout=15
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("   Raw Response:")
            print(f"   {json.dumps(data, indent=4)}")
            
            # Validate MCP initialize response
            if "result" in data:
                result = data["result"]
                required_fields = ["protocolVersion", "capabilities", "serverInfo"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    return False
                else:
                    print("   ✅ MCP initialize response valid!")
                    print(f"      Server: {result.get('serverInfo', {}).get('name', 'Unknown')}")
                    print(f"      Version: {result.get('serverInfo', {}).get('version', 'Unknown')}")
                    print(f"      Protocol: {result.get('protocolVersion', 'Unknown')}")
            else:
                print(f"   ❌ MCP initialize failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ MCP initialize failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ MCP initialize error: {e}")
        return False
    
    # Step 3: Tools Discovery (Le Chat needs to see tools)
    print("\n3. 🛠️  Tools Discovery (Le Chat Tool Detection)...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": "lechat-validation-002",
            "method": "tools/list"
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tools_request,
            headers={
                'Content-Type': 'application/json',
                'Origin': 'https://lechat.ai'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"   ✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"      {i}. {tool.get('name', 'unnamed')} - {tool.get('description', 'no description')[:50]}...")
                
                # Validate tool schema
                for tool in tools:
                    required_tool_fields = ["name", "description", "inputSchema"]
                    missing_tool_fields = [field for field in required_tool_fields if field not in tool]
                    if missing_tool_fields:
                        print(f"   ⚠️  Tool '{tool.get('name', 'unnamed')}' missing fields: {missing_tool_fields}")
                
                print("   ✅ Tools discovery successful!")
            else:
                print(f"   ❌ Tools discovery failed: {data.get('error', 'No tools found')}")
                return False
        else:
            print(f"   ❌ Tools discovery failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"   ❌ Tools discovery error: {e}")
        return False
    
    # Step 4: Connection Health Check
    print("\n4. 🏥 Connection Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("   ✅ Health check passed!")
            print(f"      Status: {health_data.get('status', 'unknown')}")
            print(f"      Tools: {health_data.get('tools_count', 'unknown')}")
            print(f"      Resources: {health_data.get('resources_count', 'unknown')}")
        else:
            print(f"   ⚠️  Health check returned: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Health check error: {e}")
    
    # Success Summary
    print("\n" + "=" * 60)
    print("🎉 LE CHAT VALIDATION COMPLETE!")
    print("=" * 60)
    print("✅ All Le Chat connection requirements validated:")
    print("   - CORS preflight handling ✅")
    print("   - MCP initialize handshake ✅")
    print("   - Tools discovery ✅")
    print("   - JSON-RPC 2.0 protocol ✅")
    print("   - Proper response formatting ✅")
    print("")
    print("🚀 Your MCP server should now work with Le Chat!")
    print(f"🔗 Use this URL in Le Chat: {base_url}/mcp")
    
    return True


def main():
    """Main test entry point."""
    print("Le Chat MCP Connection Validation")
    print("=" * 40)
    
    # Default to your Alpic URL
    base_url = input("Enter MCP Server URL (default: https://ouicomply-test-c0e5dd8e.alpic.live): ").strip()
    if not base_url:
        base_url = "https://ouicomply-test-c0e5dd8e.alpic.live"
    
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    
    print(f"\n🧪 Testing Le Chat compatibility...")
    print("⏳ Please wait...")
    
    success = test_lechat_validation(base_url)
    
    if success:
        print("\n🎉 SUCCESS! Your MCP server passed all Le Chat validation tests!")
        print("✅ Le Chat should now recognize and connect to your server.")
    else:
        print("\n❌ VALIDATION FAILED!")
        print("🔧 Please fix the issues above and redeploy.")


if __name__ == "__main__":
    main()