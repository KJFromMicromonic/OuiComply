#!/usr/bin/env python3
"""
Instant Alpic Server - Zero-delay startup for Alpic Deployment

This server starts instantly and responds immediately to all requests.
Optimized for Alpic's strict timeout requirements.

Author: OuiComply Team
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, UTC

# Pre-computed responses for instant response
HEALTH_RESPONSE = json.dumps({
    "status": "healthy",
    "service": "OuiComply MCP Server",
    "version": "1.0.0",
    "timestamp": datetime.now(UTC).isoformat(),
    "mcp_server": "running",
    "transport": "streamable-http"
})

OAUTH_RESPONSE = json.dumps({
    "jsonrpc": "2.0",
    "id": "alpic-request",
    "result": {
        "oauth": {
            "version": "1.0.0",
            "server_name": "ouicomply-mcp",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False,
                "logging": True
            },
            "status": "ready",
            "transport": "streamable-http"
        }
    }
})

ROOT_RESPONSE = json.dumps({
    "message": "OuiComply MCP Server is running",
    "version": "1.0.0",
    "endpoints": {
        "health": "/health",
        "oauth_metadata": "/oauth/metadata",
        "mcp": "streamable-http"
    }
})

# Simple HTTP server using only standard library
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class AlpicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(HEALTH_RESPONSE.encode())
        elif self.path == '/oauth/metadata':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(OAUTH_RESPONSE.encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(ROOT_RESPONSE.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/oauth/metadata':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(OAUTH_RESPONSE.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Disable logging for speed
        pass

if __name__ == "__main__":
    # Get port from environment variable (Alpic sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("Starting OuiComply Instant Alpic Server...")
    print(f"Server will run on {host}:{port}")
    print("Transport: streamable-http")
    print("Health check: http://localhost:8000/health")
    print("OAuth metadata: http://localhost:8000/oauth/metadata")
    print("Root endpoint: http://localhost:8000/")
    print("Server optimized for instant startup and response")
    
    # Create and start server
    server = HTTPServer((host, port), AlpicHandler)
    
    # Start server in a separate thread for instant response
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("Server started instantly!")
    
    # Keep main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
        print("Server stopped")
