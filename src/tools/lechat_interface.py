"""
Le Chat Interface Agent for OuiComply MCP Server.

This module provides integration with Le Chat for query parsing, document fetching
via Google Drive connector, and seamless user experience.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class QueryContext(BaseModel):
    """
    Parsed query context from Le Chat.
    
    Attributes:
        document_name: Name of the document to analyze
        team: Team context (e.g., "Procurement Team", "Sales Team")
        query_type: Type of query (compliance_check, analysis, etc.)
        urgency: Urgency level (low, medium, high, critical)
        additional_context: Any additional context from the query
    """
    document_name: str
    team: str
    query_type: str = "compliance_check"
    urgency: str = "medium"
    additional_context: Dict[str, Any] = Field(default_factory=dict)


class DocumentFetchResult(BaseModel):
    """
    Result of document fetching from Google Drive.
    
    Attributes:
        document_id: Google Drive document ID
        document_name: Name of the document
        content: Document content as text
        mime_type: MIME type of the document
        size: Size of the document in bytes
        fetch_timestamp: When the document was fetched
        success: Whether the fetch was successful
        error_message: Error message if fetch failed
    """
    document_id: str
    document_name: str
    content: str
    mime_type: str
    size: int
    fetch_timestamp: str
    success: bool = True
    error_message: Optional[str] = None


class LeChatInterface:
    """
    Le Chat interface agent for query processing and document fetching.
    
    This agent handles:
    - Query parsing and context extraction
    - Google Drive document fetching
    - Team context management
    - User experience optimization
    """
    
    def __init__(self):
        """Initialize the Le Chat interface agent."""
        self.team_patterns = {
            "procurement": ["procurement", "vendor", "supplier", "purchase"],
            "sales": ["sales", "customer", "client", "revenue"],
            "legal": ["legal", "compliance", "contract", "agreement"],
            "hr": ["hr", "human resources", "employee", "staff"],
            "finance": ["finance", "financial", "accounting", "budget"]
        }
        
        self.query_types = {
            "compliance_check": ["check", "compliance", "audit", "review"],
            "analysis": ["analyze", "analysis", "examine", "study"],
            "risk_assessment": ["risk", "assess", "evaluate", "score"],
            "documentation": ["document", "create", "generate", "write"]
        }
    
    async def parse_query(self, query: str) -> QueryContext:
        """
        Parse a Le Chat query to extract context and intent.
        
        Args:
            query: Raw query from Le Chat
            
        Returns:
            Parsed query context
        """
        logger.info(f"Parsing Le Chat query: {query}")
        
        # Extract document name
        document_name = self._extract_document_name(query)
        
        # Determine team context
        team = self._determine_team_context(query)
        
        # Determine query type
        query_type = self._determine_query_type(query)
        
        # Determine urgency
        urgency = self._determine_urgency(query)
        
        # Extract additional context
        additional_context = self._extract_additional_context(query)
        
        context = QueryContext(
            document_name=document_name,
            team=team,
            query_type=query_type,
            urgency=urgency,
            additional_context=additional_context
        )
        
        logger.info(f"Parsed query context: {context.model_dump()}")
        return context
    
    def _extract_document_name(self, query: str) -> str:
        """Extract document name from query."""
        # Look for common document patterns
        patterns = [
            r'([A-Za-z0-9_-]+\.(?:pdf|docx?|txt|doc))',  # File extensions
            r'"([^"]+)"',  # Quoted text
            r'for\s+([A-Za-z0-9_-]+)',  # "for DocumentName"
            r'check\s+([A-Za-z0-9_-]+)',  # "check DocumentName"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Fallback: extract first meaningful word sequence
        words = query.split()
        if len(words) > 1:
            # Skip common words and take the first substantial word
            skip_words = {"check", "analyze", "review", "for", "the", "a", "an"}
            for word in words:
                if word.lower() not in skip_words and len(word) > 2:
                    return word
        
        return "Unknown_Document"
    
    def _determine_team_context(self, query: str) -> str:
        """Determine team context from query."""
        query_lower = query.lower()
        
        for team, keywords in self.team_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return f"{team.title()} Team"
        
        # Default to Legal Team for compliance queries
        return "Legal Team"
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query."""
        query_lower = query.lower()
        
        for query_type, keywords in self.query_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return query_type
        
        return "compliance_check"
    
    def _determine_urgency(self, query: str) -> str:
        """Determine urgency level from query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["urgent", "asap", "immediately", "critical"]):
            return "critical"
        elif any(word in query_lower for word in ["soon", "priority", "important"]):
            return "high"
        elif any(word in query_lower for word in ["when possible", "low priority", "sometime"]):
            return "low"
        else:
            return "medium"
    
    def _extract_additional_context(self, query: str) -> Dict[str, Any]:
        """Extract additional context from query."""
        context = {}
        
        # Look for specific compliance frameworks
        frameworks = ["gdpr", "sox", "ccpa", "hipaa", "pci"]
        mentioned_frameworks = []
        for framework in frameworks:
            if framework in query.lower():
                mentioned_frameworks.append(framework.upper())
        
        if mentioned_frameworks:
            context["frameworks"] = mentioned_frameworks
        
        # Look for specific requirements
        if "contract" in query.lower():
            context["document_type"] = "contract"
        elif "policy" in query.lower():
            context["document_type"] = "policy"
        elif "agreement" in query.lower():
            context["document_type"] = "agreement"
        
        return context
    
    async def fetch_document_from_google_drive(
        self, 
        document_name: str, 
        team_context: str
    ) -> DocumentFetchResult:
        """
        Fetch document from Google Drive using Le Chat's connector.
        
        Args:
            document_name: Name of the document to fetch
            team_context: Team context for the request
            
        Returns:
            Document fetch result
        """
        logger.info(f"Fetching document from Google Drive: {document_name}")
        
        try:
            # In a real implementation, this would use Le Chat's Google Drive connector
            # For now, we'll simulate the fetch process
            await asyncio.sleep(0.5)  # Simulate network delay
            
            # Mock document content based on document name
            mock_content = self._generate_mock_document_content(document_name, team_context)
            
            result = DocumentFetchResult(
                document_id=f"gdrive_{int(asyncio.get_event_loop().time())}",
                document_name=document_name,
                content=mock_content,
                mime_type="application/pdf",
                size=len(mock_content.encode('utf-8')),
                fetch_timestamp=datetime.utcnow().isoformat(),
                success=True
            )
            
            logger.info(f"Successfully fetched document: {document_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch document: {e}")
            return DocumentFetchResult(
                document_id="",
                document_name=document_name,
                content="",
                mime_type="",
                size=0,
                fetch_timestamp=datetime.utcnow().isoformat(),
                success=False,
                error_message=str(e)
            )
    
    def _generate_mock_document_content(self, document_name: str, team_context: str) -> str:
        """Generate mock document content for testing."""
        if "vendor" in document_name.lower() or "procurement" in team_context.lower():
            return """
            VENDOR AGREEMENT
            
            This Vendor Agreement ("Agreement") is entered into between Company and Vendor.
            
            DATA PROCESSING:
            Vendor may process personal data in accordance with applicable data protection laws.
            Data retention period: 7 years from contract termination.
            
            PAYMENT TERMS:
            Net 60 payment terms apply to all invoices.
            
            CONFIDENTIALITY:
            Both parties agree to maintain confidentiality of proprietary information.
            
            TERMINATION:
            Either party may terminate with 30 days written notice.
            """
        elif "sales" in team_context.lower():
            return """
            SALES AGREEMENT
            
            This Sales Agreement governs the sale of products/services.
            
            DATA COLLECTION:
            We collect customer information for order processing and marketing.
            Customers may opt-out of marketing communications.
            
            PAYMENT TERMS:
            Payment due within 30 days of invoice date.
            
            LIABILITY:
            Our liability is limited to the purchase price of the product.
            """
        else:
            return """
            SERVICE AGREEMENT
            
            This Service Agreement outlines the terms of service provision.
            
            DATA PROTECTION:
            Personal data will be processed in compliance with GDPR.
            Data subjects have the right to access, rectify, and delete their data.
            
            CONFIDENTIALITY:
            All confidential information must be protected.
            
            COMPLIANCE:
            Both parties must comply with applicable laws and regulations.
            """
    
    async def format_response_for_lechat(
        self, 
        analysis_results: Dict[str, Any], 
        team_context: str
    ) -> str:
        """
        Format analysis results for display in Le Chat.
        
        Args:
            analysis_results: Results from compliance analysis
            team_context: Team context for personalization
            
        Returns:
            Formatted response for Le Chat
        """
        logger.info(f"Formatting response for Le Chat - team: {team_context}")
        
        # Extract key information
        status = analysis_results.get("overall_status", "unknown")
        risk_level = analysis_results.get("risk_level", "unknown")
        risk_score = analysis_results.get("risk_score", 0.0)
        issues = analysis_results.get("issues", [])
        missing_clauses = analysis_results.get("missing_clauses", [])
        
        # Format response
        response = f"🔍 **Compliance Analysis Complete**\n\n"
        response += f"**Team:** {team_context}\n"
        response += f"**Status:** {status.upper()}\n"
        response += f"**Risk Level:** {risk_level.upper()}\n"
        response += f"**Risk Score:** {risk_score:.2f}/1.0\n\n"
        
        if issues:
            response += f"**Issues Found:** {len(issues)}\n"
            for i, issue in enumerate(issues[:3], 1):  # Show first 3 issues
                response += f"{i}. **{issue.get('severity', 'unknown').upper()}:** {issue.get('description', 'No description')}\n"
            
            if len(issues) > 3:
                response += f"... and {len(issues) - 3} more issues\n"
        
        if missing_clauses:
            response += f"\n**Missing Clauses:** {len(missing_clauses)}\n"
            for clause in missing_clauses[:3]:  # Show first 3 missing clauses
                response += f"• {clause}\n"
        
        # Add team-specific recommendations
        if "procurement" in team_context.lower():
            response += "\n**Procurement Team Recommendations:**\n"
            response += "• Review payment terms for compliance\n"
            response += "• Check vendor data processing agreements\n"
        elif "sales" in team_context.lower():
            response += "\n**Sales Team Recommendations:**\n"
            response += "• Verify customer data collection notices\n"
            response += "• Check marketing consent mechanisms\n"
        
        return response
    
    async def generate_learning_prompt(
        self, 
        analysis_results: Dict[str, Any], 
        team_context: str
    ) -> str:
        """
        Generate a prompt for user learning and feedback.
        
        Args:
            analysis_results: Results from compliance analysis
            team_context: Team context for personalization
            
        Returns:
            Learning prompt for the user
        """
        issues = analysis_results.get("issues", [])
        missing_clauses = analysis_results.get("missing_clauses", [])
        
        prompt = "🤖 **Learning Opportunity**\n\n"
        prompt += f"Based on this analysis for {team_context}, I can help you learn from this experience:\n\n"
        
        if issues:
            prompt += "**Issues Found:**\n"
            for issue in issues[:2]:  # Show first 2 issues
                prompt += f"• {issue.get('description', 'No description')}\n"
        
        if missing_clauses:
            prompt += "\n**Missing Clauses:**\n"
            for clause in missing_clauses[:2]:  # Show first 2 missing clauses
                prompt += f"• {clause}\n"
        
        prompt += "\n**Would you like to:**\n"
        prompt += "1. Add a new pitfall pattern to watch for?\n"
        prompt += "2. Add a new compliance rule for your team?\n"
        prompt += "3. Update your team's risk tolerance?\n"
        prompt += "4. Just continue with the analysis\n\n"
        prompt += "Please respond with your choice (1-4) or describe what you'd like to add."
        
        return prompt
    
    async def process_user_feedback(
        self, 
        feedback: str, 
        team_context: str
    ) -> Dict[str, Any]:
        """
        Process user feedback for learning.
        
        Args:
            feedback: User feedback text
            team_context: Team context
            
        Returns:
            Processed feedback for memory update
        """
        logger.info(f"Processing user feedback for team: {team_context}")
        
        processed_feedback = {
            "team_id": team_context,
            "add_pitfall": False,
            "add_rule": False,
            "pitfall_description": "",
            "rule_description": "",
            "update_risk_tolerance": False,
            "new_risk_tolerance": None
        }
        
        feedback_lower = feedback.lower()
        
        # Check for pitfall addition
        if any(word in feedback_lower for word in ["pitfall", "watch for", "pattern", "issue"]):
            processed_feedback["add_pitfall"] = True
            processed_feedback["pitfall_description"] = feedback
        
        # Check for rule addition
        if any(word in feedback_lower for word in ["rule", "always check", "compliance", "requirement"]):
            processed_feedback["add_rule"] = True
            processed_feedback["rule_description"] = feedback
        
        # Check for risk tolerance update
        if any(word in feedback_lower for word in ["risk", "tolerance", "conservative", "aggressive"]):
            processed_feedback["update_risk_tolerance"] = True
            if "low" in feedback_lower or "conservative" in feedback_lower:
                processed_feedback["new_risk_tolerance"] = "low"
            elif "high" in feedback_lower or "aggressive" in feedback_lower:
                processed_feedback["new_risk_tolerance"] = "high"
            else:
                processed_feedback["new_risk_tolerance"] = "medium"
        
        return processed_feedback
