@echo off
title Persian File Copier Pro - فارسی کاپیر فایل حرفه‌ای
color 0A

echo.
echo ================================================================================================
echo.
echo                    Persian File Copier Pro v3.5.0
echo                       فارسی کاپیر فایل حرفه‌ای
echo.
echo ================================================================================================
echo.

REM Set encoding to UTF-8
chcp 65001 >nul

REM Check for admin rights
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [تحذير] برای دسترسی کامل، ترجیحاً برنامه را به عنوان مدیر اجرا کنید.
    echo.
)

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [خطا] پایتون نصب نیست!
    echo لطفاً از لینک زیر پایتون 3.8+ نصب کنید:
    echo https://python.org
    echo.
    pause
    exit /b 1
)

echo [✓] پایتون موجود است
python --version

REM Create virtual environment if not exists
if not exist "venv" (
    echo.
    echo [...] ایجاد محیط مجازی پایتون...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [خطا] ایجاد محیط مجازی ناموفق بود!
        pause
        exit /b 1
    )
    echo [✓] محیط مجازی ایجاد شد
) else (
    echo [✓] محیط مجازی موجود است
)

REM Activate virtual environment
echo.
echo [...] فعال‌سازی محیط مجازی...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [خطا] فعال‌سازی محیط مجازی ناموفق بود!
    pause
    exit /b 1
)

REM Update pip
echo.
echo [...] به‌روزرسانی pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo.
echo [...] نصب وابستگی‌ها...
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [خطا] نصب وابستگی‌ها ناموفق بود!
    pause
    exit /b 1
)

echo [✓] همه وابستگی‌ها نصب شدند

REM Start application
echo.
echo ================================================================================================
echo.
echo [🚀] راه‌اندازی Persian File Copier Pro...
echo.
echo [📡] سرور: http://localhost:8548
echo [📖] مستندات: http://localhost:8548/docs
echo [🔧] برای توقف: Ctrl+C در این کنسول
echo.
echo ================================================================================================
echo.

REM Start server in background and open browser
start /b python main.py

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Try to open in app mode with different browsers
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [🌐] باز کردن با Google Chrome...
    start "Persian File Copier Pro" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo [🌐] باز کردن با Google Chrome...
    start "Persian File Copier Pro" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo [🌐] باز کردن با Microsoft Edge...
    start "Persian File Copier Pro" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo [🌐] باز کردن با Microsoft Edge...
    start "Persian File Copier Pro" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://localhost:8548 --new-window --window-size=1400,900 --window-position=100,50
) else (
    echo [🌐] باز کردن با مرورگر پیش‌فرض...
    start http://localhost:8548
)

echo.
echo Persian File Copier Pro در حال اجرا است!
echo.
echo برای توقف: Ctrl+C فشار دهید
echo.

REM Keep console open
pause