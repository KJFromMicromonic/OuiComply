"""
Tests for DocumentAI integration module.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from src.tools.document_ai import (
    DocumentAIService,
    DocumentAnalysisRequest,
    ComplianceIssue,
    DocumentAnalysisResult
)


class TestDocumentAIService:
    """Test cases for DocumentAI service."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.mistral_api_key = "test_api_key"
        return config
    
    @pytest.fixture
    def document_ai_service(self, mock_config):
        """Create DocumentAI service instance for testing."""
        with patch('src.tools.document_ai.get_config', return_value=mock_config):
            return DocumentAIService()
    
    def test_load_compliance_frameworks(self, document_ai_service):
        """Test compliance framework loading."""
        frameworks = document_ai_service.compliance_frameworks
        
        assert "gdpr" in frameworks
        assert "sox" in frameworks
        assert "ccpa" in frameworks
        assert "hipaa" in frameworks
        
        # Check GDPR framework structure
        gdpr = frameworks["gdpr"]
        assert "name" in gdpr
        assert "required_clauses" in gdpr
        assert "risk_indicators" in gdpr
        assert len(gdpr["required_clauses"]) > 0
    
    @pytest.mark.asyncio
    async def test_process_document_content_bytes(self, document_ai_service):
        """Test processing document content as bytes."""
        content = b"test document content"
        result = await document_ai_service._process_document_content(content)
        assert result == content
    
    @pytest.mark.asyncio
    async def test_process_document_content_string_path(self, document_ai_service, tmp_path):
        """Test processing document content as file path string."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = await document_ai_service._process_document_content(str(test_file))
        assert result == b"test content"
    
    @pytest.mark.asyncio
    async def test_process_document_content_path_object(self, document_ai_service, tmp_path):
        """Test processing document content as Path object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = await document_ai_service._process_document_content(test_file)
        assert result == b"test content"
    
    @pytest.mark.asyncio
    async def test_process_document_content_invalid_path(self, document_ai_service):
        """Test processing document content with invalid path."""
        with pytest.raises(ValueError, match="File not found"):
            await document_ai_service._process_document_content("nonexistent_file.txt")
    
    def test_determine_document_type_provided(self, document_ai_service):
        """Test document type determination with provided type."""
        content = b"test content"
        doc_type = document_ai_service._determine_document_type("application/pdf", content)
        assert doc_type == "application/pdf"
    
    def test_determine_document_type_auto_detect(self, document_ai_service):
        """Test automatic document type detection."""
        content = b"test content"
        doc_type = document_ai_service._determine_document_type(None, content)
        # Should return a valid MIME type or fallback
        assert isinstance(doc_type, str)
    
    def test_calculate_risk_score_no_issues(self, document_ai_service):
        """Test risk score calculation with no issues."""
        issues = []
        score = document_ai_service._calculate_risk_score(issues)
        assert score == 0.0
    
    def test_calculate_risk_score_with_issues(self, document_ai_service):
        """Test risk score calculation with various issues."""
        issues = [
            ComplianceIssue(
                issue_id="1",
                severity="critical",
                category="test",
                description="Critical issue",
                recommendation="Fix it",
                framework="gdpr",
                confidence=0.9
            ),
            ComplianceIssue(
                issue_id="2",
                severity="low",
                category="test",
                description="Low issue",
                recommendation="Monitor",
                framework="gdpr",
                confidence=0.5
            )
        ]
        score = document_ai_service._calculate_risk_score(issues)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be weighted toward critical issue
    
    def test_generate_analysis_prompt(self, document_ai_service):
        """Test analysis prompt generation."""
        framework_def = {
            "name": "Test Framework",
            "required_clauses": ["clause1", "clause2"],
            "risk_indicators": ["risk1", "risk2"]
        }
        
        prompt = document_ai_service._generate_analysis_prompt(
            framework_def, "comprehensive", "doc123"
        )
        
        assert "Test Framework" in prompt
        assert "clause1" in prompt
        assert "clause2" in prompt
        assert "risk1" in prompt
        assert "risk2" in prompt
        assert "doc123" in prompt
        assert "JSON format" in prompt
    
    def test_parse_ai_response_valid_json(self, document_ai_service):
        """Test parsing valid AI response."""
        response = '''
        {
            "issues": [
                {
                    "issue_id": "test1",
                    "severity": "high",
                    "category": "test",
                    "description": "Test issue",
                    "location": "Section 1",
                    "recommendation": "Fix it",
                    "confidence": 0.8
                }
            ],
            "missing_clauses": ["clause1"],
            "recommendations": ["rec1"]
        }
        '''
        
        result = document_ai_service._parse_ai_response(response, "gdpr")
        
        assert len(result["issues"]) == 1
        assert result["issues"][0]["framework"] == "gdpr"
        assert result["missing_clauses"] == ["clause1"]
        assert result["recommendations"] == ["rec1"]
    
    def test_parse_ai_response_invalid_json(self, document_ai_service):
        """Test parsing invalid AI response falls back gracefully."""
        response = "This is not valid JSON"
        
        result = document_ai_service._parse_ai_response(response, "gdpr")
        
        assert "issues" in result
        assert "missing_clauses" in result
        assert "recommendations" in result
        assert len(result["issues"]) == 1
        assert result["issues"][0]["framework"] == "gdpr"
    
    @pytest.mark.asyncio
    async def test_analyze_document_mock(self, document_ai_service):
        """Test document analysis with mocked Mistral API."""
        request = DocumentAnalysisRequest(
            document_content="test document content",
            compliance_frameworks=["gdpr"],
            analysis_depth="basic"
        )
        
        # Mock the Mistral API calls
        with patch.object(document_ai_service.client.documents, 'create') as mock_create, \
             patch.object(document_ai_service.client.chat, 'complete') as mock_chat:
            
            # Mock document upload
            mock_create.return_value = Mock(id="doc123")
            
            # Mock chat completion
            mock_chat.return_value = Mock(
                choices=[Mock(message=Mock(content='{"issues": [], "missing_clauses": [], "recommendations": []}'))]
            )
            
            result = await document_ai_service.analyze_document(request)
            
            assert isinstance(result, DocumentAnalysisResult)
            assert result.document_id == "doc123"
            assert result.document_type is not None
            assert result.risk_score >= 0.0
            assert result.risk_score <= 1.0


class TestDocumentAnalysisRequest:
    """Test cases for DocumentAnalysisRequest model."""
    
    def test_create_request_with_required_fields(self):
        """Test creating request with only required fields."""
        request = DocumentAnalysisRequest(document_content="test content")
        
        assert request.document_content == "test content"
        assert request.document_type is None
        assert request.compliance_frameworks == ["gdpr", "sox", "ccpa"]
        assert request.analysis_depth == "comprehensive"
    
    def test_create_request_with_all_fields(self):
        """Test creating request with all fields."""
        request = DocumentAnalysisRequest(
            document_content="test content",
            document_type="application/pdf",
            compliance_frameworks=["gdpr"],
            analysis_depth="basic"
        )
        
        assert request.document_content == "test content"
        assert request.document_type == "application/pdf"
        assert request.compliance_frameworks == ["gdpr"]
        assert request.analysis_depth == "basic"


class TestComplianceIssue:
    """Test cases for ComplianceIssue model."""
    
    def test_create_compliance_issue(self):
        """Test creating a compliance issue."""
        issue = ComplianceIssue(
            issue_id="test1",
            severity="high",
            category="data_protection",
            description="Missing privacy notice",
            recommendation="Add privacy notice",
            framework="gdpr",
            confidence=0.9
        )
        
        assert issue.issue_id == "test1"
        assert issue.severity == "high"
        assert issue.category == "data_protection"
        assert issue.description == "Missing privacy notice"
        assert issue.recommendation == "Add privacy notice"
        assert issue.framework == "gdpr"
        assert issue.confidence == 0.9
    
    def test_compliance_issue_confidence_validation(self):
        """Test confidence score validation."""
        with pytest.raises(ValueError):
            ComplianceIssue(
                issue_id="test1",
                severity="high",
                category="test",
                description="Test",
                recommendation="Test",
                framework="gdpr",
                confidence=1.5  # Invalid confidence > 1.0
            )
        
        with pytest.raises(ValueError):
            ComplianceIssue(
                issue_id="test1",
                severity="high",
                category="test",
                description="Test",
                recommendation="Test",
                framework="gdpr",
                confidence=-0.1  # Invalid confidence < 0.0
            )


class TestDocumentAnalysisResult:
    """Test cases for DocumentAnalysisResult model."""
    
    def test_create_analysis_result(self):
        """Test creating an analysis result."""
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
        
        result = DocumentAnalysisResult(
            document_id="doc123",
            document_type="application/pdf",
            analysis_timestamp="2024-01-01T00:00:00Z",
            compliance_issues=issues,
            risk_score=0.8,
            missing_clauses=["clause1"],
            recommendations=["rec1"],
            metadata={"test": "value"}
        )
        
        assert result.document_id == "doc123"
        assert result.document_type == "application/pdf"
        assert result.risk_score == 0.8
        assert len(result.compliance_issues) == 1
        assert result.missing_clauses == ["clause1"]
        assert result.recommendations == ["rec1"]
    
    def test_analysis_result_risk_score_validation(self):
        """Test risk score validation."""
        with pytest.raises(ValueError):
            DocumentAnalysisResult(
                document_id="doc123",
                document_type="application/pdf",
                analysis_timestamp="2024-01-01T00:00:00Z",
                compliance_issues=[],
                risk_score=1.5,  # Invalid risk score > 1.0
                missing_clauses=[],
                recommendations=[],
                metadata={}
            )
