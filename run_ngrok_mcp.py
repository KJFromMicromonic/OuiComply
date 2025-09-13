#!/usr/bin/env python3
"""
OuiComply MCP Server with ngrok Web Exposure

This script starts the MCP HTTP server and exposes it to the web using ngrok
for testing and remote access. Perfect for ALPIC integration and testing.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import aiohttp
    from aiohttp import web
except ImportError:
    print("aiohttp is required for HTTP MCP server. Install with: pip install aiohttp")
    sys.exit(1)

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import get_config, validate_config, print_config_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NgrokMCPServer:
    """
    MCP Server with ngrok web exposure for ALPIC testing.
    
    This server provides HTTP endpoints that can be accessed via ngrok tunnel,
    making it available for remote testing and ALPIC integration.
    """
    
    def __init__(self):
        self.config = get_config()
        self.mcp_server = OuiComplyMCPServer()
        self.server = None
        self.ngrok_process = None
        self.ngrok_url = None
        self.port = int(os.getenv('PORT', str(self.config.server_port)))
        
    async def handle_mcp_request(self, request):
        """
        Handle MCP requests from ALPIC.
        
        This method processes MCP protocol messages over HTTP without authentication.
        """
        try:
            # Parse the request body
            if hasattr(request, 'json'):
                data = await request.json()
            else:
                body = await request.read()
                data = json.loads(body.decode('utf-8'))
            
            logger.info(f"Received MCP request: {data.get('method', 'unknown')}")
            
            # Handle different MCP methods
            method = data.get('method')
            params = data.get('params', {})
            
            if method == 'initialize':
                response = await self._handle_initialize(params)
            elif method == 'tools/list':
                response = await self._handle_list_tools(params)
            elif method == 'tools/call':
                response = await self._handle_call_tool(params)
            elif method == 'resources/list':
                response = await self._handle_list_resources(params)
            elif method == 'resources/read':
                response = await self._handle_read_resource(params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get('id'),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling MCP request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": data.get('id') if 'data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _handle_initialize(self, params):
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": params.get('id'),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": self.config.server_name,
                    "version": self.config.server_version
                }
            }
        }
    
    async def _handle_list_tools(self, params):
        """Handle MCP tools/list request."""
        # Get tools from the MCP server
        tools = []
        for tool in self.mcp_server.server._tools.values():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            })
        
        return {
            "jsonrpc": "2.0",
            "id": params.get('id'),
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_call_tool(self, params):
        """Handle MCP tools/call request."""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        # Call the tool through the MCP server
        try:
            result = await self.mcp_server._handle_call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "result": {
                    "content": [{"type": "text", "text": content.text} for content in result]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def _handle_list_resources(self, params):
        """Handle MCP resources/list request."""
        # Get resources from the MCP server
        resources = []
        for resource in self.mcp_server.server._resources.values():
            resources.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mimeType
            })
        
        return {
            "jsonrpc": "2.0",
            "id": params.get('id'),
            "result": {
                "resources": resources
            }
        }
    
    async def _handle_read_resource(self, params):
        """Handle MCP resources/read request."""
        uri = params.get('uri')
        
        try:
            # Read resource through the MCP server
            content = await self.mcp_server._handle_read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "result": {
                    "contents": [{"type": "text", "text": content}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": params.get('id'),
                "error": {
                    "code": -32603,
                    "message": f"Resource read failed: {str(e)}"
                }
            }

    async def create_http_server(self):
        """Create and configure the HTTP server."""
        
        async def mcp_handler(request):
            """Handle MCP requests."""
            # For GET requests, return server info
            if request.method == 'GET':
                return web.json_response({
                    "server": "OuiComply MCP Server (ngrok)",
                    "version": self.config.server_version,
                    "endpoint": "/mcp",
                    "methods": ["POST", "GET"],
                    "protocol": "MCP over HTTP",
                    "authentication": "none",
                    "ngrok_url": self.ngrok_url,
                    "local_url": f"http://localhost:{self.port}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # For POST requests, handle MCP protocol
            response_data = await self.handle_mcp_request(request)
            if isinstance(response_data, dict):
                return web.json_response(response_data)
            else:
                return response_data
        
        async def health_handler(request):
            """Handle health check requests."""
            return web.json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "server": self.config.server_name,
                "version": self.config.server_version,
                "authentication": "none",
                "ngrok_url": self.ngrok_url,
                "local_url": f"http://localhost:{self.port}",
                "uptime": "running"
            })
        
        async def info_handler(request):
            """Handle server info requests."""
            return web.json_response({
                "authentication_required": False,
                "server": self.config.server_name,
                "version": self.config.server_version,
                "ngrok_url": self.ngrok_url,
                "local_url": f"http://localhost:{self.port}",
                "endpoints": {
                    "/mcp": "MCP protocol endpoint (POST/GET)",
                    "/ssc": "SSC compatible endpoint (POST/GET)",
                    "/health": "Health check endpoint",
                    "/info": "Server information endpoint"
                },
                "tools_available": len(self.mcp_server.server._tools),
                "resources_available": len(self.mcp_server.server._resources)
            })
        
        async def ssc_handler(request):
            """Handle SSC requests (LeChat compatible)."""
            # For GET requests, return server info
            if request.method == 'GET':
                return web.json_response({
                    "server": "OuiComply MCP Server (SSC Compatible - ngrok)",
                    "version": self.config.server_version,
                    "endpoint": "/ssc",
                    "methods": ["POST", "GET"],
                    "protocol": "MCP over HTTP (SSC)",
                    "authentication": "none",
                    "lechat_compatible": True,
                    "ngrok_url": self.ngrok_url,
                    "local_url": f"http://localhost:{self.port}"
                })
            
            # For POST requests, handle MCP protocol (same as /mcp)
            response_data = await self.handle_mcp_request(request)
            if isinstance(response_data, dict):
                return web.json_response(response_data)
            else:
                return response_data
        
        app = web.Application()
        
        # MCP endpoints - LeChat looks for "mcp" in the URL
        app.router.add_post('/mcp', mcp_handler)
        app.router.add_post('/mcp/', mcp_handler)
        app.router.add_get('/mcp', mcp_handler)
        app.router.add_get('/mcp/', mcp_handler)
        
        # SSC endpoints - Alternative naming for LeChat compatibility
        app.router.add_post('/ssc', ssc_handler)
        app.router.add_post('/ssc/', ssc_handler)
        app.router.add_get('/ssc', ssc_handler)
        app.router.add_get('/ssc/', ssc_handler)
        
        # Health and info endpoints
        app.router.add_get('/health', health_handler)
        app.router.add_get('/info', info_handler)
        app.router.add_get('/', health_handler)
        
        return app

    def start_ngrok(self) -> Optional[str]:
        """
        Start ngrok tunnel for the MCP server.
        
        Returns:
            The ngrok public URL if successful, None otherwise
        """
        try:
            # Start ngrok tunnel
            cmd = ["ngrok", "http", str(self.port), "--log=stdout"]
            self.ngrok_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for ngrok to start and get the URL
            time.sleep(3)  # Give ngrok time to start
            
            # Try to get the ngrok URL from the API
            try:
                import requests
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json()
                    if tunnels.get('tunnels'):
                        self.ngrok_url = tunnels['tunnels'][0]['public_url']
                        return self.ngrok_url
            except Exception as e:
                logger.warning(f"Could not get ngrok URL from API: {e}")
            
            # Fallback: try to parse from ngrok output
            logger.info("ngrok started, but could not determine public URL automatically")
            logger.info("Check ngrok web interface at http://localhost:4040")
            return "http://localhost:4040"
            
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            return None

    def stop_ngrok(self):
        """Stop the ngrok process."""
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process.wait()
            self.ngrok_process = None

    async def run(self):
        """Run the MCP server with ngrok."""
        print("🚀 Starting OuiComply MCP Server with ngrok...")
        
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return
        
        # Print configuration summary
        print_config_summary()
        
        # Start ngrok tunnel
        print(f"🌐 Starting ngrok tunnel on port {self.port}...")
        ngrok_url = self.start_ngrok()
        
        if not ngrok_url:
            print("❌ Failed to start ngrok tunnel")
            return
        
        self.ngrok_url = ngrok_url
        print(f"✅ ngrok tunnel started: {ngrok_url}")
        
        # Create HTTP server
        app = await self.create_http_server()
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        print(f"🎯 MCP HTTP Server running on port {self.port}")
        print(f"🔗 Local URL: http://localhost:{self.port}")
        print(f"🌍 Public URL: {ngrok_url}")
        print(f"📊 Health check: {ngrok_url}/health")
        print(f"ℹ️  Server info: {ngrok_url}/info")
        print(f"🔧 MCP endpoints: {ngrok_url}/mcp (POST/GET)")
        print(f"🔧 SSC endpoints: {ngrok_url}/ssc (POST/GET) - LeChat compatible")
        print(f"🔓 No authentication required - server is open for all requests")
        print(f"🤖 LeChat will detect this as MCP server due to 'mcp'/'ssc' in URL")
        print(f"📱 ngrok web interface: http://localhost:4040")
        print()
        print("=" * 80)
        print("🎉 MCP SERVER IS NOW ACCESSIBLE VIA THE WEB!")
        print("=" * 80)
        print()
        print("For ALPIC integration:")
        print(f"  - Use this URL: {ngrok_url}/mcp")
        print(f"  - Or this URL: {ngrok_url}/ssc")
        print()
        print("For testing:")
        print(f"  - Health check: curl {ngrok_url}/health")
        print(f"  - Server info: curl {ngrok_url}/info")
        print()
        
        # Try to open the health check in browser
        try:
            webbrowser.open(f"{ngrok_url}/health")
        except Exception:
            pass
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            print("🧹 Cleaning up...")
            self.stop_ngrok()
            await runner.cleanup()
            print("✅ Cleanup complete")


async def main():
    """Main entry point for ngrok MCP server."""
    server = NgrokMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
