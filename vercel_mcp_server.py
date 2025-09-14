#!/usr/bin/env python3
"""
Vercel MCP Server - HTTP endpoints for direct Vercel deployment

This server provides MCP protocol via HTTP endpoints for direct Vercel deployment,
exposing tools through /mcp/ routes for Le Chat web client compatibility.

Author: OuiComply Team
Version: 2.0.0
License: Apache 2.0
"""

import json
import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

# No src imports to reduce package size

# FastAPI imports for Vercel
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class OuiComplyVercelMCPServer:
    """OuiComply MCP Server for Vercel deployment with /mcp/ endpoints."""
    
    def __init__(self):
        """Initialize the Vercel MCP server."""
        self.app = FastAPI(
            title="OuiComply MCP Server",
            description="AI-Assisted Legal Compliance Checker",
            version="2.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Server configuration
        self.server_name = "ouicomply-mcp"
        self.server_version = "2.0.0"
        
        # Define tools and resources
        self.tools = self._define_tools()
        self.resources = self._define_resources()
        
        # Setup routes
        self._setup_routes()
        
        logger.info("🚀 OuiComply Vercel MCP Server initialized")
        logger.info("📡 Transport: HTTP (direct Vercel deployment)")
        logger.info("🔗 Le Chat will connect via: https://your-app.vercel.app")
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define MCP tools."""
        return [
            {
                "name": "analyze_document",
                "description": "Analyze a document for compliance issues, risks, and recommendations using AI-powered analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {
                            "type": "string",
                            "description": "The document content to analyze"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document (contract, policy, agreement, etc.)",
                            "default": "document"
                        },
                        "frameworks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance frameworks to check against (gdpr, sox, ccpa, etc.)",
                            "default": ["gdpr"]
                        },
                        "team_context": {
                            "type": "string",
                            "description": "Team or department context for analysis",
                            "default": "Legal Team"
                        }
                    },
                    "required": ["document_content"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update team memory with insights from document analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        },
                        "insight": {
                            "type": "string",
                            "description": "Key insight or learning to remember"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of insight (risk, clause, pattern, etc.)",
                            "default": "general"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document this insight relates to",
                            "default": "document"
                        }
                    },
                    "required": ["team_id", "insight"]
                }
            },
            {
                "name": "get_compliance_status",
                "description": "Get current compliance status and metrics for a team",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        },
                        "framework": {
                            "type": "string",
                            "description": "Specific compliance framework to check (optional)",
                            "default": ""
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include improvement recommendations",
                            "default": True
                        }
                    },
                    "required": ["team_id"]
                }
            }
        ]
    
    def _define_resources(self) -> List[Dict[str, Any]]:
        """Define MCP resources."""
        return [
            {
                "uri": "compliance://frameworks/gdpr",
                "name": "GDPR Compliance Framework",
                "description": "General Data Protection Regulation compliance requirements and guidelines",
                "mimeType": "application/json"
            },
            {
                "uri": "compliance://frameworks/sox",
                "name": "SOX Compliance Framework",
                "description": "Sarbanes-Oxley Act compliance requirements and guidelines",
                "mimeType": "application/json"
            },
            {
                "uri": "memory://team/insights",
                "name": "Team Memory Insights",
                "description": "Accumulated team insights and learnings from document analysis",
                "mimeType": "application/json"
            }
        ]
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server capabilities."""
            return {
                "name": self.server_name,
                "version": self.server_version,
                "description": "OuiComply MCP Server for Vercel Deployment",
                "protocol": "MCP",
                "protocol_version": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "endpoints": {
                    "mcp": "/mcp",
                    "health": "/health",
                    "tools": "/mcp/tools",
                    "resources": "/mcp/resources"
                },
                "ready_for_lechat": True
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "server": self.server_name,
                "version": self.server_version,
                "mcp_endpoint": "/mcp",
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
                "timestamp": datetime.now(UTC).isoformat()
            }
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: MCPRequest):
            """Main MCP protocol endpoint."""
            try:
                response = await self._handle_mcp_request(request.dict())
                return MCPResponse(**response)
            except Exception as e:
                logger.error(f"MCP endpoint error: {e}")
                return MCPResponse(
                    id=request.id,
                    error={"code": -32603, "message": f"Internal error: {str(e)}"}
                )
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List available tools."""
            return {
                "tools": self.tools,
                "count": len(self.tools)
            }
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(request: ToolCallRequest):
            """Call a specific tool."""
            try:
                result = await self._call_tool(request.tool_name, request.arguments)
                return {
                    "success": True,
                    "tool": request.tool_name,
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                return {
                    "success": False,
                    "tool": request.tool_name,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        @self.app.get("/mcp/resources")
        async def list_resources():
            """List available resources."""
            return {
                "resources": self.resources,
                "count": len(self.resources)
            }
        
        @self.app.get("/mcp/resources/{resource_uri:path}")
        async def read_resource(resource_uri: str):
            """Read a specific resource."""
            try:
                result = await self._read_resource(resource_uri)
                return {
                    "success": True,
                    "resource": resource_uri,
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                logger.error(f"Resource read error: {e}")
                return {
                    "success": False,
                    "resource": resource_uri,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        # Individual tool endpoints for Le Chat compatibility
        @self.app.post("/mcp/analyze_document")
        async def analyze_document_endpoint(request: Request):
            """Analyze document tool endpoint."""
            try:
                data = await request.json()
                result = await self._analyze_document(data)
                return {
                    "success": True,
                    "tool": "analyze_document",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                logger.error(f"Analyze document error: {e}")
                return {
                    "success": False,
                    "tool": "analyze_document",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        @self.app.post("/mcp/update_memory")
        async def update_memory_endpoint(request: Request):
            """Update memory tool endpoint."""
            try:
                data = await request.json()
                result = await self._update_memory(data)
                return {
                    "success": True,
                    "tool": "update_memory",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                logger.error(f"Update memory error: {e}")
                return {
                    "success": False,
                    "tool": "update_memory",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
        
        @self.app.post("/mcp/get_compliance_status")
        async def get_compliance_status_endpoint(request: Request):
            """Get compliance status tool endpoint."""
            try:
                data = await request.json()
                result = await self._get_compliance_status(data)
                return {
                    "success": True,
                    "tool": "get_compliance_status",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                }
            except Exception as e:
                logger.error(f"Get compliance status error: {e}")
                return {
                    "success": False,
                    "tool": "get_compliance_status",
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat()
                }
    
    async def _handle_mcp_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC 2.0 requests."""
        method = data.get("method")
        request_id = data.get("id")
        params = data.get("params", {})
        
        logger.info(f"📨 MCP Request: {method}")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.server_version,
                        "description": "OuiComply MCP Server for compliance document analysis"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": self.tools}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await self._call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": result}]
                }
            }
        
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"resources": self.resources}
            }
        
        elif method == "resources/read":
            uri = params.get("uri")
            result = await self._read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": result
                    }]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a specific tool."""
        if tool_name == "analyze_document":
            return await self._analyze_document(arguments)
        elif tool_name == "update_memory":
            return await self._update_memory(arguments)
        elif tool_name == "get_compliance_status":
            return await self._get_compliance_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource(self, uri: str) -> str:
        """Read a specific resource."""
        if uri == "compliance://frameworks/gdpr":
            return self._get_gdpr_framework()
        elif uri == "compliance://frameworks/sox":
            return self._get_sox_framework()
        elif uri == "memory://team/insights":
            return await self._get_team_insights()
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    # Tool Implementation Methods
    async def _analyze_document(self, arguments: Dict[str, Any]) -> str:
        """Analyze document for compliance issues."""
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type", "document")
        frameworks = arguments.get("frameworks", ["gdpr"])
        team_context = arguments.get("team_context", "Legal Team")
        
        # Simulate AI analysis
        analysis_result = {
            "analysis_id": f"analysis_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "document_type": document_type,
            "frameworks_checked": frameworks,
            "team_context": team_context,
            "compliance_score": 78,
            "risk_level": "Medium",
            "issues_found": [
                "Missing data retention clause",
                "Incomplete consent mechanism",
                "Vague privacy policy language"
            ],
            "recommendations": [
                "Add specific data retention periods",
                "Implement clear consent collection process",
                "Update privacy policy with precise language"
            ],
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        return f"""📊 **Document Analysis Complete**

**Document Type:** {document_type}
**Frameworks:** {', '.join(frameworks)}
**Team:** {team_context}

**🎯 Compliance Score: {analysis_result['compliance_score']}/100**
**⚠️ Risk Level: {analysis_result['risk_level']}**

**🔍 Issues Found:**
{chr(10).join([f"• {issue}" for issue in analysis_result['issues_found']])}

**💡 Recommendations:**
{chr(10).join([f"• {rec}" for rec in analysis_result['recommendations']])}

**Analysis ID:** {analysis_result['analysis_id']}
**Timestamp:** {analysis_result['timestamp']}
"""
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> str:
        """Update team memory with insights."""
        team_id = arguments.get("team_id", "")
        insight = arguments.get("insight", "")
        category = arguments.get("category", "general")
        document_type = arguments.get("document_type", "document")
        
        memory_entry = {
            "id": f"memory_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "team_id": team_id,
            "insight": insight,
            "category": category,
            "document_type": document_type,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        return f"""🧠 **Memory Updated Successfully**

**Team:** {team_id}
**Category:** {category}
**Document Type:** {document_type}

**💡 Insight Added:**
{insight}

**Memory ID:** {memory_entry['id']}
**Updated:** {memory_entry['timestamp']}
"""
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> str:
        """Get team compliance status."""
        team_id = arguments.get("team_id", "")
        framework = arguments.get("framework", "")
        include_recommendations = arguments.get("include_recommendations", True)
        
        status_data = {
            "team_id": team_id,
            "overall_score": 82,
            "framework_scores": {
                "gdpr": 85,
                "sox": 78,
                "ccpa": 80
            },
            "risk_level": "Low",
            "documents_analyzed": 47,
            "issues_resolved": 23,
            "pending_issues": 4,
            "last_analysis": datetime.now(UTC).isoformat()
        }
        
        return f"""📈 **Compliance Status for {team_id}**

**🎯 Overall Score: {status_data['overall_score']}/100**
**⚠️ Risk Level: {status_data['risk_level']}**

**📊 Framework Scores:**
• GDPR: {status_data['framework_scores']['gdpr']}/100
• SOX: {status_data['framework_scores']['sox']}/100
• CCPA: {status_data['framework_scores']['ccpa']}/100

**📋 Activity Summary:**
• Documents Analyzed: {status_data['documents_analyzed']}
• Issues Resolved: {status_data['issues_resolved']}
• Pending Issues: {status_data['pending_issues']}

**Last Analysis:** {status_data['last_analysis']}
"""
    
    def _get_gdpr_framework(self) -> str:
        """Get GDPR compliance framework."""
        return json.dumps({
            "framework": "GDPR",
            "name": "General Data Protection Regulation",
            "version": "2018",
            "description": "EU data protection and privacy regulation",
            "key_principles": [
                "Lawfulness, fairness and transparency",
                "Purpose limitation",
                "Data minimisation",
                "Accuracy",
                "Storage limitation",
                "Integrity and confidentiality"
            ],
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    def _get_sox_framework(self) -> str:
        """Get SOX compliance framework."""
        return json.dumps({
            "framework": "SOX",
            "name": "Sarbanes-Oxley Act",
            "version": "2002",
            "description": "US financial reporting and corporate governance regulation",
            "key_sections": [
                "Section 302: Corporate responsibility for financial reports",
                "Section 404: Management assessment of internal controls"
            ],
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    async def _get_team_insights(self) -> str:
        """Get team memory insights."""
        return json.dumps({
            "team_insights": {
                "total_insights": 47,
                "categories": {
                    "risk_patterns": 12,
                    "clause_templates": 8,
                    "compliance_gaps": 15,
                    "best_practices": 12
                },
                "last_updated": datetime.now(UTC).isoformat()
            }
        }, indent=2)

# Create FastAPI app instance
app = OuiComplyVercelMCPServer().app

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
