from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from datetime import datetime, UTC

app = FastAPI(title="OuiComply MCP Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "name": "ouicomply-mcp",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(UTC).isoformat()
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "server": "ouicomply-mcp",
        "timestamp": datetime.now(UTC).isoformat()
    }

@app.post("/mcp")
def mcp_endpoint(request: dict):
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "message": "MCP endpoint working",
            "timestamp": datetime.now(UTC).isoformat()
        }
    }

# Vercel handler function
def handler(request):
    """
    Vercel serverless function handler.
    
    This function is called by Vercel for each request and routes it
    to the appropriate FastAPI endpoint.
    
    @param request The incoming HTTP request from Vercel
    @returns JSONResponse with the appropriate response
    """
    try:
        # Get the path and method from the request
        path = request.get('path', '/')
        method = request.get('httpMethod', 'GET')
        body = request.get('body', '')
        headers = request.get('headers', {})
        
        # Handle root path
        if path == '/' or path == '':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "name": "ouicomply-mcp",
                    "version": "1.0.0",
                    "status": "running",
                    "timestamp": datetime.now(UTC).isoformat()
                })
            }
        
        # Handle health endpoint
        elif path == '/health':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "healthy",
                    "server": "ouicomply-mcp",
                    "timestamp": datetime.now(UTC).isoformat()
                })
            }
        
        # Handle MCP endpoint
        elif path == '/mcp' and method == 'POST':
            try:
                request_data = json.loads(body) if body else {}
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_data.get("id"),
                        "result": {
                            "message": "MCP endpoint working",
                            "timestamp": datetime.now(UTC).isoformat()
                        }
                    })
                }
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
        
        # Handle 404 for unknown paths
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Not Found",
                    "message": f"Path {path} not found",
                    "available_endpoints": ["/", "/health", "/mcp"]
                })
            }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Internal Server Error",
                "message": str(e)
            })
        }
