#!/usr/bin/env python3
"""
Fix ngrok certificate issues and create tunnel.
"""

import os
import subprocess
import time
import requests
from pathlib import Path

def fix_ngrok_certificate():
    """Try to fix ngrok certificate issues."""
    print("🔧 Attempting to fix ngrok certificate issues...")
    
    # Try to disable certificate verification
    ngrok_config_path = Path.home() / "AppData" / "Local" / "ngrok" / "ngrok.yml"
    
    if ngrok_config_path.exists():
        print(f"✅ Found ngrok config at: {ngrok_config_path}")
        
        # Read current config
        with open(ngrok_config_path, 'r') as f:
            config = f.read()
        
        # Add certificate verification bypass
        if "insecure_skip_verify" not in config:
            config += "\n\n# Certificate verification bypass\ninsecure_skip_verify: true\n"
            
            with open(ngrok_config_path, 'w') as f:
                f.write(config)
            
            print("✅ Added certificate verification bypass to ngrok config")
        else:
            print("✅ Certificate verification bypass already configured")
    else:
        print("❌ ngrok config file not found")
        return False
    
    return True

def try_alternative_tunnel():
    """Try alternative tunneling methods."""
    print("\n🔄 Trying alternative tunneling methods...")
    
    # Method 1: Try localtunnel (if available)
    try:
        print("   Trying localtunnel...")
        result = subprocess.run(["npx", "localtunnel", "--port", "8000"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ localtunnel is available")
            return "localtunnel"
    except:
        print("   localtunnel not available")
    
    # Method 2: Try serveo
    try:
        print("   Trying serveo...")
        result = subprocess.run(["ssh", "-R", "80:localhost:8000", "serveo.net"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ serveo is available")
            return "serveo"
    except:
        print("   serveo not available")
    
    return None

def create_simple_workaround():
    """Create a simple workaround for testing."""
    print("\n🛠️  Creating simple workaround...")
    
    # Create a simple HTML page that can be used to test the API
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>OuiComply MCP Server Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }
        pre { background: #f1f1f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>OuiComply MCP Server Test Interface</h1>
        <p>This is a simple test interface for the OuiComply MCP Server.</p>
        
        <div class="test-section">
            <h3>Server Status</h3>
            <button onclick="testHealth()">Test Health</button>
            <div id="health-result" class="result"></div>
        </div>
        
        <div class="test-section">
            <h3>Le Chat Integration Test</h3>
            <button onclick="testLeChatIntegration()">Test Le Chat Integration</button>
            <div id="lechat-result" class="result"></div>
        </div>
        
        <div class="test-section">
            <h3>Document Analysis Test</h3>
            <button onclick="testDocumentAnalysis()">Test Document Analysis</button>
            <div id="analysis-result" class="result"></div>
        </div>
        
        <div class="test-section">
            <h3>Memory Update Test</h3>
            <button onclick="testMemoryUpdate()">Test Memory Update</button>
            <div id="memory-result" class="result"></div>
        </div>
    </div>

    <script>
        const baseUrl = 'http://localhost:8000';
        
        async function testHealth() {
            try {
                const response = await fetch(baseUrl + '/health');
                const data = await response.json();
                document.getElementById('health-result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('health-result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function testLeChatIntegration() {
            try {
                const response = await fetch(baseUrl + '/lechat/integration');
                const data = await response.json();
                document.getElementById('lechat-result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('lechat-result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function testDocumentAnalysis() {
            try {
                const response = await fetch(baseUrl + '/lechat/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        document_content: "This is a test service agreement for compliance analysis.",
                        document_name: "test_agreement.txt",
                        team_context: "Legal Team",
                        compliance_frameworks: ["gdpr", "sox", "ccpa"]
                    })
                });
                const data = await response.json();
                document.getElementById('analysis-result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('analysis-result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
        
        async function testMemoryUpdate() {
            try {
                const response = await fetch(baseUrl + '/memory/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        team_id: "legal_team",
                        memory_type: "compliance",
                        updates: {
                            compliance_rules: ["Test rule 1", "Test rule 2"],
                            risk_tolerance: "low"
                        }
                    })
                });
                const data = await response.json();
                document.getElementById('memory-result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('memory-result').innerHTML = '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        }
    </script>
</body>
</html>
    """
    
    with open("mcp_server_test.html", "w") as f:
        f.write(html_content)
    
    print("✅ Created test interface: mcp_server_test.html")
    print("   Open this file in your browser to test the MCP Server")
    print("   Note: This only works locally, not for Le Chat integration")

def main():
    """Main function to fix ngrok and create tunnel."""
    print("🚀 OuiComply MCP Server - Tunnel Fix")
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
    
    # Try to fix ngrok certificate issues
    if fix_ngrok_certificate():
        print("\n🔄 Trying ngrok again with fixed configuration...")
        try:
            from pyngrok import ngrok, conf
            conf.get_default().insecure_skip_verify = True
            
            tunnel = ngrok.connect(8000, proto="http")
            public_url = tunnel.public_url
            
            print(f"✅ ngrok tunnel created successfully!")
            print(f"   Public URL: {public_url}")
            print(f"   Local URL: http://localhost:8000")
            print(f"   Web Interface: http://127.0.0.1:4040")
            
            # Test the tunnel
            print(f"\n🧪 Testing tunnel...")
            time.sleep(3)
            
            try:
                response = requests.get(f"{public_url}/health", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Tunnel test successful!")
                    print(f"\n🎉 Ready for Le Chat integration!")
                    print(f"Use this URL in Le Chat: {public_url}")
                    return
                else:
                    print(f"⚠️  Tunnel created but server not responding: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Tunnel created but test failed: {e}")
                print("   Make sure the MCP Server is running: python fastapi_simple.py")
                return
                
        except Exception as e:
            print(f"❌ ngrok still failed: {e}")
    
    # Try alternative tunneling methods
    alternative = try_alternative_tunnel()
    if alternative:
        print(f"✅ Found alternative: {alternative}")
        return
    
    # Create workaround
    create_simple_workaround()
    
    print("\n📋 Next Steps:")
    print("1. For Le Chat integration, you'll need to:")
    print("   - Use a different tunneling service (like localtunnel, serveo, or cloudflare tunnel)")
    print("   - Deploy the MCP Server to a cloud service")
    print("   - Use a VPN or port forwarding")
    print("2. For local testing, use the created HTML file")

if __name__ == "__main__":
    main()
