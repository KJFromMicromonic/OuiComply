"""
SOX (Sarbanes-Oxley Act) Compliance Analyzer.

This module provides specialized analysis for SOX compliance requirements
including internal controls, financial reporting, audit requirements, and more.
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import asyncio


class SOXAnalyzer:
    """
    Analyzer for SOX (Sarbanes-Oxley Act) compliance requirements.
    
    Provides comprehensive analysis of documents for SOX compliance including:
    - Internal Controls over Financial Reporting (ICFR)
    - Management assessment and certification
    - Audit committee requirements
    - Financial disclosure controls
    - Whistleblower protections
    """
    
    def __init__(self):
        """Initialize SOX analyzer with compliance patterns."""
        
        # SOX Section 302 - Corporate Responsibility for Financial Reports
        self.section_302_elements = {
            "ceo_certification": ["ceo", "chief executive", "principal executive officer"],
            "cfo_certification": ["cfo", "chief financial", "principal financial officer"],
            "financial_statements": ["financial statements", "quarterly report", "annual report"],
            "disclosure_controls": ["disclosure controls", "procedures", "material information"],
            "internal_controls": ["internal controls", "icfr", "financial reporting controls"],
            "material_weaknesses": ["material weakness", "significant deficiency", "control deficiency"]
        }
        
        # SOX Section 404 - Management Assessment of Internal Controls
        self.section_404_elements = {
            "management_assessment": ["management assessment", "internal control assessment"],
            "icfr_effectiveness": ["effectiveness", "adequate", "operating effectively"],
            "control_framework": ["coso", "framework", "control framework"],
            "auditor_attestation": ["auditor", "attestation", "independent auditor"],
            "material_weakness_disclosure": ["material weakness", "remediation", "corrective action"],
            "documentation": ["documentation", "policies", "procedures", "evidence"]
        }
        
        # SOX Section 409 - Real Time Issuer Disclosures
        self.section_409_elements = {
            "material_changes": ["material change", "financial condition", "results of operations"],
            "rapid_disclosure": ["rapid", "current", "immediate disclosure"],
            "form_8k": ["form 8-k", "current report", "material agreement"],
            "plain_english": ["plain english", "understandable", "clear language"]
        }
        
        # SOX Section 806 - Whistleblower Protection
        self.whistleblower_elements = {
            "reporting_mechanism": ["hotline", "reporting", "anonymous", "complaint"],
            "retaliation_protection": ["retaliation", "protection", "adverse action"],
            "investigation_procedures": ["investigation", "review", "follow-up"],
            "confidentiality": ["confidential", "anonymous", "identity protection"]
        }
        
        # SOX Audit Committee Requirements (Section 301)
        self.audit_committee_elements = {
            "independence": ["independent", "non-employee", "outside director"],
            "financial_expert": ["financial expert", "accounting", "financial literacy"],
            "oversight_responsibilities": ["oversight", "external auditor", "internal audit"],
            "complaint_procedures": ["complaints", "accounting", "auditing matters"],
            "authority": ["authority", "resources", "advisors", "consultants"]
        }
        
        # Internal Controls Framework Elements
        self.internal_controls_elements = {
            "control_environment": ["control environment", "tone at the top", "integrity"],
            "risk_assessment": ["risk assessment", "identify risks", "fraud risk"],
            "control_activities": ["control activities", "policies", "procedures"],
            "information_communication": ["information", "communication", "reporting"],
            "monitoring": ["monitoring", "ongoing", "separate evaluations"],
            "entity_level_controls": ["entity level", "company level", "organization wide"],
            "process_level_controls": ["process level", "transaction level", "application controls"],
            "it_general_controls": ["it controls", "system access", "change management"]
        }
        
        # Financial Reporting Elements
        self.financial_reporting_elements = {
            "revenue_recognition": ["revenue", "recognition", "sales", "income"],
            "expense_accruals": ["expenses", "accruals", "liabilities", "provisions"],
            "asset_valuation": ["assets", "valuation", "impairment", "fair value"],
            "consolidation": ["consolidation", "subsidiaries", "intercompany"],
            "related_party": ["related party", "transactions", "disclosure"],
            "estimates_judgments": ["estimates", "judgments", "assumptions", "critical accounting"]
        }
    
    def analyze_compliance(self, document_text: str, use_mistral: bool = True) -> Dict[str, Any]:
        """
        Analyze document for SOX compliance with optional Mistral AI enhancement.
        
        Args:
            document_text: Text content to analyze
            use_mistral: Whether to use Mistral AI for enhanced analysis
            
        Returns:
            Comprehensive SOX compliance analysis
        """
        document_lower = document_text.lower()
        
        # Perform traditional keyword-based analysis
        section_302_analysis = self._analyze_section_elements(document_lower, self.section_302_elements, "Section 302")
        section_404_analysis = self._analyze_section_elements(document_lower, self.section_404_elements, "Section 404")
        section_409_analysis = self._analyze_section_elements(document_lower, self.section_409_elements, "Section 409")
        whistleblower_analysis = self._analyze_section_elements(document_lower, self.whistleblower_elements, "Whistleblower")
        audit_committee_analysis = self._analyze_section_elements(document_lower, self.audit_committee_elements, "Audit Committee")
        internal_controls_analysis = self._analyze_internal_controls(document_lower)
        financial_reporting_analysis = self._analyze_financial_reporting(document_lower)
        
        # Calculate baseline compliance score
        compliance_score = self._calculate_sox_compliance_score(
            section_302_analysis, section_404_analysis, section_409_analysis,
            whistleblower_analysis, audit_committee_analysis, internal_controls_analysis
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(compliance_score)
        
        # Generate recommendations
        recommendations = self._generate_sox_recommendations(
            section_302_analysis, section_404_analysis, section_409_analysis,
            whistleblower_analysis, audit_committee_analysis, internal_controls_analysis
        )
        
        # Base analysis result
        result = {
            "framework": "SOX",
            "compliance_score": compliance_score,
            "risk_level": risk_level,
            "section_302_analysis": section_302_analysis,
            "section_404_analysis": section_404_analysis,
            "section_409_analysis": section_409_analysis,
            "whistleblower_analysis": whistleblower_analysis,
            "audit_committee_analysis": audit_committee_analysis,
            "internal_controls_analysis": internal_controls_analysis,
            "financial_reporting_analysis": financial_reporting_analysis,
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
                    mistral_analyzer.analyze_document_with_mistral(document_text, "sox")
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
                        ))[:12]  # Limit to top 12 for SOX
                    
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
    
    def _analyze_section_elements(self, document_lower: str, elements: Dict[str, List[str]], section_name: str) -> Dict[str, Any]:
        """Analyze elements for a specific SOX section."""
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
            "section": section_name,
            "found_elements": found_elements,
            "element_details": element_details,
            "coverage": coverage,
            "total_elements_found": len(found_elements),
            "missing_elements": [element for element in elements.keys() if element not in found_elements]
        }
    
    def _analyze_internal_controls(self, document_lower: str) -> Dict[str, Any]:
        """Analyze internal controls framework elements."""
        found_controls = []
        control_details = {}
        
        for control, keywords in self.internal_controls_elements.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_controls.append(control)
                control_details[control] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        controls_coverage = len(found_controls) / len(self.internal_controls_elements)
        
        # Assess COSO framework alignment
        coso_alignment = self._assess_coso_alignment(found_controls)
        
        return {
            "found_controls": found_controls,
            "control_details": control_details,
            "controls_coverage": controls_coverage,
            "coso_alignment": coso_alignment,
            "total_controls_found": len(found_controls),
            "missing_controls": [control for control in self.internal_controls_elements.keys() 
                               if control not in found_controls]
        }
    
    def _analyze_financial_reporting(self, document_lower: str) -> Dict[str, Any]:
        """Analyze financial reporting elements."""
        found_elements = []
        element_details = {}
        
        for element, keywords in self.financial_reporting_elements.items():
            matches = sum(1 for keyword in keywords if keyword in document_lower)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                found_elements.append(element)
                element_details[element] = {
                    "confidence": confidence,
                    "matches": matches,
                    "total_keywords": len(keywords)
                }
        
        reporting_coverage = len(found_elements) / len(self.financial_reporting_elements)
        
        return {
            "found_elements": found_elements,
            "element_details": element_details,
            "reporting_coverage": reporting_coverage,
            "total_elements_found": len(found_elements),
            "missing_elements": [element for element in self.financial_reporting_elements.keys() 
                               if element not in found_elements]
        }
    
    def _assess_coso_alignment(self, found_controls: List[str]) -> Dict[str, Any]:
        """Assess alignment with COSO Internal Control Framework."""
        coso_components = {
            "control_environment": ["control_environment"],
            "risk_assessment": ["risk_assessment"],
            "control_activities": ["control_activities"],
            "information_communication": ["information_communication"],
            "monitoring": ["monitoring"]
        }
        
        aligned_components = []
        for component, required_controls in coso_components.items():
            if any(control in found_controls for control in required_controls):
                aligned_components.append(component)
        
        alignment_score = len(aligned_components) / len(coso_components)
        
        return {
            "aligned_components": aligned_components,
            "alignment_score": alignment_score,
            "missing_components": [comp for comp in coso_components.keys() 
                                 if comp not in aligned_components]
        }
    
    def _calculate_sox_compliance_score(self, section_302: Dict, section_404: Dict, 
                                      section_409: Dict, whistleblower: Dict, 
                                      audit_committee: Dict, internal_controls: Dict) -> float:
        """Calculate overall SOX compliance score."""
        # Weight different sections based on importance
        weights = {
            "section_302": 0.25,  # CEO/CFO Certification
            "section_404": 0.30,  # Internal Controls Assessment
            "section_409": 0.15,  # Real-time Disclosure
            "whistleblower": 0.10,  # Whistleblower Protection
            "audit_committee": 0.10,  # Audit Committee
            "internal_controls": 0.10   # Internal Controls Framework
        }
        
        scores = {
            "section_302": section_302["coverage"],
            "section_404": section_404["coverage"],
            "section_409": section_409["coverage"],
            "whistleblower": whistleblower["coverage"],
            "audit_committee": audit_committee["coverage"],
            "internal_controls": internal_controls["controls_coverage"]
        }
        
        # Calculate weighted average
        overall_score = sum(scores[section] * weights[section] for section in weights.keys())
        
        return min(overall_score, 1.0)
    
    def _determine_risk_level(self, compliance_score: float) -> str:
        """Determine risk level based on SOX compliance score."""
        if compliance_score >= 0.85:
            return "LOW"
        elif compliance_score >= 0.70:
            return "MEDIUM"
        elif compliance_score >= 0.50:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _generate_sox_recommendations(self, section_302: Dict, section_404: Dict,
                                    section_409: Dict, whistleblower: Dict,
                                    audit_committee: Dict, internal_controls: Dict) -> List[str]:
        """Generate SOX compliance recommendations."""
        recommendations = []
        
        # Section 302 recommendations
        if section_302["coverage"] < 0.7:
            missing = section_302["missing_elements"]
            if "ceo_certification" in missing:
                recommendations.append("Implement CEO certification process for financial reports (Section 302)")
            if "cfo_certification" in missing:
                recommendations.append("Implement CFO certification process for financial reports (Section 302)")
            if "disclosure_controls" in missing:
                recommendations.append("Establish disclosure controls and procedures")
        
        # Section 404 recommendations
        if section_404["coverage"] < 0.7:
            missing = section_404["missing_elements"]
            if "management_assessment" in missing:
                recommendations.append("Conduct management assessment of internal controls (Section 404)")
            if "auditor_attestation" in missing:
                recommendations.append("Obtain independent auditor attestation on internal controls")
            if "documentation" in missing:
                recommendations.append("Document internal control policies and procedures")
        
        # Internal controls recommendations
        if internal_controls["controls_coverage"] < 0.6:
            missing = internal_controls["missing_controls"]
            if "control_environment" in missing:
                recommendations.append("Strengthen control environment and tone at the top")
            if "risk_assessment" in missing:
                recommendations.append("Implement comprehensive risk assessment process")
            if "monitoring" in missing:
                recommendations.append("Establish ongoing monitoring of internal controls")
        
        # Whistleblower recommendations
        if whistleblower["coverage"] < 0.5:
            recommendations.append("Establish anonymous reporting hotline for financial misconduct")
            recommendations.append("Implement whistleblower protection policies")
        
        # Audit committee recommendations
        if audit_committee["coverage"] < 0.6:
            recommendations.append("Ensure audit committee independence and financial expertise")
            recommendations.append("Establish audit committee oversight procedures")
        
        # COSO framework recommendations
        if internal_controls.get("coso_alignment", {}).get("alignment_score", 0) < 0.8:
            recommendations.append("Align internal controls with COSO framework")
        
        # General recommendations
        if section_302["coverage"] < 0.5 and section_404["coverage"] < 0.5:
            recommendations.append("Conduct comprehensive SOX compliance assessment")
        
        return recommendations[:12]  # Limit to top 12 recommendations
    
    def get_sox_compliance_checklist(self) -> Dict[str, List[str]]:
        """Get SOX compliance checklist."""
        return {
            "section_302": [
                "CEO certification of financial reports",
                "CFO certification of financial reports", 
                "Disclosure controls and procedures",
                "Internal controls over financial reporting",
                "Material weakness identification and disclosure"
            ],
            "section_404": [
                "Management assessment of internal controls",
                "Documentation of internal control framework",
                "Testing of control effectiveness",
                "Independent auditor attestation",
                "Material weakness remediation"
            ],
            "section_409": [
                "Real-time disclosure of material changes",
                "Form 8-K filing procedures",
                "Plain English disclosure requirements",
                "Rapid and current information dissemination"
            ],
            "whistleblower_protection": [
                "Anonymous reporting mechanisms",
                "Retaliation protection policies",
                "Investigation procedures",
                "Confidentiality safeguards"
            ],
            "audit_committee": [
                "Independent audit committee members",
                "Financial expertise requirements",
                "Oversight of external auditors",
                "Complaint handling procedures",
                "Authority and resources"
            ],
            "internal_controls": [
                "Control environment establishment",
                "Risk assessment processes",
                "Control activities implementation",
                "Information and communication systems",
                "Monitoring activities"
            ]
        }
