@echo off
REM CUAD Contract Download Script for Windows
REM This script downloads all contracts from the CUAD dataset

echo ========================================
echo    CUAD Contract Download Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if huggingface_hub is installed
python -c "import huggingface_hub" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install huggingface_hub>=0.20.0
    if errorlevel 1 (
        echo ERROR: Failed to install huggingface_hub
        pause
        exit /b 1
    )
)

echo Starting contract download...
echo This may take several minutes depending on your internet connection.
echo.

REM Run the download script
python download_cuad_contracts.py

if errorlevel 1 (
    echo.
    echo Download completed with errors. Check the log file for details.
    pause
) else (
    echo.
    echo Download completed successfully!
    echo Contracts are now available in the docs/cuad_contracts folder.
    pause
)
