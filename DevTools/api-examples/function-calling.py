"""
Function Calling Examples for Mistral AI

This module demonstrates how to implement function calling with Mistral AI
for compliance analysis in the OuiComply project.
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from mistralai import Mistral


class ComplianceAnalyzer:
    """
    Example compliance analyzer using Mistral function calling.
    
    This class demonstrates how to use Mistral's function calling
    capabilities for structured compliance analysis.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the compliance analyzer.
        
        Args:
            api_key: Mistral API key (optional, will use env var if not provided)
        """
        self.client = Mistral(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
        self.compliance_tools = self._define_compliance_tools()
    
    def _define_compliance_tools(self) -> List[Dict[str, Any]]:
        """
        Define the compliance analysis tools for Mistral.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "analyze_compliance_issues",
                    "description": "Analyze document for compliance issues across multiple frameworks",
                    "parameters": {
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
                                "items": {"type": "string"},
                                "description": "List of required clauses not found in the document"
                            },
                            "recommendations": {
                                "type": "array",
                                "items": {"type": "string"},
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
                            }
                        },
                        "required": ["compliance_issues", "missing_clauses", "recommendations", "risk_score", "compliance_status"]
                    }
                }
            }
        ]
    
    async def analyze_document(
        self,
        document_content: str,
        frameworks: List[str] = None,
        analysis_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze a document for compliance issues using function calling.
        
        Args:
            document_content: The document content to analyze
            frameworks: List of compliance frameworks to check (default: GDPR, SOX, CCPA)
            analysis_depth: Level of analysis detail
            
        Returns:
            Structured compliance analysis results
            
        Raises:
            ValueError: If no tool call is found in the response
            Exception: If the API request fails
        """
        if frameworks is None:
            frameworks = ["gdpr", "sox", "ccpa"]
        
        # Generate analysis prompt
        prompt = self._generate_analysis_prompt(document_content, frameworks, analysis_depth)
        
        try:
            # Make the API request with function calling
            response = await self.client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal compliance expert specializing in document analysis. Use the provided function to return structured compliance analysis. Be thorough and accurate in your assessment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                tools=self.compliance_tools,
                tool_choice="required",  # Force use of the function
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=4000
            )
            
            # Process the response
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                return json.loads(tool_call.function.arguments)
            else:
                raise ValueError("No tool call found in response")
                
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
        
        Please provide a comprehensive analysis using the provided function, including:
        1. Specific compliance issues found
        2. Missing required clauses
        3. Risk assessment
        4. Actionable recommendations
        """
    
    async def analyze_multiple_documents(
        self,
        documents: List[Dict[str, str]],
        frameworks: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple documents in parallel.
        
        Args:
            documents: List of documents with 'content' and 'name' keys
            frameworks: Compliance frameworks to check
            
        Returns:
            List of analysis results for each document
        """
        if frameworks is None:
            frameworks = ["gdpr", "sox", "ccpa"]
        
        # Create tasks for parallel processing
        tasks = [
            self.analyze_document(doc["content"], frameworks)
            for doc in documents
        ]
        
        # Execute all analyses in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "document_name": documents[i]["name"],
                    "error": str(result),
                    "success": False
                })
            else:
                processed_results.append({
                    "document_name": documents[i]["name"],
                    "analysis": result,
                    "success": True
                })
        
        return processed_results


async def main():
    """
    Example usage of the ComplianceAnalyzer.
    """
    # Initialize the analyzer
    analyzer = ComplianceAnalyzer()
    
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
        # Analyze the document
        print("Analyzing document for compliance...")
        result = await analyzer.analyze_document(
            document_content=sample_document,
            frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        # Display results
        print("\n=== COMPLIANCE ANALYSIS RESULTS ===")
        print(f"Status: {result['compliance_status'].upper()}")
        print(f"Risk Score: {result['risk_score']:.2f}/1.0")
        print(f"Issues Found: {len(result['compliance_issues'])}")
        print(f"Missing Clauses: {len(result['missing_clauses'])}")
        
        if result['compliance_issues']:
            print("\n=== COMPLIANCE ISSUES ===")
            for issue in result['compliance_issues']:
                print(f"\n{issue['severity'].upper()}: {issue['description']}")
                print(f"  Category: {issue['category']}")
                print(f"  Framework: {issue['framework'].upper()}")
                print(f"  Recommendation: {issue['recommendation']}")
                print(f"  Confidence: {issue['confidence']:.2f}")
        
        if result['missing_clauses']:
            print("\n=== MISSING CLAUSES ===")
            for clause in result['missing_clauses']:
                print(f"- {clause}")
        
        if result['recommendations']:
            print("\n=== RECOMMENDATIONS ===")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"{i}. {rec}")
        
    except Exception as e:
        print(f"Analysis failed: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
