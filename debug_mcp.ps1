# OuiComply MCP Inspector Debug Script for PowerShell
# This script provides easy commands to debug MCP servers

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$Server = "",
    
    [Parameter(Position=2)]
    [string]$Method = "tools/list"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OuiComply MCP Inspector Debug Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

switch ($Command.ToLower()) {
    "check" {
        Write-Host "Checking dependencies..." -ForegroundColor Yellow
        python debug_with_inspector.py --check
    }
    
    "list" {
        Write-Host "Listing available servers..." -ForegroundColor Yellow
        python debug_with_inspector.py --list
    }
    
    "standard" {
        Write-Host "Starting standard MCP server..." -ForegroundColor Green
        python debug_with_inspector.py --server standard
    }
    
    "fastmcp" {
        Write-Host "Starting FastMCP server..." -ForegroundColor Green
        python debug_with_inspector.py --server fastmcp
    }
    
    "alpic" {
        Write-Host "Starting ALPIC server..." -ForegroundColor Green
        python debug_with_inspector.py --server alpic
    }
    
    "inspector" {
        if ($Server) {
            Write-Host "Launching MCP Inspector with $Server server..." -ForegroundColor Green
            python debug_with_inspector.py --server $Server --inspector
        } else {
            Write-Host "Launching MCP Inspector..." -ForegroundColor Green
            python debug_with_inspector.py --inspector
        }
    }
    
    "test" {
        if ($Server) {
            Write-Host "Testing server: $Server with method: $Method" -ForegroundColor Yellow
            python debug_with_inspector.py --test $Server --method $Method
        } else {
            Write-Host "Error: Please specify a server to test" -ForegroundColor Red
            Write-Host "Usage: .\debug_mcp.ps1 test [server] [method]" -ForegroundColor Yellow
        }
    }
    
    default {
        Write-Host "Usage: .\debug_mcp.ps1 [command] [options]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Cyan
        Write-Host "  check                    - Check if all dependencies are installed" -ForegroundColor White
        Write-Host "  list                     - List available MCP servers" -ForegroundColor White
        Write-Host "  standard                 - Start standard MCP server" -ForegroundColor White
        Write-Host "  fastmcp                  - Start FastMCP server" -ForegroundColor White
        Write-Host "  alpic                    - Start ALPIC server" -ForegroundColor White
        Write-Host "  inspector [server]       - Launch inspector with optional server" -ForegroundColor White
        Write-Host "  test [server] [method]   - Test server via CLI" -ForegroundColor White
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  .\debug_mcp.ps1 check" -ForegroundColor White
        Write-Host "  .\debug_mcp.ps1 list" -ForegroundColor White
        Write-Host "  .\debug_mcp.ps1 standard" -ForegroundColor White
        Write-Host "  .\debug_mcp.ps1 inspector standard" -ForegroundColor White
        Write-Host "  .\debug_mcp.ps1 test standard tools/list" -ForegroundColor White
        Write-Host ""
    }
}
