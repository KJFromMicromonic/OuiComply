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
import uvicorn
import mcp

# Alpic MCP Transport Detection Pattern
# This pattern is specifically for Alpic deployment detection
mcp.run(transport="streamable-http")

def main():
    """Start the FastMCP server with Starlette."""
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
    print("\nHealth check available at: /health")
    print("\nStarting server...")
    
    # Run the Starlette application with uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
