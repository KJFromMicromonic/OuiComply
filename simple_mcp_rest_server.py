#!/usr/bin/env python3
"""
Simple OuiComply MCP REST Server - Exposes MCP functions as REST API endpoints

This server exposes MCP tools and resources as REST API endpoints
accessible via /mcp/{function} routes, following the pattern that worked before.

Author: OuiComply Team
Version: 2.0.0
License: Apache 2.0
"""

import json
import logging
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OuiComplyMCPRESTServer:
    """OuiComply MCP Server with REST API endpoints for Alpic deployment."""
    
    def __init__(self):
        """Initialize the MCP server."""
        logger.info("OuiComply MCP REST Server initialized")
    
    def analyze_document(self, arguments: dict) -> dict:
        """Analyze document for compliance issues."""
        try:
            document_content = arguments.get("document_content", "")
            document_type = arguments.get("document_type", "contract")
            frameworks = arguments.get("frameworks", ["gdpr", "sox"])
            
            # Simulate AI analysis (replace with actual implementation)
            analysis_result = {
                "document_type": document_type,
                "frameworks_checked": frameworks,
                "compliance_score": 85,
                "issues_found": [
                    {
                        "type": "data_retention",
                        "severity": "medium",
                        "description": "Document lacks clear data retention policy",
                        "recommendation": "Add specific data retention periods"
                    }
                ],
                "recommendations": [
                    "Add data retention policy",
                    "Include privacy notice",
                    "Specify data processing purposes"
                ],
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": analysis_result,
                "metadata": {
                    "analysis_timestamp": datetime.now(UTC).isoformat(),
                    "content_length": len(document_content)
                }
            }
        except Exception as e:
            logger.error("Document analysis failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def update_memory(self, arguments: dict) -> dict:
        """Update team memory with insights."""
        try:
            team_id = arguments.get("team_id", "")
            insight = arguments.get("insight", "")
            category = arguments.get("category", "general")
            priority = arguments.get("priority", "medium")
            
            # Simulate memory update (replace with actual implementation)
            memory_entry = {
                "team_id": team_id,
                "insight": insight,
                "category": category,
                "priority": priority,
                "timestamp": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": memory_entry,
                "message": "Memory updated successfully"
            }
        except Exception as e:
            logger.error("Memory update failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_compliance_status(self, arguments: dict) -> dict:
        """Get compliance status for a team."""
        try:
            team_id = arguments.get("team_id", "")
            framework = arguments.get("framework")
            include_history = arguments.get("include_history", False)
            
            # Simulate compliance status (replace with actual implementation)
            status = {
                "team_id": team_id,
                "overall_score": 78,
                "frameworks": {
                    "gdpr": {"score": 85, "status": "compliant"},
                    "sox": {"score": 72, "status": "needs_attention"},
                    "ccpa": {"score": 80, "status": "compliant"}
                },
                "last_updated": datetime.now(UTC).isoformat()
            }
            
            return {
                "success": True,
                "data": status
            }
        except Exception as e:
            logger.error("Compliance status retrieval failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def get_compliance_frameworks(self) -> dict:
        """Get compliance frameworks resource."""
        return {
            "frameworks": {
                "gdpr": {
                    "name": "General Data Protection Regulation",
                    "description": "EU data protection and privacy regulation",
                    "requirements": ["Data minimization", "Consent management", "Right to be forgotten"]
                },
                "sox": {
                    "name": "Sarbanes-Oxley Act",
                    "description": "US financial reporting and corporate governance regulation",
                    "requirements": ["Internal controls", "Audit trails", "Financial transparency"]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    def get_legal_templates(self) -> dict:
        """Get legal templates resource."""
        return {
            "templates": {
                "privacy_policy": {
                    "name": "Privacy Policy Template",
                    "description": "GDPR-compliant privacy policy template",
                    "required_sections": ["Data collection", "Data usage", "User rights", "Contact information"]
                }
            },
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    def get_team_memory(self) -> dict:
        """Get team memory resource."""
        return {
            "teams": {},
            "global_insights": [],
            "last_updated": datetime.now(UTC).isoformat()
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server with REST API endpoints."""
        logger.info(f"Starting OuiComply MCP REST Server on {host}:{port}")
        
        class MCPRESTHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    parsed_path = urllib.parse.urlparse(self.path)
                    path_parts = parsed_path.path.strip('/').split('/')
                    
                    if self.path == '/health':
                        self._send_json_response(200, {
                            "status": "healthy",
                            "service": "OuiComply MCP REST Server",
                            "version": "2.0.0",
                            "timestamp": datetime.now(UTC).isoformat(),
                            "mcp_server": "running",
                            "endpoints": {
                                "analyze_document": "/mcp/analyze_document",
                                "update_memory": "/mcp/update_memory",
                                "get_compliance_status": "/mcp/get_compliance_status",
                                "compliance_frameworks": "/mcp/compliance_frameworks",
                                "legal_templates": "/mcp/legal_templates",
                                "team_memory": "/mcp/team_memory"
                            }
                        })
                    elif self.path == '/oauth/metadata':
                        self._send_json_response(200, {
                            "jsonrpc": "2.0",
                            "id": "alpic-request",
                            "result": {
                                "oauth": {
                                    "version": "2.0.0",
                                    "server_name": "ouicomply-mcp",
                                    "capabilities": {
                                        "tools": True,
                                        "resources": True,
                                        "prompts": False,
                                        "logging": True
                                    },
                                    "status": "ready"
                                }
                            }
                        })
                    elif path_parts[0] == 'mcp' and len(path_parts) == 2:
                        # Handle /mcp/{function} endpoints
                        function_name = path_parts[1]
                        if function_name in ['compliance_frameworks', 'legal_templates', 'team_memory']:
                            # Handle resource endpoints
                            if function_name == 'compliance_frameworks':
                                result = self.server.get_compliance_frameworks()
                            elif function_name == 'legal_templates':
                                result = self.server.get_legal_templates()
                            elif function_name == 'team_memory':
                                result = self.server.get_team_memory()
                            
                            self._send_json_response(200, result)
                        else:
                            self._send_json_response(404, {"error": f"Unknown MCP function: {function_name}"})
                    else:
                        self._send_json_response(404, {"error": "Not found"})
                except Exception as e:
                    self._send_json_response(500, {"error": str(e)})
            
            def do_POST(self):
                try:
                    parsed_path = urllib.parse.urlparse(self.path)
                    path_parts = parsed_path.path.strip('/').split('/')
                    
                    if self.path == '/oauth/metadata':
                        self._send_json_response(200, {
                            "jsonrpc": "2.0",
                            "id": "alpic-request",
                            "result": {
                                "oauth": {
                                    "version": "2.0.0",
                                    "server_name": "ouicomply-mcp",
                                    "capabilities": {
                                        "tools": True,
                                        "resources": True,
                                        "prompts": False,
                                        "logging": True
                                    },
                                    "status": "ready"
                                }
                            }
                        })
                    elif path_parts[0] == 'mcp' and len(path_parts) == 2:
                        # Handle /mcp/{function} POST endpoints
                        function_name = path_parts[1]
                        
                        # Read request body
                        content_length = int(self.headers.get('Content-Length', 0))
                        post_data = self.rfile.read(content_length)
                        
                        try:
                            arguments = json.loads(post_data.decode('utf-8'))
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Call the appropriate MCP function
                        if function_name == 'analyze_document':
                            result = self.server.analyze_document(arguments)
                        elif function_name == 'update_memory':
                            result = self.server.update_memory(arguments)
                        elif function_name == 'get_compliance_status':
                            result = self.server.get_compliance_status(arguments)
                        else:
                            result = {"error": f"Unknown MCP function: {function_name}"}
                        
                        self._send_json_response(200, result)
                    else:
                        self._send_json_response(404, {"error": "Not found"})
                except Exception as e:
                    self._send_json_response(500, {"error": str(e)})
            
            def _send_json_response(self, status_code: int, data: dict):
                """Send JSON response."""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode())
            
            def log_message(self, format, *args):
                pass
        
        # Create and start server
        server = HTTPServer((host, port), MCPRESTHandler)
        # Set the server instance on the handler
        MCPRESTHandler.server = self
        
        logger.info(f"MCP REST Server started on {host}:{port}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error("Server error", error=str(e))
            raise


def main():
    """Main entry point for the MCP REST server."""
    # Get configuration from environment variables
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    
    print("🚀 Starting OuiComply MCP REST Server")
    print("=" * 50)
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌐 URL: http://{host}:{port}")
    print("🔗 MCP Endpoints:")
    print("  - /mcp/analyze_document")
    print("  - /mcp/update_memory")
    print("  - /mcp/get_compliance_status")
    print("  - /mcp/compliance_frameworks")
    print("  - /mcp/legal_templates")
    print("  - /mcp/team_memory")
    print("=" * 50)
    
    # Create and run the server
    server = OuiComplyMCPRESTServer()
    server.run(host=host, port=port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
