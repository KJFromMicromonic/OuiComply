#!/usr/bin/env python3
"""
Test script to verify MCP Server functionality with real API calls.
This ensures the system works properly for the hackathon submission.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_config, validate_config, print_config_summary
from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from src.tools.compliance_engine import ComplianceEngine
from src.tools.lechat_interface import LeChatInterface
from src.tools.memory_integration import MemoryIntegration
from src.tools.automation_agent import AutomationAgent


async def test_real_api_calls():
    """Test the MCP server with real API calls."""
    
    print("🚀 Testing OuiComply MCP Server with Real API Calls")
    print("=" * 60)
    
    # Step 1: Validate Configuration
    print("\n🔧 Step 1: Configuration Validation")
    print("-" * 30)
    
    try:
        config = get_config()
        print_config_summary()
        
        if not validate_config():
            print("❌ Configuration validation failed!")
            return False
            
        print("✅ Configuration validated successfully!")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
        return False
    
    # Step 2: Test Mistral API Connection
    print("\n🤖 Step 2: Testing Mistral API Connection")
    print("-" * 30)
    
    try:
        document_ai = DocumentAIService()
        print("✅ DocumentAI service initialized")
        
        # Test with a simple document
        test_document = "docs/sample_contract.txt"
        if not Path(test_document).exists():
            # Create a simple test document
            test_content = """
            SERVICE AGREEMENT
            
            This Service Agreement is entered into between Company A and Company B.
            
            DATA PROCESSING:
            Company A will process personal data in accordance with applicable laws.
            
            CONFIDENTIALITY:
            Both parties agree to maintain confidentiality of sensitive information.
            
            TERMINATION:
            This agreement may be terminated with 30 days notice.
            """
            Path(test_document).write_text(test_content)
            print(f"✅ Created test document: {test_document}")
        
        # Test document analysis with real API
        print("🔄 Testing document analysis with Mistral API...")
        request = DocumentAnalysisRequest(
            document_content=test_document,
            document_type="text/plain",
            compliance_frameworks=["gdpr"],
            analysis_depth="basic"
        )
        
        analysis_result = await document_ai.analyze_document(request)
        
        print("✅ Document analysis completed successfully!")
        print(f"   📊 Document ID: {analysis_result.document_id}")
        print(f"   📄 Document Type: {analysis_result.document_type}")
        print(f"   ⚠️  Issues Found: {len(analysis_result.compliance_issues)}")
        print(f"   📈 Risk Score: {analysis_result.risk_score:.2f}")
        print(f"   📝 Missing Clauses: {len(analysis_result.missing_clauses)}")
        print(f"   💡 Recommendations: {len(analysis_result.recommendations)}")
        
        # Show sample issues
        if analysis_result.compliance_issues:
            print("\n   🔍 Sample Issues:")
            for i, issue in enumerate(analysis_result.compliance_issues[:2]):
                print(f"      {i+1}. [{issue.severity.upper()}] {issue.description}")
                print(f"         Framework: {issue.framework}")
                print(f"         Confidence: {issue.confidence:.2f}")
        
    except Exception as e:
        print(f"❌ Mistral API test failed: {str(e)}")
        print("   This might be due to API limits or network issues")
        return False
    
    # Step 3: Test Le Chat Interface
    print("\n💬 Step 3: Testing Le Chat Interface")
    print("-" * 30)
    
    try:
        lechat_interface = LeChatInterface()
        
        # Test query parsing
        query = "Analyze this service agreement for GDPR compliance"
        query_context = await lechat_interface.parse_query(query)
        
        print("✅ Query parsing successful!")
        print(f"   📄 Document: {query_context.document_name}")
        print(f"   👥 Team: {query_context.team}")
        print(f"   🔍 Query Type: {query_context.query_type}")
        print(f"   ⚡ Urgency: {query_context.urgency}")
        
        # Test document fetching simulation
        fetch_result = await lechat_interface.fetch_document_from_google_drive(
            "Test Service Agreement", "Legal Team"
        )
        
        print("✅ Document fetching simulation successful!")
        print(f"   📄 Document: {fetch_result.document_name}")
        print(f"   📊 Document ID: {fetch_result.document_id}")
        print(f"   ✅ Success: {fetch_result.success}")
        
    except Exception as e:
        print(f"❌ Le Chat Interface test failed: {str(e)}")
        return False
    
    # Step 4: Test Memory Integration
    print("\n🧠 Step 4: Testing Memory Integration")
    print("-" * 30)
    
    try:
        memory_integration = MemoryIntegration()
        team_id = "legal_team"
        
        # Test memory retrieval
        memory = await memory_integration.get_team_memory(team_id)
        print("✅ Memory integration successful!")
        print(f"   👥 Team: {team_id}")
        print(f"   📚 Compliance Rules: {len(memory.get('compliance_rules', []))}")
        print(f"   ⚠️  Pitfall Patterns: {len(memory.get('pitfall_patterns', []))}")
        
        # Test learning
        analysis_data = {
            "document_type": "service_agreement",
            "frameworks": ["gdpr"],
            "issues_found": len(analysis_result.compliance_issues),
            "risk_score": analysis_result.risk_score
        }
        
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print("✅ Learning from analysis successful!")
        
        # Test suggestions
        suggestions = await memory_integration.suggest_improvements(team_id)
        print(f"💡 Suggestions generated: {len(suggestions)}")
        
    except Exception as e:
        print(f"❌ Memory Integration test failed: {str(e)}")
        return False
    
    # Step 5: Test Compliance Engine
    print("\n📊 Step 5: Testing Compliance Engine")
    print("-" * 30)
    
    try:
        compliance_engine = ComplianceEngine()
        
        # Test compliance analysis
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Test service agreement content",
            document_type="service_agreement",
            frameworks=["gdpr"],
            analysis_depth="basic"
        )
        
        print("✅ Compliance analysis successful!")
        print(f"   📊 Overall Score: {compliance_report.overall_score:.2f}")
        print(f"   🔴 Critical Issues: {compliance_report.critical_issues}")
        print(f"   🟠 High Issues: {compliance_report.high_issues}")
        print(f"   🟡 Medium Issues: {compliance_report.medium_issues}")
        print(f"   🟢 Low Issues: {compliance_report.low_issues}")
        
    except Exception as e:
        print(f"❌ Compliance Engine test failed: {str(e)}")
        return False
    
    # Step 6: Test Automation Agent
    print("\n🤖 Step 6: Testing Automation Agent")
    print("-" * 30)
    
    try:
        automation_agent = AutomationAgent()
        
        # Test automation prompt generation
        automation_result = automation_agent.generate_automation_prompts(
            analysis_results=analysis_data,
            team_context="legal_team",
            priority="high"
        )
        
        print("✅ Automation prompt generation successful!")
        print(f"   📋 Linear Tasks: {len(automation_result.tasks)}")
        print(f"   📧 Slack Notifications: {len(automation_result.notifications)}")
        print(f"   🐛 GitHub Issues: {len(automation_result.issues)}")
        
        # Show sample prompt
        if automation_result.tasks:
            print(f"\n   📝 Sample Linear Task Prompt:")
            print(f"      {automation_result.tasks[0]['prompt'][:100]}...")
        
    except Exception as e:
        print(f"❌ Automation Agent test failed: {str(e)}")
        return False
    
    # Step 7: Test Complete Multiagentic Flow
    print("\n🔄 Step 7: Testing Complete Multiagentic Flow")
    print("-" * 30)
    
    try:
        print("1. 📥 Query Processing...")
        query_context = await lechat_interface.parse_query("Check this service agreement for compliance")
        print(f"   ✅ Query processed: {query_context.query_type}")
        
        print("2. 📄 Document Analysis...")
        # Use the analysis result from earlier
        print(f"   ✅ Analysis completed: {len(analysis_result.compliance_issues)} issues found")
        
        print("3. 🧠 Memory Integration...")
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"   ✅ Memory updated for {team_id}")
        
        print("4. 📊 Compliance Analysis...")
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Test content",
            frameworks=["gdpr"]
        )
        print(f"   ✅ Compliance score: {compliance_report.overall_score:.2f}")
        
        print("5. 🤖 Automation Prompts...")
        automation_result = automation_agent.generate_automation_prompts(
            analysis_data, "legal_team", "high"
        )
        print(f"   ✅ {len(automation_result.tasks)} automation prompts generated")
        
        print("\n✅ Complete Multiagentic Flow Successful!")
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {str(e)}")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 ALL API TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📈 Test Results Summary:")
    print("   ✅ Mistral API: Working")
    print("   ✅ Document Analysis: Working")
    print("   ✅ Le Chat Interface: Working")
    print("   ✅ Memory Integration: Working")
    print("   ✅ Compliance Engine: Working")
    print("   ✅ Automation Agent: Working")
    print("   ✅ Complete Flow: Working")
    
    print("\n🚀 MCP Server is ready for hackathon submission!")
    print("   All components are functioning correctly with real API calls.")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_real_api_calls())
    if success:
        print("\n✅ All tests passed! MCP Server is fully functional.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
