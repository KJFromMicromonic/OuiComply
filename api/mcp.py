#!/usr/bin/env python3
"""
Vercel API route for MCP server.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    Resource,
    TextContent,
    Tool,
)

# Import our existing tools
from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine


# Create the server instance
server = Server("ouicomply-mcp")

# Initialize our services
document_ai_service = DocumentAIService()
memory_integration = MemoryIntegration(use_lechat_mcp=True)
compliance_engine = ComplianceEngine()


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(
        tools=[
            Tool(
                name="analyze_document",
                description="Analyze a document for compliance issues using AI",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_content": {
                            "type": "string",
                            "description": "Document content to analyze"
                        },
                        "document_type": {
                            "type": "string",
                            "description": "Type of document (contract, policy, etc.)",
                            "default": "contract"
                        },
                        "frameworks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Compliance frameworks to check",
                            "default": ["gdpr", "sox"]
                        }
                    },
                    "required": ["document_content"]
                }
            ),
            Tool(
                name="update_memory",
                description="Update team memory with new compliance insights",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        },
                        "insight": {
                            "type": "string",
                            "description": "Compliance insight to store"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of insight",
                            "default": "general"
                        }
                    },
                    "required": ["team_id", "insight"]
                }
            ),
            Tool(
                name="get_compliance_status",
                description="Get current compliance status for a team",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Team identifier"
                        },
                        "framework": {
                            "type": "string",
                            "description": "Specific framework to check",
                            "default": "all"
                        }
                    },
                    "required": ["team_id"]
                }
            )
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "analyze_document":
            result = await analyze_document(arguments)
        elif name == "update_memory":
            result = await update_memory(arguments)
        elif name == "get_compliance_status":
            result = await get_compliance_status(arguments)
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources."""
    return ListResourcesResult(
        resources=[
            Resource(
                uri="compliance://frameworks",
                name="Compliance Frameworks",
                description="Available compliance frameworks and their requirements",
                mimeType="application/json"
            ),
            Resource(
                uri="memory://team",
                name="Team Memory",
                description="Team-specific compliance memory and insights",
                mimeType="application/json"
            )
        ]
    )


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "compliance://frameworks":
        frameworks = {
            "gdpr": {
                "name": "General Data Protection Regulation",
                "description": "EU regulation for data protection and privacy",
                "requirements": [
                    "Data minimization",
                    "Purpose limitation",
                    "Storage limitation",
                    "Accuracy",
                    "Integrity and confidentiality",
                    "Lawfulness of processing"
                ],
                "applies_to": ["EU citizens", "EU residents", "EU data processing"]
            },
            "sox": {
                "name": "Sarbanes-Oxley Act",
                "description": "US law for financial reporting and corporate governance",
                "requirements": [
                    "Internal controls over financial reporting",
                    "Management assessment of controls",
                    "Auditor attestation",
                    "Documentation and testing",
                    "Disclosure controls"
                ],
                "applies_to": ["Public companies", "Auditors", "Management"]
            },
            "ccpa": {
                "name": "California Consumer Privacy Act",
                "description": "California state law for consumer privacy rights",
                "requirements": [
                    "Right to know",
                    "Right to delete",
                    "Right to opt-out",
                    "Right to non-discrimination",
                    "Data transparency"
                ],
                "applies_to": ["California residents", "Businesses with CA customers"]
            },
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "description": "US law for health information privacy and security",
                "requirements": [
                    "Administrative safeguards",
                    "Physical safeguards",
                    "Technical safeguards",
                    "Organizational requirements",
                    "Policies and procedures"
                ],
                "applies_to": ["Healthcare providers", "Health plans", "Business associates"]
            }
        }
        return json.dumps(frameworks, indent=2)
    elif uri.startswith("memory://team/"):
        team_id = uri.replace("memory://team/", "")
        memory_data = await memory_integration.get_team_memory(team_id)
        return json.dumps(memory_data, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompts."""
    return [
        Prompt(
            name="compliance_analysis",
            description="Prompt template for compliance analysis",
            arguments=[
                PromptArgument(
                    name="document_type",
                    description="Type of document to analyze",
                    required=True
                ),
                PromptArgument(
                    name="frameworks",
                    description="Comma-separated list of frameworks to check",
                    required=False
                )
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> List[Dict[str, Any]]:
    """Get a prompt."""
    if name == "compliance_analysis":
        document_type = arguments.get("document_type", "contract")
        frameworks = arguments.get("frameworks", "gdpr,sox")
        framework_list = [f.strip() for f in frameworks.split(",")]
        
        prompt_text = f"""
# Compliance Analysis Prompt

You are a legal compliance expert analyzing a {document_type} for compliance with the following frameworks: {', '.join(framework_list)}.

## Analysis Instructions

1. **Document Review**: Carefully examine the document content for compliance issues
2. **Framework Mapping**: Check each requirement against the specified frameworks
3. **Risk Assessment**: Evaluate the severity and likelihood of compliance violations
4. **Recommendations**: Provide specific, actionable recommendations for improvement

## Required Analysis Sections

### 1. Executive Summary
- Overall compliance status (Compliant/Non-Compliant/Partially Compliant)
- Risk level (Low/Medium/High/Critical)
- Key findings and immediate actions required

### 2. Detailed Findings
For each framework ({', '.join(framework_list)}):
- Specific compliance requirements
- Current document status for each requirement
- Identified gaps and violations
- Risk assessment for each gap

### 3. Recommendations
- Immediate actions required
- Short-term improvements (1-3 months)
- Long-term compliance strategy (3-12 months)
- Resource requirements and timeline

### 4. Implementation Plan
- Priority matrix for addressing issues
- Dependencies and prerequisites
- Success metrics and monitoring

## Output Format
Provide your analysis in a structured format with clear headings, bullet points, and specific references to document sections and compliance requirements.

Remember to be thorough, accurate, and practical in your recommendations.
"""
        
        return [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_text
                }
            }
        ]
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def analyze_document(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze document for compliance."""
    try:
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type", "contract")
        frameworks = arguments.get("frameworks", ["gdpr", "sox"])
        
        # Use the compliance engine for analysis
        report = await compliance_engine.analyze_document_compliance(
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
            "summary": report.summary,
            "frameworks_analyzed": frameworks,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


async def update_memory(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Update team memory."""
    try:
        team_id = arguments.get("team_id", "default")
        insight = arguments.get("insight", "")
        category = arguments.get("category", "general")
        
        # Store the insight in memory
        result = await memory_integration.store_insight(
            team_id=team_id,
            insight=insight,
            category=category
        )
        
        return {
            "team_id": team_id,
            "insight_stored": True,
            "memory_id": result.get("memory_id", "unknown"),
            "category": category,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "team_id": arguments.get("team_id", "unknown"),
            "insight_stored": False,
            "timestamp": datetime.utcnow().isoformat()
        }


async def get_compliance_status(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Get compliance status."""
    try:
        team_id = arguments.get("team_id", "default")
        framework = arguments.get("framework", "all")
        
        # Get team status from memory
        status = await memory_integration.get_team_status(team_id)
        
        return {
            "team_id": team_id,
            "framework": framework,
            "overall_status": status.get("overall_status", "unknown"),
            "last_updated": status.get("last_updated", datetime.utcnow().isoformat()),
            "compliance_score": status.get("compliance_score", 0.0),
            "active_frameworks": status.get("active_frameworks", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "team_id": arguments.get("team_id", "unknown"),
            "framework": arguments.get("framework", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }


def handler(request):
    """Vercel serverless function handler."""
    from http.server import BaseHTTPRequestHandler
    import io
    
    class Request:
        def __init__(self, method, path, headers, body):
            self.method = method
            self.path = path
            self.headers = headers
            self.body = body
    
    # Parse the request
    method = request.get("method", "GET")
    path = request.get("path", "/")
    headers = request.get("headers", {})
    body = request.get("body", "")
    
    # Create request object
    req = Request(method, path, headers, body)
    
    # Handle different endpoints
    if path == "/health" or path == "/":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({
                "status": "healthy",
                "mcp_server": "ouicomply-vercel",
                "services": {
                    "mcp_protocol": "ready",
                    "tools": 3,
                    "resources": 2,
                    "prompts": 1
                },
                "timestamp": datetime.utcnow().isoformat(),
                "deployment": "vercel"
            })
        }
    
    elif path == "/mcp":
        if method == "POST":
            try:
                # Parse JSON-RPC request
                data = json.loads(body) if body else {}
                method_name = data.get("method")
                params = data.get("params", {})
                request_id = data.get("id")
                
                # Handle MCP methods
                if method_name == "initialize":
                    response = {
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
                                "name": "ouicomply-mcp",
                                "version": "1.0.0"
                            }
                        }
                    }
                elif method_name == "tools/list":
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
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {"tools": tools}
                    }
                elif method_name == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    # Call the appropriate tool
                    if tool_name == "analyze_document":
                        result = asyncio.run(analyze_document(arguments))
                    elif tool_name == "update_memory":
                        result = asyncio.run(update_memory(arguments))
                    elif tool_name == "get_compliance_status":
                        result = asyncio.run(get_compliance_status(arguments))
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                        }
                        return {
                            "statusCode": 200,
                            "headers": {
                                "Content-Type": "application/json",
                                "Access-Control-Allow-Origin": "*"
                            },
                            "body": json.dumps(response)
                        }
                    
                    response = {
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
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method_name}"}
                    }
                
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps(response)
                }
                
            except Exception as e:
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({
                        "jsonrpc": "2.0",
                        "id": data.get("id", "unknown"),
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                    })
                }
        else:
            return {
                "statusCode": 405,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "Method not allowed"})
            }
    
    else:
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Not found"})
        }


# Vercel entry point
def main(request):
    return handler(request)
