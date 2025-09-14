# Ultra-fast Lambda handler for direct invocation - no imports, pure response
def lambda_handler(event, context):
    """Lambda handler for direct invocation - ultra fast, no dependencies."""
    # Handle the specific payload format for oauth/metadata
    if event.get("v20250806", {}).get("message", {}).get("method") == "oauth/metadata":
        return {
            "jsonrpc": "2.0",
            "id": event["v20250806"]["message"].get("id", "unknown"),
            "result": {
                "oauth": {
                    "version": "1.0.0",
                    "server_name": "ouicomply-mcp",
                    "capabilities": {
                        "tools": True,
                        "resources": True,
                        "prompts": False,
                        "logging": True
                    },
                    "status": "ready",
                    "transport": "streamable-http"
                }
            }
        }

    # Default response
    return {
        "jsonrpc": "2.0",
        "id": "unknown",
        "error": {"code": -32601, "message": "Method not found"}
    }
