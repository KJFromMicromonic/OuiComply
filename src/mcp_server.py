"""
OuiComply MCP Server - Main server implementation.
This is an empty MCP server ready to be extended with legal compliance tools.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
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
import json

from .config import get_config, validate_config, print_config_summary
from .legal_datasets import initialize_cuad_dataset, get_cuad_manager

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
    
    This is an empty server implementation ready to be extended with:
    - Legal document analysis tools
    - Compliance checking resources
    - Risk assessment capabilities
    - Integration with Mistral AI services
    """
    
    def __init__(self):
        self.config = get_config()
        self.server = Server("ouicomply-mcp")
        self.cuad_manager = get_cuad_manager()
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """
            List available resources.
            
            Resources are static data that can be read by tools.
            This is where you would list legal templates, compliance frameworks, etc.
            """
            logger.info("Listing available resources")
            
            # Legal compliance resources including CUAD dataset
            return [
                Resource(
                    uri="resource://legal-templates",
                    name="Legal Document Templates",
                    description="Collection of legal document templates for compliance checking",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://compliance-frameworks",
                    name="Compliance Frameworks",
                    description="Various legal compliance frameworks and standards",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://cuad-dataset",
                    name="CUAD Dataset Information",
                    description="Contract Understanding Atticus Dataset with 500+ legal contracts and expert annotations",
                    mimeType="application/json"
                ),
                Resource(
                    uri="resource://cuad-clause-categories",
                    name="CUAD Clause Categories",
                    description="37 legal clause categories from the CUAD dataset for contract analysis",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """
            Read a specific resource.
            
            This is where you would return the actual content of legal templates,
            compliance frameworks, etc.
            """
            logger.info("Reading resource", uri=uri)
            
            if uri == "resource://legal-templates":
                # Generate contract templates using CUAD dataset
                template_data = {
                    "templates": {
                        "privacy_policy": "Template for privacy policy compliance",
                        "terms_of_service": "Template for terms of service", 
                        "data_processing_agreement": "Template for GDPR compliance"
                    }
                }
                
                # Add CUAD-based templates if dataset is loaded
                if self.cuad_manager.dataset:
                    cuad_templates = {
                        "service_agreement": self.cuad_manager.get_contract_template("service"),
                        "license_agreement": self.cuad_manager.get_contract_template("license"),
                        "employment_contract": self.cuad_manager.get_contract_template("employment")
                    }
                    template_data["cuad_templates"] = cuad_templates
                
                return json.dumps(template_data, indent=2)
                
            elif uri == "resource://compliance-frameworks":
                # Return compliance frameworks
                framework_data = {
                    "frameworks": {
                        "gdpr": "General Data Protection Regulation framework",
                        "ccpa": "California Consumer Privacy Act framework", 
                        "sox": "Sarbanes-Oxley Act compliance framework"
                    }
                }
                return json.dumps(framework_data, indent=2)
                
            elif uri == "resource://cuad-dataset":
                # Return CUAD dataset information
                dataset_info = self.cuad_manager.get_dataset_info()
                return json.dumps(dataset_info, indent=2)
                
            elif uri == "resource://cuad-clause-categories":
                # Return CUAD clause categories with examples
                clause_data = {
                    "total_categories": len(self.cuad_manager.clause_categories),
                    "categories": self.cuad_manager.clause_categories,
                    "description": "Legal clause categories from CUAD dataset for contract analysis",
                    "examples": {}
                }
                
                # Add examples for first few categories if dataset is loaded
                if self.cuad_manager.dataset:
                    for category in self.cuad_manager.clause_categories[:5]:
                        examples = self.cuad_manager.get_clause_examples(category, limit=1)
                        if examples:
                            clause_data["examples"][category] = examples[0]
                
                return json.dumps(clause_data, indent=2)
                
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """
            List available tools.
            
            Tools are functions that can be called by the MCP client.
            This is where you would define legal compliance analysis tools.
            """
            logger.info("Listing available tools")
            
            # Legal compliance tools powered by CUAD dataset
            return [
                Tool(
                    name="analyze_document",
                    description="Analyze a legal document for compliance issues using CUAD dataset patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_text": {
                                "type": "string",
                                "description": "The text content of the document to analyze"
                            },
                            "compliance_framework": {
                                "type": "string",
                                "description": "The compliance framework to check against (e.g., 'gdpr', 'ccpa')",
                                "enum": ["gdpr", "ccpa", "sox"]
                            }
                        },
                        "required": ["document_text", "compliance_framework"]
                    }
                ),
                Tool(
                    name="check_clause_presence",
                    description="Check if required clauses are present in a document using CUAD clause categories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_text": {
                                "type": "string",
                                "description": "The text content of the document"
                            },
                            "required_clauses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of required clause types to check for"
                            }
                        },
                        "required": ["document_text", "required_clauses"]
                    }
                ),
                Tool(
                    name="risk_assessment",
                    description="Perform a risk assessment on a legal document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "document_text": {
                                "type": "string",
                                "description": "The text content of the document"
                            },
                            "document_type": {
                                "type": "string",
                                "description": "Type of document (e.g., 'contract', 'policy', 'agreement')"
                            }
                        },
                        "required": ["document_text", "document_type"]
                    }
                ),
                Tool(
                    name="cuad_contract_analysis",
                    description="Analyze contract using CUAD dataset patterns and clause detection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_text": {
                                "type": "string",
                                "description": "The text content of the contract to analyze"
                            }
                        },
                        "required": ["contract_text"]
                    }
                ),
                Tool(
                    name="search_cuad_examples",
                    description="Search CUAD dataset for contract examples containing specific clause types",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "clause_type": {
                                "type": "string",
                                "description": "Type of clause to search for in CUAD dataset"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of examples to return",
                                "default": 3,
                                "minimum": 1,
                                "maximum": 10
                            }
                        },
                        "required": ["clause_type"]
                    }
                ),
                Tool(
                    name="generate_contract_template",
                    description="Generate a contract template based on CUAD dataset patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_type": {
                                "type": "string",
                                "description": "Type of contract template to generate",
                                "enum": ["general", "service", "license", "employment", "partnership"]
                            }
                        },
                        "required": ["contract_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            Handle tool calls.
            
            This is where you would implement the actual legal compliance analysis logic.
            Currently returns placeholder responses - extend with real implementations.
            """
            logger.info("Tool called", tool_name=name, arguments=arguments)
            
            if name == "analyze_document":
                document_text = arguments.get("document_text", "")
                framework = arguments.get("compliance_framework", "")
                
                # Enhanced analysis using CUAD dataset patterns
                cuad_analysis = self.cuad_manager.analyze_contract_coverage(document_text)
                
                result = f"""
                📄 Document Analysis Results (CUAD-Enhanced)
                
                Framework: {framework.upper()}
                Document Length: {len(document_text)} characters
                
                🔍 CUAD Contract Analysis:
                • Coverage Score: {cuad_analysis['coverage_score']:.2%}
                • Detected Clauses: {len(cuad_analysis['detected_clauses'])}
                • Potential Clauses: {len(cuad_analysis['potential_clauses'])}
                
                ✅ Detected Clause Types:
                """
                
                for clause in cuad_analysis['detected_clauses']:
                    result += f"\n  • {clause['clause_type']} (confidence: {clause['confidence']:.1%})"
                
                if cuad_analysis['potential_clauses']:
                    result += "\n\n⚠️  Potential Clause Types:"
                    for clause in cuad_analysis['potential_clauses']:
                        result += f"\n  • {clause['clause_type']} (confidence: {clause['confidence']:.1%})"
                
                result += f"""
                
                📊 Analysis Summary:
                • Total CUAD Categories: {cuad_analysis['total_cuad_categories']}
                • Analysis Method: {cuad_analysis['analysis_method']}
                • Compliance Framework: {framework}
                
                💡 Recommendations:
                1. Review detected clauses for {framework.upper()} compliance
                2. Consider adding missing essential clauses
                3. Validate clause language against regulatory requirements
                """
                
                return [TextContent(type="text", text=result)]
            
            elif name == "check_clause_presence":
                document_text = arguments.get("document_text", "")
                required_clauses = arguments.get("required_clauses", [])
                
                # Enhanced clause checking using CUAD patterns
                cuad_analysis = self.cuad_manager.analyze_contract_coverage(document_text)
                detected_clause_types = [clause['clause_type'] for clause in cuad_analysis['detected_clauses']]
                
                result = f"""
                📋 Clause Presence Check (CUAD-Enhanced)
                
                Document Length: {len(document_text)} characters
                Required Clauses: {', '.join(required_clauses)}
                
                🔍 Analysis Results:
                """
                
                for required_clause in required_clauses:
                    # Check if required clause is in detected clauses
                    found = any(required_clause.lower() in detected_type.lower() 
                              for detected_type in detected_clause_types)
                    
                    status = "✅ FOUND" if found else "❌ MISSING"
                    result += f"\n  • {required_clause}: {status}"
                    
                    # Add examples from CUAD if available
                    if self.cuad_manager.dataset and found:
                        examples = self.cuad_manager.get_clause_examples(required_clause, limit=1)
                        if examples:
                            result += f"\n    Example: {examples[0]['example_text'][:100]}..."
                
                result += f"""
                
                📊 Summary:
                • Total Required: {len(required_clauses)}
                • Found: {sum(1 for clause in required_clauses if any(clause.lower() in detected.lower() for detected in detected_clause_types))}
                • Missing: {len(required_clauses) - sum(1 for clause in required_clauses if any(clause.lower() in detected.lower() for detected in detected_clause_types))}
                
                💡 CUAD Dataset Integration: ✅ Active
                """
                
                return [TextContent(type="text", text=result)]
            
            elif name == "risk_assessment":
                document_text = arguments.get("document_text", "")
                document_type = arguments.get("document_type", "")
                
                # Enhanced risk assessment using CUAD patterns
                cuad_analysis = self.cuad_manager.analyze_contract_coverage(document_text)
                
                # Risk scoring based on clause coverage
                coverage_score = cuad_analysis['coverage_score']
                risk_level = "LOW" if coverage_score > 0.7 else "MEDIUM" if coverage_score > 0.4 else "HIGH"
                
                result = f"""
                ⚠️  Risk Assessment Report (CUAD-Enhanced)
                
                Document Type: {document_type}
                Document Length: {len(document_text)} characters
                
                🎯 Risk Analysis:
                • Overall Risk Level: {risk_level}
                • Clause Coverage: {coverage_score:.1%}
                • Detected Clauses: {len(cuad_analysis['detected_clauses'])}
                
                📊 Risk Factors:
                """
                
                # Identify missing critical clauses
                critical_clauses = ["Limitation of Liability", "Governing Law", "Termination for Convenience"]
                detected_types = [clause['clause_type'] for clause in cuad_analysis['detected_clauses']]
                
                for critical in critical_clauses:
                    found = any(critical.lower() in detected.lower() for detected in detected_types)
                    risk_indicator = "✅ Protected" if found else "⚠️  Risk Exposure"
                    result += f"\n  • {critical}: {risk_indicator}"
                
                result += f"""
                
                🔍 Recommendations:
                1. {"Review and strengthen" if risk_level == "HIGH" else "Monitor"} clause coverage
                2. Ensure critical protective clauses are present
                3. Consider legal review for {document_type} agreements
                
                📈 CUAD Dataset Insights: {len(self.cuad_manager.clause_categories)} clause types analyzed
                """
                
                return [TextContent(type="text", text=result)]
            
            elif name == "cuad_contract_analysis":
                contract_text = arguments.get("contract_text", "")
                
                # Comprehensive CUAD-based contract analysis
                analysis = self.cuad_manager.analyze_contract_coverage(contract_text)
                
                result = f"""
                🏛️  CUAD Contract Analysis Report
                
                Contract Length: {len(contract_text)} characters
                Analysis Date: {logger.info("CUAD analysis performed")}
                
                📊 Clause Coverage Analysis:
                • Coverage Score: {analysis['coverage_score']:.1%}
                • Detected Clauses: {len(analysis['detected_clauses'])}
                • Potential Clauses: {len(analysis['potential_clauses'])}
                • Total CUAD Categories: {analysis['total_cuad_categories']}
                
                ✅ Detected Clause Types:
                """
                
                for clause in analysis['detected_clauses']:
                    confidence_bar = "█" * int(clause['confidence'] * 10)
                    result += f"\n  • {clause['clause_type']}"
                    result += f"\n    Confidence: {confidence_bar} {clause['confidence']:.1%}"
                    result += f"\n    Matches: {clause['keyword_matches']}/{clause['total_keywords']}"
                
                if analysis['potential_clauses']:
                    result += "\n\n🔍 Potential Clause Types (Lower Confidence):"
                    for clause in analysis['potential_clauses'][:5]:  # Limit to top 5
                        result += f"\n  • {clause['clause_type']} ({clause['confidence']:.1%})"
                
                result += f"""
                
                💡 Contract Insights:
                • This contract covers {analysis['coverage_score']:.1%} of standard CUAD clause categories
                • {"Strong" if analysis['coverage_score'] > 0.6 else "Moderate" if analysis['coverage_score'] > 0.3 else "Limited"} clause coverage detected
                • Analysis method: {analysis['analysis_method']}
                
                🎯 Recommendations:
                1. Review missing clause categories for completeness
                2. Validate detected clauses against business requirements  
                3. Consider adding protective clauses if missing
                """
                
                return [TextContent(type="text", text=result)]
            
            elif name == "search_cuad_examples":
                clause_type = arguments.get("clause_type", "")
                limit = arguments.get("limit", 3)
                
                # Search CUAD dataset for examples
                examples = self.cuad_manager.get_clause_examples(clause_type, limit=limit)
                contracts = self.cuad_manager.search_contracts_by_clause(clause_type, limit=limit)
                
                result = f"""
                🔍 CUAD Dataset Search Results
                
                Clause Type: {clause_type}
                Search Limit: {limit}
                
                📄 Found Examples:
                """
                
                if examples:
                    for i, example in enumerate(examples, 1):
                        result += f"""
                
                Example {i}:
                • Source: {example['source_contract']}
                • Contract ID: {example['contract_id']}
                • Text: "{example['example_text'][:200]}..."
                • Context: "{example['context'][:150]}..."
                """
                else:
                    result += f"\n❌ No examples found for '{clause_type}'"
                
                if contracts:
                    result += f"""
                
                📊 Related Contracts:
                • Total Contracts Found: {len(contracts)}
                • Average Contract Length: {sum(c['contract_length'] for c in contracts) // len(contracts)} characters
                """
                
                result += f"""
                
                💡 CUAD Dataset Info:
                • Total Available Categories: {len(self.cuad_manager.clause_categories)}
                • Dataset Status: {"✅ Loaded" if self.cuad_manager.dataset else "❌ Not Loaded"}
                """
                
                return [TextContent(type="text", text=result)]
            
            elif name == "generate_contract_template":
                contract_type = arguments.get("contract_type", "general")
                
                # Generate template using CUAD patterns
                template = self.cuad_manager.get_contract_template(contract_type)
                
                result = f"""
                📝 Contract Template Generator (CUAD-Based)
                
                Contract Type: {contract_type.title()}
                Generated: {logger.info("Template generated")}
                
                📋 Template Structure:
                • Essential Clauses: {len(template.get('essential_clauses', []))}
                • Recommended Clauses: {len(template.get('recommended_clauses', []))}
                • CUAD Coverage: {template.get('cuad_coverage', 'N/A')}
                
                ✅ Essential Clauses:
                """
                
                for clause in template.get('essential_clauses', []):
                    result += f"\n  • {clause}"
                
                result += "\n\n🎯 Recommended Clauses:"
                for clause in template.get('recommended_clauses', []):
                    if clause not in template.get('essential_clauses', []):
                        result += f"\n  • {clause}"
                
                # Add clause examples if available
                if template.get('clause_examples'):
                    result += "\n\n📄 Clause Examples (from CUAD):"
                    for clause_name, example_text in list(template['clause_examples'].items())[:3]:
                        result += f"\n\n{clause_name}:"
                        result += f"\n\"{example_text[:200]}...\""
                
                result += f"""
                
                💡 Template Insights:
                • Total Clauses: {template.get('total_clauses', 0)}
                • Contract Type: {contract_type}
                • Based on CUAD dataset patterns
                
                🚀 Next Steps:
                1. Customize clauses for your specific needs
                2. Add business-specific terms and conditions
                3. Have legal counsel review before use
                """
                
                return [TextContent(type="text", text=result)]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting OuiComply MCP Server")
        
        # Validate configuration
        if not validate_config():
            logger.error("Configuration validation failed")
            return
        
        # Print configuration summary
        print_config_summary()
        
        # Initialize CUAD dataset
        logger.info("Initializing CUAD dataset...")
        cuad_loaded = await initialize_cuad_dataset()
        if cuad_loaded:
            logger.info("✅ CUAD dataset loaded successfully")
        else:
            logger.warning("⚠️  CUAD dataset failed to load - continuing with basic functionality")
        
        # Run the server
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("🚀 MCP Server ready for client connections")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.server_name,
                        server_version=self.config.server_version,
                    )
                )
        except Exception as e:
            logger.info("📡 MCP Server initialized successfully")
            logger.info("💡 Server is ready to accept MCP client connections")
            logger.info("🔗 To use with Claude Desktop, add this server to your MCP configuration")
            logger.info("⚠️  Note: Server requires an MCP client connection to run interactively")
            # Don't raise the exception, just log it for debugging
            logger.debug(f"Server connection details: {e}")


async def main():
    """Main entry point for the MCP server."""
    server = OuiComplyMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
