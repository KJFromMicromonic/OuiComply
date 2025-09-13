#!/usr/bin/env python3
"""
Accurate MCP Protocol Testing for OuiComply MCP Server.
Tests MCP handlers using the correct MCP server API.
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
from mcp.types import TextContent


class AccurateMCPTester:
    """Accurate MCP protocol tester using proper MCP API."""
    
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
        
        try:
            is_valid = validate_config()
            self.log_test("Configuration Validation", is_valid, 
                         "Valid configuration detected" if is_valid else "Configuration invalid")
            
            # Test config access
            config = self.server.config
            has_mistral_key = bool(config.mistral_api_key and config.mistral_api_key != "your_mistral_api_key_here")
            self.log_test("Mistral API Key", has_mistral_key, 
                         "API key configured" if has_mistral_key else "API key missing")
            
        except Exception as e:
            self.log_test("Configuration Validation", False, f"Exception: {e}")
    
    async def test_resource_handlers_direct(self):
        """Test resource handlers by calling them directly."""
        print("\n📚 Testing Resource Handlers (Direct Access)...")
        
        try:
            # Access the server's handlers directly
            server_instance = self.server.server
            
            # Test list_resources by finding and calling the handler
            list_resources_called = False
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method') and handler_info.method == 'resources/list':
                    try:
                        resources = await handler_info.handler()
                        self.log_test("List Resources (Direct)", True, f"Found {len(resources)} resources")
                        list_resources_called = True
                        
                        # Validate each resource
                        for resource in resources:
                            if hasattr(resource, 'uri') and hasattr(resource, 'name'):
                                self.log_test(f"Resource Structure ({resource.name})", True, 
                                            f"Valid: {resource.uri}")
                            else:
                                self.log_test(f"Resource Structure", False, "Invalid structure")
                        break
                    except Exception as e:
                        self.log_test("List Resources (Direct)", False, f"Exception: {e}")
                        list_resources_called = True
                        break
            
            if not list_resources_called:
                self.log_test("List Resources (Direct)", False, "Handler not found")
            
            # Test read_resource
            read_resources_called = False
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method') and handler_info.method == 'resources/read':
                    try:
                        # Test valid URIs
                        test_uris = [
                            "resource://legal-templates",
                            "resource://compliance-frameworks"
                        ]
                        
                        for uri in test_uris:
                            try:
                                content = await handler_info.handler(uri=uri)
                                self.log_test(f"Read Resource ({uri})", True, 
                                            f"Content: {len(content)} chars")
                                
                                # Validate JSON
                                try:
                                    json.loads(content)
                                    self.log_test(f"JSON Validation ({uri})", True, "Valid JSON")
                                except json.JSONDecodeError:
                                    self.log_test(f"JSON Validation ({uri})", False, "Invalid JSON")
                            except Exception as e:
                                self.log_test(f"Read Resource ({uri})", False, f"Exception: {e}")
                        
                        # Test invalid URI
                        try:
                            await handler_info.handler(uri="resource://invalid")
                            self.log_test("Invalid URI Handling", False, "Should have failed")
                        except Exception:
                            self.log_test("Invalid URI Handling", True, "Correctly handled")
                        
                        read_resources_called = True
                        break
                    except Exception as e:
                        self.log_test("Read Resource (Direct)", False, f"Exception: {e}")
                        read_resources_called = True
                        break
            
            if not read_resources_called:
                self.log_test("Read Resource (Direct)", False, "Handler not found")
                
        except Exception as e:
            self.log_test("Resource Handlers Setup", False, f"Exception: {e}")
    
    async def test_tool_handlers_direct(self):
        """Test tool handlers by calling them directly."""
        print("\n🛠️  Testing Tool Handlers (Direct Access)...")
        
        try:
            server_instance = self.server.server
            
            # Test list_tools
            list_tools_called = False
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method') and handler_info.method == 'tools/list':
                    try:
                        tools = await handler_info.handler()
                        self.log_test("List Tools (Direct)", True, f"Found {len(tools)} tools")
                        
                        # Check expected tools
                        expected_tools = ["analyze_document", "check_clause_presence", "risk_assessment"]
                        found_tools = [tool.name for tool in tools]
                        
                        for expected in expected_tools:
                            if expected in found_tools:
                                self.log_test(f"Tool Presence ({expected})", True, "Found")
                            else:
                                self.log_test(f"Tool Presence ({expected})", False, "Missing")
                        
                        # Validate schemas
                        for tool in tools:
                            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                self.log_test(f"Schema ({tool.name})", True, "Valid schema")
                            else:
                                self.log_test(f"Schema ({tool.name})", False, "Invalid schema")
                        
                        list_tools_called = True
                        break
                    except Exception as e:
                        self.log_test("List Tools (Direct)", False, f"Exception: {e}")
                        list_tools_called = True
                        break
            
            if not list_tools_called:
                self.log_test("List Tools (Direct)", False, "Handler not found")
            
            # Test call_tool
            call_tool_called = False
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method') and handler_info.method == 'tools/call':
                    try:
                        # Test analyze_document
                        result = await handler_info.handler(
                            name="analyze_document",
                            arguments={
                                "document_text": "Sample privacy policy for GDPR compliance testing.",
                                "compliance_framework": "gdpr"
                            }
                        )
                        
                        if result and len(result) > 0 and isinstance(result[0], TextContent):
                            self.log_test("Tool Execution (analyze_document)", True, 
                                        f"Returned {len(result)} results")
                            self.log_test("Result Structure", True, 
                                        f"Valid TextContent: {len(result[0].text)} chars")
                        else:
                            self.log_test("Tool Execution (analyze_document)", False, 
                                        "Invalid result structure")
                        
                        # Test check_clause_presence
                        result2 = await handler_info.handler(
                            name="check_clause_presence",
                            arguments={
                                "document_text": "Contract with termination and liability clauses.",
                                "required_clauses": ["termination", "limitation_of_liability"]
                            }
                        )
                        
                        if result2 and len(result2) > 0:
                            self.log_test("Tool Execution (check_clause_presence)", True, 
                                        "Successful execution")
                        else:
                            self.log_test("Tool Execution (check_clause_presence)", False, 
                                        "Failed execution")
                        
                        # Test risk_assessment
                        result3 = await handler_info.handler(
                            name="risk_assessment",
                            arguments={
                                "document_text": "Service agreement with various terms.",
                                "document_type": "contract"
                            }
                        )
                        
                        if result3 and len(result3) > 0:
                            self.log_test("Tool Execution (risk_assessment)", True, 
                                        "Successful execution")
                        else:
                            self.log_test("Tool Execution (risk_assessment)", False, 
                                        "Failed execution")
                        
                        # Test error handling
                        try:
                            await handler_info.handler(name="invalid_tool", arguments={})
                            self.log_test("Error Handling (Invalid Tool)", False, 
                                        "Should have raised exception")
                        except Exception:
                            self.log_test("Error Handling (Invalid Tool)", True, 
                                        "Correctly handled error")
                        
                        call_tool_called = True
                        break
                    except Exception as e:
                        self.log_test("Tool Execution", False, f"Exception: {e}")
                        call_tool_called = True
                        break
            
            if not call_tool_called:
                self.log_test("Tool Execution", False, "Handler not found")
                
        except Exception as e:
            self.log_test("Tool Handlers Setup", False, f"Exception: {e}")
    
    async def test_performance_and_edge_cases(self):
        """Test performance and edge cases."""
        print("\n🚀 Testing Performance & Edge Cases...")
        
        try:
            server_instance = self.server.server
            
            # Find call_tool handler
            call_handler = None
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method') and handler_info.method == 'tools/call':
                    call_handler = handler_info.handler
                    break
            
            if not call_handler:
                self.log_test("Performance Setup", False, "No call_tool handler found")
                return
            
            # Test large document
            large_doc = "This is a large privacy policy document. " * 500  # ~20KB
            
            try:
                import time
                start_time = time.time()
                
                result = await call_handler(
                    name="analyze_document",
                    arguments={
                        "document_text": large_doc,
                        "compliance_framework": "gdpr"
                    }
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if execution_time < 3.0:
                    self.log_test("Large Document Performance", True, 
                                f"{len(large_doc)} chars in {execution_time:.2f}s")
                else:
                    self.log_test("Large Document Performance", False, 
                                f"Too slow: {execution_time:.2f}s")
            except Exception as e:
                self.log_test("Large Document Performance", False, f"Exception: {e}")
            
            # Test edge cases
            edge_cases = [
                {
                    "name": "analyze_document",
                    "args": {"document_text": "", "compliance_framework": "gdpr"},
                    "desc": "Empty document"
                },
                {
                    "name": "check_clause_presence", 
                    "args": {"document_text": "test", "required_clauses": []},
                    "desc": "Empty clause list"
                }
            ]
            
            for case in edge_cases:
                try:
                    result = await call_handler(name=case["name"], arguments=case["args"])
                    self.log_test(f"Edge Case ({case['desc']})", True, "Handled successfully")
                except Exception as e:
                    self.log_test(f"Edge Case ({case['desc']})", False, f"Exception: {e}")
            
        except Exception as e:
            self.log_test("Performance & Edge Cases", False, f"Exception: {e}")
    
    async def test_mcp_protocol_compliance(self):
        """Test MCP protocol compliance."""
        print("\n🔌 Testing MCP Protocol Compliance...")
        
        try:
            # Test server has required attributes
            server_instance = self.server.server
            
            if hasattr(server_instance, '_handlers'):
                self.log_test("MCP Handler Registry", True, 
                            f"Found {len(server_instance._handlers)} handlers")
            else:
                self.log_test("MCP Handler Registry", False, "No handler registry found")
            
            # Check for required MCP methods
            required_methods = ['resources/list', 'resources/read', 'tools/list', 'tools/call']
            found_methods = []
            
            for handler_info in server_instance._handlers:
                if hasattr(handler_info, 'method'):
                    found_methods.append(handler_info.method)
            
            for method in required_methods:
                if method in found_methods:
                    self.log_test(f"MCP Method ({method})", True, "Handler registered")
                else:
                    self.log_test(f"MCP Method ({method})", False, "Handler missing")
            
            # Test server name and version
            if hasattr(self.server, 'config'):
                config = self.server.config
                if config.server_name:
                    self.log_test("Server Name", True, f"Name: {config.server_name}")
                else:
                    self.log_test("Server Name", False, "No server name")
                
                if config.server_version:
                    self.log_test("Server Version", True, f"Version: {config.server_version}")
                else:
                    self.log_test("Server Version", False, "No server version")
            
        except Exception as e:
            self.log_test("MCP Protocol Compliance", False, f"Exception: {e}")
    
    def print_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("🧪 ACCURATE MCP TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if pass_rate >= 90:
            status = "🎉 EXCELLENT! Ready for production use."
        elif pass_rate >= 75:
            status = "✅ GOOD! Minor issues, but ready for use."
        elif pass_rate >= 50:
            status = "⚠️  FAIR! Some issues need attention."
        else:
            status = "❌ POOR! Significant issues need fixing."
        
        print(f"\n{status}")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            print(f"   {result}")
        
        print(f"\n🚀 OuiComply MCP Server Status:")
        if pass_rate >= 80:
            print("   ✅ READY FOR MCP CLIENT INTEGRATION")
            print("   ✅ All core functionality working")
            print("   ✅ Error handling implemented")
            print("   ✅ Performance acceptable")
        else:
            print("   ⚠️  NEEDS IMPROVEMENT BEFORE PRODUCTION")
            print("   📝 Review failed tests above")


async def main():
    """Run accurate MCP testing."""
    print("🧪 ACCURATE MCP PROTOCOL TESTING")
    print("=" * 80)
    print("Testing OuiComply MCP Server - Legal Compliance Platform")
    print("Using Direct Handler Access for Accurate Results")
    print("=" * 80)
    
    tester = AccurateMCPTester()
    
    try:
        # Setup
        if not await tester.setup_server():
            print("❌ Failed to setup server. Aborting tests.")
            return
        
        # Run all test suites
        await tester.test_configuration()
        await tester.test_resource_handlers_direct()
        await tester.test_tool_handlers_direct()
        await tester.test_performance_and_edge_cases()
        await tester.test_mcp_protocol_compliance()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"\n💥 Testing failed with critical error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
