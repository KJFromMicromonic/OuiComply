#!/usr/bin/env python3
"""
ALPIC Minimal Server - Zero-dependency Lambda-compatible MCP server

This is the absolute minimal server that will work in AWS Lambda.
No external dependencies, instant startup, pre-computed responses.

Usage: python alpic_minimal_server.py
"""

import json
import sys
from datetime import datetime, UTC

# Pre-computed responses for instant delivery
HEALTH_RESPONSE = {
    "status": "healthy",
    "service": "OuiComply MCP Server",
    "version": "1.0.0",
    "timestamp": datetime.now(UTC).isoformat(),
    "transport": "stdio"
}

INIT_RESPONSE = {
    "jsonrpc": "2.0",
    "id": None,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True}
        },
        "serverInfo": {
            "name": "ouicomply-mcp",
            "version": "1.0.0",
            "description": "OuiComply MCP Server for compliance analysis"
        }
    }
}

TOOLS_RESPONSE = {
    "jsonrpc": "2.0",
    "id": None,
    "result": {
        "tools": [
            {
                "name": "analyze_document",
                "description": "Analyze a document for compliance issues",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_content": {
                            "type": "string",
                            "description": "The document content to analyze"
                        },
                        "frameworks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance frameworks to check",
                            "default": ["gdpr"]
                        }
                    },
                    "required": ["document_content"]
                }
            },
            {
                "name": "update_memory",
                "description": "Update team memory with insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {"type": "string", "description": "Team identifier"},
                        "insight": {"type": "string", "description": "Insight to store"}
                    },
                    "required": ["team_id", "insight"]
                }
            },
            {
                "name": "get_compliance_status",
                "description": "Get team compliance status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {"type": "string", "description": "Team identifier"}
                    },
                    "required": ["team_id"]
                }
            }
        ]
    }
}

RESOURCES_RESPONSE = {
    "jsonrpc": "2.0",
    "id": None,
    "result": {
        "resources": [
            {
                "uri": "compliance://frameworks",
                "name": "Compliance Frameworks",
                "description": "Supported compliance frameworks",
                "mimeType": "application/json"
            },
            {
                "uri": "memory://team",
                "name": "Team Memory",
                "description": "Team compliance insights",
                "mimeType": "application/json"
            }
        ]
    }
}

def get_tool_response(tool_name, arguments):
    """Generate tool response."""
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "content": [{
                "type": "text",
                "text": f"✅ **{tool_name.replace('_', ' ').title()} Complete**\n\n"
                       f"**Arguments:** {json.dumps(arguments, indent=2)}\n\n"
                       f"**Result:** Tool executed successfully\n"
                       f"**Timestamp:** {datetime.now(UTC).isoformat()}\n\n"
                       f"**Note:** This is a minimal implementation for ALPIC deployment. "
                       f"Full functionality requires the complete server with AI dependencies."
            }]
        }
    }

def get_resource_response(uri):
    """Generate resource response."""
    return {
        "jsonrpc": "2.0",
        "id": None,
        "result": {
            "contents": [{
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({
                    "resource": uri,
                    "name": uri.split("/")[-1].replace("_", " ").title(),
                    "description": f"Resource data for {uri}",
                    "last_updated": datetime.now(UTC).isoformat(),
                    "note": "This is a minimal implementation for ALPIC deployment"
                }, indent=2)
            }]
        }
    }

def main():
    """Main stdio MCP handler."""
    print("🚀 OuiComply Minimal MCP Server starting...", flush=True)
    print("📡 Transport: stdio (ALPIC compatible)", flush=True)
    print("⚡ Zero-dependency startup for AWS Lambda", flush=True)
    
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line.strip())
                method = request.get("method")
                request_id = request.get("id")
                params = request.get("params", {})
                
                # Instant responses based on method
                if method == "initialize":
                    response = INIT_RESPONSE.copy()
                    response["id"] = request_id
                elif method == "tools/list":
                    response = TOOLS_RESPONSE.copy()
                    response["id"] = request_id
                elif method == "tools/call":
                    tool_name = params.get("name", "unknown")
                    arguments = params.get("arguments", {})
                    response = get_tool_response(tool_name, arguments)
                    response["id"] = request_id
                elif method == "resources/list":
                    response = RESOURCES_RESPONSE.copy()
                    response["id"] = request_id
                elif method == "resources/read":
                    uri = params.get("uri", "unknown")
                    response = get_resource_response(uri)
                    response["id"] = request_id
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }
                
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)
    
    except KeyboardInterrupt:
        print("🛑 Server stopped by user", flush=True)
    except Exception as e:
        print(f"❌ Server error: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
