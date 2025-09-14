#!/usr/bin/env python3
"""
OuiComply MCP Server - AI-Assisted Legal Compliance Checker

A Model Context Protocol (MCP) server that provides comprehensive document compliance
analysis using Mistral's DocumentAI service, with support for multiple compliance
frameworks including GDPR, SOX, CCPA, and HIPAA.

This server implements the MCP protocol specification and provides:
- Document analysis and compliance checking tools
- Legal framework resources
- Memory integration for team insights
- Automation capabilities for compliance workflows

Author: OuiComply Team
Version: 2.0.0
License: Apache 2.0
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import structlog

# Import our tools and services
try:
    from src.tools.compliance_engine import ComplianceEngine, ComplianceReport
    from src.tools.memory_integration import MemoryIntegration
    from src.tools.automation_agent import AutomationAgent, AutomationResult
except ImportError:
    # Fallback for when running as standalone module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from src.tools.compliance_engine import ComplianceEngine, ComplianceReport
    from src.tools.memory_integration import MemoryIntegration
    from src.tools.automation_agent import AutomationAgent, AutomationResult

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class OuiComplyMCPServer:
    """
    OuiComply MCP Server for AI-assisted legal compliance checking.
    
    This server provides comprehensive document compliance analysis including:
    - Multi-framework compliance checking (GDPR, SOX, CCPA, HIPAA)
    - DocumentAI-powered document parsing and analysis
    - Risk assessment and scoring
    - Memory integration for autonomous decision-making
    - Audit trail generation
    - Structured compliance reporting
    
    The server follows the MCP protocol specification and provides tools,
    resources, and prompts for legal compliance workflows.
    """
    
    def __init__(self):
        """Initialize the OuiComply MCP Server."""
        self.server = Server("ouicomply-mcp")
        self.compliance_engine = ComplianceEngine()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.automation_agent = AutomationAgent()
        self._reports_cache = {}  # Cache for storing reports
        self._setup_handlers()
        
        logger.info("OuiComply MCP Server initialized", 
                   server_name="ouicomply-mcp",
                   version="2.0.0")
    
    def _setup_handlers(self):
        """Set up MCP server handlers for tools, resources, and prompts."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """
            List available resources.
            
            Resources are static data that can be read by tools.
            """
            logger.info("Listing available resources")
            
            return [
                Resource(
                    uri="resource://compliance-frameworks",
                    name="Compliance Frameworks",
                    description="Supported compliance frameworks (GDPR, SOX, CCPA, HIPAA)",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://legal-templates",
                    name="Legal Document Templates",
                    description="Collection of legal document templates and required sections",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://team-memory",
                    name="Team Memory",
                    description="Team-specific compliance insights and historical data",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """
            Read a specific resource.
            
            Args:
                uri: The URI of the resource to read
                
            Returns:
                The content of the resource as a string
            """
            logger.info("Reading resource", uri=uri)
            
            try:
                if uri == "resource://compliance-frameworks":
                    return self._get_compliance_frameworks()
                elif uri == "resource://legal-templates":
                    return self._get_legal_templates()
                elif uri == "resource://team-memory":
                    return await self._get_team_memory()
                else:
                    raise ValueError(f"Unknown resource: {uri}")
            except Exception as e:
                logger.error("Error reading resource", uri=uri, error=str(e))
                raise
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """
            List available tools.
            
            Tools are functions that can be called by the client.
            """
            logger.info("Listing available tools")
            
            return [
                Tool(
                    name="analyze_document",
                    description="Analyze a document for compliance issues using AI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The text content of the document to analyze"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of document (contract, policy, agreement, etc.)",
                                "default": "contract"
                            },
                            "frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Compliance frameworks to check against",
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
                ),
                Tool(
                    name="automate_compliance_workflow",
                    description="Automate compliance workflow based on document analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content to analyze"
                            },
                            "workflow_type": {
                                "type": "string",
                                "description": "Type of workflow to automate",
                                "enum": ["review", "approval", "revision", "audit"]
                            },
                            "team_id": {
                                "type": "string",
                                "description": "Team identifier for workflow context"
                            }
                        },
                        "required": ["document_content", "workflow_type", "team_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            """
            Call a specific tool.
            
            Args:
                name: The name of the tool to call
                arguments: The arguments to pass to the tool
                
            Returns:
                List of content items returned by the tool
            """
            logger.info("Calling tool", tool_name=name, arguments=arguments)
            
            try:
                if name == "analyze_document":
                    result = await self._analyze_document(arguments)
                elif name == "update_memory":
                    result = await self._update_memory(arguments)
                elif name == "get_compliance_status":
                    result = await self._get_compliance_status(arguments)
                elif name == "automate_compliance_workflow":
                    result = await self._automate_compliance_workflow(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error("Error calling tool", tool_name=name, error=str(e))
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _analyze_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a document for compliance issues.
        
        Args:
            arguments: Tool arguments containing document content and analysis parameters
            
        Returns:
            Analysis results including compliance status, issues, and recommendations
        """
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type", "contract")
        frameworks = arguments.get("frameworks", ["gdpr", "sox"])
        
        if not document_content:
            raise ValueError("document_content is required")
        
        logger.info("Analyzing document", 
                   document_type=document_type, 
                   frameworks=frameworks,
                   content_length=len(document_content))
        
        try:
            # Use the compliance engine to analyze the document
            report = await self.compliance_engine.analyze_document_compliance(
                document_content=document_content,
                document_type=document_type,
                frameworks=frameworks
            )
            
            # Cache the report for future reference
            report_id = report.report_id
            self._reports_cache[report_id] = report
            
            result = {
                "report_id": report_id,
                "status": report.overall_status.value if hasattr(report.overall_status, 'value') else str(report.overall_status),
                "risk_level": report.risk_level.value if hasattr(report.risk_level, 'value') else str(report.risk_level),
                "risk_score": report.risk_score,
                "issues_count": len(report.issues),
                "summary": report.summary,
                "frameworks_checked": frameworks,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "issues": [
                    {
                        "type": issue.type.value if hasattr(issue.type, 'value') else str(issue.type),
                        "severity": issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity),
                        "description": issue.description,
                        "recommendation": issue.recommendation,
                        "framework": issue.framework
                    }
                    for issue in report.issues
                ]
            }
            
            logger.info("Document analysis completed", 
                       report_id=report_id,
                       status=report.overall_status.value if hasattr(report.overall_status, 'value') else str(report.overall_status),
                       risk_score=report.risk_score)
            
            return result
            
        except Exception as e:
            logger.error("Error analyzing document", error=str(e))
            raise
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update team memory with new compliance insights.
        
        Args:
            arguments: Tool arguments containing team_id, insight, and category
            
        Returns:
            Memory update confirmation and details
        """
        team_id = arguments.get("team_id", "")
        insight = arguments.get("insight", "")
        category = arguments.get("category", "general")
        
        if not team_id or not insight:
            raise ValueError("team_id and insight are required")
        
        logger.info("Updating team memory", 
                   team_id=team_id, 
                   category=category,
                   insight_length=len(insight))
        
        try:
            result = await self.memory_integration.store_insight(
                team_id=team_id,
                insight=insight,
                category=category
            )
            
            logger.info("Memory updated successfully", 
                       team_id=team_id,
                       memory_id=result.get("memory_id"))
            
            return {
                "success": True,
                "team_id": team_id,
                "memory_id": result.get("memory_id"),
                "category": category,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error updating memory", team_id=team_id, error=str(e))
            raise
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current compliance status for a team.
        
        Args:
            arguments: Tool arguments containing team_id and optional framework
            
        Returns:
            Team compliance status and metrics
        """
        team_id = arguments.get("team_id", "")
        framework = arguments.get("framework", "all")
        
        if not team_id:
            raise ValueError("team_id is required")
        
        logger.info("Getting compliance status", 
                   team_id=team_id, 
                   framework=framework)
        
        try:
            status = await self.memory_integration.get_team_status(team_id)
            
            result = {
                "team_id": team_id,
                "framework": framework,
                "overall_status": status.get("overall_status", "unknown"),
                "compliance_score": status.get("compliance_score", 0),
                "last_updated": status.get("last_updated"),
                "total_insights": status.get("total_insights", 0),
                "recent_issues": status.get("recent_issues", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Compliance status retrieved", 
                       team_id=team_id,
                       status=result["overall_status"])
            
            return result
            
        except Exception as e:
            logger.error("Error getting compliance status", team_id=team_id, error=str(e))
            raise
    
    async def _automate_compliance_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automate compliance workflow based on document analysis.
        
        Args:
            arguments: Tool arguments containing document content, workflow type, and team_id
            
        Returns:
            Automation results and next steps
        """
        document_content = arguments.get("document_content", "")
        workflow_type = arguments.get("workflow_type", "")
        team_id = arguments.get("team_id", "")
        
        if not all([document_content, workflow_type, team_id]):
            raise ValueError("document_content, workflow_type, and team_id are required")
        
        logger.info("Automating compliance workflow", 
                   workflow_type=workflow_type,
                   team_id=team_id,
                   content_length=len(document_content))
        
        try:
            result = await self.automation_agent.execute_workflow(
                document_content=document_content,
                workflow_type=workflow_type,
                team_id=team_id
            )
            
            logger.info("Workflow automation completed", 
                       workflow_type=workflow_type,
                       team_id=team_id,
                       success=result.get("status") == "completed" if isinstance(result, dict) else getattr(result, "success", True))
            
            return {
                "success": result.get("status") == "completed" if isinstance(result, dict) else getattr(result, "success", True),
                "workflow_type": workflow_type,
                "team_id": team_id,
                "actions_taken": result.get("actions_taken", []) if isinstance(result, dict) else getattr(result, "actions_taken", []),
                "next_steps": result.get("next_steps", []) if isinstance(result, dict) else getattr(result, "next_steps", []),
                "automation_id": result.get("automation_id", f"automation_{team_id}_{int(datetime.utcnow().timestamp())}") if isinstance(result, dict) else getattr(result, "automation_id", f"automation_{team_id}_{int(datetime.utcnow().timestamp())}"),
                "timestamp": result.get("timestamp", datetime.utcnow().isoformat()) if isinstance(result, dict) else getattr(result, "timestamp", datetime.utcnow().isoformat())
            }
            
        except Exception as e:
            logger.error("Error automating workflow", 
                        workflow_type=workflow_type, 
                        team_id=team_id, 
                        error=str(e))
            raise
    
    def _get_compliance_frameworks(self) -> str:
        """Get compliance frameworks resource content."""
        frameworks = {
            "frameworks": {
                "gdpr": {
                    "name": "General Data Protection Regulation",
                    "description": "EU regulation for data protection and privacy",
                    "required_clauses": [
                        "data processing purpose",
                        "legal basis for processing",
                        "data retention period",
                        "data subject rights",
                        "data protection officer contact",
                        "cross-border data transfer safeguards",
                        "data breach notification",
                        "consent withdrawal mechanism"
                    ],
                    "risk_indicators": [
                        "unclear data processing purposes",
                        "missing legal basis",
                        "excessive data retention",
                        "insufficient data subject rights",
                        "unclear consent mechanisms"
                    ],
                    "key_requirements": [
                        "Data minimization",
                        "Purpose limitation",
                        "Storage limitation",
                        "Consent management",
                        "Data subject rights",
                        "Privacy by design"
                    ]
                },
                "sox": {
                    "name": "Sarbanes-Oxley Act",
                    "description": "US law for financial reporting and corporate governance",
                    "required_clauses": [
                        "financial reporting controls",
                        "internal control framework",
                        "management responsibility",
                        "auditor independence",
                        "whistleblower protection",
                        "document retention policy",
                        "conflict of interest disclosure"
                    ],
                    "risk_indicators": [
                        "weak internal controls",
                        "insufficient documentation",
                        "conflict of interest issues",
                        "inadequate audit trails"
                    ],
                    "key_requirements": [
                        "Internal controls",
                        "Financial reporting accuracy",
                        "Audit trails",
                        "Management certification",
                        "Whistleblower protection"
                    ]
                },
                "ccpa": {
                    "name": "California Consumer Privacy Act",
                    "description": "California state law for consumer privacy rights",
                    "required_clauses": [
                        "personal information collection notice",
                        "consumer rights disclosure",
                        "opt-out mechanisms",
                        "data sale restrictions",
                        "non-discrimination policy",
                        "authorized agent procedures"
                    ],
                    "risk_indicators": [
                        "unclear data collection practices",
                        "missing opt-out mechanisms",
                        "insufficient consumer rights information"
                    ],
                    "key_requirements": [
                        "Consumer rights disclosure",
                        "Opt-out mechanisms",
                        "Data collection transparency",
                        "Non-discrimination",
                        "Data deletion rights"
                    ]
                },
                "hipaa": {
                    "name": "Health Insurance Portability and Accountability Act",
                    "description": "US law for healthcare data protection",
                    "required_clauses": [
                        "privacy notice",
                        "minimum necessary standard",
                        "patient consent procedures",
                        "breach notification",
                        "business associate agreements",
                        "administrative safeguards"
                    ],
                    "risk_indicators": [
                        "insufficient privacy protections",
                        "unclear consent procedures",
                        "inadequate breach response"
                    ],
                    "key_requirements": [
                        "Administrative safeguards",
                        "Physical safeguards",
                        "Technical safeguards",
                        "Breach notification",
                        "Business associate agreements"
                    ]
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return json.dumps(frameworks, indent=2)
    
    def _get_legal_templates(self) -> str:
        """Get legal document templates resource content."""
        templates = {
            "templates": {
                "privacy_policy": {
                    "name": "Privacy Policy Template",
                    "description": "Template for website privacy policies",
                    "required_sections": [
                        "Information collection",
                        "Information use",
                        "Information sharing",
                        "Data security",
                        "User rights",
                        "Contact information"
                    ]
                },
                "terms_of_service": {
                    "name": "Terms of Service Template",
                    "description": "Template for website terms of service",
                    "required_sections": [
                        "Acceptance of terms",
                        "Use restrictions",
                        "Intellectual property",
                        "Limitation of liability",
                        "Termination",
                        "Governing law"
                    ]
                },
                "data_processing_agreement": {
                    "name": "Data Processing Agreement Template",
                    "description": "Template for GDPR-compliant data processing agreements",
                    "required_sections": [
                        "Data processing details",
                        "Data controller obligations",
                        "Data processor obligations",
                        "Data subject rights",
                        "Security measures",
                        "Breach notification"
                    ]
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return json.dumps(templates, indent=2)
    
    async def _get_team_memory(self) -> str:
        """Get team memory resource content."""
        try:
            # Get memory for all teams (this would need to be implemented in MemoryIntegration)
            memory_data = {
                "teams": {},
                "global_insights": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return json.dumps(memory_data, indent=2)
        except Exception as e:
            logger.error("Error getting team memory", error=str(e))
            return json.dumps({"error": str(e)}, indent=2)
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting OuiComply MCP Server")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ouicomply-mcp",
                    server_version="2.0.0",
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
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the server
    asyncio.run(main())
