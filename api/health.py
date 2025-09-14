#!/usr/bin/env python3
"""
Vercel health check endpoint.
"""

import json
from datetime import datetime


def handler(request):
    """Health check handler for Vercel."""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": json.dumps({
            "status": "healthy",
            "mcp_server": "ouicomply-vercel",
            "services": {
                "mcp_protocol": "ready",
                "tools": 3,
                "resources": 2,
                "prompts": 1
            },
            "timestamp": datetime.utcnow().isoformat(),
            "deployment": "vercel",
            "version": "1.0.0"
        })
    }


def main(request):
    return handler(request)
