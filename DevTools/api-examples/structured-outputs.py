"""
Structured Outputs Examples for Mistral AI

This module demonstrates how to use Mistral's structured output capabilities
with JSON schemas for reliable data extraction in compliance analysis.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from mistralai import Mistral


class StructuredComplianceAnalyzer:
    """
    Compliance analyzer using Mistral's structured output capabilities.
    
    This class demonstrates how to use JSON schemas for reliable,
    structured responses from Mistral AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the structured compliance analyzer.
        
        Args:
            api_key: Mistral API key (optional, will use env var if not provided)
        """
        self.client = Mistral(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
    
    def _get_compliance_schema(self) -> Dict[str, Any]:
        """
        Define the JSON schema for compliance analysis responses.
        
        Returns:
            JSON schema definition
        """
        return {
            "type": "object",
            "properties": {
                "compliance_issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Unique identifier for the issue"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Severity level of the issue"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of the compliance issue"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the issue"
                            },
                            "location": {
                                "type": "string",
                                "description": "Where in the document the issue was found"
                            },
                            "recommendation": {
                                "type": "string",
                                "description": "Recommended action to address the issue"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "AI confidence in the analysis"
                            },
                            "framework": {
                                "type": "string",
                                "description": "Compliance framework this relates to"
                            }
                        },
                        "required": ["issue_id", "severity", "category", "description", "recommendation", "confidence", "framework"]
                    }
                },
                "missing_clauses": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of required clauses not found in the document"
                },
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "General recommendations for compliance improvement"
                },
                "risk_score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Overall risk score (0 = low risk, 1 = high risk)"
                },
                "compliance_status": {
                    "type": "string",
                    "enum": ["compliant", "non_compliant", "partially_compliant", "requires_review"],
                    "description": "Overall compliance status"
                },
                "framework_analysis": {
                    "type": "object",
                    "properties": {
                        "gdpr": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "score": {"type": "number", "minimum": 0, "maximum": 1},
                                "issues": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "sox": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "score": {"type": "number", "minimum": 0, "maximum": 1},
                                "issues": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "ccpa": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string"},
                                "score": {"type": "number", "minimum": 0, "maximum": 1},
                                "issues": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                }
            },
            "required": ["compliance_issues", "missing_clauses", "recommendations", "risk_score", "compliance_status"]
        }
    
    async def analyze_document_structured(
        self,
        document_content: str,
        frameworks: List[str] = None,
        analysis_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a document using structured JSON schema output.
        
        Args:
            document_content: The document content to analyze
            frameworks: List of compliance frameworks to check
            analysis_depth: Level of analysis detail
            
        Returns:
            Structured compliance analysis results
            
        Raises:
            ValueError: If the response doesn't match the expected schema
            Exception: If the API request fails
        """
        if frameworks is None:
            frameworks = ["gdpr", "sox", "ccpa"]
        
        # Generate analysis prompt
        prompt = self._generate_analysis_prompt(document_content, frameworks, analysis_depth)
        
        try:
            # Make the API request with structured output
            response = await self.client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal compliance expert specializing in document analysis. Provide detailed, structured analysis of compliance issues using the exact JSON schema format specified."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "compliance_analysis",
                        "schema": self._get_compliance_schema(),
                        "strict": True  # Enforce schema compliance
                    }
                },
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=4000
            )
            
            # Parse the structured response
            result = json.loads(response.choices[0].message.content)
            
            # Validate the response structure
            self._validate_response(result)
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            print(f"Error during analysis: {e}")
            raise
    
    def _generate_analysis_prompt(
        self,
        document_content: str,
        frameworks: List[str],
        analysis_depth: str
    ) -> str:
        """
        Generate the analysis prompt for Mistral.
        
        Args:
            document_content: Document content to analyze
            frameworks: Compliance frameworks to check
            analysis_depth: Level of analysis detail
            
        Returns:
            Formatted analysis prompt
        """
        return f"""
        Analyze the following document for compliance with {', '.join(frameworks).upper()} frameworks.
        
        Analysis Requirements:
        - Depth: {analysis_depth}
        - Frameworks: {', '.join(frameworks)}
        - Focus on: Data protection, privacy rights, consent mechanisms, data retention, breach notification
        
        Document Content:
        {document_content[:2000]}...
        
        Please provide a comprehensive analysis in the exact JSON schema format specified, including:
        1. Specific compliance issues found with detailed information
        2. Missing required clauses for each framework
        3. Risk assessment and scoring
        4. Actionable recommendations
        5. Framework-specific analysis breakdown
        
        Ensure all required fields are populated and the response strictly follows the JSON schema.
        """
    
    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate that the response contains all required fields.
        
        Args:
            response: The parsed response to validate
            
        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            "compliance_issues", "missing_clauses", "recommendations", 
            "risk_score", "compliance_status"
        ]
        
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate compliance_issues structure
        if not isinstance(response["compliance_issues"], list):
            raise ValueError("compliance_issues must be a list")
        
        for issue in response["compliance_issues"]:
            required_issue_fields = [
                "issue_id", "severity", "category", "description", 
                "recommendation", "confidence", "framework"
            ]
            for field in required_issue_fields:
                if field not in issue:
                    raise ValueError(f"Missing required field in issue: {field}")
    
    async def analyze_document_with_validation(
        self,
        document_content: str,
        frameworks: List[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze a document with validation and retry logic.
        
        Args:
            document_content: The document content to analyze
            frameworks: List of compliance frameworks to check
            max_retries: Maximum number of retry attempts
            
        Returns:
            Validated compliance analysis results
            
        Raises:
            Exception: If all retry attempts fail
        """
        if frameworks is None:
            frameworks = ["gdpr", "sox", "ccpa"]
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = await self.analyze_document_structured(
                    document_content, frameworks
                )
                return result
                
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retrying
                    await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"All {max_retries} attempts failed. Last error: {last_error}")
    
    def export_analysis_report(
        self,
        analysis_result: Dict[str, Any],
        format_type: str = "markdown"
    ) -> str:
        """
        Export analysis results in various formats.
        
        Args:
            analysis_result: The analysis results to export
            format_type: Export format (markdown, json, html)
            
        Returns:
            Formatted report string
        """
        if format_type == "json":
            return json.dumps(analysis_result, indent=2)
        
        elif format_type == "markdown":
            return self._export_markdown(analysis_result)
        
        elif format_type == "html":
            return self._export_html(analysis_result)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_markdown(self, result: Dict[str, Any]) -> str:
        """Export analysis results as Markdown."""
        markdown = f"""# Compliance Analysis Report

## Summary
- **Status**: {result['compliance_status'].upper()}
- **Risk Score**: {result['risk_score']:.2f}/1.0
- **Issues Found**: {len(result['compliance_issues'])}
- **Missing Clauses**: {len(result['missing_clauses'])}

## Compliance Issues

"""
        
        for issue in result['compliance_issues']:
            markdown += f"""### {issue['severity'].upper()}: {issue['description']}

- **Category**: {issue['category']}
- **Framework**: {issue['framework'].upper()}
- **Location**: {issue.get('location', 'Not specified')}
- **Confidence**: {issue['confidence']:.2f}
- **Recommendation**: {issue['recommendation']}

"""
        
        if result['missing_clauses']:
            markdown += "## Missing Clauses\n\n"
            for clause in result['missing_clauses']:
                markdown += f"- {clause}\n"
            markdown += "\n"
        
        if result['recommendations']:
            markdown += "## Recommendations\n\n"
            for i, rec in enumerate(result['recommendations'], 1):
                markdown += f"{i}. {rec}\n"
        
        return markdown
    
    def _export_html(self, result: Dict[str, Any]) -> str:
        """Export analysis results as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Compliance Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .issue {{ margin: 20px 0; padding: 15px; border-left: 4px solid #ccc; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .low {{ border-left-color: #388e3c; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Analysis Report</h1>
        <p><strong>Status:</strong> {result['compliance_status'].upper()}</p>
        <p><strong>Risk Score:</strong> {result['risk_score']:.2f}/1.0</p>
        <p><strong>Issues Found:</strong> {len(result['compliance_issues'])}</p>
    </div>
    
    <h2>Compliance Issues</h2>
"""
        
        for issue in result['compliance_issues']:
            html += f"""    <div class="issue {issue['severity']}">
        <h3>{issue['severity'].upper()}: {issue['description']}</h3>
        <p><strong>Category:</strong> {issue['category']}</p>
        <p><strong>Framework:</strong> {issue['framework'].upper()}</p>
        <p><strong>Recommendation:</strong> {issue['recommendation']}</p>
    </div>
"""
        
        html += "</body></html>"
        return html


async def main():
    """
    Example usage of the StructuredComplianceAnalyzer.
    """
    # Initialize the analyzer
    analyzer = StructuredComplianceAnalyzer()
    
    # Example document content (privacy policy snippet)
    sample_document = """
    Privacy Policy
    
    We collect personal information from our users including names, email addresses, 
    and browsing history. This information is used to improve our services and 
    provide personalized content.
    
    We may share your information with third-party partners for marketing purposes.
    You can opt out of marketing communications at any time.
    
    We retain your information for as long as your account is active or as needed 
    to provide services to you.
    
    For questions about this policy, contact us at privacy@example.com.
    """
    
    try:
        # Analyze the document with structured output
        print("Analyzing document with structured output...")
        result = await analyzer.analyze_document_with_validation(
            document_content=sample_document,
            frameworks=["gdpr", "ccpa"],
            max_retries=3
        )
        
        # Display results
        print("\n=== STRUCTURED COMPLIANCE ANALYSIS ===")
        print(f"Status: {result['compliance_status'].upper()}")
        print(f"Risk Score: {result['risk_score']:.2f}/1.0")
        print(f"Issues Found: {len(result['compliance_issues'])}")
        print(f"Missing Clauses: {len(result['missing_clauses'])}")
        
        # Export in different formats
        print("\n=== MARKDOWN REPORT ===")
        markdown_report = analyzer.export_analysis_report(result, "markdown")
        print(markdown_report[:500] + "..." if len(markdown_report) > 500 else markdown_report)
        
        print("\n=== JSON REPORT ===")
        json_report = analyzer.export_analysis_report(result, "json")
        print(json_report[:300] + "..." if len(json_report) > 300 else json_report)
        
    except Exception as e:
        print(f"Analysis failed: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
