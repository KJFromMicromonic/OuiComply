#!/usr/bin/env python3
"""
Mistral API Integration Test for OuiComply DocumentAI

This script tests the Mistral API integration with real API calls to verify
that the DocumentAI functionality works correctly with the provided API key.

Author: OuiComply Team
Version: 1.0.0
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tools.document_ai import DocumentAIService, DocumentAnalysisRequest
from src.config import get_config


class MistralAPITester:
    """
    Test class for Mistral API integration with DocumentAI.
    
    This class provides comprehensive testing of the Mistral API integration,
    including authentication, document analysis, and compliance checking.
    """
    
    def __init__(self):
        """Initialize the API tester with configuration."""
        self.config = get_config()
        self.document_ai = DocumentAIService()
        self.test_results = {
            "api_connectivity": False,
            "document_analysis": False,
            "compliance_checking": False,
            "error_logs": []
        }
    
    async def test_api_connectivity(self) -> bool:
        """
        Test basic API connectivity and authentication.
        
        Returns:
            True if API is accessible, False otherwise
        """
        print("🔌 Testing Mistral API Connectivity")
        print("=" * 50)
        
        try:
            # Test basic API call
            response = await asyncio.to_thread(
                self.document_ai.client.chat.complete,
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Respond with 'API connection successful' if you receive this message."
                    },
                    {
                        "role": "user",
                        "content": "Test API connectivity"
                    }
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            if response.choices[0].message.content:
                print("✅ API connectivity test passed")
                print(f"   Response: {response.choices[0].message.content[:100]}...")
                self.test_results["api_connectivity"] = True
                return True
            else:
                print("❌ API connectivity test failed - No response content")
                self.test_results["error_logs"].append("No response content from API")
                return False
                
        except Exception as e:
            print(f"❌ API connectivity test failed: {str(e)}")
            self.test_results["error_logs"].append(f"API connectivity error: {str(e)}")
            return False
    
    async def test_document_analysis(self) -> bool:
        """
        Test document analysis functionality with a sample document.
        
        Returns:
            True if document analysis works, False otherwise
        """
        print("\n📄 Testing Document Analysis")
        print("=" * 50)
        
        try:
            # Create sample document content
            sample_document = """
            PRIVACY POLICY
            
            This Privacy Policy describes how our company collects, uses, and protects your personal information.
            
            DATA COLLECTION
            We collect personal information when you:
            - Register for our services
            - Contact us through our website
            - Use our mobile application
            
            DATA USE
            We use your personal information to:
            - Provide and improve our services
            - Communicate with you
            - Comply with legal obligations
            
            DATA SHARING
            We may share your information with third-party service providers who assist us in operating our business.
            
            YOUR RIGHTS
            You have the right to:
            - Access your personal information
            - Correct inaccurate information
            - Delete your personal information
            - Withdraw consent
            
            CONTACT US
            For questions about this privacy policy, contact us at privacy@company.com
            """
            
            # Create analysis request
            request = DocumentAnalysisRequest(
                document_content=sample_document,
                document_type="text/plain",
                compliance_frameworks=["gdpr", "ccpa"],
                analysis_depth="comprehensive"
            )
            
            print("   Analyzing sample privacy policy document...")
            print(f"   Document length: {len(sample_document)} characters")
            print(f"   Frameworks: {request.compliance_frameworks}")
            
            # Perform analysis
            result = await self.document_ai.analyze_document(request)
            
            # Display results
            print(f"✅ Document analysis completed")
            print(f"   Document ID: {result.document_id}")
            print(f"   Document Type: {result.document_type}")
            print(f"   Analysis Timestamp: {result.analysis_timestamp}")
            print(f"   Risk Score: {result.risk_score:.2f}")
            print(f"   Issues Found: {len(result.compliance_issues)}")
            print(f"   Missing Clauses: {len(result.missing_clauses)}")
            print(f"   Recommendations: {len(result.recommendations)}")
            
            # Display compliance issues
            if result.compliance_issues:
                print("\n   🚨 Compliance Issues Found:")
                for i, issue in enumerate(result.compliance_issues, 1):
                    print(f"      {i}. [{issue.severity.upper()}] {issue.description}")
                    print(f"         Framework: {issue.framework}")
                    print(f"         Confidence: {issue.confidence:.2f}")
                    print(f"         Recommendation: {issue.recommendation}")
                    print()
            
            # Display missing clauses
            if result.missing_clauses:
                print("   📋 Missing Required Clauses:")
                for clause in result.missing_clauses:
                    print(f"      - {clause}")
                print()
            
            # Display recommendations
            if result.recommendations:
                print("   💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"      - {rec}")
                print()
            
            self.test_results["document_analysis"] = True
            return True
            
        except Exception as e:
            print(f"❌ Document analysis test failed: {str(e)}")
            self.test_results["error_logs"].append(f"Document analysis error: {str(e)}")
            return False
    
    async def test_compliance_frameworks(self) -> bool:
        """
        Test compliance checking across multiple frameworks.
        
        Returns:
            True if compliance checking works, False otherwise
        """
        print("\n⚖️  Testing Compliance Framework Analysis")
        print("=" * 50)
        
        try:
            # Test different document types
            test_documents = {
                "gdpr_document": """
                DATA PROCESSING AGREEMENT
                
                This agreement governs the processing of personal data in accordance with GDPR.
                
                LEGAL BASIS
                We process personal data based on legitimate interest and consent.
                
                DATA RETENTION
                Personal data will be retained for 3 years after the end of the business relationship.
                
                DATA SUBJECT RIGHTS
                Data subjects have the right to access, rectify, erase, and port their data.
                """,
                
                "sox_document": """
                FINANCIAL CONTROLS POLICY
                
                This policy establishes internal controls for financial reporting.
                
                INTERNAL CONTROLS
                We maintain comprehensive internal controls over financial reporting.
                
                MANAGEMENT RESPONSIBILITY
                Management is responsible for establishing and maintaining adequate internal controls.
                
                AUDIT COMMITTEE
                The audit committee oversees the internal audit function.
                """,
                
                "ccpa_document": """
                CALIFORNIA CONSUMER PRIVACY NOTICE
                
                This notice describes how we collect and use personal information of California residents.
                
                PERSONAL INFORMATION COLLECTION
                We collect identifiers, commercial information, and internet activity information.
                
                CONSUMER RIGHTS
                California consumers have the right to know, delete, and opt-out of sale of personal information.
                
                OPT-OUT MECHANISMS
                Consumers can opt-out by calling 1-800-PRIVACY or visiting our website.
                """
            }
            
            framework_results = {}
            
            for doc_name, doc_content in test_documents.items():
                print(f"\n   Testing {doc_name}...")
                
                # Determine frameworks based on document type
                if "gdpr" in doc_name:
                    frameworks = ["gdpr"]
                elif "sox" in doc_name:
                    frameworks = ["sox"]
                elif "ccpa" in doc_name:
                    frameworks = ["ccpa"]
                else:
                    frameworks = ["gdpr", "ccpa"]
                
                # Create analysis request
                request = DocumentAnalysisRequest(
                    document_content=doc_content,
                    document_type="text/plain",
                    compliance_frameworks=frameworks,
                    analysis_depth="standard"
                )
                
                # Perform analysis
                result = await self.document_ai.analyze_document(request)
                
                # Store results
                framework_results[doc_name] = {
                    "frameworks": frameworks,
                    "issues_count": len(result.compliance_issues),
                    "risk_score": result.risk_score,
                    "missing_clauses": len(result.missing_clauses)
                }
                
                print(f"      Frameworks: {frameworks}")
                print(f"      Issues: {len(result.compliance_issues)}")
                print(f"      Risk Score: {result.risk_score:.2f}")
                print(f"      Missing Clauses: {len(result.missing_clauses)}")
            
            # Summary
            print(f"\n   📊 Framework Analysis Summary:")
            total_issues = sum(r["issues_count"] for r in framework_results.values())
            avg_risk = sum(r["risk_score"] for r in framework_results.values()) / len(framework_results)
            
            print(f"      Total Issues Found: {total_issues}")
            print(f"      Average Risk Score: {avg_risk:.2f}")
            print(f"      Documents Analyzed: {len(framework_results)}")
            
            self.test_results["compliance_checking"] = True
            return True
            
        except Exception as e:
            print(f"❌ Compliance framework test failed: {str(e)}")
            self.test_results["error_logs"].append(f"Compliance framework error: {str(e)}")
            return False
    
    async def test_document_summary(self) -> bool:
        """
        Test document summary generation.
        
        Returns:
            True if summary generation works, False otherwise
        """
        print("\n📝 Testing Document Summary Generation")
        print("=" * 50)
        
        try:
            # Test with a mock document ID
            document_id = "test_doc_123"
            
            print(f"   Generating summary for document: {document_id}")
            
            # Generate summary
            summary = await self.document_ai.get_document_summary(document_id)
            
            if summary and len(summary) > 10:
                print("✅ Document summary generated successfully")
                print(f"   Summary length: {len(summary)} characters")
                print(f"   Preview: {summary[:200]}...")
                return True
            else:
                print("❌ Document summary generation failed - Empty or invalid summary")
                return False
                
        except Exception as e:
            print(f"❌ Document summary test failed: {str(e)}")
            self.test_results["error_logs"].append(f"Document summary error: {str(e)}")
            return False
    
    def print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📊 MISTRAL API TEST SUMMARY")
        print("=" * 80)
        
        # Test results
        print("Test Results:")
        print(f"  🔌 API Connectivity: {'✅ PASS' if self.test_results['api_connectivity'] else '❌ FAIL'}")
        print(f"  📄 Document Analysis: {'✅ PASS' if self.test_results['document_analysis'] else '❌ FAIL'}")
        print(f"  ⚖️  Compliance Checking: {'✅ PASS' if self.test_results['compliance_checking'] else '❌ FAIL'}")
        
        # Error logs
        if self.test_results["error_logs"]:
            print(f"\nError Logs ({len(self.test_results['error_logs'])} errors):")
            for i, error in enumerate(self.test_results["error_logs"], 1):
                print(f"  {i}. {error}")
        
        # Overall status
        all_passed = all([
            self.test_results["api_connectivity"],
            self.test_results["document_analysis"],
            self.test_results["compliance_checking"]
        ])
        
        print(f"\nOverall Status: {'🎉 ALL TESTS PASSED' if all_passed else '💥 SOME TESTS FAILED'}")
        
        if all_passed:
            print("\n✅ Mistral API integration is working correctly!")
            print("   DocumentAI functionality is ready for production use.")
        else:
            print("\n⚠️  Some tests failed. Please check the error logs above.")
            print("   Review your API key configuration and network connectivity.")
        
        print("=" * 80)
    
    async def run_all_tests(self):
        """Run all API tests in sequence."""
        print("🧪 Starting Mistral API Integration Tests")
        print("=" * 80)
        print(f"Test started at: {datetime.now().isoformat()}")
        print(f"API Key configured: {'Yes' if self.config.mistral_api_key else 'No'}")
        print()
        
        # Run tests
        await self.test_api_connectivity()
        await self.test_document_analysis()
        await self.test_compliance_frameworks()
        await self.test_document_summary()
        
        # Print summary
        self.print_test_summary()
        
        return all([
            self.test_results["api_connectivity"],
            self.test_results["document_analysis"],
            self.test_results["compliance_checking"]
        ])


async def main():
    """Main function to run the API tests."""
    try:
        tester = MistralAPITester()
        success = await tester.run_all_tests()
        return success
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
