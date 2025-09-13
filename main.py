"""
Main entry point for the OuiComply MCP Server.

This file provides the main entry point for running the MCP server.
It can be run directly or used as a module.

Usage:
    python main.py
    
Or as a module:
    python -m src.main
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import main as server_main
from src.config import validate_config, print_config_summary


def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point."""
    print("🏛️  OuiComply MCP Server")
    print("=" * 50)
    print("AI-Assisted Legal Compliance Checker")
    print("Model Context Protocol Server")
    print("=" * 50)
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Validate configuration before starting
        if not validate_config():
            logger.error("❌ Configuration validation failed!")
            logger.error("Please check your .env file and ensure MISTRAL_KEY is set.")
            logger.error("Copy .env.example to .env and update with your API key.")
            sys.exit(1)
        
        logger.info("✅ Configuration validated successfully")
        
        # Print configuration summary
        print_config_summary()
        
        # Start the server
        logger.info("🚀 Starting MCP server...")
        asyncio.run(server_main())
        
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
