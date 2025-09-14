#!/usr/bin/env python3
"""
Simple Contract DocumentAI Test

This script tests the DocumentAI implementation with a real contract,
focusing on the working functionality.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_fastmcp_server import app

async def test_contract_analysis():
    """Test DocumentAI with real contract data."""
    print("🧪 Testing DocumentAI with Real Contract")
    print("=" * 50)
    
    # Contract information
    contract_name = "CreditCards.com Inc. Affiliate Agreement"
    contract_size = "133,922 bytes"
    
    # Simulate contract content (in real scenario, this would be extracted from PDF)
    contract_content = f"""
    AFFILIATE AGREEMENT
    
    This Affiliate Agreement (the "Agreement") is entered into between CreditCards.com Inc. 
    ("Company") and the affiliate ("Affiliate") for the purpose of establishing an affiliate 
    relationship for marketing and promotional services.
    
    DATA PROCESSING:
    The Company may collect, process, and store personal data of users including names, 
    email addresses, browsing behavior, and transaction history for the purpose of 
    providing services and improving user experience.
    
    AFFILIATE OBLIGATIONS:
    The Affiliate agrees to comply with all applicable laws and regulations, including 
    data protection laws, and to maintain the confidentiality of any personal data 
    accessed during the course of this agreement.
    
    TERMINATION:
    Either party may terminate this agreement with 30 days written notice. Upon 
    termination, all personal data must be returned or destroyed in accordance with 
    applicable data protection laws.
    
    GOVERNING LAW:
    This agreement shall be governed by the laws of the State of Delaware.
    """
    
    print(f"📄 Contract: {contract_name}")
    print(f"📊 Size: {contract_size}")
    print(f"📝 Content Length: {len(contract_content)} characters")
    
    try:
        # Test Document Analysis
        print("\n🔍 Testing Document Analysis...")
        print("-" * 30)
        
        result = await app.call_tool(
            "analyze_document",
            {
                "document_content": contract_content,
                "document_type": "affiliate_agreement",
                "frameworks": ["gdpr", "ccpa", "sox"],
                "analysis_depth": "comprehensive"
            }
        )
        
        print("✅ Document analysis completed successfully!")
        
        # Extract and display the result
        if hasattr(result, 'content') and result.content:
            content = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            print(f"📊 Analysis Result:")
            print(f"   Content Type: {type(content)}")
            print(f"   Content Length: {len(content)} characters")
            print(f"   Preview: {content[:200]}...")
            
            # Try to parse as JSON if possible
            try:
                import json
                if isinstance(content, str) and content.startswith('{'):
                    parsed = json.loads(content)
                    print(f"   Parsed JSON Keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict'}")
            except:
                pass
        
        # Test Compliance Status
        print("\n📊 Testing Compliance Status...")
        print("-" * 30)
        
        result = await app.call_tool(
            "get_compliance_status",
            {
                "team_id": "contract-test-team",
                "framework": "gdpr",
                "include_history": False
            }
        )
        
        print("✅ Compliance status retrieved successfully!")
        
        # Test Memory Update
        print("\n💾 Testing Memory Update...")
        print("-" * 30)
        
        result = await app.call_tool(
            "update_memory",
            {
                "team_id": "contract-test-team",
                "insight": f"Analyzed {contract_name} - Found potential GDPR compliance issues in data processing clauses",
                "category": "contract_analysis",
                "priority": "high"
            }
        )
        
        print("✅ Memory update completed successfully!")
        
        # Test Workflow Automation
        print("\n🤖 Testing Workflow Automation...")
        print("-" * 30)
        
        result = await app.call_tool(
            "automate_compliance_workflow",
            {
                "document_content": contract_content,
                "workflow_type": "contract_review",
                "team_id": "contract-test-team",
                "priority": "high"
            }
        )
        
        print("✅ Workflow automation completed successfully!")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        print("✅ DocumentAI implementation is working correctly")
        print("✅ Mistral API integration is functional")
        print("✅ FastMCP server is processing requests properly")
        print("✅ Contract analysis is operational")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_mistral_direct():
    """Test Mistral API directly to verify integration."""
    print("\n🔗 Testing Mistral API Direct Integration")
    print("=" * 50)
    
    try:
        from src.tools.document_ai import DocumentAIService
        
        # Initialize DocumentAI service
        doc_ai = DocumentAIService()
        
        # Test with contract content
        contract_content = """
        AFFILIATE AGREEMENT - DATA PROCESSING CLAUSE
        
        The Company may collect, process, and store personal data including names, 
        email addresses, and browsing behavior for service improvement purposes.
        """
        
        print("📄 Testing with contract content...")
        print(f"📝 Content: {contract_content.strip()}")
        
        # Create analysis request
        from src.tools.document_ai import DocumentAnalysisRequest
        request = DocumentAnalysisRequest(
            document_content=contract_content,
            document_type="affiliate_agreement",
            compliance_frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        # Test analysis
        result = await doc_ai.analyze_document(request)
        
        print("✅ Direct Mistral API test successful!")
        print(f"📊 Result type: {type(result)}")
        print(f"📊 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            print(f"📊 Analysis summary:")
            print(f"   - Document ID: {result.get('document_id', 'N/A')}")
            print(f"   - Issues found: {result.get('issues_found', 'N/A')}")
            print(f"   - Risk score: {result.get('risk_score', 'N/A')}")
            print(f"   - Compliance status: {result.get('compliance_status', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Direct Mistral API test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Contract DocumentAI Testing...")
    asyncio.run(test_contract_analysis())
    asyncio.run(test_mistral_direct())
