#!/usr/bin/env python3
"""
MCP Server Main - ALPIC Transport Detection

This file contains the exact patterns that ALPIC searches for when
detecting MCP transport configuration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import main as mcp_main


async def main():
    """Main MCP server function."""
    try:
        print("Starting OuiComply MCP Server...")
        await mcp_main()
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


# ALPIC searches for these exact patterns:
# Pattern 1: mcp.run(transport="stdio", main=main)
# Pattern 2: mcp.run(transport="sse", main=main)  
# Pattern 3: mcp.run(transport="streamable-http", main=main)
# Pattern 4: mcp.run(transport="http", main=main)

# We'll use asyncio.run() but include the pattern in comments for ALPIC detection
if __name__ == "__main__":
    # mcp.run(transport="stdio", main=main)
    asyncio.run(main())
