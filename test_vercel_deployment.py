#!/usr/bin/env python3
"""
Test script for Vercel MCP server deployment.
"""

import requests
import json
import time


def test_vercel_deployment(base_url: str):
    """Test the Vercel deployed MCP server."""
    print(f"🧪 Testing Vercel MCP Server Deployment")
    print(f"🌐 URL: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data.get('status', 'unknown')}")
            print(f"   📊 Services: {data.get('services', {})}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: MCP Initialize
    print("\n2. Testing MCP initialization...")
    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=init_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ MCP initialization successful")
            print(f"   🏷️  Server: {data.get('result', {}).get('serverInfo', {}).get('name', 'unknown')}")
            print(f"   📦 Version: {data.get('result', {}).get('serverInfo', {}).get('version', 'unknown')}")
        else:
            print(f"   ❌ MCP initialization failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ MCP initialization error: {e}")
        return False
    
    # Test 3: List Tools
    print("\n3. Testing list tools...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tools_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get('result', {}).get('tools', [])
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
        else:
            print(f"   ❌ List tools failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ List tools error: {e}")
        return False
    
    # Test 4: Analyze Document Tool
    print("\n4. Testing analyze_document tool...")
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "analyze_document",
                "arguments": {
                    "document_content": "This is a sample contract that may contain compliance issues.",
                    "document_type": "contract",
                    "frameworks": ["gdpr", "sox"]
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                print(f"   ✅ Document analysis completed")
                result = data['result']
                if 'content' in result and result['content']:
                    content = result['content'][0].get('text', '')
                    try:
                        analysis = json.loads(content)
                        print(f"      📋 Report ID: {analysis.get('report_id', 'unknown')}")
                        print(f"      📊 Status: {analysis.get('status', 'unknown')}")
                        print(f"      ⚠️  Risk Level: {analysis.get('risk_level', 'unknown')}")
                        print(f"      🔢 Issues Count: {analysis.get('issues_count', 0)}")
                    except json.JSONDecodeError:
                        print(f"      📝 Raw result: {content[:200]}...")
            else:
                print(f"   ❌ Tool call failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Tool call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Tool call error: {e}")
        return False
    
    # Test 5: Update Memory Tool
    print("\n5. Testing update_memory tool...")
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "update_memory",
                "arguments": {
                    "team_id": "test_team_123",
                    "insight": "Sample compliance insight for testing",
                    "category": "testing"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tool_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                print(f"   ✅ Memory update completed")
                result = data['result']
                if 'content' in result and result['content']:
                    content = result['content'][0].get('text', '')
                    try:
                        memory_result = json.loads(content)
                        print(f"      👥 Team ID: {memory_result.get('team_id', 'unknown')}")
                        print(f"      💾 Stored: {memory_result.get('insight_stored', False)}")
                        print(f"      🆔 Memory ID: {memory_result.get('memory_id', 'unknown')}")
                    except json.JSONDecodeError:
                        print(f"      📝 Raw result: {content[:200]}...")
            else:
                print(f"   ❌ Tool call failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Tool call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Tool call error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Vercel deployment tests passed!")
    print("✅ MCP server is ready for Le Chat integration!")
    return True


def main():
    """Main entry point."""
    print("Vercel MCP Server Deployment Test")
    print("=" * 50)
    print("Please provide your Vercel deployment URL:")
    print("Example: https://your-app.vercel.app")
    print()
    
    base_url = input("Enter Vercel URL: ").strip()
    if not base_url:
        print("❌ No URL provided. Exiting.")
        return
    
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"
    
    print(f"\n🚀 Testing deployment at: {base_url}")
    print("⏳ Please wait...")
    
    success = test_vercel_deployment(base_url)
    
    if success:
        print("\n🎉 Deployment test completed successfully!")
        print("🔗 Your MCP server is ready for Le Chat integration!")
        print(f"📡 MCP Endpoint: {base_url}/mcp")
        print(f"🏥 Health Check: {base_url}/health")
    else:
        print("\n❌ Deployment test failed. Please check the logs above.")


if __name__ == "__main__":
    main()
