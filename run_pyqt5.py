#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - PyQt5 Launcher
شرکت فناوری نوآئران مثبت سبز
"""

import sys
import os

def check_dependencies():
    """بررسی وابستگی‌ها"""
    print("=" * 60)
    print("Persian File Copier Pro v3.0 - PyQt5 Professional Edition")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("=" * 60)
    
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
        print(f"✓ PyQt5 {PyQt5.Qt.PYQT_VERSION_STR}")
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
    
    # Check Pillow
    try:
        import PIL
        print(f"✓ Pillow {PIL.__version__}")
    except ImportError:
        print("❌ Pillow یافت نشد")
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("\n❌ وابستگی‌های زیر یافت نشدند:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nبرای نصب:")
        print("pip install -r requirements_pyqt5.txt")
        return False
    
    print("\n🚀 در حال راه‌اندازی نرم‌افزار...")
    return True

def main():
    """تابع اصلی لانچر"""
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        # Import and run main application
        from main_app_pyqt5 import main
        main()
        
    except ImportError as e:
        print(f"❌ خطا در import: {e}")
        print("لطفاً مطمئن شوید که فایل main_app_pyqt5.py موجود است")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()