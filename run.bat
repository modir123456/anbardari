@echo off
title Persian File Copier Pro - C# Edition
color 0A

echo.
echo ============================================
echo  Persian File Copier Pro 3.5.0 - C# Edition
echo  فارسی کاپیر فایل حرفه‌ای - نسخه C#
echo ============================================
echo.

if not exist "PersianFileCopierPro.exe" (
    echo Building application...
    dotnet publish -c Release -o . --self-contained false
    if errorlevel 1 (
        echo Failed to build application!
        pause
        exit /b 1
    )
)

echo Starting Persian File Copier Pro...
echo.
echo 🌐 Server will be available at: http://localhost:8548
echo 📱 Open this URL in your web browser to access the application
echo.
echo Press Ctrl+C to stop the server
echo.

PersianFileCopierPro.exe

pause