"""
Tests for compliance engine module.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.tools.compliance_engine import (
    ComplianceEngine,
    ComplianceReport,
    ComplianceStatus,
    RiskLevel,
    MitigationAction
)
from src.tools.document_ai import DocumentAnalysisResult, ComplianceIssue


class TestComplianceEngine:
    """Test cases for compliance engine."""
    
    @pytest.fixture
    def compliance_engine(self):
        """Create compliance engine instance for testing."""
        return ComplianceEngine()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Create sample analysis result for testing."""
        issues = [
            ComplianceIssue(
                issue_id="1",
                severity="critical",
                category="data_protection",
                description="Missing privacy notice",
                recommendation="Add comprehensive privacy notice",
                framework="gdpr",
                confidence=0.9
            ),
            ComplianceIssue(
                issue_id="2",
                severity="high",
                category="consent",
                description="Unclear consent mechanism",
                recommendation="Clarify consent process",
                framework="gdpr",
                confidence=0.8
            )
        ]
        
        return DocumentAnalysisResult(
            document_id="doc123",
            document_type="application/pdf",
            analysis_timestamp="2024-01-01T00:00:00Z",
            compliance_issues=issues,
            risk_score=0.85,
            missing_clauses=["data_retention_policy", "breach_notification"],
            recommendations=["Implement comprehensive privacy framework"],
            metadata={
                "frameworks_analyzed": ["gdpr"],
                "total_issues": 2,
                "critical_issues": 1,
                "high_issues": 1
            }
        )
    
    def test_determine_compliance_status_compliant(self, compliance_engine):
        """Test compliance status determination for compliant document."""
        result = DocumentAnalysisResult(
            document_id="doc123",
            document_type="application/pdf",
            analysis_timestamp="2024-01-01T00:00:00Z",
            compliance_issues=[],
            risk_score=0.2,
            missing_clauses=[],
            recommendations=[],
            metadata={}
        )
        
        status = compliance_engine._determine_compliance_status(result)
        assert status == ComplianceStatus.COMPLIANT
    
    def test_determine_compliance_status_non_compliant(self, compliance_engine):
        """Test compliance status determination for non-compliant document."""
        critical_issues = [
            ComplianceIssue(
                issue_id="1",
                severity="critical",
                category="test",
                description="Critical issue",
                recommendation="Fix it",
                framework="gdpr",
                confidence=0.9
            )
        ]
        
        result = DocumentAnalysisResult(
            document_id="doc123",
            document_type="application/pdf",
            analysis_timestamp="2024-01-01T00:00:00Z",
            compliance_issues=critical_issues,
            risk_score=0.9,
            missing_clauses=["clause1", "clause2", "clause3", "clause4"],
            recommendations=[],
            metadata={}
        )
        
        status = compliance_engine._determine_compliance_status(result)
        assert status == ComplianceStatus.NON_COMPLIANT
    
    def test_determine_compliance_status_partially_compliant(self, compliance_engine):
        """Test compliance status determination for partially compliant document."""
        high_issues = [
            ComplianceIssue(
                issue_id="1",
                severity="high",
                category="test",
                description="High issue",
                recommendation="Fix it",
                framework="gdpr",
                confidence=0.8
            )
        ]
        
        result = DocumentAnalysisResult(
            document_id="doc123",
            document_type="application/pdf",
            analysis_timestamp="2024-01-01T00:00:00Z",
            compliance_issues=high_issues,
            risk_score=0.6,
            missing_clauses=["clause1", "clause2"],
            recommendations=[],
            metadata={}
        )
        
        status = compliance_engine._determine_compliance_status(result)
        assert status == ComplianceStatus.PARTIALLY_COMPLIANT
    
    def test_determine_risk_level_low(self, compliance_engine):
        """Test risk level determination for low risk."""
        risk_level = compliance_engine._determine_risk_level(0.2)
        assert risk_level == RiskLevel.LOW
    
    def test_determine_risk_level_medium(self, compliance_engine):
        """Test risk level determination for medium risk."""
        risk_level = compliance_engine._determine_risk_level(0.4)
        assert risk_level == RiskLevel.MEDIUM
    
    def test_determine_risk_level_high(self, compliance_engine):
        """Test risk level determination for high risk."""
        risk_level = compliance_engine._determine_risk_level(0.7)
        assert risk_level == RiskLevel.HIGH
    
    def test_determine_risk_level_critical(self, compliance_engine):
        """Test risk level determination for critical risk."""
        risk_level = compliance_engine._determine_risk_level(0.9)
        assert risk_level == RiskLevel.CRITICAL
    
    def test_generate_mitigation_actions(self, compliance_engine):
        """Test mitigation action generation."""
        issues = [
            ComplianceIssue(
                issue_id="1",
                severity="critical",
                category="data_protection",
                description="Missing privacy notice",
                recommendation="Add privacy notice",
                framework="gdpr",
                confidence=0.9
            ),
            ComplianceIssue(
                issue_id="2",
                severity="low",
                category="consent",
                description="Minor consent issue",
                recommendation="Review consent",
                framework="gdpr",
                confidence=0.6
            )
        ]
        
        actions = compliance_engine._generate_mitigation_actions(issues)
        
        assert len(actions) == 2
        assert actions[0].priority == "critical"
        assert actions[0].estimated_effort == 32  # Critical issues get 32 hours
        assert actions[1].priority == "low"
        assert actions[1].estimated_effort == 2  # Low issues get 2 hours
    
    def test_estimate_effort(self, compliance_engine):
        """Test effort estimation for different severities."""
        assert compliance_engine._estimate_effort("low") == 2
        assert compliance_engine._estimate_effort("medium") == 8
        assert compliance_engine._estimate_effort("high") == 16
        assert compliance_engine._estimate_effort("critical") == 32
        assert compliance_engine._estimate_effort("unknown") == 8  # Default
    
    def test_calculate_due_date(self, compliance_engine):
        """Test due date calculation for different severities."""
        due_date_low = compliance_engine._calculate_due_date("low")
        due_date_critical = compliance_engine._calculate_due_date("critical")
        
        # Critical should be sooner than low
        assert due_date_critical < due_date_low
        
        # Both should be valid ISO format dates
        datetime.fromisoformat(due_date_low.replace('Z', '+00:00'))
        datetime.fromisoformat(due_date_critical.replace('Z', '+00:00'))
    
    def test_generate_executive_summary(self, compliance_engine, sample_analysis_result):
        """Test executive summary generation."""
        status = ComplianceStatus.PARTIALLY_COMPLIANT
        risk_level = RiskLevel.HIGH
        
        summary = compliance_engine._generate_executive_summary(
            sample_analysis_result, status, risk_level
        )
        
        assert "COMPLIANCE ANALYSIS EXECUTIVE SUMMARY" in summary
        assert "doc123" in summary
        assert "PARTIALLY_COMPLIANT" in summary
        assert "HIGH" in summary
        assert "0.85" in summary
        assert "2" in summary  # Total issues
        assert "1" in summary  # Critical issues
        assert "2" in summary  # Missing clauses
    
    @pytest.mark.asyncio
    async def test_analyze_document_compliance_mock(self, compliance_engine):
        """Test document compliance analysis with mocked DocumentAI service."""
        with patch.object(compliance_engine.document_ai, 'analyze_document') as mock_analyze:
            # Mock the DocumentAI response
            mock_result = DocumentAnalysisResult(
                document_id="doc123",
                document_type="application/pdf",
                analysis_timestamp="2024-01-01T00:00:00Z",
                compliance_issues=[],
                risk_score=0.3,
                missing_clauses=[],
                recommendations=[],
                metadata={"frameworks_analyzed": ["gdpr"]}
            )
            mock_analyze.return_value = mock_result
            
            # Test the analysis
            report = await compliance_engine.analyze_document_compliance(
                document_content="test content",
                frameworks=["gdpr"],
                analysis_depth="comprehensive"
            )
            
            assert isinstance(report, ComplianceReport)
            assert report.document_id == "doc123"
            assert report.overall_status == ComplianceStatus.COMPLIANT
            assert report.risk_level == RiskLevel.MEDIUM
            assert report.risk_score == 0.3
    
    @pytest.mark.asyncio
    async def test_generate_audit_trail_entry(self, compliance_engine, sample_analysis_result):
        """Test audit trail entry generation."""
        # First generate a compliance report
        with patch.object(compliance_engine, '_generate_compliance_report') as mock_generate:
            mock_report = ComplianceReport(
                report_id="report123",
                document_id="doc123",
                generated_at="2024-01-01T00:00:00Z",
                overall_status=ComplianceStatus.PARTIALLY_COMPLIANT,
                risk_level=RiskLevel.HIGH,
                risk_score=0.85,
                frameworks_analyzed=["gdpr"],
                summary="Test summary",
                issues=sample_analysis_result.compliance_issues,
                missing_clauses=sample_analysis_result.missing_clauses,
                mitigation_actions=[],
                recommendations=sample_analysis_result.recommendations,
                metadata=sample_analysis_result.metadata
            )
            mock_generate.return_value = mock_report
            
            audit_trail = await compliance_engine.generate_audit_trail_entry(mock_report)
            
            assert "# Compliance Audit Trail Entry" in audit_trail
            assert "report123" in audit_trail
            assert "doc123" in audit_trail
            assert "PARTIALLY_COMPLIANT" in audit_trail
            assert "HIGH" in audit_trail
            assert "0.85" in audit_trail
    
    def test_export_report_json(self, compliance_engine, sample_analysis_result):
        """Test JSON report export."""
        report = ComplianceReport(
            report_id="report123",
            document_id="doc123",
            generated_at="2024-01-01T00:00:00Z",
            overall_status=ComplianceStatus.PARTIALLY_COMPLIANT,
            risk_level=RiskLevel.HIGH,
            risk_score=0.85,
            frameworks_analyzed=["gdpr"],
            summary="Test summary",
            issues=sample_analysis_result.compliance_issues,
            missing_clauses=sample_analysis_result.missing_clauses,
            mitigation_actions=[],
            recommendations=sample_analysis_result.recommendations,
            metadata=sample_analysis_result.metadata
        )
        
        json_output = compliance_engine.export_report_json(report)
        
        assert isinstance(json_output, str)
        assert "report123" in json_output
        assert "doc123" in json_output
        assert "PARTIALLY_COMPLIANT" in json_output
    
    def test_export_report_markdown(self, compliance_engine, sample_analysis_result):
        """Test Markdown report export."""
        report = ComplianceReport(
            report_id="report123",
            document_id="doc123",
            generated_at="2024-01-01T00:00:00Z",
            overall_status=ComplianceStatus.PARTIALLY_COMPLIANT,
            risk_level=RiskLevel.HIGH,
            risk_score=0.85,
            frameworks_analyzed=["gdpr"],
            summary="Test summary",
            issues=sample_analysis_result.compliance_issues,
            missing_clauses=sample_analysis_result.missing_clauses,
            mitigation_actions=[],
            recommendations=sample_analysis_result.recommendations,
            metadata=sample_analysis_result.metadata
        )
        
        markdown_output = compliance_engine.export_report_markdown(report)
        
        assert isinstance(markdown_output, str)
        assert "# Compliance Report" in markdown_output
        assert "report123" in markdown_output
        assert "doc123" in markdown_output
        assert "PARTIALLY_COMPLIANT" in markdown_output


class TestComplianceReport:
    """Test cases for ComplianceReport model."""
    
    def test_create_compliance_report(self):
        """Test creating a compliance report."""
        issues = [
            ComplianceIssue(
                issue_id="1",
                severity="high",
                category="test",
                description="Test issue",
                recommendation="Fix it",
                framework="gdpr",
                confidence=0.8
            )
        ]
        
        actions = [
            MitigationAction(
                action_id="action1",
                title="Fix Test Issue",
                description="Address the test issue",
                priority="high"
            )
        ]
        
        report = ComplianceReport(
            report_id="report123",
            document_id="doc123",
            generated_at="2024-01-01T00:00:00Z",
            overall_status=ComplianceStatus.PARTIALLY_COMPLIANT,
            risk_level=RiskLevel.HIGH,
            risk_score=0.7,
            frameworks_analyzed=["gdpr"],
            summary="Test summary",
            issues=issues,
            missing_clauses=["clause1"],
            mitigation_actions=actions,
            recommendations=["rec1"],
            metadata={"test": "value"}
        )
        
        assert report.report_id == "report123"
        assert report.document_id == "doc123"
        assert report.overall_status == ComplianceStatus.PARTIALLY_COMPLIANT
        assert report.risk_level == RiskLevel.HIGH
        assert report.risk_score == 0.7
        assert len(report.issues) == 1
        assert len(report.mitigation_actions) == 1
        assert report.missing_clauses == ["clause1"]
        assert report.recommendations == ["rec1"]


class TestMitigationAction:
    """Test cases for MitigationAction model."""
    
    def test_create_mitigation_action(self):
        """Test creating a mitigation action."""
        action = MitigationAction(
            action_id="action1",
            title="Fix Issue",
            description="Address the compliance issue",
            priority="high",
            estimated_effort=8,
            responsible_party="Legal Team",
            due_date="2024-01-15T00:00:00Z",
            dependencies=["action2"]
        )
        
        assert action.action_id == "action1"
        assert action.title == "Fix Issue"
        assert action.description == "Address the compliance issue"
        assert action.priority == "high"
        assert action.estimated_effort == 8
        assert action.responsible_party == "Legal Team"
        assert action.due_date == "2024-01-15T00:00:00Z"
        assert action.dependencies == ["action2"]
    
    def test_create_mitigation_action_minimal(self):
        """Test creating a mitigation action with minimal fields."""
        action = MitigationAction(
            action_id="action1",
            title="Fix Issue",
            description="Address the compliance issue",
            priority="high"
        )
        
        assert action.action_id == "action1"
        assert action.title == "Fix Issue"
        assert action.description == "Address the compliance issue"
        assert action.priority == "high"
        assert action.estimated_effort is None
        assert action.responsible_party is None
        assert action.due_date is None
        assert action.dependencies == []
