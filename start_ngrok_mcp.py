#!/usr/bin/env python3
"""
Start OuiComply MCP Server with ngrok integration for Le Chat testing.

This script starts the FastAPI MCP Server and exposes it via ngrok
for external access and Le Chat integration.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

import requests
import uvicorn
from pyngrok import ngrok, conf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_ngrok_installed():
    """Check if ngrok is installed and accessible."""
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"ngrok found: {result.stdout.strip()}")
            return True
        else:
            logger.error("ngrok not found in PATH")
            return False
    except FileNotFoundError:
        logger.error("ngrok not installed")
        return False


def start_ngrok_tunnel(port: int = 8000):
    """Start ngrok tunnel for the FastAPI server."""
    try:
        # Configure ngrok
        conf.get_default().region = "us"  # Use US region for better performance
        
        # Create tunnel
        tunnel = ngrok.connect(port, proto="http")
        public_url = tunnel.public_url
        
        logger.info(f"ngrok tunnel created: {public_url}")
        logger.info(f"Local server: http://localhost:{port}")
        logger.info(f"Public URL: {public_url}")
        
        return tunnel, public_url
    except Exception as e:
        logger.error(f"Failed to create ngrok tunnel: {e}")
        return None, None


def test_server_health(port: int = 8000):
    """Test if the FastAPI server is running and healthy."""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            logger.info("FastAPI server is healthy")
            return True
        else:
            logger.error(f"Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Server health check failed: {e}")
        return False


def test_lechat_integration(public_url: str):
    """Test Le Chat integration endpoints."""
    try:
        # Test integration info endpoint
        response = requests.get(f"{public_url}/lechat/integration", timeout=10)
        if response.status_code == 200:
            logger.info("Le Chat integration endpoint is working")
            integration_info = response.json()
            logger.info(f"Integration status: {integration_info.get('integration_status')}")
            return True
        else:
            logger.error(f"Le Chat integration test failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Le Chat integration test failed: {e}")
        return False


def create_lechat_test_script(public_url: str):
    """Create a test script for Le Chat integration."""
    test_script = f'''#!/usr/bin/env python3
"""
Le Chat Integration Test Script

This script tests the OuiComply MCP Server integration with Le Chat.
Server URL: {public_url}
"""

import requests
import json

def test_lechat_integration():
    """Test Le Chat integration endpoints."""
    base_url = "{public_url}"
    
    print("🔍 Testing Le Chat Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\\n1. Testing server health...")
    try:
        response = requests.get(f"{{base_url}}/health")
        if response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print(f"   ❌ Health check failed: {{response.status_code}}")
            return
    except Exception as e:
        print(f"   ❌ Health check failed: {{e}}")
        return
    
    # Test 2: Integration info
    print("\\n2. Testing integration info...")
    try:
        response = requests.get(f"{{base_url}}/lechat/integration")
        if response.status_code == 200:
            info = response.json()
            print(f"   ✅ Integration status: {{info.get('integration_status')}}")
            print(f"   ✅ Memory MCP: {{info.get('memory_mcp')}}")
        else:
            print(f"   ❌ Integration info failed: {{response.status_code}}")
            return
    except Exception as e:
        print(f"   ❌ Integration info failed: {{e}}")
        return
    
    # Test 3: Document analysis with memory
    print("\\n3. Testing document analysis with memory...")
    try:
        test_request = {{
            "document_content": "This is a test service agreement for compliance analysis.",
            "document_name": "test_agreement.txt",
            "team_context": "Legal Team",
            "compliance_frameworks": ["gdpr", "sox", "ccpa"]
        }}
        
        response = requests.post(
            f"{{base_url}}/lechat/test",
            json=test_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis completed successfully")
            print(f"   ✅ Document: {{result.get('document_name')}}")
            print(f"   ✅ Team: {{result.get('team_context')}}")
            print(f"   ✅ Memory integration: {{result.get('memory_integration')}}")
        else:
            print(f"   ❌ Analysis failed: {{response.status_code}}")
            print(f"   Response: {{response.text}}")
            return
    except Exception as e:
        print(f"   ❌ Analysis failed: {{e}}")
        return
    
    print("\\n🎉 All Le Chat integration tests passed!")
    print(f"\\n📋 Integration Summary:")
    print(f"   Server URL: {{base_url}}")
    print(f"   Status: Ready for Le Chat integration")
    print(f"   Memory MCP: Enabled")
    print(f"   Endpoints: /lechat/test, /analyze-with-memory, /memory/*")

if __name__ == "__main__":
    test_lechat_integration()
'''
    
    with open("test_lechat_integration.py", "w") as f:
        f.write(test_script)
    
    logger.info("Created test_lechat_integration.py for Le Chat testing")


def main():
    """Main function to start the MCP Server with ngrok."""
    print("🚀 Starting OuiComply MCP Server with ngrok")
    print("=" * 60)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        print("❌ ngrok is not installed. Please install ngrok first:")
        print("   https://ngrok.com/download")
        return
    
    # Start ngrok tunnel
    print("\\n1. Starting ngrok tunnel...")
    tunnel, public_url = start_ngrok_tunnel()
    if not tunnel:
        print("❌ Failed to start ngrok tunnel")
        return
    
    print(f"✅ ngrok tunnel started: {public_url}")
    
    # Start FastAPI server in background
    print("\\n2. Starting FastAPI MCP Server...")
    try:
        # Start server in a separate process
        server_process = subprocess.Popen([
            sys.executable, "fastapi_mcp_server.py"
        ])
        
        # Wait for server to start
        print("   Waiting for server to start...")
        time.sleep(5)
        
        # Test server health
        if test_server_health():
            print("✅ FastAPI server started successfully")
        else:
            print("❌ FastAPI server failed to start")
            return
        
        # Test Le Chat integration
        print("\\n3. Testing Le Chat integration...")
        if test_lechat_integration(public_url):
            print("✅ Le Chat integration is working")
        else:
            print("❌ Le Chat integration test failed")
            return
        
        # Create test script
        create_lechat_test_script(public_url)
        
        print("\\n🎉 OuiComply MCP Server is ready!")
        print("=" * 60)
        print(f"📡 Public URL: {public_url}")
        print(f"🏠 Local URL: http://localhost:8000")
        print(f"📋 Le Chat Integration: Ready")
        print(f"🧠 Memory MCP: Enabled")
        print("\\n📝 Available endpoints:")
        print(f"   • {public_url}/lechat/integration")
        print(f"   • {public_url}/lechat/test")
        print(f"   • {public_url}/analyze-with-memory")
        print(f"   • {public_url}/memory/update")
        print(f"   • {public_url}/memory/retrieve")
        print("\\n🔧 Test the integration:")
        print("   python test_lechat_integration.py")
        print("\\n⏹️  Press Ctrl+C to stop the server")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n\\n🛑 Stopping server...")
            server_process.terminate()
            ngrok.disconnect(tunnel.public_url)
            print("✅ Server stopped")
    
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        if tunnel:
            ngrok.disconnect(tunnel.public_url)


if __name__ == "__main__":
    main()
