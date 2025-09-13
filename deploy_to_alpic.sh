#!/bin/bash
# Alpic deployment script for OuiComply MCP Server

echo "🚀 Deploying OuiComply MCP Server to Alpic..."

# Check if alpic CLI is installed
if ! command -v alpic &> /dev/null; then
    echo "❌ Alpic CLI not found. Please install it first."
    echo "   Visit: https://alpic.ai/docs/installation"
    exit 1
fi

# Check if logged in
if ! alpic whoami &> /dev/null; then
    echo "❌ Not logged in to Alpic. Please run: alpic login"
    exit 1
fi

# Deploy the application
echo "📦 Deploying application..."
alpic deploy --config alpic.json

echo "✅ Deployment complete!"
echo "🔗 Your MCP Server will be available at the provided URL"
echo "📋 Use the MCP endpoint for Le Chat integration"
