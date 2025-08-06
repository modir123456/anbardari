@echo off
chcp 65001 >nul
title Persian File Copier Pro - شرکت فناوری نوآوران مثبت سبز

echo =====================================
echo 🌟 Persian File Copier Pro
echo 📦 نسخه 3.5.0 - Professional Edition  
echo 🏢 شرکت فناوری نوآوران مثبت سبز
echo 📞 تلگرام: Scrubby3137
echo =====================================
echo.

echo 🚀 در حال راه‌اندازی...
python start.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️ خطا در اجرا با python، تلاش با python3...
    python3 start.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ خطا در اجرای برنامه!
    echo 📋 لطفاً Python 3.8+ نصب کنید
    echo 🌐 دانلود از: https://python.org
    pause
)

pause