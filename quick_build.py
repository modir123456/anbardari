#!/usr/bin/env python3
"""
Persian File Copier Pro - Quick Build Script
اسکریپت ساخت سریع برای تولید فایل اجرایی
شرکت فناوری نوآئران مثبت سبز
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """نمایش بنر"""
    print("=" * 60)
    print("🚀 Persian File Copier Pro - Quick Build")
    print("   شرکت فناوری نوآئران مثبت سبز")
    print("=" * 60)

def run_command(cmd):
    """اجرای دستور"""
    print(f"💻 Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def install_pyinstaller():
    """نصب PyInstaller"""
    print("\n📦 Installing PyInstaller...")
    return run_command(f"{sys.executable} -m pip install pyinstaller")

def build_basic():
    """ساخت بنیادی"""
    print("\n🔨 Building basic executable...")
    
    # Basic PyInstaller command
    cmd = f"pyinstaller --onefile --windowed --name=\"Persian_File_Copier_Pro\" run_web_pro.py"
    
    if not run_command(cmd):
        return False
    
    print("\n✅ Basic executable created in 'dist' folder!")
    return True

def build_with_data():
    """ساخت با فایل‌های داده"""
    print("\n🔨 Building executable with data files...")
    
    # Advanced PyInstaller command with data files
    cmd = f"""pyinstaller --onefile --windowed \
--name="Persian_File_Copier_Pro" \
--add-data="web;web" \
--add-data="README.md;." \
--hidden-import=eel \
--hidden-import=psutil \
--hidden-import=requests \
--hidden-import=sqlite3 \
run_web_pro.py"""
    
    if not run_command(cmd):
        return False
    
    print("\n✅ Advanced executable created in 'dist' folder!")
    return True

def build_directory():
    """ساخت نسخه پوشه‌ای"""
    print("\n🔨 Building directory version...")
    
    cmd = f"""pyinstaller --onedir --windowed \
--name="Persian_File_Copier_Pro" \
--add-data="web;web" \
--add-data="README.md;." \
--hidden-import=eel \
--hidden-import=psutil \
--hidden-import=requests \
--hidden-import=sqlite3 \
run_web_pro.py"""
    
    if not run_command(cmd):
        return False
    
    print("\n✅ Directory version created in 'dist' folder!")
    return True

def main():
    """تابع اصلی"""
    print_banner()
    
    if len(sys.argv) > 1:
        option = sys.argv[1]
        
        if option == "--help" or option == "-h":
            print("""
🔧 Quick Build Options:

  python quick_build.py basic      - Build single executable file
  python quick_build.py advanced   - Build with all data files
  python quick_build.py directory  - Build as directory
  python quick_build.py install    - Install PyInstaller only
  
  --help, -h                       - Show this help
            """)
            return
        
        elif option == "install":
            install_pyinstaller()
            return
        
        elif option == "basic":
            if install_pyinstaller():
                build_basic()
            return
        
        elif option == "advanced":
            if install_pyinstaller():
                build_with_data()
            return
        
        elif option == "directory":
            if install_pyinstaller():
                build_directory()
            return
    
    # Interactive mode
    print("\n🔧 Choose build type:")
    print("1. Basic executable (single file)")
    print("2. Advanced executable (with data files)")
    print("3. Directory version (folder with files)")
    print("4. Install PyInstaller only")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            if install_pyinstaller():
                build_basic()
        elif choice == "2":
            if install_pyinstaller():
                build_with_data()
        elif choice == "3":
            if install_pyinstaller():
                build_directory()
        elif choice == "4":
            install_pyinstaller()
        else:
            print("❌ Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()