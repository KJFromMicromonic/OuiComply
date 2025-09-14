# OuiComply FastMCP Server Implementation

## Overview

This document describes the implementation of the OuiComply MCP server using FastMCP, which exposes all MCP tools and features as REST API endpoints accessible via `/mcp/{function}` routes, following the Model Context Protocol specification.

## Architecture

The FastMCP server implementation consists of:

1. **FastMCP Server** (`mcp_fastmcp_server.py`) - Main server using `mcp.server.fastmcp.FastMCP`
2. **Startup Script** (`start_fastmcp_server.py`) - Script to start the server
3. **Test Script** (`test_fastmcp_server.py`) - Comprehensive testing suite
4. **Underlying MCP Server** - The original `OuiComplyMCPServer` for core functionality

## Key Features

### MCP Tools (Exposed as HTTP POST endpoints)

1. **`analyze_document`**
   - **Endpoint**: `POST /tools/analyze_document`
   - **Description**: AI-powered document compliance analysis using Mistral API
   - **Parameters**:
     - `document_content` (string, required): Document text to analyze
     - `document_type` (string, default: "contract"): Type of document
     - `frameworks` (array, default: ["gdpr", "sox"]): Compliance frameworks to check
     - `analysis_depth` (string, default: "comprehensive"): Analysis depth level

2. **`update_memory`**
   - **Endpoint**: `POST /tools/update_memory`
   - **Description**: Store team compliance insights and learnings
   - **Parameters**:
     - `team_id` (string, required): Team identifier
     - `insight` (string, required): Compliance insight to store
     - `category` (string, default: "general"): Category of the insight
     - `priority` (string, default: "medium"): Priority level

3. **`get_compliance_status`**
   - **Endpoint**: `POST /tools/get_compliance_status`
   - **Description**: Get current compliance status for a team
   - **Parameters**:
     - `team_id` (string, required): Team identifier
     - `framework` (string, optional): Specific framework to check
     - `include_history` (boolean, default: false): Include historical data

4. **`automate_compliance_workflow`**
   - **Endpoint**: `POST /tools/automate_compliance_workflow`
   - **Description**: Automate compliance workflows based on document analysis
   - **Parameters**:
     - `document_content` (string, required): Document content to analyze
     - `workflow_type` (string, required): Type of workflow to automate
     - `team_id` (string, required): Team identifier
     - `priority` (string, default: "medium"): Priority level

### MCP Resources (Exposed as HTTP GET endpoints)

1. **`compliance_frameworks`**
   - **Endpoint**: `GET /resources/mcp://compliance_frameworks`
   - **Description**: Get available compliance frameworks with requirements and risk indicators
   - **Response**: JSON containing framework definitions for GDPR, SOX, CCPA, HIPAA

2. **`legal_templates`**
   - **Endpoint**: `GET /resources/mcp://legal_templates`
   - **Description**: Get available legal document templates with required sections
   - **Response**: JSON containing legal document templates

3. **`team_memory`**
   - **Endpoint**: `GET /resources/mcp://team_memory/{team_id}`
   - **Description**: Get team memory and insights for a specific team
   - **Parameters**:
     - `team_id` (path parameter): Team identifier

## Implementation Details

### FastMCP Integration

The server uses the official MCP library's FastMCP implementation:

```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
app = FastMCP("OuiComply MCP Server")

# Register tools
@app.tool(name="analyze_document", description="...")
async def analyze_document(...):
    # Implementation

# Register resources
@app.resource(uri="mcp://compliance_frameworks", name="compliance_frameworks", ...)
async def get_compliance_frameworks():
    # Implementation
```

### Error Handling

All endpoints include comprehensive error handling:

```python
try:
    # MCP server call
    result = await mcp_server._analyze_document(arguments)
    response_data = extract_content_from_mcp_result(result)
    return {"success": True, "data": response_data, ...}
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    return {"success": False, "error": "Operation failed", "detail": str(e), ...}
```

### Response Format

All endpoints return standardized responses:

```json
{
    "success": true,
    "data": {
        "content": "...",
        "type": "json|text"
    },
    "metadata": {
        "timestamp": "2025-09-14T02:56:16.001320Z",
        "additional_info": "..."
    }
}
```

## Usage

### Starting the Server

```bash
# Method 1: Direct execution
python mcp_fastmcp_server.py

# Method 2: Using startup script
python start_fastmcp_server.py
```

### Testing the Server

```bash
# Run comprehensive tests
python test_fastmcp_server.py
```

### Example API Calls

#### Document Analysis
```bash
curl -X POST "http://localhost:8000/tools/analyze_document" \
  -H "Content-Type: application/json" \
  -d '{
    "document_content": "This is a privacy policy...",
    "document_type": "privacy_policy",
    "frameworks": ["gdpr", "ccpa"]
  }'
```

#### Update Memory
```bash
curl -X POST "http://localhost:8000/tools/update_memory" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "team-123",
    "insight": "GDPR requires explicit consent",
    "category": "compliance",
    "priority": "high"
  }'
```

#### Get Compliance Frameworks
```bash
curl -X GET "http://localhost:8000/resources/mcp://compliance_frameworks"
```

## Benefits of FastMCP Implementation

1. **MCP Compliance**: Follows the official Model Context Protocol specification
2. **Standardized Interface**: Uses official MCP library for consistency
3. **REST API Access**: Exposes MCP tools as HTTP endpoints
4. **Type Safety**: Leverages Pydantic for request/response validation
5. **Error Handling**: Comprehensive error handling and logging
6. **Scalability**: Built on FastAPI foundation for high performance
7. **Documentation**: Auto-generated OpenAPI documentation

## Dependencies

- `mcp` - Official Model Context Protocol library
- `fastapi` - Web framework (via FastMCP)
- `uvicorn` - ASGI server
- `httpx` - HTTP client for testing
- `pydantic` - Data validation

## Configuration

The server runs on:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **Protocol**: HTTP/HTTPS
- **Content Type**: `application/json`

## Integration with Existing MCP Server

The FastMCP server acts as a REST API wrapper around the existing `OuiComplyMCPServer`, providing:

1. **HTTP Interface**: Converts HTTP requests to MCP tool calls
2. **Response Formatting**: Converts MCP responses to HTTP JSON
3. **Error Handling**: Standardizes error responses
4. **Logging**: Comprehensive request/response logging

This approach maintains the existing MCP functionality while adding REST API accessibility for easier integration with web applications and external systems.
