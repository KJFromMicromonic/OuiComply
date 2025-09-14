#!/usr/bin/env python3
"""
Official MCP Server implementation using the official Python SDK and FastMCP.
Based on the official MCP specification and best practices.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    Resource,
    ResourceTemplate,
    TextContent,
    Tool,
)
from pydantic import BaseModel, Field

# Import our existing tools
from src.tools.document_ai import DocumentAIService
from src.tools.memory_integration import MemoryIntegration
from src.tools.compliance_engine import ComplianceEngine


class AnalyzeDocumentRequest(BaseModel):
    """Request model for document analysis."""
    document_content: str = Field(..., description="Document content to analyze")
    document_type: str = Field(default="contract", description="Type of document")
    frameworks: List[str] = Field(default=["gdpr", "sox"], description="Compliance frameworks to check")


class UpdateMemoryRequest(BaseModel):
    """Request model for memory updates."""
    team_id: str = Field(..., description="Team identifier")
    insight: str = Field(..., description="Compliance insight to store")
    category: str = Field(default="general", description="Category of insight")


class ComplianceStatusRequest(BaseModel):
    """Request model for compliance status."""
    team_id: str = Field(..., description="Team identifier")
    framework: str = Field(default="all", description="Specific framework to check")


class OuiComplyMCPServer:
    """
    Official MCP Server for OuiComply using the official Python SDK.
    
    This server provides compliance analysis tools, resources, and prompts
    following the official MCP specification.
    """
    
    def __init__(self):
        """Initialize the MCP server with all required services."""
        self.mcp = FastMCP("OuiComply MCP Server")
        
        # Initialize our services
        self.document_ai_service = DocumentAIService()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.compliance_engine = ComplianceEngine()
        
        # Setup MCP handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all MCP handlers for tools, resources, and prompts."""
        
        # Tool handlers
        @self.mcp.tool()
        async def analyze_document(
            document_content: str,
            document_type: str = "contract",
            frameworks: List[str] = ["gdpr", "sox"]
        ) -> str:
            """
            Analyze a document for compliance issues using AI.
            
            This tool performs comprehensive compliance analysis on documents
            using multiple AI models and compliance frameworks.
            
            Args:
                document_content: The content of the document to analyze
                document_type: Type of document (contract, policy, etc.)
                frameworks: List of compliance frameworks to check
                
            Returns:
                JSON string containing the analysis results
            """
            try:
                # Use the compliance engine for analysis
                report = await self.compliance_engine.analyze_document_compliance(
                    document_content=document_content,
                    document_type=document_type,
                    frameworks=frameworks
                )
                
                result = {
                    "report_id": report.report_id,
                    "status": report.overall_status.value,
                    "risk_level": report.risk_level.value,
                    "risk_score": report.risk_score,
                    "issues_count": len(report.issues),
                    "summary": report.summary,
                    "frameworks_analyzed": frameworks,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "status": "failed",
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
                return json.dumps(error_result, indent=2)
        
        @self.mcp.tool()
        async def update_memory(
            team_id: str,
            insight: str,
            category: str = "general"
        ) -> str:
            """
            Update team memory with new compliance insights.
            
            This tool stores compliance insights and assessments in the team's
            memory for future reference and analysis.
            
            Args:
                team_id: Unique identifier for the team
                insight: The compliance insight to store
                category: Category of the insight (privacy, security, etc.)
                
            Returns:
                JSON string containing the storage result
            """
            try:
                # Store the insight in memory
                result = await self.memory_integration.store_insight(
                    team_id=team_id,
                    insight=insight,
                    category=category
                )
                
                response = {
                    "team_id": team_id,
                    "insight_stored": True,
                    "memory_id": result.get("memory_id", str(uuid.uuid4())),
                    "category": category,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                return json.dumps(response, indent=2)
                
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "team_id": team_id,
                    "insight_stored": False,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return json.dumps(error_result, indent=2)
        
        @self.mcp.tool()
        async def get_compliance_status(
            team_id: str,
            framework: str = "all"
        ) -> str:
            """
            Get current compliance status for a team.
            
            This tool retrieves the current compliance status and history
            for a specific team across different frameworks.
            
            Args:
                team_id: Unique identifier for the team
                framework: Specific framework to check (or 'all' for all frameworks)
                
            Returns:
                JSON string containing the compliance status
            """
            try:
                # Get team status from memory
                status = await self.memory_integration.get_team_status(team_id)
                
                response = {
                    "team_id": team_id,
                    "framework": framework,
                    "overall_status": status.get("overall_status", "unknown"),
                    "last_updated": status.get("last_updated", datetime.utcnow().isoformat()),
                    "compliance_score": status.get("compliance_score", 0.0),
                    "active_frameworks": status.get("active_frameworks", []),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                return json.dumps(response, indent=2)
                
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "team_id": team_id,
                    "framework": framework,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return json.dumps(error_result, indent=2)
        
        # Resource handlers
        @self.mcp.resource("compliance://frameworks")
        async def get_compliance_frameworks() -> str:
            """
            Get available compliance frameworks and their requirements.
            
            Returns:
                JSON string containing framework information
            """
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
        
        @self.mcp.resource("memory://team/{team_id}")
        async def get_team_memory(team_id: str) -> str:
            """
            Get team-specific compliance memory and insights.
            
            Args:
                team_id: Unique identifier for the team
                
            Returns:
                JSON string containing team memory data
            """
            try:
                # Get team memory from the integration service
                memory_data = await self.memory_integration.get_team_memory(team_id)
                
                response = {
                    "team_id": team_id,
                    "insights": memory_data.get("insights", []),
                    "compliance_history": memory_data.get("compliance_history", []),
                    "last_updated": memory_data.get("last_updated", datetime.utcnow().isoformat()),
                    "total_insights": len(memory_data.get("insights", [])),
                    "compliance_score": memory_data.get("compliance_score", 0.0)
                }
                
                return json.dumps(response, indent=2)
                
            except Exception as e:
                error_result = {
                    "error": str(e),
                    "team_id": team_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return json.dumps(error_result, indent=2)
        
        # Prompt handlers
        @self.mcp.prompt("compliance_analysis")
        async def compliance_analysis_prompt(
            document_type: str = "contract",
            frameworks: str = "gdpr,sox"
        ) -> List[Dict[str, Any]]:
            """
            Generate a compliance analysis prompt template.
            
            Args:
                document_type: Type of document to analyze
                frameworks: Comma-separated list of frameworks to check
                
            Returns:
                List of prompt messages
            """
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
    
    def run(self, transport: str = "streamable-http", host: str = "0.0.0.0", port: int = 8000):
        """
        Run the MCP server.
        
        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
            host: Host to bind the server to (for streamable-http)
            port: Port to bind the server to (for streamable-http)
        """
        print(f"🚀 Starting OuiComply MCP Server (Official SDK)...")
        print(f"📡 Transport: {transport}")
        if transport == "streamable-http":
            print(f"📡 Server: http://{host}:{port}")
            print(f"🔧 MCP Protocol: http://{host}:{port}/mcp")
        print(f"📚 Available Tools: analyze_document, update_memory, get_compliance_status")
        print(f"📄 Available Resources: compliance://frameworks, memory://team/{{team_id}}")
        print(f"💬 Available Prompts: compliance_analysis")
        print(f"✅ Server ready for Le Chat integration!")
        
        # Run the FastMCP server
        self.mcp.run(transport=transport)


def main():
    """Main entry point for the MCP server."""
    server = OuiComplyMCPServer()
    server.run()


if __name__ == "__main__":
    main()
