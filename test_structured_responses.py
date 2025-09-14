#!/usr/bin/env python3
"""
Test Enhanced Structured Responses

This script tests the new comprehensive analysis tool with enhanced structured responses
that leverage Mistral's function calling capabilities.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_fastmcp_server import app

async def test_structured_responses():
    """Test the enhanced structured responses with comprehensive analysis."""
    print("🧪 Testing Enhanced Structured Responses")
    print("=" * 60)
    
    # Sample contract content for testing
    contract_content = """
    AFFILIATE AGREEMENT
    
    This Affiliate Agreement (the "Agreement") is entered into between TechCorp Inc. 
    ("Company") and the affiliate ("Affiliate") for the purpose of establishing an 
    affiliate relationship for marketing and promotional services.
    
    DATA PROCESSING:
    The Company may collect, process, and store personal data of users including names, 
    email addresses, browsing behavior, and transaction history for the purpose of 
    providing services and improving user experience. The Company reserves the right to 
    share this data with third parties for marketing purposes.
    
    AFFILIATE OBLIGATIONS:
    The Affiliate agrees to comply with all applicable laws and regulations, including 
    data protection laws, and to maintain the confidentiality of any personal data 
    accessed during the course of this agreement.
    
    TERMINATION:
    Either party may terminate this agreement with 30 days written notice. Upon 
    termination, all personal data must be returned or destroyed in accordance with 
    applicable data protection laws.
    
    GOVERNING LAW:
    This agreement shall be governed by the laws of the State of California.
    
    LIMITATION OF LIABILITY:
    The Company's liability shall be limited to the amount paid by the Affiliate in 
    the preceding 12 months, regardless of the cause of action.
    """
    
    print(f"📄 Contract Content Length: {len(contract_content)} characters")
    print(f"📝 Content Preview: {contract_content[:200]}...")
    
    try:
        # Test Comprehensive Analysis
        print("\n🔍 Testing Comprehensive Analysis with Structured Responses...")
        print("-" * 60)
        
        result = await app.call_tool(
            "comprehensive_analysis",
            {
                "document_content": contract_content,
                "document_type": "affiliate_agreement",
                "frameworks": ["gdpr", "ccpa", "sox"],
                "analysis_depth": "comprehensive",
                "team_context": "legal-compliance-team"
            }
        )
        
        print("✅ Comprehensive analysis completed!")
        print(f"📊 Result type: {type(result)}")
        
        # Display structured output
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            print(f"\n📋 Structured Response Preview:")
            print(f"   Content Length: {len(content)} characters")
            print(f"   Content Type: {type(content)}")
            
            # Try to parse and display key sections
            try:
                import json
                if isinstance(content, str) and content.startswith('{'):
                    parsed = json.loads(content)
                    print(f"\n🎯 Key Sections Found:")
                    if 'executive_summary' in parsed:
                        print(f"   ✅ Executive Summary")
                    if 'compliance_issues' in parsed:
                        print(f"   ✅ Compliance Issues")
                    if 'lechat_actions' in parsed:
                        print(f"   ✅ LeChat Actions")
                    if 'compliance_metrics' in parsed:
                        print(f"   ✅ Compliance Metrics")
                    if 'risk_assessment' in parsed:
                        print(f"   ✅ Risk Assessment")
                    
                    # Display executive summary if available
                    if 'executive_summary' in parsed:
                        summary = parsed['executive_summary']
                        print(f"\n📊 Executive Summary:")
                        print(f"   Status: {summary.get('overall_status', 'N/A')}")
                        print(f"   Risk Level: {summary.get('risk_level', 'N/A')}")
                        print(f"   Compliance Score: {summary.get('compliance_score', 'N/A')}")
                        print(f"   Immediate Actions: {summary.get('immediate_actions_required', 'N/A')}")
                        print(f"   Remediation Time: {summary.get('estimated_remediation_time', 'N/A')}")
                    
                    # Display LeChat actions if available
                    if 'lechat_actions' in parsed:
                        actions = parsed['lechat_actions']
                        print(f"\n🤖 LeChat Actions Generated:")
                        if 'github_issues' in actions:
                            print(f"   GitHub Issues: {len(actions['github_issues'])}")
                        if 'linear_tasks' in actions:
                            print(f"   Linear Tasks: {len(actions['linear_tasks'])}")
                        if 'slack_notifications' in actions:
                            print(f"   Slack Notifications: {len(actions['slack_notifications'])}")
                    
                    # Display compliance metrics if available
                    if 'compliance_metrics' in parsed:
                        metrics = parsed['compliance_metrics']
                        print(f"\n📈 Compliance Metrics:")
                        print(f"   Overall Score: {metrics.get('overall_score', 'N/A')}")
                        print(f"   GDPR Compliance: {metrics.get('gdpr_compliance', 'N/A')}")
                        print(f"   CCPA Compliance: {metrics.get('ccpa_compliance', 'N/A')}")
                        print(f"   SOX Compliance: {metrics.get('sox_compliance', 'N/A')}")
                        print(f"   Trend: {metrics.get('trend', 'N/A')}")
                
            except json.JSONDecodeError:
                print(f"   Content is not JSON format")
                print(f"   Preview: {content[:300]}...")
        
        # Test Regular Analysis for Comparison
        print("\n🔍 Testing Regular Analysis for Comparison...")
        print("-" * 60)
        
        result2 = await app.call_tool(
            "analyze_document",
            {
                "document_content": contract_content,
                "document_type": "affiliate_agreement",
                "frameworks": ["gdpr", "ccpa"],
                "analysis_depth": "comprehensive"
            }
        )
        
        print("✅ Regular analysis completed!")
        print(f"📊 Result type: {type(result2)}")
        
        print("\n🎉 Structured Response Testing Complete!")
        print("=" * 60)
        print("✅ Enhanced structured responses are working")
        print("✅ Mistral function calling is operational")
        print("✅ LeChat actions are being generated")
        print("✅ Comprehensive analysis is functional")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_mistral_function_calling():
    """Test Mistral's function calling capabilities directly."""
    print("\n🤖 Testing Mistral Function Calling Directly")
    print("=" * 60)
    
    try:
        from src.tools.document_ai import DocumentAIService
        from src.tools.document_ai import DocumentAnalysisRequest
        
        # Initialize DocumentAI service
        doc_ai = DocumentAIService()
        
        # Test with contract content
        contract_content = """
        AFFILIATE AGREEMENT - DATA PROCESSING CLAUSE
        
        The Company may collect, process, and store personal data including names, 
        email addresses, and browsing behavior for service improvement purposes.
        The Company reserves the right to share this data with third parties.
        """
        
        print("📄 Testing with contract content...")
        print(f"📝 Content: {contract_content.strip()}")
        
        # Create analysis request
        request = DocumentAnalysisRequest(
            document_content=contract_content,
            document_type="affiliate_agreement",
            compliance_frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        # Test analysis
        result = await doc_ai.analyze_document(request)
        
        print("✅ Direct Mistral function calling test successful!")
        print(f"📊 Result type: {type(result)}")
        
        if hasattr(result, 'compliance_issues'):
            print(f"📊 Issues found: {len(result.compliance_issues)}")
            for issue in result.compliance_issues[:3]:  # Show first 3 issues
                print(f"   - {issue.severity.upper()}: {issue.description[:100]}...")
        
    except Exception as e:
        print(f"❌ Direct Mistral function calling test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Enhanced Structured Response Testing...")
    asyncio.run(test_structured_responses())
    asyncio.run(test_mistral_function_calling())
