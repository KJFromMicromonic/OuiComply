#!/usr/bin/env python3
"""
OuiComply Standard MCP Server - AI-Assisted Legal Compliance Checker

This server follows the standard MCP protocol patterns for Alpic deployment.
It provides the same functionality as the FastMCP server but with standard MCP patterns.

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
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server
    import mcp
except ImportError:
    print("MCP not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.server.sse import sse_server
    from mcp.server.streamable_http import streamable_http_server
    import mcp

from mcp_server import OuiComplyMCPServer
from src.tools.document_ai import DocumentAnalysisRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("ouicomply-mcp")

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

# MCP Tools
@server.list_tools()
async def list_tools() -> List[Dict[str, Any]]:
    """List available MCP tools."""
    return [
        {
            "name": "analyze_document",
            "description": "Analyze a document for compliance issues using AI-powered analysis with Mistral API",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "document_content": {
                        "type": "string",
                        "description": "The content of the document to analyze"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Type of document (contract, policy, etc.)",
                        "default": "contract"
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Compliance frameworks to check against",
                        "default": ["gdpr", "sox"]
                    },
                    "analysis_depth": {
                        "type": "string",
                        "description": "Depth of analysis",
                        "default": "comprehensive"
                    }
                },
                "required": ["document_content"]
            }
        },
        {
            "name": "update_memory",
            "description": "Update team memory with new compliance insights and learnings",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team identifier"
                    },
                    "insight": {
                        "type": "string",
                        "description": "Compliance insight to store"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category of insight",
                        "default": "general"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "default": "medium"
                    }
                },
                "required": ["team_id", "insight"]
            }
        },
        {
            "name": "get_compliance_status",
            "description": "Get current compliance status for a team across frameworks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Team identifier"
                    },
                    "framework": {
                        "type": "string",
                        "description": "Specific framework to check (optional)"
                    },
                    "include_history": {
                        "type": "boolean",
                        "description": "Include historical data",
                        "default": False
                    }
                },
                "required": ["team_id"]
            }
        },
        {
            "name": "comprehensive_analysis",
            "description": "Perform comprehensive compliance analysis with structured output and LeChat actions",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "document_content": {
                        "type": "string",
                        "description": "The content of the document to analyze"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Type of document",
                        "default": "contract"
                    },
                    "frameworks": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Compliance frameworks to check against",
                        "default": ["gdpr", "ccpa", "sox"]
                    },
                    "analysis_depth": {
                        "type": "string",
                        "description": "Depth of analysis",
                        "default": "comprehensive"
                    },
                    "team_context": {
                        "type": "string",
                        "description": "Team context for analysis"
                    }
                },
                "required": ["document_content"]
            }
        },
        {
            "name": "automate_compliance_workflow",
            "description": "Automate compliance workflow based on document analysis",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "document_content": {
                        "type": "string",
                        "description": "The content of the document to analyze"
                    },
                    "workflow_type": {
                        "type": "string",
                        "description": "Type of workflow to automate"
                    },
                    "team_id": {
                        "type": "string",
                        "description": "Team identifier"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level",
                        "default": "medium"
                    }
                },
                "required": ["document_content", "workflow_type", "team_id"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handle tool calls."""
    try:
        if name == "analyze_document":
            result = await mcp_server._analyze_document(arguments)
            response_data = extract_content_from_mcp_result(result)
            return [{"type": "text", "text": json.dumps(response_data)}]
        
        elif name == "update_memory":
            result = await mcp_server._update_memory(arguments)
            response_data = extract_content_from_mcp_result(result)
            return [{"type": "text", "text": json.dumps(response_data)}]
        
        elif name == "get_compliance_status":
            result = await mcp_server._get_compliance_status(arguments)
            response_data = extract_content_from_mcp_result(result)
            return [{"type": "text", "text": json.dumps(response_data)}]
        
        elif name == "comprehensive_analysis":
            result = await mcp_server._analyze_document(arguments)
            response_data = extract_content_from_mcp_result(result)
            return [{"type": "text", "text": json.dumps(response_data)}]
        
        elif name == "automate_compliance_workflow":
            result = await mcp_server._automate_compliance_workflow(arguments)
            response_data = extract_content_from_mcp_result(result)
            return [{"type": "text", "text": json.dumps(response_data)}]
        
        else:
            return [{"type": "text", "text": f"Unknown tool: {name}"}]
    
    except Exception as e:
        logger.error(f"Tool call failed: {str(e)}")
        return [{"type": "text", "text": f"Error: {str(e)}"}]

# MCP Resources
@server.list_resources()
async def list_resources() -> List[Dict[str, Any]]:
    """List available MCP resources."""
    return [
        {
            "uri": "mcp://compliance_frameworks",
            "name": "compliance_frameworks",
            "description": "Get available compliance frameworks with requirements and risk indicators",
            "mimeType": "application/json"
        },
        {
            "uri": "mcp://legal_templates",
            "name": "legal_templates", 
            "description": "Get available legal document templates with required sections",
            "mimeType": "application/json"
        },
        {
            "uri": "mcp://team_memory/{team_id}",
            "name": "team_memory",
            "description": "Get team memory and insights for a specific team",
            "mimeType": "application/json"
        }
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Handle resource reads."""
    try:
        if uri == "mcp://compliance_frameworks":
            frameworks_json = mcp_server._get_compliance_frameworks()
            return frameworks_json
        
        elif uri == "mcp://legal_templates":
            templates_json = mcp_server._get_legal_templates()
            return templates_json
        
        elif uri.startswith("mcp://team_memory/"):
            team_id = uri.split("/")[-1]
            memory_json = await mcp_server._get_team_memory()
            memory_data = json.loads(memory_json)
            
            # Filter by team_id if provided
            if team_id and "teams" in memory_data:
                team_memory = memory_data["teams"].get(team_id, {})
                memory_data = {"teams": {team_id: team_memory}}
            
            return json.dumps(memory_data)
        
        else:
            return json.dumps({"error": f"Unknown resource: {uri}"})
    
    except Exception as e:
        logger.error(f"Resource read failed: {str(e)}")
        return json.dumps({"error": str(e)})

# Alpic MCP Transport Detection Patterns
# These patterns ensure Alpic can detect the MCP transport type

# Pattern 1: Standard MCP run with streamable HTTP
mcp.run(transport="streamable-http")

# Pattern 2: Alternative patterns for detection
if __name__ == "__main__":
    # Run with streamable HTTP transport
    asyncio.run(streamable_http_server(server))
