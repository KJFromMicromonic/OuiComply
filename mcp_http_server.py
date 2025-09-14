#!/usr/bin/env python3
"""
HTTP wrapper for official MCP server to enable web deployment
"""

import asyncio
import json
import os
from typing import Dict, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from mcp_server_official import OuiComplyMCPServer

class MCPHTTPServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Initialize the MCP server
        self.mcp_server = OuiComplyMCPServer()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes that wrap MCP functionality."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "mcp_server": "ouicomply-official",
                "services": {
                    "mcp_protocol": "ready",
                    "tools": 3,
                    "resources": 2,
                    "prompts": 1
                },
                "timestamp": "2025-09-14T01:45:00Z"
            })
        
        @self.app.route("/", methods=["GET"])
        def root():
            """Root endpoint with server info."""
            return jsonify({
                "name": "OuiComply MCP Server (Official)",
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
                    "tools": "/tools",
                    "resources": "/resources",
                    "prompts": "/prompts",
                    "call_tool": "/call_tool"
                }
            })
        
        @self.app.route("/tools", methods=["GET"])
        def list_tools():
            """List available tools."""
            try:
                # Get tools from MCP server
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
                return jsonify({"tools": tools})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/resources", methods=["GET"])
        def list_resources():
            """List available resources."""
            try:
                resources = [
                    {
                        "name": "compliance_frameworks",
                        "description": "Available compliance frameworks and their requirements",
                        "mimeType": "application/json"
                    },
                    {
                        "name": "team_memory",
                        "description": "Team-specific compliance memory and insights",
                        "mimeType": "application/json"
                    }
                ]
                return jsonify({"resources": resources})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/prompts", methods=["GET"])
        def list_prompts():
            """List available prompts."""
            try:
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
                return jsonify({"prompts": prompts})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/mcp", methods=["POST"])
        def mcp_endpoint():
            """MCP protocol endpoint for Le Chat integration."""
            try:
                data = request.get_json()
                method = data.get("method")
                params = data.get("params", {})
                
                if method == "initialize":
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
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
                
                elif method == "tools/list":
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
                        "id": data.get("id"),
                        "result": {"tools": tools}
                    })
                
                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    if tool_name == "analyze_document":
                        result = asyncio.run(self._analyze_document(arguments))
                    elif tool_name == "update_memory":
                        result = asyncio.run(self._update_memory(arguments))
                    elif tool_name == "get_compliance_status":
                        result = asyncio.run(self._get_compliance_status(arguments))
                    else:
                        return jsonify({
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                        })
                    
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(result)
                                }
                            ]
                        }
                    })
                
                else:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    })
                
            except Exception as e:
                return jsonify({
                    "jsonrpc": "2.0",
                    "id": data.get("id", "unknown"),
                    "error": {"code": -32603, "message": str(e)}
                })
        
        @self.app.route("/mcp/sse", methods=["GET"])
        def mcp_sse_endpoint():
            """Server-Sent Events endpoint for MCP."""
            def generate():
                import time
                import json
                from datetime import datetime
                
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
        
        @self.app.route("/call_tool", methods=["POST"])
        def call_tool():
            """Call a tool with the given parameters."""
            try:
                data = request.get_json()
                tool_name = data.get("name")
                arguments = data.get("arguments", {})
                
                if not tool_name:
                    return jsonify({"error": "Tool name is required"}), 400
                
                # Call the appropriate tool
                if tool_name == "analyze_document":
                    result = asyncio.run(self._analyze_document(arguments))
                elif tool_name == "update_memory":
                    result = asyncio.run(self._update_memory(arguments))
                elif tool_name == "get_compliance_status":
                    result = asyncio.run(self._get_compliance_status(arguments))
                else:
                    return jsonify({"error": f"Unknown tool: {tool_name}"}), 400
                
                return jsonify({
                    "tool": tool_name,
                    "result": result,
                    "status": "success"
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    async def _analyze_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document for compliance."""
        try:
            document_content = arguments.get("document_content", "")
            document_type = arguments.get("document_type", "contract")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            # Use the compliance engine
            report = await self.mcp_server.compliance_engine.analyze_document_compliance(
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
            result = await self.mcp_server.memory_integration.store_insight(
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
            status = await self.mcp_server.memory_integration.get_team_status(team_id)
            
            return {
                "team_id": team_id,
                "framework": framework,
                "status": status.get("overall_status", "unknown"),
                "last_updated": status.get("last_updated", "unknown")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run(self, host="0.0.0.0", port=8000, debug=False):
        """Run the HTTP server."""
        print(f"🚀 Starting OuiComply MCP HTTP Server...")
        print(f"📡 Health Check: http://localhost:{port}/health")
        print(f"🔧 MCP Protocol: http://localhost:{port}/mcp")
        print(f"📡 SSE Endpoint: http://localhost:{port}/mcp/sse")
        print(f"🔧 Tools: http://localhost:{port}/tools")
        print(f"📚 Resources: http://localhost:{port}/resources")
        print(f"💬 Prompts: http://localhost:{port}/prompts")
        print(f"⚡ Call Tool: http://localhost:{port}/call_tool")
        
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = MCPHTTPServer()
    server.run(port=port)