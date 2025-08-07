@echo off
title Persian File Copier Pro
echo ========================================
echo Persian File Copier Pro - Desktop Mode
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting Persian File Copier Pro in Desktop Mode...
echo.

REM Start server in background
start /b python main.py

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

echo Server started. Opening application...

REM Try different browsers in app mode
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Opening with Google Chrome...
    start "Persian File Copier Pro" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:8548 --new-window --disable-web-security --disable-features=VizDisplayCompositor --window-size=1400,900 --window-position=100,50
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo Opening with Google Chrome...
    start "Persian File Copier Pro" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --app=http://localhost:8548 --new-window --disable-web-security --disable-features=VizDisplayCompositor --window-size=1400,900 --window-position=100,50
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo Opening with Microsoft Edge...
    start "Persian File Copier Pro" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50
) else (
    echo Opening with default browser...
    start "Persian File Copier Pro" http://localhost:8548
)

echo.
echo ========================================
echo Persian File Copier Pro is now running!
echo ========================================
echo.
echo To stop the application:
echo 1. Close the application window
echo 2. Press Ctrl+C in this console
echo.
echo Application URL: http://localhost:8548
echo.

REM Keep console open until user stops
pause