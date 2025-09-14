#!/usr/bin/env python3
"""
Health Check Server for OuiComply MCP Server

This server provides a simple health check endpoint for deployment platforms
like Railway and Alpic. It runs alongside the main MCP server.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import json
import os
from datetime import datetime, UTC
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self.send_health_response()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send health check response."""
        health_data = {
            "status": "healthy",
            "service": "OuiComply MCP Server",
            "version": "1.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "mcp_server": "running"
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(health_data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def start_health_server(port=8001):
    """Start the health check server."""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"Health check server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Health server error: {e}")

def run_health_server():
    """Run health server in a separate thread."""
    health_port = int(os.environ.get("HEALTH_PORT", 8001))
    health_thread = Thread(target=start_health_server, args=(health_port,), daemon=True)
    health_thread.start()
    return health_thread

if __name__ == "__main__":
    # Run health server directly for testing
    start_health_server()
