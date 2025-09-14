#!/usr/bin/env python3
"""
Startup script for the official MCP server.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_server import OuiComplyMCPServer


async def main():
    """Main entry point for the official MCP server."""
    # Get configuration from environment variables
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    print("🚀 Starting OuiComply Official MCP Server")
    print("=" * 50)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌐 URL: http://{host}:{port}")
    print("=" * 50)
    
    # Create and run the server
    server = OuiComplyMCPServer()
    await server.run(host=host, port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
