"""
Compliance Analysis Engine.

This module provides the core compliance checking logic, risk assessment,
and report generation capabilities for the OuiComply MCP Server.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field

from .document_ai import DocumentAIService, DocumentAnalysisRequest, DocumentAnalysisResult, ComplianceIssue

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    REQUIRES_REVIEW = "requires_review"


class MitigationAction(BaseModel):
    """
    Model representing a mitigation action for a compliance issue.
    
    Attributes:
        action_id: Unique identifier for the action
        title: Short title of the action
        description: Detailed description of what needs to be done
        priority: Priority level (low, medium, high, critical)
        estimated_effort: Estimated effort in hours
        responsible_party: Who should perform this action
        due_date: When this action should be completed
        dependencies: List of action IDs this depends on
    """
    action_id: str
    title: str
    description: str
    priority: str
    estimated_effort: Optional[int] = None
    responsible_party: Optional[str] = None
    due_date: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    """
    Comprehensive compliance report for a document.
    
    Attributes:
        report_id: Unique identifier for the report
        document_id: ID of the analyzed document
        generated_at: Timestamp when report was generated
        overall_status: Overall compliance status
        risk_level: Overall risk level
        risk_score: Numerical risk score (0.0-1.0)
        frameworks_analyzed: List of compliance frameworks checked
        summary: Executive summary of findings
        issues: List of identified compliance issues
        missing_clauses: List of required clauses not found
        mitigation_actions: List of recommended mitigation actions
        recommendations: General recommendations
        metadata: Additional report metadata
    """
    report_id: str
    document_id: str
    generated_at: str
    overall_status: ComplianceStatus
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=1.0)
    frameworks_analyzed: List[str]
    summary: str
    issues: List[ComplianceIssue]
    missing_clauses: List[str]
    mitigation_actions: List[MitigationAction]
    recommendations: List[str]
    metadata: Dict[str, Any]


class ComplianceEngine:
    """
    Core compliance analysis engine.
    
    This engine provides comprehensive compliance checking capabilities including:
    - Multi-framework compliance analysis
    - Risk assessment and scoring
    - Mitigation action planning
    - Report generation
    - Compliance trend analysis
    """
    
    def __init__(self):
        """Initialize the compliance engine with DocumentAI service."""
        self.document_ai = DocumentAIService()
        self.risk_thresholds = {
            "low": 0.0,
            "medium": 0.3,
            "high": 0.6,
            "critical": 0.8
        }
    
    async def analyze_document_compliance(
        self,
        document_content: Any,
        document_type: Optional[str] = None,
        frameworks: Optional[List[str]] = None,
        analysis_depth: str = "comprehensive"
    ) -> ComplianceReport:
        """
        Perform comprehensive compliance analysis on a document.
        
        Args:
            document_content: Document content to analyze
            document_type: Type of document (optional)
            frameworks: List of compliance frameworks to check (optional)
            analysis_depth: Level of analysis detail
            
        Returns:
            Comprehensive compliance report
            
        Raises:
            ValueError: If analysis parameters are invalid
            Exception: If analysis fails
        """
        logger.info(f"Starting compliance analysis - frameworks: {frameworks}, depth: {analysis_depth}")
        
        try:
            # Set default frameworks if none provided
            if not frameworks:
                frameworks = ["gdpr", "sox", "ccpa"]
            
            # Create analysis request
            request = DocumentAnalysisRequest(
                document_content=document_content,
                document_type=document_type,
                compliance_frameworks=frameworks,
                analysis_depth=analysis_depth
            )
            
            # Perform document analysis
            analysis_result = await self.document_ai.analyze_document(request)
            
            # Generate compliance report
            report = await self._generate_compliance_report(analysis_result)
            
            logger.info(f"Compliance analysis completed - report_id: {report.report_id}, status: {report.overall_status}, risk_level: {report.risk_level}")
            
            return report
            
        except Exception as e:
            logger.error(f"Compliance analysis failed: {str(e)}")
            raise
    
    async def _generate_compliance_report(
        self, 
        analysis_result: DocumentAnalysisResult
    ) -> ComplianceReport:
        """
        Generate a comprehensive compliance report from analysis results.
        
        Args:
            analysis_result: Results from document analysis
            
        Returns:
            Structured compliance report
        """
        # Determine overall compliance status
        status = self._determine_compliance_status(analysis_result)
        
        # Determine risk level
        risk_level = self._determine_risk_level(analysis_result.risk_score)
        
        # Generate mitigation actions
        mitigation_actions = self._generate_mitigation_actions(analysis_result.compliance_issues)
        
        # Generate executive summary
        summary = self._generate_executive_summary(
            analysis_result, 
            status, 
            risk_level
        )
        
        # Create report
        report = ComplianceReport(
            report_id=f"compliance_report_{int(asyncio.get_event_loop().time())}",
            document_id=analysis_result.document_id,
            generated_at=datetime.utcnow().isoformat(),
            overall_status=status,
            risk_level=risk_level,
            risk_score=analysis_result.risk_score,
            frameworks_analyzed=analysis_result.metadata.get("frameworks_analyzed", []),
            summary=summary,
            issues=analysis_result.compliance_issues,
            missing_clauses=analysis_result.missing_clauses,
            mitigation_actions=mitigation_actions,
            recommendations=analysis_result.recommendations,
            metadata={
                **analysis_result.metadata,
                "analysis_timestamp": analysis_result.analysis_timestamp,
                "total_issues": len(analysis_result.compliance_issues),
                "critical_issues": len([i for i in analysis_result.compliance_issues if i.severity == "critical"]),
                "high_issues": len([i for i in analysis_result.compliance_issues if i.severity == "high"])
            }
        )
        
        return report
    
    def _determine_compliance_status(self, analysis_result: DocumentAnalysisResult) -> ComplianceStatus:
        """
        Determine overall compliance status based on analysis results.
        
        Args:
            analysis_result: Document analysis results
            
        Returns:
            Compliance status
        """
        critical_issues = [i for i in analysis_result.compliance_issues if i.severity == "critical"]
        high_issues = [i for i in analysis_result.compliance_issues if i.severity == "high"]
        missing_clauses = len(analysis_result.missing_clauses)
        
        if critical_issues or missing_clauses > 3:
            return ComplianceStatus.NON_COMPLIANT
        elif high_issues or missing_clauses > 1:
            return ComplianceStatus.PARTIALLY_COMPLIANT
        elif analysis_result.risk_score > 0.5:
            return ComplianceStatus.REQUIRES_REVIEW
        else:
            return ComplianceStatus.COMPLIANT
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determine risk level based on numerical risk score.
        
        Args:
            risk_score: Numerical risk score (0.0-1.0)
            
        Returns:
            Risk level
        """
        if risk_score >= self.risk_thresholds["critical"]:
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds["high"]:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds["medium"]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_mitigation_actions(self, issues: List[ComplianceIssue]) -> List[MitigationAction]:
        """
        Generate mitigation actions for identified compliance issues.
        
        Args:
            issues: List of compliance issues
            
        Returns:
            List of mitigation actions
        """
        actions = []
        
        for i, issue in enumerate(issues):
            action = MitigationAction(
                action_id=f"mitigation_{issue.issue_id}",
                title=f"Address {issue.category.replace('_', ' ').title()}",
                description=issue.recommendation,
                priority=issue.severity,
                estimated_effort=self._estimate_effort(issue.severity),
                responsible_party="Legal Team",  # Default, should be configurable
                due_date=self._calculate_due_date(issue.severity)
            )
            actions.append(action)
        
        return actions
    
    def _estimate_effort(self, severity: str) -> int:
        """
        Estimate effort in hours based on issue severity.
        
        Args:
            severity: Issue severity level
            
        Returns:
            Estimated effort in hours
        """
        effort_map = {
            "low": 2,
            "medium": 8,
            "high": 16,
            "critical": 32
        }
        return effort_map.get(severity, 8)
    
    def _calculate_due_date(self, severity: str) -> str:
        """
        Calculate due date based on issue severity.
        
        Args:
            severity: Issue severity level
            
        Returns:
            Due date in ISO format
        """
        days_map = {
            "low": 30,
            "medium": 14,
            "high": 7,
            "critical": 3
        }
        
        days = days_map.get(severity, 14)
        due_date = datetime.utcnow().timestamp() + (days * 24 * 60 * 60)
        return datetime.fromtimestamp(due_date).isoformat()
    
    def _generate_executive_summary(
        self, 
        analysis_result: DocumentAnalysisResult, 
        status: ComplianceStatus, 
        risk_level: RiskLevel
    ) -> str:
        """
        Generate executive summary of compliance analysis.
        
        Args:
            analysis_result: Document analysis results
            status: Overall compliance status
            risk_level: Overall risk level
            
        Returns:
            Executive summary text
        """
        total_issues = len(analysis_result.compliance_issues)
        critical_issues = len([i for i in analysis_result.compliance_issues if i.severity == "critical"])
        high_issues = len([i for i in analysis_result.compliance_issues if i.severity == "high"])
        missing_clauses = len(analysis_result.missing_clauses)
        
        summary = f"""
        COMPLIANCE ANALYSIS EXECUTIVE SUMMARY
        
        Document ID: {analysis_result.document_id}
        Analysis Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        
        OVERALL STATUS: {status.value.upper()}
        RISK LEVEL: {risk_level.value.upper()}
        RISK SCORE: {analysis_result.risk_score:.2f}/1.0
        
        KEY FINDINGS:
        • Total Issues Identified: {total_issues}
        • Critical Issues: {critical_issues}
        • High Priority Issues: {high_issues}
        • Missing Required Clauses: {missing_clauses}
        
        FRAMEWORKS ANALYZED: {', '.join(analysis_result.metadata.get('frameworks_analyzed', []))}
        
        NEXT STEPS:
        """
        
        if critical_issues > 0:
            summary += f"\n• IMMEDIATE ACTION REQUIRED: Address {critical_issues} critical compliance issues"
        
        if missing_clauses > 0:
            summary += f"\n• Add {missing_clauses} missing required clauses to ensure full compliance"
        
        if high_issues > 0:
            summary += f"\n• Review and address {high_issues} high-priority issues within 7 days"
        
        if status == ComplianceStatus.COMPLIANT:
            summary += "\n• Document appears compliant - consider periodic review"
        
        return summary.strip()
    
    async def generate_audit_trail_entry(self, report: ComplianceReport) -> str:
        """
        Generate audit trail entry for GitHub.
        
        Args:
            report: Compliance report to create audit trail for
            
        Returns:
            Markdown formatted audit trail entry
        """
        timestamp = datetime.fromisoformat(report.generated_at.replace('Z', '+00:00'))
        
        audit_entry = f"""# Compliance Audit Trail Entry

**Report ID:** {report.report_id}  
**Document ID:** {report.document_id}  
**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M UTC')}  
**Status:** {report.overall_status.value.upper()}  
**Risk Level:** {report.risk_level.value.upper()}  
**Risk Score:** {report.risk_score:.2f}/1.0  

## Executive Summary

{report.summary}

## Compliance Issues

"""
        
        if report.issues:
            for issue in report.issues:
                audit_entry += f"""### {issue.severity.upper()}: {issue.description}

- **Category:** {issue.category}
- **Framework:** {issue.framework.upper()}
- **Location:** {issue.location or 'Not specified'}
- **Confidence:** {issue.confidence:.2f}
- **Recommendation:** {issue.recommendation}

"""
        else:
            audit_entry += "No compliance issues identified.\n\n"
        
        if report.missing_clauses:
            audit_entry += "## Missing Required Clauses\n\n"
            for clause in report.missing_clauses:
                audit_entry += f"- {clause}\n"
            audit_entry += "\n"
        
        if report.mitigation_actions:
            audit_entry += "## Recommended Mitigation Actions\n\n"
            for action in report.mitigation_actions:
                audit_entry += f"""### {action.title}

- **Priority:** {action.priority.upper()}
- **Description:** {action.description}
- **Estimated Effort:** {action.estimated_effort} hours
- **Due Date:** {action.due_date or 'Not specified'}

"""
        
        audit_entry += f"""## Metadata

- **Frameworks Analyzed:** {', '.join(report.frameworks_analyzed)}
- **Total Issues:** {report.metadata.get('total_issues', 0)}
- **Critical Issues:** {report.metadata.get('critical_issues', 0)}
- **High Priority Issues:** {report.metadata.get('high_issues', 0)}

---
*Generated by OuiComply MCP Server v1.0.0*
"""
        
        return audit_entry
    
    def export_report_json(self, report: ComplianceReport) -> str:
        """
        Export compliance report as JSON.
        
        Args:
            report: Compliance report to export
            
        Returns:
            JSON string representation of the report
        """
        return report.model_dump_json(indent=2)
    
    def export_report_markdown(self, report: ComplianceReport) -> str:
        """
        Export compliance report as Markdown.
        
        Args:
            report: Compliance report to export
            
        Returns:
            Markdown string representation of the report
        """
        markdown = f"""# Compliance Report

**Report ID:** {report.report_id}  
**Document ID:** {report.document_id}  
**Generated:** {report.generated_at}  
**Status:** {report.overall_status.value.upper()}  
**Risk Level:** {report.risk_level.value.upper()}  
**Risk Score:** {report.risk_score:.2f}/1.0  

## Executive Summary

{report.summary}

## Detailed Analysis

### Compliance Issues

"""
        
        if report.issues:
            for issue in report.issues:
                markdown += f"""#### {issue.severity.upper()}: {issue.description}

- **Issue ID:** {issue.issue_id}
- **Category:** {issue.category}
- **Framework:** {issue.framework.upper()}
- **Location:** {issue.location or 'Not specified'}
- **Confidence:** {issue.confidence:.2f}
- **Recommendation:** {issue.recommendation}

"""
        else:
            markdown += "No compliance issues identified.\n\n"
        
        if report.missing_clauses:
            markdown += "### Missing Required Clauses\n\n"
            for clause in report.missing_clauses:
                markdown += f"- {clause}\n"
            markdown += "\n"
        
        if report.mitigation_actions:
            markdown += "### Mitigation Actions\n\n"
            for action in report.mitigation_actions:
                markdown += f"""#### {action.title}

- **Action ID:** {action.action_id}
- **Priority:** {action.priority.upper()}
- **Description:** {action.description}
- **Estimated Effort:** {action.estimated_effort} hours
- **Responsible Party:** {action.responsible_party or 'Not assigned'}
- **Due Date:** {action.due_date or 'Not specified'}
- **Dependencies:** {', '.join(action.dependencies) if action.dependencies else 'None'}

"""
        
        if report.recommendations:
            markdown += "### General Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                markdown += f"{i}. {rec}\n"
            markdown += "\n"
        
        markdown += f"""## Metadata

- **Frameworks Analyzed:** {', '.join(report.frameworks_analyzed)}
- **Total Issues:** {report.metadata.get('total_issues', 0)}
- **Critical Issues:** {report.metadata.get('critical_issues', 0)}
- **High Priority Issues:** {report.metadata.get('high_issues', 0)}

---
*Generated by OuiComply MCP Server v1.0.0*
"""
        
        return markdown
