#!/usr/bin/env python3
"""
Start OuiComply MCP Server for Alpic Deployment

This script starts the MCP server with proper transport patterns
that Alpic can detect for deployment.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import MCP modules
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server
    import mcp
except ImportError:
    print("MCP not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server
    import mcp

# Alpic MCP Transport Detection Patterns
# These patterns ensure Alpic can detect the MCP transport type

# Pattern 1: Standard MCP run with streamable HTTP
mcp.run(transport="streamable-http")

# Pattern 2: Alternative patterns for detection
def run_mcp_server():
    """Run MCP server with streamable HTTP transport."""
    print("Starting OuiComply MCP Server...")
    print("Transport: streamable-http")
    print("Server will run on port 8000")
    
    # Import the server after MCP is available
    from mcp_server_standard import server
    
    # Run with streamable HTTP transport
    asyncio.run(streamable_http_server(server))

if __name__ == "__main__":
    run_mcp_server()
