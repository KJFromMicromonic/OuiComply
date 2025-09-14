import json
from datetime import datetime, timezone

def handler(request):
    """
    Vercel serverless function handler for OuiComply MCP Server.
    
    This function handles all HTTP requests and routes them to appropriate
    endpoints based on the path and method.
    
    @param request The incoming HTTP request from Vercel
    @returns Dictionary with statusCode, headers, and body
    """
    try:
        # Extract request information
        path = request.get('path', '/')
        method = request.get('httpMethod', 'GET')
        body = request.get('body', '')
        headers = request.get('headers', {})
        query = request.get('queryStringParameters', {}) or {}
        
        # Set CORS headers
        cors_headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400"
        }
        
        # Handle OPTIONS requests for CORS
        if method == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": ""
            }
        
        # Handle root path
        if path == '/' or path == '':
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "name": "ouicomply-mcp",
                    "version": "1.0.0",
                    "status": "running",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "endpoints": ["/", "/health", "/mcp"]
                })
            }
        
        # Handle health endpoint
        elif path == '/health':
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "status": "healthy",
                    "server": "ouicomply-mcp",
                    "version": "1.0.0",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "uptime": "running"
                })
            }
        
        # Handle MCP endpoint
        elif path == '/mcp':
            if method == 'POST':
                try:
                    # Parse request body
                    request_data = json.loads(body) if body else {}
                    
                    # Handle MCP JSON-RPC request
                    mcp_response = {
                        "jsonrpc": "2.0",
                        "id": request_data.get("id", "unknown"),
                        "result": {
                            "message": "MCP endpoint working",
                            "server": "ouicomply-mcp",
                            "version": "1.0.0",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "capabilities": {
                                "tools": True,
                                "resources": True,
                                "prompts": False
                            }
                        }
                    }
                    
                    return {
                        "statusCode": 200,
                        "headers": cors_headers,
                        "body": json.dumps(mcp_response)
                    }
                    
                except json.JSONDecodeError as e:
                    return {
                        "statusCode": 400,
                        "headers": cors_headers,
                        "body": json.dumps({
                            "error": "Invalid JSON in request body",
                            "message": str(e)
                        })
                    }
            else:
                return {
                    "statusCode": 405,
                    "headers": cors_headers,
                    "body": json.dumps({
                        "error": "Method Not Allowed",
                        "message": f"Method {method} not allowed for /mcp endpoint. Use POST."
                    })
                }
        
        # Handle API info endpoint
        elif path == '/api':
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "api": "OuiComply MCP Server API",
                    "version": "1.0.0",
                    "endpoints": {
                        "GET /": "Server information",
                        "GET /health": "Health check",
                        "POST /mcp": "MCP protocol endpoint"
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
        
        # Handle 404 for unknown paths
        else:
            return {
                "statusCode": 404,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Not Found",
                    "message": f"Path {path} not found",
                    "available_endpoints": ["/", "/health", "/mcp", "/api"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        }
