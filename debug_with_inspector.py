#!/usr/bin/env python3
"""
OuiComply MCP Inspector Debug Helper

This script helps you debug your OuiComply MCP servers using the MCP Inspector.
It provides easy commands to start different server types and launch the inspector.

Usage:
    python debug_with_inspector.py --help
    python debug_with_inspector.py --server standard
    python debug_with_inspector.py --server fastmcp --inspector
    python debug_with_inspector.py --server alpic --port 3000
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

class MCPInspectorDebugger:
    """Helper class for debugging MCP servers with the MCP Inspector."""
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the MCP Inspector debugger.
        
        Args:
            project_root: Path to the OuiComply project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.config_file = self.project_root / "mcp-inspector-config.json"
        self.servers = {
            "standard": "mcp_server.py",
            "fastmcp": "mcp_fastmcp_server.py", 
            "alpic": "alpic_fastmcp_server.py",
            "vercel": "vercel_mcp_server.py",
            "simple": "simple_mcp_server.py",
            "rest": "mcp_rest_server.py"
        }
        
    def check_dependencies(self) -> bool:
        """
        Check if required dependencies are installed.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        print("🔍 Checking dependencies...")
        
        # Check if MCP Inspector is installed
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/inspector", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ MCP Inspector is installed")
            else:
                print("❌ MCP Inspector not found. Install with: npm install -g @modelcontextprotocol/inspector")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ MCP Inspector not found. Install with: npm install -g @modelcontextprotocol/inspector")
            return False
            
        # Check if Python dependencies are installed
        try:
            import mcp
            print("✅ MCP Python SDK is installed")
        except ImportError:
            print("❌ MCP Python SDK not found. Install with: pip install mcp")
            return False
            
        # Check if required Python packages are available
        required_packages = ["mistralai", "pydantic", "structlog"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} is installed")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} not found")
                
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install -r requirements.txt")
            return False
            
        return True
    
    def validate_config(self) -> bool:
        """
        Validate the MCP Inspector configuration file.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        print("🔍 Validating MCP Inspector configuration...")
        
        if not self.config_file.exists():
            print("❌ Configuration file not found: mcp-inspector-config.json")
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            if "mcpServers" not in config:
                print("❌ Invalid configuration: missing 'mcpServers' section")
                return False
                
            print("✅ Configuration file is valid")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
            return False
    
    def start_server(self, server_type: str, port: Optional[int] = None) -> subprocess.Popen:
        """
        Start a specific MCP server.
        
        Args:
            server_type: Type of server to start (standard, fastmcp, alpic, etc.)
            port: Optional port for HTTP servers
            
        Returns:
            Process object for the started server
        """
        if server_type not in self.servers:
            raise ValueError(f"Unknown server type: {server_type}")
            
        server_file = self.servers[server_type]
        server_path = self.project_root / server_file
        
        if not server_path.exists():
            raise FileNotFoundError(f"Server file not found: {server_path}")
            
        print(f"🚀 Starting {server_type} server: {server_file}")
        
        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        
        # Add API keys if available
        if "MISTRAL_KEY" in os.environ:
            env["MISTRAL_KEY"] = os.environ["MISTRAL_KEY"]
        if "LECHAT_API_KEY" in os.environ:
            env["LECHAT_API_KEY"] = os.environ["LECHAT_API_KEY"]
        if "GITHUB_TOKEN" in os.environ:
            env["GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]
            
        # Set port for HTTP servers
        if port:
            env["PORT"] = str(port)
            
        # Start the server
        process = subprocess.Popen(
            [sys.executable, str(server_path)],
            cwd=self.project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server a moment to start
        time.sleep(2)
        
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            raise RuntimeError("Server failed to start")
            
        print(f"✅ {server_type} server started (PID: {process.pid})")
        return process
    
    def launch_inspector(self, server_name: Optional[str] = None, port: int = 6274) -> None:
        """
        Launch the MCP Inspector.
        
        Args:
            server_name: Specific server to connect to (optional)
            port: Port for the inspector web interface
        """
        print(f"🔍 Launching MCP Inspector on port {port}...")
        
        cmd = ["npx", "@modelcontextprotocol/inspector"]
        
        if self.config_file.exists():
            cmd.extend(["--config", str(self.config_file)])
            
        if server_name:
            cmd.extend(["--server", server_name])
            
        try:
            subprocess.run(cmd, cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n🛑 Inspector stopped by user")
        except Exception as e:
            print(f"❌ Error launching inspector: {e}")
    
    def test_server_cli(self, server_name: str, method: str = "tools/list") -> None:
        """
        Test a server using CLI mode.
        
        Args:
            server_name: Name of the server to test
            method: MCP method to test
        """
        print(f"🧪 Testing {server_name} server with method: {method}")
        
        cmd = [
            "npx", "@modelcontextprotocol/inspector", 
            "--cli",
            "--config", str(self.config_file),
            "--server", server_name,
            "--method", method
        ]
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
            print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            print(f"Exit code: {result.returncode}")
        except Exception as e:
            print(f"❌ Error testing server: {e}")
    
    def list_available_servers(self) -> None:
        """List all available servers in the configuration."""
        print("📋 Available MCP servers:")
        
        if not self.config_file.exists():
            print("❌ Configuration file not found")
            return
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            for name, server_config in config.get("mcpServers", {}).items():
                server_type = server_config.get("type", "stdio")
                if server_type == "stdio":
                    command = server_config.get("command", "python")
                    args = " ".join(server_config.get("args", []))
                    print(f"  • {name}: {command} {args}")
                else:
                    url = server_config.get("url", "unknown")
                    print(f"  • {name}: {server_type} - {url}")
                    
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")


def main():
    """Main entry point for the debug script."""
    parser = argparse.ArgumentParser(
        description="Debug OuiComply MCP servers with MCP Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_with_inspector.py --check                    # Check dependencies
  python debug_with_inspector.py --list                    # List available servers
  python debug_with_inspector.py --server standard         # Start standard server
  python debug_with_inspector.py --server fastmcp --inspector  # Start server + inspector
  python debug_with_inspector.py --test standard tools/list    # Test server via CLI
        """
    )
    
    parser.add_argument("--check", action="store_true", help="Check dependencies")
    parser.add_argument("--list", action="store_true", help="List available servers")
    parser.add_argument("--server", choices=["standard", "fastmcp", "alpic", "vercel", "simple", "rest"], 
                       help="Server type to start")
    parser.add_argument("--inspector", action="store_true", help="Launch inspector after starting server")
    parser.add_argument("--port", type=int, default=3000, help="Port for HTTP servers")
    parser.add_argument("--test", help="Test server via CLI (server name)")
    parser.add_argument("--method", default="tools/list", help="MCP method to test")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    
    args = parser.parse_args()
    
    debugger = MCPInspectorDebugger(args.project_root)
    
    try:
        if args.check:
            if debugger.check_dependencies():
                print("✅ All dependencies are available")
                sys.exit(0)
            else:
                print("❌ Some dependencies are missing")
                sys.exit(1)
                
        elif args.list:
            debugger.list_available_servers()
            
        elif args.test:
            debugger.test_server_cli(args.test, args.method)
            
        elif args.server:
            server_process = None
            try:
                # Start the server
                server_process = debugger.start_server(args.server, args.port)
                
                if args.inspector:
                    # Launch inspector
                    debugger.launch_inspector(args.server)
                else:
                    print(f"✅ {args.server} server is running (PID: {server_process.pid})")
                    print("Press Ctrl+C to stop the server")
                    server_process.wait()
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
            finally:
                if server_process and server_process.poll() is None:
                    server_process.terminate()
                    server_process.wait()
                    print("✅ Server stopped")
                    
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
