#!/usr/bin/env python3
"""
Persian File Copier Pro - Web UI Launcher
HTML/CSS/JavaScript frontend with Python backend
شرکت فناوری نوآئران مثبت سبز
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """بررسی نسخه پایتون"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def install_requirements():
    """نصب وابستگی‌ها"""
    requirements_file = 'requirements_web.txt'
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file '{requirements_file}' not found")
        return False
    
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_dependencies():
    """بررسی وابستگی‌ها"""
    required_packages = {
        'eel': 'eel',
        'psutil': 'psutil', 
        'requests': 'requests',
        'PIL': 'Pillow'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {pip_name}")
        except ImportError:
            print(f"❌ {pip_name} - Missing")
            missing_packages.append(pip_name)
    
    return missing_packages

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("Persian File Copier Pro - Web UI Launcher")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    print(f"✅ Python {platform.python_version()}")
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print(f"\n📦 Missing packages: {', '.join(missing)}")
        response = input("Install missing packages? (y/n): ").lower().strip()
        
        if response in ['y', 'yes', '']:
            if not install_requirements():
                return 1
        else:
            print("❌ Cannot proceed without required packages")
            return 1
    
    print("\n🚀 Starting Persian File Copier Pro - Web Edition...")
    
    # Import and run the web app
    try:
        from web_app import main as run_web_app
        run_web_app()
    except ImportError as e:
        print(f"❌ Error importing web app: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
        return 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())