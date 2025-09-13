#!/usr/bin/env python3
"""
ALPIC MCP Runner - Simple MCP transport detection for ALPIC

This script provides the exact pattern that ALPIC looks for when detecting
MCP transport configuration.
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


if __name__ == "__main__":
    # This is the exact pattern ALPIC looks for
    asyncio.run(main())
