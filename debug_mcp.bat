@echo off
REM OuiComply MCP Inspector Debug Script for Windows
REM This script provides easy commands to debug MCP servers

echo ========================================
echo OuiComply MCP Inspector Debug Helper
echo ========================================
echo.

if "%1"=="check" goto check_deps
if "%1"=="list" goto list_servers
if "%1"=="standard" goto start_standard
if "%1"=="fastmcp" goto start_fastmcp
if "%1"=="alpic" goto start_alpic
if "%1"=="inspector" goto launch_inspector
if "%1"=="test" goto test_server
goto show_help

:check_deps
echo Checking dependencies...
python debug_with_inspector.py --check
goto end

:list_servers
echo Listing available servers...
python debug_with_inspector.py --list
goto end

:start_standard
echo Starting standard MCP server...
python debug_with_inspector.py --server standard
goto end

:start_fastmcp
echo Starting FastMCP server...
python debug_with_inspector.py --server fastmcp
goto end

:start_alpic
echo Starting ALPIC server...
python debug_with_inspector.py --server alpic
goto end

:launch_inspector
echo Launching MCP Inspector...
python debug_with_inspector.py --server %2 --inspector
goto end

:test_server
echo Testing server: %2
python debug_with_inspector.py --test %2 --method %3
goto end

:show_help
echo Usage: debug_mcp.bat [command] [options]
echo.
echo Commands:
echo   check                    - Check if all dependencies are installed
echo   list                     - List available MCP servers
echo   standard                 - Start standard MCP server
echo   fastmcp                  - Start FastMCP server  
echo   alpic                    - Start ALPIC server
echo   inspector [server]       - Launch inspector with optional server
echo   test [server] [method]   - Test server via CLI
echo.
echo Examples:
echo   debug_mcp.bat check
echo   debug_mcp.bat list
echo   debug_mcp.bat standard
echo   debug_mcp.bat inspector standard
echo   debug_mcp.bat test standard tools/list
echo.

:end
pause
