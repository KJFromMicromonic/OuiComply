#!/usr/bin/env python3
"""
Simple ngrok test server for debugging
"""

import asyncio
import json
import subprocess
import time
import webbrowser
from aiohttp import web

async def health_handler(request):
    """Health check endpoint."""
    return web.json_response({
        "status": "healthy",
        "message": "Simple test server is running",
        "timestamp": time.time()
    })

async def mcp_handler(request):
    """MCP endpoint."""
    if request.method == 'GET':
        return web.json_response({
            "server": "Simple MCP Test Server",
            "endpoint": "/mcp",
            "methods": ["POST", "GET"]
        })
    
    # Handle POST requests
    try:
        data = await request.json()
        return web.json_response({
            "jsonrpc": "2.0",
            "id": data.get('id'),
            "result": {
                "message": "MCP request received successfully",
                "method": data.get('method', 'unknown')
            }
        })
    except Exception as e:
        return web.json_response({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Error: {str(e)}"
            }
        })

async def create_app():
    """Create the web application."""
    app = web.Application()
    app.router.add_get('/health', health_handler)
    app.router.add_get('/mcp', mcp_handler)
    app.router.add_post('/mcp', mcp_handler)
    app.router.add_get('/', health_handler)
    return app

def start_ngrok(port):
    """Start ngrok tunnel."""
    try:
        cmd = ["ngrok", "http", str(port), "--log=stdout"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Try to get the URL from ngrok API
        try:
            import requests
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels.get('tunnels'):
                    return tunnels['tunnels'][0]['public_url'], process
        except Exception as e:
            print(f"Could not get ngrok URL from API: {e}")
        
        return "http://localhost:4040", process
    except Exception as e:
        print(f"Failed to start ngrok: {e}")
        return None, None

async def main():
    """Main function."""
    port = 3000
    
    print(f"🚀 Starting simple test server on port {port}...")
    
    # Start ngrok
    print("🌐 Starting ngrok tunnel...")
    ngrok_url, ngrok_process = start_ngrok(port)
    
    if not ngrok_url:
        print("❌ Failed to start ngrok")
        return
    
    print(f"✅ ngrok tunnel started: {ngrok_url}")
    
    # Create and start the web app
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"🎯 Server running on port {port}")
    print(f"🔗 Local URL: http://localhost:{port}")
    print(f"🌍 Public URL: {ngrok_url}")
    print(f"📊 Health check: {ngrok_url}/health")
    print(f"🔧 MCP endpoint: {ngrok_url}/mcp")
    
    # Test the endpoints
    print("\n🧪 Testing endpoints...")
    try:
        import requests
        
        # Test local health
        local_response = requests.get(f"http://localhost:{port}/health", timeout=5)
        print(f"✅ Local health check: {local_response.status_code}")
        
        # Test ngrok health
        ngrok_response = requests.get(f"{ngrok_url}/health", timeout=10)
        print(f"✅ ngrok health check: {ngrok_response.status_code}")
        
        # Test MCP endpoint
        mcp_response = requests.get(f"{ngrok_url}/mcp", timeout=10)
        print(f"✅ ngrok MCP endpoint: {mcp_response.status_code}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 SERVER IS RUNNING!")
    print("="*60)
    print(f"Use this URL for testing: {ngrok_url}")
    print("Press Ctrl+C to stop")
    
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
    finally:
        if ngrok_process:
            ngrok_process.terminate()
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
