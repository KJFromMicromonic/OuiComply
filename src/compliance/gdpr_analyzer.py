"""
GDPR (General Data Protection Regulation) Compliance Analyzer.

This module provides specialized analysis for GDPR compliance requirements
including data subject rights, legal basis, consent mechanisms, and more.
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import asyncio


class GDPRAnalyzer:
    """
    Analyzer for GDPR compliance requirements.
    
    Provides comprehensive analysis of documents for GDPR compliance including:
    - Legal basis identification (Article 6)
    - Data subject rights verification
    - Consent mechanism analysis
    - International transfer compliance
    - Data retention policy checking
    """
    
    def __init__(self):
        """Initialize GDPR analyzer with compliance patterns."""
        
        # GDPR Article 6 legal bases
        self.legal_bases = {
            "consent": ["consent", "agree", "opt-in", "permission", "authorize"],
            "contract": ["contract", "agreement", "performance", "contractual"],
            "legal_obligation": ["legal obligation", "compliance", "regulatory", "statutory"],
            "vital_interests": ["vital interest", "life", "safety", "emergency"],
            "public_task": ["public task", "official authority", "public interest"],
            "legitimate_interest": ["legitimate interest", "business interest", "necessary"]
        }
        
        # Data subject rights under GDPR
        self.data_subject_rights = {
            "access": ["access", "obtain", "copy", "information"],
            "rectification": ["rectify", "correct", "update", "amend"],
            "erasure": ["delete", "erase", "remove", "right to be forgotten"],
            "restrict_processing": ["restrict", "limit", "suspend processing"],
            "data_portability": ["portability", "transfer", "export", "move data"],
            "object": ["object", "opt-out", "refuse", "withdraw"],
            "automated_decision": ["automated", "profiling", "algorithm", "decision making"]
        }
        
        # GDPR compliance elements
        self.compliance_elements = {
            "data_controller": ["controller", "data controller", "responsible party"],
            "data_processor": ["processor", "data processor", "third party"],
            "dpo": ["dpo", "data protection officer", "privacy officer"],
            "lawful_basis": ["lawful basis", "legal basis", "article 6"],
            "purpose_limitation": ["purpose", "specific purpose", "limited purpose"],
            "data_minimization": ["minimal", "necessary", "proportionate"],
            "accuracy": ["accurate", "up-to-date", "correct"],
            "storage_limitation": ["retention", "storage period", "delete"],
            "security": ["security", "protect", "safeguard", "encrypt"],
            "accountability": ["demonstrate", "record", "document", "evidence"],
            "privacy_by_design": ["privacy by design", "data protection by design"],
            "impact_assessment": ["dpia", "impact assessment", "privacy impact"],
            "breach_notification": ["breach", "notification", "incident", "72 hours"],
            "international_transfers": ["transfer", "third country", "adequacy", "safeguards"],
            "supervisory_authority": ["supervisory authority", "regulator", "dpa"]
        }
        
        # Special categories of personal data (Article 9)
        self.special_categories = [
            "racial", "ethnic", "political", "religious", "philosophical",
            "trade union", "genetic", "biometric", "health", "sex life", "sexual orientation"
        ]
    
    def analyze_compliance(self, document_text: str, use_mistral: bool = True) -> Dict[str, Any]:
        """
        Analyze document for GDPR compliance with optional Mistral AI enhancement.
        
        Args:
            document_text: Text content to analyze
            use_mistral: Whether to use Mistral AI for enhanced analysis
            
        Returns:
            Comprehensive GDPR compliance analysis
        """
        document_lower = document_text.lower()
        
        # Perform traditional keyword-based analysis
        legal_basis_analysis = self._analyze_legal_bases(document_lower)
        rights_analysis = self._analyze_data_subject_rights(document_lower)
        elements_analysis = self._analyze_compliance_elements(document_lower)
        special_data_analysis = self._analyze_special_categories(document_lower)
        
        # Calculate baseline compliance score
        compliance_score = self._calculate_compliance_score(
            legal_basis_analysis, rights_analysis, elements_analysis
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(compliance_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            legal_basis_analysis, rights_analysis, elements_analysis, special_data_analysis
        )
        
        # Base analysis result
        result = {
            "framework": "GDPR",
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "legal_basis_analysis": legal_basis_analysis,
            "data_subject_rights": rights_analysis,
            "compliance_elements": elements_analysis,
            "special_categories": special_data_analysis,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_method": "keyword_based"
        }
        
        # Enhance with Mistral AI if requested and available
        if use_mistral:
            try:
                # Import here to avoid circular imports
                from ..mistral_integration import get_mistral_analyzer
                mistral_analyzer = get_mistral_analyzer()
                
                # Get Mistral analysis asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mistral_result = loop.run_until_complete(
                    mistral_analyzer.analyze_document_with_mistral(document_text, "gdpr")
                )
                loop.close()
                
                if mistral_result.get("enhanced"):
                    # Combine traditional and Mistral analysis
                    mistral_analysis = mistral_result["mistral_analysis"]
                    
                    # Use Mistral's compliance score if higher confidence
                    if mistral_analysis.get("compliance_score", 0) > 0:
                        # Weighted average: 60% Mistral, 40% traditional
                        combined_score = (
                            mistral_analysis["compliance_score"] * 0.6 +
                            compliance_score * 0.4
                        )
                        result["compliance_score"] = combined_score
                        result["analysis_method"] = "mistral_enhanced"
                    
                    # Enhance recommendations with Mistral insights
                    mistral_recommendations = mistral_analysis.get("recommendations", [])
                    if mistral_recommendations:
                        result["recommendations"] = list(set(
                            recommendations + mistral_recommendations[:5]
                        ))[:10]  # Limit to top 10
                    
                    # Add Mistral-specific insights
                    result["mistral_insights"] = {
                        "detected_clauses": mistral_analysis.get("detected_clauses", []),
                        "key_findings": mistral_analysis.get("key_findings", []),
                        "missing_requirements": mistral_analysis.get("missing_requirements", []),
                        "model_used": mistral_result.get("model_used", "unknown")
                    }
                    
                    # Update risk level based on enhanced analysis
                    result["risk_level"] = self._determine_risk_level(result["compliance_score"])
                
            except Exception as e:
                # Fallback to traditional analysis if Mistral fails
                result["mistral_error"] = str(e)
                result["analysis_method"] = "keyword_based_fallback"
        
        return result
    
    def _analyze_legal_bases(self, document_lower: str) -> Dict[str, Any]:
        """Analyze legal bases under Article 6."""
        found_bases = []
        basis_details = {}
        
        for basis, keywords in self.legal_bases.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_bases.append(basis)
                basis_details[basis] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        return {
            "found_bases": found_bases,
            "basis_details": basis_details,
            "total_bases_found": len(found_bases),
            "has_explicit_basis": len(found_bases) > 0
        }
    
    def _analyze_data_subject_rights(self, document_lower: str) -> Dict[str, Any]:
        """Analyze data subject rights coverage."""
        found_rights = []
        rights_details = {}
        
        for right, keywords in self.data_subject_rights.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_rights.append(right)
                rights_details[right] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        rights_coverage = len(found_rights) / len(self.data_subject_rights)
        
        return {
            "found_rights": found_rights,
            "rights_details": rights_details,
            "rights_coverage": rights_coverage,
            "total_rights_found": len(found_rights),
            "missing_rights": [right for right in self.data_subject_rights.keys() 
                             if right not in found_rights]
        }
    
    def _analyze_compliance_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze GDPR compliance elements."""
        found_elements = []
        element_details = {}
        
        for element, keywords in self.compliance_elements.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_elements.append(element)
                element_details[element] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        elements_coverage = len(found_elements) / len(self.compliance_elements)
        
        return {
            "found_elements": found_elements,
            "element_details": element_details,
            "elements_coverage": elements_coverage,
            "total_elements_found": len(found_elements),
            "missing_elements": [element for element in self.compliance_elements.keys() 
                               if element not in found_elements]
        }
    
    def _analyze_special_categories(self, document_lower: str) -> Dict[str, Any]:
        """Analyze special categories of personal data (Article 9)."""
        found_categories = []
        
        for category in self.special_categories:
            if category in document_lower:
                found_categories.append(category)
        
        return {
            "found_special_categories": found_categories,
            "processes_special_data": len(found_categories) > 0,
            "requires_explicit_consent": len(found_categories) > 0,
            "total_special_categories": len(found_categories)
        }
    
    def _calculate_compliance_score(self, legal_basis: Dict, rights: Dict, elements: Dict) -> float:
        """Calculate overall GDPR compliance score."""
        # Weight different aspects of compliance
        basis_weight = 0.3
        rights_weight = 0.4
        elements_weight = 0.3
        
        # Legal basis score
        basis_score = 1.0 if legal_basis["has_explicit_basis"] else 0.0
        
        # Rights score
        rights_score = rights["rights_coverage"]
        
        # Elements score
        elements_score = elements["elements_coverage"]
        
        # Calculate weighted average
        overall_score = (
            basis_score * basis_weight +
            rights_score * rights_weight +
            elements_score * elements_weight
        )
        
        return min(overall_score, 1.0)
    
    def _determine_risk_level(self, compliance_score: float) -> str:
        """Determine risk level based on compliance score."""
        if compliance_score >= 0.8:
            return "LOW"
        elif compliance_score >= 0.6:
            return "MEDIUM"
        elif compliance_score >= 0.4:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_recommendations(self, legal_basis: Dict, rights: Dict, 
                                elements: Dict, special_data: Dict) -> List[str]:
        """Generate GDPR compliance recommendations."""
        recommendations = []
        
        # Legal basis recommendations
        if not legal_basis["has_explicit_basis"]:
            recommendations.append("Add explicit legal basis under GDPR Article 6")
        
        # Data subject rights recommendations
        if rights["rights_coverage"] < 0.7:
            missing_rights = rights["missing_rights"]
            if "access" in missing_rights:
                recommendations.append("Include data subject access rights (Article 15)")
            if "erasure" in missing_rights:
                recommendations.append("Add right to erasure/deletion (Article 17)")
            if "rectification" in missing_rights:
                recommendations.append("Include right to rectification (Article 16)")
        
        # Compliance elements recommendations
        missing_elements = elements["missing_elements"]
        if "dpo" in missing_elements:
            recommendations.append("Designate and provide Data Protection Officer contact")
        if "breach_notification" in missing_elements:
            recommendations.append("Include data breach notification procedures")
        if "international_transfers" in missing_elements:
            recommendations.append("Address international data transfer safeguards")
        if "impact_assessment" in missing_elements:
            recommendations.append("Consider Data Protection Impact Assessment (DPIA)")
        
        # Special categories recommendations
        if special_data["processes_special_data"]:
            recommendations.append("Ensure explicit consent for special category data (Article 9)")
            recommendations.append("Implement enhanced security measures for sensitive data")
        
        # General recommendations
        if elements["elements_coverage"] < 0.5:
            recommendations.append("Conduct comprehensive GDPR compliance review")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def get_compliance_checklist(self) -> Dict[str, List[str]]:
        """Get GDPR compliance checklist."""
        return {
            "legal_basis": [
                "Identify and document legal basis under Article 6",
                "Ensure lawful basis is appropriate for processing purpose",
                "Communicate legal basis to data subjects"
            ],
            "data_subject_rights": [
                "Implement procedures for access requests (Article 15)",
                "Enable data rectification and correction (Article 16)", 
                "Provide data erasure/deletion capability (Article 17)",
                "Allow restriction of processing (Article 18)",
                "Enable data portability (Article 20)",
                "Respect objection to processing (Article 21)"
            ],
            "compliance_elements": [
                "Designate Data Protection Officer if required",
                "Implement privacy by design principles",
                "Conduct Data Protection Impact Assessments",
                "Establish breach notification procedures",
                "Document processing activities (Article 30)",
                "Ensure adequate security measures (Article 32)"
            ],
            "international_transfers": [
                "Verify adequacy decisions for third countries",
                "Implement appropriate safeguards (Article 46)",
                "Use Standard Contractual Clauses if needed",
                "Consider Binding Corporate Rules for groups"
            ]
        }
