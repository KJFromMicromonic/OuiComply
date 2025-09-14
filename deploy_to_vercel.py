#!/usr/bin/env python3
"""
Deployment script for Vercel MCP server.
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def check_vercel_cli():
    """Check if Vercel CLI is installed."""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Vercel CLI not found")
        return False


def install_vercel_cli():
    """Install Vercel CLI."""
    print("📦 Installing Vercel CLI...")
    print("⚠️  Note: Vercel CLI should be installed via npm, not pip")
    print("   Please run: npm install -g vercel")
    print("   Or visit: https://vercel.com/cli")
    return False


def check_files():
    """Check if all required files exist."""
    required_files = [
        'vercel.json',
        'api/mcp.py',
        'api/health.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True


def check_environment():
    """Check environment variables."""
    required_vars = ['MISTRAL_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   You can set these in the Vercel dashboard after deployment")
        return False
    
    print("✅ Environment variables found")
    return True


def deploy_to_vercel():
    """Deploy to Vercel."""
    print("🚀 Deploying to Vercel...")
    
    try:
        # Check if already logged in
        result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔐 Please log in to Vercel:")
            subprocess.run(['vercel', 'login'], check=True)
        
        # Deploy
        result = subprocess.run(['vercel', '--prod'], check=True, capture_output=True, text=True)
        print("✅ Deployment successful!")
        
        # Extract deployment URL
        lines = result.stdout.split('\n')
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                url = line.strip()
                print(f"🌐 Deployment URL: {url}")
                print(f"📡 MCP Endpoint: {url}/mcp")
                print(f"🏥 Health Check: {url}/health")
                return url
        
        print("⚠️  Could not extract deployment URL from output")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return None


def test_deployment(url):
    """Test the deployment."""
    if not url:
        print("⚠️  No URL provided, skipping test")
        return
    
    print(f"\n🧪 Testing deployment at {url}...")
    
    try:
        import requests
        
        # Test health check
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
        
        # Test MCP initialization
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
                }
            }
        }
        
        response = requests.post(
            f"{url}/mcp",
            json=init_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                print("✅ MCP initialization successful")
                server_info = data['result'].get('serverInfo', {})
                print(f"   Server: {server_info.get('name', 'unknown')}")
                print(f"   Version: {server_info.get('version', 'unknown')}")
            else:
                print(f"❌ MCP initialization failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ MCP initialization failed: {response.status_code}")
        
    except ImportError:
        print("⚠️  requests library not found, skipping automated test")
        print("   You can test manually by running: python test_vercel_deployment.py")
    except Exception as e:
        print(f"⚠️  Test failed: {e}")
        print("   You can test manually by running: python test_vercel_deployment.py")


def main():
    """Main deployment process."""
    print("🚀 OuiComply MCP Server - Vercel Deployment")
    print("=" * 50)
    
    # Check prerequisites
    print("\n1. Checking prerequisites...")
    
    if not check_vercel_cli():
        if not install_vercel_cli():
            print("❌ Cannot proceed without Vercel CLI")
            return False
    
    if not check_files():
        print("❌ Missing required files. Please ensure all files are present.")
        return False
    
    check_environment()  # This is just a warning, not a blocker
    
    # Deploy
    print("\n2. Deploying to Vercel...")
    url = deploy_to_vercel()
    
    if not url:
        print("❌ Deployment failed")
        return False
    
    # Test deployment
    print("\n3. Testing deployment...")
    test_deployment(url)
    
    print("\n" + "=" * 50)
    print("🎉 Deployment completed!")
    print(f"🌐 Your MCP server is available at: {url}")
    print(f"📡 MCP Endpoint: {url}/mcp")
    print(f"🏥 Health Check: {url}/health")
    print("\n📚 Next steps:")
    print("1. Set environment variables in Vercel dashboard if needed")
    print("2. Test the deployment with: python test_vercel_deployment.py")
    print("3. Configure Le Chat to use your MCP server")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
