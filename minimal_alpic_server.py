#!/usr/bin/env python3
"""
Minimal Alpic Server - Ultra-simple deployment for Alpic

This is the most basic server possible for Alpic deployment.
Uses only Python standard library with minimal overhead.

Author: OuiComply Team
Version: 1.0.0
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class MinimalHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","service":"OuiComply MCP Server","version":"1.0.0","mcp_server":"running","transport":"streamable-http"}')
        elif self.path == '/oauth/metadata':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"jsonrpc":"2.0","id":"alpic-request","result":{"oauth":{"version":"1.0.0","server_name":"ouicomply-mcp","capabilities":{"tools":true,"resources":true,"prompts":false,"logging":true},"status":"ready","transport":"streamable-http"}}}')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"message":"OuiComply MCP Server is running","version":"1.0.0","endpoints":{"health":"/health","oauth_metadata":"/oauth/metadata","mcp":"streamable-http"}}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/oauth/metadata':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"jsonrpc":"2.0","id":"alpic-request","result":{"oauth":{"version":"1.0.0","server_name":"ouicomply-mcp","capabilities":{"tools":true,"resources":true,"prompts":false,"logging":true},"status":"ready","transport":"streamable-http"}}}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting Minimal Alpic Server on {host}:{port}")
    
    try:
        server = HTTPServer((host, port), MinimalHandler)
        print("Server started!")
        server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
