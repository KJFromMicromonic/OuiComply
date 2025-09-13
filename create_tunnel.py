#!/usr/bin/env python3
"""
Create a tunnel for OuiComply MCP Server using pyngrok with different settings.
"""

import time
import requests
from pyngrok import ngrok, conf

def create_tunnel_with_retry():
    """Create ngrok tunnel with retry and different configurations."""
    print("🌐 Creating ngrok tunnel for OuiComply MCP Server...")
    
    # Try different configurations
    configs = [
        {"region": "us", "log_level": "info"},
        {"region": "eu", "log_level": "warn"},
        {"region": "ap", "log_level": "error"},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n🔄 Attempt {i}/3: Trying configuration {config}")
        
        try:
            # Configure ngrok
            conf.get_default().region = config["region"]
            conf.get_default().log_level = config["log_level"]
            
            # Create tunnel
            tunnel = ngrok.connect(8000, proto="http")
            public_url = tunnel.public_url
            
            print(f"✅ Tunnel created successfully!")
            print(f"   Public URL: {public_url}")
            print(f"   Local URL: http://localhost:8000")
            print(f"   Web Interface: http://127.0.0.1:4040")
            
            # Test the tunnel
            print(f"\n🧪 Testing tunnel...")
            time.sleep(3)  # Wait for tunnel to be ready
            
            try:
                response = requests.get(f"{public_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Tunnel test successful!")
                    return tunnel, public_url
                else:
                    print(f"⚠️  Tunnel created but server not responding: {response.status_code}")
                    # Keep the tunnel but warn the user
                    return tunnel, public_url
            except Exception as e:
                print(f"⚠️  Tunnel created but test failed: {e}")
                print("   Make sure the MCP Server is running: python fastapi_simple.py")
                return tunnel, public_url
                
        except Exception as e:
            print(f"❌ Configuration {i} failed: {e}")
            continue
    
    print("\n❌ All tunnel creation attempts failed")
    return None, None

def main():
    """Main function to create tunnel."""
    print("🚀 OuiComply MCP Server - Tunnel Creation")
    print("=" * 50)
    
    # Check if MCP Server is running
    print("🔍 Checking if MCP Server is running...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is running")
        else:
            print("⚠️  MCP Server health check failed")
    except Exception as e:
        print(f"❌ MCP Server is not running: {e}")
        print("   Please start it first: python fastapi_simple.py")
        return
    
    # Create tunnel
    tunnel, public_url = create_tunnel_with_retry()
    
    if tunnel and public_url:
        print("\n🎉 Tunnel setup complete!")
        print("=" * 50)
        print(f"📡 Public URL: {public_url}")
        print(f"🏠 Local URL: http://localhost:8000")
        print(f"🔧 Web Interface: http://127.0.0.1:4040")
        print("\n📋 Use this URL in Le Chat:")
        print(f"   {public_url}")
        print("\n⏹️  Press Ctrl+C to stop the tunnel")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping tunnel...")
            ngrok.disconnect(public_url)
            print("✅ Tunnel stopped")
    else:
        print("\n❌ Failed to create tunnel")
        print("   You may need to:")
        print("   1. Check your internet connection")
        print("   2. Verify ngrok authentication")
        print("   3. Try running ngrok manually: ngrok http 8000")

if __name__ == "__main__":
    main()
