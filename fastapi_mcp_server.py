#!/usr/bin/env python3
"""
FastAPI wrapper for OuiComply MCP Server.

This module provides a FastAPI web interface for the MCP Server,
enabling integration with Le Chat and other external clients.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import OuiComplyMCPServer
from src.tools.memory_integration import MemoryIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OuiComply MCP Server",
    description="FastAPI wrapper for OuiComply MCP Server with Le Chat integration",
    version="1.0.0"
)

# Add CORS middleware for Le Chat integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP Server instance
mcp_server: Optional[OuiComplyMCPServer] = None


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis."""
    document_content: str = Field(..., description="Document content to analyze")
    document_name: str = Field(..., description="Name of the document")
    team_context: str = Field(default="Legal Team", description="Team context for analysis")
    compliance_frameworks: List[str] = Field(default=["gdpr", "sox", "ccpa"], description="Compliance frameworks to check")
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth level")


class MemoryUpdateRequest(BaseModel):
    """Request model for memory updates."""
    team_id: str = Field(..., description="Team identifier")
    memory_type: str = Field(..., description="Type of memory (compliance or behavioral)")
    updates: Dict[str, Any] = Field(..., description="Memory updates to apply")


class MemoryRetrieveRequest(BaseModel):
    """Request model for memory retrieval."""
    team_id: str = Field(..., description="Team identifier")
    memory_type: Optional[str] = Field(default=None, description="Type of memory to retrieve")


@app.on_event("startup")
async def startup_event():
    """Initialize the MCP Server on startup."""
    global mcp_server
    try:
        logger.info("Initializing OuiComply MCP Server...")
        mcp_server = OuiComplyMCPServer()
        logger.info("MCP Server initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP Server: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "OuiComply MCP Server API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "analyze_document": "/analyze-document",
            "analyze_with_memory": "/analyze-with-memory",
            "memory": "/memory",
            "lechat_integration": "/lechat"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mcp_server": "initialized" if mcp_server else "not_initialized",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        # Get tools from MCP server
        tools = []
        for tool in mcp_server.server.list_tools():
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-document")
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze a document for compliance issues."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        # Call the MCP server's analyze_document tool
        result = await mcp_server._handle_analyze_document({
            "document_content": request.document_content,
            "document_name": request.document_name,
            "compliance_frameworks": request.compliance_frameworks,
            "analysis_depth": request.analysis_depth
        })
        
        return {
            "success": True,
            "result": result[0].text if result else "No result",
            "document_name": request.document_name,
            "team_context": request.team_context
        }
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-with-memory")
async def analyze_with_memory(request: DocumentAnalysisRequest):
    """Analyze a document with team-specific memory integration."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        # Call the MCP server's analyze_with_memory tool
        result = await mcp_server._handle_analyze_with_memory({
            "document_content": request.document_content,
            "document_name": request.document_name,
            "team_context": request.team_context,
            "compliance_frameworks": request.compliance_frameworks
        })
        
        return {
            "success": True,
            "result": result[0].text if result else "No result",
            "document_name": request.document_name,
            "team_context": request.team_context,
            "memory_integration": "enabled"
        }
    except Exception as e:
        logger.error(f"Memory-integrated analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/update")
async def update_memory(request: MemoryUpdateRequest):
    """Update team memory through Le Chat MCP."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        # Update memory via Le Chat MCP
        await mcp_server.memory_integration.update_memory_via_lechat(
            team_id=request.team_id,
            memory_type=request.memory_type,
            updates=request.updates
        )
        
        return {
            "success": True,
            "message": f"Memory updated for team {request.team_id}",
            "memory_type": request.memory_type
        }
    except Exception as e:
        logger.error(f"Memory update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/retrieve")
async def retrieve_memory(request: MemoryRetrieveRequest):
    """Retrieve team memory through Le Chat MCP."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        if request.memory_type:
            # Retrieve specific memory type
            memory = await mcp_server.memory_integration.retrieve_memory_via_lechat(
                team_id=request.team_id,
                memory_type=request.memory_type
            )
        else:
            # Retrieve all team memory
            memory = await mcp_server.memory_integration.get_team_memory(request.team_id)
        
        return {
            "success": True,
            "team_id": request.team_id,
            "memory": memory
        }
    except Exception as e:
        logger.error(f"Memory retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lechat/integration")
async def lechat_integration_info():
    """Get Le Chat integration information."""
    return {
        "integration_status": "ready",
        "memory_mcp": "enabled",
        "available_endpoints": [
            "/analyze-with-memory",
            "/memory/update",
            "/memory/retrieve"
        ],
        "sample_requests": {
            "analyze_with_memory": {
                "document_content": "Your document content here",
                "document_name": "contract.pdf",
                "team_context": "Legal Team",
                "compliance_frameworks": ["gdpr", "sox", "ccpa"]
            },
            "memory_update": {
                "team_id": "legal_team",
                "memory_type": "compliance",
                "updates": {
                    "compliance_rules": ["New rule 1", "New rule 2"],
                    "risk_tolerance": "low"
                }
            }
        }
    }


@app.post("/lechat/test")
async def lechat_test(request: DocumentAnalysisRequest):
    """Test endpoint specifically designed for Le Chat integration."""
    if not mcp_server:
        raise HTTPException(status_code=500, detail="MCP Server not initialized")
    
    try:
        logger.info(f"Le Chat test request received for document: {request.document_name}")
        
        # Perform analysis with memory integration
        result = await mcp_server._handle_analyze_with_memory({
            "document_content": request.document_content,
            "document_name": request.document_name,
            "team_context": request.team_context,
            "compliance_frameworks": request.compliance_frameworks
        })
        
        # Format response for Le Chat
        response_text = result[0].text if result else "Analysis completed"
        
        return {
            "success": True,
            "message": "Analysis completed successfully",
            "document_name": request.document_name,
            "team_context": request.team_context,
            "analysis_result": response_text,
            "memory_integration": "Le Chat MCP enabled",
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Le Chat test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "fastapi_mcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
