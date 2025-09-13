#!/usr/bin/env python3
"""
Simple test script to test the MCP Server components without API calls.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.compliance_engine import ComplianceEngine, ComplianceIssue
from src.tools.lechat_interface import LeChatInterface
from src.tools.memory_integration import MemoryIntegration
from src.tools.automation_agent import AutomationAgent


async def test_mcp_components():
    """Test the MCP server components with mock data."""
    
    print("🚀 Testing OuiComply MCP Server Components")
    print("=" * 60)
    
    # Initialize services
    print("\n📋 Initializing Services...")
    compliance_engine = ComplianceEngine()
    lechat_interface = LeChatInterface()
    memory_integration = MemoryIntegration()
    automation_agent = AutomationAgent()
    
    print("✅ All services initialized!")
    
    # Test 1: Le Chat Interface
    print("\n💬 Test 1: Le Chat Interface")
    print("-" * 30)
    
    try:
        # Test query parsing
        query = "Analyze this service agreement for GDPR compliance issues"
        query_context = await lechat_interface.parse_query(query)
        
        print(f"✅ Query Parsed Successfully!")
        print(f"   📄 Document: {query_context.document_name}")
        print(f"   👥 Team: {query_context.team}")
        print(f"   🔍 Query Type: {query_context.query_type}")
        print(f"   ⚡ Urgency: {query_context.urgency}")
        
        # Test document fetching simulation
        fetch_result = await lechat_interface.fetch_document_from_google_drive(
            "IntegrityFunds Service Agreement", 
            "Legal Team"
        )
        
        print(f"✅ Document Fetch Simulated Successfully!")
        print(f"   📄 Document: {fetch_result.document_name}")
        print(f"   📊 Document ID: {fetch_result.document_id}")
        print(f"   ✅ Success: {fetch_result.success}")
        print(f"   📏 Size: {fetch_result.size} bytes")
        
    except Exception as e:
        print(f"❌ Le Chat Interface Test Failed: {str(e)}")
        return
    
    # Test 2: Memory Integration
    print("\n🧠 Test 2: Memory Integration")
    print("-" * 30)
    
    try:
        team_id = "legal_team"
        
        # Get team memory
        memory = await memory_integration.get_team_memory(team_id)
        print(f"✅ Team Memory Retrieved Successfully!")
        print(f"   👥 Team: {team_id}")
        print(f"   📚 Compliance Rules: {len(memory.get('compliance_rules', []))}")
        print(f"   ⚠️  Pitfall Patterns: {len(memory.get('pitfall_patterns', []))}")
        print(f"   📊 Behavioral Memory: {len(memory.get('behavioral_memory', []))}")
        
        # Test learning from analysis
        analysis_data = {
            "document_type": "service_agreement",
            "frameworks": ["gdpr", "sox"],
            "issues_found": 3,
            "risk_score": 0.75
        }
        
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"✅ Learning from Analysis Complete!")
        
        # Get suggestions
        suggestions = await memory_integration.suggest_improvements(team_id)
        print(f"💡 Improvement Suggestions: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions[:2]):
            print(f"   {i+1}. {suggestion}")
        
    except Exception as e:
        print(f"❌ Memory Integration Test Failed: {str(e)}")
        return
    
    # Test 3: Compliance Engine
    print("\n📊 Test 3: Compliance Engine")
    print("-" * 30)
    
    try:
        # Create mock compliance issues
        mock_issues = [
            ComplianceIssue(
                issue_id="gdpr_001",
                severity="high",
                category="data_processing",
                description="Missing explicit consent mechanism for data processing",
                location="Privacy Policy Section 2",
                recommendation="Add clear consent checkboxes and opt-in mechanisms",
                framework="gdpr",
                confidence=0.85
            ),
            ComplianceIssue(
                issue_id="sox_001",
                severity="critical",
                category="internal_controls",
                description="Insufficient documentation of internal financial controls",
                location="Financial Controls Section",
                recommendation="Implement comprehensive internal control documentation",
                framework="sox",
                confidence=0.95
            )
        ]
        
        mock_missing_clauses = [
            "Data Protection Officer contact information",
            "Cross-border transfer safeguards",
            "Whistleblower protection procedures"
        ]
        
        mock_recommendations = [
            "Review and update GDPR compliance documentation",
            "Conduct regular compliance audits",
            "Implement staff training on compliance requirements"
        ]
        
        # Test compliance analysis
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Mock service agreement content for testing",
            document_type="service_agreement",
            frameworks=["gdpr", "sox"],
            analysis_depth="comprehensive"
        )
        
        print(f"✅ Compliance Analysis Complete!")
        print(f"   📊 Overall Score: {compliance_report.overall_score:.2f}")
        print(f"   ⚠️  Critical Issues: {compliance_report.critical_issues}")
        print(f"   🔴 High Issues: {compliance_report.high_issues}")
        print(f"   🟡 Medium Issues: {compliance_report.medium_issues}")
        print(f"   🟢 Low Issues: {compliance_report.low_issues}")
        print(f"   📝 Missing Clauses: {compliance_report.missing_clauses_count}")
        print(f"   💡 Recommendations: {compliance_report.recommendations_count}")
        
    except Exception as e:
        print(f"❌ Compliance Engine Test Failed: {str(e)}")
        return
    
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
        
        print(f"✅ Automation Prompts Generated Successfully!")
        print(f"   📋 Linear Tasks: {len(automation_result.tasks)}")
        print(f"   📧 Slack Notifications: {len(automation_result.notifications)}")
        print(f"   🐛 GitHub Issues: {len(automation_result.issues)}")
        
        # Show sample prompts
        if automation_result.tasks:
            print(f"\n   📝 Sample Linear Task Prompt:")
            print(f"      {automation_result.tasks[0]['prompt'][:150]}...")
        
        if automation_result.notifications:
            print(f"\n   📧 Sample Slack Notification:")
            print(f"      {automation_result.notifications[0]['prompt'][:150]}...")
        
    except Exception as e:
        print(f"❌ Automation Agent Test Failed: {str(e)}")
        return
    
    # Test 5: Complete Multiagentic Flow
    print("\n🔄 Test 5: Complete Multiagentic Flow")
    print("-" * 30)
    
    try:
        # Simulate the complete flow
        print("1. 📥 Query Processing...")
        query_context = await lechat_interface.parse_query("Check this service agreement for compliance")
        print(f"   ✅ Query: '{query_context.query_type}' for {query_context.document_name}")
        
        print("2. 📄 Document Fetching...")
        fetch_result = await lechat_interface.fetch_document_from_google_drive(
            "Test Service Agreement", "Legal Team"
        )
        print(f"   ✅ Document: {fetch_result.document_name}")
        
        print("3. 🧠 Memory Integration...")
        await memory_integration.learn_from_analysis(team_id, analysis_data)
        print(f"   ✅ Memory updated for {team_id}")
        
        print("4. 📊 Compliance Analysis...")
        compliance_report = await compliance_engine.analyze_document_compliance(
            document_content="Mock service agreement content for testing",
            document_type="service_agreement",
            frameworks=["gdpr", "sox"]
        )
        print(f"   ✅ Compliance score: {compliance_report.overall_score:.2f}")
        
        print("5. 💬 Response Formatting...")
        formatted_response = lechat_interface.format_response_for_lechat(
            {
                "compliance_report": compliance_report,
                "issues": mock_issues
            },
            "legal_team"
        )
        print(f"   ✅ Response formatted ({len(formatted_response)} chars)")
        
        print("6. 🤖 Automation Prompts...")
        automation_result = automation_agent.generate_automation_prompts(
            analysis_data, "legal_team", "high"
        )
        print(f"   ✅ {len(automation_result.tasks)} automation prompts generated")
        
        print("\n✅ Complete Multiagentic Flow Successful!")
        print(f"   📊 Total Issues: {len(mock_issues)}")
        print(f"   📈 Compliance Score: {compliance_report.overall_score:.2f}")
        print(f"   📝 Automation Tasks: {len(automation_result.tasks)}")
        print(f"   📧 Notifications: {len(automation_result.notifications)}")
        print(f"   🐛 Issues: {len(automation_result.issues)}")
        
    except Exception as e:
        print(f"❌ Complete Flow Test Failed: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All MCP Server Component Tests Passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_mcp_components())
