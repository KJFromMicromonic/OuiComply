#!/usr/bin/env python3
"""
OuiComply MCP HTTP Server for ALPIC

This file provides an HTTP-based MCP server that ALPIC can connect to.
ALPIC requires HTTP/HTTPS endpoints for MCP connections, not stdio.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    import aiohttp
    from aiohttp import web
except ImportError:
    print("aiohttp is required for HTTP MCP server. Install with: pip install aiohttp")
    exit(1)

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
import sys
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import get_config, validate_config, print_config_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPHTTPServer:
    """
    HTTP-based MCP server for ALPIC deployment.
    
    This server provides HTTP endpoints that ALPIC can connect to
    for MCP communication.
    """
    
    def __init__(self):
        self.config = get_config()
        self.mcp_server = OuiComplyMCPServer()
        self.server = None
        
    async def handle_mcp_request(self, request):
        """
        Handle MCP requests from ALPIC.
        
        This method processes MCP protocol messages over HTTP.
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


# Create a simple HTTP server using aiohttp
async def create_http_server():
    """Create and configure the HTTP server."""
    
    mcp_server = MCPHTTPServer()
    
    async def mcp_handler(request):
        """Handle MCP requests."""
        response_data = await mcp_server.handle_mcp_request(request)
        return web.json_response(response_data)
    
    async def health_handler(request):
        """Handle health check requests."""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": mcp_server.config.server_name,
            "version": mcp_server.config.server_version
        })
    
    app = web.Application()
    app.router.add_post('/mcp', mcp_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', health_handler)
    
    return app


async def main():
    """Main entry point for HTTP MCP server."""
    print("Starting OuiComply MCP HTTP Server for ALPIC...")
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed")
        return
    
    # Print configuration summary
    print_config_summary()
    
    # Create HTTP server
    app = await create_http_server()
    if app is None:
        return
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', '8000'))
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"MCP HTTP Server running on port {port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"MCP endpoint: http://localhost:{port}/mcp")
    
    # Keep the server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Server stopped by user")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    import os
    asyncio.run(main())
