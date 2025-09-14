#!/usr/bin/env python3
"""
Proper MCP Server implementation that routes everything through /mcp
Based on official MCP specification for Le Chat integration
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Import our existing tools
from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine

class MCPProperServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize our services
        self.document_ai_service = DocumentAIService()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.compliance_engine = ComplianceEngine()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all routes with MCP protocol compliance."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "mcp_server": "ouicomply-proper",
                "services": {
                    "mcp_protocol": "ready",
                    "tools": 3,
                    "resources": 2,
                    "prompts": 1
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @self.app.route("/", methods=["GET"])
        def root():
            """Root endpoint with server info."""
            return jsonify({
                "name": "OuiComply MCP Server",
                "version": "1.0.0",
                "protocol": "MCP",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True
                },
                "endpoints": {
                    "health": "/health",
                    "mcp": "/mcp",
                    "mcp_sse": "/mcp/sse",
                    "analyze_document": "/mcp/analyze_document",
                    "update_memory": "/mcp/update_memory",
                    "get_compliance_status": "/mcp/get_compliance_status"
                }
            })
        
        @self.app.route("/mcp", methods=["POST"])
        def mcp_endpoint():
            """Main MCP protocol endpoint - handles all MCP requests."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }), 400
                
                method = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                # Handle different MCP methods
                if method == "initialize":
                    return self._handle_initialize(request_id, params)
                elif method == "tools/list":
                    return self._handle_tools_list(request_id, params)
                elif method == "tools/call":
                    return self._handle_tools_call(request_id, params)
                elif method == "resources/list":
                    return self._handle_resources_list(request_id, params)
                elif method == "resources/read":
                    return self._handle_resources_read(request_id, params)
                elif method == "prompts/list":
                    return self._handle_prompts_list(request_id, params)
                elif method == "prompts/get":
                    return self._handle_prompts_get(request_id, params)
                else:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    })
                
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": data.get("id", "unknown"),
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }), 500
        
        # Function-based routing endpoints
        @self.app.route("/mcp/analyze_document", methods=["POST"])
        def analyze_document_endpoint():
            """
            Analyze document for compliance issues using AI.
            
            POST /mcp/analyze_document
            Body: {
                "document_content": "string",
                "document_type": "string (optional)",
                "frameworks": ["string"] (optional)
            }
            """
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "Request body is required"}), 400
                
                # Validate required fields
                if not data.get("document_content"):
                    return jsonify({"error": "document_content is required"}), 400
                
                # Call the analyze document function
                result = asyncio.run(self._analyze_document(data))
                
                return jsonify({
                    "function": "analyze_document",
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                return jsonify({
                    "function": "analyze_document",
                    "status": "error",
                    "error": str(e)
                }), 500
        
        @self.app.route("/mcp/update_memory", methods=["POST"])
        def update_memory_endpoint():
            """
            Update team memory with new compliance insights.
            
            POST /mcp/update_memory
            Body: {
                "team_id": "string",
                "insight": "string",
                "category": "string (optional)"
            }
            """
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "Request body is required"}), 400
                
                # Validate required fields
                if not data.get("team_id") or not data.get("insight"):
                    return jsonify({"error": "team_id and insight are required"}), 400
                
                # Call the update memory function
                result = asyncio.run(self._update_memory(data))
                
                return jsonify({
                    "function": "update_memory",
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                return jsonify({
                    "function": "update_memory",
                    "status": "error",
                    "error": str(e)
                }), 500
        
        @self.app.route("/mcp/get_compliance_status", methods=["POST"])
        def get_compliance_status_endpoint():
            """
            Get current compliance status for a team.
            
            POST /mcp/get_compliance_status
            Body: {
                "team_id": "string",
                "framework": "string (optional)"
            }
            """
            try:
                data = request.get_json()
                if not data:
                    return jsonify({"error": "Request body is required"}), 400
                
                # Validate required fields
                if not data.get("team_id"):
                    return jsonify({"error": "team_id is required"}), 400
                
                # Call the get compliance status function
                result = asyncio.run(self._get_compliance_status(data))
                
                return jsonify({
                    "function": "get_compliance_status",
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                return jsonify({
                    "function": "get_compliance_status",
                    "status": "error",
                    "error": str(e)
                }), 500
        
        @self.app.route("/mcp/sse", methods=["GET"])
        def mcp_sse_endpoint():
            """Server-Sent Events endpoint for MCP."""
            def generate():
                import time
                
                # Send initial connection event
                yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                
                # Keep connection alive and send periodic updates
                while True:
                    try:
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                        time.sleep(30)  # Send heartbeat every 30 seconds
                    except GeneratorExit:
                        break
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                        break
            
            return Response(generate(), mimetype='text/event-stream')
    
    def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP initialize request."""
        return jsonify({
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
                    "name": "ouicomply-mcp",
                    "version": "1.0.0"
                }
            }
        })
    
    def _handle_tools_list(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP tools/list request."""
        tools = [
            {
                "name": "analyze_document",
                "description": "Analyze a document for compliance issues using AI",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {"type": "string", "description": "Document content to analyze"},
                        "document_type": {"type": "string", "description": "Type of document (contract, policy, etc.)"},
                        "frameworks": {"type": "array", "items": {"type": "string"}, "description": "Compliance frameworks to check"}
                    },
                    "required": ["document_content"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update team memory with new compliance insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {"type": "string", "description": "Team identifier"},
                        "insight": {"type": "string", "description": "Compliance insight to store"},
                        "category": {"type": "string", "description": "Category of insight"}
                    },
                    "required": ["team_id", "insight"]
                }
            },
            {
                "name": "get_compliance_status",
                "description": "Get current compliance status for a team",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {"type": "string", "description": "Team identifier"},
                        "framework": {"type": "string", "description": "Specific framework to check"}
                    },
                    "required": ["team_id"]
                }
            }
        ]
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        })
    
    def _handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "analyze_document":
                result = asyncio.run(self._analyze_document(arguments))
            elif tool_name == "update_memory":
                result = asyncio.run(self._update_memory(arguments))
            elif tool_name == "get_compliance_status":
                result = asyncio.run(self._get_compliance_status(arguments))
            else:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })
            
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            })
        except Exception as e:
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Tool execution error: {str(e)}"}
            })
    
    def _handle_resources_list(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP resources/list request."""
        resources = [
            {
                "uri": "compliance://frameworks",
                "name": "Compliance Frameworks",
                "description": "Available compliance frameworks and their requirements",
                "mimeType": "application/json"
            },
            {
                "uri": "memory://team",
                "name": "Team Memory",
                "description": "Team-specific compliance memory and insights",
                "mimeType": "application/json"
            }
        ]
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": resources}
        })
    
    def _handle_resources_read(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP resources/read request."""
        uri = params.get("uri")
        
        if uri == "compliance://frameworks":
            content = {
                "frameworks": ["gdpr", "sox", "ccpa", "hipaa"],
                "descriptions": {
                    "gdpr": "General Data Protection Regulation",
                    "sox": "Sarbanes-Oxley Act",
                    "ccpa": "California Consumer Privacy Act",
                    "hipaa": "Health Insurance Portability and Accountability Act"
                }
            }
        elif uri == "memory://team":
            content = {
                "team_id": "default",
                "insights": [],
                "last_updated": datetime.utcnow().isoformat()
            }
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"Resource not found: {uri}"}
            })
        
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, indent=2)
                    }
                ]
            }
        })
    
    def _handle_prompts_list(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP prompts/list request."""
        prompts = [
            {
                "name": "compliance_analysis",
                "description": "Prompt template for compliance analysis",
                "arguments": [
                    {"name": "document_type", "description": "Type of document to analyze", "required": True},
                    {"name": "frameworks", "description": "Compliance frameworks to check", "required": False}
                ]
            }
        ]
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"prompts": prompts}
        })
    
    def _handle_prompts_get(self, request_id: Any, params: Dict[str, Any]) -> Response:
        """Handle MCP prompts/get request."""
        prompt_name = params.get("name")
        prompt_args = params.get("arguments", {})
        
        if prompt_name == "compliance_analysis":
            document_type = prompt_args.get("document_type", "contract")
            frameworks = prompt_args.get("frameworks", ["gdpr", "sox"])
            
            prompt_text = f"""
            Analyze the following {document_type} for compliance with {', '.join(frameworks)} frameworks.
            
            Please identify:
            1. Compliance issues and violations
            2. Missing required clauses
            3. Risk assessment
            4. Recommendations for improvement
            
            Provide a detailed analysis with specific references to the relevant compliance requirements.
            """
            
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
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
            })
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"Prompt not found: {prompt_name}"}
            })
    
    async def _analyze_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document for compliance."""
        try:
            document_content = arguments.get("document_content", "")
            document_type = arguments.get("document_type", "contract")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            # Use the compliance engine
            report = await self.compliance_engine.analyze_document_compliance(
                document_content=document_content,
                document_type=document_type,
                frameworks=frameworks
            )
            
            return {
                "report_id": report.report_id,
                "status": report.overall_status.value,
                "risk_level": report.risk_level.value,
                "risk_score": report.risk_score,
                "issues_count": len(report.issues),
                "summary": report.summary
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update team memory."""
        try:
            team_id = arguments.get("team_id", "default")
            insight = arguments.get("insight", "")
            category = arguments.get("category", "general")
            
            # Use memory integration
            result = await self.memory_integration.store_insight(
                team_id=team_id,
                insight=insight,
                category=category
            )
            
            return {
                "team_id": team_id,
                "insight_stored": True,
                "memory_id": result.get("memory_id", "unknown")
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance status."""
        try:
            team_id = arguments.get("team_id", "default")
            framework = arguments.get("framework", "all")
            
            # Use memory integration to get status
            status = await self.memory_integration.get_team_status(team_id)
            
            return {
                "team_id": team_id,
                "framework": framework,
                "status": status.get("overall_status", "unknown"),
                "last_updated": status.get("last_updated", "unknown")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run(self, host="0.0.0.0", port=8000, debug=False):
        """Run the MCP server."""
        print(f"🚀 Starting OuiComply MCP Server (Proper Implementation)...")
        print(f"📡 Health Check: http://localhost:{port}/health")
        print(f"🔧 MCP Protocol: http://localhost:{port}/mcp")
        print(f"📡 SSE Endpoint: http://localhost:{port}/mcp/sse")
        print(f"✅ All tool calls, resources, and prompts routed through /mcp")
        print(f"")
        print(f"🔧 Function-based routing endpoints:")
        print(f"   📄 Analyze Document: POST http://localhost:{port}/mcp/analyze_document")
        print(f"   🧠 Update Memory: POST http://localhost:{port}/mcp/update_memory")
        print(f"   📊 Get Compliance Status: POST http://localhost:{port}/mcp/get_compliance_status")
        
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = MCPProperServer()
    server.run(port=port)
