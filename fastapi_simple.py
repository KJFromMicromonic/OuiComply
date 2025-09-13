#!/usr/bin/env python3
"""
Simple FastAPI server for OuiComply MCP Server testing.

This is a simplified version that focuses on testing the Le Chat integration
without the full MCP server complexity.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI app."""
    # Startup
    logger.info("Starting OuiComply MCP Server - Simple")
    yield
    # Shutdown
    logger.info("Shutting down OuiComply MCP Server - Simple")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="OuiComply MCP Server - Simple",
    description="Simple FastAPI wrapper for OuiComply MCP Server testing",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for Le Chat integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "OuiComply MCP Server API - Simple Version",
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
        "mcp_server": "simple_mode",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    tools = [
        {
            "name": "analyze_document",
            "description": "Analyze a document for compliance issues",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_content": {"type": "string"},
                    "document_name": {"type": "string"},
                    "compliance_frameworks": {"type": "array", "items": {"type": "string"}},
                    "analysis_depth": {"type": "string"}
                }
            }
        },
        {
            "name": "analyze_with_memory",
            "description": "Analyze a document with team-specific memory integration",
            "input_schema": {
                "type": "object",
                "properties": {
                    "document_content": {"type": "string"},
                    "document_name": {"type": "string"},
                    "team_context": {"type": "string"},
                    "compliance_frameworks": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        {
            "name": "update_memory",
            "description": "Update team memory through Le Chat MCP",
            "input_schema": {
                "type": "object",
                "properties": {
                    "team_id": {"type": "string"},
                    "memory_type": {"type": "string"},
                    "updates": {"type": "object"}
                }
            }
        }
    ]
    return {"tools": tools}


@app.post("/analyze-document")
async def analyze_document(request: DocumentAnalysisRequest):
    """Analyze a document for compliance issues."""
    try:
        # Simulate document analysis
        analysis_result = {
            "success": True,
            "document_name": request.document_name,
            "team_context": request.team_context,
            "frameworks": request.compliance_frameworks,
            "analysis_depth": request.analysis_depth,
            "issues_found": 3,
            "risk_level": "medium",
            "compliance_status": "requires_review",
            "recommendations": [
                "Add data protection clauses",
                "Include breach notification procedures",
                "Specify data retention periods"
            ],
            "message": "Document analysis completed successfully (simulated)"
        }
        
        return analysis_result
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-with-memory")
async def analyze_with_memory(request: DocumentAnalysisRequest):
    """Analyze a document with team-specific memory integration."""
    try:
        # Simulate memory-integrated analysis
        analysis_result = {
            "success": True,
            "document_name": request.document_name,
            "team_context": request.team_context,
            "frameworks": request.compliance_frameworks,
            "analysis_depth": request.analysis_depth,
            "issues_found": 4,
            "risk_level": "high",
            "compliance_status": "non_compliant",
            "team_memory_updated": True,
            "memory_integration": "Le Chat MCP enabled",
            "recommendations": [
                "Add data protection clauses (based on team history)",
                "Include breach notification procedures (team preference)",
                "Specify data retention periods (compliance rule)",
                "Review consent mechanisms (team pitfall pattern)"
            ],
            "message": "Memory-integrated analysis completed successfully (simulated)"
        }
        
        return analysis_result
    except Exception as e:
        logger.error(f"Memory-integrated analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/update")
async def update_memory(request: MemoryUpdateRequest):
    """Update team memory through Le Chat MCP."""
    try:
        # Simulate memory update via Le Chat MCP
        memory_key = f"ouicomply_{request.team_id}_{request.memory_type}"
        
        logger.info(f"Memory update simulated: {memory_key}")
        logger.info(f"Updates: {request.updates}")
        
        return {
            "success": True,
            "message": f"Memory updated for team {request.team_id} via Le Chat MCP",
            "memory_type": request.memory_type,
            "memory_key": memory_key,
            "updates_applied": request.updates
        }
    except Exception as e:
        logger.error(f"Memory update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/lechat/integration")
async def lechat_integration_info():
    """Get Le Chat integration information."""
    return {
        "integration_status": "ready",
        "memory_mcp": "enabled",
        "server_mode": "simple",
        "available_endpoints": [
            "/analyze-with-memory",
            "/memory/update",
            "/lechat/test"
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
    try:
        logger.info(f"Le Chat test request received for document: {request.document_name}")
        
        # Simulate analysis with memory integration
        result = {
            "success": True,
            "message": "Analysis completed successfully",
            "document_name": request.document_name,
            "team_context": request.team_context,
            "analysis_result": {
                "issues_found": 5,
                "risk_level": "high",
                "compliance_status": "non_compliant",
                "recommendations": [
                    "Add GDPR compliance clauses",
                    "Include data subject rights section",
                    "Specify lawful basis for processing",
                    "Add breach notification procedures",
                    "Include data retention policies"
                ]
            },
            "memory_integration": "Le Chat MCP enabled",
            "team_learning": "Analysis patterns stored for future reference",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return result
    except Exception as e:
        logger.error(f"Le Chat test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "fastapi_simple:app",
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable reload to avoid conflicts
        log_level="info"
    )
