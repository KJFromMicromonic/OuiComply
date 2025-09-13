"""
PDF Analysis Tool for MCP Server.

This tool provides step-by-step PDF document analysis using the PDFProcessor.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.types import TextContent
from .pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class PDFAnalysisTool:
    """
    PDF Analysis Tool for MCP Server.
    
    Provides step-by-step PDF document processing and analysis.
    """
    
    def __init__(self):
        """Initialize the PDF analysis tool."""
        self.processor = PDFProcessor()
    
    async def analyze_pdf_document(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Analyze a PDF document step by step.
        
        Args:
            arguments: Dictionary containing:
                - document_path: Path to the PDF file
                - include_steps: Whether to include detailed step information
                - output_format: Output format (detailed, summary, structured)
        
        Returns:
            List of TextContent with analysis results
        """
        try:
            document_path = arguments.get("document_path", "")
            include_steps = arguments.get("include_steps", True)
            output_format = arguments.get("output_format", "detailed")
            
            if not document_path:
                return [TextContent(
                    type="text",
                    text="Error: document_path is required"
                )]
            
            # Convert to Path object
            pdf_path = Path(document_path)
            
            if not pdf_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: PDF file not found: {document_path}"
                )]
            
            if pdf_path.suffix.lower() != '.pdf':
                return [TextContent(
                    type="text",
                    text=f"Error: File is not a PDF: {document_path}"
                )]
            
            logger.info(f"Starting PDF analysis: {pdf_path.name}")
            
            # Process PDF step by step
            results = await self.processor.process_pdf_step_by_step(pdf_path)
            
            # Format output based on requested format
            if output_format == "summary":
                content = self._format_summary_output(results)
            elif output_format == "structured":
                content = self._format_structured_output(results)
            else:  # detailed
                content = self._format_detailed_output(results, include_steps)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            return [TextContent(
                type="text",
                text=f"Error during PDF analysis: {str(e)}"
            )]
    
    def _format_summary_output(self, results: Dict[str, Any]) -> str:
        """Format results as a summary."""
        if results["overall_status"] != "success":
            return f"❌ PDF Analysis Failed\nError: {results.get('error', 'Unknown error')}"
        
        structured = results["structured_output"]
        compliance = results["compliance_analysis"]
        
        return f"""# PDF Analysis Summary

**Document:** {results["filename"]}
**File Size:** {results["file_size"]:,} bytes
**Status:** ✅ Successfully Processed

## Document Summary
{structured["summary"]}

## Key Sections
{chr(10).join(f"- {section}" for section in structured["key_sections"])}

## Compliance Areas
{chr(10).join(f"- {area}" for area in structured["compliance_areas"])}

## Risk Assessment
- **Overall Risk Score:** {compliance["overall_risk_score"]:.1f}/1.0
- **Compliance Status:** {compliance["compliance_status"].replace("_", " ").title()}
- **Risk Indicators:** {len(compliance["risk_indicators"])} found

## Recommendations
{chr(10).join(f"- {rec}" for rec in structured["recommendations"])}

**Confidence Score:** {structured["confidence_score"]:.1f}/1.0
"""
    
    def _format_structured_output(self, results: Dict[str, Any]) -> str:
        """Format results as structured data."""
        if results["overall_status"] != "success":
            return f"Error: {results.get('error', 'Unknown error')}"
        
        import json
        return json.dumps(results, indent=2, default=str)
    
    def _format_detailed_output(self, results: Dict[str, Any], include_steps: bool) -> str:
        """Format results with detailed information."""
        if results["overall_status"] != "success":
            return f"❌ PDF Analysis Failed\nError: {results.get('error', 'Unknown error')}"
        
        content = f"""# PDF Document Analysis - Detailed Report

**Document:** {results["filename"]}
**File Path:** {results["file_path"]}
**File Size:** {results["file_size"]:,} bytes
**Processing Time:** {results["processing_time"]}

"""
        
        if include_steps:
            content += "## Processing Steps\n\n"
            for step_name, step_data in results["steps"].items():
                status_icon = "✅" if step_data["status"] == "success" else "❌"
                content += f"### {step_name.replace('_', ' ').title()}\n"
                content += f"{status_icon} **Status:** {step_data['status']}\n"
                content += f"**Timestamp:** {step_data['timestamp']}\n"
                
                # Add step-specific details
                if step_name == "read_pdf":
                    content += f"**File Size:** {step_data['file_size']:,} bytes\n"
                elif step_name == "extract_text":
                    content += f"**Text Length:** {step_data['text_length']:,} characters\n"
                    content += f"**Page Count:** {step_data['page_count']}\n"
                elif step_name == "structured_output":
                    content += f"**Summary Length:** {step_data['summary_length']:,} characters\n"
                    content += f"**Key Sections:** {step_data['key_sections_count']}\n"
                    content += f"**Confidence Score:** {step_data['confidence_score']:.2f}\n"
                elif step_name == "compliance_analysis":
                    content += f"**Compliance Areas:** {step_data['compliance_areas']}\n"
                    content += f"**Risk Indicators:** {step_data['risk_indicators']}\n"
                    content += f"**Recommendations:** {step_data['recommendations']}\n"
                
                content += "\n"
        
        # Add document content summary
        doc_content = results["document_content"]
        content += f"""## Document Content

**Document ID:** {doc_content["document_id"]}
**Content Type:** {doc_content["content_type"]}
**Page Count:** {doc_content["page_count"]}
**Text Length:** {len(doc_content["extracted_text"]):,} characters

### Extracted Text Preview
```
{doc_content["extracted_text"][:500]}...
```

"""
        
        # Add structured output
        structured = results["structured_output"]
        content += f"""## Structured Analysis

**Summary:** {structured["summary"]}

**Key Sections:**
{chr(10).join(f"- {section}" for section in structured["key_sections"])}

**Compliance Areas:**
{chr(10).join(f"- {area}" for area in structured["compliance_areas"])}

**Risk Indicators:**
{chr(10).join(f"- {indicator}" for indicator in structured["risk_indicators"])}

**Recommendations:**
{chr(10).join(f"- {rec}" for rec in structured["recommendations"])}

**Confidence Score:** {structured["confidence_score"]:.2f}/1.0

"""
        
        # Add compliance analysis
        compliance = results["compliance_analysis"]
        content += f"""## Compliance Analysis

**Overall Risk Score:** {compliance["overall_risk_score"]:.2f}/1.0
**Compliance Status:** {compliance["compliance_status"].replace("_", " ").title()}

**Critical Issues:** {len(compliance["critical_issues"])}
{chr(10).join(f"- {issue}" for issue in compliance["critical_issues"]) if compliance["critical_issues"] else "None identified"}

**Missing Clauses:** {len(compliance["missing_clauses"])}
{chr(10).join(f"- {clause}" for clause in compliance["missing_clauses"]) if compliance["missing_clauses"] else "None identified"}

"""
        
        return content
