@echo off
echo Starting OuiComply MCP Server with ngrok...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install FastAPI dependencies if needed
echo Installing FastAPI dependencies...
pip install -r requirements_fastapi.txt

REM Start the MCP Server with ngrok
echo.
echo Starting MCP Server...
python start_ngrok_mcp.py

pause
