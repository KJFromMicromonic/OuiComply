#!/usr/bin/env python3
"""
Fixed MCP Server implementation using the official Python SDK.
Based on the official MCP specification and best practices.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

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


class OuiComplyMCPServer:
    """
    Official MCP Server for OuiComply using the official Python SDK.
    
    This server provides compliance analysis tools, resources, and prompts
    following the official MCP specification.
    """
    
    def __init__(self):
        """Initialize the MCP server with all required services."""
        self.server = Server("ouicomply-mcp")
        
        # Initialize our services
        self.document_ai_service = DocumentAIService()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.compliance_engine = ComplianceEngine()
        
        # Setup MCP handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all MCP handlers for tools, resources, and prompts."""
        
        # Tool handlers
        @self.server.list_tools()
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
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "analyze_document":
                    result = await self._analyze_document(arguments)
                elif name == "update_memory":
                    result = await self._update_memory(arguments)
                elif name == "get_compliance_status":
                    result = await self._get_compliance_status(arguments)
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
        
        # Resource handlers
        @self.server.list_resources()
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
        
        @self.server.read_resource()
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
                memory_data = await self.memory_integration.get_team_memory(team_id)
                return json.dumps(memory_data, indent=2)
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        # Prompt handlers
        @self.server.list_prompts()
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
        
        @self.server.get_prompt()
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
    
    async def _analyze_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document for compliance."""
        try:
            document_content = arguments.get("document_content", "")
            document_type = arguments.get("document_type", "contract")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            # Use the compliance engine for analysis
            report = await self.compliance_engine.analyze_document_compliance(
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
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update team memory."""
        try:
            team_id = arguments.get("team_id", "default")
            insight = arguments.get("insight", "")
            category = arguments.get("category", "general")
            
            # Store the insight in memory
            result = await self.memory_integration.store_insight(
                team_id=team_id,
                insight=insight,
                category=category
            )
            
            return {
                "team_id": team_id,
                "insight_stored": True,
                "memory_id": result.get("memory_id", str(uuid.uuid4())),
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
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance status."""
        try:
            team_id = arguments.get("team_id", "default")
            framework = arguments.get("framework", "all")
            
            # Get team status from memory
            status = await self.memory_integration.get_team_status(team_id)
            
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
    
    async def run(self):
        """Run the MCP server."""
        print(f"🚀 Starting OuiComply MCP Server (Official SDK)...")
        print(f"📚 Available Tools: analyze_document, update_memory, get_compliance_status")
        print(f"📄 Available Resources: compliance://frameworks, memory://team/{{team_id}}")
        print(f"💬 Available Prompts: compliance_analysis")
        print(f"✅ Server ready for Le Chat integration!")
        
        # Run the MCP server
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ouicomply-mcp",
                    server_version="1.0.0",
                    capabilities={
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": True, "listChanged": True},
                        "prompts": {"listChanged": True}
                    }
                )
            )


async def main():
    """Main entry point for the MCP server."""
    server = OuiComplyMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
