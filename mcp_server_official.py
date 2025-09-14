#!/usr/bin/env python3
"""
Official MCP Server for OuiComply using the mcp library
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ListResourcesRequest,
    ListResourcesResult,
    Resource,
    ReadResourceRequest,
    ReadResourceResult,
    ListPromptsRequest,
    ListPromptsResult,
    Prompt,
    GetPromptRequest,
    GetPromptResult,
    PromptMessage,
)

# Import our existing tools
from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine

class OuiComplyMCPServer:
    def __init__(self):
        self.server = Server("ouicomply-mcp")
        
        # Initialize our services
        self.document_ai_service = DocumentAIService()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.compliance_engine = ComplianceEngine()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="analyze_document",
                    description="Analyze a document for compliance issues using AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Content of the document to analyze"
                            },
                            "document_name": {
                                "type": "string", 
                                "description": "Name of the document"
                            }
                        },
                        "required": ["document_content", "document_name"]
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
                            }
                        },
                        "required": ["team_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_document":
                    document_content = arguments.get("document_content", "")
                    document_name = arguments.get("document_name", "Unknown")
                    
                    # Use our compliance engine
                    result = await self.compliance_engine.analyze_document(
                        document_content=document_content,
                        document_name=document_name
                    )
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "update_memory":
                    team_id = arguments.get("team_id", "")
                    memory_type = arguments.get("memory_type", "compliance")
                    updates = arguments.get("updates", {})
                    
                    # Update memory through our integration
                    result = await self.memory_integration.update_team_memory(
                        team_id=team_id,
                        memory_type=memory_type,
                        updates=updates
                    )
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                elif name == "get_compliance_status":
                    team_id = arguments.get("team_id", "")
                    
                    # Get compliance status
                    result = await self.compliance_engine.get_compliance_status(team_id)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                    
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )]
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="ouicomply://compliance-frameworks",
                    name="Compliance Frameworks",
                    description="Available compliance frameworks",
                    mimeType="application/json"
                ),
                Resource(
                    uri="ouicomply://team-memory",
                    name="Team Memory", 
                    description="Team-specific compliance memory",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource."""
            if uri == "ouicomply://compliance-frameworks":
                return json.dumps({
                    "frameworks": [
                        "GDPR", "CCPA", "HIPAA", "SOX", "PCI-DSS"
                    ],
                    "last_updated": datetime.utcnow().isoformat()
                })
            elif uri == "ouicomply://team-memory":
                return json.dumps({
                    "teams": {},
                    "last_updated": datetime.utcnow().isoformat()
                })
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Prompt]:
            """List available prompts."""
            return [
                Prompt(
                    name="compliance_analysis",
                    description="Analyze document for compliance issues",
                    arguments=[
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
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: Dict[str, Any]) -> GetPromptResult:
            """Get a prompt."""
            if name == "compliance_analysis":
                document_content = arguments.get("document_content", "")
                frameworks = arguments.get("frameworks", ["GDPR", "CCPA"])
                
                prompt_text = f"""
Analyze the following document for compliance issues with {', '.join(frameworks)}:

Document: {document_content}

Please provide:
1. Compliance score (0-100)
2. Risk level (low/medium/high)
3. Specific issues found
4. Recommendations for improvement
5. Priority actions needed
"""
                
                return GetPromptResult(
                    description="Compliance analysis prompt",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=prompt_text
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown prompt: {name}")
    
    async def run(self):
        """Run the MCP server."""
        print("🚀 Starting OuiComply MCP Server (Official)...")
        print("📡 Using official MCP library")
        print("🔧 Tools: analyze_document, update_memory, get_compliance_status")
        print("📚 Resources: compliance-frameworks, team-memory")
        print("💬 Prompts: compliance_analysis")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ouicomply-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """Main entry point."""
    server = OuiComplyMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
