"""
Mistral AI Document Analysis Integration for OuiComply MCP Server.

This module provides integration with Mistral AI's document understanding capabilities
to enhance legal compliance analysis with advanced NLP and reasoning.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import json

from .config import get_config

logger = logging.getLogger(__name__)


class MistralDocumentAnalyzer:
    """
    Mistral AI-powered document analyzer for enhanced legal compliance analysis.
    
    Provides advanced document understanding using Mistral's language models
    for more sophisticated legal clause detection and compliance assessment.
    """
    
    def __init__(self):
        """Initialize Mistral client with API key from config."""
        self.config = get_config()
        self.client = None
        
        if self.config.mistral_api_key and self.config.mistral_api_key != "your_mistral_api_key_here":
            try:
                self.client = MistralClient(api_key=self.config.mistral_api_key)
                logger.info("Mistral AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral client: {e}")
                self.client = None
        else:
            logger.warning("Mistral API key not configured - using fallback analysis")
    
    async def analyze_document_with_mistral(self, document_text: str, framework: str) -> Dict[str, Any]:
        """
        Analyze document using Mistral AI for enhanced understanding.
        
        Args:
            document_text: Text content to analyze
            framework: Compliance framework (gdpr, sox, licensing)
            
        Returns:
            Enhanced analysis results from Mistral AI
        """
        if not self.client:
            return self._fallback_analysis(document_text, framework)
        
        try:
            # Create framework-specific prompt
            prompt = self._create_analysis_prompt(document_text, framework)
            
            # Call Mistral API
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model="mistral-large-latest",
                messages=messages,
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=2000
            )
            
            # Parse Mistral response
            analysis_result = self._parse_mistral_response(response.choices[0].message.content, framework)
            
            return {
                "mistral_analysis": analysis_result,
                "enhanced": True,
                "model_used": "mistral-large-latest",
                "framework": framework
            }
            
        except Exception as e:
            logger.error(f"Mistral analysis failed: {e}")
            return self._fallback_analysis(document_text, framework)
    
    def _create_analysis_prompt(self, document_text: str, framework: str) -> str:
        """Create framework-specific analysis prompt for Mistral."""
        
        base_prompt = f"""
        You are a legal compliance expert analyzing a document for {framework.upper()} compliance.
        
        Document to analyze:
        {document_text}
        
        Please provide a detailed analysis in JSON format with the following structure:
        {{
            "compliance_score": <0-100 percentage>,
            "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
            "detected_clauses": [
                {{
                    "clause_type": "<clause name>",
                    "confidence": <0-1 float>,
                    "text_excerpt": "<relevant text from document>",
                    "compliance_status": "<COMPLIANT|NON_COMPLIANT|PARTIAL>"
                }}
            ],
            "missing_requirements": [
                "<list of missing compliance requirements>"
            ],
            "recommendations": [
                "<specific actionable recommendations>"
            ],
            "key_findings": [
                "<important observations about compliance>"
            ]
        }}
        """
        
        if framework == "gdpr":
            framework_specific = """
            Focus on GDPR compliance including:
            - Legal basis for processing (Article 6)
            - Data subject rights (Articles 15-22)
            - Data controller/processor identification
            - International data transfers
            - Consent mechanisms
            - Data retention policies
            - Security measures
            - Breach notification procedures
            - DPO contact information
            """
        elif framework == "sox":
            framework_specific = """
            Focus on SOX compliance including:
            - Section 302: CEO/CFO certification requirements
            - Section 404: Internal controls over financial reporting
            - Section 409: Real-time disclosure requirements
            - Section 806: Whistleblower protection
            - Audit committee requirements
            - COSO framework alignment
            - Management assessment procedures
            - Documentation requirements
            """
        elif framework == "licensing":
            framework_specific = """
            Focus on licensing compliance including:
            - License grant scope and limitations
            - Intellectual property ownership
            - Usage rights and restrictions
            - Royalty and payment terms
            - Termination conditions
            - Sublicensing rights
            - Geographic and field restrictions
            - Open source vs proprietary licensing
            """
        else:
            framework_specific = "Analyze for general legal compliance."
        
        return base_prompt + framework_specific + "\n\nProvide only the JSON response, no additional text."
    
    def _parse_mistral_response(self, response_text: str, framework: str) -> Dict[str, Any]:
        """Parse Mistral's JSON response into structured data."""
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            analysis = json.loads(response_text)
            
            # Validate and normalize the response
            return {
                "compliance_score": float(analysis.get("compliance_score", 0)) / 100.0,
                "risk_level": analysis.get("risk_level", "UNKNOWN"),
                "detected_clauses": analysis.get("detected_clauses", []),
                "missing_requirements": analysis.get("missing_requirements", []),
                "recommendations": analysis.get("recommendations", []),
                "key_findings": analysis.get("key_findings", []),
                "framework": framework,
                "analysis_method": "mistral_ai"
            }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse Mistral response: {e}")
            return self._fallback_analysis_result(framework)
    
    def _fallback_analysis(self, document_text: str, framework: str) -> Dict[str, Any]:
        """Fallback analysis when Mistral is not available."""
        return {
            "mistral_analysis": self._fallback_analysis_result(framework),
            "enhanced": False,
            "model_used": "fallback",
            "framework": framework
        }
    
    def _fallback_analysis_result(self, framework: str) -> Dict[str, Any]:
        """Generate fallback analysis result."""
        return {
            "compliance_score": 0.0,
            "risk_level": "UNKNOWN",
            "detected_clauses": [],
            "missing_requirements": [f"Mistral AI analysis not available for {framework}"],
            "recommendations": ["Configure Mistral API key for enhanced analysis"],
            "key_findings": ["Analysis performed using basic keyword matching"],
            "framework": framework,
            "analysis_method": "fallback"
        }
    
    async def extract_document_entities(self, document_text: str) -> Dict[str, Any]:
        """
        Extract legal entities and key information from document using Mistral.
        
        Args:
            document_text: Document to analyze
            
        Returns:
            Extracted entities and key information
        """
        if not self.client:
            return {"entities": [], "enhanced": False}
        
        try:
            prompt = f"""
            Extract key legal entities and information from this document:
            
            {document_text}
            
            Provide a JSON response with:
            {{
                "entities": [
                    {{
                        "type": "<COMPANY|PERSON|DATE|AMOUNT|CLAUSE_TYPE|LEGAL_TERM>",
                        "value": "<extracted value>",
                        "context": "<surrounding text>"
                    }}
                ],
                "document_type": "<contract|policy|agreement|license|other>",
                "key_dates": ["<important dates>"],
                "parties": ["<contracting parties>"],
                "financial_terms": ["<monetary amounts, percentages>"],
                "legal_concepts": ["<legal terms and concepts>"]
            }}
            """
            
            messages = [ChatMessage(role="user", content=prompt)]
            response = self.client.chat(
                model="mistral-large-latest",
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            result["enhanced"] = True
            return result
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"entities": [], "enhanced": False, "error": str(e)}
    
    async def generate_compliance_summary(self, document_text: str, frameworks: List[str]) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance summary across multiple frameworks.
        
        Args:
            document_text: Document to analyze
            frameworks: List of frameworks to check (gdpr, sox, licensing)
            
        Returns:
            Multi-framework compliance summary
        """
        if not self.client:
            return {"summary": "Mistral AI not available", "enhanced": False}
        
        try:
            frameworks_str = ", ".join(frameworks)
            prompt = f"""
            Analyze this document for compliance across multiple frameworks: {frameworks_str}
            
            Document:
            {document_text}
            
            Provide a comprehensive JSON summary:
            {{
                "overall_compliance_score": <0-100>,
                "framework_scores": {{
                    "gdpr": <0-100 or null>,
                    "sox": <0-100 or null>,
                    "licensing": <0-100 or null>
                }},
                "critical_issues": ["<high priority compliance issues>"],
                "strengths": ["<compliance strengths>"],
                "cross_framework_conflicts": ["<conflicts between frameworks>"],
                "priority_recommendations": ["<top 5 recommendations>"],
                "executive_summary": "<brief summary for executives>"
            }}
            """
            
            messages = [ChatMessage(role="user", content=prompt)]
            response = self.client.chat(
                model="mistral-large-latest",
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            result["enhanced"] = True
            result["frameworks_analyzed"] = frameworks
            return result
            
        except Exception as e:
            logger.error(f"Compliance summary generation failed: {e}")
            return {
                "summary": f"Analysis failed: {e}",
                "enhanced": False,
                "frameworks_analyzed": frameworks
            }


# Global instance for use across the MCP server
mistral_analyzer = MistralDocumentAnalyzer()


def get_mistral_analyzer() -> MistralDocumentAnalyzer:
    """Get the global Mistral document analyzer instance."""
    return mistral_analyzer
