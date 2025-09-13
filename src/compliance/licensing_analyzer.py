"""
Licensing Clause Analyzer.

This module provides specialized analysis for licensing agreements and clauses
including license grants, restrictions, intellectual property, and terms.
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import asyncio


class LicensingAnalyzer:
    """
    Analyzer for licensing agreements and clauses.
    
    Provides comprehensive analysis of documents for licensing compliance including:
    - License grant scope and limitations
    - Intellectual property ownership and assignment
    - Usage restrictions and permissions
    - Termination conditions and effects
    - Royalty and payment terms
    """
    
    def __init__(self):
        """Initialize licensing analyzer with clause patterns."""
        
        # License grant elements
        self.license_grant_elements = {
            "grant_clause": ["grant", "license", "hereby grants", "permission"],
            "scope_definition": ["scope", "field of use", "territory", "application"],
            "exclusivity": ["exclusive", "non-exclusive", "sole", "limited"],
            "transferability": ["transfer", "assign", "sublicense", "delegate"],
            "revocability": ["revocable", "irrevocable", "terminate", "cancel"],
            "duration": ["term", "duration", "period", "expiry", "perpetual"]
        }
        
        # Intellectual property elements
        self.ip_elements = {
            "ownership": ["ownership", "title", "proprietor", "belongs to"],
            "copyright": ["copyright", "author", "work", "expression"],
            "patent": ["patent", "invention", "claims", "patent rights"],
            "trademark": ["trademark", "service mark", "brand", "logo"],
            "trade_secret": ["trade secret", "confidential", "proprietary"],
            "moral_rights": ["moral rights", "attribution", "integrity"],
            "derivative_works": ["derivative", "modification", "adaptation", "enhancement"],
            "improvements": ["improvements", "enhancements", "developments", "upgrades"]
        }
        
        # Usage restrictions and permissions
        self.usage_elements = {
            "permitted_uses": ["permitted", "allowed", "authorized", "may use"],
            "prohibited_uses": ["prohibited", "forbidden", "not permitted", "shall not"],
            "commercial_use": ["commercial", "business", "profit", "revenue"],
            "personal_use": ["personal", "individual", "non-commercial", "private"],
            "modification_rights": ["modify", "alter", "change", "customize"],
            "distribution_rights": ["distribute", "share", "publish", "disseminate"],
            "reproduction_rights": ["reproduce", "copy", "duplicate", "replicate"],
            "public_performance": ["perform", "display", "broadcast", "exhibit"]
        }
        
        # Termination and breach elements
        self.termination_elements = {
            "termination_triggers": ["breach", "violation", "default", "failure"],
            "notice_requirements": ["notice", "notification", "written notice", "days notice"],
            "cure_period": ["cure", "remedy", "correct", "grace period"],
            "effect_of_termination": ["upon termination", "effect", "consequences", "survival"],
            "return_obligations": ["return", "destroy", "cease use", "discontinue"],
            "survival_clauses": ["survive", "remain in effect", "continue", "persist"]
        }
        
        # Financial terms
        self.financial_elements = {
            "royalties": ["royalty", "royalties", "percentage", "revenue share"],
            "license_fees": ["license fee", "payment", "consideration", "compensation"],
            "minimum_payments": ["minimum", "guaranteed", "advance", "upfront"],
            "payment_schedule": ["payment schedule", "quarterly", "annually", "monthly"],
            "audit_rights": ["audit", "inspect", "examine records", "verification"],
            "currency": ["currency", "dollars", "euros", "exchange rate"],
            "taxes": ["taxes", "withholding", "vat", "duties"],
            "late_fees": ["late fee", "penalty", "interest", "overdue"]
        }
        
        # Compliance and legal elements
        self.compliance_elements = {
            "governing_law": ["governed by", "governing law", "jurisdiction", "applicable law"],
            "dispute_resolution": ["dispute", "arbitration", "mediation", "litigation"],
            "indemnification": ["indemnify", "hold harmless", "defend", "liability"],
            "warranties": ["warranty", "represent", "guarantee", "assure"],
            "disclaimers": ["disclaim", "as is", "no warranty", "exclude"],
            "limitation_of_liability": ["limit", "liability", "damages", "consequential"],
            "force_majeure": ["force majeure", "act of god", "unforeseeable", "beyond control"],
            "compliance_laws": ["comply", "applicable laws", "regulations", "standards"]
        }
        
        # License types and models
        self.license_types = {
            "open_source": ["open source", "gpl", "mit", "apache", "bsd", "creative commons"],
            "proprietary": ["proprietary", "commercial", "closed source", "private"],
            "copyleft": ["copyleft", "share-alike", "viral", "reciprocal"],
            "permissive": ["permissive", "liberal", "minimal restrictions"],
            "dual_license": ["dual license", "alternative", "choice of license"],
            "subscription": ["subscription", "saas", "service", "recurring"],
            "perpetual": ["perpetual", "permanent", "indefinite", "forever"],
            "evaluation": ["evaluation", "trial", "demo", "test"]
        }
    
    def analyze_compliance(self, document_text: str, use_mistral: bool = True) -> Dict[str, Any]:
        """
        Analyze document for licensing compliance and clause coverage with optional Mistral AI enhancement.
        
        Args:
            document_text: Text content to analyze
            use_mistral: Whether to use Mistral AI for enhanced analysis
            
        Returns:
            Comprehensive licensing analysis
        """
        document_lower = document_text.lower()
        
        # Perform traditional keyword-based analysis
        grant_analysis = self._analyze_license_grant(document_lower)
        ip_analysis = self._analyze_ip_elements(document_lower)
        usage_analysis = self._analyze_usage_elements(document_lower)
        termination_analysis = self._analyze_termination_elements(document_lower)
        financial_analysis = self._analyze_financial_elements(document_lower)
        compliance_analysis = self._analyze_compliance_elements(document_lower)
        license_type_analysis = self._analyze_license_types(document_lower)
        
        # Calculate baseline licensing score
        licensing_score = self._calculate_licensing_score(
            grant_analysis, ip_analysis, usage_analysis, 
            termination_analysis, financial_analysis, compliance_analysis
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(licensing_score)
        
        # Generate recommendations
        recommendations = self._generate_licensing_recommendations(
            grant_analysis, ip_analysis, usage_analysis,
            termination_analysis, financial_analysis, compliance_analysis
        )
        
        # Base analysis result
        result = {
            "framework": "Licensing",
            "licensing_score": licensing_score,
            "risk_level": risk_level,
            "license_grant_analysis": grant_analysis,
            "ip_analysis": ip_analysis,
            "usage_analysis": usage_analysis,
            "termination_analysis": termination_analysis,
            "financial_analysis": financial_analysis,
            "compliance_analysis": compliance_analysis,
            "license_type_analysis": license_type_analysis,
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
                    mistral_analyzer.analyze_document_with_mistral(document_text, "licensing")
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
                            licensing_score * 0.4
                        )
                        result["licensing_score"] = combined_score
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
                    result["risk_level"] = self._determine_risk_level(result["licensing_score"])
                
            except Exception as e:
                # Fallback to traditional analysis if Mistral fails
                result["mistral_error"] = str(e)
                result["analysis_method"] = "keyword_based_fallback"
        
        return result
    
    def _analyze_license_grant(self, document_lower: str) -> Dict[str, Any]:
        """Analyze license grant elements."""
        return self._analyze_element_category(document_lower, self.license_grant_elements, "License Grant")
    
    def _analyze_ip_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze intellectual property elements."""
        return self._analyze_element_category(document_lower, self.ip_elements, "Intellectual Property")
    
    def _analyze_usage_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze usage restrictions and permissions."""
        return self._analyze_element_category(document_lower, self.usage_elements, "Usage Rights")
    
    def _analyze_termination_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze termination and breach elements."""
        return self._analyze_element_category(document_lower, self.termination_elements, "Termination")
    
    def _analyze_financial_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze financial terms and obligations."""
        return self._analyze_element_category(document_lower, self.financial_elements, "Financial Terms")
    
    def _analyze_compliance_elements(self, document_lower: str) -> Dict[str, Any]:
        """Analyze compliance and legal elements."""
        return self._analyze_element_category(document_lower, self.compliance_elements, "Legal Compliance")
    
    def _analyze_license_types(self, document_lower: str) -> Dict[str, Any]:
        """Analyze license types and models."""
        found_types = []
        type_details = {}
        
        for license_type, keywords in self.license_types.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_types.append(license_type)
                type_details[license_type] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        # Determine primary license type
        primary_type = None
        if type_details:
            primary_type = max(type_details.keys(), key=lambda x: type_details[x]["confidence"])
        
        return {
            "found_types": found_types,
            "type_details": type_details,
            "primary_type": primary_type,
            "total_types_found": len(found_types),
            "is_open_source": "open_source" in found_types,
            "is_proprietary": "proprietary" in found_types,
            "has_copyleft": "copyleft" in found_types
        }
    
    def _analyze_element_category(self, document_lower: str, elements: Dict[str, List[str]], category_name: str) -> Dict[str, Any]:
        """Generic method to analyze element categories."""
        found_elements = []
        element_details = {}
        
        for element, keywords in elements.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_elements.append(element)
                element_details[element] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        coverage = len(found_elements) / len(elements)
        
        return {
            "category": category_name,
            "found_elements": found_elements,
            "element_details": element_details,
            "coverage": coverage,
            "total_elements_found": len(found_elements),
            "missing_elements": [element for element in elements.keys() if element not in found_elements]
        }
    
    def _calculate_licensing_score(self, grant: Dict, ip: Dict, usage: Dict,
                                 termination: Dict, financial: Dict, compliance: Dict) -> float:
        """Calculate overall licensing compliance score."""
        # Weight different aspects of licensing
        weights = {
            "grant": 0.25,      # License grant is fundamental
            "ip": 0.20,         # IP ownership and rights
            "usage": 0.20,      # Usage rights and restrictions
            "termination": 0.15, # Termination conditions
            "financial": 0.10,   # Financial terms
            "compliance": 0.10   # Legal compliance
        }
        
        scores = {
            "grant": grant["coverage"],
            "ip": ip["coverage"],
            "usage": usage["coverage"],
            "termination": termination["coverage"],
            "financial": financial["coverage"],
            "compliance": compliance["coverage"]
        }
        
        # Calculate weighted average
        overall_score = sum(scores[aspect] * weights[aspect] for aspect in weights.keys())
        
        return min(overall_score, 1.0)
    
    def _determine_risk_level(self, licensing_score: float) -> str:
        """Determine risk level based on licensing score."""
        if licensing_score >= 0.80:
            return "LOW"
        elif licensing_score >= 0.60:
            return "MEDIUM"
        elif licensing_score >= 0.40:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_licensing_recommendations(self, grant: Dict, ip: Dict, usage: Dict,
                                          termination: Dict, financial: Dict, compliance: Dict) -> List[str]:
        """Generate licensing compliance recommendations."""
        recommendations = []
        
        # License grant recommendations
        if grant["coverage"] < 0.7:
            missing = grant["missing_elements"]
            if "grant_clause" in missing:
                recommendations.append("Include clear license grant clause defining rights granted")
            if "scope_definition" in missing:
                recommendations.append("Define scope of license including field of use and territory")
            if "exclusivity" in missing:
                recommendations.append("Specify whether license is exclusive or non-exclusive")
            if "duration" in missing:
                recommendations.append("Define license term and duration")
        
        # IP recommendations
        if ip["coverage"] < 0.6:
            missing = ip["missing_elements"]
            if "ownership" in missing:
                recommendations.append("Clarify intellectual property ownership and title")
            if "derivative_works" in missing:
                recommendations.append("Address rights to derivative works and modifications")
            if "improvements" in missing:
                recommendations.append("Define ownership of improvements and enhancements")
        
        # Usage recommendations
        if usage["coverage"] < 0.6:
            missing = usage["missing_elements"]
            if "permitted_uses" in missing:
                recommendations.append("Clearly define permitted uses and applications")
            if "prohibited_uses" in missing:
                recommendations.append("Specify prohibited uses and restrictions")
            if "commercial_use" in missing:
                recommendations.append("Address commercial use rights and limitations")
        
        # Termination recommendations
        if termination["coverage"] < 0.5:
            missing = termination["missing_elements"]
            if "termination_triggers" in missing:
                recommendations.append("Define termination triggers and breach conditions")
            if "notice_requirements" in missing:
                recommendations.append("Specify notice requirements for termination")
            if "effect_of_termination" in missing:
                recommendations.append("Clarify effects and consequences of termination")
        
        # Financial recommendations
        if financial["coverage"] < 0.4:
            missing = financial["missing_elements"]
            if "royalties" in missing and "license_fees" in missing:
                recommendations.append("Define payment terms, royalties, or license fees")
            if "audit_rights" in missing:
                recommendations.append("Include audit rights for financial verification")
        
        # Compliance recommendations
        if compliance["coverage"] < 0.6:
            missing = compliance["missing_elements"]
            if "governing_law" in missing:
                recommendations.append("Specify governing law and jurisdiction")
            if "dispute_resolution" in missing:
                recommendations.append("Include dispute resolution mechanisms")
            if "limitation_of_liability" in missing:
                recommendations.append("Address limitation of liability and damages")
        
        # General recommendations
        if grant["coverage"] < 0.5 and ip["coverage"] < 0.5:
            recommendations.append("Conduct comprehensive licensing agreement review")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def get_licensing_checklist(self) -> Dict[str, List[str]]:
        """Get licensing compliance checklist."""
        return {
            "license_grant": [
                "Clear license grant clause",
                "Scope and field of use definition",
                "Exclusivity specification",
                "Transferability and sublicensing rights",
                "License duration and term"
            ],
            "intellectual_property": [
                "IP ownership clarification",
                "Copyright and patent rights",
                "Derivative works ownership",
                "Improvements and enhancements",
                "Moral rights and attribution"
            ],
            "usage_rights": [
                "Permitted uses definition",
                "Prohibited uses specification",
                "Commercial vs personal use",
                "Modification rights",
                "Distribution and reproduction rights"
            ],
            "termination": [
                "Termination triggers and conditions",
                "Notice requirements",
                "Cure periods for breaches",
                "Effects of termination",
                "Survival of obligations"
            ],
            "financial_terms": [
                "Royalty rates and calculations",
                "License fees and payments",
                "Payment schedules",
                "Audit rights and procedures",
                "Currency and tax provisions"
            ],
            "legal_compliance": [
                "Governing law specification",
                "Dispute resolution procedures",
                "Indemnification provisions",
                "Warranty and disclaimer clauses",
                "Limitation of liability"
            ]
        }
    
    def identify_license_type(self, document_text: str) -> Dict[str, Any]:
        """
        Identify the type of license based on document content.
        
        Args:
            document_text: Text content to analyze
            
        Returns:
            License type identification and characteristics
        """
        document_lower = document_text.lower()
        type_analysis = self._analyze_license_types(document_lower)
        
        # Additional analysis for specific license characteristics
        characteristics = {
            "has_source_code_requirements": any(term in document_lower for term in 
                ["source code", "source form", "preferred form"]),
            "has_attribution_requirements": any(term in document_lower for term in 
                ["attribution", "credit", "acknowledge", "copyright notice"]),
            "has_share_alike": any(term in document_lower for term in 
                ["share-alike", "copyleft", "same license", "derivative works"]),
            "allows_commercial_use": any(term in document_lower for term in 
                ["commercial", "business", "profit", "revenue"]) and 
                not any(term in document_lower for term in ["non-commercial", "not for profit"]),
            "allows_modification": any(term in document_lower for term in 
                ["modify", "alter", "change", "derivative"]) and
                not any(term in document_lower for term in ["no derivatives", "noderivs"]),
            "requires_disclosure": any(term in document_lower for term in 
                ["disclose", "make available", "provide source"])
        }
        
        return {
            "license_types": type_analysis,
            "characteristics": characteristics,
            "license_family": self._determine_license_family(type_analysis, characteristics)
        }
    
    def _determine_license_family(self, type_analysis: Dict, characteristics: Dict) -> str:
        """Determine the license family based on analysis."""
        if type_analysis.get("is_open_source"):
            if characteristics.get("has_share_alike") or type_analysis.get("has_copyleft"):
                return "Copyleft Open Source"
            else:
                return "Permissive Open Source"
        elif type_analysis.get("is_proprietary"):
            return "Proprietary Commercial"
        else:
            return "Unknown/Custom"
