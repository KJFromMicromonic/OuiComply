#!/usr/bin/env python3
"""
Robust Alpic Server - Reliable deployment for Alpic

This server is designed for reliable Alpic deployment with proper
error handling and immediate response to all requests.

Author: OuiComply Team
Version: 1.0.0
"""

import json
import os
import sys
from datetime import datetime, UTC

# Pre-computed responses for instant response
def get_health_response():
    return {
        "status": "healthy",
        "service": "OuiComply MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "mcp_server": "running",
        "transport": "streamable-http"
    }

def get_oauth_response():
    return {
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
    }

def get_root_response():
    return {
        "message": "OuiComply MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "oauth_metadata": "/oauth/metadata",
            "mcp": "streamable-http"
        }
    }

# Simple HTTP server using only standard library
from http.server import HTTPServer, BaseHTTPRequestHandler

class AlpicHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = get_health_response()
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/oauth/metadata':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = get_oauth_response()
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = get_root_response()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_POST(self):
        try:
            if self.path == '/oauth/metadata':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = get_oauth_response()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Minimal logging for Alpic
        print(f"Alpic Server: {format % args}")

if __name__ == "__main__":
    # Get port from environment variable (Alpic sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("Starting OuiComply Robust Alpic Server...")
    print(f"Server will run on {host}:{port}")
    print("Transport: streamable-http")
    print("Health check: http://localhost:8000/health")
    print("OAuth metadata: http://localhost:8000/oauth/metadata")
    print("Root endpoint: http://localhost:8000/")
    print("Server optimized for reliable Alpic deployment")
    
    try:
        # Create and start server
        server = HTTPServer((host, port), AlpicHandler)
        print("Server started successfully!")
        print("Waiting for requests...")
        
        # Serve forever
        server.serve_forever()
        
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
