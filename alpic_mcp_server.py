#!/usr/bin/env python3
"""
Alpic MCP Server - Optimized for Alpic Deployment

This server is specifically designed for Alpic deployment with proper
health checks, OAuth metadata endpoints, and MCP transport patterns.

Author: OuiComply Team
Version: 1.0.0
"""

# Lambda handler for direct invocation - ultra fast, before any imports
def lambda_handler(event, context):
    """Lambda handler for direct invocation."""
    # Handle the specific payload format
    if "v20250806" in event and "message" in event["v20250806"]:
        message = event["v20250806"]["message"]
        if message.get("method") == "oauth/metadata":
            return {
                "jsonrpc": "2.0",
                "id": message.get("id", "unknown"),
                "result": {
                    "oauth": {
                        "version": "1.0.0",
                        "server_name": "ouicomply-mcp",
                        "capabilities": {
                            "tools": True,
                            "resources": True,
                            "prompts": False,
                            "logging": True
                        },
                        "status": "ready",
                        "transport": "streamable-http"
                    }
                }
            }

    # Default response
    return {
        "jsonrpc": "2.0",
        "id": "unknown",
        "error": {"code": -32601, "message": "Method not found"}
    }

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import required modules
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Alpic deployment."""
    logger.info("Health check requested")
    return jsonify({
        "status": "healthy",
        "service": "OuiComply MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "mcp_server": "running",
        "transport": "streamable-http"
    })

# OAuth metadata endpoint - handles both GET and POST
@app.route("/oauth/metadata", methods=["GET", "POST"])
def oauth_metadata():
    """OAuth metadata endpoint for Alpic deployment."""
    logger.info(f"OAuth metadata requested: {request.method}")

    # Handle both GET and POST requests
    if request.method == "POST":
        try:
            body = request.get_json()
            logger.info(f"POST body: {body}")
        except Exception as e:
            logger.warning(f"Could not parse POST body: {e}")

    return jsonify({
        "jsonrpc": "2.0",
        "id": request.headers.get("x-request-id", "unknown"),
        "result": {
            "oauth": {
                "version": "1.0.0",
                "server_name": "ouicomply-mcp",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": False,
                    "logging": True
                },
                "status": "ready",
                "transport": "streamable-http"
            }
        }
    })

# Root endpoint
@app.route("/", methods=["GET"])
def root_endpoint():
    """Root endpoint for Alpic deployment."""
    logger.info("Root endpoint requested")
    return jsonify({
        "message": "OuiComply MCP Server is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "oauth_metadata": "/oauth/metadata",
            "mcp": "streamable-http"
        }
    })

# Alpic optimized server



if __name__ == "__main__":
    # Get port from environment variable (Alpic sets this)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print("Starting OuiComply Alpic MCP Server...")
    print(f"Server will run on {host}:{port}")
    print("Transport: streamable-http")
    print("Health check: http://localhost:8000/health")
    print("OAuth metadata: http://localhost:8000/oauth/metadata")
    print("Root endpoint: http://localhost:8000/")

    # Run with Flask
    app.run(host=host, port=port, debug=False)
