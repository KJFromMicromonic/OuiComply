#!/usr/bin/env python3
"""
Alpic deployment configuration for OuiComply MCP Server.
"""

import os
import json
from pathlib import Path

def create_alpic_config():
    """Create Alpic deployment configuration."""
    
    # Alpic configuration
    alpic_config = {
        "name": "ouicomply-mcp-server",
        "description": "OuiComply MCP Server for Le Chat Integration",
        "version": "1.0.0",
        "runtime": "python3.11",
        "entrypoint": "mcp_server_lechat.py",
        "port": 8000,
        "environment": {
            "PYTHONPATH": "/app",
            "MISTRAL_API_KEY": os.getenv("MISTRAL_API_KEY", ""),
            "LOG_LEVEL": "INFO"
        },
        "dependencies": "requirements_mcp.txt",
        "health_check": "/health",
        "endpoints": {
            "mcp": "/mcp",
            "sse": "/mcp/sse",
            "health": "/health",
            "lechat": "/lechat/integration"
        },
        "capabilities": {
            "mcp_protocol": True,
            "server_sent_events": True,
            "tool_calling": True,
            "resource_management": True,
            "prompt_templates": True
        }
    }
    
    # Save configuration
    with open("alpic.json", "w") as f:
        json.dump(alpic_config, f, indent=2)
    
    print("✅ Alpic configuration created: alpic.json")
    return alpic_config

def create_dockerfile():
    """Create Dockerfile for Alpic deployment."""
    
    dockerfile_content = """# OuiComply MCP Server for Alpic
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_mcp.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_mcp.txt

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "mcp_server_lechat.py"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile created")

def create_deployment_script():
    """Create deployment script for Alpic."""
    
    script_content = """#!/bin/bash
# Alpic deployment script for OuiComply MCP Server

echo "🚀 Deploying OuiComply MCP Server to Alpic..."

# Check if alpic CLI is installed
if ! command -v alpic &> /dev/null; then
    echo "❌ Alpic CLI not found. Please install it first."
    echo "   Visit: https://alpic.ai/docs/installation"
    exit 1
fi

# Check if logged in
if ! alpic whoami &> /dev/null; then
    echo "❌ Not logged in to Alpic. Please run: alpic login"
    exit 1
fi

# Deploy the application
echo "📦 Deploying application..."
alpic deploy --config alpic.json

echo "✅ Deployment complete!"
echo "🔗 Your MCP Server will be available at the provided URL"
echo "📋 Use the MCP endpoint for Le Chat integration"
"""
    
    with open("deploy_to_alpic.sh", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    # Make it executable
    os.chmod("deploy_to_alpic.sh", 0o755)
    
    print("✅ Deployment script created: deploy_to_alpic.sh")

def create_test_script():
    """Create test script for deployed MCP server."""
    
    test_script = """#!/usr/bin/env python3
'''
Test script for deployed OuiComply MCP Server on Alpic.
'''

import requests
import json
import sys

def test_mcp_server(base_url):
    '''Test the deployed MCP server.'''
    
    print(f"🧪 Testing MCP Server at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test MCP endpoint
    print("\\n2. Testing MCP endpoint...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP initialize successful")
            print(f"   Server: {result.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ MCP initialize failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP test error: {e}")
        return False
    
    # Test tools list
    print("\\n3. Testing tools list...")
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": "test-2",
            "method": "tools/list"
        }
        
        response = requests.post(
            f"{base_url}/mcp",
            json=tools_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            print(f"❌ Tools list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools test error: {e}")
        return False
    
    # Test Le Chat integration
    print("\\n4. Testing Le Chat integration...")
    try:
        response = requests.get(f"{base_url}/lechat/integration", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Le Chat integration ready")
            print(f"   MCP Endpoint: {result.get('mcp_endpoint', 'Unknown')}")
            print(f"   SSE Endpoint: {result.get('sse_endpoint', 'Unknown')}")
            print(f"   Tools: {result.get('tools', 0)}")
        else:
            print(f"❌ Le Chat integration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Le Chat test error: {e}")
        return False
    
    print("\\n🎉 All tests passed! MCP Server is ready for Le Chat integration.")
    return True

def main():
    '''Main test function.'''
    if len(sys.argv) != 2:
        print("Usage: python test_alpic_deployment.py <BASE_URL>")
        print("Example: python test_alpic_deployment.py https://your-app.alpic.ai")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    if test_mcp_server(base_url):
        print("\\n📋 Next steps:")
        print(f"1. Configure Le Chat to use: {base_url}/mcp")
        print(f"2. Use SSE endpoint: {base_url}/mcp/sse")
        print("3. Test document analysis through Le Chat")
    else:
        print("\\n❌ Some tests failed. Check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open("test_alpic_deployment.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_alpic_deployment.py")

def main():
    """Main function to create Alpic deployment files."""
    print("🚀 Creating Alpic deployment configuration...")
    print("=" * 50)
    
    # Create configuration files
    config = create_alpic_config()
    create_dockerfile()
    create_deployment_script()
    create_test_script()
    
    print("\n✅ Alpic deployment files created!")
    print("\n📋 Files created:")
    print("   - alpic.json (Alpic configuration)")
    print("   - Dockerfile (Container configuration)")
    print("   - deploy_to_alpic.sh (Deployment script)")
    print("   - test_alpic_deployment.py (Test script)")
    
    print("\n🚀 Next steps:")
    print("1. Install Alpic CLI: https://alpic.ai/docs/installation")
    print("2. Login to Alpic: alpic login")
    print("3. Deploy: ./deploy_to_alpic.sh")
    print("4. Test: python test_alpic_deployment.py <YOUR_ALPIC_URL>")
    
    print("\n🔧 Le Chat Integration:")
    print("   - MCP Endpoint: <YOUR_ALPIC_URL>/mcp")
    print("   - SSE Endpoint: <YOUR_ALPIC_URL>/mcp/sse")
    print("   - Health Check: <YOUR_ALPIC_URL>/health")

if __name__ == "__main__":
    main()
