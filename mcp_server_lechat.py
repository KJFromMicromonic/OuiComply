#!/usr/bin/env python3
"""
MCP Server for Le Chat Integration with proper MCP/SSE protocol support.
This server implements the Model Context Protocol (MCP) that Le Chat expects.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Import our existing tools
from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """MCP request model."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    """MCP response model."""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPNotification(BaseModel):
    """MCP notification model."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPLeChatServer:
    """MCP Server implementation for Le Chat integration."""
    
    def __init__(self):
        self.app = FastAPI(
            title="OuiComply MCP Server for Le Chat",
            description="Model Context Protocol server for Le Chat integration",
            version="1.0.0"
        )
        
        # Initialize services
        self.document_ai = DocumentAIService()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.compliance_engine = ComplianceEngine()
        
        # MCP protocol state
        self.tools = self._initialize_tools()
        self.resources = self._initialize_resources()
        self.prompts = self._initialize_prompts()
        
        # Setup routes
        self._setup_routes()
        
        # Setup CORS for Le Chat
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _initialize_tools(self) -> List[Dict[str, Any]]:
        """Initialize MCP tools for Le Chat."""
        return [
            {
                "name": "analyze_document",
                "description": "Analyze a document for compliance issues using AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {
                            "type": "string",
                            "description": "The content of the document to analyze"
                        },
                        "document_name": {
                            "type": "string",
                            "description": "Name of the document"
                        },
                        "team_context": {
                            "type": "string",
                            "description": "Team context for analysis"
                        },
                        "compliance_frameworks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance frameworks to check against"
                        }
                    },
                    "required": ["document_content", "document_name"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update team memory with new compliance insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        },
                        "memory_type": {
                            "type": "string",
                            "enum": ["compliance", "behavioral"],
                            "description": "Type of memory to update"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Memory updates to apply"
                        }
                    },
                    "required": ["team_id", "memory_type", "updates"]
                }
            },
            {
                "name": "get_compliance_status",
                "description": "Get current compliance status for a team",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        }
                    },
                    "required": ["team_id"]
                }
            }
        ]
    
    def _initialize_resources(self) -> List[Dict[str, Any]]:
        """Initialize MCP resources."""
        return [
            {
                "uri": "ouicomply://compliance-frameworks",
                "name": "Compliance Frameworks",
                "description": "Available compliance frameworks",
                "mimeType": "application/json"
            },
            {
                "uri": "ouicomply://team-memory",
                "name": "Team Memory",
                "description": "Team-specific compliance memory",
                "mimeType": "application/json"
            }
        ]
    
    def _initialize_prompts(self) -> List[Dict[str, Any]]:
        """Initialize MCP prompts."""
        return [
            {
                "name": "compliance_analysis",
                "description": "Analyze document for compliance issues",
                "arguments": [
                    {
                        "name": "document_content",
                        "description": "Content to analyze",
                        "required": True
                    },
                    {
                        "name": "frameworks",
                        "description": "Compliance frameworks to check",
                        "required": False
                    }
                ]
            }
        ]
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "OuiComply MCP Server",
                "version": "1.0.0",
                "protocol": "MCP",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True
                }
            }
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "document_ai": "ready",
                    "memory_integration": "ready",
                    "compliance_engine": "ready"
                }
            }
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: MCPRequest):
            """Main MCP endpoint for Le Chat."""
            try:
                return await self._handle_mcp_request(request)
            except Exception as e:
                logger.error(f"MCP request error: {e}")
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": "Internal error",
                        "data": str(e)
                    }
                ).dict()
        
        @self.app.get("/mcp/sse")
        async def mcp_sse(request: Request):
            """Server-Sent Events endpoint for MCP."""
            return EventSourceResponse(self._mcp_sse_generator(request))
        
        @self.app.post("/mcp/sse")
        async def mcp_sse_post(request: Request):
            """POST endpoint for MCP SSE."""
            body = await request.json()
            mcp_request = MCPRequest(**body)
            return EventSourceResponse(self._mcp_sse_generator(request, mcp_request))
        
        # Legacy endpoints for backward compatibility
        @self.app.get("/lechat/integration")
        async def lechat_integration():
            return {
                "status": "ready",
                "mcp_endpoint": "/mcp",
                "sse_endpoint": "/mcp/sse",
                "tools": len(self.tools),
                "resources": len(self.resources),
                "prompts": len(self.prompts)
            }
        
        @self.app.post("/lechat/test")
        async def lechat_test(request: Request):
            """Test endpoint for Le Chat integration."""
            try:
                data = await request.json()
                
                # Simulate document analysis
                result = {
                    "status": "success",
                    "analysis": {
                        "compliance_score": 85,
                        "risk_level": "medium",
                        "issues_found": 3,
                        "recommendations": [
                            "Update privacy policy language",
                            "Add data retention clause",
                            "Include GDPR compliance statement"
                        ]
                    },
                    "memory_updated": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP requests."""
        method = request.method
        
        if method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "OuiComply MCP Server",
                        "version": "1.0.0"
                    }
                }
            )
        
        elif method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={"tools": self.tools}
            )
        
        elif method == "tools/call":
            return await self._handle_tool_call(request)
        
        elif method == "resources/list":
            return MCPResponse(
                id=request.id,
                result={"resources": self.resources}
            )
        
        elif method == "resources/read":
            return await self._handle_resource_read(request)
        
        elif method == "prompts/list":
            return MCPResponse(
                id=request.id,
                result={"prompts": self.prompts}
            )
        
        elif method == "prompts/get":
            return await self._handle_prompt_get(request)
        
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            )
    
    async def _handle_tool_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tool calls."""
        params = request.params or {}
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "analyze_document":
                result = await self._analyze_document_tool(arguments)
            elif tool_name == "update_memory":
                result = await self._update_memory_tool(arguments)
            elif tool_name == "get_compliance_status":
                result = await self._get_compliance_status_tool(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            )
        
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            )
    
    async def _analyze_document_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document analysis tool call."""
        document_content = arguments.get("document_content", "")
        document_name = arguments.get("document_name", "unknown")
        team_context = arguments.get("team_context", "General")
        frameworks = arguments.get("compliance_frameworks", ["gdpr", "sox", "ccpa"])
        
        # Use our existing document AI service
        result = await self.document_ai.analyze_document(
            document_content=document_content,
            document_name=document_name,
            team_context=team_context,
            compliance_frameworks=frameworks
        )
        
        return {
            "tool": "analyze_document",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _update_memory_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory update tool call."""
        team_id = arguments.get("team_id")
        memory_type = arguments.get("memory_type")
        updates = arguments.get("updates", {})
        
        if memory_type == "compliance":
            await self.memory_integration.update_compliance_memory(team_id, updates)
        elif memory_type == "behavioral":
            await self.memory_integration.update_behavioral_memory(team_id, updates)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
        
        return {
            "tool": "update_memory",
            "status": "success",
            "team_id": team_id,
            "memory_type": memory_type,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _get_compliance_status_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle compliance status tool call."""
        team_id = arguments.get("team_id")
        
        # Get team memory
        memory = await self.memory_integration.get_team_memory(team_id)
        
        return {
            "tool": "get_compliance_status",
            "team_id": team_id,
            "compliance_status": memory.get("compliance", {}),
            "behavioral_status": memory.get("behavioral", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_resource_read(self, request: MCPRequest) -> MCPResponse:
        """Handle resource read requests."""
        params = request.params or {}
        uri = params.get("uri")
        
        if uri == "ouicomply://compliance-frameworks":
            content = {
                "frameworks": ["gdpr", "sox", "ccpa", "hipaa", "pci-dss"],
                "descriptions": {
                    "gdpr": "General Data Protection Regulation",
                    "sox": "Sarbanes-Oxley Act",
                    "ccpa": "California Consumer Privacy Act",
                    "hipaa": "Health Insurance Portability and Accountability Act",
                    "pci-dss": "Payment Card Industry Data Security Standard"
                }
            }
        elif uri == "ouicomply://team-memory":
            content = {
                "teams": list(self.memory_integration.teams.keys()),
                "memory_types": ["compliance", "behavioral"]
            }
        else:
            raise ValueError(f"Unknown resource: {uri}")
        
        return MCPResponse(
            id=request.id,
            result={
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, indent=2)
                    }
                ]
            }
        )
    
    async def _handle_prompt_get(self, request: MCPRequest) -> MCPResponse:
        """Handle prompt get requests."""
        params = request.params or {}
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if prompt_name == "compliance_analysis":
            document_content = arguments.get("document_content", "")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            prompt_text = f"""
            Analyze the following document for compliance issues:
            
            Document: {document_content}
            
            Check against these frameworks: {', '.join(frameworks)}
            
            Provide:
            1. Compliance score (0-100)
            2. Risk level (low/medium/high)
            3. Specific issues found
            4. Recommendations for improvement
            """
            
            return MCPResponse(
                id=request.id,
                result={
                    "description": "Compliance analysis prompt",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": prompt_text
                            }
                        }
                    ]
                }
            )
        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")
    
    async def _mcp_sse_generator(self, request: Request, initial_request: Optional[MCPRequest] = None):
        """Generate SSE events for MCP."""
        try:
            # Send initial connection event
            yield {
                "event": "mcp.connected",
                "data": json.dumps({
                    "server": "OuiComply MCP Server",
                    "version": "1.0.0",
                    "timestamp": datetime.utcnow().isoformat()
                })
            }
            
            # Handle initial request if provided
            if initial_request:
                response = await self._handle_mcp_request(initial_request)
                yield {
                    "event": "mcp.response",
                    "data": json.dumps(response.dict())
                }
            
            # Keep connection alive and handle additional requests
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                # Send heartbeat
                yield {
                    "event": "mcp.heartbeat",
                    "data": json.dumps({
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield {
                "event": "mcp.error",
                "data": json.dumps({
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
            }

# Create the server instance
mcp_server = MCPLeChatServer()
app = mcp_server.app

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8002))
    
    print("🚀 Starting OuiComply MCP Server for Le Chat...")
    print(f"📡 MCP Endpoint: http://localhost:{port}/mcp")
    print(f"📡 SSE Endpoint: http://localhost:{port}/mcp/sse")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print(f"🔧 Le Chat Integration: http://localhost:{port}/lechat/integration")
    
    uvicorn.run(
        "mcp_server_lechat:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
