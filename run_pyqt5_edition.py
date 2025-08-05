#!/usr/bin/env python3
"""
Persian File Copier Pro - PyQt5 Edition Launcher Script
This script checks dependencies and launches the PyQt5 application
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    # Check PyQt5
    try:
        from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
        print(f"✓ PyQt5 {PYQT_VERSION_STR} (Qt {QT_VERSION_STR})")
    except ImportError:
        missing_deps.append("PyQt5 (install with: pip install PyQt5)")
    except Exception:
        try:
            import PyQt5
            print("✓ PyQt5 is available")
        except ImportError:
            missing_deps.append("PyQt5 (install with: pip install PyQt5)")
    
    # Check psutil
    try:
        import psutil
        print(f"✓ psutil {psutil.__version__}")
    except ImportError:
        missing_deps.append("psutil (install with: pip install psutil)")
    
    # Check requests
    try:
        import requests
        print(f"✓ requests {requests.__version__}")
    except ImportError:
        missing_deps.append("requests (install with: pip install requests)")
    
    # Check Pillow (optional for icons)
    try:
        import PIL
        print(f"✓ Pillow (PIL) {PIL.__version__}")
    except ImportError:
        print("⚠ Pillow not found (icons will use defaults)")
    
    if missing_deps:
        print("\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        return False
    
    return True

def install_pyqt5():
    """Try to install PyQt5 automatically"""
    print("\n🔧 Attempting to install PyQt5...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
        print("✓ PyQt5 installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install PyQt5 automatically")
        print("Please install manually with: pip install PyQt5")
        return False

def install_missing_deps():
    """Try to install all missing dependencies automatically"""
    print("\n🔧 Attempting to install missing dependencies...")
    deps_to_install = ["PyQt5", "psutil", "requests", "Pillow"]
    
    for dep in deps_to_install:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ {dep} installed successfully")
        except subprocess.CalledProcessError:
            print(f"⚠ Failed to install {dep} - please install manually")
    
    return True

def launch_application():
    """Launch the main PyQt5 application"""
    try:
        from persian_file_copier_pyqt5 import main
        print("\n🚀 Launching Persian File Copier Pro - PyQt5 Edition...")
        main()
    except ImportError as e:
        print(f"❌ Failed to import PyQt5 application: {e}")
        print("Make sure persian_file_copier_pyqt5.py exists in the current directory")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("Persian File Copier Pro - PyQt5 Edition Launcher")
    print("شرکت فناوری نوآئران مثبت سبز")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        # Try to install missing dependencies
        try:
            if install_missing_deps():
                # Recheck dependencies
                print("\n🔄 Rechecking dependencies...")
                if not check_dependencies():
                    print("\n💡 Manual installation may be required:")
                    print("1. Install PyQt5: pip install PyQt5")
                    print("2. Install psutil: pip install psutil") 
                    print("3. Install requests: pip install requests")
                    print("4. Install Pillow: pip install Pillow")
                    sys.exit(1)
            else:
                sys.exit(1)
        except Exception as e:
            print(f"\n❌ Installation failed: {e}")
            print("\n💡 Manual installation instructions:")
            print("1. Install PyQt5: pip install PyQt5")
            print("2. Install psutil: pip install psutil")
            print("3. Install requests: pip install requests") 
            print("4. Install Pillow: pip install Pillow")
            print("\nOr install all at once:")
            print("pip install PyQt5 psutil requests Pillow")
            sys.exit(1)
    
    # Launch the PyQt5 application
    if not launch_application():
        sys.exit(1)

if __name__ == "__main__":
    main()