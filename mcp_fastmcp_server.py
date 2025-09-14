#!/usr/bin/env python3
"""
OuiComply FastMCP Server - AI-Assisted Legal Compliance Checker

This server uses FastMCP to expose all MCP tools and features as REST API endpoints
accessible via /mcp/{function} routes, following the Model Context Protocol specification.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server.fastmcp import FastMCP

from mcp_server import OuiComplyMCPServer
from src.tools.document_ai import DocumentAnalysisRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app = FastMCP("OuiComply MCP Server")

# Initialize the underlying MCP server
mcp_server = OuiComplyMCPServer()


# Utility functions
def extract_content_from_mcp_result(result) -> Dict[str, Any]:
    """Extract content from MCP result and convert to dictionary."""
    if not result:
        return {"content": "", "type": "text"}
    
    # Handle dictionary results (from MCP server methods)
    if isinstance(result, dict):
        return {"content": result, "type": "json"}
    
    # Handle MCP result objects with content attribute
    if hasattr(result, 'content') and result.content:
        content_items = []
        for item in result.content:
            if hasattr(item, 'text'):
                content_items.append(item.text)
            elif hasattr(item, 'content'):
                content_items.append(str(item.content))
            else:
                content_items.append(str(item))
        
        # Try to parse as JSON if it looks like structured data
        combined_content = "\n".join(content_items)
        try:
            parsed_content = json.loads(combined_content)
            return {"content": parsed_content, "type": "json"}
        except json.JSONDecodeError:
            return {"content": combined_content, "type": "text"}
    
    # Handle other types
    return {"content": str(result), "type": "text"}


# MCP Tools as FastMCP endpoints

@app.tool(
    name="analyze_document",
    description="Analyze a document for compliance issues using AI-powered analysis with Mistral API"
)
async def analyze_document(
    document_content: str,
    document_type: str = "contract",
    frameworks: List[str] = None,
    analysis_depth: str = "comprehensive"
) -> Dict[str, Any]:
    """
    Analyze a document for compliance issues using AI.
    
    This tool provides comprehensive document analysis with AI-powered
    compliance checking across multiple frameworks using Mistral API.
    """
    if frameworks is None:
        frameworks = ["gdpr", "sox"]
    
    try:
        logger.info(f"Analyzing document - type: {document_type}, frameworks: {frameworks}")
        
        # Prepare arguments for MCP server
        arguments = {
            "document_content": document_content,
            "document_type": document_type,
            "frameworks": frameworks
        }
        
        # Call MCP server method
        result = await mcp_server._analyze_document(arguments)
        
        # Extract and format response
        response_data = extract_content_from_mcp_result(result)
        
        return {
            "success": True,
            "data": response_data,
            "metadata": {
                "document_type": document_type,
                "frameworks": frameworks,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
                "content_length": len(document_content)
            }
        }
        
    except Exception as e:
        logger.error(f"Document analysis failed: {str(e)}")
        return {
            "success": False,
            "error": "Document analysis failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.tool(
    name="update_memory",
    description="Update team memory with new compliance insights and learnings"
)
async def update_memory(
    team_id: str,
    insight: str,
    category: str = "general",
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Update team memory with new compliance insights.
    
    This tool stores compliance insights and learnings
    for future reference and team collaboration.
    """
    try:
        logger.info(f"Updating memory for team: {team_id}")
        
        # Prepare arguments for MCP server
        arguments = {
            "team_id": team_id,
            "insight": insight,
            "category": category,
            "priority": priority
        }
        
        # Call MCP server method
        result = await mcp_server._update_memory(arguments)
        
        # Extract and format response
        response_data = extract_content_from_mcp_result(result)
        
        return {
            "success": True,
            "data": response_data,
            "metadata": {
                "team_id": team_id,
                "category": category,
                "priority": priority,
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Memory update failed: {str(e)}")
        return {
            "success": False,
            "error": "Memory update failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.tool(
    name="get_compliance_status",
    description="Get current compliance status for a team across frameworks"
)
async def get_compliance_status(
    team_id: str,
    framework: Optional[str] = None,
    include_history: bool = False
) -> Dict[str, Any]:
    """
    Get current compliance status for a team.
    
    This tool provides comprehensive compliance status
    across all frameworks or a specific framework.
    """
    try:
        logger.info(f"Getting compliance status for team: {team_id}")
        
        # Prepare arguments for MCP server
        arguments = {
            "team_id": team_id,
            "framework": framework,
            "include_history": include_history
        }
        
        # Call MCP server method
        result = await mcp_server._get_compliance_status(arguments)
        
        # Extract and format response
        response_data = extract_content_from_mcp_result(result)
        
        return {
            "success": True,
            "data": response_data,
            "metadata": {
                "team_id": team_id,
                "framework": framework,
                "include_history": include_history,
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Compliance status retrieval failed: {str(e)}")
        return {
            "success": False,
            "error": "Compliance status retrieval failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.tool(
    name="comprehensive_analysis",
    description="Perform comprehensive compliance analysis with structured output and LeChat actions"
)
async def comprehensive_analysis(
    document_content: str,
    document_type: str = "contract",
    frameworks: List[str] = None,
    analysis_depth: str = "comprehensive",
    team_context: str = None
) -> Dict[str, Any]:
    """
    Perform comprehensive compliance analysis with structured output.
    
    Returns:
        - Executive summary with key findings
        - Detailed compliance issues with implementation guidance
        - LeChat actions for GitHub, Linear, and Slack
        - Compliance metrics and risk assessment
    """
    if frameworks is None:
        frameworks = ["gdpr", "ccpa", "sox"]
    
    logger.info(f"Performing comprehensive analysis - type: {document_type}, frameworks: {frameworks}")
    
    try:
        # Call MCP server method
        result = await mcp_server._analyze_document({
            "document_content": document_content,
            "document_type": document_type,
            "frameworks": frameworks,
            "analysis_depth": analysis_depth,
            "team_context": team_context
        })
        
        # Extract and format response
        response_data = extract_content_from_mcp_result(result)
        
        return {
            "success": True,
            "data": response_data,
            "metadata": {
                "document_type": document_type,
                "frameworks": frameworks,
                "analysis_timestamp": datetime.now(UTC).isoformat(),
                "content_length": len(document_content),
                "analysis_type": "comprehensive"
            }
        }
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {str(e)}")
        return {
            "success": False,
            "error": "Comprehensive analysis failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.tool(
    name="automate_compliance_workflow",
    description="Automate compliance workflow based on document analysis"
)
async def automate_compliance_workflow(
    document_content: str,
    workflow_type: str,
    team_id: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Automate compliance workflow based on document analysis.
    
    This tool triggers automated compliance workflows
    based on document analysis results.
    """
    try:
        logger.info(f"Automating workflow: {workflow_type} for team: {team_id}")
        
        # Prepare arguments for MCP server
        arguments = {
            "document_content": document_content,
            "workflow_type": workflow_type,
            "team_id": team_id,
            "priority": priority
        }
        
        # Call MCP server method
        result = await mcp_server._automate_compliance_workflow(arguments)
        
        # Extract and format response
        response_data = extract_content_from_mcp_result(result)
        
        return {
            "success": True,
            "data": response_data,
            "metadata": {
                "workflow_type": workflow_type,
                "team_id": team_id,
                "priority": priority,
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Workflow automation failed: {str(e)}")
        return {
            "success": False,
            "error": "Workflow automation failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


# MCP Resources as FastMCP endpoints

@app.resource(
    uri="mcp://compliance_frameworks",
    name="compliance_frameworks",
    description="Get available compliance frameworks with requirements and risk indicators",
    mime_type="application/json"
)
async def get_compliance_frameworks() -> Dict[str, Any]:
    """
    Get available compliance frameworks.
    
    This resource returns all supported compliance frameworks
    with their requirements and risk indicators.
    """
    try:
        logger.info("Retrieving compliance frameworks")
        
        # Get frameworks from MCP server
        frameworks_json = mcp_server._get_compliance_frameworks()
        frameworks_data = json.loads(frameworks_json)
        
        return {
            "success": True,
            "data": frameworks_data,
            "metadata": {
                "count": len(frameworks_data.get("frameworks", {})),
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Compliance frameworks retrieval failed: {str(e)}")
        return {
            "success": False,
            "error": "Compliance frameworks retrieval failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.resource(
    uri="mcp://legal_templates",
    name="legal_templates",
    description="Get available legal document templates with required sections",
    mime_type="application/json"
)
async def get_legal_templates() -> Dict[str, Any]:
    """
    Get available legal document templates.
    
    This resource returns all available legal document templates
    with their required sections and descriptions.
    """
    try:
        logger.info("Retrieving legal templates")
        
        # Get templates from MCP server
        templates_json = mcp_server._get_legal_templates()
        templates_data = json.loads(templates_json)
        
        return {
            "success": True,
            "data": templates_data,
            "metadata": {
                "count": len(templates_data.get("templates", {})),
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Legal templates retrieval failed: {str(e)}")
        return {
            "success": False,
            "error": "Legal templates retrieval failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


@app.resource(
    uri="mcp://team_memory/{team_id}",
    name="team_memory",
    description="Get team memory and insights for a specific team",
    mime_type="application/json"
)
async def get_team_memory(team_id: str) -> Dict[str, Any]:
    """
    Get team memory and insights.
    
    This resource retrieves stored compliance insights
    and learnings for a specific team.
    """
    try:
        logger.info(f"Retrieving team memory for: {team_id}")
        
        # Get team memory from MCP server
        memory_json = await mcp_server._get_team_memory()
        memory_data = json.loads(memory_json)
        
        # Filter by team_id if provided
        if team_id and "teams" in memory_data:
            team_memory = memory_data["teams"].get(team_id, {})
            memory_data = {"teams": {team_id: team_memory}}
        
        return {
            "success": True,
            "data": memory_data,
            "metadata": {
                "team_id": team_id,
                "timestamp": datetime.now(UTC).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Team memory retrieval failed: {str(e)}")
        return {
            "success": False,
            "error": "Team memory retrieval failed",
            "detail": str(e),
            "timestamp": datetime.now(UTC).isoformat()
        }


# Health check function for deployment platforms
def get_health_status():
    """Get health status for deployment platforms."""
    return {
        "status": "healthy",
        "service": "OuiComply MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat()
    }

# FastMCP server is ready - tools and resources are registered


if __name__ == "__main__":
    # Run the FastMCP server
    import uvicorn
    uvicorn.run(
        "mcp_fastmcp_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
