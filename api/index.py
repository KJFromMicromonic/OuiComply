from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
