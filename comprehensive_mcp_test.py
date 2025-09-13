#!/usr/bin/env python3
"""
Comprehensive MCP Protocol Testing for OuiComply MCP Server.
Tests all MCP endpoints, error handling, and edge cases.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import traceback

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp_server import OuiComplyMCPServer
from src.config import validate_config


class MCPProtocolTester:
    """Comprehensive MCP protocol tester."""
    
    def __init__(self):
        self.server = None
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append(f"{status} {test_name}: {message}")
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        print(f"   {status} {test_name}")
        if message and not success:
            print(f"      {message}")
    
    async def setup_server(self):
        """Set up the MCP server for testing."""
        print("🔧 Setting up MCP Server...")
        try:
            self.server = OuiComplyMCPServer()
            self.log_test("Server Setup", True, "Server instance created successfully")
            return True
        except Exception as e:
            self.log_test("Server Setup", False, f"Failed to create server: {e}")
            return False
    
    async def test_configuration(self):
        """Test configuration validation."""
        print("\n📋 Testing Configuration...")
        
        # Test valid configuration
        try:
            is_valid = validate_config()
            self.log_test("Configuration Validation", is_valid, 
                         "Valid configuration detected" if is_valid else "Configuration invalid")
        except Exception as e:
            self.log_test("Configuration Validation", False, f"Exception: {e}")
    
    async def test_resource_handlers(self):
        """Test all resource-related MCP handlers."""
        print("\n📚 Testing Resource Handlers...")
        
        # Test list_resources
        try:
            # Find the list_resources handler
            list_handler = None
            for name, handler in self.server.server.request_handlers.items():
                if "list_resources" in str(name).lower():
                    list_handler = handler
                    break
            
            if list_handler:
                resources = await list_handler()
                self.log_test("List Resources", True, f"Found {len(resources)} resources")
                
                # Validate resource structure
                for resource in resources:
                    if hasattr(resource, 'uri') and hasattr(resource, 'name'):
                        self.log_test(f"Resource Structure ({resource.name})", True, 
                                    f"Valid resource: {resource.uri}")
                    else:
                        self.log_test(f"Resource Structure ({resource})", False, 
                                    "Invalid resource structure")
            else:
                self.log_test("List Resources", False, "No list_resources handler found")
        except Exception as e:
            self.log_test("List Resources", False, f"Exception: {e}")
        
        # Test read_resource
        try:
            # Find the read_resource handler
            read_handler = None
            for name, handler in self.server.server.request_handlers.items():
                if "read_resource" in str(name).lower():
                    read_handler = handler
                    break
            
            if read_handler:
                # Test valid resource URIs
                test_uris = [
                    "resource://legal-templates",
                    "resource://compliance-frameworks"
                ]
                
                for uri in test_uris:
                    try:
                        content = await read_handler(uri=uri)
                        self.log_test(f"Read Resource ({uri})", True, 
                                    f"Content length: {len(content)} chars")
                        
                        # Validate JSON content
                        try:
                            json.loads(content)
                            self.log_test(f"Resource JSON Validation ({uri})", True, 
                                        "Valid JSON content")
                        except json.JSONDecodeError:
                            self.log_test(f"Resource JSON Validation ({uri})", False, 
                                        "Invalid JSON content")
                    except Exception as e:
                        self.log_test(f"Read Resource ({uri})", False, f"Exception: {e}")
                
                # Test invalid resource URI
                try:
                    await read_handler(uri="resource://invalid-resource")
                    self.log_test("Invalid Resource Handling", False, 
                                "Should have raised exception for invalid URI")
                except Exception:
                    self.log_test("Invalid Resource Handling", True, 
                                "Correctly handled invalid URI")
            else:
                self.log_test("Read Resource", False, "No read_resource handler found")
        except Exception as e:
            self.log_test("Read Resource", False, f"Exception: {e}")
    
    async def test_tool_handlers(self):
        """Test all tool-related MCP handlers."""
        print("\n🛠️  Testing Tool Handlers...")
        
        # Test list_tools
        try:
            # Find the list_tools handler
            list_handler = None
            for name, handler in self.server.server.request_handlers.items():
                if "list_tools" in str(name).lower():
                    list_handler = handler
                    break
            
            if list_handler:
                tools = await list_handler()
                self.log_test("List Tools", True, f"Found {len(tools)} tools")
                
                # Validate tool structure
                expected_tools = ["analyze_document", "check_clause_presence", "risk_assessment"]
                found_tools = [tool.name for tool in tools]
                
                for expected_tool in expected_tools:
                    if expected_tool in found_tools:
                        self.log_test(f"Tool Presence ({expected_tool})", True, 
                                    "Tool found in list")
                    else:
                        self.log_test(f"Tool Presence ({expected_tool})", False, 
                                    "Tool missing from list")
                
                # Validate tool schemas
                for tool in tools:
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        self.log_test(f"Tool Schema ({tool.name})", True, 
                                    "Valid input schema")
                    else:
                        self.log_test(f"Tool Schema ({tool.name})", False, 
                                    "Missing or invalid input schema")
            else:
                self.log_test("List Tools", False, "No list_tools handler found")
        except Exception as e:
            self.log_test("List Tools", False, f"Exception: {e}")
    
    async def test_tool_execution(self):
        """Test tool execution with various inputs."""
        print("\n⚙️  Testing Tool Execution...")
        
        # Find the call_tool handler
        call_handler = None
        for name, handler in self.server.server.request_handlers.items():
            if "call_tool" in str(name).lower():
                call_handler = handler
                break
        
        if not call_handler:
            self.log_test("Tool Execution Setup", False, "No call_tool handler found")
            return
        
        # Test analyze_document tool
        test_cases = [
            {
                "name": "analyze_document",
                "args": {
                    "document_text": "This is a sample privacy policy with personal data collection.",
                    "compliance_framework": "gdpr"
                },
                "description": "Valid GDPR analysis"
            },
            {
                "name": "analyze_document", 
                "args": {
                    "document_text": "California privacy policy for CCPA compliance.",
                    "compliance_framework": "ccpa"
                },
                "description": "Valid CCPA analysis"
            },
            {
                "name": "check_clause_presence",
                "args": {
                    "document_text": "This contract includes termination clauses and liability limitations.",
                    "required_clauses": ["termination", "limitation_of_liability"]
                },
                "description": "Valid clause checking"
            },
            {
                "name": "risk_assessment",
                "args": {
                    "document_text": "Service agreement with payment terms and termination conditions.",
                    "document_type": "contract"
                },
                "description": "Valid risk assessment"
            }
        ]
        
        # Test valid cases
        for test_case in test_cases:
            try:
                result = await call_handler(
                    name=test_case["name"],
                    arguments=test_case["args"]
                )
                
                if result and len(result) > 0:
                    self.log_test(f"Tool Execution ({test_case['description']})", True, 
                                f"Returned {len(result)} result(s)")
                    
                    # Validate result structure
                    if hasattr(result[0], 'text'):
                        self.log_test(f"Result Structure ({test_case['name']})", True, 
                                    f"Valid text content: {len(result[0].text)} chars")
                    else:
                        self.log_test(f"Result Structure ({test_case['name']})", False, 
                                    "Invalid result structure")
                else:
                    self.log_test(f"Tool Execution ({test_case['description']})", False, 
                                "No results returned")
            except Exception as e:
                self.log_test(f"Tool Execution ({test_case['description']})", False, 
                            f"Exception: {e}")
        
        # Test error cases
        error_cases = [
            {
                "name": "invalid_tool",
                "args": {},
                "description": "Invalid tool name"
            },
            {
                "name": "analyze_document",
                "args": {
                    "document_text": "test",
                    "compliance_framework": "invalid_framework"
                },
                "description": "Invalid framework"
            },
            {
                "name": "analyze_document",
                "args": {
                    "compliance_framework": "gdpr"
                    # Missing required document_text
                },
                "description": "Missing required parameter"
            }
        ]
        
        for error_case in error_cases:
            try:
                result = await call_handler(
                    name=error_case["name"],
                    arguments=error_case["args"]
                )
                self.log_test(f"Error Handling ({error_case['description']})", False, 
                            "Should have raised exception")
            except Exception:
                self.log_test(f"Error Handling ({error_case['description']})", True, 
                            "Correctly handled error case")
    
    async def test_performance(self):
        """Test performance with larger documents."""
        print("\n🚀 Testing Performance...")
        
        # Find the call_tool handler
        call_handler = None
        for name, handler in self.server.server.request_handlers.items():
            if "call_tool" in str(name).lower():
                call_handler = handler
                break
        
        if not call_handler:
            self.log_test("Performance Test Setup", False, "No call_tool handler found")
            return
        
        # Create large document
        large_document = "This is a privacy policy. " * 1000  # ~25KB document
        
        try:
            import time
            start_time = time.time()
            
            result = await call_handler(
                name="analyze_document",
                arguments={
                    "document_text": large_document,
                    "compliance_framework": "gdpr"
                }
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time < 5.0:  # Should complete within 5 seconds
                self.log_test("Large Document Performance", True, 
                            f"Processed {len(large_document)} chars in {execution_time:.2f}s")
            else:
                self.log_test("Large Document Performance", False, 
                            f"Too slow: {execution_time:.2f}s for {len(large_document)} chars")
        except Exception as e:
            self.log_test("Large Document Performance", False, f"Exception: {e}")
        
        # Test concurrent requests
        try:
            import time
            start_time = time.time()
            
            # Run 5 concurrent requests
            tasks = []
            for i in range(5):
                task = call_handler(
                    name="analyze_document",
                    arguments={
                        "document_text": f"Document {i} for concurrent testing.",
                        "compliance_framework": "gdpr"
                    }
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            execution_time = end_time - start_time
            
            successful_results = [r for r in results if not isinstance(r, Exception)]
            
            if len(successful_results) == 5 and execution_time < 10.0:
                self.log_test("Concurrent Requests", True, 
                            f"Processed 5 concurrent requests in {execution_time:.2f}s")
            else:
                self.log_test("Concurrent Requests", False, 
                            f"Failed: {len(successful_results)}/5 successful in {execution_time:.2f}s")
        except Exception as e:
            self.log_test("Concurrent Requests", False, f"Exception: {e}")
    
    async def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("\n🔍 Testing Edge Cases...")
        
        # Find the call_tool handler
        call_handler = None
        for name, handler in self.server.server.request_handlers.items():
            if "call_tool" in str(name).lower():
                call_handler = handler
                break
        
        if not call_handler:
            self.log_test("Edge Case Setup", False, "No call_tool handler found")
            return
        
        edge_cases = [
            {
                "name": "analyze_document",
                "args": {
                    "document_text": "",  # Empty document
                    "compliance_framework": "gdpr"
                },
                "description": "Empty document",
                "should_succeed": True
            },
            {
                "name": "analyze_document",
                "args": {
                    "document_text": "x" * 100000,  # Very large document
                    "compliance_framework": "gdpr"
                },
                "description": "Very large document (100KB)",
                "should_succeed": True
            },
            {
                "name": "check_clause_presence",
                "args": {
                    "document_text": "test document",
                    "required_clauses": []  # Empty clause list
                },
                "description": "Empty clause list",
                "should_succeed": True
            },
            {
                "name": "analyze_document",
                "args": {
                    "document_text": "test",
                    "compliance_framework": "gdpr",
                    "extra_param": "should_be_ignored"  # Extra parameter
                },
                "description": "Extra parameters",
                "should_succeed": True
            }
        ]
        
        for case in edge_cases:
            try:
                result = await call_handler(
                    name=case["name"],
                    arguments=case["args"]
                )
                
                if case["should_succeed"]:
                    self.log_test(f"Edge Case ({case['description']})", True, 
                                "Handled successfully")
                else:
                    self.log_test(f"Edge Case ({case['description']})", False, 
                                "Should have failed but succeeded")
            except Exception as e:
                if case["should_succeed"]:
                    self.log_test(f"Edge Case ({case['description']})", False, 
                                f"Unexpected exception: {e}")
                else:
                    self.log_test(f"Edge Case ({case['description']})", True, 
                                "Correctly failed as expected")
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("🧪 COMPREHENSIVE MCP TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            print(f"\n🎉 EXCELLENT! The MCP server is highly reliable.")
        elif pass_rate >= 75:
            print(f"\n✅ GOOD! The MCP server is working well with minor issues.")
        elif pass_rate >= 50:
            print(f"\n⚠️  FAIR! The MCP server has some issues that need attention.")
        else:
            print(f"\n❌ POOR! The MCP server has significant issues.")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"   {result}")
        
        print(f"\n🚀 OuiComply MCP Server Status: {'READY FOR PRODUCTION' if pass_rate >= 80 else 'NEEDS IMPROVEMENT'}")


async def main():
    """Run comprehensive MCP testing."""
    print("🧪 COMPREHENSIVE MCP PROTOCOL TESTING")
    print("=" * 80)
    print("Testing OuiComply MCP Server - Legal Compliance Platform")
    print("=" * 80)
    
    tester = MCPProtocolTester()
    
    try:
        # Setup
        if not await tester.setup_server():
            print("❌ Failed to setup server. Aborting tests.")
            return
        
        # Run all test suites
        await tester.test_configuration()
        await tester.test_resource_handlers()
        await tester.test_tool_handlers()
        await tester.test_tool_execution()
        await tester.test_performance()
        await tester.test_edge_cases()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"\n💥 Testing failed with critical error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
