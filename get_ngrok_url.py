#!/usr/bin/env python3
"""
Get ngrok tunnel URL for the MCP Server.
"""

import requests
import json
import time

def get_ngrok_url():
    """Get the ngrok tunnel URL."""
    try:
        # Wait a moment for ngrok to start
        time.sleep(2)
        
        # Get tunnel information from ngrok API
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get("tunnels", [])
            
            if tunnels:
                # Find the HTTP tunnel
                for tunnel in tunnels:
                    if tunnel.get("proto") == "http":
                        public_url = tunnel.get("public_url")
                        if public_url:
                            print(f"✅ ngrok tunnel found: {public_url}")
                            return public_url
                
                print("❌ No HTTP tunnel found")
                return None
            else:
                print("❌ No tunnels found")
                return None
        else:
            print(f"❌ Failed to get tunnel info: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting ngrok URL: {e}")
        return None

def test_tunnel(public_url):
    """Test if the tunnel is working."""
    if not public_url:
        return False
        
    try:
        response = requests.get(f"{public_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Tunnel is working - MCP Server accessible at {public_url}")
            return True
        else:
            print(f"❌ Tunnel test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tunnel test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Getting ngrok tunnel URL...")
    
    public_url = get_ngrok_url()
    if public_url:
        print(f"\n📡 Public URL: {public_url}")
        print(f"🏠 Local URL: http://localhost:8000")
        print(f"🔧 Web Interface: http://127.0.0.1:4040")
        
        # Test the tunnel
        if test_tunnel(public_url):
            print(f"\n🎉 Ready for Le Chat integration!")
            print(f"Use this URL in Le Chat: {public_url}")
        else:
            print(f"\n⚠️  Tunnel created but MCP Server not accessible")
            print("Make sure the MCP Server is running: python fastapi_simple.py")
    else:
        print("\n❌ Failed to get ngrok URL")
        print("Make sure ngrok is running: ngrok http 8000")
