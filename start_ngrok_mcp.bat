@echo off
REM OuiComply MCP Server with ngrok - Windows Batch Script
REM This script starts the MCP server and exposes it via ngrok

echo ========================================
echo OuiComply MCP Server with ngrok
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if ngrok is available
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok is not installed or not in PATH
    echo Please install ngrok from https://ngrok.com/ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "Scripts\activate.bat" (
    echo WARNING: Virtual environment not found
    echo Make sure you're in the correct directory with a Python virtual environment
    echo.
)

REM Activate virtual environment if it exists
if exist "Scripts\activate.bat" (
    echo Activating virtual environment...
    call Scripts\activate.bat
)

REM Install/upgrade required packages
echo Installing required packages...
pip install -r requirements.txt
pip install aiohttp requests

echo.
echo Starting MCP Server with ngrok...
echo Press Ctrl+C to stop the server
echo.

REM Run the ngrok MCP server
python run_ngrok_mcp.py

pause
