#!/usr/bin/env python3
"""
Start OuiComply FastMCP Server

This script starts the FastMCP server that exposes all MCP tools and features
as REST API endpoints accessible via /mcp/{function} routes.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_fastmcp_server import app
from health_server import run_health_server

async def main():
    """Start the FastMCP server."""
    # Get port from environment variable (Railway/Alpic sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("Starting OuiComply FastMCP Server...")
    print(f"Server will run on {host}:{port}")
    print("Server will expose MCP tools and resources via HTTP endpoints")
    print("Available tools:")
    print("  - analyze_document: AI-powered document compliance analysis")
    print("  - update_memory: Store team compliance insights")
    print("  - get_compliance_status: Get team compliance status")
    print("  - automate_compliance_workflow: Automate compliance workflows")
    print("\nAvailable resources:")
    print("  - compliance_frameworks: Get compliance framework definitions")
    print("  - legal_templates: Get legal document templates")
    print("  - team_memory: Get team memory and insights")
    print("\nStarting health check server...")
    
    # Start health check server in a separate thread
    health_thread = run_health_server()
    print("Health check server started on port 8001")
    print("Health check available at: http://localhost:8001/health")
    
    print("\nStarting MCP server...")
    
    # Run the FastMCP server
    # FastMCP uses different methods for different transport types
    try:
        # Try SSE transport (most common for web deployment)
        print(f"Starting MCP server with SSE transport on {host}:{port}")
        await app.run_sse_async()
    except Exception as e:
        print(f"SSE transport failed: {e}")
        try:
            # Fallback to stdio transport
            print("Using stdio transport - server will run via stdin/stdout")
            await app.run_stdio_async()
        except Exception as e2:
            print(f"All transport methods failed: {e2}")
            print("Please check your FastMCP installation and configuration")

if __name__ == "__main__":
    asyncio.run(main())
