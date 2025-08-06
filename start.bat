@echo off
title Persian File Copier Pro

echo =====================================
echo Persian File Copier Pro
echo Version 3.5.0 - Professional Edition  
echo Positive Green Innovation Tech Company
echo Telegram: Scrubby3137
echo =====================================
echo.

echo Starting application...
python start.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error with python, trying python3...
    python3 start.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error running application!
    echo Please install Python 3.8+
    echo Download from: https://python.org
    pause
)

pause