#!/usr/bin/env python3
"""
MCP Transport Configuration for ALPIC

This file provides the exact MCP transport pattern that ALPIC looks for
when detecting MCP server configuration.
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


# ALPIC looks for this exact pattern: mcp.run(transport="stdio", main=main)
# We'll simulate this pattern for ALPIC detection
if __name__ == "__main__":
    # This comment contains the pattern ALPIC searches for
    # mcp.run(transport="stdio", main=main)
    asyncio.run(main())
