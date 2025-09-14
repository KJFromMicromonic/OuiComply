#!/usr/bin/env python3
"""
OuiComply Deployment Fix Script

This script fixes common deployment issues for Vercel and ALPIC platforms.
It ensures all configuration files are correct and dependencies are properly set.

Usage: python fix_deployments.py [vercel|alpic|both]
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class DeploymentFixer:
    """Fixes deployment configuration issues for OuiComply MCP Server."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.fixes_applied = []
        
    def fix_vercel_deployment(self) -> bool:
        """Fix Vercel deployment configuration."""
        print("🔧 Fixing Vercel deployment...")
        
        try:
            # Fix vercel.json
            vercel_config = {
                "version": 2,
                "builds": [
                    {
                        "src": "api/index.py",
                        "use": "@vercel/python"
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "/api/index.py"
                    }
                ],
                "env": {
                    "MISTRAL_KEY": "@mistral_key",
                    "LECHAT_API_KEY": "@lechat_api_key", 
                    "GITHUB_TOKEN": "@github_token"
                }
            }
            
            with open(self.project_root / "vercel.json", "w") as f:
                json.dump(vercel_config, f, indent=2)
            
            self.fixes_applied.append("✅ Fixed vercel.json configuration")
            
            # Ensure api/index.py exists and is correct
            api_file = self.project_root / "api" / "index.py"
            if not api_file.exists():
                print("❌ api/index.py not found!")
                return False
                
            # Fix requirements_vercel.txt
            requirements_content = """# OuiComply MCP Server Dependencies for Vercel Deployment
# Minimal dependencies to stay under 250MB limit

# Core FastAPI dependencies (minimal versions)
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Core Python dependencies
python-dotenv==1.0.0

# HTTP and networking
httpx==0.25.2

# Validation and schemas
jsonschema==4.20.0

# AI dependencies (minimal)
mistralai==1.9.10

# Document processing (minimal)
PyPDF2==3.0.0
python-docx==0.8.11

# Data processing (minimal)
pandas==2.0.0
numpy==1.24.0
"""
            
            with open(self.project_root / "requirements_vercel.txt", "w") as f:
                f.write(requirements_content)
            
            self.fixes_applied.append("✅ Fixed requirements_vercel.txt")
            
            # Create .vercelignore if it doesn't exist
            vercelignore_content = """# Vercel ignore file
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# OuiComply specific
docs/
tests/
*.md
!README.md
debug_*
test_*
mcp-inspector-config.json
alpic.yaml
requirements.txt
requirements_alpic.txt
mcp_server.py
mcp_fastmcp_server.py
alpic_fastmcp_server.py
alpic_instant_server.py
simple_*
robust_*
ultra_*
minimal_*
vercel_minimal.py
"""
            
            with open(self.project_root / ".vercelignore", "w") as f:
                f.write(vercelignore_content)
            
            self.fixes_applied.append("✅ Created .vercelignore")
            
            print("✅ Vercel deployment fixed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing Vercel deployment: {e}")
            return False
    
    def fix_alpic_deployment(self) -> bool:
        """Fix ALPIC deployment configuration."""
        print("🔧 Fixing ALPIC deployment...")
        
        try:
            # Fix alpic.yaml
            alpic_config = {
                "name": "ouicomply-mcp-server",
                "version": "1.0.0",
                "description": "OuiComply MCP Server - AI Assisted Legal Compliance Checker",
                "build": {
                    "command": "pip install -r requirements_alpic.txt",
                    "python_version": "3.12"
                },
                "runtime": {
                    "command": "python alpic_fastmcp_server.py",
                    "port": 8000,
                    "health_check": "http://localhost:8000/health"
                },
                "environment": {
                    "MISTRAL_API_KEY": "${MISTRAL_API_KEY}",
                    "REDIS_URL": "${REDIS_URL}",
                    "PORT": "8000",
                    "HOST": "0.0.0.0"
                },
                "mcp": {
                    "server_name": "ouicomply-mcp",
                    "server_version": "1.0.0",
                    "capabilities": {
                        "tools": True,
                        "resources": True,
                        "prompts": False,
                        "logging": True
                    }
                },
                "deployment": {
                    "auto_deploy": True,
                    "branch": "main",
                    "restart_policy": "on_failure",
                    "scaling": {
                        "min_instances": 1,
                        "max_instances": 10
                    }
                },
                "monitoring": {
                    "enabled": True,
                    "metrics": [
                        "request_count",
                        "response_time", 
                        "error_rate",
                        "mcp_tool_usage"
                    ],
                    "logs": {
                        "level": "info",
                        "retention_days": 30
                    }
                },
                "security": {
                    "rate_limiting": {
                        "enabled": True,
                        "requests_per_minute": 100
                    },
                    "authentication": {
                        "enabled": False,
                        "type": "api_key"
                    },
                    "cors": {
                        "enabled": True,
                        "origins": ["*"]
                    }
                }
            }
            
            with open(self.project_root / "alpic.yaml", "w") as f:
                yaml.dump(alpic_config, f, default_flow_style=False, indent=2)
            
            self.fixes_applied.append("✅ Fixed alpic.yaml configuration")
            
            # Ensure alpic_fastmcp_server.py exists
            alpic_file = self.project_root / "alpic_fastmcp_server.py"
            if not alpic_file.exists():
                print("❌ alpic_fastmcp_server.py not found!")
                return False
            
            # Fix requirements_alpic.txt
            requirements_content = """# OuiComply MCP Server Dependencies for Alpic Deployment
# Optimized for FastMCP with stdio transport

# Core MCP and FastMCP dependencies
mcp>=1.14.0
fastmcp>=0.1.0

# Core Python dependencies
pydantic>=2.10.3
pydantic-settings>=2.1.0
structlog>=23.2.0
python-dotenv>=1.0.0

# AI and ML dependencies
mistralai>=1.9.10

# HTTP and networking (minimal for stdio transport)
httpx>=0.25.0

# Document processing
PyPDF2>=3.0.0
python-docx>=0.8.11
Pillow>=10.0.0

# Data processing
pandas>=2.0.0
numpy>=1.24.0

# Validation and schemas
jsonschema>=4.17.0

# Async support
asyncio-mqtt>=0.16.0
"""
            
            with open(self.project_root / "requirements_alpic.txt", "w") as f:
                f.write(requirements_content)
            
            self.fixes_applied.append("✅ Fixed requirements_alpic.txt")
            
            print("✅ ALPIC deployment fixed!")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing ALPIC deployment: {e}")
            return False
    
    def create_deployment_scripts(self) -> bool:
        """Create deployment helper scripts."""
        print("🔧 Creating deployment scripts...")
        
        try:
            # Create Vercel deployment script
            vercel_script = """#!/bin/bash
# Vercel Deployment Script for OuiComply MCP Server

echo "🚀 Deploying OuiComply MCP Server to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Deploy to Vercel
echo "📦 Deploying to Vercel..."
vercel --prod

# Set environment variables
echo "🔑 Setting environment variables..."
vercel env add MISTRAL_KEY
vercel env add LECHAT_API_KEY
vercel env add GITHUB_TOKEN

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://your-app.vercel.app"
"""
            
            with open(self.project_root / "deploy_vercel.sh", "w") as f:
                f.write(vercel_script)
            
            # Create ALPIC deployment script
            alpic_script = """#!/bin/bash
# ALPIC Deployment Script for OuiComply MCP Server

echo "🚀 Deploying OuiComply MCP Server to ALPIC..."

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

# Commit and push changes
echo "📦 Committing changes..."
git add .
git commit -m "Deploy to ALPIC - $(date)"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Deployment initiated!"
echo "🌐 Check your ALPIC dashboard for deployment status"
echo "🔗 Your app will be available at: https://your-app.alpic.com"
"""
            
            with open(self.project_root / "deploy_alpic.sh", "w") as f:
                f.write(alpic_script)
            
            # Create Windows batch files
            vercel_bat = """@echo off
REM Vercel Deployment Script for OuiComply MCP Server

echo 🚀 Deploying OuiComply MCP Server to Vercel...

REM Check if Vercel CLI is installed
vercel --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
)

REM Deploy to Vercel
echo 📦 Deploying to Vercel...
vercel --prod

REM Set environment variables
echo 🔑 Setting environment variables...
vercel env add MISTRAL_KEY
vercel env add LECHAT_API_KEY
vercel env add GITHUB_TOKEN

echo ✅ Deployment complete!
echo 🌐 Your app is available at: https://your-app.vercel.app
pause
"""
            
            with open(self.project_root / "deploy_vercel.bat", "w") as f:
                f.write(vercel_bat)
            
            alpic_bat = """@echo off
REM ALPIC Deployment Script for OuiComply MCP Server

echo 🚀 Deploying OuiComply MCP Server to ALPIC...

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git not found. Please install Git first.
    pause
    exit /b 1
)

REM Commit and push changes
echo 📦 Committing changes...
git add .
git commit -m "Deploy to ALPIC - %date%"

echo 🚀 Pushing to GitHub...
git push origin main

echo ✅ Deployment initiated!
echo 🌐 Check your ALPIC dashboard for deployment status
echo 🔗 Your app will be available at: https://your-app.alpic.com
pause
"""
            
            with open(self.project_root / "deploy_alpic.bat", "w") as f:
                f.write(alpic_bat)
            
            self.fixes_applied.append("✅ Created deployment scripts")
            
            print("✅ Deployment scripts created!")
            return True
            
        except Exception as e:
            print(f"❌ Error creating deployment scripts: {e}")
            return False
    
    def run_all_fixes(self) -> bool:
        """Run all deployment fixes."""
        print("🔧 Running all deployment fixes...")
        
        success = True
        
        # Fix Vercel
        if not self.fix_vercel_deployment():
            success = False
        
        # Fix ALPIC
        if not self.fix_alpic_deployment():
            success = False
        
        # Create deployment scripts
        if not self.create_deployment_scripts():
            success = False
        
        return success
    
    def print_summary(self):
        """Print summary of fixes applied."""
        print("\n" + "="*50)
        print("🔧 DEPLOYMENT FIXES SUMMARY")
        print("="*50)
        
        for fix in self.fixes_applied:
            print(fix)
        
        print("\n📋 NEXT STEPS:")
        print("1. Set your environment variables:")
        print("   - MISTRAL_KEY: Your Mistral API key")
        print("   - LECHAT_API_KEY: Your LeChat API key (optional)")
        print("   - GITHUB_TOKEN: Your GitHub token (optional)")
        
        print("\n2. Deploy to Vercel:")
        print("   - Run: vercel --prod")
        print("   - Or use: deploy_vercel.bat (Windows) / deploy_vercel.sh (Linux/Mac)")
        
        print("\n3. Deploy to ALPIC:")
        print("   - Push to GitHub: git push origin main")
        print("   - Or use: deploy_alpic.bat (Windows) / deploy_alpic.sh (Linux/Mac)")
        
        print("\n4. Test your deployments:")
        print("   - Vercel: python test_vercel_deployment.py")
        print("   - ALPIC: python test_alpic_deployment.py")
        
        print("\n✅ All fixes applied successfully!")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix OuiComply deployment issues")
    parser.add_argument("platform", choices=["vercel", "alpic", "both"], 
                       default="both", nargs="?",
                       help="Platform to fix (default: both)")
    parser.add_argument("--project-root", default=".", 
                       help="Project root directory (default: current directory)")
    
    args = parser.parse_args()
    
    fixer = DeploymentFixer(args.project_root)
    
    print("🔧 OuiComply Deployment Fixer")
    print("="*40)
    
    success = True
    
    if args.platform in ["vercel", "both"]:
        if not fixer.fix_vercel_deployment():
            success = False
    
    if args.platform in ["alpic", "both"]:
        if not fixer.fix_alpic_deployment():
            success = False
    
    if args.platform == "both":
        if not fixer.create_deployment_scripts():
            success = False
    
    fixer.print_summary()
    
    if success:
        print("\n🎉 All deployment issues fixed!")
        sys.exit(0)
    else:
        print("\n❌ Some issues could not be fixed. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
