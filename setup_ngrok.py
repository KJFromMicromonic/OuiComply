#!/usr/bin/env python3
"""
Setup ngrok for OuiComply MCP Server.

This script helps set up ngrok authentication and creates a tunnel
for Le Chat integration.
"""

import subprocess
import sys
import time
from pyngrok import ngrok, conf

def setup_ngrok():
    """Set up ngrok for the MCP Server."""
    print("🔧 Setting up ngrok for OuiComply MCP Server")
    print("=" * 50)
    
    # Check if ngrok is installed
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ ngrok is not properly installed")
            return False
    except FileNotFoundError:
        print("❌ ngrok is not installed. Please install it from https://ngrok.com/download")
        return False
    
    # Check if ngrok is authenticated
    print("\n🔐 Checking ngrok authentication...")
    try:
        # Try to create a test tunnel to check authentication
        test_tunnel = ngrok.connect(8000, proto="http")
        public_url = test_tunnel.public_url
        print(f"✅ ngrok is authenticated and working")
        print(f"   Test URL: {public_url}")
        
        # Disconnect the test tunnel
        ngrok.disconnect(public_url)
        return True
        
    except Exception as e:
        print(f"❌ ngrok authentication failed: {e}")
        print("\n🔑 To authenticate ngrok:")
        print("1. Go to https://dashboard.ngrok.com/get-started/your-authtoken")
        print("2. Copy your authtoken")
        print("3. Run: ngrok config add-authtoken YOUR_TOKEN_HERE")
        print("4. Then run this script again")
        return False

def create_tunnel(port=8000):
    """Create an ngrok tunnel for the MCP Server."""
    print(f"\n🌐 Creating ngrok tunnel for port {port}...")
    
    try:
        # Configure ngrok
        conf.get_default().region = "us"
        
        # Create tunnel
        tunnel = ngrok.connect(port, proto="http")
        public_url = tunnel.public_url
        
        print(f"✅ ngrok tunnel created successfully!")
        print(f"   Local URL: http://localhost:{port}")
        print(f"   Public URL: {public_url}")
        print(f"   Web Interface: http://127.0.0.1:4040")
        
        return tunnel, public_url
        
    except Exception as e:
        print(f"❌ Failed to create ngrok tunnel: {e}")
        return None, None

def test_tunnel(public_url):
    """Test if the tunnel is working."""
    print(f"\n🧪 Testing tunnel: {public_url}")
    
    try:
        import requests
        response = requests.get(f"{public_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Tunnel is working - MCP Server is accessible")
            return True
        else:
            print(f"❌ Tunnel test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tunnel test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 OuiComply MCP Server - ngrok Setup")
    print("=" * 50)
    
    # Check ngrok setup
    if not setup_ngrok():
        print("\n❌ ngrok setup failed. Please fix authentication and try again.")
        return
    
    # Create tunnel
    tunnel, public_url = create_tunnel()
    if not tunnel:
        print("\n❌ Failed to create tunnel")
        return
    
    # Test tunnel
    if test_tunnel(public_url):
        print("\n🎉 ngrok setup complete!")
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
            print("\n\n🛑 Stopping ngrok tunnel...")
            ngrok.disconnect(public_url)
            print("✅ Tunnel stopped")
    else:
        print("\n❌ Tunnel test failed. Make sure the MCP Server is running on port 8000")
        print("   Run: python fastapi_simple.py")

if __name__ == "__main__":
    main()
