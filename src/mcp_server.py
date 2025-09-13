"""
OuiComply MCP Server - AI-Assisted Legal Compliance Checker.

This MCP server provides comprehensive document compliance analysis using
Mistral's DocumentAI service, with support for multiple compliance frameworks
including GDPR, SOX, CCPA, and HIPAA.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union
from pathlib import Path

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

from .config import get_config, validate_config, print_config_summary
from .tools.compliance_engine import ComplianceEngine, ComplianceReport
from .tools.memory_integration import LeChatMemoryService

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
    - LeChat memory integration for autonomous decision-making
    - Audit trail generation for GitHub
    - Structured compliance reporting
    """
    
    def __init__(self):
        self.config = get_config()
        self.server = Server("ouicomply-mcp")
        self.compliance_engine = ComplianceEngine()
        self.memory_service = LeChatMemoryService()
        self._reports_cache = {}  # Cache for storing reports
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
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
                    uri="resource://risk-assessment-criteria",
                    name="Risk Assessment Criteria",
                    description="Risk assessment criteria and scoring methodology",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://compliance-templates",
                    name="Compliance Templates",
                    description="Templates for compliance reports and audit trails",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """
            Read a specific resource.
            """
            logger.info(f"Reading resource: {uri}")
            
            if uri == "resource://compliance-frameworks":
                return json.dumps({
                    "frameworks": {
                        "gdpr": {
                            "name": "General Data Protection Regulation",
                            "description": "EU data protection and privacy regulation",
                            "required_clauses": [
                                "data processing purpose",
                                "legal basis for processing",
                                "data retention period",
                                "data subject rights",
                                "data protection officer contact"
                            ]
                        },
                        "sox": {
                            "name": "Sarbanes-Oxley Act",
                            "description": "US financial reporting and corporate governance regulation",
                            "required_clauses": [
                                "financial reporting controls",
                                "internal control framework",
                                "management responsibility",
                                "auditor independence"
                            ]
                        },
                        "ccpa": {
                            "name": "California Consumer Privacy Act",
                            "description": "California consumer privacy and data protection law",
                            "required_clauses": [
                                "personal information collection notice",
                                "consumer rights disclosure",
                                "opt-out mechanisms",
                                "data sale restrictions"
                            ]
                        },
                        "hipaa": {
                            "name": "Health Insurance Portability and Accountability Act",
                            "description": "US healthcare data protection regulation",
                            "required_clauses": [
                                "privacy notice",
                                "minimum necessary standard",
                                "patient consent procedures",
                                "breach notification"
                            ]
                        }
                    }
                }, indent=2)
            
            elif uri == "resource://risk-assessment-criteria":
                return json.dumps({
                    "risk_levels": {
                        "low": {"threshold": 0.0, "description": "Minimal compliance risk"},
                        "medium": {"threshold": 0.3, "description": "Moderate compliance risk"},
                        "high": {"threshold": 0.6, "description": "Significant compliance risk"},
                        "critical": {"threshold": 0.8, "description": "Severe compliance risk"}
                    },
                    "scoring_factors": {
                        "missing_clauses": 0.3,
                        "critical_issues": 0.4,
                        "high_issues": 0.2,
                        "medium_issues": 0.1
                    }
                }, indent=2)
            
            elif uri == "resource://compliance-templates":
                return json.dumps({
                    "templates": {
                        "audit_trail": "GitHub audit trail markdown template",
                        "compliance_report": "Structured compliance report template",
                        "mitigation_plan": "Risk mitigation action plan template"
                    }
                }, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """
            List available tools.
            
            Tools are functions that can be called by the MCP client.
            """
            logger.info("Listing available tools")
            
            return [
                Tool(
                    name="analyze_document_compliance",
                    description="Perform comprehensive compliance analysis on a document using Mistral DocumentAI",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content as text, file path, or base64 encoded data"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "MIME type or file extension of the document (optional)"
                            },
                            "compliance_frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of compliance frameworks to check against",
                                "default": ["gdpr", "sox", "ccpa"]
                            },
                            "analysis_depth": {
                                "type": "string",
                                "description": "Level of analysis detail",
                                "enum": ["basic", "standard", "comprehensive"],
                                "default": "comprehensive"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="generate_compliance_report",
                    description="Generate a structured compliance report from analysis results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_id": {
                                "type": "string",
                                "description": "ID of the compliance report to generate"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format for the report",
                                "enum": ["json", "markdown", "html"],
                                "default": "markdown"
                            }
                        },
                        "required": ["report_id"]
                    }
                ),
                Tool(
                    name="store_assessment_in_memory",
                    description="Store compliance assessment in LeChat memory for autonomous decision-making",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_id": {
                                "type": "string",
                                "description": "ID of the compliance report to store"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "ID of the user (optional)"
                            },
                            "organization_id": {
                                "type": "string",
                                "description": "ID of the organization (optional)"
                            }
                        },
                        "required": ["report_id"]
                    }
                ),
                Tool(
                    name="search_compliance_memories",
                    description="Search stored compliance assessments in LeChat memory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for compliance memories"
                            },
                            "category": {
                                "type": "string",
                                "description": "Filter by memory category (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="generate_audit_trail",
                    description="Generate audit trail entry for GitHub",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "report_id": {
                                "type": "string",
                                "description": "ID of the compliance report"
                            },
                            "repository": {
                                "type": "string",
                                "description": "GitHub repository for audit trail (optional)"
                            },
                            "branch": {
                                "type": "string",
                                "description": "GitHub branch for audit trail (optional)",
                                "default": "main"
                            }
                        },
                        "required": ["report_id"]
                    }
                ),
                Tool(
                    name="get_compliance_history",
                    description="Get compliance assessment history for a user or organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "Filter by user ID (optional)"
                            },
                            "organization_id": {
                                "type": "string",
                                "description": "Filter by organization ID (optional)"
                            },
                            "document_id": {
                                "type": "string",
                                "description": "Filter by document ID (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 20
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_risk_trends",
                    description="Analyze compliance risk trends over time",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "Filter by user ID (optional)"
                            },
                            "organization_id": {
                                "type": "string",
                                "description": "Filter by organization ID (optional)"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to analyze",
                                "default": 30
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            Handle tool calls.
            
            This implements the actual legal compliance analysis logic using
            Mistral DocumentAI and the compliance engine.
            """
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                if name == "analyze_document_compliance":
                    return await self._handle_analyze_document_compliance(arguments)
                elif name == "generate_compliance_report":
                    return await self._handle_generate_compliance_report(arguments)
                elif name == "store_assessment_in_memory":
                    return await self._handle_store_assessment_in_memory(arguments)
                elif name == "search_compliance_memories":  
                    return await self._handle_search_compliance_memories(arguments)
                elif name == "generate_audit_trail":
                    return await self._handle_generate_audit_trail(arguments)
                elif name == "get_compliance_history":
                    return await self._handle_get_compliance_history(arguments)
                elif name == "analyze_risk_trends":
                    return await self._handle_analyze_risk_trends(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Tool execution failed - tool: {name}, error: {str(e)}")
                return [TextContent(
                    type="text", 
                    text=f"Error executing tool '{name}': {str(e)}"
                )]
    
    async def _handle_analyze_document_compliance(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle document compliance analysis."""
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type")
        frameworks = arguments.get("compliance_frameworks", ["gdpr", "sox", "ccpa"])
        analysis_depth = arguments.get("analysis_depth", "comprehensive")
        
        # Perform compliance analysis
        report = await self.compliance_engine.analyze_document_compliance(
            document_content=document_content,
            document_type=document_type,
            frameworks=frameworks,
            analysis_depth=analysis_depth
        )
        
        # Store report in memory for future reference
        self._reports_cache[report.report_id] = report
        
        # Generate summary
        summary = f"""
        COMPLIANCE ANALYSIS COMPLETED
        
        Report ID: {report.report_id}
        Document ID: {report.document_id}
        Status: {report.overall_status.value.upper()}
        Risk Level: {report.risk_level.value.upper()}
        Risk Score: {report.risk_score:.2f}/1.0
        
        Frameworks Analyzed: {', '.join(report.frameworks_analyzed)}
        Total Issues: {len(report.issues)}
        Critical Issues: {len([i for i in report.issues if i.severity == 'critical'])}
        Missing Clauses: {len(report.missing_clauses)}
        
        Executive Summary:
        {report.summary}
        
        Use 'generate_compliance_report' with report_id '{report.report_id}' to get detailed results.
        """
        
        return [TextContent(type="text", text=summary.strip())]
    
    async def _handle_generate_compliance_report(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compliance report generation."""
        report_id = arguments.get("report_id", "")
        format_type = arguments.get("format", "markdown")
        
        if report_id not in self._reports_cache:
            return [TextContent(
                type="text", 
                text=f"Report not found: {report_id}. Please run analysis first."
            )]
        
        report = self._reports_cache[report_id]
        
        if format_type == "json":
            content = self.compliance_engine.export_report_json(report)
        elif format_type == "markdown":
            content = self.compliance_engine.export_report_markdown(report)
        else:
            content = f"Unsupported format: {format_type}"
        
        return [TextContent(type="text", text=content)]
    
    async def _handle_store_assessment_in_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle storing assessment in LeChat memory."""
        report_id = arguments.get("report_id", "")
        user_id = arguments.get("user_id")
        organization_id = arguments.get("organization_id")
        
        if report_id not in self._reports_cache:
            return [TextContent(
                type="text", 
                text=f"Report not found: {report_id}. Please run analysis first."
            )]
        
        report = self._reports_cache[report_id]
        
        try:
            memory_id = await self.memory_service.store_compliance_assessment(
                report=report,
                user_id=user_id,
                organization_id=organization_id
            )
            
            return [TextContent(
                type="text", 
                text=f"Assessment stored in LeChat memory with ID: {memory_id}"
            )]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to store assessment in memory: {str(e)}"
            )]
    
    async def _handle_search_compliance_memories(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle searching compliance memories."""
        query = arguments.get("query", "")
        category = arguments.get("category")
        tags = arguments.get("tags")
        limit = arguments.get("limit", 10)
        
        try:
            results = await self.memory_service.search_memories(
                query=query,
                category=category,
                tags=tags,
                limit=limit
            )
            
            if not results:
                return [TextContent(type="text", text="No matching memories found.")]
            
            content = f"Found {len(results)} matching memories:\n\n"
            for i, result in enumerate(results, 1):
                content += f"{i}. **{result.title}**\n"
                content += f"   Category: {result.category}\n"
                content += f"   Relevance: {result.relevance_score:.2f}\n"
                content += f"   Created: {result.created_at}\n"
                content += f"   Content: {result.content[:200]}...\n\n"
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to search memories: {str(e)}"
            )]
    
    async def _handle_generate_audit_trail(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle audit trail generation."""
        report_id = arguments.get("report_id", "")
        repository = arguments.get("repository")
        branch = arguments.get("branch", "main")
        
        if report_id not in self._reports_cache:
            return [TextContent(
                type="text", 
                text=f"Report not found: {report_id}. Please run analysis first."
            )]
        
        report = self._reports_cache[report_id]
        
        try:
            audit_trail = await self.compliance_engine.generate_audit_trail_entry(report)
            
            content = f"""# Audit Trail Entry Generated

**Repository:** {repository or 'Not specified'}
**Branch:** {branch}
**Report ID:** {report_id}

## Audit Trail Content

{audit_trail}

---
*This audit trail entry can be committed to your GitHub repository.*
"""
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to generate audit trail: {str(e)}"
            )]
    
    async def _handle_get_compliance_history(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle getting compliance history."""
        user_id = arguments.get("user_id")
        organization_id = arguments.get("organization_id")
        document_id = arguments.get("document_id")
        limit = arguments.get("limit", 20)
        
        try:
            history = await self.memory_service.get_compliance_history(
                user_id=user_id,
                organization_id=organization_id,
                document_id=document_id,
                limit=limit
            )
            
            if not history:
                return [TextContent(type="text", text="No compliance history found.")]
            
            content = f"Compliance History ({len(history)} entries):\n\n"
            for i, entry in enumerate(history, 1):
                content += f"{i}. **{entry.title}**\n"
                content += f"   Category: {entry.category}\n"
                content += f"   Relevance: {entry.relevance_score:.2f}\n"
                content += f"   Created: {entry.created_at}\n"
                content += f"   Tags: {', '.join(entry.tags)}\n\n"
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to get compliance history: {str(e)}"
            )]
    
    async def _handle_analyze_risk_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle risk trend analysis."""
        user_id = arguments.get("user_id")
        organization_id = arguments.get("organization_id")
        days = arguments.get("days", 30)
        
        try:
            trends = await self.memory_service.get_risk_trends(
                user_id=user_id,
                organization_id=organization_id,
                days=days
            )
            
            content = f"""# Risk Trend Analysis

**Analysis Period:** {days} days
**Total Assessments:** {trends['total_assessments']}
**Average Risk Score:** {trends['average_risk_score']:.2f}/1.0
**Total Issues:** {trends['total_issues']}
**Critical Issues:** {trends['total_critical_issues']}
**Trend Direction:** {trends['trend_direction'].title()}
**Overall Risk Level:** {trends['risk_level'].title()}

## Analysis Summary

Based on the compliance assessments over the past {days} days, the overall risk level is **{trends['risk_level'].title()}** with an average risk score of {trends['average_risk_score']:.2f}.

**Key Insights:**
- {trends['total_assessments']} assessments were analyzed
- {trends['total_issues']} total compliance issues identified
- {trends['total_critical_issues']} critical issues requiring immediate attention

**Recommendations:**
- Monitor compliance trends regularly
- Address critical issues promptly
- Implement preventive measures for common issues
"""
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to analyze risk trends: {str(e)}"
            )]

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting OuiComply MCP Server")
        
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return
        
        # Print configuration summary
        print_config_summary()
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.config.server_name,
                    server_version=self.config.server_version,
                    capabilities={}
                )
            )


async def main():
    """Main entry point for the MCP server."""
    server = OuiComplyMCPServer()
    await server.run()


# ALPIC-compatible MCP transport pattern
def run_mcp_server():
    """ALPIC-compatible MCP server runner."""
    asyncio.run(main())


if __name__ == "__main__":
    # Use mcp.run() pattern for ALPIC compatibility
    asyncio.run(main())
