#!/usr/bin/env python3
"""
Minimal Vercel MCP Server - Ultra-lightweight for debugging
"""

import json
from datetime import datetime, UTC
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
app = FastAPI(
    title="OuiComply MCP Server",
    description="Minimal MCP Server for Vercel",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ouicomply-mcp",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(UTC).isoformat()
    }

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "server": "ouicomply-mcp",
        "timestamp": datetime.now(UTC).isoformat()
    }

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """MCP endpoint."""
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "message": "MCP endpoint working",
            "timestamp": datetime.now(UTC).isoformat()
        }
    }

# For Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
