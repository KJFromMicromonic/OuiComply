#!/usr/bin/env python3
"""
OuiComply MCP Server with Local Network Access

This script starts the MCP HTTP server and makes it accessible on your local network
without requiring ngrok. Perfect for testing within your local network.
"""

import asyncio
import json
import logging
import os
import socket
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


class LocalNetworkMCPServer:
    """
    MCP Server with local network access for testing.
    
    This server provides HTTP endpoints accessible on your local network,
    making it perfect for testing without requiring ngrok or external tunnels.
    """
    
    def __init__(self):
        self.config = get_config()
        self.mcp_server = OuiComplyMCPServer()
        self.server = None
        self.port = int(os.getenv('PORT', str(self.config.server_port)))
        self.local_ip = self._get_local_ip()
        
    def _get_local_ip(self) -> str:
        """Get the local IP address of this machine."""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception:
            return "127.0.0.1"
    
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
                    "server": "OuiComply MCP Server (Local Network)",
                    "version": self.config.server_version,
                    "endpoint": "/mcp",
                    "methods": ["POST", "GET"],
                    "protocol": "MCP over HTTP",
                    "authentication": "none",
                    "local_ip": self.local_ip,
                    "port": self.port,
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
                "local_ip": self.local_ip,
                "port": self.port,
                "uptime": "running"
            })
        
        async def info_handler(request):
            """Handle server info requests."""
            return web.json_response({
                "authentication_required": False,
                "server": self.config.server_name,
                "version": self.config.server_version,
                "local_ip": self.local_ip,
                "port": self.port,
                "endpoints": {
                    "/mcp": "MCP protocol endpoint (POST/GET)",
                    "/ssc": "SSC compatible endpoint (POST/GET)",
                    "/health": "Health check endpoint",
                    "/info": "Server information endpoint"
                },
                "tools_available": len(self.mcp_server.server._tools),
                "resources_available": len(self.mcp_server.server._resources),
                "access_urls": {
                    "localhost": f"http://localhost:{self.port}",
                    "local_network": f"http://{self.local_ip}:{self.port}",
                    "any_device_on_network": f"http://{self.local_ip}:{self.port}"
                }
            })
        
        async def ssc_handler(request):
            """Handle SSC requests (LeChat compatible)."""
            # For GET requests, return server info
            if request.method == 'GET':
                return web.json_response({
                    "server": "OuiComply MCP Server (SSC Compatible - Local Network)",
                    "version": self.config.server_version,
                    "endpoint": "/ssc",
                    "methods": ["POST", "GET"],
                    "protocol": "MCP over HTTP (SSC)",
                    "authentication": "none",
                    "lechat_compatible": True,
                    "local_ip": self.local_ip,
                    "port": self.port
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

    async def run(self):
        """Run the MCP server with local network access."""
        print("🚀 Starting OuiComply MCP Server with Local Network Access...")
        
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return
        
        # Print configuration summary
        print_config_summary()
        
        # Create HTTP server
        app = await self.create_http_server()
        
        # Start the server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        print(f"🎯 MCP HTTP Server running on port {self.port}")
        print(f"🔗 Localhost URL: http://localhost:{self.port}")
        print(f"🌐 Local Network URL: http://{self.local_ip}:{self.port}")
        print(f"📊 Health check: http://{self.local_ip}:{self.port}/health")
        print(f"ℹ️  Server info: http://{self.local_ip}:{self.port}/info")
        print(f"🔧 MCP endpoints: http://{self.local_ip}:{self.port}/mcp (POST/GET)")
        print(f"🔧 SSC endpoints: http://{self.local_ip}:{self.port}/ssc (POST/GET) - LeChat compatible")
        print(f"🔓 No authentication required - server is open for all requests")
        print(f"🤖 LeChat will detect this as MCP server due to 'mcp'/'ssc' in URL")
        print()
        print("=" * 80)
        print("🎉 MCP SERVER IS NOW ACCESSIBLE ON YOUR LOCAL NETWORK!")
        print("=" * 80)
        print()
        print("For ALPIC integration:")
        print(f"  - Use this URL: http://{self.local_ip}:{self.port}/mcp")
        print(f"  - Or this URL: http://{self.local_ip}:{self.port}/ssc")
        print()
        print("For testing from other devices on your network:")
        print(f"  - Health check: curl http://{self.local_ip}:{self.port}/health")
        print(f"  - Server info: curl http://{self.local_ip}:{self.port}/info")
        print()
        print("For testing from this machine:")
        print(f"  - Health check: curl http://localhost:{self.port}/health")
        print(f"  - Server info: curl http://localhost:{self.port}/info")
        print()
        print("⚠️  Note: This server is only accessible from devices on your local network.")
        print("   For external access, you'll need to set up ngrok or another tunneling service.")
        print()
        
        # Try to open the health check in browser
        try:
            webbrowser.open(f"http://localhost:{self.port}/health")
        except Exception:
            pass
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            print("🧹 Cleaning up...")
            await runner.cleanup()
            print("✅ Cleanup complete")


async def main():
    """Main entry point for local network MCP server."""
    server = LocalNetworkMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
