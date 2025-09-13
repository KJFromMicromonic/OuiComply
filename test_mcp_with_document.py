#!/usr/bin/env python3
"""
Test script to test the MCP Server with a real document from the docs folder.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from src.tools.compliance_engine import ComplianceEngine
from src.tools.lechat_interface import LeChatInterface
from src.tools.memory_integration import MemoryIntegration
from src.tools.automation_agent import AutomationAgent


async def test_mcp_with_document():
    """Test the MCP server components with a real document."""
    
    print("🚀 Testing OuiComply MCP Server with Real Document")
    print("=" * 60)
    
    # Initialize services
    print("\n📋 Initializing Services...")
    document_ai = DocumentAIService()
    compliance_engine = ComplianceEngine()
    lechat_interface = LeChatInterface()
    memory_integration = MemoryIntegration()
    automation_agent = AutomationAgent()
    
    # Test document path
    test_document = "docs/IntegrityFunds_20200121_485BPOS_EX-99.E%20UNDR%20CONTR_11948727_EX-99.E%20UNDR%20CONTR_Service%20Agreement (1).pdf"
    
    print(f"\n📄 Testing with document: {test_document}")
    
    # Check if document exists
    if not Path(test_document).exists():
        print(f"❌ Document not found: {test_document}")
        return
    
    print("✅ Document found!")
    
    # Test 1: Document Analysis
    print("\n🔍 Test 1: Document Analysis")
    print("-" * 30)
    
    try:
        request = DocumentAnalysisRequest(
            document_content=test_document,
            document_type="application/pdf",
            compliance_frameworks=["gdpr", "sox", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        analysis_result = await document_ai.analyze_document(request)
        
        print(f"✅ Document Analysis Complete!")
        print(f"   📊 Document ID: {analysis_result.document_id}")
        print(f"   📄 Document Type: {analysis_result.document_type}")
        print(f"   ⚠️  Issues Found: {len(analysis_result.compliance_issues)}")
        print(f"   📈 Risk Score: {analysis_result.risk_score:.2f}")
        print(f"   📝 Missing Clauses: {len(analysis_result.missing_clauses)}")
        print(f"   💡 Recommendations: {len(analysis_result.recommendations)}")
        
        # Show some issues
        if analysis_result.compliance_issues:
            print("\n   🔍 Sample Issues:")
            for i, issue in enumerate(analysis_result.compliance_issues[:3]):
                print(f"      {i+1}. [{issue.severity.upper()}] {issue.description}")
                print(f"         Framework: {issue.framework}")
                print(f"         Confidence: {issue.confidence:.2f}")
        
    except Exception as e:
        print(f"❌ Document Analysis Failed: {str(e)}")
        return
    
    # Test 2: Le Chat Interface
    print("\n💬 Test 2: Le Chat Interface")
    print("-" * 30)
    
    try:
        # Simulate query parsing
        query = "Analyze this service agreement for GDPR compliance issues"
        query_context = lechat_interface.parse_query(query)
        
        print(f"✅ Query Parsed: {query_context.intent}")
        print(f"   📋 Frameworks: {query_context.compliance_frameworks}")
        print(f"   🎯 Priority: {query_context.priority}")
        
        # Simulate document fetching
        fetch_result = lechat_interface.fetch_document_from_google_drive(
            "IntegrityFunds Service Agreement", 
            "Legal Team"
        )
        
        print(f"✅ Document Fetch Simulated: {fetch_result.status}")
        print(f"   📄 Document: {fetch_result.document_name}")
        print(f"   👥 Team: {fetch_result.team_context}")
        
    except Exception as e:
        print(f"❌ Le Chat Interface Test Failed: {str(e)}")
    
    # Test 3: Memory Integration
    print("\n🧠 Test 3: Memory Integration")
    print("-" * 30)
    
    try:
        team_id = "legal_team"
        
        # Get team memory
        memory = memory_integration.get_team_memory(team_id)
        print(f"✅ Team Memory Retrieved for: {team_id}")
        print(f"   📚 Rules: {len(memory.compliance_rules)}")
        print(f"   ⚠️  Pitfalls: {len(memory.pitfall_patterns)}")
        print(f"   📊 Behaviors: {len(memory.behavioral_memory)}")
        
        # Simulate learning from analysis
        analysis_data = {
            "document_type": "service_agreement",
            "frameworks": ["gdpr", "sox"],
            "issues_found": len(analysis_result.compliance_issues),
            "risk_score": analysis_result.risk_score
        }
        
        memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"✅ Learning from Analysis Complete")
        
        # Get suggestions
        suggestions = memory_integration.suggest_improvements(team_id)
        print(f"💡 Suggestions: {len(suggestions)}")
        
    except Exception as e:
        print(f"❌ Memory Integration Test Failed: {str(e)}")
    
    # Test 4: Automation Agent
    print("\n🤖 Test 4: Automation Agent")
    print("-" * 30)
    
    try:
        # Generate automation prompts
        automation_result = automation_agent.generate_automation_prompts(
            analysis_results=analysis_data,
            team_context="legal_team",
            priority="high"
        )
        
        print(f"✅ Automation Prompts Generated")
        print(f"   📋 Tasks: {len(automation_result.tasks)}")
        print(f"   📧 Notifications: {len(automation_result.notifications)}")
        print(f"   🐛 Issues: {len(automation_result.issues)}")
        
        # Show sample prompts
        if automation_result.tasks:
            print(f"\n   📝 Sample Linear Task Prompt:")
            print(f"      {automation_result.tasks[0]['prompt'][:100]}...")
        
    except Exception as e:
        print(f"❌ Automation Agent Test Failed: {str(e)}")
    
    # Test 5: Complete Multiagentic Flow
    print("\n🔄 Test 5: Complete Multiagentic Flow")
    print("-" * 30)
    
    try:
        # Simulate the complete flow
        print("1. 📥 Query Processing...")
        query_context = lechat_interface.parse_query("Check this service agreement for compliance")
        
        print("2. 📄 Document Analysis...")
        # (Already done above)
        
        print("3. 🧠 Memory Integration...")
        memory_integration.learn_from_analysis(team_id, analysis_data)
        
        print("4. 📊 Compliance Analysis...")
        compliance_report = compliance_engine.analyze_document(
            analysis_result.compliance_issues,
            analysis_result.missing_clauses,
            analysis_result.recommendations
        )
        
        print("5. 💬 Response Formatting...")
        formatted_response = lechat_interface.format_response_for_lechat(
            {
                "analysis_result": analysis_result,
                "compliance_report": compliance_report
            },
            "legal_team"
        )
        
        print("6. 🤖 Automation Prompts...")
        automation_result = automation_agent.generate_automation_prompts(
            analysis_data, "legal_team", "high"
        )
        
        print("✅ Complete Multiagentic Flow Successful!")
        print(f"   📊 Total Issues: {len(analysis_result.compliance_issues)}")
        print(f"   📈 Risk Score: {analysis_result.risk_score:.2f}")
        print(f"   🎯 Compliance Score: {compliance_report.overall_score:.2f}")
        print(f"   📝 Automation Tasks: {len(automation_result.tasks)}")
        
    except Exception as e:
        print(f"❌ Complete Flow Test Failed: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 MCP Server Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_with_document())
