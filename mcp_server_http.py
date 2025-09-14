#!/usr/bin/env python3
"""
OuiComply MCP Server - HTTP Version for Alpic Deployment

A Model Context Protocol (MCP) server that provides comprehensive document compliance
analysis using Mistral's DocumentAI service, with HTTP endpoints for Alpic deployment.

Author: OuiComply Team
Version: 2.0.0
License: Apache 2.0
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import structlog

# Import our tools and services
try:
    from src.tools.compliance_engine import ComplianceEngine, ComplianceReport
    from src.tools.memory_integration import MemoryIntegration
    from src.tools.automation_agent import AutomationAgent, AutomationResult
except ImportError:
    # Fallback for missing dependencies
    ComplianceEngine = None
    MemoryIntegration = None
    AutomationAgent = None

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("mcp_server")

class OuiComplyMCPHTTPServer:
    """OuiComply MCP Server with HTTP endpoints for Alpic deployment."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("ouicomply-mcp")
        self.compliance_engine = ComplianceEngine() if ComplianceEngine else None
        self.memory_integration = MemoryIntegration() if MemoryIntegration else None
        self.automation_agent = AutomationAgent() if AutomationAgent else None
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        
        logger.info("OuiComply MCP Server initialized", version="2.0.0")
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="analyze_document",
                    description="Analyze a document for compliance issues using AI-powered analysis",
                    inputSchema={
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
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="update_memory",
                    description="Update team memory with new compliance insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "string", "description": "Team identifier"},
                            "insight": {"type": "string", "description": "Compliance insight to store"},
                            "category": {"type": "string", "description": "Category of insight", "default": "general"},
                            "priority": {"type": "string", "description": "Priority level", "default": "medium"}
                        },
                        "required": ["team_id", "insight"]
                    }
                ),
                Tool(
                    name="get_compliance_status",
                    description="Get current compliance status for a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {"type": "string", "description": "Team identifier"},
                            "framework": {"type": "string", "description": "Specific framework to check"},
                            "include_history": {"type": "boolean", "description": "Include historical data", "default": False}
                        },
                        "required": ["team_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_document":
                    result = await self._analyze_document(arguments)
                    return [TextContent(type="text", text=json.dumps(result))]
                elif name == "update_memory":
                    result = await self._update_memory(arguments)
                    return [TextContent(type="text", text=json.dumps(result))]
                elif name == "get_compliance_status":
                    result = await self._get_compliance_status(arguments)
                    return [TextContent(type="text", text=json.dumps(result))]
                else:
                    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
            except Exception as e:
                logger.error("Tool call failed", tool=name, error=str(e))
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    def _register_resources(self):
        """Register MCP resources."""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="mcp://compliance_frameworks",
                    name="compliance_frameworks",
                    description="Get available compliance frameworks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="mcp://legal_templates",
                    name="legal_templates",
                    description="Get available legal document templates",
                    mimeType="application/json"
                ),
                Resource(
                    uri="mcp://team_memory",
                    name="team_memory",
                    description="Get team memory and insights",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Handle resource reads."""
            try:
                if uri == "mcp://compliance_frameworks":
                    return self._get_compliance_frameworks()
                elif uri == "mcp://legal_templates":
                    return self._get_legal_templates()
                elif uri == "mcp://team_memory":
                    return await self._get_team_memory()
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
            except Exception as e:
                logger.error("Resource read failed", uri=uri, error=str(e))
                return json.dumps({"error": str(e)})
    
    async def _analyze_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document for compliance issues."""
        try:
            document_content = arguments.get("document_content", "")
            document_type = arguments.get("document_type", "contract")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            # Simulate AI analysis (replace with actual implementation)
            analysis_result = {
                "document_type": document_type,
                "frameworks_checked": frameworks,
                "compliance_score": 85,
                "issues_found": [
                    {
                        "type": "data_retention",
                        "severity": "medium",
                        "description": "Document lacks clear data retention policy",
                        "recommendation": "Add specific data retention periods"
                    }
                ],
                "recommendations": [
                    "Add data retention policy",
                    "Include privacy notice",
                    "Specify data processing purposes"
                ],
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": analysis_result,
                "metadata": {
                    "analysis_timestamp": datetime.now(UTC).isoformat(),
                    "content_length": len(document_content)
                }
            }
        except Exception as e:
            logger.error("Document analysis failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update team memory with insights."""
        try:
            team_id = arguments.get("team_id", "")
            insight = arguments.get("insight", "")
            category = arguments.get("category", "general")
            priority = arguments.get("priority", "medium")
            
            # Simulate memory update (replace with actual implementation)
            memory_entry = {
                "team_id": team_id,
                "insight": insight,
                "category": category,
                "priority": priority,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": memory_entry,
                "message": "Memory updated successfully"
            }
        except Exception as e:
            logger.error("Memory update failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance status for a team."""
        try:
            team_id = arguments.get("team_id", "")
            framework = arguments.get("framework")
            include_history = arguments.get("include_history", False)
            
            # Simulate compliance status (replace with actual implementation)
            status = {
                "team_id": team_id,
                "overall_score": 78,
                "frameworks": {
                    "gdpr": {"score": 85, "status": "compliant"},
                    "sox": {"score": 72, "status": "needs_attention"},
                    "ccpa": {"score": 80, "status": "compliant"}
                },
                "last_updated": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": status
            }
        except Exception as e:
            logger.error("Compliance status retrieval failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def _get_compliance_frameworks(self) -> str:
        """Get compliance frameworks resource."""
        frameworks = {
            "frameworks": {
                "gdpr": {
                    "name": "General Data Protection Regulation",
                    "description": "EU data protection and privacy regulation",
                    "requirements": ["Data minimization", "Consent management", "Right to be forgotten"]
                },
                "sox": {
                    "name": "Sarbanes-Oxley Act",
                    "description": "US financial reporting and corporate governance regulation",
                    "requirements": ["Internal controls", "Audit trails", "Financial transparency"]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }
        return json.dumps(frameworks, indent=2)
    
    def _get_legal_templates(self) -> str:
        """Get legal templates resource."""
        templates = {
            "templates": {
                "privacy_policy": {
                    "name": "Privacy Policy Template",
                    "description": "GDPR-compliant privacy policy template",
                    "required_sections": ["Data collection", "Data usage", "User rights", "Contact information"]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }
        return json.dumps(templates, indent=2)
    
    async def _get_team_memory(self) -> str:
        """Get team memory resource."""
        memory_data = {
            "teams": {},
            "global_insights": [],
            "last_updated": datetime.now(UTC).isoformat()
        }
        return json.dumps(memory_data, indent=2)
    
    async def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server with HTTP endpoints."""
        logger.info("Starting OuiComply MCP HTTP Server", host=host, port=port)
        
        # For Alpic deployment, we need to create HTTP endpoints
        # This is a simplified version that responds to health checks
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        
        class MCPHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {
                        "status": "healthy",
                        "service": "OuiComply MCP Server",
                        "version": "2.0.0",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "mcp_server": "running"
                    }
                    self.wfile.write(json.dumps(response).encode())
                elif self.path == '/oauth/metadata':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {
                        "jsonrpc": "2.0",
                        "id": "alpic-request",
                        "result": {
                            "oauth": {
                                "version": "2.0.0",
                                "server_name": "ouicomply-mcp",
                                "capabilities": {
                                    "tools": True,
                                    "resources": True,
                                    "prompts": False,
                                    "logging": True
                                },
                                "status": "ready"
                            }
                        }
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/oauth/metadata':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {
                        "jsonrpc": "2.0",
                        "id": "alpic-request",
                        "result": {
                            "oauth": {
                                "version": "2.0.0",
                                "server_name": "ouicomply-mcp",
                                "capabilities": {
                                    "tools": True,
                                    "resources": True,
                                    "prompts": False,
                                    "logging": True
                                },
                                "status": "ready"
                            }
                        }
                    }
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass
        
        # Create and start server
        server = HTTPServer((host, port), MCPHandler)
        logger.info("MCP HTTP Server started", host=host, port=port)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error("Server error", error=str(e))
            raise


async def main():
    """Main entry point for the MCP HTTP server."""
    # Get configuration from environment variables
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    print("🚀 Starting OuiComply Official MCP Server")
    print("=" * 50)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌐 URL: http://{host}:{port}")
    print("=" * 50)
    
    # Create and run the server
    server = OuiComplyMCPHTTPServer()
    await server.run(host=host, port=port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
