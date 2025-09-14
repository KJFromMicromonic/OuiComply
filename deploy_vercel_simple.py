#!/usr/bin/env python3
"""
Simple Vercel deployment guide and file checker.
"""

import os
import sys
from pathlib import Path


def check_files():
    """Check if all required files exist."""
    required_files = [
        'vercel.json',
        'api/mcp.py',
        'api/health.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True


def check_environment():
    """Check environment variables."""
    required_vars = ['MISTRAL_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   You can set these in the Vercel dashboard after deployment")
        return False
    
    print("✅ Environment variables found")
    return True


def show_deployment_instructions():
    """Show step-by-step deployment instructions."""
    print("\n" + "=" * 60)
    print("🚀 VERCEL DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 STEP 1: Prepare Your Repository")
    print("   1. Push your code to GitHub")
    print("   2. Ensure all files are committed:")
    print("      - vercel.json")
    print("      - api/mcp.py")
    print("      - api/health.py")
    print("      - requirements.txt")
    print("      - src/ directory")
    
    print("\n🌐 STEP 2: Deploy via Vercel Dashboard")
    print("   1. Go to https://vercel.com/dashboard")
    print("   2. Click 'New Project'")
    print("   3. Import your GitHub repository")
    print("   4. Configure project:")
    print("      - Framework Preset: 'Other'")
    print("      - Root Directory: './' (or leave empty)")
    print("      - Build Command: (leave empty)")
    print("      - Output Directory: (leave empty)")
    print("   5. Click 'Deploy'")
    
    print("\n🔧 STEP 3: Set Environment Variables")
    print("   1. Go to Project Settings → Environment Variables")
    print("   2. Add these variables:")
    print("      - MISTRAL_API_KEY: your_mistral_api_key")
    print("      - LECHAT_API_KEY: your_lechat_api_key (optional)")
    print("      - LOG_LEVEL: INFO")
    print("   3. Redeploy after adding variables")
    
    print("\n🧪 STEP 4: Test Your Deployment")
    print("   1. Get your deployment URL (e.g., https://your-app.vercel.app)")
    print("   2. Test health check:")
    print("      curl https://your-app.vercel.app/health")
    print("   3. Run automated tests:")
    print("      python test_vercel_deployment.py")
    
    print("\n🔗 STEP 5: Configure Le Chat")
    print("   1. Use your MCP server URL:")
    print("      https://your-app.vercel.app/mcp")
    print("   2. Add to Le Chat MCP configuration")
    print("   3. Test the connection")
    
    print("\n" + "=" * 60)
    print("🎉 Your MCP server will be ready for Le Chat integration!")
    print("=" * 60)


def show_manual_deployment():
    """Show manual deployment steps."""
    print("\n📝 MANUAL DEPLOYMENT STEPS")
    print("-" * 40)
    
    print("\n1. Install Vercel CLI (if you want to use CLI):")
    print("   npm install -g vercel")
    print("   # OR")
    print("   yarn global add vercel")
    
    print("\n2. Login to Vercel:")
    print("   vercel login")
    
    print("\n3. Deploy:")
    print("   vercel --prod")
    
    print("\n4. Follow the prompts:")
    print("   - Set up and deploy? Y")
    print("   - Which scope? (choose your account)")
    print("   - Link to existing project? N")
    print("   - Project name? ouicomply-mcp")
    print("   - Directory? ./")


def main():
    """Main deployment checker."""
    print("🚀 OuiComply MCP Server - Vercel Deployment Checker")
    print("=" * 60)
    
    # Check prerequisites
    print("\n1. Checking prerequisites...")
    
    if not check_files():
        print("❌ Missing required files. Please ensure all files are present.")
        return False
    
    check_environment()  # This is just a warning, not a blocker
    
    # Show deployment instructions
    show_deployment_instructions()
    
    # Show manual deployment option
    print("\n" + "=" * 60)
    print("🛠️  ALTERNATIVE: Manual CLI Deployment")
    print("=" * 60)
    show_manual_deployment()
    
    print("\n" + "=" * 60)
    print("✅ Ready for deployment!")
    print("Choose either the dashboard method or CLI method above.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
