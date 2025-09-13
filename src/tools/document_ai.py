"""
DocumentAI Integration Module for Mistral AI.

This module provides comprehensive document analysis capabilities using Mistral's
DocumentAI service for compliance checking and risk assessment.
"""

import asyncio
import base64
import io
import logging
from typing import Any, Dict, List, Optional, Union, BinaryIO
from pathlib import Path
import mimetypes

import httpx
from mistralai import Mistral
from mistralai.models.documents import DocumentType
from pydantic import BaseModel, Field

from ..config import get_config

logger = logging.getLogger(__name__)


class DocumentAnalysisRequest(BaseModel):
    """
    Request model for document analysis.
    
    Attributes:
        document_content: The document content as bytes or file path
        document_type: Type of document (pdf, docx, txt, etc.)
        compliance_frameworks: List of compliance frameworks to check against
        analysis_depth: Level of analysis detail (basic, standard, comprehensive)
    """
    document_content: Union[bytes, str, Path] = Field(
        description="Document content as bytes, file path, or base64 string"
    )
    document_type: Optional[str] = Field(
        default=None,
        description="MIME type or file extension of the document"
    )
    compliance_frameworks: List[str] = Field(
        default=["gdpr", "sox", "ccpa"],
        description="Compliance frameworks to analyze against"
    )
    analysis_depth: str = Field(
        default="comprehensive",
        description="Analysis depth level"
    )


class ComplianceIssue(BaseModel):
    """
    Model representing a compliance issue found in a document.
    
    Attributes:
        issue_id: Unique identifier for the issue
        severity: Severity level (low, medium, high, critical)
        category: Category of compliance issue
        description: Human-readable description of the issue
        location: Where in the document the issue was found
        recommendation: Suggested mitigation action
        framework: Which compliance framework this relates to
        confidence: AI confidence score (0.0-1.0)
    """
    issue_id: str
    severity: str
    category: str
    description: str
    location: Optional[str] = None
    recommendation: str
    framework: str
    confidence: float = Field(ge=0.0, le=1.0)


class DocumentAnalysisResult(BaseModel):
    """
    Comprehensive document analysis result.
    
    Attributes:
        document_id: Unique identifier for the analyzed document
        document_type: Type of document analyzed
        analysis_timestamp: When the analysis was performed
        compliance_issues: List of identified compliance issues
        risk_score: Overall risk score (0.0-1.0)
        missing_clauses: List of required clauses not found
        recommendations: General recommendations for the document
        metadata: Additional analysis metadata
    """
    document_id: str
    document_type: str
    analysis_timestamp: str
    compliance_issues: List[ComplianceIssue]
    risk_score: float = Field(ge=0.0, le=1.0)
    missing_clauses: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class DocumentAIService:
    """
    Service for document analysis using Mistral's DocumentAI.
    
    This service provides comprehensive document analysis capabilities including:
    - Document parsing and content extraction
    - Compliance framework analysis
    - Risk assessment and scoring
    - Clause presence checking
    - Structured report generation
    """
    
    def __init__(self):
        """Initialize the DocumentAI service with Mistral client."""
        self.config = get_config()
        self.client = Mistral(api_key=self.config.mistral_api_key)
        self.compliance_frameworks = self._load_compliance_frameworks()
        
    def _load_compliance_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """
        Load compliance framework definitions.
        
        Returns:
            Dictionary mapping framework names to their definitions
        """
        return {
            "gdpr": {
                "name": "General Data Protection Regulation",
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
                ]
            },
            "sox": {
                "name": "Sarbanes-Oxley Act",
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
                ]
            },
            "ccpa": {
                "name": "California Consumer Privacy Act",
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
                ]
            },
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
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
                ]
            }
        }
    
    async def analyze_document(self, request: DocumentAnalysisRequest) -> DocumentAnalysisResult:
        """
        Analyze a document for compliance issues using Mistral DocumentAI.
        
        Args:
            request: Document analysis request containing document content and parameters
            
        Returns:
            Comprehensive analysis result with compliance issues and recommendations
            
        Raises:
            ValueError: If document content cannot be processed
            httpx.HTTPError: If Mistral API request fails
        """
        logger.info("Starting document analysis", 
                   frameworks=request.compliance_frameworks,
                   depth=request.analysis_depth)
        
        try:
            # Process document content
            document_bytes = await self._process_document_content(request.document_content)
            document_type = self._determine_document_type(request.document_type, document_bytes)
            
            # Upload document to Mistral
            document_id = await self._upload_document(document_bytes, document_type)
            
            # Perform compliance analysis
            analysis_result = await self._perform_compliance_analysis(
                document_id, 
                request.compliance_frameworks,
                request.analysis_depth
            )
            
            # Generate structured result
            result = DocumentAnalysisResult(
                document_id=document_id,
                document_type=document_type,
                analysis_timestamp=asyncio.get_event_loop().time(),
                compliance_issues=analysis_result["issues"],
                risk_score=analysis_result["risk_score"],
                missing_clauses=analysis_result["missing_clauses"],
                recommendations=analysis_result["recommendations"],
                metadata=analysis_result["metadata"]
            )
            
            logger.info("Document analysis completed", 
                       document_id=document_id,
                       issues_found=len(result.compliance_issues),
                       risk_score=result.risk_score)
            
            return result
            
        except Exception as e:
            logger.error("Document analysis failed", error=str(e))
            raise
    
    async def _process_document_content(self, content: Union[bytes, str, Path]) -> bytes:
        """
        Process document content into bytes format.
        
        Args:
            content: Document content in various formats
            
        Returns:
            Document content as bytes
            
        Raises:
            ValueError: If content cannot be processed
        """
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            # Try to decode as base64 first
            try:
                return base64.b64decode(content)
            except Exception:
                # Treat as file path
                path = Path(content)
                if path.exists():
                    return path.read_bytes()
                else:
                    raise ValueError(f"File not found: {content}")
        elif isinstance(content, Path):
            if content.exists():
                return content.read_bytes()
            else:
                raise ValueError(f"File not found: {content}")
        else:
            raise ValueError("Unsupported content type")
    
    def _determine_document_type(self, provided_type: Optional[str], content: bytes) -> str:
        """
        Determine the MIME type of the document.
        
        Args:
            provided_type: User-provided document type
            content: Document content as bytes
            
        Returns:
            MIME type string
        """
        if provided_type:
            return provided_type
        
        # Try to detect from content
        try:
            import magic
            mime_type = magic.from_buffer(content, mime=True)
            return mime_type
        except ImportError:
            # magic library not available, use fallback
            pass
        except Exception:
            # magic detection failed, use fallback
            pass
        
        # Fallback to file extension detection
        return "application/octet-stream"
    
    async def _upload_document(self, content: bytes, document_type: str) -> str:
        """
        Upload document to Mistral DocumentAI service.
        
        Args:
            content: Document content as bytes
            document_type: MIME type of the document
            
        Returns:
            Document ID from Mistral service
            
        Raises:
            httpx.HTTPError: If upload fails
        """
        try:
            # Convert bytes to base64 for Mistral API
            content_b64 = base64.b64encode(content).decode('utf-8')
            
            # Upload to Mistral
            response = await self.client.documents.create(
                file=content_b64,
                name=f"compliance_doc_{asyncio.get_event_loop().time()}",
                type=DocumentType.PDF if document_type == "application/pdf" else DocumentType.TEXT
            )
            
            return response.id
            
        except Exception as e:
            logger.error("Document upload failed", error=str(e))
            raise
    
    async def _perform_compliance_analysis(
        self, 
        document_id: str, 
        frameworks: List[str], 
        depth: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive compliance analysis using Mistral AI.
        
        Args:
            document_id: ID of the uploaded document
            frameworks: List of compliance frameworks to check
            depth: Analysis depth level
            
        Returns:
            Analysis results dictionary
        """
        issues = []
        missing_clauses = []
        recommendations = []
        
        # Analyze each compliance framework
        for framework in frameworks:
            if framework not in self.compliance_frameworks:
                logger.warning(f"Unknown compliance framework: {framework}")
                continue
                
            framework_def = self.compliance_frameworks[framework]
            
            # Generate analysis prompt
            analysis_prompt = self._generate_analysis_prompt(
                framework_def, 
                depth, 
                document_id
            )
            
            # Get AI analysis
            try:
                response = await self.client.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a legal compliance expert specializing in document analysis. Provide detailed, structured analysis of compliance issues."
                        },
                        {
                            "role": "user", 
                            "content": analysis_prompt
                        }
                    ],
                    temperature=0.1
                )
                
                # Parse AI response
                framework_analysis = self._parse_ai_response(
                    response.choices[0].message.content,
                    framework
                )
                
                issues.extend(framework_analysis["issues"])
                missing_clauses.extend(framework_analysis["missing_clauses"])
                recommendations.extend(framework_analysis["recommendations"])
                
            except Exception as e:
                logger.error(f"Analysis failed for framework {framework}", error=str(e))
                continue
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(issues)
        
        return {
            "issues": issues,
            "missing_clauses": list(set(missing_clauses)),
            "recommendations": list(set(recommendations)),
            "risk_score": risk_score,
            "metadata": {
                "frameworks_analyzed": frameworks,
                "analysis_depth": depth,
                "total_issues": len(issues)
            }
        }
    
    def _generate_analysis_prompt(
        self, 
        framework_def: Dict[str, Any], 
        depth: str, 
        document_id: str
    ) -> str:
        """
        Generate analysis prompt for Mistral AI.
        
        Args:
            framework_def: Compliance framework definition
            depth: Analysis depth level
            document_id: Document ID to analyze
            
        Returns:
            Formatted analysis prompt
        """
        required_clauses = framework_def["required_clauses"]
        risk_indicators = framework_def["risk_indicators"]
        
        prompt = f"""
        Analyze the document (ID: {document_id}) for compliance with {framework_def['name']}.
        
        Required Analysis:
        1. Check for presence of required clauses: {', '.join(required_clauses)}
        2. Identify risk indicators: {', '.join(risk_indicators)}
        3. Assess overall compliance posture
        4. Provide specific recommendations
        
        Analysis Depth: {depth}
        
        Please provide your analysis in the following JSON format:
        {{
            "issues": [
                {{
                    "issue_id": "unique_id",
                    "severity": "low|medium|high|critical",
                    "category": "clause_missing|risk_indicator|compliance_gap",
                    "description": "Detailed description",
                    "location": "Where found in document",
                    "recommendation": "Specific mitigation action",
                    "confidence": 0.95
                }}
            ],
            "missing_clauses": ["list", "of", "missing", "clauses"],
            "recommendations": ["list", "of", "general", "recommendations"]
        }}
        
        Be thorough and specific in your analysis.
        """
        
        return prompt
    
    def _parse_ai_response(self, response: str, framework: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.
        
        Args:
            response: Raw AI response
            framework: Compliance framework name
            
        Returns:
            Parsed analysis results
        """
        try:
            import json
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Add framework to issues
                for issue in parsed.get("issues", []):
                    issue["framework"] = framework
                
                return parsed
            else:
                # Fallback parsing
                return self._fallback_parse(response, framework)
                
        except Exception as e:
            logger.error("Failed to parse AI response", error=str(e))
            return self._fallback_parse(response, framework)
    
    def _fallback_parse(self, response: str, framework: str) -> Dict[str, Any]:
        """
        Fallback parsing when JSON parsing fails.
        
        Args:
            response: Raw AI response
            framework: Compliance framework name
            
        Returns:
            Basic parsed results
        """
        return {
            "issues": [
                {
                    "issue_id": f"fallback_{framework}_1",
                    "severity": "medium",
                    "category": "analysis_error",
                    "description": "Unable to parse detailed analysis",
                    "location": "Document analysis",
                    "recommendation": "Manual review required",
                    "framework": framework,
                    "confidence": 0.5
                }
            ],
            "missing_clauses": [],
            "recommendations": ["Manual review recommended due to parsing issues"]
        }
    
    def _calculate_risk_score(self, issues: List[ComplianceIssue]) -> float:
        """
        Calculate overall risk score based on identified issues.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not issues:
            return 0.0
        
        severity_weights = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8,
            "critical": 1.0
        }
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for issue in issues:
            weight = severity_weights.get(issue.severity, 0.5)
            total_weighted_score += weight * issue.confidence
            total_weight += weight
        
        return min(total_weighted_score / total_weight if total_weight > 0 else 0.0, 1.0)
    
    async def get_document_summary(self, document_id: str) -> str:
        """
        Get a summary of the analyzed document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document summary text
        """
        try:
            response = await self.client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a legal document summarizer. Provide clear, concise summaries of legal documents."
                    },
                    {
                        "role": "user",
                        "content": f"Provide a summary of document {document_id}, focusing on key legal terms, obligations, and potential compliance considerations."
                    }
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("Failed to generate document summary", error=str(e))
            return "Unable to generate summary due to processing error."
