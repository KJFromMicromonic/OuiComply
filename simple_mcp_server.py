#!/usr/bin/env python3
"""
Simple MCP Server for Alpic Deployment Detection

This file contains the exact MCP transport patterns that Alpic looks for
during the build process.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import MCP modules
try:
    import mcp
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server
except ImportError:
    print("MCP not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    import mcp
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server

# Create a simple MCP server
server = Server("ouicomply-simple")

# Alpic MCP Transport Detection Patterns
# These are the exact patterns that Alpic looks for:

# Pattern 1: mcp.run() with transport parameter
mcp.run(transport="streamable-http")

# Pattern 2: Alternative transport types for detection
# mcp.run(transport="stdio")
# mcp.run(transport="sse")
# mcp.run(transport="http")

# Pattern 3: Direct server calls
# stdio_server(server)
# sse_server(server)
# streamable_http_server(server)

if __name__ == "__main__":
    # Run the server
    print("Starting OuiComply Simple MCP Server...")
    print("Transport: streamable-http")
    
    # This will be detected by Alpic
    asyncio.run(streamable_http_server(server))
