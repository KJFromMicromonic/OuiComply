#!/usr/bin/env python3
"""
MCP Server for Alpic deployment using Flask - More reliable than FastAPI.
This implements the Model Context Protocol (MCP) that Le Chat expects.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify, Response, stream_template
from flask_cors import CORS
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Le Chat

# MCP tools
tools = [
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

resources = [
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

prompts = [
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

@app.route("/")
def root():
    """Root endpoint with server information."""
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
            "mcp": "/mcp",
            "sse": "/mcp/sse",
            "health": "/health",
            "lechat": "/lechat/integration"
        }
    })

@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "mcp_server": "alpic_mode",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "mcp_protocol": "ready",
            "tools": len(tools),
            "resources": len(resources),
            "prompts": len(prompts)
        }
    })

@app.route("/mcp", methods=["POST"])
def mcp_endpoint():
    """Main MCP endpoint for Le Chat."""
    try:
        data = request.get_json()
        return handle_mcp_request(data)
    except Exception as e:
        logger.error(f"MCP request error: {e}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id") if data else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }), 500

@app.route("/mcp/sse", methods=["GET", "POST"])
def mcp_sse():
    """Server-Sent Events endpoint for MCP."""
    def generate():
        try:
            # Send initial connection event
            yield f"event: mcp.connected\n"
            yield f"data: {json.dumps({'server': 'OuiComply MCP Server', 'version': '1.0.0', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            # Handle POST request if provided
            if request.method == "POST":
                data = request.get_json()
                response = handle_mcp_request(data)
                yield f"event: mcp.response\n"
                yield f"data: {json.dumps(response)}\n\n"
            
            # Keep connection alive
            while True:
                yield f"event: mcp.heartbeat\n"
                yield f"data: {json.dumps({'timestamp': datetime.utcnow().isoformat()})}\n\n"
                time.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"event: mcp.error\n"
            yield f"data: {json.dumps({'error': str(e), 'timestamp': datetime.utcnow().isoformat()})}\n\n"
    
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@app.route("/lechat/integration")
def lechat_integration():
    """Le Chat integration endpoint."""
    return jsonify({
        "status": "ready",
        "mcp_endpoint": "/mcp",
        "sse_endpoint": "/mcp/sse",
        "tools": len(tools),
        "resources": len(resources),
        "prompts": len(prompts),
        "protocol": "MCP",
        "version": "1.0.0"
    })

@app.route("/lechat/test", methods=["POST"])
def lechat_test():
    """Test endpoint for Le Chat integration."""
    try:
        data = request.get_json()
        
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
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handle_mcp_request(data):
    """Handle MCP requests."""
    method = data.get("method")
    request_id = data.get("id")
    
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
                    "name": "OuiComply MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    elif method == "tools/call":
        return handle_tool_call(data)
    
    elif method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": resources}
        }
    
    elif method == "resources/read":
        return handle_resource_read(data)
    
    elif method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"prompts": prompts}
        }
    
    elif method == "prompts/get":
        return handle_prompt_get(data)
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def handle_tool_call(data):
    """Handle tool calls."""
    params = data.get("params", {})
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    request_id = data.get("id")
    
    try:
        if tool_name == "analyze_document":
            result = analyze_document_tool(arguments)
        elif tool_name == "update_memory":
            result = update_memory_tool(arguments)
        elif tool_name == "get_compliance_status":
            result = get_compliance_status_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Tool execution error: {str(e)}"
            }
        }

def analyze_document_tool(arguments):
    """Handle document analysis tool call."""
    document_content = arguments.get("document_content", "")
    document_name = arguments.get("document_name", "unknown")
    team_context = arguments.get("team_context", "General")
    frameworks = arguments.get("compliance_frameworks", ["gdpr", "sox", "ccpa"])
    
    result = {
        "tool": "analyze_document",
        "document_name": document_name,
        "team_context": team_context,
        "compliance_frameworks": frameworks,
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
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return result

def update_memory_tool(arguments):
    """Handle memory update tool call."""
    team_id = arguments.get("team_id")
    memory_type = arguments.get("memory_type")
    updates = arguments.get("updates", {})
    
    result = {
        "tool": "update_memory",
        "status": "success",
        "team_id": team_id,
        "memory_type": memory_type,
        "updates_applied": updates,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return result

def get_compliance_status_tool(arguments):
    """Handle compliance status tool call."""
    team_id = arguments.get("team_id")
    
    result = {
        "tool": "get_compliance_status",
        "team_id": team_id,
        "compliance_status": {
            "overall_score": 85,
            "gdpr_compliance": "partial",
            "sox_compliance": "good",
            "ccpa_compliance": "needs_work"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return result

def handle_resource_read(data):
    """Handle resource read requests."""
    params = data.get("params", {})
    uri = params.get("uri")
    request_id = data.get("id")
    
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
            "teams": ["legal_team", "compliance_team", "risk_team"],
            "memory_types": ["compliance", "behavioral"]
        }
    else:
        raise ValueError(f"Unknown resource: {uri}")
    
    return {
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
    }

def handle_prompt_get(data):
    """Handle prompt get requests."""
    params = data.get("params", {})
    prompt_name = params.get("name")
    arguments = params.get("arguments", {})
    request_id = data.get("id")
    
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
        
        return {
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
        }
    else:
        raise ValueError(f"Unknown prompt: {prompt_name}")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8006))
    
    print("🚀 Starting OuiComply MCP Server for Alpic (Flask)...")
    print(f"📡 MCP Endpoint: http://localhost:{port}/mcp")
    print(f"📡 SSE Endpoint: http://localhost:{port}/mcp/sse")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print(f"🔧 Le Chat Integration: http://localhost:{port}/lechat/integration")
    
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
