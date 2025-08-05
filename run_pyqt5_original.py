#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - PyQt5 Original Style Launcher
شرکت فناوری نوآئران مثبت سبز
راه‌انداز نسخه PyQt5 با طراحی مشابه نسخه اولیه
"""

import sys
import os

def check_dependencies():
    """بررسی وابستگی‌ها"""
    print("=" * 70)
    print("Persian File Copier Pro - PyQt5 Original Style Edition")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("نسخه PyQt5 با طراحی مشابه نسخه اولیه CustomTkinter")
    print("=" * 70)
    
    missing_deps = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ مورد نیاز است")
        return False
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Check PyQt5
    try:
        import PyQt5
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"✓ PyQt5 {QT_VERSION_STR}")
    except ImportError:
        print("❌ PyQt5 یافت نشد")
        missing_deps.append("PyQt5")
    
    # Check psutil
    try:
        import psutil
        print(f"✓ psutil {psutil.__version__}")
    except ImportError:
        print("❌ psutil یافت نشد")
        missing_deps.append("psutil")
    
    # Check requests
    try:
        import requests
        print(f"✓ requests {requests.__version__}")
    except ImportError:
        print("❌ requests یافت نشد")
        missing_deps.append("requests")
    
    if missing_deps:
        print(f"\n❌ وابستگی‌های زیر یافت نشدند:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nبرای نصب:")
        print("pip install PyQt5 psutil requests")
        return False
    
    print("\n🚀 در حال راه‌اندازی نسخه PyQt5 اصلی...")
    return True

def main():
    """تابع اصلی"""
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        # Import and run PyQt5 original application
        print("📁 بارگذاری ماژول PyQt5...")
        from main_app_pyqt5_original_style import main as run_pyqt5_app
        
        print("🎨 راه‌اندازی رابط کاربری PyQt5...")
        run_pyqt5_app()
        
    except ImportError as e:
        print(f"❌ خطا در import: {e}")
        print("لطفاً مطمئن شوید که فایل main_app_pyqt5_original_style.py موجود است")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        print("\nجزئیات خطا:")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()