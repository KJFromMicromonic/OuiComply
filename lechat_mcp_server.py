#!/usr/bin/env python3
"""
Le Chat Compatible MCP Server - Complete Flask Implementation with /mcp/ routes

This server provides proper JSON-RPC 2.0 MCP protocol implementation
that Le Chat can detect and use seamlessly, while also exposing tools
through /mcp/ routes for Alpic compatibility.
"""

import os
import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeChatMCPServer:
    """Complete MCP Server implementation for Le Chat integration with /mcp/ routes."""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Server configuration
        self.server_name = os.getenv("MCP_SERVER_NAME", "ouicomply-mcp")
        self.server_version = os.getenv("MCP_SERVER_VERSION", "1.0.0")
        self.mistral_key = os.getenv("MISTRAL_KEY", "")
        
        # MCP Protocol definitions
        self.tools = self._define_tools()
        self.resources = self._define_resources()
        self.prompts = self._define_prompts()
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"🚀 {self.server_name} v{self.server_version} initialized")
        logger.info(f"📚 Tools: {len(self.tools)}")
        logger.info(f"📄 Resources: {len(self.resources)}")
        logger.info(f"💬 Prompts: {len(self.prompts)}")
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define MCP tools that Le Chat can discover and use."""
        return [
            {
                "name": "analyze_document",
                "description": "Analyze a document for compliance issues, risks, and recommendations",
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
        """Define MCP resources available to Le Chat."""
        return [
            {
                "uri": "compliance://frameworks/gdpr",
                "name": "GDPR Compliance Framework",
                "description": "General Data Protection Regulation compliance requirements",
                "mimeType": "text/plain"
            },
            {
                "uri": "compliance://frameworks/sox",
                "name": "SOX Compliance Framework", 
                "description": "Sarbanes-Oxley Act compliance requirements",
                "mimeType": "text/plain"
            },
            {
                "uri": "memory://team/insights",
                "name": "Team Memory Insights",
                "description": "Accumulated team insights and learnings",
                "mimeType": "application/json"
            }
        ]
    
    def _define_prompts(self) -> List[Dict[str, Any]]:
        """Define MCP prompts available to Le Chat."""
        return [
            {
                "name": "compliance_analysis",
                "description": "Comprehensive document compliance analysis prompt",
                "arguments": [
                    {
                        "name": "document_content",
                        "description": "Document content to analyze",
                        "required": True
                    },
                    {
                        "name": "frameworks",
                        "description": "Compliance frameworks to check against",
                        "required": False
                    }
                ]
            }
        ]
    
    def _setup_routes(self):
        """Setup Flask routes for MCP protocol and /mcp/ routes."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "server": self.server_name,
                "version": self.server_version,
                "mcp_endpoint": "/mcp",
                "sse_endpoint": "/mcp/sse",
                "tools_count": len(self.tools),
                "resources_count": len(self.resources),
                "prompts_count": len(self.prompts),
                "timestamp": datetime.now(UTC).isoformat()
            })
        
        @self.app.route("/", methods=["GET"])
        def root():
            """Root endpoint with server capabilities."""
            return jsonify({
                "name": self.server_name,
                "version": self.server_version,
                "description": "OuiComply MCP Server for Le Chat Integration",
                "protocol": "MCP",
                "protocol_version": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "endpoints": {
                    "mcp": "/mcp",
                    "sse": "/mcp/sse",
                    "health": "/health",
                    "lechat_integration": "/lechat/integration"
                },
                "ready_for_lechat": True
            })
        
        @self.app.route("/mcp", methods=["POST", "OPTIONS"])
        def mcp_endpoint():
            """Main MCP protocol endpoint - Le Chat connects here."""
            
            if request.method == "OPTIONS":
                # Handle CORS preflight
                response = jsonify({"status": "ok"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                response.headers.add("Access-Control-Allow-Headers", "Content-Type")
                response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
                return response
            
            try:
                data = request.get_json()
                if not data:
                    return jsonify({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    }), 400
                
                # Handle MCP JSON-RPC request
                response = self._handle_mcp_request(data)
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"MCP endpoint error: {e}")
                return jsonify({
                    "jsonrpc": "2.0", 
                    "id": data.get("id") if data else None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }), 500
        
        @self.app.route("/mcp/sse", methods=["GET"])
        def mcp_sse():
            """Server-Sent Events endpoint for real-time updates."""
            def event_stream():
                yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
                
                # Keep connection alive
                import time
                while True:
                    try:
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
                        time.sleep(30)
                    except GeneratorExit:
                        break
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
                        break
            
            return Response(event_stream(), mimetype='text/event-stream')
        
        @self.app.route("/lechat/integration", methods=["GET"])
        def lechat_integration():
            """Le Chat integration information."""
            return jsonify({
                "status": "ready",
                "mcp_endpoint": "/mcp",
                "sse_endpoint": "/mcp/sse", 
                "protocol": "MCP",
                "protocol_version": "2024-11-05",
                "server_name": self.server_name,
                "server_version": self.server_version,
                "tools": len(self.tools),
                "resources": len(self.resources),
                "prompts": len(self.prompts),
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                    "server_sent_events": True
                },
                "description": "Complete MCP server for compliance document analysis"
            })
        
        # Add /mcp/ routes for Alpic compatibility
        self._setup_mcp_routes()
    
    def _setup_mcp_routes(self):
        """Setup /mcp/ routes for Alpic compatibility."""
        
        @self.app.route("/mcp/analyze_document", methods=["GET", "POST"])
        def mcp_analyze_document():
            """MCP analyze_document tool via /mcp/ route."""
            try:
                if request.method == "GET":
                    # Return tool definition
                    return jsonify({
                        "tool": "analyze_document",
                        "description": "Analyze a document for compliance issues, risks, and recommendations",
                        "usage": "POST with document_content and optional parameters",
                        "parameters": {
                            "document_content": "string (required)",
                            "document_type": "string (optional, default: document)",
                            "frameworks": "array (optional, default: [gdpr])",
                            "team_context": "string (optional, default: Legal Team)"
                        }
                    })
                
                # Handle POST request
                data = request.get_json() or {}
                result = self._analyze_document(data)
                return jsonify({
                    "success": True,
                    "tool": "analyze_document",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
                
            except Exception as e:
                logger.error(f"analyze_document error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "tool": "analyze_document"
                }), 500
        
        @self.app.route("/mcp/update_memory", methods=["GET", "POST"])
        def mcp_update_memory():
            """MCP update_memory tool via /mcp/ route."""
            try:
                if request.method == "GET":
                    # Return tool definition
                    return jsonify({
                        "tool": "update_memory",
                        "description": "Update team memory with insights from document analysis",
                        "usage": "POST with team_id, insight and optional parameters",
                        "parameters": {
                            "team_id": "string (required)",
                            "insight": "string (required)",
                            "category": "string (optional, default: general)",
                            "document_type": "string (optional, default: document)"
                        }
                    })
                
                # Handle POST request
                data = request.get_json() or {}
                result = self._update_memory(data)
                return jsonify({
                    "success": True,
                    "tool": "update_memory",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
                
            except Exception as e:
                logger.error(f"update_memory error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "tool": "update_memory"
                }), 500
        
        @self.app.route("/mcp/get_compliance_status", methods=["GET", "POST"])
        def mcp_get_compliance_status():
            """MCP get_compliance_status tool via /mcp/ route."""
            try:
                if request.method == "GET":
                    # Return tool definition
                    return jsonify({
                        "tool": "get_compliance_status",
                        "description": "Get current compliance status and metrics for a team",
                        "usage": "POST with team_id and optional parameters",
                        "parameters": {
                            "team_id": "string (required)",
                            "framework": "string (optional)",
                            "include_recommendations": "boolean (optional, default: true)"
                        }
                    })
                
                # Handle POST request
                data = request.get_json() or {}
                result = self._get_compliance_status(data)
                return jsonify({
                    "success": True,
                    "tool": "get_compliance_status",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
                
            except Exception as e:
                logger.error(f"get_compliance_status error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "tool": "get_compliance_status"
                }), 500
        
        @self.app.route("/mcp/compliance_frameworks", methods=["GET"])
        def mcp_compliance_frameworks():
            """MCP compliance_frameworks resource via /mcp/ route."""
            try:
                result = self._get_compliance_frameworks()
                return jsonify({
                    "success": True,
                    "resource": "compliance_frameworks",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
            except Exception as e:
                logger.error(f"compliance_frameworks error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "resource": "compliance_frameworks"
                }), 500
        
        @self.app.route("/mcp/legal_templates", methods=["GET"])
        def mcp_legal_templates():
            """MCP legal_templates resource via /mcp/ route."""
            try:
                result = self._get_legal_templates()
                return jsonify({
                    "success": True,
                    "resource": "legal_templates",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
            except Exception as e:
                logger.error(f"legal_templates error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "resource": "legal_templates"
                }), 500
        
        @self.app.route("/mcp/team_memory", methods=["GET"])
        def mcp_team_memory():
            """MCP team_memory resource via /mcp/ route."""
            try:
                result = self._get_team_memory()
                return jsonify({
                    "success": True,
                    "resource": "team_memory",
                    "result": result,
                    "timestamp": datetime.now(UTC).isoformat()
                })
            except Exception as e:
                logger.error(f"team_memory error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "resource": "team_memory"
                }), 500
    
    def _handle_mcp_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC 2.0 requests."""
        method = data.get("method")
        request_id = data.get("id")
        params = data.get("params", {})
        
        logger.info(f"📨 MCP Request: {method}")
        
        # Handle different MCP methods
        if method == "initialize":
            return self._handle_initialize(request_id, params)

        elif method == "tools/list":
            return self._handle_tools_list(request_id)

        elif method == "tools/call":
            return self._handle_tools_call(request_id, params)

        elif method == "resources/list":
            return self._handle_resources_list(request_id)

        elif method == "resources/read":
            return self._handle_resources_read(request_id, params)

        elif method == "prompts/list":
            return self._handle_prompts_list(request_id)

        elif method == "prompts/get":
            return self._handle_prompts_get(request_id, params)

        elif method == "oauth/metadata":
            return self._handle_oauth_metadata(request_id)

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
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
    
    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle tools/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    def _handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"🔧 Calling tool: {tool_name}")
        
        try:
            if tool_name == "analyze_document":
                result = self._analyze_document(arguments)
            elif tool_name == "update_memory":
                result = self._update_memory(arguments)
            elif tool_name == "get_compliance_status":
                result = self._get_compliance_status(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    def _handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle resources/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": self.resources
            }
        }
    
    def _handle_resources_read(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request."""
        uri = params.get("uri")
        
        # Mock resource content based on URI
        if uri == "compliance://frameworks/gdpr":
            content = "GDPR compliance requires: data protection, consent management, breach notification, data subject rights..."
        elif uri == "compliance://frameworks/sox":
            content = "SOX compliance requires: internal controls, financial reporting accuracy, audit trails..."
        elif uri == "memory://team/insights":
            content = json.dumps({"insights": [], "last_updated": datetime.now(UTC).isoformat()})
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"Unknown resource: {uri}"}
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": content
                    }
                ]
            }
        }
    
    def _handle_prompts_list(self, request_id: Any) -> Dict[str, Any]:
        """Handle prompts/list request."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "prompts": self.prompts
            }
        }
    
    def _handle_prompts_get(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/get request."""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "compliance_analysis":
            document_content = arguments.get("document_content", "")
            frameworks = arguments.get("frameworks", ["gdpr"])
            
            prompt = f"""Analyze this document for compliance with {', '.join(frameworks)}:

Document: {document_content[:500]}...

Provide:
1. Compliance score (0-100)
2. Key issues found
3. Risk assessment 
4. Specific recommendations
5. Missing clauses or requirements
"""
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "description": "Comprehensive compliance analysis prompt",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": prompt
                            }
                        }
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": f"Unknown prompt: {name}"}
            }
    
    # Tool Implementation Methods
    def _analyze_document(self, arguments: Dict[str, Any]) -> str:
        """Analyze document for compliance issues."""
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type", "document")
        frameworks = arguments.get("frameworks", ["gdpr"])
        team_context = arguments.get("team_context", "Legal Team")
        
        # Mock analysis result - replace with your actual implementation
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
            "missing_clauses": [
                "Data subject rights section",
                "Breach notification procedures"
            ],
            "compliance_gaps": {
                "gdpr": ["Article 6 (Legal basis)", "Article 13 (Information to be provided)"]
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        # Format result for Le Chat
        result = f"""📊 **Document Analysis Complete**

**Document Type:** {document_type}
**Frameworks:** {', '.join(frameworks)}
**Team:** {team_context}

**🎯 Compliance Score: {analysis_result['compliance_score']}/100**
**⚠️ Risk Level: {analysis_result['risk_level']}**

**🔍 Issues Found:**
{chr(10).join([f"• {issue}" for issue in analysis_result['issues_found']])}

**💡 Recommendations:**
{chr(10).join([f"• {rec}" for rec in analysis_result['recommendations']])}

**📋 Missing Clauses:**
{chr(10).join([f"• {clause}" for clause in analysis_result['missing_clauses']])}

**Analysis ID:** {analysis_result['analysis_id']}
**Timestamp:** {analysis_result['timestamp']}
"""
        
        logger.info(f"✅ Document analysis completed: {analysis_result['compliance_score']}/100")
        return result
    
    def _update_memory(self, arguments: Dict[str, Any]) -> str:
        """Update team memory with insights."""
        team_id = arguments.get("team_id", "")
        insight = arguments.get("insight", "")
        category = arguments.get("category", "general")
        document_type = arguments.get("document_type", "document")
        
        # Mock memory update - replace with your actual implementation
        memory_entry = {
            "id": f"memory_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "team_id": team_id,
            "insight": insight,
            "category": category,
            "document_type": document_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "confidence": 0.95
        }
        
        result = f"""🧠 **Memory Updated Successfully**

**Team:** {team_id}
**Category:** {category}
**Document Type:** {document_type}

**💡 Insight Added:**
{insight}

**Memory ID:** {memory_entry['id']}
**Confidence:** {memory_entry['confidence']}
**Updated:** {memory_entry['timestamp']}
"""
        
        logger.info(f"🧠 Memory updated for team: {team_id}")
        return result
    
    def _get_compliance_status(self, arguments: Dict[str, Any]) -> str:
        """Get team compliance status."""
        team_id = arguments.get("team_id", "")
        framework = arguments.get("framework", "")
        include_recommendations = arguments.get("include_recommendations", True)
        
        # Mock compliance status - replace with your actual implementation
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
        
        result = f"""📈 **Compliance Status for {team_id}**

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
        
        if include_recommendations and status_data['pending_issues'] > 0:
            result += f"""

**🔧 Recommendations:**
• Review {status_data['pending_issues']} pending compliance issues
• Focus on SOX compliance improvements
• Schedule quarterly compliance review
"""
        
        logger.info(f"📈 Compliance status retrieved for team: {team_id}")
        return result
    
    def _get_compliance_frameworks(self) -> Dict[str, Any]:
        """Get compliance frameworks resource."""
        return {
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
    
    def _get_legal_templates(self) -> Dict[str, Any]:
        """Get legal templates resource."""
        return {
            "templates": {
                "privacy_policy": {
                    "name": "Privacy Policy Template",
                    "description": "GDPR-compliant privacy policy template",
                    "required_sections": ["Data collection", "Data usage", "User rights", "Contact information"]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    def _get_team_memory(self) -> Dict[str, Any]:
        """Get team memory resource."""
        return {
            "teams": {},
            "global_insights": [],
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the Flask MCP server."""
        logger.info(f"🚀 Starting {self.server_name} v{self.server_version}")
        logger.info(f"📡 Le Chat MCP Endpoint: http://{host}:{port}/mcp")
        logger.info(f"📊 Health Check: http://{host}:{port}/health")
        logger.info(f"🔗 Integration Info: http://{host}:{port}/lechat/integration")
        logger.info("🔧 MCP Tools via /mcp/ routes:")
        logger.info("  - /mcp/analyze_document")
        logger.info("  - /mcp/update_memory")
        logger.info("  - /mcp/get_compliance_status")
        logger.info("  - /mcp/compliance_frameworks")
        logger.info("  - /mcp/legal_templates")
        logger.info("  - /mcp/team_memory")
        logger.info("✅ Ready for Le Chat integration and Alpic deployment!")
        
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point."""
    # Get configuration from environment
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # Create and run server
    server = LeChatMCPServer()
    server.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
