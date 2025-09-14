import json
from datetime import datetime, timezone

def handler(request):
    """
    Simple Vercel serverless function handler for OuiComply MCP Server.
    
    @param request The incoming HTTP request from Vercel
    @returns Dictionary with statusCode, headers, and body
    """
    try:
        # Get basic request info with defaults
        path = request.get('path', '/') if request else '/'
        method = request.get('httpMethod', 'GET') if request else 'GET'
        body = request.get('body', '') if request else ''
        
        # Basic CORS headers
        headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        
        # Handle OPTIONS requests
        if method == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": headers,
                "body": ""
            }
        
        # Handle root path
        if path == '/' or path == '':
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "name": "ouicomply-mcp",
                    "version": "1.0.0",
                    "status": "running",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
        
        # Handle health endpoint
        elif path == '/health':
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "status": "healthy",
                    "server": "ouicomply-mcp",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
        
        # Handle MCP endpoint
        elif path == '/mcp' and method == 'POST':
            try:
                request_data = json.loads(body) if body else {}
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_data.get("id", "unknown"),
                        "result": {
                            "message": "MCP endpoint working",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    })
                }
            except:
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "Invalid JSON"})
                }
        
        # Handle 404
        else:
            return {
                "statusCode": 404,
                "headers": headers,
                "body": json.dumps({
                    "error": "Not Found",
                    "path": path,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        }
