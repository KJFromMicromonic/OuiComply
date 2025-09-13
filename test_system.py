#!/usr/bin/env python3
"""
Test script for OuiComply MCP Server.

This script tests the compliance analysis system with sample documents.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from tools.compliance_engine import ComplianceEngine
from tools.memory_integration import LeChatMemoryService


async def test_document_analysis():
    """Test document analysis with a sample document."""
    print("🧪 Testing OuiComply Document Analysis System")
    print("=" * 50)
    
    # Check if Mistral API key is set
    mistral_key = os.getenv("MISTRAL_KEY")
    if not mistral_key or mistral_key == "your_mistral_api_key_here":
        print("❌ MISTRAL_KEY not set. Please set your Mistral API key in .env file")
        print("   Example: MISTRAL_KEY=your_actual_api_key_here")
        return False
    
    try:
        # Initialize services
        print("📋 Initializing services...")
        document_ai = DocumentAIService()
        compliance_engine = ComplianceEngine()
        
        # Create a sample document content for testing
        sample_document = """
        PRIVACY POLICY
        
        This privacy policy describes how our company collects, uses, and protects your personal information.
        
        DATA COLLECTION
        We collect personal information when you:
        - Register for our services
        - Contact us for support
        - Use our website
        
        DATA USAGE
        We use your personal information to:
        - Provide our services
        - Improve our products
        - Send you marketing communications
        
        DATA RETENTION
        We retain your personal information for as long as necessary to provide our services.
        
        YOUR RIGHTS
        You have the right to:
        - Access your personal information
        - Correct inaccurate data
        - Delete your data
        - Object to processing
        
        CONTACT US
        For questions about this privacy policy, contact us at privacy@company.com
        
        Last updated: January 2024
        """
        
        print("📄 Testing with sample privacy policy document...")
        
        # Test 1: Document Analysis Request
        print("\n1️⃣ Testing Document Analysis Request...")
        request = DocumentAnalysisRequest(
            document_content=sample_document,
            compliance_frameworks=["gdpr", "ccpa"],
            analysis_depth="comprehensive"
        )
        
        print(f"   ✅ Request created successfully")
        print(f"   📊 Frameworks: {request.compliance_frameworks}")
        print(f"   🔍 Analysis depth: {request.analysis_depth}")
        
        # Test 2: Document Analysis (this will make actual API calls)
        print("\n2️⃣ Testing Document Analysis with Mistral AI...")
        print("   ⏳ This may take a moment...")
        
        try:
            analysis_result = await document_ai.analyze_document(request)
            
            print(f"   ✅ Analysis completed successfully!")
            print(f"   📋 Document ID: {analysis_result.document_id}")
            print(f"   📄 Document Type: {analysis_result.document_type}")
            print(f"   ⚠️  Issues Found: {len(analysis_result.compliance_issues)}")
            print(f"   📊 Risk Score: {analysis_result.risk_score:.2f}/1.0")
            print(f"   📝 Missing Clauses: {len(analysis_result.missing_clauses)}")
            
            # Display issues if any
            if analysis_result.compliance_issues:
                print("\n   🔍 Compliance Issues Found:")
                for i, issue in enumerate(analysis_result.compliance_issues, 1):
                    print(f"      {i}. [{issue.severity.upper()}] {issue.description}")
                    print(f"         Framework: {issue.framework.upper()}")
                    print(f"         Recommendation: {issue.recommendation}")
                    print()
            
            # Display missing clauses
            if analysis_result.missing_clauses:
                print("   📋 Missing Required Clauses:")
                for clause in analysis_result.missing_clauses:
                    print(f"      - {clause}")
                print()
            
        except Exception as e:
            print(f"   ❌ Document analysis failed: {str(e)}")
            print("   💡 This might be due to:")
            print("      - Invalid Mistral API key")
            print("      - Network connectivity issues")
            print("      - Mistral API service issues")
            return False
        
        # Test 3: Compliance Report Generation
        print("\n3️⃣ Testing Compliance Report Generation...")
        
        try:
            # Generate compliance report
            report = await compliance_engine.analyze_document_compliance(
                document_content=sample_document,
                frameworks=["gdpr", "ccpa"],
                analysis_depth="comprehensive"
            )
            
            print(f"   ✅ Compliance report generated!")
            print(f"   📋 Report ID: {report.report_id}")
            print(f"   📊 Status: {report.overall_status.value.upper()}")
            print(f"   ⚠️  Risk Level: {report.risk_level.value.upper()}")
            print(f"   📈 Risk Score: {report.risk_score:.2f}/1.0")
            print(f"   🔧 Mitigation Actions: {len(report.mitigation_actions)}")
            
            # Test report export
            print("\n   📄 Testing Report Export...")
            json_report = compliance_engine.export_report_json(report)
            markdown_report = compliance_engine.export_report_markdown(report)
            
            print(f"   ✅ JSON export: {len(json_report)} characters")
            print(f"   ✅ Markdown export: {len(markdown_report)} characters")
            
            # Save sample report
            with open("sample_compliance_report.json", "w") as f:
                f.write(json_report)
            print(f"   💾 Sample report saved as 'sample_compliance_report.json'")
            
        except Exception as e:
            print(f"   ❌ Compliance report generation failed: {str(e)}")
            return False
        
        # Test 4: Memory Integration (if configured)
        print("\n4️⃣ Testing Memory Integration...")
        
        lechat_key = os.getenv("LECHAT_API_KEY")
        if lechat_key and lechat_key != "your_lechat_api_key":
            try:
                memory_service = LeChatMemoryService()
                
                # Store assessment in memory
                memory_id = await memory_service.store_compliance_assessment(
                    report=report,
                    user_id="test_user",
                    organization_id="test_org"
                )
                
                print(f"   ✅ Assessment stored in memory: {memory_id}")
                
                # Search memories
                search_results = await memory_service.search_memories(
                    query="GDPR compliance",
                    category="compliance_assessment",
                    limit=5
                )
                
                print(f"   ✅ Memory search completed: {len(search_results)} results found")
                
            except Exception as e:
                print(f"   ⚠️  Memory integration test failed: {str(e)}")
                print("   💡 This is optional and won't affect core functionality")
        else:
            print("   ⏭️  Skipping memory integration test (LECHAT_API_KEY not configured)")
        
        # Test 5: Audit Trail Generation
        print("\n5️⃣ Testing Audit Trail Generation...")
        
        try:
            audit_trail = await compliance_engine.generate_audit_trail_entry(report)
            
            print(f"   ✅ Audit trail generated!")
            print(f"   📄 Length: {len(audit_trail)} characters")
            
            # Save audit trail
            with open("sample_audit_trail.md", "w") as f:
                f.write(audit_trail)
            print(f"   💾 Audit trail saved as 'sample_audit_trail.md'")
            
        except Exception as e:
            print(f"   ❌ Audit trail generation failed: {str(e)}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print("\n📁 Generated Files:")
        print("   - sample_compliance_report.json")
        print("   - sample_audit_trail.md")
        
        print("\n🚀 Next Steps:")
        print("   1. Review the generated compliance report")
        print("   2. Check the audit trail for GitHub integration")
        print("   3. Configure LeChat memory integration if needed")
        print("   4. Deploy to Vercel for production use")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure MISTRAL_KEY is set in .env file")
        print("   2. Check your internet connection")
        print("   3. Verify Mistral API key is valid")
        print("   4. Install all dependencies: pip install -r requirements.txt")
        return False


async def test_mcp_server_tools():
    """Test MCP server tools directly."""
    print("\n🔧 Testing MCP Server Tools...")
    print("=" * 30)
    
    try:
        from mcp_server import OuiComplyMCPServer
        
        # Initialize server
        server = OuiComplyMCPServer()
        
        # Test tool listing
        print("📋 Testing tool listing...")
        tools = await server.server.list_tools()
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")
        
        # Test resource listing
        print("\n📚 Testing resource listing...")
        resources = await server.server.list_resources()
        print(f"   ✅ Found {len(resources)} resources:")
        for resource in resources:
            print(f"      - {resource.name}: {resource.description}")
        
        print("\n✅ MCP Server tools test completed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP Server tools test failed: {str(e)}")
        return False


def main():
    """Main test function."""
    print("🚀 OuiComply System Test")
    print("=" * 50)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Creating from template...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("   ✅ Created .env file from template")
            print("   📝 Please edit .env file with your API keys")
        else:
            print("   ❌ .env.example not found. Please create .env file manually")
            return
    
    # Run tests
    async def run_tests():
        success = True
        
        # Test MCP server tools
        if not await test_mcp_server_tools():
            success = False
        
        # Test document analysis
        if not await test_document_analysis():
            success = False
        
        return success
    
    # Run async tests
    try:
        success = asyncio.run(run_tests())
        
        if success:
            print("\n🎉 All tests passed! System is ready for use.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
