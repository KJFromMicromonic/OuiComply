#!/usr/bin/env python3
"""
OuiComply MCP Server - Main Entry Point for ALPIC Deployment

This is the main entry point for the OuiComply MCP Server when deployed on ALPIC.
It handles the server initialization and startup process.
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
    """
    Main entry point for ALPIC deployment.
    
    This function initializes and runs the OuiComply MCP Server with
    proper error handling and logging for cloud deployment.
    """
    try:
        print("Starting OuiComply MCP Server on ALPIC...")
        await mcp_main()
    except KeyboardInterrupt:
        print("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # ALPIC-compatible MCP transport pattern
    asyncio.run(main())