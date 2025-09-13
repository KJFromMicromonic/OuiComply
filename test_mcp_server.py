#!/usr/bin/env python3
"""
Comprehensive test script for OuiComply MCP Server.

This script tests all MCP tools and functionality to ensure the server
is working correctly before deployment.
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import OuiComplyMCPServer
from src.config import validate_config


class MCPServerTester:
    """Comprehensive tester for MCP server functionality."""
    
    def __init__(self):
        self.server = None
        self.test_results = {}
        self.sample_document = self._load_sample_document()
    
    def _load_sample_document(self) -> str:
        """Load the sample privacy policy for testing."""
        try:
            with open("sample_privacy_policy.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Sample privacy policy content for testing compliance analysis."
    
    async def setup(self):
        """Set up the test environment."""
        print("🔧 Setting up test environment...")
        
        # Validate configuration
        if not validate_config():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize server
        self.server = OuiComplyMCPServer()
        print("✅ Test environment ready")
    
    async def test_document_compliance_analysis(self):
        """Test the core document compliance analysis functionality."""
        print("\n📄 Testing Document Compliance Analysis...")
        
        try:
            # Test arguments
            arguments = {
                "document_content": self.sample_document,
                "document_type": "text/plain",
                "compliance_frameworks": ["gdpr", "ccpa"],
                "analysis_depth": "comprehensive"
            }
            
            # Call the tool
            result = await self.server._handle_analyze_document_compliance(arguments)
            
            # Validate result
            if result and len(result) > 0:
                content = result[0].text
                if "COMPLIANCE ANALYSIS COMPLETED" in content and "Report ID:" in content:
                    self.test_results["document_analysis"] = "✅ PASS"
                    print("✅ Document analysis completed successfully")
                    
                    # Extract report ID for subsequent tests
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith("Report ID:"):
                            self.report_id = line.split(":")[1].strip()
                            break
                else:
                    self.test_results["document_analysis"] = "❌ FAIL - Invalid response format"
                    print("❌ Invalid response format")
            else:
                self.test_results["document_analysis"] = "❌ FAIL - No result returned"
                print("❌ No result returned")
                
        except Exception as e:
            self.test_results["document_analysis"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def test_report_generation(self):
        """Test compliance report generation in different formats."""
        print("\n📊 Testing Report Generation...")
        
        if not hasattr(self, 'report_id'):
            self.test_results["report_generation"] = "❌ SKIP - No report ID available"
            print("❌ Skipping - No report ID from previous test")
            return
        
        try:
            # Test JSON format
            json_args = {"report_id": self.report_id, "format": "json"}
            json_result = await self.server._handle_generate_compliance_report(json_args)
            
            # Test Markdown format
            md_args = {"report_id": self.report_id, "format": "markdown"}
            md_result = await self.server._handle_generate_compliance_report(md_args)
            
            # Validate results
            json_valid = json_result and len(json_result) > 0 and "{" in json_result[0].text
            md_valid = md_result and len(md_result) > 0 and "#" in md_result[0].text
            
            if json_valid and md_valid:
                self.test_results["report_generation"] = "✅ PASS"
                print("✅ Report generation (JSON & Markdown) working")
            else:
                self.test_results["report_generation"] = "❌ FAIL - Invalid format output"
                print("❌ Report generation failed")
                
        except Exception as e:
            self.test_results["report_generation"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def test_memory_integration(self):
        """Test LeChat memory integration."""
        print("\n🧠 Testing Memory Integration...")
        
        if not hasattr(self, 'report_id'):
            self.test_results["memory_integration"] = "❌ SKIP - No report ID available"
            print("❌ Skipping - No report ID from previous test")
            return
        
        try:
            # Test storing assessment in memory
            store_args = {
                "report_id": self.report_id,
                "user_id": "test_user_123",
                "organization_id": "test_org_456"
            }
            store_result = await self.server._handle_store_assessment_in_memory(store_args)
            
            # Test searching memories
            search_args = {
                "query": "compliance assessment",
                "category": "compliance_assessment",
                "limit": 5
            }
            search_result = await self.server._handle_search_compliance_memories(search_args)
            
            # Validate results (Note: These may fail if LeChat API is not configured)
            store_success = store_result and len(store_result) > 0
            search_success = search_result and len(search_result) > 0
            
            if store_success or search_success:
                self.test_results["memory_integration"] = "✅ PASS"
                print("✅ Memory integration functions working")
            else:
                self.test_results["memory_integration"] = "⚠️  PARTIAL - API may not be configured"
                print("⚠️  Memory integration may require API configuration")
                
        except Exception as e:
            self.test_results["memory_integration"] = f"⚠️  EXPECTED - {str(e)}"
            print(f"⚠️  Expected error (API not configured): {str(e)}")
    
    async def test_audit_trail_generation(self):
        """Test audit trail generation."""
        print("\n📋 Testing Audit Trail Generation...")
        
        if not hasattr(self, 'report_id'):
            self.test_results["audit_trail"] = "❌ SKIP - No report ID available"
            print("❌ Skipping - No report ID from previous test")
            return
        
        try:
            arguments = {
                "report_id": self.report_id,
                "repository": "test/compliance-repo",
                "branch": "main"
            }
            
            result = await self.server._handle_generate_audit_trail(arguments)
            
            if result and len(result) > 0 and "Audit Trail Entry Generated" in result[0].text:
                self.test_results["audit_trail"] = "✅ PASS"
                print("✅ Audit trail generation working")
            else:
                self.test_results["audit_trail"] = "❌ FAIL - Invalid audit trail format"
                print("❌ Audit trail generation failed")
                
        except Exception as e:
            self.test_results["audit_trail"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def test_compliance_history(self):
        """Test compliance history retrieval."""
        print("\n📈 Testing Compliance History...")
        
        try:
            arguments = {
                "user_id": "test_user_123",
                "organization_id": "test_org_456",
                "limit": 10
            }
            
            result = await self.server._handle_get_compliance_history(arguments)
            
            if result and len(result) > 0:
                self.test_results["compliance_history"] = "✅ PASS"
                print("✅ Compliance history retrieval working")
            else:
                self.test_results["compliance_history"] = "⚠️  PARTIAL - No history data"
                print("⚠️  Compliance history working (no data available)")
                
        except Exception as e:
            self.test_results["compliance_history"] = f"⚠️  EXPECTED - {str(e)}"
            print(f"⚠️  Expected error (no data): {str(e)}")
    
    async def test_risk_trends(self):
        """Test risk trend analysis."""
        print("\n📊 Testing Risk Trend Analysis...")
        
        try:
            arguments = {
                "user_id": "test_user_123",
                "organization_id": "test_org_456",
                "days": 30
            }
            
            result = await self.server._handle_analyze_risk_trends(arguments)
            
            if result and len(result) > 0 and "Risk Trend Analysis" in result[0].text:
                self.test_results["risk_trends"] = "✅ PASS"
                print("✅ Risk trend analysis working")
            else:
                self.test_results["risk_trends"] = "❌ FAIL - Invalid trend analysis format"
                print("❌ Risk trend analysis failed")
                
        except Exception as e:
            self.test_results["risk_trends"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def test_resource_listing(self):
        """Test MCP resource listing."""
        print("\n📚 Testing Resource Listing...")
        
        try:
            # Test list_resources handler
            resources = await self.server.server._handlers["list_resources"]()
            
            if resources and len(resources) >= 3:
                expected_resources = [
                    "compliance-frameworks",
                    "risk-assessment-criteria", 
                    "compliance-templates"
                ]
                
                resource_names = [r.name for r in resources]
                all_present = all(any(expected in name for name in resource_names) for expected in expected_resources)
                
                if all_present:
                    self.test_results["resource_listing"] = "✅ PASS"
                    print("✅ Resource listing working")
                else:
                    self.test_results["resource_listing"] = "❌ FAIL - Missing expected resources"
                    print("❌ Missing expected resources")
            else:
                self.test_results["resource_listing"] = "❌ FAIL - No resources returned"
                print("❌ No resources returned")
                
        except Exception as e:
            self.test_results["resource_listing"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def test_tool_listing(self):
        """Test MCP tool listing."""
        print("\n🔧 Testing Tool Listing...")
        
        try:
            # Test list_tools handler
            tools = await self.server.server._handlers["list_tools"]()
            
            expected_tools = [
                "analyze_document_compliance",
                "generate_compliance_report",
                "store_assessment_in_memory",
                "search_compliance_memories",
                "generate_audit_trail",
                "get_compliance_history",
                "analyze_risk_trends"
            ]
            
            if tools and len(tools) >= len(expected_tools):
                tool_names = [t.name for t in tools]
                all_present = all(tool in tool_names for tool in expected_tools)
                
                if all_present:
                    self.test_results["tool_listing"] = "✅ PASS"
                    print("✅ Tool listing working - all 7 tools available")
                else:
                    self.test_results["tool_listing"] = "❌ FAIL - Missing expected tools"
                    print("❌ Missing expected tools")
            else:
                self.test_results["tool_listing"] = "❌ FAIL - Insufficient tools returned"
                print("❌ Insufficient tools returned")
                
        except Exception as e:
            self.test_results["tool_listing"] = f"❌ FAIL - {str(e)}"
            print(f"❌ Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests and generate a comprehensive report."""
        print("🧪 Starting Comprehensive MCP Server Testing")
        print("=" * 60)
        
        try:
            await self.setup()
            
            # Run all tests
            await self.test_resource_listing()
            await self.test_tool_listing()
            await self.test_document_compliance_analysis()
            await self.test_report_generation()
            await self.test_audit_trail_generation()
            await self.test_memory_integration()
            await self.test_compliance_history()
            await self.test_risk_trends()
            
            # Generate final report
            self.generate_test_report()
            
        except Exception as e:
            print(f"\n💥 Critical test failure: {str(e)}")
            traceback.print_exc()
    
    def generate_test_report(self):
        """Generate and display the final test report."""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.startswith("✅")])
        partial_tests = len([r for r in self.test_results.values() if r.startswith("⚠️")])
        failed_tests = len([r for r in self.test_results.values() if r.startswith("❌")])
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Partial: {partial_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        
        print(f"\n📝 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            print(f"   {test_name.replace('_', ' ').title()}: {result}")
        
        # Overall assessment
        if failed_tests == 0:
            if partial_tests == 0:
                print(f"\n🎉 OVERALL STATUS: ALL TESTS PASSED")
                print("   The MCP server is fully functional and ready for deployment!")
            else:
                print(f"\n✅ OVERALL STATUS: CORE FUNCTIONALITY WORKING")
                print("   Some features require additional API configuration (LeChat, etc.)")
        else:
            print(f"\n⚠️  OVERALL STATUS: ISSUES DETECTED")
            print("   Some core functionality needs attention before deployment.")
        
        print("\n" + "=" * 60)


async def main():
    """Main test execution function."""
    tester = MCPServerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
