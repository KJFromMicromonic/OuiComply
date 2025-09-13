#!/usr/bin/env python3
"""
Setup tunnel for OuiComply MCP Server using various methods.
"""

import subprocess
import time
import requests
import webbrowser
from pathlib import Path

def check_server_running():
    """Check if the MCP Server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def try_cloudflare_tunnel():
    """Try to set up Cloudflare tunnel."""
    print("🌐 Trying Cloudflare Tunnel...")
    
    try:
        # Check if cloudflared is installed
        result = subprocess.run(["cloudflared", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Cloudflare Tunnel is installed")
            
            # Create tunnel
            print("   Creating tunnel...")
            result = subprocess.run([
                "cloudflared", "tunnel", "--url", "http://localhost:8000"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract URL from output
                output = result.stdout
                if "https://" in output:
                    url = output.split("https://")[1].split()[0]
                    public_url = f"https://{url}"
                    print(f"✅ Cloudflare tunnel created: {public_url}")
                    return public_url
            
        else:
            print("❌ Cloudflare Tunnel not installed")
            print("   Install from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
    except Exception as e:
        print(f"❌ Cloudflare tunnel failed: {e}")
    
    return None

def try_localtunnel():
    """Try to set up localtunnel."""
    print("🌐 Trying LocalTunnel...")
    
    try:
        # Check if localtunnel is available
        result = subprocess.run(["npx", "localtunnel", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ LocalTunnel is available")
            
            # Create tunnel
            print("   Creating tunnel...")
            result = subprocess.run([
                "npx", "localtunnel", "--port", "8000", "--subdomain", "ouicomply-mcp"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Extract URL from output
                output = result.stdout
                if "https://" in output:
                    url = output.split("https://")[1].split()[0]
                    public_url = f"https://{url}"
                    print(f"✅ LocalTunnel created: {public_url}")
                    return public_url
            
        else:
            print("❌ LocalTunnel not available")
    except Exception as e:
        print(f"❌ LocalTunnel failed: {e}")
    
    return None

def try_serveo():
    """Try to set up serveo tunnel."""
    print("🌐 Trying Serveo...")
    
    try:
        # Create tunnel using serveo
        result = subprocess.run([
            "ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:8000", "serveo.net"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            output = result.stdout
            if "https://" in output:
                url = output.split("https://")[1].split()[0]
                public_url = f"https://{url}"
                print(f"✅ Serveo tunnel created: {public_url}")
                return public_url
        else:
            print("❌ Serveo tunnel failed")
    except Exception as e:
        print(f"❌ Serveo failed: {e}")
    
    return None

def test_tunnel(public_url):
    """Test if the tunnel is working."""
    if not public_url:
        return False
    
    print(f"\n🧪 Testing tunnel: {public_url}")
    
    try:
        response = requests.get(f"{public_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Tunnel is working!")
            return True
        else:
            print(f"❌ Tunnel test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tunnel test failed: {e}")
        return False

def open_test_interface():
    """Open the local test interface."""
    test_file = Path("mcp_server_test.html")
    if test_file.exists():
        print("🌐 Opening local test interface...")
        webbrowser.open(f"file://{test_file.absolute()}")
        print("✅ Test interface opened in browser")
    else:
        print("❌ Test interface not found")

def main():
    """Main function to set up tunnel."""
    print("🚀 OuiComply MCP Server - Tunnel Setup")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_running():
        print("❌ MCP Server is not running!")
        print("   Please start it first: python fastapi_simple.py")
        return
    
    print("✅ MCP Server is running")
    
    # Try different tunneling methods
    methods = [
        try_cloudflare_tunnel,
        try_localtunnel,
        try_serveo
    ]
    
    public_url = None
    for method in methods:
        public_url = method()
        if public_url:
            break
    
    if public_url:
        # Test the tunnel
        if test_tunnel(public_url):
            print(f"\n🎉 Tunnel setup complete!")
            print("=" * 50)
            print(f"📡 Public URL: {public_url}")
            print(f"🏠 Local URL: http://localhost:8000")
            print(f"\n📋 Use this URL in Le Chat: {public_url}")
            print("\n⏹️  Press Ctrl+C to stop the tunnel")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping tunnel...")
                print("✅ Tunnel stopped")
        else:
            print(f"\n⚠️  Tunnel created but not working properly")
            print(f"   URL: {public_url}")
            print("   Check your internet connection and try again")
    else:
        print("\n❌ All tunneling methods failed")
        print("\n🛠️  Alternative solutions:")
        print("1. Deploy to a cloud service (Heroku, Railway, Render)")
        print("2. Use manual port forwarding")
        print("3. Use a VPN service")
        print("4. Test locally using the test interface")
        
        # Open local test interface
        open_test_interface()

if __name__ == "__main__":
    main()
