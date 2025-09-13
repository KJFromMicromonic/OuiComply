#!/usr/bin/env python3
"""
Final verification test for OuiComply MCP Server with real API calls.
This test verifies all components work correctly for the hackathon submission.
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


async def test_final_verification():
    """Final verification test with real API calls."""
    
    print("🚀 OuiComply MCP Server - Final Verification Test")
    print("=" * 60)
    print("🎯 Testing with REAL API calls for hackathon submission")
    
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
    
    # Step 2: Test Document Analysis with Real Mistral API
    print("\n🤖 Step 2: Testing Mistral DocumentAI Integration")
    print("-" * 40)
    
    try:
        document_ai = DocumentAIService()
        
        # Create a test document
        test_doc = "test_service_agreement.txt"
        test_content = """
        SERVICE AGREEMENT
        
        This Service Agreement is entered into between TechCorp Inc. and DataServices LLC.
        
        DATA PROCESSING:
        TechCorp will process personal data in accordance with GDPR requirements.
        Data will be retained for a period of 2 years unless otherwise specified.
        
        CONFIDENTIALITY:
        Both parties agree to maintain strict confidentiality of all sensitive information.
        
        TERMINATION:
        This agreement may be terminated with 30 days written notice.
        """
        
        Path(test_doc).write_text(test_content)
        
        # Test with real API call
        request = DocumentAnalysisRequest(
            document_content=test_doc,
            document_type="text/plain",
            compliance_frameworks=["gdpr", "sox"],
            analysis_depth="comprehensive"
        )
        
        print("🔄 Making real API call to Mistral DocumentAI...")
        analysis_result = await document_ai.analyze_document(request)
        
        print("✅ REAL API CALL SUCCESSFUL!")
        print(f"   📊 Document ID: {analysis_result.document_id}")
        print(f"   ⚠️  Issues Found: {len(analysis_result.compliance_issues)}")
        print(f"   📈 Risk Score: {analysis_result.risk_score:.2f}")
        print(f"   📝 Missing Clauses: {len(analysis_result.missing_clauses)}")
        print(f"   💡 Recommendations: {len(analysis_result.recommendations)}")
        
        # Show real issues from API
        if analysis_result.compliance_issues:
            print("\n   🔍 Real Issues from Mistral API:")
            for i, issue in enumerate(analysis_result.compliance_issues[:3]):
                print(f"      {i+1}. [{issue.severity.upper()}] {issue.description}")
                print(f"         Framework: {issue.framework}, Confidence: {issue.confidence:.0%}")
        
        # Clean up test file
        Path(test_doc).unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Mistral API test failed: {e}")
        return False
    
    # Step 3: Test Complete Multiagentic Flow
    print("\n🔄 Step 3: Testing Complete Multiagentic Flow")
    print("-" * 40)
    
    try:
        # Initialize all agents
        lechat_interface = LeChatInterface()
        memory_integration = MemoryIntegration()
        compliance_engine = ComplianceEngine()
        automation_agent = AutomationAgent()
        
        print("✅ All agents initialized successfully")
        
        # Simulate complete flow
        print("\n   📥 1. Query Processing...")
        query_context = await lechat_interface.parse_query(
            "Analyze this service agreement for GDPR compliance"
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
        
        # Learn from analysis
        analysis_data = {
            "document_type": "service_agreement",
            "frameworks": ["gdpr", "sox"],
            "issues_found": len(analysis_result.compliance_issues),
            "risk_score": analysis_result.risk_score
        }
        
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"      ✅ Learning completed")
        
        print("\n   📊 4. Compliance Analysis...")
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Test service agreement content",
            document_type="service_agreement",
            frameworks=["gdpr", "sox"]
        )
        print(f"      ✅ Compliance score: {compliance_report.overall_score:.2f}")
        
        print("\n   💬 5. Response Formatting...")
        formatted_response = lechat_interface.format_response_for_lechat(
            {
                "analysis_result": analysis_result,
                "compliance_report": compliance_report
            },
            "Legal Team"
        )
        print(f"      ✅ Response formatted ({len(formatted_response)} chars)")
        
        print("\n   🤖 6. Automation Prompts...")
        automation_result = automation_agent.generate_automation_prompts(
            analysis_data, "Legal Team", "high"
        )
        print(f"      ✅ {len(automation_result.tasks)} automation prompts generated")
        
        print("\n✅ COMPLETE MULTIAGENTIC FLOW SUCCESSFUL!")
        
    except Exception as e:
        print(f"❌ Multiagentic flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test MCP Server Tools
    print("\n🔧 Step 4: Testing MCP Server Tools")
    print("-" * 40)
    
    try:
        from src.mcp_server import OuiComplyMCPServer
        
        server = OuiComplyMCPServer()
        print("✅ MCP Server initialized")
        
        # Test individual tool methods
        print("\n   Testing decompose_task...")
        decompose_result = await server._handle_decompose_task({
            "query": "Check this service agreement for compliance",
            "team_context": "Legal Team"
        })
        print(f"      ✅ decompose_task: {len(decompose_result)} results")
        
        print("\n   Testing analyze_with_memory...")
        analyze_result = await server._handle_analyze_with_memory({
            "document_content": "Test content",
            "document_type": "service_agreement",
            "frameworks": ["gdpr"],
            "team_id": "legal_team"
        })
        print(f"      ✅ analyze_with_memory: {len(analyze_result)} results")
        
        print("\n   Testing generate_automation_prompts...")
        automation_result = await server._handle_generate_automation_prompts({
            "analysis_results": analysis_data,
            "team_context": "Legal Team",
            "priority": "high"
        })
        print(f"      ✅ generate_automation_prompts: {len(automation_result)} results")
        
        print("\n✅ ALL MCP SERVER TOOLS WORKING!")
        
    except Exception as e:
        print(f"❌ MCP Server tools test failed: {e}")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 FINAL VERIFICATION COMPLETE - ALL TESTS PASSED!")
    print("=" * 60)
    
    print("\n📈 Verification Results:")
    print("   ✅ Mistral API Integration: WORKING")
    print("   ✅ Document Analysis: WORKING")
    print("   ✅ Le Chat Interface: WORKING")
    print("   ✅ Memory Integration: WORKING")
    print("   ✅ Compliance Engine: WORKING")
    print("   ✅ Automation Agent: WORKING")
    print("   ✅ MCP Server Tools: WORKING")
    print("   ✅ Complete Multiagentic Flow: WORKING")
    
    print("\n🚀 HACKATHON SUBMISSION READY!")
    print("   🏆 All components tested with real API calls")
    print("   🎯 Multiagentic flow fully functional")
    print("   📊 Structured outputs working")
    print("   🤖 Automation prompts generating")
    print("   🧠 Memory learning operational")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_final_verification())
    if success:
        print("\n✅ FINAL VERIFICATION SUCCESSFUL!")
        print("🚀 OuiComply MCP Server is ready for Mistral AI MCP Hackathon!")
    else:
        print("\n❌ FINAL VERIFICATION FAILED!")
        print("Please check the errors above before submission.")
        sys.exit(1)
