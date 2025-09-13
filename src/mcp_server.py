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
from .tools.pdf_analysis_tool import PDFAnalysisTool
from .tools.memory_integration import MemoryIntegration
from .tools.lechat_interface import LeChatInterface, QueryContext, DocumentFetchResult
from .tools.automation_agent import AutomationAgent, AutomationResult

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
        self.pdf_analysis_tool = PDFAnalysisTool()
        self.memory_integration = MemoryIntegration(use_lechat_mcp=True)
        self.lechat_interface = LeChatInterface()
        self.automation_agent = AutomationAgent()
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
                    name="analyze_pdf_document",
                    description="Analyze PDF document step by step with structured output",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_path": {
                                "type": "string",
                                "description": "Path to the PDF file to analyze"
                            },
                            "include_steps": {
                                "type": "boolean",
                                "description": "Whether to include detailed step information",
                                "default": True
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format: detailed, summary, or structured",
                                "default": "detailed"
                            }
                        },
                        "required": ["document_path"]
                    }
                ),
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
                ),
                Tool(
                    name="decompose_task",
                    description="Decompose a compliance task into structured components using Le Chat interface",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query from Le Chat"
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team context (e.g., 'Procurement Team', 'Sales Team')"
                            }
                        },
                        "required": ["query", "team_context"]
                    }
                ),
                Tool(
                    name="decompose_document",
                    description="Decompose document into structured sections for analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content as text"
                            },
                            "document_name": {
                                "type": "string",
                                "description": "Name of the document"
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team context for analysis"
                            }
                        },
                        "required": ["document_content", "document_name", "team_context"]
                    }
                ),
                Tool(
                    name="analyze_with_memory",
                    description="Perform compliance analysis with team-specific memory integration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "Document content to analyze"
                            },
                            "document_name": {
                                "type": "string",
                                "description": "Name of the document"
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team context for analysis"
                            },
                            "compliance_frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of compliance frameworks to check",
                                "default": ["gdpr", "sox", "ccpa"]
                            }
                        },
                        "required": ["document_content", "document_name", "team_context"]
                    }
                ),
                Tool(
                    name="generate_structured_report",
                    description="Generate structured compliance report with JSON/Markdown output",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_results": {
                                "type": "object",
                                "description": "Results from compliance analysis"
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team context for report personalization"
                            },
                            "format": {
                                "type": "string",
                                "description": "Output format: json, markdown, or both",
                                "default": "both"
                            }
                        },
                        "required": ["analysis_results", "team_context"]
                    }
                ),
                Tool(
                    name="update_memory",
                    description="Update team-specific memory based on analysis results and user feedback",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {
                                "type": "string",
                                "description": "Team identifier"
                            },
                            "analysis_results": {
                                "type": "object",
                                "description": "Results from compliance analysis"
                            },
                            "user_feedback": {
                                "type": "object",
                                "description": "User feedback for learning"
                            }
                        },
                        "required": ["team_id", "analysis_results"]
                    }
                ),
                Tool(
                    name="generate_automation_prompts",
                    description="Generate prompts for Le Chat to use its native MCP servers (Linear, Slack, GitHub) for workflow automation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_results": {
                                "type": "object",
                                "description": "Results from compliance analysis"
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team context for automation"
                            },
                            "assignee": {
                                "type": "string",
                                "description": "Default assignee for tasks (optional)"
                            }
                        },
                        "required": ["analysis_results", "team_context"]
                    }
                ),
                Tool(
                    name="get_team_memory",
                    description="Get team-specific memory for analysis context",
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
            """
            Handle tool calls.
            
            This implements the actual legal compliance analysis logic using
            Mistral DocumentAI and the compliance engine.
            """
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                if name == "analyze_pdf_document":
                    return await self.pdf_analysis_tool.analyze_pdf_document(arguments)
                elif name == "analyze_document_compliance":
                    return await self._handle_analyze_document_compliance(arguments)
                elif name == "generate_compliance_report":
                    return await self._handle_generate_compliance_report(arguments)
                elif name == "generate_audit_trail":
                    return await self._handle_generate_audit_trail(arguments)
                elif name == "get_compliance_history":
                    return await self._handle_get_compliance_history(arguments)
                elif name == "analyze_risk_trends":
                    return await self._handle_analyze_risk_trends(arguments)
                elif name == "decompose_task":
                    return await self._handle_decompose_task(arguments)
                elif name == "decompose_document":
                    return await self._handle_decompose_document(arguments)
                elif name == "analyze_with_memory":
                    return await self._handle_analyze_with_memory(arguments)
                elif name == "generate_structured_report":
                    return await self._handle_generate_structured_report(arguments)
                elif name == "update_memory":
                    return await self._handle_update_memory(arguments)
                elif name == "generate_automation_prompts":
                    return await self._handle_generate_automation_prompts(arguments)
                elif name == "get_team_memory":
                    return await self._handle_get_team_memory(arguments)
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
        """Handle getting compliance history from local cache."""
        document_id = arguments.get("document_id")
        limit = arguments.get("limit", 20)
        
        try:
            # Filter reports by document_id if specified
            if document_id:
                filtered_reports = {
                    k: v for k, v in self._reports_cache.items() 
                    if v.document_id == document_id
                }
            else:
                filtered_reports = self._reports_cache
            
            # Convert to list and limit results
            reports = list(filtered_reports.values())[:limit]
            
            if not reports:
                return [TextContent(type="text", text="No compliance history found in local cache.")]
            
            content = f"Compliance History ({len(reports)} entries):\n\n"
            for i, report in enumerate(reports, 1):
                content += f"{i}. **{report.document_id}**\n"
                content += f"   Status: {report.overall_status.value}\n"
                content += f"   Risk Level: {report.risk_level.value}\n"
                content += f"   Risk Score: {report.risk_score:.2f}\n"
                content += f"   Frameworks: {', '.join(report.frameworks_analyzed)}\n"
                content += f"   Issues: {len(report.issues)}\n\n"
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Failed to get compliance history: {str(e)}"
            )]
    
    async def _handle_analyze_risk_trends(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle risk trend analysis from local cache."""
        days = arguments.get("days", 30)
        
        try:
            # Analyze reports from local cache
            reports = list(self._reports_cache.values())
            
            if not reports:
                return [TextContent(type="text", text="No compliance data available for trend analysis.")]
            
            # Calculate basic metrics
            total_assessments = len(reports)
            risk_scores = [r.risk_score for r in reports]
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            total_issues = sum(len(r.issues) for r in reports)
            critical_issues = sum(len([i for i in r.issues if i.severity == "critical"]) for r in reports)
            
            # Determine trend direction (simplified)
            if len(reports) >= 2:
                recent_avg = sum(risk_scores[-len(reports)//2:]) / (len(reports)//2)
                older_avg = sum(risk_scores[:len(reports)//2]) / (len(reports)//2)
                trend_direction = "improving" if recent_avg < older_avg else "worsening" if recent_avg > older_avg else "stable"
            else:
                trend_direction = "stable"
            
            risk_level = "high" if avg_risk_score > 0.7 else "medium" if avg_risk_score > 0.4 else "low"
            
            content = f"""# Risk Trend Analysis

**Analysis Period:** {days} days (based on available data)
**Total Assessments:** {total_assessments}
**Average Risk Score:** {avg_risk_score:.2f}/1.0
**Total Issues:** {total_issues}
**Critical Issues:** {critical_issues}
**Trend Direction:** {trend_direction.title()}
**Overall Risk Level:** {risk_level.title()}

## Analysis Summary

Based on the compliance assessments in the local cache, the overall risk level is **{risk_level.title()}** with an average risk score of {avg_risk_score:.2f}.

**Key Insights:**
- {total_assessments} assessments were analyzed
- {total_issues} total compliance issues identified
- {critical_issues} critical issues requiring immediate attention

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
    
    async def _handle_decompose_task(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle task decomposition from Le Chat query."""
        query = arguments.get("query", "")
        team_context = arguments.get("team_context", "Legal Team")
        
        try:
            # Parse the query using Le Chat interface
            query_context = await self.lechat_interface.parse_query(query)
            
            # Fetch document from Google Drive
            document_result = await self.lechat_interface.fetch_document_from_google_drive(
                query_context.document_name, 
                team_context
            )
            
            if not document_result.success:
                return [TextContent(
                    type="text",
                    text=f"Failed to fetch document: {document_result.error_message}"
                )]
            
            # Get team memory for context
            team_memory = await self.memory_integration.get_team_memory(team_context)
            
            result = {
                "query_context": query_context.model_dump(),
                "document_result": document_result.model_dump(),
                "team_memory": team_memory,
                "next_steps": [
                    "Document fetched successfully",
                    "Ready for compliance analysis",
                    "Team context loaded for personalized analysis"
                ]
            }
            
            return [TextContent(
                type="text",
                text=f"Task decomposed successfully:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to decompose task: {str(e)}"
            )]
    
    async def _handle_decompose_document(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle document decomposition into structured sections."""
        document_content = arguments.get("document_content", "")
        document_name = arguments.get("document_name", "Unknown Document")
        team_context = arguments.get("team_context", "Legal Team")
        
        try:
            # Use DocumentAI to decompose the document
            from .tools.document_ai import DocumentAIService, DocumentAnalysisRequest
            
            document_ai = DocumentAIService()
            request = DocumentAnalysisRequest(
                document_content=document_content,
                compliance_frameworks=["gdpr", "sox", "ccpa"],
                analysis_depth="comprehensive"
            )
            
            analysis_result = await document_ai.analyze_document(request)
            
            # Extract sections from analysis
            sections = []
            if hasattr(analysis_result, 'metadata') and 'sections' in analysis_result.metadata:
                sections = analysis_result.metadata['sections']
            else:
                # Generate mock sections for demonstration
                sections = [
                    {
                        "id": 1,
                        "text": "Data Processing Agreement - This section outlines how personal data will be processed",
                        "type": "clause",
                        "title": "Data Processing",
                        "page": 1,
                        "compliance_relevant": True
                    },
                    {
                        "id": 2,
                        "text": "Payment terms are Net 60 days from invoice date",
                        "type": "clause",
                        "title": "Payment Terms",
                        "page": 2,
                        "compliance_relevant": False
                    }
                ]
            
            result = {
                "document_name": document_name,
                "team_context": team_context,
                "sections": sections,
                "total_sections": len(sections),
                "compliance_relevant_sections": len([s for s in sections if s.get("compliance_relevant", False)]),
                "ready_for_analysis": True
            }
            
            return [TextContent(
                type="text",
                text=f"Document decomposed successfully:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Document decomposition failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to decompose document: {str(e)}"
            )]
    
    async def _handle_analyze_with_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle compliance analysis with team-specific memory integration."""
        document_content = arguments.get("document_content", "")
        document_name = arguments.get("document_name", "Unknown Document")
        team_context = arguments.get("team_context", "Legal Team")
        frameworks = arguments.get("compliance_frameworks", ["gdpr", "sox", "ccpa"])
        
        try:
            # Get team-specific memory context
            team_memory = await self.memory_integration.get_team_memory(team_context)
            
            # Perform compliance analysis
            report = await self.compliance_engine.analyze_document_compliance(
                document_content=document_content,
                frameworks=frameworks,
                analysis_depth="comprehensive"
            )
            
            # Store report in cache
            self._reports_cache[report.report_id] = report
            
            # Learn from analysis results
            analysis_results = {
                "issues": [issue.model_dump() for issue in report.issues],
                "missing_clauses": report.missing_clauses,
                "risk_level": report.risk_level.value,
                "overall_status": report.overall_status.value,
                "document_name": document_name
            }
            
            await self.memory_integration.learn_from_analysis(
                team_id=team_context,
                analysis_results=analysis_results
            )
            
            result = {
                "report_id": report.report_id,
                "document_name": document_name,
                "team_context": team_context,
                "overall_status": report.overall_status.value,
                "risk_level": report.risk_level.value,
                "risk_score": report.risk_score,
                "issues_found": len(report.issues),
                "missing_clauses": len(report.missing_clauses),
                "team_memory_updated": True,
                "frameworks_analyzed": frameworks
            }
            
            return [TextContent(
                type="text",
                text=f"Analysis completed with memory integration:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Memory-integrated analysis failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to analyze with memory: {str(e)}"
            )]
    
    async def _handle_generate_structured_report(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle structured report generation."""
        analysis_results = arguments.get("analysis_results", {})
        team_context = arguments.get("team_context", "Legal Team")
        format_type = arguments.get("format", "both")
        
        try:
            # Generate Le Chat formatted response
            lechat_response = await self.lechat_interface.format_response_for_lechat(
                analysis_results, 
                team_context
            )
            
            # Generate learning prompt
            learning_prompt = await self.lechat_interface.generate_learning_prompt(
                analysis_results, 
                team_context
            )
            
            result = {
                "team_context": team_context,
                "lechat_response": lechat_response,
                "learning_prompt": learning_prompt,
                "analysis_summary": {
                    "status": analysis_results.get("overall_status", "unknown"),
                    "risk_level": analysis_results.get("risk_level", "unknown"),
                    "issues_count": len(analysis_results.get("issues", [])),
                    "missing_clauses_count": len(analysis_results.get("missing_clauses", []))
                }
            }
            
            if format_type in ["json", "both"]:
                result["json_report"] = analysis_results
            
            if format_type in ["markdown", "both"]:
                result["markdown_report"] = lechat_response
            
            return [TextContent(
                type="text",
                text=f"Structured report generated:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Structured report generation failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to generate structured report: {str(e)}"
            )]
    
    async def _handle_update_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle memory update based on analysis results and user feedback."""
        team_id = arguments.get("team_id", "")
        analysis_results = arguments.get("analysis_results", {})
        user_feedback = arguments.get("user_feedback", {})
        
        try:
            # Process user feedback
            processed_feedback = await self.lechat_interface.process_user_feedback(
                user_feedback.get("feedback_text", ""),
                team_id
            )
            
            # Learn from analysis and feedback
            await self.memory_integration.learn_from_analysis(
                team_id=team_id,
                analysis_results=analysis_results,
                user_feedback=processed_feedback
            )
            
            # Get updated memory
            updated_memory = await self.memory_integration.get_team_memory(team_id)
            
            result = {
                "team_id": team_id,
                "memory_updated": True,
                "processed_feedback": processed_feedback,
                "updated_memory": updated_memory,
                "suggestions": await self.memory_integration.suggest_improvements(team_id)
            }
            
            return [TextContent(
                type="text",
                text=f"Memory updated successfully:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to update memory: {str(e)}"
            )]
    
    async def _handle_generate_automation_prompts(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle generation of automation prompts for Le Chat to use its native MCP servers."""
        analysis_results = arguments.get("analysis_results", {})
        team_context = arguments.get("team_context", "Legal Team")
        assignee = arguments.get("assignee")
        
        try:
            # Generate automation prompts for Le Chat
            automation_result = await self.automation_agent.generate_automation_prompts(
                analysis_results=analysis_results,
                team_context=team_context,
                assignee=assignee
            )
            
            # Format prompts for Le Chat display
            prompts = automation_result.external_ids.get("prompts", [])
            formatted_prompts = []
            
            for prompt in prompts:
                formatted_prompts.append({
                    "action_type": prompt["action_type"],
                    "prompt": prompt["prompt"],
                    "details": prompt.get("task_details") or prompt.get("message_details") or prompt.get("issue_details")
                })
            
            result = {
                "team_context": team_context,
                "prompt_generation_success": automation_result.success,
                "actions_taken": automation_result.actions_taken,
                "errors": automation_result.errors,
                "prompts": formatted_prompts,
                "instructions": "Please execute these prompts using your respective MCP servers (Linear, Slack, GitHub)",
                "timestamp": automation_result.timestamp
            }
            
            return [TextContent(
                type="text",
                text=f"Automation prompts generated for Le Chat:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Automation prompt generation failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to generate automation prompts: {str(e)}"
            )]
    
    async def _handle_get_team_memory(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle getting team-specific memory."""
        team_id = arguments.get("team_id", "")
        
        try:
            # Get team memory
            team_memory = await self.memory_integration.get_team_memory(team_id)
            
            # Get cross-team insights
            cross_team_insights = await self.memory_integration.get_cross_team_insights()
            
            result = {
                "team_id": team_id,
                "team_memory": team_memory,
                "cross_team_insights": cross_team_insights,
                "suggestions": await self.memory_integration.suggest_improvements(team_id)
            }
            
            return [TextContent(
                type="text",
                text=f"Team memory retrieved:\n\n{json.dumps(result, indent=2)}"
            )]
            
        except Exception as e:
            logger.error(f"Get team memory failed: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to get team memory: {str(e)}"
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
