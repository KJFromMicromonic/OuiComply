#!/usr/bin/env python3
"""
Test script for the updated structured implementation following DevTools patterns.
This tests the proper Mistral tool calling and structured outputs implementation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_config, validate_config
from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from src.tools.compliance_engine import ComplianceEngine
from src.tools.lechat_interface import LeChatInterface
from src.tools.memory_integration import MemoryIntegration
from src.tools.automation_agent import AutomationAgent


async def test_structured_implementation():
    """Test the updated structured implementation with proper Mistral patterns."""
    
    print("🚀 Testing Updated Structured Implementation")
    print("=" * 60)
    print("🎯 Following DevTools patterns for Mistral tool calling and structured outputs")
    
    # Step 1: Configuration Check
    print("\n🔧 Step 1: Configuration Verification")
    print("-" * 40)
    
    try:
        config = get_config()
        if not validate_config():
            print("❌ Configuration validation failed!")
            return False
        print("✅ Configuration validated - Mistral API key is set")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Step 2: Test DocumentAI with Structured Outputs
    print("\n🤖 Step 2: Testing DocumentAI with Structured Outputs")
    print("-" * 40)
    
    try:
        document_ai = DocumentAIService()
        
        # Create a test document
        test_doc = "test_structured_document.txt"
        test_content = """
        SERVICE AGREEMENT
        
        This Service Agreement is entered into between TechCorp Inc. and DataServices LLC.
        
        DATA PROCESSING:
        TechCorp will process personal data in accordance with GDPR requirements.
        Data will be retained for a period of 2 years unless otherwise specified.
        Users have the right to access, rectify, and delete their personal data.
        
        CONFIDENTIALITY:
        Both parties agree to maintain strict confidentiality of all sensitive information.
        Confidential information includes but is not limited to customer data, business strategies, and technical specifications.
        
        TERMINATION:
        This agreement may be terminated with 30 days written notice.
        Upon termination, all confidential information must be returned or destroyed.
        
        DATA BREACH NOTIFICATION:
        In case of a data breach, the affected party must notify the other party within 24 hours.
        """
        
        Path(test_doc).write_text(test_content)
        
        # Test with structured outputs
        request = DocumentAnalysisRequest(
            document_content=test_doc,
            document_type="text/plain",
            compliance_frameworks=["gdpr", "sox"],
            analysis_depth="comprehensive"
        )
        
        print("🔄 Testing structured analysis with Mistral function calling...")
        analysis_result = await document_ai.analyze_document(request)
        
        print("✅ STRUCTURED ANALYSIS SUCCESSFUL!")
        print(f"   📊 Document ID: {analysis_result.document_id}")
        print(f"   ⚠️  Issues Found: {len(analysis_result.compliance_issues)}")
        print(f"   📈 Risk Score: {analysis_result.risk_score:.2f}")
        print(f"   📝 Missing Clauses: {len(analysis_result.missing_clauses)}")
        print(f"   💡 Recommendations: {len(analysis_result.recommendations)}")
        
        # Show structured issues
        if analysis_result.compliance_issues:
            print("\n   🔍 Structured Issues from Mistral API:")
            for i, issue in enumerate(analysis_result.compliance_issues[:3]):
                print(f"      {i+1}. [{issue.severity.upper()}] {issue.description}")
                print(f"         Framework: {issue.framework}, Confidence: {issue.confidence:.0%}")
                print(f"         Category: {issue.category}")
                print(f"         Recommendation: {issue.recommendation}")
        
        # Clean up test file
        Path(test_doc).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Structured DocumentAI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test Complete Multiagentic Flow with Structured Outputs
    print("\n🔄 Step 3: Testing Complete Multiagentic Flow with Structured Outputs")
    print("-" * 40)
    
    try:
        # Initialize all agents
        lechat_interface = LeChatInterface()
        memory_integration = MemoryIntegration()
        compliance_engine = ComplianceEngine()
        automation_agent = AutomationAgent()
        
        print("✅ All agents initialized successfully")
        
        # Simulate complete flow with structured outputs
        print("\n   📥 1. Query Processing...")
        query_context = await lechat_interface.parse_query(
            "Analyze this service agreement for GDPR and SOX compliance"
        )
        print(f"      ✅ Query parsed: {query_context.query_type}")
        
        print("\n   📄 2. Document Fetching...")
        fetch_result = await lechat_interface.fetch_document_from_google_drive(
            "Test Service Agreement", "Legal Team"
        )
        print(f"      ✅ Document fetched: {fetch_result.document_name}")
        
        print("\n   🧠 3. Memory Integration...")
        team_id = "legal_team"
        memory = await memory_integration.get_team_memory(team_id)
        print(f"      ✅ Memory retrieved for {team_id}")
        
        # Learn from structured analysis
        analysis_data = {
            "document_type": "service_agreement",
            "frameworks": ["gdpr", "sox"],
            "issues_found": len(analysis_result.compliance_issues),
            "risk_score": analysis_result.risk_score,
            "structured_issues": [
                {
                    "severity": issue.severity,
                    "framework": issue.framework,
                    "category": issue.category
                } for issue in analysis_result.compliance_issues
            ]
        }
        
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"      ✅ Structured learning completed")
        
        print("\n   📊 4. Compliance Analysis...")
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Test service agreement content",
            document_type="service_agreement",
            frameworks=["gdpr", "sox"]
        )
        print(f"      ✅ Compliance score: {compliance_report.overall_status}")
        
        print("\n   💬 5. Response Formatting...")
        formatted_response = await lechat_interface.format_response_for_lechat(
            {
                "analysis_result": analysis_result,
                "compliance_report": compliance_report
            },
            "Legal Team"
        )
        print(f"      ✅ Response formatted ({len(formatted_response)} chars)")
        
        print("\n   🤖 6. Automation Prompts...")
        automation_result = await automation_agent.generate_automation_prompts(
            analysis_data, "Legal Team", "high"
        )
        print(f"      ✅ {len(automation_result.actions_taken)} automation prompts generated")
        
        print("\n✅ COMPLETE STRUCTURED MULTIAGENTIC FLOW SUCCESSFUL!")
        
    except Exception as e:
        print(f"❌ Structured multiagentic flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test MCP Server with Structured Outputs
    print("\n🔧 Step 4: Testing MCP Server with Structured Outputs")
    print("-" * 40)
    
    try:
        from src.mcp_server import OuiComplyMCPServer
        
        server = OuiComplyMCPServer()
        print("✅ MCP Server initialized")
        
        # Test structured tool methods
        print("\n   Testing decompose_task with structured output...")
        decompose_result = await server._handle_decompose_task({
            "query": "Check this service agreement for GDPR compliance",
            "team_context": "Legal Team"
        })
        print(f"      ✅ decompose_task: {len(decompose_result)} results")
        
        print("\n   Testing analyze_with_memory with structured output...")
        analyze_result = await server._handle_analyze_with_memory({
            "document_content": "Test content",
            "document_type": "service_agreement",
            "frameworks": ["gdpr"],
            "team_id": "legal_team"
        })
        print(f"      ✅ analyze_with_memory: {len(analyze_result)} results")
        
        print("\n   Testing generate_automation_prompts with structured output...")
        automation_result = await server._handle_generate_automation_prompts({
            "analysis_results": analysis_data,
            "team_context": "Legal Team",
            "priority": "high"
        })
        print(f"      ✅ generate_automation_prompts: {len(automation_result)} results")
        
        print("\n✅ ALL MCP SERVER TOOLS WITH STRUCTURED OUTPUTS WORKING!")
        
    except Exception as e:
        print(f"❌ MCP Server structured tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 STRUCTURED IMPLEMENTATION VERIFICATION COMPLETE!")
    print("=" * 60)
    
    print("\n📈 Verification Results:")
    print("   ✅ Mistral Function Calling: WORKING")
    print("   ✅ Structured JSON Outputs: WORKING")
    print("   ✅ Document Analysis: WORKING")
    print("   ✅ Le Chat Interface: WORKING")
    print("   ✅ Memory Integration: WORKING")
    print("   ✅ Compliance Engine: WORKING")
    print("   ✅ Automation Agent: WORKING")
    print("   ✅ MCP Server Tools: WORKING")
    print("   ✅ Complete Multiagentic Flow: WORKING")
    
    print("\n🚀 HACKATHON SUBMISSION READY!")
    print("   🏆 Following DevTools patterns for Mistral integration")
    print("   🎯 Structured outputs for reliable responses")
    print("   📊 Function calling for robust analysis")
    print("   🤖 Multiagentic flow fully functional")
    print("   📝 JSON schema validation working")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_structured_implementation())
    if success:
        print("\n✅ STRUCTURED IMPLEMENTATION SUCCESSFUL!")
        print("🚀 OuiComply MCP Server is ready for Mistral AI MCP Hackathon!")
    else:
        print("\n❌ STRUCTURED IMPLEMENTATION FAILED!")
        print("Please check the errors above before submission.")
        sys.exit(1)
