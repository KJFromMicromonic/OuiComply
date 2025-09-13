# OuiComply MCP Server with ngrok - PowerShell Script
# This script starts the MCP server and exposes it via ngrok

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OuiComply MCP Server with ngrok" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if ngrok is available
try {
    $ngrokVersion = ngrok version 2>&1
    Write-Host "✅ ngrok found: $ngrokVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install ngrok from https://ngrok.com/ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (Test-Path "Scripts\activate.ps1") {
    Write-Host "✅ Virtual environment found" -ForegroundColor Green
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "Scripts\activate.ps1"
} else {
    Write-Host "⚠️  WARNING: Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Make sure you're in the correct directory with a Python virtual environment" -ForegroundColor Yellow
    Write-Host ""
}

# Install/upgrade required packages
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install aiohttp requests

Write-Host ""
Write-Host "🚀 Starting MCP Server with ngrok..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the ngrok MCP server
try {
    python run_ngrok_mcp.py
} catch {
    Write-Host "❌ Error running MCP server: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
