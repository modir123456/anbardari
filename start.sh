#!/bin/bash

# Persian File Copier Pro - Launcher Script
# شرکت فناوری نوآوران مثبت سبز

clear

echo "====================================="
echo "🌟 Persian File Copier Pro"
echo "📦 نسخه 3.5.0 - Professional Edition"  
echo "🏢 شرکت فناوری نوآوران مثبت سبز"
echo "📞 تلگرام: Scrubby3137"
echo "====================================="
echo

echo "🚀 در حال راه‌اندازی..."

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 start.py
elif command -v python &> /dev/null; then
    python start.py
else
    echo "❌ خطا: Python یافت نشد!"
    echo "📋 لطفاً Python 3.8+ نصب کنید"
    echo "🌐 دانلود از: https://python.org"
    echo
    echo "برای ادامه Enter را فشار دهید..."
    read
    exit 1
fi

echo
echo "🙏 از استفاده از Persian File Copier Pro متشکریم!"
echo "برای خروج Enter را فشار دهید..."
read