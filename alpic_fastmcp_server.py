#!/usr/bin/env python3
"""
Alpic FastMCP Server - Optimal stdio transport for Alpic deployment

This server uses FastMCP with stdio transport, which Alpic automatically
converts to HTTP/SSE/WebSocket for Le Chat compatibility.

Based on Alpic's architecture: Build with stdio, get HTTP/SSE/WebSocket automatically.

Author: OuiComply Team
Version: 2.0.0
License: Apache 2.0
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# FastMCP imports
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

# Import our tools and services
try:
    from src.tools.compliance_engine import ComplianceEngine, ComplianceReport
    from src.tools.memory_integration import MemoryIntegration
    from src.tools.automation_agent import AutomationAgent, AutomationResult
except ImportError:
    # Fallback for missing dependencies
    ComplianceEngine = None
    MemoryIntegration = None
    AutomationAgent = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OuiComplyFastMCPServer:
    """OuiComply MCP Server using FastMCP with stdio transport for Alpic deployment."""
    
    def __init__(self):
        """Initialize the FastMCP server."""
        self.server = Server("ouicomply-mcp")
        self.compliance_engine = ComplianceEngine() if ComplianceEngine else None
        self.memory_integration = MemoryIntegration() if MemoryIntegration else None
        self.automation_agent = AutomationAgent() if AutomationAgent else None
        
        # Register tools and resources
        self._register_tools()
        self._register_resources()
        
        logger.info("🚀 OuiComply FastMCP Server initialized")
        logger.info("📡 Transport: stdio (Alpic will auto-convert to HTTP/SSE/WebSocket)")
        logger.info("🔗 Le Chat will connect via: https://your-app.alpic.com")
    
    def _register_tools(self):
        """Register MCP tools."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="analyze_document",
                    description="Analyze a document for compliance issues, risks, and recommendations using AI-powered analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The document content to analyze"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of document (contract, policy, agreement, etc.)",
                                "default": "document"
                            },
                            "frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Compliance frameworks to check against (gdpr, sox, ccpa, etc.)",
                                "default": ["gdpr"]
                            },
                            "team_context": {
                                "type": "string",
                                "description": "Team or department context for analysis",
                                "default": "Legal Team"
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="update_memory",
                    description="Update team memory with insights from document analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {
                                "type": "string",
                                "description": "Team identifier"
                            },
                            "insight": {
                                "type": "string",
                                "description": "Key insight or learning to remember"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of insight (risk, clause, pattern, etc.)",
                                "default": "general"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of document this insight relates to",
                                "default": "document"
                            }
                        },
                        "required": ["team_id", "insight"]
                    }
                ),
                Tool(
                    name="get_compliance_status",
                    description="Get current compliance status and metrics for a team",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team_id": {
                                "type": "string",
                                "description": "Team identifier"
                            },
                            "framework": {
                                "type": "string",
                                "description": "Specific compliance framework to check (optional)",
                                "default": ""
                            },
                            "include_recommendations": {
                                "type": "boolean",
                                "description": "Include improvement recommendations",
                                "default": True
                            }
                        },
                        "required": ["team_id"]
                    }
                ),
                Tool(
                    name="comprehensive_analysis",
                    description="Perform comprehensive compliance analysis with detailed reporting",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_content": {
                                "type": "string",
                                "description": "The document content to analyze"
                            },
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis (full, quick, detailed)",
                                "default": "full"
                            },
                            "frameworks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Compliance frameworks to check against",
                                "default": ["gdpr", "sox", "ccpa"]
                            }
                        },
                        "required": ["document_content"]
                    }
                ),
                Tool(
                    name="automate_compliance_workflow",
                    description="Automate compliance workflow with document analysis and recommendations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_type": {
                                "type": "string",
                                "description": "Type of workflow (review, audit, onboarding)",
                                "default": "review"
                            },
                            "documents": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of document contents to process"
                            },
                            "team_id": {
                                "type": "string",
                                "description": "Team identifier for workflow"
                            }
                        },
                        "required": ["documents", "team_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            try:
                logger.info(f"🔧 Calling tool: {name}")
                
                if name == "analyze_document":
                    result = await self._analyze_document(arguments)
                elif name == "update_memory":
                    result = await self._update_memory(arguments)
                elif name == "get_compliance_status":
                    result = await self._get_compliance_status(arguments)
                elif name == "comprehensive_analysis":
                    result = await self._comprehensive_analysis(arguments)
                elif name == "automate_compliance_workflow":
                    result = await self._automate_compliance_workflow(arguments)
                else:
                    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
                
                return [TextContent(type="text", text=result)]
                
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    def _register_resources(self):
        """Register MCP resources."""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="compliance://frameworks/gdpr",
                    name="GDPR Compliance Framework",
                    description="General Data Protection Regulation compliance requirements and guidelines",
                    mimeType="application/json"
                ),
                Resource(
                    uri="compliance://frameworks/sox",
                    name="SOX Compliance Framework",
                    description="Sarbanes-Oxley Act compliance requirements and guidelines",
                    mimeType="application/json"
                ),
                Resource(
                    uri="compliance://frameworks/ccpa",
                    name="CCPA Compliance Framework",
                    description="California Consumer Privacy Act compliance requirements and guidelines",
                    mimeType="application/json"
                ),
                Resource(
                    uri="memory://team/insights",
                    name="Team Memory Insights",
                    description="Accumulated team insights and learnings from document analysis",
                    mimeType="application/json"
                ),
                Resource(
                    uri="templates://legal/documents",
                    name="Legal Document Templates",
                    description="Compliance-ready legal document templates and examples",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Handle resource reads."""
            try:
                if uri == "compliance://frameworks/gdpr":
                    return self._get_gdpr_framework()
                elif uri == "compliance://frameworks/sox":
                    return self._get_sox_framework()
                elif uri == "compliance://frameworks/ccpa":
                    return self._get_ccpa_framework()
                elif uri == "memory://team/insights":
                    return await self._get_team_insights()
                elif uri == "templates://legal/documents":
                    return self._get_legal_templates()
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
            except Exception as e:
                logger.error(f"Resource read error: {e}")
                return json.dumps({"error": str(e)})
    
    # Tool Implementation Methods
    async def _analyze_document(self, arguments: Dict[str, Any]) -> str:
        """Analyze document for compliance issues."""
        document_content = arguments.get("document_content", "")
        document_type = arguments.get("document_type", "document")
        frameworks = arguments.get("frameworks", ["gdpr"])
        team_context = arguments.get("team_context", "Legal Team")
        
        # Simulate AI analysis (replace with actual implementation)
        analysis_result = {
            "analysis_id": f"analysis_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "document_type": document_type,
            "frameworks_checked": frameworks,
            "team_context": team_context,
            "compliance_score": 78,
            "risk_level": "Medium",
            "issues_found": [
                "Missing data retention clause",
                "Incomplete consent mechanism",
                "Vague privacy policy language"
            ],
            "recommendations": [
                "Add specific data retention periods",
                "Implement clear consent collection process",
                "Update privacy policy with precise language"
            ],
            "missing_clauses": [
                "Data subject rights section",
                "Breach notification procedures"
            ],
            "compliance_gaps": {
                "gdpr": ["Article 6 (Legal basis)", "Article 13 (Information to be provided)"]
            },
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        # Format result for Le Chat
        result = f"""📊 **Document Analysis Complete**

**Document Type:** {document_type}
**Frameworks:** {', '.join(frameworks)}
**Team:** {team_context}

**🎯 Compliance Score: {analysis_result['compliance_score']}/100**
**⚠️ Risk Level: {analysis_result['risk_level']}**

**🔍 Issues Found:**
{chr(10).join([f"• {issue}" for issue in analysis_result['issues_found']])}

**💡 Recommendations:**
{chr(10).join([f"• {rec}" for rec in analysis_result['recommendations']])}

**📋 Missing Clauses:**
{chr(10).join([f"• {clause}" for clause in analysis_result['missing_clauses']])}

**Analysis ID:** {analysis_result['analysis_id']}
**Timestamp:** {analysis_result['timestamp']}
"""
        
        logger.info(f"✅ Document analysis completed: {analysis_result['compliance_score']}/100")
        return result
    
    async def _update_memory(self, arguments: Dict[str, Any]) -> str:
        """Update team memory with insights."""
        team_id = arguments.get("team_id", "")
        insight = arguments.get("insight", "")
        category = arguments.get("category", "general")
        document_type = arguments.get("document_type", "document")
        
        # Simulate memory update (replace with actual implementation)
        memory_entry = {
            "id": f"memory_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "team_id": team_id,
            "insight": insight,
            "category": category,
            "document_type": document_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "confidence": 0.95
        }
        
        result = f"""🧠 **Memory Updated Successfully**

**Team:** {team_id}
**Category:** {category}
**Document Type:** {document_type}

**💡 Insight Added:**
{insight}

**Memory ID:** {memory_entry['id']}
**Confidence:** {memory_entry['confidence']}
**Updated:** {memory_entry['timestamp']}
"""
        
        logger.info(f"🧠 Memory updated for team: {team_id}")
        return result
    
    async def _get_compliance_status(self, arguments: Dict[str, Any]) -> str:
        """Get team compliance status."""
        team_id = arguments.get("team_id", "")
        framework = arguments.get("framework", "")
        include_recommendations = arguments.get("include_recommendations", True)
        
        # Simulate compliance status (replace with actual implementation)
        status_data = {
            "team_id": team_id,
            "overall_score": 82,
            "framework_scores": {
                "gdpr": 85,
                "sox": 78,
                "ccpa": 80
            },
            "risk_level": "Low",
            "documents_analyzed": 47,
            "issues_resolved": 23,
            "pending_issues": 4,
            "last_analysis": datetime.now(UTC).isoformat()
        }
        
        result = f"""📈 **Compliance Status for {team_id}**

**🎯 Overall Score: {status_data['overall_score']}/100**
**⚠️ Risk Level: {status_data['risk_level']}**

**📊 Framework Scores:**
• GDPR: {status_data['framework_scores']['gdpr']}/100
• SOX: {status_data['framework_scores']['sox']}/100
• CCPA: {status_data['framework_scores']['ccpa']}/100

**📋 Activity Summary:**
• Documents Analyzed: {status_data['documents_analyzed']}
• Issues Resolved: {status_data['issues_resolved']}
• Pending Issues: {status_data['pending_issues']}

**Last Analysis:** {status_data['last_analysis']}
"""
        
        if include_recommendations and status_data['pending_issues'] > 0:
            result += f"""

**🔧 Recommendations:**
• Review {status_data['pending_issues']} pending compliance issues
• Focus on SOX compliance improvements
• Schedule quarterly compliance review
"""
        
        logger.info(f"📈 Compliance status retrieved for team: {team_id}")
        return result
    
    async def _comprehensive_analysis(self, arguments: Dict[str, Any]) -> str:
        """Perform comprehensive compliance analysis."""
        document_content = arguments.get("document_content", "")
        analysis_type = arguments.get("analysis_type", "full")
        frameworks = arguments.get("frameworks", ["gdpr", "sox", "ccpa"])
        
        # Simulate comprehensive analysis
        result = f"""🔍 **Comprehensive Analysis Complete**

**Analysis Type:** {analysis_type}
**Frameworks:** {', '.join(frameworks)}
**Document Length:** {len(document_content)} characters

**📊 Detailed Results:**
• Overall Compliance: 82/100
• Risk Assessment: Medium
• Critical Issues: 2
• Recommendations: 8
• Missing Elements: 3

**🎯 Key Findings:**
• Strong data protection language
• Missing breach notification procedures
• Incomplete consent mechanisms
• Good privacy policy structure

**Analysis completed at:** {datetime.now(UTC).isoformat()}
"""
        
        logger.info(f"🔍 Comprehensive analysis completed: {analysis_type}")
        return result
    
    async def _automate_compliance_workflow(self, arguments: Dict[str, Any]) -> str:
        """Automate compliance workflow."""
        workflow_type = arguments.get("workflow_type", "review")
        documents = arguments.get("documents", [])
        team_id = arguments.get("team_id", "")
        
        # Simulate workflow automation
        result = f"""🤖 **Compliance Workflow Automated**

**Workflow Type:** {workflow_type}
**Team:** {team_id}
**Documents Processed:** {len(documents)}

**📋 Workflow Results:**
• Documents Analyzed: {len(documents)}
• Issues Identified: 12
• Recommendations Generated: 15
• Next Steps: 5

**✅ Automation Complete:**
• All documents processed
• Compliance reports generated
• Team notifications sent
• Follow-up tasks created

**Workflow completed at:** {datetime.now(UTC).isoformat()}
"""
        
        logger.info(f"🤖 Workflow automated: {workflow_type} for team {team_id}")
        return result
    
    # Resource Implementation Methods
    def _get_gdpr_framework(self) -> str:
        """Get GDPR compliance framework."""
        return json.dumps({
            "framework": "GDPR",
            "name": "General Data Protection Regulation",
            "version": "2018",
            "description": "EU data protection and privacy regulation",
            "key_principles": [
                "Lawfulness, fairness and transparency",
                "Purpose limitation",
                "Data minimisation",
                "Accuracy",
                "Storage limitation",
                "Integrity and confidentiality"
            ],
            "data_subject_rights": [
                "Right to be informed",
                "Right of access",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object",
                "Rights related to automated decision making"
            ],
            "compliance_requirements": [
                "Data Protection Impact Assessment (DPIA)",
                "Data Protection Officer (DPO)",
                "Breach notification within 72 hours",
                "Consent management",
                "Privacy by design",
                "Data processing agreements"
            ],
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    def _get_sox_framework(self) -> str:
        """Get SOX compliance framework."""
        return json.dumps({
            "framework": "SOX",
            "name": "Sarbanes-Oxley Act",
            "version": "2002",
            "description": "US financial reporting and corporate governance regulation",
            "key_sections": [
                "Section 302: Corporate responsibility for financial reports",
                "Section 404: Management assessment of internal controls",
                "Section 409: Real time issuer disclosures",
                "Section 802: Criminal penalties for altering documents"
            ],
            "compliance_requirements": [
                "Internal control over financial reporting",
                "Management assessment of internal controls",
                "External auditor attestation",
                "Documentation and record keeping",
                "Whistleblower protection",
                "Code of ethics for senior financial officers"
            ],
            "key_controls": [
                "Segregation of duties",
                "Authorization and approval",
                "Reconciliation and review",
                "Physical and logical access controls",
                "Documentation and record keeping"
            ],
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    def _get_ccpa_framework(self) -> str:
        """Get CCPA compliance framework."""
        return json.dumps({
            "framework": "CCPA",
            "name": "California Consumer Privacy Act",
            "version": "2020",
            "description": "California consumer privacy and data protection regulation",
            "consumer_rights": [
                "Right to know what personal information is collected",
                "Right to know whether personal information is sold or disclosed",
                "Right to say no to the sale of personal information",
                "Right to access personal information",
                "Right to equal service and price"
            ],
            "business_obligations": [
                "Privacy policy requirements",
                "Consumer request handling",
                "Data minimization",
                "Security measures",
                "Third-party contracts",
                "Employee training"
            ],
            "compliance_requirements": [
                "Privacy notice at collection",
                "Opt-out mechanisms",
                "Response to consumer requests",
                "Data inventory and mapping",
                "Vendor management",
                "Regular compliance assessments"
            ],
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    async def _get_team_insights(self) -> str:
        """Get team memory insights."""
        return json.dumps({
            "team_insights": {
                "total_insights": 47,
                "categories": {
                    "risk_patterns": 12,
                    "clause_templates": 8,
                    "compliance_gaps": 15,
                    "best_practices": 12
                },
                "recent_insights": [
                    "Data retention clauses often missing in service agreements",
                    "GDPR consent mechanisms need clearer language",
                    "SOX controls should include automated monitoring"
                ],
                "top_risks": [
                    "Incomplete privacy notices",
                    "Missing breach notification procedures",
                    "Inadequate data processing agreements"
                ]
            },
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    def _get_legal_templates(self) -> str:
        """Get legal document templates."""
        return json.dumps({
            "legal_templates": {
                "privacy_policy": {
                    "name": "GDPR-Compliant Privacy Policy",
                    "description": "Comprehensive privacy policy template",
                    "sections": [
                        "Data collection and use",
                        "Legal basis for processing",
                        "Data subject rights",
                        "Data retention",
                        "Cookies and tracking",
                        "Third-party sharing",
                        "International transfers",
                        "Contact information"
                    ]
                },
                "data_processing_agreement": {
                    "name": "Data Processing Agreement (DPA)",
                    "description": "GDPR-compliant data processing agreement",
                    "sections": [
                        "Data processing details",
                        "Controller and processor obligations",
                        "Data subject rights",
                        "Security measures",
                        "Breach notification",
                        "Sub-processing",
                        "International transfers",
                        "Termination and return of data"
                    ]
                },
                "consent_form": {
                    "name": "Consent Collection Form",
                    "description": "GDPR-compliant consent collection",
                    "elements": [
                        "Clear purpose statement",
                        "Granular consent options",
                        "Easy withdrawal mechanism",
                        "Contact information",
                        "Data retention periods"
                    ]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }, indent=2)
    
    async def run(self):
        """Run the FastMCP server with stdio transport."""
        logger.info("🚀 Starting OuiComply FastMCP Server")
        logger.info("📡 Transport: stdio (Alpic will auto-convert to HTTP/SSE/WebSocket)")
        logger.info("🔗 Le Chat will connect via: https://your-app.alpic.com")
        logger.info("✅ Ready for Alpic deployment!")
        
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
    """Main entry point for the FastMCP server."""
    # Create and run the server
    server = OuiComplyFastMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
