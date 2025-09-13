"""
Test cases for Mistral AI function calling functionality.

This module contains comprehensive tests for the function calling
implementation in the OuiComply project.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from api_examples.function_calling import ComplianceAnalyzer


class TestComplianceAnalyzer:
    """Test cases for the ComplianceAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a ComplianceAnalyzer instance for testing."""
        return ComplianceAnalyzer(api_key="test_key")
    
    @pytest.fixture
    def sample_document(self):
        """Sample document content for testing."""
        return """
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
    
    @pytest.fixture
    def mock_response(self):
        """Mock API response for testing."""
        return {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "function": {
                            "name": "analyze_compliance_issues",
                            "arguments": json.dumps({
                                "compliance_issues": [
                                    {
                                        "issue_id": "test_issue_1",
                                        "severity": "high",
                                        "category": "data_protection",
                                        "description": "Missing explicit consent mechanism",
                                        "location": "Section 2",
                                        "recommendation": "Add clear consent checkbox",
                                        "confidence": 0.9,
                                        "framework": "gdpr"
                                    }
                                ],
                                "missing_clauses": [
                                    "Data subject rights information",
                                    "Data retention period specification"
                                ],
                                "recommendations": [
                                    "Add comprehensive data subject rights section",
                                    "Specify exact data retention periods"
                                ],
                                "risk_score": 0.7,
                                "compliance_status": "partially_compliant"
                            })
                        }
                    }]
                }
            }]
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test that the analyzer initializes correctly."""
        assert analyzer.client is not None
        assert len(analyzer.compliance_tools) == 1
        assert analyzer.compliance_tools[0]["type"] == "function"
    
    def test_compliance_tools_structure(self, analyzer):
        """Test that compliance tools are properly structured."""
        tool = analyzer.compliance_tools[0]["function"]
        
        assert tool["name"] == "analyze_compliance_issues"
        assert "parameters" in tool
        assert "properties" in tool["parameters"]
        assert "compliance_issues" in tool["parameters"]["properties"]
        assert "required" in tool["parameters"]
    
    @pytest.mark.asyncio
    async def test_analyze_document_success(self, analyzer, sample_document, mock_response):
        """Test successful document analysis."""
        # Mock the client's chat.complete method
        analyzer.client.chat.complete = AsyncMock(return_value=MagicMock(**mock_response))
        
        # Test the analysis
        result = await analyzer.analyze_document(
            document_content=sample_document,
            frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        # Verify the result structure
        assert "compliance_issues" in result
        assert "missing_clauses" in result
        assert "recommendations" in result
        assert "risk_score" in result
        assert "compliance_status" in result
        
        # Verify specific values
        assert result["compliance_status"] == "partially_compliant"
        assert result["risk_score"] == 0.7
        assert len(result["compliance_issues"]) == 1
        assert result["compliance_issues"][0]["severity"] == "high"
    
    @pytest.mark.asyncio
    async def test_analyze_document_no_tool_calls(self, analyzer, sample_document):
        """Test error handling when no tool calls are returned."""
        # Mock response without tool calls
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Some response without tool calls"
                }
            }]
        }
        
        analyzer.client.chat.complete = AsyncMock(return_value=MagicMock(**mock_response))
        
        # Test that ValueError is raised
        with pytest.raises(ValueError, match="No tool call found in response"):
            await analyzer.analyze_document(sample_document)
    
    @pytest.mark.asyncio
    async def test_analyze_document_api_error(self, analyzer, sample_document):
        """Test error handling when API call fails."""
        # Mock API error
        analyzer.client.chat.complete = AsyncMock(side_effect=Exception("API Error"))
        
        # Test that exception is propagated
        with pytest.raises(Exception, match="API Error"):
            await analyzer.analyze_document(sample_document)
    
    @pytest.mark.asyncio
    async def test_analyze_multiple_documents(self, analyzer):
        """Test analyzing multiple documents in parallel."""
        documents = [
            {"name": "doc1", "content": "Privacy policy content 1"},
            {"name": "doc2", "content": "Privacy policy content 2"}
        ]
        
        # Mock successful responses for both documents
        mock_response = {
            "choices": [{
                "message": {
                    "tool_calls": [{
                        "function": {
                            "name": "analyze_compliance_issues",
                            "arguments": json.dumps({
                                "compliance_issues": [],
                                "missing_clauses": [],
                                "recommendations": [],
                                "risk_score": 0.1,
                                "compliance_status": "compliant"
                            })
                        }
                    }]
                }
            }]
        }
        
        analyzer.client.chat.complete = AsyncMock(return_value=MagicMock(**mock_response))
        
        # Test parallel analysis
        results = await analyzer.analyze_multiple_documents(documents, ["gdpr"])
        
        # Verify results
        assert len(results) == 2
        assert all(result["success"] for result in results)
        assert results[0]["document_name"] == "doc1"
        assert results[1]["document_name"] == "doc2"
    
    @pytest.mark.asyncio
    async def test_analyze_multiple_documents_with_error(self, analyzer):
        """Test analyzing multiple documents when one fails."""
        documents = [
            {"name": "doc1", "content": "Privacy policy content 1"},
            {"name": "doc2", "content": "Privacy policy content 2"}
        ]
        
        # Mock one success and one failure
        def mock_complete(*args, **kwargs):
            if "doc1" in str(kwargs.get("messages", [])):
                return MagicMock(**{
                    "choices": [{
                        "message": {
                            "tool_calls": [{
                                "function": {
                                    "name": "analyze_compliance_issues",
                                    "arguments": json.dumps({
                                        "compliance_issues": [],
                                        "missing_clauses": [],
                                        "recommendations": [],
                                        "risk_score": 0.1,
                                        "compliance_status": "compliant"
                                    })
                                }
                            }]
                        }
                    }]
                })
            else:
                raise Exception("API Error")
        
        analyzer.client.chat.complete = AsyncMock(side_effect=mock_complete)
        
        # Test parallel analysis with error
        results = await analyzer.analyze_multiple_documents(documents, ["gdpr"])
        
        # Verify results
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "API Error" in results[1]["error"]
    
    def test_generate_analysis_prompt(self, analyzer, sample_document):
        """Test analysis prompt generation."""
        prompt = analyzer._generate_analysis_prompt(
            document_content=sample_document,
            frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        # Verify prompt contains expected elements
        assert "GDPR" in prompt
        assert "CCPA" in prompt
        assert "comprehensive" in prompt
        assert "Privacy Policy" in prompt
        assert "data protection" in prompt.lower()
    
    def test_compliance_tools_required_fields(self, analyzer):
        """Test that compliance tools have all required fields."""
        tool = analyzer.compliance_tools[0]["function"]
        parameters = tool["parameters"]
        
        # Check required fields
        required_fields = ["compliance_issues", "missing_clauses", "recommendations", "risk_score", "compliance_status"]
        assert all(field in parameters["required"] for field in required_fields)
        
        # Check compliance_issues structure
        issues_props = parameters["properties"]["compliance_issues"]["items"]["properties"]
        issue_required_fields = ["issue_id", "severity", "category", "description", "recommendation", "confidence", "framework"]
        assert all(field in issues_props for field in issue_required_fields)
    
    @pytest.mark.asyncio
    async def test_different_analysis_depths(self, analyzer, sample_document, mock_response):
        """Test analysis with different depth levels."""
        analyzer.client.chat.complete = AsyncMock(return_value=MagicMock(**mock_response))
        
        # Test different analysis depths
        for depth in ["basic", "standard", "comprehensive"]:
            result = await analyzer.analyze_document(
                document_content=sample_document,
                frameworks=["gdpr"],
                analysis_depth=depth
            )
            
            assert result["compliance_status"] == "partially_compliant"
            assert "compliance_issues" in result
    
    @pytest.mark.asyncio
    async def test_different_frameworks(self, analyzer, sample_document, mock_response):
        """Test analysis with different compliance frameworks."""
        analyzer.client.chat.complete = AsyncMock(return_value=MagicMock(**mock_response))
        
        # Test different framework combinations
        framework_combinations = [
            ["gdpr"],
            ["sox"],
            ["ccpa"],
            ["gdpr", "sox"],
            ["gdpr", "ccpa", "sox"]
        ]
        
        for frameworks in framework_combinations:
            result = await analyzer.analyze_document(
                document_content=sample_document,
                frameworks=frameworks,
                analysis_depth="standard"
            )
            
            assert "compliance_issues" in result
            assert "risk_score" in result


class TestComplianceAnalyzerIntegration:
    """Integration tests for the ComplianceAnalyzer."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_api_call(self):
        """Test with real API call (requires valid API key)."""
        # Skip if no API key is available
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key or api_key == "test_key_here":
            pytest.skip("No valid API key available for integration test")
        
        analyzer = ComplianceAnalyzer(api_key=api_key)
        sample_document = "This is a test privacy policy document."
        
        try:
            result = await analyzer.analyze_document(
                document_content=sample_document,
                frameworks=["gdpr"],
                analysis_depth="basic"
            )
            
            # Verify basic structure
            assert "compliance_issues" in result
            assert "risk_score" in result
            assert isinstance(result["risk_score"], (int, float))
            
        except Exception as e:
            pytest.fail(f"Integration test failed: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
