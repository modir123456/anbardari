#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Persian File Copier Pro - Enhanced Edition Launcher
شرکت فناوری نوآئران مثبت سبز
راه‌انداز نسخه پیشرفته با UI بهبود یافته
"""

import sys
import os
import subprocess

def check_dependencies():
    """بررسی وابستگی‌ها"""
    print("=" * 70)
    print("Persian File Copier Pro - Enhanced UI/UX Edition v2.0")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("نسخه پیشرفته با UI بهبود یافته و عملکرد روان‌تر")
    print("=" * 70)
    
    missing_deps = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ مورد نیاز است")
        return False
    else:
        print(f"✓ Python {sys.version.split()[0]}")
    
    # Check tkinter
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        print("❌ tkinter یافت نشد")
        missing_deps.append("tkinter")
    
    # Check customtkinter
    try:
        import customtkinter
        print(f"✓ customtkinter {customtkinter.__version__}")
    except ImportError:
        print("❌ customtkinter یافت نشد")
        missing_deps.append("customtkinter")
    
    # Check psutil
    try:
        import psutil
        print(f"✓ psutil {psutil.__version__}")
    except ImportError:
        print("❌ psutil یافت نشد")
        missing_deps.append("psutil")
    
    if missing_deps:
        print(f"\n❌ وابستگی‌های زیر یافت نشدند:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\nبرای نصب:")
        print("pip install customtkinter psutil")
        return False
    
    print("\n🚀 در حال راه‌اندازی نسخه پیشرفته...")
    return True

def main():
    """تابع اصلی"""
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        # Import and run enhanced application
        print("📁 بارگذاری ماژول‌های پیشرفته...")
        from file_copier_app_enhanced import main as run_enhanced_app
        
        print("🎨 راه‌اندازی رابط کاربری پیشرفته...")
        run_enhanced_app()
        
    except ImportError as e:
        print(f"❌ خطا در import: {e}")
        print("لطفاً مطمئن شوید که فایل file_copier_app_enhanced.py موجود است")
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