@echo off
REM ClutchG Setup and Test Script
REM สคริปต์ติดตั้งและทดสอบ ClutchG App

setlocal enabledelayedexpansion

echo ============================================================
echo ClutchG Setup and Test Script
echo ============================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "SRC_DIR=%SCRIPT_DIR%src"

REM Step 1: Check Python
echo Step 1: Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [OK] Python found
    python --version
) else (
    echo [ERROR] Python not found! Please install Python 3.11+ first.
    pause
    exit /b 1
)
echo.

REM Step 2: Install Dependencies
echo Step 2: Installing dependencies...
echo Running: pip install -r requirements.txt
echo.
cd "%SCRIPT_DIR%"
pip install -r requirements.txt
if %ERRORLEVEL%==0 (
    echo.
    echo [OK] Dependencies installed successfully
) else (
    echo.
    echo [ERROR] Failed to install dependencies
    echo Try running manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

REM Step 3: Test Imports
echo Step 3: Testing imports...
python "%SRC_DIR%\test_imports.py"
if %ERRORLEVEL%==0 (
    echo [OK] All imports successful
) else (
    echo [ERROR] Import test failed
    pause
    exit /b 1
)
echo.

REM Step 4: Test App Initialization
echo Step 4: Testing app initialization...
python "%SRC_DIR%\test_app_init.py"
if %ERRORLEVEL%==0 (
    echo [OK] App initialization successful
) else (
    echo [ERROR] App initialization failed
    pause
    exit /b 1
)
echo.

REM Step 5: Launch App
echo Step 5: Launching ClutchG App...
echo.
echo Press Ctrl+C to stop the app
echo.
python "%SRC_DIR%\app_minimal.py"

if %ERRORLEVEL NEQ 0 (
    echo.
    echo [ERROR] App launch failed
    echo.
    echo For debugging, try:
    echo 1. cd "%SRC_DIR%"
    echo 2. python app_minimal.py
    echo.
    echo And check the error message carefully
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ClutchG ran successfully!
echo ============================================================
pause
