"""
Tests for MCP server implementation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import TextContent

from src.mcp_server import OuiComplyMCPServer


class TestOuiComplyMCPServer:
    """Test cases for OuiComply MCP Server."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.mistral_api_key = "test_api_key"
        config.server_name = "ouicomply-mcp"
        config.server_version = "0.1.0"
        return config
    
    @pytest.fixture
    def mcp_server(self, mock_config):
        """Create MCP server instance for testing."""
        with patch('src.mcp_server.get_config', return_value=mock_config), \
             patch('src.mcp_server.ComplianceEngine'), \
             patch('src.mcp_server.LeChatMemoryService'):
            return OuiComplyMCPServer()
    
    def test_server_initialization(self, mcp_server):
        """Test server initialization."""
        assert mcp_server.config is not None
        assert mcp_server.server is not None
        assert mcp_server.compliance_engine is not None
        assert mcp_server.memory_service is not None
        assert isinstance(mcp_server._reports_cache, dict)
    
    @pytest.mark.asyncio
    async def test_handle_analyze_document_compliance(self, mcp_server):
        """Test document compliance analysis handler."""
        # Mock the compliance engine
        mock_report = Mock()
        mock_report.report_id = "report123"
        mock_report.document_id = "doc123"
        mock_report.overall_status.value = "compliant"
        mock_report.risk_level.value = "low"
        mock_report.risk_score = 0.2
        mock_report.frameworks_analyzed = ["gdpr"]
        mock_report.issues = []
        mock_report.missing_clauses = []
        mock_report.summary = "Document is compliant"
        
        mcp_server.compliance_engine.analyze_document_compliance = AsyncMock(return_value=mock_report)
        
        arguments = {
            "document_content": "test document content",
            "compliance_frameworks": ["gdpr"],
            "analysis_depth": "comprehensive"
        }
        
        result = await mcp_server._handle_analyze_document_compliance(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "COMPLIANCE ANALYSIS COMPLETED" in result[0].text
        assert "report123" in result[0].text
        assert "compliant" in result[0].text.upper()
        
        # Check that report was cached
        assert "report123" in mcp_server._reports_cache
    
    @pytest.mark.asyncio
    async def test_handle_generate_compliance_report_found(self, mcp_server):
        """Test compliance report generation when report is found."""
        # Mock a cached report
        mock_report = Mock()
        mock_report.report_id = "report123"
        mcp_server._reports_cache["report123"] = mock_report
        
        # Mock the compliance engine export methods
        mcp_server.compliance_engine.export_report_json = Mock(return_value='{"report": "data"}')
        mcp_server.compliance_engine.export_report_markdown = Mock(return_value="# Report")
        
        # Test JSON format
        arguments = {"report_id": "report123", "format": "json"}
        result = await mcp_server._handle_generate_compliance_report(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert '{"report": "data"}' in result[0].text
        
        # Test Markdown format
        arguments = {"report_id": "report123", "format": "markdown"}
        result = await mcp_server._handle_generate_compliance_report(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "# Report" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_generate_compliance_report_not_found(self, mcp_server):
        """Test compliance report generation when report is not found."""
        arguments = {"report_id": "nonexistent", "format": "json"}
        result = await mcp_server._handle_generate_compliance_report(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Report not found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_store_assessment_in_memory_success(self, mcp_server):
        """Test storing assessment in memory successfully."""
        # Mock a cached report
        mock_report = Mock()
        mock_report.report_id = "report123"
        mcp_server._reports_cache["report123"] = mock_report
        
        # Mock the memory service
        mcp_server.memory_service.store_compliance_assessment = AsyncMock(return_value="memory123")
        
        arguments = {
            "report_id": "report123",
            "user_id": "user123",
            "organization_id": "org123"
        }
        
        result = await mcp_server._handle_store_assessment_in_memory(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "memory123" in result[0].text
        
        # Verify the memory service was called correctly
        mcp_server.memory_service.store_compliance_assessment.assert_called_once_with(
            report=mock_report,
            user_id="user123",
            organization_id="org123"
        )
    
    @pytest.mark.asyncio
    async def test_handle_store_assessment_in_memory_error(self, mcp_server):
        """Test storing assessment in memory with error."""
        # Mock a cached report
        mock_report = Mock()
        mock_report.report_id = "report123"
        mcp_server._reports_cache["report123"] = mock_report
        
        # Mock the memory service to raise an exception
        mcp_server.memory_service.store_compliance_assessment = AsyncMock(
            side_effect=Exception("Memory service error")
        )
        
        arguments = {"report_id": "report123"}
        
        result = await mcp_server._handle_store_assessment_in_memory(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Failed to store assessment in memory" in result[0].text
        assert "Memory service error" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_search_compliance_memories_success(self, mcp_server):
        """Test searching compliance memories successfully."""
        # Mock search results
        mock_results = [
            Mock(
                title="Test Memory 1",
                category="compliance_assessment",
                relevance_score=0.9,
                created_at="2024-01-01T00:00:00Z",
                content="Test content 1"
            ),
            Mock(
                title="Test Memory 2",
                category="compliance_assessment",
                relevance_score=0.7,
                created_at="2024-01-02T00:00:00Z",
                content="Test content 2"
            )
        ]
        
        mcp_server.memory_service.search_memories = AsyncMock(return_value=mock_results)
        
        arguments = {
            "query": "test query",
            "category": "compliance_assessment",
            "limit": 10
        }
        
        result = await mcp_server._handle_search_compliance_memories(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Found 2 matching memories" in result[0].text
        assert "Test Memory 1" in result[0].text
        assert "Test Memory 2" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_search_compliance_memories_no_results(self, mcp_server):
        """Test searching compliance memories with no results."""
        mcp_server.memory_service.search_memories = AsyncMock(return_value=[])
        
        arguments = {"query": "test query"}
        
        result = await mcp_server._handle_search_compliance_memories(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "No matching memories found" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_generate_audit_trail_success(self, mcp_server):
        """Test generating audit trail successfully."""
        # Mock a cached report
        mock_report = Mock()
        mock_report.report_id = "report123"
        mcp_server._reports_cache["report123"] = mock_report
        
        # Mock the compliance engine
        mcp_server.compliance_engine.generate_audit_trail_entry = AsyncMock(
            return_value="# Audit Trail Content"
        )
        
        arguments = {
            "report_id": "report123",
            "repository": "test/repo",
            "branch": "main"
        }
        
        result = await mcp_server._handle_generate_audit_trail(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Audit Trail Entry Generated" in result[0].text
        assert "test/repo" in result[0].text
        assert "main" in result[0].text
        assert "# Audit Trail Content" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_get_compliance_history_success(self, mcp_server):
        """Test getting compliance history successfully."""
        # Mock history results
        mock_history = [
            Mock(
                title="History Entry 1",
                category="compliance_assessment",
                relevance_score=0.8,
                created_at="2024-01-01T00:00:00Z",
                tags=["gdpr", "compliance"]
            ),
            Mock(
                title="History Entry 2",
                category="compliance_assessment",
                relevance_score=0.6,
                created_at="2024-01-02T00:00:00Z",
                tags=["sox", "compliance"]
            )
        ]
        
        mcp_server.memory_service.get_compliance_history = AsyncMock(return_value=mock_history)
        
        arguments = {
            "user_id": "user123",
            "limit": 20
        }
        
        result = await mcp_server._handle_get_compliance_history(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Compliance History (2 entries)" in result[0].text
        assert "History Entry 1" in result[0].text
        assert "History Entry 2" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_analyze_risk_trends_success(self, mcp_server):
        """Test analyzing risk trends successfully."""
        # Mock trends data
        mock_trends = {
            "total_assessments": 10,
            "average_risk_score": 0.6,
            "total_issues": 25,
            "total_critical_issues": 3,
            "trend_direction": "improving",
            "risk_level": "medium"
        }
        
        mcp_server.memory_service.get_risk_trends = AsyncMock(return_value=mock_trends)
        
        arguments = {
            "user_id": "user123",
            "days": 30
        }
        
        result = await mcp_server._handle_analyze_risk_trends(arguments)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Risk Trend Analysis" in result[0].text
        assert "10" in result[0].text  # Total assessments
        assert "0.60" in result[0].text  # Average risk score
        assert "25" in result[0].text  # Total issues
        assert "3" in result[0].text  # Critical issues
        assert "improving" in result[0].text  # Trend direction
        assert "medium" in result[0].text  # Risk level
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown_tool(self, mcp_server):
        """Test handling unknown tool calls."""
        result = await mcp_server.handle_call_tool("unknown_tool", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Unknown tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_exception(self, mcp_server):
        """Test handling tool call exceptions."""
        # Mock a tool handler to raise an exception
        mcp_server._handle_analyze_document_compliance = AsyncMock(
            side_effect=Exception("Test error")
        )
        
        result = await mcp_server.handle_call_tool("analyze_document_compliance", {})
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error executing tool" in result[0].text
        assert "Test error" in result[0].text
